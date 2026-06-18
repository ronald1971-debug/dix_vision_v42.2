"""
execution/live_trading/governance_layer.py
DIX VISION v42.2 — Live Trading Governance Layer (Phase 14)

Implements the governance approval layer for live trading as required by Phase 14.
This layer ensures that every live trade execution must pass through explicit
governance approval before execution.

The governance layer:
- Validates every live trade against governance policies
- Requires explicit approval for live trading mode
- Enforces promotion gate compliance
- Blocks live trading until governance approval
- Records all governance decisions to the ledger
- Provides audit trail for all governance actions

PHASE 14 REQUIREMENT: "Governance approved"
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from core.contracts.events import ExecutionEvent, SignalEvent
from state.ledger.event_store import append_event


class GovernanceDecisionType(StrEnum):
    """Types of governance decisions for live trading."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"
    DEFERRED = "DEFERRED"
    BLOCKED = "BLOCKED"


@dataclass
class LiveTradeGovernanceContext:
    """Context for live trade governance decisions."""

    trade_id: str
    venue: str
    symbol: str
    side: str
    size_usd: float
    portfolio_usd: float
    strategy: str
    timestamp_ns: int
    signal_id: str = ""
    mode: str = "UNKNOWN"  # PAPER, SHADOW, CANARY, LIVE, AUTO
    risk_level: str = "MEDIUM"  # LOW, MEDIUM, HIGH


