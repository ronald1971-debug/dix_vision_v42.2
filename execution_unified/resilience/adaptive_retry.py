"""
execution_unified.resilience.adaptive_retry
DIX VISION v42.2 — Enhanced Adaptive Retry Strategy with World Context

Provides intelligent retry strategies for transient failures with world context integration.
Phase 12.1: Enhanced Execution System - World-aware retry capabilities.

Enhanced with world context integration (Phase 12.1):
- Intelligent retry decision making with confidence scoring
- World-aware retry strategy selection
- Exponential backoff with jitter
- Retry budget management
- Retry success prediction
- Deadlock prevention
- Retry performance monitoring
"""

from __future__ import annotations

import logging
import threading
import time
import random
import hashlib
from datetime import datetime
from typing import Callable, Optional, TypeVar, Any, List, Dict, Tuple
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import deque

# World context integration (Phase 12.1 enhancement)
try:
    from world_model.indicator_integration import get_integration_bridge
    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class WorldContext:
    """World context for retry strategy with enhanced metadata."""
    
    market_regime: str = "unknown"
    market_trend: str = "unknown"
    volatility_regime: str = "unknown"
    liquidity_state: str = "unknown"
    agent_activity: Dict[str, float] = field(default_factory=dict)
    causal_factors: List[str] = field(default_factory=list)
    prediction_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


T = TypeVar('T')

T = TypeVar('T')


class RetryPolicy(Enum):
    """Retry policy types."""
    EXPONENTIAL_BACKOFF = "EXPONENTIAL_BACKOFF"
    LINEAR_BACKOFF = "LINEAR_BACKOFF"
    FIXED_DELAY = "FIXED_DELAY"
    JITTERED_BACKOFF = "JITTERED_BACKOFF"


@dataclass
class RetryConfig:
    """Enhanced retry configuration with world-aware parameters (Phase 12.1)."""
    
    max_attempts: int = 3
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    policy: RetryPolicy = RetryPolicy.EXPONENTIAL_BACKOFF
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.1  # For jittered backoff
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,)
    # Phase 12.1 enhancements
    world_aware: bool = True  # Enable world-aware retry decisions
    retry_budget: int = 100  # Maximum retry operations per window
    confidence_threshold: float = 0.3  # Minimum confidence to retry


@dataclass
class RetryResult:
    """Enhanced result of retry attempt with world context (Phase 12.1)."""
    
    success: bool
    attempts: int
    total_time_ms: float
    result: Optional[T] = None
    last_error: Optional[Exception] = None
    retry_delays: List[float] = field(default_factory=list)
    confidence_score: float = 0.0  # Phase 12.1 enhancement
    world_context: Optional[WorldContext] = None  # Phase 12.1 enhancement
    predicted_success_probability: float = 0.0  # Phase 12.1 enhancement


class SuccessPredictor:
    """Predicts retry success probability based on world context (Phase 12.1)."""
    
    def __init__(self):
        self._history: deque = deque(maxlen=100)
        self._operation_stats: Dict[str, Dict[str, float]] = {}
    
    def predict_success(
        self,
        operation: str,
        attempt: int,
        world_context: Optional[WorldContext]
    ) -> float:
        """Predict success probability for retry attempt."""
        # Base success probability
        base_success = 0.5 / attempt  # Decreases with attempts
        
        # Adjust based on world context
        if world_context:
            if world_context.volatility_regime == "high":
                base_success *= 0.8  # Lower success in high volatility
            elif world_context.volatility_regime == "low":
                base_success *= 1.2  # Higher success in low volatility
            
            if world_context.liquidity_state == "low":
                base_success *= 0.9  # Lower success in low liquidity
        
        # Get historical success rate for this operation
        op_stats = self._operation_stats.get(operation, {"attempts": 0, "successes": 0})
        if op_stats["attempts"] > 0:
            historical_success = op_stats["successes"] / op_stats["attempts"]
            base_success = (base_success + historical_success) / 2
        
        return min(1.0, max(0.0, base_success))
    
    def record_outcome(self, operation: str, success: bool) -> None:
        """Record operation outcome for learning."""
        if operation not in self._operation_stats:
            self._operation_stats[operation] = {"attempts": 0, "successes": 0}
        
        self._operation_stats[operation]["attempts"] += 1
        if success:
            self._operation_stats[operation]["successes"] += 1


