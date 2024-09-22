# loki_logging_handler

A logging handler that sends log messages to Loki in text or JSON format.

## Features

* Buffer logs in memory and send to Loki in batch
* Logs pushed in text or JSON format
* Logger extra keys added automatically as keys into pushed JSON
* Publish logs compressed

## Args

* `url` (str): The URL of the Loki server.
* `labels` (dict): A dictionary of labels to attach to each log message.
* `auth` (tuple, optional): A tuple of user id and api key. Defaults to None.
* `buffer_timeout` (int, optional): The time in seconds to wait before flushing the buffer. Defaults to 10.
* `buffer_size_threshold` (int, optional): The number of log messages to buffer before flushing. Defaults to 10000.
* `compressed` (bool, optional): Whether to compress the log messages before sending them to Loki. Defaults to `True`.
* `defaultFormatter` (logging.Formatter, optional): The formatter to use for log messages. Defaults to `PlainFormatter`.

## Formatters

* `logging.Formatter`: Formater for logging the message text. (default)
* `JsonFormatter`: Formater for logging the message and additional fields as JSON.

## Quick start

```python
from loki_logging_handler.loki_handler import LokiHandler
import logging
import os 

# Set up logging
logger = logging.getLogger("custom_logger")
logger.setLevel(logging.DEBUG)

# Create an instance of the custom handler
custom_handler = LokiHandler(
    url=os.environ["LOKI_URL"],
    labels={"application": "Test", "envornment": "Develop"},
    auth=(os.environ["LOKI_USER_ID"], os.environ["LOKI_API_KEY"]),
    # formatter=JsonFormatter(),
    # buffer_timeout=10,
    # buffer_size_threshold=10000,
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

### Default formatter

```
sample message with args test 42
```

with fields:

| Field       | Value   |
|-------------|---------|
| application | Test    |
| envornment  | Develop |
| level       | INFO    |

### Default formatter with exception

```
exception message
Traceback (most recent call last):
  File "/home/eric/loki-logger-handler/example.py", line 32, in <module>
    raise Exception("test exception")
Exception: test exception
```

### Json Formatter

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

### Json Formatter with exception

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