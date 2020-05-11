"""Detailed color detection module
"""

__author__ = "Emre Biçer"


import math
import os
import sys

import cv2
import numpy

from ..exceptions import TorchException
from ..logger import log_e
from .base_services import Service
from .common import asset_file, base64_to_image_obj, temp_file


class DetailedColor(Service):
    """A service for detecting color on  the image
    """

    def __init__(self):
        service_name = "detailed_color"
        super().__init__(service_name)

    def predict(self, req: dict) -> str:

        # Convert base64 string to an image object
        try:
            image_obj = base64_to_image_obj(req)
        except TorchException as ex:
            raise TorchException(msg=str(ex), origin=self.service_name)

        random_file_name = super().get_random_name()
        temp_image_filename = temp_file(self.service_name,
                                        random_file_name) + ".jpg"

        # Write the binary file to the disk
        with open(temp_image_filename, "wb") as img_file:
            img_file.write(image_obj)

        # Read the image from disk
        try:
            myimg = cv2.imread(temp_image_filename)
            avg_color_per_row = numpy.average(myimg, axis=0)
            avg_color = numpy.average(avg_color_per_row, axis=0)
            # The format will be in BGR order (cv2 reads it that way)
            # convert it to RGB
            avg_color = avg_color.tolist()
            avg_color.reverse()

            # Now loop over the dataset to find the most similar color
            # (considering k = 1), the datapoints are single

            # temp vars for comparison of most similar data
            min_score = sys.maxsize  # Best match
            final_color = ''

            # Read the data set
            data_set_path = asset_file(self.service_name,
                                       'detailed_color_dataset.txt')
            with open(data_set_path) as data_set:
                for line in data_set:
                    cur_r, cur_g, cur_b, cur_color = line.split(',')
                    # Calculate eucladien distance
                    current_res = math.sqrt(
                        (int(cur_r) - avg_color[0]) ** 2 +
                        (int(cur_g) - avg_color[1]) ** 2 +
                        (int(cur_b) - avg_color[2]) ** 2
                    )
                    if current_res < min_score:
                        min_score = current_res
                        final_color = cur_color

        except Exception as err:
            # Log the error then throw the error
            log_e(self.service_name, str(err))
            raise err

        # remove the image file
        os.remove(temp_image_filename)
        final_color = final_color.replace('\n', '')
        return final_color, 1
