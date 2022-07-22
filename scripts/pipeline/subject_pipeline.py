import json
import logging
import sys
import traceback


from src.utils.slurm_tools import submit_subject_jobs
from src.utils.file_access import get_params
from src.utils.logger import get_logger

logger = get_logger(file_name="subject-slurm")
logger.setLevel(logging.INFO)


def main(params):

    results = submit_subject_jobs(params)
    return results


if __name__ == "__main__":

    results = {}
    try:
        # Get parameters
        params = get_params()

        # Submit
        results = main(params)

        logger.info(json.dumps(params, sort_keys=True, indent=4))

    except FileNotFoundError as e:
        logger.exception(e.strerror)
        sys.exit(-1)

    except Exception as e:  # noqa

        logger.error(f"Unexpected exception during submitting a script. \n {traceback.format_exc()}")
        sys.exit(-1)

    successes = [k for k, v in results.items() if v == "success"]
    failures = [k for k, v in results.items() if v == "failure"]
    logger.info(f"{len(successes)} / {len(successes) + len(failures)} jobs submitted.")
