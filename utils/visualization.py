import numpy as np
import seaborn as sns

from matplotlib import pyplot as plt


def plot_single_area(results, stats, area, figsize=(15, 5), fill_alpha=.3,
                     x_tick=100, scale=10, subdivide=10, loc=.4, mode="percentage", p_thresh=.05):

    # R like color
    colors = sns.color_palette("husl", 2)  # two colours, svc vs dummy

    # Split data and meta data
    meta, data = results["meta"], results["data"]

    # Convert to ms
    tmin = meta["classification-tmin"] * 1e3
    tmax = meta["classification-tmax"] * 1e3

    # Get time step size
    step = 1e3 / meta["sfreq"]
    times = np.arange(tmin, tmax, step)

    fig, ax = plt.subplots(figsize=figsize)

    # Mode percentage or score
    if mode == "percentage":
        rescale = 100
        measure = "(%)"
    else:
        rescale = 1
        measure = "(out of 1)"

    ax.grid()
    ax.axhline(.5 * rescale, color="k", linestyle=":")  # chance level is .5 / 50%

    # Plot scores for the classifier
    ax.set_xticks(np.arange(tmin, tmax, x_tick))
    ax.plot(times, data["scores"].mean(axis=0) * rescale, label="LinearSVC", color=colors[0])
    ax.fill_between(times, data["lowers"] * rescale, data["uppers"] * rescale, color=colors[0], alpha=fill_alpha)

    # Plot scores for the dummy classifier
    ax.set_xticks(np.arange(tmin, tmax, 100))
    ax.plot(times, data["dummy-scores"].mean(axis=0) * rescale, label="Dummy", color=colors[1])
    ax.fill_between(times, data["dummy-lowers"] * rescale, data["dummy-uppers"] * rescale,
                    color=colors[1], alpha=fill_alpha)

    ax.legend(title="Classifiers", loc="upper right")

    # Annotate
    condition_name = {"nv": "Noun vs. Verb"}
    ax.set_title(f"Classification accuracy,  {area}, Condition={condition_name[meta['conditions']]}")
    ax.set_xlabel(f"Time (ms)")
    ax.set_ylabel(f"Accuracy {measure}")

    # Add significance
    _add_significance(ax, stats, times, loc=loc * rescale, scale=scale, subdivide=subdivide, p_thresh=p_thresh)
    return fig


def _add_significance(ax, stats, times, loc, scale, subdivide=-1, p_thresh=.05):

    # Results of cluster test
    _, clusters, p_values, _ = stats

    colors = sns.color_palette("husl", len(clusters))  # one color per cluster

    # Subdivide individual steps for smooth plot
    if subdivide > 0:
        step = times[1] - times[0]  # current step size
        times = np.arange(times[0], times[-1], step / subdivide)
    else:
        subdivide = 1

    # Hard code relative place to avoid overlap
    buffer_x = 10
    buffer_y = -.5

    # Plot
    for i, (cluster, p) in enumerate(zip(clusters, p_values)):
        if p < p_thresh:

            # Number of points
            n_steps = len(cluster[0]) * subdivide

            # Make indices for new `times`
            idx = np.arange(cluster[0][0] * subdivide, (cluster[0][-1] + 1) * subdivide)

            # Plot, scale based on the p-values
            ax.scatter(times[idx], [loc] * n_steps, s=[1 / p * scale] * n_steps, color=colors[i])

            # Write p-values next to the points
            ax.text(times[idx][-1] + buffer_x, loc + buffer_y, f"p={np.round(p, decimals=2)}")

