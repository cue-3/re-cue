# Performance Benchmarks and Regression Testing

This document describes the performance benchmarking and regression testing infrastructure for RE-cue.

## Overview

The performance testing framework consists of:

1. **Benchmark Tests** (`test_performance_benchmarks.py`) - Measure and track performance metrics
2. **Regression Tests** (`test_performance_regression.py`) - Detect performance regressions
3. **Baseline Metrics** (`performance_baseline.json`) - Expected performance standards
4. **Benchmark Runner** (`run_benchmarks.py`) - Automated benchmark execution

## Running Benchmarks

### Run All Benchmarks and Regression Tests

```bash
cd reverse-engineer-python
python3 tests/run_benchmarks.py
```

### Run Only Benchmarks

```bash
python3 tests/run_benchmarks.py --benchmark-only
```

### Run Only Regression Tests

```bash
python3 tests/run_benchmarks.py --regression-only
```

### Save Results to JSON

```bash
python3 tests/run_benchmarks.py --output results/benchmark-$(date +%Y%m%d).json
```

### Update Baseline Metrics

After verifying that current performance is acceptable:

```bash
python3 tests/run_benchmarks.py --update-baseline
```

## Benchmark Metrics

### 1. Project Analysis Performance

Measures analysis time for projects of different sizes:

- **Small Project** (10 files, ~500 lines)
  - Expected: < 2 seconds
  - Throughput: > 5 files/second

- **Medium Project** (50 files, ~2500 lines)
  - Expected: < 5 seconds
  - Throughput: > 10 files/second

- **Large Project** (100 files, ~5000 lines)
  - Expected: < 10 seconds
  - Throughput: > 10 files/second

### 2. Parallel Processing Speedup

Measures the effectiveness of parallel processing:

- **Test Configuration**: 40 files, 4 workers
- **Expected Speedup**: > 1.2x faster than sequential
- **Typical Speedup**: 2-4x depending on I/O vs CPU bound work

### 3. Cache Effectiveness

Measures caching performance:

- **Cache Speedup**: > 1.5x faster on second run
- **Cache Hit Rate**: > 95% on warm cache
- **Typical Speedup**: 3-5x for cached files

### 4. File Tracking Performance

Measures incremental analysis efficiency:

- **Tracking 100 files**: < 1 second
- **Change detection**: < 0.5 seconds

### 5. Cache Operations Performance

Measures cache read/write performance:

- **Write Performance**: > 50 operations/second
- **Read Performance**: > 100 operations/second
- **Persistence**: < 1 second for 50 entries

### 6. Parallel Processor Overhead

Measures overhead of parallel processing infrastructure:

- **Configuration**: 20 files, 1 worker
- **Overhead**: Process creation and management overhead
- **Note**: Overhead is amortized across many files

## Performance Baselines

Baseline metrics are stored in `tests/performance_baseline.json`:

```json
{
  "small_project_analysis": {
    "max_duration": 2.0,
    "min_throughput": 5.0
  },
  "medium_project_analysis": {
    "max_duration": 5.0,
    "min_throughput": 10.0
  },
  "large_project_analysis": {
    "max_duration": 10.0,
    "min_throughput": 10.0
  },
  "parallel_speedup": {
    "min_speedup": 1.2
  },
  "cache_speedup": {
    "min_speedup": 1.5,
    "min_hit_rate": 95.0
  },
  "file_tracking": {
    "max_track_time": 1.0,
    "max_check_time": 0.5
  },
  "cache_operations": {
    "max_write_time": 1.0,
    "max_read_time": 0.5,
    "min_write_throughput": 50.0,
    "min_read_throughput": 100.0
  }
}
```

## Regression Tests

Regression tests compare current performance against baseline metrics and fail if:

- Analysis takes longer than the baseline maximum duration
- Throughput falls below the baseline minimum
- Parallel speedup degrades below acceptable levels
- Cache effectiveness decreases significantly

### Running Regression Tests in CI/CD

Add to your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Run Performance Regression Tests
  run: |
    cd reverse-engineer-python
    python3 tests/run_benchmarks.py --regression-only --verbose
```

## Understanding Results

### Benchmark Output

```
======================================================================
PERFORMANCE BENCHMARK RESULTS
======================================================================
Small Project Analysis (10 files, ~500 lines):
  Duration: 0.001s
  Throughput: 8190.4 items/s
  Metadata: {'file_count': 10, 'result_count': 10}
