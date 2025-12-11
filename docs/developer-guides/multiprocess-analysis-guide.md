# Multi-Process Analysis Guide (ENH-PERF-004)

## Overview

RE-cue now supports multi-process analysis for CPU-bound tasks, significantly improving performance when analyzing large codebases. This enhancement leverages Python's `multiprocessing` module to process multiple files concurrently.

## Features

- **Parallel File Processing**: Framework analyzers can now process multiple files in parallel using multiple CPU cores
- **Configurable Worker Count**: Control the number of worker processes based on your system resources
- **Automatic Fallback**: Seamlessly falls back to sequential processing when parallel processing is disabled or unavailable
- **Error Resilience**: Handles errors gracefully without affecting other parallel tasks
- **Consistent Results**: Produces identical results whether using parallel or sequential processing

## Usage

### Command Line Interface

Multi-process analysis is **enabled by default**. You can control it using these flags:

```bash
# Use parallel processing (default)
reverse-engineer --use-cases

# Explicitly enable parallel processing
reverse-engineer --use-cases --parallel

# Disable parallel processing
reverse-engineer --use-cases --no-parallel

# Set maximum number of workers (default: CPU count)
reverse-engineer --use-cases --max-workers 4
```

### Programmatic Usage

When using framework analyzers directly:

```python
from pathlib import Path
from reverse_engineer.frameworks.java_spring.analyzer import JavaSpringAnalyzer

# Enable parallel processing (default)
analyzer = JavaSpringAnalyzer(
    repo_root=Path("/path/to/project"),
    verbose=True,
    enable_parallel=True,
    max_workers=None,  # Use CPU count
)

# Disable parallel processing
analyzer = JavaSpringAnalyzer(
    repo_root=Path("/path/to/project"),
    verbose=True,
    enable_parallel=False,
)

# Custom worker count
analyzer = JavaSpringAnalyzer(
    repo_root=Path("/path/to/project"),
    verbose=True,
    enable_parallel=True,
    max_workers=4,
)

# Run analysis
endpoints = analyzer.discover_endpoints()
models = analyzer.discover_models()
services = analyzer.discover_services()
```

## Performance Characteristics

### When to Use Parallel Processing

Parallel processing is most beneficial when:

- **Large codebases**: Projects with hundreds of files
- **Complex analysis**: Each file requires significant processing
- **Multi-core systems**: Systems with multiple CPU cores available
- **I/O bound tasks**: When file reading dominates processing time

### When to Disable Parallel Processing

Consider disabling parallel processing when:

- **Small projects**: Less than 10 files (overhead exceeds benefit)
- **Limited resources**: Systems with limited CPU or memory
- **Debugging**: Sequential processing provides clearer error messages
- **Consistency testing**: Comparing exact execution order

### Performance Guidelines

The analyzer uses intelligent defaults:

- **Threshold**: Parallel processing activates only for 10+ files
- **Worker Count**: Defaults to CPU count, capped at 16 workers
- **Optimal Range**: 2-8 workers typically provides best performance

## Implementation Details

### Module-Level Processor Functions

Framework analyzers use module-level processor functions to ensure compatibility with multiprocessing:

```python
# Module-level function (picklable)
def _process_controller_file(file_path: Path) -> dict[str, Any]:
    """Process a Spring controller file to extract endpoints."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    # ... processing logic ...
    return {"file": str(file_path), "endpoints": endpoints}

# In analyzer class
class JavaSpringAnalyzer(BaseAnalyzer):
    def discover_endpoints(self) -> list[Endpoint]:
        # Collect all files
        all_controller_files = [...]
        
        # Process in parallel
        results = self._process_files_parallel(
            all_controller_files,
            _process_controller_file,
            desc="Processing controllers",
        )
        
        # Convert results to domain objects
        for result in results:
            # ... create Endpoint objects ...
```

### BaseAnalyzer Integration

All framework analyzers inherit parallel processing support from `BaseAnalyzer`:

```python
class BaseAnalyzer(ABC):
    def __init__(
        self,
        repo_root: Path,
        verbose: bool = False,
        enable_parallel: bool = True,
        max_workers: Optional[int] = None,
    ):
        # ... initialization ...
        self.enable_parallel = enable_parallel
        self.max_workers = max_workers
    
    def _process_files_parallel(
        self,
        files: list[Path],
        processor_func: Callable[[Path], Any],
        desc: str = "Processing files",
    ) -> list[Any]:
        """Process files in parallel using multiprocessing."""
        # Delegates to OptimizedAnalyzer if available
        # Falls back to sequential processing otherwise
```

## Supported Frameworks

Currently, the following framework analyzers support multi-process analysis:

- ✅ **Java Spring Boot** (`JavaSpringAnalyzer`)
  - Controllers
  - Models/Entities
  - Services

Additional frameworks will be updated in future releases.

## Error Handling

The multi-process analyzer handles errors gracefully:

- **Per-file errors**: Logged but don't stop overall processing
- **Max error limit**: Configurable threshold (default: 10)
- **Early termination**: Stops if too many errors occur
- **Detailed logging**: Verbose mode shows per-file errors

Example error output:

```
[INFO] Processing 50 files using 4 workers...
Processing controllers: [█████████████████████] 100.0% (50/50) ETA: 0s
⚠️  2 errors occurred during processing

Errors:
  • BadController.java: Invalid syntax at line 15
  • EmptyController.java: No endpoints found
```

