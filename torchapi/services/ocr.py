"""Optical character recognition module
"""

__author__ = "Emre Biçer"


try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

import os
from .base_services import Service
from .common import asset_file, temp_file, base64_to_image_obj
from ..exceptions import TorchException


class OcrService(Service):
    """A service for optical character recognition
    """

    def __init__(self):
        service_name = "ocr"
        super().__init__(service_name)

    def predict(self, req: dict) -> str:
        
        # Specify the path for Windows
        #pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

        """
         NOTE: not sure this function should be called predict,
         but this is the function name that 'api.py' calls.
        """

        # The base-64 string is converted into an image object but this object
        # cannot be passed to Tesseract OCR engine directly. The object is first dumped into a
        # temp file and then the filename is passed to Tesseract OCR engine.
        try:
            image_obj = base64_to_image_obj(req)
        except TorchException as ex:
            raise TorchException(msg=str(ex), origin=self.service_name)

        random_file_name = super().get_random_name()
        temp_image_filename = temp_file(self.service_name, random_file_name)

        with open(temp_image_filename, "wb") as img_file:
            img_file.write(image_obj)
        try:
            # Send the image name to the OCR engine
            
            # Check if the language is specified
            lang = req.get("language", None)
            if lang:
                result = pytesseract.image_to_string(Image.open(temp_image_filename), lang=lang)
            else:
                result = pytesseract.image_to_string(Image.open(temp_image_filename))
        except:
            raise Exception("Could not load image data")

        # remove the image file
        os.remove(temp_image_filename)
        return result
    
    
