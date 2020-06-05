"""Torch API baknote service test

Emulation of a server sending request to the API.
"""


import datetime
import json
import os

from torchapi import handle


def main():
    """Emulates a server sending requests to the API.
    """

    # Emulate getting a base-64 image from the front end
    (dirpath, dirnames, _) = next(
        os.walk(os.path.join(os.path.dirname(__file__), "test_input")))

    # Emulate server operation
    for dirname in dirnames:
        # Get only banknote service related directories
        if dirname in ['5', '10', '20', '50', 'bg']:
            # Currency detection tests
            full_path = os.path.join(dirpath, dirname)
            (_, _, filenames) = next(os.walk(full_path))
            for filename in filenames:
                with open(os.path.join(full_path, filename), "r") as base64_file:
                    image_base64 = base64_file.read()

                    # Emulate getting a request from the front end as json

                    # Banknote detection
                    request = {"request": "banknote", "image": image_base64}
                    request_json = json.dumps(request)

                    print(
                        f"{str(datetime.datetime.now())} - Sending request (banknote detection)")
                    response = handle(request_json)
                    print(f"Actual class {dirname} - response = {response}")


if __name__ == "__main__":
    main()
