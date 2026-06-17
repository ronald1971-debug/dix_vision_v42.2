"""Execution Adapter Circuit Breaker — EXEC-05.01.

Circuit breaker pattern for execution adapters to prevent cascading
failures. Monitors adapter health and automatically stops routing
requests to failing adapters with configurable recovery strategies.
"""

from __future__ import annotations

import dataclasses
import enum
from collections import deque
from collections.abc import Callable, Mapping
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_FAILURE_THRESHOLD: Final[int] = 5
"""Number of consecutive failures before circuit opens."""

DEFAULT_SUCCESS_THRESHOLD: Final[int] = 2
"""Number of consecutive successes before circuit closes."""

DEFAULT_TIMEOUT_NS: Final[int] = 60_000_000_000  # 60 seconds
"""Time in nanoseconds before circuit transitions from open to half-open."""

DEFAULT_CALL_TIMEOUT_NS: Final[int] = 10_000_000_000  # 10 seconds
"""Maximum time in nanoseconds for a single adapter call."""

MAX_EVENT_HISTORY: Final[int] = 1000
"""Maximum number of events to retain for analysis."""

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CircuitState(enum.Enum):
    """State of the adapter circuit breaker."""
    CLOSED = "CLOSED"  # Normal operation, calls allowed
    OPEN = "OPEN"  # Circuit tripped, calls rejected
    HALF_OPEN = "HALF_OPEN"  # Testing if adapter has recovered


class FailureType(enum.Enum):
    """Types of adapter failures."""
    TIMEOUT = "TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    UNKNOWN = "UNKNOWN"


