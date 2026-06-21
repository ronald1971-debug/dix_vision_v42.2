"""
Registry Operator
Real implementation for operator registry
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
import time

from core.contracts.operator_authority import (
    OperatorAuthority,
    LearningAuthority,
    PracticeAuthority,
    LiveExecutionAuthority,
    TradingDomain,
    TradingMode
)

DEFAULT_AUTHORITY = OperatorAuthority(
    learning=LearningAuthority.READ_ONLY,
    practice=PracticeAuthority.DISABLED,
    live_execution=LiveExecutionAuthority.DISABLED,
    operator_id="default",
    granted_ts_ns=0,
    notes="Default read-only authority"
)

class OperatorStatus(Enum):
    """Operator status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    BUSY = "busy"

@dataclass
class Operator:
    """Operator information"""
    operator_id: str
    name: str
    email: str = ""
    status: OperatorStatus = OperatorStatus.OFFLINE
    permissions: List[str] = field(default_factory=list)
    last_active: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class OperatorRegistry:
    """Registry for operator management"""
    
    def __init__(self):
        self._operators: Dict[str, Operator] = {}
        self._current_operator: Optional[str] = None
    
    def register(self, operator: Operator) -> bool:
        """Register an operator"""
        self._operators[operator.operator_id] = operator
        return True
    
    def get_operator(self, operator_id: str) -> Optional[Operator]:
        """Get operator by ID"""
        return self._operators.get(operator_id)
    
    def get_all_operators(self) -> List[Operator]:
        """Get all operators"""
        return list(self._operators.values())
    
    def set_current_operator(self, operator_id: str) -> bool:
        """Set current operator"""
        if operator_id in self._operators:
            self._current_operator = operator_id
            return True
        return False
    
    def get_current_operator(self) -> Optional[Operator]:
        """Get current operator"""
        if self._current_operator:
            return self._operators.get(self._current_operator)
        return None
    
    def update_status(self, operator_id: str, status: OperatorStatus) -> bool:
        """Update operator status"""
        if operator_id in self._operators:
            self._operators[operator_id].status = status
            self._operators[operator_id].last_active = time.time()
            return True
        return False

def get_operator_registry() -> OperatorRegistry:
    """Get the global operator registry"""
    return OperatorRegistry()

__all__ = [
    "DEFAULT_AUTHORITY",
    "OperatorStatus",
    "Operator",
    "OperatorRegistry",
    "get_operator_registry"
]
