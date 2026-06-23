"""
Execution Unified Core Live Trading - Ledger Backed Operations
Provides ledger-backed operations for live trading
NO LAZY LOADING - All components load directly
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class LiveOperationType(Enum):
    """Live operation types"""

    TRADE_REQUEST = "TRADE_REQUEST"
    TRADE_EXECUTION = "TRADE_EXECUTION"
    POSITION_UPDATE = "POSITION_UPDATE"
    BALANCE_UPDATE = "BALANCE_UPDATE"


@dataclass
class LiveOperationRecord:
    """Record of a live operation"""

    operation_id: str
    operation_type: LiveOperationType
    venue: str
    symbol: str
    timestamp_ns: int
    payload: Dict[str, Any] = field(default_factory=dict)
    operation_hash: str = ""


@dataclass
class LiveOperationResult:
    """Result of a live operation"""

    recorded: bool
    operation_id: str = ""
    error: str = ""


class LedgerBackedOperations:
    """Ledger-backed operations manager"""

    def __init__(self):
        self._enabled = False
        self._operations: List[LiveOperationRecord] = []

    def enable(self):
        """Enable ledger-backed operations"""
        self._enabled = True

    def is_enabled(self) -> bool:
        """Check if ledger-backed operations are enabled"""
        return self._enabled

    def record_operation(
        self,
        operation_type: LiveOperationType,
        venue: str,
        symbol: str,
        timestamp_ns: int,
        payload: Dict[str, Any] = None,
    ) -> LiveOperationResult:
        """Record a live operation to the ledger"""
        if not self._enabled:
            return LiveOperationResult(recorded=False, error="Not enabled")

        record = LiveOperationRecord(
            operation_id=f"op_{timestamp_ns}",
            operation_type=operation_type,
            venue=venue,
            symbol=symbol,
            timestamp_ns=timestamp_ns,
            payload=payload or {},
        )
        self._operations.append(record)
        return LiveOperationResult(recorded=True, operation_id=record.operation_id)


_ledger_ops = None


def get_live_trading_ledger_backed_operations() -> LedgerBackedOperations:
    """Get ledger-backed operations instance"""
    global _ledger_ops
    if _ledger_ops is None:
        _ledger_ops = LedgerBackedOperations()
    return _ledger_ops


__all__ = [
    "LiveOperationType",
    "LiveOperationRecord",
    "LiveOperationResult",
    "LedgerBackedOperations",
    "get_live_trading_ledger_backed_operations",
]
