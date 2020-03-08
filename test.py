"""Torch API test

Emulation of a server sending request to the API.
"""

__author__ = "Omar Othman; Emre Bicer"

import datetime
import json
import os

from torchapi.api import handle


def main():
    """Emulates a server sending requests to the API.
    """

    # emulate getting a base-64 image from the front end
    (dirpath, dirnames, _) = next(os.walk(os.path.join(os.path.dirname(__file__), "test_input")))

    # emulate server operation
    for dirname in dirnames:
        full_path = os.path.join(dirpath, dirname)
        (_, _, filenames) = next(os.walk(full_path))
        for filename in filenames:
            with open(os.path.join(full_path, filename), "r") as base64_file:
                image_base64 = base64_file.read()

            # emulate getting a request from the front end as json
            
            # banknote detection
            request = {"request": "banknote", "image": image_base64}
            request_json = json.dumps(request)

            print(f"{str(datetime.datetime.now())} - Sending request")
            response = handle(request_json)
            print(f"Actual class {dirname} - response = {response}")


            # optical character recognition
            request["request"] = "ocr" 
            request_json = json.dumps(request)

            print(f"{str(datetime.datetime.now())} - Sending request")
            response = handle(request_json)
            print(f"Actual class {dirname} - OCR = {response}")


if __name__ == "__main__":
    main()
