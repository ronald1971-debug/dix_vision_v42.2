"""
execution_unified.resilience.adaptive_retry
DIX VISION v42.2 — Adaptive Retry Strategy (Quick Win)

Provides intelligent retry strategies for transient failures.
This is a quick win implementation for execution resilience.
"""

from __future__ import annotations

import logging
import threading
import time
import random
from datetime import datetime
from typing import Callable, Optional, TypeVar, Any, List
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryPolicy(Enum):
    """Retry policy types."""
    EXPONENTIAL_BACKOFF = "EXPONENTIAL_BACKOFF"
    LINEAR_BACKOFF = "LINEAR_BACKOFF"
    FIXED_DELAY = "FIXED_DELAY"
    JITTERED_BACKOFF = "JITTERED_BACKOFF"


@dataclass
class RetryConfig:
    """Retry configuration."""
    
    max_attempts: int = 3
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    policy: RetryPolicy = RetryPolicy.EXPONENTIAL_BACKOFF
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.1  # For jittered backoff
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,)


@dataclass
class RetryResult:
    """Result of retry attempt."""
    
    success: bool
    attempts: int
    total_time_ms: float
    result: Optional[T] = None
    last_error: Optional[Exception] = None
    retry_delays: List[float] = field(default_factory=list)


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
    Adaptive retry strategy that selects optimal retry policy.
    
    This strategy monitors success rates and adapts the retry policy
    based on historical performance.
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
        
        logger.info(f"[ADAPTIVE_RETRY] Initialized with policy: {self._config.policy}")
    
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
        config: Optional[RetryConfig] = None
    ) -> RetryResult:
        """
        Execute function with adaptive retry strategy.
        
        Args:
            func: Function to execute
            config: Optional override config
            
        Returns:
            Retry result
        """
        start_time = time.time()
        retry_config = config or self._config
        retry_delays = []
        
        # Use current strategy
        strategy = self._current_strategy
        
        for attempt in range(retry_config.max_attempts):
            try:
                result = func()
                total_time_ms = (time.time() - start_time) * 1000
                
                # Update performance tracking
                with self._lock:
                    self._update_performance(retry_config.policy, success=True)
                
                return RetryResult(
                    success=True,
                    attempts=attempt + 1,
                    total_time_ms=total_time_ms,
                    result=result,
                    retry_delays=retry_delays
                )
                
            except Exception as e:
                retry_delays.append(strategy.get_delay_ms(attempt))
                
                # Check if should retry
                if not strategy.should_retry(attempt + 1, e):
                    total_time_ms = (time.time() - start_time) * 1000
                    
                    # Update performance tracking
                    with self._lock:
                        self._update_performance(retry_config.policy, success=False)
                    
                    return RetryResult(
                        success=False,
                        attempts=attempt + 1,
                        total_time_ms=total_time_ms,
                        last_error=e,
                        retry_delays=retry_delays
                    )
                
                # Wait before retry
                delay_ms = strategy.get_delay_ms(attempt)
                time.sleep(delay_ms / 1000)
        
        # Should not reach here, but just in case
        total_time_ms = (time.time() - start_time) * 1000
        return RetryResult(
            success=False,
            attempts=retry_config.max_attempts,
            total_time_ms=total_time_ms,
            last_error=Exception("Max attempts exceeded"),
            retry_delays=retry_delays
        )
    
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
        """Get retry statistics."""
        with self._lock:
            return {
                "current_policy": self._config.policy.value,
                "config": {
                    "max_attempts": self._config.max_attempts,
                    "base_delay_ms": self._config.base_delay_ms,
                    "max_delay_ms": self._config.max_delay_ms,
                },
                "policy_performance": {
                    policy.value: perf
                    for policy, perf in self._policy_performance.items()
                }
            }


__all__ = [
    "RetryPolicy",
    "RetryConfig",
    "RetryResult",
    "RetryStrategy",
    "AdaptiveRetryStrategy",
    "get_adaptive_retry",
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