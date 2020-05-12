"""Threshold Grid Search

Searches for the best threshold value for the given classes.

Note that this script must be run while the background threshold is ZERO. The
aim is to figure out a suitable threshold level. Running the confidence analysis
while a threshold does exist will result in misleading statistics.

This script requires args.

Synopsis:

    gridsearch.py (-|<title>|-s) <class>... [-t]

(-|<title>|-s): text to append to the graph title, e.g. "Delta values for a
                range of thresholds for <title>". "-" uses the default value
                ("class(es)" appended by the given classes). "-s" means
                calculate each class separately.
<class>...:     the class(es) inside data/base64/ of the class to include in the
                grid search.
[-t]:           plot threshold curve (correct vs. incorrect curve).
"""


__author__ = "Omar Othman <omar.othman@live.com>"


import json
import os
import sys

from matplotlib import pyplot as plt
import numpy as np
from tqdm import tqdm

from torchapi.api import handle


DEFAULT_TITLE = "-"
FLAG_SEPARATE = "-s"
FLAG_THRESHOLD_CURVE = "-t"
# the total number of classes in the model, not the ones included in the
# analysis only.
NUM_CLASSES = 6
TITLE_DELTA = "Delta values for a range of thresholds for %s"
TITLE_THRESHOLD_CURVE = "Correct–incorrect curve for %s"
STEP_SIZE = 0.01
TEST_DIR = os.path.join(os.path.dirname(__file__), "data", "base64")


def main():
    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)

    threshold_curve = False
    title = sys.argv[1]
    class_names = sys.argv[2:]
    if len(class_names) > 1 and class_names[-1] == FLAG_THRESHOLD_CURVE:
        threshold_curve = True
        class_names = class_names[:-1]

    if title == FLAG_SEPARATE:
        for class_name in class_names:
            grid_search("-", [class_name], threshold_curve)
    else:
        grid_search(title, class_names, threshold_curve)

    plt.show()


def grid_search(title, class_names, threshold_curve):
    if title == DEFAULT_TITLE:
        title = f"class{'es' if len(class_names) > 1 else ''} {', '.join(class_names)}"

    print(f"Calculating confidences for {title}...")
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
    best_t_index = np.argmin(deltas)
    best_t = tvals[best_t_index]
    print(f"Best threshold: {best_t}")
    plt.figure()
    if threshold_curve:
        correct_count = []
        incorrect_count = []
        for tval in tvals:
            correct_count.append(
                sum([1 for x in correct_confidences if x > tval]) / total_samples)
            incorrect_count.append(
                sum([1 for x in incorrect_confidences if x > tval]) / total_samples)
        plt.plot(correct_count, incorrect_count, label="Threshold values")
        plt.scatter([1],[0], color="orange", label="Optimal point") # marker="o", s=80,
        nearest_point = (correct_count[best_t_index], incorrect_count[best_t_index])
        plt.plot([1, nearest_point[0]], [0, nearest_point[1]], color="gray",
                  linestyle=":", label="Nearest point")
        plt.text(nearest_point[0], nearest_point[1], f"$t$ = {best_t:.2f}")
        plt.xlim([-0.1, 1.1])
        plt.ylim([-0.1, 1.1])
        plt.xlabel("Correct percentage")
        plt.ylabel("Incorrect percentage")
        plt.title(TITLE_THRESHOLD_CURVE % title)
        plt.legend()
        plt.grid()
    else:
        plt.plot(tvals, deltas)
        plt.xlim([tvals[0], tvals[-1]])
        plt.xlabel("Threshold")
        plt.ylabel("$\delta$")
        plt.title(TITLE_DELTA % title)
        plt.grid()


def delta(t, correct, incorrect, total):
    correct_percentage = np.sum([1 for x in correct if x > t]) / total
    incorrect_percentage = np.sum([1 for x in incorrect if x > t]) / total
    return correct_percentage ** 2 - 2 * correct_percentage + incorrect_percentage ** 2


def print_help():
    print("Synopsis:")
    print(f"    {os.path.basename(sys.argv[0])} (-|<title>|{FLAG_SEPARATE}) <class>... "
          f"[{FLAG_THRESHOLD_CURVE}]")
    print(f"(-|<title>|{FLAG_SEPARATE}): text to append to the graph title, e.g. \"Delta "
          "values for a")
    print("                range of thresholds for <title>\". \"-\" uses the default value")
    print(
        f"                (\"class(es)\" appended by the given classes). \"{FLAG_SEPARATE}\" means")
    print("                calculate each class separately.")
    print("<class>...:     the class(es) inside data/base64/ of the class to include in the")
    print("                grid search.")
    print(f"[{FLAG_THRESHOLD_CURVE}]:           plot threshold curve (correct vs. "
          "incorrect curve).")


if __name__ == "__main__":
    main()
