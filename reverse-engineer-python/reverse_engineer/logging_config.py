"""
Structured logging configuration for RE-cue.

This module provides a flexible, structured logging framework with:
- Configurable log levels
- JSON and text formatting
- File rotation support
- Performance tracking
- Error context
"""

import json
import logging
import logging.handlers
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as JSON.

    This formatter creates structured log entries with consistent fields
    for better parsing and analysis in log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON string representation of the log record
        """
        from datetime import datetime, timezone

        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "performance"):
            log_data["performance"] = record.performance

        if hasattr(record, "context"):
            log_data["context"] = record.context

        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        return json.dumps(log_data)


class PerformanceLogger:
    """
    Context manager for logging performance metrics.

    Usage:
        with PerformanceLogger(logger, "operation_name"):
            # code to measure
            pass
    """

    def __init__(self, logger: logging.Logger, operation: str, context: Optional[Dict] = None):
        """
        Initialize performance logger.

        Args:
            logger: Logger instance to use
            operation: Name of the operation being measured
            context: Additional context to include in log
        """
        self.logger = logger
        self.operation = operation
        self.context = context or {}
        self.start_time = 0.0

    def __enter__(self):
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log performance metrics."""
        duration_ms = (time.perf_counter() - self.start_time) * 1000

        # Create log record with performance data
        extra = {
            "performance": {
                "operation": self.operation,
                "duration_ms": round(duration_ms, 2),
                **self.context,
            }
        }

        if exc_type:
            extra["performance"]["failed"] = True
            self.logger.warning(
                f"Performance: {self.operation} failed after {duration_ms:.2f}ms",
                extra=extra,
                exc_info=(exc_type, exc_val, exc_tb),
            )
        else:
            self.logger.debug(
                f"Performance: {self.operation} completed in {duration_ms:.2f}ms", extra=extra
            )


def configure_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_type: str = "text",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file for file-based logging
        format_type: Format type - 'json' or 'text'
        max_bytes: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        enable_console: Whether to log to console (default: True)

    Returns:
        Configured root logger
    """
    # Get root logger
    root_logger = logging.getLogger("reverse_engineer")
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers and close them properly
    for handler in root_logger.handlers[:]:
        handler.close()
    root_logger.handlers.clear()

    # Configure formatter
    if format_type.lower() == "json":
        formatter = JSONFormatter()
    else:
        # Text formatter with timestamp and context
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Add file handler with rotation if log file specified
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"reverse_engineer.{name}")


# Convenience functions for backward compatibility
def log_debug(message: str, context: Optional[Dict] = None, **kwargs):
    """
    Log a debug message.

    Args:
        message: Message to log
        context: Additional context to include
        **kwargs: Additional keyword arguments for logger
    """
    logger = logging.getLogger("reverse_engineer")
    extra = {"context": context} if context else {}
    logger.debug(message, extra=extra, **kwargs)


def log_info(message: str, context: Optional[Dict] = None, **kwargs):
    """
    Log an info message.

    Args:
        message: Message to log
        context: Additional context to include
        **kwargs: Additional keyword arguments for logger
    """
    logger = logging.getLogger("reverse_engineer")
    extra = {"context": context} if context else {}
    logger.info(message, extra=extra, **kwargs)


def log_warning(message: str, context: Optional[Dict] = None, **kwargs):
    """
    Log a warning message.

    Args:
        message: Message to log
        context: Additional context to include
        **kwargs: Additional keyword arguments for logger
    """
    logger = logging.getLogger("reverse_engineer")
    extra = {"context": context} if context else {}
    logger.warning(message, extra=extra, **kwargs)


def log_error(message: str, context: Optional[Dict] = None, exc_info: bool = False, **kwargs):
    """
    Log an error message.

    Args:
        message: Message to log
        context: Additional context to include
        exc_info: Whether to include exception information
        **kwargs: Additional keyword arguments for logger
    """
    logger = logging.getLogger("reverse_engineer")
    extra = {"context": context} if context else {}
    logger.error(message, extra=extra, exc_info=exc_info, **kwargs)


def log_critical(message: str, context: Optional[Dict] = None, exc_info: bool = False, **kwargs):
    """
    Log a critical message.

    Args:
        message: Message to log
        context: Additional context to include
        exc_info: Whether to include exception information
        **kwargs: Additional keyword arguments for logger
    """
    logger = logging.getLogger("reverse_engineer")
    extra = {"context": context} if context else {}
    logger.critical(message, extra=extra, exc_info=exc_info, **kwargs)
