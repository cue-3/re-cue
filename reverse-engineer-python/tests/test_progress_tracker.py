"""
Tests for the progress tracking system.
"""

import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from reverse_engineer.domain.progress import (
    AnalysisProgress,
    AnalysisStage,
    FileProgress,
    ProgressStatus,
    ProgressSummary,
    StageProgress,
)
from reverse_engineer.progress_tracker import (
    AnalysisProgressTracker,
    ConsoleProgressCallback,
)


class TestAnalysisStage(unittest.TestCase):
    """Tests for AnalysisStage enum."""

    def test_stage_values(self):
        """Test that all expected stages exist."""
        expected_stages = [
            "initialization",
            "endpoints",
            "models",
            "views",
            "services",
            "features",
            "actors",
            "boundaries",
            "relationships",
            "use_cases",
            "generation",
            "complete",
        ]

        for stage_value in expected_stages:
            self.assertIn(stage_value, [s.value for s in AnalysisStage])


class TestProgressStatus(unittest.TestCase):
    """Tests for ProgressStatus enum."""

    def test_status_values(self):
        """Test that all expected statuses exist."""
        expected_statuses = [
            "pending",
            "in_progress",
            "completed",
            "failed",
            "cancelled",
            "recovered",
        ]

        for status_value in expected_statuses:
            self.assertIn(status_value, [s.value for s in ProgressStatus])


class TestFileProgress(unittest.TestCase):
    """Tests for FileProgress dataclass."""

    def test_file_progress_creation(self):
        """Test creating a FileProgress instance."""
        fp = FileProgress(path="/path/to/file.java")
        self.assertEqual(fp.path, "/path/to/file.java")
        self.assertEqual(fp.status, ProgressStatus.PENDING)
        self.assertIsNone(fp.started_at)
        self.assertIsNone(fp.completed_at)
        self.assertIsNone(fp.error_message)
        self.assertEqual(fp.retry_count, 0)

    def test_file_progress_duration(self):
        """Test duration calculation."""
        fp = FileProgress(
            path="/path/to/file.java",
            started_at=datetime(2023, 1, 1, 12, 0, 0),
            completed_at=datetime(2023, 1, 1, 12, 0, 5),
        )
        self.assertEqual(fp.duration_seconds, 5.0)

    def test_file_progress_duration_none(self):
        """Test duration when not complete."""
        fp = FileProgress(path="/path/to/file.java")
        self.assertIsNone(fp.duration_seconds)


class TestStageProgress(unittest.TestCase):
    """Tests for StageProgress dataclass."""

    def test_stage_progress_creation(self):
        """Test creating a StageProgress instance."""
        sp = StageProgress(stage=AnalysisStage.ENDPOINTS)
        self.assertEqual(sp.stage, AnalysisStage.ENDPOINTS)
        self.assertEqual(sp.status, ProgressStatus.PENDING)
        self.assertEqual(sp.total_files, 0)
        self.assertEqual(sp.processed_files, 0)

    def test_percentage_calculation(self):
        """Test percentage calculation."""
        sp = StageProgress(
            stage=AnalysisStage.ENDPOINTS,
            total_files=10,
            processed_files=5,
        )
        self.assertEqual(sp.percentage, 50.0)

    def test_percentage_zero_files(self):
        """Test percentage when no files."""
        sp = StageProgress(stage=AnalysisStage.ENDPOINTS, total_files=0)
        self.assertEqual(sp.percentage, 0.0)

        sp.status = ProgressStatus.COMPLETED
        self.assertEqual(sp.percentage, 100.0)

    def test_duration_calculation(self):
        """Test duration calculation."""
        sp = StageProgress(
            stage=AnalysisStage.ENDPOINTS,
            started_at=datetime(2023, 1, 1, 12, 0, 0),
            completed_at=datetime(2023, 1, 1, 12, 1, 0),
        )
        self.assertEqual(sp.duration_seconds, 60.0)

    def test_estimated_remaining(self):
        """Test estimated remaining time."""
        sp = StageProgress(
            stage=AnalysisStage.ENDPOINTS,
            total_files=100,
            processed_files=50,
            started_at=datetime.now(),
        )
        # Add a small delay to get a non-zero elapsed time
        time.sleep(0.01)

        remaining = sp.estimated_remaining_seconds
        self.assertIsNotNone(remaining)
        self.assertGreater(remaining, 0)


