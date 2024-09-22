import logging

class PlainFormatter(logging.Formatter):
    """
    Custom plain text formatter for logging records.

    This formatter drops all fields except the log message.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        # Call getMessage() instead of format() because we intend to drop other fields 
        # (e.g. timestamp, level name, etc.) and keep only the message
        return record.getMessage()