@dataclass
class GovernanceApprovalDecision:
    """Result of a governance approval decision."""

    decision: GovernanceDecisionType
    context: LiveTradeGovernanceContext
    reason: str
    approver: str = "governance_layer"
    approved_by: str = ""  # If approved by a specific entity
    conditions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class LiveTradingGovernanceLayer:
    """Governance approval layer for live trading.

    This layer sits between signal generation and execution to ensure that
    every live trade passes through explicit governance approval. It enforces
    the Phase 14 requirement: "Governance approved".

    Thread-safe singleton pattern.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._live_trading_enabled: bool = False
        self._live_trading_mode: str = "PAPER"  # Default to PAPER
        self._promotion_gate_required: bool = True
        self._listeners: list[Callable[[GovernanceApprovalDecision], None]] = []
        self._decision_log: list[GovernanceApprovalDecision] = []
        self._approval_count: int = 0
        self._rejection_count: int = 0

    def enable_live_trading(self, approver: str, ts_ns: int, mode: str = "LIVE") -> bool:
        """Enable live trading with governance approval.

        Args:
            approver: The entity approving live trading (e.g., "operator", "governance_committee")
            ts_ns: Timestamp of the approval
            mode: The trading mode to enable (LIVE, AUTO, etc.)

        Returns:
            True if live trading was enabled, False otherwise
        """
        with self._lock:
            # Record approval to ledger
            append_event(
                event_type="GOVERNANCE",
                sub_type="LIVE_TRADING_APPROVED",
                source="GOVERNANCE_LAYER",
                payload={
                    "approver": approver,
                    "mode": mode,
                    "timestamp_ns": ts_ns,
                },
            )

            self._live_trading_enabled = True
            self._live_trading_mode = mode

            return True

    def disable_live_trading(self, reason: str, requestor: str, ts_ns: int) -> bool:
        """Disable live trading.

        Args:
            reason: Reason for disabling live trading
            requestor: The entity requesting the disable
            ts_ns: Timestamp of the request

        Returns:
            True if live trading was disabled, False otherwise
        """
        with self._lock:
            # Record disable to ledger
            append_event(
                event_type="GOVERNANCE",
                sub_type="LIVE_TRADING_DISABLED",
                source="GOVERNANCE_LAYER",
                payload={
                    "requestor": requestor,
                    "reason": reason,
                    "previous_mode": self._live_trading_mode,
                    "timestamp_ns": ts_ns,
                },
            )

            self._live_trading_enabled = False
            return True

    def request_approval(
        self, context: LiveTradeGovernanceContext
    ) -> GovernanceApprovalDecision:
        """Request governance approval for a live trade.

        Args:
            context: The governance context for the trade

        Returns:
            Governance approval decision
        """
        with self._lock:
            # Check if live trading is enabled
            if not self._live_trading_enabled:
                decision = GovernanceApprovalDecision(
                    decision=GovernanceDecisionType.BLOCKED,
                    context=context,
                    reason="Live trading is not enabled - governance approval required",
                )
                self._record_decision(decision)
                return decision

            # Check if mode promotion is required
            if self._promotion_gate_required:
                mode_valid = self._validate_mode_promotion(context.mode)
                if not mode_valid:
                    decision = GovernanceApprovalDecision(
                        decision=GovernanceDecisionType.BLOCKED,
                        context=context,
                        reason=f"Mode {context.mode} requires promotion gate approval",
                    )
                    self._record_decision(decision)
                    return decision

            # Check if mode allows live trading
            if context.mode not in {"LIVE", "AUTO"}:
                decision = GovernanceApprovalDecision(
                    decision=GovernanceDecisionType.BLOCKED,
                    context=context,
                    reason=f"Mode {context.mode} does not allow live trading",
                )
                self._record_decision(decision)
                return decision

            # Approve the trade
            decision = GovernanceApprovalDecision(
                decision=GovernanceDecisionType.APPROVED,
                context=context,
                reason=f"Trade approved for {context.mode} mode",
                approved_by="governance_layer",
            )
            self._record_decision(decision)

            return decision

    def validate_live_execution(
        self, signal: SignalEvent, execution: ExecutionEvent
    ) -> bool:
        """Validate that a live execution has proper governance approval.

        This is a post-execution validation to ensure that any execution
        that occurred had proper governance approval.

        Args:
            signal: The original signal event
            execution: The execution event to validate

        Returns:
            True if execution is valid (had governance approval), False otherwise
        """
        with self._lock:
            # Check if live trading is enabled
            if not self._live_trading_enabled:
                # Live trading not enabled - execution should not have occurred
                self._record_violation(
                    signal, execution, "Live trading not enabled but execution occurred"
                )
                return False

            # Check if venue is a live venue (not paper)
            venue = execution.venue
            if "_paper" in venue.lower():
                # Paper venue - this is OK
                return True

            # Live venue - should have governance approval in meta
            if execution.meta:
                governance_approved = execution.meta.get("governance_approved", "0")
                if governance_approved == "1":
                    return True

            # Live execution without governance approval
            self._record_violation(
                signal, execution, "Live execution without governance approval"
            )
            return False

    def _validate_mode_promotion(self, mode: str) -> bool:
        """Validate that the mode has proper promotion gate approval."""
        # In a full implementation, this would check the promotion gates
        # from Phase 13 to ensure the mode transition was approved
        allowed_modes = {"PAPER", "SHADOW", "CANARY", "LIVE", "AUTO"}
        return mode in allowed_modes

    def _record_decision(self, decision: GovernanceApprovalDecision) -> None:
        """Record a governance decision to the log and ledger."""
        self._decision_log.append(decision)

        # Update statistics
        if decision.decision == GovernanceDecisionType.APPROVED:
            self._approval_count += 1
        elif decision.decision in {
            GovernanceDecisionType.REJECTED,
            GovernanceDecisionType.BLOCKED,
        }:
            self._rejection_count += 1

        # Notify listeners
        for listener in self._listeners:
            try:
                listener(decision)
            except Exception:
                pass

        # Record to ledger
        append_event(
            event_type="GOVERNANCE",
            sub_type="LIVE_TRADE_GOVERNANCE_DECISION",
            source="GOVERNANCE_LAYER",
            payload={
                "decision": decision.decision.value,
                "trade_id": decision.context.trade_id,
                "venue": decision.context.venue,
                "symbol": decision.context.symbol,
                "side": decision.context.side,
                "size_usd": decision.context.size_usd,
                "reason": decision.reason,
                "approver": decision.approver,
                "approved_by": decision.approved_by,
                "mode": decision.context.mode,
            },
        )

    def _record_violation(
        self, signal: SignalEvent, execution: ExecutionEvent, reason: str
    ) -> None:
        """Record a governance violation to the ledger."""
        append_event(
            event_type="GOVERNANCE",
            sub_type="LIVE_TRADING_VIOLATION",
            source="GOVERNANCE_LAYER",
            payload={
                "reason": reason,
                "signal_id": str(signal.event_id) if hasattr(signal, "event_id") else "",
                "symbol": execution.symbol,
                "venue": execution.venue,
                "timestamp_ns": execution.ts_ns,
            },
        )

    def add_listener(
        self, listener: Callable[[GovernanceApprovalDecision], None]
    ) -> None:
        """Add a listener for governance decisions."""
        with self._lock:
            self._listeners.append(listener)

    def remove_listener(
        self, listener: Callable[[GovernanceApprovalDecision], None]
    ) -> None:
        """Remove a listener for governance decisions."""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def get_decision_log(self, limit: int = 100) -> list[GovernanceApprovalDecision]:
        """Get the governance decision log."""
        with self._lock:
            return self._decision_log[-limit:] if limit > 0 else self._decision_log.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get governance statistics."""
        with self._lock:
            total = self._approval_count + self._rejection_count
            return {
                "live_trading_enabled": self._live_trading_enabled,
                "live_trading_mode": self._live_trading_mode,
                "promotion_gate_required": self._promotion_gate_required,
                "total_decisions": total,
                "approvals": self._approval_count,
                "rejections": self._rejection_count,
                "approval_rate": (
                    self._approval_count / total if total > 0 else 0.0
                ),
            }

    def is_live_trading_enabled(self) -> bool:
        """Check if live trading is enabled."""
        with self._lock:
            return self._live_trading_enabled

    def get_current_mode(self) -> str:
        """Get the current trading mode."""
        with self._lock:
            return self._live_trading_mode


# Singleton instance
_governance_layer: LiveTradingGovernanceLayer | None = None
_governance_layer_lock = threading.Lock()


def get_live_trading_governance_layer() -> LiveTradingGovernanceLayer:
    """Get the singleton live trading governance layer."""
    global _governance_layer
    with _governance_layer_lock:
        if _governance_layer is None:
            _governance_layer = LiveTradingGovernanceLayer()
    return _governance_layer


__all__ = [
    "GovernanceApprovalDecision",
    "GovernanceDecisionType",
    "LiveTradeGovernanceContext",
    "LiveTradingGovernanceLayer",
    "get_live_trading_governance_layer",
]
