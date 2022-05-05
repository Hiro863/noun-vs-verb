import os
from pathlib import Path

# Directory names
job_dir = Path(f"{os.getcwd()}/.job")
data_dir = Path("")  # todo: set data directory here
raw_dir = data_dir / "raw_dir"
results_dir = data_dir / "results_dir"
events_dir = data_dir / "events_dir"
param_dir = data_dir / "param_dir"


# Specify which subject data to use (todo: read from file?)
subject_list = ["sub-V1001", "sub-V1002"]

# Process requirement per subject (todo: change this later)
time = "2:00:00"  # hours:minutes:seconds
mem = "10"        # in GB


def make_dirs(path):
    if not path.exists():
        os.makedirs(path)


def main():

    make_dirs(job_dir)
    make_dirs(data_dir)
    make_dirs(raw_dir)
    make_dirs(results_dir)

    for subject in subject_list:
        job_file = job_dir / f"{subject}.job"
        src_dir = raw_dir / subject
        dst_dir = results_dir / subject

        make_dirs(dst_dir)

        with open(job_file) as file:
            file.writelines("#!/bin/bash\n")
            file.writelines(f"#SBATCH --job-name={subject}.job\n")
            file.writelines(f"#SBATCH --output=.out/{subject}.out\n")
            file.writelines(f"#SBATCH --error=.out/{subject}.err\n")
            file.writelines(f"#SBATCH --time={time}\n")
            file.writelines(f"#SBATCH --mem={mem}\n")
            file.writelines(f"#SBATCH --qos=normal\n")
            file.writelines(f"#SBATCH --mail-type=ALL\n")
            file.writelines(f"#SBATCH --mail-user=$?????\n")  # todo?
            file.writelines(f"#SBATCH $HOME/project/root/executables/run_preprocessing.py "  # todo: which path?
                            f"--src_dir \"{src_dir}\" "
                            f"--dst_dir \"{dst_dir}\" "
                            f"--events_dir \"{events_dir}\" "
                            f"--param_dir \"{param_dir}\" "
                            f"--subject_name \"{subject}\" \n")

        # Queue the task
        os.system(f"sbatch {job_file}")


if __name__ == "__main__":
    main()
