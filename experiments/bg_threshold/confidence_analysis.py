"""Confidence Analysis

Plots statistics on the the confidence range of correct and incorrect
predictions as box plots.

Note that this script must be run while the background threshold is ZERO. The
aim is to figure out a suitable threshold level. Running the confidence analysis
while a threshold does exist will result in misleading statistics.

This script accepts args. See print_help.
"""

__author__ = "Omar Othman <omar.othman@live.com>"


import json
import os
import sys

import matplotlib.pyplot as plt

from .util import assert_banknote_threshold, load_base64, predict


TEST_DIR = os.path.join(os.path.dirname(__file__), "data", "base64")


def main():

    assert_banknote_threshold(0)

    # parse args
    save = False
    arg_error = False
    if len(sys.argv) > 2:
        arg_error = True
    if len(sys.argv) == 2:
        if sys.argv[1] not in ["-s", "--save"]:
            arg_error = True
        else:
            save = True
    if arg_error:
        print_help(os.path.basename(sys.argv[0]))
        sys.exit(1)


    # get all directories (classes) in the test directory
    (dirpath, dirnames, _) = next(os.walk(os.path.join(TEST_DIR)))
    errors = []

    # true positives
    true_positive_confidences = []
    for dirname in dirnames:
        # ignore 'bg' class
        if dirname == 'bg':
            continue
        # for each directory (class), run the inference on all images
        images = load_base64(dirname, os.path.join(dirpath, dirname))
        for (response_json, _) in predict(images):
            if response_json["status"] == "error":
                errors.append(f"{dirname}: {response_json['error_message']}")
                continue
            if response_json["status"] == "ok":
                if response_json["response"] == dirname:
                    true_positive_confidences.append(
                        response_json["confidence"]
                    )

    # false positives
    false_positive_confidences = []
    images = load_base64('bg', os.path.join(dirpath, 'bg'))
    for (response_json, _) in predict(images):
        if response_json["status"] == "error":
            errors.append(f"bg: {response_json['error_message']}")
            continue
        if response_json["status"] == "ok":
            false_positive_confidences.append(response_json["confidence"])

    if errors:
        print("\nErrors:")
        for error in errors:
            print(error)

    if save:
        print("\nSaving confidences...")
        with open(os.path.join(os.path.dirname(__file__), "output/tp.json"), "w") as out_file:
            out_file.write(json.dumps(true_positive_confidences))
        with open(os.path.join(os.path.dirname(__file__), "output/fp.json"), "w") as out_file:
            out_file.write(json.dumps(false_positive_confidences))

    print("\nPlotting results...")
    plt.boxplot([true_positive_confidences,
                 false_positive_confidences], widths=0.7)
    plt.xticks([1, 2], ["True positives", "False positives"])
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
