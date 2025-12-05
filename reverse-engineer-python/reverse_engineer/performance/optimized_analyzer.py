"""
Enhanced analyzer with performance optimizations for large codebases.

This module extends the base analyzer with:
- Parallel file processing
- Incremental analysis (skip unchanged files)
- Caching of analysis results
- Progress reporting
- Early termination on errors
"""

import re
from pathlib import Path
from typing import Any, Callable, Optional

from ..utils import log_info
from .cache_manager import CacheManager
from .optimization import (
    FileTracker,
    ParallelProcessor,
    ProgressReporter,
    get_optimal_worker_count,
    read_file_efficiently,
)


class OptimizedAnalyzer:
    """
    Wrapper for analyzer operations with performance optimizations.

    This class provides optimized file processing methods that can be used
    by the main analyzer classes.
    """

    def __init__(
        self,
        repo_root: Path,
        output_dir: Optional[Path] = None,
        enable_incremental: bool = True,
        enable_parallel: bool = True,
        enable_caching: bool = True,
        max_workers: Optional[int] = None,
        verbose: bool = True,
    ):
        """
        Initialize optimized analyzer.

        Args:
            repo_root: Root directory of the repository
            output_dir: Directory for output and state files
            enable_incremental: Enable incremental analysis
            enable_parallel: Enable parallel processing
            enable_caching: Enable result caching
            max_workers: Maximum number of worker processes
            verbose: Enable verbose output
        """
        self.repo_root = repo_root
        self.output_dir = output_dir or (repo_root / "specs" / "001-reverse")
        self.enable_incremental = enable_incremental
        self.enable_parallel = enable_parallel
        self.enable_caching = enable_caching
        self.max_workers = max_workers
        self.verbose = verbose

        # Initialize file tracker for incremental analysis
        if enable_incremental:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            state_file = self.output_dir / ".file_tracker_state.json"
            self.file_tracker: Optional[FileTracker] = FileTracker(state_file)
        else:
            self.file_tracker = None

        # Initialize cache manager
        if enable_caching:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            cache_dir = self.output_dir / ".cache"
            self.cache_manager: Optional[CacheManager] = CacheManager(cache_dir)
        else:
            self.cache_manager = None

    def process_files_optimized(
        self,
        files: list[Path],
        processor: Callable[[Path], Any],
        desc: str = "Processing files",
        skip_unchanged: bool = True,
        analysis_type: str = "default",
        use_cache: bool = True,
    ) -> list[Any]:
        """
        Process files with optimizations.

        Args:
            files: List of file paths to process
            processor: Function to process each file
            desc: Description for progress reporting
            skip_unchanged: Skip unchanged files if incremental analysis is enabled
            analysis_type: Type of analysis (for cache key differentiation)
            use_cache: Whether to use cached results

        Returns:
            List of processing results (successful ones only)
        """
        if not files:
            return []

        # Try to get results from cache if enabled
        cached_results = []
        files_to_process = list(files)  # Make a copy

        if self.enable_caching and use_cache and self.cache_manager:
            files_needing_processing = []
            for file_path in files:
                cached_result = self.cache_manager.get(file_path, analysis_type)
                if cached_result is not None:
                    cached_results.append(cached_result)
                else:
                    files_needing_processing.append(file_path)

            files_to_process = files_needing_processing

            if cached_results and self.verbose:
                log_info(f"  Retrieved {len(cached_results)} results from cache", self.verbose)

        # Filter out unchanged files if incremental analysis is enabled
        # Note: When caching is enabled, the cache already handles file change detection
        # via content hash. Incremental analysis (mtime-based) is redundant with caching,
        # so we only use it when caching is disabled.
        should_use_incremental = (
            self.enable_incremental
            and skip_unchanged
            and self.file_tracker
            and not (self.enable_caching and use_cache)
        )

        if should_use_incremental:
            original_count = len(files_to_process)
            files_to_process = self.file_tracker.filter_changed_files(files_to_process)
            skipped_count = original_count - len(files_to_process)

            if skipped_count > 0 and self.verbose:
                log_info(f"  Skipping {skipped_count} unchanged files", self.verbose)

        if not files_to_process:
            if self.verbose and not cached_results:
                log_info("  All files are up to date", self.verbose)
            return cached_results

        results = []

        # Decide whether to use parallel processing
        use_parallel = (
            self.enable_parallel and len(files_to_process) > 10  # Only use parallel for 10+ files
        )

        if use_parallel:
            # Use parallel processing
            worker_count = self.max_workers or get_optimal_worker_count(len(files_to_process))
            if self.verbose:
                log_info(
                    f"  Processing {len(files_to_process)} files using {worker_count} workers...",
                    self.verbose,
                )

            parallel_processor = ParallelProcessor(max_workers=worker_count, verbose=self.verbose)

            process_results = parallel_processor.process_files(files_to_process, processor, desc)

            # Extract successful results, update file tracker, and cache
            for file_path, result, error in process_results:
                if error is None and result is not None:
                    results.append(result)
                    if self.file_tracker:
                        self.file_tracker.update_file(file_path)
                    if self.cache_manager and use_cache:
                        self.cache_manager.put(file_path, result, analysis_type)
        else:
            # Use sequential processing with progress bar
            if self.verbose:
                log_info(
                    f"  Processing {len(files_to_process)} files sequentially...", self.verbose
                )

            progress = ProgressReporter(len(files_to_process), desc, self.verbose)

            for file_path in files_to_process:
                try:
                    result = processor(file_path)
                    if result is not None:
                        results.append(result)
                    if self.file_tracker:
                        self.file_tracker.update_file(file_path)
                    if self.cache_manager and use_cache:
                        self.cache_manager.put(file_path, result, analysis_type)
                except Exception as e:
                    if self.verbose:
                        log_info(f"  Error processing {file_path}: {e}", self.verbose)
                    progress.add_error(f"{file_path}: {e}")
                finally:
                    progress.update()

            progress.finish()

        # Save file tracker state
        if self.file_tracker:
            self.file_tracker.save_state()

        # Save cache
        if self.cache_manager:
            self.cache_manager.save_cache()

        # Combine cached and newly processed results
        all_results = cached_results + results
        return all_results

    def find_files_by_pattern(self, patterns: list[str], exclude_test: bool = True) -> list[Path]:
        """
        Find files matching patterns with optimized search.

        Args:
            patterns: List of glob patterns to search
            exclude_test: Exclude test files

        Returns:
            List of matching file paths
        """
        files = []
        seen = set()

        for pattern in patterns:
            for file_path in self.repo_root.rglob(pattern):
                # Skip if already seen
                if file_path in seen:
                    continue

                # Skip test files if requested
                if exclude_test and self._is_test_file(file_path):
                    continue

                files.append(file_path)
                seen.add(file_path)

        return files

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file."""
        path_str = str(file_path).lower()
        return any(
            [
                "/test/" in path_str,
                "/tests/" in path_str,
                "test" in file_path.stem.lower(),
                file_path.name.startswith("test_"),
                file_path.name.endswith("_test.py"),
                file_path.name.endswith("_test.java"),
                file_path.name.endswith("Test.java"),
                file_path.name.endswith(".test.js"),
                file_path.name.endswith(".spec.js"),
            ]
        )

    def clear_cache(self):
        """Clear all cached results."""
        if self.cache_manager:
            self.cache_manager.invalidate_all()
            self.cache_manager.save_cache()
            if self.verbose:
                log_info("Cache cleared", self.verbose)

    def print_cache_stats(self):
        """Print cache statistics."""
        if self.cache_manager:
            self.cache_manager.print_statistics()
        else:
            print("Caching is not enabled")

    def cleanup_cache(self):
        """Clean up expired and invalid cache entries."""
        if self.cache_manager:
            expired = self.cache_manager.cleanup_expired()
            invalid = self.cache_manager.cleanup_invalid()
            self.cache_manager.save_cache()
            if self.verbose:
                log_info(
                    f"Removed {expired} expired and {invalid} invalid cache entries", self.verbose
                )
            return expired + invalid
        return 0


# Module-level processor functions for parallel processing
# These must be at module level to be picklable


def process_java_controller(file_path: Path) -> dict:
    """
    Process a Java controller file to extract endpoints.
    This is a module-level function for parallel processing.

    Note: Import of re module is at module level to avoid overhead.
    """
    try:
        content = read_file_efficiently(file_path)
        endpoints = []

        controller_name = file_path.stem.replace("Controller", "")

        # Extract base path from @RequestMapping
        base_path = ""
        base_match = re.search(r'@RequestMapping\("([^"]*)"\)', content)
        if base_match:
            base_path = base_match.group(1)

        # Find all endpoint methods
        mapping_pattern = r'@(Get|Post|Put|Delete|Patch)Mapping(?:\("([^"]*)"\))?'

        lines = content.split("\n")
        for i, line in enumerate(lines):
            match = re.search(mapping_pattern, line)
            if match:
                method = match.group(1).upper()
                path = match.group(2) or ""
                full_path = base_path + path

                # Check for authentication in nearby lines
                authenticated = False
                start_line = max(0, i - 10)
                for check_line in lines[start_line:i]:
                    if "@PreAuthorize" in check_line:
                        authenticated = True
                        break

                endpoints.append(
                    {
                        "method": method,
                        "path": full_path,
                        "controller": controller_name,
                        "authenticated": authenticated,
                        "file": str(file_path),
                    }
                )

        return {"file": str(file_path), "endpoints": endpoints}

    except Exception as e:
        return {"file": str(file_path), "error": str(e)}


def process_java_model(file_path: Path) -> dict:
    """
    Process a Java model file to extract model information.
    This is a module-level function for parallel processing.

    Note: Import of re module is at module level to avoid overhead.
    """
    try:
        content = read_file_efficiently(file_path)
        model_name = file_path.stem

        # Count private fields
        field_count = len(re.findall(r"^\s*private\s+", content, re.MULTILINE))

        return {"name": model_name, "fields": field_count, "file": str(file_path)}

    except Exception as e:
        return {"name": file_path.stem, "error": str(e)}


def process_java_service(file_path: Path) -> dict:
    """
    Process a Java service file to extract service information.
    This is a module-level function for parallel processing.
    """
    try:
        content = read_file_efficiently(file_path)
        service_name = file_path.stem.replace("Service", "")

        # Check if it's an interface
        is_interface = "@Service" not in content and "interface" in content

        return {"name": service_name, "is_interface": is_interface, "file": str(file_path)}

    except Exception as e:
        return {"name": file_path.stem, "error": str(e)}
