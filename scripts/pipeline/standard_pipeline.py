import json
import sys
from time import sleep
from datetime import datetime
from pathlib import Path

from utils.file_access import load_json
from utils.logger import get_logger

SLEEP = 10


def main(param_path):
    # Read the parameters
    params = load_json(param_path)
    logger = get_logger(params["log-dir"], params["log-name"])

    start = datetime.now()
    logger.info(f"Launching standard pipeline at {start}")
    logger.info(f"Following parameters are used ----------------------------------------------------------------------")
    logger.info(json.dumps(params, sort_keys=True, indent=4))

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
    logger.info(f"Process terminated at {end}")  # todo success
    logger.info(f"Process took {end - start}")
    print(f"")


if __name__ == "__main__":

    param_path = Path(sys.argv[1])

    main(param_path)



