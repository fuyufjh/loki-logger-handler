import json
from typing import Dict, List, Any


# A log entry is a single log message with a timestamp, a set of labels, and a message
# TODO: additional metadata
class LogEntry:
    def __init__(self, timestamp: float, message: str):
        self.timestamp = timestamp
        self.message = message

# A stream is a collection of log entries with the same labels
class Stream:
    def __init__(self, labels: Dict[str, str] = dict()):
        self.labels = labels
        self.values: List[LogEntry] = []

    def append(self, log_entry: LogEntry) -> None:
        self.values.append(log_entry)
    
    def serialize(self):
        return json.dumps(self, cls=_StreamEncoder)


class _StreamEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Stream):
            return {
                "stream": obj.labels,
                "values": [[str(int(entry.timestamp * 1e9)), entry.message] for entry in obj.values]
            }
        return json.JSONEncoder.default(self, obj)


# A Loki request is a collection of streams
class LokiRequest:
    def __init__(self, streams):
        self.streams = streams
        
    def serialize(self):
        return json.dumps(self, cls=_LokiRequestEncoder)


class _LokiRequestEncoder(_StreamEncoder):
    def default(self, obj):
        if isinstance(obj, LokiRequest):
            return {"streams": [self.default(stream) for stream in obj.streams]}
        return super().default(obj)