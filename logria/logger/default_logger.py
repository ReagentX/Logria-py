"""
Handles the internal logger for debugging purposes
"""

import logging


def setup_default_logger(name: str) -> logging.Logger:
    """
    Create a logger instance we can import to anywhere, logs in format:
    2019-10-28 14:32:57,843 - model.views - INFO - Received request to get_data

    To create an instance of the logger, import with
        from repricing_modules.helpers import logger
    and declare with this call:
        LOGGER = logger.setup_default_logger(__name__)
    """
    # Create Python/Django logger instance for the module
    logger = logging.getLogger(name)
    # Log all types of messages
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # create formatter; use color escape codes
    formatter = logging.Formatter(
        '\u001b[33m%(asctime)s \u001b[0m- \u001b[34m%(name)s.%(funcName)s \u001b[0m- \u001b[32m%(processName)s \u001b[0m- \u001b[36m%(levelname)s \u001b[0m- %(message)s')
    # add formatter to console handler
    console_handler.setFormatter(formatter)
    # add console handler to logger
    logger.addHandler(console_handler)
    return logger
