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

This script accepts no args.
"""

__author__ = "Omar Othman <omar.othman@live.com>"


import json
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

import numpy as np

from torchapi.api import handle


# PLOT_TITLE = "Banknote model accuracy, single thresh = 0.65"
PLOT_TITLE = "Banknote model accuracy, no thresh"
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

    print("\nPredicting classes...")
    for i, dirname in enumerate(dirnames):

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
        correct_preds[i] = correct_preds[i] / len(filenames) * 100
        incorrect_preds[i] = incorrect_preds[i] / len(filenames) * 100
        bg_preds[i] = bg_preds[i] / len(filenames) * 100
        error_preds[i] = error_preds[i] / len(filenames) * 100

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
    plt.title(PLOT_TITLE)
    plt.xticks(x, dirnames)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
