"""Base services

Classes representing common functionalities for services.
"""

__author__ = "Emre Bicer; Omar Othman"


from abc import ABC, abstractmethod
import os
import random
import numpy as np

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

from .common import asset_file, temp_file, base64_to_image_obj
from ..exceptions import TorchException
from ..logger import log_e, log_i

# alphanumeric population for random name generator
_POPULATION = list(map(chr, list(range(48, 58)) +
                       list(range(65, 91)) + list(range(97, 123))))
_RANDOM_STRING_LENGTH = 64


class Service(ABC):
    """Base class for all Torch services.
    """

    def __init__(self, service_name, config=None):
        self.service_name = service_name
        self.config = config
        log_i(self.service_name, "Initiating new class")

    @abstractmethod
    def predict(self, req: dict) -> (str, float):
        """Runs inference on the given `req`uest.

        Returns the predicted class as a string and its confidence level. The
        confidence level is a number between 0 and 1.
        """

    def get_random_name(self) -> str:
        return "".join(random.choices(_POPULATION, k=_RANDOM_STRING_LENGTH))


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

    def __init__(self, service_name, config=None, class_map: dict = None,
                 model_filename: str = "model.h5"):
        super().__init__(service_name, config)
        self.class_map = class_map
        self.model_filename = asset_file(self.service_name, model_filename)

        # configurations
        self.background_threshold = 0.0
        if self.config:
            self.background_threshold = self.config.get(
                "background_threshold", 0.0)

        # sanity checks
        invalid_threshold = False
        # convert int to float
        if isinstance(self.background_threshold, int):
            self.background_threshold = float(self.background_threshold)
        if isinstance(self.background_threshold, float):
            if not 0 <= self.background_threshold < 1:
                invalid_threshold = True
        else:  # list
            if not class_map:
                raise ValueError(
                    "Class map must be provided if background threshold is a list")
            if len(self.background_threshold) != len(class_map):
                raise ValueError(
                    "Threshold list length must the be same as the class map")
            if np.max(self.background_threshold) >= 1 or np.min(self.background_threshold) < 0:
                invalid_threshold = True
        if invalid_threshold:
            raise ValueError(
                "Background threshold must be between 0 (inclusive) and 1 (exclusive)")

        try:
            self.model = load_model(self.model_filename)
            log_i(self.service_name, "Model loaded")
        except:
            log_e(self.service_name, "Could not load model")
            raise Exception(f"Could not load model [{self.service_name}]")
        self.image_size = (224, 224)

    def predict(self, req: dict) -> (str, float):
        """Runs inference on the image in the given `req`uest.

        Returns the predicted class as a string and its confidence level. If the
        confidence level is below a given threshold (defined in the
        constructor), the predicted class is set to 'bg'.

        The confidence level is a number between 0 and 1 and is the one that
        corresponds to the predicted class's activation node in the model's last
        layer.
        """
        # The base-64 string is converted into an image object but this object
        # cannot be passed to Keras directly. The object is first dumped into a
        # temp file and then the filename is passed to Keras.
        try:
            image_obj = base64_to_image_obj(req)
        except TorchException as ex:
            raise TorchException(str(ex), self.service_name)
        random_file_name = super().get_random_name()
        temp_image_filename = temp_file(self.service_name, random_file_name)
        with open(temp_image_filename, "wb") as img_file:
            img_file.write(image_obj)
        try:
            temp_image = self.__load_image(temp_image_filename)
        except:
            raise TorchException(
                "Could not load image data", self.service_name)
        # Get a value between 0 and 1 for each class (pred is a list in a list)
        pred = self.model.predict(temp_image)
        # Get the index of the highest prediction
        result = np.argmax(pred, axis=1)
        if self.class_map:
            prediction_class = self.class_map.get(result[0], None)
            if not prediction_class:
                raise Exception(
                    "Unexpected class from model [{self.service_name}]")
        else:
            prediction_class = result[0]
        os.remove(temp_image_filename)

        confidence = float(pred[0][result[0]])
        # Compare the confidence with either the single-value threshold or the
        # corresponding class threshold if threshold is a provided as a list.
        if (isinstance(self.background_threshold, float) and
                confidence < self.background_threshold) \
                or (isinstance(self.background_threshold, list) and
                    confidence < self.background_threshold[result[0]]):
            prediction_class = 'bg'

        # Always return a string class
        return str(prediction_class), confidence

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
