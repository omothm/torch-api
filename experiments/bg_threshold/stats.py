import os
import json
import numpy as np
import scipy.stats as ss
from matplotlib import pyplot as plt


def main():
    with open(os.path.join(os.path.dirname(__file__), "output/correct.json"), "r") as in_file:
        correct = json.load(in_file)
    correct_std = np.std(correct)
    correct_mean = np.mean(correct)
    with open(os.path.join(os.path.dirname(__file__), "output/incorrect.json"), "r") as in_file:
        incorrect = json.load(in_file)
    incorrect_std = np.std(incorrect)
    incorrect_mean = np.mean(incorrect)

    # x_range = np.linspace(0, 1, num=100)
    # correct_pdf = ss.norm(correct_mean, correct_std).pdf(x_range)
    # correct_cdf = 1 - ss.norm(correct_mean, correct_std).cdf(x_range)
    # incorrect_pdf = ss.norm(incorrect_mean, incorrect_std).pdf(x_range)
    # incorrect_cdf = ss.norm(incorrect_mean, incorrect_std).cdf(x_range)
    # ymax = np.max([correct_pdf, incorrect_pdf]) + 0.1
    # plt.plot([correct_mean, correct_mean], [0, ymax], color="gray")
    # plt.plot([incorrect_mean, incorrect_mean], [0, ymax], color="gray")
    # plt.plot(x_range, correct_pdf, label="Correct PDF")
    # plt.plot(x_range, incorrect_pdf, label="Incorrect PDF")
    # plt.plot(x_range, correct_cdf, label="Correct mirrored CDF")
    # plt.plot(x_range, incorrect_cdf, label="Incorrect CDF")
    # plt.xlim([0, 1])
    # plt.ylim([0, ymax])
    # plt.grid()
    # plt.legend()
    # plt.show()
    
    # plt.boxplot(correct, widths=0.5)
    # plt.minorticks_on()
    # plt.plot([0, 2], [np.percentile(correct, 25), np.percentile(correct, 25)])
    # plt.plot([0, 2], [np.percentile(correct, 75), np.percentile(correct, 75)])
    # plt.ylim(0, 1)
    # plt.show()
    
    print("Correct:")
    print("Mean:", correct_mean)
    print("25th:", np.percentile(correct, 25))
    print("50th:", np.percentile(correct, 50))
    print("75th:", np.percentile(correct, 75))
    print("Incorrect:")
    print("Mean:", incorrect_mean)
    print("25th:", np.percentile(incorrect, 25))
    print("50th:", np.percentile(incorrect, 50))
    print("75th:", np.percentile(incorrect, 75))


if __name__ == "__main__":
    main()
