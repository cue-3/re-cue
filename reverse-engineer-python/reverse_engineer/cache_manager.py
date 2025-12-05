"""
Cache management for incremental analysis.

DEPRECATED: This module has been moved to reverse_engineer.performance.cache_manager
This file is kept for backward compatibility only.
"""

# Re-export from new location for backward compatibility
from .performance.cache_manager import CacheEntry, CacheManager, CacheStatistics

__all__ = ["CacheManager", "CacheEntry", "CacheStatistics"]
