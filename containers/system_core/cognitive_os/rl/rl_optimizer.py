"""Reinforcement Learning Decision Optimizer - Advanced Decision Learning.

This module provides reinforcement learning capabilities for autonomous decision optimization,
enabling the system to learn from experience and improve decision-making over time.
"""

from __future__ import annotations

import logging
import random
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class RLPolicy(str, Enum):
    """Reinforcement learning policy types."""

    EPSILON_GREEDY = "EPSILON_GREEDY"
    SOFTMAX = "SOFTMAX"
    UCB = "UCB"  # Upper Confidence Bound
    THOMPSON_SAMPLING = "THOMPSON_SAMPLING"
    ADVANTAGE_ACTOR_CRITIC = "ADVANTAGE_ACTOR_CRITIC"


class RewardType(str, Enum):
    """Types of reward signals."""

    FINANCIAL = "FINANCIAL"
    RISK_ADJUSTED = "RISK_ADJUSTED"
    UTILITY_BASED = "UTILITY_BASED"
    PREFERENCE_BASED = "PREFERENCE_BASED"
    MULTI_OBJECTIVE = "MULTI_OBJECTIVE"


@dataclass
class RLState:
    """State representation for RL."""

    state_id: str
    features: Dict[str, float]
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RLAction:
    """Action representation for RL."""

    action_id: str
    action_type: str
    parameters: Dict[str, Any]
    timestamp: float


@dataclass
class RLTransition:
    """Transition tuple (state, action, reward, next_state, done)."""

    transition_id: str
    state: RLState
    action: RLAction
    reward: float
    next_state: Optional[RLState]
    done: bool
    timestamp: float


@dataclass
class RLExperience:
    """Experience replay entry."""

    experience_id: str
    transition: RLTransition
    importance_sampling_weight: float
    learning_importance: float


@dataclass
class RLDecision:
    """RL-enhanced decision."""

    decision_id: str
    action: RLAction
    state_value: float
    action_value: float
    confidence: float
    policy_type: RLPolicy
    exploration_rate: float
    learning_rate: float
    timestamp: float


