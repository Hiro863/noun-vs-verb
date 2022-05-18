import logging
import os
import pickle
import sys

import numpy as np
from pathlib import Path

from mvpa.classification import classify_temporal
from utils.file_access import read_json, read_data
from utils.logger import get_logger


fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"


logging.basicConfig(level=logging.DEBUG,
                    format=fmt,
                    handlers=[logging.StreamHandler(sys.stdout)])


MAX_JOBS = 32


def run_classification(label_name, params, n_cores):
    logging.info(f"Starting classification for the area {label_name}")

    n_jobs = min(n_cores, MAX_JOBS)

    # Load data
    x_path = Path(params["dataset-dir"]) / label_name #/ "x.dat"  #todo handle both
    y_path = Path(params["dataset-dir"]) / label_name / params["conditions"] / "y.npy"
    included_path = Path(params["dataset-dir"]) / label_name / params["conditions"] / "included.npy"
    x = read_data(x_path) # np.load(str(x_path))
    y = np.load(str(y_path))
    included = np.load(str(included_path))
    x = x[included]

    results = classify_temporal(x, y, params, n_jobs)

    dst_dir = Path(params["dst-dir"])
    if not dst_dir.exists():
        os.makedirs(dst_dir)
    with open(Path(params["dst-dir"]) / f"{label_name}.pickle", "wb") as handle:
        pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":

    # Get input from the bash script
    label_id = int(sys.argv[1])
    n_cores = int(sys.argv[2])
    param_dir = Path(sys.argv[3])

    logger = get_logger("/data/home/hiroyoshi/semi-final/logs", f"dateset-{label_id}")

    # Get the parameters
    params = read_json(param_dir, "classification-params.json")
    print(param_dir)
    #parcellation = params["parcellation"]
    path = Path(params["idx-to-name"])
    print(params)
    with open(path, "rb") as handle:
        idx_to_name = pickle.load(handle)

    label_name = idx_to_name[label_id]

    run_classification(label_name, params, n_cores)


