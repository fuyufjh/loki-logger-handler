import unittest
from loki_logger_handler.formatters.plain_formatter import PlainFormatter
import logging

class TestPlainFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = PlainFormatter()

    def test_format_simple_message(self):
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname=None,
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )
        formatted = self.formatter.format(record)
        self.assertEqual(formatted, 'Test message')

    def test_format_message_with_args(self):
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname=None,
            lineno=0,
            msg='Test message: %s, %d',
            args=('arg1', 42),
            exc_info=None
        )
        formatted = self.formatter.format(record)
        self.assertEqual(formatted, 'Test message: arg1, 42')

    def test_format_message_with_dict_args(self):
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname=None,
            lineno=0,
            msg='Test message: %(key1)s, %(key2)d',
            args={'key1': 'value1', 'key2': 42},
            exc_info=None
        )
        formatted = self.formatter.format(record)
        self.assertEqual(formatted, 'Test message: value1, 42')