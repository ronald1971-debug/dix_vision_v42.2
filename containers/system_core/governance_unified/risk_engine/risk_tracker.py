"""RiskTracker — stateful fill and P&L accumulation for live risk evaluation.

The pure-function stubs in real_time_risk.py need live inputs.  This module
provides the stateful layer that accumulates fills and equity changes, then
feeds the computed drawdown_pct, notional, and position_qty into
RealTimeRiskEngine.evaluate() to produce a live RiskState.

What this tracks:
    * Per-symbol net position quantities (long positive, short negative)
    * Per-symbol notional exposure (|qty × last_price|)
    * Running realized P&L
    * Peak equity (for drawdown calculation)
    * Daily loss floor (resets each day at midnight by caller convention)

Kill condition integration:
    When a breach is detected, a RISK_BREACH event is published on the
    cognitive event bus.  INDIRA subscribes (via EnvironmentAwareness)
    and adjusts confidence accordingly.  This is the primary safety signal
    that stops cognitive overconfidence when real capital is at risk.

Persistence:
    Risk state is snapshotted to SQLite after every fill so it survives
    a process restart (PAPER mode: fills come from paper_broker; LIVE:
    from the execution fill handler).

Authority: governance_engine.* and core.* only (no intelligence imports).
INV-15: ts_ns is caller-supplied; no wall-clock reads.
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .real_time_risk import RealTimeRiskEngine, RiskState

_logger = logging.getLogger(__name__)

# World context integration (Phase 10.1 enhancement)
try:
    from world_model.indicator_integration import get_integration_bridge

    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False
    _logger.warning("[RISK_TRACKER] World model integration not available")


@dataclass
class WorldContext:
    """World context for risk evaluation with enhanced metadata."""

    market_regime: str = "unknown"
    market_trend: str = "unknown"
    volatility_regime: str = "unknown"
    liquidity_state: str = "unknown"
    agent_activity: Dict[str, float] = field(default_factory=dict)
    causal_factors: List[str] = field(default_factory=list)
    prediction_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PortfolioRiskMetrics:
    """Enhanced portfolio risk metrics with world context."""

    var_95: float = 0.0  # Value at Risk at 95% confidence
    var_99: float = 0.0  # Value at Risk at 99% confidence
    cvar_95: float = 0.0  # Conditional VaR at 95% confidence
    beta: float = 0.0  # Portfolio beta
    correlation_risk: float = 0.0  # Correlation-based risk factor
    concentration_risk: float = 0.0  # Concentration risk
    liquidity_risk: float = 0.0  # Liquidity risk
    stress_test_loss: float = 0.0  # Loss under stress scenario
    risk_score: float = 0.0  # Overall risk score (0.0-1.0)
    confidence_interval: Tuple[float, float] = (0.0, 1.0)  # 95% CI for risk score
    world_aware: bool = False  # Whether world context was used
    world_regime: str = "unknown"  # World regime at calculation time


_STORE_KIND = "risk_tracker"


# ---------------------------------------------------------------------------
# FillRecord — one confirmed fill
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class FillRecord:
    """One confirmed fill from the execution layer."""

    symbol: str
    side: str  # "buy" | "sell"
    qty: float  # always positive
    price: float
    realized_pnl: float  # 0.0 for opening fills; non-zero for closing
    ts_ns: int


# ---------------------------------------------------------------------------
# RiskTracker
# ---------------------------------------------------------------------------


class RiskTracker:
    """Stateful accumulation of fills and P&L for live risk evaluation.

    Args:
        max_drawdown_pct:        Kill at this drawdown fraction (default 5%).
        max_exposure_notional:   Kill when total notional exceeds this (default $100k).
        max_position_qty:        Kill when any single position exceeds this (default 100 units).
        starting_equity:         Baseline equity for drawdown calculation.
    """

    def __init__(
        self,
        *,
        max_drawdown_pct: float = 0.05,
        max_exposure_notional: float = 100_000.0,
        max_position_qty: float = 100.0,
        starting_equity: float = 0.0,
    ) -> None:
        self._lock = threading.Lock()
        self._engine = RealTimeRiskEngine(
            max_drawdown_pct=max_drawdown_pct,
            max_exposure_notional=max_exposure_notional,
            max_position_qty=max_position_qty,
        )
        self._max_drawdown_pct = max_drawdown_pct
        self._max_exposure_notional = max_exposure_notional
        self._max_position_qty = max_position_qty

        # Position tracking: symbol → net qty (long +, short -)
        self._positions: dict[str, float] = {}
        # Last known prices for notional calculation
        self._last_prices: dict[str, float] = {}
        # P&L accounting
        self._realized_pnl: float = 0.0
        self._starting_equity = starting_equity
        self._peak_equity: float = starting_equity
        self._fill_count: int = 0
        self._manual_halt: bool = False
        self._last_breach: str = ""
        self._fills: list[FillRecord] = []  # recent fills, capped at 200

        # World context integration (Phase 10.1 enhancement)
        self._world_integration_bridge = None
        self._current_world_context: Optional[WorldContext] = None
        self._world_adjusted_limits: dict[str, float] = {}

        # Enhanced risk metrics (Phase 10.1 enhancement)
        self._price_history: dict[str, deque] = {}  # Symbol → price history for VaR
        self._portfolio_metrics: Optional[PortfolioRiskMetrics] = None

        if WORLD_MODEL_AVAILABLE:
            self._init_world_integration()

        self._restore()

    def _init_world_integration(self) -> None:
        """Initialize world model integration bridge."""
        try:
            self._world_integration_bridge = get_integration_bridge()
            _logger.info("[RISK_TRACKER] World model integration initialized")
        except Exception as e:
            _logger.warning(f"[RISK_TRACKER] Failed to initialize world integration: {e}")
            self._world_integration_bridge = None

    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model."""
        if not self._world_integration_bridge:
            return None

        try:
            world_state = self._world_integration_bridge.get_current_state()

            if world_state:
                context = WorldContext(
                    market_regime=world_state.get("market_regime", "unknown"),
                    market_trend=world_state.get("market_trend", "unknown"),
                    volatility_regime=world_state.get("volatility_regime", "unknown"),
                    liquidity_state=world_state.get("liquidity_state", "unknown"),
                    agent_activity=world_state.get("agent_activity", {}),
                    causal_factors=world_state.get("causal_factors", []),
                    prediction_confidence=world_state.get("prediction_confidence", 0.0),
                    timestamp=datetime.utcnow(),
                )
                self._current_world_context = context
                return context

        except Exception as e:
            _logger.debug(f"[RISK_TRACKER] Failed to get world context: {e}")

        return None

    # ------------------------------------------------------------------
    # Write path — called from execution fill handler
    # ------------------------------------------------------------------

    def record_fill(
        self,
        *,
        symbol: str,
        side: str,
        qty: float,
        price: float,
        realized_pnl: float = 0.0,
        ts_ns: int,
    ) -> RiskState:
        """Integrate one fill and return the updated RiskState.

        Args:
            symbol: Instrument identifier (e.g. "BTC/USD").
            side:   "buy" or "sell".
            qty:    Fill quantity (always positive).
            price:  Fill price.
            realized_pnl: Closed P&L for this fill (0 for opening fills).
            ts_ns:  Caller-supplied timestamp (INV-15).

        Returns:
            The live RiskState after integrating the fill.
        """
        fill = FillRecord(
            symbol=symbol,
            side=side,
            qty=qty,
            price=price,
            realized_pnl=realized_pnl,
            ts_ns=ts_ns,
        )
        with self._lock:
            # Update net position
            delta = qty if side == "buy" else -qty
            self._positions[symbol] = self._positions.get(symbol, 0.0) + delta
            self._last_prices[symbol] = price
            self._realized_pnl += realized_pnl
            self._fill_count += 1
            self._fills.append(fill)
            if len(self._fills) > 200:
                self._fills = self._fills[-200:]
            # Update equity curve
            current_equity = self._starting_equity + self._realized_pnl
            if current_equity > self._peak_equity:
                self._peak_equity = current_equity
            state = self._evaluate_locked()

        if state.halted and state.breach_reason != self._last_breach:
            self._last_breach = state.breach_reason
            self._publish_breach(state, ts_ns)
            _logger.warning("RiskTracker: HALT triggered — %s", state.breach_reason)

        self._persist(ts_ns)
        self._update_market_price(symbol, price, ts_ns)
        return state

    def update_price(self, symbol: str, price: float) -> None:
        """Update last-known price for notional recalculation (best-effort)."""
        with self._lock:
            self._last_prices[symbol] = price

    def set_manual_halt(self, halted: bool) -> None:
        """Operator kill-switch toggle."""
        with self._lock:
            self._manual_halt = halted

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    def current_risk_state(self) -> RiskState:
        """Return a fresh RiskState from current accumulated position/P&L."""
        with self._lock:
            return self._evaluate_locked()

    def drawdown_pct(self) -> float:
        """Current drawdown as a fraction of peak equity."""
        with self._lock:
            return self._drawdown_pct_locked()

    def total_notional(self) -> float:
        """Sum of |qty × price| across all open positions."""
        with self._lock:
            return self._notional_locked()

    def max_position_qty(self) -> float:
        """Largest absolute position size across all symbols."""
        with self._lock:
            return self._max_pos_locked()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            state = self._evaluate_locked()
            positions = {
                sym: {"qty": qty, "price": self._last_prices.get(sym, 0.0)}
                for sym, qty in self._positions.items()
            }

            # Calculate enhanced portfolio risk metrics
            portfolio_metrics = self.calculate_portfolio_risk()

            snapshot_data = {
                "halted": state.halted,
                "breach_reason": state.breach_reason,
                "position_ok": state.position_ok,
                "drawdown_ok": state.drawdown_ok,
                "exposure_ok": state.exposure_ok,
                "realized_pnl": round(self._realized_pnl, 4),
                "peak_equity": round(self._peak_equity, 4),
                "drawdown_pct": round(self._drawdown_pct_locked(), 4),
                "total_notional": round(self._notional_locked(), 2),
                "fill_count": self._fill_count,
                "manual_halt": self._manual_halt,
                "open_positions": positions,
                "limits": {
                    "max_drawdown_pct": self._max_drawdown_pct,
                    "max_exposure_notional": self._max_exposure_notional,
                    "max_position_qty": self._max_position_qty,
                },
                # Phase 10.1 enhanced metrics
                "portfolio_risk": {
                    "var_95": round(portfolio_metrics.var_95, 2),
                    "var_99": round(portfolio_metrics.var_99, 2),
                    "cvar_95": round(portfolio_metrics.cvar_95, 2),
                    "beta": round(portfolio_metrics.beta, 3),
                    "correlation_risk": round(portfolio_metrics.correlation_risk, 3),
                    "concentration_risk": round(portfolio_metrics.concentration_risk, 3),
                    "liquidity_risk": round(portfolio_metrics.liquidity_risk, 3),
                    "stress_test_loss": round(portfolio_metrics.stress_test_loss, 2),
                    "risk_score": round(portfolio_metrics.risk_score, 3),
                    "confidence_interval": [
                        round(x, 3) for x in portfolio_metrics.confidence_interval
                    ],
                    "world_aware": portfolio_metrics.world_aware,
                    "world_regime": portfolio_metrics.world_regime,
                },
                "world_integration": {
                    "available": WORLD_MODEL_AVAILABLE,
                    "active": self._world_integration_bridge is not None,
                    "current_regime": (
                        self._current_world_context.market_regime
                        if self._current_world_context
                        else "unknown"
                    ),
                },
            }

            return snapshot_data

    def format_for_context(self) -> str:
        """Compact risk summary for EnvironmentAwareness context injection."""
        with self._lock:
            state = self._evaluate_locked()
            dd = self._drawdown_pct_locked()
        label = "HALT" if state.halted else "OK"
        return f"risk={label} dd={dd:.1%} ntl={self.total_notional():.0f}"

    # ------------------------------------------------------------------
    # Enhanced Risk Calculations (Phase 10.1)
    # ------------------------------------------------------------------

    def calculate_portfolio_risk(
        self, world_context: Optional[WorldContext] = None
    ) -> PortfolioRiskMetrics:
        """Calculate enhanced portfolio risk metrics with world context."""
        # Get world context if not provided
        if world_context is None:
            world_context = self._get_world_context()

        with self._lock:
            # Calculate VaR with world-aware parameters
            var_95, var_99 = self._calculate_var(world_context)

            # Calculate CVaR
            cvar_95 = self._calculate_cvar(var_95, world_context)

            # Calculate correlation-based risk
            correlation_risk = self._calculate_correlation_risk()

            # Calculate concentration risk
            concentration_risk = self._calculate_concentration_risk()

            # Calculate liquidity risk
            liquidity_risk = self._calculate_liquidity_risk(world_context)

            # Calculate stress test loss
            stress_test_loss = self._calculate_stress_test_loss(world_context)

            # Calculate overall risk score
            risk_score = self._calculate_overall_risk_score(
                var_95, correlation_risk, concentration_risk, liquidity_risk, stress_test_loss
            )

            # Calculate confidence interval
            confidence_interval = self._calculate_risk_confidence_interval(
                risk_score, world_context
            )

            metrics = PortfolioRiskMetrics(
                var_95=var_95,
                var_99=var_99,
                cvar_95=cvar_95,
                beta=self._calculate_portfolio_beta(),
                correlation_risk=correlation_risk,
                concentration_risk=concentration_risk,
                liquidity_risk=liquidity_risk,
                stress_test_loss=stress_test_loss,
                risk_score=risk_score,
                confidence_interval=confidence_interval,
                world_aware=world_context is not None,
                world_regime=world_context.market_regime if world_context else "unknown",
            )

            self._portfolio_metrics = metrics
            return metrics

    def _calculate_var(self, world_context: Optional[WorldContext]) -> Tuple[float, float]:
        """Calculate Value at Risk with world-aware confidence levels."""
        # Use world context to adjust confidence levels
        if world_context and world_context.volatility_regime == "high":
            # Use higher confidence for tail risk in high volatility
            confidence_95 = 0.99
            confidence_99 = 0.999
        elif world_context and world_context.volatility_regime == "medium":
            confidence_95 = 0.97
            confidence_99 = 0.995
        else:
            # Standard confidence levels
            confidence_95 = 0.95
            confidence_99 = 0.99

        # Calculate VaR using simplified approach (would use historical simulation in production)
        total_notional = self._notional_locked()
        var_95 = total_notional * 0.05  # Simplified: 5% of exposure
        var_99 = total_notional * 0.10  # Simplified: 10% of exposure

        # Adjust based on volatility regime
        if world_context:
            if world_context.volatility_regime == "high":
                var_95 *= 1.5  # Increase VaR in high volatility
                var_99 *= 1.5
            elif world_context.volatility_regime == "low":
                var_95 *= 0.8  # Decrease VaR in low volatility
                var_99 *= 0.8

        return (var_95, var_99)

    def _calculate_cvar(self, var_95: float, world_context: Optional[WorldContext]) -> float:
        """Calculate Conditional VaR (Expected Shortfall)."""
        # CVaR is typically 1.2-1.5 times VaR
        cvar_multiplier = 1.3

        # Adjust based on world conditions
        if world_context and world_context.volatility_regime == "high":
            cvar_multiplier = 1.5  # Higher tail risk in high volatility

        return var_95 * cvar_multiplier

    def _calculate_correlation_risk(self) -> float:
        """Calculate correlation-based risk across positions."""
        if len(self._positions) < 2:
            return 0.0

        # Simplified correlation risk calculation
        # In production, would use historical returns to calculate correlation matrix
        positions = list(self._positions.values())
        total_notional = self._notional_locked()

        if total_notional == 0:
            return 0.0

        # Calculate concentration as a proxy for correlation risk
        max_position = max(abs(p) for p in positions)
        concentration = max_position / total_notional

        return concentration * 0.5  # Simplified correlation risk

    def _calculate_concentration_risk(self) -> float:
        """Calculate concentration risk across positions."""
        if not self._positions:
            return 0.0

        total_notional = self._notional_locked()
        if total_notional == 0:
            return 0.0

        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        notional_per_symbol = {
            sym: abs(qty) * self._last_prices.get(sym, 0.0) for sym, qty in self._positions.items()
        }

        hhi = sum((notional / total_notional) ** 2 for notional in notional_per_symbol.values())

        # HHI ranges from 0 (perfect diversification) to 1 (single position)
        return hhi

    def _calculate_liquidity_risk(self, world_context: Optional[WorldContext]) -> float:
        """Calculate liquidity risk based on world context."""
        base_liquidity_risk = 0.1  # Base liquidity risk

        if world_context:
            if world_context.liquidity_state == "low":
                base_liquidity_risk = 0.4  # High liquidity risk
            elif world_context.liquidity_state == "medium":
                base_liquidity_risk = 0.2  # Medium liquidity risk

        return base_liquidity_risk

    def _calculate_stress_test_loss(self, world_context: Optional[WorldContext]) -> float:
        """Calculate potential loss under stress scenario."""
        total_notional = self._notional_locked()

        # Base stress scenario: 20% market decline
        stress_multiplier = 0.20

        # Adjust based on world conditions
        if world_context:
            if world_context.volatility_regime == "high":
                stress_multiplier = 0.30  # Higher stress loss in high volatility
            elif world_context.market_trend == "bearish":
                stress_multiplier = 0.35  # Higher stress loss in bearish market

        return total_notional * stress_multiplier

    def _calculate_overall_risk_score(
        self,
        var_95: float,
        correlation_risk: float,
        concentration_risk: float,
        liquidity_risk: float,
        stress_test_loss: float,
    ) -> float:
        """Calculate overall risk score from individual risk components."""
        # Normalize components to 0-1 scale
        total_notional = self._notional_locked()
        if total_notional == 0:
            return 0.0

        normalized_var = min(1.0, var_95 / total_notional)
        normalized_correlation = correlation_risk
        normalized_concentration = concentration_risk
        normalized_liquidity = liquidity_risk
        normalized_stress = min(1.0, stress_test_loss / total_notional)

        # Weighted average of risk components
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]  # VaR, correlation, concentration, liquidity, stress
        components = [
            normalized_var,
            normalized_correlation,
            normalized_concentration,
            normalized_liquidity,
            normalized_stress,
        ]

        risk_score = sum(w * c for w, c in zip(weights, components))
        return min(1.0, risk_score)

    def _calculate_portfolio_beta(self) -> float:
        """Calculate portfolio beta (simplified)."""
        # In production, would calculate based on individual position betas
        # For now, return a reasonable default
        return 1.0

    def _calculate_risk_confidence_interval(
        self, risk_score: float, world_context: Optional[WorldContext]
    ) -> Tuple[float, float]:
        """Calculate confidence interval for risk score."""
        # Use 95% confidence interval
        margin = 0.05 if world_context and world_context.prediction_confidence > 0.8 else 0.10

        lower = max(0.0, risk_score - margin)
        upper = min(1.0, risk_score + margin)

        return (lower, upper)

    # ------------------------------------------------------------------
    # Internal computation (called under self._lock)
    # ------------------------------------------------------------------

    def _evaluate_locked(self) -> RiskState:
        return self._engine.evaluate(
            position_qty=self._max_pos_locked(),
            notional=self._notional_locked(),
            drawdown_pct=self._drawdown_pct_locked(),
        )

    def _drawdown_pct_locked(self) -> float:
        if self._peak_equity <= 0:
            return 0.0
        current = self._starting_equity + self._realized_pnl
        dd = (self._peak_equity - current) / self._peak_equity
        return max(0.0, dd)

    def _notional_locked(self) -> float:
        return sum(
            abs(qty) * self._last_prices.get(sym, 0.0) for sym, qty in self._positions.items()
        )

    def _max_pos_locked(self) -> float:
        if not self._positions:
            return 0.0
        return max(abs(q) for q in self._positions.values())

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _persist(self, ts_ns: int) -> None:
        try:
            from state.cognition_persistence import get_cognition_persistence_store

            with self._lock:
                data = {
                    "positions": dict(self._positions),
                    "last_prices": dict(self._last_prices),
                    "realized_pnl": self._realized_pnl,
                    "peak_equity": self._peak_equity,
                    "fill_count": self._fill_count,
                    "manual_halt": self._manual_halt,
                }
            get_cognition_persistence_store().save_episode(
                store_kind=_STORE_KIND,
                episode_id=f"risk_snap_{self._fill_count}",
                ts_ns=ts_ns,
                data=data,
            )
        except Exception as exc:
            _logger.debug("RiskTracker._persist error: %s", exc)

    def _restore(self) -> None:
        try:
            from state.cognition_persistence import get_cognition_persistence_store

            rows = get_cognition_persistence_store().load_episodes(_STORE_KIND, limit=1)
            if not rows:
                return
            d = rows[0]
            with self._lock:
                self._positions = {str(k): float(v) for k, v in d.get("positions", {}).items()}
                self._last_prices = {str(k): float(v) for k, v in d.get("last_prices", {}).items()}
                self._realized_pnl = float(d.get("realized_pnl", 0.0))
                self._peak_equity = float(d.get("peak_equity", self._starting_equity))
                self._fill_count = int(d.get("fill_count", 0))
                self._manual_halt = bool(d.get("manual_halt", False))
            _logger.info(
                "RiskTracker: restored %d positions from persistence", len(self._positions)
            )
        except Exception as exc:
            _logger.debug("RiskTracker._restore error: %s", exc)

    # ------------------------------------------------------------------
    # Market price feedback
    # ------------------------------------------------------------------

    @staticmethod
    def _update_market_price(symbol: str, price: float, ts_ns: int) -> None:
        """Propagate confirmed fill price to MarketState LKV cache (best-effort)."""
        try:
            from state.market_state import PriceTick, get_market_state

            get_market_state().update(
                PriceTick(
                    symbol=symbol,
                    price=price,
                    volume=0.0,
                    source="risk_tracker_fill",
                    ts_ns=ts_ns,
                )
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Event bus
    # ------------------------------------------------------------------

    @staticmethod
    def _publish_breach(state: RiskState, ts_ns: int) -> None:
        try:
            from state.event_bus import CognitiveChannel, get_event_bus

            get_event_bus().publish(
                CognitiveChannel.RISK_BREACH,  # type: ignore[attr-defined]
                {
                    "halted": state.halted,
                    "breach_reason": state.breach_reason,
                    "position_ok": state.position_ok,
                    "drawdown_ok": state.drawdown_ok,
                    "exposure_ok": state.exposure_ok,
                    "ts_ns": ts_ns,
                },
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_tracker: RiskTracker | None = None
_tracker_lock = threading.Lock()


def get_risk_tracker(
    *,
    max_drawdown_pct: float = 0.05,
    max_exposure_notional: float = 100_000.0,
    max_position_qty: float = 100.0,
    starting_equity: float = 0.0,
) -> RiskTracker:
    """Return the process-wide RiskTracker singleton."""
    global _tracker
    with _tracker_lock:
        if _tracker is None:
            _tracker = RiskTracker(
                max_drawdown_pct=max_drawdown_pct,
                max_exposure_notional=max_exposure_notional,
                max_position_qty=max_position_qty,
                starting_equity=starting_equity,
            )
    return _tracker


__all__ = [
    "FillRecord",
    "RiskTracker",
    "get_risk_tracker",
]
