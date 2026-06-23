"""Platform Understanding Layer - Advanced Platform Mechanics and Microstructure Analysis.

This module provides sophisticated platform understanding capabilities including
platform mechanics modeling, order book dynamics analysis, cross-platform
arbitrage detection, and platform health monitoring.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class PlatformType(str, Enum):
    """Classification of trading platforms."""

    CENTRALIZED_EXCHANGE = "CENTRALIZED_EXCHANGE"
    DECENTRALIZED_EXCHANGE = "DECENTRALIZED_EXCHANGE"
    P2P_MARKETPLACE = "P2P_MARKETPLACE"
    BROKERAGE_PLATFORM = "BROKERAGE_PLATFORM"
    LIQUIDITY_POOL = "LIQUIDITY_POOL"
    DARK_POOL = "DARK_POOL"


class OrderBookState(str, Enum):
    """Order book state classification."""

    BALANCED = "BALANCED"
    BUY_HEAVY = "BUY_HEAVY"
    SELL_HEAVY = "SELL_HEAVY"
    ILLIQUID = "ILLIQUID"
    VOLATILE = "VOLATILE"
    MANIPULATED = "MANIPULATED"


@dataclass
class PlatformMechanics:
    """Platform trading mechanics and rules."""

    platform_id: str
    platform_type: PlatformType
    order_types: List[str]  # "market", "limit", "stop", "iceberg", etc.
    fee_structure: Dict[str, float]  # "maker", "taker", "withdrawal"
    latency_profile: Dict[str, float]  # "order_ack", "execution", "settlement"
    limits: Dict[str, Any]  # position limits, rate limits, etc.
    routing_rules: Dict[str, Any]
    last_updated: float


@dataclass
class OrderBook:
    """Order book representation."""

    symbol: str
    platform: str
    bids: List[Tuple[float, float]]  # (price, quantity)
    asks: List[Tuple[float, float]]  # (price, quantity)
    timestamp: float
    spread: float = 0.0
    mid_price: float = 0.0
    total_bid_volume: float = 0.0
    total_ask_volume: float = 0.0


@dataclass
class OrderBookDynamics:
    """Order book dynamics analysis."""

    symbol: str
    platform: str
    current_state: OrderBookState
    liquidity_score: float
    depth_profile: Dict[str, float]
    imbalance_ratio: float
    price_impact: float
    volatility_index: float
    manipulation_indicators: List[str]
    trend_direction: str
    momentum: float


@dataclass
class PlatformAnomaly:
    """Detected platform anomaly."""

    anomaly_id: str
    platform: str
    anomaly_type: str  # "latency_spike", "freeze", "manipulation", "liquidity_drain"
    severity: str  # "low", "medium", "high", "critical"
    timestamp: float
    description: str
    metrics: Dict[str, float]
    recommended_action: str


@dataclass
class ArbitrageOpportunity:
    """Detected arbitrage opportunity."""

    opportunity_id: str
    symbol: str
    platforms: List[str]
    price_diff: float
    price_diff_pct: float
    estimated_profit: float
    risk_level: str
    timestamp: float
    execution_window: float  # Time window for execution


class PlatformUnderstanding:
    """Advanced platform understanding with sophisticated analysis."""

    def __init__(self, history_window: int = 1000):
        self._lock = threading.Lock()
        self._history_window = history_window
        self._platform_mechanics: Dict[str, PlatformMechanics] = {}
        self._order_book_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=history_window)
        )
        self._anomalies: List[PlatformAnomaly] = []
        self._arbitrage_opportunities: List[ArbitrageOpportunity] = []
        self._order_book_analyzer = OrderBookAnalyzer()
        self._platform_health_monitor = PlatformHealthMonitor()
        self._arbitrage_detector = ArbitrageDetector()
        self._initialized = False

    def start(self) -> bool:
        """Start platform understanding system."""
        logger.info("[PLATFORM_UNDERSTANDING] Starting advanced platform understanding...")
        self._initialized = True
        logger.info("[PLATFORM_UNDERSTANDING] Advanced platform understanding started")
        return True

    def stop(self) -> bool:
        """Stop platform understanding system."""
        logger.info("[PLATFORM_UNDERSTANDING] Stopping advanced platform understanding...")
        self._initialized = False
        logger.info("[PLATFORM_UNDERSTANDING] Advanced platform understanding stopped")
        return True

    def register_platform_mechanics(self, mechanics: PlatformMechanics) -> None:
        """Register platform mechanics."""
        with self._lock:
            self._platform_mechanics[mechanics.platform_id] = mechanics
            logger.info(
                f"[PLATFORM_UNDERSTANDING] Registered mechanics for {mechanics.platform_id}"
            )

    def model_order_book_dynamics(self, order_book: OrderBook) -> OrderBookDynamics:
        """Model order book dynamics with advanced analysis."""
        logger.debug(
            f"[PLATFORM_UNDERSTANDING] Modeling order book dynamics for {order_book.symbol} on {order_book.platform}"
        )

        # Store order book in history
        with self._lock:
            self._order_book_history[f"{order_book.platform}_{order_book.symbol}"].append(
                order_book
            )

        # Analyze dynamics
        dynamics = self._order_book_analyzer.analyze_dynamics(
            order_book, self._get_historical_order_books(order_book.platform, order_book.symbol)
        )

        return dynamics

    def detect_platform_anomalies(
        self, platform: str, current_metrics: Dict[str, float]
    ) -> List[PlatformAnomaly]:
        """Detect platform-specific anomalies."""
        logger.info(f"[PLATFORM_UNDERSTANDING] Detecting anomalies for {platform}")

        # Detect anomalies using health monitor
        anomalies = self._platform_health_monitor.detect_anomalies(
            platform, current_metrics, self._platform_mechanics.get(platform)
        )

        # Store detected anomalies
        with self._lock:
            self._anomalies.extend(anomalies)
            # Keep only recent anomalies
            if len(self._anomalies) > 500:
                self._anomalies = self._anomalies[-500:]

        return anomalies

    def detect_arbitrage_opportunities(
        self, symbol: str, current_prices: Dict[str, float]
    ) -> List[ArbitrageOpportunity]:
        """Detect cross-platform arbitrage opportunities."""
        logger.info(f"[PLATFORM_UNDERSTANDING] Detecting arbitrage opportunities for {symbol}")

        # Detect arbitrage opportunities
        opportunities = self._arbitrage_detector.detect_opportunities(
            symbol, current_prices, self._platform_mechanics
        )

        # Store detected opportunities
        with self._lock:
            self._arbitrage_opportunities.extend(opportunities)
            # Keep only recent opportunities
            if len(self._arbitrage_opportunities) > 1000:
                self._arbitrage_opportunities = self._arbitrage_opportunities[-1000:]

        return opportunities

    def assess_platform_health(self, platform: str) -> Dict[str, Any]:
        """Assess overall platform health."""
        logger.info(f"[PLATFORM_UNDERSTANDING] Assessing health for {platform}")

        mechanics = self._platform_mechanics.get(platform)
        if not mechanics:
            return {"error": "Platform mechanics not registered"}

        # Assess health
        health_assessment = self._platform_health_monitor.assess_health(
            platform, mechanics, self._get_recent_anomalies(platform)
        )

        return health_assessment

    def get_platform_mechanics(self, platform: str) -> Optional[PlatformMechanics]:
        """Get platform mechanics."""
        with self._lock:
            return self._platform_mechanics.get(platform)

    def _get_historical_order_books(
        self, platform: str, symbol: str, limit: int = 50
    ) -> List[OrderBook]:
        """Get historical order books for analysis."""
        with self._lock:
            history = list(self._order_book_history[f"{platform}_{symbol}"])
            return history[-limit:] if history else []

    def _get_recent_anomalies(self, platform: str, limit: int = 20) -> List[PlatformAnomaly]:
        """Get recent anomalies for a platform."""
        with self._lock:
            platform_anomalies = [a for a in self._anomalies if a.platform == platform]
            return platform_anomalies[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get platform understanding statistics."""
        with self._lock:
            return {
                "total_platforms": len(self._platform_mechanics),
                "total_anomalies": len(self._anomalies),
                "total_arbitrage_opportunities": len(self._arbitrage_opportunities),
                "order_books_tracked": len(self._order_book_history),
                "platforms_by_type": self._count_by_platform_type(),
            }

    def _count_by_platform_type(self) -> Dict[str, int]:
        """Count platforms by type."""
        counts = defaultdict(int)
        for mechanics in self._platform_mechanics.values():
            counts[mechanics.platform_type.value] += 1
        return dict(counts)


