"""
Cache manager for analysis results to speed up re-runs.

This module provides:
- File-level caching based on content hash
- Incremental updates (only re-analyze changed files)
- Cache invalidation strategies
- Persistent cache storage
- Cache statistics reporting
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class CacheEntry:
    """Represents a cached analysis result."""

    file_path: str
    file_hash: str
    timestamp: float
    result: Any
    metadata: Optional[dict[str, Any]] = None


@dataclass
class CacheStatistics:
    """Statistics about cache usage."""

    hits: int = 0
    misses: int = 0
    total_entries: int = 0
    cache_size_bytes: int = 0
    oldest_entry: Optional[float] = None
    newest_entry: Optional[float] = None

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100.0


class CacheManager:
    """
    Manages caching of analysis results.

    Features:
    - File-level caching based on SHA-256 hash
    - Automatic cache invalidation when files change
    - Persistent storage in JSON format
    - Cache statistics tracking
    - Configurable cache directory and TTL
    """

    def __init__(
        self,
        cache_dir: Path,
        cache_name: str = "analysis_cache",
        ttl_seconds: Optional[int] = None,
        max_entries: Optional[int] = None,
    ):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files
            cache_name: Name of the cache file
            ttl_seconds: Time-to-live for cache entries (None = no expiration)
            max_entries: Maximum number of cache entries (None = unlimited)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_file = self.cache_dir / f"{cache_name}.json"
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries

        # In-memory cache
        self._cache: dict[str, CacheEntry] = {}

        # Statistics
        self._stats = CacheStatistics()

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load existing cache
        self._load_cache()

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA-256 hash of file contents.

        Args:
            file_path: Path to the file

        Returns:
            Hexadecimal hash string
        """
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            # Return empty string if file can't be read
            return ""

    def _compute_key(self, file_path: Path, analysis_type: str = "default") -> str:
        """
        Compute cache key for a file.

        Args:
            file_path: Path to the file
            analysis_type: Type of analysis (for supporting multiple analyses per file)

        Returns:
            Cache key string
        """
        # Use normalized path + analysis type as key
        normalized_path = str(file_path.resolve())
        return f"{normalized_path}:{analysis_type}"

    def _is_expired(self, entry: CacheEntry) -> bool:
        """
        Check if a cache entry has expired.

        Args:
            entry: Cache entry to check

        Returns:
            True if expired, False otherwise
        """
        if self.ttl_seconds is None:
            return False

        age_seconds = time.time() - entry.timestamp
        return age_seconds > self.ttl_seconds

    def _load_cache(self):
        """Load cache from disk."""
        if not self.cache_file.exists():
            return

        try:
            with open(self.cache_file, encoding="utf-8") as f:
                data = json.load(f)

            # Load cache entries
            for key, entry_dict in data.get("entries", {}).items():
                entry = CacheEntry(**entry_dict)
                # Skip expired entries
                if not self._is_expired(entry):
                    self._cache[key] = entry

            # Load statistics
            stats_dict = data.get("statistics", {})
            if stats_dict:
                self._stats = CacheStatistics(**stats_dict)

            # Update total entries count
            self._stats.total_entries = len(self._cache)

        except Exception as e:
            print(f"Warning: Could not load cache from {self.cache_file}: {e}")
            self._cache = {}
            self._stats = CacheStatistics()

    def save_cache(self):
        """Save cache to disk."""
        try:
            # Update statistics
            self._update_statistics()

            # Prepare data for serialization
            data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "entries": {key: asdict(entry) for key, entry in self._cache.items()},
                "statistics": asdict(self._stats),
            }

            # Write atomically: write to temp file, then rename
            temp_file = self.cache_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic rename
            temp_file.replace(self.cache_file)

        except Exception as e:
            print(f"Warning: Could not save cache to {self.cache_file}: {e}")

    def _update_statistics(self):
        """Update cache statistics."""
        self._stats.total_entries = len(self._cache)

        if self._cache:
            timestamps = [entry.timestamp for entry in self._cache.values()]
            self._stats.oldest_entry = min(timestamps)
            self._stats.newest_entry = max(timestamps)
        else:
            self._stats.oldest_entry = None
            self._stats.newest_entry = None

        # Estimate cache size
        try:
            if self.cache_file.exists():
                self._stats.cache_size_bytes = self.cache_file.stat().st_size
        except Exception as e:
            # Ignore exceptions in cache size calculation, just warn
            print(f"Warning: Could not determine cache size: {e}")

    def get(self, file_path: Path, analysis_type: str = "default") -> Optional[Any]:
        """
        Get cached result for a file.

        Args:
            file_path: Path to the file
            analysis_type: Type of analysis

        Returns:
            Cached result if valid, None otherwise
        """
        key = self._compute_key(file_path, analysis_type)

        # Check if entry exists
        if key not in self._cache:
            self._stats.misses += 1
            return None

        entry = self._cache[key]

        # Check if entry is expired
        if self._is_expired(entry):
            del self._cache[key]
            self._stats.misses += 1
            return None

        # Verify file hasn't changed
        try:
            current_hash = self._compute_file_hash(file_path)
            if current_hash != entry.file_hash:
                # File changed, invalidate cache
                del self._cache[key]
                self._stats.misses += 1
                return None
        except Exception:
            # If we can't verify, assume invalid
            self._stats.misses += 1
            return None

        # Cache hit!
        self._stats.hits += 1
        return entry.result

    def put(
        self,
        file_path: Path,
        result: Any,
        analysis_type: str = "default",
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Store analysis result in cache.

        Args:
            file_path: Path to the analyzed file
            result: Analysis result to cache
            analysis_type: Type of analysis
            metadata: Optional metadata about the analysis
        """
        try:
            key = self._compute_key(file_path, analysis_type)
            file_hash = self._compute_file_hash(file_path)

            # Create cache entry
            entry = CacheEntry(
                file_path=str(file_path.resolve()),
                file_hash=file_hash,
                timestamp=time.time(),
                result=result,
                metadata=metadata,
            )

            # Store in cache
            self._cache[key] = entry

            # Enforce max entries limit
            if self.max_entries and len(self._cache) > self.max_entries:
                self._evict_oldest()

        except Exception as e:
            print(f"Warning: Could not cache result for {file_path}: {e}")

    def _evict_oldest(self):
        """Evict oldest cache entries when limit is reached."""
        if not self._cache:
            return

        # Sort by timestamp and remove oldest entries
        entries_by_age = sorted(self._cache.items(), key=lambda x: x[1].timestamp)

        # Keep only max_entries
        num_to_remove = len(self._cache) - self.max_entries
        for i in range(num_to_remove):
            key, _ = entries_by_age[i]
            del self._cache[key]

    def invalidate(self, file_path: Path, analysis_type: str = "default"):
        """
        Invalidate cache entry for a specific file.

        Args:
            file_path: Path to the file
            analysis_type: Type of analysis
        """
        key = self._compute_key(file_path, analysis_type)
        if key in self._cache:
            del self._cache[key]

    def invalidate_all(self):
        """Clear all cache entries."""
        self._cache.clear()
        self._stats = CacheStatistics()

    def get_statistics(self) -> CacheStatistics:
        """
        Get cache statistics.

        Returns:
            CacheStatistics object
        """
        self._update_statistics()
        return self._stats

    def print_statistics(self):
        """Print cache statistics to console."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("CACHE STATISTICS")
        print("=" * 60)
        print(f"Cache File:        {self.cache_file}")
        print(f"Total Entries:     {stats.total_entries}")
        print(f"Cache Size:        {stats.cache_size_bytes:,} bytes")
        print(f"Cache Hits:        {stats.hits}")
        print(f"Cache Misses:      {stats.misses}")
        print(f"Hit Rate:          {stats.hit_rate:.1f}%")

        if stats.oldest_entry:
            oldest = datetime.fromtimestamp(stats.oldest_entry)
            print(f"Oldest Entry:      {oldest.strftime('%Y-%m-%d %H:%M:%S')}")

        if stats.newest_entry:
            newest = datetime.fromtimestamp(stats.newest_entry)
            print(f"Newest Entry:      {newest.strftime('%Y-%m-%d %H:%M:%S')}")

        print("=" * 60 + "\n")

    def get_cached_files(self, analysis_type: str = "default") -> list[Path]:
        """
        Get list of files that have cached results.

        Args:
            analysis_type: Type of analysis to filter by

        Returns:
            List of file paths with cached results
        """
        cached_files = []
        for key, entry in self._cache.items():
            if key.endswith(f":{analysis_type}"):
                cached_files.append(Path(entry.file_path))
        return cached_files

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        if self.ttl_seconds is None:
            return 0

        expired_keys = [key for key, entry in self._cache.items() if self._is_expired(entry)]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def cleanup_invalid(self) -> int:
        """
        Remove cache entries for files that no longer exist or have changed.

        Returns:
            Number of entries removed
        """
        invalid_keys = []

        for key, entry in self._cache.items():
            file_path = Path(entry.file_path)

            # Check if file exists
            if not file_path.exists():
                invalid_keys.append(key)
                continue

            # Check if file hash matches
            try:
                current_hash = self._compute_file_hash(file_path)
                if current_hash != entry.file_hash:
                    invalid_keys.append(key)
            except Exception:
                invalid_keys.append(key)

        for key in invalid_keys:
            del self._cache[key]

        return len(invalid_keys)