class CallResult(enum.Enum):
    """Result of an adapter call."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class AdapterCallEvent:
    """Record of an adapter call for circuit breaker monitoring."""
    adapter_name: str
    timestamp_ns: int
    result: CallResult
    duration_ns: int
    failure_type: FailureType | None = None
    error_message: str = ""
    metadata: Mapping[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.adapter_name:
            raise ValueError("adapter_name must be non-empty")
        if self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must be >= 0")
        if self.duration_ns < 0:
            raise ValueError("duration_ns must be >= 0")


@dataclasses.dataclass(frozen=True, slots=True)
class CircuitBreakerConfig:
    """Configuration for adapter circuit breaker."""
    failure_threshold: int = DEFAULT_FAILURE_THRESHOLD
    success_threshold: int = DEFAULT_SUCCESS_THRESHOLD
    timeout_ns: int = DEFAULT_TIMEOUT_NS
    call_timeout_ns: int = DEFAULT_CALL_TIMEOUT_NS
    sliding_window_size: int = 10  # Number of recent calls to consider
    enable_half_open: bool = True
    auto_reset: bool = False
    metrics_enabled: bool = True

    def __post_init__(self) -> None:
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if self.success_threshold < 1:
            raise ValueError("success_threshold must be >= 1")
        if self.timeout_ns <= 0:
            raise ValueError("timeout_ns must be > 0")
        if self.call_timeout_ns <= 0:
            raise ValueError("call_timeout_ns must be > 0")
        if self.sliding_window_size < 1:
            raise ValueError("sliding_window_size must be >= 1")


@dataclasses.dataclass(frozen=True, slots=True)
class CircuitBreakerMetrics:
    """Metrics about circuit breaker performance."""
    adapter_name: str
    state: CircuitState
    total_calls: int
    successful_calls: int
    failed_calls: int
    timeout_calls: int
    consecutive_failures: int
    consecutive_successes: int
    last_failure_time_ns: int
    last_success_time_ns: int
    state_transitions: int
    total_trip_count: int
    failure_rate: float
    average_duration_ns: int


@dataclasses.dataclass(frozen=True, slots=True)
class CircuitBreakerDecision:
    """Decision made by circuit breaker for a request."""
    allowed: bool
    state: CircuitState
    adapter_name: str
    reason: str
    timestamp_ns: int
    metadata: Mapping[str, Any] = dataclasses.field(default_factory=dict)


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------


class AdapterCircuitBreaker:
    """Circuit breaker for execution adapters.
    
    Monitors adapter calls and automatically trips the circuit when
    consecutive failures exceed the threshold. Supports automatic
    recovery through the half-open state.
    
    Usage::
    
        breaker = AdapterCircuitBreaker("binance", config=CircuitBreakerConfig())
        decision = breaker.should_allow_call()
        if decision.allowed:
            try:
                result = adapter.call()
                breaker.record_success(result, duration_ns)
            except Exception as e:
                breaker.record_failure(str(e), FailureType.CONNECTION_ERROR)
    
    The circuit breaker is thread-safe and maintains call history
    for metrics and analysis.
    """
    
    def __init__(
        self,
        adapter_name: str,
        config: CircuitBreakerConfig | None = None,
    ) -> None:
        """Initialize the adapter circuit breaker.
        
        Args:
            adapter_name: Name of the adapter being protected
            config: Circuit breaker configuration
        """
        self._adapter_name = adapter_name
        self._config = config or CircuitBreakerConfig()
        
        self._lock = Lock()
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._last_state_change_ns = 0
        self._trip_count = 0
        self._state_transition_count = 0
        
        self._call_history: deque[AdapterCallEvent] = deque(maxlen=MAX_EVENT_HISTORY)
        self._total_calls = 0
        self._successful_calls = 0
        self._failed_calls = 0
        self._timeout_calls = 0
        
        self._last_failure_time_ns = 0
        self._last_success_time_ns = 0
        self._total_duration_ns = 0
    
    def should_allow_call(self, timestamp_ns: int | None = None) -> CircuitBreakerDecision:
        """Determine if a call to the adapter should be allowed.
        
        Args:
            timestamp_ns: Current timestamp in nanoseconds
            
        Returns:
            Decision indicating if call is allowed and the current state
        """
        import time
        
        if timestamp_ns is None:
            timestamp_ns = time.time_ns()
        
        with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if (self._state == CircuitState.OPEN and 
                self._config.enable_half_open and
                timestamp_ns >= self._last_state_change_ns + self._config.timeout_ns):
                self._transition_to_state(CircuitState.HALF_OPEN, timestamp_ns)
            
            # Determine if call is allowed
            allowed = self._state != CircuitState.OPEN
            
            if allowed:
                reason = f"Circuit is {self._state.value}, calls allowed"
            else:
                reason = "Circuit is OPEN, calls rejected until timeout expires"
            
            return CircuitBreakerDecision(
                allowed=allowed,
                state=self._state,
                adapter_name=self._adapter_name,
                reason=reason,
                timestamp_ns=timestamp_ns,
            )
    
    def record_success(
        self,
        duration_ns: int,
        timestamp_ns: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        """Record a successful adapter call.
        
        Args:
            duration_ns: Duration of the call in nanoseconds
            timestamp_ns: Timestamp of the call
            metadata: Additional metadata
        """
        import time
        
        if timestamp_ns is None:
            timestamp_ns = time.time_ns()
        
        event = AdapterCallEvent(
            adapter_name=self._adapter_name,
            timestamp_ns=timestamp_ns,
            result=CallResult.SUCCESS,
            duration_ns=duration_ns,
            metadata=metadata or {},
        )
        
        with self._lock:
            self._record_event(event)
            self._consecutive_failures = 0
            self._consecutive_successes += 1
            self._last_success_time_ns = timestamp_ns
            
            # Check if we should close the circuit from HALF_OPEN
            if (self._state == CircuitState.HALF_OPEN and
                self._consecutive_successes >= self._config.success_threshold):
                self._transition_to_state(CircuitState.CLOSED, timestamp_ns)
    
    def record_failure(
        self,
        error_message: str,
        failure_type: FailureType,
        duration_ns: int = 0,
        timestamp_ns: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        """Record a failed adapter call.
        
        Args:
            error_message: Error message from the failure
            failure_type: Type of failure
            duration_ns: Duration of the call in nanoseconds
            timestamp_ns: Timestamp of the call
            metadata: Additional metadata
        """
        import time
        
        if timestamp_ns is None:
            timestamp_ns = time.time_ns()
        
        event = AdapterCallEvent(
            adapter_name=self._adapter_name,
            timestamp_ns=timestamp_ns,
            result=CallResult.FAILURE,
            duration_ns=duration_ns,
            failure_type=failure_type,
            error_message=error_message,
            metadata=metadata or {},
        )
        
        with self._lock:
            self._record_event(event)
            self._consecutive_successes = 0
            self._consecutive_failures += 1
            self._last_failure_time_ns = timestamp_ns
            
            # Check if we should trip the circuit
            if (self._state != CircuitState.OPEN and
                self._consecutive_failures >= self._config.failure_threshold):
                self._transition_to_state(CircuitState.OPEN, timestamp_ns)
    
    def record_timeout(
        self,
        duration_ns: int,
        timestamp_ns: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        """Record a timeout during adapter call.
        
        Args:
            duration_ns: Duration before timeout in nanoseconds
            timestamp_ns: Timestamp of the timeout
            metadata: Additional metadata
        """
        import time
        
        if timestamp_ns is None:
            timestamp_ns = time.time_ns()
        
        event = AdapterCallEvent(
            adapter_name=self._adapter_name,
            timestamp_ns=timestamp_ns,
            result=CallResult.TIMEOUT,
            duration_ns=duration_ns,
            failure_type=FailureType.TIMEOUT,
            error_message="Call timeout",
            metadata=metadata or {},
        )
        
        with self._lock:
            self._record_event(event)
            self._consecutive_successes = 0
            self._consecutive_failures += 1
            self._last_failure_time_ns = timestamp_ns
            self._timeout_calls += 1
            
            # Check if we should trip the circuit
            if (self._state != CircuitState.OPEN and
                self._consecutive_failures >= self._config.failure_threshold):
                self._transition_to_state(CircuitState.OPEN, timestamp_ns)
    
    def reset(self, timestamp_ns: int | None = None) -> None:
        """Manually reset the circuit breaker to CLOSED state.
        
        Args:
            timestamp_ns: Timestamp of the reset
        """
        import time
        
        if timestamp_ns is None:
            timestamp_ns = time.time_ns()
        
        with self._lock:
            self._transition_to_state(CircuitState.CLOSED, timestamp_ns)
            self._consecutive_failures = 0
            self._consecutive_successes = 0
    
    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get current circuit breaker metrics.
        
        Returns:
            Current metrics
        """
        with self._lock:
            failure_rate = 0.0
            if self._total_calls > 0:
                failure_rate = self._failed_calls / self._total_calls
            
            avg_duration = 0
            if self._total_calls > 0:
                avg_duration = self._total_duration_ns // self._total_calls
            
            return CircuitBreakerMetrics(
                adapter_name=self._adapter_name,
                state=self._state,
                total_calls=self._total_calls,
                successful_calls=self._successful_calls,
                failed_calls=self._failed_calls,
                timeout_calls=self._timeout_calls,
                consecutive_failures=self._consecutive_failures,
                consecutive_successes=self._consecutive_successes,
                last_failure_time_ns=self._last_failure_time_ns,
                last_success_time_ns=self._last_success_time_ns,
                state_transitions=self._state_transition_count,
                total_trip_count=self._trip_count,
                failure_rate=failure_rate,
                average_duration_ns=avg_duration,
            )
    
    def get_recent_events(self, count: int = 10) -> list[AdapterCallEvent]:
        """Get recent call events.
        
        Args:
            count: Number of recent events to return
            
        Returns:
            List of recent events
        """
        with self._lock:
            return list(self._call_history)[-count:]
    
    def _record_event(self, event: AdapterCallEvent) -> None:
        """Record an event in the history."""
        self._call_history.append(event)
        self._total_calls += 1
        
        if event.result == CallResult.SUCCESS:
            self._successful_calls += 1
        elif event.result == CallResult.FAILURE:
            self._failed_calls += 1
        elif event.result == CallResult.TIMEOUT:
            self._timeout_calls += 1
            self._failed_calls += 1
        
        self._total_duration_ns += event.duration_ns
    
    def _transition_to_state(self, new_state: CircuitState, timestamp_ns: int) -> None:
        """Transition to a new circuit state."""
        if self._state == CircuitState.OPEN and new_state != CircuitState.OPEN:
            self._consecutive_failures = 0
        elif new_state == CircuitState.OPEN:
            self._trip_count += 1
        
        self._state = new_state
        self._last_state_change_ns = timestamp_ns
        self._state_transition_count += 1


