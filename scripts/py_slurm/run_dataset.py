import pickle
import sys
from utils.file_access import read_json
from pathlib import Path
from mne import read_labels_from_annot
from processing.dataset import generate_dataset


if __name__ == "__main__":

    # Get input from the bash script
    area_id = int(sys.argv[1])
    n_cores = int(sys.argv[2])
    param_dir = Path(sys.argv[3])

    # Get the parameters
    params = read_json(param_dir, "dataset-params.json")

    # Set up directories
    root = Path(params["directories"]["root"])
    epoch_dir = root / "test-epochs-dir"  # todo remove
    dataset_dir = root / "dataset-dir"

    with open(params["directories"]["idx-to-name"], "rb") as handle:
        idx_to_name = pickle.load(handle)
    subjects_dir = params["directories"]["subjects-dir"]
    labels = read_labels_from_annot("fsaverage", params["parcellation"], params["hemi"], subjects_dir=subjects_dir)
    name = idx_to_name[area_id]

    generate_dataset(epoch_dir, dataset_dir / name, name, memmap=params["memmap"])
