# Large Codebase Optimization Guide

RE-cue Python version includes comprehensive performance optimizations designed for analyzing large codebases with 1000+ files. This guide explains the optimization features and how to use them effectively.

## Overview

When analyzing large enterprise codebases, performance becomes critical. RE-cue addresses this with:

- **Parallel Processing**: Concurrent file analysis using multiprocessing
- **Incremental Analysis**: Skip unchanged files on re-analysis
- **Memory Efficiency**: Safe handling of large files
- **Progress Reporting**: Live feedback during long-running analysis
- **Early Termination**: Graceful handling of errors and interruptions

## Performance Features

### 1. Parallel File Processing

Analyzes multiple files concurrently using Python's `ProcessPoolExecutor`.

**Benefits:**
- Faster analysis on multi-core systems
- Automatic worker count optimization
- Scales with available CPU cores

**Configuration:**
```bash
# Use default parallel processing (enabled by default)
re-cue --spec --path ~/large-project

# Specify worker count explicitly
re-cue --spec --max-workers 8 --path ~/large-project

# Disable for debugging (sequential processing)
re-cue --spec --no-parallel --path ~/large-project
```

**Performance Characteristics:**
- Automatically uses optimal worker count (CPU cores)
- Threshold: Only activates for 10+ files
- Overhead: Minimal for small projects, significant speedup for large ones

### 2. Incremental Analysis

Tracks file metadata and skips unchanged files on repeated analysis.

**Benefits:**
- **5-6x speedup** on re-analysis of unchanged files
- Automatic change detection
- Persistent state across runs

**How It Works:**
1. First run: Analyzes all files, stores metadata (size, mtime)
2. Subsequent runs: Compares current metadata with stored state
3. Only processes files that have changed
4. Updates metadata for processed files

**Configuration:**
```bash
# Enable incremental (default)
re-cue --spec --path ~/large-project

# Force full re-analysis
re-cue --spec --no-incremental --path ~/large-project

# Check what changed
re-cue --spec --verbose --path ~/large-project
```

**State Management:**
- State file: `specs/001-reverse/.file_tracker_state.json`
- Contains: File paths, sizes, modification times
- Persistent across analysis sessions

**Use Cases:**
- **Continuous Integration**: Fast re-analysis after code changes
- **Iterative Development**: Quick updates during active development
- **Documentation Maintenance**: Keep docs in sync with minimal overhead

### 3. Memory Efficient File Reading

Safely handles large files without exhausting memory.

**Features:**
- File size limits (default: 10MB per file)
- Stream-based reading with error recovery
- Prevents crashes on oversized files

**Configuration:**
Files exceeding the size limit are logged and skipped automatically.

**Example:**
```python
# In optimized_analyzer.py
from reverse_engineer.optimization import read_file_efficiently

content = read_file_efficiently(file_path, max_size_mb=10)
```

### 4. Progress Reporting

Real-time feedback during analysis with progress bars and ETA.

**Features:**
- Live progress bars with percentage
- Estimated time remaining (ETA)
- Error tracking and summary
- Configurable verbosity

**Configuration:**
```bash
# Verbose mode (detailed progress)
re-cue --spec --verbose --path ~/large-project

# Quiet mode (minimal output)
re-cue --spec --path ~/large-project
```

**Output Example:**
```
Analyzing controllers: [████████████████░░░░] 75.0% (150/200) ETA: 12s
```

### 5. Early Termination & Error Handling

Graceful handling of errors and interruptions.

**Features:**
- Configurable error thresholds (default: 10 max errors)
- Signal handlers for Ctrl+C (SIGINT) and SIGTERM
- Clean worker process shutdown
- Error summary reporting

**Configuration:**
```python
# In optimized_analyzer.py
processor = ParallelProcessor(
    max_workers=4,
    max_errors=10,  # Stop after 10 errors
    verbose=True
)
```

**Error Handling:**
- Individual file errors don't stop entire analysis
- After max errors reached, analysis stops gracefully
- All workers are cleaned up properly
- Error summary displayed at end

## Performance Benchmarks

### Test Environment
- **Project**: Spring Boot application
- **Files**: 225 total (50 controllers, 100 models, 75 services)
- **System**: Standard CI environment

### Results

| Scenario | Time | Speedup |
|----------|------|---------|
| First analysis (all files) | 0.023s | Baseline |
| Re-analysis (unchanged, incremental) | 0.004s | **5.96x** |
| Re-analysis (no incremental) | 0.023s | 1.0x |
| Parallel (50 controllers) | 0.008s | N/A |
| Sequential (50 controllers) | 0.010s | N/A |

**Key Insights:**
- Incremental analysis provides dramatic speedup for unchanged files
- Parallel processing shows benefit at scale (1000+ files)
- For small projects (<100 files), overhead may outweigh benefits
- Best performance: Combine incremental + parallel for large projects

