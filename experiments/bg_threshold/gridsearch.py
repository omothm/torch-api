"""Threshold Grid Search

Searches for the best threshold value for the given classes. In the case of
single class thresholding (-s) thresholding, a background class (default name
"bg") is loaded along with the given class to calculate false positives and true
negatives.

Note that this script must be run while the background threshold is ZERO. The
aim is to figure out a suitable threshold level. Running the confidence analysis
while a threshold does exist will result in misleading statistics.

This script requires args. See print_help.
"""


__author__ = "Omar Othman <omar.othman@live.com>"


import os
import sys

from matplotlib import pyplot as plt
import numpy as np

from .util import assert_banknote_threshold, load_base64, predict, TEST_DIR


FLAG_SEPARATE = "-s"
FLAG_THRESHOLD_CURVE = "-t"

DEFAULT_TITLE = "-"
# the total number of classes in the model, not the ones included in the
# analysis only.
NUM_CLASSES = 6
TITLE_DELTA = "Delta values for a range of thresholds for %s"
TITLE_THRESHOLD_CURVE = "TP-FP curve for %s"

STEP_SIZE = 0.01

BACKGROUND = "bg"


def main():
    # make sure that there is no threshold
    assert_banknote_threshold(0)

    # sanity check for args
    if len(sys.argv) < 3:
        _print_help()
        sys.exit(1)

    # get args
    option_threshold_curve = False
    title = sys.argv[1]
    class_names = sys.argv[2:]
    if len(class_names) > 1 and class_names[-1] == FLAG_THRESHOLD_CURVE:
        option_threshold_curve = True
        class_names = class_names[:-1]

    background = load_base64(
        BACKGROUND,
        os.path.join(TEST_DIR, BACKGROUND),
        desc=f"[{BACKGROUND}] loading"
    )

    # run grid search
    if title == FLAG_SEPARATE:
        for class_name in class_names:
            grid_search("-", [class_name], background, option_threshold_curve)
    else:
        grid_search(title, class_names, background, option_threshold_curve)

    # show plots
    plt.show()


def grid_search(title, class_names, background_images, option_threshold_curve):
    """Finds the best threshold for the given class names and background images.
    """
    # prepare title
    if title == DEFAULT_TITLE:
        title = f"class{'es' if len(class_names) > 1 else ''} {', '.join(class_names)}"

    # calculate true positive confidences
    true_positive_confidences = []
    for class_name in class_names:
        images = load_base64(
            class_name,
            os.path.join(TEST_DIR, class_name),
            desc=f"[{class_name}] loading"
        )
        true_positive_confidences.extend(_calculate_tp_confidences(
            images,
            class_name
        ))

    # calculate false positive confidences
    false_positive_confidences = _calculate_fp_confidences(
        background_images,
        class_names
    )

    print("Grid searching...")
    tvals = np.linspace(0, 1, int(1 / STEP_SIZE) + 1)
    # discard thresholds below the 1/num_classes
    tvals = [t for t in tvals if t >= 1 / NUM_CLASSES]
    deltas, tp_percentages, fp_percentages = calculate_deltas(
        tvals,
        true_positive_confidences,
        false_positive_confidences
    )
    best_t_index = np.argmin(deltas)
    best_t = tvals[best_t_index]
    print(f"Best threshold: {best_t}")

    plt.figure()
    plt.plot(tvals, deltas)
    plt.xlim([tvals[0], tvals[-1]])
    plt.xlabel("Threshold")
    plt.ylabel("$\delta$")
    plt.title(TITLE_DELTA % title)
    plt.grid()

    if option_threshold_curve:
        plt.figure()
        plt.plot(
            tp_percentages,
            fp_percentages,
            label="Threshold values"
        )
        plt.scatter([1], [0], color="orange", label="Optimal point")
        nearest_point = (
            tp_percentages[best_t_index],
            fp_percentages[best_t_index]
        )
        plt.plot(
            [1, nearest_point[0]],
            [0, nearest_point[1]],
            color="gray",
            linestyle=":",
            label="Nearest point"
        )
        plt.text(nearest_point[0], nearest_point[1], f"$t$ = {best_t:.2f}")
        plt.xlim([-0.1, 1.1])
        plt.ylim([-0.1, 1.1])
        plt.xlabel("True positive percentage")
        plt.ylabel("False positive percentage")
        plt.title(TITLE_THRESHOLD_CURVE % title)
        plt.legend()
        plt.grid()


def calculate_deltas(tvals, tp_confidences, fp_confidences):
    """Calculates deltas for all threshold values `tvals` and returns three
    lists: deltas, true positive percentages, false positive percentages.
    """
    deltas = []
    tp_percentages = []
    fp_percentages = []
    for tval in tvals:
        dval, tp_pct, fp_pct = delta(
            tval,
            tp_confidences,
            fp_confidences
        )
        deltas.append(dval)
        tp_percentages.append(tp_pct)
        fp_percentages.append(fp_pct)
    return deltas, tp_percentages, fp_percentages


def delta(tval, tp_confidences, fp_confidences):
    """Calculates delta (as described in the thesis) for the given threshold
    value, and the percentages of true positives and false positives at that
    threshold.
    """
    tp_percentage = \
        np.sum([1 for x in tp_confidences if x > tval]) / len(tp_confidences)
    if fp_confidences:
        fp_percentage = np.sum([1 for x in fp_confidences if x > tval]) / \
            len(fp_confidences)
    else:
        fp_percentage = 0
    delta_value = tp_percentage ** 2 - 2 * tp_percentage + fp_percentage ** 2
    return delta_value, tp_percentage, fp_percentage


def _calculate_tp_confidences(images, test_class):
    """Returns confidences of true positives.
    """
    confidences = []
    for (response_json, class_name) in predict(images, desc=f"[{test_class}] inference"):
        if response_json["status"] != "ok":
            raise Exception(f"Not OK response in {class_name}")
        if class_name == test_class and response_json["response"] == class_name:
            confidences.append(response_json["confidence"])
    return confidences


def _calculate_fp_confidences(images, test_classes):
    """Returns confidences of true negatives.
    """
    confidences = []
    for (response_json, class_name) in predict(images, desc=f"[{BACKGROUND}] inference"):
        if response_json["status"] != "ok":
            raise Exception(f"Not OK response in {class_name}")
        if response_json["response"] in test_classes:
            confidences.append(response_json["confidence"])
    return confidences


def _print_help():
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
    print(f"[{FLAG_THRESHOLD_CURVE}]:           additionally plot threshold curve (correct vs. "
          "incorrect curve).")


if __name__ == "__main__":
    main()
