import logging
from . import Formatter

class PlainFormatter(Formatter):
    def __init__(self):
        pass

    def format(self, record: logging.LogRecord) -> str:
        return record.getMessage()