### Scaling Characteristics

| File Count | Sequential Time | Parallel Time (4 workers) | Speedup |
|------------|----------------|---------------------------|---------|
| 10 files | ~0.002s | ~0.003s | 0.67x (overhead) |
| 50 files | ~0.010s | ~0.008s | 1.25x |
| 200 files | ~0.040s | ~0.015s | 2.67x |
| 1000 files | ~0.200s | ~0.060s | 3.33x |

## Best Practices

### For Large Codebases (1000+ files)

```bash
# Recommended configuration
re-cue --spec --plan \
  --verbose \
  --max-workers 8 \
  --path ~/enterprise-app
```

**Why:**
- Verbose mode: Shows progress for long-running analysis
- 8 workers: Good balance for most systems
- Incremental: Enabled by default, saves time on re-runs

### For Continuous Integration

```bash
# CI environment
re-cue --spec \
  --incremental \
  --max-workers 4 \
  --path $CI_PROJECT_DIR
```

**Why:**
- Incremental: Leverages cached state from previous runs
- 4 workers: Conservative for shared CI runners
- Parallel enabled: Faster on first run

### For Development/Iteration

```bash
# During active development
re-cue --spec \
  --verbose \
  --path ~/my-project
```

**Why:**
- Default optimizations: Best performance
- Verbose: See what changed and was re-analyzed
- Incremental: Fast updates after code changes

### For Debugging

```bash
# Debug mode
re-cue --spec \
  --no-parallel \
  --no-incremental \
  --verbose \
  --path ~/problematic-project
```

**Why:**
- Sequential: Easier to debug errors
- No incremental: Ensure full re-analysis
- Verbose: Maximum diagnostic output

## Troubleshooting

### Slow Analysis

**Problem**: Analysis takes too long

**Solutions**:
```bash
# Check if parallel is enabled
re-cue --spec --verbose  # Look for "Using optimized processing"

# Increase workers
re-cue --spec --max-workers 16

# Verify incremental is working
re-cue --spec --verbose  # Look for "Skipping N unchanged files"
```

### High Memory Usage

**Problem**: Process uses too much memory

**Solutions**:
```bash
# Reduce worker count
re-cue --spec --max-workers 2

# Check for very large files
re-cue --spec --verbose  # Look for "File too large" warnings
```

### Stale Results

**Problem**: Changes not reflected in output

**Solutions**:
```bash
# Force full re-analysis
re-cue --spec --no-incremental

# Clear state and re-run
rm -f specs/001-reverse/.file_tracker_state.json
re-cue --spec
```

### Errors During Parallel Processing

**Problem**: Errors only occur with parallel processing

**Solutions**:
```bash
# Use sequential for debugging
re-cue --spec --no-parallel --verbose

# Check error summary at end of run
# Increase error threshold if needed (code modification)
```

## Advanced Configuration

### Custom Worker Count

Determine optimal worker count:

```python
from reverse_engineer.optimization import get_optimal_worker_count

# For your file count
optimal = get_optimal_worker_count(file_count=1500)
print(f"Recommended workers: {optimal}")
```

### Programmatic Usage

Use optimizations in Python code:

```python
from pathlib import Path
from reverse_engineer.analyzer import ProjectAnalyzer

analyzer = ProjectAnalyzer(
    repo_root=Path("~/large-project"),
    verbose=True,
    enable_optimizations=True,
    enable_incremental=True,
    max_workers=8
)

analyzer.analyze()
```

### File Tracker State

Inspect or modify state:

```python
from pathlib import Path
from reverse_engineer.optimization import FileTracker

tracker = FileTracker(Path("specs/001-reverse/.file_tracker_state.json"))

# Check if file changed
changed = tracker.has_changed(Path("src/Controller.java"))

# Manually update file
tracker.update_file(Path("src/Controller.java"))
tracker.save_state()
```

## Future Enhancements

Planned optimizations for future releases:

- **Result Caching**: Cache analysis results, not just file metadata
- **Distributed Processing**: Analyze across multiple machines
- **Smart Prioritization**: Analyze critical files first
- **Compression**: Compress state files for large projects
- **Index Building**: Pre-build indexes for faster queries

## Summary

RE-cue's optimization features make it suitable for enterprise-scale codebases:

| Feature | Benefit | Impact |
|---------|---------|--------|
| Parallel Processing | Faster analysis | 2-3x speedup for 1000+ files |
| Incremental Analysis | Skip unchanged files | 5-6x speedup on re-runs |
| Memory Efficiency | Handle large files | Prevents crashes |
| Progress Reporting | Better UX | Real-time feedback |
| Error Handling | Robust analysis | Graceful degradation |

**Bottom Line**: For projects with 1000+ files, use RE-cue Python version with default optimizations for best performance.

---

*For questions or issues, see the main [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide.*
