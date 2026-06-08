"""Mock Feed Replacement — DASH-06.04.

System for systematically replacing mock data feeds with real data
sources. Provides identification of mock feeds, integration with
real data providers, fallback mechanisms, and validation of
data quality and completeness.
"""

from __future__ import annotations

import dataclasses
import enum
from collections.abc import Callable
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_ENABLE_VALIDATION: Final[bool] = True
DEFAULT_ENABLE_FALLBACK: Final[bool] = True
DEFAULT_MIN_DATA_QUALITY: Final[float] = 0.8
DEFAULT_MAX_FAILURES_BEFORE_FALLBACK: Final[int] = 3
DEFAULT_DATA_CACHE_SIZE: Final[int] = 1000

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class FeedType(enum.Enum):
    """Types of data feeds."""
    MARKET_DATA = "MARKET_DATA"
    ORDER_BOOK = "ORDER_BOOK"
    TRADES = "TRADES"
    NEWS = "NEWS"
    ON_CHAIN = "ON_CHAIN"
    ECONOMIC_DATA = "ECONOMIC_DATA"
    SOCIAL_SENTIMENT = "SOCIAL_SENTIMENT"
    PORTFOLIO = "PORTFOLIO"
    EXECUTION = "EXECUTION"
    GOVERNANCE = "GOVERNANCE"


class FeedStatus(enum.Enum):
    """Status of data feeds."""
    MOCK = "MOCK"  # Using mock data
    TRANSITIONING = "TRANSITIONING"  # Moving from mock to real
    LIVE = "LIVE"  # Using real data
    DEGRADED = "DEGRADED"  # Real data with issues
    FAILED = "FAILED"  # Real data failed, using fallback


class DataSource(enum.Enum):
    """Types of data sources."""
    MOCK_GENERATOR = "MOCK_GENERATOR"
    WEBSOCKET = "WEBSOCKET"
    REST_API = "REST_API"
    DATABASE = "DATABASE"
    FILE = "FILE"
    COMPOSITE = "COMPOSITE"  # Multiple sources combined


class ValidationLevel(enum.Enum):
    """Levels of data validation."""
    NONE = "NONE"  # No validation
    BASIC = "BASIC"  # Basic format validation
    STANDARD = "STANDARD"  # Standard validation
    STRICT = "STRICT"  # Strict validation with consistency checks


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class MockFeedReplacementConfig:
    """Configuration for mock feed replacement."""
    enable_validation: bool = DEFAULT_ENABLE_VALIDATION
    enable_fallback: bool = DEFAULT_ENABLE_FALLBACK
    min_data_quality: float = DEFAULT_MIN_DATA_QUALITY
    max_failures_before_fallback: int = DEFAULT_MAX_FAILURES_BEFORE_FALLBACK
    data_cache_size: int = DEFAULT_DATA_CACHE_SIZE
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    enable_monitoring: bool = True
    auto_transition_enabled: bool = False

    def __post_init__(self) -> None:
        if not (0.0 <= self.min_data_quality <= 1.0):
            raise ValueError("min_data_quality must be in [0.0, 1.0]")
        if self.max_failures_before_fallback < 1:
            raise ValueError("max_failures_before_fallback must be >= 1")
        if self.data_cache_size < 1:
            raise ValueError("data_cache_size must be >= 1")


