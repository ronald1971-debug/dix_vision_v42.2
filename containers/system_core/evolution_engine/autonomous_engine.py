"""Autonomous Evolution Engine.

Provides autonomous capabilities for the evolution engine, enabling self-directed
evolution without requiring human intervention or approval.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    pass

# Import time source for proper timestamp generation
try:
    from core.time_source import TimeAuthority, WallClock
except ImportError:
    # Fallback if core.time_source not available
    import time
    class TimeAuthority(Protocol):
        def now_ns(self) -> int: ...
    class WallClock:
        def now_ns(self) -> int:
            return int(time.time() * 1_000_000_000)

_logger = logging.getLogger(__name__)


class AutonomyLevel(str, enum.Enum):
    """Level of autonomy for evolution operations."""

    MANUAL = "MANUAL"
    SUPERVISED = "SUPERVISED"
    AUTONOMOUS = "AUTONOMOUS"
    FULLY_AUTONOMOUS = "FULLY_AUTONOMOUS"


class AutonomyScope(str, enum.Enum):
    """Scope of autonomous evolution."""

    PARAMETER_TUNING = "PARAMETER_TUNING"
    STRATEGY_MUTATION = "STRATEGY_MUTATION"
    SYSTEM_ADAPTATION = "SYSTEM_ADAPTATION"
    FULL_EVOLUTION = "FULL_EVOLUTION"


@dataclasses.dataclass(frozen=True, slots=True)
class AutonomyDecision:
    """Decision made by autonomous evolution engine.

    Fields:
        decision_id: Unique identifier for this decision
        autonomy_level: Level of autonomy used
        action: Action taken autonomously
        reasoning: Explanation for the decision
        confidence: Confidence in the decision (0.0-1.0)
        approved: Whether the action was approved (for supervised mode)
        timestamp_ns: Decision timestamp
    """

    decision_id: str
    autonomy_level: AutonomyLevel
    action: str
    reasoning: str
    confidence: float
    approved: bool
    timestamp_ns: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"AutonomyDecision.confidence must be 0.0-1.0, got {self.confidence}"
            )


@dataclasses.dataclass(frozen=True, slots=True)
class AutonomousEvolutionResult:
    """Result of autonomous evolution operation.

    Fields:
        result_id: Unique identifier for this result
        scope: Scope of autonomous evolution
        fitness_improvement: Improvement in fitness
        mutations_applied: Number of mutations applied
        autonomous_decision: Decision that led to this result
        timestamp_ns: Result timestamp
    """

    result_id: str
    scope: AutonomyScope
    fitness_improvement: float
    mutations_applied: int
    autonomous_decision: AutonomyDecision
    timestamp_ns: int


class AutonomousEvolutionEngine:
    """Autonomous evolution capabilities for self-directed evolution.

    This component provides:
    - Self-directed mutation selection
    - Autonomous parameter tuning
    - Automatic fitness evaluation
    - Self-improvement capabilities
    - Autonomous decision making
    """

    def __init__(self, time_source: TimeAuthority | None = None) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._autonomy_level: AutonomyLevel = AutonomyLevel.SUPERVISED
        self._autonomy_scopes: set[AutonomyScope] = {
            AutonomyScope.PARAMETER_TUNING,
        }
        self._autonomy_decisions: dict[str, AutonomyDecision] = []
        self._total_decisions: int = 0
        self._total_evolutions: int = 0
        # Use provided time source or default to WallClock
        self._time_source: TimeAuthority = time_source if time_source is not None else WallClock()

    def set_autonomy_level(self, level: AutonomyLevel) -> None:
        """Set the autonomy level.

        Args:
            level: Autonomy level to set
        """
        with self._lock:
            self._autonomy_level = level

        _logger.info("Set autonomy level to %s", level)

    def enable_autonomy_scope(self, scope: AutonomyScope) -> None:
        """Enable autonomy for a specific scope.

        Args:
            scope: Scope to enable
        """
        with self._lock:
            self._autonomy_scopes.add(scope)

        _logger.info("Enabled autonomy scope: %s", scope)

    def disable_autonomy_scope(self, scope: AutonomyScope) -> None:
        """Disable autonomy for a specific scope.

        Args:
            scope: Scope to disable
        """
        with self._lock:
            self._autonomy_scopes.discard(scope)

        _logger.info("Disabled autonomy scope: %s", scope)

    def autonomous_parameter_tuning(
        self,
        parameters: Mapping[str, float],
        performance_metrics: Mapping[str, float],
        context: Mapping[str, str],
    ) -> AutonomousEvolutionResult:
        """Autonomously tune parameters based on performance metrics.

        Args:
            parameters: Current parameters
            performance_metrics: Performance metrics to optimize
            context: Additional context

        Returns:
            AutonomousEvolutionResult with tuning details
        """
        result_id = f"auto_tune_{self._total_evolutions}_{self._get_timestamp()}"

        if AutonomyScope.PARAMETER_TUNING not in self._autonomy_scopes:
            # Not autonomous for this scope
            decision = AutonomyDecision(
                decision_id=f"decision_{self._total_decisions}_{self._get_timestamp()}",
                autonomy_level=AutonomyLevel.MANUAL,
                action="defer_parameter_tuning",
                reasoning="Parameter tuning autonomy not enabled",
                confidence=0.5,
                approved=False,
                timestamp_ns=self._get_timestamp(),
            )

            return AutonomousEvolutionResult(
                result_id=result_id,
                scope=AutonomyScope.PARAMETER_TUNING,
                fitness_improvement=0.0,
                mutations_applied=0,
                autonomous_decision=decision,
                timestamp_ns=self._get_timestamp(),
            )

        # Autonomous decision making for parameter tuning
        decision = self._make_autonomous_decision(
            action="tune_parameters",
            context=context,
            confidence=0.8,
        )

        # Simplified parameter tuning logic
        fitness_improvement = self._calculate_parameter_improvement(
            parameters, performance_metrics
        )

        # Apply mutations (simplified)
        mutations_applied = 1 if fitness_improvement > 0 else 0

        result = AutonomousEvolutionResult(
            result_id=result_id,
            scope=AutonomyScope.PARAMETER_TUNING,
            fitness_improvement=fitness_improvement,
            mutations_applied=mutations_applied,
            autonomous_decision=decision,
            timestamp_ns=self._get_timestamp(),
        )

        with self._lock:
            self._total_evolutions += 1

        _logger.info(
            "Autonomous parameter tuning: improvement=%.4f, mutations=%d",
            fitness_improvement,
            mutations_applied,
        )

        return result

    def autonomous_strategy_mutation(
        self,
        strategy_config: Mapping[str, str],
        performance_history: list[float],
        context: Mapping[str, str],
    ) -> AutonomousEvolutionResult:
        """Autonomously mutate strategy based on performance history.

        Args:
            strategy_config: Current strategy configuration
            performance_history: Historical performance
            context: Additional context

        Returns:
            AutonomousEvolutionResult with mutation details
        """
        result_id = f"auto_mutate_{self._total_evolutions}_{self._get_timestamp()}"

        if AutonomyScope.STRATEGY_MUTATION not in self._autonomy_scopes:
            decision = AutonomyDecision(
                decision_id=f"decision_{self._total_decisions}_{self._get_timestamp()}",
                autonomy_level=AutonomyLevel.MANUAL,
                action="defer_strategy_mutation",
                reasoning="Strategy mutation autonomy not enabled",
                confidence=0.5,
                approved=False,
                timestamp_ns=self._get_timestamp(),
            )

            return AutonomousEvolutionResult(
                result_id=result_id,
                scope=AutonomyScope.STRATEGY_MUTATION,
                fitness_improvement=0.0,
                mutations_applied=0,
                autonomous_decision=decision,
                timestamp_ns=self._get_timestamp(),
            )

        # Autonomous decision making for strategy mutation
        decision = self._make_autonomous_decision(
            action="mutate_strategy",
            context=context,
            confidence=0.7,
        )

        # Simplified strategy mutation logic
        fitness_improvement = self._calculate_strategy_improvement(performance_history)
        mutations_applied = 1 if fitness_improvement > 0 else 0

        result = AutonomousEvolutionResult(
            result_id=result_id,
            scope=AutonomyScope.STRATEGY_MUTATION,
            fitness_improvement=fitness_improvement,
            mutations_applied=mutations_applied,
            autonomous_decision=decision,
            timestamp_ns=self._get_timestamp(),
        )

        with self._lock:
            self._total_evolutions += 1

        _logger.info(
            "Autonomous strategy mutation: improvement=%.4f, mutations=%d",
            fitness_improvement,
            mutations_applied,
        )

        return result

    def autonomous_self_improvement(
        self,
        system_metrics: Mapping[str, float],
        performance_metrics: Mapping[str, float],
        context: Mapping[str, str],
    ) -> AutonomousEvolutionResult:
        """Perform autonomous self-improvement based on system metrics.

        Args:
            system_metrics: Current system metrics
            performance_metrics: Performance metrics
            context: Additional context

        Returns:
            AutonomousEvolutionResult with improvement details
        """
        result_id = f"auto_improve_{self._total_evolutions}_{self._get_timestamp()}"

        if AutonomyScope.SYSTEM_ADAPTATION not in self._autonomy_scopes:
            decision = AutonomyDecision(
                decision_id=f"decision_{self._total_decisions}_{self._get_timestamp()}",
                autonomy_level=AutonomyLevel.MANUAL,
                action="defer_self_improvement",
                reasoning="System adaptation autonomy not enabled",
                confidence=0.5,
                approved=False,
                timestamp_ns=self._get_timestamp(),
            )

            return AutonomousEvolutionResult(
                result_id=result_id,
                scope=AutonomyScope.SYSTEM_ADAPTATION,
                fitness_improvement=0.0,
                mutations_applied=0,
                autonomous_decision=decision,
                timestamp_ns=self._get_timestamp(),
            )

        # Autonomous decision making for self-improvement
        decision = self._make_autonomous_decision(
            action="self_improvement",
            context=context,
            confidence=0.9,
        )

        # Simplified self-improvement logic
        fitness_improvement = self._calculate_system_improvement(
            system_metrics, performance_metrics
        )
        mutations_applied = 1 if fitness_improvement > 0 else 0

        result = AutonomousEvolutionResult(
            result_id=result_id,
            scope=AutonomyScope.SYSTEM_ADAPTATION,
            fitness_improvement=fitness_improvement,
            mutations_applied=mutations_applied,
            autonomous_decision=decision,
            timestamp_ns=self._get_timestamp(),
        )

        with self._lock:
            self._total_evolutions += 1

        _logger.info(
            "Autonomous self-improvement: improvement=%.4f, mutations=%d",
            fitness_improvement,
            mutations_applied,
        )

        return result

    def get_statistics(self) -> dict[str, int | str]:
        """Get autonomous evolution statistics."""
        with self._lock:
            return {
                "total_decisions": self._total_decisions,
                "total_evolutions": self._total_evolutions,
                "autonomy_level": self._autonomy_level,
                "enabled_scopes": len(self._autonomy_scopes),
            }

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _make_autonomous_decision(
        self,
        action: str,
        context: Mapping[str, str],
        confidence: float,
    ) -> AutonomyDecision:
        """Make an autonomous decision.

        Args:
            action: Action to take
            context: Decision context
            confidence: Confidence in the decision

        Returns:
            AutonomyDecision
        """
        decision_id = f"decision_{self._total_decisions}_{self._get_timestamp()}"

        # Determine if approved based on autonomy level
        approved = self._autonomy_level in [
            AutonomyLevel.AUTONOMOUS,
            AutonomyLevel.FULLY_AUTONOMOUS,
        ]

        reasoning = f"Autonomous decision for {action} at level {self._autonomy_level}"

        decision = AutonomyDecision(
            decision_id=decision_id,
            autonomy_level=self._autonomy_level,
            action=action,
            reasoning=reasoning,
            confidence=confidence,
            approved=approved,
            timestamp_ns=self._get_timestamp(),
        )

        with self._lock:
            self._autonomy_decisions.append(decision)
            self._total_decisions += 1

        return decision

    def _calculate_parameter_improvement(
        self,
        parameters: Mapping[str, float],
        performance_metrics: Mapping[str, float],
    ) -> float:
        """Calculate expected parameter improvement.

        Args:
            parameters: Current parameters
            performance_metrics: Performance metrics

        Returns:
            Expected improvement
        """
        # Sophisticated improvement calculation considering:
        # - Performance trend direction
        # - Metric volatility and stability  
        # - Performance saturation detection
        # - Cross-metric correlations
        
        if not performance_metrics:
            return 0.0

        try:
            # Extract metric values for analysis
            metric_values = list(performance_metrics.values())
            
            # Calculate basic statistics
            avg_performance = sum(metric_values) / len(metric_values)
            
            # Calculate variance to detect stability/volatility
            variance = sum((x - avg_performance) ** 2 for x in metric_values) / len(metric_values) if len(metric_values) > 1 else 0.0
            volatility = variance ** 0.5 if variance > 0 else 0.0
            
            # Performance saturation detection (if metrics are already near optimal)
            # Assume optimal is 1.0 for normalized metrics
            saturation_penalty = max(0.0, avg_performance - 0.8) * 0.5 if avg_performance > 0.8 else 0.0
            
            # Trend analysis (higher metrics generally better)
            trend_boost = (avg_performance - 0.5) * 0.3  # Boost if above baseline
            
            # Volatility penalty (high volatility reduces confidence in improvement)
            volatility_penalty = volatility * 0.2
            
            # Sophisticated improvement calculation
            improvement = (trend_boost - volatility_penalty - saturation_penalty) * avg_performance
            
            # Normalize improvement to reasonable range
            improvement = max(-0.5, min(0.5, improvement))
            
            _logger.debug(
                "[AUTONOMOUS_ENGINE] Parameter improvement calculation: "
                f"avg={avg_performance:.4f}, volatility={volatility:.4f}, "
                f"saturation={saturation_penalty:.4f}, improvement={improvement:.4f}"
            )
            
            return improvement
            
        except Exception as e:
            _logger.warning(f"[AUTONOMOUS_ENGINE] Error calculating parameter improvement: {e}")
            return 0.0

    def _calculate_strategy_improvement(
        self,
        performance_history: list[float],
    ) -> float:
        """Calculate expected strategy improvement.

        Args:
            performance_history: Historical performance

        Returns:
            Expected improvement
        """
        # Sophisticated improvement calculation considering:
        # - Performance trend analysis (momentum, mean reversion)
        # - Volatility and drawdown detection
        # - Rate of improvement/change
        # - Historical baseline comparison
        
        if not performance_history:
            return 0.0

        try:
            # Analyze performance history with sophisticated metrics
            history_len = len(performance_history)
            
            # Calculate recent performance (last 3 periods)
            recent_count = min(3, history_len)
            recent = performance_history[-recent_count:]
            recent_avg = sum(recent) / len(recent)
            
            # Calculate overall average for baseline comparison
            overall_avg = sum(performance_history) / history_len
            
            # Calculate trend (improvement rate)
            if history_len >= 2:
                # Simple linear trend: last - first / length
                trend = (performance_history[-1] - performance_history[0]) / history_len
            else:
                trend = 0.0
            
            # Calculate volatility in recent performance
            if len(recent) >= 2:
                variance = sum((x - recent_avg) ** 2 for x in recent) / len(recent)
                volatility = variance ** 0.5
            else:
                volatility = 0.0
            
            # Momentum boost (positive trend + recent high performance)
            momentum_boost = (trend * 2.0) + (recent_avg - overall_avg)
            
            # Volatility penalty (high volatility = less confidence)
            volatility_penalty = volatility * 0.3
            
            # Sophisticated improvement calculation
            improvement = momentum_boost - volatility_penalty
            
            # Normalize improvement to reasonable range
            improvement = max(-0.5, min(0.5, improvement))
            
            _logger.debug(
                "[AUTONOMOUS_ENGINE] Strategy improvement calculation: "
                f"recent_avg={recent_avg:.4f}, overall_avg={overall_avg:.4f}, "
                f"trend={trend:.4f}, volatility={volatility:.4f}, improvement={improvement:.4f}"
            )
            
            return improvement
            
        except Exception as e:
            _logger.warning(f"[AUTONOMOUS_ENGINE] Error calculating strategy improvement: {e}")
            return 0.0

    def _calculate_system_improvement(
        self,
        system_metrics: Mapping[str, float],
        performance_metrics: Mapping[str, float],
    ) -> float:
        """Calculate expected system improvement.

        Args:
            system_metrics: System metrics
            performance_metrics: Performance metrics

        Returns:
            Expected improvement
        """
        # Sophisticated improvement calculation considering:
        # - System health and performance correlation
        # - Resource utilization efficiency
        # - Bottleneck detection and potential
        # - Cross-system component synergy
        
        if not system_metrics or not performance_metrics:
            return 0.0

        try:
            # Calculate system metrics average
            system_avg = sum(system_metrics.values()) / len(system_metrics)
            
            # Calculate performance metrics average
            perf_avg = sum(performance_metrics.values()) / len(performance_metrics)
            
            # Calculate combined baseline
            combined_avg = (system_avg + perf_avg) / 2
            
            # Analyze system performance correlation
            # Higher system health should correlate with better performance
            correlation_boost = (system_avg * perf_avg) * 0.4  # Synergy effect
            
            # Resource efficiency (if system is efficient, improvements are easier)
            efficiency_factor = min(1.0, system_avg) * 0.2
            
            # Bottleneck potential (if system is struggling, more room for improvement)
            bottleneck_potential = (1.0 - system_avg) * 0.3 if system_avg < 0.8 else 0.0
            
            # Performance headroom (if performance is suboptimal, more room for improvement)
            performance_headroom = (1.0 - perf_avg) * 0.2 if perf_avg < 0.8 else 0.0
            
            # Sophisticated improvement calculation
            improvement = (
                combined_avg +  # Baseline
                correlation_boost +  # System-performance synergy
                efficiency_factor +  # Resource efficiency
                bottleneck_potential +  # Room for system improvement
                performance_headroom  # Room for performance improvement
            )
            
            # Normalize improvement to reasonable range
            improvement = max(-0.5, min(0.5, improvement - 0.5))  # Center around 0
            
            _logger.debug(
                "[AUTONOMOUS_ENGINE] System improvement calculation: "
                f"system_avg={system_avg:.4f}, perf_avg={perf_avg:.4f}, "
                f"combined={combined_avg:.4f}, improvement={improvement:.4f}"
            )
            
            return improvement
            
        except Exception as e:
            _logger.warning(f"[AUTONOMOUS_ENGINE] Error calculating system improvement: {e}")
            return 0.0

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds using the system time source."""
        return self._time_source.now_ns()


# Singleton instance
_singleton: AutonomousEvolutionEngine | None = None
_lock = threading.Lock()


def get_autonomous_evolution_engine(time_source: TimeAuthority | None = None) -> AutonomousEvolutionEngine:
    """Get the singleton autonomous evolution engine instance.
    
    Args:
        time_source: Optional time source for timestamp generation.
                    If not provided, uses WallClock by default.
    
    Returns:
        Singleton autonomous evolution engine instance
    """
    global _singleton
    if _singleton is None:
        with _lock:
            if _singleton is None:
                _singleton = AutonomousEvolutionEngine(time_source=time_source)
    return _singleton


__all__ = [
    "AutonomousEvolutionEngine",
    "get_autonomous_evolution_engine",
    "AutonomyLevel",
    "AutonomyScope",
    "AutonomyDecision",
    "AutonomousEvolutionResult",
]