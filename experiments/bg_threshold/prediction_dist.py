"""Plots the distribution of predictions for a specific class.

This script requires args. See print_help.
"""

__author__ = "Omar Othman <omar.othman@live.com>"


import os
import sys

import matplotlib.pyplot as plt

from .util import load_base64, predict, TEST_DIR


def main():
    # get args
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    class_name = sys.argv[1]

    print("Loading images...")
    images = load_base64(class_name, os.path.join(TEST_DIR, class_name))
    num_samples = len(images)

    print("Predicting...")
    confidences = {}
    for (response, _) in predict(images):
        if response["status"] != "ok":
            raise ValueError("Error in prediction")
        prediction = response["response"]
        if prediction not in confidences:
            confidences[prediction] = []
        confidences[prediction].append(response["confidence"])

    # plot
    _, ax1 = plt.subplots()
    classes = list(confidences)
    xticks = range(1, len(classes) + 1)
    confidences_list = list(map(lambda x: confidences[x], classes))
    # first axis
    color = "lightgray"
    ax1.set_ylabel("Percentage")
    ax1.bar(
        xticks,
        [len(x) / num_samples for x in confidences_list],
        color=color
    )
    ax1.tick_params(axis="y")
    # second axis
    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Confidence", color=color)
    ax2.boxplot(
        confidences_list,
        boxprops={"color": color},
        whiskerprops={"color": color},
        capprops={"color": color}
    )
    ax2.tick_params(axis="y", labelcolor=color)
    # common settings
    ax1.set_title(f"Predictions distribution for class {class_name}")
    ax1.set_xlabel("Predicted class")
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(classes)
    ax1.set_axisbelow(True)
    ax1.grid()
    plt.show()


def print_help():
    filename = os.path.basename(sys.argv[0])
    print("Synopsis:")
    print(f"    {filename} <class>")
    print("<class>: class name (and directory) to plot distributions for.")


if __name__ == "__main__":
    main()
