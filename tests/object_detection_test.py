"""Torch API object detection service test

"""

__author__ = "Emre Bicer"

import base64
import datetime
import json
import os

# torchapi is at the parent directory
# add 'parent_dir' to the path
import sys
sys.path.insert(0,'..')
from torchapi.api import handle


def main():
    """Emulates a server sending requests to the API.
    """

    ocr_test_count = 0
    ocr_average_similarity = 0.0

    # Get the full path for input directory
    test_input_path = os.path.join(os.path.dirname(__file__), 'test_input')

    # Get the full path for object detection test input dircetory
    object_detection_test_input_path = os.path.join(test_input_path, 'object_detection_test_images')

    # Get all images
    test_files = os.listdir(object_detection_test_input_path)

    for im in test_files:
        # Emulate the api call
        request = {}
        request["request"] = "object_detection"

        # Read the current_test_file and convert to base64
        with open(os.path.join(object_detection_test_input_path, im) , 'rb') as image_file:
            encoded_string = base64.b64encode(
                image_file.read())
        request["image"] = "data:image/png;base64," + \
            encoded_string.decode('utf-8')
        request_json = json.dumps(request)

        print(
            f"{str(datetime.datetime.now())} - Sending request (Object Detection)")

        response = handle(request_json)
        response_dict = json.loads(response)

        print(f"{response_dict}")


if __name__ == "__main__":
    main()
