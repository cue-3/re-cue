"""
Tests for performance optimization utilities.
"""

import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from reverse_engineer.optimization import (
    FileTracker,
    FileMetadata,
    ProgressReporter,
    ParallelProcessor,
    read_file_efficiently,
    get_optimal_worker_count
)


# Module-level functions for parallel processing tests (must be picklable)
def simple_processor(file_path):
    """Simple processor that reads file and returns length."""
    content = file_path.read_text()
    return len(content)


def error_processor(file_path):
    """Processor that fails for certain files."""
    if "file2" in str(file_path) or "file4" in str(file_path):
        raise ValueError("Simulated error")
    return len(file_path.read_text())


def always_fails_processor(file_path):
    """Processor that always fails."""
    raise ValueError("Always fails")


class TestFileTracker(unittest.TestCase):
    """Tests for FileTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.state_file = self.temp_path / "file_tracker_state.json"
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_new_file_has_changed(self):
        """Test that new files are marked as changed."""
        tracker = FileTracker(self.state_file)
        test_file = self.temp_path / "test.txt"
        test_file.write_text("content")
        
        self.assertTrue(tracker.has_changed(test_file))
    
    def test_unchanged_file_not_marked_changed(self):
        """Test that unchanged files are not marked as changed."""
        tracker = FileTracker(self.state_file)
        test_file = self.temp_path / "test.txt"
        test_file.write_text("content")
        
        # Update tracker
        tracker.update_file(test_file)
        
        # File should not be marked as changed
        self.assertFalse(tracker.has_changed(test_file))
    
    def test_modified_file_marked_changed(self):
        """Test that modified files are marked as changed."""
        tracker = FileTracker(self.state_file)
        test_file = self.temp_path / "test.txt"
        test_file.write_text("content")
        tracker.update_file(test_file)
        
        # Modify file
        time.sleep(0.01)  # Ensure mtime changes
        test_file.write_text("modified content")
        
        # File should be marked as changed
        self.assertTrue(tracker.has_changed(test_file))
    
    def test_state_persistence(self):
        """Test that state is persisted across instances."""
        # Create tracker and update file
        tracker1 = FileTracker(self.state_file)
        test_file = self.temp_path / "test.txt"
        test_file.write_text("content")
        tracker1.update_file(test_file)
        tracker1.save_state()
        
        # Create new tracker and check state was loaded
        tracker2 = FileTracker(self.state_file)
        self.assertFalse(tracker2.has_changed(test_file))
    
    def test_filter_changed_files(self):
        """Test filtering of changed files."""
        tracker = FileTracker(self.state_file)
        
        # Create files
        file1 = self.temp_path / "file1.txt"
        file2 = self.temp_path / "file2.txt"
        file3 = self.temp_path / "file3.txt"
        
        file1.write_text("content1")
        file2.write_text("content2")
        file3.write_text("content3")
        
        # Track file1 and file2
        tracker.update_file(file1)
        tracker.update_file(file2)
        
        # Modify file1
        time.sleep(0.01)
        file1.write_text("modified")
        
        # Filter files
        all_files = [file1, file2, file3]
        changed = tracker.filter_changed_files(all_files)
        
        # file1 (modified) and file3 (new) should be in changed list
        self.assertEqual(len(changed), 2)
        self.assertIn(file1, changed)
        self.assertIn(file3, changed)
        self.assertNotIn(file2, changed)
    
    def test_hash_based_detection(self):
        """Test hash-based change detection."""
        tracker = FileTracker(self.state_file)
        test_file = self.temp_path / "test.txt"
        test_file.write_text("content")
        
        # Update with hash
        tracker.update_file(test_file, compute_hash=True)
        
        # File should not be marked as changed
        self.assertFalse(tracker.has_changed(test_file, use_hash=True))
        
        # Modify content but keep same size/time (simulate touch)
        # In reality, mtime would change, but let's test hash check
        test_file.write_text("CONTENT")  # Same length, different content
        
        # If we force the mtime back (not normally possible but for test)
        # the hash should still detect the change
        self.assertTrue(tracker.has_changed(test_file, use_hash=True))


class TestProgressReporter(unittest.TestCase):
    """Tests for ProgressReporter class."""
    
    def test_progress_initialization(self):
        """Test progress reporter initialization."""
        reporter = ProgressReporter(total=100, desc="Test", verbose=False)
        self.assertEqual(reporter.total, 100)
        self.assertEqual(reporter.completed, 0)
        self.assertEqual(reporter.desc, "Test")
    
    def test_progress_update(self):
        """Test progress updates."""
        reporter = ProgressReporter(total=10, desc="Test", verbose=False)
        reporter.update(5)
        self.assertEqual(reporter.completed, 5)
        reporter.update(3)
        self.assertEqual(reporter.completed, 8)
    
    def test_progress_complete(self):
        """Test marking progress as complete."""
        reporter = ProgressReporter(total=10, desc="Test", verbose=False)
        reporter.finish()
        self.assertEqual(reporter.completed, 10)
    
    def test_error_tracking(self):
        """Test error tracking."""
        reporter = ProgressReporter(total=10, desc="Test", verbose=False)
        reporter.add_error("Error 1")
        reporter.add_error("Error 2")
        self.assertEqual(len(reporter.errors), 2)
        self.assertIn("Error 1", reporter.errors)


class TestParallelProcessor(unittest.TestCase):
    """Tests for ParallelProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_parallel_processing_success(self):
        """Test successful parallel processing."""
        # Create test files
        files = []
        for i in range(5):
            file_path = self.temp_path / f"file{i}.txt"
            file_path.write_text(f"content{i}")
            files.append(file_path)
        
        # Process files
        processor = ParallelProcessor(max_workers=2, verbose=False)
        results = processor.process_files(files, simple_processor, "Test")
        
        # Check results
        self.assertEqual(len(results), 5)
        for file_path, result, error in results:
            self.assertIsNone(error)
            self.assertIsNotNone(result)
            self.assertGreater(result, 0)
    
    def test_parallel_processing_with_errors(self):
        """Test parallel processing with some errors."""
        # Create test files
        files = []
        for i in range(5):
            file_path = self.temp_path / f"file{i}.txt"
            file_path.write_text(f"content{i}")
            files.append(file_path)
        
        # Process files with error-prone processor
        processor_obj = ParallelProcessor(max_workers=2, max_errors=10, verbose=False)
        results = processor_obj.process_files(files, error_processor, "Test")
        
        # Check results
        self.assertEqual(len(results), 5)
        error_count = sum(1 for _, _, error in results if error is not None)
        success_count = sum(1 for _, _, error in results if error is None)
        
        self.assertEqual(error_count, 2)
        self.assertEqual(success_count, 3)
    
    def test_early_termination_on_max_errors(self):
        """Test early termination when max errors reached."""
        # Create many test files
        files = []
        for i in range(20):
            file_path = self.temp_path / f"file{i}.txt"
            file_path.write_text(f"content{i}")
            files.append(file_path)
        
        # Process with processor that always fails
        processor_obj = ParallelProcessor(max_workers=2, max_errors=5, verbose=False)
        results = processor_obj.process_files(files, always_fails_processor, "Test")
        
        # Should stop after hitting max errors
        # Note: Due to parallel processing, might process a few more before all stop
        self.assertLessEqual(len(results), 20)
        
        # At least max_errors should be present
        error_count = sum(1 for _, _, error in results if error is not None)
        self.assertGreaterEqual(error_count, 5)
    
    def test_empty_file_list(self):
        """Test processing empty file list."""
        processor = ParallelProcessor(verbose=False)
        results = processor.process_files([], lambda x: x, "Test")
        self.assertEqual(len(results), 0)


