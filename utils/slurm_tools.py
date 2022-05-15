import logging
import os
import pickle
from pathlib import Path
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(file_name="slurm-tools")
logger.setLevel(logging.INFO)


# These are not valid subject numbers
not_subject = [14, 15, 18, 21, 23, 41, 43, 47, 51, 56, 60, 67, 82, 91, 112]

# Technical problems
prob_subjects = []

def get_subject_list():
    return []

def get_subject_id_list():
    return []

def get_area_id_list(parcellation="aparc"):
    return []


def init_status(name: str, n_tasks: int, mem: int, id_list: list):

    array = []
    for item_id in id_list:
        item_status = {"ID": item_id, "submitted": False, "submission-success": False, "completed": False,
                       "submission-time": None, "completion-time": None, "elapsed": None}
        array.append(item_status)

    return {"name": name, "n-tasks": n_tasks, "mem": mem, "completed": False, "array": array}


def update_status(status, success: bool):

    status["submitted"] = True
    status["submission-success"] = success
    status["submission-time"] = datetime.now()


def check_status(path: Path):

    if path.exists():
        with open(path, "rb") as handle:
            status = pickle.load(handle)
        return status
    else:
        return None


def save_status(status, path: Path):
    if not path.exists():
        os.makedirs(path)
    with open(path, "wb") as handle:
        pickle.dump(status, handle, protocol=pickle.HIGHEST_PROTOCOL)


def make_job_file(script: str, script_dir: Path, log_dir: Path, job_dir: Path,
                  name: str, array_str: str, output: str, params: dict,
                  n_tasks_per_node=1, mem_per_cpu=1):

    logger.info(f"Making a job file for the script {script}")

    # Make sure directories exist
    logs_dir = log_dir / name
    if not logs_dir.exists():
        os.makedirs(logs_dir)
    if not job_dir.exists():
        os.makedirs(job_dir)

    job_file = ""

    job_file += "#!/bin/bash\n"

    job_file += f"#SBATCH --job-name={name}\n"                      # name to be displayed for squeue etc.
    job_file += f"#SBATCH --array={array_str}\n"                    # job array, e.g. 1,2,3
    job_file += f"#SBATCH --ntasks-per-node={n_tasks_per_node}\n"   # number of tasks
    job_file += f"#SBATCH --chdir={logs_dir}\n"                     # working directory in logs_dir
    job_file += f"#SBATCH --mem-per-cpu={mem_per_cpu}gb\n"          # number of memory in GB
    job_file += f"#SBATCH --output={output}.out\n"                  # output file name

    job_file += f"scripts_dir={script_dir}\n"

    job_file += f"export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa\n"
    job_file += f"python $scripts_dir/{script}"

    for name, value in params.items():

        if isinstance(value, list):
            job_file += f"--{name} {[str(item) + ' ' for item in value]}"
        else:
            job_file += f"--{name} {value}"
    job_file += "\n"

    job_path = job_dir / f"{name}.job"

    with open(job_path, "w") as f:
        f.write(job_file)

    logger.info(f"The job file was added to the job directory \n {job_file}")

    return job_path
