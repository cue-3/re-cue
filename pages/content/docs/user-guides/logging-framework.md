---
title: "Logging Framework Guide"
weight: 20
---


## Overview

RE-cue includes a comprehensive structured logging framework that provides:

- **Configurable log levels** - Set verbosity from DEBUG to CRITICAL
- **Multiple output formats** - Text or JSON for log aggregation systems
- **File rotation** - Automatic log file management with size limits
- **Performance logging** - Built-in context manager for timing operations
- **Error tracking** - Rich exception information with context

## Quick Start

### Basic Usage

The simplest way to use logging is through the command-line interface:

```bash
# Enable verbose logging
recue --spec --verbose

# Write logs to a file
recue --spec --log-file recue.log

# Use JSON format for structured logging
recue --spec --log-format json --log-file recue.json

# Set log level to DEBUG
recue --spec --log-level DEBUG
```

### In Code

```python
from reverse_engineer.logging_config import configure_logging, get_logger

# Configure logging at application startup
configure_logging(
    level="INFO",
    log_file="myapp.log",
    format_type="text",
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5
)

# Get a logger for your module
logger = get_logger(__name__)

# Log messages
logger.info("Starting analysis")
logger.debug("Processing file: %s", filename)
logger.warning("Deprecated feature used")
logger.error("Failed to process file", exc_info=True)
```

## Configuration Options

### Log Levels

Log levels control which messages are output. From least to most severe:

- `DEBUG` - Detailed information for diagnosing problems
- `INFO` - General informational messages (default)
- `WARNING` - Warning messages for potentially problematic situations
- `ERROR` - Error messages for failures that don't stop execution
- `CRITICAL` - Critical errors that may cause application failure

### Output Formats

#### Text Format (Default)

Human-readable format suitable for console and text log files:

```
2025-12-22 16:50:56 [INFO] reverse_engineer.analyzer - Starting project analysis
2025-12-22 16:50:57 [DEBUG] reverse_engineer.analyzer - Found 42 Java files
2025-12-22 16:50:58 [INFO] reverse_engineer.analyzer - Analysis complete
```

#### JSON Format

Machine-readable format suitable for log aggregation systems like Elasticsearch, Splunk, or CloudWatch:

```json
{
  "timestamp": "2025-12-22T16:50:56.123456Z",
  "level": "INFO",
  "logger": "reverse_engineer.analyzer",
  "message": "Starting project analysis",
  "module": "analyzer",
  "function": "analyze",
  "line": 42
}
```

JSON logs can include additional structured data:

```json
{
  "timestamp": "2025-12-22T16:50:57.234567Z",
  "level": "DEBUG",
  "logger": "reverse_engineer.analyzer",
  "message": "Performance: analyze_endpoints completed in 123.45ms",
  "module": "analyzer",
  "function": "analyze_endpoints",
  "line": 215,
  "performance": {
    "operation": "analyze_endpoints",
    "duration_ms": 123.45,
    "file_count": 42
  }
}
```

### File Rotation

Log rotation prevents log files from growing indefinitely:

```bash
# Rotate when log reaches 10MB, keep 5 backups
recue --spec --log-file app.log --log-max-bytes 10485760 --log-backup-count 5
```

When the log file reaches the maximum size, it is rotated:
- `app.log` → `app.log.1`
- `app.log.1` → `app.log.2`
- ...
- `app.log.4` → `app.log.5` (oldest log is deleted)

### CLI Arguments

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `--log-level` | DEBUG, INFO, WARNING, ERROR, CRITICAL | INFO | Set logging level |
| `--log-file` | path | (none) | Write logs to file with rotation |
| `--log-format` | text, json | text | Log output format |
| `--log-max-bytes` | number | 10485760 | Max log file size before rotation (bytes) |
| `--log-backup-count` | number | 5 | Number of rotated log files to keep |
| `--no-console-log` | flag | false | Disable console logging |

## Advanced Features

### Performance Logging

Track operation performance with the `PerformanceLogger` context manager:

```python
from reverse_engineer.logging_config import get_logger, PerformanceLogger

logger = get_logger(__name__)

with PerformanceLogger(logger, "analyze_endpoints", context={"file_count": 42}):
    # Code to measure
    endpoints = analyze_endpoints(files)
```

This automatically logs:
- Operation name
- Duration in milliseconds
- Success or failure status
- Any additional context

Output (text):
```
2025-12-22 16:50:58 [DEBUG] reverse_engineer.analyzer - Performance: analyze_endpoints completed in 123.45ms
```

Output (JSON):
```json
{
  "timestamp": "2025-12-22T16:50:58.345678Z",
  "level": "DEBUG",
  "logger": "reverse_engineer.analyzer",
  "message": "Performance: analyze_endpoints completed in 123.45ms",
  "performance": {
    "operation": "analyze_endpoints",
    "duration_ms": 123.45,
    "file_count": 42
  }
}
```

