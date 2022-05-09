import logging
import re
import os
import sys
from pathlib import Path
from typing import List
import numpy as np
from mne import read_epochs
from utils.file_access import write_json

fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"


logging.basicConfig(level=logging.DEBUG,
                    format=fmt,
                    handlers=[logging.StreamHandler(sys.stdout)])

########################################################################################################################
# DATASET GENERATION                                                                                                   #
########################################################################################################################


def _get_events_paths(epoch_dir: Path, reject_list: List[str]):

    fname = "events.npy"
    events_path_list = []

    for subject_dir in os.listdir(epoch_dir):   # e.g. "sub-V1001"

        # Skip rejected subjects
        if subject_dir in reject_list:
            continue

        subject_path = epoch_dir / subject_dir  # "epochs/sub-V1001"

        if re.match(r"^sub-[AV]\d+$", str(subject_dir)):  # there are hidden files in the directory
            events_path = subject_path / fname
            events_path_list.append(events_path)
    return events_path_list


def _get_stc_paths(epoch_dir: Path, area_name: str, reject_list: List[str]):

    stc_path_list = []

    for subject_dir in os.listdir(epoch_dir):   # e.g. "sub-V1001"

        # Skip rejected subjects
        if subject_dir in reject_list:
            continue

        subject_path = epoch_dir / subject_dir  # "epochs/sub-V1001"

        if re.match(r"^sub-[AV]\d+$", str(subject_dir)):  # there are hidden files in the directory

            # Look for matching cortical area
            stc_dir = subject_path / "stc"                      # e.g. "epochs/sub-V1001/stc"
            for area_file in os.listdir(stc_dir):               # e.g. "epochs/sub-V1001/stc/..."
                if area_file.startswith(area_name):             # e.g. "fusiform_1-h.npy"
                    stc_path_list.append(stc_dir / area_file)   # e.g. "epochs/sub-V1001/stc/fusiform_1-h.npy"

    return stc_path_list


def _get_epoch_paths(epoch_dir: Path, reject_list: List[str]):

    epoch_path_list = []

    for subject_dir in os.listdir(epoch_dir):  # e.g. "sub-V1001"

        # Skip rejected subjects
        if subject_dir in reject_list:
            continue

        subject_path = epoch_dir / subject_dir  # "epochs/sub-V1001"

        if re.match(r"^sub-[AV]\d+$", str(subject_dir)):  # there are hidden files in the directory

            # Look for matching cortical area
            for file in os.listdir(subject_path):                 # e.g. "epochs/sub-V1001/..."
                if re.match(r".*epo.fif$", file):                 # e.g. "sub-V1001-epo.fif"
                    epoch_path_list.append(subject_path / file)   # e.g. "epochs/sub-V1001/sub-V1001-epo.fif"

    return epoch_path_list


def _generate_x(dst_dir: Path, paths: List[Path], sensor=False):
    x_list = []
    for path in paths:

        # Read x
        if sensor:
            epochs = read_epochs(path)
            x = epochs.get_data()
        else:
            x = np.load(str(path))

        x_list.append(x)

    x = np.vstack(x_list)  # todo: won’t work if shape is different
    fname = "x.npy"
    np.save(str(dst_dir / fname), x)


def _generate_x_mmap(dst_dir: Path, paths: List[Path], sensor=False):

    # Get the size of final array
    x_shape = _get_array_size(paths, sensor=sensor)
    fname = "x.dat"
    x_map = np.memmap(str(dst_dir / fname), dtype="float64", mode="w+", shape=x_shape)

    # Use memory map for x
    curr_idx = 0
    for idx, path in enumerate(paths):

        # Read x
        if sensor:
            epochs = read_epochs(path)
            x = epochs.get_data()
        else:
            x = np.load(str(path))

        x_map[curr_idx: curr_idx + x.shape[0]] = x
        curr_idx += x.shape[0]
        x_map.flush()

    shape = {"shape": x_shape}
    fname = "x_shape.json"
    write_json(dst_dir, file_name=fname, data=shape)


def _generate_y(dst_dir: Path, events_paths: List[Path]):
    y_list = []
    for event_path in events_paths:
        events = np.load(str(event_path))
        y = events[:, 2]
        y_list.append(y)

    y = np.hstack(y_list)
    fname = "y.npy"
    np.save(str(dst_dir / fname), y)


def _get_array_size(paths, sensor=False):

    dim_0 = 0
    dim_rest = None
    for path in paths:

        # Read single x data
        if sensor:
            epochs = read_epochs(path)
            x = epochs.get_data()
            shape = np.array(x.shape)
            del x
        else:
            with open(str(path), "rb") as f:
                shape, fortran, dtype = np.lib.format.read_array_header_1_0(f)
                shape = np.array(shape)
        dim_0 += shape[0]
        if dim_rest is None:
            dim_rest = shape[1:]

    x_shape = [dim_0]
    x_shape.extend(dim_rest)

    return tuple(x_shape)


def _get_reject_list(reject_path: Path):

    with open(reject_path, "r") as file:
        reject_text = file.read()

    return reject_text.splitlines()


def generate_dataset(epoch_dir: Path, dst_dir: Path, area_name: str, memmap=True, reject=None) -> None:
    """
    :param epoch_dir:
    :param dst_dir:
    :param area_name:
    :param memmap:
    :param reject:
    :return:
    """
    logging.debug(f"Generating dataset for {area_name}")

    # Get list of subjects to ignore
    if reject is not None:
        reject_list = _get_reject_list(reject)
    else:
        reject_list = []

    # List of path to event.npy
    events_paths = _get_events_paths(epoch_dir, reject_list)

    # Sensor space dataset
    if area_name == "sensor":
        epoch_paths = _get_epoch_paths(epoch_dir, reject_list)

        if memmap:
            _generate_x_mmap(dst_dir, epoch_paths, sensor=True)
        else:
            _generate_x(dst_dir, epoch_paths, sensor=True)

    # Source space dataset
    else:
        stc_paths = _get_stc_paths(epoch_dir, area_name, reject_list)

        # Generate x array
        if memmap:
            _generate_x_mmap(dst_dir, stc_paths)
        else:
            _generate_x(dst_dir, stc_paths)

    # Generate y array
    _generate_y(dst_dir, events_paths)
