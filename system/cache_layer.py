"""Caching layer for API calls - Reduces rate limit pressure and improves performance.

Implements:
- TTL-based caching for API responses
- Category-specific cache policies
- Cache size limits with LRU eviction
- Cache statistics and monitoring
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any, Callable
import hashlib

LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """A cached API response."""
    
    key: str
    data: Any
    created_ts_ns: int
    ttl_seconds: int
    access_count: int
    last_accessed_ts_ns: int


class CachePolicy:
    """Cache policies for different data types."""
    
    # Crypto prices: Very short TTL (real-time data changes rapidly)
    CRYPTO_PRICE_TTL = 30  # 30 seconds
    
    # Forex rates: Short TTL (change but not as fast as crypto)
    FOREX_RATE_TTL = 60  # 60 seconds
    
    # Stock quotes: Short TTL
    STOCK_QUOTE_TTL = 60  # 60 seconds
    
    # Macro indicators: Long TTL (change slowly)
    MACRO_INDICATOR_TTL = 3600  # 1 hour
    
    # Historical data: Very long TTL (doesn't change)
    HISTORICAL_TTL = 86400  # 24 hours


class DataCache:
    """Thread-safe cache for API responses with TTL and LRU eviction."""
    
    def __init__(self, max_size: int = 1000):
        self._lock = threading.RLock()
        self._cache: dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._hits: int = 0
        self._misses: int = 0
        self._evictions: int = 0
    
    def _make_key(self, provider: str, method: str, params: tuple) -> str:
        """Create a cache key from provider, method, and parameters."""
        key_str = f"{provider}:{method}:{params}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, provider: str, method: str, params: tuple, ttl_seconds: int) -> Any | None:
        """Get cached value if not expired."""
        key = self._make_key(provider, method, params)
        
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            entry = self._cache[key]
            now_ns = int(datetime.now(UTC).timestamp() * 1_000_000_000)
            age_seconds = (now_ns - entry.created_ts_ns) / 1_000_000_000
            
            if age_seconds > entry.ttl_seconds:
                # Expired, remove
                del self._cache[key]
                self._misses += 1
                return None
            
            # Update access tracking
            self._cache[key] = CacheEntry(
                **{
                    **entry.__dict__,
                    "access_count": entry.access_count + 1,
                    "last_accessed_ts_ns": now_ns,
                }
            )
            self._hits += 1
            return entry.data
    
    def set(self, provider: str, method: str, params: tuple, data: Any, ttl_seconds: int) -> None:
        """Cache a value."""
        key = self._make_key(provider, method, params)
        now_ns = int(datetime.now(UTC).timestamp() * 1_000_000_000)
        
        with self._lock:
            # LRU eviction if at max size
            if len(self._cache) >= self._max_size:
                self._evict_lru()
            
            self._cache[key] = CacheEntry(
                key=key,
                data=data,
                created_ts_ns=now_ns,
                ttl_seconds=ttl_seconds,
                access_count=0,
                last_accessed_ts_ns=now_ns,
            )
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return
        
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed_ts_ns)
        del self._cache[lru_key]
        self._evictions += 1
        LOG.debug(f"Evicted LRU cache entry: {lru_key}")
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            LOG.info("Cache cleared")
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": hit_rate,
            }
    
    def invalidate_pattern(self, provider: str | None = None) -> int:
        """Invalidate all entries matching a pattern (e.g., provider)."""
        with self._lock:
            if provider is None:
                count = len(self._cache)
                self._cache.clear()
                LOG.info(f"Invalidated all cache entries: {count}")
                return count
            
            keys_to_delete = [
                key for key in self._cache.keys()
                if key.startswith(provider.lower())
            ]
            
            for key in keys_to_delete:
                del self._cache[key]
            
            LOG.info(f"Invalidated {len(keys_to_delete)} cache entries for {provider}")
            return len(keys_to_delete)


class CachedAPIFetcher:
    """API fetcher with automatic caching."""
    
    def __init__(self, cache_max_size: int = 1000):
        self._cache = DataCache(max_size=cache_max_size)
        self._fetcher = None  # Will be set externally
    
    def set_fetcher(self, fetcher: Callable) -> None:
        """Set the actual API fetcher function."""
        self._fetcher = fetcher
    
    def fetch(self, provider: str, method: str, params: tuple = (), ttl_seconds: int = 60) -> Any:
        """Fetch with caching."""
        # Try cache first
        cached = self._cache.get(provider, method, params, ttl_seconds)
        if cached is not None:
            return cached
        
        # Cache miss, fetch from API
        if self._fetcher:
            data = self._fetcher(provider, method, params)
            # Cache the result
            self._cache.set(provider, method, params, data, ttl_seconds)
            return data
        else:
            LOG.warning("No fetcher configured, returning None")
            return None
    
    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return self._cache.get_stats()
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()


# Singleton cache instance
_cache_fetcher: CachedAPIFetcher | None = None
_cache_lock = threading.Lock()


def get_cached_fetcher(cache_max_size: int = 1000) -> CachedAPIFetcher:
    """Get the singleton cached API fetcher."""
    global _cache_fetcher, _cache_lock
    
    with _cache_lock:
        if _cache_fetcher is None:
            _cache_fetcher = CachedAPIFetcher(cache_max_size=cache_max_size)
        return _cache_fetcher