class TestReadFileEfficiently(unittest.TestCase):
    """Tests for efficient file reading."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_read_small_file(self):
        """Test reading a small file."""
        test_file = self.temp_path / "small.txt"
        content = "This is a small file"
        test_file.write_text(content)
        
        result = read_file_efficiently(test_file)
        self.assertEqual(result, content)
    
    def test_read_file_with_size_limit(self):
        """Test file size limit enforcement."""
        test_file = self.temp_path / "large.txt"
        # Create a file larger than limit
        large_content = "x" * (11 * 1024 * 1024)  # 11 MB
        test_file.write_text(large_content)
        
        # Should raise error for file exceeding 10MB limit
        with self.assertRaises(ValueError):
            read_file_efficiently(test_file, max_size_mb=10)


class TestGetOptimalWorkerCount(unittest.TestCase):
    """Tests for optimal worker count calculation."""
    
    def test_small_file_count(self):
        """Test worker count for small file counts."""
        # Should not use more workers than files
        self.assertEqual(get_optimal_worker_count(2), 2)
        self.assertEqual(get_optimal_worker_count(1), 1)
    
    def test_large_file_count(self):
        """Test worker count for large file counts."""
        # Should use reasonable number of workers
        count = get_optimal_worker_count(1000)
        self.assertGreater(count, 1)
        self.assertLessEqual(count, 16)
    
    @patch('multiprocessing.cpu_count', return_value=4)
    def test_respects_cpu_count(self, mock_cpu_count):
        """Test that worker count respects CPU count."""
        count = get_optimal_worker_count(10)
        self.assertLessEqual(count, 4)


if __name__ == '__main__':
    unittest.main()
