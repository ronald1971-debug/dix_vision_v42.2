"""
Execution Unified Slippage - Slippage Calculation Infrastructure
Provides slippage calculation and protection capabilities
NO LAZY LOADING - All components load directly
"""

import asyncio
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SlippageModel(Enum):
    """Slippage model type"""

    LINEAR = "linear"
    SQUARE_ROOT = "square_root"
    POWER = "power"
    LOGARITHMIC = "logarithmic"
    CUSTOM = "custom"


class SlippageDirection(Enum):
    """Slippage direction"""

    POSITIVE = "positive"  # Unfavorable for trader
    NEGATIVE = "negative"  # Favorable for trader
    NEUTRAL = "neutral"


@dataclass
class SlippageConfig:
    """Slippage configuration"""

    model: SlippageModel = SlippageModel.SQUARE_ROOT
    base_slippage_bps: float = 5.0  # 5 basis points
    max_slippage_bps: float = 50.0  # 50 basis points max
    slippage_tolerance_bps: float = 20.0  # 20 basis points tolerance
    enable_slippage_protection: bool = True
    enable_mev_protection: bool = True
    volume_impact_factor: float = 0.1
    liquidity_factor: float = 0.05


@dataclass
class SlippageMetrics:
    """Slippage performance metrics"""

    total_trades: int = 0
    average_slippage_bps: float = 0.0
    max_slippage_bps: float = 0.0
    min_slippage_bps: float = 0.0
    total_slippage_cost: float = 0.0
    mev_blocks_avoided: int = 0
    last_calculation_ns: int = 0

    def __post_init__(self):
        if self.last_calculation_ns == 0:
            self.last_calculation_ns = datetime.now().timestamp_ns()


@dataclass
class SlippageEstimate:
    """Slippage estimation result"""

    estimated_slippage_bps: float
    confidence_level: float
    slippage_direction: SlippageDirection
    execution_price_estimate: float
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)


