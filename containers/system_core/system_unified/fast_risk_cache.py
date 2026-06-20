"""
System Unified Fast Risk Cache - High-Performance Risk Data Cache
Provides fast caching for risk calculations and risk data access
NO LAZY LOADING - All components load directly
"""

import logging
import time
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk level enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

@dataclass
class RiskData:
    """Risk data structure"""
    metric: str
    value: float
    level: RiskLevel
    timestamp_ns: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = datetime.now().timestamp_ns()

@dataclass
class RiskCacheEntry:
    """Risk cache entry"""
    key: str
    data: RiskData
    expiry_ns: int
    last_access_ns: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now().timestamp_ns() > self.expiry_ns

class FastRiskCache:
    """
    Fast Risk Cache - High-performance risk data caching
    
    Provides efficient caching for risk calculations and risk data access
    Required by system components for real-time risk monitoring
    """
    
    def __init__(self, default_ttl_ns: int = 60_000_000_000):  # 60 seconds default
        """Initialize fast risk cache"""
        self._cache: Dict[str, RiskCacheEntry] = {}
        self._default_ttl_ns = default_ttl_ns
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'invalidations': 0,
            'evictions': 0
        }
        logger.info("FastRiskCache initialized with default TTL: %d ns", default_ttl_ns)
    
    def get(self, key: str) -> Optional[RiskData]:
        """Get risk data from cache"""
        entry = self._cache.get(key)
        if entry is None:
            self._stats['misses'] += 1
            return None
        
        if entry.is_expired:
            self._invalidate(key)
            self._stats['misses'] += 1
            return None
        
        entry.last_access_ns = datetime.now().timestamp_ns()
        self._stats['hits'] += 1
        return entry.data
    
    def set(self, key: str, data: RiskData, ttl_ns: Optional[int] = None) -> None:
        """Set risk data in cache"""
        if ttl_ns is None:
            ttl_ns = self._default_ttl_ns
        
        expiry_ns = datetime.now().timestamp_ns() + ttl_ns
        entry = RiskCacheEntry(
            key=key,
            data=data,
            expiry_ns=expiry_ns,
            last_access_ns=datetime.now().timestamp_ns()
        )
        
        self._cache[key] = entry
        self._stats['sets'] += 1
        logger.debug("Risk data cached: %s (TTL: %d ns)", key, ttl_ns)
    
    def invalidate(self, key: str) -> bool:
        """Invalidate cache entry"""
        if key in self._cache:
            del self._cache[key]
            self._stats['invalidations'] += 1
            return True
        return False
    
    def _invalidate(self, key: str) -> None:
        """Internal invalidation without stat tracking"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        logger.info("FastRiskCache cleared")
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        current_time_ns = datetime.now().timestamp_ns()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.expiry_ns < current_time_ns
        ]
        
        for key in expired_keys:
            del self._cache[key]
            self._stats['evictions'] += 1
        
        if expired_keys:
            logger.info("Cleaned up %d expired risk cache entries", len(expired_keys))
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self._stats.copy()
    
    def get_size(self) -> int:
        """Get cache size"""
        return len(self._cache)

# Global cache instance
_global_cache: Optional[FastRiskCache] = None

def get_fast_risk_cache() -> FastRiskCache:
    """Get global fast risk cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = FastRiskCache()
    return _global_cache

def get_risk_data(key: str) -> Optional[RiskData]:
    """Get risk data from global cache"""
    cache = get_fast_risk_cache()
    return cache.get(key)

def set_risk_data(key: str, data: RiskData, ttl_ns: Optional[int] = None) -> None:
    """Set risk data in global cache"""
    cache = get_fast_risk_cache()
    cache.set(key, data, ttl_ns)

def invalidate_risk_data(key: str) -> bool:
    """Invalidate risk data in global cache"""
    cache = get_fast_risk_cache()
    return cache.invalidate(key)

def get_risk_cache() -> FastRiskCache:
    """Get global risk cache instance (alias for get_fast_risk_cache)"""
    return get_fast_risk_cache()

def initialize_cache(default_ttl_ns: int = 60_000_000_000) -> FastRiskCache:
    """Initialize global cache with custom TTL"""
    global _global_cache
    _global_cache = FastRiskCache(default_ttl_ns=default_ttl_ns)
    return _global_cache
