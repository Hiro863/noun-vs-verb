import sys
from utils.file_access import read_json
from pathlib import Path
from processing.coregistration import get_trans
from utils.file_access import read_mous_subject

if __name__ == "__main__":

    # Get input from the bash script
    subj_id = int(sys.argv[1])
    n_cores = int(sys.argv[2])
    param_dir = Path(sys.argv[3])

    # Get params
    params = read_json(param_dir, "coregistration-params.json")

    # Set up directories
    subjects_dir = Path(params["subjects_dir"])
    coreg_dir = Path(params["coreg_dir"])
    data_dir = Path(params["data_dir"])

    # Subject name
    subj_name = f"sub-V1{str(subj_id).zfill(3)}"
    dst_dir = data_dir / subj_name

    # Read raw
    raw = read_mous_subject(data_dir / subj_name)

    get_trans(subject=str(subjects_dir), dst_dir=dst_dir, subjects_dir=subjects_dir, info=raw.info)
