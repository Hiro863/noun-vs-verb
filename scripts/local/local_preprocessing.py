import argparse
import logging
import os

from joblib import Parallel, delayed, cpu_count
from pathlib import Path
from processing.preprocessing import process_single_subject
from utils.file_access import read_json, get_mous_raw_paths, get_project_root


fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"

root = get_project_root()
log_path = root / "data/logs"

logging.basicConfig(level=logging.DEBUG, filename=log_path / "debug.log", format=fmt)


def determine_n_jobs(n_jobs: int, n_subjects: int):
    n_cores = cpu_count()
    n_jobs = max(1, min(n_jobs, n_cores, n_subjects))
    return n_jobs


def get_args():

    parser = argparse.ArgumentParser(description="Process multiple subject data in parallel. "
                                     "Required arguments are: src_dir, dst_dir, events_dir, param_dir")

    parser.add_argument("--src_dir",
                        type=str,
                        required=True,
                        help="Path to the directory containing all the subject data")

    parser.add_argument("--dst_dir",
                        type=str,
                        required=True,
                        help="Path to the directory to save results")

    parser.add_argument("--events_dir",
                        type=str,
                        required=True,
                        help="Path to the directory containing all the events CSV files")

    parser.add_argument("--param_dir",
                        type=str,
                        required=True,
                        help="Path to the directory containing all the parameter JSON files")

    parser.add_argument("--n_jobs",
                        type=int,
                        required=False,
                        help="Number of parallel jobs to use. Default is 1.")

    args = parser.parse_args()

    src_dir = args.src_dir
    dst_dir = args.dst_dir
    events_dir = args.events_dir
    param_dir = args.param_dir
    n_jobs = 1 if args.n_jobs is None else args.n_jobs

    # Make sure that paths are strings
    def check_type(arg, name):
        if not isinstance(arg, str):
            msg = f"'{name}' must be string but got '{type(arg)}'"
            logging.exception(msg)
            raise TypeError(msg)

    check_type(src_dir, "src_dir")
    check_type(dst_dir, "dst_dir")
    check_type(events_dir, "events_dir")
    check_type(param_dir, "param_dir")

    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)
    events_dir = Path(events_dir)
    param_dir = Path(param_dir)

    # Check if they exist
    def check_exists(path, name):
        if not path.exists():
            msg = f"Path '{name}' does not exist"
            logging.exception(msg)
            raise FileNotFoundError(msg)

    check_exists(src_dir, "src_dir")
    check_exists(dst_dir, "dst_dir")
    check_exists(events_dir, "events_dir")
    check_exists(param_dir, "param_dir")

    params = read_json(param_dir, "preprocess_params.json")

    return src_dir, dst_dir, events_dir, params, n_jobs


def main():

    src_dir, dst_dir, events_dir, params, n_jobs = get_args()

    raw_list = get_mous_raw_paths(src_dir)

    n_jobs = determine_n_jobs(n_jobs, n_subjects=len(raw_list))

    parallel_funcs = []
    for subject_path, subject_name in raw_list:

        # Store results in separate directories
        subject_epoch_dir = dst_dir / subject_name

        if not subject_epoch_dir.exists():
            os.makedirs(subject_epoch_dir)

        func = delayed(process_single_subject)(src_dir=subject_path,
                                               dst_dir=subject_epoch_dir,
                                               events_dir=events_dir,
                                               subject_name=subject_name,
                                               downsample_params=params["downsample params"],
                                               filter_params=params["filter params"],
                                               artifact_params=params["artifact params"],
                                               epoch_params=params["epoch params"],
                                               stc_params=params["stc params"])
        parallel_funcs.append(func)

    parallel_pool = Parallel(n_jobs=n_jobs)
    parallel_pool(parallel_funcs)


if __name__ == "__main__":
    main()
