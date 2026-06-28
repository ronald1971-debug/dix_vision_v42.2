"""
execution_unified.resilience.circuit_breaker
DIX VISION v42.2 — Circuit Breaker (Quick Win)

Provides circuit breaking capabilities for critical execution paths to prevent
cascading failures. This is a quick win implementation for execution resilience.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Circuit tripped, calls fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5  # Number of failures before opening
    success_threshold: int = 2  # Number of successes to close from half-open
    timeout_ms: int = 60000  # Time to wait before transitioning from open to half-open
    reset_timeout_ms: int = 120000  # Time to fully reset circuit


@dataclass
class CircuitBreakerResult:
    """Result of circuit breaker execution."""

    success: bool
    circuit_state: CircuitState
    execution_time_ms: float
    from_cache: bool = False
    error_message: str = ""


class CircuitBreaker:
    """
    Circuit breaker for preventing cascading failures.

    Circuit Breaker Pattern:
    1. CLOSED: Normal operation, track failures
    2. OPEN: After threshold failures, fail fast
    3. HALF_OPEN: After timeout, allow test calls
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self._name = name
        self._config = config or CircuitBreakerConfig()

        self._lock = threading.Lock()

        # State
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._last_state_change: datetime = datetime.utcnow()

        # Metrics
        self._total_calls = 0
        self._total_failures = 0
        self._total_successes = 0

        logger.info(f"[CIRCUIT_BREAKER] Initialized '{name}' with config: {self._config}")

    def execute(
        self, func: Callable[[], T], fallback: Optional[Callable[[], T]] = None
    ) -> CircuitBreakerResult:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            fallback: Fallback function if circuit is open

        Returns:
            Circuit breaker execution result
        """
        self._total_calls += 1
        start_time = time.time()

        with self._lock:
            # Check if circuit is open
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    # Circuit is open, fail fast
                    if fallback:
                        try:
                            result = fallback()
                            return CircuitBreakerResult(
                                success=True,
                                circuit_state=self._state,
                                execution_time_ms=(time.time() - start_time) * 1000,
                                from_cache=True,
                            )
                        except Exception as e:
                            return CircuitBreakerResult(
                                success=False,
                                circuit_state=self._state,
                                execution_time_ms=(time.time() - start_time) * 1000,
                                error_message=f"Fallback failed: {str(e)}",
                            )
                    else:
                        return CircuitBreakerResult(
                            success=False,
                            circuit_state=self._state,
                            execution_time_ms=(time.time() - start_time) * 1000,
                            error_message="Circuit is open",
                        )

        # Execute function
        try:
            result = func()
            execution_time_ms = (time.time() - start_time) * 1000

            # Record success
            with self._lock:
                self._on_success()

            return CircuitBreakerResult(
                success=True, circuit_state=self._state, execution_time_ms=execution_time_ms
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000

            # Record failure
            with self._lock:
                self._on_failure()

            return CircuitBreakerResult(
                success=False,
                circuit_state=self._state,
                execution_time_ms=execution_time_ms,
                error_message=str(e),
            )

    def _on_success(self) -> None:
        """Handle successful execution."""
        self._total_successes += 1
        self._failure_count = 0

        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self._config.success_threshold:
                self._transition_to_closed()

    def _on_failure(self) -> None:
        """Handle failed execution."""
        self._total_failures += 1
        self._last_failure_time = datetime.utcnow()
        self._failure_count += 1

        if self._state == CircuitState.CLOSED:
            if self._failure_count >= self._config.failure_threshold:
                self._transition_to_open()
        elif self._state == CircuitState.HALF_OPEN:
            # Failed in half-open, reopen circuit
            self._transition_to_open()

    def _transition_to_open(self) -> None:
        """Transition circuit to open state."""
        old_state = self._state
        self._state = CircuitState.OPEN
        self._last_state_change = datetime.utcnow()
        self._success_count = 0

        logger.warning(f"[CIRCUIT_BREAKER] '{self._name}' transitioned {old_state} -> OPEN")

    def _transition_to_half_open(self) -> None:
        """Transition circuit to half-open state."""
        old_state = self._state
        self._state = CircuitState.HALF_OPEN
        self._last_state_change = datetime.utcnow()
        self._failure_count = 0

        logger.info(f"[CIRCUIT_BREAKER] '{self._name}' transitioned {old_state} -> HALF_OPEN")

    def _transition_to_closed(self) -> None:
        """Transition circuit to closed state."""
        old_state = self._state
        self._state = CircuitState.CLOSED
        self._last_state_change = datetime.utcnow()
        self._success_count = 0

        logger.info(f"[CIRCUIT_BREAKER] '{self._name}' transitioned {old_state} -> CLOSED")

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset from open to half-open."""
        if self._last_state_change is None:
            return True

        time_since_state_change = datetime.utcnow() - self._last_state_change
        return time_since_state_change >= timedelta(milliseconds=self._config.timeout_ms)

    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            # Auto-transition from open to half-open if timeout has elapsed
            if self._state == CircuitState.OPEN and self._should_attempt_reset():
                self._transition_to_half_open()
            return self._state

    def get_statistics(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        with self._lock:
            return {
                "name": self._name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "total_calls": self._total_calls,
                "total_failures": self._total_failures,
                "total_successes": self._total_successes,
                "failure_rate": (
                    self._total_failures / self._total_calls if self._total_calls > 0 else 0.0
                ),
                "last_failure_time": (
                    self._last_failure_time.isoformat() if self._last_failure_time else None
                ),
                "last_state_change": (
                    self._last_state_change.isoformat() if self._last_state_change else None
                ),
                "config": {
                    "failure_threshold": self._config.failure_threshold,
                    "success_threshold": self._config.success_threshold,
                    "timeout_ms": self._config.timeout_ms,
                },
            }

    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._last_state_change = datetime.utcnow()

            logger.info(f"[CIRCUIT_BREAKER] '{self._name}' reset to CLOSED state")


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""

    def __init__(self):
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get_or_create(
        self, name: str, config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get or create a circuit breaker."""
        with self._lock:
            if name not in self._circuit_breakers:
                self._circuit_breakers[name] = CircuitBreaker(name, config)
            return self._circuit_breakers[name]

    def get_all_statistics(self) -> Dict[str, dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        with self._lock:
            return {name: cb.get_statistics() for name, cb in self._circuit_breakers.items()}


# Singleton registry
_circuit_breaker_registry = CircuitBreakerRegistry()


def get_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """Get or create a circuit breaker from registry."""
    return _circuit_breaker_registry.get_or_create(name, config)


__all__ = [
    "CircuitState",
    "CircuitBreakerConfig",
    "CircuitBreakerResult",
    "CircuitBreaker",
    "CircuitBreakerRegistry",
    "get_circuit_breaker",
]
