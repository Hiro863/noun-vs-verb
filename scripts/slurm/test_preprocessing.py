import sys
from utils.file_access import read_json
from pathlib import Path
from processing.preprocessing import process_single_subject

if __name__ == "__main__":

    # Get input from the bash script
    subj_id = sys.argv[1]
    # n_jobs = sys.argv[2]

    subj_name = f"sub-V100{subj_id}"

    # Set up directories
    root = Path("/data/home/hiroyoshi/test-dir")
    src_dir = root / "test-src" / subj_name
    dst_dir = root / "test-dst"
    events_dir = root / "events_dir"
    param_dir = root / "param_dir"

    params = read_json(param_dir, "preprocess_params.json")
    process_single_subject(src_dir, dst_dir, events_dir, subj_name,
                           downsample_params=params["downsample params"], filter_params=params["filter params"],
                           artifact_params=params["artifact params"], epoch_params=params["epoch params"],
                           stc_params=params["stc params"])

