"""
execution_engine/paper_trading/paper_only_enforcer.py
DIX VISION v42.2 — Paper-Only Environment Enforcer (Phase 13)

Ensures 100% paper environment by blocking any live trading attempts.
This is a critical safety mechanism that enforces the Phase 13 exit criteria:
"100% paper environment."

The enforcer:
- Blocks any execution attempts with live venue adapters
- Validates that all trades use paper adapters only
- Raises alerts if live trading is attempted
- Records enforcement actions to the ledger
- Provides a hard safety guarantee that no real capital is at risk

INV-56 Triad Lock: Paper fills are tagged paper=1 and never disguised as live.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from core.contracts.events import ExecutionEvent, SignalEvent
from state.ledger.event_store import append_event


class EnforcementAction(StrEnum):
    """Types of enforcement actions taken."""

    BLOCKED_LIVE_TRADE = "BLOCKED_LIVE_TRADE"
    ALLOWED_PAPER_TRADE = "ALLOWED_PAPER_TRADE"
    ALERT_LIVE_ATTEMPT = "ALERT_LIVE_ATTEMPT"
    ENFORCEMENT_ENABLED = "ENFORCEMENT_ENABLED"
    ENFORCEMENT_DISABLED = "ENFORCEMENT_DISABLED"  # Only for testing


@dataclass
class EnforcementEvent:
    """Record of an enforcement action."""

    action: EnforcementAction
    venue: str
    symbol: str
    timestamp_ns: int
    reason: str
    attempted_signal_id: str = ""
    blocked: bool = False


@dataclass
class EnforcementConfig:
    """Configuration for the paper-only enforcer."""

    enabled: bool = True  # Master switch for enforcement
    block_live_trades: bool = True  # Block trades to live venues
    alert_on_live_attempt: bool = True  # Alert when live trading is attempted
    allowed_paper_venues: set[str] = field(
        default_factory=lambda: {
            "binance_paper",
            "coinbase_paper",
            "kraken_paper",
            "alpaca_paper",
            "oanda_paper",
            "ibkr_paper",
        }
    )
    blocked_live_venues: set[str] = field(
        default_factory=lambda: {
            "binance",
            "coinbase",
            "kraken",
            "alpaca",
            "oanda",
            "ibkr",
            "binance_live",
            "coinbase_live",
            "kraken_live",
            "alpaca_live",
            "oanda_live",
            "ibkr_live",
        }
    )
    enforcement_override_allowed: bool = False  # Allow operator override (dangerous)


class PaperOnlyEnforcer:
    """Enforces 100% paper trading environment.

    This class provides a hard safety guarantee that no live trading can
    occur while the enforcer is enabled. All attempts to trade with live
    venue adapters are blocked and recorded to the ledger.

    Thread-safe singleton pattern.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._config = EnforcementConfig()
        self._enforcement_log: list[EnforcementEvent] = []
        self._listeners: list[Callable[[EnforcementEvent], None]] = []
        self._enforcement_count: int = 0
        self._blocked_count: int = 0

    def configure(self, config: EnforcementConfig) -> None:
        """Update the enforcement configuration."""
        with self._lock:
            old_enabled = self._config.enabled
            self._config = config

            # Record configuration change to ledger
            action = (
                EnforcementAction.ENFORCEMENT_ENABLED
                if config.enabled
                else EnforcementAction.ENFORCEMENT_DISABLED
            )
            self._record_enforcement(
                EnforcementEvent(
                    action=action,
                    venue="system",
                    symbol="N/A",
                    timestamp_ns=self._get_timestamp_ns(),
                    reason=f"Configuration changed: enabled={config.enabled}",
                )
            )

    def check_trade_allowed(
        self, signal: SignalEvent, venue: str
    ) -> tuple[bool, str, EnforcementAction]:
        """Check if a trade is allowed under the paper-only policy.

        Args:
            signal: The signal event for the trade
            venue: The venue identifier

        Returns:
            (allowed, reason, action) tuple:
            - allowed: True if trade is allowed, False if blocked
            - reason: Human-readable reason for the decision
            - action: The enforcement action taken
        """
        with self._lock:
            self._enforcement_count += 1

            # Check if enforcement is enabled
            if not self._config.enabled:
                return (
                    True,
                    "Enforcement disabled - trade allowed (WARNING: not paper-only)",
                    EnforcementAction.ALLOWED_PAPER_TRADE,
                )

            # Check if venue is a paper venue
            if venue in self._config.allowed_paper_venues:
                # Paper venue - allow
                return (
                    True,
                    f"Paper venue allowed: {venue}",
                    EnforcementAction.ALLOWED_PAPER_TRADE,
                )

            # Check if venue is a blocked live venue
            if venue in self._config.blocked_live_venues:
                # Live venue - block
                self._blocked_count += 1

                # Record enforcement event
                enforcement_event = EnforcementEvent(
                    action=EnforcementAction.BLOCKED_LIVE_TRADE,
                    venue=venue,
                    symbol=signal.symbol,
                    timestamp_ns=self._get_timestamp_ns(),
                    reason=f"Live venue blocked: {venue}",
                    attempted_signal_id=str(signal.event_id) if hasattr(signal, "event_id") else "",
                    blocked=True,
                )
                self._record_enforcement(enforcement_event)

                # Alert if configured
                if self._config.alert_on_live_attempt:
                    self._alert_live_attempt(enforcement_event)

                return (
                    False,
                    f"Live venue blocked: {venue} (paper-only mode)",
                    EnforcementAction.BLOCKED_LIVE_TRADE,
                )

            # Unknown venue - block for safety
            self._blocked_count += 1
            enforcement_event = EnforcementEvent(
                action=EnforcementAction.BLOCKED_LIVE_TRADE,
                venue=venue,
                symbol=signal.symbol,
                timestamp_ns=self._get_timestamp_ns(),
                reason=f"Unknown venue blocked: {venue} (paper-only safety)",
                attempted_signal_id=str(signal.event_id) if hasattr(signal, "event_id") else "",
                blocked=True,
            )
            self._record_enforcement(enforcement_event)

            return (
                False,
                f"Unknown venue blocked: {venue} (paper-only safety)",
                EnforcementAction.BLOCKED_LIVE_TRADE,
            )

    def validate_execution(self, signal: SignalEvent, execution: ExecutionEvent) -> bool:
        """Validate that an execution is from a paper venue.

        This is a post-execution validation to ensure that any execution
        that made it through has the proper paper tagging (INV-56).

        Args:
            signal: The original signal event
            execution: The execution event to validate

        Returns:
            True if execution is valid (from paper venue), False otherwise
        """
        with self._lock:
            # Check INV-56 compliance: paper flag must be "1"
            paper_flag = execution.meta.get("paper", "0") if execution.meta else "0"
            if paper_flag != "1":
                # INV-56 violation - execution not tagged as paper
                enforcement_event = EnforcementEvent(
                    action=EnforcementAction.BLOCKED_LIVE_TRADE,
                    venue=execution.venue,
                    symbol=execution.symbol,
                    timestamp_ns=execution.ts_ns,
                    reason=f"INV-56 violation: paper flag={paper_flag} (expected '1')",
                    attempted_signal_id=str(signal.event_id) if hasattr(signal, "event_id") else "",
                    blocked=True,
                )
                self._record_enforcement(enforcement_event)

                # Alert on violation
                if self._config.alert_on_live_attempt:
                    self._alert_live_attempt(enforcement_event)

                return False

            # Check that venue is in allowed paper venues
            venue = execution.venue
            if venue not in self._config.allowed_paper_venues:
                enforcement_event = EnforcementEvent(
                    action=EnforcementAction.BLOCKED_LIVE_TRADE,
                    venue=venue,
                    symbol=execution.symbol,
                    timestamp_ns=execution.ts_ns,
                    reason=f"Execution from non-paper venue: {venue}",
                    attempted_signal_id=str(signal.event_id) if hasattr(signal, "event_id") else "",
                    blocked=True,
                )
                self._record_enforcement(enforcement_event)

                if self._config.alert_on_live_attempt:
                    self._alert_live_attempt(enforcement_event)

                return False

            return True

    def enable_enforcement(self) -> None:
        """Enable paper-only enforcement."""
        with self._lock:
            if not self._config.enabled:
                self._config.enabled = True
                self._record_enforcement(
                    EnforcementEvent(
                        action=EnforcementAction.ENFORCEMENT_ENABLED,
                        venue="system",
                        symbol="N/A",
                        timestamp_ns=self._get_timestamp_ns(),
                        reason="Paper-only enforcement enabled",
                    )
                )

    def disable_enforcement(self, require_override: bool = True) -> bool:
        """Disable paper-only enforcement.

        Args:
            require_override: If True, requires override permission

        Returns:
            True if enforcement was disabled, False if override was required but not allowed
        """
        with self._lock:
            if require_override and not self._config.enforcement_override_allowed:
                return False

            if self._config.enabled:
                self._config.enabled = False
                self._record_enforcement(
                    EnforcementEvent(
                        action=EnforcementAction.ENFORCEMENT_DISABLED,
                        venue="system",
                        symbol="N/A",
                        timestamp_ns=self._get_timestamp_ns(),
                        reason="Paper-only enforcement disabled (DANGEROUS)",
                    )
                )

            return True

    def add_listener(self, listener: Callable[[EnforcementEvent], None]) -> None:
        """Add a listener for enforcement events."""
        with self._lock:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[EnforcementEvent], None]) -> None:
        """Remove a listener for enforcement events."""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def get_enforcement_log(self, limit: int = 100) -> list[EnforcementEvent]:
        """Get the enforcement log."""
        with self._lock:
            return self._enforcement_log[-limit:] if limit > 0 else self._enforcement_log.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get enforcement statistics."""
        with self._lock:
            return {
                "enforcement_enabled": self._config.enabled,
                "total_enforcement_checks": self._enforcement_count,
                "total_blocked_trades": self._blocked_count,
                "block_rate": (
                    self._blocked_count / self._enforcement_count
                    if self._enforcement_count > 0
                    else 0.0
                ),
                "allowed_paper_venues": list(self._config.allowed_paper_venues),
                "blocked_live_venues": list(self._config.blocked_live_venues),
                "override_allowed": self._config.enforcement_override_allowed,
            }

    def _record_enforcement(self, event: EnforcementEvent) -> None:
        """Record an enforcement event to the log and ledger."""
        self._enforcement_log.append(event)

        # Notify listeners
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass  # Don't let listener errors break enforcement

        # Record to ledger
        append_event(
            event_type="GOVERNANCE",
            sub_type="PAPER_ONLY_ENFORCEMENT",
            source="PAPER_TRADING",
            payload={
                "action": event.action.value,
                "venue": event.venue,
                "symbol": event.symbol,
                "timestamp_ns": event.timestamp_ns,
                "reason": event.reason,
                "attempted_signal_id": event.attempted_signal_id,
                "blocked": event.blocked,
            },
        )

    def _alert_live_attempt(self, event: EnforcementEvent) -> None:
        """Alert on live trading attempt."""
        # In production, this would trigger alarms, send notifications, etc.
        # For now, just log to the enforcement log (already done in _record_enforcement)

    def _get_timestamp_ns(self) -> int:
        """Get current timestamp in nanoseconds."""
        import time

        return int(time.time() * 1_000_000_000)

    def is_paper_environment(self) -> bool:
        """Check if the current environment is 100% paper-only."""
        with self._lock:
            return self._config.enabled


# Singleton instance
_enforcer: PaperOnlyEnforcer | None = None
_enforcer_lock = threading.Lock()


def get_paper_only_enforcer() -> PaperOnlyEnforcer:
    """Get the singleton paper-only enforcer."""
    global _enforcer
    with _enforcer_lock:
        if _enforcer is None:
            _enforcer = PaperOnlyEnforcer()
    return _enforcer


__all__ = [
    "EnforcementAction",
    "EnforcementConfig",
    "EnforcementEvent",
    "PaperOnlyEnforcer",
    "get_paper_only_enforcer",
]
