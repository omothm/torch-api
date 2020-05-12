import numpy as np
from matplotlib import pyplot as plt


def main():
    x_vals = np.linspace(0, 1, int(1/0.1))
    y_vals = (2 ** (x_vals * 10)) / 1300
    for x_val, y_val in zip(x_vals[1:], y_vals[1:]):
        plt.plot([1,x_val], [0,y_val],color="gray",linestyle=":")
    plt.plot(x_vals, y_vals, marker="o", label="Various threshold values")
    plt.scatter([1],[0], marker="o", s=80, color="orange", label="Optimal point")
    plt.plot([1,x_vals[0]], [0,y_vals[0]],color="gray",linestyle=":",label="Distances")
    plt.xlabel("Correct")
    plt.ylabel("Incorrect")
    plt.title("Example correct–incorrect curve")
    plt.ylim()
    plt.grid()
    plt.legend()
    plt.show()



if __name__ == "__main__":
    main()
