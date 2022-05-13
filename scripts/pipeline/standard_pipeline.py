import sys
from time import sleep
from datetime import datetime
from pathlib import Path

from utils.file_access import read_json


SLEEP = 10


def main(param_dir):

    start = datetime.now()
    print(f"Launching standard pipeline at {start}")
    # todo print parameters here

    downsample, epoch, source, dataset, condition, analysis = False

    while not all(downsample, epoch, source, dataset, condition, analysis):

        # Downsample
        # downsample = submit_downsample(params["downsample"], status)

        # Epoch
        # epoch = submit_epoch(params["epoch"], status)

        # Source localize
        # source = submit_source_localize(params["source-localize"], status)

        # Dataset
        # dataset = submit_dataset(params["dataset"], status)

        # Condition
        # condition = submit_condition(params["condition"], status)

        # Analysis
        # analysis = submit_analysis(params["analysis"], status)

        sleep(SLEEP)

    end = datetime.now()
    print(f"Process terminated at {end}")  # todo success
    print(f"Process took {end - start}")
    print(f"")


if __name__ == "__main__":

    param_dir = Path(sys.argv[1])

    main(param_dir)



