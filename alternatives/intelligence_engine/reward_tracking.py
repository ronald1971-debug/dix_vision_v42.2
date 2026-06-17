"""Reward Tracking System — INT-07.04.

Reward tracking system for the intelligence engine to monitor,
analyze, and optimize reward signals used in learning and
decision-making. Provides reward shaping, analysis, and
optimization capabilities.
"""

from __future__ import annotations

import dataclasses
import enum
from collections import deque
from collections.abc import Callable
from decimal import Decimal
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_REWARD_HISTORY_SIZE: Final[int] = 10000
DEFAULT_REWARD_SMOOTHING_WINDOW: Final[int] = 100
DEFAULT_ENABLE_REWARD_SHAPING: Final[bool] = True
DEFAULT_ENABLE_BASELINE_TRACKING: Final[bool] = True

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class RewardSource(enum.Enum):
    """Sources of reward signals."""
    EXECUTION = "EXECUTION"  # From trading execution
    RISK = "RISK"  # From risk management
    MARKET = "MARKET"  # From market performance
    STRATEGY = "STRATEGY"  # From strategy metrics
    EXTERNAL = "EXTERNAL"  # From external signals
    COMPOSITE = "COMPOSITE"  # Combined from multiple sources


class RewardType(enum.Enum):
    """Types of reward signals."""
    IMMEDIATE = "IMMEDIATE"  # Direct reward from action
    DELAYED = "DELAYED"  - Reward realized later
    CUMULATIVE = "CUMULATIVE"  - Accumulated reward over time
    SHAPED = "SHAPED"  - Modified reward for learning
    BASELINE = "BASELINE"  - Baseline-adjusted reward
    NORMALIZED = "NORMALIZED"  - Normalized reward


class RewardStatus(enum.Enum):
    """Status of reward tracking."""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    RESET = "RESET"
    ARCHIVED = "ARCHIVED"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class RewardTrackingConfig:
    """Configuration for reward tracking."""
    reward_history_size: int = DEFAULT_REWARD_HISTORY_SIZE
    reward_smoothing_window: int = DEFAULT_REWARD_SMOOTHING_WINDOW
    enable_reward_shaping: bool = DEFAULT_ENABLE_REWARD_SHAPING
    enable_baseline_tracking: bool = DEFAULT_ENABLE_BASELINE_TRACKING
    enable_clipping: bool = True
    clip_range: tuple[float, float] = (-10.0, 10.0)
    enable_normalization: bool = True
    normalization_window: int = 1000

    def __post_init__(self) -> None:
        if self.reward_history_size < 1:
            raise ValueError("reward_history_size must be >= 1")
        if self.reward_smoothing_window < 1:
            raise ValueError("reward_smoothing_window must be >= 1")
        if self.clip_range[0] >= self.clip_range[1]:
            raise ValueError("clip_range[0] must be < clip_range[1]")


