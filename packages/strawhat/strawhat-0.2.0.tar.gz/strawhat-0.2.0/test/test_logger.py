#!/usr/bin/env python3
from strawhat import Logger

log_path = "../logs"

LOG = Logger(log_path).get_logger()

LOG.info("Hello world")
