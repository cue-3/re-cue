#!/usr/bin/env python3
"""
Example demonstrating the RE-cue logging framework.

This script shows various logging features including:
- Basic logging configuration
- Different log levels
- JSON vs text output
- Performance logging
- Contextual logging
"""

from pathlib import Path
from reverse_engineer.logging_config import (
    configure_logging,
    get_logger,
    PerformanceLogger,
    log_info,
    log_warning,
)


def example_basic_logging():
    """Example: Basic logging setup and usage."""
    print("=" * 60)
    print("Example 1: Basic Logging")
    print("=" * 60)

    # Configure logging with text format
    configure_logging(level="INFO", enable_console=True)

    # Get a logger for this module
    logger = get_logger(__name__)

    # Log at different levels
    logger.debug("This won't appear (level is INFO)")
    logger.info("Starting example")
    logger.warning("This is a warning")
    logger.error("This is an error")

    print()


def example_file_logging():
    """Example: Logging to file with rotation."""
    print("=" * 60)
    print("Example 2: File Logging with Rotation")
    print("=" * 60)

    log_file = Path("/tmp/recue-example.log")

    # Configure with file output
    configure_logging(
        level="DEBUG",
        log_file=log_file,
        max_bytes=1024 * 1024,  # 1MB
        backup_count=3,
        enable_console=True,
    )

    logger = get_logger(__name__)
    logger.info("Logging to file: %s", log_file)
    logger.debug("Debug message written to file")

    print(f"Log file created at: {log_file}")
    if log_file.exists():
        print(f"Log file size: {log_file.stat().st_size} bytes")
    print()


def example_json_logging():
    """Example: JSON structured logging."""
    print("=" * 60)
    print("Example 3: JSON Structured Logging")
    print("=" * 60)

    log_file = Path("/tmp/recue-json.log")

    # Configure with JSON format
    configure_logging(
        level="INFO", log_file=log_file, format_type="json", enable_console=False
    )

    logger = get_logger(__name__)

    # Log with structured data
    logger.info("User action", extra={"context": {"user": "alice", "action": "analyze"}})

    logger.info(
        "Analysis complete",
        extra={
            "context": {
                "endpoints": 42,
                "models": 15,
                "framework": "Spring Boot",
            }
        },
    )

    # Read and display the JSON log
    if log_file.exists():
        content = log_file.read_text()
        print("JSON log output:")
        print(content)
    print()


def example_performance_logging():
    """Example: Performance measurement with context manager."""
    print("=" * 60)
    print("Example 4: Performance Logging")
    print("=" * 60)

    configure_logging(level="DEBUG", enable_console=True)

    logger = get_logger(__name__)

    # Measure operation performance
    with PerformanceLogger(logger, "file_analysis", context={"file_count": 100}):
        # Simulate some work
        import time

        time.sleep(0.1)

    print()


def example_contextual_logging():
    """Example: Logging with rich context."""
    print("=" * 60)
    print("Example 5: Contextual Logging")
    print("=" * 60)

    configure_logging(level="INFO", enable_console=True)

    # Using convenience functions with context
    log_info(
        "Project analysis started",
        context={
            "project_path": "/home/user/myproject",
            "framework": "Java Spring",
            "file_count": 156,
        },
    )

    log_warning("Deprecated pattern detected", context={"file": "UserController.java", "line": 42})

    print()


def example_error_logging():
    """Example: Error logging with exception info."""
    print("=" * 60)
    print("Example 6: Error Logging with Exceptions")
    print("=" * 60)

    configure_logging(level="ERROR", enable_console=True)

    logger = get_logger(__name__)

    try:
        # Simulate an error
        1 / 0
    except ZeroDivisionError:
        logger.error("Mathematical error occurred", exc_info=True)

    print()


def example_different_log_levels():
    """Example: Comparing different log levels."""
    print("=" * 60)
    print("Example 7: Log Level Filtering")
    print("=" * 60)

    # Configure with WARNING level
    print("With WARNING level:")
    configure_logging(level="WARNING", enable_console=True)

    logger = get_logger(__name__)
    logger.debug("Debug message (hidden)")
    logger.info("Info message (hidden)")
    logger.warning("Warning message (visible)")
    logger.error("Error message (visible)")

    print()


def example_module_loggers():
    """Example: Using module-specific loggers."""
    print("=" * 60)
    print("Example 8: Module-Specific Loggers")
    print("=" * 60)

    configure_logging(level="INFO", enable_console=True)

    # Get loggers for different modules
    analyzer_logger = get_logger("analyzer")
    generator_logger = get_logger("generator")
    detector_logger = get_logger("detector")

    analyzer_logger.info("Starting analysis")
    generator_logger.info("Generating documentation")
    detector_logger.info("Detecting framework")

    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("RE-cue Logging Framework Examples")
    print("=" * 60 + "\n")

    example_basic_logging()
    example_file_logging()
    example_json_logging()
    example_performance_logging()
    example_contextual_logging()
    example_error_logging()
    example_different_log_levels()
    example_module_loggers()

    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
