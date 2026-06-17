"""MICRO-01 — Advanced market microstructure analysis.

Enhances INDIRA's market microstructure analysis with order book dynamics,
liquidity depth analysis, and microstructure pattern recognition.

Pure computation. No clocks, no I/O. INV-15 deterministic.
B1: No imports from execution_engine/governance_engine/learning_engine/evolution_engine.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any
from collections import deque
from enum import Enum


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
    bid_price_levels: tuple[tuple[float, float], ...]  # (price, quantity) pairs
    ask_price_levels: tuple[tuple[float, float], ...]  # (price, quantity) pairs
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
    liquidity_score: float  # 0.0 to 1.0
    depth_at_bbp: dict[float, float]  # Percentage depth at various basis points
    spread_tier: str  # "tight", "normal", "wide"
    depth_tier: str  # "deep", "medium", "shallow"
    concentration_risk: float  # How concentrated liquidity is at best prices
    resilience_score: float  # How resilient order book is to large orders
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class MicrostructureSignal:
    """Signal derived from microstructure analysis."""
    signal_id: str
    pattern_type: MicrostructurePattern
    signal_strength: float  # 0.0 to 1.0
    direction: str  # "bullish", "bearish", "neutral"
    confidence: float  # Statistical confidence
    time_validity_bars: int  # How long this signal remains valid
    actionable_insights: tuple[str, ...]
    risk_warnings: tuple[str, ...]
    timestamp_ns: int


class OrderBookAnalyzer:
    """Analyzes order book dynamics and microstructure patterns.
    
    Processes order book snapshots to identify liquidity conditions,
    order imbalances, and trading opportunities.
    """
    
    def __init__(self, lookback_window: int = 50) -> None:
        self._lookback_window = lookback_window
        
        self._order_book_history: deque[OrderBookSnapshot] = deque(maxlen=lookback_window)
        self._spread_history: deque[float] = deque(maxlen=lookback_window)
        self._imbalance_history: deque[float] = deque(maxlen=lookback_window)
        
    def update_order_book(self, snapshot: OrderBookSnapshot) -> None:
        """Update order book snapshot history.
        
        Args:
            snapshot: Current order book snapshot
        """
        self._order_book_history.append(snapshot)
        self._spread_history.append(snapshot.spread)
        self._imbalance_history.append(snapshot.bid_ask_ratio)
    
    def analyze_liquidity_profile(self, timestamp_ns: int) -> LiquidityProfile:
        """Analyze current liquidity profile.
        
        Args:
            timestamp_ns: Current timestamp
            
        Returns:
            Current liquidity profile
        """
        if not self._order_book_history:
            return LiquidityProfile(
                liquidity_score=0.5,
                depth_at_bbp={},
                spread_tier="normal",
                depth_tier="medium",
                concentration_risk=0.5,
                resilience_score=0.5,
                timestamp_ns=timestamp_ns
            )
        
        latest = self._order_book_history[-1]
        
        # Calculate liquidity score
        liquidity_score = self._calculate_liquidity_score(latest)
        
        # Calculate depth at various basis points
        depth_at_bbp = self._calculate_depth_at_bbp(latest)
        
        # Determine spread tier
        spread_tier = self._classify_spread(latest.spread, latest.mid_price)
        
        # Determine depth tier
        depth_tier = self._classify_depth(latest.total_bid_depth + latest.total_ask_depth)
        
        # Calculate concentration risk
        concentration_risk = self._calculate_concentration_risk(latest)
        
        # Calculate resilience
        resilience_score = self._calculate_resilience(latest)
        
        return LiquidityProfile(
            liquidity_score=liquidity_score,
            depth_at_bbp=depth_at_bbp,
            spread_tier=spread_tier,
            depth_tier=depth_tier,
            concentration_risk=concentration_risk,
            resilience_score=resilience_score,
            timestamp_ns=timestamp_ns
        )
    
    def _calculate_liquidity_score(self, snapshot: OrderBookSnapshot) -> float:
        """Calculate overall liquidity score."""
        # Factors: spread tightness, depth, balance
        mid = snapshot.mid_price
        
        # Spread score (tighter is better)
        spread_pct = snapshot.spread / mid if mid > 0 else 0.0
        spread_score = max(0.0, 1.0 - spread_pct / 0.01)  # 1% spread = 0 score
        
        # Depth score (more depth is better)
        total_depth = snapshot.total_bid_depth + snapshot.total_ask_depth
        depth_score = min(1.0, total_depth / 1000000)  # Scale to reasonable range
        
        # Balance score (balanced is better)
        balance_ratio = min(snapshot.bid_quantity, snapshot.ask_quantity) / max(snapshot.bid_quantity, snapshot.ask_quantity, 1)
        balance_score = balance_ratio
        
        # Combined score
        liquidity_score = (spread_score * 0.4 + depth_score * 0.4 + balance_score * 0.2)
        
        return min(1.0, max(0.0, liquidity_score))
    
    def _calculate_depth_at_bbp(self, snapshot: OrderBookSnapshot) -> dict[float, float]:
        """Calculate depth at various basis points."""
        depth_at_bbp = {}
        
        mid = snapshot.mid_price
        
        # Calculate depth at 1, 5, 10, 20 basis points
        for bps in [1, 5, 10, 20]:
            tick = mid * (bps / 10000)
            
            bid_depth = sum(
                qty for price, qty in snapshot.bid_price_levels
                if price >= mid - tick
            )
            ask_depth = sum(
                qty for price, qty in snapshot.ask_price_levels
                if price <= mid + tick
            )
            
            total_depth = bid_depth + ask_depth
            depth_at_bbp[bps] = total_depth
    
    def _classify_spread(self, spread: float, mid_price: float) -> str:
        """Classify spread into tiers."""
        spread_pct = spread / mid if mid_price > 0 else 0.0
        
        if spread_pct < 0.0001:  # < 1 basis point
            return "tight"
        elif spread_pct < 0.0005:  # < 5 basis points
            return "normal"
        else:
            return "wide"
    
    def _classify_depth(self, total_depth: float) -> str:
        """Classify depth into tiers."""
        if total_depth > 1000000:  # > $1M
            return "deep"
        elif total_depth > 100000:  # > $100k
            return "medium"
        else:
            return "shallow"
    
    def _calculate_concentration_risk(self, snapshot: OrderBookSnapshot) -> float:
        """Calculate liquidity concentration risk at best prices."""
        # Calculate what % of depth is at best 2 levels
        best_bid_depth = snapshot.bid_quantity
        best_ask_depth = snapshot.ask_quantity
        
        total_depth = snapshot.total_bid_depth + snapshot.total_ask_depth
        if total_depth == 0:
            return 1.0  # High risk if no depth
        
        concentration = (best_bid_depth + best_ask_depth) / total_depth
        
        # Higher concentration = higher risk
        return concentration
    
    def _calculate_resilience(self, snapshot: OrderBookSnapshot) -> float:
        """Calculate order book resilience to large orders."""
        # Resilience based on depth distribution and slope
        
        # Calculate depth slope (how quickly depth decreases with price movement)
        if len(snapshot.bid_price_levels) >= 2:
            first_bid_qty = snapshot.bid_price_levels[0][1]
            second_bid_qty = snapshot.bid_price_levels[1][1]
            
            if first_bid_qty > 0:
                slope_ratio = second_bid_qty / first_bid_qty
                # Higher ratio means flatter, more resilient
                resilience_score = min(1.0, slope_ratio)
            else:
                resilience_score = 0.5
        else:
            resilience_score = 0.5
        
        return resilience_score
    
    def detect_order_imbalance(self, threshold: float = 2.0) -> MicrostructureSignal | None:
        """Detect significant order imbalance.
        
        Args:
            threshold: Imbalance threshold to trigger signal
            
        Returns:
            Microstructure signal if imbalance detected
        """
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
                timestamp_ns=latest.timestamp_ns
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
                timestamp_ns=latest.timestamp_ns
            )
        
        return None
    
    def detect_spread_widening(self) -> MicrostructureSignal | None:
        """Detect spread widening patterns.
        
        Returns:
            Microstructure signal if spread widening detected
        """
        if len(self._spread_history) < 10:
            return None
        
        recent_spreads = list(self._spread_history[-10:])
        earlier_spreads = list(self._spread_history[-20:-10])
        
        avg_recent = sum(recent_spreads) / len(recent_spreads)
        avg_earlier = sum(earlier_spreads) / len(earlier_spreads) if earlier_spreads else avg_recent
        
        if avg_recent > avg_earlier * 1.2:  # 20% spread increase
            latest = self._order_book_history[-1]
            
            return MicrostructureSignal(
                signal_id=f"spread_{latest.timestamp_ns}",
                pattern_type=MicrostructurePattern.SPREAD_WIDENING,
                signal_strength=min(1.0, (avg_recent - avg_earlier) / avg_earlier),
                direction="bearish",
                confidence=0.7,
                time_validity_bars=5,
                actionable_insights=("reduce_position_size", "widen_stops"),
                risk_warnings=("increased_transaction_costs", "liquidity_concerns"),
                timestamp_ns=latest.timestamp_ns
            )
        
        return None
    
    def detect_liquidity_spike(self) -> MicrostructureSignal | None:
        """Detect sudden liquidity changes.
        
        Returns:
            Microstructure signal if liquidity spike detected
        """
        if len(self._order_book_history) < 5:
            return None
        
        latest = self._order_book_history[-1]
        earlier = self._order_book_history[-2]
        
        latest_depth = latest.total_bid_depth + latest.total_ask_depth
        earlier_depth = earlier.total_bid_depth + earlier.total_ask_depth
        
        if earlier_depth > 0:
            depth_change = abs(latest_depth - earlier_depth) / earlier_depth
            
            if depth_change > 0.5:  # 50% depth change
                direction = "bullish" if latest_depth > earlier_depth else "bearish"
                
                return MicrostructureSignal(
                    signal_id=f"liquidity_{latest.timestamp_ns}",
                    pattern_type=MicrostructurePattern.LIQUIDITY_SPIKE,
                    signal_strength=min(1.0, depth_change / 2.0),
                    direction=direction,
                    confidence=0.75,
                    time_validity_bars=2,
                    actionable_insights=("adjust_execution_urgency", "monitor_volatility"),
                    risk_warnings=("slippage_risk_increase", "price_impact_change"),
                    timestamp_ns=latest.timestamp_ns
                )
        
        return None


class MicrostructurePatternRecognizer:
    """Recognizes trading patterns from microstructure data.
    
    Identifies patterns like momentum building, mean reversion setups,
    and price impact dynamics from order book evolution.
    """
    
    def __init__(self, pattern_window: int = 20) -> None:
        self._pattern_window = pattern_window
        
        self._microstructure_signals: deque[MicrostructureSignal] = deque(maxlen=50)
        self._pattern_history: dict[str, list[dict[str, Any]]] = {}
        
    def recognize_patterns(
        self,
        order_book_snapshots: tuple[OrderBookSnapshot, ...],
        timestamp_ns: int
    ) -> tuple[MicrostructureSignal, ...]:
        """Recognize patterns from order book evolution.
        
        Args:
            order_book_snapshots: Recent order book snapshots
            timestamp_ns: Current timestamp
            
        Returns:
            Tuple of recognized pattern signals
        """
        patterns = []
        
        if len(order_book_snapshots) < 3:
            return ()
        
        # Analyze price movement patterns
        mid_prices = [s.mid_price for s in order_book_spshots]
        
        # Detect momentum building
        momentum_signal = self._detect_momentum_building(mid_prices, timestamp_ns)
        if momentum_signal:
            patterns.append(momentum_signal)
        
        # Detect mean reversion
        mean_reversion_signal = self._detect_mean_reversion(mid_prices, timestamp_ns)
        if mean_reversion_signal:
            patterns.append(mean_reversion_signal)
        
        # Detect price impact patterns
        impact_signal = self._detect_price_impact(order_book_snapshots, timestamp_ns)
        if impact_signal:
            patterns.append(impact_signal)
        
        return tuple(patterns)
    
    def _detect_momentum_building(
        self,
        mid_prices: list[float],
        timestamp_ns: int
    ) -> MicrostructureSignal | None:
        """Detect momentum building pattern."""
        if len(mid_prices) < 5:
            return None
        
        # Calculate price changes
        price_changes = []
        for i in range(1, len(mid_prices)):
            change = (mid_prices[i] - mid_prices[i-1]) / mid_prices[i-1] if mid_prices[i-1] > 0 else 0
            price_changes.append(change)
        
        # Check for consistent directional movement
        positive_changes = sum(1 for c in price_changes if c > 0)
        negative_changes = len(price_changes) - positive_changes
        
        if positive_changes >= len(price_changes) * 0.7:
            direction = "bullish"
            strength = positive_changes / len(price_changes)
        elif negative_changes >= len(price_changes) * 0.7:
            direction = "bearish"
            strength = negative_changes / len(price_changes)
        else:
            return None
        
        return MicrostructureSignal(
            signal_id=f"momentum_{timestamp_ns}",
            pattern_type=MicrostructurePattern.MOMENTUM_BUILDING,
            signal_strength=strength,
            direction=direction,
            confidence=0.6,
            time_validity_bars=5,
            actionable_insights=("trend_following", "breakout_trading"),
            risk_warnings=("momentum_exhaustion_possible", "mean_reversion_setup"),
            timestamp_ns=timestamp_ns
        )
    
    def _detect_mean_reversion(
        self,
        mid_prices: list[float],
        timestamp_ns: int
    ) -> MicrostructureSignal | None:
        """Detect mean reversion pattern."""
        if len(mid_prices) < 5:
            return None
        
        # Calculate mean
        mean_price = sum(mid_prices) / len(mid_prices)
        
        # Calculate deviation from mean
        deviations = [abs(p - mean_price) / mean_price for p in mid_prices if mean_price > 0]
        avg_deviation = sum(deviations) / len(deviations) if deviations else 0.0
        
        # Check if prices are oscillating around mean
        recent_deviations = deviations[-3:]
        if all(d < avg_deviation for d in recent_deviations):
            # Prices converging to mean
            direction = "neutral"
            strength = 1.0 - avg_deviation
            
            return MicrostructureSignal(
                signal_id=f"mean_reversion_{timestamp_ns}",
                pattern_type=MicrostructurePattern.MEAN_REVERSION,
                signal_strength=strength,
                direction=direction,
                confidence=0.5,
                time_validity_bars=3,
                actionable_insights=("mean_reversion_trading", "range_trading"),
                risk_warnings=("low_volatility", "range_bound_market"),
                timestamp_ns=timestamp_ns
            )
        
        return None
    
    def _detect_price_impact(
        self,
        snapshots: tuple[OrderBookSnapshot, ...],
        timestamp_ns: int
    ) -> MicrostructureSignal | None:
        """Detect price impact patterns."""
        if len(snapshots) < 3:
            return None
        
        # Analyze spread and price correlation
        spreads = [s.spread for s in snapshots]
        mid_prices = [s.mid_price for s in snapshots]
        
        # Calculate correlation between spread widening and price movement
        spread_changes = []
        price_changes = []
        
        for i in range(1, len(snapshots)):
            spread_changes.append(spreads[i] - spreads[i-1])
            price_changes.append(mid_prices[i] - mid_prices[i-1])
        
        if len(spread_changes) < 2 or len(price_changes) < 2:
            return None
        
        # Calculate correlation
        n = min(len(spread_changes), len(price_changes))
        spread_changes = spread_changes[:n]
        price_changes = price_changes[:n]
        
        mean_spread = sum(spread_changes) / n
        mean_price = sum(price_changes) / n
        
        cov = sum((s - mean_spread) * (p - mean_price) for s, p in zip(spread_changes, price_changes)) / n
        std_spread = math.sqrt(sum((s - mean_spread) ** 2 for s in spread_changes) / n) or 1e-12
        std_price = math.sqrt(sum((p - mean_price) ** 2 for p in price_changes) / n) or 1e-12
        
        correlation = max(-1.0, min(1.0, cov / (std_spread * std_price)))
        
        if correlation < -0.7:  # Strong negative correlation
            return MicrostructureSignal(
                signal_id=f"impact_{timestamp_ns}",
                pattern_type=MicrostructurePattern.PRICE_IMPACT,
                signal_strength=abs(correlation),
                direction="bearish",
                confidence=0.7,
                time_validity_bars=4,
                actionable_insights=("large_moves_costly", "careful_position_sizing"),
                risk_warnings=("high_transaction_costs", "market_impact_significant"),
                timestamp_ns=timestamp_ns
            )
        
        return None


__all__ = [
    "MicrostructurePattern",
    "OrderBookSnapshot",
    "LiquidityProfile",
    "MicrostructureSignal",
    "OrderBookAnalyzer",
    "MicrostructurePatternRecognizer"
]