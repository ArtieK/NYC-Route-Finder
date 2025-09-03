"""
Simple caching utilities for API responses.
"""
from datetime import datetime, timedelta
from typing import Any, Optional


class SimpleCache:
    """
    In-memory cache for API responses with TTL support.
    """

    def __init__(self):
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str, ttl_seconds: int = 300) -> Optional[Any]:
        """
        Get value from cache if it exists and hasn't expired.

        Args:
            key: Cache key
            ttl_seconds: Time to live in seconds (default 5 minutes)

        Returns:
            Cached value or None if expired/missing
        """
        if key not in self._cache:
            return None

        timestamp = self._timestamps.get(key)
        if not timestamp:
            return None

        age = (datetime.now() - timestamp).total_seconds()
        if age > ttl_seconds:
            # Expired, remove from cache
            del self._cache[key]
            del self._timestamps[key]
            return None

        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
        self._timestamps[key] = datetime.now()

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        self._timestamps.clear()

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)


# Global cache instance
api_cache = SimpleCache()
