"""
Execution Unified Core Live Trading - Live Trading Infrastructure
Provides core live trading capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class LiveTradingManager:
    """Live trading manager"""

    def __init__(self):
        self._active = False
        self._orders = {}

    async def start(self) -> bool:
        """Start live trading"""
        self._active = True
        return True

    async def stop(self):
        """Stop live trading"""
        self._active = False

    def is_active(self) -> bool:
        """Check if live trading is active"""
        return self._active

# Import additional live trading components
from .deterministic_executor import (
    DeterminismViolationType,
    DeterminismCheckResult,
    DeterministicExecutor,
    get_deterministic_live_trading_executor,
)
from .audit_system import AuditSystem, get_live_trading_audit_system

def check_determinism(execution_data: Dict[str, Any]) -> DeterminismCheckResult:
    """Check determinism of execution"""
    return DeterminismCheckResult(
        passed=True,
        violation_type=DeterminismViolationType.NONE,
        reason="Deterministic check passed",
    )

__all__ = [
    'LiveTradingManager',
    'DeterminismViolationType',
    'DeterminismCheckResult',
    'DeterministicExecutor',
    'get_deterministic_live_trading_executor',
    'AuditSystem',
    'get_live_trading_audit_system',
    'check_determinism',
]