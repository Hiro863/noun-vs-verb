from matplotlib import pyplot as plt
import numpy as np


def plot_sliding(mean, lower, upper, n_classes):
    fig, ax = plt.subplots()
    time = np.arange(0, mean.size)
    ax.plot(mean)
    ax.fill_between(time, lower, upper, alpha=.2)

    ax.axhline(.5, color="k", linestyle="--", label="chance level")
    fig.savefig("plot.png")


def plot_generalization():
    # todo
    pass
