class RetryStrategy(ABC):
    """Abstract retry strategy."""
    
    @abstractmethod
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if should retry."""
        pass
    
    @abstractmethod
    def get_delay_ms(self, attempt: int) -> float:
        """Get delay before next retry."""
        pass


class ExponentialBackoffStrategy(RetryStrategy):
    """Exponential backoff retry strategy."""
    
    def __init__(self, config: RetryConfig):
        self._config = config
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        return attempt < self._config.max_attempts and isinstance(error, self._config.retryable_exceptions)
    
    def get_delay_ms(self, attempt: int) -> float:
        delay = self._config.base_delay_ms * (self._config.backoff_multiplier ** attempt)
        return min(delay, self._config.max_delay_ms)


class LinearBackoffStrategy(RetryStrategy):
    """Linear backoff retry strategy."""
    
    def __init__(self, config: RetryConfig):
        self._config = config
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        return attempt < self._config.max_attempts and isinstance(error, self._config.retryable_exceptions)
    
    def get_delay_ms(self, attempt: int) -> float:
        delay = self._config.base_delay_ms + (attempt * self._config.base_delay_ms)
        return min(delay, self._config.max_delay_ms)


class FixedDelayStrategy(RetryStrategy):
    """Fixed delay retry strategy."""
    
    def __init__(self, config: RetryConfig):
        self._config = config
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        return attempt < self._config.max_attempts and isinstance(error, self._config.retryable_exceptions)
    
    def get_delay_ms(self, attempt: int) -> float:
        return min(self._config.base_delay_ms, self._config.max_delay_ms)


class JitteredBackoffStrategy(RetryStrategy):
    """Jittered backoff retry strategy (exponential with randomness)."""
    
    def __init__(self, config: RetryConfig):
        self._config = config
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        return attempt < self._config.max_attempts and isinstance(error, self._config.retryable_exceptions)
    
    def get_delay_ms(self, attempt: int) -> float:
        # Exponential backoff with jitter
        base_delay = self._config.base_delay_ms * (self._config.backoff_multiplier ** attempt)
        jitter = base_delay * self._config.jitter_factor * random.random()
        delay = base_delay + jitter
        return min(delay, self._config.max_delay_ms)


class AdaptiveRetryStrategy:
    """
    Enhanced adaptive retry strategy with world context integration (Phase 12.1).
    
    This strategy monitors success rates, adapts the retry policy based on 
    historical performance, and incorporates world context for intelligent
    retry decision making.
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self._config = config or RetryConfig()
        self._lock = threading.Lock()
        
        # Performance tracking
        self._policy_performance: Dict[RetryPolicy, dict[str, float]] = {
            RetryPolicy.EXPONENTIAL_BACKOFF: {"success_rate": 0.0, "attempts": 0},
            RetryPolicy.LINEAR_BACKOFF: {"success_rate": 0.0, "attempts": 0},
            RetryPolicy.FIXED_DELAY: {"success_rate": 0.0, "attempts": 0},
            RetryPolicy.JITTERED_BACKOFF: {"success_rate": 0.0, "attempts": 0},
        }
        
        self._current_strategy: RetryStrategy = self._create_strategy(self._config.policy)
        
        # Phase 12.1 enhancements
        self._world_integration_bridge = None
        self._current_world_context: Optional[WorldContext] = None
        self._success_predictor = SuccessPredictor()
        self._retry_budget_remaining = self._config.retry_budget
        self._retry_history: deque = deque(maxlen=200)
        self._operation_name: str = "default"
        
        if WORLD_MODEL_AVAILABLE and self._config.world_aware:
            self._init_world_integration()
        
        logger.info(f"[ADAPTIVE_RETRY] Initialized with policy: {self._config.policy}, world_aware: {self._config.world_aware}")
    
    def _init_world_integration(self) -> None:
        """Initialize world model integration bridge."""
        try:
            self._world_integration_bridge = get_integration_bridge()
            logger.info("[ADAPTIVE_RETRY] World model integration initialized")
        except Exception as e:
            logger.warning(f"[ADAPTIVE_RETRY] Failed to initialize world integration: {e}")
            self._world_integration_bridge = None
    
    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model."""
        if not self._world_integration_bridge or not self._config.world_aware:
            return None
        
        try:
            world_state = self._world_integration_bridge.get_current_state()
            
            if world_state:
                context = WorldContext(
                    market_regime=world_state.get('market_regime', 'unknown'),
                    market_trend=world_state.get('market_trend', 'unknown'),
                    volatility_regime=world_state.get('volatility_regime', 'unknown'),
                    liquidity_state=world_state.get('liquidity_state', 'unknown'),
                    agent_activity=world_state.get('agent_activity', {}),
                    causal_factors=world_state.get('causal_factors', []),
                    prediction_confidence=world_state.get('prediction_confidence', 0.0),
                    timestamp=datetime.utcnow()
                )
                self._current_world_context = context
                return context
        
        except Exception as e:
            logger.debug(f"[ADAPTIVE_RETRY] Failed to get world context: {e}")
        
        return None
    
    def set_operation_name(self, name: str) -> None:
        """Set operation name for success prediction tracking."""
        self._operation_name = name
    
    def _create_strategy(self, policy: RetryPolicy) -> RetryStrategy:
        """Create retry strategy instance."""
        if policy == RetryPolicy.EXPONENTIAL_BACKOFF:
            return ExponentialBackoffStrategy(self._config)
        elif policy == RetryPolicy.LINEAR_BACKOFF:
            return LinearBackoffStrategy(self._config)
        elif policy == RetryPolicy.FIXED_DELAY:
            return FixedDelayStrategy(self._config)
        elif policy == RetryPolicy.JITTERED_BACKOFF:
            return JitteredBackoffStrategy(self._config)
        else:
            return ExponentialBackoffStrategy(self._config)  # Default
    
    def execute_with_retry(
        self,
        func: Callable[[], T],
        config: Optional[RetryConfig] = None,
        operation_name: Optional[str] = None
    ) -> RetryResult:
        """
        Enhanced execute function with adaptive retry strategy and world context (Phase 12.1).
        
        Args:
            func: Function to execute
            config: Optional override config
            operation_name: Optional operation name for tracking
            
        Returns:
            Enhanced retry result with world context
        """
        start_time = time.time()
        retry_config = config or self._config
        retry_delays = []
        
        # Set operation name if provided
        if operation_name:
            self.set_operation_name(operation_name)
        
        # Get world context for world-aware retry decisions
        world_context = self._get_world_context() if retry_config.world_aware else None
        
        # Adjust max attempts based on world context
        max_attempts = retry_config.max_attempts
        if world_context and world_context.volatility_regime == "high":
            max_attempts = min(retry_config.max_attempts + 2, 10)  # More retries in high volatility
        elif world_context and world_context.volatility_regime == "low":
            max_attempts = max(retry_config.max_attempts - 1, 1)  # Fewer retries in low volatility
        
        # Check retry budget
        if self._retry_budget_remaining <= 0:
            logger.warning("[ADAPTIVE_RETRY] Retry budget exhausted")
            return RetryResult(
                success=False,
                attempts=0,
                total_time_ms=(time.time() - start_time) * 1000,
                last_error=Exception("Retry budget exhausted"),
                confidence_score=0.0,
                world_context=world_context,
                predicted_success_probability=0.0
            )
        
        # Use current strategy
        strategy = self._current_strategy
        
        for attempt in range(max_attempts):
            try:
                result = func()
                total_time_ms = (time.time() - start_time) * 1000
                
                # Update performance tracking
                with self._lock:
                    self._update_performance(retry_config.policy, success=True)
                    self._retry_budget_remaining -= 1
                    self._success_predictor.record_outcome(self._operation_name, True)
                
                return RetryResult(
                    success=True,
                    attempts=attempt + 1,
                    total_time_ms=total_time_ms,
                    result=result,
                    retry_delays=retry_delays,
                    confidence_score=1.0,
                    world_context=world_context,
                    predicted_success_probability=self._success_predictor.predict_success(
                        self._operation_name, attempt + 1, world_context
                    )
                )
                
            except Exception as e:
                # Predict success probability
                predicted_success = self._success_predictor.predict_success(
                    self._operation_name, attempt + 1, world_context
                )
                
                retry_delays.append(strategy.get_delay_ms(attempt))
                
                # Check if should retry with world-aware decision
                should_retry = self._should_retry_world_aware(
                    attempt + 1, e, predicted_success, world_context, retry_config
                )
                
                if not should_retry:
                    total_time_ms = (time.time() - start_time) * 1000
                    
                    # Update performance tracking
                    with self._lock:
                        self._update_performance(retry_config.policy, success=False)
                        self._success_predictor.record_outcome(self._operation_name, False)
                    
                    return RetryResult(
                        success=False,
                        attempts=attempt + 1,
                        total_time_ms=total_time_ms,
                        last_error=e,
                        retry_delays=retry_delays,
                        confidence_score=predicted_success,
                        world_context=world_context,
                        predicted_success_probability=predicted_success
                    )
                
                # Wait before retry with world-aware backoff
                delay_ms = self._calculate_backoff_with_world_context(
                    attempt, world_context, strategy
                )
                time.sleep(delay_ms / 1000)
        
        # Should not reach here, but just in case
        total_time_ms = (time.time() - start_time) * 1000
        return RetryResult(
            success=False,
            attempts=max_attempts,
            total_time_ms=total_time_ms,
            last_error=Exception("Max attempts exceeded"),
            retry_delays=retry_delays,
            confidence_score=0.0,
            world_context=world_context,
            predicted_success_probability=0.0
        )
    
    def _should_retry_world_aware(
        self,
        attempt: int,
        error: Exception,
        predicted_success: float,
        world_context: Optional[WorldContext],
        config: RetryConfig
    ) -> bool:
        """World-aware retry decision making (Phase 12.1)."""
        # Check if exception is retryable
        if not isinstance(error, config.retryable_exceptions):
            return False
        
        # Check confidence threshold
        if predicted_success < config.confidence_threshold:
            return False
        
        # Standard retry limit check
        if attempt >= config.max_attempts:
            return False
        
        # World-aware adjustments
        if world_context:
            # More aggressive retry in high volatility
            if world_context.volatility_regime == "high" and attempt < config.max_attempts + 2:
                return True
            
            # Less aggressive retry in low volatility
            if world_context.volatility_regime == "low" and attempt >= config.max_attempts - 1:
                return False
        
        return True
    
    def _calculate_backoff_with_world_context(
        self,
        attempt: int,
        world_context: Optional[WorldContext],
        strategy: RetryStrategy
    ) -> float:
        """Calculate backoff with world context adjustment (Phase 12.1)."""
        base_delay = strategy.get_delay_ms(attempt)
        
        if world_context:
            # Longer backoff in low liquidity
            if world_context.liquidity_state == "low":
                return base_delay * 2.0
            # Shorter backoff in high liquidity
            elif world_context.liquidity_state == "high":
                return base_delay * 0.8
            # Shorter backoff during high volatility for faster recovery
            if world_context.volatility_regime == "high":
                return base_delay * 0.9
        
        return base_delay
    
    def _update_performance(self, policy: RetryPolicy, success: bool) -> None:
        """Update performance tracking for a policy."""
        perf = self._policy_performance[policy]
        perf["attempts"] += 1
        
        # Update success rate
        if success:
            perf["success_rate"] = (perf["success_rate"] * (perf["attempts"] - 1) + 1.0) / perf["attempts"]
        else:
            perf["success_rate"] = (perf["success_rate"] * (perf["attempts"] - 1)) / perf["attempts"]
    
    def adapt_strategy(self) -> None:
        """Adapt retry strategy based on performance tracking."""
        with self._lock:
            # Find best performing policy
            best_policy = max(
                self._policy_performance.items(),
                key=lambda x: x[1]["success_rate"] if x[1]["attempts"] > 0 else 0.0
            )
            
            if best_policy[0] != self._config.policy:
                logger.info(f"[ADAPTIVE_RETRY] Adapting strategy from {self._config.policy} to {best_policy[0]}")
                self._config.policy = best_policy[0]
                self._current_strategy = self._create_strategy(best_policy[0])
    
    def get_statistics(self) -> dict[str, Any]:
        """Enhanced retry statistics with world context (Phase 12.1)."""
        with self._lock:
            return {
                "current_policy": self._config.policy.value,
                "config": {
                    "max_attempts": self._config.max_attempts,
                    "base_delay_ms": self._config.base_delay_ms,
                    "max_delay_ms": self._config.max_delay_ms,
                    "world_aware": self._config.world_aware,
                    "confidence_threshold": self._config.confidence_threshold,
                },
                "policy_performance": {
                    policy.value: perf
                    for policy, perf in self._policy_performance.items()
                },
                # Phase 12.1 enhancements
                "world_integration_available": WORLD_MODEL_AVAILABLE,
                "world_integration_active": self._world_integration_bridge is not None,
                "current_world_context": self._current_world_context.market_regime if self._current_world_context else "unknown",
                "retry_budget_remaining": self._retry_budget_remaining,
                "retry_budget_total": self._config.retry_budget,
                "operation_stats": self._success_predictor._operation_stats,
            }
    
    def reset_retry_budget(self) -> None:
        """Reset retry budget (Phase 12.1 enhancement)."""
        with self._lock:
            self._retry_budget_remaining = self._config.retry_budget


__all__ = [
    "RetryPolicy",
    "RetryConfig",
    "RetryResult",
    "RetryStrategy",
    "ExponentialBackoffStrategy",
    "LinearBackoffStrategy",
    "FixedDelayStrategy",
    "JitteredBackoffStrategy",
    "AdaptiveRetryStrategy",
    "SuccessPredictor",  # Phase 12.1 enhancement
    "WorldContext",  # Phase 12.1 enhancement
]


# Singleton instance
_adaptive_retry: Optional[AdaptiveRetryStrategy] = None
_adaptive_retry_lock = threading.Lock()

def get_adaptive_retry(config: Optional[RetryConfig] = None) -> AdaptiveRetryStrategy:
    """Get the singleton adaptive retry strategy instance."""
    global _adaptive_retry
    if _adaptive_retry is None:
        with _adaptive_retry_lock:
            if _adaptive_retry is None:
                _adaptive_retry = AdaptiveRetryStrategy(config or RetryConfig())
    return _adaptive_retry