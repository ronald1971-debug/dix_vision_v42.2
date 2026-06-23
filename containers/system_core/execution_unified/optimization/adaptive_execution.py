"""
execution_unified.optimization.adaptive_execution
DIX VISION v42.2 — Adaptive Execution Strategies (Priority 2)

Provides adaptive execution strategies based on conditions.
This is a Priority 2 enhancement for performance optimization.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Types of execution strategies."""

    LATENCY_OPTIMIZED = "LATENCY_OPTIMIZED"
    THROUGHPUT_OPTIMIZED = "THROUGHPUT_OPTIMIZED"
    COST_OPTIMIZED = "COST_OPTIMIZED"
    BALANCED = "BALANCED"
    CONSERVATIVE = "CONSERVATIVE"
    AGGRESSIVE = "AGGRESSIVE"


@dataclass
class ConditionAnalysis:
    """Analysis of current execution conditions."""

    market_condition: str  # VOLATILE, STABLE, TRENDING, RANGING
    system_load: str  # LOW, MEDIUM, HIGH, CRITICAL
    time_constraint: str  # STRICT, MODERATE, FLEXIBLE
    risk_tolerance: str  # LOW, MEDIUM, HIGH
    resource_availability: str  # SCARCE, ADEQUATE, ABUNDANT
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExecutionStrategy:
    """Execution strategy configuration."""

    strategy_type: StrategyType
    priority_level: int  # Higher is higher priority
    parameters: Dict[str, float] = field(default_factory=dict)
    performance_weights: Dict[str, float] = field(default_factory=dict)
    description: str = ""


@dataclass
class StrategySelection:
    """Result of strategy selection."""

    selected_strategy: ExecutionStrategy
    confidence: float = 0.0  # 0.0 to 1.0
    reasoning: str = ""
    alternative_strategies: List[ExecutionStrategy] = field(default_factory=list)


@dataclass
class StrategyPerformance:
    """Performance feedback for a strategy."""

    strategy_type: StrategyType
    execution_count: int
    success_rate: float
    average_latency_ms: float
    average_throughput: float
    cost_per_execution: float
    last_used: datetime = field(default_factory=datetime.utcnow)


class ConditionAnalyzer:
    """Analyzes current execution conditions."""

    def __init__(self):
        self._lock = threading.Lock()

        # Thresholds
        self._load_thresholds = {"LOW": 30.0, "MEDIUM": 60.0, "HIGH": 85.0, "CRITICAL": 95.0}

        logger.info("[CONDITION_ANALYZER] Initialized")

    def analyze(self, execution_context: Dict[str, Any]) -> ConditionAnalysis:
        """
        Analyze current execution conditions.

        Args:
            execution_context: Current execution context

        Returns:
            Condition analysis
        """
        with self._lock:
            # Analyze market conditions
            market_condition = self._analyze_market_condition(execution_context)

            # Analyze system load
            system_load = self._analyze_system_load(execution_context)

            # Analyze time constraints
            time_constraint = execution_context.get("time_constraint", "MODERATE")

            # Analyze risk tolerance
            risk_tolerance = execution_context.get("risk_tolerance", "MEDIUM")

            # Analyze resource availability
            resource_availability = self._analyze_resource_availability(execution_context)

            return ConditionAnalysis(
                market_condition=market_condition,
                system_load=system_load,
                time_constraint=time_constraint,
                risk_tolerance=risk_tolerance,
                resource_availability=resource_availability,
            )

    def _analyze_market_condition(self, context: Dict[str, Any]) -> str:
        """Analyze market conditions."""
        volatility = context.get("market_volatility", 0.0)
        trend = context.get("market_trend", 0.0)

        if volatility > 0.8:
            return "VOLATILE"
        elif abs(trend) > 0.5:
            return "TRENDING"
        elif volatility < 0.2:
            return "STABLE"
        else:
            return "RANGING"

    def _analyze_system_load(self, context: Dict[str, Any]) -> str:
        """Analyze system load."""
        cpu_load = context.get("cpu_usage", 0.0)

        if cpu_load < self._load_thresholds["LOW"]:
            return "LOW"
        elif cpu_load < self._load_thresholds["MEDIUM"]:
            return "MEDIUM"
        elif cpu_load < self._load_thresholds["HIGH"]:
            return "HIGH"
        else:
            return "CRITICAL"

    def _analyze_resource_availability(self, context: Dict[str, Any]) -> str:
        """Analyze resource availability."""
        memory_available = context.get("memory_available", 0.0)

        if memory_available > 70.0:
            return "ABUNDANT"
        elif memory_available > 40.0:
            return "ADEQUATE"
        else:
            return "SCARCE"


