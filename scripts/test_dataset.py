import sys
from utils.file_access import read_json
from pathlib import Path
from mne import read_labels_from_annot
from processing.dataset import generate_dataset


if __name__ == "__main__":

    # Get input from the bash script
    area_id = int(sys.argv[1])
    n_cores = int(sys.argv[2])

    # Set up directories
    root = Path("/data/home/hiroyoshi/test-dir")
    epoch_dir = root / "epoch_dir"
    dataset_dir = root / "dataset_dir"
    param_dir = root / "param_dir"

    params = read_json(param_dir, "preprocess_params.json")

    subjects_dir = "/data/home/hiroyoshi/data/mne_data/MNE-sample-data/subjects"
    labels = read_labels_from_annot("fsaverage", "aparc", "lh", subjects_dir=subjects_dir)
    name = labels[area_id].name

    generate_dataset(epoch_dir, dataset_dir, name)
