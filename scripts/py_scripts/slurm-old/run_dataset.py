import argparse
import logging
from pathlib import Path
from src.processing import generate_dataset

fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"

log_path = Path("../../data/logs")

logging.basicConfig(level=logging.DEBUG, filename=log_path / "debug.log", format=fmt)


########################################################################################################################
# COMBINE SUBJECT DATA INTO A SINGLE DATASET                                                                           #
########################################################################################################################

def get_args():

    parser = argparse.ArgumentParser(description="Single subject preprocessing. Required arguments are:"
                                     "epoch_dir, dst_dir, param_dir, area_name, memmap")

    parser.add_argument("--epoch_dir",
                        type=str,
                        required=True,
                        help="Path to the directory containing the epoch data")

    parser.add_argument("--dst_dir",
                        type=str,
                        required=True,
                        help="Path to the directory to save the dataset in")

    parser.add_argument("--area_name",
                        type=str,
                        required=True,
                        help="Name of the cortical area to make dataset for. If 'sensor', "
                        "make a dataset for the sensor space.")

    parser.add_argument("--memmap",
                        type=bool,
                        required=False,
                        help="Whether to use memmap or work directly in RAM. By default memmap is used.")

    parser.add_argument("--reject",
                        type=str,
                        required=False,
                        help="Path to file containing list of subjects to ignore")

    args = parser.parse_args()

    epoch_dir = args.epoch_dir
    dst_dir = args.dst_dir
    area_name = args.area_name
    memmap = True if args.memmap is None else args.memmap
    reject = args.reject

    # Make sure that paths are strings
    def check_type(arg, name, target):
        if not isinstance(arg, target):
            msg = f"'{name}' must be {target} but got '{type(arg)}'"
            logging.exception(msg)
            raise TypeError(msg)

    check_type(epoch_dir, "epoch_dir", str)
    check_type(dst_dir, "dst_dir", str)
    check_type(area_name, "area_name", str)
    check_type(memmap, "memmap", bool)

    epoch_dir = Path(epoch_dir)
    dst_dir = Path(dst_dir)

    # Check if they exist
    def check_exists(path, name):
        if not path.exists():
            msg = f"Path '{name}' does not exist"
            logging.exception(msg)
            raise FileNotFoundError(msg)

    check_exists(epoch_dir, "epoch_dir")
    check_exists(dst_dir, "dst_dir")

    return epoch_dir, dst_dir, area_name, memmap, reject


def main():
    epoch_dir, dst_dir, area_name, memmap, reject = get_args()
    generate_dataset(epoch_dir, dst_dir, area_name, memmap, reject)


if __name__ == "__main__":
    main()