### Logging with Context

Add structured context to log messages:

```python
from reverse_engineer.logging_config import log_info

log_info(
    "User action completed",
    context={
        "user": "alice",
        "action": "analyze_project",
        "project": "/path/to/project"
    }
)
```

JSON output includes the context:
```json
{
  "timestamp": "2025-12-22T16:51:00.123456Z",
  "level": "INFO",
  "logger": "reverse_engineer",
  "message": "User action completed",
  "context": {
    "user": "alice",
    "action": "analyze_project",
    "project": "/path/to/project"
  }
}
```

### Exception Logging

Log exceptions with full traceback:

```python
from reverse_engineer.logging_config import log_error

try:
    result = risky_operation()
except Exception as e:
    log_error("Operation failed", exc_info=True)
```

This includes the full exception traceback in both text and JSON formats.

### Module-Specific Loggers

Get loggers for specific modules to track the source of log messages:

```python
from reverse_engineer.logging_config import get_logger

logger = get_logger(__name__)  # Creates logger "reverse_engineer.<module_name>"
logger.info("Module-specific message")
```

All module loggers share the same configuration but have distinct names for filtering.

## Integration Examples

### With Existing Code

The logging framework is backward compatible with existing `log_info()` calls:

```python
from reverse_engineer.utils import log_info

# Old style - still works
log_info("Analysis started", verbose=True)

# New style - with structured logging
from reverse_engineer.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Analysis started")
```

### Configuration File

You can configure logging in `.recue.yaml`:

```yaml
logging:
  level: INFO
  file: recue.log
  format: json
  max_bytes: 10485760
  backup_count: 5
  console: true
```

### Environment Variables

Override logging configuration with environment variables:

```bash
export RECUE_LOG_LEVEL=DEBUG
export RECUE_LOG_FILE=debug.log
export RECUE_LOG_FORMAT=json

recue --spec
```

## Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information
  ```python
  logger.debug("Processing file %s with %d lines", filename, line_count)
  ```

- **INFO**: General progress and state changes
  ```python
  logger.info("Analysis completed: %d endpoints found", count)
  ```

- **WARNING**: Recoverable issues that may indicate problems
  ```python
  logger.warning("Deprecated API pattern detected in %s", filename)
  ```

- **ERROR**: Errors that prevent specific operations
  ```python
  logger.error("Failed to parse file %s", filename, exc_info=True)
  ```

- **CRITICAL**: Severe errors that may crash the application
  ```python
  logger.critical("Database connection failed - cannot continue")
  ```

### 2. Include Context in Log Messages

Good:
```python
logger.info("Endpoint analysis complete", extra={
    "context": {
        "endpoint_count": 42,
        "duration_ms": 123.45,
        "framework": "Spring Boot"
    }
})
```

Less helpful:
```python
logger.info("Analysis complete")
```

### 3. Use Performance Logging for Operations

Good:
```python
with PerformanceLogger(logger, "analyze_models", context={"model_count": len(models)}):
    analyze_models(models)
```

Manual (more error-prone):
```python
start = time.time()
analyze_models(models)
logger.debug("Models analyzed in %.2f seconds", time.time() - start)
```

### 4. Structure Log Messages for Parsing

When using JSON format, structure your messages consistently:

```python
# Good - action-first, details in context
logger.info("File processed", extra={
    "context": {
        "file": filename,
        "size_bytes": size,
        "duration_ms": duration
    }
})

# Avoid - unstructured string concatenation
logger.info(f"Processed {filename} ({size} bytes) in {duration}ms")
```

### 5. Don't Log Sensitive Information

Avoid logging:
- Passwords, API keys, tokens
- Personal identifiable information (PII)
- Credit card numbers
- Internal system paths (in production)

## Troubleshooting

### Logs Not Appearing

If logs aren't appearing:

1. Check log level configuration:
   ```bash
   recue --spec --log-level DEBUG
   ```

2. Verify logger is configured:
   ```python
   import logging
   logger = logging.getLogger("reverse_engineer")
   print(f"Logger level: {logger.level}")
   print(f"Handlers: {logger.handlers}")
   ```

3. Check file permissions if using file logging

### Performance Impact

Logging has minimal performance impact when:
- Using appropriate log levels (avoid DEBUG in production)
- File rotation is configured properly
- JSON formatting is only used when needed

### Log File Size

Control log file size with:
```bash
# Smaller logs, fewer backups
recue --spec --log-max-bytes 1048576 --log-backup-count 3

# Larger logs, more backups
recue --spec --log-max-bytes 52428800 --log-backup-count 10
```

## Future Enhancements

Planned improvements to the logging framework:

- [ ] Time-based rotation (daily, weekly)
- [ ] Compression of rotated logs
- [ ] Remote logging to syslog/rsyslog
- [ ] Integration with monitoring systems
- [ ] Custom formatters for different outputs
- [ ] Log sampling for high-volume scenarios