class OrderBookAnalyzer:
    """Advanced order book dynamics analysis."""

    def analyze_dynamics(
        self, current_order_book: OrderBook, historical_order_books: List[OrderBook]
    ) -> OrderBookDynamics:
        """Analyze order book dynamics comprehensively."""
        # Calculate basic metrics
        spread, mid_price = self._calculate_spread_and_mid(current_order_book)
        total_bid_volume = sum(qty for _, qty in current_order_book.bids)
        total_ask_volume = sum(qty for _, qty in current_order_book.asks)

        # Determine order book state
        current_state = self._determine_order_book_state(
            current_order_book, spread, total_bid_volume, total_ask_volume
        )

        # Calculate liquidity score
        liquidity_score = self._calculate_liquidity_score(
            current_order_book, historical_order_books
        )

        # Calculate depth profile
        depth_profile = self._calculate_depth_profile(current_order_book)

        # Calculate imbalance ratio
        imbalance_ratio = self._calculate_imbalance_ratio(total_bid_volume, total_ask_volume)

        # Calculate price impact
        price_impact = self._calculate_price_impact(current_order_book)

        # Calculate volatility index
        volatility_index = self._calculate_volatility_index(historical_order_books)

        # Detect manipulation indicators
        manipulation_indicators = self._detect_manipulation(
            current_order_book, historical_order_books
        )

        # Determine trend direction
        trend_direction, momentum = self._determine_trend_and_momentum(historical_order_books)

        return OrderBookDynamics(
            symbol=current_order_book.symbol,
            platform=current_order_book.platform,
            current_state=current_state,
            liquidity_score=liquidity_score,
            depth_profile=depth_profile,
            imbalance_ratio=imbalance_ratio,
            price_impact=price_impact,
            volatility_index=volatility_index,
            manipulation_indicators=manipulation_indicators,
            trend_direction=trend_direction,
            momentum=momentum,
        )

    def _calculate_spread_and_mid(self, order_book: OrderBook) -> Tuple[float, float]:
        """Calculate spread and mid-price."""
        if order_book.bids and order_book.asks:
            best_bid = order_book.bids[0][0]
            best_ask = order_book.asks[0][0]
            spread = best_ask - best_bid
            mid_price = (best_bid + best_ask) / 2
            return spread, mid_price
        return 0.0, 0.0

    def _determine_order_book_state(
        self, order_book: OrderBook, spread: float, bid_vol: float, ask_vol: float
    ) -> OrderBookState:
        """Determine current order book state."""
        total_volume = bid_vol + ask_vol
        if total_volume == 0:
            return OrderBookState.ILLIQUID

        # Check for illiquidity
        if total_volume < 0.01:
            return OrderBookState.ILLIQUID

        # Check for imbalance
        imbalance_ratio = abs(bid_vol - ask_vol) / total_volume
        if imbalance_ratio > 0.7:
            if bid_vol > ask_vol:
                return OrderBookState.BUY_HEAVY
            else:
                return OrderBookState.SELL_HEAVY

        # Check for manipulation (extreme spread)
        if order_book.bids and order_book.asks:
            mid_price = (order_book.bids[0][0] + order_book.asks[0][0]) / 2
            spread_pct = spread / mid_price if mid_price > 0 else 0
            if spread_pct > 0.05:  # More than 5% spread
                return OrderBookState.MANIPULATED

        return OrderBookState.BALANCED

    def _calculate_liquidity_score(
        self, current_order_book: OrderBook, historical_order_books: List[OrderBook]
    ) -> float:
        """Calculate comprehensive liquidity score."""
        if not current_order_book.bids or not current_order_book.asks:
            return 0.0

        # Current liquidity metrics
        total_volume = sum(qty for _, qty in current_order_book.bids) + sum(
            qty for _, qty in current_order_book.asks
        )
        spread, mid_price = self._calculate_spread_and_mid(current_order_book)
        spread_pct = spread / mid_price if mid_price > 0 else 0

        # Depth metrics
        bid_depth = len(current_order_book.bids)
        ask_depth = len(current_order_book.asks)

        # Historical consistency
        historical_liquidity = []
        for ob in historical_order_books:
            if ob.bids and ob.asks:
                hist_vol = sum(qty for _, qty in ob.bids) + sum(qty for _, qty in ob.asks)
                historical_liquidity.append(hist_vol)

        consistency_score = 1.0
        if historical_liquidity:
            consistency_score = (
                1.0 - (np.std(historical_liquidity) / np.mean(historical_liquidity))
                if np.mean(historical_liquidity) > 0
                else 0.5
            )

        # Combine scores
        volume_score = min(1.0, total_volume / 100.0)  # Normalize to 100 units as reference
        depth_score = min(
            1.0, (bid_depth + ask_depth) / 40.0
        )  # Normalize to 40 levels as reference
        spread_score = max(0.0, 1.0 - spread_pct * 10)  # Penalize wide spreads

        liquidity_score = (
            volume_score * 0.4 + depth_score * 0.3 + spread_score * 0.2 + consistency_score * 0.1
        )

        return max(0.0, min(1.0, liquidity_score))

    def _calculate_depth_profile(self, order_book: OrderBook) -> Dict[str, float]:
        """Calculate depth profile of order book."""
        if not order_book.bids or not order_book.asks:
            return {}

        # Calculate depth at different price levels
        bid_levels = [0, 0.5, 1.0, 2.0]  # Percentage from best bid
        ask_levels = [0, 0.5, 1.0, 2.0]  # Percentage from best ask

        best_bid = order_book.bids[0][0]
        best_ask = order_book.asks[0][0]

        depth_profile = {}

        # Bid depth
        for level_pct in bid_levels:
            price_threshold = best_bid * (1 - level_pct)
            volume_at_level = sum(qty for price, qty in order_book.bids if price >= price_threshold)
            depth_profile[f"bid_depth_{int(level_pct*100)}pct"] = volume_at_level

        # Ask depth
        for level_pct in ask_levels:
            price_threshold = best_ask * (1 + level_pct)
            volume_at_level = sum(qty for price, qty in order_book.asks if price <= price_threshold)
            depth_profile[f"ask_depth_{int(level_pct*100)}pct"] = volume_at_level

        return depth_profile

    def _calculate_imbalance_ratio(self, bid_vol: float, ask_vol: float) -> float:
        """Calculate bid-ask imbalance ratio."""
        total_vol = bid_vol + ask_vol
        if total_vol == 0:
            return 0.0
        return (bid_vol - ask_vol) / total_vol

    def _calculate_price_impact(self, order_book: OrderBook) -> float:
        """Calculate price impact of trades."""
        if not order_book.bids or not order_book.asks:
            return 0.0

        # Calculate price impact for different trade sizes
        trade_sizes = [1.0, 5.0, 10.0, 50.0]  # Reference trade sizes
        price_impacts = []

        best_bid = order_book.bids[0][0]
        best_ask = order_book.asks[0][0]
        mid_price = (best_bid + best_ask) / 2

        for size in trade_sizes:
            # Calculate price impact for buy trade
            remaining_size = size
            total_cost = 0.0

            for price, qty in order_book.asks:
                if remaining_size <= 0:
                    break
                fill_qty = min(qty, remaining_size)
                total_cost += fill_qty * price
                remaining_size -= fill_qty

            if size > 0 and total_cost > 0:
                avg_price = total_cost / min(size, sum(qty for _, qty in order_book.asks))
                impact = (avg_price - mid_price) / mid_price if mid_price > 0 else 0
                price_impacts.append(impact)

        return np.mean(price_impacts) if price_impacts else 0.0

    def _calculate_volatility_index(self, historical_order_books: List[OrderBook]) -> float:
        """Calculate volatility index from historical order books."""
        if len(historical_order_books) < 10:
            return 0.0

        # Calculate price changes
        mid_prices = []
        for ob in historical_order_books:
            if ob.bids and ob.asks:
                mid = (ob.bids[0][0] + ob.asks[0][0]) / 2
                mid_prices.append(mid)

        if len(mid_prices) < 2:
            return 0.0

        # Calculate price changes
        price_changes = [
            (
                abs(mid_prices[i] - mid_prices[i - 1]) / mid_prices[i - 1]
                if mid_prices[i - 1] > 0
                else 0
            )
            for i in range(1, len(mid_prices))
        ]

        # Volatility index as average relative price change
        return np.mean(price_changes) if price_changes else 0.0

    def _detect_manipulation(
        self, current_order_book: OrderBook, historical_order_books: List[OrderBook]
    ) -> List[str]:
        """Detect potential order book manipulation indicators."""
        indicators = []

        if not current_order_book.bids or not current_order_book.asks:
            return indicators

        # Check for spoofing (large orders with no intention to execute)
        large_bid_threshold = 10.0  # 10x average
        large_ask_threshold = 10.0

        avg_bid_size = (
            np.mean([qty for _, qty in current_order_book.bids]) if current_order_book.bids else 0
        )
        avg_ask_size = (
            np.mean([qty for _, qty in current_order_book.asks]) if current_order_book.asks else 0
        )

        if avg_bid_size > 0:
            max_bid_size = max(qty for _, qty in current_order_book.bids)
            if max_bid_size > large_bid_threshold * avg_bid_size:
                indicators.append("potential_bid_spoofing")

        if avg_ask_size > 0:
            max_ask_size = max(qty for _, qty in current_order_book.asks)
            if max_ask_size > large_ask_threshold * avg_ask_size:
                indicators.append("potential_ask_spoofing")

        # Check for layering (multiple large orders at different price levels)
        large_orders = [
            qty
            for _, qty in current_order_book.bids + current_order_book.asks
            if qty > avg_bid_size * 3
        ]
        if len(large_orders) > 5:
            indicators.append("potential_layering")

        # Check for sudden liquidity changes
        if len(historical_order_books) >= 5:
            recent_volumes = []
            for ob in historical_order_books[-5:]:
                if ob.bids and ob.asks:
                    vol = sum(qty for _, qty in ob.bids) + sum(qty for _, qty in ob.asks)
                    recent_volumes.append(vol)

            if recent_volumes:
                current_vol = sum(qty for _, qty in current_order_book.bids) + sum(
                    qty for _, qty in current_order_book.asks
                )
                avg_recent_vol = np.mean(recent_volumes)

                if current_vol < avg_recent_vol * 0.3:
                    indicators.append("sudden_liquidity_drain")
                elif current_vol > avg_recent_vol * 3.0:
                    indicators.append("sudden_liquidity_injection")

        return indicators

    def _determine_trend_and_momentum(
        self, historical_order_books: List[OrderBook]
    ) -> Tuple[str, float]:
        """Determine price trend and momentum."""
        if len(historical_order_books) < 5:
            return "neutral", 0.0

        # Calculate mid prices
        mid_prices = []
        for ob in historical_order_books:
            if ob.bids and ob.asks:
                mid = (ob.bids[0][0] + ob.asks[0][0]) / 2
                mid_prices.append(mid)

        if len(mid_prices) < 3:
            return "neutral", 0.0

        # Calculate trend using linear regression
        x = np.arange(len(mid_prices))
        y = np.array(mid_prices)
        slope = np.polyfit(x, y, 1)[0]

        # Normalize slope by average price
        avg_price = np.mean(mid_prices)
        normalized_slope = slope / avg_price if avg_price > 0 else 0

        # Determine trend direction
        if normalized_slope > 0.01:
            trend = "strong_up"
        elif normalized_slope > 0.005:
            trend = "up"
        elif normalized_slope < -0.01:
            trend = "strong_down"
        elif normalized_slope < -0.005:
            trend = "down"
        else:
            trend = "neutral"

        # Calculate momentum (rate of change)
        if len(mid_prices) >= 2:
            momentum = (mid_prices[-1] - mid_prices[0]) / mid_prices[0] if mid_prices[0] > 0 else 0
        else:
            momentum = 0.0

        return trend, momentum