class TestAnalysisProgress(unittest.TestCase):
    """Tests for AnalysisProgress dataclass."""

    def test_analysis_progress_creation(self):
        """Test creating an AnalysisProgress instance."""
        ap = AnalysisProgress()
        self.assertEqual(ap.total_stages, 8)
        self.assertEqual(ap.current_stage_index, 0)
        self.assertEqual(ap.status, ProgressStatus.PENDING)
        self.assertFalse(ap.cancellation_requested)

    def test_overall_percentage(self):
        """Test overall percentage calculation."""
        ap = AnalysisProgress(total_stages=4)
        ap.stages = [
            StageProgress(stage=AnalysisStage.ENDPOINTS, status=ProgressStatus.COMPLETED),
            StageProgress(stage=AnalysisStage.MODELS, status=ProgressStatus.COMPLETED),
            StageProgress(stage=AnalysisStage.VIEWS, status=ProgressStatus.PENDING),
            StageProgress(stage=AnalysisStage.SERVICES, status=ProgressStatus.PENDING),
        ]
        self.assertEqual(ap.overall_percentage, 50.0)

    def test_cancellation(self):
        """Test cancellation functionality."""
        ap = AnalysisProgress()
        self.assertFalse(ap.is_cancelled())

        ap.request_cancellation()
        self.assertTrue(ap.is_cancelled())
        self.assertIsNotNone(ap.cancelled_at)

    def test_current_stage(self):
        """Test getting current stage."""
        ap = AnalysisProgress()
        ap.stages = [
            StageProgress(stage=AnalysisStage.ENDPOINTS),
            StageProgress(stage=AnalysisStage.MODELS),
        ]
        ap.current_stage_index = 1

        current = ap.current_stage
        self.assertIsNotNone(current)
        self.assertEqual(current.stage, AnalysisStage.MODELS)

    def test_duration(self):
        """Test duration calculation."""
        ap = AnalysisProgress(
            started_at=datetime(2023, 1, 1, 12, 0, 0),
            completed_at=datetime(2023, 1, 1, 12, 5, 0),
        )
        self.assertEqual(ap.duration_seconds, 300.0)


class TestProgressSummary(unittest.TestCase):
    """Tests for ProgressSummary dataclass."""

    def test_from_progress(self):
        """Test creating summary from progress."""
        ap = AnalysisProgress(
            total_stages=2,
            status=ProgressStatus.IN_PROGRESS,
            started_at=datetime.now(),
            total_files_discovered=100,
            total_files_processed=50,
            total_errors=2,
            total_recovered=1,
        )
        ap.stages = [
            StageProgress(
                stage=AnalysisStage.ENDPOINTS,
                status=ProgressStatus.COMPLETED,
            ),
            StageProgress(
                stage=AnalysisStage.MODELS,
                status=ProgressStatus.IN_PROGRESS,
                total_files=50,
                processed_files=25,
            ),
        ]
        ap.current_stage_index = 1

        summary = ProgressSummary.from_progress(ap)

        self.assertEqual(summary.status, "in_progress")
        self.assertEqual(summary.files_processed, 50)
        self.assertEqual(summary.total_files, 100)
        self.assertEqual(summary.errors, 2)
        self.assertEqual(summary.recovered, 1)
        self.assertEqual(summary.current_stage, "models")