# ---------------------------------------------------------------------------
# Circuit Breaker Registry
# ---------------------------------------------------------------------------


class CircuitBreakerRegistry:
    """Registry for managing multiple adapter circuit breakers."""
    
    def __init__(self) -> None:
        """Initialize the circuit breaker registry."""
        self._lock = Lock()
        self._breakers: dict[str, AdapterCircuitBreaker] = {}
    
    def get_or_create(
        self,
        adapter_name: str,
        config: CircuitBreakerConfig | None = None,
    ) -> AdapterCircuitBreaker:
        """Get or create a circuit breaker for an adapter.
        
        Args:
            adapter_name: Name of the adapter
            config: Configuration for the circuit breaker
            
        Returns:
            Circuit breaker instance
        """
        with self._lock:
            if adapter_name not in self._breakers:
                self._breakers[adapter_name] = AdapterCircuitBreaker(
                    adapter_name, config
                )
            return self._breakers[adapter_name]
    
    def get(self, adapter_name: str) -> AdapterCircuitBreaker | None:
        """Get a circuit breaker for an adapter.
        
        Args:
            adapter_name: Name of the adapter
            
        Returns:
            Circuit breaker instance or None if not found
        """
        with self._lock:
            return self._breakers.get(adapter_name)
    
    def get_all_metrics(self) -> dict[str, CircuitBreakerMetrics]:
        """Get metrics for all registered circuit breakers.
        
        Returns:
            Dictionary of adapter names to metrics
        """
        with self._lock:
            return {
                name: breaker.get_metrics()
                for name, breaker in self._breakers.items()
            }
    
    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        import time
        
        timestamp_ns = time.time_ns()
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset(timestamp_ns)
    
    def reset_breaker(self, adapter_name: str) -> bool:
        """Reset a specific circuit breaker.
        
        Args:
            adapter_name: Name of the adapter
            
        Returns:
            True if reset successfully
        """
        import time
        
        with self._lock:
            breaker = self._breakers.get(adapter_name)
            if breaker:
                breaker.reset(time.time_ns())
                return True
            return False


