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
        timeout=10,
        compressed=True,
        formatter=logging.Formatter(),
        auth: Optional[Tuple[str, str]] = None,
        additional_headers=dict()
    ):
        super().__init__()

        self.labels = labels
        self.timeout = timeout
        self.formatter = formatter
        self.loki_client = LokiClient(url=url, compressed=compressed, auth=auth, additional_headers=additional_headers)
        self.buffer: queue.Queue[BufferEntry] = queue.Queue()

        self.flush_lock = threading.Lock()
        self.flush_thread = threading.Thread(target=self.flush_loop, daemon=True)
        self.flush_thread.start()

        atexit.register(self.flush)

    @override
    def emit(self, record: logging.LogRecord):
        self.buffer.put(BufferEntry(record.created, record.levelname, self.format(record)))

    def flush_loop(self):
        while True:
            if not self.buffer.empty():                
                self.flush()
            else:
                time.sleep(self.timeout)

    def flush(self):
        with self.flush_lock:
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



