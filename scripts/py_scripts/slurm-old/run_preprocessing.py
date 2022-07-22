import argparse
import logging
from pathlib import Path
from src.utils.file_access import read_json
from src.processing.preprocessing import process_single_subject

fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"

logging.basicConfig(level=logging.DEBUG, format=fmt)
logging.getLogger().addHandler(logging.StreamHandler())

########################################################################################################################
# RUN PREPROCESSING ON A SINGLE SUBJECT DATA                                                                           #
########################################################################################################################
# Epochs directory will contain following:                                                                             #
# <epoch_dir>                                                                                                          #
#   - <subject name>                                                                                                   #
#       - <subject name>-epo.fif                    Epochs object in .fif format                                       #
#       - <subject name>-<cortical area name>.stc   SourceEstimate object in .stc format                               #
########################################################################################################################


def get_args():

    parser = argparse.ArgumentParser(description="Single subject preprocessing. Required arguments are:"
                                     "src_dir, dst_dir, events_dir, param_dir, subject_name")

    parser.add_argument("--src_dir",
                        type=str,
                        required=True,
                        help="Path to the directory containing the subject data")

    parser.add_argument("--dst_dir",
                        type=str,
                        required=True,
                        help="Path to the directory to save the results in")

    parser.add_argument("--events_dir",
                        type=str,
                        required=True,
                        help="Path to the directory in which all events files are stored")

    parser.add_argument("--param_dir",
                        type=str,
                        required=True,
                        help="Path to the directory containing all parameter JSON files")

    parser.add_argument("--subject_name",
                        type=str,
                        required=True,
                        help="Name of the subject to be preprocessed")

    args = parser.parse_args()

    src_dir = args.src_dir
    dst_dir = args.dst_dir
    events_dir = args.events_dir
    param_dir = args.param_dir
    subject_name = args.subject_name

    # Make sure that paths are strings
    def check_type(arg, name):
        if not isinstance(arg, str):
            msg = f"'{name}' must be string but got '{type(arg)}'"
            logging.exception(msg)
            raise TypeError(msg)

    check_type(src_dir, "src_dir")
    check_type(dst_dir, "dst_dir")
    check_type(events_dir, "events_dir")
    check_type(param_dir, "param_dir")
    check_type(subject_name, "subject_name")

    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)
    events_dir = Path(events_dir)
    param_dir = Path(param_dir)

    # Check if they exist
    def check_exists(path, name):
        if not path.exists():
            msg = f"Path '{name}' does not exist"
            logging.exception(msg)
            raise FileNotFoundError(msg)

    check_exists(src_dir, "src_dir")
    check_exists(dst_dir, "dst_dir")
    check_exists(events_dir, "events_dir")
    check_exists(param_dir, "param_dir")

    params = read_json(param_dir, "preprocess_params.json")

    return src_dir, dst_dir, events_dir, subject_name, params


def main():
    src_dir, dst_dir, events_dir, subject_name, params = get_args()

    process_single_subject(src_dir, dst_dir, events_dir, subject_name,
                           downsample_params=params["downsample params"], filter_params=params["filter params"],
                           artifact_params=params["artifact params"], epoch_params=params["epoch params"],
                           stc_params=params["stc params"])


if __name__ == "__main__":
    main()
