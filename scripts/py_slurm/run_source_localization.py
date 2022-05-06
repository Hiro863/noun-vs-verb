import sys
from utils.file_access import read_json, write_json
from pathlib import Path
from mne import read_epochs
from processing.preprocessing import source_localize_

if __name__ == "__main__":

    # Get input from the bash script
    subj_id = sys.argv[1]
    n_cores = int(sys.argv[2])
    param_dir = Path(sys.argv[3])

    subj_name = f"sub-V1{str(subj_id).zfill(3)}"

    # Get the parameters
    params = read_json(param_dir, "preprocessing-params.json")

    # Set up directories
    root = Path(params["directories"]["root"])
    epochs_dir = root / "epochs-dir" / subj_name

    epochs = read_epochs(epochs_dir / f"{subj_name}-epo.fif")

    source_localize_(dst_dir=epochs_dir, subject=subj_name, epochs=epochs, params=params["stc params"], n_jobs=n_cores)

    write_json(dir_path=epochs_dir / "stc", file_name="parameters.json", data=params["stc params"])
