"""
Performance benchmark tests for RE-cue.

This module provides comprehensive performance benchmarks to:
1. Measure analysis time vs file count
2. Track memory usage patterns
3. Measure template rendering speed
4. Test cache effectiveness
5. Measure parallel processing speedup

Benchmarks establish baseline metrics and detect performance regressions.
"""

import json
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List

from reverse_engineer.performance import (
    CacheManager,
    FileTracker,
    OptimizedAnalyzer,
    ParallelProcessor,
)


# Module-level processor functions (must be picklable for multiprocessing)
def benchmark_processor_simple(file_path: Path) -> dict:
    """Simple processor for benchmarking."""
    content = file_path.read_text()
    return {"file": str(file_path), "lines": content.count("\n")}


def benchmark_processor_with_delay(file_path: Path) -> dict:
    """Processor with artificial delay for benchmarking parallelization."""
    import time

    content = file_path.read_text()
    time.sleep(0.01)
    return {"file": str(file_path), "lines": content.count("\n")}


def benchmark_processor_file_content(file_path: Path) -> dict:
    """Processor that reads file content."""
    content = file_path.read_text()
    return {"file": str(file_path), "length": len(content)}


class PerformanceBenchmarkResult:
    """Container for benchmark results."""

    def __init__(
        self,
        name: str,
        duration: float,
        throughput: float = 0.0,
        memory_mb: float = 0.0,
        metadata: Dict[str, Any] = None,
    ):
        """
        Initialize benchmark result.

        Args:
            name: Name of the benchmark
            duration: Time taken in seconds
            throughput: Items processed per second
            memory_mb: Memory used in MB (if measured)
            metadata: Additional metrics
        """
        self.name = name
        self.duration = duration
        self.throughput = throughput
        self.memory_mb = memory_mb
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "duration_seconds": self.duration,
            "throughput_per_second": self.throughput,
            "memory_mb": self.memory_mb,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        """String representation."""
        parts = [
            f"{self.name}:",
            f"  Duration: {self.duration:.3f}s",
        ]
        if self.throughput > 0:
            parts.append(f"  Throughput: {self.throughput:.1f} items/s")
        if self.memory_mb > 0:
            parts.append(f"  Memory: {self.memory_mb:.1f} MB")
        if self.metadata:
            parts.append(f"  Metadata: {self.metadata}")
        return "\n".join(parts)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmark test suite."""

    @classmethod
    def setUpClass(cls):
        """Set up benchmark environment."""
        cls.results: List[PerformanceBenchmarkResult] = []
        cls.temp_dir = tempfile.mkdtemp()
        cls.project_root = Path(cls.temp_dir) / "benchmark-project"
        cls.project_root.mkdir()

    @classmethod
    def tearDownClass(cls):
        """Clean up and report results."""
        import shutil

        if Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir)

        # Print benchmark summary
        print("\n" + "=" * 70)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("=" * 70)
        for result in cls.results:
            print(result)
            print("-" * 70)

    def _create_java_files(self, count: int, lines_per_file: int = 50) -> List[Path]:
        """
        Create Java files for testing.

        Args:
            count: Number of files to create
            lines_per_file: Approximate lines per file

        Returns:
            List of created file paths
        """
        src_dir = self.project_root / "src" / "main" / "java" / "com" / "example"
        src_dir.mkdir(parents=True, exist_ok=True)

        files = []
        for i in range(count):
            file_path = src_dir / f"Class{i}.java"
            content_lines = [
                f"package com.example;",
                "",
                f"import org.springframework.web.bind.annotation.*;",
                "",
                f"@RestController",
                f'@RequestMapping("/api/resource{i}")',
                f"public class Class{i} {{",
                "",
            ]

            # Add methods to reach desired line count
            methods_needed = (lines_per_file - len(content_lines) - 1) // 5
            for j in range(methods_needed):
                content_lines.extend(
                    [
                        f"    @GetMapping",
                        f"    public String method{j}() {{",
                        f'        return "result{j}";',
                        f"    }}",
                        "",
                    ]
                )

            content_lines.append("}")

            file_path.write_text("\n".join(content_lines))
            files.append(file_path)

        return files

    def _create_python_files(self, count: int, lines_per_file: int = 30) -> List[Path]:
        """
        Create Python files for testing.

        Args:
            count: Number of files to create
            lines_per_file: Approximate lines per file

        Returns:
            List of created file paths
        """
        src_dir = self.project_root / "app"
        src_dir.mkdir(parents=True, exist_ok=True)

        files = []
        for i in range(count):
            file_path = src_dir / f"module{i}.py"
            content_lines = [
                f'"""Module {i} for testing."""',
                "",
                "from flask import Flask, jsonify",
                "",
                f"app{i} = Flask(__name__)",
                "",
            ]

            # Add routes to reach desired line count
            routes_needed = (lines_per_file - len(content_lines)) // 4
            for j in range(routes_needed):
                content_lines.extend(
                    [
                        f"@app{i}.route('/api/endpoint{j}')",
                        f"def endpoint{j}():",
                        f"    return jsonify({{'result': '{j}'}})",
                        "",
                    ]
                )

            file_path.write_text("\n".join(content_lines))
            files.append(file_path)

        return files

    def test_benchmark_small_project_analysis(self):
        """Benchmark: Analyze small project (10 files, ~500 lines)."""
        files = self._create_java_files(count=10, lines_per_file=50)

        analyzer = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=False,
            verbose=False,
        )

        start = time.time()
        results = analyzer.process_files_optimized(
            files, benchmark_processor_simple, "Small project"
        )
        duration = time.time() - start

        throughput = len(files) / duration if duration > 0 else 0

        result = PerformanceBenchmarkResult(
            name="Small Project Analysis (10 files, ~500 lines)",
            duration=duration,
            throughput=throughput,
            metadata={"file_count": len(files), "result_count": len(results)},
        )
        self.results.append(result)

        # Assertion: Should complete in reasonable time
        self.assertLess(duration, 2.0, "Small project should analyze in < 2s")
        self.assertEqual(len(results), len(files))

    def test_benchmark_medium_project_analysis(self):
        """Benchmark: Analyze medium project (50 files, ~2500 lines)."""
        files = self._create_java_files(count=50, lines_per_file=50)

        analyzer = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=False,
            verbose=False,
        )

        start = time.time()
        results = analyzer.process_files_optimized(
            files, benchmark_processor_simple, "Medium project"
        )
        duration = time.time() - start

        throughput = len(files) / duration if duration > 0 else 0

        result = PerformanceBenchmarkResult(
            name="Medium Project Analysis (50 files, ~2500 lines)",
            duration=duration,
            throughput=throughput,
            metadata={"file_count": len(files), "result_count": len(results)},
        )
        self.results.append(result)

        # Assertion: Should scale reasonably
        self.assertLess(duration, 5.0, "Medium project should analyze in < 5s")
        self.assertEqual(len(results), len(files))

    def test_benchmark_large_project_analysis(self):
        """Benchmark: Analyze large project (100 files, ~5000 lines)."""
        files = self._create_java_files(count=100, lines_per_file=50)

        analyzer = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=False,
            verbose=False,
        )

        start = time.time()
        results = analyzer.process_files_optimized(
            files, benchmark_processor_simple, "Large project"
        )
        duration = time.time() - start

        throughput = len(files) / duration if duration > 0 else 0

        result = PerformanceBenchmarkResult(
            name="Large Project Analysis (100 files, ~5000 lines)",
            duration=duration,
            throughput=throughput,
            metadata={"file_count": len(files), "result_count": len(results)},
        )
        self.results.append(result)

        # Assertion: Should handle large projects
        self.assertLess(duration, 10.0, "Large project should analyze in < 10s")
        self.assertEqual(len(results), len(files))

    def test_benchmark_parallel_speedup(self):
        """Benchmark: Measure parallel processing speedup."""
        # Use more files to ensure parallel processing is used
        files = self._create_java_files(count=40, lines_per_file=50)

        # Sequential
        analyzer_seq = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=False,
            enable_incremental=False,
            verbose=False,
        )

        start = time.time()
        results_seq = analyzer_seq.process_files_optimized(
            files, benchmark_processor_with_delay, "Sequential"
        )
        duration_seq = time.time() - start

        # Parallel
        analyzer_par = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=True,
            enable_incremental=False,
            max_workers=4,
            verbose=False,
        )

        start = time.time()
        results_par = analyzer_par.process_files_optimized(
            files, benchmark_processor_with_delay, "Parallel"
        )
        duration_par = time.time() - start

        speedup = duration_seq / duration_par if duration_par > 0 else 0

        result = PerformanceBenchmarkResult(
            name="Parallel Processing Speedup (40 files, 4 workers)",
            duration=duration_par,
            throughput=len(files) / duration_par if duration_par > 0 else 0,
            metadata={
                "sequential_time": duration_seq,
                "parallel_time": duration_par,
                "speedup": speedup,
                "workers": 4,
                "sequential_count": len(results_seq),
                "parallel_count": len(results_par),
            },
        )
        self.results.append(result)

        # Assertion: Both should process all files
        self.assertEqual(len(results_seq), len(files), f"Sequential processed {len(results_seq)} files, expected {len(files)}")
        self.assertEqual(len(results_par), len(files), f"Parallel processed {len(results_par)} files, expected {len(files)}")
        # Parallel should provide some speedup
        self.assertGreater(speedup, 1.0, "Parallel processing should be faster")

    def test_benchmark_cache_effectiveness(self):
        """Benchmark: Measure cache effectiveness."""
        files = self._create_python_files(count=30, lines_per_file=30)

        output_dir = Path(self.temp_dir) / "cache_benchmark"
        output_dir.mkdir(exist_ok=True)

        # First run (cold cache)
        analyzer1 = OptimizedAnalyzer(
            repo_root=self.project_root,
            output_dir=output_dir,
            enable_caching=True,
            enable_parallel=False,
            verbose=False,
        )

        start = time.time()
        analyzer1.process_files_optimized(
            files, benchmark_processor_simple, "First run"
        )
        duration_first = time.time() - start
        analyzer1.cache_manager.save_cache()

        # Second run (warm cache)
        analyzer2 = OptimizedAnalyzer(
            repo_root=self.project_root,
            output_dir=output_dir,
            enable_caching=True,
            enable_parallel=False,
            verbose=False,
        )

        start = time.time()
        analyzer2.process_files_optimized(
            files, benchmark_processor_simple, "Second run"
        )
        duration_second = time.time() - start

        stats = analyzer2.cache_manager.get_statistics()
        speedup = duration_first / duration_second if duration_second > 0 else 0

        result = PerformanceBenchmarkResult(
            name="Cache Effectiveness (30 files)",
            duration=duration_second,
            throughput=len(files) / duration_second if duration_second > 0 else 0,
            metadata={
                "first_run_time": duration_first,
                "second_run_time": duration_second,
                "speedup": speedup,
                "cache_hits": stats.hits,
                "cache_misses": stats.misses,
                "hit_rate": stats.hit_rate,
            },
        )
        self.results.append(result)

        # Assertion: Cache should provide significant speedup
        self.assertGreater(speedup, 1.5, "Cache should provide at least 1.5x speedup")
        self.assertEqual(stats.hits, len(files), "All files should be cache hits")

    def test_benchmark_file_tracking(self):
        """Benchmark: Measure file tracking performance."""
        files = self._create_java_files(count=100, lines_per_file=50)
        state_file = Path(self.temp_dir) / "tracker_state.json"

        tracker = FileTracker(state_file)

        # Benchmark initial tracking
        start = time.time()
        for file in files:
            tracker.update_file(file, compute_hash=False)
        duration_track = time.time() - start

        # Save state
        tracker.save_state()

        # Benchmark loading
        start = time.time()
        tracker2 = FileTracker(state_file)
        duration_load = time.time() - start

        # Benchmark change detection
        start = time.time()
        changed = tracker2.filter_changed_files(files)
        duration_check = time.time() - start

        result = PerformanceBenchmarkResult(
            name="File Tracking Performance (100 files)",
            duration=duration_track + duration_load + duration_check,
            throughput=len(files) / (duration_track + duration_check)
            if (duration_track + duration_check) > 0
            else 0,
            metadata={
                "track_time": duration_track,
                "load_time": duration_load,
                "check_time": duration_check,
                "changed_files": len(changed),
            },
        )
        self.results.append(result)

        # Assertion: Should be fast
        self.assertLess(duration_track, 1.0, "Tracking 100 files should take < 1s")
        self.assertLess(duration_check, 0.5, "Checking 100 files should take < 0.5s")
        self.assertEqual(len(changed), 0, "No files should be marked as changed")

    def test_benchmark_cache_operations(self):
        """Benchmark: Measure cache operation performance."""
        cache_dir = Path(self.temp_dir) / "cache_ops"
        cache_dir.mkdir(exist_ok=True)
        cache = CacheManager(cache_dir)

        files = self._create_python_files(count=50, lines_per_file=30)
        test_data = [{"file": str(f), "data": f"result{i}"} for i, f in enumerate(files)]

        # Benchmark cache writes
        start = time.time()
        for file, data in zip(files, test_data):
            cache.put(file, data)
        duration_write = time.time() - start

        # Benchmark cache reads (hits)
        start = time.time()
        for file in files:
            result = cache.get(file)
            self.assertIsNotNone(result)
        duration_read = time.time() - start

        # Benchmark persistence
        start = time.time()
        cache.save_cache()
        duration_save = time.time() - start

        # Benchmark loading
        cache2 = CacheManager(cache_dir)
        start = time.time()
        for file in files:
            result = cache2.get(file)
            self.assertIsNotNone(result)
        duration_reload = time.time() - start

        result = PerformanceBenchmarkResult(
            name="Cache Operations (50 entries)",
            duration=duration_write + duration_read + duration_save + duration_reload,
            throughput=len(files) / (duration_write + duration_read)
            if (duration_write + duration_read) > 0
            else 0,
            metadata={
                "write_time": duration_write,
                "read_time": duration_read,
                "save_time": duration_save,
                "reload_time": duration_reload,
                "write_throughput": len(files) / duration_write
                if duration_write > 0
                else 0,
                "read_throughput": len(files) / duration_read if duration_read > 0 else 0,
            },
        )
        self.results.append(result)

        # Assertions: Should be fast
        self.assertLess(duration_write, 1.0, "Writing 50 entries should take < 1s")
        self.assertLess(duration_read, 0.5, "Reading 50 entries should take < 0.5s")
        self.assertLess(duration_save, 1.0, "Saving cache should take < 1s")

    def test_benchmark_parallel_processor_overhead(self):
        """Benchmark: Measure parallel processor overhead."""
        files = self._create_java_files(count=20, lines_per_file=30)

        # Measure direct processing (baseline)
        start = time.time()
        baseline_results = [benchmark_processor_file_content(f) for f in files]
        duration_baseline = time.time() - start

        # Measure with ParallelProcessor (1 worker)
        processor_obj = ParallelProcessor(max_workers=1, verbose=False)
        start = time.time()
        parallel_results = processor_obj.process_files(
            files, benchmark_processor_file_content, "Test"
        )
        duration_parallel = time.time() - start

        overhead = duration_parallel - duration_baseline
        overhead_percent = (
            (overhead / duration_baseline * 100) if duration_baseline > 0.001 else 0
        )

        result = PerformanceBenchmarkResult(
            name="Parallel Processor Overhead (20 files, 1 worker)",
            duration=duration_parallel,
            throughput=len(files) / duration_parallel if duration_parallel > 0 else 0,
            metadata={
                "baseline_time": duration_baseline,
                "parallel_time": duration_parallel,
                "overhead_seconds": overhead,
                "overhead_percent": overhead_percent,
            },
        )
        self.results.append(result)

        # Assertion: Both should complete successfully
        # parallel_results is a list of tuples: (file_path, result, error)
        # where error is None for successful processing
        successful_parallel = [r for r in parallel_results if r[2] is None]
        self.assertEqual(
            len(baseline_results),
            len(successful_parallel),
            f"Expected {len(baseline_results)} successful results, got {len(successful_parallel)}",
        )


if __name__ == "__main__":
    unittest.main()
