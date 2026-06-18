"""
execution/live_trading/audit_system.py
DIX VISION v42.2 — Live Trading Audit System (Phase 14)

Implements full auditability for live trading as required by Phase 14.
This provides comprehensive audit trails for all live trading activities.

The audit system:
- Records every governance decision
- Tracks every risk constraint check
- Logs every ledger-backed operation
- Monitors determinism violations
- Provides complete decision traceability
- Generates audit reports for compliance

PHASE 14 REQUIREMENT: "Auditable"
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from execution_unified.live_trading.deterministic_executor import (
    DeterminismCheckResult,
)
from execution_unified.live_trading.governance_layer import (
    GovernanceApprovalDecision,
    GovernanceDecisionType,
)
from execution_unified.live_trading.ledger_backed_operations import (
    LiveOperationRecord,
)
from execution_unified.live_trading.risk_constraints import (
    RiskCheckResult,
)


class AuditEventType(StrEnum):
    """Types of audit events."""

    GOVERNANCE_DECISION = "GOVERNANCE_DECISION"
    RISK_CONSTRAINT_CHECK = "RISK_CONSTRAINT_CHECK"
    LEDGER_OPERATION = "LEDGER_OPERATION"
    DETERMINISM_CHECK = "DETERMINISM_CHECK"
    TRADE_EXECUTION = "TRADE_EXECUTION"
    POSITION_UPDATE = "POSITION_UPDATE"
    BALANCE_UPDATE = "BALANCE_UPDATE"
    SYSTEM_EVENT = "SYSTEM_EVENT"


@dataclass
class AuditEvent:
    """An audit event."""

    event_id: str
    event_type: AuditEventType
    timestamp_ns: int
    timestamp_utc: str
    source: str
    payload: dict[str, Any]
    severity: str = "INFO"  # INFO, WARNING, ERROR, CRITICAL


@dataclass
class AuditTrail:
    """Complete audit trail for a trade or operation."""

    trail_id: str
    start_timestamp_ns: int
    end_timestamp_ns: int
    events: list[AuditEvent] = field(default_factory=list)
    final_outcome: str = ""


@dataclass
class AuditReport:
    """Comprehensive audit report."""

    report_id: str
    generated_at_ns: int
    generated_at_utc: str
    period_start_ns: int
    period_end_ns: int
    total_events: int = 0
    event_counts: dict[str, int] = field(default_factory=dict)
    governance_decisions: dict[str, int] = field(default_factory=dict)
    risk_violations: int = 0
    determinism_violations: int = 0
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    summary: str = ""


class LiveTradingAuditSystem:
    """Comprehensive audit system for live trading.

    This class provides full auditability for all live trading activities
    as required by Phase 14. It integrates with all Phase 14 components
    to provide complete decision traceability.

    Thread-safe singleton pattern.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._audit_log: list[AuditEvent] = []
        self._trails: dict[str, AuditTrail] = {}
        self._listeners: list[Callable[[AuditEvent], None]] = []
        self._event_counter: int = 0
        self._enabled: bool = True

    def enable(self) -> None:
        """Enable the audit system."""
        with self._lock:
            self._enabled = True

    def disable(self) -> None:
        """Disable the audit system (DANGEROUS)."""
        with self._lock:
            self._enabled = False

    def record_governance_decision(
        self, decision: GovernanceApprovalDecision
    ) -> str:
        """Record a governance decision to the audit log."""
        with self._lock:
            if not self._enabled:
                return ""

            self._event_counter += 1
            event_id = f"audit_{self._event_counter}"

            event = AuditEvent(
                event_id=event_id,
                event_type=AuditEventType.GOVERNANCE_DECISION,
                timestamp_ns=self._get_timestamp_ns(),
                timestamp_utc=self._get_timestamp_utc(),
                source="GOVERNANCE_LAYER",
                payload={
                    "decision": decision.decision.value,
                    "trade_id": decision.context.trade_id,
                    "venue": decision.context.venue,
                    "symbol": decision.context.symbol,
                    "reason": decision.reason,
                    "approver": decision.approver,
                    "approved_by": decision.approved_by,
                    "mode": decision.context.mode,
                },
                severity="INFO" if decision.decision == GovernanceDecisionType.APPROVED else "WARNING",
            )

            self._add_to_log(event)
            return event_id

    def record_risk_check(self, result: RiskCheckResult) -> str:
        """Record a risk constraint check to the audit log."""
        with self._lock:
            if not self._enabled:
                return ""

            self._event_counter += 1
            event_id = f"audit_{self._event_counter}"

            event = AuditEvent(
                event_id=event_id,
                event_type=AuditEventType.RISK_CONSTRAINT_CHECK,
                timestamp_ns=self._get_timestamp_ns(),
                timestamp_utc=self._get_timestamp_utc(),
                source="RISK_CONSTRAINTS",
                payload={
                    "constraint_type": result.constraint_type.value,
                    "passed": result.passed,
                    "constraint_value": result.constraint_value,
                    "actual_value": result.actual_value,
                    "reason": result.reason,
                    "metadata": result.metadata,
                },
                severity="ERROR" if not result.passed else "INFO",
            )

            self._add_to_log(event)
            return event_id

    def record_ledger_operation(self, record: LiveOperationRecord) -> str:
        """Record a ledger operation to the audit log."""
        with self._lock:
            if not self._enabled:
                return ""

            self._event_counter += 1
            event_id = f"audit_{self._event_counter}"

            event = AuditEvent(
                event_id=event_id,
                event_type=AuditEventType.LEDGER_OPERATION,
                timestamp_ns=record.timestamp_ns,
                timestamp_utc=self._timestamp_ns_to_utc(record.timestamp_ns),
                source="LEDGER_BACKED_OPERATIONS",
                payload={
                    "operation_id": record.operation_id,
                    "operation_type": record.operation_type.value,
                    "venue": record.venue,
                    "symbol": record.symbol,
                    "payload": record.payload,
                    "operation_hash": record.operation_hash,
                },
                severity="INFO",
            )

            self._add_to_log(event)
            return event_id

    def record_determinism_check(self, result: DeterminismCheckResult) -> str:
        """Record a determinism check to the audit log."""
        with self._lock:
            if not self._enabled:
                return ""

            self._event_counter += 1
            event_id = f"audit_{self._event_counter}"

            event = AuditEvent(
                event_id=event_id,
                event_type=AuditEventType.DETERMINISM_CHECK,
                timestamp_ns=self._get_timestamp_ns(),
                timestamp_utc=self._get_timestamp_utc(),
                source="DETERMINISTIC_EXECUTOR",
                payload={
                    "passed": result.passed,
                    "violation_type": result.violation_type.value if result.violation_type else None,
                    "reason": result.reason,
                    "metadata": result.metadata,
                },
                severity="ERROR" if not result.passed else "INFO",
            )

            self._add_to_log(event)
            return event_id

    def record_trade_execution(
        self,
        trade_id: str,
        venue: str,
        symbol: str,
        side: str,
        qty: float,
        price: float,
        status: str,
        timestamp_ns: int,
        governance_approved: bool,
        risk_constraints_passed: bool,
    ) -> str:
        """Record a trade execution to the audit log."""
        with self._lock:
            if not self._enabled:
                return ""

            self._event_counter += 1
            event_id = f"audit_{self._event_counter}"

            event = AuditEvent(
                event_id=event_id,
                event_type=AuditEventType.TRADE_EXECUTION,
                timestamp_ns=timestamp_ns,
                timestamp_utc=self._timestamp_ns_to_utc(timestamp_ns),
                source="TRADE_EXECUTOR",
                payload={
                    "trade_id": trade_id,
                    "venue": venue,
                    "symbol": symbol,
                    "side": side,
                    "qty": qty,
                    "price": price,
                    "status": status,
                    "governance_approved": governance_approved,
                    "risk_constraints_passed": risk_constraints_passed,
                },
                severity="ERROR" if status == "REJECTED" else "INFO",
            )

            self._add_to_log(event)
            return event_id

    def create_audit_trail(
        self, trail_id: str, start_timestamp_ns: int
    ) -> AuditTrail:
        """Create a new audit trail."""
        with self._lock:
            trail = AuditTrail(
                trail_id=trail_id,
                start_timestamp_ns=start_timestamp_ns,
                end_timestamp_ns=start_timestamp_ns,
            )
            self._trails[trail_id] = trail
            return trail

    def add_event_to_trail(self, trail_id: str, event: AuditEvent) -> bool:
        """Add an event to an existing audit trail."""
        with self._lock:
            trail = self._trails.get(trail_id)
            if trail:
                trail.events.append(event)
                trail.end_timestamp_ns = event.timestamp_ns
                return True
            return False

    def generate_audit_report(
        self, period_start_ns: int, period_end_ns: int
    ) -> AuditReport:
        """Generate a comprehensive audit report for a time period."""
        with self._lock:
            report = AuditReport(
                report_id=f"audit_report_{self._event_counter}",
                generated_at_ns=self._get_timestamp_ns(),
                generated_at_utc=self._get_timestamp_utc(),
                period_start_ns=period_start_ns,
                period_end_ns=period_end_ns,
            )

            # Filter events within the period
            period_events = [
                e
                for e in self._audit_log
                if period_start_ns <= e.timestamp_ns <= period_end_ns
            ]
            report.total_events = len(period_events)

            # Count events by type
            for event in period_events:
                report.event_counts[event.event_type.value] = (
                    report.event_counts.get(event.event_type.value, 0) + 1
                )

                # Count governance decisions
                if event.event_type == AuditEventType.GOVERNANCE_DECISION:
                    decision = event.payload.get("decision", "")
                    report.governance_decisions[decision] = (
                        report.governance_decisions.get(decision, 0) + 1
                    )

                # Count risk violations
                if event.event_type == AuditEventType.RISK_CONSTRAINT_CHECK:
                    if not event.payload.get("passed", True):
                        report.risk_violations += 1

                # Count determinism violations
                if event.event_type == AuditEventType.DETERMINISM_CHECK:
                    if not event.payload.get("passed", True):
                        report.determinism_violations += 1

                # Count trades
                if event.event_type == AuditEventType.TRADE_EXECUTION:
                    report.total_trades += 1
                    if event.payload.get("status") == "FILLED":
                        report.successful_trades += 1
                    else:
                        report.failed_trades += 1

            # Generate summary
            report.summary = self._generate_summary(report)

            return report

    def _generate_summary(self, report: AuditReport) -> str:
        """Generate a human-readable summary of the audit report."""
        summary_parts = [
            f"Audit Report: {report.report_id}",
            f"Period: {report.period_start_ns} to {report.period_end_ns}",
            f"Total Events: {report.total_events}",
            f"Total Trades: {report.total_trades}",
            f"Successful Trades: {report.successful_trades}",
            f"Failed Trades: {report.failed_trades}",
            f"Risk Violations: {report.risk_violations}",
            f"Determinism Violations: {report.determinism_violations}",
        ]

        # Add governance decision summary
        if report.governance_decisions:
            gov_summary = " | ".join(
                f"{k}: {v}" for k, v in report.governance_decisions.items()
            )
            summary_parts.append(f"Governance Decisions: {gov_summary}")

        return " | ".join(summary_parts)

    def _add_to_log(self, event: AuditEvent) -> None:
        """Add an event to the audit log."""
        self._audit_log.append(event)

        # Notify listeners
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass

    def get_audit_log(self, limit: int = 100) -> list[AuditEvent]:
        """Get the audit log."""
        with self._lock:
            return self._audit_log[-limit:] if limit > 0 else self._audit_log.copy()

    def get_audit_trail(self, trail_id: str) -> AuditTrail | None:
        """Get an audit trail by ID."""
        with self._lock:
            return self._trails.get(trail_id)

    def add_listener(self, listener: Callable[[AuditEvent], None]) -> None:
        """Add a listener for audit events."""
        with self._lock:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[AuditEvent], None]) -> None:
        """Remove a listener for audit events."""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def is_enabled(self) -> bool:
        """Check if the audit system is enabled."""
        with self._lock:
            return self._enabled

    def _get_timestamp_ns(self) -> int:
        """Get current timestamp in nanoseconds."""
        import time

        return int(time.time() * 1_000_000_000)

    def _get_timestamp_utc(self) -> str:
        """Get current timestamp in UTC."""
        return datetime.now(UTC).isoformat()

    def _timestamp_ns_to_utc(self, ts_ns: int) -> str:
        """Convert nanosecond timestamp to UTC string."""
        return datetime.fromtimestamp(ts_ns / 1_000_000_000, tz=UTC).isoformat()


# Singleton instance
_audit_system: LiveTradingAuditSystem | None = None
_audit_system_lock = threading.Lock()


def get_live_trading_audit_system() -> LiveTradingAuditSystem:
    """Get the singleton live trading audit system."""
    global _audit_system
    with _audit_system_lock:
        if _audit_system is None:
            _audit_system = LiveTradingAuditSystem()
    return _audit_system


__all__ = [
    "AuditEvent",
    "AuditReport",
    "AuditTrail",
    "AuditEventType",
    "LiveTradingAuditSystem",
    "get_live_trading_audit_system",
]
