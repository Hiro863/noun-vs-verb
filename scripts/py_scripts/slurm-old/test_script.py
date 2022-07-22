from src.utils.file_access import read_json
from pathlib import Path
from src.processing.preprocessing import process_single_subject

if __name__ == "__main__":
    src_dir = "/data/home/hiroyoshi/test-dir/test-src/sub-V1001"
    dst_dir = "/data/home/hiroyoshi/test-dir/test-dst"
    events_dir = "/data/home/hiroyoshi/test-dir/events_dir"
    param_dir = "/data/home/hiroyoshi/test-dir/param_dir"
    subject_name = "sub-V1001"

    params = read_json(Path(param_dir), "preprocess_params.json")
    process_single_subject(Path(src_dir), Path(dst_dir), Path(events_dir), subject_name,
                           downsample_params=params["downsample params"], filter_params=params["filter params"],
                           artifact_params=params["artifact params"], epoch_params=params["epoch params"],
                           stc_params=params["stc params"])

