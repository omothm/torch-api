"""Object detection module
"""

__author__ = "Emre Biçer"


try:
    from PIL import Image
except ImportError:
    import Image
import numpy as np
import os
import tensorflow as tf
from pattern.en import pluralize

from .assets.object_detection.utils import label_map_util

from .base_services import Service
from .common import asset_file, temp_file, base64_to_image_obj
from ..exceptions import TorchException
from ..logger import log_e, log_i


class ObjectDetectionService(Service):
    """A service for detectin objects
    """

    MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
    LABELS_FILE = 'mscoco_label_map.pbtxt'
    CLASSIFICATION_THRESHOLD = .5

    def __init__(self):
        service_name = "object_detection"

        super().__init__(service_name)

        # Declare the labels (category index)
        labels_path = asset_file(service_name, self.LABELS_FILE)
        self.category_index = label_map_util.\
            create_category_index_from_labelmap(labels_path,
                                                use_display_name=True)

        # Load the model
        try:
            self.detection_model = self.load_model(self.MODEL_NAME)
            log_i(self.service_name, "Model loaded")
        except Exception as e:
            log_e(self.service_name, "Could not load model" + ", error:"
                  + str(e))
            raise Exception(f"Could not load model [{self.service_name}]")

    def load_model(self, model_name):
        """
        Loads the prediction model with the given name
        from the disk and returns the model
        """
        model_path = asset_file(self.service_name, model_name)
        model = tf.saved_model.load(str(model_path))
        model = model.signatures['serving_default']

        return model

    def run_inference_for_single_image(self, model, image) -> dict:
        """
        Detect objects in the given image object,
            Expects the model instance and the image object
            returns a dictionary with keys:
                'detection_scores'
                'detection_classes'
                'detection_boxes'
                'num_detections'
        """
        image = np.asarray(image)
        # The input needs to be a tensor,
        # convert it using `tf.convert_to_tensor`.
        input_tensor = tf.convert_to_tensor(image)
        # The model expects a batch of images, so add an
        # axis with `tf.newaxis`.
        input_tensor = input_tensor[tf.newaxis, ...]

        # Run inference
        output_dict = model(input_tensor)

        # All outputs are batches tensors.
        # Convert to numpy arrays, and take index [0] to remove
        # the batch dimension.
        # We're only interested in the first num_detections.
        num_detections = int(output_dict.pop('num_detections'))
        output_dict = {key: value[0, :num_detections].numpy()
                       for key, value in output_dict.items()}
        output_dict['num_detections'] = num_detections

        # detection_classes should be ints.
        output_dict['detection_classes'] = \
            output_dict['detection_classes'].astype(np.int64)

        return output_dict

    def get_objects_with_frames(self, image_path: str) -> list:
        image_np = np.array(Image.open(image_path))
        result_dict = self.\
                run_inference_for_single_image(self.detection_model, image_np)

        # Filter the output by the threshold value
        approved_indexes = []

        for index, score in enumerate(result_dict['detection_scores']):
            if score > self.CLASSIFICATION_THRESHOLD:
                approved_indexes.append(index)

        final_objects = []

        # Get the approved classified objects
        for index, class_id in enumerate(result_dict['detection_classes']):
            if index in approved_indexes:
                category = self.category_index.get(class_id)
                final_objects.append({
                    'object_name' : category['name'],
                    'frames' : result_dict['detection_boxes'][index]
                })

        return final_objects
    

    def predict(self, req: dict) -> (str, float):
        """
            Expects a dictionary type `req`uest
            This dictionart must have an `image` key that
            stores base64 encoded image file.

            Returns a 2-d tuple; detected objects with count numbers
            and average confidence score of predictions
            e.g.
                ('2 person,3 kite,', 'confidence': 0.810070)
        """

        # Convert base64 encoded data to image and save
        # to the disk
        try:
            image_obj = base64_to_image_obj(req)
        except TorchException as ex:
            raise TorchException(msg=str(ex), origin=self.service_name)

        random_file_name = super().get_random_name()
        temp_image_filename = temp_file(self.service_name,
                                        random_file_name) + ".jpg"

        # Write the image to the disk
        with open(temp_image_filename, "wb") as img_file:
            img_file.write(image_obj)

        try:
            # Now read the image and detect objects in it
            image_np = np.array(Image.open(temp_image_filename))
            result_dict = self.\
                run_inference_for_single_image(self.detection_model, image_np)

            # {result_dict} includes keys:
            #   'detection_scores'
            #   'detection_classes'
            #   'detection_boxes'
            #   'num_detections'

            # Filter the output by the threshold value
            approved_indexes = []

            avg_prediction_score = .0

            for index, score in enumerate(result_dict['detection_scores']):
                if score > self.CLASSIFICATION_THRESHOLD:
                    approved_indexes.append(index)
                    avg_prediction_score += score

            approved_classifications = {}
            # Get the approved classified objects
            for index, class_id in enumerate(result_dict['detection_classes']):
                if index in approved_indexes:
                    category = self.category_index.get(class_id)
                    if category['name'] in approved_classifications.keys():
                        # Increment the count
                        approved_classifications[category['name']] += 1
                    else:
                        approved_classifications[category['name']] = 1

            # Prepare the result string
            result = ''
            for key in approved_classifications.keys():
                if approved_classifications[key] > 1:
                    # Convert to plural
                    result += str(approved_classifications[key]) + ' ' + pluralize(key) + ','
                else:
                    # Already singular
                    result += str(approved_classifications[key]) + ' ' + key + ','

            if len(approved_indexes) != 0:
                # Calculate the average prediction accuracy
                avg_prediction_score = \
                    avg_prediction_score / len(approved_indexes)

        except Exception as err:
            # remove the image file
            # os.remove(temp_image_filename)

            # Log the error then throw the error
            log_e(self.service_name, str(err))
            raise err

        # Remove the image file
        os.remove(temp_image_filename)

        if result == '':
            result = 'nothing'
        else:
            # Remove the last comma
            result = result[:-1]
            if ',' in result:
                # Get the last , index
                last_comma_index = result.rfind(',')
                result = result[:last_comma_index] + " and " + result[last_comma_index+1:]

        # Finally add a space after each comma
        result = result.replace(',',', ')

        # Pattern library can't pluralize these keywords so do it manually here
        result = result.replace('buss', 'busses')
        result = result.replace('skis', 'pair of skis')
        result = result.replace('skiss', 'pair of skis')

        return result, avg_prediction_score
