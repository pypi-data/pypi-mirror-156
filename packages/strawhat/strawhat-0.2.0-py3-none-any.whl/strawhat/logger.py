import logging
import os
import time
from .files import mkdir


class Logger:
    def __init__(self, log_path, new_logs_on_every_run=False):
        mkdir(log_path)

        if new_logs_on_every_run:
            dt = time.strftime("%b-%d-%Y_%H%M", time.localtime())
        else:
            dt = str()

        # Initialising logging path
        self.LOG_FILE_DEBUG = os.path.join(log_path, "log_debug_" + dt + ".log")
        self.LOG_FILE_WARNING = os.path.join(
            log_path, "log_warning_" + dt + ".log"
        )
        self.LOG_FILE_ERROR = os.path.join(log_path, "log_error_" + dt + ".log")

        self.LOG_LEVEL = logging.DEBUG

        self.LOG_FORMAT = logging.Formatter(
            "%(asctime)s | "
            "%(filename)s | "
            "%(funcName)s | "
            "%(levelname)s | "
            "line %(lineno)d :: "
            "%(message)s "
        )

    def add_file_handler(self, logger, log_file, log_level):
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(self.LOG_FORMAT)
        logger.addHandler(file_handler)
        return logger

    def get_logger(self, name=__name__):
        logger = logging.getLogger(name)
        logger.setLevel(self.LOG_LEVEL)

        # debug log
        logger = self.add_file_handler(
            logger, log_file=self.LOG_FILE_DEBUG, log_level=logging.DEBUG
        )
        # warning log
        logger = self.add_file_handler(
            logger, log_file=self.LOG_FILE_WARNING, log_level=logging.WARNING
        )
        # error log
        logger = self.add_file_handler(
            logger, log_file=self.LOG_FILE_ERROR, log_level=logging.ERROR
        )
        return logger
