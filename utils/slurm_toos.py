import os
import pickle
from pathlib import Path


def make_status(path: Path):

    # Submission time

    # Done
    pass


def check_status(path: Path):

    if path.exists():
        with open(path, "rb") as handle:
            status = pickle.load(handle)
        return status
    else:
        return None


def make_job_file(script: str, script_dir: Path, log_dir: Path, job_dir: Path,
                  name: str, array_str: str, output: str,
                  n_tasks_per_node=1, mem_per_cpu=1):

    logs_dir = log_dir / name
    if not logs_dir.exists:
        os.makedirs(logs_dir)

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

    params = []
    for param in params:
        job_file += f"{param} "
    job_file += "\n"

    job_path = job_dir / f"{name}.job"
    print(job_file)

    with open(job_path, "w") as f:
        f.write(job_file)

    return job_path
