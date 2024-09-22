import unittest
import json
import logging
from loki_logging_handler.formatters.json_formatter import JsonFormatter

class TestJsonFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = JsonFormatter()

    def create_log_record(self, level=logging.INFO, msg="Test message", args=(), extra=None):
        logger = logging.getLogger("test_logger")
        return logger.makeRecord(
            name="test_logger",
            level=level,
            fn="test_file.py",
            lno=50,
            msg=msg,
            args=args,
            exc_info=None,
            func="test_function",
            extra=extra
        )

    def test_default_fields(self):
        record = self.create_log_record()
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        expected_fields = {"message", "timestamp", "thread", "function", "module", "logger", "level"}
        self.assertTrue(expected_fields.issubset(set(parsed.keys())))
        self.assertEqual(parsed["message"], "Test message")
        self.assertEqual(parsed["level"], "INFO")

    def test_extra_fields(self):
        extra = {"custom_field": "custom_value"}
        record = self.create_log_record(extra=extra)
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        self.assertIn("custom_field", parsed)
        self.assertEqual(parsed["custom_field"], "custom_value")

    def test_error_level_fields(self):
        record = self.create_log_record(level=logging.ERROR)
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        error_fields = {"file", "path", "line", "stacktrace"}
        self.assertTrue(error_fields.issubset(set(parsed.keys())))
        self.assertEqual(parsed["file"], "test_file.py")
        self.assertEqual(parsed["line"], 50)

    def test_non_error_level_fields(self):
        record = self.create_log_record(level=logging.INFO)
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        error_fields = {"file", "path", "line", "stacktrace"}
        self.assertFalse(any(field in parsed for field in error_fields))

    def test_message_formatting(self):
        record = self.create_log_record(msg="Test message with %s", args=("bar",))
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        
        self.assertEqual(parsed["message"], "Test message with bar")
