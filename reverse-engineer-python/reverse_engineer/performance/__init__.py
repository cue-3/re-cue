"""
Performance optimization utilities.

This package contains modules for caching, parallel processing,
file tracking, and optimized analysis operations.
"""

from .cache_manager import CacheManager, CacheEntry, CacheStatistics
from .optimization import (
    FileTracker,
    FileMetadata,
    ProgressReporter,
    ParallelProcessor,
    read_file_efficiently,
    get_optimal_worker_count,
)
from .optimized_analyzer import (
    OptimizedAnalyzer,
    process_java_controller,
    process_java_model,
    process_java_service,
)

__all__ = [
    # Cache management
    'CacheManager',
    'CacheEntry',
    'CacheStatistics',
    # File tracking and optimization
    'FileTracker',
    'FileMetadata',
    'ProgressReporter',
    'ParallelProcessor',
    'read_file_efficiently',
    'get_optimal_worker_count',
    # Optimized analyzer
    'OptimizedAnalyzer',
    'process_java_controller',
    'process_java_model',
    'process_java_service',
]
