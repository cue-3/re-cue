"""Test imports from performance package."""

import unittest


class TestPerformanceImports(unittest.TestCase):
    """Test that performance modules can be imported."""

    def test_import_from_performance_package(self):
        """Test importing from new performance package."""
        from reverse_engineer.performance import (
            CacheManager,
            FileTracker,
            ProgressReporter,
            ParallelProcessor,
            OptimizedAnalyzer,
        )
        
        # Verify classes are importable
        self.assertIsNotNone(CacheManager)
        self.assertIsNotNone(FileTracker)
        self.assertIsNotNone(ProgressReporter)
        self.assertIsNotNone(ParallelProcessor)
        self.assertIsNotNone(OptimizedAnalyzer)

    def test_cache_manager_import(self):
        """Test importing CacheManager."""
        from reverse_engineer.performance.cache_manager import (
            CacheManager,
            CacheEntry,
            CacheStatistics,
        )
        
        self.assertIsNotNone(CacheManager)
        self.assertIsNotNone(CacheEntry)
        self.assertIsNotNone(CacheStatistics)

    def test_optimization_imports(self):
        """Test importing optimization components."""
        from reverse_engineer.performance.optimization import (
            FileTracker,
            ProgressReporter,
            ParallelProcessor,
        )
        
        self.assertIsNotNone(FileTracker)
        self.assertIsNotNone(ProgressReporter)
        self.assertIsNotNone(ParallelProcessor)


if __name__ == '__main__':
    unittest.main()
