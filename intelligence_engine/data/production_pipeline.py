"""Production-Grade Data Pipeline Implementation.

Real-time data processing pipelines for production market data integration.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any, Dict, List, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import time
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DataQuality(str, Enum):
    """Data quality levels."""
    HIGH = "HIGH"  # Real-time, complete, validated
    MEDIUM = "MEDIUM"  # Slightly delayed, mostly complete
    LOW = "LOW"  # Delayed, incomplete, needs validation
    INVALID = "INVALID"  # Failed validation, should be rejected


class DataSource(str, Enum):
    """Production data sources."""
    WEBSOCKET = "WEBSOCKET"  # Real-time streaming data
    REST_API = "REST_API"  # Poll-based data
    FIX_PROTOCOL = "FIX_PROTOCOL"  # Financial Information Exchange
    DATABASE = "DATABASE"  # Historical data storage
    CACHE = "CACHE"  # Redis/Memcached
    MESSAGE_QUEUE = "MESSAGE_QUEUE"  # Kafka/RabbitMQ


@dataclass
class MarketDataMessage:
    """Standardized market data message for production pipelines."""
    symbol: str
    timestamp: float
    price: float
    volume: float
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    source: DataSource
    quality: DataQuality
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "price": self.price,
            "volume": self.volume,
            "bid": self.bid,
            "ask": self.ask,
            "bid_size": self.bid_size,
            "ask_size": self.ask_size,
            "source": self.source.value,
            "quality": self.quality.value,
            "metadata": self.metadata
        }


class DataValidator:
    """Real data validation for production pipelines."""

    @staticmethod
    def validate_market_data(message: MarketDataMessage) -> tuple[bool, DataQuality, List[str]]:
        """Validate market data message."""
        issues = []

        # Basic validation
        if message.price <= 0:
            issues.append("Price must be positive")
        if message.volume < 0:
            issues.append("Volume cannot be negative")
        if message.bid <= 0:
            issues.append("Bid must be positive")
        if message.ask <= 0:
            issues.append("Ask must be positive")
        if message.bid >= message.ask:
            issues.append("Bid must be less than ask")

        # Timestamp validation
        current_time = time.time()
        if abs(current_time - message.timestamp) > 5.0:  # 5 seconds stale
            issues.append(f"Data is stale: {abs(current_time - message.timestamp):.2f}s old")

        # Spread validation
        spread = (message.ask - message.bid) / message.bid if message.bid > 0 else float('inf')
        if spread > 0.05:  # 5% spread threshold
            issues.append(f"Spread too wide: {spread:.4f}")

        if issues:
            return False, DataQuality.INVALID, issues

        # Determine quality level
        if abs(current_time - message.timestamp) < 0.1 and spread < 0.01:
            return True, DataQuality.HIGH, []
        elif abs(current_time - message.timestamp) < 1.0 and spread < 0.02:
            return True, DataQuality.MEDIUM, []
        else:
            return True, DataQuality.LOW, []


class DataBuffer:
    """Thread-safe data buffer for real-time processing."""

    def __init__(self, max_size: int = 1000):
        self._buffer: deque = deque(maxlen=max_size)
        self._lock = threading.Lock()
        self._max_size = max_size

    def put(self, message: MarketDataMessage) -> None:
        """Add message to buffer."""
        with self._lock:
            self._buffer.append(message)

    def get(self, count: int = 1) -> List[MarketDataMessage]:
        """Get messages from buffer."""
        with self._lock:
            if count == 1:
                return [self._buffer.pop()] if self._buffer else []
            else:
                messages = []
                for _ in range(min(count, len(self._buffer))):
                    messages.append(self._buffer.pop())
                return messages

    def peek(self, count: int = 1) -> List[MarketDataMessage]:
        """Peek at messages without removing."""
        with self._lock:
            if count == 1:
                return [self._buffer[0]] if self._buffer else []
            else:
                return list(self._buffer)[:count]

    def size(self) -> int:
        """Get current buffer size."""
        with self._lock:
            return len(self._buffer)

    def clear(self) -> None:
        """Clear buffer."""
        with self._lock:
            self._buffer.clear()


class DataProcessor:
    """Real data processing with transformation and enrichment."""

    def __init__(self):
        self._calculators = {
            "momentum": self._calculate_momentum,
            "volatility": self._calculate_volatility,
            "spread": self._calculate_spread,
            "mid_price": self._calculate_mid_price
        }

    def process_message(self, message: MarketDataMessage) -> MarketDataMessage:
        """Process and enrich market data message."""
        # Calculate derived metrics
        derived_metrics = {}
        for metric_name, calculator in self._calculators.items():
            try:
                derived_metrics[metric_name] = calculator(message)
            except Exception as e:
                logger.warning(f"Failed to calculate {metric_name}: {e}")

        # Enrich metadata
        enriched_metadata = message.metadata.copy()
        enriched_metadata.update(derived_metrics)
        enriched_metadata["processed_time"] = time.time()
        enriched_metadata["processing_latency_ms"] = (time.time() - message.timestamp) * 1000

        return MarketDataMessage(
            symbol=message.symbol,
            timestamp=message.timestamp,
            price=message.price,
            volume=message.volume,
            bid=message.bid,
            ask=message.ask,
            bid_size=message.bid_size,
            ask_size=message.ask_size,
            source=message.source,
            quality=message.quality,
            metadata=enriched_metadata
        )

    def _calculate_momentum(self, message: MarketDataMessage) -> float:
        """Calculate price momentum."""
        # This would use historical data in production
        # For now, return placeholder
        return 0.0

    def _calculate_volatility(self, message: MarketDataMessage) -> float:
        """Calculate volatility."""
        spread = message.ask - message.bid
        return spread / message.price if message.price > 0 else 0.0

    def _calculate_spread(self, message: MarketDataMessage) -> float:
        """Calculate bid-ask spread."""
        return message.ask - message.bid

    def _calculate_mid_price(self, message: MarketDataMessage) -> float:
        """Calculate mid price."""
        return (message.bid + message.ask) / 2.0


class ProductionDataPipeline:
    """Production-grade data pipeline for real-time market data."""

    def __init__(self):
        self._validator = DataValidator()
        self._processor = DataProcessor()
        self._buffer = DataBuffer(max_size=10000)
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._statistics = {
            "total_messages": 0,
            "valid_messages": 0,
            "invalid_messages": 0,
            "messages_by_source": defaultdict(int),
            "messages_by_quality": defaultdict(int),
            "processing_times": deque(maxlen=1000)
        }
        self._lock = threading.Lock()
        self._running = False

    async def start(self) -> None:
        """Start the data pipeline."""
        self._running = True
        logger.info("Production data pipeline started")

    async def stop(self) -> None:
        """Stop the data pipeline."""
        self._running = False
        logger.info("Production data pipeline stopped")

    async def process_message(self, raw_message: Dict[str, Any]) -> Optional[MarketDataMessage]:
        """Process a raw message through the pipeline."""
        start_time = time.time()

        try:
            # Parse raw message
            message = self._parse_raw_message(raw_message)
            if not message:
                return None

            # Validate message
            is_valid, quality, issues = self._validator.validate_market_data(message)

            # Update statistics
            with self._lock:
                self._statistics["total_messages"] += 1
                if is_valid:
                    self._statistics["valid_messages"] += 1
                    message.quality = quality
                    self._statistics["messages_by_quality"][quality] += 1
                else:
                    self._statistics["invalid_messages"] += 1
                    message.quality = DataQuality.INVALID
                    self._statistics["messages_by_quality"][DataQuality.INVALID] += 1
                    logger.warning(f"Invalid message: {issues}")
                    return None

                self._statistics["messages_by_source"][message.source] += 1

            # Process message (enrich with calculations)
            processed_message = self._processor.process_message(message)

            # Add to buffer
            self._buffer.put(processed_message)

            # Notify subscribers
            await self._notify_subscribers(processed_message)

            # Track processing time
            processing_time = time.time() - start_time
            self._statistics["processing_times"].append(processing_time)

            return processed_message

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return None

    def _parse_raw_message(self, raw_message: Dict[str, Any]) -> Optional[MarketDataMessage]:
        """Parse raw message into standardized format."""
        try:
            # Determine source
            source_str = raw_message.get("source", "REST_API")
            try:
                source = DataSource(source_str)
            except ValueError:
                source = DataSource.REST_API

            return MarketDataMessage(
                symbol=raw_message.get("symbol", ""),
                timestamp=raw_message.get("timestamp", time.time()),
                price=float(raw_message.get("price", 0.0)),
                volume=float(raw_message.get("volume", 0.0)),
                bid=float(raw_message.get("bid", 0.0)),
                ask=float(raw_message.get("ask", 0.0)),
                bid_size=float(raw_message.get("bid_size", 0.0)),
                ask_size=float(raw_message.get("ask_size", 0.0)),
                source=source,
                quality=DataQuality.MEDIUM,  # Will be set during validation
                metadata=raw_message.get("metadata", {})
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to parse raw message: {e}")
            return None

    async def _notify_subscribers(self, message: MarketDataMessage) -> None:
        """Notify all subscribers of new message."""
        # In production, this would use asyncio properly
        for callback in self._subscribers[message.symbol]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")

    def subscribe(self, symbol: str, callback: Callable) -> None:
        """Subscribe to updates for a specific symbol."""
        with self._lock:
            self._subscribers[symbol].append(callback)
        logger.info(f"Subscribed to {symbol}")

    def unsubscribe(self, symbol: str, callback: Callable) -> None:
        """Unsubscribe from updates for a specific symbol."""
        with self._lock:
            if callback in self._subscribers[symbol]:
                self._subscribers[symbol].remove(callback)
        logger.info(f"Unsubscribed from {symbol}")

    def get_buffered_messages(self, symbol: Optional[str] = None, count: int = 100) -> List[MarketDataMessage]:
        """Get buffered messages."""
        messages = self._buffer.peek(count)

        if symbol:
            messages = [msg for msg in messages if msg.symbol == symbol]

        return messages

    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        with self._lock:
            processing_times = list(self._statistics["processing_times"])
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0

            return {
                "total_messages": self._statistics["total_messages"],
                "valid_messages": self._statistics["valid_messages"],
                "invalid_messages": self._statistics["invalid_messages"],
                "validation_rate": (
                    self._statistics["valid_messages"] / self._statistics["total_messages"]
                    if self._statistics["total_messages"] > 0 else 0.0
                ),
                "messages_by_source": dict(self._statistics["messages_by_source"]),
                "messages_by_quality": {k.value: v for k, v in self._statistics["messages_by_quality"].items()},
                "average_processing_time_ms": avg_processing_time * 1000,
                "buffer_size": self._buffer.size(),
                "running": self._running
            }


class MarketDataSimulator:
    """Simulate real market data for production pipeline testing."""

    def __init__(self, pipeline: ProductionDataPipeline):
        self._pipeline = pipeline
        self._symbols = ["BTC/USD", "ETH/USD", "AAPL", "GOOGL", "MSFT"]
        self._running = False
        self._base_prices = {
            "BTC/USD": 45000.0,
            "ETH/USD": 3000.0,
            "AAPL": 175.0,
            "GOOGL": 140.0,
            "MSFT": 330.0
        }

    async def start_simulation(self, update_interval: float = 0.1) -> None:
        """Start market data simulation."""
        self._running = True
        logger.info(f"Starting market data simulation with {update_interval}s interval")

        while self._running:
            for symbol in self._symbols:
                await self._generate_tick(symbol)
            await asyncio.sleep(update_interval)

    async def stop_simulation(self) -> None:
        """Stop market data simulation."""
        self._running = False
        logger.info("Market data simulation stopped")

    async def _generate_tick(self, symbol: str) -> None:
        """Generate a simulated market data tick."""
        base_price = self._base_prices.get(symbol, 100.0)

        # Simulate price movement
        price_change = (hash(symbol + str(time.time())) % 1000) / 1000.0 - 0.5
        price = base_price * (1 + price_change * 0.001)

        # Calculate bid/ask spread
        spread = price * 0.0005  # 0.05% spread
        bid = price - spread / 2
        ask = price + spread / 2

        # Simulate volume
        volume = (hash(symbol + str(time.time())) % 10000) + 100

        raw_message = {
            "symbol": symbol,
            "timestamp": time.time(),
            "price": price,
            "volume": volume,
            "bid": bid,
            "ask": ask,
            "bid_size": volume * 10,
            "ask_size": volume * 10,
            "source": "WEBSOCKET",
            "metadata": {"simulated": True}
        }

        await self._pipeline.process_message(raw_message)


# Singleton instance
_production_pipeline: Optional[ProductionDataPipeline] = None
_pipeline_lock = threading.Lock()


def get_production_pipeline() -> ProductionDataPipeline:
    """Get the singleton production data pipeline instance."""
    global _production_pipeline
    if _production_pipeline is None:
        with _pipeline_lock:
            if _production_pipeline is None:
                _production_pipeline = ProductionDataPipeline()
    return _production_pipeline


__all__ = [
    "MarketDataMessage",
    "DataValidator",
    "DataBuffer",
    "DataProcessor",
    "ProductionDataPipeline",
    "MarketDataSimulator",
    "get_production_pipeline",
    "DataQuality",
    "DataSource",
]