class StrategySelector:
    """Selects optimal execution strategy based on conditions."""

    def __init__(self):
        self._lock = threading.Lock()

        # Available strategies
        self._available_strategies = {
            StrategyType.LATENCY_OPTIMIZED: ExecutionStrategy(
                strategy_type=StrategyType.LATENCY_OPTIMIZED,
                priority_level=90,
                parameters={"timeout_ms": 50.0, "max_retries": 1},
                performance_weights={"latency": 0.8, "throughput": 0.2, "cost": 0.0},
                description="Optimize for minimum latency",
            ),
            StrategyType.THROUGHPUT_OPTIMIZED: ExecutionStrategy(
                strategy_type=StrategyType.THROUGHPUT_OPTIMIZED,
                priority_level=80,
                parameters={"batch_size": 10, "parallelism": 4},
                performance_weights={"latency": 0.3, "throughput": 0.7, "cost": 0.0},
                description="Optimize for maximum throughput",
            ),
            StrategyType.COST_OPTIMIZED: ExecutionStrategy(
                strategy_type=StrategyType.COST_OPTIMIZED,
                priority_level=60,
                parameters={"use_spot_instances": True, "min_instances": 1},
                performance_weights={"latency": 0.2, "throughput": 0.2, "cost": 0.6},
                description="Optimize for minimum cost",
            ),
            StrategyType.BALANCED: ExecutionStrategy(
                strategy_type=StrategyType.BALANCED,
                priority_level=70,
                parameters={"timeout_ms": 100.0, "parallelism": 2},
                performance_weights={"latency": 0.4, "throughput": 0.4, "cost": 0.2},
                description="Balanced approach",
            ),
            StrategyType.CONSERVATIVE: ExecutionStrategy(
                strategy_type=StrategyType.CONSERVATIVE,
                priority_level=50,
                parameters={"max_retries": 5, "timeout_ms": 200.0},
                performance_weights={"latency": 0.3, "throughput": 0.3, "cost": 0.4},
                description="Conservative approach with high safety",
            ),
            StrategyType.AGGRESSIVE: ExecutionStrategy(
                strategy_type=StrategyType.AGGRESSIVE,
                priority_level=85,
                parameters={"timeout_ms": 30.0, "max_retries": 0},
                performance_weights={"latency": 0.6, "throughput": 0.4, "cost": 0.0},
                description="Aggressive approach for speed",
            ),
        }

        logger.info(
            "[STRATEGY_SELECTOR] Initialized with {len(self._available_strategies)} strategies"
        )

    def select(
        self,
        conditions: ConditionAnalysis,
        available_strategies: Optional[List[StrategyType]] = None,
    ) -> StrategySelection:
        """
        Select optimal strategy based on conditions.

        Args:
            conditions: Current execution conditions
            available_strategies: List of available strategies (None = all)

        Returns:
            Strategy selection with confidence
        """
        with self._lock:
            strategies_to_consider = available_strategies or list(self._available_strategies.keys())

            # Score each strategy
            scored_strategies = []
            for strategy_type in strategies_to_consider:
                if strategy_type in self._available_strategies:
                    strategy = self._available_strategies[strategy_type]
                    score, reasoning = self._score_strategy(strategy, conditions)
                    scored_strategies.append((score, strategy, reasoning))

            # Sort by score
            scored_strategies.sort(key=lambda x: x[0], reverse=True)

            if not scored_strategies:
                # Fallback to balanced strategy
                strategy = self._available_strategies[StrategyType.BALANCED]
                return StrategySelection(
                    selected_strategy=strategy,
                    confidence=0.5,
                    reasoning="Fallback to balanced strategy",
                )

            # Select best strategy
            best_score, best_strategy, best_reasoning = scored_strategies[0]
            confidence = min(best_score / 100.0, 1.0)

            # Get alternatives
            alternatives = [s[1] for s in scored_strategies[1:3]]  # Top 2 alternatives

            return StrategySelection(
                selected_strategy=best_strategy,
                confidence=confidence,
                reasoning=best_reasoning,
                alternative_strategies=alternatives,
            )

    def _score_strategy(
        self, strategy: ExecutionStrategy, conditions: ConditionAnalysis
    ) -> tuple[float, str]:
        """Score strategy based on conditions."""
        score = strategy.priority_level
        reasoning_parts = []

        # Time constraint adjustment
        if conditions.time_constraint == "STRICT":
            if strategy.strategy_type in [StrategyType.LATENCY_OPTIMIZED, StrategyType.AGGRESSIVE]:
                score += 20
                reasoning_parts.append("Matches strict time constraint")
        elif conditions.time_constraint == "FLEXIBLE":
            if strategy.strategy_type in [
                StrategyType.COST_OPTIMIZED,
                StrategyType.THROUGHPUT_OPTIMIZED,
            ]:
                score += 15
                reasoning_parts.append("Cost-effective for flexible deadline")

        # System load adjustment
        if conditions.system_load in ["HIGH", "CRITICAL"]:
            if strategy.strategy_type == StrategyType.CONSERVATIVE:
                score += 15
                reasoning_parts.append("Conservative approach for high load")
            elif strategy.strategy_type == StrategyType.AGGRESSIVE:
                score -= 20
                reasoning_parts.append("Aggressive not suitable for high load")

        # Risk tolerance adjustment
        if conditions.risk_tolerance == "LOW":
            if strategy.strategy_type == StrategyType.CONSERVATIVE:
                score += 20
                reasoning_parts.append("Matches low risk tolerance")
        elif conditions.risk_tolerance == "HIGH":
            if strategy.strategy_type == StrategyType.AGGRESSIVE:
                score += 15
                reasoning_parts.append("Matches high risk tolerance")

        # Resource availability adjustment
        if conditions.resource_availability == "SCARCE":
            if strategy.strategy_type == StrategyType.COST_OPTIMIZED:
                score += 15
                reasoning_parts.append("Resource efficient")

        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Default selection"

        return max(score, 0.0), reasoning


