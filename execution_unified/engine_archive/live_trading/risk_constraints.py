"""
execution_engine.live_trading.risk_constraints
DIX VISION v42.2 — Live Trading Risk Constraints (Phase 14)

Migrated from execution/live_trading/risk_constraints.py

Implements risk constraints specifically for live trading as required by Phase 14.
This ensures that live trading operates within strict risk limits to protect capital.

The risk constraints system:
- Enforces position size limits for live trading
- Validates portfolio exposure limits
- Implements circuit breakers for live trading
- Enforces leverage limits
- Provides real-time risk monitoring
- Records all constraint violations to the ledger

PHASE 14 REQUIREMENT: "Risk constrained"
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from state.ledger.event_store import append_event


class RiskConstraintType(StrEnum):
    """Types of risk constraints."""

    POSITION_SIZE_LIMIT = "POSITION_SIZE_LIMIT"
    PORTFOLIO_EXPOSURE_LIMIT = "PORTFOLIO_EXPOSURE_LIMIT"
    LEVERAGE_LIMIT = "LEVERAGE_LIMIT"
    CIRCUIT_BREAKER = "CIRCUIT_BREAKER"
    DAILY_LOSS_LIMIT = "DAILY_LOSS_LIMIT"
    VOLATILITY_LIMIT = "VOLATILITY_LIMIT"
    CONCENTRATION_LIMIT = "CONCENTRATION_LIMIT"


@dataclass
class RiskConstraintConfig:
    """Configuration for risk constraints."""

    max_position_usd: float = 10_000.0  # Maximum single position size
    max_portfolio_exposure_pct: float = 0.1  # 10% max portfolio exposure per asset
    max_leverage: float = 3.0  # Maximum leverage
    circuit_breaker_loss_pct: float = 0.02  # 2% circuit breaker
    daily_loss_limit_usd: float = 1_000.0  # Daily loss limit
    max_volatility: float = 0.1  # 10% max volatility
    max_concentration_pct: float = 0.3  # 30% max concentration in single asset


@dataclass
class RiskCheckResult:
    """Result of a risk constraint check."""

    passed: bool
    constraint_type: RiskConstraintType
    constraint_value: float
    actual_value: float
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LiveTradeRiskContext:
    """Context for live trade risk checks."""

    trade_id: str
    venue: str
    symbol: str
    side: str
    size_usd: float
    price: float
    portfolio_usd: float
    current_positions: dict[str, float]
    daily_pnl_usd: float
    volatility: float = 0.0
    leverage: float = 1.0


class LiveTradingRiskConstraints:
    """Risk constraints for live trading.

    This class enforces strict risk limits on live trading to protect capital.
    All constraints are checked before trade execution and violations are
    recorded to the ledger.

    Thread-safe singleton pattern.
    """

    def __init__(self, config: RiskConstraintConfig | None = None) -> None:
        self._lock = threading.Lock()
        self._config = config or RiskConstraintConfig()
        self._violation_log: list[RiskCheckResult] = []
        self._listeners: list[Callable[[RiskCheckResult], None]] = []
        self._enabled: bool = True
        self._daily_pnl_usd: float = 0.0
        self._daily_reset_ts_ns: int = 0
        self._total_violations: int = 0

    def configure(self, config: RiskConstraintConfig) -> None:
        """Update the risk constraint configuration."""
        with self._lock:
            self._config = config

    def enable(self) -> None:
        """Enable risk constraint enforcement."""
        with self._lock:
            self._enabled = True

    def disable(self) -> None:
        """Disable risk constraint enforcement (DANGEROUS)."""
        with self._lock:
            self._enabled = False

    def check_risk_constraints(
        self, context: LiveTradeRiskContext
    ) -> tuple[bool, list[RiskCheckResult]]:
        """Check all risk constraints for a live trade.

        Args:
            context: The risk context for the trade

        Returns:
            (passed, results) tuple where passed is True if all checks pass,
            and results is a list of all check results
        """
        with self._lock:
            if not self._enabled:
                # Risk constraints disabled - allow but log warning
                return True, []

            results: list[RiskCheckResult] = []

            # Check 1: Position size limit
            position_result = self._check_position_size_limit(context)
            results.append(position_result)

            # Check 2: Portfolio exposure limit
            exposure_result = self._check_portfolio_exposure_limit(context)
            results.append(exposure_result)

            # Check 3: Leverage limit
            leverage_result = self._check_leverage_limit(context)
            results.append(leverage_result)

            # Check 4: Circuit breaker (daily loss)
            circuit_result = self._check_circuit_breaker(context)
            results.append(circuit_result)

            # Check 5: Volatility limit
            volatility_result = self._check_volatility_limit(context)
            results.append(volatility_result)

            # Check 6: Concentration limit
            concentration_result = self._check_concentration_limit(context)
            results.append(concentration_result)

            # Record any violations
            violations = [r for r in results if not r.passed]
            for violation in violations:
                self._record_violation(violation)

            return all(r.passed for r in results), results

    def update_daily_pnl(self, pnl_usd: float, ts_ns: int) -> None:
        """Update daily P&L and reset if new day."""
        with self._lock:
            # Check if we need to reset daily P&L (new day)
            if self._daily_reset_ts_ns == 0:
                self._daily_reset_ts_ns = ts_ns
            else:
                # Reset if more than 24 hours have passed
                ns_per_day = 24 * 60 * 60 * 1_000_000_000
                if ts_ns - self._daily_reset_ts_ns > ns_per_day:
                    self._daily_pnl_usd = 0.0
                    self._daily_reset_ts_ns = ts_ns

            self._daily_pnl_usd += pnl_usd

    def _check_position_size_limit(
        self, context: LiveTradeRiskContext
    ) -> RiskCheckResult:
        """Check if the position size exceeds the limit."""
        passed = context.size_usd <= self._config.max_position_usd
        return RiskCheckResult(
            passed=passed,
            constraint_type=RiskConstraintType.POSITION_SIZE_LIMIT,
            constraint_value=self._config.max_position_usd,
            actual_value=context.size_usd,
            reason=(
                f"Position size ${context.size_usd:,.2f} "
                f"{'within' if passed else 'exceeds'} limit ${self._config.max_position_usd:,.2f}"
            ),
            metadata={"symbol": context.symbol, "venue": context.venue},
        )

    def _check_portfolio_exposure_limit(
        self, context: LiveTradeRiskContext
    ) -> RiskCheckResult:
        """Check if portfolio exposure exceeds the limit."""
        current_exposure = context.current_positions.get(context.symbol, 0.0)
        new_exposure = current_exposure + context.size_usd
        exposure_pct = new_exposure / context.portfolio_usd if context.portfolio_usd > 0 else 0.0
        passed = exposure_pct <= self._config.max_portfolio_exposure_pct

        return RiskCheckResult(
            passed=passed,
            constraint_type=RiskConstraintType.PORTFOLIO_EXPOSURE_LIMIT,
            constraint_value=self._config.max_portfolio_exposure_pct,
            actual_value=exposure_pct,
            reason=(
                f"Portfolio exposure {exposure_pct:.2%} "
                f"{'within' if passed else 'exceeds'} limit {self._config.max_portfolio_exposure_pct:.2%}"
            ),
            metadata={
                "symbol": context.symbol,
                "current_exposure": current_exposure,
                "new_exposure": new_exposure,
                "portfolio_usd": context.portfolio_usd,
            },
        )

    def _check_leverage_limit(
        self, context: LiveTradeRiskContext
    ) -> RiskCheckResult:
        """Check if leverage exceeds the limit."""
        passed = context.leverage <= self._config.max_leverage

        return RiskCheckResult(
            passed=passed,
            constraint_type=RiskConstraintType.LEVERAGE_LIMIT,
            constraint_value=self._config.max_leverage,
            actual_value=context.leverage,
            reason=(
                f"Leverage {context.leverage:.2f}x "
                f"{'within' if passed else 'exceeds'} limit {self._config.max_leverage:.2f}x"
            ),
            metadata={"symbol": context.symbol, "venue": context.venue},
        )

    def _check_circuit_breaker(
        self, context: LiveTradeRiskContext
    ) -> RiskCheckResult:
        """Check if daily losses trigger circuit breaker."""
        loss_pct = abs(context.daily_pnl_usd) / context.portfolio_usd if context.portfolio_usd > 0 else 0.0
        passed = loss_pct < self._config.circuit_breaker_loss_pct

        return RiskCheckResult(
            passed=passed,
            constraint_type=RiskConstraintType.CIRCUIT_BREAKER,
            constraint_value=self._config.circuit_breaker_loss_pct,
            actual_value=loss_pct,
            reason=(
                f"Daily loss {loss_pct:.2%} "
                f"{'below' if passed else 'triggers'} circuit breaker {self._config.circuit_breaker_loss_pct:.2%}"
            ),
            metadata={
                "daily_pnl_usd": context.daily_pnl_usd,
                "portfolio_usd": context.portfolio_usd,
            },
        )

    def _check_volatility_limit(
        self, context: LiveTradeRiskContext
    ) -> RiskCheckResult:
        """Check if volatility exceeds the limit."""
        passed = context.volatility <= self._config.max_volatility

        return RiskCheckResult(
            passed=passed,
            constraint_type=RiskConstraintType.VOLATILITY_LIMIT,
            constraint_value=self._config.max_volatility,
            actual_value=context.volatility,
            reason=(
                f"Volatility {context.volatility:.2%} "
                f"{'within' if passed else 'exceeds'} limit {self._config.max_volatility:.2%}"
            ),
            metadata={"symbol": context.symbol, "venue": context.venue},
        )

    def _check_concentration_limit(
        self, context: LiveTradeRiskContext
    ) -> RiskCheckResult:
        """Check if concentration exceeds the limit."""
        current_exposure = context.current_positions.get(context.symbol, 0.0)
        new_exposure = current_exposure + context.size_usd
        concentration_pct = new_exposure / context.portfolio_usd if context.portfolio_usd > 0 else 0.0
        passed = concentration_pct <= self._config.max_concentration_pct

        return RiskCheckResult(
            passed=passed,
            constraint_type=RiskConstraintType.CONCENTRATION_LIMIT,
            constraint_value=self._config.max_concentration_pct,
            actual_value=concentration_pct,
            reason=(
                f"Concentration {concentration_pct:.2%} "
                f"{'within' if passed else 'exceeds'} limit {self._config.max_concentration_pct:.2%}"
            ),
            metadata={
                "symbol": context.symbol,
                "concentration_pct": concentration_pct,
                "portfolio_usd": context.portfolio_usd,
            },
        )

    def _record_violation(self, result: RiskCheckResult) -> None:
        """Record a risk constraint violation to the log and ledger."""
        self._violation_log.append(result)
        self._total_violations += 1

        # Notify listeners
        for listener in self._listeners:
            try:
                listener(result)
            except Exception:
                pass

        # Record to ledger
        append_event(
            event_type="GOVERNANCE",
            sub_type="RISK_CONSTRAINT_VIOLATION",
            source="LIVE_TRADING_RISK_CONSTRAINTS",
            payload={
                "constraint_type": result.constraint_type.value,
                "constraint_value": result.constraint_value,
                "actual_value": result.actual_value,
                "reason": result.reason,
                "metadata": result.metadata,
            },
        )

    def add_listener(self, listener: Callable[[RiskCheckResult], None]) -> None:
        """Add a listener for risk constraint violations."""
        with self._lock:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[RiskCheckResult], None]) -> None:
        """Remove a listener for risk constraint violations."""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def get_violation_log(self, limit: int = 100) -> list[RiskCheckResult]:
        """Get the violation log."""
        with self._lock:
            return self._violation_log[-limit:] if limit > 0 else self._violation_log.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get risk constraint statistics."""
        with self._lock:
            return {
                "enabled": self._enabled,
                "total_violations": self._total_violations,
                "daily_pnl_usd": self._daily_pnl_usd,
                "daily_reset_ts_ns": self._daily_reset_ts_ns,
                "config": {
                    "max_position_usd": self._config.max_position_usd,
                    "max_portfolio_exposure_pct": self._config.max_portfolio_exposure_pct,
                    "max_leverage": self._config.max_leverage,
                    "circuit_breaker_loss_pct": self._config.circuit_breaker_loss_pct,
                    "daily_loss_limit_usd": self._config.daily_loss_limit_usd,
                    "max_volatility": self._config.max_volatility,
                    "max_concentration_pct": self._config.max_concentration_pct,
                },
            }


# Singleton instance
_risk_constraints: LiveTradingRiskConstraints | None = None
_risk_constraints_lock = threading.Lock()


def get_live_trading_risk_constraints(
    config: RiskConstraintConfig | None = None,
) -> LiveTradingRiskConstraints:
    """Get the singleton live trading risk constraints."""
    global _risk_constraints
    with _risk_constraints_lock:
        if _risk_constraints is None:
            _risk_constraints = LiveTradingRiskConstraints(config)
    return _risk_constraints


__all__ = [
    "LiveTradeRiskContext",
    "LiveTradingRiskConstraints",
    "RiskCheckResult",
    "RiskConstraintConfig",
    "RiskConstraintType",
    "get_live_trading_risk_constraints",
]
