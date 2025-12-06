"""
Analysis progress tracking for RE-cue.

This module provides a comprehensive progress tracking system that integrates
with the domain models and provides file-by-file progress, stage completion
percentage, time estimates, cancellation support, and error recovery.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional
import logging

from .domain.progress import (
    AnalysisProgress,
    AnalysisStage,
    FileProgress,
    ProgressCallback,
    ProgressStatus,
    ProgressSummary,
    StageProgress,
)


class ConsoleProgressCallback(ProgressCallback):
    """
    A console-based progress callback that prints progress to stderr.

    This is the default callback used when verbose mode is enabled.
    Implements the ProgressCallback protocol.
    """

    def __init__(self, verbose: bool = True, show_files: bool = False):
        """
        Initialize the console progress callback.

        Args:
            verbose: Whether to show detailed progress
            show_files: Whether to show individual file progress
        """
        self.verbose = verbose
        self.show_files = show_files
        self._cancellation_requested = False
        self._last_progress_print = datetime.now()
        self._print_interval_seconds = 0.5  # Minimum time between progress prints

    def on_stage_start(self, stage: StageProgress) -> None:
        """Called when a stage starts."""
        if self.verbose:
            icon = self._get_stage_icon(stage.stage)
            print(
                f"\n{icon} Starting {stage.stage.value}...",
                file=sys.stderr,
            )

    def on_stage_complete(self, stage: StageProgress) -> None:
        """Called when a stage completes."""
        if self.verbose:
            duration = stage.duration_seconds or 0
            status_icon = "✓" if stage.status == ProgressStatus.COMPLETED else "✗"
            print(
                f"  {status_icon} {stage.stage.value} complete "
                f"({stage.processed_files} files, {duration:.1f}s)",
                file=sys.stderr,
            )

    def on_file_start(self, file_path: str, stage: AnalysisStage) -> None:
        """Called when file processing starts."""
        if self.verbose and self.show_files:
            print(f"    → Processing: {Path(file_path).name}", file=sys.stderr)

    def on_file_complete(
        self, file_path: str, stage: AnalysisStage, success: bool
    ) -> None:
        """Called when file processing completes."""
        if self.verbose and self.show_files:
            status = "✓" if success else "✗"
            print(f"    {status} {Path(file_path).name}", file=sys.stderr)

    def on_progress_update(self, progress: AnalysisProgress) -> None:
        """Called periodically with overall progress update."""
        if not self.verbose:
            return

        # Rate limit progress updates
        now = datetime.now()
        if (now - self._last_progress_print).total_seconds() < self._print_interval_seconds:
            return
        self._last_progress_print = now

        summary = ProgressSummary.from_progress(progress)
        self._print_progress_bar(summary)

    def on_error(self, error: str, file_path: Optional[str] = None) -> None:
        """Called when an error occurs."""
        if self.verbose:
            location = f" in {file_path}" if file_path else ""
            print(f"\n  ⚠️  Error{location}: {error}", file=sys.stderr)

    def on_analysis_complete(self, progress: AnalysisProgress) -> None:
        """Called when the entire analysis completes."""
        if self.verbose:
            summary = ProgressSummary.from_progress(progress)
            print(f"\n{'═' * 50}", file=sys.stderr)
            print("  Analysis Complete", file=sys.stderr)
            print(f"{'═' * 50}", file=sys.stderr)
            print(f"  Status: {summary.status}", file=sys.stderr)
            print(f"  Duration: {summary.elapsed_time}", file=sys.stderr)
            print(
                f"  Files: {summary.files_processed}/{summary.total_files}",
                file=sys.stderr,
            )
            if summary.errors > 0:
                print(f"  Errors: {summary.errors}", file=sys.stderr)
            if summary.recovered > 0:
                print(f"  Recovered: {summary.recovered}", file=sys.stderr)
            print(f"{'═' * 50}\n", file=sys.stderr)

    def should_cancel(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancellation_requested

    def request_cancellation(self) -> None:
        """Request cancellation of the analysis."""
        self._cancellation_requested = True

    def _print_progress_bar(self, summary: ProgressSummary) -> None:
        """Print a progress bar to stderr."""
        bar_length = 30
        filled = int(bar_length * summary.overall_percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(
            f"\r  [{bar}] {summary.overall_percentage:.1f}% "
            f"| {summary.current_stage} "
            f"| ETA: {summary.estimated_remaining}",
            end="",
            file=sys.stderr,
            flush=True,
        )

    def _get_stage_icon(self, stage: AnalysisStage) -> str:
        """Get an icon for a stage."""
        icons = {
            AnalysisStage.INITIALIZATION: "🚀",
            AnalysisStage.ENDPOINTS: "📍",
            AnalysisStage.MODELS: "📦",
            AnalysisStage.VIEWS: "🎨",
            AnalysisStage.SERVICES: "⚙️",
            AnalysisStage.FEATURES: "✨",
            AnalysisStage.ACTORS: "👥",
            AnalysisStage.BOUNDARIES: "🏢",
            AnalysisStage.RELATIONSHIPS: "🔗",
            AnalysisStage.USE_CASES: "📋",
            AnalysisStage.GENERATION: "📝",
            AnalysisStage.COMPLETE: "✅",
        }
        return icons.get(stage, "•")


class AnalysisProgressTracker:
    """
    Comprehensive progress tracking for analysis operations.

    This class manages progress across all analysis stages and provides:
    - File-by-file progress tracking
    - Stage completion percentage
    - Time estimates (ETA)
    - Cancellation support
    - Error recovery capabilities
    """

    def __init__(
        self,
        callback: Optional[ProgressCallback] = None,
        verbose: bool = True,
        max_retries: int = 2,
    ):
        """
        Initialize the progress tracker.

        Args:
            callback: Optional progress callback for external reporting
            verbose: Whether to show progress output
            max_retries: Maximum number of retries for failed files
        """
        self.callback = callback or ConsoleProgressCallback(verbose=verbose)
        self.verbose = verbose
        self.max_retries = max_retries
        self.progress = AnalysisProgress()
        self._initialize_stages()

    def _initialize_stages(self) -> None:
        """Initialize all analysis stages."""
        stages = [
            AnalysisStage.ENDPOINTS,
            AnalysisStage.MODELS,
            AnalysisStage.VIEWS,
            AnalysisStage.SERVICES,
            AnalysisStage.FEATURES,
            AnalysisStage.ACTORS,
            AnalysisStage.BOUNDARIES,
            AnalysisStage.USE_CASES,
        ]

        self.progress.total_stages = len(stages)
        self.progress.stages = [
            StageProgress(stage=stage) for stage in stages
        ]

    def start_analysis(self) -> None:
        """Start the analysis tracking."""
        self.progress.status = ProgressStatus.IN_PROGRESS
        self.progress.started_at = datetime.now()

    def start_stage(
        self, stage: AnalysisStage, total_files: int = 0
    ) -> StageProgress:
        """
        Start tracking a new stage.

        Args:
            stage: The stage being started
            total_files: Total number of files to process in this stage

        Returns:
            The StageProgress object for this stage
        """
        # Find the stage in our list
        stage_progress = None
        for i, sp in enumerate(self.progress.stages):
            if sp.stage == stage:
                stage_progress = sp
                self.progress.current_stage_index = i
                break

        if stage_progress is None:
            # Stage not in predefined list, add it
            stage_progress = StageProgress(stage=stage)
            self.progress.stages.append(stage_progress)
            self.progress.current_stage_index = len(self.progress.stages) - 1

        stage_progress.status = ProgressStatus.IN_PROGRESS
        stage_progress.started_at = datetime.now()
        stage_progress.total_files = total_files

        if self.callback:
            try:
                self.callback.on_stage_start(stage_progress)
            except Exception:
                pass

        return stage_progress

    def complete_stage(
        self, stage: AnalysisStage, error: Optional[str] = None
    ) -> None:
        """
        Mark a stage as complete.

        Args:
            stage: The stage being completed
            error: Optional error message if stage failed
        """
        stage_progress = self._get_stage(stage)
        if stage_progress is None:
            return

        stage_progress.completed_at = datetime.now()
        if error:
            stage_progress.status = ProgressStatus.FAILED
            stage_progress.error_message = error
        else:
            stage_progress.status = ProgressStatus.COMPLETED

        # Update totals
        self.progress.total_files_processed += stage_progress.processed_files
        self.progress.total_errors += stage_progress.failed_files
        self.progress.total_recovered += stage_progress.recovered_files

        if self.callback:
            try:
                self.callback.on_stage_complete(stage_progress)
            except Exception:
                pass

    def start_file(self, file_path: str, stage: AnalysisStage) -> FileProgress:
        """
        Start tracking a file.

        Args:
            file_path: Path to the file being processed
            stage: The stage processing this file

        Returns:
            FileProgress object for this file
        """
        stage_progress = self._get_stage(stage)
        if stage_progress is None:
            return FileProgress(path=file_path)

        file_progress = FileProgress(
            path=file_path,
            status=ProgressStatus.IN_PROGRESS,
            started_at=datetime.now(),
        )
        stage_progress.files.append(file_progress)

        if self.callback:
            try:
                self.callback.on_file_start(file_path, stage)
            except Exception:
                pass

        return file_progress

    def complete_file(
        self,
        file_path: str,
        stage: AnalysisStage,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """
        Mark a file as complete.

        Args:
            file_path: Path to the file
            stage: The stage that processed this file
            success: Whether processing succeeded
            error: Optional error message if processing failed
        """
        stage_progress = self._get_stage(stage)
        if stage_progress is None:
            return

        # Find the file progress
        file_progress = None
        for fp in stage_progress.files:
            if fp.path == file_path:
                file_progress = fp
                break

        if file_progress is None:
            # File wasn't tracked, create a record
            file_progress = FileProgress(
                path=file_path,
                started_at=datetime.now(),
            )
            stage_progress.files.append(file_progress)

        file_progress.completed_at = datetime.now()
        if success:
            file_progress.status = ProgressStatus.COMPLETED
            stage_progress.processed_files += 1
        else:
            file_progress.status = ProgressStatus.FAILED
            file_progress.error_message = error
            stage_progress.failed_files += 1

        if self.callback:
            try:
                self.callback.on_file_complete(file_path, stage, success)
            except Exception:
                pass

        # Update overall progress
        self._update_progress()

    def recover_file(
        self,
        file_path: str,
        stage: AnalysisStage,
        processor: Callable[[Path], Any],
    ) -> Optional[Any]:
        """
        Attempt to recover from a file processing error.

        Args:
            file_path: Path to the file that failed
            stage: The stage processing this file
            processor: Function to reprocess the file

        Returns:
            Result of successful processing, or None if recovery failed
        """
        stage_progress = self._get_stage(stage)
        if stage_progress is None:
            return None

        # Find the file progress
        file_progress = None
        for fp in stage_progress.files:
            if fp.path == file_path:
                file_progress = fp
                break

        if file_progress is None:
            return None

        # Check if we've exceeded max retries
        if file_progress.retry_count >= self.max_retries:
            return None

        file_progress.retry_count += 1
        file_progress.status = ProgressStatus.IN_PROGRESS
        file_progress.started_at = datetime.now()

        try:
            result = processor(Path(file_path))
            file_progress.status = ProgressStatus.RECOVERED
            file_progress.completed_at = datetime.now()
            stage_progress.recovered_files += 1
            stage_progress.failed_files = max(0, stage_progress.failed_files - 1)
            self.progress.total_recovered += 1
            return result
        except Exception as e:
            file_progress.status = ProgressStatus.FAILED
            file_progress.error_message = str(e)
            file_progress.completed_at = datetime.now()
            return None

    def complete_analysis(self, error: Optional[str] = None) -> AnalysisProgress:
        """
        Mark the entire analysis as complete.

        Args:
            error: Optional error message if analysis failed

        Returns:
            The final AnalysisProgress object
        """
        self.progress.completed_at = datetime.now()

        if self.progress.cancellation_requested:
            self.progress.status = ProgressStatus.CANCELLED
        elif error:
            self.progress.status = ProgressStatus.FAILED
            self.progress.error_message = error
        else:
            self.progress.status = ProgressStatus.COMPLETED

        if self.callback:
            try:
                self.callback.on_analysis_complete(self.progress)
            except Exception:
                pass

        return self.progress

    def request_cancellation(self) -> None:
        """Request cancellation of the analysis."""
        self.progress.request_cancellation()
        if hasattr(self.callback, "request_cancellation"):
            self.callback.request_cancellation()

    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        if self.progress.is_cancelled():
            return True
        if self.callback:
            try:
                return self.callback.should_cancel()
            except Exception:
                pass
        return False

    def get_summary(self) -> ProgressSummary:
        """Get a summary of the current progress."""
        return ProgressSummary.from_progress(self.progress)

    def _get_stage(self, stage: AnalysisStage) -> Optional[StageProgress]:
        """Get the StageProgress for a given stage."""
        for sp in self.progress.stages:
            if sp.stage == stage:
                return sp
        return None

    def _update_progress(self) -> None:
        """Update overall progress and notify callback."""
        # Recalculate totals
        self.progress.total_files_discovered = sum(
            s.total_files for s in self.progress.stages
        )

        if self.callback:
            try:
                self.callback.on_progress_update(self.progress)
            except Exception:
                logging.exception("Exception occurred during progress update callback.")
