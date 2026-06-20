"""
Hot-path fast risk cache - deterministic risk evaluation without IO
Phase 2 / EXEC-11 hot-path purity (T1 rule: deterministic, no IO)
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    """Deterministic risk levels for hot path"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SAFE = "safe"

@dataclass
class RiskSnapshot:
    """Risk snapshot for hot-path evaluation"""
    risk_level: RiskLevel
    confidence: float
    risk_value: float
    metadata: Dict[str, Any]
    
    def is_acceptable(self) -> bool:
        """Deterministic risk acceptability check"""
        return self.risk_level in (RiskLevel.LOW, RiskLevel.SAFE)

class FastRiskCache:
    """
    Hot-path fast risk cache - deterministic risk evaluation
    
    Provides in-memory risk evaluation without external dependencies
    Required by hot-path execution for deterministic risk gating
    """
    
    def __init__(self):
        """Initialize hot-path risk cache"""
        self._cache: Dict[str, RiskSnapshot] = {}
        self._thresholds = {
            RiskLevel.CRITICAL: 1.0,
            RiskLevel.HIGH: 0.75,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.LOW: 0.25,
            RiskLevel.SAFE: 0.0
        }
    
    def evaluate(self, risk_value: float, context: Dict[str, Any]) -> RiskSnapshot:
        """Evaluate risk deterministically based on value"""
        if risk_value >= self._thresholds[RiskLevel.CRITICAL]:
            level = RiskLevel.CRITICAL
        elif risk_value >= self._thresholds[RiskLevel.HIGH]:
            level = RiskLevel.HIGH
        elif risk_value >= self._thresholds[RiskLevel.MEDIUM]:
            level = RiskLevel.MEDIUM
        elif risk_value >= self._thresholds[RiskLevel.LOW]:
            level = RiskLevel.LOW
        else:
            level = RiskLevel.SAFE
        
        snapshot = RiskSnapshot(
            risk_level=level,
            confidence=min(1.0, risk_value / 0.5),  # Simple confidence calculation
            risk_value=risk_value,
            metadata=context
        )
        
        self._cache[f"risk_{risk_value}"] = snapshot
        return snapshot
    
    def get_cached(self, key: str) -> Optional[RiskSnapshot]:
        """Get cached risk evaluation"""
        return self._cache.get(key)
    
    def clear(self) -> None:
        """Clear cache"""
        self._cache.clear()

# Global hot-path cache instance
_global_cache: Optional[FastRiskCache] = None

def get_fast_risk_cache() -> FastRiskCache:
    """Get global hot-path cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = FastRiskCache()
    return _global_cache
