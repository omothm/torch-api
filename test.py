"""Torch API test

Emulation of a server sending request to the API.
"""

__author__ = "Omar Othman; Emre Bicer; Ezgi Nur Ucay"

import datetime
import json
import os
import base64
from difflib import SequenceMatcher



from torchapi.api import handle


def main():
    """Emulates a server sending requests to the API.
    """

    # emulate getting a base-64 image from the front end
    (dirpath, dirnames, _) = next(os.walk(os.path.join(os.path.dirname(__file__), "test_input")))

    # emulate server operation
    for dirname in dirnames:        
        if dirname in ['5','10','20','50','bg']:
            # Currency detection tests
            full_path = os.path.join(dirpath, dirname)
            (_, _, filenames) = next(os.walk(full_path))
            for filename in filenames:        
                with open(os.path.join(full_path, filename), "r") as base64_file:
                    image_base64 = base64_file.read()

                    # emulate getting a request from the front end as json
                    
                    # banknote detection
                    request = {"request": "banknote", "image": image_base64}
                    request_json = json.dumps(request)

                    print(f"{str(datetime.datetime.now())} - Sending request (banknote detection)")
                    response = handle(request_json)
                    print(f"Actual class {dirname} - response = {response}")

        elif dirname in ['ocr_test_images']:
                # OCR tests

                # Get the full dir path
                full_path = os.path.join(dirpath, dirname)

                # Get the all sub directory names
                ocr_test_dirs = os.listdir(full_path)

                for current_dir in ocr_test_dirs:
                    dir_path = os.path.join(full_path,current_dir)
                    if os.path.isdir(dir_path):
                        # Get all file names in this dir
                        current_test_files = os.listdir(dir_path)

                        for current_file in current_test_files:
                            # Emulate the api call
                            request = {}
                            request["request"] = "ocr" 

                            # Read the current_test_file and convert to base64
                            with open(os.path.join(dir_path,current_file), "rb") as image_file:
                                encoded_string = base64.b64encode(image_file.read())
                            request["image"] = "data:image/png;base64," + encoded_string.decode('utf-8')
                            request_json = json.dumps(request)

                            print(f"{str(datetime.datetime.now())} - Sending request (OCR)")

                            response = handle(request_json)
                            response_dict = json.loads(response)

                            # Calculate the accuracy
                            file_name_without_extension = os.path.splitext(os.path.basename(current_file))[0]
                            similarity = SequenceMatcher(None, response_dict["response"], file_name_without_extension).ratio()                    

                            print(f"{response_dict['time']} - OCR Result similarity score: {similarity}")
                        
        elif dirname in ['color_test_images']:

           # Get the full dir path
            full_path = os.path.join(dirpath, dirname)
            # Get the all sub directory names
            color_test_dirs = os.listdir(full_path)
                        
            for current_dir in color_test_dirs:
                dir_path = os.path.join(full_path,current_dir)
                if os.path.isdir(dir_path):
                        # Get all file names in this dir
                        current_test_files = os.listdir(dir_path)

                        for file in current_test_files:
                            with open(os.path.join(dir_path, file), "r") as base64_file:
                                image_base64 = base64_file.read()

                                # color detection 
                                request = {"request": "color", "image": image_base64}
                                request_json = json.dumps(request)

                                print(f"{str(datetime.datetime.now())} - Sending request")
                                response = handle(request_json)
                                print(f"Actual class {dirname} - Color = {response}")

if __name__ == "__main__":
    main()
