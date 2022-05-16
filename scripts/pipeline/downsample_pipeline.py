import argparse
import logging
import sys
import traceback

from pathlib import Path
from subprocess import call

from utils.file_access import load_json
from utils.slurm_tools import (check_status, save_status, update_status, init_status, make_job_file, get_subject_list,
                               get_subject_id_list)
from utils.logger import get_logger

logger = get_logger(file_name="downsample-slurm")
logger.setLevel(logging.INFO)


def submit_downsample(status_dir: Path, script_dir: Path, job_dir: Path, log_dir: Path,
                      status: dict, params: dict):

    subjects = get_subject_list()

    for idx, (subject_id, subject) in enumerate(subjects):

        # Check status is necessary
        subject_file = status_dir / "downsample" / f"{subject}-status.pickle"
        subject_status = check_status(subject_file)

        # Make job file
        if not subject_status:
            job_path = make_job_file(script="processing/downsample.py",
                                     script_dir=script_dir, log_dir=log_dir, job_dir=job_dir,
                                     name=f"downsample-{subject}", array_str=subject_id,
                                     output=f"downsample-{subject}.out",
                                     params=params["params"],  # only python 3.6 < keeps original order
                                     n_tasks_per_node=params["slurm"]["n-tasks"], mem_per_cpu=params["slurm"]["mem"])

            # Submit job
            out = call(["sbatch", job_path])
            if out.returncode == 0:
                update_status(status["array"][idx], success=True)
            else:
                update_status(status["array"][idx], success=False)

            # Save details
            save_status(status["array"][idx], path=subject_file)


def get_args():

    # Parse arguments
    parser = argparse.ArgumentParser(description="Submit downsampling job to slurm")

    # Read parameter from JSON
    parser.add_argument("--json_path", type=str, required=True, help="Path to JSON containing parameters")

    args = parser.parse_args()
    return load_json(Path(args.json_path))


if __name__ == "__main__":

    # Get parameters
    params = get_args()

    # Launch submission
    status = init_status(name=params["name"], n_tasks=params["n-tasks"],
                         mem=params["mem"], id_list=get_subject_id_list())

    submit_downsample(status_dir=params["status-dir"], script_dir=params["script-dir"], job_dir=params["job-dir"],
                      log_dir=params["log-dir"], status=status, params=params["params"])
