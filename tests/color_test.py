"""Torch API Color service test

"""

import datetime
import json
import os

from torchapi import handle


def main():
    """Emulates a server sending requests to the API.
    """


    # Get the full path for input directory
    test_input_path = os.path.join(os.path.dirname(__file__), 'test_input')

    # Get the full path for color test inputs dircetory
    color_test_input_path = os.path.join(test_input_path, 'color_test_images')

    # Get the all sub directory names
    color_test_dirs = os.listdir(color_test_input_path)

    for current_dir in color_test_dirs:
        dir_path = os.path.join(color_test_input_path, current_dir)
        if os.path.isdir(dir_path):
            # Get all file names in this dir
            current_test_files = os.listdir(dir_path)

            if os.path.isdir(dir_path):
                # Get all file names in this dir
                current_test_files = os.listdir(dir_path)

                for file in current_test_files:
                    with open(os.path.join(dir_path, file), "r") as base64_file:
                        image_base64 = base64_file.read()

                    # Emulate api request
                    request = {"request": "color",
                                "image": image_base64}
                    request_json = json.dumps(request)

                    print(
                        f"{str(datetime.datetime.now())} - Sending request")
                    response = handle(request_json)
                    print(
                        f"Actual class {current_dir} - Color = {response}")

    
if __name__ == "__main__":
    main()
