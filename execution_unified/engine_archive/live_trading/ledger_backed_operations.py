"""
execution_engine.live_trading.ledger_backed_operations
DIX VISION v42.2 — Ledger-Backed Live Trading Operations (Phase 14)

Migrated from execution/live_trading/ledger_backed_operations.py

Ensures that all live trading operations are backed by the ledger as required
by Phase 14. This provides complete auditability and replay capability for
all live trading activities.

The ledger-backed operations system:
- Records every live trade operation to the ledger
- Maintains hash-chained operation logs
- Provides replay capability for live trading
- Ensures no operation can be lost or modified
- Records all state transitions
- Maintains complete decision audit trails

PHASE 14 REQUIREMENT: "Ledger backed"
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from core.contracts.events import ExecutionEvent, SignalEvent
from state.ledger.event_store import append_event


class LiveOperationType(StrEnum):
    """Types of live trading operations."""

    TRADE_REQUEST = "TRADE_REQUEST"
    TRADE_EXECUTION = "TRADE_EXECUTION"
    TRADE_FILLED = "TRADE_FILLED"
    TRADE_CANCELLED = "TRADE_CANCELLED"
    TRADE_REJECTED = "TRADE_REJECTED"
    POSITION_UPDATE = "POSITION_UPDATE"
    BALANCE_UPDATE = "BALANCE_UPDATE"
    RISK_LIMIT_BREACH = "RISK_LIMIT_BREACH"
    CIRCUIT_BREAKER_TRIGGERED = "CIRCUIT_BREAKER_TRIGGERED"


@dataclass
class LiveOperationRecord:
    """Record of a live trading operation."""

    operation_id: str
    operation_type: LiveOperationType
    venue: str
    symbol: str
    timestamp_ns: int
    payload: dict[str, Any] = field(default_factory=dict)
    previous_hash: str = ""
    operation_hash: str = ""

    def compute_hash(self) -> str:
        """Compute hash of the operation record."""
        import hashlib
        import json

        data = json.dumps(
            {
                "operation_id": self.operation_id,
                "operation_type": self.operation_type.value,
                "venue": self.venue,
                "symbol": self.symbol,
                "timestamp_ns": self.timestamp_ns,
                "payload": self.payload,
                "previous_hash": self.previous_hash,
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class LedgerBackedOperationResult:
    """Result of a ledger-backed operation."""

    operation_id: str
    recorded: bool
    ledger_event_id: str = ""
    operation_hash: str = ""
    reason: str = ""


class LiveTradingLedgerBackedOperations:
    """Ledger-backed operations for live trading.

    This class ensures that every live trading operation is recorded to the
    ledger with hash chaining, providing complete auditability and replay
    capability as required by Phase 14.

    Thread-safe singleton pattern.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._operation_log: list[LiveOperationRecord] = []
        self._listeners: list[Callable[[LiveOperationRecord], None]] = []
        self._prev_hash: str = "GENESIS"
        self._operation_counter: int = 0
        self._enabled: bool = True

    def enable(self) -> None:
        """Enable ledger-backed operation recording."""
        with self._lock:
            self._enabled = True

    def disable(self) -> None:
        """Disable ledger-backed operation recording (DANGEROUS)."""
        with self._lock:
            self._enabled = False

    def record_operation(
        self,
        operation_type: LiveOperationType,
        venue: str,
        symbol: str,
        timestamp_ns: int,
        payload: dict[str, Any],
    ) -> LedgerBackedOperationResult:
        """Record a live trading operation to the ledger.

        Args:
            operation_type: Type of operation
            venue: Trading venue
            symbol: Trading symbol
            timestamp_ns: Timestamp in nanoseconds
            payload: Operation payload

        Returns:
            Result of the recording operation
        """
        with self._lock:
            if not self._enabled:
                return LedgerBackedOperationResult(
                    operation_id="",
                    recorded=False,
                    reason="Ledger-backed operations disabled",
                )

            self._operation_counter += 1
            operation_id = f"live_op_{self._operation_counter}"

            # Create operation record
            record = LiveOperationRecord(
                operation_id=operation_id,
                operation_type=operation_type,
                venue=venue,
                symbol=symbol,
                timestamp_ns=timestamp_ns,
                payload=payload,
                previous_hash=self._prev_hash,
            )
            record.operation_hash = record.compute_hash()

            # Record to event store
            try:
                event = append_event(
                    event_type="MARKET",
                    sub_type="LIVE_TRADING_OPERATION",
                    source="LIVE_TRADING_LEDGER",
                    payload={
                        "operation_id": record.operation_id,
                        "operation_type": record.operation_type.value,
                        "venue": record.venue,
                        "symbol": record.symbol,
                        "timestamp_ns": record.timestamp_ns,
                        "payload": record.payload,
                        "previous_hash": record.previous_hash,
                        "operation_hash": record.operation_hash,
                    },
                )

                # Update hash chain
                self._prev_hash = record.operation_hash

                # Add to operation log
                self._operation_log.append(record)

                # Notify listeners
                for listener in self._listeners:
                    try:
                        listener(record)
                    except Exception:
                        pass

                return LedgerBackedOperationResult(
                    operation_id=operation_id,
                    recorded=True,
                    ledger_event_id=event.event_id,
                    operation_hash=record.operation_hash,
                )

            except Exception as e:
                return LedgerBackedOperationResult(
                    operation_id=operation_id,
                    recorded=False,
                    reason=f"Ledger recording failed: {e}",
                )

    def record_trade_execution(
        self,
        signal: SignalEvent,
        execution: ExecutionEvent,
        governance_approved: bool,
        risk_constraints_passed: bool,
    ) -> LedgerBackedOperationResult:
        """Record a complete trade execution with all context.

        Args:
            signal: The original signal event
            execution: The execution event
            governance_approved: Whether governance approved the trade
            risk_constraints_passed: Whether risk constraints passed

        Returns:
            Result of the recording operation
        """
        payload = {
            "signal_id": str(signal.event_id) if hasattr(signal, "event_id") else "",
            "execution_id": str(execution.event_id) if hasattr(execution, "event_id") else "",
            "side": execution.side.value if hasattr(execution.side, "value") else str(execution.side),
            "qty": execution.qty,
            "price": execution.price,
            "status": execution.status.value if hasattr(execution.status, "value") else str(execution.status),
            "venue": execution.venue,
            "governance_approved": governance_approved,
            "risk_constraints_passed": risk_constraints_passed,
            "timestamp_ns": execution.ts_ns,
        }

        return self.record_operation(
            operation_type=LiveOperationType.TRADE_EXECUTION,
            venue=execution.venue,
            symbol=execution.symbol,
            timestamp_ns=execution.ts_ns,
            payload=payload,
        )

    def record_position_update(
        self,
        venue: str,
        symbol: str,
        position_qty: float,
        position_value_usd: float,
        timestamp_ns: int,
    ) -> LedgerBackedOperationResult:
        """Record a position update to the ledger."""
        payload = {
            "position_qty": position_qty,
            "position_value_usd": position_value_usd,
            "timestamp_ns": timestamp_ns,
        }

        return self.record_operation(
            operation_type=LiveOperationType.POSITION_UPDATE,
            venue=venue,
            symbol=symbol,
            timestamp_ns=timestamp_ns,
            payload=payload,
        )

    def record_balance_update(
        self,
        venue: str,
        asset: str,
        balance: float,
        balance_usd: float,
        timestamp_ns: int,
    ) -> LedgerBackedOperationResult:
        """Record a balance update to the ledger."""
        payload = {
            "asset": asset,
            "balance": balance,
            "balance_usd": balance_usd,
            "timestamp_ns": timestamp_ns,
        }

        return self.record_operation(
            operation_type=LiveOperationType.BALANCE_UPDATE,
            venue=venue,
            symbol=asset,  # Using asset as symbol for balance updates
            timestamp_ns=timestamp_ns,
            payload=payload,
        )

    def verify_hash_chain(self) -> bool:
        """Verify the integrity of the operation hash chain.

        Returns:
            True if hash chain is valid, False otherwise
        """
        with self._lock:
            prev_hash = "GENESIS"
            for record in self._operation_log:
                if record.previous_hash != prev_hash:
                    return False
                computed = record.compute_hash()
                if computed != record.operation_hash:
                    return False
                prev_hash = record.operation_hash
            return True

    def get_operation_log(self, limit: int = 100) -> list[LiveOperationRecord]:
        """Get the operation log."""
        with self._lock:
            return self._operation_log[-limit:] if limit > 0 else self._operation_log.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get operation statistics."""
        with self._lock:
            operation_counts: dict[str, int] = {}
            for record in self._operation_log:
                op_type = record.operation_type.value
                operation_counts[op_type] = operation_counts.get(op_type, 0) + 1

            return {
                "enabled": self._enabled,
                "total_operations": len(self._operation_log),
                "operation_counter": self._operation_counter,
                "hash_chain_valid": self.verify_hash_chain(),
                "current_hash": self._prev_hash,
                "operation_counts": operation_counts,
            }

    def add_listener(self, listener: Callable[[LiveOperationRecord], None]) -> None:
        """Add a listener for operation records."""
        with self._lock:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[LiveOperationRecord], None]) -> None:
        """Remove a listener for operation records."""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def is_enabled(self) -> bool:
        """Check if ledger-backed operations are enabled."""
        with self._lock:
            return self._enabled


# Singleton instance
_ledger_backed_ops: LiveTradingLedgerBackedOperations | None = None
_ledger_backed_ops_lock = threading.Lock()


def get_live_trading_ledger_backed_operations() -> LiveTradingLedgerBackedOperations:
    """Get the singleton live trading ledger-backed operations."""
    global _ledger_backed_ops
    with _ledger_backed_ops_lock:
        if _ledger_backed_ops is None:
            _ledger_backed_ops = LiveTradingLedgerBackedOperations()
    return _ledger_backed_ops


__all__ = [
    "LedgerBackedOperationResult",
    "LiveOperationRecord",
    "LiveOperationType",
    "LiveTradingLedgerBackedOperations",
    "get_live_trading_ledger_backed_operations",
]