class StrategyOptimizer:
    """Optimizes strategy parameters based on performance feedback."""

    def __init__(self):
        self._lock = threading.Lock()
        self._performance_history: Dict[StrategyType, StrategyPerformance] = {}

        logger.info("[STRATEGY_OPTIMIZER] Initialized")

    def optimize(
        self, strategy: ExecutionStrategy, performance_feedback: Dict[str, float]
    ) -> ExecutionStrategy:
        """
        Optimize strategy parameters based on performance feedback.

        Args:
            strategy: Strategy to optimize
            performance_feedback: Performance metrics

        Returns:
            Optimized strategy
        """
        with self._lock:
            # Update performance history
            if strategy.strategy_type not in self._performance_history:
                self._performance_history[strategy.strategy_type] = StrategyPerformance(
                    strategy_type=strategy.strategy_type,
                    execution_count=0,
                    success_rate=0.0,
                    average_latency_ms=0.0,
                    average_throughput=0.0,
                    cost_per_execution=0.0,
                )

            perf = self._performance_history[strategy.strategy_type]
            perf.execution_count += 1
            perf.success_rate = performance_feedback.get("success_rate", perf.success_rate)
            perf.average_latency_ms = performance_feedback.get(
                "latency_ms", perf.average_latency_ms
            )
            perf.average_throughput = performance_feedback.get(
                "throughput", perf.average_throughput
            )
            perf.cost_per_execution = performance_feedback.get("cost", perf.cost_per_execution)
            perf.last_used = datetime.utcnow()

            # Optimize parameters based on performance
            optimized_params = strategy.parameters.copy()

            # Optimize timeout based on latency
            current_timeout = strategy.parameters.get("timeout_ms", 100.0)
            avg_latency = perf.average_latency_ms

            if avg_latency > current_timeout * 0.9:
                # Increase timeout if latency is close to timeout
                optimized_params["timeout_ms"] = current_timeout * 1.2
            elif avg_latency < current_timeout * 0.5:
                # Decrease timeout for faster execution
                optimized_params["timeout_ms"] = max(current_timeout * 0.8, 10.0)

            # Optimize parallelism based on throughput
            current_parallelism = strategy.parameters.get("parallelism", 1)
            if perf.average_throughput < 100 and current_parallelism < 8:
                optimized_params["parallelism"] = current_parallelism + 1

            return ExecutionStrategy(
                strategy_type=strategy.strategy_type,
                priority_level=strategy.priority_level,
                parameters=optimized_params,
                performance_weights=strategy.performance_weights.copy(),
                description=strategy.description,
            )