----------------------------------------------------------------------
```

**Key Metrics:**
- **Duration**: Total time taken for the operation
- **Throughput**: Items processed per second
- **Metadata**: Additional context-specific metrics

### Interpreting Speedup

- **Speedup < 1.0**: Parallel processing is slower (overhead exceeds benefit)
- **Speedup 1.0-2.0**: Modest improvement (I/O bound or small dataset)
- **Speedup 2.0-4.0**: Good parallelization (balanced workload)
- **Speedup > 4.0**: Excellent parallelization (CPU bound work)

### Cache Hit Rate

- **0-20%**: Poor cache effectiveness, check file change detection
- **20-50%**: Moderate effectiveness, many files are changing
- **50-80%**: Good effectiveness for active development
- **80-95%**: Very good, stable codebase
- **>95%**: Excellent, minimal changes between runs

## Performance Optimization Guidelines

### When to Use Parallel Processing

- **Use when**: Processing 10+ files with CPU-bound operations
- **Skip when**: Processing < 10 files or I/O is the bottleneck
- **Optimal workers**: 4-8 for most cases, up to 16 for large datasets

### When to Use Caching

- **Use when**: Running analysis multiple times on same codebase
- **Skip when**: One-time analysis or rapidly changing code
- **Cache invalidation**: Automatic via file content hash

### When to Use Incremental Analysis

- **Use when**: Large codebase with infrequent changes
- **Skip when**: Most files change frequently
- **Best for**: CI/CD environments with minimal diffs

## Troubleshooting Performance Issues

### Slow Analysis

1. Check file count: `find . -name "*.java" | wc -l`
2. Enable parallel processing: `--enable-parallel`
3. Enable caching: `--enable-caching`
4. Check disk I/O: Use SSD for better performance

### Cache Not Effective

1. Verify cache is enabled: Check `--enable-caching` flag
2. Check cache statistics: Look for high miss rate
3. Verify file hashes: Content-based, so format changes trigger miss
4. Check cache directory permissions

### Parallel Processing Not Helping

1. Check file count: Need > 10 files for parallel
2. Verify CPU usage: Should see multiple cores active
3. Check I/O bottleneck: SSD helps with parallel I/O
4. Reduce worker count if system is overloaded

## Extending the Benchmarks

To add new benchmarks:

1. Add test method to `TestPerformanceBenchmarks` class
2. Use `PerformanceBenchmarkResult` to capture metrics
3. Add baseline expectations to `performance_baseline.json`
4. Add corresponding regression test in `TestPerformanceRegression`

Example:

```python
def test_benchmark_new_feature(self):
    """Benchmark: New feature performance."""
    # Setup
    files = self._create_test_files(count=20)
    
    # Measure
    start = time.time()
    result = perform_operation(files)
    duration = time.time() - start
    
    # Record
    benchmark = PerformanceBenchmarkResult(
        name="New Feature (20 files)",
        duration=duration,
        throughput=len(files) / duration,
        metadata={"additional": "metrics"}
    )
    self.results.append(benchmark)
    
    # Assert
    self.assertLess(duration, 1.0, "Should complete in < 1s")
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install Dependencies
        run: |
          cd reverse-engineer-python
          pip install -e .
      - name: Run Benchmarks
        run: |
          cd reverse-engineer-python
          python3 tests/run_benchmarks.py --output results.json
      - name: Run Regression Tests
        run: |
          cd reverse-engineer-python
          python3 tests/run_benchmarks.py --regression-only
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: reverse-engineer-python/results.json
```

### GitLab CI

```yaml
performance:
  stage: test
  script:
    - cd reverse-engineer-python
    - pip install -e .
    - python3 tests/run_benchmarks.py --regression-only
  artifacts:
    paths:
      - reverse-engineer-python/results.json
    when: always
```

## Performance Monitoring

### Track Performance Over Time

```bash
# Save results with timestamp
DATE=$(date +%Y%m%d-%H%M%S)
python3 tests/run_benchmarks.py --output "results/benchmark-${DATE}.json"
```

### Compare Results

```python
import json
from pathlib import Path

# Load two result files
with open("results/benchmark-20240101.json") as f:
    old = json.load(f)
with open("results/benchmark-20240115.json") as f:
    new = json.load(f)

# Compare specific metrics
for old_b, new_b in zip(old["benchmarks"], new["benchmarks"]):
    if old_b["name"] == new_b["name"]:
        old_dur = old_b["duration_seconds"]
        new_dur = new_b["duration_seconds"]
        change = ((new_dur - old_dur) / old_dur) * 100
        print(f"{old_b['name']}: {change:+.1f}%")
```

## Related Documentation

- [Performance Optimization Guide](./performance-optimization.md) - ENH-PERF-001 implementation
- [Large Codebase Analysis](./large-codebase-optimization.md) - Optimization strategies
- [Caching System](./caching-system.md) - Cache implementation details

## Support

For questions or issues:

1. Check benchmark output for specific failures
2. Review baseline metrics in `performance_baseline.json`
3. Run with `--verbose` for detailed output
4. File an issue with benchmark results attached
