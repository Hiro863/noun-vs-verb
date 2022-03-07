import os
from pathlib import Path

# Directory names
job_dir = Path(f"{os.getcwd()}/.job")
data_dir = Path("")  # todo: set data directory here
epoch_dir = data_dir / "epochs"
dataset_dir = data_dir / "dataset"
memmap = True
reject_file = None  # todo: add later
include_sensor = True  # include sensor space


# Process requirement per subject (todo: change this later)
time = "2:00:00"  # hours:minutes:seconds
mem = "10"        # in GB


def get_area_list(include_sensor=True):
    area_list = []
    if include_sensor:
        area_list.append("sensor")

    # todo: implement here
    return area_list


def make_dirs(path):
    if not path.exists():
        os.makedirs(path)


def main():

    area_list = get_area_list(include_sensor)

    make_dirs(job_dir)
    make_dirs(data_dir)
    make_dirs(epoch_dir)
    make_dirs(dataset_dir)

    for area in area_list:
        job_file = job_dir / f"{area}.job"
        dst_dir = dataset_dir / area

        make_dirs(dst_dir)

        with open(job_file) as file:
            file.writelines("#!/bin/bash\n")
            file.writelines(f"#SBATCH --job-name={area}.job\n")
            file.writelines(f"#SBATCH --output=.out/{area}.out\n")
            file.writelines(f"#SBATCH --error=.out/{area}.err\n")
            file.writelines(f"#SBATCH --time={time}\n")
            file.writelines(f"#SBATCH --mem={mem}\n")
            file.writelines(f"#SBATCH --qos=normal\n")
            file.writelines(f"#SBATCH --mail-type=ALL\n")
            file.writelines(f"#SBATCH --mail-user=$?????\n")  # todo?
            file.writelines(f"#SBATCH $HOME/project/root/executables/run_dataset.py "  # todo: which path?
                            f"--epoch_dir \"{epoch_dir}\" "
                            f"--dst_dir \"{dst_dir}\" "
                            f"--area_name \"{area}\" "
                            f"--memmap \"{memmap}\" "
                            f"--reject \"{reject_file}\" \n")

        # Queue the task
        os.system(f"sbatch {job_file}")
