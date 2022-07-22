import numpy as np
import seaborn as sns

from mne import read_source_spaces, SourceEstimate
from matplotlib import pyplot as plt
from matplotlib import gridspec

from src.utils.file_access import read_labels


# finish this file


def _get_times(meta):

    # Convert to ms
    tmin = meta["classification-tmin"] * 1e3
    tmax = meta["classification-tmax"] * 1e3

    # Get time step size
    step = 1e3 / meta["sfreq"]
    times = np.arange(tmin, tmax, step)
    return tmin, tmax, step, times


def plot_single_area(results, stats, area, figsize=(15, 5), fill_alpha=.3,
                     plot_dummy=False, x_tick=100, subdivide=10, loc=.4, mode="percentage", p_thresh=.05):

    # R like color
    colors = sns.color_palette("husl", 2)  # two colours, svc vs dummy

    # Split data and meta data
    meta, data = results["meta"], results["data"]

    # Get times
    tmin, tmax, step, times = _get_times(meta)

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

    if plot_dummy:
        # Plot scores for the dummy classifier
        ax.set_xticks(np.arange(tmin, tmax, 100))
        ax.plot(times, data["dummy-scores"].mean(axis=0) * rescale, color=colors[1])
        ax.fill_between(times, data["dummy-lowers"] * rescale, data["dummy-uppers"] * rescale,
                        color=colors[1], alpha=fill_alpha)

        ax.legend(title="Classifiers", loc="upper right")

    # Annotate
    condition_name = {"nv": "Noun vs. Verb"}
    ax.set_title(f"Classification accuracy,  {area}, Condition={condition_name[meta['conditions']]}")
    ax.set_xlabel(f"Time (ms)")
    ax.set_ylabel(f"Accuracy {measure}")

    # Add significance
    _add_significance(ax, stats, np.arange(tmin, tmax + step, step), loc=loc * rescale,
                      subdivide=subdivide, p_thresh=p_thresh)
    return fig


def _add_significance(ax, stats, times, loc, subdivide=-1, p_thresh=.05):

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
    buffer_x = -10
    buffer_y = -2

    # Plot
    for i, (cluster, p) in enumerate(zip(clusters, p_values)):
        if p < p_thresh:

            # Number of points
            n_steps = len(cluster[0]) * subdivide

            # Make indices for new `times`
            idx = np.arange(cluster[0][0] * subdivide, (cluster[0][-1] + 1) * subdivide)

            # Plot, scale based on the p-values
            ax.scatter(times[idx], [loc] * n_steps, color=colors[i])

            # Write p-values next to the points
            ax.text((times[idx][0] + times[idx][-1]) / 2 + buffer_x, loc + buffer_y, f"p={np.round(p, decimals=5)}")


def plot_multiple_areas(result_list, stats, figsize=(15, 5), alpha=.9,
                        hspace=-.9, y_max=.8, colors=None, mode="percentage"):
    n_areas = len(result_list)

    fig = plt.figure(figsize=figsize)

    if not colors:
        colors = sns.color_palette("husl", n_areas)

    # Make them overlap
    gs = (gridspec.GridSpec(n_areas, 1))
    gs.update(hspace=hspace)

    # Mode percentage or score
    if mode == "percentage":
        rescale = 100
        measure = "(%)"
    else:
        rescale = 1
        measure = "(out of 1)"

    axes = []
    for i, results in enumerate(result_list):
        axes.append(fig.add_subplot(gs[i: i + 1, 0:]))

        tmin, tmax, step, times = _get_times(results["meta"])

        # Plot
        scores = results["data"]["scores"].mean(axis=0)
        axes[i].plot(times, scores * rescale, color="k", linewidth=.2)
        axes[i].fill_between(times, [.5 * rescale] * times.size, scores * rescale, color=colors[i], alpha=alpha)

        # Y-lim
        axes[i].set_ylim(.5 * rescale, y_max * rescale)

        # Transparent background
        rect = axes[i].patch
        rect.set_alpha(0)

        if i < n_areas - 1:

            # Remove ticks
            axes[i].set_xticks([])
            axes[i].set_yticks([])

            # Remove borders
            spines = ["top", "right", "left", "bottom"]
            for s in spines:
                axes[i].spines[s].set_visible(False)
        else:
            # Set ticks
            axes[i].set_xticks(np.arange(tmin, tmax, 100))
            axes[i].set_yticks(np.arange(.5 * rescale, 1.2 * rescale, .1 * rescale))

            spines = ["top", "right", "bottom"]
            for s in spines:
                axes[i].spines[s].set_visible(False)

            # Set axis length
            axes[i].spines["left"].set_bounds(.5 * rescale, 1. * rescale)
            axes[i].get_yticklabels()[-1].set_visible(False)
            axes[i].get_yticklines()[-1].set_visible(False)

    # Annotate
    condition_name = {"nv": "Noun vs. Verb"}
    conditions = result_list[0]["meta"]["conditions"]
    axes[0].set_title(f"Classification accuracy, Condition={conditions}")
    axes[-1].set_xlabel(f"Time (ms)")
    axes[-1].set_ylabel(f"Accuracy {measure}")
    return fig


def _make_source_estimate(meta, data, src_path, parc, hemi, subjects_dir, center_chance=True, percentage=True):
    src = read_source_spaces(src_path)
    labels = read_labels(parc=parc, subject="fsvaverage", hemi=hemi, subjects_dir=subjects_dir)

    n_times = data.shape[1]
    accuracy = np.zeros((src[0]["np"] * 2, n_times))  # 2 (hemispheres) x number sources, time steps

    center = .5 if center_chance else 0.
    rescale = 100 if percentage else 1

    for i, label in enumerate(labels):
        if label.name.startswith("unknown"):
            continue

        vertices = label.get_vertices_used(np.arange(src[0]["np"]))
        accuracy[vertices] = (data.mean(axis=0)[:, i] - center) * rescale

    tstep = 1e3 / meta["sfreq"]
    stc = SourceEstimate(accuracy, tmin=0, tstep=tstep, vertices=[np.arange(src[0]["np"]), np.arange(src[0]["np"])],
                         subject="fsaverage")
    return stc


def plot_spatiotemporal_accuracy(meta, data, src_path, parc, hemi, subjects_dir, center_chance=True, percentage=True):
    stc = _make_source_estimate(meta=meta, data=data, src_path=src_path, parc=parc, hemi=hemi,
                                subjects_dir=subjects_dir, center_chance=center_chance, percentage=percentage)


def plot_pie(df, key, labels, title, colors, figsize=(5, 5)):
    fig, ax = plt.subplots(figsize=figsize)

    ax.pie(df.groupby([key]).size(), labels=labels, autopct="%1.0f%%", colors=colors)

    # Hollow out the middle
    ax.set_title(title)

    circle = plt.Circle((0, 0), 0.7, color="white")
    p = plt.gcf()
    p.gca().add_artist(circle)
