from pathlib import Path
from subprocess import call
from utils.slurm_toos import check_status, make_job_file


# These are not valid subject numbers
not_subject = [14, 15, 18, 21, 23, 41, 43, 47, 51, 56, 60, 67, 82, 91, 112]
# Technical problems
prob_subjects = []


def _get_subject_list():
    return []


def submit_downsample(status_dir: Path, script_dir: Path, job_dir: Path, log_dir: Path,
                      status: dict, params: dict):

    subjects = _get_subject_list()

    for idx, subject in subjects:

        # Check status is necessary
        subject_file = status_dir / "downsample" / f"{subject}-status.pickle"
        subject_status = check_status(subject_file)

        # Make job file
        if not subject_status:
            job_path = make_job_file(script="processing/downsample.py",
                                     script_dir=script_dir, log_dir=log_dir, job_dir=job_dir,
                                     name=f"downsample-{subject}", array_str=idx, output=f"downsample-{subject}.out",
                                     n_tasks_per_node=params["n-tasks"], mem_per_cpu=params["mem"])

            # Submit job
            out = call(["sbatch", job_path])
            if out.returncode == 0:
                pass

            # Save details

        # Update status

    return False


if __name__ == "__main__":
    submit_downsample()


