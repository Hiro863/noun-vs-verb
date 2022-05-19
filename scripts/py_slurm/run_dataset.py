import logging
import os
import pickle
import sys
from utils.file_access import read_json
from pathlib import Path
from mne import read_labels_from_annot
from processing.dataset import generate_dataset
from utils.logger import get_logger



if __name__ == "__main__":

    # Get input from the bash script
    area_id = int(sys.argv[1])
    n_cores = int(sys.argv[2])
    param_dir = Path(sys.argv[3])
    logger = get_logger("/data/home/hiroyoshi/high-res/logs", f"dateset-{area_id}")


    # Get the parameters
    params = read_json(param_dir, "dataset-params.json")

    # Set up directories
    root = Path(params["directories"]["root"])
    epoch_dir = root / "epochs-dir"
    dataset_dir = root / "dataset-dir"  # todo: only debug
    if not dataset_dir.exists(): # todo remove this
        os.makedirs(dataset_dir)

    with open(params["directories"]["idx-to-name"], "rb") as handle:
        idx_to_name = pickle.load(handle)
    subjects_dir = params["directories"]["subjects-dir"]
    labels = read_labels_from_annot("fsaverage", params["parcellation"], params["hemi"], subjects_dir=subjects_dir)
    name = idx_to_name[area_id]

    dst_dir = dataset_dir / name
    if not dst_dir.exists():
        os.makedirs(dst_dir)

    generate_dataset(epoch_dir, dst_dir, name, memmap=params["memmap"], max_subjects=params["max"])
