"""Base services

Classes representing common functionalities for services.
"""

__author__ = "Emre Bicer; Omar Othman"

import os
import random
import numpy as np

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

from .common import asset_file, temp_file, base64_to_image_obj
from ..exceptions import TorchException
from ..logger import log_e, log_i

# alphanumeric population for random name generator
_POPULATION = list(map(chr, list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123))))
_RANDOM_STRING_LENGTH = 64


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
    """

    def __init__(self, service_name, class_map: dict = None,
                 model_filename: str = "model.h5"):
        super().__init__(service_name)
        self.class_map = class_map
        self.model_filename = asset_file(self.service_name, model_filename)
        try:
            self.model = load_model(self.model_filename)
            log_i(self.service_name, "Model loaded")
        except:
            log_e(self.service_name, "Could not load model")
            raise Exception(f"Could not load model [{self.service_name}]")
        self.image_size = (224, 224)

    def predict(self, req: dict) -> int:
        """Runs inference on the image provided in the given `req`uest.
        """
        # The base-64 string is converted into an image object but this object
        # cannot be passed to Keras directly. The object is first dumped into a
        # temp file and then the filename is passed to Keras.
        try:
            image_obj = base64_to_image_obj(req)
        except TorchException as ex:
            raise TorchException(msg=str(ex), origin=self.service_name)
        random_file_name = self.__get_random_name()
        temp_image_filename = temp_file(self.service_name, random_file_name)
        with open(temp_image_filename, "wb") as img_file:
            img_file.write(image_obj)
        try:
            temp_image = self.__load_image(temp_image_filename)
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
        os.remove(temp_image_filename)
        return prediction_class


    def __get_random_name(self) -> str:
        return "".join(random.choices(_POPULATION, k=_RANDOM_STRING_LENGTH))

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
