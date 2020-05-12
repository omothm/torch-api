"""Confidence Analysis

Plots statistics on the the confidence range of correct and incorrect
predictions as box plots.

Note that this script must be run while the background threshold is ZERO. The
aim is to figure out a suitable threshold level. Running the confidence analysis
while a threshold does exist will result in misleading statistics.

This script accepts args.

Synopsis:

    analysis.py [-s|--save]

-s | --save: an optional switch that saves the confidence values of correct and
             incorrect predictions to two separate json files.
"""

__author__ = "Omar Othman <omar.othman@live.com>"


import json
import os
import sys

import matplotlib.pyplot as plt
from tqdm import tqdm

from torchapi.api import handle


TEST_DIR = os.path.join(os.path.dirname(__file__), "data", "base64")


def main():

    save = False
    arg_error = False
    if len(sys.argv) > 2:
        arg_error = True
    if len(sys.argv) == 2 and sys.argv[1] not in ["-s", "--save"]:
        arg_error = True
    else:
        save = True

    if arg_error:
        print_help(os.path.basename(sys.argv[0]))
        sys.exit(1)

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

    if save:
        print("\nSaving confidences...")
        with open(os.path.join(os.path.dirname(__file__), "output/correct.json"), "w") as out_file:
            out_file.write(json.dumps(correct_confidences))
        with open(os.path.join(os.path.dirname(__file__), "output/incorrect.json"), "w") as out_file:
            out_file.write(json.dumps(incorrect_confidences))

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


def print_help(filename):
    print("Synopsis:")
    print(f"    {filename} [-s|--save]")
    print("-s | --save: an optional switch that saves the confidence values of correct and")
    print("             incorrect predictions to two separate json files.")


if __name__ == "__main__":
    main()
