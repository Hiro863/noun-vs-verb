import json
import logging
import os
import pickle
import sys
import re

import mne
import numpy as np

from typing import Union, Callable
from collections import OrderedDict
from pathlib import Path

from mne.io import read_raw_ctf, Raw
from mne import read_labels_from_annot, morph_labels

# todo: tidy this file


def get_project_root() -> Path:
    return Path(__file__).parent.parent


fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"

logging.basicConfig(level=logging.DEBUG,
                    format=fmt,
                    handlers=[logging.StreamHandler(sys.stdout)])


def read_raw(src_dir: Path, dst_dir: Path, file_reader: Callable) -> Union[None, Raw]:

    logging.debug(f"Reading raw file")

    raw = None

    try:
        raw = file_reader(src_dir)
    except FileNotFoundError as e:
        logging.exception(f"File {src_dir} was not found. Skipping this subject. {e.strerror}")

        # Remove dst_dir so as not to propagate errors
        try:
            if dst_dir.exists():
                os.remove(dst_dir)
        except OSError as e:
            logging.exception(f"Error: {e.strerror}")

    return raw


def load_json(json_path: Path):
    with open(json_path) as file:
        data = json.load(file)
    return data


def read_json(dir_path: Path, file_name: str):
    # later: comment

    json_dir = dir_path / file_name

    with open(json_dir) as file:
        data = json.load(file)

    return data


def write_json(dir_path: Path, file_name: str, data):

    json_file = json.dumps(data, indent=4, ensure_ascii=False)

    with open(dir_path / file_name, "w") as file:
        file.write(json_file)


########################################################################################################################
# File processing specific to MOUS dataset                                                                             #
########################################################################################################################


def get_mous_raw_paths(data_dir: Path) -> list:  # later list of tuples

    logging.debug(f"Reading MOUS dataset paths from {data_dir}")

    path_list = []
    for file in os.listdir(data_dir):

        if re.match(r"^sub-[AV]\d+$", file):  # e.g. sub-V1001

            logging.debug(f"File {file} matched")

            subject_path = data_dir / file

            if os.path.isdir(subject_path):
                logging.debug(f"adding {subject_path} to the list")
                path_list.append((subject_path, file))  # Path and subject name
            else:
                msg = f"Expected a directory but got a file for the path {subject_path}."
                logging.exception(msg)
                raise TypeError(msg)

    return path_list


def read_mous_subject(subject_dir: Path, preload=True):
    # later comment
    logging.debug(f"Parsing {subject_dir}")

    meg_dir = subject_dir / "meg"
    ctf_dir = None

    for file_name in os.listdir(meg_dir):
        logging.debug(f"Parsing {meg_dir} {file_name}")

        if re.match(r"^sub-[AV]\d+_task-visual_meg\.ds$", file_name):
            ctf_dir = meg_dir / file_name

    if ctf_dir is None:
        msg = f"The CTF directory in {meg_dir} was not found."
        logging.exception(msg)
        raise FileNotFoundError(msg)

    raw = read_raw_ctf(str(ctf_dir), preload=preload)

    logging.debug(f"File {ctf_dir} successfully read")
    return raw


def get_mous_meg_channels(channels: list):
    # later comment
    picks = []
    for channel in channels:
        if re.match(r"M.*4304", channel):  # Select MEG gradiometers
            picks.append(channel)
    return picks


def read_raw_format(path, format):

    if format == "fif":
        raw = mne.io.read_raw(path)
        return raw
    elif format == "ctf":
        raw = read_raw_ctf(path)
        return raw


def _get_file_names(results_dir: Path):

    name_to_file = {}
    for file in os.listdir(results_dir):
        if re.match(r"^\..*", file):  # skip hidden files, e.g. .DS_Store...
            continue

        name = re.sub(r"\.pickle", "", file)
        name_to_file[name] = file

    name_to_file = OrderedDict(sorted(name_to_file.items()))
    return name_to_file


def read_dict(path):
    with open(path, "rb") as handle:
        data = pickle.load(handle)
    return data


def read_labels(parc, subject, hemi, subjects_dir):
    labels = read_labels_from_annot("fsaverage", parc=parc, hemi=hemi, subjects_dir=subjects_dir)

    if subject is not "fsaverage":
        labels = morph_labels(labels, subject_to=subject, subject_from="fsaverage",
                              subjects_dir=subjects_dir, surf_name="white")
    return labels


def read_scores(results_dir: Path):
    name_to_file = _get_file_names(results_dir)  # ordered dict to load in correct order

    meta, data = None, []
    for name, file in name_to_file.items():

        with open(results_dir / file, "rb") as handle:
            results = pickle.load(handle)

        if not meta:  # metadata is the same for all
            mata = results["meta"]

        data.append(results["data"]["scores"])

    data = np.stack(data, axis=2)
    return meta, data


def read_data(data_dir: Path):

    json_path = data_dir / "x_shape.json"
    if json_path.exists():

        x_path = data_dir / "x.dat"

        if x_path.exists():
            json_data = load_json(data_dir / "x_shape.json")
            print(json_data)
            print(x_path)
            x = np.memmap(str(x_path), dtype="float64", mode="r+", shape=tuple(json_data["shape"]))
            return x
        else:
            raise FileNotFoundError(f"'x.dat' file was not found in {data_dir}")
    else:
        x_path = data_dir / "x.npy"

        if x_path.exists():
            x = np.load(x_path)
            return x
        else:
            raise FileNotFoundError(f"Neither JSON file nor 'x.npy' file was found in {data_dir}")


