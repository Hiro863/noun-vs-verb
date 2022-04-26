import json
import logging
import os
import re
from typing import Union, Callable
from pathlib import Path
from mne.io import read_raw_ctf, Raw


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"

root = get_project_root()
print(root)

logging.basicConfig(level=logging.DEBUG, filename=root / "meg-mvpa/data/logs/debug.log", format=fmt)


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


def read_mous_subject(subject_dir: Path):
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

    raw = read_raw_ctf(str(ctf_dir), preload=True).crop(0, 30)  # todo: debug purpose, remove crop

    logging.debug(f"File {ctf_dir} successfully read")
    return raw


def get_mous_meg_channels(channels: list):
    # later comment
    picks = []
    for channel in channels:
        if re.match(r"M.*4304", channel):  # Select MEG gradiometers
            picks.append(channel)
    return picks