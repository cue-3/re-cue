"""
Progress tracking domain models for RE-cue.

These dataclasses represent the progress tracking system for analysis operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol


class AnalysisStage(Enum):
    """Represents different stages of analysis."""

    INITIALIZATION = "initialization"
    ENDPOINTS = "endpoints"
    MODELS = "models"
    VIEWS = "views"
    SERVICES = "services"
    FEATURES = "features"
    ACTORS = "actors"
    BOUNDARIES = "boundaries"
    RELATIONSHIPS = "relationships"
    USE_CASES = "use_cases"
    GENERATION = "generation"
    COMPLETE = "complete"


class ProgressStatus(Enum):
    """Status of a progress item."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RECOVERED = "recovered"


@dataclass
class FileProgress:
    """Progress information for a single file being analyzed."""

    path: str
    status: ProgressStatus = ProgressStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate processing duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class StageProgress:
    """Progress information for an analysis stage."""

    stage: AnalysisStage
    status: ProgressStatus = ProgressStatus.PENDING
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    recovered_files: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    files: list[FileProgress] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        """Calculate stage completion percentage."""
        if self.total_files == 0:
            return 100.0 if self.status == ProgressStatus.COMPLETED else 0.0
        return (self.processed_files / self.total_files) * 100.0

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate stage duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return None

    @property
    def estimated_remaining_seconds(self) -> Optional[float]:
        """Estimate remaining time based on current progress."""
        if self.processed_files == 0 or self.started_at is None:
            return None

        elapsed = (datetime.now() - self.started_at).total_seconds()
        if elapsed <= 0:
            return None

        rate = self.processed_files / elapsed
        remaining = self.total_files - self.processed_files
        return remaining / rate if rate > 0 else None


@dataclass
class AnalysisProgress:
    """
    Complete progress information for an analysis operation.

    This is the main progress tracking model that aggregates all progress
    information across stages and files.
    """

    total_stages: int = 8
    current_stage_index: int = 0
    status: ProgressStatus = ProgressStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    stages: list[StageProgress] = field(default_factory=list)
    total_files_discovered: int = 0
    total_files_processed: int = 0
    total_errors: int = 0
    total_recovered: int = 0
    cancellation_requested: bool = False
    error_message: Optional[str] = None

    @property
    def overall_percentage(self) -> float:
        """Calculate overall completion percentage across all stages."""
        if self.total_stages == 0:
            return 100.0 if self.status == ProgressStatus.COMPLETED else 0.0

        # Weight each stage equally
        completed_stages = sum(
            1 for s in self.stages if s.status == ProgressStatus.COMPLETED
        )
        current_stage_progress = 0.0
        if self.stages and self.current_stage_index < len(self.stages):
            current = self.stages[self.current_stage_index]
            if current.status == ProgressStatus.IN_PROGRESS:
                current_stage_progress = current.percentage / 100.0

        return ((completed_stages + current_stage_progress) / self.total_stages) * 100.0

    @property
    def current_stage(self) -> Optional[StageProgress]:
        """Get the current stage being processed."""
        if 0 <= self.current_stage_index < len(self.stages):
            return self.stages[self.current_stage_index]
        return None

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return None

    @property
    def estimated_total_seconds(self) -> Optional[float]:
        """Estimate total time based on current progress."""
        if self.overall_percentage <= 0 or self.duration_seconds is None:
            return None

        return (self.duration_seconds / self.overall_percentage) * 100.0

    @property
    def estimated_remaining_seconds(self) -> Optional[float]:
        """Estimate remaining time based on current progress."""
        total = self.estimated_total_seconds
        elapsed = self.duration_seconds
        if total is None or elapsed is None:
            return None
        return max(0, total - elapsed)

    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self.cancellation_requested

    def request_cancellation(self) -> None:
        """Request cancellation of the analysis."""
        self.cancellation_requested = True
        self.cancelled_at = datetime.now()


class ProgressCallback(Protocol):
    """
    Protocol for progress callbacks.

    Implementations can provide custom progress reporting (e.g., to UI, logs, etc.)
    """

    def on_stage_start(self, stage: StageProgress) -> None:
        """Called when a stage starts."""
        pass

    def on_stage_complete(self, stage: StageProgress) -> None:
        """Called when a stage completes."""
        pass

    def on_file_start(self, file_path: str, stage: AnalysisStage) -> None:
        """Called when file processing starts."""
        pass

    def on_file_complete(self, file_path: str, stage: AnalysisStage, success: bool) -> None:
        """Called when file processing completes."""
        pass

    def on_progress_update(self, progress: "AnalysisProgress") -> None:
        """Called periodically with overall progress update."""
        pass

    def on_error(self, error: str, file_path: Optional[str] = None) -> None:
        """Called when an error occurs."""
        pass

    def on_analysis_complete(self, progress: "AnalysisProgress") -> None:
        """Called when the entire analysis completes."""
        pass

    def should_cancel(self) -> bool:
        """Check if cancellation has been requested by the callback."""
        pass


@dataclass
class ProgressSummary:
    """Summary of analysis progress for display."""

    status: str
    overall_percentage: float
    current_stage: str
    current_stage_percentage: float
    elapsed_time: str
    estimated_remaining: str
    files_processed: int
    total_files: int
    errors: int
    recovered: int

    @staticmethod
    def from_progress(progress: AnalysisProgress) -> "ProgressSummary":
        """Create a summary from an AnalysisProgress instance."""

        def format_time(seconds: Optional[float]) -> str:
            if seconds is None:
                return "--"
            if seconds < 60:
                return f"{int(seconds)}s"
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"

        current = progress.current_stage
        current_stage_name = current.stage.value if current else "unknown"
        current_stage_pct = current.percentage if current else 0.0

        return ProgressSummary(
            status=progress.status.value,
            overall_percentage=progress.overall_percentage,
            current_stage=current_stage_name,
            current_stage_percentage=current_stage_pct,
            elapsed_time=format_time(progress.duration_seconds),
            estimated_remaining=format_time(progress.estimated_remaining_seconds),
            files_processed=progress.total_files_processed,
            total_files=progress.total_files_discovered,
            errors=progress.total_errors,
            recovered=progress.total_recovered,
        )
