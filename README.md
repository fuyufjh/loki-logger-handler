# loki_logger_handler

A logging handler that sends log messages to Loki in text or JSON format.

## Features

* Logs pushed in text or JSON format
* Logger extra keys added automatically as keys into pushed JSON
* Publish in batch of Streams
* Publish logs compressed

## Args

* `url` (str): The URL of the Loki server.
* `labels` (dict): A dictionary of labels to attach to each log message.
* `auth` (tuple, optional): A tuple of user id and api key. Defaults to None.
* `timeout` (int, optional): The time in seconds to wait before flushing the buffer. Defaults to 10.
* `compressed` (bool, optional): Whether to compress the log messages before sending them to Loki. Defaults to `True`.
* `defaultFormatter` (logging.Formatter, optional): The formatter to use for log messages. Defaults to `PlainFormatter`.

## Formatters

* `logging.Formatter`: Formater for logging the message text. (default)
* `JsonFormatter`: Formater for logging the message and additional fields as JSON.

## Quick start

```python
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler,
import logging
import os 

# Set up logging
logger = logging.getLogger("custom_logger")
logger.setLevel(logging.DEBUG)

# Create an instance of the custom handler
custom_handler = LokiLoggerHandler(
    url=os.environ["LOKI_URL"],
    labels={"application": "Test", "envornment": "Develop"},
    timeout=10,
    auth=(os.environ["LOKI_USER_ID"], os.environ["LOKI_API_KEY"])
)
logger.addHandler(custom_handler)

logger.info("sample message with args %s %d", "test", 42)
logger.info("sample message with extra", extra={'custom_field': 'custom_value'})
logger.error("error message")
try:
    raise Exception("test exception")
except Exception as e:
    logger.exception("exception message")
```

## Messages samples

### PlainFormatter

```
2024-09-22 20:14:49.245   sample message with args test 42
```

with fields:

| Field       | Value   |
|-------------|---------|
| application | Test    |
| envornment  | Develop |
| level       | INFO    |

### JsonFormatter

```json
{
  "message": "sample message test 42",
  "timestamp": 1727007836.0348141,
  "thread": 140158402386816,
  "function": "<module>",
  "module": "example",
  "logger": "custom_logger",
  "level": "INFO",
  "exc_text": null
}
```

### JsonFormatter with exception

```json
{
  "message": "exception message",
  "timestamp": 1727007836.0350208,
  "thread": 140158402386816,
  "function": "<module>",
  "module": "example",
  "logger": "custom_logger",
  "level": "ERROR",
  "exc_text": null,
  "file": "example.py",
  "path": "/home/eric/loki-logger-handler/example.py",
  "line": 27,
  "stacktrace": "Traceback (most recent call last):\n  File \"/home/eric/loki-logger-handler/example.py\", line 25, in <module>\n    raise Exception(\"test exception\")\nException: test exception\n"
}
```