class TestConsoleProgressCallback(unittest.TestCase):
    """Tests for ConsoleProgressCallback."""

    def test_callback_creation(self):
        """Test creating a callback."""
        callback = ConsoleProgressCallback(verbose=False)
        self.assertFalse(callback.verbose)
        self.assertFalse(callback._cancellation_requested)

    def test_cancellation(self):
        """Test cancellation request."""
        callback = ConsoleProgressCallback(verbose=False)
        self.assertFalse(callback.should_cancel())

        callback.request_cancellation()
        self.assertTrue(callback.should_cancel())

    @patch("sys.stderr")
    def test_on_stage_start(self, mock_stderr):
        """Test stage start notification."""
        callback = ConsoleProgressCallback(verbose=True)
        stage = StageProgress(stage=AnalysisStage.ENDPOINTS)
        callback.on_stage_start(stage)
        # Verify no exceptions raised

    @patch("sys.stderr")
    def test_on_error(self, mock_stderr):
        """Test error notification."""
        callback = ConsoleProgressCallback(verbose=True)
        callback.on_error("Test error", "/path/to/file.java")
        # Verify no exceptions raised


class TestAnalysisProgressTracker(unittest.TestCase):
    """Tests for AnalysisProgressTracker."""

    def test_tracker_creation(self):
        """Test creating a tracker."""
        tracker = AnalysisProgressTracker(verbose=False)
        self.assertIsNotNone(tracker.progress)
        self.assertEqual(tracker.progress.total_stages, 8)

    def test_start_analysis(self):
        """Test starting analysis."""
        tracker = AnalysisProgressTracker(verbose=False)
        tracker.start_analysis()

        self.assertEqual(tracker.progress.status, ProgressStatus.IN_PROGRESS)
        self.assertIsNotNone(tracker.progress.started_at)

    def test_start_and_complete_stage(self):
        """Test starting and completing a stage."""
        tracker = AnalysisProgressTracker(verbose=False)
        tracker.start_analysis()

        stage = tracker.start_stage(AnalysisStage.ENDPOINTS, total_files=10)
        self.assertEqual(stage.status, ProgressStatus.IN_PROGRESS)
        self.assertEqual(stage.total_files, 10)

        tracker.complete_stage(AnalysisStage.ENDPOINTS)
        self.assertEqual(stage.status, ProgressStatus.COMPLETED)

    def test_start_and_complete_file(self):
        """Test file progress tracking."""
        tracker = AnalysisProgressTracker(verbose=False)
        tracker.start_analysis()
        tracker.start_stage(AnalysisStage.ENDPOINTS, total_files=1)

        file_progress = tracker.start_file("/path/to/file.java", AnalysisStage.ENDPOINTS)
        self.assertEqual(file_progress.status, ProgressStatus.IN_PROGRESS)

        tracker.complete_file("/path/to/file.java", AnalysisStage.ENDPOINTS, success=True)

        # Check file was marked complete
        stage = tracker._get_stage(AnalysisStage.ENDPOINTS)
        self.assertEqual(stage.processed_files, 1)

    def test_complete_file_with_error(self):
        """Test file completion with error."""
        tracker = AnalysisProgressTracker(verbose=False)
        tracker.start_analysis()
        tracker.start_stage(AnalysisStage.ENDPOINTS, total_files=1)
        tracker.start_file("/path/to/file.java", AnalysisStage.ENDPOINTS)

        tracker.complete_file(
            "/path/to/file.java",
            AnalysisStage.ENDPOINTS,
            success=False,
            error="Test error",
        )

        stage = tracker._get_stage(AnalysisStage.ENDPOINTS)
        self.assertEqual(stage.failed_files, 1)

    def test_cancellation(self):
        """Test cancellation functionality."""
        tracker = AnalysisProgressTracker(verbose=False)
        tracker.start_analysis()

        self.assertFalse(tracker.is_cancelled())

        tracker.request_cancellation()
        self.assertTrue(tracker.is_cancelled())

    def test_complete_analysis(self):
        """Test completing analysis."""
        tracker = AnalysisProgressTracker(verbose=False)
        tracker.start_analysis()

        result = tracker.complete_analysis()

        self.assertEqual(result.status, ProgressStatus.COMPLETED)
        self.assertIsNotNone(result.completed_at)

    def test_complete_analysis_with_error(self):
        """Test completing analysis with error."""
        tracker = AnalysisProgressTracker(verbose=False)
        tracker.start_analysis()

        result = tracker.complete_analysis(error="Test error")

        self.assertEqual(result.status, ProgressStatus.FAILED)
        self.assertEqual(result.error_message, "Test error")

    def test_complete_analysis_cancelled(self):
        """Test completing cancelled analysis."""
        tracker = AnalysisProgressTracker(verbose=False)
        tracker.start_analysis()
        tracker.request_cancellation()

        result = tracker.complete_analysis()

        self.assertEqual(result.status, ProgressStatus.CANCELLED)

    def test_get_summary(self):
        """Test getting progress summary."""
        tracker = AnalysisProgressTracker(verbose=False)
        tracker.start_analysis()

        summary = tracker.get_summary()

        self.assertIsInstance(summary, ProgressSummary)
        self.assertEqual(summary.status, "in_progress")

    def test_recover_file(self):
        """Test file recovery."""
        tracker = AnalysisProgressTracker(verbose=False, max_retries=2)
        tracker.start_analysis()
        tracker.start_stage(AnalysisStage.ENDPOINTS, total_files=1)

        # Create a failed file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".java", delete=False
        ) as f:
            f.write("public class Test {}")
            temp_path = f.name

        try:
            tracker.start_file(temp_path, AnalysisStage.ENDPOINTS)
            tracker.complete_file(temp_path, AnalysisStage.ENDPOINTS, success=False, error="Initial error")

            # Attempt recovery
            def processor(path):
                return {"success": True}

            result = tracker.recover_file(temp_path, AnalysisStage.ENDPOINTS, processor)

            self.assertIsNotNone(result)
            self.assertEqual(result["success"], True)

            stage = tracker._get_stage(AnalysisStage.ENDPOINTS)
            self.assertEqual(stage.recovered_files, 1)

        finally:
            Path(temp_path).unlink()