class AdaptiveExecutionStrategy:
    """
    Adaptive execution strategies based on conditions.

    Features:
    - Condition analysis (market, load, time, risk, resources)
    - Strategy selection based on conditions
    - Strategy optimization based on feedback
    - Performance tracking
    - Continuous improvement
    """

    def __init__(self):
        self._lock = threading.Lock()

        # Components
        self._condition_analyzer = ConditionAnalyzer()
        self._strategy_selector = StrategySelector()
        self._strategy_optimizer = StrategyOptimizer()

        # Strategy usage tracking
        self._strategy_usage: Dict[StrategyType, int] = {}

        logger.info("[ADAPTIVE_EXECUTION] Adaptive Execution Strategy system initialized")

    def select_strategy(
        self,
        execution_context: Dict[str, Any],
        available_strategies: Optional[List[StrategyType]] = None,
    ) -> StrategySelection:
        """
        Select optimal execution strategy based on conditions.

        Args:
            execution_context: Current execution context
            available_strategies: Available strategies

        Returns:
            Strategy selection
        """
        with self._lock:
            # Step 1: Analyze conditions
            conditions = self._condition_analyzer.analyze(execution_context)

            # Step 2: Select strategy
            selection = self._strategy_selector.select(conditions, available_strategies)

            # Step 3: Track usage
            strategy_type = selection.selected_strategy.strategy_type
            self._strategy_usage[strategy_type] = self._strategy_usage.get(strategy_type, 0) + 1

            return selection

    def update_feedback(
        self, strategy_type: StrategyType, performance_feedback: Dict[str, float]
    ) -> ExecutionStrategy:
        """
        Update performance feedback and optimize strategy.

        Args:
            strategy_type: Strategy type to update
            performance_feedback: Performance metrics

        Returns:
            Optimized strategy
        """
        with self._lock:
            strategy = self._strategy_selector._available_strategies.get(strategy_type)
            if strategy:
                optimized = self._strategy_optimizer.optimize(strategy, performance_feedback)
                # Update available strategies
                self._strategy_selector._available_strategies[strategy_type] = optimized
                return optimized
            return strategy

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution strategy statistics."""
        with self._lock:
            return {
                "strategy_usage": {
                    strategy_type.value: count
                    for strategy_type, count in self._strategy_usage.items()
                },
                "available_strategies": len(self._strategy_selector._available_strategies),
                "performance_history": {
                    strategy_type.value: {
                        "execution_count": perf.execution_count,
                        "success_rate": perf.success_rate,
                        "average_latency_ms": perf.average_latency_ms,
                    }
                    for strategy_type, perf in self._strategy_optimizer._performance_history.items()
                },
            }


# Singleton instance
_adaptive_execution_strategy: Optional[AdaptiveExecutionStrategy] = None
_adaptive_execution_strategy_lock = threading.Lock()


def get_adaptive_execution_strategy() -> AdaptiveExecutionStrategy:
    """Get the singleton adaptive execution strategy instance."""
    global _adaptive_execution_strategy
    if _adaptive_execution_strategy is None:
        with _adaptive_execution_strategy_lock:
            if _adaptive_execution_strategy is None:
                _adaptive_execution_strategy = AdaptiveExecutionStrategy()
    return _adaptive_execution_strategy


def get_adaptive_execution_strategies() -> AdaptiveExecutionStrategy:
    """Get the singleton adaptive execution strategies instance (alias)."""
    return get_adaptive_execution_strategy()


__all__ = [
    "StrategyType",
    "ConditionAnalysis",
    "ExecutionStrategy",
    "StrategySelection",
    "StrategyPerformance",
    "ConditionAnalyzer",
    "StrategySelector",
    "StrategyOptimizer",
    "AdaptiveExecutionStrategy",
    "get_adaptive_execution_strategy",
    "get_adaptive_execution_strategies",
]
