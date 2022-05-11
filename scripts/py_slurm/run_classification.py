import logging
import os
import pickle
import sys

import numpy as np
from joblib import Parallel, delayed
from pathlib import Path

from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

from mvpa.classification import classify, get_slice, get_indices
from utils.file_access import read_json


fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"


logging.basicConfig(level=logging.DEBUG,
                    format=fmt,
                    handlers=[logging.StreamHandler(sys.stdout)])


MAX_JOBS = 32


def format_results(data, params):
    scores, lowers, uppers = [], [], []
    d_scores, d_lowers, d_uppers = [], [], []
    for s, l, u, ds, dl, du in data:  # per time step
        scores.append(s)
        lowers.append(l)
        uppers.append(u)
        d_scores.append(ds)
        d_lowers.append(dl)
        d_uppers.append(du)

    scores = np.stack(scores, axis=1)  # cv x time steps
    lowers = np.array(lowers)
    uppers = np.array(uppers)
    d_scores = np.stack(d_scores, axis=1)
    d_lowers = np.array(d_lowers)
    d_uppers = np.array(d_uppers)

    results = {"meta": params,
               "data":
                   {
                       "scores": scores,
                       "lowers": lowers,
                       "uppers": uppers,
                       "dummy-scores": d_scores,
                       "dummy-lowers": d_lowers,
                       "dummy-uppers": d_uppers
                   }}
    return results


def run_classification(label_name, params, n_cores):
    logging.info(f"Starting classification for the area {label_name}")

    n_jobs = min(n_cores, MAX_JOBS)

    # Create parallel functions per time point
    parallel_funcs = []

    # Load data
    x_path = Path(params["dataset-dir"]) / label_name / params["condition"] / "x.npy"
    y_path = Path(params["dataset-dir"]) / label_name / params["condition"] / "y.npy"
    # included_path = Path(params["dataset-dir"]) / label_name / params["included"]
    x = np.load(str(x_path))
    y = np.load(str(y_path))
    # included = np.load(str(included_path))
    # x = x[included]

    name_to_obj = {"LinearSVC": LinearSVC(max_iter=params["max-iter"])}

    # Time array
    times = np.arange(params["epochs-tmin"], params["epochs-tmax"], 1 / params["sfreq"])
    start_idx, end_idx = get_indices(times,
                                     params["classification-tmin"],
                                     params["classification-tmax"],
                                     params["sfreq"])

    clf = make_pipeline(StandardScaler(), name_to_obj[params["clf"]])
    #print(x.shape)
    for t_idx in range(start_idx, end_idx):
        x_slice = get_slice(x=x, t_idx=t_idx, window_size=params["window-size"], sfreq=params["sfreq"])
        #print(x_slice.shape)
        #print(t_idx)
        func = delayed(classify)(x=x_slice, y=y, cv=params["cv"],
                                 clf=clf, scoring=roc_auc_score)
        parallel_funcs.append(func)

    logging.debug(f"Total of {len(parallel_funcs)} parallel functions added")
    logging.debug(f"Executing {n_jobs} jobs in parallel")

    parallel_pool = Parallel(n_jobs=n_jobs)
    results = parallel_pool(parallel_funcs)
    results = format_results(data=results, params=params)

    dst_dir = Path(params["dst-dir"])
    if not dst_dir.exists():
        os.makedirs(dst_dir)
    with open(Path(params["dst-dir"]) / f"{label_name}.pickle", "wb") as handle:
        pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)

    logging.info(f"{len(parallel_funcs)} time steps processed")


if __name__ == "__main__":

    # Get input from the bash script
    label_id = int(sys.argv[1])
    n_cores = int(sys.argv[2])
    param_dir = Path(sys.argv[3])

    # Get the parameters
    params = read_json(param_dir, "classification-params.json")
    parcellation = params["parcellation"]
    root = Path(params["dict-dir"])
    with open(root / f"{parcellation}-idx_to_name.pickle", "rb") as handle:
        idx_to_name = pickle.load(handle)

    label_name = idx_to_name[label_id]

    run_classification(label_name, params, n_cores)