class TestProgressTrackerIntegration(unittest.TestCase):
    """Integration tests for the progress tracking system."""

    def test_full_analysis_workflow(self):
        """Test a complete analysis workflow."""
        tracker = AnalysisProgressTracker(verbose=False)
        tracker.start_analysis()

        stages = [
            AnalysisStage.ENDPOINTS,
            AnalysisStage.MODELS,
            AnalysisStage.VIEWS,
        ]

        for stage in stages:
            tracker.start_stage(stage, total_files=3)

            for i in range(3):
                file_path = f"/path/to/file{i}.java"
                tracker.start_file(file_path, stage)
                tracker.complete_file(file_path, stage, success=True)

            tracker.complete_stage(stage)

        result = tracker.complete_analysis()

        self.assertEqual(result.status, ProgressStatus.COMPLETED)
        self.assertEqual(result.total_files_processed, 9)
        self.assertEqual(result.total_errors, 0)

    def test_analysis_with_errors_and_recovery(self):
        """Test analysis with errors and recovery attempts."""
        tracker = AnalysisProgressTracker(verbose=False, max_retries=2)
        tracker.start_analysis()

        tracker.start_stage(AnalysisStage.ENDPOINTS, total_files=2)

        # First file succeeds
        tracker.start_file("/path/file1.java", AnalysisStage.ENDPOINTS)
        tracker.complete_file("/path/file1.java", AnalysisStage.ENDPOINTS, success=True)

        # Second file fails
        tracker.start_file("/path/file2.java", AnalysisStage.ENDPOINTS)
        tracker.complete_file(
            "/path/file2.java",
            AnalysisStage.ENDPOINTS,
            success=False,
            error="Parse error",
        )

        tracker.complete_stage(AnalysisStage.ENDPOINTS)
        result = tracker.complete_analysis()

        self.assertEqual(result.status, ProgressStatus.COMPLETED)
        self.assertEqual(result.total_files_processed, 1)
        self.assertEqual(result.total_errors, 1)


if __name__ == "__main__":
    unittest.main()
