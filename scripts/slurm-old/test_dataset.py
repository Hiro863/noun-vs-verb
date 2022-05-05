import sys
from mne import read_labels_from_annot
from utils.file_access import read_json
from pathlib import Path
from processing.dataset import generate_dataset
from processing.preprocessing import process_single_subject

if __name__ == "__main__":

    # Get input from the bash script
    area_id = int(sys.argv[1])
    # n_jobs = sys.argv[2]

    # Set up directories
    root = Path("/data/home/hiroyoshi/test-dir")
    epoch_dir = root / "test-dst"
    dst_dir = root / "dataset-dir"
    param_dir = root / "param_dir"

    params = read_json(param_dir, "preprocess_params.json")

    # Get labels
    parcellation = params["stc params"]["parcellation"]
    hemi = params["stc params"]["hemi"]
    subjects_dir = "/data/home/hiroyoshi/data/MNE-sample-data/subjects"
    labels = read_labels_from_annot("fsaverage", parcellation, hemi, subjects_dir=subjects_dir)

    generate_dataset(epoch_dir, dst_dir, labels[area_id].name, memmap=True, reject=None)

