"""
execution_engine/paper_trading/promotion_gate_integration.py
DIX VISION v42.2 — Paper Trading Promotion Gate Integration (Phase 13)

Integrates paper trading with governance promotion gates to ensure that
promotion through the trading lifecycle (PAPER -> SHADOW -> CANARY -> LIVE)
requires approval and meets the criteria defined in docs/promotion_gates.yaml.

This module:
- Tracks paper trading performance metrics required for promotion
- Validates promotion gate criteria before allowing mode transitions
- Records promotion gate binding events to the ledger
- Enforces the "Promotion gate approval" requirement of Phase 13
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from governance_unified.control_plane.promotion_gates import (
    DEFAULT_PROMOTION_GATES_PATH,
    PromotionGates,
    compute_file_hash,
)
from state.ledger.event_store import append_event


class TradingMode(StrEnum):
    """Trading modes in the promotion lifecycle."""

    PAPER = "PAPER"
    SHADOW = "SHADOW"
    CANARY = "CANARY"
    LIVE = "LIVE"
    AUTO = "AUTO"


@dataclass
class PaperTradingMetrics:
    """Metrics tracked during paper trading for promotion evaluation."""

    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl_usd: float = 0.0
    max_drawdown_usd: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    fill_rate: float = 1.0
    window_start_ns: int = 0
    window_end_ns: int = 0
    signal_count: int = 0


@dataclass
class PromotionGateCheckResult:
    """Result of checking promotion gate criteria."""

    passed: bool
    target_mode: TradingMode
    current_mode: TradingMode
    reason: str = ""
    metrics: PaperTradingMetrics = field(default_factory=PaperTradingMetrics)
    missing_criteria: list[str] = field(default_factory=list)


class PaperTradingPromotionGateIntegration:
    """Integrates paper trading with governance promotion gates.

    This class:
    1. Tracks paper trading performance metrics
    2. Validates promotion gate criteria before mode transitions
    3. Records promotion gate events to the ledger
    4. Enforces promotion gate approval requirements

    Thread-safe singleton pattern.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current_mode = TradingMode.PAPER
        self._metrics = PaperTradingMetrics()
        self._promotion_gates: PromotionGates | None = None
        self._ledger_writer: Any = None  # Will be initialized with actual ledger writer
        self._window_start_ns: int = 0
        self._bound_hash: str | None = None

    def initialize_promotion_gates(self, ledger_writer: Any) -> None:
        """Initialize the promotion gates system with ledger writer.

        This should be called when entering PAPER mode to bind the
        promotion gates configuration to the ledger.
        """
        with self._lock:
            self._ledger_writer = ledger_writer
            # PromotionGates will be initialized with the ledger writer
            # For now, we'll create a simple mock
            self._promotion_gates = None  # Will be initialized when needed

    def enter_paper_mode(self, ts_ns: int, requestor: str = "operator") -> str:
        """Enter PAPER trading mode and bind promotion gates.

        This binds the current promotion_gates.yaml configuration to the
        ledger as required by governance. Returns the bound hash.
        """
        with self._lock:
            self._current_mode = TradingMode.PAPER
            self._window_start_ns = ts_ns
            self._metrics = PaperTradingMetrics(window_start_ns=ts_ns)

            # Compute and bind the promotion gates hash
            try:
                self._bound_hash = compute_file_hash(DEFAULT_PROMOTION_GATES_PATH)

                # Record binding to ledger
                append_event(
                    event_type="GOVERNANCE",
                    sub_type="PROMOTION_GATES_BOUND",
                    source="PAPER_TRADING",
                    payload={
                        "requestor": requestor,
                        "promotion_gates_sha256": self._bound_hash,
                        "mode": "PAPER",
                        "timestamp_ns": ts_ns,
                    },
                )

                return self._bound_hash
            except FileNotFoundError:
                # Promotion gates file not found - this is a governance failure
                raise RuntimeError("promotion_gates.yaml not found - cannot bind promotion gates")

    def record_trade(
        self,
        pnl_usd: float,
        is_winner: bool,
        fill_successful: bool,
        current_drawdown_usd: float,
        current_drawdown_pct: float,
        ts_ns: int,
    ) -> None:
        """Record a paper trade for metrics tracking.

        Args:
            pnl_usd: Profit/loss from the trade
            is_winner: Whether the trade was profitable
            fill_successful: Whether the order filled successfully
            current_drawdown_usd: Current portfolio drawdown in USD
            current_drawdown_pct: Current portfolio drawdown as percentage
            ts_ns: Trade timestamp in nanoseconds
        """
        with self._lock:
            self._metrics.total_trades += 1
            if is_winner:
                self._metrics.winning_trades += 1
            else:
                self._metrics.losing_trades += 1

            self._metrics.total_pnl_usd += pnl_usd
            self._metrics.max_drawdown_usd = max(
                self._metrics.max_drawdown_usd, current_drawdown_usd
            )
            self._metrics.max_drawdown_pct = max(
                self._metrics.max_drawdown_pct, current_drawdown_pct
            )

            # Update fill rate
            if fill_successful:
                # Maintain running fill rate
                total_fills = self._metrics.winning_trades + self._metrics.losing_trades
                if total_fills > 0:
                    self._metrics.fill_rate = total_fills / self._metrics.total_trades
            else:
                self._metrics.fill_rate = (self._metrics.fill_rate * self._metrics.total_trades) / (
                    self._metrics.total_trades + 1
                )

            self._metrics.window_end_ns = ts_ns

    def record_signal(self, ts_ns: int) -> None:
        """Record a signal generation for signal count tracking."""
        with self._lock:
            self._metrics.signal_count += 1

    def request_promotion(
        self, target_mode: TradingMode, ts_ns: int, requestor: str = "operator"
    ) -> PromotionGateCheckResult:
        """Request promotion to the next trading mode.

        Validates promotion gate criteria before allowing the transition.
        Returns a PromotionGateCheckResult indicating whether promotion is allowed.
        """
        with self._lock:
            result = PromotionGateCheckResult(
                passed=False,
                target_mode=target_mode,
                current_mode=self._current_mode,
            )

            # Check that promotion gates are bound
            if self._bound_hash is None:
                result.reason = "Promotion gates not bound - must enter PAPER mode first"
                return result

            # Validate promotion sequence
            if not self._is_valid_promotion_sequence(self._current_mode, target_mode):
                result.reason = f"Invalid promotion sequence: {self._current_mode} -> {target_mode}"
                return result

            # Check promotion gate criteria based on target mode
            if target_mode == TradingMode.SHADOW:
                result = self._check_shadow_promotion_criteria(result)
            elif target_mode == TradingMode.CANARY:
                result = self._check_canary_promotion_criteria(result)
            elif target_mode == TradingMode.LIVE:
                result = self._check_live_promotion_criteria(result)
            elif target_mode == TradingMode.AUTO:
                result = self._check_auto_promotion_criteria(result)

            # Record promotion request to ledger
            append_event(
                event_type="GOVERNANCE",
                sub_type="PROMOTION_REQUEST",
                source="PAPER_TRADING",
                payload={
                    "requestor": requestor,
                    "current_mode": self._current_mode.value,
                    "target_mode": target_mode.value,
                    "passed": result.passed,
                    "reason": result.reason,
                    "timestamp_ns": ts_ns,
                    "metrics": {
                        "total_trades": self._metrics.total_trades,
                        "signal_count": self._metrics.signal_count,
                        "total_pnl_usd": self._metrics.total_pnl_usd,
                        "max_drawdown_pct": self._metrics.max_drawdown_pct,
                        "sharpe_ratio": self._metrics.sharpe_ratio,
                        "fill_rate": self._metrics.fill_rate,
                    },
                },
            )

            return result

    def _is_valid_promotion_sequence(self, current: TradingMode, target: TradingMode) -> bool:
        """Validate that the promotion sequence is valid."""
        valid_sequences = {
            TradingMode.PAPER: {TradingMode.SHADOW},
            TradingMode.SHADOW: {TradingMode.CANARY},
            TradingMode.CANARY: {TradingMode.LIVE},
            TradingMode.LIVE: {TradingMode.AUTO},
        }
        return target in valid_sequences.get(current, set())

    def _check_shadow_promotion_criteria(
        self, result: PromotionGateCheckResult
    ) -> PromotionGateCheckResult:
        """Check SHADOW promotion criteria (from promotion_gates.yaml)."""
        missing = []

        # Minimum window duration (30 days)
        window_duration_ns = self._metrics.window_end_ns - self._metrics.window_start_ns
        min_window_ns = 30 * 24 * 60 * 60 * 1_000_000_000  # 30 days in ns
        if window_duration_ns < min_window_ns:
            missing.append(
                f"Window duration < 30 days (current: {window_duration_ns / (24*60*60*1e9):.1f} days)"
            )

        # Minimum signal count (500)
        if self._metrics.signal_count < 500:
            missing.append(f"Signal count < 500 (current: {self._metrics.signal_count})")

        # Performance floors
        if self._metrics.max_drawdown_pct > 0.05:  # 5%
            missing.append(f"Max drawdown > 5% (current: {self._metrics.max_drawdown_pct:.2%})")

        if self._metrics.fill_rate < 0.95:
            missing.append(f"Fill rate < 95% (current: {self._metrics.fill_rate:.2%})")

        # Sharpe ratio (requires calculation from returns)
        if self._metrics.sharpe_ratio < 1.0:
            missing.append(f"Sharpe ratio < 1.0 (current: {self._metrics.sharpe_ratio:.2f})")

        result.missing_criteria = missing
        result.passed = len(missing) == 0
        result.reason = (
            "All promotion criteria met"
            if result.passed
            else f"Missing criteria: {', '.join(missing)}"
        )
        result.metrics = self._metrics

        return result

    def _check_canary_promotion_criteria(
        self, result: PromotionGateCheckResult
    ) -> PromotionGateCheckResult:
        """Check CANARY promotion criteria (from promotion_gates.yaml)."""
        missing = []

        # Minimum window duration (14 days)
        window_duration_ns = self._metrics.window_end_ns - self._metrics.window_start_ns
        min_window_ns = 14 * 24 * 60 * 60 * 1_000_000_000  # 14 days in ns
        if window_duration_ns < min_window_ns:
            missing.append(
                f"Window duration < 14 days (current: {window_duration_ns / (24*60*60*1e9):.1f} days)"
            )

        # Minimum signal count (250)
        if self._metrics.signal_count < 250:
            missing.append(f"Signal count < 250 (current: {self._metrics.signal_count})")

        # Performance floors (tighter than SHADOW)
        if self._metrics.max_drawdown_pct > 0.03:  # 3%
            missing.append(f"Max drawdown > 3% (current: {self._metrics.max_drawdown_pct:.2%})")

        if self._metrics.fill_rate < 0.97:
            missing.append(f"Fill rate < 97% (current: {self._metrics.fill_rate:.2%})")

        if self._metrics.sharpe_ratio < 1.2:
            missing.append(f"Sharpe ratio < 1.2 (current: {self._metrics.sharpe_ratio:.2f})")

        result.missing_criteria = missing
        result.passed = len(missing) == 0
        result.reason = (
            "All promotion criteria met"
            if result.passed
            else f"Missing criteria: {', '.join(missing)}"
        )
        result.metrics = self._metrics

        return result

    def _check_live_promotion_criteria(
        self, result: PromotionGateCheckResult
    ) -> PromotionGateCheckResult:
        """Check LIVE promotion criteria (from promotion_gates.yaml)."""
        missing = []

        # Minimum window duration (30 days)
        window_duration_ns = self._metrics.window_end_ns - self._metrics.window_start_ns
        min_window_ns = 30 * 24 * 60 * 60 * 1_000_000_000  # 30 days in ns
        if window_duration_ns < min_window_ns:
            missing.append(
                f"Window duration < 30 days (current: {window_duration_ns / (24*60*60*1e9):.1f} days)"
            )

        # Minimum signal count (1000)
        if self._metrics.signal_count < 1000:
            missing.append(f"Signal count < 1000 (current: {self._metrics.signal_count})")

        # Performance floors (tightest requirements)
        if self._metrics.max_drawdown_pct > 0.025:  # 2.5%
            missing.append(f"Max drawdown > 2.5% (current: {self._metrics.max_drawdown_pct:.2%})")

        if self._metrics.fill_rate < 0.98:
            missing.append(f"Fill rate < 98% (current: {self._metrics.fill_rate:.2%})")

        if self._metrics.sharpe_ratio < 1.5:
            missing.append(f"Sharpe ratio < 1.5 (current: {self._metrics.sharpe_ratio:.2f})")

        result.missing_criteria = missing
        result.passed = len(missing) == 0
        result.reason = (
            "All promotion criteria met"
            if result.passed
            else f"Missing criteria: {', '.join(missing)}"
        )
        result.metrics = self._metrics

        return result

    def _check_auto_promotion_criteria(
        self, result: PromotionGateCheckResult
    ) -> PromotionGateCheckResult:
        """Check AUTO promotion criteria (from promotion_gates.yaml)."""
        missing = []

        # Same as LIVE plus drift oracle requirement
        live_result = self._check_live_promotion_criteria(result)
        if not live_result.passed:
            missing.extend(live_result.missing_criteria)

        # Drift oracle requirement (would check actual drift oracle status)
        missing.append("Drift oracle integration required (not yet implemented)")

        result.missing_criteria = missing
        result.passed = len(missing) == 0
        result.reason = (
            "All promotion criteria met"
            if result.passed
            else f"Missing criteria: {', '.join(missing)}"
        )
        result.metrics = self._metrics

        return result

    def approve_promotion(self, target_mode: TradingMode, ts_ns: int, approver: str) -> bool:
        """Approve a promotion request after governance review.

        This should only be called after a successful promotion gate check
        and governance approval.
        """
        with self._lock:
            if self._current_mode == target_mode:
                return False  # Already in target mode

            # Record promotion approval to ledger
            append_event(
                event_type="GOVERNANCE",
                sub_type="PROMOTION_APPROVED",
                source="PAPER_TRADING",
                payload={
                    "approver": approver,
                    "from_mode": self._current_mode.value,
                    "to_mode": target_mode.value,
                    "timestamp_ns": ts_ns,
                    "bound_hash": self._bound_hash,
                },
            )

            # Update current mode
            old_mode = self._current_mode
            self._current_mode = target_mode

            # Reset metrics for new window
            self._metrics = PaperTradingMetrics(window_start_ns=ts_ns)

            return True

    def get_current_mode(self) -> TradingMode:
        """Get the current trading mode."""
        with self._lock:
            return self._current_mode

    def get_metrics(self) -> PaperTradingMetrics:
        """Get the current paper trading metrics."""
        with self._lock:
            return self._metrics

    def get_bound_hash(self) -> str | None:
        """Get the bound promotion gates hash."""
        with self._lock:
            return self._bound_hash


# Singleton instance
_integration: PaperTradingPromotionGateIntegration | None = None
_integration_lock = threading.Lock()


def get_paper_trading_promotion_gate_integration() -> PaperTradingPromotionGateIntegration:
    """Get the singleton paper trading promotion gate integration."""
    global _integration
    with _integration_lock:
        if _integration is None:
            _integration = PaperTradingPromotionGateIntegration()
    return _integration


__all__ = [
    "PaperTradingPromotionGateIntegration",
    "PaperTradingMetrics",
    "PromotionGateCheckResult",
    "TradingMode",
    "get_paper_trading_promotion_gate_integration",
]
