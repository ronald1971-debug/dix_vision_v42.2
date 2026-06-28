"""EXEC-01 — Advanced execution intelligence for optimal trade execution.

Enhances INDIRA's execution capabilities with optimal execution planning,
market impact modeling, and advanced execution algorithms to minimize
slippage and maximize execution quality.

Pure computation. No clocks, no I/O. INV-15 deterministic.
B1: No imports from execution_engine/governance_engine/learning_engine/evolution_engine.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ExecutionAlgorithm(Enum):
    """Types of execution algorithms."""

    VWAP = "vwap"  # Volume-weighted average price
    TWAP = "twap"  # Time-weighted average price
    POV = "pov"  # Percentage of volume
    IMPLEMENTATION_SHORTFALL = "implementation_shortfall"  # Optimized execution
    MARKET_IMPACT_MINIMIZATION = "market_impact_minimization"  # Impact-aware
    ADAPTIVE = "adaptive"  # Dynamic algorithm selection


class LiquidityProfile(Enum):
    """Liquidity profile of the market."""

    HIGH = "high"  # Deep liquidity, easy execution
    MEDIUM = "medium"  # Moderate liquidity
    LOW = "low"  # Thin liquidity, careful execution required
    FRAGMENTED = "fragmented"  # Liquidity scattered across venues


@dataclass(frozen=True, slots=True)
class MarketImpactModel:
    """Model for predicting market impact of trades."""

    symbol: str
    temporary_impact_coefficient: float  # Short-term price impact
    permanent_impact_coefficient: float  # Long-term price impact
    liquidity_factor: float  # Market liquidity adjustment
    volatility_sensitivity: float  # Impact sensitivity to volatility
    time_decay: float  # How impact decays over time
    avg_daily_volume: float
    avg_spread: float


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """Optimal execution plan for a trade."""

    plan_id: str
    symbol: str
    side: str  # "buy" or "sell"
    total_quantity: float
    algorithm: ExecutionAlgorithm
    schedule: tuple[tuple[int, float], ...]  # (time_bar, quantity) pairs
    expected_market_impact: float
    expected_slippage: float
    execution_quality_score: float  # 0.0 to 1.0
    risk_adjusted_return: float
    estimated_completion_bars: int
    alternative_plans: tuple[str, ...]  # IDs of alternative plans
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class VenueAnalysis:
    """Analysis of execution venues for optimal routing."""

    venue_id: str
    venue_type: str  # "exchange", "dark_pool", "ecm", "internal"
    liquidity_score: float
    cost_estimate: float  # Estimated cost per unit
    speed_estimate: float  # Expected execution speed (bars)
    reliability_score: float
    optimal_for: tuple[str, ...]  # Order types this venue is optimal for


@dataclass(frozen=True, slots=True)
class ExecutionOptimizationResult:
    """Result of execution optimization."""

    optimal_algorithm: ExecutionAlgorithm
    optimal_venues: tuple[VenueAnalysis, ...]
    optimal_schedule: tuple[tuple[int, float], ...]
    expected_cost_benefit: float  # Improvement over naive execution
    confidence: float
    reasoning: tuple[str, ...]
    risk_factors: tuple[str, ...]
    timestamp_ns: int


class MarketImpactEstimator:
    """Estimates market impact of trades using structural models.

    Models both temporary impact (short-term price pressure) and
    permanent impact (long-term price effects) to optimize execution.
    """

    def __init__(self) -> None:
        self._impact_models: dict[str, MarketImpactModel] = {}
        self._impact_history: deque[dict[str, Any]] = deque(maxlen=100)

    def calibrate_model(
        self, symbol: str, historical_trades: list[dict[str, Any]]
    ) -> MarketImpactModel:
        """Calibrate market impact model for a symbol.

        Args:
            symbol: Trading symbol
            historical_trades: Historical trade data for calibration

        Returns:
            Calibrated market impact model
        """
        # Simplified calibration - in production would use regression
        # on actual execution data

        avg_volume = (
            sum(t.get("volume", 0) for t in historical_trades[-50:]) / 50
            if historical_trades
            else 1000000.0
        )
        avg_spread = (
            sum(t.get("spread", 0.001) for t in historical_trades[-50:]) / 50
            if historical_trades
            else 0.001
        )

        # Model parameters (simplified)
        temp_impact = 0.1 / math.sqrt(avg_volume / 1000000) if avg_volume > 0 else 0.1
        perm_impact = 0.05 / math.sqrt(avg_volume / 1000000) if avg_volume > 0 else 0.05
        liquidity_factor = min(1.0, avg_volume / 5000000)  # Normalized liquidity
        vol_sensitivity = 0.5  # Moderate sensitivity to volatility
        time_decay = 0.2  # Impact decays over time

        model = MarketImpactModel(
            symbol=symbol,
            temporary_impact_coefficient=temp_impact,
            permanent_impact_coefficient=perm_impact,
            liquidity_factor=liquidity_factor,
            volatility_sensitivity=vol_sensitivity,
            time_decay=time_decay,
            avg_daily_volume=avg_volume,
            avg_spread=avg_spread,
        )

        self._impact_models[symbol] = model

        return model

    def estimate_impact(
        self,
        symbol: str,
        quantity: float,
        execution_time_bars: int,
        current_volatility: float = 1.0,
    ) -> dict[str, float]:
        """Estimate market impact for a trade.

        Args:
            symbol: Trading symbol
            quantity: Trade quantity
            execution_time_bars: Time available for execution
            current_volatility: Current market volatility

        Returns:
            Dictionary with impact estimates
        """
        if symbol not in self._impact_models:
            # Use default model
            model = MarketImpactModel(
                symbol=symbol,
                temporary_impact_coefficient=0.1,
                permanent_impact_coefficient=0.05,
                liquidity_factor=0.5,
                volatility_sensitivity=0.5,
                time_decay=0.2,
                avg_daily_volume=1000000.0,
                avg_spread=0.001,
            )
        else:
            model = self._impact_models[symbol]

        # Normalize quantity by average daily volume
        normalized_quantity = (
            quantity / model.avg_daily_volume if model.avg_daily_volume > 0 else 0.0
        )

        # Calculate temporary impact (decays with execution time)
        time_factor = math.exp(-model.time_decay * execution_time_bars / 10)
        temp_impact = (
            model.temporary_impact_coefficient
            * normalized_quantity
            * (1 + model.volatility_sensitivity * (current_volatility - 1.0))
            * time_factor
        )

        # Calculate permanent impact (independent of execution time)
        perm_impact = (
            model.permanent_impact_coefficient
            * normalized_quantity
            * model.liquidity_factor
            * (1 + model.volatility_sensitivity * (current_volatility - 1.0))
        )

        # Total impact
        total_impact = temp_impact + perm_impact

        # Estimate slippage (spread component)
        spread_impact = model.avg_spread * (1 + (current_volatility - 1.0) * 0.5)

        return {
            "temporary_impact": temp_impact,
            "permanent_impact": perm_impact,
            "total_impact": total_impact,
            "spread_impact": spread_impact,
            "total_cost": total_impact + spread_impact,
            "execution_time_adjustment": time_factor,
        }


class OptimalExecutionPlanner:
    """Plans optimal execution schedules to minimize market impact.

    Uses market impact models and optimization algorithms to determine
    the best execution schedule, algorithm selection, and venue routing.
    """

    def __init__(self, default_execution_bars: int = 20, max_execution_bars: int = 100) -> None:
        self._default_execution_bars = default_execution_bars
        self._max_execution_bars = max_execution_bars

        self._impact_estimator = MarketImpactEstimator()
        self._execution_history: deque[ExecutionPlan] = deque(maxlen=50)
        self._venue_analysis: dict[str, tuple[VenueAnalysis, ...]] = {}

    def plan_execution(
        self,
        symbol: str,
        side: str,
        quantity: float,
        urgency: float = 0.5,  # 0.0 to 1.0, higher = more urgent
        market_conditions: dict[str, Any] | None = None,
        timestamp_ns: int = 0,
    ) -> ExecutionOptimizationResult:
        """Plan optimal execution for a trade.

        Args:
            symbol: Trading symbol
            side: "buy" or "sell"
            quantity: Trade quantity
            urgency: Execution urgency (0.0 to 1.0)
            market_conditions: Current market conditions
            timestamp_ns: Current timestamp

        Returns:
            Execution optimization result with optimal plan
        """
        market_conditions = market_conditions or {}

        # Estimate market impact for different execution timeframes
        execution_time_options = [
            max(5, int(self._default_execution_bars * (1.0 - urgency) * 0.5)),
            self._default_execution_bars,
            min(
                self._max_execution_bars, int(self._default_execution_bars * (1.0 + urgency) * 2.0)
            ),
        ]

        impact_estimates = {}
        for time_bars in execution_time_options:
            impact = self._impact_estimator.estimate_impact(
                symbol, quantity, time_bars, market_conditions.get("volatility", 1.0)
            )
            impact_estimates[time_bars] = impact

        # Select optimal execution time based on cost-benefit
        optimal_time = self._select_execution_time(impact_estimates, urgency)

        # Select optimal algorithm
        optimal_algorithm = self._select_algorithm(
            symbol, side, quantity, optimal_time, market_conditions
        )

        # Generate optimal schedule
        optimal_schedule = self._generate_schedule(side, quantity, optimal_time, optimal_algorithm)

        # Analyze venues
        venues = self._analyze_venues(symbol, side, quantity, market_conditions)

        # Calculate expected quality and cost-benefit
        execution_quality = self._calculate_execution_quality(
            impact_estimates[optimal_time], optimal_schedule, venues
        )

        cost_benefit = self._calculate_cost_benefit(
            impact_estimates, optimal_time, execution_quality
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            optimal_algorithm, optimal_time, impact_estimates, market_conditions
        )

        # Identify risk factors
        risk_factors = self._identify_risk_factors(
            impact_estimates[optimal_time], market_conditions, venues
        )

        return ExecutionOptimizationResult(
            optimal_algorithm=optimal_algorithm,
            optimal_venues=venues,
            optimal_schedule=optimal_schedule,
            expected_cost_benefit=cost_benefit,
            confidence=execution_quality,
            reasoning=tuple(reasoning),
            risk_factors=tuple(risk_factors),
            timestamp_ns=timestamp_ns,
        )

    def _select_execution_time(
        self, impact_estimates: dict[int, dict[str, float]], urgency: float
    ) -> int:
        """Select optimal execution time based on impact vs urgency."""
        # Balance between minimizing impact and execution urgency
        scored_options = []

        for time_bars, impact in impact_estimates.items():
            # Lower impact is better
            impact_score = 1.0 - min(impact["total_cost"], 1.0)
            # Faster execution is better for high urgency
            urgency_score = 1.0 - (time_bars / self._max_execution_bars)

            # Weighted combination
            combined_score = impact_score * (1.0 - urgency) + urgency_score * urgency
            scored_options.append((time_bars, combined_score))

        # Select time with highest combined score
        scored_options.sort(key=lambda x: x[1], reverse=True)
        return scored_options[0][0]

    def _select_algorithm(
        self,
        symbol: str,
        side: str,
        quantity: float,
        execution_time_bars: int,
        market_conditions: dict[str, Any],
    ) -> ExecutionAlgorithm:
        """Select optimal execution algorithm."""
        volatility = market_conditions.get("volatility", 1.0)
        liquidity = market_conditions.get("liquidity", "medium")

        # Algorithm selection logic
        if volatility > 1.5:
            # High volatility - use adaptive algorithms
            return ExecutionAlgorithm.ADAPTIVE
        elif liquidity == "low":
            # Low liquidity - use POV to avoid impact
            return ExecutionAlgorithm.POV
        elif execution_time_bars < 10:
            # Urgent execution - use implementation shortfall
            return ExecutionAlgorithm.IMPLEMENTATION_SHORTFALL
        elif quantity > 1000000:  # Large order
            # Large order - use market impact minimization
            return ExecutionAlgorithm.MARKET_IMPACT_MINIMIZATION
        else:
            # Standard case - use TWAP
            return ExecutionAlgorithm.TWAP

    def _generate_schedule(
        self, side: str, quantity: float, execution_time_bars: int, algorithm: ExecutionAlgorithm
    ) -> tuple[tuple[int, float], ...]:
        """Generate execution schedule based on algorithm."""
        schedule = []

        if algorithm == ExecutionAlgorithm.TWAP:
            # Time-weighted average - equal slices
            slice_size = quantity / execution_time_bars
            for bar in range(execution_time_bars):
                schedule.append((bar, slice_size))

        elif algorithm == ExecutionAlgorithm.VWAP:
            # Volume-weighted - would use predicted volume profile
            # Simplified: assume higher volume in middle of day
            volume_profile = [0.8, 0.9, 1.0, 1.1, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7]
            # Extend or contract profile to match execution_time_bars
            normalized_profile = []
            for i in range(execution_time_bars):
                profile_idx = int((i / execution_time_bars) * len(volume_profile))
                profile_idx = min(profile_idx, len(volume_profile) - 1)
                normalized_profile.append(volume_profile[profile_idx])

            total_profile = sum(normalized_profile)
            for bar, weight in enumerate(normalized_profile):
                slice_size = (weight / total_profile) * quantity
                schedule.append((bar, slice_size))

        elif algorithm == ExecutionAlgorithm.POV:
            # Percentage of volume - assume 20% participation rate
            participation_rate = 0.2
            slice_size = quantity / execution_time_bars  # Simplified
            for bar in range(execution_time_bars):
                schedule.append((bar, slice_size))

        else:
            # Default to TWAP for other algorithms
            slice_size = quantity / execution_time_bars
            for bar in range(execution_time_bars):
                schedule.append((bar, slice_size))

        return tuple(schedule)

    def _analyze_venues(
        self, symbol: str, side: str, quantity: float, market_conditions: dict[str, Any]
    ) -> tuple[VenueAnalysis, ...]:
        """Analyze execution venues for optimal routing."""
        # Simplified venue analysis - in production would query real venue data
        venues = [
            VenueAnalysis(
                venue_id="primary_exchange",
                venue_type="exchange",
                liquidity_score=0.8,
                cost_estimate=0.001,
                speed_estimate=1.0,
                reliability_score=0.95,
                optimal_for=("large_orders", "standard_execution"),
            ),
            VenueAnalysis(
                venue_id="dark_pool_1",
                venue_type="dark_pool",
                liquidity_score=0.6,
                cost_estimate=0.0005,
                speed_estimate=3.0,
                reliability_score=0.85,
                optimal_for=("large_orders", "minimal_impact"),
            ),
            VenueAnalysis(
                venue_id="ecm_1",
                venue_type="ecm",
                liquidity_score=0.7,
                cost_estimate=0.0008,
                speed_estimate=2.0,
                reliability_score=0.9,
                optimal_for=("medium_orders", "speed"),
            ),
        ]

        return tuple(venues)

    def _calculate_execution_quality(
        self,
        impact_estimate: dict[str, float],
        schedule: tuple[tuple[int, float], ...],
        venues: tuple[VenueAnalysis, ...],
    ) -> float:
        """Calculate overall execution quality score."""
        # Lower impact is better
        impact_score = 1.0 - min(impact_estimate["total_cost"], 1.0)

        # Smooth schedule is better
        slice_sizes = [s[1] for s in schedule]
        if len(slice_sizes) > 1:
            avg_slice = sum(slice_sizes) / len(slice_sizes)
            variance = sum((s - avg_slice) ** 2 for s in slice_sizes) / len(slice_sizes)
            smoothness_score = 1.0 - min(variance / (avg_slice**2 + 1e-12), 1.0)
        else:
            smoothness_score = 0.5

        # Venue quality
        venue_score = sum(v.liquidity_score * v.reliability_score for v in venues) / len(venues)

        # Combined score
        quality = impact_score * 0.4 + smoothness_score * 0.3 + venue_score * 0.3

        return min(1.0, max(0.0, quality))

    def _calculate_cost_benefit(
        self,
        impact_estimates: dict[int, dict[str, float]],
        optimal_time: int,
        execution_quality: float,
    ) -> float:
        """Calculate cost-benefit of optimal execution."""
        # Compare to immediate execution (1 bar)
        immediate_impact = impact_estimates.get(1, {"total_cost": 0.1})
        optimal_impact = impact_estimates.get(optimal_time, {"total_cost": 0.05})

        cost_reduction = immediate_impact["total_cost"] - optimal_impact["total_cost"]
        cost_benefit = cost_reduction * execution_quality

        return cost_benefit

    def _generate_reasoning(
        self,
        algorithm: ExecutionAlgorithm,
        execution_time: int,
        impact_estimates: dict[int, dict[str, float]],
        market_conditions: dict[str, Any],
    ) -> list[str]:
        """Generate reasoning for execution decisions."""
        reasoning = [
            f"Selected {algorithm.value} algorithm based on market conditions",
            f"Execution time: {execution_time} bars balances impact reduction with urgency",
            f"Expected total impact: {impact_estimates[execution_time]['total_cost']:.2%}",
            f"Liquidity factor: {market_conditions.get('liquidity', 'unknown')}",
        ]

        volatility = market_conditions.get("volatility", 1.0)
        if volatility > 1.2:
            reasoning.append("High volatility environment - using adaptive execution parameters")
        elif volatility < 0.8:
            reasoning.append("Low volatility environment - can use more aggressive execution")

        return reasoning

    def _identify_risk_factors(
        self,
        impact_estimate: dict[str, float],
        market_conditions: dict[str, Any],
        venues: tuple[VenueAnalysis, ...],
    ) -> list[str]:
        """Identify potential risk factors for execution."""
        risks = []

        if impact_estimate["total_cost"] > 0.05:
            risks.append("High market impact expected - consider breaking into smaller orders")

        if market_conditions.get("volatility", 1.0) > 1.5:
            risks.append("High volatility may increase slippage risk")

        liquidity = market_conditions.get("liquidity", "medium")
        if liquidity == "low":
            risks.append("Low liquidity - execution may be challenging")

        venue_risks = [v.venue_id for v in venues if v.reliability_score < 0.8]
        if venue_risks:
            risks.append(f"Some venues have lower reliability: {venue_risks}")

        return risks if risks else ["No significant risk factors identified"]


__all__ = [
    "ExecutionAlgorithm",
    "LiquidityProfile",
    "MarketImpactModel",
    "ExecutionPlan",
    "VenueAnalysis",
    "ExecutionOptimizationResult",
    "MarketImpactEstimator",
    "OptimalExecutionPlanner",
]
