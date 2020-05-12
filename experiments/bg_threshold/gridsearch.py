"""Threshold Grid Search

Searches for the best threshold value for the given classes.

Note that this script must be run while the background threshold is ZERO. The
aim is to figure out a suitable threshold level. Running the confidence analysis
while a threshold does exist will result in misleading statistics.

This script requires args.

Synopsis:

    gridsearch.py <class>...

<class>...: the class(es) inside data/base64/ of the class to include in the
grid search.
"""


__author__ = "Omar Othman <omar.othman@live.com>"


import json
import os
import sys

from matplotlib import pyplot as plt
import numpy as np
from tqdm import tqdm

from torchapi.api import handle


# the total number of classes in the model, not the ones included in the
# analysis only.
NUM_CLASSES = 6
# used in the plot title.
TARGET_CLASS_NAMES = "class 200"
PLOT_TITLE = f"Delta values for a range of thresholds for {TARGET_CLASS_NAMES}"
STEP_SIZE = 0.01
TEST_DIR = os.path.join(os.path.dirname(__file__), "data", "base64")


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    class_names = sys.argv[1:]

    print("Calculating confidences...")
    total_samples = 0
    correct_confidences = []
    incorrect_confidences = []
    for class_name in class_names:
        class_path = os.path.join(TEST_DIR, class_name)
        (_, _, filenames) = next(os.walk(class_path))
        for filename in tqdm(filenames, desc=class_name, unit="file"):

            # get the base64 image string
            with open(os.path.join(class_path, filename), "r") as base64_file:
                image_base64 = base64_file.read()

            # build the request
            request_json = {"request": "banknote", "image": image_base64}
            request = json.dumps(request_json)

            # infer
            response = handle(request)
            response_json = json.loads(response)
            if response_json["status"] == "ok":
                total_samples = total_samples + 1
                if response_json["response"] == class_name:
                    correct_confidences.append(response_json["confidence"])
                else:
                    incorrect_confidences.append(response_json["confidence"])
            else:
                raise Exception(
                    f"Inference error in the class {class_name} file {filename}")

    print("Grid searching...")
    tvals = np.linspace(0, 1, int(1 / STEP_SIZE) + 1)
    # discard thresholds below the 1/num_classes
    tvals = [t for t in tvals if t >= 1 / NUM_CLASSES]

    deltas = [delta(t, correct_confidences, incorrect_confidences, total_samples)
              for t in tvals]
    best_t = tvals[np.argmin(deltas)]
    print(f"Best threshold: {best_t}")
    plt.plot(tvals, deltas)
    plt.xlim([tvals[0], tvals[-1]])
    plt.xlabel("Threshold")
    plt.ylabel("$\delta$")
    plt.title(PLOT_TITLE)
    plt.grid()
    plt.show()

    # correct_count = []
    # incorrect_count = []
    # for tval in tvals:
    #     correct_count.append(sum([1 for x in correct_confidences if x > tval]) / total_samples)
    #     incorrect_count.append(
    #         sum([1 for x in incorrect_confidences if x > tval]) / total_samples)
    # plt.plot(correct_count, incorrect_count)
    # plt.xlabel("Correct percentage")
    # plt.ylabel("Incorrect percentage")
    # plt.show()


def delta(t, correct, incorrect, total):
    correct_percentage = np.sum([1 for x in correct if x > t]) / total
    incorrect_percentage = np.sum([1 for x in incorrect if x > t]) / total
    return correct_percentage ** 2 - 2 * correct_percentage + incorrect_percentage ** 2


def print_help():
    print("Synopsis:")
    print(f"    {os.path.basename(sys.argv[0])} <class>...")
    print("<class>...: the class(es) inside data/base64/ of the class to include in the")
    print("grid search.")


if __name__ == "__main__":
    main()
