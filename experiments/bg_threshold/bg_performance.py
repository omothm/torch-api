"""Banknote background threshold performance

Plots the predictions of the model to analyze the performance of background
thresholding.

The threshold is defined inside the API itself, in the api.py file. To test
a different threshold, change it in the api.py file and then run this script.
After changing the threshold you may want to change the title of the resulting
plot by changing the PLOT_TITLE constant below.

This script does not perform any thresholding on its own--it just prints out
the prediction results. Thresholding logic is completely embedded in the API
itself (specifically, in the KerasCnnImageService class).

This script does not accept args.
"""

__author__ = "Omar Othman <omar.othman@live.com>"


import os

import matplotlib.pyplot as plt
import numpy as np

from torchapi import get_config

from .util import load_base64, predict


PLOT_TITLE = "Banknote model accuracy, %s"
TEST_DIR = os.path.join(os.path.dirname(__file__), "data", "base64")


def main():
    # get all directories (classes) in the test directory
    (dirpath, dirnames, _) = next(
        os.walk(os.path.join(os.path.dirname(__file__), TEST_DIR)))

    # initiate prediction counters
    correct_preds = [0 for _ in enumerate(dirnames)]
    incorrect_preds = [0 for _ in enumerate(dirnames)]
    bg_preds = [0 for _ in enumerate(dirnames)]
    error_preds = [0 for _ in enumerate(dirnames)]
    fp_percentage = None
    for i, dirname in enumerate(dirnames):
        print(f"[Class {dirname}]")
        images = load_base64(dirname, os.path.join(dirpath, dirname))
        for (response_json, _) in predict(images):
            if response_json["status"] == "error":
                error_preds[i] = error_preds[i] + 1
            elif response_json["status"] == "ok":
                if response_json["response"] == 'bg':
                    bg_preds[i] = bg_preds[i] + 1
                elif response_json["response"] == dirname:
                    correct_preds[i] = correct_preds[i] + 1
                else:
                    incorrect_preds[i] = incorrect_preds[i] + 1
            else:
                raise ValueError("Unknown status")

        # normalize the prediction between 0 and 100
        correct_preds[i] = correct_preds[i] / len(images) * 100
        incorrect_preds[i] = incorrect_preds[i] / len(images) * 100
        bg_preds[i] = bg_preds[i] / len(images) * 100
        error_preds[i] = error_preds[i] / len(images) * 100
        if dirname == 'bg':
            fp_percentage = 100 - bg_preds[i]

    print("\nStatistics:")
    # filter zero out because it belongs to "bg"
    tp_percentage = np.average([x for x in correct_preds if x != 0])
    print(f"True positive: {tp_percentage:.2f}%")
    print(f"False positive: {fp_percentage:.2f}%")

    print("\nPlotting results...")
    x = np.arange(len(dirnames))
    width = 0.15
    cats = [correct_preds, incorrect_preds, bg_preds, error_preds]
    labels = ["Correct", "Incorrect", "Background", "Error"]
    for i, cat in enumerate(cats):
        plt.bar(x + ((1 - len(cats)) / 2 + i) *
                width, cat, width, label=labels[i])
    plt.xlabel('Class')
    plt.ylabel('Percentage')
    plt.grid(which='major', axis='y')
    plt.ylim([0, 100])
    thresh = get_config("banknote")["background_threshold"]
    plt.title(PLOT_TITLE %
              f"{'multi-' if isinstance(thresh, list) else 'single '}thresh = {thresh}")
    plt.xticks(x, dirnames)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
