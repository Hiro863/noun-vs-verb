import logging


def get_handlers(log_path, file_name):
    fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
          "%(funcName)s() :: Line %(lineno)d :: %(message)s"

    formatter = logging.Formatter(fmt)

    # Print to file
    file_handler = logging.FileHandler(f"{log_path}/{file_name}.log")
    file_handler.setFormatter(formatter)

    # Print to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    return file_handler, console_handler