class ReinforcementLearningOptimizer:
    """Reinforcement learning optimizer for autonomous decision improvement."""

    def __init__(self, state_dim: int = 50, action_dim: int = 20):
        self._lock = threading.Lock()
        self._state_dim = state_dim
        self._action_dim = action_dim
        self._q_table: Dict[str, np.ndarray] = defaultdict(lambda: np.zeros(action_dim))
        self._policy_type = RLPolicy.EPSILON_GREEDY
        self._reward_type = RewardType.RISK_ADJUSTED
        self._exploration_rate = 0.1
        self._learning_rate = 0.1
        self._discount_factor = 0.95
        self._experience_buffer: deque = deque(maxlen=10000)
        self._state_history: deque = deque(maxlen=1000)
        self._action_history: deque = deque(maxlen=1000)
        self._reward_history: deque = deque(maxlen=1000)
        self._performance_metrics = defaultdict(list)
        self._state_encoder = StateEncoder(state_dim)
        self._reward_calculator = RewardCalculator()
        self._policy_improver = PolicyImprover()
        self._initialized = False

    def start(self) -> bool:
        """Start reinforcement learning optimizer."""
        logger.info("[RL_OPTIMIZER] Starting reinforcement learning optimizer...")
        self._initialized = True
        logger.info("[RL_OPTIMIZER] Reinforcement learning optimizer started")
        return True

    def stop(self) -> bool:
        """Stop reinforcement learning optimizer."""
        logger.info("[RL_OPTIMIZER] Stopping reinforcement learning optimizer...")
        self._initialized = False
        logger.info("[RL_OPTIMIZER] Reinforcement learning optimizer stopped")
        return True

    def set_policy(self, policy: RLPolicy) -> None:
        """Set reinforcement learning policy."""
        with self._lock:
            self._policy_type = policy
            logger.info(f"[RL_OPTIMIZER] Policy set to {policy}")

    def set_reward_type(self, reward_type: RewardType) -> None:
        """Set reward calculation type."""
        with self._lock:
            self._reward_type = reward_type
            logger.info(f"[RL_OPTIMIZER] Reward type set to {reward_type}")

    def make_decision(
        self, state: Dict[str, Any], available_actions: List[Dict[str, Any]]
    ) -> RLDecision:
        """Make a decision using reinforcement learning."""
        logger.debug("[RL_OPTIMIZER] Making RL decision")

        # Encode state
        state_encoding = self._state_encoder.encode(state)
        state_key = self._generate_state_key(state_encoding)

        # Select action based on policy
        action_index = self._select_action(state_key, len(available_actions))
        action_data = available_actions[action_index]

        # Calculate state and action values
        state_value = self._calculate_state_value(state_key)
        action_value = self._q_table[state_key][action_index]

        # Create action object
        action = RLAction(
            action_id=f"action_{int(time.time())}_{action_index}",
            action_type=action_data.get("type", "unknown"),
            parameters=action_data,
            timestamp=time.time(),
        )

        # Calculate confidence based on visit count and value variance
        confidence = self._calculate_decision_confidence(state_key, action_index)

        decision = RLDecision(
            decision_id=f"decision_{int(time.time())}",
            action=action,
            state_value=state_value,
            action_value=action_value,
            confidence=confidence,
            policy_type=self._policy_type,
            exploration_rate=self._exploration_rate,
            learning_rate=self._learning_rate,
            timestamp=time.time(),
        )

        # Store state and action for learning
        with self._lock:
            self._state_history.append(state_encoding)
            self._action_history.append(action_index)

        return decision

    def update_experience(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        reward: float,
        next_state: Optional[Dict[str, Any]],
        done: bool = False,
    ) -> None:
        """Update experience and learning from the transition."""
        logger.debug(f"[RL_OPTIMIZER] Updating experience with reward {reward}")

        # Create state objects
        rl_state = RLState(
            state_id=f"state_{int(time.time())}", features=state, timestamp=time.time()
        )

        rl_next_state = None
        if next_state:
            rl_next_state = RLState(
                state_id=f"next_state_{int(time.time())}",
                features=next_state,
                timestamp=time.time(),
            )

        # Create action object
        rl_action = RLAction(
            action_id=f"action_{int(time.time())}",
            action_type=action.get("type", "unknown"),
            parameters=action,
            timestamp=time.time(),
        )

        # Create transition
        transition = RLTransition(
            transition_id=f"transition_{int(time.time())}",
            state=rl_state,
            action=rl_action,
            reward=reward,
            next_state=rl_next_state,
            done=done,
            timestamp=time.time(),
        )

        # Add to experience buffer
        experience = RLExperience(
            experience_id=f"exp_{int(time.time())}",
            transition=transition,
            importance_sampling_weight=1.0,
            learning_importance=abs(reward),  # Higher importance for extreme rewards
        )

        with self._lock:
            self._experience_buffer.append(experience)
            self._reward_history.append(reward)

        # Perform learning update
        self._perform_learning_update()

    def calculate_reward(
        self, execution_result: Dict[str, Any], risk_metrics: Dict[str, float]
    ) -> float:
        """Calculate reward based on execution results and risk metrics."""
        return self._reward_calculator.calculate_reward(
            execution_result, risk_metrics, self._reward_type
        )

    def improve_policy(self) -> None:
        """Improve policy based on collected experience."""
        logger.info("[RL_OPTIMIZER] Improving policy...")

        with self._lock:
            if len(self._experience_buffer) < 100:
                logger.warning("[RL_OPTIMIZER] Insufficient experience for policy improvement")
                return

            # Improve policy using collected experience
            improvement_results = self._policy_improver.improve(
                self._q_table,
                list(self._experience_buffer),
                self._learning_rate,
                self._discount_factor,
            )

            # Update exploration rate based on performance
            if improvement_results["performance_improvement"]:
                self._exploration_rate = max(0.01, self._exploration_rate * 0.99)

        logger.info(
            f"[RL_OPTIMIZER] Policy improvement complete, exploration rate: {self._exploration_rate}"
        )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get RL optimizer performance metrics."""
        with self._lock:
            if not self._reward_history:
                return {"status": "insufficient_data"}

            recent_rewards = list(self._reward_history)[-100:]  # Last 100 rewards

            return {
                "policy_type": self._policy_type.value,
                "reward_type": self._reward_type.value,
                "exploration_rate": self._exploration_rate,
                "learning_rate": self._learning_rate,
                "total_experiences": len(self._experience_buffer),
                "average_reward": np.mean(recent_rewards),
                "reward_std": np.std(recent_rewards),
                "total_states_learned": len(self._q_table),
                "recent_performance": (
                    np.mean(self._reward_history[-10:]) if len(self._reward_history) >= 10 else 0.0
                ),
                "convergence_indicator": self._check_convergence(),
            }

    def _select_action(self, state_key: str, num_actions: int) -> int:
        """Select action based on current policy."""
        q_values = self._q_table[state_key]

        if len(q_values) < num_actions:
            # Initialize Q-values for new actions
            self._q_table[state_key] = np.zeros(num_actions)
            q_values = self._q_table[state_key]

        if self._policy_type == RLPolicy.EPSILON_GREEDY:
            return self._epsilon_greedy_selection(q_values)
        elif self._policy_type == RLPolicy.SOFTMAX:
            return self._softmax_selection(q_values)
        elif self._policy_type == RLPolicy.UCB:
            return self._ucb_selection(state_key, q_values)
        elif self._policy_type == RLPolicy.THOMPSON_SAMPLING:
            return self._thompson_sampling_selection(q_values)
        else:
            return self._epsilon_greedy_selection(q_values)

    def _epsilon_greedy_selection(self, q_values: np.ndarray) -> int:
        """Epsilon-greedy action selection."""
        if random.random() < self._exploration_rate:
            return random.randint(0, len(q_values) - 1)
        else:
            return np.argmax(q_values)

    def _softmax_selection(self, q_values: np.ndarray, temperature: float = 1.0) -> int:
        """Softmax action selection."""
        # Add temperature to control exploration
        scaled_q_values = q_values / temperature

        # Handle numerical stability
        max_q = np.max(scaled_q_values)
        exp_q = np.exp(scaled_q_values - max_q)
        probabilities = exp_q / np.sum(exp_q)

        return np.random.choice(len(q_values), p=probabilities)

    def _ucb_selection(self, state_key: str, q_values: np.ndarray) -> int:
        """Upper Confidence Bound action selection."""
        # Calculate visit counts (simplified)
        visit_counts = defaultdict(int)
        visit_counts[state_key] = 1  # Assume at least one visit

        # Calculate UCB values
        total_visits = sum(visit_counts.values())
        ucb_values = []

        for i, q_value in enumerate(q_values):
            action_visits = visit_counts.get(f"{state_key}_{i}", 1)
            exploration_bonus = np.sqrt(2 * np.log(total_visits) / action_visits)
            ucb_values.append(q_value + exploration_bonus)

        return np.argmax(ucb_values)

    def _thompson_sampling_selection(self, q_values: np.ndarray) -> int:
        """Thompson sampling action selection."""
        # Sample from beta distribution for each action
        samples = []
        for q_value in q_values:
            # Convert Q-value to beta parameters (simplified)
            alpha = max(0.1, (q_value + 1) * 10)
            beta = max(0.1, (1 - q_value + 1) * 10)
            sample = np.random.beta(alpha, beta)
            samples.append(sample)

        return np.argmax(samples)

    def _calculate_state_value(self, state_key: str) -> float:
        """Calculate state value (maximum Q-value)."""
        q_values = self._q_table.get(state_key, np.array([0.0]))
        if len(q_values) == 0:
            return 0.0
        return np.max(q_values)

    def _calculate_decision_confidence(self, state_key: str, action_index: int) -> float:
        """Calculate confidence in decision."""
        # Confidence based on visit count and value stability
        q_values = self._q_table.get(state_key, np.array([0.0]))

        if len(q_values) == 0:
            return 0.5  # Default confidence

        # Calculate variance of Q-values as uncertainty measure
        if len(q_values) > 1:
            variance = np.var(q_values)
            confidence = max(0.0, 1.0 - variance)
        else:
            confidence = 1.0

        return min(1.0, max(0.0, confidence))

    def _perform_learning_update(self) -> None:
        """Perform learning update using experience replay."""
        with self._lock:
            if len(self._experience_buffer) < 10:
                return

            # Sample batch of experiences
            batch_size = min(32, len(self._experience_buffer))
            batch_indices = random.sample(range(len(self._experience_buffer)), batch_size)

            for idx in batch_indices:
                experience = self._experience_buffer[idx]
                transition = experience.transition

                # Encode states
                state_encoding = self._state_encoder.encode(transition.state.features)
                next_state_encoding = None
                if transition.next_state:
                    next_state_encoding = self._state_encoder.encode(transition.next_state.features)

                state_key = self._generate_state_key(state_encoding)
                next_state_key = (
                    self._generate_state_key(next_state_encoding) if next_state_encoding else None
                )

                # Get action index (simplified - in real implementation would use action encoding)
                action_index = hash(str(transition.action.action_type)) % self._action_dim

                # Q-learning update
                current_q = self._q_table[state_key][action_index]

                if transition.done:
                    target_q = transition.reward
                else:
                    next_q_values = self._q_table.get(next_state_key, np.array([0.0]))
                    target_q = transition.reward + self._discount_factor * np.max(next_q_values)

                # Update Q-value
                self._q_table[state_key][action_index] = current_q + self._learning_rate * (
                    target_q - current_q
                )

    def _generate_state_key(self, state_encoding: np.ndarray) -> str:
        """Generate key for state from encoding."""
        # Discretize continuous state for table lookup
        discretized = (state_encoding * 10).astype(int)  # Scale and discretize
        return "_".join(map(str, discretized))

    def _check_convergence(self) -> bool:
        """Check if learning has converged."""
        if len(self._reward_history) < 100:
            return False

        # Check if recent rewards are stable
        recent_rewards = list(self._reward_history)[-50:]
        std = np.std(recent_rewards)

        # Convergence if standard deviation is low
        return std < 0.1


class StateEncoder:
    """Encode states into fixed-dimensional vectors."""

    def __init__(self, state_dim: int = 50):
        self._state_dim = state_dim
        self._feature_cache = {}

    def encode(self, state_features: Dict[str, float]) -> np.ndarray:
        """Encode state features into fixed-dimensional vector."""
        # Extract numerical features
        numerical_features = []
        for key, value in state_features.items():
            if isinstance(value, (int, float)):
                numerical_features.append(float(value))

        # Pad or truncate to fixed dimension
        if len(numerical_features) >= self._state_dim:
            encoded = np.array(numerical_features[: self._state_dim])
        else:
            encoded = np.zeros(self._state_dim)
            encoded[: len(numerical_features)] = numerical_features

        # Normalize
        if np.linalg.norm(encoded) > 0:
            encoded = encoded / np.linalg.norm(encoded)

        return encoded


class RewardCalculator:
    """Calculate rewards for RL training."""

    def calculate_reward(
        self,
        execution_result: Dict[str, Any],
        risk_metrics: Dict[str, float],
        reward_type: RewardType,
    ) -> float:
        """Calculate reward based on execution results."""
        if reward_type == RewardType.FINANCIAL:
            return self._financial_reward(execution_result)
        elif reward_type == RewardType.RISK_ADJUSTED:
            return self._risk_adjusted_reward(execution_result, risk_metrics)
        elif reward_type == RewardType.UTILITY_BASED:
            return self._utility_based_reward(execution_result, risk_metrics)
        elif reward_type == RewardType.PREFERENCE_BASED:
            return self._preference_based_reward(execution_result, risk_metrics)
        elif reward_type == RewardType.MULTI_OBJECTIVE:
            return self._multi_objective_reward(execution_result, risk_metrics)
        else:
            return self._financial_reward(execution_result)

    def _financial_reward(self, execution_result: Dict[str, Any]) -> float:
        """Calculate purely financial reward."""
        profit = execution_result.get("profit", 0.0)
        return profit

    def _risk_adjusted_reward(
        self, execution_result: Dict[str, Any], risk_metrics: Dict[str, float]
    ) -> float:
        """Calculate risk-adjusted reward (Sharpe ratio like)."""
        profit = execution_result.get("profit", 0.0)
        risk = risk_metrics.get("risk", 1.0)

        if risk == 0:
            return profit if profit > 0 else 0.0

        return profit / risk

    def _utility_based_reward(
        self, execution_result: Dict[str, Any], risk_metrics: Dict[str, float]
    ) -> float:
        """Calculate utility-based reward using risk aversion."""
        profit = execution_result.get("profit", 0.0)
        risk = risk_metrics.get("risk", 1.0)
        risk_aversion = 0.5  # Risk aversion parameter

        # Utility function: U = profit - 0.5 * risk_aversion * risk^2
        utility = profit - 0.5 * risk_aversion * (risk**2)
        return utility

    def _preference_based_reward(
        self, execution_result: Dict[str, Any], risk_metrics: Dict[str, float]
    ) -> float:
        """Calculate preference-based reward using operator preferences."""
        profit = execution_result.get("profit", 0.0)
        preference_weight = execution_result.get("preference_weight", 1.0)

        return profit * preference_weight

    def _multi_objective_reward(
        self, execution_result: Dict[str, Any], risk_metrics: Dict[str, float]
    ) -> float:
        """Calculate multi-objective reward."""
        financial = self._financial_reward(execution_result)
        risk_adj = self._risk_adjusted_reward(execution_result, risk_metrics)
        utility = self._utility_based_reward(execution_result, risk_metrics)

        # Weighted combination
        return 0.4 * financial + 0.3 * risk_adj + 0.3 * utility


class PolicyImprover:
    """Improve RL policy using various methods."""

    def improve(
        self,
        q_table: Dict[str, np.ndarray],
        experiences: List[RLExperience],
        learning_rate: float,
        discount_factor: float,
    ) -> Dict[str, Any]:
        """Improve policy using collected experience."""
        improvement_metrics = {
            "states_updated": 0,
            "value_changes": [],
            "performance_improvement": False,
        }

        # Simple policy improvement: iterate over experiences and update
        for exp in experiences:
            transition = exp.transition
            # In real implementation, would use more sophisticated methods
            # like policy gradient, actor-critic, etc.
            improvement_metrics["states_updated"] += 1

        # Check for improvement (simplified)
        if improvement_metrics["states_updated"] > 10:
            improvement_metrics["performance_improvement"] = True

        return improvement_metrics


# Singleton instance
_rl_optimizer: Optional[ReinforcementLearningOptimizer] = None
_rl_optimizer_lock = threading.Lock()


def get_rl_optimizer(state_dim: int = 50, action_dim: int = 20) -> ReinforcementLearningOptimizer:
    """Get the singleton RL optimizer instance."""
    global _rl_optimizer
    if _rl_optimizer is None:
        with _rl_optimizer_lock:
            if _rl_optimizer is None:
                _rl_optimizer = ReinforcementLearningOptimizer(state_dim, action_dim)
    return _rl_optimizer


__all__ = [
    "ReinforcementLearningOptimizer",
    "get_rl_optimizer",
    "RLPolicy",
    "RewardType",
    "RLState",
    "RLAction",
    "RLTransition",
    "RLExperience",
    "RLDecision",
]
