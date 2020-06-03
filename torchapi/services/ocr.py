"""Optical character recognition module
"""

__author__ = "Emre Biçer"


try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

import os
import re
from .base_services import Service
from .common import asset_file, temp_file, base64_to_image_obj
from ..exceptions import TorchException
from ..logger import log_e

import cv2
import numpy as np

class OcrService(Service):
    """A service for optical character recognition
    """

    def __init__(self):
        service_name = "ocr"
        super().__init__(service_name)

    def pre_process_image(self, full_img_path:str):
        """
            Reads the image from the given path,
            applies image processing techniques
                - resizing with inter_area interpolation
                - bilateral filter
                - adaptive thresholding
            Overrides the new image file to the 
            previous path.
        """
        
        # Read the image as 1 channel (grayscaled)
        img = cv2.imread(full_img_path,cv2.CV_8UC1)
        
        # Resize the image
        img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        
        # Remove the noise
        img = cv2.bilateralFilter(img,9,75,75)

        # Apply thresholding to stand out texts only
        cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)        
        
        # Write the image to the disk
        cv2.imwrite(full_img_path,img)
        

    def predict(self, req: dict) -> str:
        
        # Specify the path for Windows
        # pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

        """
         NOTE: not sure if this function should be called predict,
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
        temp_image_filename = temp_file(self.service_name, random_file_name) + ".jpg"

        with open(temp_image_filename, "wb") as img_file:
            img_file.write(image_obj)
            
        # Preprocess the image for better ocr
        self.pre_process_image(temp_image_filename)
        
        try:
            # Send the image name to the OCR engine
            
            # Check if the language is specified
            lang = req.get("language", None)
            config = ("--oem 1")

            if lang:
                result = pytesseract.image_to_string(Image.open(temp_image_filename), lang=lang, config=config)
            else:
                result = pytesseract.image_to_string(Image.open(temp_image_filename), config=config)

            # Format the output, avoid unnecessarry chars

            # Replace all whitespaces with single space
            result = re.sub(r'()\s', ' ', result)
            # Replace punctiation chars with single space
            result = re.sub(r'[.,!;:]', ' ', result)
            # If not char, number or (+ - %) replace with single space
            result = re.sub(r'[^a-zA-Z0-9+\-%]', ' ', result)
            # Make sure all spaces are only a single space
            result = ' '.join(result.split())


        except Exception as err:
            # remove the image file
            os.remove(temp_image_filename)
            
            # Log the error then throw the error
            log_e(self.service_name,str(err))
            raise err

        # remove the image file
        os.remove(temp_image_filename)
        return result,1
    
    
