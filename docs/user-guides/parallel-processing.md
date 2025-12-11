# Parallel Processing for Faster Analysis

## Overview

RE-cue automatically uses parallel processing to analyze large codebases faster by utilizing multiple CPU cores. This feature is enabled by default and requires no configuration for most users.

## Quick Start

### Default Behavior (Recommended)

Simply run your analysis as usual:

```bash
reverse-engineer --use-cases
```

RE-cue will automatically:
- Detect the number of CPU cores
- Use parallel processing for projects with 10+ files
- Fall back to sequential processing for smaller projects

### Performance Tips

For large projects (100+ files):

```bash
# Let RE-cue use all CPU cores (default)
reverse-engineer --use-cases --verbose
```

For resource-constrained systems:

```bash
# Limit to 2 worker processes
reverse-engineer --use-cases --max-workers 2
```

For debugging or troubleshooting:

```bash
# Disable parallel processing for clearer error messages
reverse-engineer --use-cases --no-parallel --verbose
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--parallel` | Enable parallel processing | Enabled |
| `--no-parallel` | Disable parallel processing | - |
| `--max-workers N` | Set maximum worker processes | CPU count |

## When Does It Help?

### Most Beneficial For

- **Large codebases**: 50+ files benefit significantly
- **Complex projects**: Spring Boot, Django, Rails applications
- **Multi-module projects**: Multiple services or microservices
- **Modern hardware**: Systems with 4+ CPU cores

### Minimal Benefit For

- **Small projects**: Less than 10 files (auto-disabled)
- **Simple structures**: Single-file applications
- **Limited hardware**: Single-core or memory-constrained systems

## Expected Speedup

Based on benchmarks:

| Project Size | Sequential | Parallel (4 cores) | Speedup |
|--------------|------------|-------------------|---------|
| 10 files     | 0.5s       | 0.6s              | 0.8x    |
| 50 files     | 2.5s       | 1.2s              | 2.1x    |
| 100 files    | 5.0s       | 1.8s              | 2.8x    |
| 500 files    | 25.0s      | 7.5s              | 3.3x    |

*Note: Actual performance varies based on hardware and project complexity*

## Troubleshooting

### Slower Performance with Parallel Processing

If parallel processing seems slower:

1. Check project size - small projects have overhead
2. Disable for projects under 20 files: `--no-parallel`
3. Monitor system resources during analysis

### Out of Memory Errors

If you encounter memory issues:

1. Reduce worker count: `--max-workers 2`
2. Close other applications during analysis
3. Use sequential processing: `--no-parallel`

### Inconsistent Results

Parallel processing should produce identical results to sequential. If you notice differences:

1. Run again with sequential: `--no-parallel`
2. Compare outputs carefully
3. Report issue with project details

## Examples

### Standard Analysis

```bash
# Analyze project with default settings
reverse-engineer --use-cases /path/to/project
```

### Large Project Optimization

```bash
# Analyze large codebase with maximum parallelism
reverse-engineer --use-cases \
  --parallel \
  --cache \
  --incremental \
  --verbose \
  /path/to/large/project
```

### Resource-Constrained System

```bash
# Analyze with limited resources
reverse-engineer --use-cases \
  --max-workers 2 \
  --no-cache \
  /path/to/project
```

### Debugging Mode

```bash
# Analyze with detailed error messages
reverse-engineer --use-cases \
  --no-parallel \
  --verbose \
  /path/to/project
```

## Combining with Other Optimizations

Parallel processing works well with other performance features:

### With Caching

```bash
# First run: analyze and cache results
reverse-engineer --use-cases --parallel --cache

# Subsequent runs: use cached results for unchanged files
reverse-engineer --use-cases --parallel --cache
```

### With Incremental Analysis

```bash
# Only analyze changed files
reverse-engineer --use-cases --parallel --incremental
```

### Complete Optimization Stack

```bash
# Use all performance features together
reverse-engineer --use-cases \
  --parallel \
  --cache \
  --incremental \
  --max-workers 4 \
  --verbose
```

## Technical Details

For developers and advanced users:

- **Technology**: Python `multiprocessing.ProcessPoolExecutor`
- **Isolation**: Each worker runs in separate process (no shared state issues)
- **Pickling**: Module-level functions ensure compatibility
- **Error Handling**: Per-file errors don't stop overall processing
- **Progress**: Real-time progress bar shows completion status

## Learn More

- [Multi-Process Analysis Developer Guide](../developer-guides/multiprocess-analysis-guide.md)
- [Performance Benchmarks](../developer-guides/performance-benchmarks.md)
- [Large Codebase Integration](../developer-guides/large-codebase-testing.md)

## Feedback

If you experience issues or have suggestions:

1. Check [Troubleshooting](#troubleshooting) section above
2. Review [GitHub Issues](https://github.com/cue-3/re-cue/issues)
3. Submit detailed bug report with:
   - Project size (number of files)
   - Command used
   - System specifications (CPU cores, RAM)
   - Error messages or unexpected behavior