class SlippageCalculator:
    """
    Slippage Calculator - Core slippage calculation infrastructure

    Provides slippage estimation, calculation, and protection capabilities
    Required by archival components for slippage operations
    """

    def __init__(self, config: Optional[SlippageConfig] = None):
        self._config = config or SlippageConfig()
        self._metrics = SlippageMetrics()
        self._liquidity_data: Dict[str, Dict[str, Any]] = {}
        self._historical_slippage: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()

    async def estimate_slippage(
        self,
        symbol: str,
        order_side: str,
        quantity: float,
        current_price: float,
        market_depth: Optional[Dict[str, Any]] = None,
    ) -> SlippageEstimate:
        """Estimate slippage for an order"""
        # Get liquidity data
        liquidity = await self._get_liquidity_data(symbol, market_depth)

        # Calculate slippage based on model
        slippage_bps = await self._calculate_slippage(
            symbol, order_side, quantity, current_price, liquidity
        )

        # Determine direction
        direction = self._determine_direction(order_side, slippage_bps)

        # Calculate execution price estimate
        price_impact = (slippage_bps / 10000) * current_price
        execution_price = (
            current_price + price_impact
            if direction == SlippageDirection.POSITIVE
            else current_price - price_impact
        )

        # Determine confidence level
        confidence = await self._calculate_confidence(symbol, liquidity)

        # Risk factors
        risk_factors = await self._assess_risk_factors(symbol, quantity, liquidity)

        # Mitigation strategies
        mitigation = await self._suggest_mitigation_strategies(slippage_bps, risk_factors)

        estimate = SlippageEstimate(
            estimated_slippage_bps=slippage_bps,
            confidence_level=confidence,
            slippage_direction=direction,
            execution_price_estimate=execution_price,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation,
        )

        return estimate

    async def calculate_actual_slippage(
        self, symbol: str, expected_price: float, execution_price: float
    ) -> float:
        """Calculate actual slippage from execution"""
        if expected_price == 0:
            return 0.0

        price_diff = execution_price - expected_price
        slippage_bps = (price_diff / expected_price) * 10000

        # Update metrics
        async with self._lock:
            self._metrics.total_trades += 1

            # Update average
            if self._metrics.total_trades == 1:
                self._metrics.average_slippage_bps = abs(slippage_bps)
            else:
                self._metrics.average_slippage_bps = (
                    self._metrics.average_slippage_bps * (self._metrics.total_trades - 1)
                    + abs(slippage_bps)
                ) / self._metrics.total_trades

            # Update max/min
            self._metrics.max_slippage_bps = max(self._metrics.max_slippage_bps, abs(slippage_bps))
            self._metrics.min_slippage_bps = (
                min(self._metrics.min_slippage_bps, abs(slippage_bps))
                if self._metrics.min_slippage_bps > 0
                else abs(slippage_bps)
            )

            self._metrics.total_slippage_cost += abs(price_diff)
            self._metrics.last_calculation_ns = datetime.now().timestamp_ns()

        # Store historical data
        if symbol not in self._historical_slippage:
            self._historical_slippage[symbol] = []
        self._historical_slippage[symbol].append(abs(slippage_bps))

        # Keep only last 100 data points
        if len(self._historical_slippage[symbol]) > 100:
            self._historical_slippage[symbol] = self._historical_slippage[symbol][-100:]

        logger.info(f"Calculated slippage for {symbol}: {slippage_bps:.2f} bps")

        return slippage_bps

    async def check_slippage_protection(self, symbol: str, estimated_slippage_bps: float) -> bool:
        """Check if slippage exceeds protection threshold"""
        if not self._config.enable_slippage_protection:
            return True

        if estimated_slippage_bps > self._config.max_slippage_bps:
            logger.warning(
                f"Estimated slippage {estimated_slippage_bps:.2f} bps exceeds max {self._config.max_slippage_bps:.2f} bps"
            )
            return False

        return True

    async def update_liquidity_data(self, symbol: str, liquidity_data: Dict[str, Any]):
        """Update liquidity data for a symbol"""
        async with self._lock:
            self._liquidity_data[symbol] = liquidity_data
            liquidity_data["last_updated"] = datetime.now().timestamp_ns()

        logger.debug(f"Updated liquidity data for {symbol}")

    async def get_metrics(self) -> SlippageMetrics:
        """Get slippage metrics"""
        return self._metrics

    async def _get_liquidity_data(
        self, symbol: str, market_depth: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get liquidity data for a symbol"""
        if market_depth:
            return market_depth

        async with self._lock:
            return self._liquidity_data.get(symbol, {"liquidity_score": 0.5})

    async def _calculate_slippage(
        self,
        symbol: str,
        order_side: str,
        quantity: float,
        current_price: float,
        liquidity: Dict[str, Any],
    ) -> float:
        """Calculate slippage based on model"""
        model = self._config.model
        base_slippage = self._config.base_slippage_bps

        liquidity_score = liquidity.get("liquidity_score", 0.5)
        volume_impact = self._config.volume_impact_factor * (quantity / current_price)

        if model == SlippageModel.LINEAR:
            slippage = base_slippage * (1 + volume_impact) / liquidity_score

        elif model == SlippageModel.SQUARE_ROOT:
            slippage = base_slippage * math.sqrt(1 + volume_impact) / liquidity_score

        elif model == SlippageModel.POWER:
            slippage = base_slippage * math.pow(1 + volume_impact, 0.8) / liquidity_score

        elif model == SlippageModel.LOGARITHMIC:
            slippage = base_slippage * math.log(1 + volume_impact + 1) / liquidity_score

        else:  # CUSTOM or default
            slippage = base_slippage * (1 + volume_impact) / liquidity_score

        return min(slippage, self._config.max_slippage_bps)

    def _determine_direction(self, order_side: str, slippage_bps: float) -> SlippageDirection:
        """Determine slippage direction"""
        if slippage_bps == 0:
            return SlippageDirection.NEUTRAL

        # For buys, positive slippage is unfavorable (higher price)
        # For sells, negative slippage is unfavorable (lower price)
        if order_side.lower() == "buy":
            return SlippageDirection.POSITIVE if slippage_bps > 0 else SlippageDirection.NEGATIVE
        else:
            return SlippageDirection.POSITIVE if slippage_bps < 0 else SlippageDirection.NEGATIVE

    async def _calculate_confidence(self, symbol: str, liquidity: Dict[str, Any]) -> float:
        """Calculate confidence level for slippage estimate"""
        historical_data = self._historical_slippage.get(symbol, [])

        if len(historical_data) < 5:
            return 0.5  # Low confidence with limited historical data

        # Calculate variance
        variance = sum(
            (x - sum(historical_data) / len(historical_data)) ** 2 for x in historical_data
        ) / len(historical_data)

        # Higher variance = lower confidence
        confidence = max(0.1, min(0.9, 1.0 - (variance / 100.0)))

        # Adjust by liquidity quality
        liquidity_score = liquidity.get("liquidity_score", 0.5)
        confidence *= liquidity_score

        return confidence

    async def _assess_risk_factors(
        self, symbol: str, quantity: float, liquidity: Dict[str, Any]
    ) -> List[str]:
        """Assess risk factors for slippage"""
        risk_factors = []

        liquidity_score = liquidity.get("liquidity_score", 0.5)
        if liquidity_score < 0.3:
            risk_factors.append("low_liquidity")

        # Check order size
        avg_volume = liquidity.get("average_volume", 1000000.0)
        if quantity > avg_volume * 0.01:  # >1% of average volume
            risk_factors.append("large_order_size")

        # Check volatility
        volatility = liquidity.get("volatility", 0.02)
        if volatility > 0.05:  # >5% daily volatility
            risk_factors.append("high_volatility")

        return risk_factors

    async def _suggest_mitigation_strategies(
        self, slippage_bps: float, risk_factors: List[str]
    ) -> List[str]:
        """Suggest strategies to mitigate slippage"""
        strategies = []

        if slippage_bps > self._config.slippage_tolerance_bps:
            strategies.append("split_order_into_smaller_parts")
            strategies.append("use_limit_orders_instead_of_market")
            strategies.append("execute_over_longer_time_period")

        if "low_liquidity" in risk_factors:
            strategies.append("use_iceberg_orders")
            strategies.append("consider_alternative_venues")

        if "high_volatility" in risk_factors:
            strategies.append("use_volatility_adjusted_pricing")
            strategies.append("implement_dynamic_time_horizon")

        return strategies


# Global slippage calculator instance
_slippage_calculator = None


def get_slippage_calculator() -> SlippageCalculator:
    """Get global slippage calculator instance"""
    global _slippage_calculator
    if _slippage_calculator is None:
        _slippage_calculator = SlippageCalculator()
    return _slippage_calculator


__all__ = [
    "SlippageModel",
    "SlippageDirection",
    "SlippageConfig",
    "SlippageMetrics",
    "SlippageEstimate",
    "SlippageCalculator",
    "get_slippage_calculator",
]
