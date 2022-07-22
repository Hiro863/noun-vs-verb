import json
import sys
from time import sleep
from datetime import datetime
from pathlib import Path

from src.utils.file_access import load_json
from src.utils.logger import get_logger
from src.utils.slurm_tools import init_status, get_subject_id_list, get_area_id_list
from scripts.pipeline.downsample_pipeline import submit_downsample

SLEEP = 10  # in seconds


def _init_all_status(params: dict):

    # Downsampling status, per subject
    slurm = params["downsample"]["slurm"]
    downsample = init_status(name="downsample", n_tasks=slurm["n-tasks"], mem=slurm["mem"],
                             id_list=get_subject_id_list())

    # Epoching status, per subject
    slurm = params["epoching"]["slurm"]
    epoching = init_status(name="epoching", n_tasks=slurm["n-tasks"], mem=slurm["mem"],
                           id_list=get_subject_id_list())

    # Source localization, per subject
    slurm = params["source-localization"]["slurm"]
    source = init_status(name="source-localization", n_tasks=slurm["n-tasks"], mem=slurm["mem"],
                         id_list=get_subject_id_list())

    # Dataset generation, per cortical area
    slurm = params["dataset"]["slurm"]
    dataset = init_status(name="dataset", n_tasks=slurm["n-tasks"], mem=slurm["mem"],
                          id_list=get_area_id_list())

    # Condition conversion, per cortical area
    slurm = params["conversion"]["slurm"]
    condition = init_status(name="condition", n_tasks=slurm["n-tasks"], mem=slurm["mem"],
                            id_list=get_area_id_list())

    # Classification, per cortical area
    slurm = params["classification"]["slurm"]
    classification = init_status(name="classification", n_tasks=slurm["n-tasks"], mem=slurm["mem"],
                                 id_list=get_area_id_list())

    return {"downsample": downsample, "epoching": epoching, "source-localization": source,
            "dataset": dataset, "condition": condition, "classification": classification}


def main(param_path):

    # Read the parameters
    params = load_json(param_path)
    logger = get_logger(params["log-dir"], params["log-name"])

    # Print initial status
    start = datetime.now()
    logger.info(f"Launching standard pipeline at {start}")
    logger.info(f"Following parameters are used ----------------------------------------------------------------------")
    logger.info(json.dumps(params, sort_keys=True, indent=4))

    # Initialization
    root_status = init_status(params)

    # Periodically check and submit jobs if possible until all jobs are completed (or failed)
    while not all(root_status["downsample"], root_status["epoching"], root_status["source-localization"],
                  root_status["dataset"], root_status["condition"], root_status["classification"]):

        # Downsample
        submit_downsample(status_dir=params["status-dir"], script_dir=params["script-dir"], job_dir=params["job-dir"],
                          log_dir=params["log-dir"], status=root_status["downsample"], params=params["downsample"])

        # downsample = submit_downsample(params["downsample"], status)

        # Epoch
        # epoch = submit_epoch(params["epoch"], status)

        # Source localize
        # source = submit_source_localize(params["source-localize"], status)

        # Dataset
        # dataset = submit_dataset(params["dataset"], status)

        # Condition
        # condition = submit_condition(params["condition"], status)

        # Classification
        # analysis = submit_analysis(params["analysis"], status)

        sleep(SLEEP)

    # Print the resulting results
    end = datetime.now()
    logger.info(f"Process terminated at {end}")
    logger.info(f"Process took {end - start}")
    logger.info(f"Process final status -------------------------------------------------------------------------------")
    logger.info(json.dumps(root_status, sort_keys=True, indent=4))


if __name__ == "__main__":

    param_path = Path(sys.argv[1])

    main(param_path)
