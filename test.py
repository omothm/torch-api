"""Torch API test

Emulation of a server sending request to the API.
"""

__author__ = "Omar Othman"

import datetime
import json
import time

from torchapi.api import handle


def main():
    """Emulates a server sending requests to the API.
    """

    # emulate getting a base-64 image from the front end
    with open("example_base64.txt", "r") as base64_file:
        image_base64 = base64_file.read()

    # emulate getting a request from the front end as json
    request = {"request": "banknote", "image": image_base64}
    request_json = json.dumps(request)

    # emulate server operation
    while True:
        print(f"{str(datetime.datetime.now())} - Sending request")
        response = handle(request_json)
        print(response)
        time.sleep(3)


if __name__ == "__main__":
    main()
