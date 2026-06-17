"""
execution/live_trading/deterministic_executor.py
DIX VISION v42.2 — Deterministic Live Trading Executor (Phase 14)

Ensures deterministic execution for live trading as required by Phase 14.
This provides reproducible, predictable execution behavior that can be
verified and replayed.

The deterministic executor:
- Enforces deterministic order submission
- Provides deterministic timestamp ordering
- Ensures reproducible execution behavior
- Supports deterministic replay for verification
- Maintains execution sequence integrity
- Records non-deterministic events as warnings

PHASE 14 REQUIREMENT: "Deterministic"
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from core.contracts.events import ExecutionEvent, SignalEvent
from state.ledger.event_store import append_event


class DeterminismViolationType(StrEnum):
    """Types of determinism violations."""

    TIMESTAMP_OUT_OF_ORDER = "TIMESTAMP_OUT_OF_ORDER"
    DUPLICATE_SIGNAL = "DUPLICATE_SIGNAL"
    DUPLICATE_EXECUTION = "DUPLICATE_EXECUTION"
    NON_DETERMINISTIC_SOURCE = "NON_DETERMINISTIC_SOURCE"
    SEQUENCE_GAP = "SEQUENCE_GAP"
    CLOCK_DRIFT = "CLOCK_DRIFT"


@dataclass
class DeterminismCheckResult:
    """Result of a determinism check."""

    passed: bool
    violation_type: DeterminismViolationType | None = None
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeterministicExecutionRecord:
    """Record of a deterministic execution."""

    sequence: int
    timestamp_ns: int
    signal_id: str
    execution_id: str
    venue: str
    symbol: str
    side: str
    qty: float
    price: float
    status: str
    payload: dict[str, Any] = field(default_factory=dict)


class DeterministicLiveTradingExecutor:
    """Deterministic executor for live trading.

    This class ensures that live trading execution is deterministic and
    reproducible as required by Phase 14. It maintains strict ordering
    and sequence integrity.

    Thread-safe singleton pattern.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sequence: int = 0
        self._last_timestamp_ns: int = 0
        self._execution_log: list[DeterministicExecutionRecord] = []
        self._signal_ids_seen: set[str] = set()
        self._execution_ids_seen: set[str] = set()
        self._listeners: list[Callable[[DeterminismCheckResult], None]] = []
        self._enabled: bool = True
        self._violation_count: int = 0

    def enable(self) -> None:
        """Enable determinism enforcement."""
        with self._lock:
            self._enabled = True

    def disable(self) -> None:
        """Disable determinism enforcement (DANGEROUS)."""
        with self._lock:
            self._enabled = False

    def execute_trade(
        self,
        signal: SignalEvent,
        execution_func: Callable[[], ExecutionEvent],
    ) -> tuple[bool, ExecutionEvent, DeterminismCheckResult]:
        """Execute a trade with determinism guarantees.

        Args:
            signal: The signal event
            execution_func: Function to execute the trade

        Returns:
            (success, execution_event, determinism_result) tuple
        """
        with self._lock:
            if not self._enabled:
                # Determinism disabled - execute without checks
                execution = execution_func()
                return True, execution, DeterminismCheckResult(passed=True)

            # Check determinism before execution
            determinism_check = self._check_execution_determinism(signal)
            if not determinism_check.passed:
                # Determinism violation - record and reject
                self._record_violation(determinism_check)
                return False, self._create_rejected_execution(signal, determinism_check), determinism_check

            # Execute the trade
            try:
                execution = execution_func()
            except Exception as e:
                # Execution failed - record as determinism issue
                determinism_check = DeterminismCheckResult(
                    passed=False,
                    violation_type=DeterminismViolationType.NON_DETERMINISTIC_SOURCE,
                    reason=f"Execution function raised exception: {e}",
                )
                self._record_violation(determinism_check)
                return False, self._create_rejected_execution(signal, determinism_check), determinism_check

            # Check post-execution determinism
            post_check = self._check_execution_result_determinism(signal, execution)
            if not post_check.passed:
                self._record_violation(post_check)
                return False, execution, post_check

            # Record successful execution
            self._record_execution(signal, execution)

            return True, execution, post_check

    def _check_execution_determinism(self, signal: SignalEvent) -> DeterminismCheckResult:
        """Check determinism before execution."""
        # Check timestamp ordering
        if signal.ts_ns < self._last_timestamp_ns:
            return DeterminismCheckResult(
                passed=False,
                violation_type=DeterminismViolationType.TIMESTAMP_OUT_OF_ORDER,
                reason=f"Signal timestamp {signal.ts_ns} < last timestamp {self._last_timestamp_ns}",
                metadata={
                    "signal_ts_ns": signal.ts_ns,
                    "last_ts_ns": self._last_timestamp_ns,
                },
            )

        # Check for duplicate signals
        signal_id = str(signal.event_id) if hasattr(signal, "event_id") else ""
        if signal_id in self._signal_ids_seen:
            return DeterminismCheckResult(
                passed=False,
                violation_type=DeterminismViolationType.DUPLICATE_SIGNAL,
                reason=f"Duplicate signal ID: {signal_id}",
                metadata={"signal_id": signal_id},
            )

        return DeterminismCheckResult(passed=True)

    def _check_execution_result_determinism(
        self, signal: SignalEvent, execution: ExecutionEvent
    ) -> DeterminismCheckResult:
        """Check determinism after execution."""
        # Check for duplicate executions
        execution_id = str(execution.event_id) if hasattr(execution, "event_id") else ""
        if execution_id in self._execution_ids_seen:
            return DeterminismCheckResult(
                passed=False,
                violation_type=DeterminismViolationType.DUPLICATE_EXECUTION,
                reason=f"Duplicate execution ID: {execution_id}",
                metadata={"execution_id": execution_id},
            )

        # Check timestamp ordering
        if execution.ts_ns < self._last_timestamp_ns:
            return DeterminismCheckResult(
                passed=False,
                violation_type=DeterminismViolationType.TIMESTAMP_OUT_OF_ORDER,
                reason=f"Execution timestamp {execution.ts_ns} < last timestamp {self._last_timestamp_ns}",
                metadata={
                    "execution_ts_ns": execution.ts_ns,
                    "last_ts_ns": self._last_timestamp_ns,
                },
            )

        return DeterminismCheckResult(passed=True)

    def _record_execution(self, signal: SignalEvent, execution: ExecutionEvent) -> None:
        """Record a deterministic execution."""
        self._sequence += 1
        self._last_timestamp_ns = execution.ts_ns

        signal_id = str(signal.event_id) if hasattr(signal, "event_id") else ""
        execution_id = str(execution.event_id) if hasattr(execution, "event_id") else ""

        self._signal_ids_seen.add(signal_id)
        self._execution_ids_seen.add(execution_id)

        record = DeterministicExecutionRecord(
            sequence=self._sequence,
            timestamp_ns=execution.ts_ns,
            signal_id=signal_id,
            execution_id=execution_id,
            venue=execution.venue,
            symbol=execution.symbol,
            side=execution.side.value if hasattr(execution.side, "value") else str(execution.side),
            qty=execution.qty,
            price=execution.price,
            status=execution.status.value if hasattr(execution.status, "value") else str(execution.status),
        )
        self._execution_log.append(record)

    def _create_rejected_execution(
        self, signal: SignalEvent, determinism_check: DeterminismCheckResult
    ) -> ExecutionEvent:
        """Create a rejected execution event."""
        from core.contracts.events import ExecutionStatus

        return ExecutionEvent(
            ts_ns=signal.ts_ns,
            symbol=signal.symbol,
            side=signal.side,
            qty=0.0,
            price=0.0,
            status=ExecutionStatus.REJECTED,
            venue="determinism_enforcer",
            order_id="",
            meta={
                "reason": determinism_check.reason,
                "violation_type": determinism_check.violation_type.value if determinism_check.violation_type else "UNKNOWN",
                "metadata": determinism_check.metadata,
            },
            produced_by_engine="determinism_enforcer",
        )

    def _record_violation(self, result: DeterminismCheckResult) -> None:
        """Record a determinism violation."""
        self._violation_count += 1

        # Notify listeners
        for listener in self._listeners:
            try:
                listener(result)
            except Exception:
                pass

        # Record to ledger
        append_event(
            event_type="GOVERNANCE",
            sub_type="DETERMINISM_VIOLATION",
            source="DETERMINISTIC_EXECUTOR",
            payload={
                "violation_type": result.violation_type.value if result.violation_type else "UNKNOWN",
                "reason": result.reason,
                "metadata": result.metadata,
            },
        )

    def verify_determinism(self) -> bool:
        """Verify that the execution log is deterministic."""
        with self._lock:
            if len(self._execution_log) == 0:
                return True

            # Check sequence continuity
            expected_sequence = 1
            for record in self._execution_log:
                if record.sequence != expected_sequence:
                    return False
                expected_sequence += 1

            # Check timestamp ordering
            prev_ts = self._execution_log[0].timestamp_ns
            for record in self._execution_log[1:]:
                if record.timestamp_ns < prev_ts:
                    return False
                prev_ts = record.timestamp_ns

            return True

    def get_execution_log(self, limit: int = 100) -> list[DeterministicExecutionRecord]:
        """Get the execution log."""
        with self._lock:
            return self._execution_log[-limit:] if limit > 0 else self._execution_log.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get determinism statistics."""
        with self._lock:
            return {
                "enabled": self._enabled,
                "sequence": self._sequence,
                "last_timestamp_ns": self._last_timestamp_ns,
                "total_executions": len(self._execution_log),
                "unique_signals": len(self._signal_ids_seen),
                "unique_executions": len(self._execution_ids_seen),
                "violation_count": self._violation_count,
                "determinism_verified": self.verify_determinism(),
            }

    def add_listener(self, listener: Callable[[DeterminismCheckResult], None]) -> None:
        """Add a listener for determinism violations."""
        with self._lock:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[DeterminismCheckResult], None]) -> None:
        """Remove a listener for determinism violations."""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def reset_sequence(self) -> None:
        """Reset the sequence (for testing only)."""
        with self._lock:
            self._sequence = 0
            self._last_timestamp_ns = 0
            self._signal_ids_seen.clear()
            self._execution_ids_seen.clear()
            self._execution_log.clear()


# Singleton instance
_deterministic_executor: DeterministicLiveTradingExecutor | None = None
_deterministic_executor_lock = threading.Lock()


def get_deterministic_live_trading_executor() -> DeterministicLiveTradingExecutor:
    """Get the singleton deterministic live trading executor."""
    global _deterministic_executor
    with _deterministic_executor_lock:
        if _deterministic_executor is None:
            _deterministic_executor = DeterministicLiveTradingExecutor()
    return _deterministic_executor


__all__ = [
    "DeterminismCheckResult",
    "DeterminismViolationType",
    "DeterministicExecutionRecord",
    "DeterministicLiveTradingExecutor",
    "get_deterministic_live_trading_executor",
]
