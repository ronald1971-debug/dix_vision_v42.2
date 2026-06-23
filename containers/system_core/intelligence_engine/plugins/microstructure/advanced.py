"""MICRO-ADV-01 — Advanced market microstructure analysis plugin v1.

Enhanced microstructure analysis with order book dynamics, liquidity depth analysis,
and microstructure pattern recognition. Contract-compliant implementation.

Pure computation. No clocks, no I/O. INV-15 deterministic.
B1: No imports from execution_engine/governance_engine/learning_engine/evolution_engine.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from core.contracts.engine import (
    HealthState,
    HealthStatus,
    MicrostructurePlugin,
    PluginLifecycle,
)
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick


class MicrostructurePattern(Enum):
    """Types of market microstructure patterns."""

    ORDER_IMBALANCE = "order_imbalance"
    LIQUIDITY_SPIKE = "liquidity_spike"
    SPREAD_WIDENING = "spread_widening"
    PRICE_IMPACT = "price_impact"
    DEPTH_DISTRIBUTION = "depth_distribution"
    MOMENTUM_BUILDING = "momentum_building"
    MEAN_REVERSION = "mean_reversion"


@dataclass(frozen=True, slots=True)
class OrderBookSnapshot:
    """Snapshot of order book state."""

    timestamp_ns: int
    best_bid: float
    best_ask: float
    bid_quantity: float
    ask_quantity: float
    bid_price_levels: tuple[tuple[float, float], ...]
    ask_price_levels: tuple[tuple[float, float], ...]
    total_bid_depth: float
    total_ask_depth: float
    spread: float
    mid_price: float

    @property
    def bid_ask_ratio(self) -> float:
        """Ratio of bid to ask quantities."""
        return self.bid_quantity / self.ask_quantity if self.ask_quantity > 0 else 0.0


@dataclass(frozen=True, slots=True)
class LiquidityProfile:
    """Liquidity profile analysis."""

    liquidity_score: float
    depth_at_bbp: dict[float, float]
    spread_tier: str
    depth_tier: str
    concentration_risk: float
    resilience_score: float
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class MicrostructureSignal:
    """Signal derived from microstructure analysis."""

    signal_id: str
    pattern_type: MicrostructurePattern
    signal_strength: float
    direction: str
    confidence: float
    time_validity_bars: int
    actionable_insights: tuple[str, ...]
    risk_warnings: tuple[str, ...]
    timestamp_ns: int


class OrderBookAnalyzer:
    """Analyzes order book dynamics and microstructure patterns."""

    def __init__(self, lookback_window: int = 50) -> None:
        self._lookback_window = lookback_window
        self._order_book_history: deque[OrderBookSnapshot] = deque(maxlen=lookback_window)
        self._spread_history: deque[float] = deque(maxlen=lookback_window)
        self._imbalance_history: deque[float] = deque(maxlen=lookback_window)

    def update_order_book(self, snapshot: OrderBookSnapshot) -> None:
        """Update order book snapshot history."""
        self._order_book_history.append(snapshot)
        self._spread_history.append(snapshot.spread)
        self._imbalance_history.append(snapshot.bid_ask_ratio)

    def analyze_liquidity_profile(self, timestamp_ns: int) -> LiquidityProfile:
        """Analyze current liquidity profile."""
        if not self._order_book_history:
            return LiquidityProfile(
                liquidity_score=0.5,
                depth_at_bbp={},
                spread_tier="normal",
                depth_tier="medium",
                concentration_risk=0.5,
                resilience_score=0.5,
                timestamp_ns=timestamp_ns,
            )

        latest = self._order_book_history[-1]

        liquidity_score = self._calculate_liquidity_score(latest)
        depth_at_bbp = self._calculate_depth_at_bbp(latest)
        spread_tier = self._classify_spread(latest.spread, latest.mid_price)
        depth_tier = self._classify_depth(latest.total_bid_depth + latest.total_ask_depth)
        concentration_risk = self._calculate_concentration_risk(latest)
        resilience_score = self._calculate_resilience(latest)

        return LiquidityProfile(
            liquidity_score=liquidity_score,
            depth_at_bbp=depth_at_bbp,
            spread_tier=spread_tier,
            depth_tier=depth_tier,
            concentration_risk=concentration_risk,
            resilience_score=resilience_score,
            timestamp_ns=timestamp_ns,
        )

    def _calculate_liquidity_score(self, snapshot: OrderBookSnapshot) -> float:
        """Calculate overall liquidity score."""
        mid = snapshot.mid_price
        spread_pct = snapshot.spread / mid if mid > 0 else 0.0
        spread_score = max(0.0, 1.0 - spread_pct / 0.01)

        total_depth = snapshot.total_bid_depth + snapshot.total_ask_depth
        depth_score = min(1.0, total_depth / 1000000)

        balance_ratio = min(snapshot.bid_quantity, snapshot.ask_quantity) / max(
            snapshot.bid_quantity, snapshot.ask_quantity, 1
        )
        balance_score = balance_ratio

        liquidity_score = spread_score * 0.4 + depth_score * 0.4 + balance_score * 0.2
        return min(1.0, max(0.0, liquidity_score))

    def _calculate_depth_at_bbp(self, snapshot: OrderBookSnapshot) -> dict[float, float]:
        """Calculate depth at various basis points."""
        depth_at_bbp = {}
        mid = snapshot.mid_price

        for bps in [1, 5, 10, 20]:
            tick = mid * (bps / 10000)
            bid_depth = sum(qty for price, qty in snapshot.bid_price_levels if price >= mid - tick)
            ask_depth = sum(qty for price, qty in snapshot.ask_price_levels if price <= mid + tick)
            total_depth = bid_depth + ask_depth
            depth_at_bbp[bps] = total_depth

        return depth_at_bbp

    def _classify_spread(self, spread: float, mid_price: float) -> str:
        """Classify spread into tiers."""
        spread_pct = spread / mid_price if mid_price > 0 else 0.0
        if spread_pct < 0.0001:
            return "tight"
        elif spread_pct < 0.0005:
            return "normal"
        else:
            return "wide"

    def _classify_depth(self, total_depth: float) -> str:
        """Classify depth into tiers."""
        if total_depth > 1000000:
            return "deep"
        elif total_depth > 100000:
            return "medium"
        else:
            return "shallow"

    def _calculate_concentration_risk(self, snapshot: OrderBookSnapshot) -> float:
        """Calculate liquidity concentration risk at best prices."""
        best_bid_depth = snapshot.bid_quantity
        best_ask_depth = snapshot.ask_quantity
        total_depth = snapshot.total_bid_depth + snapshot.total_ask_depth

        if total_depth == 0:
            return 1.0

        concentration = (best_bid_depth + best_ask_depth) / total_depth
        return concentration

    def _calculate_resilience(self, snapshot: OrderBookSnapshot) -> float:
        """Calculate order book resilience score."""
        mid = snapshot.mid_price
        total_depth = snapshot.total_bid_depth + snapshot.total_ask_depth

        if total_depth == 0:
            return 0.0

        # Calculate weighted average depth
        weighted_depth = 0.0
        weight_sum = 0.0

        for price, qty in snapshot.bid_price_levels:
            distance = (mid - price) / mid if mid > 0 else 0
            weight = max(0.1, 1.0 - distance * 100)
            weighted_depth += qty * weight
            weight_sum += weight

        for price, qty in snapshot.ask_price_levels:
            distance = (price - mid) / mid if mid > 0 else 0
            weight = max(0.1, 1.0 - distance * 100)
            weighted_depth += qty * weight
            weight_sum += weight

        if weight_sum == 0:
            return 0.5

        resilience = weighted_depth / weight_sum / total_depth
        return min(1.0, max(0.0, resilience))

    def detect_order_imbalance(self, threshold: float = 2.0) -> MicrostructureSignal | None:
        """Detect significant order imbalance."""
        if not self._order_book_history:
            return None

        latest = self._order_book_history[-1]
        current_imbalance = latest.bid_ask_ratio

        if current_imbalance > threshold:
            return MicrostructureSignal(
                signal_id=f"imbalance_{latest.timestamp_ns}",
                pattern_type=MicrostructurePattern.ORDER_IMBALANCE,
                signal_strength=min(1.0, (current_imbalance - threshold) / 3.0),
                direction="bearish" if current_imbalance > 1.0 else "bullish",
                confidence=0.8,
                time_validity_bars=3,
                actionable_insights=("strong_selling_pressure", "potential_reversal_setup"),
                risk_warnings=("momentum_reversal_possible", "high_volatility_expected"),
                timestamp_ns=latest.timestamp_ns,
            )
        elif current_imbalance < (1.0 / threshold):
            return MicrostructureSignal(
                signal_id=f"imbalance_{latest.timestamp_ns}",
                pattern_type=MicrostructurePattern.ORDER_IMBALANCE,
                signal_strength=min(1.0, ((1.0 / current_imbalance) - threshold) / 3.0),
                direction="bullish" if current_imbalance < 1.0 else "bearish",
                confidence=0.8,
                time_validity_bars=3,
                actionable_insights=("strong_buying_pressure", "potential_breakout"),
                risk_warnings=("momentum_continuation", "liquidity_drying"),
                timestamp_ns=latest.timestamp_ns,
            )

        return None


@dataclass(slots=True)
class MicrostructureAdvanced(MicrostructurePlugin):
    """Advanced microstructure analysis plugin with order book dynamics.

    Enhances market microstructure analysis with order book dynamics,
    liquidity depth analysis, and microstructure pattern recognition.
    """

    name: str = "microstructure_advanced"
    version: str = "1.0.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    lookback_window: int = 50
    imbalance_threshold: float = 2.0
    confidence_threshold: float = 0.6
    min_confidence: float = 0.4

    _analyzer: OrderBookAnalyzer = field(init=False, repr=False)
    _tick_history: deque[MarketTick] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.lookback_window < 10:
            raise ValueError("lookback_window must be >= 10")
        if self.imbalance_threshold < 1.0:
            raise ValueError("imbalance_threshold must be >= 1.0")
        if not (0.0 <= self.confidence_threshold <= 1.0):
            raise ValueError("confidence_threshold must be in [0.0, 1.0]")
        if not (0.0 <= self.min_confidence <= 1.0):
            raise ValueError("min_confidence must be in [0.0, 1.0]")

        self._analyzer = OrderBookAnalyzer(lookback_window=self.lookback_window)
        self._tick_history = deque(maxlen=self.lookback_window)

    def on_tick(self, tick: MarketTick) -> Sequence[SignalEvent]:
        """Process a market tick and emit microstructure signals.

        Args:
            tick: The market tick to process.

        Returns:
            A sequence of SignalEvents based on advanced microstructure analysis.
        """
        self._tick_history.append(tick)

        # Convert tick to order book snapshot
        snapshot = self._tick_to_order_book_snapshot(tick)

        # Update analyzer
        self._analyzer.update_order_book(snapshot)

        # Generate signals
        signals = []

        # Detect order imbalance
        imbalance_signal = self._analyzer.detect_order_imbalance(self.imbalance_threshold)
        if imbalance_signal and imbalance_signal.confidence >= self.min_confidence:
            signal_event = self._microstructure_signal_to_event(imbalance_signal, tick)
            if signal_event:
                signals.append(signal_event)

        # Analyze liquidity profile
        liquidity_profile = self._analyzer.analyze_liquidity_profile(tick.timestamp_ns)

        # Generate liquidity-based signals
        if liquidity_profile.liquidity_score < 0.3:
            # Low liquidity signal
            signal_event = SignalEvent(
                source=self.name,
                timestamp_ns=tick.timestamp_ns,
                symbol=tick.symbol,
                side=Side.HOLD,
                confidence=max(self.min_confidence, 1.0 - liquidity_profile.liquidity_score),
                reason=f"low_liquidity_score:{liquidity_profile.liquidity_score:.2f}",
                metadata={"liquidity_profile": liquidity_profile.liquidity_score},
            )
            signals.append(signal_event)

        return signals

    def _tick_to_order_book_snapshot(self, tick: MarketTick) -> OrderBookSnapshot:
        """Convert market tick to order book snapshot."""
        # Create simplified order book snapshot from tick data
        # In a real implementation, this would use actual order book data

        bid_price = tick.bid if hasattr(tick, "bid") and tick.bid else tick.last * 0.999
        ask_price = tick.ask if hasattr(tick, "ask") and tick.ask else tick.last * 1.001
        mid_price = (bid_price + ask_price) / 2
        spread = ask_price - bid_price

        # Simulated order book levels
        bid_levels = tuple(
            (bid_price * (1 - i * 0.0001), tick.volume * (1 - i * 0.1)) for i in range(5)
        )
        ask_levels = tuple(
            (ask_price * (1 + i * 0.0001), tick.volume * (1 - i * 0.1)) for i in range(5)
        )

        total_bid_depth = sum(qty for _, qty in bid_levels)
        total_ask_depth = sum(qty for _, qty in ask_levels)

        return OrderBookSnapshot(
            timestamp_ns=tick.timestamp_ns,
            best_bid=bid_price,
            best_ask=ask_price,
            bid_quantity=tick.volume if hasattr(tick, "volume") else 1.0,
            ask_quantity=tick.volume if hasattr(tick, "volume") else 1.0,
            bid_price_levels=bid_levels,
            ask_price_levels=ask_levels,
            total_bid_depth=total_bid_depth,
            total_ask_depth=total_ask_depth,
            spread=spread,
            mid_price=mid_price,
        )

    def _microstructure_signal_to_event(
        self, microsignal: MicrostructureSignal, tick: MarketTick
    ) -> SignalEvent | None:
        """Convert microstructure signal to signal event."""
        if microsignal.confidence < self.confidence_threshold:
            return None

        # Map direction to side
        direction_map = {"bullish": Side.BUY, "bearish": Side.SELL, "neutral": Side.HOLD}

        side = direction_map.get(microsignal.direction, Side.HOLD)

        # Create signal event
        return SignalEvent(
            source=self.name,
            timestamp_ns=tick.timestamp_ns,
            symbol=tick.symbol,
            side=side,
            confidence=microsignal.confidence,
            reason=f"{microsignal.pattern_type.value}:{microsignal.direction}",
            metadata={
                "pattern_type": microsignal.pattern_type.value,
                "signal_strength": microsignal.signal_strength,
                "time_validity_bars": microsignal.time_validity_bars,
                "insights": microsignal.actionable_insights,
                "warnings": microsignal.risk_warnings,
            },
        )

    def check_self(self) -> HealthStatus:
        """Health check for the plugin."""
        try:
            # Check if analyzer is operational
            if not self._analyzer:
                return HealthStatus(
                    engine_name=self.name,
                    state=HealthState.DEGRADED,
                    detail="Analyzer not initialized",
                )

            # Check tick history
            if len(self._tick_history) == 0:
                return HealthStatus(
                    engine_name=self.name,
                    state=HealthState.ALIVE,
                    detail=f"{self.name} v{self.version} lifecycle={self.lifecycle} window={self.lookback_window} (awaiting data)",
                )

            return HealthStatus(
                engine_name=self.name,
                state=HealthState.ALIVE,
                detail=f"{self.name} v{self.version} lifecycle={self.lifecycle} window={self.lookback_window} samples={len(self._tick_history)}",
            )

        except Exception as e:
            return HealthStatus(
                engine_name=self.name,
                state=HealthState.FAIL,
                detail=f"Health check failed: {str(e)}",
            )


__all__ = [
    "MicrostructureAdvanced",
    "OrderBookAnalyzer",
    "MicrostructurePattern",
    "OrderBookSnapshot",
    "LiquidityProfile",
    "MicrostructureSignal",
]
