"""Market Context Memory — INT-07.02.

Market context memory system for the intelligence engine to maintain
historical market state, patterns, and relationships. Provides
context-aware decision making by storing and retrieving relevant
market information with efficient indexing and retrieval.
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

DEFAULT_MEMORY_SIZE: Final[int] = 10_000
DEFAULT_CONTEXT_WINDOW_NS: Final[int] = 3600_000_000_000  # 1 hour
DEFAULT_ENABLE_PATTERN_DETECTION: Final[bool] = True
DEFAULT_ENABLE_COMPRESSION: Final[bool] = False
DEFAULT_RETENTION_DAYS: Final[int] = 30

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ContextType(enum.Enum):
    """Types of market context data."""
    PRICE = "PRICE"
    VOLUME = "VOLUME"
    VOLATILITY = "VOLATILITY"
    SPREAD = "SPREAD"
    ORDER_BOOK = "ORDER_BOOK"
    TRADES = "TRADES"
    SENTIMENT = "SENTIMENT"
    MACRO = "MACRO"
    NEWS = "NEWS"
    ON_CHAIN = "ON_CHAIN"


class MemoryPriority(enum.Enum):
    """Priority levels for memory storage."""
    CRITICAL = "CRITICAL"  # Always retain
    HIGH = "HIGH"  # Prefer to retain
    NORMAL = "NORMAL"  # Standard retention
    LOW = "LOW"  # May be evicted first


class PatternType(enum.Enum):
    """Types of patterns detected in market context."""
    TREND = "TREND"
    REVERSAL = "REVERSAL"
    CONSOLIDATION = "CONSOLIDATION"
    BREAKOUT = "BREAKOUT"
    MOMENTUM = "MOMENTUM"
    MEAN_REVERSION = "MEAN_REVERSION"
    SEASONAL = "SEASONAL"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class MemoryConfig:
    """Configuration for market context memory."""
    memory_size: int = DEFAULT_MEMORY_SIZE
    context_window_ns: int = DEFAULT_CONTEXT_WINDOW_NS
    enable_pattern_detection: bool = DEFAULT_ENABLE_PATTERN_DETECTION
    enable_compression: bool = DEFAULT_ENABLE_COMPRESSION
    retention_days: int = DEFAULT_RETENTION_DAYS
    enable_indexing: bool = True
    enable_similarity_search: bool = True

    def __post_init__(self) -> None:
        if self.memory_size < 1:
            raise ValueError("memory_size must be >= 1")
        if self.context_window_ns < 1:
            raise ValueError("context_window_ns must be >= 1")
        if self.retention_days < 1:
            raise ValueError("retention_days must be >= 1")


@dataclasses.dataclass(frozen=True, slots=True)
class MarketContext:
    """A piece of market context data."""
    context_id: str
    context_type: ContextType
    symbol: str
    timestamp_ns: int
    data: dict[str, Any]
    priority: MemoryPriority = MemoryPriority.NORMAL
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.context_id:
            raise ValueError("context_id must be non-empty")
        if not self.symbol:
            raise ValueError("symbol must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class MarketPattern:
    """A detected pattern in market context."""
    pattern_id: str
    pattern_type: PatternType
    symbol: str
    start_timestamp_ns: int
    end_timestamp_ns: int
    confidence: float
    characteristics: dict[str, Any]
    related_contexts: list[str]  # context_ids
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pattern_id:
            raise ValueError("pattern_id must be non-empty")
        if not self.symbol:
            raise ValueError("symbol must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class ContextQuery:
    """Query for retrieving market context."""
    symbol: str | None = None
    context_type: ContextType | None = None
    start_timestamp_ns: int | None = None
    end_timestamp_ns: int | None = None
    limit: int = 100
    priority_filter: MemoryPriority | None = None
    data_filters: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class MemoryMetrics:
    """Metrics about market context memory."""
    total_contexts: int
    contexts_by_type: dict[str, int]
    contexts_by_symbol: dict[str, int]
    contexts_by_priority: dict[str, int]
    total_patterns: int
    patterns_by_type: dict[str, int]
    memory_utilization: float
    average_context_age_ns: int
    retrieval_count: int
    patterns_detected_today: int


# ---------------------------------------------------------------------------
# Market Context Memory
# ---------------------------------------------------------------------------


class MarketContextMemory:
    """Market context memory system.
    
    Maintains historical market state, patterns, and relationships
    to provide context-aware decision making. Features:
    
    - Efficient storage and retrieval of market context
    - Time-windowed access to recent context
    - Pattern detection in market behavior
    - Similarity search for related contexts
    - Priority-based retention management
    - Comprehensive metrics and monitoring
    """
    
    def __init__(
        self,
        config: MemoryConfig | None = None,
    ) -> None:
        """Initialize the market context memory.
        
        Args:
            config: Memory configuration
        """
        self._config = config or MemoryConfig()
        self._lock = Lock()
        
        # Context storage
        self._contexts: deque[MarketContext] = deque(maxlen=self._config.memory_size)
        
        # Indexes
        self._contexts_by_symbol: dict[str, list[str]] = {}  # symbol -> [context_ids]
        self._contexts_by_type: dict[ContextType, list[str]] = {}  # type -> [context_ids]
        self._contexts_by_time: dict[int, list[str]] = {}  # timestamp -> [context_ids]
        
        # Pattern storage
        self._patterns: dict[str, MarketPattern] = {}
        self._patterns_by_symbol: dict[str, list[str]] = {}  # symbol -> [pattern_ids]
        
        # Metrics
        self._metrics = self._init_metrics()
        self._retrieval_count = 0
    
    def store_context(
        self,
        context: MarketContext,
    ) -> None:
        """Store market context in memory.
        
        Args:
            context: Market context to store
        """
        with self._lock:
            # Add to storage
            self._contexts.append(context)
            
            # Update indexes
            self._update_indexes(context)
            
            # Update metrics
            self._metrics.total_contexts += 1
            self._metrics.contexts_by_type[context.context_type.value] = \
                self._metrics.contexts_by_type.get(context.context_type.value, 0) + 1
            self._metrics.contexts_by_symbol[context.symbol] = \
                self._metrics.contexts_by_symbol.get(context.symbol, 0) + 1
            self._metrics.contexts_by_priority[context.priority.value] = \
                self._metrics.contexts_by_priority.get(context.priority.value, 0) + 1
            
            # Detect patterns if enabled
            if self._config.enable_pattern_detection:
                self._detect_patterns_for_context(context)
    
    def retrieve_context(
        self,
        query: ContextQuery,
    ) -> list[MarketContext]:
        """Retrieve market context based on query.
        
        Args:
            query: Context query parameters
            
        Returns:
            List of matching contexts
        """
        with self._lock:
            self._retrieval_count += 1
            
            results = list(self._contexts)
            
            # Filter by symbol
            if query.symbol:
                context_ids = set(self._contexts_by_symbol.get(query.symbol, []))
                results = [c for c in results if c.context_id in context_ids]
            
            # Filter by type
            if query.context_type:
                context_ids = set(self._contexts_by_type.get(query.context_type, []))
                results = [c for c in results if c.context_id in context_ids]
            
            # Filter by time range
            if query.start_timestamp_ns:
                results = [c for c in results if c.timestamp_ns >= query.start_timestamp_ns]
            
            if query.end_timestamp_ns:
                results = [c for c in results if c.timestamp_ns <= query.end_timestamp_ns]
            
            # Filter by priority
            if query.priority_filter:
                results = [c for c in results if c.priority == query.priority_filter]
            
            # Filter by data fields
            for key, value in query.data_filters.items():
                results = [c for c in results if c.data.get(key) == value]
            
            # Apply limit
            results = results[:query.limit]
            
            return results
    
    def get_recent_context(
        self,
        symbol: str,
        context_type: ContextType | None = None,
        window_ns: int | None = None,
    ) -> list[MarketContext]:
        """Get recent context for a symbol within time window.
        
        Args:
            symbol: Trading symbol
            context_type: Optional context type filter
            window_ns: Time window in nanoseconds
            
        Returns:
            Recent contexts
        """
        import time
        
        if window_ns is None:
            window_ns = self._config.context_window_ns
        
        query = ContextQuery(
            symbol=symbol,
            context_type=context_type,
            start_timestamp_ns=time.time_ns() - window_ns,
        )
        
        return self.retrieve_context(query)
    
    def detect_pattern(
        self,
        pattern: MarketPattern,
    ) -> None:
        """Store a detected market pattern.
        
        Args:
            pattern: Market pattern to store
        """
        with self._lock:
            self._patterns[pattern.pattern_id] = pattern
            
            # Update symbol index
            if pattern.symbol not in self._patterns_by_symbol:
                self._patterns_by_symbol[pattern.symbol] = []
            self._patterns_by_symbol[pattern.symbol].append(pattern.pattern_id)
            
            # Update metrics
            self._metrics.total_patterns += 1
            self._metrics.patterns_by_type[pattern.pattern_type.value] = \
                self._metrics.patterns_by_type.get(pattern.pattern_type.value, 0) + 1
    
    def get_patterns(
        self,
        symbol: str | None = None,
        pattern_type: PatternType | None = None,
    ) -> list[MarketPattern]:
        """Get detected patterns.
        
        Args:
            symbol: Optional symbol filter
            pattern_type: Optional pattern type filter
            
        Returns:
            List of patterns
        """
        with self._lock:
            results = list(self._patterns.values())
            
            if symbol:
                pattern_ids = set(self._patterns_by_symbol.get(symbol, []))
                results = [p for p in results if p.pattern_id in pattern_ids]
            
            if pattern_type:
                results = [p for p in results if p.pattern_type == pattern_type]
            
            return results
    
    def find_similar_contexts(
        self,
        context: MarketContext,
        threshold: float = 0.7,
        limit: int = 10,
    ) -> list[tuple[MarketContext, float]]:
        """Find contexts similar to the given context.
        
        Args:
            context: Reference context
            threshold: Similarity threshold
            limit: Maximum number of results
            
        Returns:
            List of (context, similarity_score) tuples
        """
        if not self._config.enable_similarity_search:
            return []
        
        with self._lock:
            similarities = []
            
            for stored_context in self._contexts:
                if stored_context.context_id == context.context_id:
                    continue
                
                similarity = self._calculate_similarity(context, stored_context)
                if similarity >= threshold:
                    similarities.append((stored_context, similarity))
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
    
    def get_metrics(self) -> MemoryMetrics:
        """Get memory metrics.
        
        Returns:
            Current metrics
        """
        import time
        
        with self._lock:
            # Calculate memory utilization
            memory_utilization = len(self._contexts) / self._config.memory_size
            
            # Calculate average context age
            if self._contexts:
                now_ns = time.time_ns()
                ages = [(now_ns - c.timestamp_ns) for c in self._contexts]
                avg_age = sum(ages) / len(ages)
            else:
                avg_age = 0
            
            return dataclasses.replace(
                self._metrics,
                memory_utilization=memory_utilization,
                average_context_age_ns=int(avg_age),
                retrieval_count=self._retrieval_count,
            )
    
    def cleanup_old_contexts(self, retention_days: int | None = None) -> int:
        """Remove contexts older than retention period.
        
        Args:
            retention_days: Retention period in days
            
        Returns:
            Number of contexts removed
        """
        import time
        
        if retention_days is None:
            retention_days = self._config.retention_days
        
        cutoff_ns = time.time_ns() - (retention_days * 24 * 3600 * 1_000_000_000)
        
        with self._lock:
            original_count = len(self._contexts)
            
            # Remove old contexts
            self._contexts = deque(
                [c for c in self._contexts if c.timestamp_ns > cutoff_ns],
                maxlen=self._config.memory_size
            )
            
            # Rebuild indexes
            self._rebuild_indexes()
            
            removed = original_count - len(self._contexts)
            
            # Update metrics
            self._metrics.total_contexts = len(self._contexts)
            
            return removed
    
    def _update_indexes(self, context: MarketContext) -> None:
        """Update indexes for a context.
        
        Args:
            context: Context to index
        """
        # Symbol index
        if context.symbol not in self._contexts_by_symbol:
            self._contexts_by_symbol[context.symbol] = []
        self._contexts_by_symbol[context.symbol].append(context.context_id)
        
        # Type index
        if context.context_type not in self._contexts_by_type:
            self._contexts_by_type[context.context_type] = []
        self._contexts_by_type[context.context_type].append(context.context_id)
        
        # Time index
        if context.timestamp_ns not in self._contexts_by_time:
            self._contexts_by_time[context.timestamp_ns] = []
        self._contexts_by_time[context.timestamp_ns].append(context.context_id)
    
    def _rebuild_indexes(self) -> None:
        """Rebuild all indexes from current contexts."""
        self._contexts_by_symbol.clear()
        self._contexts_by_type.clear()
        self._contexts_by_time.clear()
        
        for context in self._contexts:
            self._update_indexes(context)
    
    def _detect_patterns_for_context(self, context: MarketContext) -> None:
        """Detect patterns in a context (placeholder implementation).
        
        Args:
            context: Context to analyze for patterns
        """
        # Analyze context data for patterns like trends, reversals, breakouts, etc.
        import time
        
        # Get recent contexts for analysis
        recent_contexts = self._retrieve_recent_contexts(context, 20)
        
        if len(recent_contexts) < 3:
            return  # Need minimum data points for pattern detection
        
        # Detect trend pattern
        if context.context_type == ContextType.PRICE:
            self._detect_price_trend(context, recent_contexts)
        
        # Detect volatility pattern
        if context.context_type in (ContextType.PRICE, ContextType.VOLATILITY):
            self._detect_volatility_pattern(context, recent_contexts)
        
        # Detect volume pattern
        if context.context_type == ContextType.VOLUME:
            self._detect_volume_pattern(context, recent_contexts)
        
        # Create pattern detection event if significant pattern found
        pattern_type = self._determine_pattern_type(context, recent_contexts)
        if pattern_type != PatternType.UNKNOWN:
            self._register_detected_pattern(context, pattern_type, recent_contexts)
    
    def _retrieve_recent_contexts(
        self,
        context: MarketContext,
        count: int = 10,
    ) -> list[MarketContext]:
        """Retrieve recent contexts of the same type and symbol.
        
        Args:
            context: Reference context
            count: Number of contexts to retrieve
            
        Returns:
            List of recent contexts
        """
        contexts = []
        for ctx in reversed(self._contexts):
            if (ctx.symbol == context.symbol and
                ctx.context_type == context.context_type and
                ctx.timestamp_ns < context.timestamp_ns):
                contexts.append(ctx)
                if len(contexts) >= count:
                    break
        return contexts
    
    def _detect_price_trend(
        self,
        context: MarketContext,
        recent_contexts: list[MarketContext],
    ) -> None:
        """Detect trend patterns in price data.
        
        Args:
            context: Current context
            recent_contexts: Recent contexts to analyze
        """
        prices = [ctx.data.get("price", 0.0) for ctx in recent_contexts]
        if len(prices) < 2:
            return
        
        # Simple trend detection using linear regression slope
        x = list(range(len(prices)))
        avg_price = sum(prices) / len(prices)
        
        # Calculate slope
        n = len(prices)
        sum_x = sum(x)
        sum_y = sum(prices)
        sum_xy = sum(xi * yi for xi, yi in zip(x, prices))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum(x * x) - sum_x * sum_x)) if n > 1 else 0
        
        # Determine trend type
        if slope > 0 and abs(slope) > avg_price * 0.01:
            return PatternType.TREND
        elif slope < 0 and abs(slope) > avg_price * 0.01:
            return PatternType.TREND
        elif abs(slope) < avg_price * 0.01:
            return PatternType.CONSOLIDATION
    
    def _detect_volatility_pattern(
        self,
        context: MarketContext,
        recent_contexts: list[MarketContext],
    ) -> None:
        """Detect volatility patterns.
        
        Args:
            context: Current context
            recent_contexts: Recent contexts to analyze
        """
        volatilities = [ctx.data.get("volatility", 0.0) for ctx in recent_contexts]
        if len(volatilities) < 3:
            return
        
        # Check for volatility breakouts
        recent_vol = volatilities[-1]
        avg_vol = sum(volatilities[:-1]) / (len(volatilities) - 1)
        
        if recent_vol > avg_vol * 2.0:
            return PatternType.BREAKOUT
        elif recent_vol < avg_vol * 0.5:
            return PatternType.CONSOLIDATION
    
    def _detect_volume_pattern(
        self,
        context: MarketContext,
        recent_contexts: list[MarketContext],
    ) -> None:
        """Detect volume patterns.
        
        Args:
            context: Current context
            recent_contexts: Recent contexts to analyze
        """
        volumes = [ctx.data.get("volume", 0.0) for ctx in recent_contexts]
        if len(volumes) < 3:
            return
        
        recent_vol = volumes[-1]
        avg_vol = sum(volumes[:-1]) / (len(volumes) - 1)
        
        if recent_vol > avg_vol * 2.0:
            return PatternType.BREAKOUT
        elif recent_vol < avg_vol * 0.5:
            return PatternType.CONSOLIDATION
    
    def _determine_pattern_type(
        self,
        context: MarketContext,
        recent_contexts: list[MarketContext],
    ) -> PatternType:
        """Determine the most likely pattern type.
        
        Args:
            context: Current context
            recent_contexts: Recent contexts to analyze
            
        Returns:
            Detected pattern type
        """
        # Simple pattern determination based on data analysis
        prices = [ctx.data.get("price", 0.0) for ctx in recent_contexts]
        if len(prices) < 2:
            return PatternType.UNKNOWN
        
        # Calculate price momentum
        if len(prices) >= 3:
            short_momentum = (prices[-1] - prices[-3]) / prices[-3]
            long_momentum = (prices[-1] - prices[0]) / prices[0]
            
            if abs(short_momentum) > 0.05:
                return PatternType.TREND
            elif abs(long_momentum) > 0.02:
                return PatternType.TREND
            elif abs(short_momentum) < 0.01:
                return PatternType.CONSOLIDATION
        
        return PatternType.UNKNOWN
    
    def _register_detected_pattern(
        self,
        context: MarketContext,
        pattern_type: PatternType,
        recent_contexts: list[MarketContext],
    ) -> None:
        """Register a detected pattern.
        
        Args:
            context: Current context
            pattern_type: Detected pattern type
            recent_contexts: Contexts used for detection
        """
        import secrets
        import time
        
        # Create pattern record
        pattern = MarketPattern(
            pattern_id=secrets.token_hex(16),
            pattern_type=pattern_type,
            symbol=context.symbol,
            start_timestamp_ns=recent_contexts[0].timestamp_ns if recent_contexts else context.timestamp_ns,
            end_timestamp_ns=context.timestamp_ns,
            confidence=0.7,  # Base confidence
            characteristics={
                "data_points": len(recent_contexts),
                "context_type": context.context_type.value,
            },
            related_contexts=[ctx.context_id for ctx in recent_contexts],
            metadata={"detection_method": "simple_momentum"},
        )
        
        self.detect_pattern(pattern)
    
    def _calculate_similarity(
        self,
        context1: MarketContext,
        context2: MarketContext,
    ) -> float:
        """Calculate similarity between two contexts.
        
        Args:
            context1: First context
            context2: Second context
            
        Returns:
            Similarity score in [0.0, 1.0]
        """
        # Simple similarity calculation (can be enhanced)
        similarity = 0.0
        
        # Same symbol and type
        if context1.symbol == context2.symbol:
            similarity += 0.3
        if context1.context_type == context2.context_type:
            similarity += 0.3
        
        # Time proximity
        time_diff = abs(context1.timestamp_ns - context2.timestamp_ns)
        if time_diff < 1_000_000_000:  # 1 second
            similarity += 0.2
        elif time_diff < 60_000_000_000:  # 1 minute
            similarity += 0.1
        
        # Data similarity (simple comparison)
        common_keys = set(context1.data.keys()) & set(context2.data.keys())
        if common_keys:
            matching_values = 0
            for key in common_keys:
                if context1.data[key] == context2.data[key]:
                    matching_values += 1
            similarity += (matching_values / len(common_keys)) * 0.2
        
        return min(1.0, similarity)
    
    def _init_metrics(self) -> MemoryMetrics:
        """Initialize memory metrics."""
        return MemoryMetrics(
            total_contexts=0,
            contexts_by_type={},
            contexts_by_symbol={},
            contexts_by_priority={},
            total_patterns=0,
            patterns_by_type={},
            memory_utilization=0.0,
            average_context_age_ns=0,
            retrieval_count=0,
            patterns_detected_today=0,
        )


# ---------------------------------------------------------------------------
# Market Context Memory Manager
# ---------------------------------------------------------------------------


class MarketContextMemoryManager:
    """Manager for market context memory."""
    
    def __init__(self, config: MemoryConfig | None = None) -> None:
        """Initialize the market context memory manager.
        
        Args:
            config: Memory configuration
        """
        self._config = config or MemoryConfig()
        self._memory = MarketContextMemory(config)
    
    def store_context(self, context: MarketContext) -> None:
        """Store a context.
        
        Args:
            context: Market context
        """
        self._memory.store_context(context)
    
    def retrieve_context(self, query: ContextQuery) -> list[MarketContext]:
        """Retrieve contexts.
        
        Args:
            query: Context query
            
        Returns:
            Matching contexts
        """
        return self._memory.retrieve_context(query)
    
    def get_recent_context(
        self,
        symbol: str,
        context_type: ContextType | None = None,
        window_ns: int | None = None,
    ) -> list[MarketContext]:
        """Get recent context.
        
        Args:
            symbol: Trading symbol
            context_type: Context type filter
            window_ns: Time window
            
        Returns:
            Recent contexts
        """
        return self._memory.get_recent_context(symbol, context_type, window_ns)
    
    def detect_pattern(self, pattern: MarketPattern) -> None:
        """Detect a pattern.
        
        Args:
            pattern: Market pattern
        """
        self._memory.detect_pattern(pattern)
    
    def get_patterns(
        self,
        symbol: str | None = None,
        pattern_type: PatternType | None = None,
    ) -> list[MarketPattern]:
        """Get patterns.
        
        Args:
            symbol: Symbol filter
            pattern_type: Pattern type filter
            
        Returns:
            Patterns
        """
        return self._memory.get_patterns(symbol, pattern_type)
    
    def get_metrics(self) -> MemoryMetrics:
        """Get metrics.
        
        Returns:
            Current metrics
        """
        return self._memory.get_metrics()


__all__ = [
    "ContextType",
    "MemoryPriority",
    "PatternType",
    "MemoryConfig",
    "MarketContext",
    "MarketPattern",
    "ContextQuery",
    "MemoryMetrics",
    "MarketContextMemory",
    "MarketContextMemoryManager",
]
