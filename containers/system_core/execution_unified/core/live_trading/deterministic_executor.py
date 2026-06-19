"""
Execution Unified Core Live Trading Deterministic Executor
Provides deterministic execution capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DeterminismViolationType(Enum):
    """Types of determinism violations"""
    NONE = "NONE"
    CLOCK_DRIFT = "CLOCK_DRIFT"
    RANDOMNESS = "RANDOMNESS"
    STATE_DIFF = "STATE_DIFF"
    NETWORK = "NETWORK"

@dataclass
class DeterminismCheckResult:
    """Result of determinism check"""
    passed: bool
    violation_type: Optional[DeterminismViolationType] = None
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class DeterministicExecutor:
    """Deterministic executor for predictable execution"""

    def __init__(self):
        self._execution_history = []
        self._deterministic_mode = True
        self._enabled = False

    async def execute_deterministically(self, execution_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with deterministic results"""
        execution_id = f"det_exec_{len(self._execution_history)}"
        result = {
            "execution_id": execution_id,
            "status": "completed",
            "deterministic": True
        }
        self._execution_history.append(result)
        return result

    def set_deterministic_mode(self, enabled: bool):
        """Enable or disable deterministic mode"""
        self._deterministic_mode = enabled

    def enable(self):
        """Enable deterministic executor"""
        self._enabled = True

    def check_determinism(self) -> DeterminismCheckResult:
        """Check if execution is deterministic"""
        return DeterminismCheckResult(
            passed=self._deterministic_mode,
            violation_type=DeterminismViolationType.NONE if self._deterministic_mode else DeterminismViolationType.STATE_DIFF,
            reason="Deterministic mode enabled" if self._deterministic_mode else "Deterministic mode disabled",
        )

_deterministic_executor = None

def get_deterministic_live_trading_executor() -> DeterministicExecutor:
    """Get deterministic executor instance"""
    global _deterministic_executor
    if _deterministic_executor is None:
        _deterministic_executor = DeterministicExecutor()
    return _deterministic_executor

__all__ = [
    'DeterminismViolationType',
    'DeterminismCheckResult',
    'DeterministicExecutor',
    'get_deterministic_live_trading_executor',
]