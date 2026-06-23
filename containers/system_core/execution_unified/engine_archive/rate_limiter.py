"""Execution Rate Limiter — EXEC-05.02.

Rate limiting system for execution adapters to prevent API abuse
and stay within exchange rate limits. Implements multiple rate
limiting strategies with sliding window, token bucket, and adaptive
algorithms.
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

DEFAULT_RATE_LIMIT: Final[int] = 10
"""Default number of requests allowed per time window."""

DEFAULT_TIME_WINDOW_NS: Final[int] = 1_000_000_000  # 1 second
"""Default time window in nanoseconds."""

DEFAULT_BURST_CAPACITY: Final[int] = 20
"""Default burst capacity for token bucket."""

DEFAULT_REFILL_RATE: Final[int] = 10
"""Default refill rate for token bucket (tokens per second)."""

MAX_WINDOW_SIZE: Final[int] = 10_000
"""Maximum number of timestamps to retain in sliding window."""

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class RateLimitStrategy(enum.Enum):
    """Rate limiting strategies."""

    SLIDING_WINDOW = "SLIDING_WINDOW"  # Count requests in sliding time window
    TOKEN_BUCKET = "TOKEN_BUCKET"  # Token bucket algorithm
    FIXED_WINDOW = "FIXED_WINDOW"  # Fixed time window counter
    ADAPTIVE = "ADAPTIVE"  # Adaptive rate limiting based on response


class LimitResult(enum.Enum):
    """Result of rate limit check."""

    ALLOWED = "ALLOWED"  # Request allowed
    DENIED = "DENIED"  # Request denied, rate limit exceeded
    THROTTLED = "THROTTLED"  # Request allowed but should throttle


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class RateLimitConfig:
    """Configuration for rate limiting."""

    rate_limit: int = DEFAULT_RATE_LIMIT  # requests per window
    time_window_ns: int = DEFAULT_TIME_WINDOW_NS
    burst_capacity: int = DEFAULT_BURST_CAPACITY
    refill_rate: int = DEFAULT_REFILL_RATE
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    enable_burst: bool = True
    enable_throttling: bool = False
    adaptive_factor: float = 1.0  # Factor for adaptive limiting

    def __post_init__(self) -> None:
        if self.rate_limit < 1:
            raise ValueError("rate_limit must be >= 1")
        if self.time_window_ns <= 0:
            raise ValueError("time_window_ns must be > 0")
        if self.burst_capacity < self.rate_limit:
            raise ValueError("burst_capacity must be >= rate_limit")
        if self.refill_rate < 1:
            raise ValueError("refill_rate must be >= 1")
        if self.adaptive_factor < 0.0:
            raise ValueError("adaptive_factor must be >= 0.0")


@dataclasses.dataclass(frozen=True, slots=True)
class RateLimitDecision:
    """Decision made by rate limiter for a request."""

    allowed: bool
    result: LimitResult
    adapter_name: str
    reason: str
    timestamp_ns: int
    retry_after_ns: int  # When to retry if denied
    current_rate: float  # Current requests per second
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class RateLimitMetrics:
    """Metrics about rate limiter performance."""

    adapter_name: str
    total_requests: int
    allowed_requests: int
    denied_requests: int
    throttled_requests: int
    current_rate: float
    peak_rate: float
    average_rate: float
    tokens_remaining: int | None
    window_utilization: float


# ---------------------------------------------------------------------------
# Rate Limiter Implementations
# ---------------------------------------------------------------------------


class SlidingWindowRateLimiter:
    """Sliding window rate limiter.

    Counts requests within a sliding time window. When a request arrives,
    it removes timestamps older than the window and checks if the count
    exceeds the limit.
    """

    def __init__(
        self,
        adapter_name: str,
        config: RateLimitConfig,
    ) -> None:
        """Initialize the sliding window rate limiter.

        Args:
            adapter_name: Name of the adapter being limited
            config: Rate limit configuration
        """
        self._adapter_name = adapter_name
        self._config = config
        self._lock = Lock()

        self._timestamps: deque[int] = deque()
        self._total_requests = 0
        self._allowed_requests = 0
        self._denied_requests = 0
        self._throttled_requests = 0

        self._peak_rate = 0.0
        self._total_rate = 0.0
        self._rate_samples = 0

    def check(
        self,
        timestamp_ns: int | None = None,
    ) -> RateLimitDecision:
        """Check if a request should be allowed.

        Args:
            timestamp_ns: Current timestamp in nanoseconds

        Returns:
            Decision indicating if request is allowed
        """
        import time

        if timestamp_ns is None:
            timestamp_ns = time.time_ns()

        with self._lock:
            # Remove timestamps older than the window
            cutoff = timestamp_ns - self._config.time_window_ns
            while self._timestamps and self._timestamps[0] <= cutoff:
                self._timestamps.popleft()

            current_count = len(self._timestamps)
            self._total_requests += 1

            # Calculate current rate
            current_rate = current_count / (self._config.time_window_ns / 1_000_000_000)

            # Update metrics
            if current_rate > self._peak_rate:
                self._peak_rate = current_rate

            self._total_rate += current_rate
            self._rate_samples += 1

            # Check if limit exceeded
            if current_count >= self._config.rate_limit:
                self._denied_requests += 1

                # Calculate retry after
                if self._timestamps:
                    oldest_timestamp = self._timestamps[0]
                    retry_after = oldest_timestamp + self._config.time_window_ns - timestamp_ns
                else:
                    retry_after = 0

                return RateLimitDecision(
                    allowed=False,
                    result=LimitResult.DENIED,
                    adapter_name=self._adapter_name,
                    reason=f"Rate limit exceeded: {current_count}/{self._config.rate_limit} requests in window",
                    timestamp_ns=timestamp_ns,
                    retry_after_ns=retry_after,
                    current_rate=current_rate,
                )

            # Add current timestamp
            self._timestamps.append(timestamp_ns)
            self._allowed_requests += 1

            # Check throttling
            if self._config.enable_throttling:
                utilization = current_count / self._config.rate_limit
                if utilization > 0.8:  # 80% utilization threshold
                    self._throttled_requests += 1
                    return RateLimitDecision(
                        allowed=True,
                        result=LimitResult.THROTTLED,
                        adapter_name=self._adapter_name,
                        reason=f"Request allowed but throttle recommended: {utilization:.1%} utilization",
                        timestamp_ns=timestamp_ns,
                        retry_after_ns=0,
                        current_rate=current_rate,
                    )

            return RateLimitDecision(
                allowed=True,
                result=LimitResult.ALLOWED,
                adapter_name=self._adapter_name,
                reason="Request allowed",
                timestamp_ns=timestamp_ns,
                retry_after_ns=0,
                current_rate=current_rate,
            )

    def get_metrics(self) -> RateLimitMetrics:
        """Get current rate limiter metrics.

        Returns:
            Current metrics
        """
        import time

        timestamp_ns = time.time_ns()

        with self._lock:
            # Remove old timestamps
            cutoff = timestamp_ns - self._config.time_window_ns
            while self._timestamps and self._timestamps[0] <= cutoff:
                self._timestamps.popleft()

            current_count = len(self._timestamps)
            current_rate = current_count / (self._config.time_window_ns / 1_000_000_000)

            avg_rate = 0.0
            if self._rate_samples > 0:
                avg_rate = self._total_rate / self._rate_samples

            window_utilization = current_count / self._config.rate_limit

            return RateLimitMetrics(
                adapter_name=self._adapter_name,
                total_requests=self._total_requests,
                allowed_requests=self._allowed_requests,
                denied_requests=self._denied_requests,
                throttled_requests=self._throttled_requests,
                current_rate=current_rate,
                peak_rate=self._peak_rate,
                average_rate=avg_rate,
                tokens_remaining=None,
                window_utilization=window_utilization,
            )


class TokenBucketRateLimiter:
    """Token bucket rate limiter.

    Uses a token bucket algorithm where tokens are added at a fixed rate
    up to a maximum capacity. Each request consumes one token. Requests
    are denied when no tokens are available.
    """

    def __init__(
        self,
        adapter_name: str,
        config: RateLimitConfig,
    ) -> None:
        """Initialize the token bucket rate limiter.

        Args:
            adapter_name: Name of the adapter being limited
            config: Rate limit configuration
        """
        self._adapter_name = adapter_name
        self._config = config
        self._lock = Lock()

        self._tokens = config.burst_capacity
        self._last_refill_ns = 0

        self._total_requests = 0
        self._allowed_requests = 0
        self._denied_requests = 0
        self._throttled_requests = 0

    def check(
        self,
        timestamp_ns: int | None = None,
    ) -> RateLimitDecision:
        """Check if a request should be allowed.

        Args:
            timestamp_ns: Current timestamp in nanoseconds

        Returns:
            Decision indicating if request is allowed
        """
        import time

        if timestamp_ns is None:
            timestamp_ns = time.time_ns()

        with self._lock:
            # Refill tokens
            self._refill_tokens(timestamp_ns)

            self._total_requests += 1

            # Check if tokens available
            if self._tokens < 1:
                self._denied_requests += 1

                # Calculate time until next token
                if self._config.refill_rate > 0:
                    retry_after = int((1.0 / self._config.refill_rate) * 1_000_000_000)
                else:
                    retry_after = self._config.time_window_ns

                return RateLimitDecision(
                    allowed=False,
                    result=LimitResult.DENIED,
                    adapter_name=self._adapter_name,
                    reason=f"No tokens available: {self._tokens:.2f} tokens",
                    timestamp_ns=timestamp_ns,
                    retry_after_ns=retry_after,
                    current_rate=self._config.refill_rate,
                )

            # Consume token
            self._tokens -= 1
            self._allowed_requests += 1

            # Calculate current rate estimate
            current_rate = self._config.refill_rate

            return RateLimitDecision(
                allowed=True,
                result=LimitResult.ALLOWED,
                adapter_name=self._adapter_name,
                reason=f"Request allowed: {self._tokens:.2f} tokens remaining",
                timestamp_ns=timestamp_ns,
                retry_after_ns=0,
                current_rate=current_rate,
            )

    def _refill_tokens(self, timestamp_ns: int) -> None:
        """Refill tokens based on time elapsed."""
        if self._last_refill_ns == 0:
            self._last_refill_ns = timestamp_ns
            return

        time_elapsed = timestamp_ns - self._last_refill_ns
        if time_elapsed <= 0:
            return

        # Calculate tokens to add
        seconds_elapsed = time_elapsed / 1_000_000_000
        tokens_to_add = seconds_elapsed * self._config.refill_rate

        # Add tokens up to capacity
        self._tokens = min(self._config.burst_capacity, self._tokens + tokens_to_add)
        self._last_refill_ns = timestamp_ns

    def get_metrics(self) -> RateLimitMetrics:
        """Get current rate limiter metrics.

        Returns:
            Current metrics
        """
        import time

        timestamp_ns = time.time_ns()

        with self._lock:
            self._refill_tokens(timestamp_ns)

            current_rate = self._config.refill_rate
            window_utilization = 1.0 - (self._tokens / self._config.burst_capacity)

            return RateLimitMetrics(
                adapter_name=self._adapter_name,
                total_requests=self._total_requests,
                allowed_requests=self._allowed_requests,
                denied_requests=self._denied_requests,
                throttled_requests=self._throttled_requests,
                current_rate=current_rate,
                peak_rate=current_rate,
                average_rate=current_rate,
                tokens_remaining=int(self._tokens),
                window_utilization=window_utilization,
            )


class AdaptiveRateLimiter:
    """Adaptive rate limiter.

    Adjusts rate limits based on response times and error rates.
    Automatically throttles when detecting degraded performance.
    """

    def __init__(
        self,
        adapter_name: str,
        config: RateLimitConfig,
    ) -> None:
        """Initialize the adaptive rate limiter.

        Args:
            adapter_name: Name of the adapter being limited
            config: Rate limit configuration
        """
        self._adapter_name = adapter_name
        self._config = config
        self._lock = Lock()

        self._base_limiter = SlidingWindowRateLimiter(adapter_name, config)

        self._response_times: deque[int] = deque(maxlen=100)
        self._error_count = 0
        self._total_responses = 0

        self._current_rate_limit = config.rate_limit
        self._adaptive_enabled = True

    def check(
        self,
        timestamp_ns: int | None = None,
    ) -> RateLimitDecision:
        """Check if a request should be allowed.

        Args:
            timestamp_ns: Current timestamp in nanoseconds

        Returns:
            Decision indicating if request is allowed
        """
        # Adapt rate limit based on recent performance
        if self._adaptive_enabled:
            self._adapt_rate_limit()

        # Use base limiter with adapted rate
        return self._base_limiter.check(timestamp_ns)

    def record_response(
        self,
        success: bool,
        response_time_ns: int,
        timestamp_ns: int | None = None,
    ) -> None:
        """Record a response for adaptive learning.

        Args:
            success: Whether the response was successful
            response_time_ns: Response time in nanoseconds
            timestamp_ns: Timestamp of the response
        """
        import time

        if timestamp_ns is None:
            timestamp_ns = time.time_ns()

        with self._lock:
            self._response_times.append(response_time_ns)
            self._total_responses += 1

            if not success:
                self._error_count += 1

    def _adapt_rate_limit(self) -> None:
        """Adapt rate limit based on recent performance."""
        if len(self._response_times) < 10:
            return

        # Calculate average response time
        avg_response_time = sum(self._response_times) / len(self._response_times)

        # Calculate error rate
        error_rate = self._error_count / self._total_responses if self._total_responses > 0 else 0

        # Adapt based on performance
        if error_rate > 0.1 or avg_response_time > 5_000_000_000:  # 10% error or >5s response
            # Reduce rate limit
            adaptation_factor = 0.8 * self._config.adaptive_factor
            new_limit = max(1, int(self._config.rate_limit * adaptation_factor))
            self._current_rate_limit = min(self._current_rate_limit, new_limit)
        elif error_rate < 0.01 and avg_response_time < 1_000_000_000:  # <1% error and <1s response
            # Increase rate limit
            adaptation_factor = 1.2 * self._config.adaptive_factor
            new_limit = int(self._config.rate_limit * adaptation_factor)
            self._current_rate_limit = min(new_limit, self._config.rate_limit)

        # Update base limiter config
        self._base_limiter._config = dataclasses.replace(
            self._base_limiter._config, rate_limit=self._current_rate_limit
        )

    def get_metrics(self) -> RateLimitMetrics:
        """Get current rate limiter metrics.

        Returns:
            Current metrics
        """
        return self._base_limiter.get_metrics()


class RateLimiter:
    """Unified rate limiter that supports multiple strategies."""

    def __init__(
        self,
        adapter_name: str,
        config: RateLimitConfig | None = None,
    ) -> None:
        """Initialize the rate limiter.

        Args:
            adapter_name: Name of the adapter being limited
            config: Rate limit configuration
        """
        self._adapter_name = adapter_name
        self._config = config or RateLimitConfig()

        # Create appropriate limiter based on strategy
        if self._config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            self._limiter = TokenBucketRateLimiter(adapter_name, self._config)
        elif self._config.strategy == RateLimitStrategy.ADAPTIVE:
            self._limiter = AdaptiveRateLimiter(adapter_name, self._config)
        else:  # Default to sliding window
            self._limiter = SlidingWindowRateLimiter(adapter_name, self._config)

    def check(
        self,
        timestamp_ns: int | None = None,
    ) -> RateLimitDecision:
        """Check if a request should be allowed.

        Args:
            timestamp_ns: Current timestamp in nanoseconds

        Returns:
            Decision indicating if request is allowed
        """
        return self._limiter.check(timestamp_ns)

    def get_metrics(self) -> RateLimitMetrics:
        """Get current rate limiter metrics.

        Returns:
            Current metrics
        """
        return self._limiter.get_metrics()


# ---------------------------------------------------------------------------
# Rate Limiter Registry
# ---------------------------------------------------------------------------


class RateLimiterRegistry:
    """Registry for managing multiple rate limiters."""

    def __init__(self) -> None:
        """Initialize the rate limiter registry."""
        self._lock = Lock()
        self._limiters: dict[str, RateLimiter] = {}

    def get_or_create(
        self,
        adapter_name: str,
        config: RateLimitConfig | None = None,
    ) -> RateLimiter:
        """Get or create a rate limiter for an adapter.

        Args:
            adapter_name: Name of the adapter
            config: Rate limit configuration

        Returns:
            Rate limiter instance
        """
        with self._lock:
            if adapter_name not in self._limiters:
                self._limiters[adapter_name] = RateLimiter(adapter_name, config)
            return self._limiters[adapter_name]

    def get(self, adapter_name: str) -> RateLimiter | None:
        """Get a rate limiter for an adapter.

        Args:
            adapter_name: Name of the adapter

        Returns:
            Rate limiter instance or None if not found
        """
        with self._lock:
            return self._limiters.get(adapter_name)

    def get_all_metrics(self) -> dict[str, RateLimitMetrics]:
        """Get metrics for all registered rate limiters.

        Returns:
            Dictionary of adapter names to metrics
        """
        with self._lock:
            return {name: limiter.get_metrics() for name, limiter in self._limiters.items()}


# ---------------------------------------------------------------------------
# Rate Limiter Decorator
# ---------------------------------------------------------------------------


def with_rate_limiting(
    registry: RateLimiterRegistry,
    adapter_name: str,
    config: RateLimitConfig | None = None,
):
    """Decorator to apply rate limiting to adapter methods.

    Args:
        registry: Rate limiter registry
        adapter_name: Name of the adapter
        config: Rate limit configuration
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            limiter = registry.get_or_create(adapter_name, config)

            decision = limiter.check()
            if not decision.allowed:
                raise RuntimeError(f"Rate limit exceeded for {adapter_name}: {decision.reason}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = [
    "RateLimitStrategy",
    "LimitResult",
    "RateLimitConfig",
    "RateLimitDecision",
    "RateLimitMetrics",
    "SlidingWindowRateLimiter",
    "TokenBucketRateLimiter",
    "AdaptiveRateLimiter",
    "RateLimiter",
    "RateLimiterRegistry",
    "with_rate_limiting",
]
