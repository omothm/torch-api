"""Class Confidence Analysis

Plots statistics on the the confidence range of a given class.

This script accepts args.

Synopsis:

    analysis.py <path>...

<path>...: the paths inside data/base64/ of the class to analyze.
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

    if len(sys.argv) < 2:
        print_help(os.path.basename(sys.argv[0]))
        sys.exit(1)

    class_names = sys.argv[1:]

    confidences = [[] for _ in enumerate(class_names)]

    print("\nPredicting images...")
    errors = []

    # for each directory (class), run the inference on all images
    for i, class_name in enumerate(class_names):
        path = os.path.join(TEST_DIR, class_name)
        (_, _, filenames) = next(os.walk(path))
        for filename in tqdm(filenames, desc=class_name, unit="file"):

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
                errors.append(f"{filename}: {response_json['error_message']}")
                continue

            if response_json["status"] == "ok":
                confidences[i].append(response_json["confidence"])

    if errors:
        print("\nErrors:")
        for error in errors:
            print(error)

    print("\nPlotting results...")
    plt.boxplot(confidences, widths=0.5)
    plt.xticks(range(1, len(class_names) + 1), class_names)
    plt.minorticks_on()
    plt.grid(which='major', axis='y')
    plt.grid(which='minor', axis='y', linestyle=':', alpha=0.3)
    plt.ylim(0, 1)
    plt.ylabel("Confidence level")
    plt.title('Confidence statistics')
    plt.show()


def print_help(filename):
    print("Synopsis:")
    print(f"    {filename} <path>...")
    print("<path>...: the paths inside data/base64/ of the class to analyze.")


if __name__ == "__main__":
    main()
