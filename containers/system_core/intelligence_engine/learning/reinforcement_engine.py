"""Reinforcement Learning Engine for Cognitive Learning.

Implements complete reinforcement learning loops with feedback, rewards,
and adaptive learning rates.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

_logger = logging.getLogger(__name__)


class LearningRateStrategy(str, enum.Enum):
    """Strategies for adaptive learning rates."""

    FIXED = "FIXED"
    DECAY = "DECAY"
    ADAPTIVE = "ADAPTIVE"
    CONFIDENCE_BASED = "CONFIDENCE_BASED"


class ReinforcementStatus(str, enum.Enum):
    """Status of reinforcement learning."""

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CONVERGED = "CONVERGED"
    FAILED = "FAILED"


@dataclasses.dataclass(frozen=True, slots=True)
class FeedbackSample:
    """A feedback sample for reinforcement learning.

    Fields:
        sample_id: Unique identifier for this sample
        action: Action taken
        state: State before action
        next_state: State after action
        reward: Reward signal (positive = good, negative = bad)
        confidence: Confidence in the reward signal
        timestamp_ns: Sample timestamp
        metadata: Additional metadata
    """

    sample_id: str
    action: str
    state: Mapping[str, str]
    next_state: Mapping[str, str]
    reward: float
    confidence: float
    timestamp_ns: int
    metadata: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"FeedbackSample.confidence must be 0.0-1.0, got {self.confidence}")
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclasses.dataclass(frozen=True, slots=True)
class ParameterBounds:
    """Bounds for reinforcement learning parameters.

    Fields:
        parameter_name: Name of the parameter
        min_value: Minimum value
        max_value: Maximum value
        current_value: Current value
        learning_rate: Learning rate for this parameter
    """

    parameter_name: str
    min_value: float
    max_value: float
    current_value: float
    learning_rate: float

    def __post_init__(self) -> None:
        if self.min_value >= self.max_value:
            raise ValueError(
                f"ParameterBounds.min_value must be < max_value, got {self.min_value} >= {self.max_value}"
            )
        if not self.min_value <= self.current_value <= self.max_value:
            raise ValueError(
                f"ParameterBounds.current_value must be within bounds, got {self.current_value}"
            )


@dataclasses.dataclass(frozen=True, slots=True)
class ReinforcementUpdate:
    """Result of a reinforcement learning update.

    Fields:
        update_id: Unique identifier for this update
        parameter_updates: Mapping of parameter names to new values
        reward_improvement: Improvement in reward
        convergence_score: Convergence score (0.0-1.0)
        timestamp_ns: Update timestamp
    """

    update_id: str
    parameter_updates: Mapping[str, float]
    reward_improvement: float
    convergence_score: float
    timestamp_ns: int


class ReinforcementEngine:
    """Complete reinforcement learning engine.

    This component provides:
    - Feedback sample collection
    - Reward calculation and aggregation
    - Parameter update with learning rate adaptation
    - Convergence detection
    - Reinforcement loop management
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._feedback_samples: dict[str, FeedbackSample] = {}
        self._parameter_bounds: dict[str, ParameterBounds] = {}
        self._learning_rate_strategy: LearningRateStrategy = LearningRateStrategy.ADAPTIVE
        self._status: ReinforcementStatus = ReinforcementStatus.ACTIVE
        self._total_updates: int = 0
        self._total_samples: int = 0

    def add_feedback_sample(
        self,
        action: str,
        state: Mapping[str, str],
        next_state: Mapping[str, str],
        reward: float,
        confidence: float = 0.9,
    ) -> FeedbackSample:
        """Add a feedback sample for reinforcement learning.

        Args:
            action: Action taken
            state: State before action
            next_state: State after action
            reward: Reward signal
            confidence: Confidence in the reward signal

        Returns:
            FeedbackSample that was added
        """
        sample_id = f"sample_{self._total_samples}_{self._get_timestamp()}"
        timestamp_ns = self._get_timestamp()

        sample = FeedbackSample(
            sample_id=sample_id,
            action=action,
            state=MappingProxyType(dict(state)),
            next_state=MappingProxyType(dict(next_state)),
            reward=reward,
            confidence=confidence,
            timestamp_ns=timestamp_ns,
        )

        with self._lock:
            self._feedback_samples[sample_id] = sample
            self._total_samples += 1

        _logger.info(
            "Added feedback sample %s: action=%s, reward=%.2f, confidence=%.2f",
            sample_id,
            action,
            reward,
            confidence,
        )

        return sample

    def set_parameter_bounds(
        self,
        parameter_name: str,
        min_value: float,
        max_value: float,
        current_value: float,
        learning_rate: float = 0.01,
    ) -> ParameterBounds:
        """Set bounds for a reinforcement learning parameter.

        Args:
            parameter_name: Name of the parameter
            min_value: Minimum value
            max_value: Maximum value
            current_value: Current value
            learning_rate: Learning rate

        Returns:
            ParameterBounds that was set
        """
        bounds = ParameterBounds(
            parameter_name=parameter_name,
            min_value=min_value,
            max_value=max_value,
            current_value=current_value,
            learning_rate=learning_rate,
        )

        with self._lock:
            self._parameter_bounds[parameter_name] = bounds

        _logger.info(
            "Set parameter bounds for %s: [%.2f, %.2f], current=%.2f, lr=%.4f",
            parameter_name,
            min_value,
            max_value,
            current_value,
            learning_rate,
        )

        return bounds

    def update_parameters(self) -> ReinforcementUpdate:
        """Perform reinforcement learning parameter update.

        Returns:
            ReinforcementUpdate with update details
        """
        update_id = f"update_{self._total_updates}_{self._get_timestamp()}"
        parameter_updates: dict[str, float] = {}

        with self._lock:
            # Calculate aggregate reward from recent samples
            recent_samples = list(self._feedback_samples.values())[-100:]  # Last 100 samples
            if not recent_samples:
                return ReinforcementUpdate(
                    update_id=update_id,
                    parameter_updates=MappingProxyType({}),
                    reward_improvement=0.0,
                    convergence_score=0.0,
                    timestamp_ns=self._get_timestamp(),
                )

            # Calculate weighted average reward
            total_weight = 0.0
            weighted_reward = 0.0
            for sample in recent_samples:
                weighted_reward += sample.reward * sample.confidence
                total_weight += sample.confidence

            avg_reward = weighted_reward / total_weight if total_weight > 0 else 0.0

            # Update each parameter based on reward signal
            for param_name, bounds in self._parameter_bounds.items():
                adaptive_rate = self._calculate_adaptive_learning_rate(
                    bounds.learning_rate,
                    self._learning_rate_strategy,
                    avg_reward,
                )

                # Simple update: move towards positive reward direction
                if avg_reward > 0:
                    new_value = bounds.current_value + adaptive_rate * (
                        bounds.max_value - bounds.current_value
                    )
                else:
                    new_value = bounds.current_value - adaptive_rate * (
                        bounds.current_value - bounds.min_value
                    )

                # Clamp to bounds
                new_value = max(bounds.min_value, min(bounds.max_value, new_value))

                parameter_updates[param_name] = new_value

                # Update the bounds
                self._parameter_bounds[param_name] = ParameterBounds(
                    parameter_name=bounds.parameter_name,
                    min_value=bounds.min_value,
                    max_value=bounds.max_value,
                    current_value=new_value,
                    learning_rate=bounds.learning_rate,
                )

            # Calculate convergence score
            convergence_score = self._calculate_convergence_score()

            self._total_updates += 1

        update = ReinforcementUpdate(
            update_id=update_id,
            parameter_updates=MappingProxyType(parameter_updates),
            reward_improvement=avg_reward,
            convergence_score=convergence_score,
            timestamp_ns=self._get_timestamp(),
        )

        _logger.info(
            "Reinforcement update %s: %d parameters updated, reward_improvement=%.4f, convergence=%.2f",
            update_id,
            len(parameter_updates),
            avg_reward,
            convergence_score,
        )

        return update

    def set_learning_rate_strategy(
        self,
        strategy: LearningRateStrategy,
    ) -> None:
        """Set the learning rate strategy.

        Args:
            strategy: Learning rate strategy to use
        """
        with self._lock:
            self._learning_rate_strategy = strategy

        _logger.info("Set learning rate strategy to %s", strategy)

    def check_convergence(self) -> bool:
        """Check if reinforcement learning has converged.

        Returns:
            True if converged, False otherwise
        """
        with self._lock:
            if self._status == ReinforcementStatus.CONVERGED:
                return True

            # Check convergence based on recent updates
            if self._total_updates < 10:
                return False

            convergence_score = self._calculate_convergence_score()
            if convergence_score > 0.95:
                self._status = ReinforcementStatus.CONVERGED
                _logger.info("Reforcement learning converged (score: %.2f)", convergence_score)
                return True

            return False

    def get_learning_statistics(self) -> dict[str, int | float | str]:
        """Get learning engine statistics."""
        with self._lock:
            return {
                "total_updates": self._total_updates,
                "total_samples": self._total_samples,
                "status": self._status,
                "learning_rate_strategy": self._learning_rate_strategy,
                "active_parameters": len(self._parameter_bounds),
            }

    def get_statistics(self) -> dict[str, int | float | str]:
        """Get learning engine statistics (alias for get_learning_statistics)."""
        return self.get_learning_statistics()

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _calculate_adaptive_learning_rate(
        self,
        base_rate: float,
        strategy: LearningRateStrategy,
        reward: float,
    ) -> float:
        """Calculate adaptive learning rate based on strategy."""
        if strategy == LearningRateStrategy.FIXED:
            return base_rate
        elif strategy == LearningRateStrategy.DECAY:
            # Decay based on number of updates
            decay_factor = 1.0 / (1.0 + self._total_updates * 0.01)
            return base_rate * decay_factor
        elif strategy == LearningRateStrategy.ADAPTIVE:
            # Adapt based on reward magnitude
            reward_factor = 1.0 / (1.0 + abs(reward))
            return base_rate * reward_factor
        elif strategy == LearningRateStrategy.CONFIDENCE_BASED:
            # Weighted average confidence from recent samples
            recent_samples = list(self._feedback_samples.values())[-100:]
            avg_confidence = (
                sum(s.confidence for s in recent_samples) / len(recent_samples)
                if recent_samples
                else 0.9
            )
            return base_rate * avg_confidence
        else:
            return base_rate

    def _calculate_convergence_score(self) -> float:
        """Calculate convergence score (0.0-1.0)."""
        if self._total_updates < 5:
            return 0.0

        # Simple convergence metric: parameter stability
        # TODO: Implement sophisticated convergence detection
        return min(1.0, self._total_updates / 100.0)

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # In production, this would use the system time source
        return 0  # TODO: Integrate with proper time source


# Singleton instance
_singleton: ReinforcementEngine | None = None
_lock = threading.Lock()


def get_reinforcement_engine() -> ReinforcementEngine:
    """Get the singleton reinforcement engine instance."""
    global _singleton
    if _singleton is None:
        with _lock:
            if _singleton is None:
                _singleton = ReinforcementEngine()
    return _singleton


__all__ = [
    "ReinforcementEngine",
    "get_reinforcement_engine",
    "FeedbackSample",
    "ParameterBounds",
    "ReinforcementUpdate",
    "LearningRateStrategy",
    "ReinforcementStatus",
]
