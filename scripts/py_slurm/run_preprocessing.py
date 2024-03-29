import os
import sys
from src.utils.file_access import read_json, write_json
from pathlib import Path
from src.processing.preprocessing import process_single_subject
from src.utils.logger import get_logger


if __name__ == "__main__":

    logger = get_logger("/data/home/hiroyoshi/final/logs", "preprocessing")
    print("hello?")

    # Get input from the bash script
    subj_id = sys.argv[1]
    n_cores = int(sys.argv[2])
    param_dir = Path(sys.argv[3])

    subj_name = f"sub-V1{str(subj_id).zfill(3)}"

    # Get the parameters
    params = read_json(param_dir, "preprocessing-params.json")

    # Set up directories
    root = Path(params["directories"]["root"])
    raw_dir = Path(params["directories"]["raw-dir"]) / subj_name
    epochs_dir = root / "epochs-dir" / subj_name
    events_dir = root / "events-dir"

    if not epochs_dir.exists():
        os.makedirs(epochs_dir)

    process_single_subject(raw_dir, epochs_dir, events_dir, subj_name,
                           downsample_params=params["downsample params"], filter_params=params["filter params"],
                           artifact_params=params["artifact params"], epoch_params=params["epoch params"],
                           stc_params=params["stc params"],
                           stc=False,
                           n_cores=n_cores)

    write_json(dir_path=epochs_dir, file_name="parameters.json", data=params)

