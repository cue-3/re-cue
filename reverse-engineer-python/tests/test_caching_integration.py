"""
Integration tests for caching with optimized analyzer.
"""

import tempfile
import time
import unittest
from pathlib import Path

from reverse_engineer.optimized_analyzer import OptimizedAnalyzer


def simple_file_processor(file_path: Path) -> dict:
    """Simple processor for testing."""
    content = file_path.read_text()
    return {
        'file': str(file_path),
        'length': len(content),
        'lines': content.count('\n')
    }


class TestCachingIntegration(unittest.TestCase):
    """Integration tests for caching with optimized analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create test files
        self.test_files = []
        for i in range(5):
            test_file = self.temp_path / f"test{i}.py"
            test_file.write_text(f"print({i})\n" * (i + 1))
            self.test_files.append(test_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_caching_speeds_up_rerun(self):
        """Test that caching speeds up re-runs."""
        analyzer = OptimizedAnalyzer(
            repo_root=self.temp_path,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        # First run - no cache
        start = time.time()
        results1 = analyzer.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="First run"
        )
        time1 = time.time() - start
        
        # Verify results
        self.assertEqual(len(results1), len(self.test_files))
        
        # Check cache stats
        stats = analyzer.cache_manager.get_statistics()
        self.assertEqual(stats.total_entries, len(self.test_files))
        self.assertEqual(stats.hits, 0)
        self.assertEqual(stats.misses, len(self.test_files))
        
        # Second run - should use cache
        analyzer2 = OptimizedAnalyzer(
            repo_root=self.temp_path,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        start = time.time()
        results2 = analyzer2.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="Second run"
        )
        time2 = time.time() - start
        
        # Verify results match
        self.assertEqual(len(results2), len(results1))
        
        # Check cache was used
        stats2 = analyzer2.cache_manager.get_statistics()
        self.assertEqual(stats2.hits, len(self.test_files))
        
        # Second run should be faster (or at least not significantly slower)
        # Note: In a real scenario, the speedup would be more noticeable
        # For this simple test, we just verify cache was used
        print(f"\nFirst run: {time1:.4f}s, Second run: {time2:.4f}s")
    
    def test_cache_invalidation_on_file_change(self):
        """Test that cache is invalidated when files change."""
        analyzer = OptimizedAnalyzer(
            repo_root=self.temp_path,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        # First run
        analyzer.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="First run"
        )
        
        # Save cache to ensure persistence
        analyzer.cache_manager.save_cache()
        
        # Modify one file
        modified_file = self.test_files[2]
        modified_file.write_text("print('modified')\n" * 10)
        
        # Second run - new analyzer instance loads existing cache
        analyzer2 = OptimizedAnalyzer(
            repo_root=self.temp_path,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        # Before processing, cache should have 5 entries from first run
        stats_before = analyzer2.cache_manager.get_statistics()
        self.assertEqual(stats_before.total_entries, 5)
        # Stats are cumulative and loaded from disk, including previous run's misses
        prev_misses = stats_before.misses
        
        analyzer2.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="Second run"
        )
        
        # After processing
        stats_after = analyzer2.cache_manager.get_statistics()
        # 4 files unchanged = cache hit, 1 file modified = cache miss and reprocess
        # Total entries should still be 5 (modified entry gets updated)
        self.assertEqual(stats_after.total_entries, 5)
        # New misses should be just 1 (the modified file)
        new_misses = stats_after.misses - prev_misses
        self.assertEqual(new_misses, 1)
    
    def test_cache_disabled(self):
        """Test that analysis works with caching disabled."""
        analyzer = OptimizedAnalyzer(
            repo_root=self.temp_path,
            enable_caching=False,
            enable_incremental=False,  # Disable incremental too for this test
            enable_parallel=False,
            verbose=False
        )
        
        # First run
        results1 = analyzer.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="First run"
        )
        
        # Verify results
        self.assertEqual(len(results1), len(self.test_files))
        
        # Cache manager should be None
        self.assertIsNone(analyzer.cache_manager)
        
        # Second run
        results2 = analyzer.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="Second run"
        )
        
        # Should still work
        self.assertEqual(len(results2), len(self.test_files))
    
    def test_mixed_cached_and_new_files(self):
        """Test processing mix of cached and new files."""
        analyzer = OptimizedAnalyzer(
            repo_root=self.temp_path,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        # First run with subset of files
        subset = self.test_files[:3]
        results1 = analyzer.process_files_optimized(
            subset,
            simple_file_processor,
            desc="First run"
        )
        
        self.assertEqual(len(results1), 3)
        analyzer.cache_manager.save_cache()
        
        # Second run with all files (includes new ones) - fresh analyzer
        analyzer2 = OptimizedAnalyzer(
            repo_root=self.temp_path,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        # Before processing
        stats_before = analyzer2.cache_manager.get_statistics()
        prev_misses = stats_before.misses
        prev_hits = stats_before.hits
        
        results2 = analyzer2.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="Second run"
        )
        
        self.assertEqual(len(results2), len(self.test_files))
        
        # Check cache stats - calculate new hits/misses from this run
        stats_after = analyzer2.cache_manager.get_statistics()
        new_hits = stats_after.hits - prev_hits
        new_misses = stats_after.misses - prev_misses
        
        # First 3 files should be cache hits, last 2 should be misses
        self.assertEqual(new_hits, 3)  
        self.assertEqual(new_misses, 2)
    
    def test_cache_cleanup(self):
        """Test cache cleanup methods."""
        analyzer = OptimizedAnalyzer(
            repo_root=self.temp_path,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        # Process files
        analyzer.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="Initial run"
        )
        
        # Check initial cache
        stats = analyzer.cache_manager.get_statistics()
        self.assertEqual(stats.total_entries, len(self.test_files))
        
        # Delete some files
        self.test_files[0].unlink()
        self.test_files[1].unlink()
        
        # Modify one file
        self.test_files[2].write_text("modified content")
        
        # Cleanup invalid entries
        removed = analyzer.cleanup_cache()
        
        # Should remove 3 entries (2 deleted + 1 modified)
        self.assertEqual(removed, 3)
        
        # Check updated cache
        stats = analyzer.cache_manager.get_statistics()
        self.assertEqual(stats.total_entries, 2)
    
    def test_clear_cache(self):
        """Test clearing all cache entries."""
        analyzer = OptimizedAnalyzer(
            repo_root=self.temp_path,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        # Process files
        analyzer.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="Initial run"
        )
        
        # Verify cache has entries
        stats = analyzer.cache_manager.get_statistics()
        self.assertEqual(stats.total_entries, len(self.test_files))
        
        # Clear cache
        analyzer.clear_cache()
        
        # Verify cache is empty
        stats = analyzer.cache_manager.get_statistics()
        self.assertEqual(stats.total_entries, 0)
    
    def test_analysis_type_separation(self):
        """Test that different analysis types are cached separately."""
        analyzer = OptimizedAnalyzer(
            repo_root=self.temp_path,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        # Process files with first analysis type
        analyzer.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="Endpoints analysis",
            analysis_type="endpoints"
        )
        
        # Check cache after first run
        stats1 = analyzer.cache_manager.get_statistics()
        self.assertEqual(stats1.total_entries, len(self.test_files))
        
        # Process same files with different analysis type
        analyzer.process_files_optimized(
            self.test_files,
            simple_file_processor,
            desc="Models analysis",
            analysis_type="models"
        )
        
        # Both analysis types should be cached separately
        stats2 = analyzer.cache_manager.get_statistics()
        self.assertEqual(stats2.total_entries, len(self.test_files) * 2)
        
        # Verify we can retrieve each type independently
        endpoints_cached = analyzer.cache_manager.get_cached_files(analysis_type="endpoints")
        models_cached = analyzer.cache_manager.get_cached_files(analysis_type="models")
        self.assertEqual(len(endpoints_cached), len(self.test_files))
        self.assertEqual(len(models_cached), len(self.test_files))


if __name__ == '__main__':
    unittest.main()
