---
title: "Caching System"
weight: 20
---


## Overview

The RE-cue caching system speeds up re-runs of analysis by storing results from previous analyses. When you run analysis on the same codebase again, cached results are retrieved for files that haven't changed, dramatically reducing analysis time.

## Features

### File-Level Caching
- Each file's analysis results are cached individually
- Based on SHA-256 hash of file contents
- Automatic cache invalidation when files change

### Multiple Analysis Types
- Support for caching different types of analysis per file
- Examples: endpoints, models, services, use cases
- Each analysis type is cached separately

### Cache Persistence
- Cache is stored in JSON format on disk
- Survives across runs and system restarts
- Located in `<project>/specs/001-reverse/.cache/`

### Cache Statistics
- Track cache hits and misses
- Monitor cache size and entry count
- Calculate hit rate percentage
- View oldest and newest entries

### Automatic Cleanup
- Remove expired entries (if TTL is set)
- Remove invalid entries (deleted or changed files)
- Configurable maximum cache size

## Usage

### Basic Usage

By default, caching is **enabled** when you run analysis:

```bash
# Caching is enabled by default
recue --spec --description "my project"
```

### Disable Caching

To disable caching for a specific run:

```bash
recue --no-cache --spec --description "my project"
```

### Clear Cache

To clear all cached results before running analysis:

```bash
recue --clear-cache --spec --description "my project"
```

### View Cache Statistics

To view current cache statistics:

```bash
recue --cache-stats
```

Output example:
```
============================================================
CACHE STATISTICS
============================================================
Cache File:        /path/to/project/specs/001-reverse/.cache/analysis_cache.json
Total Entries:     150
Cache Size:        2,456,789 bytes
Cache Hits:        120
Cache Misses:      30
Hit Rate:          80.0%
Oldest Entry:      2025-11-23 10:15:30
Newest Entry:      2025-11-24 00:30:45
============================================================
```

### Clean Up Cache

To remove expired and invalid cache entries:

```bash
recue --cleanup-cache
```

## How It Works

### 1. File Analysis

When a file is analyzed:
1. Compute SHA-256 hash of file contents
2. Check if hash exists in cache for this analysis type
3. If found and valid, return cached result
4. If not found, analyze file and cache result

### 2. Cache Validation

For each cached entry, the system:
- Checks if the file still exists
- Computes current file hash
- Compares with cached hash
- Invalidates entry if hash differs

### 3. Cache Storage

Cache is stored as JSON with structure:
```json
{
  "version": "1.0",
  "timestamp": "2025-11-24T00:30:45.123456",
  "entries": {
    "file_path:analysis_type": {
      "file_path": "/absolute/path/to/file.py",
      "file_hash": "abc123...",
      "timestamp": 1732412445.123,
      "result": { ... },
      "metadata": { ... }
    }
  },
  "statistics": {
    "hits": 120,
    "misses": 30,
    "total_entries": 150
  }
}
```

## Configuration

### In Code

When creating an analyzer programmatically:

```python
from reverse_engineer.optimized_analyzer import OptimizedAnalyzer

analyzer = OptimizedAnalyzer(
    repo_root=repo_path,
    enable_caching=True,        # Enable/disable caching
    enable_incremental=True,    # Works alongside caching
    enable_parallel=True,       # Independent optimization
    verbose=True
)
```

### Cache Manager Options

For advanced usage, you can configure the cache manager:

```python
from reverse_engineer.cache_manager import CacheManager

cache = CacheManager(
    cache_dir=Path("my_cache"),
    cache_name="custom_cache",
    ttl_seconds=3600,           # 1 hour TTL
    max_entries=1000            # Limit to 1000 entries
)
```

## Performance Benefits

### Typical Speedup

- **First run**: No cache, full analysis
- **Second run**: ~5-10x faster for unchanged files
- **After small changes**: Only changed files re-analyzed

### Example Scenario

Project with 500 Python files:
- First run: 120 seconds
- Modify 10 files
- Second run: ~15 seconds (10 files analyzed, 490 from cache)
- Speedup: **8x faster**

## Integration with Other Optimizations

The caching system works alongside other optimizations:

### With Incremental Analysis
- **Incremental**: Skips files based on modification time
- **Caching**: Retrieves results from previous runs
- **Together**: Maximum performance, minimal re-work

### With Parallel Processing
- Cache lookups are fast (no parallel needed)
- Only files needing analysis use parallel processing
- Reduces CPU usage when many files are cached

## Cache Maintenance

### Automatic Maintenance

The cache automatically:
- Validates entries on access
- Removes entries for deleted files
- Updates entries for changed files

### Manual Maintenance

Periodically run cleanup:
```bash
# Remove invalid entries
recue --cleanup-cache

# Or clear everything and start fresh
recue --clear-cache
```

### Cache Location

Cache files are stored in:
```
<project-root>/
└── specs/
    └── 001-reverse/
        └── .cache/
            └── analysis_cache.json
```

To manually delete cache:
```bash
rm -rf specs/001-reverse/.cache/
```

## Troubleshooting

### Cache Not Working

If cache doesn't seem to work:
1. Check if caching is enabled (default: yes)
2. Verify cache directory exists and is writable
3. Check for file permission issues
4. View cache stats to see hit/miss rate

### Cache Taking Too Much Space

If cache grows too large:
1. Use `--cleanup-cache` to remove invalid entries
2. Use `--clear-cache` to start fresh
3. Consider setting `max_entries` in code

### Incorrect Results from Cache

If you suspect cache has stale data:
1. Use `--clear-cache` to invalidate all entries
2. Run analysis again to rebuild cache
3. File hash validation should prevent this

## Best Practices

### 1. Enable by Default
Leave caching enabled unless you have specific reasons to disable it.

### 2. Periodic Cleanup
Run cleanup monthly or after major refactoring:
```bash
recue --cleanup-cache
```

### 3. Fresh Start After Major Changes
After major codebase restructuring:
```bash
recue --clear-cache --spec --description "after refactor"
```

### 4. Monitor Statistics
Check cache effectiveness periodically:
```bash
recue --cache-stats
```

### 5. Combine with Other Optimizations
Use caching with incremental and parallel processing:
```bash
# All optimizations enabled (default)
recue --spec --description "optimized run"
```

## Advanced Topics

### Multiple Analysis Types

Different analysis types can be cached for the same file:

```python
# Cache endpoints analysis
analyzer.process_files_optimized(
    files,
    endpoint_processor,
    analysis_type="endpoints"
)

# Cache models analysis (separate cache)
analyzer.process_files_optimized(
    files,
    model_processor,
    analysis_type="models"
)
```

### Custom Cache Keys

The cache key format is:
```
<absolute_file_path>:<analysis_type>
```

This ensures different analysis types don't conflict.

### Cache Statistics API

Access statistics programmatically:

```python
stats = analyzer.cache_manager.get_statistics()
print(f"Hit rate: {stats.hit_rate:.1f}%")
print(f"Total entries: {stats.total_entries}")
```

## See Also

- [Performance Optimizations](../README-PYTHON.md#performance-optimizations)
- [Incremental Analysis](../README-PYTHON.md#incremental-analysis)
- [Parallel Processing](../README-PYTHON.md#parallel-processing)
