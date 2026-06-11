"""Data Quality Monitoring - Tracks quality of data from each source.

Monitors:
- Data freshness
- Data completeness
- Data consistency
- Outlier detection
- Latency tracking
- Error rates
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

LOG = logging.getLogger(__name__)


class QualityScore(StrEnum):
    """Quality score for data."""
    
    EXCELLENT = "excellent"  # 0.9-1.0
    GOOD = "good"  # 0.7-0.9
    FAIR = "fair"  # 0.5-0.7
    POOR = "poor"  # 0.3-0.5
    VERY_POOR = "very_poor"  # 0.0-0.3


@dataclass(frozen=True, slots=True)
class DataQualityMetrics:
    """Quality metrics for a data point."""
    
    source_id: str
    freshness_score: float  # 0.0 to 1.0, higher is fresher
    completeness_score: float  # 0.0 to 1.0, higher is more complete
    consistency_score: float  # 0.0 to 1.0, higher is more consistent
    outlier_score: float  # 0.0 to 1.0, lower is better (fewer outliers)
    latency_score: float  # 0.0 to 1.0, higher is lower latency
    error_rate_score: float  # 0.0 to 1.0, higher is fewer errors
    overall_score: float  # 0.0 to 1.0
    quality_level: QualityScore
    timestamp_ns: int


class DataQualityMonitor:
    """Monitors data quality from all sources."""
    
    def __init__(self, history_size: int = 100):
        self._lock = threading.RLock()
        self._history: dict[str, deque[dict[str, Any]]] = {}
        self._history_size = history_size
        self._outlier_threshold: float = 2.0  # Standard deviations
    
    def record_data_point(self, source_id: str, data: dict[str, Any], latency_ms: float) -> None:
        """Record a data point and calculate quality metrics."""
        with self._lock:
            if source_id not in self._history:
                self._history[source_id] = deque(maxlen=self._history_size)
            
            record = {
                "data": data,
                "latency_ms": latency_ms,
                "timestamp_ns": int(datetime.now(UTC).timestamp() * 1_000_000_000),
            }
            self._history[source_id].append(record)
    
    def calculate_quality_metrics(self, source_id: str) -> DataQualityMetrics:
        """Calculate quality metrics for a source."""
        with self._lock:
            if source_id not in self._history or len(self._history[source_id]) == 0:
                return self._empty_metrics(source_id)
            
            history = list(self._history[source_id])
            
            # Calculate individual scores
            freshness_score = self._calculate_freshness(history)
            completeness_score = self._calculate_completeness(history)
            consistency_score = self._calculate_consistency(history)
            outlier_score = self._calculate_outlier_score(history)
            latency_score = self._calculate_latency_score(history)
            error_rate_score = 1.0  # Assuming no errors for successful calls
            
            # Calculate overall score (weighted average)
            overall_score = (
                freshness_score * 0.2 +
                completeness_score * 0.2 +
                consistency_score * 0.2 +
                outlier_score * 0.2 +
                latency_score * 0.1 +
                error_rate_score * 0.1
            )
            
            # Determine quality level
            quality_level = self._score_to_level(overall_score)
            
            return DataQualityMetrics(
                source_id=source_id,
                freshness_score=freshness_score,
                completeness_score=completeness_score,
                consistency_score=consistency_score,
                outlier_score=outlier_score,
                latency_score=latency_score,
                error_rate_score=error_rate_score,
                overall_score=overall_score,
                quality_level=quality_level,
                timestamp_ns=int(datetime.now(UTC).timestamp() * 1_000_000_000),
            )
    
    def _calculate_freshness(self, history: list[dict[str, Any]]) -> float:
        """Calculate data freshness score (higher = fresher)."""
        if not history:
            return 0.0
        
        latest_timestamp = history[-1]["timestamp_ns"]
        now_ns = int(datetime.now(UTC).timestamp() * 1_000_000_000)
        age_seconds = (now_ns - latest_timestamp) / 1_000_000_000
        
        # Score decays with age (0-10 minutes = 1.0, older = lower)
        max_age_seconds = 600  # 10 minutes
        return max(0.0, 1.0 - (age_seconds / max_age_seconds))
    
    def _calculate_completeness(self, history: list[dict[str, Any]]) -> float:
        """Calculate data completeness score (higher = more complete)."""
        if not history:
            return 0.0
        
        # Check for missing fields in recent data
        recent_data = history[-1]["data"]
        required_fields = ["price", "timestamp"]
        present_count = sum(1 for field in required_fields if field in recent_data)
        
        return present_count / len(required_fields)
    
    def _calculate_consistency(self, history: list[dict[str, Any]]) -> float:
        """Calculate data consistency score (higher = more consistent)."""
        if len(history) < 2:
            return 1.0  # Can't measure consistency with single point
        
        # Calculate standard deviation of prices
        try:
            prices = [
                float(h["data"].get("price", 0))
                for h in history
                if "data" in h and "price" in h["data"]
            ]
            
            if len(prices) < 2:
                return 1.0
            
            import statistics
            mean = statistics.mean(prices)
            stdev = statistics.stdev(prices)
            
            # Lower volatility = more consistent (for stable data types)
            # For crypto/forex, higher volatility is normal
            # Use coefficient of variation
            cv = (stdev / mean) if mean > 0 else 0.0
            
            # CV < 0.1 = very consistent (1.0), CV > 1.0 = very inconsistent (0.0)
            return max(0.0, 1.0 - cv)
            
        except Exception as e:
            LOG.debug(f"Error calculating consistency: {e}")
            return 0.5  # Neutral score on error
    
    def _calculate_outlier_score(self, history: list[dict[str, Any]]) -> float:
        """Calculate outlier score (higher = fewer outliers)."""
        if len(history) < 10:
            return 1.0  # Not enough data to detect outliers
        
        try:
            prices = [
                float(h["data"].get("price", 0))
                for h in history
                if "data" in h and "price" in h["data"]
            ]
            
            if len(prices) < 10:
                return 1.0
            
            import statistics
            mean = statistics.mean(prices)
            stdev = statistics.stdev(prices)
            
            if stdev == 0:
                return 1.0
            
            # Count outliers (beyond 2 standard deviations)
            outliers = sum(1 for p in prices if abs(p - mean) > self._outlier_threshold * stdev)
            outlier_ratio = outliers / len(prices)
            
            # Fewer outliers = higher score
            return max(0.0, 1.0 - outlier_ratio)
            
        except Exception as e:
            LOG.debug(f"Error calculating outlier score: {e}")
            return 0.5
    
    def _calculate_latency_score(self, history: list[dict[str, Any]]) -> float:
        """Calculate latency score (higher = lower latency)."""
        if not history:
            return 0.5  # Neutral score
        
        latencies = [h["latency_ms"] for h in history]
        
        if not latencies:
            return 0.5
        
        import statistics
        mean_latency = statistics.mean(latencies)
        
        # Latency < 100ms = excellent (1.0)
        # Latency < 500ms = good (0.8)
        # Latency < 1000ms = fair (0.6)
        # Latency < 2000ms = poor (0.4)
        # Latency > 2000ms = very poor (0.2)
        
        if mean_latency < 100:
            return 1.0
        elif mean_latency < 500:
            return 0.8
        elif mean_latency < 1000:
            return 0.6
        elif mean_latency < 2000:
            return 0.4
        else:
            return 0.2
    
    def _score_to_level(self, score: float) -> QualityScore:
        """Convert numeric score to quality level."""
        if score >= 0.9:
            return QualityScore.EXCELLENT
        elif score >= 0.7:
            return QualityScore.GOOD
        elif score >= 0.5:
            return QualityScore.FAIR
        elif score >= 0.3:
            return QualityScore.POOR
        else:
            return QualityScore.VERY_POOR
    
    def _empty_metrics(self, source_id: str) -> DataQualityMetrics:
        """Return empty metrics when no data available."""
        return DataQualityMetrics(
            source_id=source_id,
            freshness_score=0.0,
            completeness_score=0.0,
            consistency_score=0.0,
            outlier_score=0.0,
            latency_score=0.0,
            error_rate_score=0.0,
            overall_score=0.0,
            quality_level=QualityScore.VERY_POOR,
            timestamp_ns=int(datetime.now(UTC).timestamp() * 1_000_000_000),
        )
    
    def get_all_metrics(self) -> dict[str, DataQualityMetrics]:
        """Get quality metrics for all sources."""
        with self._lock:
            return {
                source_id: self.calculate_quality_metrics(source_id)
                for source_id in self._history.keys()
            }
    
    def get_low_quality_sources(self, threshold: float = 0.5) -> list[str]:
        """Get sources with quality below threshold."""
        metrics = self.get_all_metrics()
        return [
            source_id
            for source_id, metric in metrics.items()
            if metric.overall_score < threshold
        ]


# Singleton monitor instance
_quality_monitor: DataQualityMonitor | None = None
_monitor_lock = threading.Lock()


def get_quality_monitor(history_size: int = 100) -> DataQualityMonitor:
    """Get the singleton data quality monitor."""
    global _quality_monitor, _monitor_lock
    
    with _monitor_lock:
        if _quality_monitor is None:
            _quality_monitor = DataQualityMonitor(history_size=history_size)
        return _quality_monitor
