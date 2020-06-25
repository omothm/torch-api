"""Color detection module with knn classifier 
"""

__author__ = "Ezgi Nur Ucay"

from .base_services import Service
from .common import base64_to_image_obj, temp_file, asset_file
from .assets.color_detection.utils.knn_classifier import classify
from .assets.color_detection.utils.color_feature_extraction import histogram_of_test_image
from ..exceptions import TorchException
from .object_detection import ObjectDetectionService
import os
import cv2

class ColorDetectionService(Service):
    """A service for detecting color of object.
    """

    def __init__(self, object_detection: ObjectDetectionService):
        service_name = "color"
        self.frame = object_detection
        super().__init__(service_name)

    def predict(self, req: dict) -> str:
        """
        Detect color in the given base64,
        returns a dictionary with keys:
            'prediction'
            'object_name'
        If the object cannot be detected, the color detection service will 
        return the result based on the histogram of the whole image. 
        If one or more objects are detected, knn value is calculated for 
        each object depending on its frames and the name of the object is 
        returned with the prediction value.
        """

        try:
            image_obj = base64_to_image_obj(req)
        except TorchException as ex:
            raise TorchException(msg=str(ex), origin=self.service_name)

        random_file_name = super().get_random_name()
        temp_image_filename = temp_file(self.service_name, random_file_name)

        with open(temp_image_filename, "wb") as img_file:
            img_file.write(image_obj)

        objects = self.frame.get_objects_with_frames(temp_image_filename)
        prediction = ''

        try:
            if not objects:
                histogram_of_test_image(temp_image_filename)
                prediction += str(classify('training.data','test.data'))
            else:
                frames = list(map(lambda x: x['frames'], objects))
                object_names = list(map(lambda x: x['object_name'], objects))

                for i in range(len(frames)):
                    histogram_of_test_image(temp_image_filename, frames[i])
                    prediction += str(classify('training.data', 'test.data'))+' '+str(object_names[i])
                    if i != len(frames) - 1:
                        prediction+=','

            os.remove(temp_image_filename)
            return str(prediction), 1

        except:
            raise Exception("Could not detect color")

    def add_training_data(img_path, img_tag):
        add_training_histogram(img_path, img_tag)