@dataclasses.dataclass(frozen=True, slots=True)
class RewardEvent:
    """A reward event."""
    event_id: str
    source: RewardSource
    reward_type: RewardType
    strategy_id: str
    action_id: str
    raw_reward: float
    shaped_reward: float
    final_reward: float
    timestamp_ns: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id must be non-empty")
        if not self.strategy_id:
            raise ValueError("strategy_id must be non-empty")
        if not self.action_id:
            raise ValueError("action_id must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class RewardMetrics:
    """Metrics about reward tracking."""
    strategy_id: str
    total_rewards: int
    total_raw_reward: float
    average_raw_reward: float
    total_shaped_reward: float
    average_shaped_reward: float
    total_final_reward: float
    average_final_reward: float
    reward_volatility: float
    reward_trend: float
    best_reward: float
    worst_reward: float
    reward_percentile_25: float
    reward_percentile_75: float
    last_updated_ns: int


@dataclasses.dataclass(frozen=True, slots=True)
class RewardBaseline:
    """Baseline reward for comparison."""
    baseline_id: str
    strategy_id: str
    baseline_type: str  # "random", "market", "strategy"
    baseline_value: float
    timestamp_ns: int
    window_size: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.datafield(frozen=True, slots=True)
class RewardAnalysis:
    """Analysis of reward patterns."""
    analysis_id: str
    strategy_id: str
    analysis_timestamp_ns: int
    reward_distribution: dict[str, Any]
    seasonality_detected: bool
    trend_analysis: dict[str, Any]
    outlier_detection: dict[str, Any]
    recommendations: list[str]
    confidence: float


# ---------------------------------------------------------------------------
# Reward Tracker
# ---------------------------------------------------------------------------


class RewardTracker:
    """Reward tracking system for intelligence engine.
    
    Tracks, analyzes, and optimizes reward signals used in
    learning and decision-making. Provides:
    
    - Reward event tracking with history
    - Reward shaping for improved learning
    - Baseline tracking for comparison
    - Reward analysis and pattern detection
    - Reward optimization recommendations
    - Comprehensive metrics and monitoring
    """
    
    def __init__(
        self,
        config: RewardTrackingConfig | None = None,
    ) -> None:
        """Initialize the reward tracker.
        
        Args:
            config: Reward tracking configuration
        """
        self._config = config or RewardTrackingConfig()
        self._lock = Lock()
        
        # Reward storage
        self._reward_events: deque[RewardEvent] = deque(
            maxlen=self._config.reward_history_size
        )
        self._rewards_by_strategy: dict[str, deque[RewardEvent]] = {}  # strategy_id -> events
        self._rewards_by_source: dict[RewardSource, deque[RewardEvent]] = {}  # source -> events
        
        # Baselines
        self._baselines: dict[str, RewardBaseline] = {}  # strategy_id -> baseline
        
        # Metrics cache
        self._metrics_cache: dict[str, RewardMetrics] = {}
        
        # Reward shaping functions
        self._shaping_functions: dict[str, Callable[[float, dict[str, Any]], float]] = {}
        
        # Status
        self._status = RewardStatus.ACTIVE
    
    def record_reward(
        self,
        source: RewardSource,
        reward_type: RewardType,
        strategy_id: str,
        action_id: str,
        raw_reward: float,
        metadata: dict[str, Any] | None = None,
        timestamp_ns: int | None = None,
    ) -> RewardEvent:
        """Record a reward event.
        
        Args:
            source: Reward source
            reward_type: Reward type
            strategy_id: Strategy identifier
            action_id: Action identifier
            raw_reward: Raw reward value
            metadata: Additional metadata
            timestamp_ns: Event timestamp
            
        Returns:
            Recorded reward event
        """
        import secrets
        import time
        
        if timestamp_ns is None:
            timestamp_ns = time.time_ns()
        
        event_id = secrets.token_hex(16)
        
        # Apply reward shaping if enabled
        shaped_reward = self._shape_reward(raw_reward, metadata or {})
        
        # Apply clipping if enabled
        final_reward = self._clip_reward(shaped_reward)
        
        event = RewardEvent(
            event_id=event_id,
            source=source,
            reward_type=reward_type,
            strategy_id=strategy_id,
            action_id=action_id,
            raw_reward=raw_reward,
            shaped_reward=shaped_reward,
            final_reward=final_reward,
            timestamp_ns=timestamp_ns,
            metadata=metadata or {},
        )
        
        with self._lock:
            if self._status != RewardStatus.ACTIVE:
                return event
            
            # Store event
            self._reward_events.append(event)
            
            # Update strategy-specific storage
            if strategy_id not in self._rewards_by_strategy:
                self._rewards_by_strategy[strategy_id] = deque(maxlen=self._config.reward_history_size)
            self._rewards_by_strategy[strategy_id].append(event)
            
            # Update source-specific storage
            if source not in self._rewards_by_source:
                self._rewards_by_source[source] = deque(maxlen=self._config.reward_history_size)
            self._rewards_by_source[source].append(event)
            
            # Invalidate metrics cache
            self._metrics_cache.clear()
        
        return event
    
    def get_strategy_metrics(
        self,
        strategy_id: str,
    ) -> RewardMetrics | None:
        """Get reward metrics for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Reward metrics or None if no data
        """
        import time
        
        with self._lock:
            # Check cache
            if strategy_id in self._metrics_cache:
                return self._metrics_cache[strategy_id]
            
            events = self._rewards_by_strategy.get(strategy_id)
            if not events or len(events) == 0:
                return None
            
            # Calculate metrics
            raw_rewards = [e.raw_reward for e in events]
            shaped_rewards = [e.shaped_reward for e in events]
            final_rewards = [e.final_reward for e in events]
            
            total = len(events)
            total_raw = sum(raw_rewards)
            avg_raw = total_raw / total if total > 0 else 0.0
            total_shaped = sum(shaped_rewards)
            avg_shaped = total_shaped / total if total > 0 else 0.0
            total_final = sum(final_rewards)
            avg_final = total_final / total if total > 0 else 0.0
            
            # Calculate volatility
            if len(final_rewards) > 1:
                variance = sum((r - avg_final) ** 2 for r in final_rewards) / len(final_rewards)
                volatility = variance ** 0.5
            else:
                volatility = 0.0
            
            # Calculate trend
            if len(final_rewards) >= 10:
                recent = final_rewards[-10:]
                earlier = final_rewards[-20:-10]
                trend = sum(recent) / len(recent) - sum(earlier) / len(earlier)
            else:
                trend = 0.0
            
            # Calculate percentiles
            sorted_rewards = sorted(final_rewards)
            best_reward = sorted_rewards[-1] if sorted_rewards else 0.0
            worst_reward = sorted_rewards[0] if sorted_rewards else 0.0
            p25 = sorted_rewards[int(len(sorted_rewards) * 0.25)] if sorted_rewards else 0.0
            p75 = sorted_rewards[int(len(sorted_rewards) * 0.75)] if sorted_rewards else 0.0
            
            metrics = RewardMetrics(
                strategy_id=strategy_id,
                total_rewards=total,
                total_raw_reward=total_raw,
                average_raw_reward=avg_raw,
                total_shaped_reward=total_shaped,
                average_shaped_reward=avg_shaped,
                total_final_reward=total_final,
                average_final_reward=avg_final,
                reward_volatility=volatility,
                reward_trend=trend,
                best_reward=best_reward,
                worst_reward=worst_reward,
                reward_percentile_25=p25,
                reward_percentile_75=p75,
                last_updated_ns=time.time_ns(),
            )
            
            self._metrics_cache[strategy_id] = metrics
            return metrics
    
    def set_baseline(
        self,
        strategy_id: str,
        baseline_type: str,
        baseline_value: float,
        window_size: int = 100,
    ) -> RewardBaseline:
        """Set a baseline reward for comparison.
        
        Args:
            strategy_id: Strategy identifier
            baseline_type: Type of baseline
            baseline_value: Baseline value
            window_size: Window size for baseline
            
        Returns:
            Reward baseline
        """
        import secrets
        import time
        
        baseline = RewardBaseline(
            baseline_id=secrets.token_hex(16),
            strategy_id=strategy_id,
            baseline_type=baseline_type,
            baseline_value=baseline_value,
            timestamp_ns=time.time_ns(),
            window_size=window_size,
        )
        
        with self._lock:
            self._baselines[strategy_id] = baseline
        
        return baseline
    
    def get_baseline(
        self,
        strategy_id: str,
    ) -> RewardBaseline | None:
        """Get baseline for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Reward baseline or None
        """
        with self._lock:
            return self._baselines.get(strategy_id)
    
    def analyze_rewards(
        self,
        strategy_id: str,
    ) -> RewardAnalysis | None:
        """Analyze reward patterns for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Reward analysis or None if no data
        """
        import secrets
        import time
        
        with self._lock:
            events = self._rewards_by_strategy.get(strategy_id)
            if not events or len(events) < 20:
                return None
        
        final_rewards = [e.final_reward for e in events]
        
        # Distribution analysis
        sorted_rewards = sorted(final_rewards)
        distribution = {
            "mean": sum(final_rewards) / len(final_rewards),
            "median": sorted_rewards[len(sorted_rewards) // 2],
            "std": (sum((r - (sum(final_rewards) / len(final_rewards))) ** 2 for r in final_rewards) / len(final_rewards)) ** 0.5,
            "min": sorted_rewards[0],
            "max": sorted_rewards[-1],
            "percentiles": {
                "p25": sorted_rewards[int(len(sorted_rewards) * 0.25)],
                "p50": sorted_rewards[int(len(sorted_rewards) * 0.50)],
                "p75": sorted_rewards[int(len(sorted_rewards) * 0.75)],
                "p90": sorted_rewards[int(len(sorted_rewards) * 0.90)],
            },
        }
        
        # Trend analysis
        if len(final_rewards) >= 20:
            first_half = final_rewards[:len(final_rewards) // 2]
            second_half = final_rewards[len(final_rewards) // 2:]
            trend = {
                "direction": "increasing" if sum(second_half) > sum(first_half) else "decreasing",
                "magnitude": abs(sum(second_half) - sum(first_half)) / len(first_half),
                "consistency": 1.0 - (sum(abs(r1 - r2) for r1, r2 in zip(final_rewards[:-1], final_rewards[1:])) / len(final_rewards)),
            }
        else:
            trend = {"direction": "unknown", "magnitude": 0.0, "consistency": 0.0}
        
        # Outlier detection (simple z-score)
        mean = distribution["mean"]
        std = distribution["std"]
        if std > 0:
            z_scores = [(r - mean) / std for r in final_rewards]
            outliers = [(i, r, z) for i, (r, z) in enumerate(zip(final_rewards, z_scores)) if abs(z) > 2]
            outlier_detection = {
                "count": len(outliers),
                "indices": [o[0] for o in outliers],
                "values": [o[1] for o in outliers],
                "z_scores": [o[2] for o in outliers],
            }
        else:
            outlier_detection = {"count": 0, "indices": [], "values": [], "z_scores": []}
        
        # Generate recommendations
        recommendations = []
        if trend["direction"] == "decreasing" and trend["magnitude"] > 0.5:
            recommendations.append("Reward trend declining - review strategy parameters")
        if distribution["std"] > distribution["mean"]:
            recommendations.append("High reward volatility - consider reward smoothing")
        if outlier_detection["count"] > len(final_rewards) * 0.1:
            recommendations.append("High outlier rate - investigate reward source")
        
        analysis = RewardAnalysis(
            analysis_id=secrets.token_hex(16),
            strategy_id=strategy_id,
            analysis_timestamp_ns=time.time_ns(),
            reward_distribution=distribution,
            seasonality_detected=False,  # Placeholder for seasonality detection
            trend_analysis=trend,
            outlier_detection=outlier_detection,
            recommendations=recommendations,
            confidence=0.8,  # Placeholder confidence
        )
        
        return analysis
    
    def register_shaping_function(
        self,
        name: str,
        shaping_function: Callable[[float, dict[str, Any]], float],
    ) -> None:
        """Register a reward shaping function.
        
        Args:
            name: Function name
            shaping_function: Shaping function
        """
        with self._lock:
            self._shaping_functions[name] = shaping_function
    
    def set_status(self, status: RewardStatus) -> None:
        """Set the tracker status.
        
        Args:
            status: New status
        """
        with self._lock:
            self._status = status
    
    def get_status(self) -> RewardStatus:
        """Get current tracker status.
        
        Returns:
            Current status
        """
        with self._lock:
            return self._status
    
    def _shape_reward(
        self,
        raw_reward: float,
        metadata: dict[str, Any],
    ) -> float:
        """Apply reward shaping to raw reward.
        
        Args:
            raw_reward: Raw reward value
            metadata: Additional context
            
        Returns:
            Shaped reward
        """
        if not self._config.enable_reward_shaping:
            return raw_reward
        
        # Apply registered shaping functions if any
        shaped = raw_reward
        for name, func in self._shaping_functions.items():
            shaped = func(shaped, metadata)
        
        return shaped
    
    def _clip_reward(self, reward: float) -> float:
        """Clip reward to configured range.
        
        Args:
            reward: Reward to clip
            
        Returns:
            Clipped reward
        """
        if not self._config.enable_clipping:
            return reward
        
        min_val, max_val = self._config.clip_range
        return max(min_val, min(max_val, reward))


# ---------------------------------------------------------------------------
# Reward Tracking Manager
# ---------------------------------------------------------------------------


class RewardTrackingManager:
    """Manager for reward tracking."""
    
    def __init__(self, config: RewardTrackingConfig | None = None) -> None:
        """Initialize the reward tracking manager.
        
        Args:
            config: Reward tracking configuration
        """
        self._config = config or RewardTrackingConfig()
        self._tracker = RewardTracker(config)
    
    def record_reward(
        self,
        source: RewardSource,
        reward_type: RewardType,
        strategy_id: str,
        action_id: str,
        raw_reward: float,
        metadata: dict[str, Any] | None = None,
        timestamp_ns: int | None = None,
    ) -> RewardEvent:
        """Record a reward.
        
        Args:
            source: Reward source
            reward_type: Reward type
            strategy_id: Strategy ID
            action_id: Action ID
            raw_reward: Raw reward
            metadata: Metadata
            timestamp_ns: Timestamp
            
        Returns:
            Reward event
        """
        return self._tracker.record_reward(
            source, reward_type, strategy_id, action_id, raw_reward, metadata, timestamp_ns
        )
    
    def get_strategy_metrics(self, strategy_id: str) -> RewardMetrics | None:
        """Get strategy metrics.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Strategy metrics
        """
        return self._tracker.get_strategy_metrics(strategy_id)
    
    def analyze_rewards(self, strategy_id: str) -> RewardAnalysis | None:
        """Analyze rewards.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Reward analysis
        """
        return self._tracker.analyze_rewards(strategy_id)


__all__ = [
    "RewardSource",
    "RewardType",
    "RewardStatus",
    "RewardTrackingConfig",
    "RewardEvent",
    "RewardMetrics",
    "RewardBaseline",
    "RewardAnalysis",
    "RewardTracker",
    "RewardTrackingManager",
]
