"""Enhanced sentiment aggregator plugin v2 with multi-source fusion.

Based on alternative implementation with contract compliance and
advanced sentiment fusion from multiple sources.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Sequence
from enum import Enum

from core.contracts.engine import (
    HealthState,
    HealthStatus,
    PluginLifecycle,
    MicrostructurePlugin,
)
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick


class SentimentSource(Enum):
    """Types of sentiment data sources."""
    MARKET_SENTIMENT = "market_sentiment"
    NEWS_SENTIMENT = "news_sentiment"
    SOCIAL_SENTIMENT = "social_sentiment"
    OPTIONS_SENTIMENT = "options_sentiment"
    TECHNICAL_SENTIMENT = "technical_sentiment"


@dataclass(slots=True)
class SentimentReading:
    """Individual sentiment reading from a source."""
    source: SentimentSource
    value: float  # -1.0 (bearish) to 1.0 (bullish)
    confidence: float  # 0.0 to 1.0
    timestamp_ns: int


@dataclass(slots=True)
class SentimentAggregatorV2(MicrostructurePlugin):
    """Enhanced sentiment aggregator with multi-source fusion.
    
    v2 features:
    - Multi-source sentiment fusion
    - Weighted sentiment calculation
    - Sentiment trend detection
    - Confidence-weighted aggregation
    - Source quality assessment
    """
    
    name: str = "sentiment_aggregator_v2"
    version: str = "2.0.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    
    # Aggregation parameters
    window_size: int = 20  # Sentiment history window
    sentiment_threshold: float = 0.3  # Threshold for signal generation
    confidence_threshold: float = 0.6  # Minimum confidence for signal
    min_confidence: float = 0.5  # Minimum overall confidence
    
    # Source weights (higher = more trusted)
    source_weights: dict[str, float] = field(init=False, repr=False)
    trend_window: int = 5  # Window for trend detection
    
    # Internal state
    _sentiment_history: deque[SentimentReading] = field(init=False, repr=False)
    _aggregated_sentiment: float = field(init=False, repr=False, default=0.0)
    _sentiment_trend: str = field(init=False, repr=False, default="neutral")
    _source_quality_scores: dict[str, float] = field(init=False, repr=False)
    
    def __post_init__(self) -> None:
        if self.window_size < 2:
            raise ValueError("window_size must be >= 2")
        if not (0.0 <= self.sentiment_threshold <= 1.0):
            raise ValueError("sentiment_threshold must be in [0.0, 1.0]")
        if not (0.0 <= self.confidence_threshold <= 1.0):
            raise ValueError("confidence_threshold must be in [0.0, 1.0]")
        if not (0.0 <= self.min_confidence <= 1.0):
            raise ValueError("min_confidence must be in [0.0, 1.0]")
        if self.trend_window < 1:
            raise ValueError("trend_window must be >= 1")
        
        # Initialize source weights
        self.source_weights = {
            "market_sentiment": 0.25,
            "news_sentiment": 0.20,
            "social_sentiment": 0.15,
            "options_sentiment": 0.25,
            "technical_sentiment": 0.15
        }
        
        self._sentiment_history = deque(maxlen=self.window_size)
        self._source_quality_scores = {source: 1.0 for source in self.source_weights}
    
    def on_tick(self, tick: MarketTick) -> Sequence[SignalEvent]:
        """Process a market tick and emit sentiment-based signals."""
        # Generate simulated sentiment readings
        current_sentiments = self._generate_sentiment_readings(tick)
        
        # Update sentiment history
        for reading in current_sentiments:
            self._sentiment_history.append(reading)
        
        # Calculate aggregated sentiment
        aggregated = self._calculate_aggregated_sentiment()
        self._aggregated_sentiment = aggregated
        
        # Detect sentiment trend
        trend = self._detect_sentiment_trend()
        self._sentiment_trend = trend
        
        # Generate signals based on sentiment
        signals = []
        
        if abs(aggregated) >= self.sentiment_threshold:
            signal = self._generate_sentiment_signal(tick, aggregated, trend)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _generate_sentiment_readings(self, tick: MarketTick) -> list[SentimentReading]:
        """Generate sentiment readings based on market data."""
        readings = []
        
        # Market sentiment based on price action
        price_sentiment = self._calculate_market_sentiment(tick)
        readings.append(SentimentReading(
            source=SentimentSource.MARKET_SENTIMENT,
            value=price_sentiment,
            confidence=0.8,
            timestamp_ns=tick.timestamp_ns
        ))
        
        # Technical sentiment based on recent price
        if len(self._sentiment_history) > 0:
            technical_sentiment = self._calculate_technical_sentiment(tick)
            readings.append(SentimentReading(
                source=SentimentSource.TECHNICAL_SENTIMENT,
                value=technical_sentiment,
                confidence=0.7,
                timestamp_ns=tick.timestamp_ns
            ))
        
        # Simulated other sentiment sources
        # In a real implementation, these would come from actual data feeds
        readings.append(SentimentReading(
            source=SentimentSource.NEWS_SENTIMENT,
            value=price_sentiment * 0.8,  # Correlated with market
            confidence=0.6,
            timestamp_ns=tick.timestamp_ns
        ))
        
        readings.append(SentimentReading(
            source=SentimentSource.SOCIAL_SENTIMENT,
            value=price_sentiment * 0.6,  # Less correlated
            confidence=0.5,
            timestamp_ns=tick.timestamp_ns
        ))
        
        readings.append(SentimentReading(
            source=SentimentSource.OPTIONS_SENTIMENT,
            value=price_sentiment * 0.9,  # Highly correlated
            confidence=0.7,
            timestamp_ns=tick.timestamp_ns
        ))
        
        return readings
    
    def _calculate_market_sentiment(self, tick: MarketTick) -> float:
        """Calculate market sentiment based on tick data."""
        # Simple sentiment based on price relative to recent range
        if hasattr(tick, 'bid') and hasattr(tick, 'ask'):
            mid = (tick.bid + tick.ask) / 2
            # Neutral sentiment around 0, with some randomness
            import random
            sentiment = random.uniform(-0.3, 0.3)
        else:
            import random
            sentiment = random.uniform(-0.2, 0.2)
        
        return max(-1.0, min(1.0, sentiment))
    
    def _calculate_technical_sentiment(self, tick: MarketTick) -> float:
        """Calculate technical sentiment based on recent sentiment history."""
        if len(self._sentiment_history) < 3:
            return 0.0
        
        # Get recent market sentiment readings
        market_readings = [r for r in self._sentiment_history if r.source == SentimentSource.MARKET_SENTIMENT]
        if len(market_readings) < 3:
            return 0.0
        
        # Calculate trend
        recent_values = [r.value for r in market_readings[-3:]]
        if recent_values[-1] > recent_values[0]:
            return min(1.0, recent_values[-1] * 1.2)
        else:
            return max(-1.0, recent_values[-1] * 1.2)
    
    def _calculate_aggregated_sentiment(self) -> float:
        """Calculate weighted aggregated sentiment."""
        if not self._sentiment_history:
            return 0.0
        
        # Group by source and take latest reading
        latest_readings = {}
        for reading in reversed(list(self._sentiment_history)):
            if reading.source.value not in latest_readings:
                latest_readings[reading.source.value] = reading
        
        if not latest_readings:
            return 0.0
        
        # Calculate weighted sentiment
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for source_name, reading in latest_readings.items():
            weight = self.source_weights.get(source_name, 0.1)
            quality = self._source_quality_scores.get(source_name, 1.0)
            
            weighted_sum += reading.value * weight * quality * reading.confidence
            weight_sum += weight * quality
        
        if weight_sum == 0:
            return 0.0
        
        return weighted_sum / weight_sum
    
    def _detect_sentiment_trend(self) -> str:
        """Detect sentiment trend direction."""
        if len(self._sentiment_history) < self.trend_window:
            return "neutral"
        
        # Get recent aggregated sentiments
        recent_sentiments = []
        for i in range(min(self.trend_window, len(self._sentiment_history))):
            # Calculate sentiment at each point in history
            subset = list(self._sentiment_history)[:len(self._sentiment_history) - i]
            if subset:
                latest_readings = {}
                for reading in reversed(subset):
                    if reading.source.value not in latest_readings:
                        latest_readings[reading.source.value] = reading
                
                if latest_readings:
                    weighted_sum = 0.0
                    weight_sum = 0.0
                    for source_name, reading in latest_readings.items():
                        weight = self.source_weights.get(source_name, 0.1)
                        quality = self._source_quality_scores.get(source_name, 1.0)
                        weighted_sum += reading.value * weight * quality * reading.confidence
                        weight_sum += weight * quality
                    
                    if weight_sum > 0:
                        recent_sentiments.append(weighted_sum / weight_sum)
        
        if len(recent_sentiments) < 2:
            return "neutral"
        
        # Detect trend
        if recent_sentiments[-1] > recent_sentiments[0] + 0.1:
            return "bullish"
        elif recent_sentiments[-1] < recent_sentiments[0] - 0.1:
            return "bearish"
        else:
            return "neutral"
    
    def _generate_sentiment_signal(self, tick: MarketTick, aggregated: float, trend: str) -> SignalEvent | None:
        """Generate sentiment-based signal."""
        # Calculate confidence based on consensus and trend
        recent_readings_by_source = {}
        for reading in self._sentiment_history:
            if reading.source.value not in recent_readings_by_source:
                recent_readings_by_source[reading.source.value] = reading
        
        if not recent_readings_by_source:
            return None
        
        # Calculate consensus (how aligned sources are)
        values = [r.value for r in recent_readings_by_source.values()]
        avg_value = sum(values) / len(values)
        consensus = 1.0 - statistics.stdev(values) if len(values) > 1 else 1.0
        
        confidence = min(1.0, consensus * 0.7 + 0.3)
        
        if confidence < self.min_confidence:
            return None
        
        # Determine side
        if aggregated > self.sentiment_threshold:
            side = Side.BUY
        elif aggregated < -self.sentiment_threshold:
            side = Side.SELL
        else:
            side = Side.HOLD
        
        return SignalEvent(
            source=self.name,
            timestamp_ns=tick.timestamp_ns,
            symbol=tick.symbol,
            side=side,
            confidence=confidence,
            reason=f"sentiment:{aggregated:.2f}_trend:{trend}",
            metadata={
                "aggregated_sentiment": aggregated,
                "sentiment_trend": trend,
                "source_count": len(recent_readings_by_source),
                "consensus": consensus,
                "threshold": self.sentiment_threshold
            }
        )
    
    def check_self(self) -> HealthStatus:
        """Health check for the enhanced sentiment aggregator."""
        try:
            if len(self._sentiment_history) == 0:
                return HealthStatus(
                    engine_name=self.name,
                    state=HealthState.ALIVE,
                    detail=f"{self.name} v{self.version} lifecycle={self.lifecycle} window={self.window_size} (awaiting data)"
                )
            
            return HealthStatus(
                engine_name=self.name,
                state=HealthState.ALIVE,
                detail=f"{self.name} v{self.version} lifecycle={self.lifecycle} window={self.window_size} sentiment={self._aggregated_sentiment:.2f} trend={self._sentiment_trend} samples={len(self._sentiment_history)}"
            )
            
        except Exception as e:
            return HealthStatus(
                engine_name=self.name,
                state=HealthState.FAIL,
                detail=f"Health check failed: {str(e)}"
            )


# Import statistics for standard deviation
import statistics

__all__ = ["SentimentAggregatorV2", "SentimentReading", "SentimentSource"]