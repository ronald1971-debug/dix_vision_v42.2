"""Closed Feedback Loop — INT-07.01.

Implementation of closed feedback loops for the intelligence engine
to enable continuous learning and adaptation. Integrates execution
feedback, market context, and performance metrics to improve
decision-making over time.
"""

from __future__ import annotations

import dataclasses
import enum
from collections import deque
from collections.abc import Callable
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_FEEDBACK_WINDOW_SIZE: Final[int] = 1000
DEFAULT_LEARNING_RATE: Final[float] = 0.01
DEFAULT_EXPLORATION_RATE: Final[float] = 0.1
DEFAULT_ENABLE_ADAPTIVE_LEARNING: Final[bool] = True
DEFAULT_FEEDBACK_DELAY_TOLERANCE_MS: Final[int] = 1000

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class FeedbackType(enum.Enum):
    """Types of feedback in the closed loop."""
    EXECUTION_RESULT = "EXECUTION_RESULT"
    MARKET_STATE_CHANGE = "MARKET_STATE_CHANGE"
    STRATEGY_PERFORMANCE = "STRATEGY_PERFORMANCE"
    RISK_EVENT = "RISK_EVENT"
    SYSTEM_EVENT = "SYSTEM_EVENT"
    USER_CORRECTION = "USER_CORRECTION"
    EXTERNAL_SIGNAL = "EXTERNAL_SIGNAL"


class FeedbackQuality(enum.Enum):
    """Quality levels for feedback signals."""
    HIGH = "HIGH"  # Reliable, high-confidence feedback
    MEDIUM = "MEDIUM"  # Moderately reliable feedback
    LOW = "LOW"  # Low-confidence or noisy feedback
    UNKNOWN = "UNKNOWN"  # Unknown quality


class LearningMode(enum.Enum):
    """Learning modes for the feedback loop."""
    ONLINE = "ONLINE"  # Real-time learning
    BATCH = "BATCH"  - Batch learning from accumulated data
    REINFORCEMENT = "REINFORCEMENT"  # RL-based learning
    SUPERVISED = "SUPERVISED"  # Supervised learning
    HYBRID = "HYBRID"  - Combination of multiple modes


class LoopState(enum.Enum):
    """States of the feedback loop."""
    IDLE = "IDLE"
    COLLECTING = "COLLECTING"
    PROCESSING = "PROCESSING"
    UPDATING = "UPDATING"
    EVALUATING = "EVALUATING"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class FeedbackLoopConfig:
    """Configuration for the closed feedback loop."""
    feedback_window_size: int = DEFAULT_FEEDBACK_WINDOW_SIZE
    learning_rate: float = DEFAULT_LEARNING_RATE
    exploration_rate: float = DEFAULT_EXPLORATION_RATE
    enable_adaptive_learning: bool = DEFAULT_ENABLE_ADAPTIVE_LEARNING
    feedback_delay_tolerance_ms: int = DEFAULT_FEEDBACK_DELAY_TOLERANCE_MS
    learning_mode: LearningMode = LearningMode.HYBRID
    enable_reward_shaping: bool = True
    enable_experience_replay: bool = True

    def __post_init__(self) -> None:
        if self.feedback_window_size < 1:
            raise ValueError("feedback_window_size must be >= 1")
        if not (0.0 <= self.learning_rate <= 1.0):
            raise ValueError("learning_rate must be in [0.0, 1.0]")
        if not (0.0 <= self.exploration_rate <= 1.0):
            raise ValueError("exploration_rate must be in [0.0, 1.0]")


