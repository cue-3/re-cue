"""
Tests for cache manager functionality.
"""

import json
import tempfile
import time
import unittest
from pathlib import Path

from reverse_engineer.cache_manager import (
    CacheManager,
    CacheStatistics
)


class TestCacheManager(unittest.TestCase):
    """Tests for CacheManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.cache_dir = self.temp_path / "cache"
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_initialization(self):
        """Test cache manager initialization."""
        cache = CacheManager(self.cache_dir)
        
        # Check cache directory was created
        self.assertTrue(self.cache_dir.exists())
        self.assertTrue(self.cache_dir.is_dir())
        
        # Check cache file path
        self.assertTrue(str(cache.cache_file).endswith("analysis_cache.json"))
    
    def test_put_and_get(self):
        """Test basic cache put and get operations."""
        cache = CacheManager(self.cache_dir)
        
        # Create test file
        test_file = self.temp_path / "test.py"
        test_file.write_text("print('hello')")
        
        # Cache a result
        result = {"endpoints": ["/api/test"], "count": 1}
        cache.put(test_file, result)
        
        # Retrieve cached result
        cached_result = cache.get(test_file)
        self.assertIsNotNone(cached_result)
        self.assertEqual(cached_result, result)
    
    def test_cache_miss_for_new_file(self):
        """Test cache miss for files not in cache."""
        cache = CacheManager(self.cache_dir)
        
        test_file = self.temp_path / "test.py"
        test_file.write_text("print('hello')")
        
        # Try to get non-existent cache entry
        result = cache.get(test_file)
        self.assertIsNone(result)
        
        # Check statistics
        stats = cache.get_statistics()
        self.assertEqual(stats.misses, 1)
        self.assertEqual(stats.hits, 0)
    
    def test_cache_invalidation_on_file_change(self):
        """Test that cache is invalidated when file changes."""
        cache = CacheManager(self.cache_dir)
        
        test_file = self.temp_path / "test.py"
        test_file.write_text("print('hello')")
        
        # Cache a result
        result1 = {"version": 1}
        cache.put(test_file, result1)
        
        # Verify cache hit
        cached = cache.get(test_file)
        self.assertEqual(cached, result1)
        
        # Modify file
        test_file.write_text("print('goodbye')")
        
        # Should be cache miss due to file change
        cached = cache.get(test_file)
        self.assertIsNone(cached)
    
    def test_persistence(self):
        """Test that cache persists across instances."""
        test_file = self.temp_path / "test.py"
        test_file.write_text("print('hello')")
        
        # Create cache and store result
        cache1 = CacheManager(self.cache_dir)
        result = {"data": "test"}
        cache1.put(test_file, result)
        cache1.save_cache()
        
        # Create new cache instance
        cache2 = CacheManager(self.cache_dir)
        
        # Should load cached result
        cached = cache2.get(test_file)
        self.assertEqual(cached, result)
    
    def test_multiple_analysis_types(self):
        """Test caching different analysis types for same file."""
        cache = CacheManager(self.cache_dir)
        
        test_file = self.temp_path / "test.py"
        test_file.write_text("print('hello')")
        
        # Cache different analysis results
        result_endpoints = {"endpoints": ["/api/test"]}
        result_models = {"models": ["User", "Post"]}
        
        cache.put(test_file, result_endpoints, analysis_type="endpoints")
        cache.put(test_file, result_models, analysis_type="models")
        
        # Retrieve each analysis type
        cached_endpoints = cache.get(test_file, analysis_type="endpoints")
        cached_models = cache.get(test_file, analysis_type="models")
        
        self.assertEqual(cached_endpoints, result_endpoints)
        self.assertEqual(cached_models, result_models)
    
    def test_statistics_tracking(self):
        """Test cache statistics tracking."""
        cache = CacheManager(self.cache_dir)
        
        test_file1 = self.temp_path / "test1.py"
        test_file1.write_text("print('1')")
        test_file2 = self.temp_path / "test2.py"
        test_file2.write_text("print('2')")
        
        # Put two files
        cache.put(test_file1, {"data": "1"})
        cache.put(test_file2, {"data": "2"})
        
        # Get one hit and one miss
        cache.get(test_file1)  # hit
        cache.get(self.temp_path / "nonexistent.py")  # miss
        
        stats = cache.get_statistics()
        self.assertEqual(stats.hits, 1)
        self.assertEqual(stats.misses, 1)
        self.assertEqual(stats.total_entries, 2)
        self.assertEqual(stats.hit_rate, 50.0)
    
    def test_invalidate_single_entry(self):
        """Test invalidating a single cache entry."""
        cache = CacheManager(self.cache_dir)
        
        test_file1 = self.temp_path / "test1.py"
        test_file1.write_text("print('1')")
        test_file2 = self.temp_path / "test2.py"
        test_file2.write_text("print('2')")
        
        cache.put(test_file1, {"data": "1"})
        cache.put(test_file2, {"data": "2"})
        
        # Invalidate one entry
        cache.invalidate(test_file1)
        
        # Check results
        self.assertIsNone(cache.get(test_file1))
        self.assertIsNotNone(cache.get(test_file2))
    
    def test_invalidate_all(self):
        """Test clearing all cache entries."""
        cache = CacheManager(self.cache_dir)
        
        test_file1 = self.temp_path / "test1.py"
        test_file1.write_text("print('1')")
        test_file2 = self.temp_path / "test2.py"
        test_file2.write_text("print('2')")
        
        cache.put(test_file1, {"data": "1"})
        cache.put(test_file2, {"data": "2"})
        
        # Clear all
        cache.invalidate_all()
        
        # Check results
        self.assertIsNone(cache.get(test_file1))
        self.assertIsNone(cache.get(test_file2))
        
        stats = cache.get_statistics()
        self.assertEqual(stats.total_entries, 0)
    
    def test_max_entries_limit(self):
        """Test that cache respects max entries limit."""
        cache = CacheManager(self.cache_dir, max_entries=3)
        
        # Add 5 files (should keep only 3)
        for i in range(5):
            test_file = self.temp_path / f"test{i}.py"
            test_file.write_text(f"print({i})")
            cache.put(test_file, {"data": i})
            time.sleep(0.01)  # Ensure different timestamps
        
        stats = cache.get_statistics()
        self.assertEqual(stats.total_entries, 3)
    
    def test_ttl_expiration(self):
        """Test that cache entries expire based on TTL."""
        # Create cache with 1 second TTL
        cache = CacheManager(self.cache_dir, ttl_seconds=1)
        
        test_file = self.temp_path / "test.py"
        test_file.write_text("print('hello')")
        
        # Cache a result
        cache.put(test_file, {"data": "test"})
        
        # Should be available immediately
        self.assertIsNotNone(cache.get(test_file))
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        self.assertIsNone(cache.get(test_file))
    
    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = CacheManager(self.cache_dir, ttl_seconds=1)
        
        test_file1 = self.temp_path / "test1.py"
        test_file1.write_text("print('1')")
        test_file2 = self.temp_path / "test2.py"
        test_file2.write_text("print('2')")
        
        cache.put(test_file1, {"data": "1"})
        time.sleep(1.1)
        cache.put(test_file2, {"data": "2"})
        
        # Clean up expired entries
        removed = cache.cleanup_expired()
        
        self.assertEqual(removed, 1)
        self.assertIsNone(cache.get(test_file1))
        self.assertIsNotNone(cache.get(test_file2))
    
    def test_cleanup_invalid(self):
        """Test cleanup of invalid entries (deleted/changed files)."""
        cache = CacheManager(self.cache_dir)
        
        test_file1 = self.temp_path / "test1.py"
        test_file1.write_text("print('1')")
        test_file2 = self.temp_path / "test2.py"
        test_file2.write_text("print('2')")
        
        cache.put(test_file1, {"data": "1"})
        cache.put(test_file2, {"data": "2"})
        
        # Delete one file and modify another
        test_file1.unlink()
        test_file2.write_text("print('modified')")
        
        # Clean up invalid entries
        removed = cache.cleanup_invalid()
        
        self.assertEqual(removed, 2)
        stats = cache.get_statistics()
        self.assertEqual(stats.total_entries, 0)
    
    def test_get_cached_files(self):
        """Test getting list of cached files."""
        cache = CacheManager(self.cache_dir)
        
        test_file1 = self.temp_path / "test1.py"
        test_file1.write_text("print('1')")
        test_file2 = self.temp_path / "test2.py"
        test_file2.write_text("print('2')")
        
        cache.put(test_file1, {"data": "1"}, analysis_type="endpoints")
        cache.put(test_file2, {"data": "2"}, analysis_type="endpoints")
        cache.put(test_file1, {"data": "models"}, analysis_type="models")
        
        # Get cached files for specific analysis type
        cached_endpoints = cache.get_cached_files(analysis_type="endpoints")
        self.assertEqual(len(cached_endpoints), 2)
        
        cached_models = cache.get_cached_files(analysis_type="models")
        self.assertEqual(len(cached_models), 1)
    
    def test_metadata_storage(self):
        """Test storing and retrieving metadata with cache entries."""
        cache = CacheManager(self.cache_dir)
        
        test_file = self.temp_path / "test.py"
        test_file.write_text("print('hello')")
        
        metadata = {
            "analyzer_version": "1.0",
            "analysis_duration": 0.5,
            "framework": "Flask"
        }
        
        cache.put(test_file, {"data": "test"}, metadata=metadata)
        
        # Save and reload to test persistence
        cache.save_cache()
        cache2 = CacheManager(self.cache_dir)
        
        # Verify metadata persisted
        key = cache2._compute_key(test_file, "default")
        entry = cache2._cache[key]
        self.assertEqual(entry.metadata, metadata)
    
    def test_concurrent_cache_operations(self):
        """Test that multiple operations work correctly."""
        cache = CacheManager(self.cache_dir)
        
        # Create multiple test files
        files = []
        for i in range(10):
            test_file = self.temp_path / f"test{i}.py"
            test_file.write_text(f"print({i})")
            files.append(test_file)
            cache.put(test_file, {"data": i})
        
        # Mix of hits and misses
        for i in range(5):
            self.assertIsNotNone(cache.get(files[i]))
        
        for i in range(5, 10):
            files[i].write_text(f"print('modified {i}')")
            self.assertIsNone(cache.get(files[i]))
        
        stats = cache.get_statistics()
        self.assertEqual(stats.hits, 5)
        self.assertEqual(stats.misses, 5)
    
    def test_empty_file_hash(self):
        """Test caching of empty files."""
        cache = CacheManager(self.cache_dir)
        
        test_file = self.temp_path / "empty.py"
        test_file.write_text("")
        
        cache.put(test_file, {"data": "empty"})
        
        # Should be able to retrieve
        cached = cache.get(test_file)
        self.assertEqual(cached, {"data": "empty"})
    
    def test_large_cache_entries(self):
        """Test caching of large results."""
        cache = CacheManager(self.cache_dir)
        
        test_file = self.temp_path / "large.py"
        test_file.write_text("print('large')")
        
        # Create large result
        large_result = {
            "endpoints": [f"/api/endpoint{i}" for i in range(1000)],
            "models": [f"Model{i}" for i in range(500)]
        }
        
        cache.put(test_file, large_result)
        
        # Should be able to retrieve
        cached = cache.get(test_file)
        self.assertEqual(len(cached["endpoints"]), 1000)
        self.assertEqual(len(cached["models"]), 500)
    
    def test_cache_file_format(self):
        """Test that cache file has correct JSON format."""
        cache = CacheManager(self.cache_dir)
        
        test_file = self.temp_path / "test.py"
        test_file.write_text("print('hello')")
        
        cache.put(test_file, {"data": "test"})
        cache.save_cache()
        
        # Verify cache file format
        with open(cache.cache_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('version', data)
        self.assertIn('timestamp', data)
        self.assertIn('entries', data)
        self.assertIn('statistics', data)
        
        self.assertEqual(data['version'], '1.0')


class TestCacheStatistics(unittest.TestCase):
    """Tests for CacheStatistics class."""
    
    def test_hit_rate_calculation(self):
        """Test hit rate calculation."""
        stats = CacheStatistics(hits=7, misses=3)
        self.assertEqual(stats.hit_rate, 70.0)
    
    def test_hit_rate_zero_total(self):
        """Test hit rate with zero total accesses."""
        stats = CacheStatistics(hits=0, misses=0)
        self.assertEqual(stats.hit_rate, 0.0)
    
    def test_hit_rate_perfect(self):
        """Test perfect hit rate."""
        stats = CacheStatistics(hits=10, misses=0)
        self.assertEqual(stats.hit_rate, 100.0)
    
    def test_hit_rate_zero(self):
        """Test zero hit rate."""
        stats = CacheStatistics(hits=0, misses=10)
        self.assertEqual(stats.hit_rate, 0.0)


if __name__ == '__main__':
    unittest.main()
