"""
Performance optimization utilities for large codebase analysis.

This module provides:
- Parallel file processing using multiprocessing
- Incremental analysis (track and skip unchanged files)
- Memory-efficient file reading
- Progress reporting
- Early termination on errors
"""

import hashlib
import json
import multiprocessing
import signal
import sys
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from .domain.progress import AnalysisStage, ProgressCallback


@dataclass
class FileMetadata:
    """Metadata for tracking file changes."""

    path: str
    size: int
    mtime: float
    hash: Optional[str] = None


class FileTracker:
    """Tracks file modifications for incremental analysis."""

    def __init__(self, state_file: Path):
        """Initialize file tracker with state file path."""
        self.state_file = state_file
        self.file_metadata: dict[str, FileMetadata] = {}
        self._load_state()

    def _load_state(self):
        """Load previous file metadata from state file."""
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file) as f:
                data = json.load(f)
                for path, meta_dict in data.get("files", {}).items():
                    self.file_metadata[path] = FileMetadata(**meta_dict)
        except Exception as e:
            print(f"Warning: Could not load file tracker state: {e}", file=sys.stderr)

    def save_state(self):
        """Save current file metadata to state file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "timestamp": datetime.now().isoformat(),
            "files": {path: asdict(meta) for path, meta in self.file_metadata.items()},
        }

        try:
            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save file tracker state: {e}", file=sys.stderr)

    def has_changed(self, file_path: Path, use_hash: bool = False) -> bool:
        """
        Check if a file has changed since last analysis.

        Args:
            file_path: Path to the file to check
            use_hash: If True, use file hash for comparison (slower but more accurate)

        Returns:
            True if file has changed or is new, False otherwise
        """
        try:
            stat = file_path.stat()
            path_str = str(file_path)

            # New file
            if path_str not in self.file_metadata:
                return True

            old_meta = self.file_metadata[path_str]

            # Check size and mtime first (fast)
            if old_meta.size != stat.st_size or old_meta.mtime != stat.st_mtime:
                return True

            # Optionally check hash for more certainty
            if use_hash:
                current_hash = self._compute_hash(file_path)
                if old_meta.hash != current_hash:
                    return True

            return False

        except Exception:
            # If we can't check, assume it changed
            return True

    def update_file(self, file_path: Path, compute_hash: bool = False):
        """
        Update metadata for a file.

        Args:
            file_path: Path to the file
            compute_hash: Whether to compute and store file hash
        """
        try:
            stat = file_path.stat()
            path_str = str(file_path)

            file_hash = None
            if compute_hash:
                file_hash = self._compute_hash(file_path)

            self.file_metadata[path_str] = FileMetadata(
                path=path_str, size=stat.st_size, mtime=stat.st_mtime, hash=file_hash
            )
        except Exception as e:
            print(f"Warning: Could not update metadata for {file_path}: {e}", file=sys.stderr)

    def _compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file contents."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return ""

    def filter_changed_files(self, files: list[Path], use_hash: bool = False) -> list[Path]:
        """
        Filter a list of files to only include changed files.

        Args:
            files: List of file paths to check
            use_hash: Whether to use hash-based comparison

        Returns:
            List of files that have changed
        """
        return [f for f in files if self.has_changed(f, use_hash)]


class ProgressReporter:
    """Reports analysis progress with live updates."""

    def __init__(
        self,
        total: int,
        desc: str = "Processing",
        verbose: bool = True,
        callback: Optional["ProgressCallback"] = None,
        stage: Optional["AnalysisStage"] = None,
    ):
        """
        Initialize progress reporter.

        Args:
            total: Total number of items to process
            desc: Description of what's being processed
            verbose: Whether to show progress
            callback: Optional ProgressCallback for external progress reporting
            stage: Optional AnalysisStage for tracking
        """
        self.total = total
        self.completed = 0
        self.desc = desc
        self.verbose = verbose
        self.start_time = datetime.now()
        self.errors: list[str] = []
        self.callback = callback
        self.stage = stage
        self._cancellation_requested = False
        self._recovered_count = 0

    def update(self, n: int = 1, file_path: Optional[str] = None, success: bool = True):
        """Update progress by n items.

        Args:
            n: Number of items completed
            file_path: Optional file path that was processed
            success: Whether the item was processed successfully
        """
        self.completed += n
        if self.verbose:
            self._print_progress()

        # Notify callback if provided
        if self.callback and file_path and self.stage:
            try:
                self.callback.on_file_complete(file_path, self.stage, success)
            except Exception:
                pass  # Don't let callback errors affect processing

    def _print_progress(self):
        """Print current progress to stderr."""
        if self.total == 0:
            percent = 100
        else:
            percent = (self.completed / self.total) * 100

        elapsed = (datetime.now() - self.start_time).total_seconds()

        # Estimate time remaining
        if self.completed > 0:
            rate = self.completed / elapsed
            remaining = (self.total - self.completed) / rate
            eta = f"ETA: {int(remaining)}s"
        else:
            eta = "ETA: --"

        # Create progress bar
        bar_length = 30
        filled = int(bar_length * self.completed / self.total) if self.total > 0 else bar_length
        bar = "█" * filled + "░" * (bar_length - filled)

        # Print with carriage return to overwrite
        print(
            f"\r{self.desc}: [{bar}] {percent:.1f}% ({self.completed}/{self.total}) {eta}",
            end="",
            file=sys.stderr,
            flush=True,
        )

        # Print newline when complete
        if self.completed >= self.total:
            print(file=sys.stderr)

    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        if self.callback:
            try:
                self.callback.on_error(error)
            except Exception:
                pass

    def add_recovery(self, file_path: str):
        """Record a successful recovery from an error.

        Args:
            file_path: Path of file that was recovered
        """
        self._recovered_count += 1

    def finish(self):
        """Mark progress as complete."""
        self.completed = self.total
        if self.verbose:
            self._print_progress()

    def request_cancellation(self):
        """Request cancellation of processing."""
        self._cancellation_requested = True

    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        if self._cancellation_requested:
            return True
        if self.callback:
            try:
                return self.callback.should_cancel()
            except Exception:
                pass
        return False

    @property
    def percentage(self) -> float:
        """Get current completion percentage."""
        if self.total == 0:
            return 100.0
        return (self.completed / self.total) * 100.0

    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def estimated_remaining_seconds(self) -> Optional[float]:
        """Estimate remaining time in seconds."""
        if self.completed == 0:
            return None
        rate = self.completed / self.elapsed_seconds
        if rate <= 0:
            return None
        return (self.total - self.completed) / rate

    @property
    def error_count(self) -> int:
        """Get the number of errors encountered."""
        return len(self.errors)

    @property
    def recovered_count(self) -> int:
        """Get the number of recovered errors."""
        return self._recovered_count


class ParallelProcessor:
    """
    Process files in parallel with error handling.

    Thread Safety:
    - Uses ProcessPoolExecutor which creates separate processes (not threads)
    - Each worker process has its own memory space, so no shared state issues
    - Progress tracking uses instance variables, safe when used from single thread
    - Not safe to call process_files from multiple threads simultaneously

    Usage: Create one instance per analysis task, use from single thread.
    """

    def __init__(
        self, max_workers: Optional[int] = None, max_errors: int = 10, verbose: bool = True
    ):
        """
        Initialize parallel processor.

        Args:
            max_workers: Maximum number of worker processes (None = CPU count)
            max_errors: Maximum errors before terminating early
            verbose: Whether to show progress
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.max_errors = max_errors
        self.verbose = verbose
        self._stop_event = threading.Event()

        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle termination signals."""
        print("\n\nReceived stop signal. Terminating gracefully...", file=sys.stderr)
        self._stop_event.set()

    def process_files(
        self,
        files: list[Path],
        processor_func: Callable[[Path], Any],
        desc: str = "Processing files",
    ) -> list[tuple[Path, Any, Optional[str]]]:
        """
        Process files in parallel.

        Args:
            files: List of file paths to process
            processor_func: Function to process each file (must be picklable)
            desc: Description for progress reporting

        Returns:
            List of tuples (file_path, result, error_message)
            If processing succeeded, error_message is None
            If processing failed, result is None and error_message contains the error
        """
        if not files:
            return []

        results = []
        error_count = 0
        progress = ProgressReporter(len(files), desc, self.verbose)

        try:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(self._safe_process, processor_func, file_path): file_path
                    for file_path in files
                }

                # Process results as they complete
                for future in as_completed(future_to_file):
                    # Check for stop request or max errors
                    if self._stop_event.is_set() or error_count >= self.max_errors:
                        # Graceful shutdown: cancel pending futures and wait for running ones
                        executor.shutdown(wait=True, cancel_futures=False)
                        break

                    file_path = future_to_file[future]
                    try:
                        result, error = future.result()
                        results.append((file_path, result, error))

                        if error:
                            error_count += 1
                            progress.add_error(f"{file_path}: {error}")

                            if self.verbose and error_count >= self.max_errors:
                                print(
                                    f"\n\nMaximum error count ({self.max_errors}) reached. Stopping...",
                                    file=sys.stderr,
                                )

                        progress.update()

                    except Exception as e:
                        error_count += 1
                        error_msg = f"Unexpected error: {e}"
                        results.append((file_path, None, error_msg))
                        progress.add_error(f"{file_path}: {error_msg}")
                        progress.update()

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Cleaning up...", file=sys.stderr)
            self._stop_event.set()

        finally:
            progress.finish()

        # Print error summary if there were errors
        if error_count > 0 and self.verbose:
            print(f"\n⚠️  {error_count} errors occurred during processing", file=sys.stderr)
            if progress.errors and len(progress.errors) <= 5:
                print("\nErrors:", file=sys.stderr)
                for error in progress.errors:
                    print(f"  • {error}", file=sys.stderr)
            elif progress.errors:
                print(f"\nShowing first 5 of {len(progress.errors)} errors:", file=sys.stderr)
                for error in progress.errors[:5]:
                    print(f"  • {error}", file=sys.stderr)

        return results

    @staticmethod
    def _safe_process(func: Callable[[Path], Any], file_path: Path) -> tuple[Any, Optional[str]]:
        """
        Safely process a file, catching exceptions.

        Args:
            func: Processing function
            file_path: File to process

        Returns:
            Tuple of (result, error_message)
        """
        try:
            result = func(file_path)
            return result, None
        except Exception as e:
            return None, str(e)


def read_file_efficiently(file_path: Path, max_size_mb: int = 10) -> str:
    """
    Read a file efficiently with size checking.

    For very large files, this can be extended to read in chunks or skip.

    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in MB to read fully

    Returns:
        File contents as string

    Raises:
        ValueError: If file is too large
    """
    stat = file_path.stat()
    size_mb = stat.st_size / (1024 * 1024)

    if size_mb > max_size_mb:
        raise ValueError(f"File too large ({size_mb:.1f}MB > {max_size_mb}MB): {file_path}")

    with open(file_path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def get_optimal_worker_count(file_count: int) -> int:
    """
    Determine optimal number of worker processes based on file count.

    Args:
        file_count: Number of files to process

    Returns:
        Optimal worker count
    """
    cpu_count = multiprocessing.cpu_count()

    # For small numbers of files, don't use more workers than files
    if file_count < cpu_count:
        return max(1, file_count)

    # For large numbers of files, use all CPUs but don't go crazy
    return min(cpu_count, 16)
