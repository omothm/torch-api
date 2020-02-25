"""Base services

Classes representing common functionalities for services.
"""

__author__ = "Emre Bicer; Omar Othman"

import numpy as np

from keras.models import load_model
from keras.preprocessing import image

from .common import asset_file, temp_file, base64_to_image_obj
from ..exceptions import TorchException
from ..logger import log_i


class Service:
    """Base class for all Torch services.
    """

    def __init__(self, service_name):
        self.service_name = service_name
        log_i(self.service_name, "Initiating new class")


class KerasCnnImageService(Service):
    """Base class for any service that uses CNN image classification using Keras
    h5 model.

    ### Arguments
    `service_name`: a unique name for the service to use in file directories and
    log messages.

    `class_map`: a `dict` mapping model outputs to desired class names. If not
    provided, model output is directly returned.

    `model_filename`: name of model file to load from the assets directory.
    Default is `model.h5`.

    `temp_image_filename`: name of file, used to temporarily save the image
    being processed, to load from the temp directory. Default is `image`.
    """

    def __init__(self, service_name, class_map: dict = None,
                 model_filename: str = "model.h5", temp_image_filename: str = "image"):
        super().__init__(service_name)
        self.class_map = class_map
        self.model_filename = asset_file(self.service_name, model_filename)
        self.temp_image_filename = temp_file(
            self.service_name, temp_image_filename)
        self.model = None
        self.image_size = (224, 224)

    def predict(self, req: dict) -> int:
        """Runs inference on the image provided in the given `req`uest.
        """
        try:
            image_obj = base64_to_image_obj(req)
        except TorchException as ex:
            raise TorchException(msg=str(ex), origin=self.service_name)
        with open(self.temp_image_filename, "wb") as img_file:
            img_file.write(image_obj)
        # load model only once per session
        if not self.model:
            try:
                self.model = load_model(self.model_filename)
                log_i(self.service_name, "Model loaded")
            except:
                raise Exception(f"Could not load model [{self.service_name}]")
        try:
            temp_image = self.__load_image(self.temp_image_filename)
        except:
            raise Exception("Could not load image data")
        pred = self.model.predict(temp_image)
        result = np.argmax(pred, axis=1)
        if self.class_map:
            prediction_class = self.class_map.get(result[0], None)
            if not prediction_class:
                raise Exception(
                    "Unexpected class from model [{self.service_name}]")
        else:
            prediction_class = result[0]
        return prediction_class

    def __load_image(self, img_path):
        """
            Resize the image and map the pixel values between 0 and 1
        """
        # Load the image with given size
        img = image.load_img(img_path, target_size=self.image_size)
        # convert the image into array format (height, width, channels)
        img_tensor = image.img_to_array(img)
        # add a dimension because the model expects this shape: (batch_size,
        # height, width, channels)
        img_tensor = np.expand_dims(img_tensor, axis=0)
        # imshow expects values in the range [0, 1]
        img_tensor /= 255.

        return img_tensor
