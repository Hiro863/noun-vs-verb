import os
import pickle
import sys
import numpy as np
from utils.file_access import read_json
from pathlib import Path
from mne import read_labels_from_annot
from events.conditions import convert_to_nv


def convert(params):
    x = np.load(params["x-path"])
    y = np.load(params["y-path"])
    idx_to_name


if __name__ == "__main__":

    # Get input from the bash script
    area_id = int(sys.argv[1])
    n_cores = int(sys.argv[2])
    param_dir = Path(sys.argv[3])

    # Get the parameters
    params = read_json(param_dir, "conditions-params.json")

    # Set up directories
    root = Path(params["directories"]["root"])
    dataset_dir = root / "dataset-dir"

    with open(params["directories"]["idx-to-name"], "rb") as handle:
        idx_to_name = pickle.load(handle)
    subjects_dir = params["directories"]["subjects-dir"]
    labels = read_labels_from_annot("fsaverage", params["parcellation"], params["hemi"], subjects_dir=subjects_dir)
    name = idx_to_name[area_id]