@dataclasses.dataclass(frozen=True, slots=True)
class FeedbackSignal:
    """A feedback signal in the closed loop."""
    signal_id: str
    feedback_type: FeedbackType
    quality: FeedbackQuality
    timestamp_ns: int
    source: str
    data: dict[str, Any]
    reward: float = 0.0
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.signal_id:
            raise ValueError("signal_id must be non-empty")
        if not self.source:
            raise ValueError("source must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class DecisionContext:
    """Context around a decision made by the intelligence engine."""
    decision_id: str
    action: str
    state: dict[str, Any]
    timestamp_ns: int
    expected_outcome: dict[str, Any] | None = None
    confidence: float = 0.0
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class FeedbackResult:
    """Result of processing feedback."""
    result_id: str
    feedback_signal: FeedbackSignal
    decision_context: DecisionContext | None
    learning_update: dict[str, Any] | None = None
    new_policy_state: dict[str, Any] | None = None
    performance_delta: float = 0.0
    timestamp_ns: int = 0
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class LoopMetrics:
    """Metrics about the feedback loop performance."""
    total_signals: int
    signals_by_type: dict[str, int]
    signals_by_quality: dict[str, int]
    total_updates: int
    average_update_delay_ms: float
    learning_iterations: int
    convergence_rate: float
    policy_changes: int
    reward_accumulated: float
    average_reward: float
    exploration_exploitation_ratio: float


# ---------------------------------------------------------------------------
# Closed Feedback Loop
# ---------------------------------------------------------------------------


class ClosedFeedbackLoop:
    """Closed feedback loop for intelligence engine learning.
    
    Implements a comprehensive feedback system that:
    - Collects feedback from multiple sources (execution, market, risk, user)
    - Processes feedback to extract learning signals
    - Updates policies and strategies based on feedback
    - Evaluates the impact of updates
    - Maintains performance metrics and convergence tracking
    
    The loop supports multiple learning modes (online, batch, reinforcement)
    and can adapt its learning parameters based on feedback quality
    and system performance.
    """
    
    def __init__(
        self,
        config: FeedbackLoopConfig | None = None,
    ) -> None:
        """Initialize the closed feedback loop.
        
        Args:
            config: Feedback loop configuration
        """
        self._config = config or FeedbackLoopConfig()
        self._lock = Lock()
        
        # Feedback storage
        self._feedback_signals: deque[FeedbackSignal] = deque(
            maxlen=self._config.feedback_window_size
        )
        self._decision_contexts: deque[DecisionContext] = deque(
            maxlen=self._config.feedback_window_size
        )
        
        # Policy state
        self._policy_state: dict[str, Any] = {}
        
        # Learning parameters
        self._current_learning_rate = self._config.learning_rate
        self._current_exploration_rate = self._config.exploration_rate
        
        # State management
        self._loop_state = LoopState.IDLE
        
        # Event handlers
        self._feedback_handlers: list[Callable[[FeedbackSignal], None]] = []
        self._update_handlers: list[Callable[dict[str, Any]], None]] = []
        
        # Metrics
        self._metrics = self._init_metrics()
        self._update_delays: deque[int] = deque(maxlen=100)
        self._rewards: deque[float] = deque(maxlen=1000)
        self._learning_iterations = 0
    
    def add_feedback_signal(
        self,
        signal: FeedbackSignal,
    ) -> None:
        """Add a feedback signal to the loop.
        
        Args:
            signal: Feedback signal to add
        """
        with self._lock:
            self._feedback_signals.append(signal)
            self._metrics.total_signals += 1
            self._metrics.signals_by_type[signal.feedback_type.value] = \
                self._metrics.signals_by_type.get(signal.feedback_type.value, 0) + 1
            self._metrics.signals_by_quality[signal.quality.value] = \
                self._metrics.signals_by_quality.get(signal.quality.value, 0) + 1
            
            # Track reward
            if signal.reward != 0.0:
                self._rewards.append(signal.reward)
                self._metrics.reward_accumulated += signal.reward
                if len(self._rewards) > 0:
                    self._metrics.average_reward = sum(self._rewards) / len(self._rewards)
            
            # Notify handlers
            for handler in self._feedback_handlers:
                try:
                    handler(signal)
                except Exception:
                    pass
        
        # Trigger processing if in COLLECTING state
        if self._loop_state == LoopState.COLLECTING:
            self.process_feedback()
    
    def add_decision_context(
        self,
        context: DecisionContext,
    ) -> None:
        """Add a decision context to the loop.
        
        Args:
            context: Decision context
        """
        with self._lock:
            self._decision_contexts.append(context)
    
    def start_collection(self) -> None:
        """Start collecting feedback signals."""
        with self._lock:
            self._loop_state = LoopState.COLLECTING
    
    def stop_collection(self) -> None:
        """Stop collecting feedback signals."""
        with self._lock:
            self._loop_state = LoopState.IDLE
    
    def process_feedback(self) -> FeedbackResult | None:
        """Process accumulated feedback and generate updates.
        
        Returns:
            Feedback result or None if no feedback to process
        """
        import time
        import secrets
        
        with self._lock:
            if not self._feedback_signals:
                return None
            
            self._loop_state = LoopState.PROCESSING
            
            # Get most recent feedback
            recent_signal = self._feedback_signals[-1]
            
            # Get matching decision context if available
            matching_context = self._find_matching_context(recent_signal)
            
            # Generate learning update
            learning_update = self._generate_learning_update(recent_signal, matching_context)
            
            # Apply update to policy
            if learning_update:
                new_policy_state = self._apply_learning_update(learning_update)
            else:
                new_policy_state = None
            
            # Calculate performance delta
            performance_delta = self._calculate_performance_delta(recent_signal)
            
            # Update exploration/exploitation if adaptive learning enabled
            if self._config.enable_adaptive_learning:
                self._adapt_learning_parameters()
            
            result = FeedbackResult(
                result_id=secrets.token_hex(16),
                feedback_signal=recent_signal,
                decision_context=matching_context,
                learning_update=learning_update,
                new_policy_state=new_policy_state,
                performance_delta=performance_delta,
                timestamp_ns=time.time_ns(),
            )
            
            self._loop_state = LoopState.EVALUATING
            
            # Track update delay
            if matching_context:
                delay_ms = (recent_signal.timestamp_ns - matching_context.timestamp_ns) / 1_000_000
                self._update_delays.append(delay_ms)
                if len(self._update_delays) > 0:
                    self._metrics.average_update_delay_ms = sum(self._update_delays) / len(self._update_delays)
            
            return result
    
    def evaluate_updates(self) -> dict[str, Any]:
        """Evaluate the impact of recent updates.
        
        Returns:
            Evaluation results
        """
        with self._lock:
            # Calculate convergence rate
            convergence_rate = self._calculate_convergence_rate()
            
            # Calculate exploration/exploitation ratio
            exploration_exploitation_ratio = (
                self._current_exploration_rate / (1.0 - self._current_exploration_rate)
                if self._current_exploration_rate < 1.0
                else float('inf')
            )
            
            return {
                "convergence_rate": convergence_rate,
                "exploration_exploitation_ratio": exploration_exploitation_ratio,
                "learning_rate": self._current_learning_rate,
                "exploration_rate": self._current_exploration_rate,
                "policy_changes": self._metrics.policy_changes,
                "total_updates": self._metrics.total_updates,
            }
    
    def get_policy_state(self) -> dict[str, Any]:
        """Get the current policy state.
        
        Returns:
            Current policy state
        """
        with self._lock:
            return dict(self._policy_state)
    
    def get_metrics(self) -> LoopMetrics:
        """Get feedback loop metrics.
        
        Returns:
            Current metrics
        """
        with self._lock:
            # Calculate exploration/exploitation ratio
            exploration_exploitation_ratio = (
                self._current_exploration_rate / (1.0 - self._current_exploration_rate)
                if self._current_exploration_rate < 1.0
                else float('inf')
            )
            
            return dataclasses.replace(
                self._metrics,
                learning_iterations=self._learning_iterations,
                convergence_rate=self._calculate_convergence_rate(),
                exploration_exploitation_ratio=exploration_exploitation_ratio,
            )
    
    def register_feedback_handler(
        self,
        handler: Callable[[FeedbackSignal], None],
    ) -> None:
        """Register a feedback signal handler.
        
        Args:
            handler: Handler callable
        """
        with self._lock:
            self._feedback_handlers.append(handler)
    
    def register_update_handler(
        self,
        handler: Callable[[dict[str, Any]], None],
    ) -> None:
        """Register a policy update handler.
        
        Args:
            handler: Handler callable
        """
        with self._lock:
            self._update_handlers.append(handler)
    
    def _find_matching_context(
        self,
        signal: FeedbackSignal,
    ) -> DecisionContext | None:
        """Find decision context matching a feedback signal.
        
        Args:
            signal: Feedback signal
            
        Returns:
            Matching context or None
        """
        # Simple matching based on time proximity (can be enhanced)
        for context in reversed(self._decision_contexts):
            time_diff = abs(signal.timestamp_ns - context.timestamp_ns)
            if time_diff < self._config.feedback_delay_tolerance_ms * 1_000_000:
                return context
        return None
    
    def _generate_learning_update(
        self,
        signal: FeedbackSignal,
        context: DecisionContext | None,
    ) -> dict[str, Any] | None:
        """Generate a learning update from feedback.
        
        Args:
            signal: Feedback signal
            context: Decision context
            
        Returns:
            Learning update or None
        """
        import time
        
        if signal.quality == FeedbackQuality.LOW:
            return None
        
        update = {
            "signal_id": signal.signal_id,
            "feedback_type": signal.feedback_type.value,
            "learning_rate": self._current_learning_rate,
            "timestamp_ns": time.time_ns(),
        }
        
        if context:
            update["decision_id"] = context.decision_id
            update["action"] = context.action
            update["confidence"] = context.confidence
            update["expected_outcome"] = context.expected_outcome
            update["actual_outcome"] = signal.data
        
        # Reward shaping if enabled
        if self._config.enable_reward_shaping and signal.reward != 0.0:
            update["reward"] = signal.reward
            update["shaped_reward"] = self._shape_reward(signal.reward, context)
        
        return update
    
    def _apply_learning_update(
        self,
        update: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply a learning update to the policy.
        
        Args:
            update: Learning update
            
        Returns:
            New policy state
        """
        import time
        
        # Simple policy update (actual implementation would be more sophisticated)
        new_policy_state = dict(self._policy_state)
        
        # Update based on learning rate and signal
        for key, value in update.items():
            if key in ["signal_id", "timestamp_ns", "feedback_type"]:
                continue
            if isinstance(value, (int, float)):
                current_value = new_policy_state.get(key, 0.0)
                new_value = current_value + (value - current_value) * self._current_learning_rate
                new_policy_state[key] = new_value
        
        self._policy_state = new_policy_state
        self._metrics.total_updates += 1
        self._metrics.policy_changes += 1
        self._learning_iterations += 1
        
        # Notify update handlers
        for handler in self._update_handlers:
            try:
                handler(new_policy_state)
            except Exception:
                pass
        
        return new_policy_state
    
    def _calculate_performance_delta(self, signal: FeedbackSignal) -> float:
        """Calculate performance delta from feedback signal.
        
        Args:
            signal: Feedback signal
            
        Returns:
            Performance delta
        """
        if signal.reward != 0.0:
            return signal.reward
        
        # Alternative performance calculation
        if "performance" in signal.data:
            return float(signal.data["performance"])
        
        return 0.0
    
    def _shape_reward(
        self,
        reward: float,
        context: DecisionContext | None,
    ) -> float:
        """Apply reward shaping to the raw reward.
        
        Args:
            reward: Raw reward
            context: Decision context
            
        Returns:
            Shaped reward
        """
        shaped = reward
        
        # Shaping based on confidence
        if context and context.confidence < 0.5:
            shaped *= 0.8  # Reduce reward for low-confidence decisions
        
        # Shaping based on signal quality
        # (would use signal.quality if available)
        
        return shaped
    
    def _adapt_learning_parameters(self) -> None:
        """Adapt learning parameters based on performance."""
        if len(self._rewards) < 10:
            return
        
        # Calculate average recent reward
        recent_rewards = list(self._rewards)[-10:]
        avg_reward = sum(recent_rewards) / len(recent_rewards)
        
        # Adapt learning rate
        if avg_reward > 0:
            # Good performance, reduce exploration
            self._current_exploration_rate = max(
                0.01, self._current_exploration_rate * 0.99
            )
        else:
            # Poor performance, increase exploration
            self._current_exploration_rate = min(
                0.5, self._current_exploration_rate * 1.01
            )
        
        # Adapt learning rate based on convergence
        convergence = self._calculate_convergence_rate()
        if convergence < 0.01:
            # Converging, reduce learning rate
            self._current_learning_rate = max(
                0.001, self._current_learning_rate * 0.99
            )
        elif convergence > 0.1:
            # Not converging, increase learning rate
            self._current_learning_rate = min(
                0.1, self._current_learning_rate * 1.01
            )
    
    def _calculate_convergence_rate(self) -> float:
        """Calculate the convergence rate of the policy.
        
        Returns:
            Convergence rate
        """
        if len(self._rewards) < 20:
            return 0.0
        
        # Calculate variance in recent rewards as convergence indicator
        recent_rewards = list(self._rewards)[-20:]
        avg_reward = sum(recent_rewards) / len(recent_rewards)
        variance = sum((r - avg_reward) ** 2 for r in recent_rewards) / len(recent_rewards)
        
        # Lower variance indicates convergence
        convergence = 1.0 / (1.0 + variance)
        
        return convergence
    
    def _init_metrics(self) -> LoopMetrics:
        """Initialize loop metrics."""
        return LoopMetrics(
            total_signals=0,
            signals_by_type={},
            signals_by_quality={},
            total_updates=0,
            average_update_delay_ms=0.0,
            learning_iterations=0,
            convergence_rate=0.0,
            policy_changes=0,
            reward_accumulated=0.0,
            average_reward=0.0,
            exploration_exploitation_ratio=self._config.exploration_rate / (1.0 - self._config.exploration_rate),
        )


# ---------------------------------------------------------------------------
# Closed Feedback Loop Manager
# ---------------------------------------------------------------------------


class ClosedFeedbackLoopManager:
    """Manager for closed feedback loops."""
    
    def __init__(self, config: FeedbackLoopConfig | None = None) -> None:
        """Initialize the closed feedback loop manager.
        
        Args:
            config: Feedback loop configuration
        """
        self._config = config or FeedbackLoopConfig()
        self._loop = ClosedFeedbackLoop(config)
    
    def add_feedback_signal(self, signal: FeedbackSignal) -> None:
        """Add a feedback signal.
        
        Args:
            signal: Feedback signal
        """
        self._loop.add_feedback_signal(signal)
    
    def add_decision_context(self, context: DecisionContext) -> None:
        """Add a decision context.
        
        Args:
            context: Decision context
        """
        self._loop.add_decision_context(context)
    
    def process_feedback(self) -> FeedbackResult | None:
        """Process accumulated feedback.
        
        Returns:
            Feedback result or None
        """
        return self._loop.process_feedback()
    
    def get_policy_state(self) -> dict[str, Any]:
        """Get current policy state.
        
        Returns:
            Policy state
        """
        return self._loop.get_policy_state()
    
    def get_metrics(self) -> LoopMetrics:
        """Get metrics.
        
        Returns:
            Current metrics
        """
        return self._loop.get_metrics()


__all__ = [
    "FeedbackType",
    "FeedbackQuality",
    "LearningMode",
    "LoopState",
    "FeedbackLoopConfig",
    "FeedbackSignal",
    "DecisionContext",
    "FeedbackResult",
    "LoopMetrics",
    "ClosedFeedbackLoop",
    "ClosedFeedbackLoopManager",
]
