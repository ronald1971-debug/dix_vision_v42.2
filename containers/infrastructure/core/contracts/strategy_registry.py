"""
Core Contracts Strategy Registry
Real implementation for strategy registry management
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time

class StrategyKind(Enum):
    """Strategy kind enumeration"""
    TRADING = "trading"
    INVESTMENT = "investment"
    SPECULATION = "speculation"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"
    HEDGING = "hedging"
    ALLOCATION = "allocation"
    RISK_MANAGEMENT = "risk_management"

class StrategyStatus(Enum):
    """Strategy status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    VALIDATING = "validating"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"
    FAILED = "failed"

class StrategyLifecycle(Enum):
    """Strategy lifecycle enumeration"""
    CREATED = "created"
    PROPOSED = "proposed"
    VALIDATED = "validated"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    RETIRED = "retired"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DELETED = "deleted"

class StrategyLifecycleError(Exception):
    """Strategy lifecycle error"""
    def __init__(self, message: str, current_lifecycle: StrategyLifecycle, expected_lifecycles: List[StrategyLifecycle]):
        self.current_lifecycle = current_lifecycle
        self.expected_lifecycles = expected_lifecycles
        super().__init__(f"{message} (current: {current_lifecycle.value}, expected: {[l.value for l in expected_lifecycles]})")

@dataclass
class StrategyRecord:
    """Strategy record information"""
    strategy_id: str
    strategy_name: str
    kind: StrategyKind
    status: StrategyStatus
    version: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    parameters: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """Check if strategy is active"""
        return self.status == StrategyStatus.ACTIVE
    
    def is_deprecated(self) -> bool:
        """Check if strategy is deprecated"""
        return self.status in [StrategyStatus.DEPRECATED, StrategyStatus.ARCHIVED]

class StrategyRegistry:
    """Registry for strategy records"""
    def __init__(self):
        self._strategies: Dict[str, StrategyRecord] = {}
        self._strategies_by_kind: Dict[StrategyKind, List[str]] = {
            kind: [] for kind in StrategyKind
        }
    
    def register_strategy(self, strategy: StrategyRecord) -> bool:
        """Register a strategy"""
        self._strategies[strategy.strategy_id] = strategy
        if strategy.kind not in self._strategies_by_kind:
            self._strategies_by_kind[strategy.kind] = []
        self._strategies_by_kind[strategy.kind].append(strategy.strategy_id)
        return True
    
    def get_strategy(self, strategy_id: str) -> Optional[StrategyRecord]:
        """Get a specific strategy"""
        return self._strategies.get(strategy_id)
    
    def get_strategies_by_kind(self, kind: StrategyKind) -> List[StrategyRecord]:
        """Get all strategies of a kind"""
        strategy_ids = self._strategies_by_kind.get(kind, [])
        return [self._strategies[sid] for sid in strategy_ids if sid in self._strategies]
    
    def get_active_strategies(self) -> List[StrategyRecord]:
        """Get all active strategies"""
        return [s for s in self._strategies.values() if s.is_active()]

# Global strategy registry
_strategy_registry: Optional[StrategyRegistry] = None

def get_strategy_registry() -> StrategyRegistry:
    """Get the global strategy registry"""
    global _strategy_registry
    if _strategy_registry is None:
        _strategy_registry = StrategyRegistry()
    return _strategy_registry

def is_legal_transition(current_lifecycle: StrategyLifecycle, target_lifecycle: StrategyLifecycle) -> bool:
    """Check if a lifecycle transition is legal"""
    # Define legal transitions
    legal_transitions = {
        StrategyLifecycle.CREATED: [StrategyLifecycle.PROPOSED, StrategyLifecycle.DELETED],
        StrategyLifecycle.PROPOSED: [StrategyLifecycle.VALIDATED, StrategyLifecycle.APPROVED, StrategyLifecycle.DELETED],
        StrategyLifecycle.VALIDATED: [StrategyLifecycle.APPROVED, StrategyLifecycle.PROPOSED, StrategyLifecycle.DELETED],
        StrategyLifecycle.APPROVED: [StrategyLifecycle.DEPLOYED, StrategyLifecycle.PROPOSED],
        StrategyLifecycle.DEPLOYED: [StrategyLifecycle.ACTIVE, StrategyLifecycle.APPROVED],
        StrategyLifecycle.ACTIVE: [StrategyLifecycle.PAUSED, StrategyLifecycle.SUSPENDED, StrategyLifecycle.RETIRED, StrategyLifecycle.DELETED],
        StrategyLifecycle.PAUSED: [StrategyLifecycle.ACTIVE, StrategyLifecycle.RETIRED, StrategyLifecycle.DELETED],
        StrategyLifecycle.SUSPENDED: [StrategyLifecycle.ACTIVE, StrategyLifecycle.RETIRED, StrategyLifecycle.DEPRECATED, StrategyLifecycle.DELETED],
        StrategyLifecycle.RETIRED: [StrategyLifecycle.DEPRECATED, StrategyLifecycle.ACTIVE],
        StrategyLifecycle.DEPRECATED: [StrategyLifecycle.ARCHIVED, StrategyLifecycle.DELETED],
        StrategyLifecycle.ARCHIVED: [StrategyLifecycle.DELETED],
        StrategyLifecycle.DELETED: []
    }
    
    return target_lifecycle in legal_transitions.get(current_lifecycle, [])

__all__ = [
    "StrategyKind",
    "StrategyStatus",
    "StrategyLifecycle",
    "StrategyLifecycleError",
    "StrategyRecord",
    "StrategyRegistry",
    "get_strategy_registry",
    "is_legal_transition"
]