class PlatformHealthMonitor:
    """Platform health monitoring and anomaly detection."""

    def assess_health(
        self, platform: str, mechanics: PlatformMechanics, recent_anomalies: List[PlatformAnomaly]
    ) -> Dict[str, Any]:
        """Comprehensive platform health assessment."""
        # Calculate health score
        health_score = self._calculate_health_score(mechanics, recent_anomalies)

        # Categorize health status
        health_status = self._categorize_health(health_score)

        # Identify risk factors
        risk_factors = self._identify_risk_factors(mechanics, recent_anomalies)

        return {
            "platform": platform,
            "health_score": health_score,
            "health_status": health_status,
            "risk_factors": risk_factors,
            "recent_anomaly_count": len(recent_anomalies),
            "latency_metrics": mechanics.latency_profile,
            "recommendation": self._generate_recommendation(health_status, risk_factors),
        }

    def detect_anomalies(
        self,
        platform: str,
        current_metrics: Dict[str, float],
        mechanics: Optional[PlatformMechanics],
    ) -> List[PlatformAnomaly]:
        """Detect platform anomalies from current metrics."""
        anomalies = []

        if not mechanics:
            return anomalies

        # Check for latency anomalies
        current_latency = current_metrics.get(
            "latency", mechanics.latency_profile.get("execution", 1.0)
        )
        expected_latency = mechanics.latency_profile.get("execution", 1.0)

        if current_latency > expected_latency * 3.0:
            anomalies.append(
                PlatformAnomaly(
                    anomaly_id=f"latency_{int(time.time())}",
                    platform=platform,
                    anomaly_type="latency_spike",
                    severity="high" if current_latency > expected_latency * 5.0 else "medium",
                    timestamp=time.time(),
                    description=f"Latency spike detected: {current_latency:.2f}s vs expected {expected_latency:.2f}s",
                    metrics={
                        "current_latency": current_latency,
                        "expected_latency": expected_latency,
                    },
                    recommended_action=(
                        "reduce_trading_activity"
                        if current_latency > expected_latency * 5.0
                        else "monitor_closely"
                    ),
                )
            )

        # Check for liquidity anomalies
        liquidity_metrics = current_metrics.get("liquidity", {})
        current_depth = liquidity_metrics.get("order_book_depth", 0)

        if current_depth < mechanics.limits.get("min_depth", 10):
            anomalies.append(
                PlatformAnomaly(
                    anomaly_id=f"liquidity_{int(time.time())}",
                    platform=platform,
                    anomaly_type="liquidity_drain",
                    severity=(
                        "high"
                        if current_depth < mechanics.limits.get("min_depth", 10) * 0.5
                        else "medium"
                    ),
                    timestamp=time.time(),
                    description=f"Liquidity drain detected: depth {current_depth} below minimum {mechanics.limits.get('min_depth', 10)}",
                    metrics={
                        "current_depth": current_depth,
                        "minimum_depth": mechanics.limits.get("min_depth", 10),
                    },
                    recommended_action="reduce_position_sizes",
                )
            )

        # Check for freeze conditions
        freeze_indicators = current_metrics.get("freeze_indicators", 0)
        if freeze_indicators > 3:
            anomalies.append(
                PlatformAnomaly(
                    anomaly_id=f"freeze_{int(time.time())}",
                    platform=platform,
                    anomaly_type="freeze",
                    severity="critical" if freeze_indicators > 5 else "high",
                    timestamp=time.time(),
                    description=f"Platform freeze indicators: {freeze_indicators}",
                    metrics={"freeze_indicators": freeze_indicators},
                    recommended_action="halt_trading_immediately",
                )
            )

        return anomalies

    def _calculate_health_score(
        self, mechanics: PlatformMechanics, recent_anomalies: List[PlatformAnomaly]
    ) -> float:
        """Calculate overall platform health score."""
        base_score = 1.0

        # Penalize based on anomalies
        for anomaly in recent_anomalies:
            severity_multipliers = {"low": 0.05, "medium": 0.15, "high": 0.30, "critical": 0.50}
            penalty = severity_multipliers.get(anomaly.severity, 0.15)
            base_score -= penalty

        # Reward for low latency
        execution_latency = mechanics.latency_profile.get("execution", 1.0)
        if execution_latency < 0.1:  # Very fast
            base_score += 0.1
        elif execution_latency < 0.5:  # Fast
            base_score += 0.05

        return max(0.0, min(1.0, base_score))

    def _categorize_health(self, health_score: float) -> str:
        """Categorize health score into status."""
        if health_score > 0.9:
            return "excellent"
        elif health_score > 0.75:
            return "good"
        elif health_score > 0.5:
            return "fair"
        elif health_score > 0.25:
            return "poor"
        else:
            return "critical"

    def _identify_risk_factors(
        self, mechanics: PlatformMechanics, recent_anomalies: List[PlatformAnomaly]
    ) -> List[str]:
        """Identify risk factors for the platform."""
        risk_factors = []

        # Latency risk
        execution_latency = mechanics.latency_profile.get("execution", 1.0)
        if execution_latency > 1.0:
            risk_factors.append("high_latency")

        # Fee risk
        maker_fee = mechanics.fee_structure.get("maker", 0)
        taker_fee = mechanics.fee_structure.get("taker", 0)
        if maker_fee > 0.002 or taker_fee > 0.002:  # More than 0.2%
            risk_factors.append("high_fees")

        # Anomaly-based risk
        anomaly_types = [a.anomaly_type for a in recent_anomalies]
        if "latency_spike" in anomaly_types:
            risk_factors.append("latency_instability")
        if "liquidity_drain" in anomaly_types:
            risk_factors.append("liquidity_instability")
        if "freeze" in anomaly_types:
            risk_factors.append("platform_instability")

        return risk_factors

    def _generate_recommendation(self, health_status: str, risk_factors: List[str]) -> str:
        """Generate recommendation based on health assessment."""
        if health_status == "critical":
            return "immediately_halt_all_trading"
        elif health_status == "poor":
            return "significantly_reduce_exposure"
        elif health_status == "fair":
            return "reduce_exposure_and_monitor"
        elif health_status == "good":
            return "normal_trading_with_monitoring"
        else:  # excellent
            return "full_trading_operations"


