import logging


def get_logger(log_path, file_name):
    fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
          "%(funcName)s() :: Line %(lineno)d :: %(message)s"

    formatter = logging.Formatter(fmt)
    root_logger = logging.getLogger()

    # Print to file
    file_handler = logging.FileHandler(f"{log_path}/{file_name}.log")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Print to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return root_logger


