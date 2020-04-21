"""Confidence Analysis

Plots statistics on the the confidence range of correct and incorrect
predictions as box plots.

Note that this script must be run while the background threshold is ZERO. The
aim is to figure out a suitable threshold level. Running the confidence analysis
while a threshold does ex

This script accepts no args.
"""

__author__ = "Omar Othman <omar.othman@live.com>"


import json
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

from torchapi.api import handle
from torchapi.exceptions import TorchException


TEST_DIR = os.path.join(os.path.dirname(__file__), "data", "base64")


def main():

    # two lists for correctly predicted and incorrectly predicted values'
    # confidence values.
    correct_confidences = []
    incorrect_confidences = []

    # get all directories (classes) in the test directory
    (dirpath, dirnames, _) = next(os.walk(os.path.join(TEST_DIR)))

    print("\nPredicting classes...")
    errors = []
    for dirname in dirnames:

        # ignore 'bg' class
        if dirname == 'bg':
            continue

        # for each directory (class), run the inference on all images
        path = os.path.join(dirpath, dirname)
        (_, _, filenames) = next(os.walk(path))
        for filename in tqdm(filenames, desc=dirname, unit="file"):

            # get the base64 image string
            with open(os.path.join(path, filename), "r") as base64_file:
                image_base64 = base64_file.read()

            # build the request
            request_json = {"request": "banknote", "image": image_base64}
            request = json.dumps(request_json)

            # infer
            response = handle(request)
            response_json = json.loads(response)
            if response_json["status"] == "error":
                errors.append(
                    f"{dirname}/{filename}: {response_json['error_message']}")
                continue

            if response_json["status"] == "ok":
                if response_json["response"] == dirname:
                    correct_confidences.append(response_json["confidence"])
                else:
                    incorrect_confidences.append(response_json["confidence"])

    if errors:
        print("\nErrors:")
        for error in errors:
            print(error)

    print("\nPlotting results...")
    plt.boxplot([correct_confidences, incorrect_confidences], widths=0.7)
    plt.xticks([1, 2], ["Correct", "Incorrect"])
    plt.minorticks_on()
    plt.grid(which='major', axis='y')
    plt.grid(which='minor', axis='y', linestyle=':', alpha=0.3)
    plt.ylim(0, 1)
    plt.ylabel("Confidence level")
    plt.title('Confidence statistics')
    plt.show()


if __name__ == "__main__":
    main()