@dataclasses.dataclass(frozen=True, slots=True)
class FeedDefinition:
    """Definition of a data feed."""
    feed_id: str
    feed_type: FeedType
    name: str
    description: str
    current_status: FeedStatus
    current_source: DataSource
    target_source: DataSource | None = None
    required_fields: list[str] = dataclasses.field(default_factory=list)
    update_frequency_ms: int = 1000
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.feed_id:
            raise ValueError("feed_id must be non-empty")
        if not self.name:
            raise ValueError("name must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class DataPoint:
    """A single data point from a feed."""
    feed_id: str
    timestamp_ns: int
    data: dict[str, Any]
    quality_score: float
    source: DataSource
    is_mock: bool = False
    validation_passed: bool = True
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class FeedValidationResult:
    """Result of validating a feed."""
    feed_id: str
    is_valid: bool
    quality_score: float
    missing_fields: list[str]
    invalid_values: dict[str, str]
    consistency_errors: list[str]
    timestamp_ns: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class ReplacementMetrics:
    """Metrics about mock feed replacement progress."""
    total_feeds: int
    mock_feeds: int
    live_feeds: int
    transitioning_feeds: int
    failed_feeds: int
    total_data_points: int
    mock_data_points: int
    real_data_points: int
    average_quality_score: float
    fallback_activations: int
    transitions_completed: int


# ---------------------------------------------------------------------------
# Mock Feed Replacer
# ---------------------------------------------------------------------------


class MockFeedReplacer:
    """System for replacing mock data feeds with real data sources.
    
    Provides systematic identification of mock feeds, integration
    with real data providers, validation of data quality, and
    fallback mechanisms to ensure continuous operation.
    """
    
    def __init__(
        self,
        config: MockFeedReplacementConfig | None = None,
    ) -> None:
        """Initialize the mock feed replacer.
        
        Args:
            config: Replacement configuration
        """
        self._config = config or MockFeedReplacementConfig()
        self._lock = Lock()
        
        # Feed definitions
        self._feeds: dict[str, FeedDefinition] = {}
        
        # Data sources
        self._data_sources: dict[str, Callable[[], DataPoint]] = {}
        
        # Data cache
        self._data_cache: dict[str, list[DataPoint]] = {}  # feed_id -> data points
        
        # Feed failures
        self._feed_failures: dict[str, int] = {}  # feed_id -> failure count
        
        # Validation results
        self._validation_results: dict[str, FeedValidationResult] = {}
        
        # Metrics
        self._metrics = ReplacementMetrics(
            total_feeds=0,
            mock_feeds=0,
            live_feeds=0,
            transitioning_feeds=0,
            failed_feeds=0,
            total_data_points=0,
            mock_data_points=0,
            real_data_points=0,
            average_quality_score=0.0,
            fallback_activations=0,
            transitions_completed=0,
        )
    
    def register_feed(
        self,
        feed_definition: FeedDefinition,
    ) -> None:
        """Register a data feed.
        
        Args:
            feed_definition: Feed definition
        """
        with self._lock:
            self._feeds[feed_definition.feed_id] = feed_definition
            self._data_cache[feed_definition.feed_id] = []
            
            # Update metrics
            self._metrics.total_feeds += 1
            if feed_definition.current_status == FeedStatus.MOCK:
                self._metrics.mock_feeds += 1
            elif feed_definition.current_status == FeedStatus.LIVE:
                self._metrics.live_feeds += 1
            elif feed_definition.current_status == FeedStatus.TRANSITIONING:
                self._metrics.transitioning_feeds += 1
            elif feed_definition.current_status == FeedStatus.FAILED:
                self._metrics.failed_feeds += 1
    
    def register_data_source(
        self,
        feed_id: str,
        source: Callable[[], DataPoint],
    ) -> None:
        """Register a data source for a feed.
        
        Args:
            feed_id: Feed identifier
            source: Data source callable
        """
        with self._lock:
            self._data_sources[feed_id] = source
    
    def transition_to_real(
        self,
        feed_id: str,
        target_source: DataSource,
    ) -> bool:
        """Transition a feed from mock to real data.
        
        Args:
            feed_id: Feed to transition
            target_source: Target data source
            
        Returns:
            True if transition initiated successfully
        """
        with self._lock:
            feed = self._feeds.get(feed_id)
            if not feed:
                return False
            
            if feed.current_status != FeedStatus.MOCK:
                return False
            
            # Update feed definition
            updated_feed = dataclasses.replace(
                feed,
                current_status=FeedStatus.TRANSITIONING,
                target_source=target_source,
            )
            self._feeds[feed_id] = updated_feed
            
            # Update metrics
            self._metrics.mock_feeds -= 1
            self._metrics.transitioning_feeds += 1
            
            return True
    
    def complete_transition(
        self,
        feed_id: str,
    ) -> bool:
        """Complete a transition to real data.
        
        Args:
            feed_id: Feed to complete transition for
            
        Returns:
            True if transition completed successfully
        """
        with self._lock:
            feed = self._feeds.get(feed_id)
            if not feed:
                return False
            
            if feed.current_status != FeedStatus.TRANSITIONING:
                return False
            
            # Update feed definition
            updated_feed = dataclasses.replace(
                feed,
                current_status=FeedStatus.LIVE,
                current_source=feed.target_source or DataSource.REST_API,
                target_source=None,
            )
            self._feeds[feed_id] = updated_feed
            
            # Update metrics
            self._metrics.transitioning_feeds -= 1
            self._metrics.live_feeds += 1
            self._metrics.transitions_completed += 1
            
            return True
    
    def fallback_to_mock(
        self,
        feed_id: str,
        reason: str = "",
    ) -> bool:
        """Fallback a feed to mock data.
        
        Args:
            feed_id: Feed to fallback
            reason: Reason for fallback
            
        Returns:
            True if fallback successful
        """
        with self._lock:
            feed = self._feeds.get(feed_id)
            if not feed:
                return False
            
            # Update feed definition
            updated_feed = dataclasses.replace(
                feed,
                current_status=FeedStatus.MOCK,
                current_source=DataSource.MOCK_GENERATOR,
            )
            self._feeds[feed_id] = updated_feed
            
            # Update metrics
            self._metrics.failed_feeds += 1
            if feed.current_status == FeedStatus.LIVE:
                self._metrics.live_feeds -= 1
            elif feed.current_status == FeedStatus.TRANSITIONING:
                self._metrics.transitioning_feeds -= 1
            self._metrics.mock_feeds += 1
            self._metrics.fallback_activations += 1
            
            # Reset failures
            self._feed_failures[feed_id] = 0
            
            return True
    
    def get_data_point(
        self,
        feed_id: str,
    ) -> DataPoint | None:
        """Get a data point from a feed.
        
        Args:
            feed_id: Feed identifier
            
        Returns:
            Data point or None if feed not found
        """
        
        with self._lock:
            feed = self._feeds.get(feed_id)
            if not feed:
                return None
            
            # Try to get data from real source
            if feed.current_source != DataSource.MOCK_GENERATOR:
                source = self._data_sources.get(feed_id)
                if source:
                    try:
                        data_point = source()
                        
                        # Validate if enabled
                        if self._config.enable_validation:
                            validation_result = self._validate_data_point(data_point, feed)
                            if not validation_result.is_valid:
                                raise ValueError(f"Validation failed: {validation_result.missing_fields}")
                        
                        # Add to cache
                        cache = self._data_cache.get(feed_id, [])
                        cache.append(data_point)
                        if len(cache) > self._config.data_cache_size:
                            cache.pop(0)
                        
                        # Update metrics
                        self._metrics.total_data_points += 1
                        self._metrics.real_data_points += 1
                        
                        # Reset failures on success
                        self._feed_failures[feed_id] = 0
                        
                        return data_point
                    except Exception as e:
                        # Increment failure count
                        self._feed_failures[feed_id] = \
                            self._feed_failures.get(feed_id, 0) + 1
                        
                        # Check if we should fallback
                        if (self._config.enable_fallback and
                            self._feed_failures[feed_id] >= self._config.max_failures_before_fallback):
                            self.fallback_to_mock(feed_id, str(e))
            
            # Fallback to mock data
            mock_data_point = self._generate_mock_data_point(feed)
            
            # Add to cache
            cache = self._data_cache.get(feed_id, [])
            cache.append(mock_data_point)
            if len(cache) > self._config.data_cache_size:
                cache.pop(0)
            
            # Update metrics
            self._metrics.total_data_points += 1
            self._metrics.mock_data_points += 1
            
            return mock_data_point
    
    def validate_feed(
        self,
        feed_id: str,
    ) -> FeedValidationResult | None:
        """Validate a feed's data quality.
        
        Args:
            feed_id: Feed to validate
            
        Returns:
            Validation result or None if feed not found
        """
        with self._lock:
            feed = self._feeds.get(feed_id)
            if not feed:
                return None
            
            # Get recent data points from cache
            cache = self._data_cache.get(feed_id, [])
            if not cache:
                return FeedValidationResult(
                    feed_id=feed_id,
                    is_valid=False,
                    quality_score=0.0,
                    missing_fields=feed.required_fields,
                    invalid_values={},
                    consistency_errors=["No data available"],
                    timestamp_ns=0,
                )
            
            # Calculate quality score
            quality_scores = [dp.quality_score for dp in cache]
            average_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
            # Check for missing fields
            missing_fields = []
            for data_point in cache[-10:]:  # Check last 10 points
                for field in feed.required_fields:
                    if field not in data_point.data:
                        missing_fields.append(field)
            
            missing_fields = list(set(missing_fields))
            
            return FeedValidationResult(
                feed_id=feed_id,
                is_valid=average_quality >= self._config.min_data_quality and len(missing_fields) == 0,
                quality_score=average_quality,
                missing_fields=missing_fields,
                invalid_values={},
                consistency_errors=[],
                timestamp_ns=cache[-1].timestamp_ns if cache else 0,
            )
    
    def get_metrics(self) -> ReplacementMetrics:
        """Get replacement metrics.
        
        Returns:
            Current metrics
        """
        with self._lock:
            # Calculate average quality score
            total_quality = 0.0
            quality_count = 0
            for cache in self._data_cache.values():
                for data_point in cache:
                    total_quality += data_point.quality_score
                    quality_count += 1
            
            avg_quality = total_quality / quality_count if quality_count > 0 else 0.0
            
            return dataclasses.replace(
                self._metrics,
                average_quality_score=avg_quality,
            )
    
    def _validate_data_point(
        self,
        data_point: DataPoint,
        feed: FeedDefinition,
    ) -> FeedValidationResult:
        """Validate a data point.
        
        Args:
            data_point: Data point to validate
            feed: Feed definition
            
        Returns:
            Validation result
        """
        import time
        
        missing_fields = []
        for field in feed.required_fields:
            if field not in data_point.data:
                missing_fields.append(field)
        
        invalid_values = {}
        for field, value in data_point.data.items():
            # Basic validation (can be extended)
            if value is None:
                invalid_values[field] = "Value is None"
        
        is_valid = (
            len(missing_fields) == 0 and
            len(invalid_values) == 0 and
            data_point.quality_score >= self._config.min_data_quality
        )
        
        return FeedValidationResult(
            feed_id=feed.feed_id,
            is_valid=is_valid,
            quality_score=data_point.quality_score,
            missing_fields=missing_fields,
            invalid_values=invalid_values,
            consistency_errors=[],
            timestamp_ns=time.time_ns(),
        )
    
    def _generate_mock_data_point(self, feed: FeedDefinition) -> DataPoint:
        """Generate mock data for a feed.
        
        Args:
            feed: Feed definition
            
        Returns:
            Mock data point
        """
        import random
        import time
        
        # Generate mock data based on feed type
        mock_data = {}
        
        if feed.feed_type == FeedType.MARKET_DATA:
            mock_data = {
                "symbol": "BTC/USDT",
                "price": random.uniform(30000, 70000),
                "volume": random.uniform(100, 1000),
                "change_24h": random.uniform(-5, 5),
            }
        elif feed.feed_type == FeedType.NEWS:
            mock_data = {
                "headline": "Market shows positive momentum",
                "sentiment": random.choice(["positive", "negative", "neutral"]),
                "source": "mock_feed",
            }
        else:
            # Generic mock data
            mock_data = {
                "value": random.uniform(0, 100),
                "timestamp": time.time_ns(),
            }
        
        return DataPoint(
            feed_id=feed.feed_id,
            timestamp_ns=time.time_ns(),
            data=mock_data,
            quality_score=1.0,  # Mock data always has perfect quality
            source=DataSource.MOCK_GENERATOR,
            is_mock=True,
        )


# ---------------------------------------------------------------------------
# Mock Feed Replacement Manager
# ---------------------------------------------------------------------------


class MockFeedReplacementManager:
    """Manager for mock feed replacement."""
    
    def __init__(self, config: MockFeedReplacementConfig | None = None) -> None:
        """Initialize the mock feed replacement manager.
        
        Args:
            config: Replacement configuration
        """
        self._config = config or MockFeedReplacementConfig()
        self._replacer = MockFeedReplacer(config)
    
    def register_feed(self, feed_definition: FeedDefinition) -> None:
        """Register a feed.
        
        Args:
            feed_definition: Feed definition
        """
        self._replacer.register_feed(feed_definition)
    
    def register_data_source(
        self,
        feed_id: str,
        source: Callable[[], DataPoint],
    ) -> None:
        """Register a data source.
        
        Args:
            feed_id: Feed ID
            source: Data source
        """
        self._replacer.register_data_source(feed_id, source)
    
    def transition_to_real(
        self,
        feed_id: str,
        target_source: DataSource,
    ) -> bool:
        """Transition to real data.
        
        Args:
            feed_id: Feed ID
            target_source: Target source
            
        Returns:
            True if successful
        """
        return self._replacer.transition_to_real(feed_id, target_source)
    
    def complete_transition(self, feed_id: str) -> bool:
        """Complete transition.
        
        Args:
            feed_id: Feed ID
            
        Returns:
            True if successful
        """
        return self._replacer.complete_transition(feed_id)
    
    def get_data_point(self, feed_id: str) -> DataPoint | None:
        """Get data point.
        
        Args:
            feed_id: Feed ID
            
        Returns:
            Data point or None
        """
        return self._replacer.get_data_point(feed_id)
    
    def get_metrics(self) -> ReplacementMetrics:
        """Get metrics.
        
        Returns:
            Current metrics
        """
        return self._replacer.get_metrics()


__all__ = [
    "FeedType",
    "FeedStatus",
    "DataSource",
    "ValidationLevel",
    "MockFeedReplacementConfig",
    "FeedDefinition",
    "DataPoint",
    "FeedValidationResult",
    "ReplacementMetrics",
    "MockFeedReplacer",
    "MockFeedReplacementManager",
]