class ArbitrageDetector:
    """Cross-platform arbitrage opportunity detection."""

    def detect_opportunities(
        self, symbol: str, current_prices: Dict[str, float], mechanics: Dict[str, PlatformMechanics]
    ) -> List[ArbitrageOpportunity]:
        """Detect arbitrage opportunities across platforms."""
        if len(current_prices) < 2:
            return []

        opportunities = []

        # Find best buy and sell prices
        best_buy_platform = min(
            current_prices.items(), key=lambda x: x[1]
        )  # Lowest price for buying
        best_sell_platform = max(
            current_prices.items(), key=lambda x: x[1]
        )  # Highest price for selling

        buy_platform, buy_price = best_buy_platform
        sell_platform, sell_price = best_sell_platform

        # Calculate price difference
        price_diff = sell_price - buy_price
        price_diff_pct = price_diff / buy_price if buy_price > 0 else 0

        # Check if arbitrage is profitable after fees
        if price_diff_pct > 0.01:  # More than 1% difference
            # Calculate fees
            buy_mechanics = mechanics.get(buy_platform)
            sell_mechanics = mechanics.get(sell_platform)

            if buy_mechanics and sell_mechanics:
                buy_fee = buy_mechanics.fee_structure.get("taker", 0.002)
                sell_fee = sell_mechanics.fee_structure.get("taker", 0.002)
                total_fee_rate = buy_fee + sell_fee

                # Calculate estimated profit
                gross_profit_pct = price_diff_pct
                net_profit_pct = gross_profit_pct - total_fee_rate

                if net_profit_pct > 0.005:  # More than 0.5% net profit
                    # Estimate execution window based on latencies
                    buy_latency = buy_mechanics.latency_profile.get("execution", 0.5)
                    sell_latency = sell_mechanics.latency_profile.get("execution", 0.5)
                    execution_window = (
                        max(buy_latency, sell_latency) * 2 + 1.0
                    )  # Add 1 second buffer

                    # Assess risk level
                    risk_level = self._assess_arbitrage_risk(
                        buy_mechanics, sell_mechanics, price_diff_pct
                    )

                    opportunity = ArbitrageOpportunity(
                        opportunity_id=f"arb_{int(time.time())}_{hash(symbol + buy_platform + sell_platform) % 10000}",
                        symbol=symbol,
                        platforms=[buy_platform, sell_platform],
                        price_diff=price_diff,
                        price_diff_pct=price_diff_pct,
                        estimated_profit=net_profit_pct,
                        risk_level=risk_level,
                        timestamp=time.time(),
                        execution_window=execution_window,
                    )
                    opportunities.append(opportunity)

        # Also check for triangular arbitrage opportunities (3+ platforms)
        if len(current_prices) >= 3:
            triangular_opportunities = self._detect_triangular_arbitrage(
                symbol, current_prices, mechanics
            )
            opportunities.extend(triangular_opportunities)

        return opportunities

    def _detect_triangular_arbitrage(
        self, symbol: str, prices: Dict[str, float], mechanics: Dict[str, PlatformMechanics]
    ) -> List[ArbitrageOpportunity]:
        """Detect triangular arbitrage opportunities."""
        opportunities = []

        # This is a simplified triangular arbitrage detection
        # In production, would need more sophisticated logic
        platforms = list(prices.keys())

        for i in range(len(platforms)):
            for j in range(len(platforms)):
                for k in range(len(platforms)):
                    if i != j and j != k and i != k:
                        # Check for arbitrage path
                        p1 = prices[platforms[i]]
                        p2 = prices[platforms[j]]
                        p3 = prices[platforms[k]]

                        # Simplified check
                        if (p3 / p2 * p1 / p3 - 1.0) > 0.01:  # More than 1% profit potential
                            opportunity = ArbitrageOpportunity(
                                opportunity_id=f"tri_arb_{int(time.time())}_{hash(platforms[i] + platforms[j] + platforms[k]) % 10000}",
                                symbol=symbol,
                                platforms=[platforms[i], platforms[j], platforms[k]],
                                price_diff=0.0,
                                price_diff_pct=(p3 / p2 * p1 / p3 - 1.0),
                                estimated_profit=0.01,  # Simplified
                                risk_level="high",  # Triangular arbitrage is higher risk
                                timestamp=time.time(),
                                execution_window=5.0,  # Shorter window for triangular arbitrage
                            )
                            opportunities.append(opportunity)

        return opportunities

    def _assess_arbitrage_risk(
        self,
        buy_mechanics: PlatformMechanics,
        sell_mechanics: PlatformMechanics,
        price_diff_pct: float,
    ) -> str:
        """Assess risk level of arbitrage opportunity."""
        risk_score = 0.0

        # Latency risk
        buy_latency = buy_mechanics.latency_profile.get("execution", 0.5)
        sell_latency = sell_mechanics.latency_profile.get("execution", 0.5)
        total_latency = buy_latency + sell_latency
        risk_score += total_latency * 0.1

        # Fee risk
        buy_fee = buy_mechanics.fee_structure.get("taker", 0.002)
        sell_fee = sell_mechanics.fee_structure.get("taker", 0.002)
        total_fee = buy_fee + sell_fee
        risk_score += total_fee * 5.0

        # Price difference risk (smaller differences are riskier)
        if price_diff_pct < 0.02:
            risk_score += 0.3
        elif price_diff_pct < 0.05:
            risk_score += 0.1

        # Categorize risk
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.6:
            return "medium"
        else:
            return "high"


# Singleton instance
_platform_understanding: Optional[PlatformUnderstanding] = None
_platform_understanding_lock = threading.Lock()


def get_platform_understanding(history_window: int = 1000) -> PlatformUnderstanding:
    """Get the singleton platform understanding instance."""
    global _platform_understanding
    if _platform_understanding is None:
        with _platform_understanding_lock:
            if _platform_understanding is None:
                _platform_understanding = PlatformUnderstanding(history_window)
    return _platform_understanding


__all__ = [
    "PlatformUnderstanding",
    "get_platform_understanding",
    "PlatformType",
    "OrderBookState",
    "PlatformMechanics",
    "OrderBook",
    "OrderBookDynamics",
    "PlatformAnomaly",
    "ArbitrageOpportunity",
]
