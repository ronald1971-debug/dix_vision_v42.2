"""
System Unified Fast Risk Cache - High-Performance Risk Management
Provides fast risk caching for real-time risk operations
NO LAZY LOADING - All components load directly
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class RiskConstraintType(Enum):
    """Risk constraint type"""
    POSITION_SIZE = "position_size"
    EXPOSURE = "exposure"
    LEVERAGE = "leverage"
    DRAWDOWN = "drawdown"
    VAR = "var"
    CONCENTRATION = "concentration"

@dataclass
class RiskConstraints:
    """Risk constraints data structure"""
    max_position_size: float = 1000000.0
    max_exposure: float = 5000000.0
    max_leverage: float = 3.0
    max_drawdown: float = 0.20
    max_var: float = 0.05
    max_concentration: float = 0.30
    risk_constraint_type: RiskConstraintType = RiskConstraintType.POSITION_SIZE
    
    def validate_position(self, position_size: float) -> bool:
        """Validate position against constraints"""
        return position_size <= self.max_position_size
    
    def validate_exposure(self, exposure: float) -> bool:
        """Validate exposure against constraints"""
        return exposure <= self.max_exposure

class FastRiskCache:
    """Fast risk cache for real-time risk operations"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = 10000
        self._hits = 0
        self._misses = 0
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get risk data from cache"""
        if key in self._cache:
            self._hits += 1
            # Update access time
            self._cache[key]['last_access'] = time.time()
            return self._cache[key]['data']
        else:
            self._misses += 1
            return None
    
    def set(self, key: str, data: Dict[str, Any], ttl_seconds: int = 300):
        """Set risk data in cache"""
        if key in self._cache:
            del self._cache[key]  # Move to end (LRU)
        
        self._cache[key] = {
            'data': data,
            'created_at': time.time(),
            'last_access': time.time(),
            'ttl': ttl_seconds
        }
        
        # Remove old entries if cache is full
        if len(self._cache) > self._max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]['created_at'])
            del self._cache[oldest_key]
    
    def invalidate(self, key: str):
        """Invalidate cached risk data"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """Clear all cached risk data"""
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'size': len(self._cache),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0.0
        }

# Global instance
_fast_risk_cache = None

def get_fast_risk_cache() -> FastRiskCache:
    """Get global fast risk cache instance"""
    global _fast_risk_cache
    if _fast_risk_cache is None:
        _fast_risk_cache = FastRiskCache()
    return _fast_risk_cache

def get_risk_data(key: str) -> Optional[Dict[str, Any]]:
    """Get risk data (convenience function)"""
    cache = get_fast_risk_cache()
    return cache.get(key)

def set_risk_data(key: str, data: Dict[str, Any], ttl_seconds: int = 300):
    """Set risk data (convenience function)"""
    cache = get_fast_risk_cache()
    cache.set(key, data, ttl_seconds)

def invalidate_risk_data(key: str):
    """Invalidate risk data (convenience function)"""
    cache = get_fast_risk_cache()
    cache.invalidate(key)

# Alias for backward compatibility
get_risk_cache = get_fast_risk_cache

__all__ = [
    'RiskConstraintType',
    'RiskConstraints',
    'FastRiskCache',
    'get_fast_risk_cache',
    'get_risk_data',
    'set_risk_data',
    'invalidate_risk_data',
    'get_risk_cache'
]