## Testing

Comprehensive tests ensure reliability:

```bash
# Run multi-process analysis tests
python3 -m unittest tests.test_multiprocess_analysis -v

# Run performance benchmarks
python3 -m unittest tests.test_multiprocess_performance -v

# Run all framework integration tests
python3 -m unittest tests.test_framework_integration -v
```

## Best Practices

### 1. Use Default Settings for Most Projects

```bash
# Simple - uses sensible defaults
reverse-engineer --use-cases
```

### 2. Adjust Workers for Resource-Constrained Environments

```bash
# Limit to 2 workers on smaller systems
reverse-engineer --use-cases --max-workers 2
```

### 3. Enable Verbose Mode for Troubleshooting

```bash
# See detailed progress and errors
reverse-engineer --use-cases --verbose
```

### 4. Disable for Debugging

```bash
# Easier to trace errors sequentially
reverse-engineer --use-cases --no-parallel --verbose
```

### 5. Combine with Other Optimizations

```bash
# Use caching for faster re-runs
reverse-engineer --use-cases --parallel --cache

# Skip unchanged files
reverse-engineer --use-cases --parallel --incremental
```

## Troubleshooting

### Issue: Parallel processing is slower than sequential

**Cause**: Small number of files, high overhead

**Solution**: Let the analyzer decide (automatic threshold), or disable for very small projects

```bash
reverse-engineer --use-cases --no-parallel
```

### Issue: Out of memory errors

**Cause**: Too many workers processing large files

**Solution**: Reduce worker count

```bash
reverse-engineer --use-cases --max-workers 2
```

### Issue: Inconsistent results between runs

**Cause**: Non-deterministic processing order (should not affect final results)

**Solution**: Verify with sequential processing; file a bug if results differ

```bash
reverse-engineer --use-cases --no-parallel
```

## Future Enhancements

Planned improvements:

- [ ] Extend to all framework analyzers (Rails, Laravel, Django, etc.)
- [ ] Adaptive worker count based on file size and complexity
- [ ] Progress reporting improvements for better user feedback
- [ ] Memory-efficient processing for very large files
- [ ] Distributed processing across multiple machines

## Related Documentation

- [Performance Optimization Guide](./performance-benchmarks.md)
- [Large Codebase Integration Tests](../tests/test_large_codebase_integration.py)
- [Cache Manager Documentation](../../reverse_engineer/performance/cache_manager.py)

## Technical Details

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│ CLI / User Interface                                     │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ ProjectAnalyzer / Framework Analyzer                     │
│  - enable_parallel: bool                                 │
│  - max_workers: Optional[int]                            │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ BaseAnalyzer                                             │
│  - _get_optimized_analyzer()                             │
│  - _process_files_parallel()                             │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ OptimizedAnalyzer                                        │
│  - process_files_optimized()                             │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ ParallelProcessor                                        │
│  - ProcessPoolExecutor                                   │
│  - Progress tracking                                     │
│  - Error handling                                        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ Module-Level Processor Functions                        │
│  - _process_controller_file()                            │
│  - _process_model_file()                                 │
│  - _process_service_file()                               │
└─────────────────────────────────────────────────────────┘
```

### Execution Flow

1. **Initialization**: Analyzer initialized with `enable_parallel` and `max_workers`
2. **File Collection**: Gather all files to process (controllers, models, services)
3. **Threshold Check**: If files < 10, use sequential processing
4. **Worker Allocation**: Determine optimal worker count based on CPU cores and file count
5. **Parallel Execution**: Submit tasks to ProcessPoolExecutor
6. **Result Collection**: Aggregate results as they complete
7. **Error Handling**: Track and report errors without stopping execution
8. **Domain Conversion**: Convert raw results to domain objects (Endpoint, Model, Service)

## Contributing

To add multi-process support to a new framework analyzer:

1. Create module-level processor functions (must be picklable)
2. Update analyzer constructor to accept `enable_parallel` and `max_workers`
3. Call `super().__init__()` with parallel parameters
4. Use `self._process_files_parallel()` instead of loops
5. Add tests to verify parallel and sequential consistency
6. Update this documentation

Example template:

```python
# Module-level processor
def _process_my_file(file_path: Path) -> Optional[dict[str, Any]]:
    """Process file and return data dict."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    # ... processing ...
    return {"name": name, "data": data}

class MyFrameworkAnalyzer(BaseAnalyzer):
    def __init__(
        self,
        repo_root: Path,
        verbose: bool = False,
        enable_parallel: bool = True,
        max_workers: Optional[int] = None,
    ):
        super().__init__(repo_root, verbose, enable_parallel, max_workers)
    
    def discover_components(self) -> list[Component]:
        all_files = [...]  # Collect files
        
        results = self._process_files_parallel(
            all_files,
            _process_my_file,
            desc="Processing components",
        )
        
        # Convert to domain objects
        for result in results:
            if result is not None:
                component = Component(...)
                self.components.append(component)
        
        return self.components
```

## References

- [Python multiprocessing documentation](https://docs.python.org/3/library/multiprocessing.html)
- [ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor)
- [ENH-PERF-001: Large Codebase Optimization](./performance-benchmarks.md)
- [ENH-PERF-004 Issue](https://github.com/cue-3/re-cue/issues/XXX)
