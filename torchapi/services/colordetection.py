"""Color detection module with knn classifier 
"""

__author__ = "Ezgi Nur Ucay"

from .base_services import Service
from .common import base64_to_image_obj,temp_file
from .color.knn_classifier import classify
from .color.color_feature_extraction import histogram_of_test_image
from ..exceptions import TorchException
import os

class ColorDetectionService(Service):
    """A service for detecting color of object.
    """

    def __init__(self):
        service_name = "color"
        super().__init__(service_name)

    def predict(self,req:dict) -> str:

        try:
            image_obj = base64_to_image_obj(req)
        except TorchException as ex:
            raise TorchException(msg=str(ex), origin=self.service_name)

        random_file_name = super().get_random_name()
        temp_image_filename = temp_file(self.service_name, random_file_name)

        with open(temp_image_filename, "wb") as img_file:
            img_file.write(image_obj)
        try:
            histogram_of_test_image(temp_image_filename)
            prediction=classify('training.data','test.data')
            os.remove(temp_image_filename)
            return str(prediction), 1
            
        except:
            raise Exception("Could not detect color")

    def add_training_data(img_path,img_tag):
        add_training_histogram(img_path,img_tag);