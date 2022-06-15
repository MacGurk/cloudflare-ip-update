import logging
from logging.handlers import RotatingFileHandler
import os


def init(script_dir):
    log_file_name = "ip_update.log"
    log_file_path = os.path.join(script_dir, log_file_name)

    logging_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logging_handler = RotatingFileHandler(
        log_file_path,
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=10,
        encoding=None,
        delay=False
    )
    logging_handler.setFormatter(logging_formatter)
    logging_handler.setLevel(logging.INFO)

    logger = logging.getLogger("root")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging_handler)
