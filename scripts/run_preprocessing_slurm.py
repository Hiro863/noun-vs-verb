import os
from pathlib import Path
from utils.file_access import read_json

no_subject = [14, 15, 18, 21, 23, 41, 43, 47, 51, 56, 60, 67, 82, 91, 112]
prob_subject = [3, 4, 5, 6, 9, 10, 11, 14, 17, 26, 30, 33, 44, 90, 97, 107, 109]

LOGS_DIR = Path("/data/home/hiroyoshi/logs")
JOBS_DIR = Path("/data/home/hiroyoshi/jobs")
PARAM_DIR = Path("")
JOB_DIR = Path("")
TOTAL_SUBJECTS = 1#17


def get_job_file(name, array_str, n_tasks_per_node, mem_per_cpu, script, script_dir, param_dir):

    logs_dir = LOGS_DIR / name
    if not logs_dir.exists:
        os.makedirs(logs_dir)

    job_file = ""

    job_file += "#!/bin/bash\n"

    job_file += f"#SBATCH --job-name={name}\n"
    job_file += f"#SBATCH --array={array_str}\n"
    job_file += f"#SBATCH --ntasks-per-node={n_tasks_per_node}\n"
    job_file += f"#SBATCH --chdir={logs_dir}\n"
    job_file += f"#SBATCH --mem-per-cpu={mem_per_cpu}gb\n"

    job_file += f"scripts_dir={script_dir}\n"
    job_file += f"param_dir={param_dir}\n"

    job_file += f"export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa\n"
    job_file += f"python $scripts_dir/{script} $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE $param_dir\n"

    job_path = JOBS_DIR / f"{name}.job"

    with open(job_path, "w") as f:
        f.write(job_file)

    return job_path

def run_downsampling(subjects):
    pass


def main():
    subject_ids = [i for i in range(TOTAL_SUBJECTS) if i not in no_subject or prob_subject]
    subjects = "".join(str(s) + "," for s in subject_ids)[:-1]

    path = get_job_file("preprocessing", array_str=subjects, n_tasks_per_node=32, mem_per_cpu=5,
                        script="run_preprocessing.py",
                        script_dir="/data/home/hiroyoshi/scripts/meg-mvpa/scripts/py_slurm",
                        param_dir="/data/home/hiroyoshi/mous_wd/param-dir")

    os.system(f"sbatch {path}")


if __name__ == "__main__":

    # params = read_json(PARAM_DIR, "preprocessing-params.json")

    main()#(params)

