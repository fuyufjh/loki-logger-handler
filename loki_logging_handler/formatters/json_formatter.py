import logging
import json
import traceback

class JsonFormatter(logging.Formatter):
    """
    JsonFormatter is a custom logging formatter that formats log records as JSON.
    """

    # Ref. https://docs.python.org/3/library/logging.html#logrecord-attributes
    LOG_RECORD_FIELDS = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "message": record.getMessage(),
            "timestamp": record.created,
            "thread": record.thread,
            "function": record.funcName,
            "module": record.module,
            "logger": record.name,
            "level": record.levelname,
        }

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in self.LOG_RECORD_FIELDS:
                log_data[key] = value

        if record.levelname == "ERROR":
            log_data["file"] = record.filename
            log_data["path"] = record.pathname
            log_data["line"] = record.lineno
            log_data["stacktrace"] = traceback.format_exc()

        return json.dumps(log_data)