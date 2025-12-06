#!/usr/bin/env python3
"""
Performance benchmark runner for RE-cue.

This script runs all performance benchmarks and generates a comprehensive report.
It can be used in CI/CD pipelines to monitor performance trends over time.

Usage:
    python run_benchmarks.py [options]

Options:
    --output FILE       Save benchmark results to JSON file
    --baseline FILE     Load baseline metrics from file
    --update-baseline   Update baseline with current results
    --regression-only   Run only regression tests
    --benchmark-only    Run only benchmark tests
    --verbose          Show detailed output
"""

import argparse
import json
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_benchmark_suite(verbose: bool = False) -> tuple[unittest.TestResult, List[Dict[str, Any]]]:
    """
    Run benchmark test suite.

    Args:
        verbose: Show verbose output

    Returns:
        Tuple of (test result, benchmark results)
    """
    from tests.test_performance_benchmarks import TestPerformanceBenchmarks

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPerformanceBenchmarks)

    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    # Extract benchmark results
    benchmark_results = []
    if hasattr(TestPerformanceBenchmarks, "results"):
        benchmark_results = [r.to_dict() for r in TestPerformanceBenchmarks.results]

    return result, benchmark_results


def run_regression_suite(verbose: bool = False) -> unittest.TestResult:
    """
    Run regression test suite.

    Args:
        verbose: Show verbose output

    Returns:
        Test result
    """
    from tests.test_performance_regression import TestPerformanceRegression

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPerformanceRegression)

    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    return result


