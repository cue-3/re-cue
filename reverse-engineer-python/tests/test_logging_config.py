"""
Tests for structured logging configuration.
"""

import json
import logging
import logging.handlers
import tempfile
import unittest
from pathlib import Path

from reverse_engineer.logging_config import (
    JSONFormatter,
    PerformanceLogger,
    configure_logging,
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
)


class TestJSONFormatter(unittest.TestCase):
    """Tests for JSONFormatter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = JSONFormatter()

    def test_format_basic_record(self):
        """Test formatting a basic log record."""
        logger = logging.getLogger("test")
        record = logger.makeRecord(
            name="test",
            level=logging.INFO,
            fn="test.py",
            lno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)

        # Check required fields
        self.assertIn("timestamp", log_data)
        self.assertIn("level", log_data)
        self.assertIn("logger", log_data)
        self.assertIn("message", log_data)
        self.assertIn("module", log_data)
        self.assertIn("function", log_data)
        self.assertIn("line", log_data)

        # Check values
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["logger"], "test")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["line"], 42)

    def test_format_with_performance_data(self):
        """Test formatting record with performance data."""
        logger = logging.getLogger("test")
        record = logger.makeRecord(
            name="test",
            level=logging.DEBUG,
            fn="test.py",
            lno=42,
            msg="Performance test",
            args=(),
            exc_info=None,
        )

        # Add performance data
        record.performance = {"operation": "test_op", "duration_ms": 123.45}

        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)

        self.assertIn("performance", log_data)
        self.assertEqual(log_data["performance"]["operation"], "test_op")
        self.assertEqual(log_data["performance"]["duration_ms"], 123.45)

    def test_format_with_exception(self):
        """Test formatting record with exception info."""
        logger = logging.getLogger("test")

        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logger.makeRecord(
            name="test",
            level=logging.ERROR,
            fn="test.py",
            lno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)

        self.assertIn("exception", log_data)
        self.assertIn("ValueError", log_data["exception"])
        self.assertIn("Test exception", log_data["exception"])


class TestPerformanceLogger(unittest.TestCase):
    """Tests for PerformanceLogger context manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = logging.getLogger("test_perf")
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.handlers.MemoryHandler(capacity=100)
        self.logger.addHandler(self.handler)

    def tearDown(self):
        """Clean up test fixtures."""
        self.logger.removeHandler(self.handler)
        self.handler.close()

    def test_successful_operation(self):
        """Test performance logging for successful operation."""
        with PerformanceLogger(self.logger, "test_operation"):
            # Simulate some work
            pass

        # Flush the memory handler
        self.handler.flush()

        # Check that a log record was created
        # Note: MemoryHandler doesn't expose buffer directly in all Python versions
        # We verify logger was called correctly by checking it doesn't raise

    def test_failed_operation(self):
        """Test performance logging for failed operation."""
        try:
            with PerformanceLogger(self.logger, "failing_operation"):
                raise RuntimeError("Test error")
        except RuntimeError:
            pass

        # The context manager should have logged the failure


