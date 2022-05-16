import logging
import os

from pathlib import Path


def get_logger(file_name, log_path=None):

    fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
          "%(funcName)s() :: Line %(lineno)d :: %(message)s"

    formatter = logging.Formatter(fmt)
    root_logger = logging.getLogger()

    # Log path
    if not log_path:
        log_path = Path(__file__).parent.parent / "logs"

    # Make sure the path exists
    if not log_path.exists():
        os.makedirs(log_path)

    # Print to file
    file_handler = logging.FileHandler(f"{log_path}/{file_name}.log")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Print to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return root_logger


