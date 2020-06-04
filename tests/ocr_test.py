"""Torch API OCR service test

"""

__author__ = "Emre Bicer"

import time
import base64
import datetime
import json
import os
from difflib import SequenceMatcher
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
    ocr_total_duration = .0
    ocr_max_inference_duration = -1.0
    ocr_minimum_similarity = 1.0

    # Get the full path for input directory
    test_input_path = os.path.join(os.path.dirname(__file__), 'test_input')

    # Get the full path for ocr test inputs dircetory
    ocr_test_input_path = os.path.join(test_input_path, 'ocr_test_images')

    # Get the all sub directory names
    ocr_test_dirs = os.listdir(ocr_test_input_path)

    for current_dir in ocr_test_dirs:
        dir_path = os.path.join(ocr_test_input_path, current_dir)
        if os.path.isdir(dir_path):
            # Get all file names in this dir
            current_test_files = os.listdir(dir_path)

            for current_file in current_test_files:
                # Emulate the api call for each test image
                request = {}
                request["request"] = "ocr"

                # Read the test image file
                with open(os.path.join(dir_path, current_file), "rb") as image_file:
                    encoded_string = base64.b64encode(
                        image_file.read())
                request["image"] = "data:image/png;base64," + \
                    encoded_string.decode('utf-8')
                request_json = json.dumps(request)

                print(
                    f"{str(datetime.datetime.now())} - Sending request (OCR)")


                # Start timer
                inference_time_start = time.time()

                response = handle(request_json)
                ocr_test_count += 1

                # End the timer
                inference_duration = (time.time() - inference_time_start)
                ocr_total_duration += inference_duration

                # At initial test the time is biased because of imported libraries,
                # If it is the duration for 1st test just ignore it
                if ocr_max_inference_duration < inference_duration and ocr_test_count != 1:
                    ocr_max_inference_duration = inference_duration

                response_dict = json.loads(response)
                if response_dict['status'] == 'ok':
                    # Calculate the accuracy
                    file_name_without_extension = os.path.splitext(
                        os.path.basename(current_file))[0]
                    similarity = SequenceMatcher(
                        None, response_dict["response"], file_name_without_extension).ratio()

                    if ocr_minimum_similarity > similarity:
                        ocr_minimum_similarity = similarity

                    ocr_average_similarity += similarity
                    """
                        print(f"    - OCR Actual result:{file_name_without_extension}")
                        print(f"    - OCR Found  result:{response_dict['response']}   <{similarity}>")
                        """
                    print(
                        f"{response_dict['time']} - OCR Result similarity score: {similarity}")

    # Calculate the average similarity score for OCR
    ocr_average_similarity = ocr_average_similarity / ocr_test_count
    ocr_average_duration = ocr_total_duration / ocr_test_count

    print('\n\nSummary\n')

    print(f'\t# of tests: {ocr_test_count}')
    print(f'\tDuration results:')
    print(f'\t\tTotal inference duration:{ocr_total_duration} seconds')
    print(f'\t\tAverage inference duration:{ocr_average_duration} seconds')
    print(f'\t\tMaximum inference duration:{ocr_max_inference_duration} seconds')
    print(f'\tSimilarity results: range -> [0, 1]')
    print(f'\t\tAverage similarity score:{ocr_average_similarity}')
    print(f'\t\tMinimum similarity score:{ocr_minimum_similarity}\n')


if __name__ == "__main__":
    main()