def save_benchmark_results(
    results: List[Dict[str, Any]], output_file: Path, metadata: Dict[str, Any] = None
):
    """
    Save benchmark results to JSON file.

    Args:
        results: List of benchmark results
        output_file: Path to output file
        metadata: Additional metadata to include
    """
    output = {
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {},
        "benchmarks": results,
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Benchmark results saved to: {output_file}")


def update_baseline_file(results: List[Dict[str, Any]], baseline_file: Path):
    """
    Update baseline file with current results.

    Args:
        results: List of benchmark results
        baseline_file: Path to baseline file
    """
    # Convert results to baseline format
    baselines = {}

    for result in results:
        name = result["name"]
        duration = result["duration_seconds"]
        throughput = result["throughput_per_second"]
        metadata = result.get("metadata", {})

        # Extract key metrics based on benchmark name
        if "Small Project" in name:
            baselines["small_project_analysis"] = {
                "max_duration": duration * 1.2,  # 20% margin
                "min_throughput": throughput * 0.8,
            }
        elif "Medium Project" in name:
            baselines["medium_project_analysis"] = {
                "max_duration": duration * 1.2,
                "min_throughput": throughput * 0.8,
            }
        elif "Large Project" in name:
            baselines["large_project_analysis"] = {
                "max_duration": duration * 1.2,
                "min_throughput": throughput * 0.8,
            }
        elif "Parallel Processing Speedup" in name:
            speedup = metadata.get("speedup", 1.0)
            baselines["parallel_speedup"] = {
                "min_speedup": speedup * 0.8,
            }
        elif "Cache Effectiveness" in name:
            speedup = metadata.get("speedup", 1.0)
            hit_rate = metadata.get("hit_rate", 100.0)
            baselines["cache_speedup"] = {
                "min_speedup": speedup * 0.8,
                "min_hit_rate": hit_rate * 0.95,
            }
        elif "File Tracking" in name:
            track_time = metadata.get("track_time", 1.0)
            check_time = metadata.get("check_time", 0.5)
            baselines["file_tracking"] = {
                "max_track_time": track_time * 1.2,
                "max_check_time": check_time * 1.2,
            }
        elif "Cache Operations" in name:
            write_time = metadata.get("write_time", 1.0)
            read_time = metadata.get("read_time", 0.5)
            write_throughput = metadata.get("write_throughput", 50.0)
            read_throughput = metadata.get("read_throughput", 100.0)
            baselines["cache_operations"] = {
                "max_write_time": write_time * 1.2,
                "max_read_time": read_time * 1.2,
                "min_write_throughput": write_throughput * 0.8,
                "min_read_throughput": read_throughput * 0.8,
            }

    # Save baseline file
    baseline_file.parent.mkdir(parents=True, exist_ok=True)
    with open(baseline_file, "w", encoding="utf-8") as f:
        json.dump(baselines, f, indent=2)

    print(f"\n✓ Baseline updated: {baseline_file}")


def print_summary(
    benchmark_result: unittest.TestResult = None,
    regression_result: unittest.TestResult = None,
    benchmark_data: List[Dict[str, Any]] = None,
):
    """
    Print summary of results.

    Args:
        benchmark_result: Benchmark test result
        regression_result: Regression test result
        benchmark_data: Benchmark data
    """
    print("\n" + "=" * 70)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 70)

    if benchmark_result:
        print(f"\nBenchmark Tests:")
        print(f"  Ran: {benchmark_result.testsRun}")
        print(f"  Passed: {benchmark_result.testsRun - len(benchmark_result.failures) - len(benchmark_result.errors)}")
        print(f"  Failed: {len(benchmark_result.failures)}")
        print(f"  Errors: {len(benchmark_result.errors)}")

    if regression_result:
        print(f"\nRegression Tests:")
        print(f"  Ran: {regression_result.testsRun}")
        print(f"  Passed: {regression_result.testsRun - len(regression_result.failures) - len(regression_result.errors)}")
        print(f"  Failed: {len(regression_result.failures)}")
        print(f"  Errors: {len(regression_result.errors)}")

    if benchmark_data:
        print(f"\nBenchmark Results: {len(benchmark_data)} benchmarks completed")
        print("\nKey Metrics:")
        for result in benchmark_data:
            name = result["name"]
            duration = result["duration_seconds"]
            throughput = result["throughput_per_second"]
            print(f"  • {name}: {duration:.3f}s", end="")
            if throughput > 0:
                print(f" ({throughput:.1f} items/s)", end="")
            print()

    print("\n" + "=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run RE-cue performance benchmarks and regression tests"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save benchmark results to JSON file",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Load baseline metrics from file",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Update baseline with current results",
    )
    parser.add_argument(
        "--regression-only",
        action="store_true",
        help="Run only regression tests",
    )
    parser.add_argument(
        "--benchmark-only",
        action="store_true",
        help="Run only benchmark tests",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output",
    )

    args = parser.parse_args()

    # Change to tests directory
    tests_dir = Path(__file__).parent
    import os

    os.chdir(tests_dir.parent)

    start_time = time.time()

    benchmark_result = None
    regression_result = None
    benchmark_data = None

    # Run benchmarks
    if not args.regression_only:
        print("\n" + "=" * 70)
        print("Running Performance Benchmarks...")
        print("=" * 70)
        benchmark_result, benchmark_data = run_benchmark_suite(args.verbose)

        # Save results if requested
        if args.output:
            metadata = {
                "python_version": sys.version,
                "platform": sys.platform,
            }
            save_benchmark_results(benchmark_data, args.output, metadata)

        # Update baseline if requested
        if args.update_baseline:
            baseline_file = args.baseline or (tests_dir / "performance_baseline.json")
            update_baseline_file(benchmark_data, baseline_file)

    # Run regression tests
    if not args.benchmark_only:
        print("\n" + "=" * 70)
        print("Running Performance Regression Tests...")
        print("=" * 70)
        regression_result = run_regression_suite(args.verbose)

    # Print summary
    total_time = time.time() - start_time
    print_summary(benchmark_result, regression_result, benchmark_data)
    print(f"\nTotal time: {total_time:.2f}s")

    # Exit with appropriate code
    success = True
    if benchmark_result and (benchmark_result.failures or benchmark_result.errors):
        success = False
    if regression_result and (regression_result.failures or regression_result.errors):
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
