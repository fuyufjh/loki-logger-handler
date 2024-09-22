import queue
import unittest
from unittest.mock import patch, MagicMock
import logging
from loki_logging_handler.loki_client import LokiClient
from loki_logging_handler.loki_handler import LokiHandler, BufferEntry
from loki_logging_handler.models import Stream, LokiRequest, LogEntry

class TestLokiLoggerHandler(unittest.TestCase):

    def setUp(self):
        self.url = "http://loki.example.com"
        self.labels = {"app": "test_app", "environment": "testing"}
        self.auth = ("test_user_id", "test_api_key")
        self.handler = LokiHandler(self.url, self.labels, auth=self.auth)

    def test_init(self):
        self.assertEqual(self.handler.labels, self.labels)
        self.assertEqual(self.handler.buffer_timeout, 10)
        self.assertIsInstance(self.handler.formatter, logging.Formatter)
        self.assertIsInstance(self.handler.loki_client, LokiClient)
        self.assertIsInstance(self.handler.buffer, queue.Queue)

    @patch('loki_logging_handler.loki_handler.BufferEntry')
    def test_emit(self, mock_buffer_entry):
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.created = 1234567890.0

        with patch.object(self.handler.buffer, 'put') as mock_put:
            self.handler.emit(record)

            mock_buffer_entry.assert_called_once_with(1234567890.0, "INFO", "Test message")
            mock_put.assert_called_once()

    @patch('loki_logging_handler.loki_client.LokiClient.send')
    def test_flush(self, mock_send):
        # Add some test entries to the buffer
        self.handler.buffer.put(BufferEntry(1234567890.0, "INFO", "Test message 1"))
        self.handler.buffer.put(BufferEntry(1234567891.0, "ERROR", "Test message 2"))

        self.handler.flush()

        # Check if LokiClient.send was called with the correct LokiRequest
        mock_send.assert_called_once()
        request_arg = mock_send.call_args[0][0]
        self.assertIsInstance(request_arg, LokiRequest)
        
        # Verify the contents of the LokiRequest
        streams = request_arg.streams
        self.assertEqual(len(streams), 2)  # One for INFO, one for ERROR
        
        info_stream = next(s for s in streams if s.labels['level'] == 'INFO')
        error_stream = next(s for s in streams if s.labels['level'] == 'ERROR')
        
        self.assertEqual(info_stream.labels, {"level": "INFO", "app": "test_app", "environment": "testing"})
        self.assertEqual(error_stream.labels, {"level": "ERROR", "app": "test_app", "environment": "testing"})
        
        self.assertEqual(len(info_stream.values), 1)
        self.assertEqual(len(error_stream.values), 1)
        
        self.assertEqual(info_stream.values[0].message, "Test message 1")
        self.assertEqual(error_stream.values[0].message, "Test message 2")

        expected_serialized = (
            '{"streams": ['
            '{"stream": {"level": "INFO", "app": "test_app", "environment": "testing"}, '
            '"values": [["1234567890000000000", "Test message 1"]]}, '
            '{"stream": {"level": "ERROR", "app": "test_app", "environment": "testing"}, '
            '"values": [["1234567891000000000", "Test message 2"]]}'
            ']}'
        )
        self.assertEqual(request_arg.serialize(), expected_serialized)

    def test_flush_empty_buffer(self):
        with patch('loki_logging_handler.loki_client.LokiClient.send') as mock_send:
            self.handler.flush()
            mock_send.assert_not_called()

    def test_init_with_auth(self):
        handler = LokiHandler(self.url, self.labels, auth=self.auth)
        self.assertEqual(handler.loki_client.headers["Authorization"], f"Bearer {self.auth[0]}:{self.auth[1]}")

    def test_init_without_auth(self):
        handler = LokiHandler(self.url, self.labels)
        self.assertNotIn("Authorization", handler.loki_client.headers)

    def test_init_with_additional_headers(self):
        additional_headers = {"X-Custom-Header": "CustomValue", "X-Another-Header": "AnotherValue"}
        handler = LokiHandler(self.url, self.labels, additional_headers=additional_headers)
        
        for key, value in additional_headers.items():
            self.assertIn(key, handler.loki_client.headers)
            self.assertEqual(handler.loki_client.headers[key], value)
        
        # Ensure the default Content-type header is still present
        self.assertIn("Content-type", handler.loki_client.headers)
        self.assertEqual(handler.loki_client.headers["Content-type"], "application/json")

    def test_init_additional_headers_dont_override_defaults(self):
        additional_headers = {"Content-type": "text/plain"}
        handler = LokiHandler(self.url, self.labels, additional_headers=additional_headers)
        
        # Ensure the default Content-type header is not overridden
        self.assertIn("Content-type", handler.loki_client.headers)
        self.assertEqual(handler.loki_client.headers["Content-type"], "application/json")


if __name__ == '__main__':
    unittest.main()
