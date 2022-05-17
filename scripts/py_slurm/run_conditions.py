import pickle
import sys
import os
import numpy as np
from utils.file_access import read_json
from pathlib import Path
from mne import read_labels_from_annot
#from events.conditions import convert_y
from processing.condition import convert_y
from utils.logger import get_logger


def convert(name, params):
    dir_name = Path(params["dir-name"]) / name

    y = np.load(str(dir_name / "y.npy"))
    y, included = convert_y(y, mode=params["mode"],
                            df_dir=Path(params["df-dir"]),
                            to_index=params["to-index"],
                            balance=params["balance"],
                            params=params["params"])

    dst_dir = dir_name / params["dst-name"]
    if not dst_dir.exists():
        os.makedirs(dst_dir)

    np.save(str(dst_dir / "y.npy"), y)
    np.save(str(dst_dir / "included.npy"), included)


if __name__ == "__main__":

    # Get input from the bash script
    area_id = int(sys.argv[1])
    n_cores = int(sys.argv[2])
    param_dir = Path(sys.argv[3])

    logger = get_logger("/data/home/hiroyoshi/mous_wd/logs", f"dateset-{area_id}")

    # Get the parameters
    params = read_json(param_dir, "conditions-params-length.json")

    # Set up directories
    root = Path(params["root"])
    dataset_dir = root / "dataset-dir"

    with open(params["idx-to-name"], "rb") as handle:
        idx_to_name = pickle.load(handle)
    subjects_dir = params["subjects-dir"]
    labels = read_labels_from_annot("fsaverage", params["parcellation"], params["hemi"], subjects_dir=subjects_dir)

    name = idx_to_name[area_id]

    convert(name, params)