# ---------------------------------------------------------------------------
# Circuit Breaker Decorator
# ---------------------------------------------------------------------------


def with_circuit_breaker(
    registry: CircuitBreakerRegistry,
    adapter_name: str,
    config: CircuitBreakerConfig | None = None,
):
    """Decorator to apply circuit breaker to adapter methods.
    
    Args:
        registry: Circuit breaker registry
        adapter_name: Name of the adapter
        config: Circuit breaker configuration
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            breaker = registry.get_or_create(adapter_name, config)
            import time
            
            decision = breaker.should_allow_call()
            if not decision.allowed:
                raise RuntimeError(f"Circuit breaker is OPEN for {adapter_name}: {decision.reason}")
            
            start_ns = time.time_ns()
            try:
                result = func(*args, **kwargs)
                duration_ns = time.time_ns() - start_ns
                breaker.record_success(duration_ns)
                return result
            except Exception as e:
                duration_ns = time.time_ns() - start_ns
                failure_type = FailureType.UNKNOWN
                
                error_lower = str(e).lower()
                if "timeout" in error_lower or "timed out" in error_lower:
                    failure_type = FailureType.TIMEOUT
                elif "connection" in error_lower:
                    failure_type = FailureType.CONNECTION_ERROR
                elif "rate limit" in error_lower:
                    failure_type = FailureType.RATE_LIMIT
                elif "auth" in error_lower:
                    failure_type = FailureType.AUTHENTICATION_ERROR
                
                breaker.record_failure(str(e), failure_type, duration_ns)
                raise
        return wrapper
    return decorator


__all__ = [
    "CircuitState",
    "FailureType",
    "CallResult",
    "AdapterCallEvent",
    "CircuitBreakerConfig",
    "CircuitBreakerMetrics",
    "CircuitBreakerDecision",
    "AdapterCircuitBreaker",
    "CircuitBreakerRegistry",
    "with_circuit_breaker",
]
