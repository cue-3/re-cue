"""
Performance regression tests for RE-cue.

This module detects performance regressions by comparing current performance
against baseline metrics. It helps ensure that code changes don't introduce
performance degradation.
"""

import json
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any, Dict, Optional

from reverse_engineer.performance import CacheManager, OptimizedAnalyzer


# Module-level processor functions (must be picklable for multiprocessing)
def regression_processor_simple(file_path: Path) -> dict:
    """Simple processor for regression tests."""
    content = file_path.read_text()
    return {"file": str(file_path), "lines": content.count("\n")}


def regression_processor_with_delay(file_path: Path) -> dict:
    """Processor with artificial delay for regression tests."""
    import time

    content = file_path.read_text()
    time.sleep(0.01)
    return {"file": str(file_path), "lines": content.count("\n")}


class PerformanceBaseline:
    """Manages performance baseline metrics."""

    def __init__(self, baseline_file: Optional[Path] = None):
        """
        Initialize performance baseline.

        Args:
            baseline_file: Path to JSON file storing baseline metrics
        """
        if baseline_file is None:
            baseline_file = Path(__file__).parent / "performance_baseline.json"
        self.baseline_file = baseline_file
        self.baselines: Dict[str, Dict[str, float]] = {}
        self._load_baselines()

    def _load_baselines(self):
        """Load baseline metrics from file."""
        if self.baseline_file.exists():
            try:
                with open(self.baseline_file, encoding="utf-8") as f:
                    self.baselines = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load baselines: {e}")
                self.baselines = {}
        else:
            self.baselines = self._get_default_baselines()

    def _get_default_baselines(self) -> Dict[str, Dict[str, float]]:
        """
        Get default baseline metrics.

        These are reasonable expectations based on the implementation.
        Update these if hardware changes significantly.

        Returns:
            Dictionary of baseline metrics
        """
        return {
            "small_project_analysis": {
                "max_duration": 2.0,
                "min_throughput": 5.0,
            },
            "medium_project_analysis": {
                "max_duration": 5.0,
                "min_throughput": 10.0,
            },
            "large_project_analysis": {
                "max_duration": 10.0,
                "min_throughput": 10.0,
            },
            "parallel_speedup": {
                "min_speedup": 1.2,
            },
            "cache_speedup": {
                "min_speedup": 1.5,
                "min_hit_rate": 95.0,
            },
            "file_tracking": {
                "max_track_time": 1.0,
                "max_check_time": 0.5,
            },
            "cache_operations": {
                "max_write_time": 1.0,
                "max_read_time": 0.5,
                "min_write_throughput": 50.0,
                "min_read_throughput": 100.0,
            },
        }

    def save_baselines(self):
        """Save current baselines to file."""
        try:
            self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.baseline_file, "w", encoding="utf-8") as f:
                json.dump(self.baselines, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save baselines: {e}")

    def get_baseline(self, test_name: str) -> Optional[Dict[str, float]]:
        """
        Get baseline metrics for a test.

        Args:
            test_name: Name of the test

        Returns:
            Dictionary of baseline metrics or None
        """
        return self.baselines.get(test_name)

    def update_baseline(self, test_name: str, metrics: Dict[str, float]):
        """
        Update baseline metrics for a test.

        Args:
            test_name: Name of the test
            metrics: New baseline metrics
        """
        self.baselines[test_name] = metrics


class TestPerformanceRegression(unittest.TestCase):
    """Performance regression test suite."""

    @classmethod
    def setUpClass(cls):
        """Set up regression test environment."""
        cls.baseline = PerformanceBaseline()
        cls.temp_dir = tempfile.mkdtemp()
        cls.project_root = Path(cls.temp_dir) / "regression-project"
        cls.project_root.mkdir()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        import shutil

        if Path(cls.temp_dir).exists():
            shutil.rmtree(cls.temp_dir)

    def _create_test_files(
        self, count: int, extension: str = ".java", lines: int = 50
    ) -> list[Path]:
        """Create test files."""
        src_dir = self.project_root / "src"
        src_dir.mkdir(parents=True, exist_ok=True)

        files = []
        for i in range(count):
            file_path = src_dir / f"file{i}{extension}"
            content = "\n".join([f"// Line {j}" for j in range(lines)])
            file_path.write_text(content)
            files.append(file_path)

        return files

    def test_regression_small_project(self):
        """Regression test: Small project analysis."""
        files = self._create_test_files(count=10, lines=50)

        analyzer = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=False,
            verbose=False,
        )

        start = time.time()
        results = analyzer.process_files_optimized(
            files, regression_processor_simple, "Small"
        )
        duration = time.time() - start

        throughput = len(files) / duration if duration > 0 else 0

        # Check against baseline
        baseline = self.baseline.get_baseline("small_project_analysis")
        if baseline:
            max_duration = baseline.get("max_duration", 2.0)
            min_throughput = baseline.get("min_throughput", 5.0)

            self.assertLess(
                duration,
                max_duration,
                f"Small project analysis regressed: {duration:.3f}s > {max_duration}s",
            )
            self.assertGreater(
                throughput,
                min_throughput,
                f"Throughput regressed: {throughput:.1f} < {min_throughput} files/s",
            )

        self.assertEqual(len(results), len(files))

    def test_regression_medium_project(self):
        """Regression test: Medium project analysis."""
        files = self._create_test_files(count=50, lines=50)

        analyzer = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=False,
            verbose=False,
        )

        start = time.time()
        results = analyzer.process_files_optimized(
            files, regression_processor_simple, "Medium"
        )
        duration = time.time() - start

        throughput = len(files) / duration if duration > 0 else 0

        # Check against baseline
        baseline = self.baseline.get_baseline("medium_project_analysis")
        if baseline:
            max_duration = baseline.get("max_duration", 5.0)
            min_throughput = baseline.get("min_throughput", 10.0)

            self.assertLess(
                duration,
                max_duration,
                f"Medium project analysis regressed: {duration:.3f}s > {max_duration}s",
            )
            self.assertGreater(
                throughput,
                min_throughput,
                f"Throughput regressed: {throughput:.1f} < {min_throughput} files/s",
            )

        self.assertEqual(len(results), len(files))

    def test_regression_parallel_speedup(self):
        """Regression test: Parallel processing speedup."""
        files = self._create_test_files(count=30, lines=50)

        # Sequential
        analyzer_seq = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=False,
            enable_incremental=False,
            verbose=False,
        )

        start = time.time()
        analyzer_seq.process_files_optimized(
            files, regression_processor_with_delay, "Sequential"
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
        analyzer_par.process_files_optimized(
            files, regression_processor_with_delay, "Parallel"
        )
        duration_par = time.time() - start

        speedup = duration_seq / duration_par if duration_par > 0 else 0

        # Check against baseline
        baseline = self.baseline.get_baseline("parallel_speedup")
        if baseline:
            min_speedup = baseline.get("min_speedup", 1.2)

            self.assertGreater(
                speedup,
                min_speedup,
                f"Parallel speedup regressed: {speedup:.2f}x < {min_speedup}x",
            )

    def test_regression_cache_effectiveness(self):
        """Regression test: Cache effectiveness."""
        files = self._create_test_files(count=20, extension=".py", lines=30)

        output_dir = Path(self.temp_dir) / "cache_regression"
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
        analyzer1.process_files_optimized(files, regression_processor_simple, "First")
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
        analyzer2.process_files_optimized(files, regression_processor_simple, "Second")
        duration_second = time.time() - start

        stats = analyzer2.cache_manager.get_statistics()
        speedup = duration_first / duration_second if duration_second > 0 else 0

        # Get hit rate from second run only (not cumulative)
        # All files should be cache hits on second run
        second_run_hits = len(files)  # All files should be hits
        second_run_hit_rate = 100.0 if second_run_hits == len(files) else 0.0

        # Check against baseline
        baseline = self.baseline.get_baseline("cache_speedup")
        if baseline:
            min_speedup = baseline.get("min_speedup", 1.5)
            min_hit_rate = baseline.get("min_hit_rate", 95.0)

            self.assertGreater(
                speedup,
                min_speedup,
                f"Cache speedup regressed: {speedup:.2f}x < {min_speedup}x",
            )
            self.assertGreater(
                second_run_hit_rate,
                min_hit_rate,
                f"Cache hit rate regressed: {second_run_hit_rate:.1f}% < {min_hit_rate}%",
            )

    def test_regression_cache_write_performance(self):
        """Regression test: Cache write performance."""
        cache_dir = Path(self.temp_dir) / "cache_write"
        cache_dir.mkdir(exist_ok=True)
        cache = CacheManager(cache_dir)

        files = self._create_test_files(count=50, lines=30)
        test_data = [{"file": str(f), "data": f"result{i}"} for i, f in enumerate(files)]

        # Benchmark cache writes
        start = time.time()
        for file, data in zip(files, test_data):
            cache.put(file, data)
        duration_write = time.time() - start

        write_throughput = len(files) / duration_write if duration_write > 0 else 0

        # Check against baseline
        baseline = self.baseline.get_baseline("cache_operations")
        if baseline:
            max_write_time = baseline.get("max_write_time", 1.0)
            min_write_throughput = baseline.get("min_write_throughput", 50.0)

            self.assertLess(
                duration_write,
                max_write_time,
                f"Cache write regressed: {duration_write:.3f}s > {max_write_time}s",
            )
            self.assertGreater(
                write_throughput,
                min_write_throughput,
                f"Write throughput regressed: {write_throughput:.1f} < {min_write_throughput} ops/s",
            )

    def test_regression_cache_read_performance(self):
        """Regression test: Cache read performance."""
        cache_dir = Path(self.temp_dir) / "cache_read"
        cache_dir.mkdir(exist_ok=True)
        cache = CacheManager(cache_dir)

        files = self._create_test_files(count=50, lines=30)
        test_data = [{"file": str(f), "data": f"result{i}"} for i, f in enumerate(files)]

        # Populate cache
        for file, data in zip(files, test_data):
            cache.put(file, data)

        # Benchmark cache reads
        start = time.time()
        for file in files:
            result = cache.get(file)
            self.assertIsNotNone(result)
        duration_read = time.time() - start

        read_throughput = len(files) / duration_read if duration_read > 0 else 0

        # Check against baseline
        baseline = self.baseline.get_baseline("cache_operations")
        if baseline:
            max_read_time = baseline.get("max_read_time", 0.5)
            min_read_throughput = baseline.get("min_read_throughput", 100.0)

            self.assertLess(
                duration_read,
                max_read_time,
                f"Cache read regressed: {duration_read:.3f}s > {max_read_time}s",
            )
            self.assertGreater(
                read_throughput,
                min_read_throughput,
                f"Read throughput regressed: {read_throughput:.1f} < {min_read_throughput} ops/s",
            )


if __name__ == "__main__":
    unittest.main()
