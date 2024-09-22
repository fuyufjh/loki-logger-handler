import queue
import threading
import time
import logging
import atexit
from loki_logging_handler.loki_client import LokiClient
from loki_logging_handler.models import Stream, LokiRequest, LogEntry
from typing import Optional, Tuple, override
from typing import Dict


class BufferEntry:
    def __init__(self, timestamp: float, level: str, message: str):
        self.timestamp = timestamp
        self.level = level
        self.message = message


class LokiHandler(logging.Handler):
    def __init__(
        self,
        url,
        labels: Dict[str, str],
        buffer_timeout=10,
        buffer_size_threshold=10000,
        compressed=True,
        formatter=logging.Formatter(),
        auth: Optional[Tuple[str, str]] = None,
        additional_headers=dict(),
    ):
        super().__init__()

        self.labels = labels
        self.buffer_timeout = buffer_timeout
        self.buffer_size_threshold = buffer_size_threshold
        self.formatter = formatter
        self.loki_client = LokiClient(url=url, compressed=compressed, auth=auth, additional_headers=additional_headers)
        self.buffer: queue.Queue[BufferEntry] = queue.Queue()

        self.flush_lock = threading.Lock()
        self.flush_condition = threading.Condition(self.flush_lock)
        self.flush_thread = threading.Thread(target=self.flush_loop, daemon=True)
        self.flush_thread.start()

        atexit.register(self.flush)

    @override
    def emit(self, record: logging.LogRecord):
        self.buffer.put(BufferEntry(record.created, record.levelname, self.format(record)))
        if self.buffer.qsize() >= self.buffer_size_threshold:
            with self.flush_condition:
                self.flush_condition.notify()

    def flush_loop(self):
        while True:
            with self.flush_condition:
                self.flush_condition.wait(self.buffer_timeout)
                if not self.buffer.empty():
                    self.flush()

    def flush(self):
        streams: Dict[str, Stream] = dict() # log level -> stream

        while not self.buffer.empty():
            e = self.buffer.get()
            if e.level not in streams:
                full_labels = { 
                    "level": e.level,
                    **self.labels
                }
                stream = Stream(full_labels)
                streams[e.level] = stream
            streams[e.level].append(LogEntry(e.timestamp, e.message))

        if streams:
            request = LokiRequest(streams.values())
            self.loki_client.send(request)
