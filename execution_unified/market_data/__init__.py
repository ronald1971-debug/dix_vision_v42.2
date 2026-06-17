"""Market Data Infrastructure - unified market data ingestion and processing.

Provides:
- Aggregator: Multi-source market data aggregation with gap detection
- BookBuilder: L2 order book construction from streaming deltas
- OrderBook: High-performance order book data structures
- Normalizer: Cross-venue data normalization
- LatencyTracker: Performance monitoring and analysis

RUNTIME_SAFE design (no clock reads, no external I/O, pure functional core).
"""

from .aggregator import (
    BookDelta,
    BookGap,
    OrderBookLevel,
    OrderBookSnapshot,
    OrderBookAggregator,
    parse_binance_trade,
    parse_binance_book_snapshot,
    parse_binance_book_delta,
)

from .book_builder import (
    BookDelta as BookBuilderDelta,
    BookBuilder,
    OrderBookState,
)

from .orderbook import (
    L2OrderBook as UnifiedOrderBook,
    OrderBookSnapshot as UnifiedOrderBookSnapshot,
    PriceLevelMap,
    PurePyPriceLevelMap,
    pure_python_orderbook_factory as orderbook_factory,
    sortedcontainers_orderbook_factory,
)

from .normalizer import (
    NormalizedBook,
    NormalizedLevel,
    NormalizedTick,
)

from .latency_tracker import (
    LatencyTracker,
    LatencyStats,
    LatencySample,
)

__all__ = [
    # Aggregator
    "BookDelta",
    "BookGap",
    "OrderBookLevel",
    "OrderBookSnapshot",
    "OrderBookAggregator",
    "parse_binance_trade",
    "parse_binance_book_snapshot",
    "parse_binance_book_delta",
    # BookBuilder
    "BookBuilderDelta",
    "BookBuilder",
    "OrderBookState",
    # OrderBook
    "UnifiedOrderBook",
    "UnifiedOrderBookSnapshot",
    "PriceLevelMap",
    "PurePyPriceLevelMap",
    "orderbook_factory",
    "sortedcontainers_orderbook_factory",
    # Normalizer
    "NormalizedBook",
    "NormalizedLevel",
    "NormalizedTick",
    # LatencyTracker
    "LatencyTracker",
    "LatencyStats",
    "LatencySample",
]