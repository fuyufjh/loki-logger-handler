import traceback
import logging
import json
from . import Formatter

class LoguruFormatter(Formatter):
    def __init__(self):
        pass

    def format(self, record: logging.LogRecord) -> str:
        formatted = {
            "message": record.get("message"),
            "timestamp": record.get("time").timestamp(),
            "process": record.get("process").id,
            "thread": record.get("thread").id,
            "function": record.get("function"),
            "module": record.get("module"),
            "name": record.get("name"),
            "level": record.get("level").name,
        }

        if record.get("extra"):
            if record.get("extra").get("extra"):
                formatted.update(record.get("extra").get("extra"))
            else:
                formatted.update(record.get("extra"))

        if record.get("level").name == "ERROR":
            formatted["file"] = record.get("file").name
            formatted["path"] = record.get("file").path
            formatted["line"] = record.get("line")

            if record.get("exception"):
                exc_type, exc_value, exc_traceback = record.get("exception")
                formatted_traceback = traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                )
                formatted["stacktrace"] = "".join(formatted_traceback)

        return json.dumps(formatted)