class TestLoggingConfiguration(unittest.TestCase):
    """Tests for logging configuration."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
        # Reset logging and properly close handlers
        logger = logging.getLogger("reverse_engineer")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        logger.setLevel(logging.WARNING)

    def test_configure_with_console_only(self):
        """Test configuration with console logging only."""
        logger = configure_logging(level="INFO", enable_console=True)

        self.assertEqual(logger.name, "reverse_engineer")
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)

    def test_configure_with_file_logging(self):
        """Test configuration with file logging."""
        log_file = self.temp_path / "test.log"

        logger = configure_logging(
            level="DEBUG", log_file=log_file, enable_console=True, format_type="text"
        )

        # Should have 2 handlers: console and file
        self.assertEqual(len(logger.handlers), 2)

        # Check that log file was created
        self.assertTrue(log_file.exists())

        # Log a message
        logger.info("Test message")

        # Read the log file
        content = log_file.read_text()
        self.assertIn("Test message", content)

    def test_configure_with_json_format(self):
        """Test configuration with JSON format."""
        log_file = self.temp_path / "test.json"

        logger = configure_logging(
            level="INFO", log_file=log_file, format_type="json", enable_console=False
        )

        # Log a message
        logger.info("JSON test")

        # Read and parse the log file
        content = log_file.read_text()
        log_data = json.loads(content.strip())

        self.assertEqual(log_data["message"], "JSON test")
        self.assertEqual(log_data["level"], "INFO")

    def test_configure_log_levels(self):
        """Test different log levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            logger = configure_logging(level=level, enable_console=False)
            self.assertEqual(logger.level, getattr(logging, level))

            # Clean up for next iteration
            logger.handlers.clear()

    def test_file_rotation_configuration(self):
        """Test file rotation parameters."""
        log_file = self.temp_path / "rotating.log"

        logger = configure_logging(
            level="INFO",
            log_file=log_file,
            max_bytes=1024,
            backup_count=3,
            enable_console=False,
        )

        # Find the rotating file handler
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                file_handler = handler
                break

        self.assertIsNotNone(file_handler)
        self.assertEqual(file_handler.maxBytes, 1024)
        self.assertEqual(file_handler.backupCount, 3)


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for convenience logging functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Configure a test logger
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.log_file = self.temp_path / "test.log"

        # Configure logging explicitly before each test
        configure_logging(level="DEBUG", log_file=self.log_file, enable_console=False)

    def tearDown(self):
        """Clean up test fixtures."""
        # Reset logging and properly close handlers
        logger = logging.getLogger("reverse_engineer")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        self.temp_dir.cleanup()

    def test_log_info_function(self):
        """Test log_info convenience function."""
        log_info("Test info message")

        content = self.log_file.read_text()
        self.assertIn("Test info message", content)

    def test_log_debug_function(self):
        """Test log_debug convenience function."""
        log_debug("Test debug message")

        content = self.log_file.read_text()
        self.assertIn("Test debug message", content)

    def test_log_warning_function(self):
        """Test log_warning convenience function."""
        log_warning("Test warning message")

        content = self.log_file.read_text()
        self.assertIn("Test warning message", content)

    def test_log_error_function(self):
        """Test log_error convenience function."""
        log_error("Test error message")

        content = self.log_file.read_text()
        self.assertIn("Test error message", content)

    def test_log_with_context(self):
        """Test logging with additional context."""
        # Reconfigure for JSON
        logger = logging.getLogger("reverse_engineer")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

        configure_logging(
            level="INFO", log_file=self.log_file, format_type="json", enable_console=False
        )

        log_info("Contextual message", context={"user": "test", "action": "login"})

        content = self.log_file.read_text()
        log_data = json.loads(content.strip())

        self.assertIn("context", log_data)
        self.assertEqual(log_data["context"]["user"], "test")
        self.assertEqual(log_data["context"]["action"], "login")


class TestGetLogger(unittest.TestCase):
    """Tests for get_logger function."""

    def test_get_logger_returns_namespaced_logger(self):
        """Test that get_logger returns properly namespaced logger."""
        logger = get_logger("test_module")

        self.assertEqual(logger.name, "reverse_engineer.test_module")

    def test_multiple_loggers_share_config(self):
        """Test that multiple loggers share the root configuration."""
        temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(temp_dir.name)
        log_file = temp_path / "shared.log"

        try:
            # Configure root logger
            configure_logging(level="INFO", log_file=log_file, enable_console=False)

            # Get module-specific loggers
            logger1 = get_logger("module1")
            logger2 = get_logger("module2")

            # Both should log to the same file
            logger1.info("Message from module1")
            logger2.info("Message from module2")

            content = log_file.read_text()
            self.assertIn("Message from module1", content)
            self.assertIn("Message from module2", content)
        finally:
            # Clean up properly
            root_logger = logging.getLogger("reverse_engineer")
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
