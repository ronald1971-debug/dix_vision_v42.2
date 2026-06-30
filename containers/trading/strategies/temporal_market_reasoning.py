"""
DIX VISION Temporal Market Reasoning System

Applies the existing temporal reasoning capabilities to market patterns
for time-aware market analysis and prediction.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import numpy as np

# Import existing temporal reasoning
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/cognitive_os/temporal")
from temporal_reasoning import TemporalReasoningSystem, TemporalRelation, TemporalPattern

logger = logging.getLogger(__name__)


@dataclass
class MarketTemporalPattern:
    """Temporal pattern in market data."""
    pattern_id: str
    pattern_type: str  # "seasonal", "cyclical", "trend", "anomaly"
    temporal_relation: TemporalRelation
    pattern_strength: float
    confidence: float
    time_horizon: timedelta
    predictive_power: float
    market_context: Dict[str, Any]
    timestamp: float


@dataclass
class TemporalMarketPrediction:
    """Market prediction based on temporal reasoning."""
    prediction_id: str
    prediction_type: str  # "price", "volatility", "volume", "regime"
    prediction_horizon: timedelta
    predicted_value: float
    confidence: float
    temporal_evidence: List[str]
    reasoning_chain: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TemporalAnomalyDetection:
    """Detection of temporal anomalies in market data."""
    anomaly_id: str
    anomaly_type: str
    severity: str  # "low", "medium", "high", "critical"
    detected_at: datetime
    expected_pattern: str
    actual_pattern: str
    deviation_score: float
    market_impact: str
    timestamp: datetime = field(default_factory=datetime.now)


class TemporalMarketReasoning:
    """
    Temporal market reasoning system.
    
    Applies temporal reasoning to:
    - Detect temporal patterns in market data
    - Predict future market states based on temporal patterns
    - Identify temporal anomalies
    - Understand time-based market relationships
    """
    
    def __init__(self):
        # Initialize temporal reasoning system
        self._temporal_reasoning = TemporalReasoningSystem()
        
        # Market temporal patterns
        self._market_patterns: Dict[str, MarketTemporalPattern] = {}
        
        # Temporal predictions
        self._temporal_predictions: List[TemporalMarketPrediction] = []
        
        # Temporal anomalies
        self._temporal_anomalies: List[TemporalAnomalyDetection] = []
        
        # Historical market data with timestamps
        self._market_history: deque = deque(maxlen=10000)
        
        # Temporal analysis parameters
        self._time_windows = {
            "intraday": timedelta(hours=1),
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
            "monthly": timedelta(days=30)
        }
        
        self._lock = threading.Lock()
        
        logger.info("Temporal Market Reasoning System initialized")
    
    def add_market_data_point(self, timestamp: datetime, market_data: Dict[str, Any]) -> None:
        """Add a market data point with timestamp."""
        data_point = {
            "timestamp": timestamp,
            "data": market_data
        }
        
        with self._lock:
            self._market_history.append(data_point)
    
    def detect_temporal_patterns(self, time_window: str = "daily") -> List[MarketTemporalPattern]:
        """Detect temporal patterns in market data."""
        window_delta = self._time_windows.get(time_window, timedelta(days=1))
        
        # Get recent market data within time window
        cutoff_time = datetime.now() - window_delta
        recent_data = [
            point for point in self._market_history
            if point["timestamp"] >= cutoff_time
        ]
        
        if len(recent_data) < 10:
            return []
        
        patterns = []
        
        # Detect seasonal patterns
        seasonal_patterns = self._detect_seasonal_patterns(recent_data, time_window)
        patterns.extend(seasonal_patterns)
        
        # Detect cyclical patterns
        cyclical_patterns = self._detect_cyclical_patterns(recent_data, time_window)
        patterns.extend(cyclical_patterns)
        
        # Detect trend patterns
        trend_patterns = self._detect_trend_patterns(recent_data, time_window)
        patterns.extend(trend_patterns)
        
        # Detect anomalies
        anomalies = self._detect_temporal_anomalies(recent_data, time_window)
        self._temporal_anomalies.extend(anomalies)
        
        with self._lock:
            for pattern in patterns:
                self._market_patterns[pattern.pattern_id] = pattern
        
        return patterns
    
    def _detect_seasonal_patterns(self, market_data: List[Dict], time_window: str) -> List[MarketTemporalPattern]:
        """Detect seasonal patterns in market data."""
        patterns = []
        
        # Group data by time of day/day of week
        time_groups = defaultdict(list)
        
        for point in market_data:
            timestamp = point["timestamp"]
            data = point["data"]
            
            if time_window == "intraday":
                time_key = timestamp.hour
            elif time_window == "daily":
                time_key = timestamp.weekday()
            elif time_window == "weekly":
                time_key = timestamp.isocalendar()[1]  # Week number
            else:
                time_key = timestamp.day
            
            time_groups[time_key].append(data)
        
        # Analyze each time group for patterns
        for time_key, group_data in time_groups.items():
            if len(group_data) < 3:
                continue
            
            # Calculate statistics for this time group
            prices = [d.get("price", 0.0) for d in group_data]
            volumes = [d.get("volume", 0.0) for d in group_data]
            
            avg_price = np.mean(prices)
            avg_volume = np.mean(volumes)
            price_volatility = np.std(prices) if len(prices) > 1 else 0.0
            
            # Determine if this is a significant pattern
            overall_avg_price = np.mean([d.get("price", 0.0) for d in market_data])
            price_deviation = abs(avg_price - overall_avg_price) / overall_avg_price if overall_avg_price > 0 else 0.0
            
            if price_deviation > 0.1:  # 10% deviation is significant
                pattern = MarketTemporalPattern(
                    pattern_id=f"seasonal_{time_window}_{time_key}",
                    pattern_type="seasonal",
                    temporal_relation=TemporalRelation.BEFORE,
                    pattern_strength=price_deviation,
                    confidence=min(1.0, len(group_data) / 10.0),
                    time_horizon=self._time_windows[time_window],
                    predictive_power=price_deviation * 0.8,
                    market_context={
                        "time_key": time_key,
                        "avg_price": avg_price,
                        "avg_volume": avg_volume,
                        "price_volatility": price_volatility
                    },
                    timestamp=datetime.now().timestamp()
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_cyclical_patterns(self, market_data: List[Dict], time_window: str) -> List[MarketTemporalPattern]:
        """Detect cyclical patterns in market data."""
        patterns = []
        
        # Extract price series
        prices = [point["data"].get("price", 0.0) for point in market_data]
        timestamps = [point["timestamp"] for point in market_data]
        
        if len(prices) < 20:
            return patterns
        
        # Detect cycles using autocorrelation
        autocorrelations = []
        for lag in range(1, min(20, len(prices) // 2)):
            correlation = np.corrcoef(prices[:-lag], prices[lag:])[0, 1]
            autocorrelations.append((lag, correlation))
        
        # Find significant correlations
        for lag, correlation in autocorrelations:
            if abs(correlation) > 0.5:  # Significant correlation
                pattern = MarketTemporalPattern(
                    pattern_id=f"cyclical_{time_window}_lag{lag}",
                    pattern_type="cyclical",
                    temporal_relation=TemporalRelation.BEFORE,
                    pattern_strength=abs(correlation),
                    confidence=0.7,
                    time_horizon=timedelta(seconds=lag * 3600),  # Convert lag to hours
                    predictive_power=abs(correlation) * 0.9,
                    market_context={
                        "lag": lag,
                        "correlation": correlation,
                        "cycle_length": lag
                    },
                    timestamp=datetime.now().timestamp()
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_trend_patterns(self, market_data: List[Dict], time_window: str) -> List[MarketTemporalPattern]:
        """Detect trend patterns in market data."""
        patterns = []
        
        # Extract price series
        prices = [point["data"].get("price", 0.0) for point in market_data]
        
        if len(prices) < 10:
            return patterns
        
        # Calculate trend using linear regression
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # Linear regression
        slope, intercept = np.polyfit(x, y, 1)
        r_squared = np.corrcoef(x, y)[0, 1] ** 2
        
        # Determine trend strength
        trend_strength = abs(slope) / np.mean(prices) if np.mean(prices) > 0 else 0.0
        
        if trend_strength > 0.01 and r_squared > 0.5:  # Significant trend
            trend_direction = "upward" if slope > 0 else "downward"
            
            pattern = MarketTemporalPattern(
                pattern_id=f"trend_{time_window}_{trend_direction}",
                pattern_type="trend",
                temporal_relation=TemporalRelation.DURING,
                pattern_strength=trend_strength,
                confidence=r_squared,
                time_horizon=self._time_windows[time_window],
                predictive_power=r_squared * 0.85,
                market_context={
                    "trend_direction": trend_direction,
                    "slope": slope,
                    "r_squared": r_squared,
                    "intercept": intercept
                },
                timestamp=datetime.now().timestamp()
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_temporal_anomalies(self, market_data: List[Dict], time_window: str) -> List[TemporalAnomalyDetection]:
        """Detect temporal anomalies in market data."""
        anomalies = []
        
        # Extract key metrics
        prices = [point["data"].get("price", 0.0) for point in market_data]
        volumes = [point["data"].get("volume", 0.0) for point in market_data]
        
        if len(prices) < 10:
            return anomalies
        
        # Calculate expected patterns based on historical data
        price_mean = np.mean(prices)
        price_std = np.std(prices) if len(prices) > 1 else 0.0
        volume_mean = np.mean(volumes)
        volume_std = np.std(volumes) if len(volumes) > 1 else 0.0
        
        # Detect anomalies
        for i, point in enumerate(market_data):
            price = point["data"].get("price", 0.0)
            volume = point["data"].get("volume", 0.0)
            timestamp = point["timestamp"]
            
            # Price anomaly
            price_z_score = (price - price_mean) / price_std if price_std > 0 else 0
            if abs(price_z_score) > 2.5:  # More than 2.5 standard deviations
                severity = "critical" if abs(price_z_score) > 3.5 else "high"
                
                anomaly = TemporalAnomalyDetection(
                    anomaly_id=f"price_anomaly_{int(timestamp.timestamp())}",
                    anomaly_type="price_spike",
                    severity=severity,
                    detected_at=timestamp,
                    expected_pattern=f"Price around {price_mean:.2f} ± {price_std:.2f}",
                    actual_pattern=f"Price: {price:.2f} (z-score: {price_z_score:.2f})",
                    deviation_score=abs(price_z_score),
                    market_impact="high" if severity in ["high", "critical"] else "medium",
                    timestamp=datetime.now()
                )
                anomalies.append(anomaly)
            
            # Volume anomaly
            volume_z_score = (volume - volume_mean) / volume_std if volume_std > 0 else 0
            if abs(volume_z_score) > 2.5:
                severity = "critical" if abs(volume_z_score) > 3.5 else "high"
                
                anomaly = TemporalAnomalyDetection(
                    anomaly_id=f"volume_anomaly_{int(timestamp.timestamp())}",
                    anomaly_type="volume_spike",
                    severity=severity,
                    detected_at=timestamp,
                    expected_pattern=f"Volume around {volume_mean:.0f} ± {volume_std:.0f}",
                    actual_pattern=f"Volume: {volume:.0f} (z-score: {volume_z_score:.2f})",
                    deviation_score=abs(volume_z_score),
                    market_impact="high" if severity in ["high", "critical"] else "medium",
                    timestamp=datetime.now()
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def predict_market_state(self, prediction_type: str,
                           horizon_hours: int = 24) -> TemporalMarketPrediction:
        """Predict market state based on temporal patterns."""
        prediction_horizon = timedelta(hours=horizon_hours)
        
        # Get relevant temporal patterns
        relevant_patterns = [
            pattern for pattern in self._market_patterns.values()
            if pattern.pattern_type in ["seasonal", "cyclical", "trend"]
        ]
        
        if not relevant_patterns:
            # Use simple extrapolation if no patterns
            recent_data = list(self._market_history)[-10:] if self._market_history else []
            if recent_data:
                recent_prices = [point["data"].get("price", 0.0) for point in recent_data]
                predicted_value = np.mean(recent_prices)
                confidence = 0.5
                temporal_evidence = ["Limited temporal data - using simple mean"]
            else:
                predicted_value = 0.0
                confidence = 0.0
                temporal_evidence = ["No temporal data available"]
        else:
            # Combine pattern predictions
            pattern_predictions = []
            pattern_evidence = []
            
            for pattern in relevant_patterns:
                if pattern.pattern_type == "trend":
                    # Use trend slope for prediction
                    slope = pattern.market_context.get("slope", 0.0)
                    current_price = pattern.market_context.get("avg_price", 100.0)
                    predicted_change = slope * horizon_hours
                    pattern_predictions.append(current_price + predicted_change)
                    pattern_evidence.append(f"Trend pattern: {pattern.market_context.get('trend_direction', 'unknown')}")
                
                elif pattern.pattern_type == "seasonal":
                    # Use seasonal average
                    seasonal_avg = pattern.market_context.get("avg_price", 100.0)
                    pattern_predictions.append(seasonal_avg)
                    pattern_evidence.append(f"Seasonal pattern: time_key={pattern.market_context.get('time_key', 'unknown')}")
                
                elif pattern.pattern_type == "cyclical":
                    # Use cyclical pattern
                    cycle_length = pattern.market_context.get("cycle_length", 1)
                    correlation = pattern.market_context.get("correlation", 0.0)
                    recent_price = relevant_patterns[0].market_context.get("avg_price", 100.0)
                    predicted_change = correlation * 10  # Simplified prediction
                    pattern_predictions.append(recent_price + predicted_change)
                    pattern_evidence.append(f"Cyclical pattern: cycle_length={cycle_length}")
            
            if pattern_predictions:
                predicted_value = np.mean(pattern_predictions)
                confidence = np.mean([pattern.confidence for pattern in relevant_patterns])
                temporal_evidence = pattern_evidence
            else:
                predicted_value = 0.0
                confidence = 0.0
                temporal_evidence = ["No predictive patterns found"]
        
        # Build reasoning chain
        reasoning_chain = [
            f"Analyzed {len(relevant_patterns)} temporal patterns",
            f"Prediction horizon: {horizon_hours} hours",
            f"Primary pattern: {relevant_patterns[0].pattern_type if relevant_patterns else 'none'}"
        ]
        reasoning_chain.extend(temporal_evidence)
        
        prediction = TemporalMarketPrediction(
            prediction_id=f"prediction_{int(datetime.now().timestamp())}",
            prediction_type=prediction_type,
            prediction_horizon=prediction_horizon,
            predicted_value=predicted_value,
            confidence=confidence,
            temporal_evidence=temporal_evidence,
            reasoning_chain=reasoning_chain
        )
        
        with self._lock:
            self._temporal_predictions.append(prediction)
        
        return prediction
    
    def get_temporal_market_insights(self) -> Dict[str, Any]:
        """Get comprehensive temporal market insights."""
        with self._lock:
            recent_patterns = list(self._market_patterns.values())[-20:] if self._market_patterns else []
            recent_predictions = self._temporal_predictions[-10:] if self._temporal_predictions else []
            recent_anomalies = self._temporal_anomalies[-10:] if self._temporal_anomalies else []
            
            pattern_types = {}
            for pattern in recent_patterns:
                pattern_type = pattern.pattern_type
                pattern_types[pattern_type] = pattern_types.get(pattern_type, 0) + 1
            
            anomaly_severity = {}
            for anomaly in recent_anomalies:
                severity = anomaly.severity
                anomaly_severity[severity] = anomaly_severity.get(severity, 0) + 1
            
            return {
                "total_patterns_detected": len(self._market_patterns),
                "pattern_type_distribution": pattern_types,
                "total_predictions_made": len(self._temporal_predictions),
                "average_prediction_confidence": np.mean([p.confidence for p in recent_predictions]) if recent_predictions else 0.0,
                "total_anomalies_detected": len(self._temporal_anomalies),
                "anomaly_severity_distribution": anomaly_severity,
                "data_points_analyzed": len(self._market_history),
                "time_windows_available": list(self._time_windows.keys())
            }


class TemporalTradingStrategy:
    """
    Trading strategy based on temporal market reasoning.
    
    Uses temporal patterns and predictions for trading decisions.
    """
    
    def __init__(self):
        self._temporal_reasoning = TemporalMarketReasoning()
        self._strategy_decisions: List[Dict[str, Any]] = []
        
        self._lock = threading.Lock()
        
        logger.info("Temporal Trading Strategy initialized")
    
    def generate_temporal_signal(self, current_market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signal based on temporal reasoning."""
        # Add current data point
        self._temporal_reasoning.add_market_data_point(datetime.now(), current_market_data)
        
        # Detect temporal patterns
        patterns = self._temporal_reasoning.detect_temporal_patterns()
        
        # Get market prediction
        prediction = self._temporal_reasoning.predict_market_state("price", horizon_hours=24)
        
        # Generate signal based on prediction
        current_price = current_market_data.get("price", 0.0)
        predicted_price = prediction.predicted_value
        
        if predicted_price > current_price * 1.02:  # 2% increase predicted
            action = "BUY"
            confidence = prediction.confidence * 0.8
            reason = f"Temporal prediction suggests price increase: {current_price:.2f} -> {predicted_price:.2f}"
        elif predicted_price < current_price * 0.98:  # 2% decrease predicted
            action = "SELL"
            confidence = prediction.confidence * 0.8
            reason = f"Temporal prediction suggests price decrease: {current_price:.2f} -> {predicted_price:.2f}"
        else:
            action = "HOLD"
            confidence = prediction.confidence * 0.5
            reason = "Temporal prediction suggests price stability"
        
        signal = {
            "action": action,
            "confidence": confidence,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "reason": reason,
            "temporal_patterns_found": len(patterns),
            "prediction_confidence": prediction.confidence,
            "reasoning_chain": prediction.reasoning_chain
        }
        
        with self._lock:
            self._strategy_decisions.append(signal)
        
        return signal
    
    def get_temporal_strategy_status(self) -> Dict[str, Any]:
        """Get temporal strategy status."""
        return self._temporal_reasoning.get_temporal_market_insights()


# Global instances
_temporal_market_reasoning: Optional[TemporalMarketReasoning] = None
_temporal_trading_strategy: Optional[TemporalTradingStrategy] = None


def get_temporal_market_reasoning() -> TemporalMarketReasoning:
    """Get global temporal market reasoning instance."""
    global _temporal_market_reasoning
    if _temporal_market_reasoning is None:
        _temporal_market_reasoning = TemporalMarketReasoning()
    return _temporal_market_reasoning


def get_temporal_trading_strategy() -> TemporalTradingStrategy:
    """Get global temporal trading strategy instance."""
    global _temporal_trading_strategy
    if _temporal_trading_strategy is None:
        _temporal_trading_strategy = TemporalTradingStrategy()
    return _temporal_trading_strategy