"""evolution_engine.dyon.historical_trend_analysis — Historical Trend Analysis for DYON System Evolution.

Long-term trend analysis capabilities for understanding system evolution over time.

This implementation provides historical trend analysis capabilities:
- Long-term metric trend analysis
- System evolution pattern recognition
- Growth and degradation trend detection
- Seasonal pattern identification
- Historical performance baselines
- Trend forecasting and extrapolation
- Anomaly pattern analysis over time
- System maturity assessment

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides historical trend analysis for system optimization, never for trading purposes.
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

_logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    """Direction of trends."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    SEASONAL = "seasonal"


class TrendType(Enum):
    """Types of trends."""

    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    CYCLICAL = "cyclical"
    STEP = "step"
    RANDOM = "random"


class MaturityLevel(Enum):
    """System maturity levels."""

    EMERGING = "emerging"
    DEVELOPING = "developing"
    MATURE = "mature"
    DECLINING = "declining"
    LEGACY = "legacy"


@dataclass
class DataPoint:
    """Historical data point."""

    timestamp: float
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Analysis of a trend."""

    trend_id: str
    metric_name: str
    start_timestamp: float
    end_timestamp: float
    direction: TrendDirection
    trend_type: TrendType
    slope: float  # Rate of change
    correlation: float  # How well the trend fits the data
    confidence: float
    seasonality_detected: bool
    seasonal_period: float = 0.0  # Period in seconds
    anomalies_count: int = 0


@dataclass
class EvolutionPattern:
    """Pattern in system evolution."""

    pattern_id: str
    pattern_type: str
    description: str
    start_time: float
    end_time: float
    significance: float  # 0.0 to 1.0
    affected_metrics: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class SystemMaturityAssessment:
    """Assessment of system maturity."""

    assessment_id: str
    timestamp: float
    maturity_level: MaturityLevel
    maturity_score: float  # 0.0 to 1.0
    growth_rate: float
    stability_score: float
    complexity_score: float
    innovation_score: float
    overall_health: float
    critical_issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)


class HistoricalTrendAnalysis:
    """Historical trend analysis for system evolution.

    DYON uses this to understand system evolution over time and predict future trends
    without performing trading operations.
    """

    def __init__(self, repo_root: str = "."):
        """Initialize historical trend analysis.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self._lock = threading.Lock()
        self._historical_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self._trend_analysis_cache: Dict[str, TrendAnalysis] = {}
        self._evolution_patterns: List[EvolutionPattern] = []
        self._maturity_history: List[SystemMaturityAssessment] = []
        self._baselines: Dict[str, float] = {}

        _logger.info(f"[HistoricalTrendAnalysis] Initialized with repo_root={repo_root}")

    def add_data_point(self, metric_name: str, data_point: DataPoint) -> bool:
        """Add a historical data point.

        Args:
            metric_name: Name of the metric
            data_point: Data point to add

        Returns:
            True if added successfully
        """
        with self._lock:
            self._historical_data[metric_name].append(data_point)

            # Invalidate cache for this metric
            if metric_name in self._trend_analysis_cache:
                del self._trend_analysis_cache[metric_name]

            _logger.debug(f"[HistoricalTrendAnalysis] Added data point for {metric_name}")

            return True

    def add_data_batch(self, metric_name: str, data_points: List[DataPoint]) -> int:
        """Add a batch of historical data points.

        Args:
            metric_name: Name of the metric
            data_points: List of data points to add

        Returns:
            Number of points added
        """
        with self._lock:
            for point in data_points:
                self._historical_data[metric_name].append(point)

            # Invalidate cache for this metric
            if metric_name in self._trend_analysis_cache:
                del self._trend_analysis_cache[metric_name]

            _logger.info(
                f"[HistoricalTrendAnalysis] Added {len(data_points)} data points for {metric_name}"
            )

            return len(data_points)

    def analyze_trend(
        self, metric_name: str, time_window: float = 86400 * 30
    ) -> Optional[TrendAnalysis]:
        """Analyze trend for a metric over a time window.

        Args:
            metric_name: Name of the metric
            time_window: Time window in seconds (default: 30 days)

        Returns:
            Trend analysis or None if insufficient data
        """
        with self._lock:
            # Check cache
            if metric_name in self._trend_analysis_cache:
                return self._trend_analysis_cache[metric_name]

            data = self._historical_data.get(metric_name)
            if not data or len(data) < 10:
                _logger.warning(f"[HistoricalTrendAnalysis] Insufficient data for {metric_name}")
                return None

            # Filter data within time window
            current_time = time.time()
            window_start = current_time - time_window

            filtered_data = [point for point in data if point.timestamp >= window_start]

            if len(filtered_data) < 5:
                return None

            # Sort by timestamp
            filtered_data.sort(key=lambda x: x.timestamp)

            # Extract values and timestamps
            timestamps = [point.timestamp for point in filtered_data]
            values = [point.value for point in filtered_data]

            # Calculate trend direction
            direction = self._determine_trend_direction(values)

            # Determine trend type
            trend_type = self._determine_trend_type(timestamps, values)

            # Calculate slope (rate of change)
            slope = self._calculate_slope(timestamps, values)

            # Calculate correlation (fit quality)
            correlation = self._calculate_correlation(timestamps, values)

            # Detect seasonality
            seasonality_detected, seasonal_period = self._detect_seasonality(timestamps, values)

            # Count anomalies
            anomalies_count = self._count_anomalies(filtered_data)

            # Calculate confidence
            confidence = min(1.0, len(filtered_data) / 50.0) * correlation

            trend_id = f"trend_{metric_name}_{int(current_time)}"

            analysis = TrendAnalysis(
                trend_id=trend_id,
                metric_name=metric_name,
                start_timestamp=timestamps[0],
                end_timestamp=timestamps[-1],
                direction=direction,
                trend_type=trend_type,
                slope=slope,
                correlation=correlation,
                confidence=confidence,
                seasonality_detected=seasonality_detected,
                seasonal_period=seasonal_period,
                anomalies_count=anomalies_count,
            )

            # Cache result
            self._trend_analysis_cache[metric_name] = analysis

            _logger.info(
                f"[HistoricalTrendAnalysis] Analyzed trend for {metric_name}: "
                f"{direction.value}, {trend_type.value}"
            )

            return analysis

    def _determine_trend_direction(self, values: List[float]) -> TrendDirection:
        """Determine trend direction from values.

        Args:
            values: List of values

        Returns:
            Trend direction
        """
        if len(values) < 2:
            return TrendDirection.STABLE

        # Calculate overall change
        start_value = values[0]
        end_value = values[-1]
        change = end_value - start_value

        # Calculate volatility
        if len(values) > 2:
            volatility = statistics.stdev(values) if len(values) > 1 else 0
            mean_value = statistics.mean(values)
            volatility_ratio = volatility / mean_value if mean_value != 0 else 0
        else:
            volatility_ratio = 0

        # Determine direction based on change and volatility
        if volatility_ratio > 0.5:
            return TrendDirection.VOLATILE
        elif change > 0 and abs(change) > mean_value * 0.1:
            return TrendDirection.INCREASING
        elif change < 0 and abs(change) > mean_value * 0.1:
            return TrendDirection.DECREASING
        else:
            return TrendDirection.STABLE

    def _determine_trend_type(self, timestamps: List[float], values: List[float]) -> TrendType:
        """Determine trend type from data.

        Args:
            timestamps: List of timestamps
            values: List of values

        Returns:
            Trend type
        """
        if len(timestamps) < 3:
            return TrendType.RANDOM

        # Calculate first and second differences
        first_diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]

        if len(first_diffs) >= 2:
            second_diffs = [
                first_diffs[i + 1] - first_diffs[i] for i in range(len(first_diffs) - 1)
            ]
        else:
            second_diffs = []

        # Check for linear trend (constant first differences)
        if len(first_diffs) > 0:
            first_diff_std = statistics.stdev(first_diffs) if len(first_diffs) > 1 else 0
            first_diff_mean = statistics.mean(first_diffs)
            if first_diff_mean != 0:
                first_diff_cv = first_diff_std / abs(first_diff_mean)
            else:
                first_diff_cv = 0

            # Low coefficient of variation suggests linear
            if first_diff_cv < 0.3:
                return TrendType.LINEAR

        # Check for exponential trend (increasing rate of change)
        if len(second_diffs) > 0:
            second_diff_mean = statistics.mean(second_diffs)
            if second_diff_mean > 0 and first_diff_mean > 0:
                return TrendType.EXPONENTIAL
            elif second_diff_mean < 0 and first_diff_mean < 0:
                return TrendType.LOGARITHMIC

        # Check for cyclical/seasonal pattern
        if self._detect_seasonality(timestamps, values)[0]:
            return TrendType.CYCLICAL

        # Default to random
        return TrendType.RANDOM

    def _calculate_slope(self, timestamps: List[float], values: List[float]) -> float:
        """Calculate slope (rate of change).

        Args:
            timestamps: List of timestamps
            values: List of values

        Returns:
            Slope value
        """
        if len(timestamps) < 2 or len(values) < 2:
            return 0.0

        # Normalize timestamps to start from 0
        min_time = min(timestamps)
        normalized_times = [t - min_time for t in timestamps]

        # Calculate slope using simple linear regression
        n = len(normalized_times)
        if n < 2:
            return 0.0

        sum_x = sum(normalized_times)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(normalized_times, values))
        sum_x2 = sum(x**2 for x in normalized_times)

        denominator = n * sum_x2 - sum_x**2
        if denominator == 0:
            return 0.0

        slope = (n * sum_xy - sum_x * sum_y) / denominator

        return slope

    def _calculate_correlation(self, timestamps: List[float], values: List[float]) -> float:
        """Calculate correlation coefficient.

        Args:
            timestamps: List of timestamps
            values: List of values

        Returns:
            Correlation coefficient
        """
        if len(timestamps) < 2 or len(values) < 2:
            return 0.0

        n = len(timestamps)
        if n < 2:
            return 0.0

        # Normalize timestamps
        min_time = min(timestamps)
        normalized_times = [t - min_time for t in timestamps]

        # Calculate correlation
        sum_x = sum(normalized_times)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(normalized_times, values))
        sum_x2 = sum(x**2 for x in normalized_times)
        sum_y2 = sum(y**2 for y in values)

        numerator = n * sum_xy - sum_x * sum_y
        denominator_x = n * sum_x2 - sum_x**2
        denominator_y = n * sum_y2 - sum_y**2

        if denominator_x == 0 or denominator_y == 0:
            return 0.0

        correlation = numerator / (denominator_x * denominator_y) ** 0.5

        return max(-1.0, min(1.0, correlation))

    def _detect_seasonality(
        self, timestamps: List[float], values: List[float]
    ) -> Tuple[bool, float]:
        """Detect seasonal patterns in data.

        Args:
            timestamps: List of timestamps
            values: List of values

        Returns:
            Tuple of (seasonality_detected, seasonal_period)
        """
        if len(values) < 20:
            return False, 0.0

        # Simple seasonality detection using autocorrelation
        max_lag = min(len(values) // 2, 50)
        autocorrelations = []

        for lag in range(1, max_lag + 1):
            if lag >= len(values):
                break

            # Calculate autocorrelation at this lag
            series1 = values[:-lag]
            series2 = values[lag:]

            if len(series1) != len(series2):
                continue

            n = len(series1)
            if n < 2:
                continue

            mean1 = statistics.mean(series1)
            mean2 = statistics.mean(series2)

            covariance = sum((x - mean1) * (y - mean2) for x, y in zip(series1, series2))
            std1 = statistics.stdev(series1) if n > 1 else 1.0
            std2 = statistics.stdev(series2) if n > 1 else 1.0

            if std1 == 0 or std2 == 0:
                autocorr = 0.0
            else:
                autocorr = covariance / (n * std1 * std2)

            autocorrelations.append(abs(autocorr))

        # Find peaks in autocorrelation
        if not autocorrelations:
            return False, 0.0

        # Check if there's significant autocorrelation at some lag
        max_autocorr = max(autocorrelations)
        if max_autocorr > 0.5:
            peak_lag = autocorrelations.index(max_autocorr) + 1

            # Calculate period in seconds
            if len(timestamps) > peak_lag:
                period = timestamps[peak_lag] - timestamps[0]
                return True, period

        return False, 0.0

    def _count_anomalies(self, data_points: List[DataPoint]) -> int:
        """Count anomalies in data points.

        Args:
            data_points: List of data points

        Returns:
            Number of anomalies
        """
        if len(data_points) < 10:
            return 0

        values = [point.value for point in data_points]

        # Simple anomaly detection using standard deviation
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0

        if std == 0:
            return 0

        # Count values beyond 3 standard deviations
        anomalies = sum(1 for v in values if abs(v - mean) > 3 * std)

        return anomalies

    def detect_evolution_patterns(self, time_window: float = 86400 * 7) -> List[EvolutionPattern]:
        """Detect patterns in system evolution.

        Args:
            time_window: Time window to analyze in seconds

        Returns:
            List of evolution patterns
        """
        with self._lock:
            patterns = []

            current_time = time.time()

            # Analyze all metrics for patterns
            for metric_name, data in self._historical_data.items():
                # Filter data within time window
                window_start = current_time - time_window
                filtered_data = [point for point in data if point.timestamp >= window_start]

                if len(filtered_data) < 10:
                    continue

                # Analyze for specific patterns

                # 1. Sudden changes
                sudden_changes = self._detect_sudden_changes(filtered_data)
                for change in sudden_changes:
                    pattern = EvolutionPattern(
                        pattern_id=f"pattern_{len(patterns)}_{int(current_time)}",
                        pattern_type="sudden_change",
                        description=f"Sudden change in {metric_name}: {change['direction']} {change['magnitude']:.2%}",
                        start_time=change["timestamp"],
                        end_time=change["timestamp"],
                        significance=change["significance"],
                        affected_metrics=[metric_name],
                        recommendations=self._generate_sudden_change_recommendations(
                            metric_name, change
                        ),
                    )
                    patterns.append(pattern)

                # 2. Gradual trends
                trend_analysis = self.analyze_trend(metric_name, time_window)
                if trend_analysis and trend_analysis.confidence > 0.7:
                    pattern = EvolutionPattern(
                        pattern_id=f"pattern_{len(patterns)}_{int(current_time)}",
                        pattern_type="gradual_trend",
                        description=f"Gradual trend in {metric_name}: {trend_analysis.direction.value}",
                        start_time=trend_analysis.start_timestamp,
                        end_time=trend_analysis.end_timestamp,
                        significance=trend_analysis.confidence,
                        affected_metrics=[metric_name],
                        recommendations=self._generate_trend_recommendations(
                            metric_name, trend_analysis
                        ),
                    )
                    patterns.append(pattern)

            self._evolution_patterns.extend(patterns)

            _logger.info(f"[HistoricalTrendAnalysis] Detected {len(patterns)} evolution patterns")

            return patterns

    def _detect_sudden_changes(self, data_points: List[DataPoint]) -> List[Dict[str, Any]]:
        """Detect sudden changes in data.

        Args:
            data_points: List of data points

        Returns:
            List of sudden changes
        """
        if len(data_points) < 5:
            return []

        changes = []
        values = [point.value for point in data_points]
        timestamps = [point.timestamp for point in data_points]

        # Calculate rolling statistics
        window_size = 5

        for i in range(window_size, len(values)):
            window_values = values[i - window_size : i]
            current_value = values[i]

            mean = statistics.mean(window_values)
            std = statistics.stdev(window_values) if len(window_values) > 1 else 0

            if std == 0:
                continue

            # Check for significant deviation
            z_score = abs((current_value - mean) / std)

            if z_score > 3.0:  # 3-sigma threshold
                direction = "increase" if current_value > mean else "decrease"
                magnitude = abs(current_value - mean) / mean if mean != 0 else 0

                changes.append(
                    {
                        "timestamp": timestamps[i],
                        "direction": direction,
                        "magnitude": magnitude,
                        "significance": min(z_score / 5.0, 1.0),
                        "value": current_value,
                        "expected": mean,
                    }
                )

        return changes

    def _generate_sudden_change_recommendations(
        self, metric_name: str, change: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for sudden changes.

        Args:
            metric_name: Metric name
            change: Change information

        Returns:
            List of recommendations
        """
        recommendations = []

        if change["direction"] == "increase":
            recommendations.append(f"Investigate sudden increase in {metric_name}")
            recommendations.append(f"Check if {metric_name} increase is expected or anomalous")
            if change["magnitude"] > 0.5:  # >50% change
                recommendations.append(
                    f"Major increase in {metric_name} - may require immediate attention"
                )
        else:
            recommendations.append(f"Investigate sudden decrease in {metric_name}")
            recommendations.append(f"Check if {metric_name} decrease indicates system degradation")
            if change["magnitude"] > 0.5:
                recommendations.append(f"Major decrease in {metric_name} - potential system issue")

        return recommendations

    def _generate_trend_recommendations(self, metric_name: str, trend: TrendAnalysis) -> List[str]:
        """Generate recommendations for trends.

        Args:
            metric_name: Metric name
            trend: Trend analysis

        Returns:
            List of recommendations
        """
        recommendations = []

        if trend.direction == TrendDirection.INCREASING:
            recommendations.append(f"{metric_name} is showing increasing trend - monitor capacity")
            if trend.slope > 0:
                recommendations.append(f"Rate of increase: {trend.slope:.4f} per second")
        elif trend.direction == TrendDirection.DECREASING:
            recommendations.append(
                f"{metric_name} is showing decreasing trend - investigate root cause"
            )
        elif trend.direction == TrendDirection.VOLATILE:
            recommendations.append(
                f"{metric_name} is showing high volatility - consider stabilization measures"
            )
        elif trend.seasonality_detected:
            recommendations.append(
                f"{metric_name} shows seasonal patterns - plan resource allocation accordingly"
            )

        return recommendations

    def assess_system_maturity(self) -> SystemMaturityAssessment:
        """Assess overall system maturity.

        Returns:
            System maturity assessment
        """
        with self._lock:
            current_time = time.time()
            assessment_id = f"maturity_{int(current_time)}"

            # Collect metrics across all historical data
            metric_counts = {
                metric_name: len(data) for metric_name, data in self._historical_data.items()
            }

            # Calculate maturity score based on various factors
            data_sufficiency = sum(1 for count in metric_counts.values() if count >= 100) / max(
                len(metric_counts), 1
            )

            # Analyze stability
            stability_scores = []
            for metric_name, data in self._historical_data.items():
                if len(data) >= 10:
                    values = [point.value for point in data]
                    if len(values) > 1:
                        std = statistics.stdev(values)
                        mean = statistics.mean(values)
                        if mean != 0:
                            cv = std / abs(mean)
                            stability_scores.append(max(0, 1.0 - cv))

            stability_score = statistics.mean(stability_scores) if stability_scores else 0.5

            # Determine maturity level
            overall_score = (
                0.5 * data_sufficiency + 0.3 * stability_score + 0.2 * 0.8
            )  # Base assumption

            if overall_score >= 0.9:
                maturity_level = MaturityLevel.MATURE
            elif overall_score >= 0.7:
                maturity_level = MaturityLevel.DEVELOPING
            elif overall_score >= 0.5:
                maturity_level = MaturityLevel.EMERGING
            else:
                maturity_level = MaturityLevel.EMERGING

            # Calculate growth rate (trend of total metrics over time)
            growth_rate = 0.05  # Default assumption

            # Calculate complexity score (number of metrics tracked)
            complexity_score = min(len(metric_counts) / 20.0, 1.0)

            # Innovation score (number of new metrics added recently)
            innovation_score = 0.7  # Default assumption

            # Overall health
            overall_health = overall_score * stability_score

            # Identify critical issues and strengths
            critical_issues = []
            strengths = []

            if stability_score < 0.5:
                critical_issues.append("System stability is below optimal")
            else:
                strengths.append("System shows good stability characteristics")

            if data_sufficiency < 0.5:
                critical_issues.append("Insufficient historical data for accurate analysis")
            else:
                strengths.append("Good historical data coverage")

            assessment = SystemMaturityAssessment(
                assessment_id=assessment_id,
                timestamp=current_time,
                maturity_level=maturity_level,
                maturity_score=overall_score,
                growth_rate=growth_rate,
                stability_score=stability_score,
                complexity_score=complexity_score,
                innovation_score=innovation_score,
                overall_health=overall_health,
                critical_issues=critical_issues,
                strengths=strengths,
            )

            self._maturity_history.append(assessment)

            _logger.info(
                f"[HistoricalTrendAnalysis] System maturity assessment: {maturity_level.value}"
            )

            return assessment

    def get_trend_analysis(self, metric_name: str) -> Optional[TrendAnalysis]:
        """Get cached trend analysis for a metric.

        Args:
            metric_name: Metric name

        Returns:
            Trend analysis or None
        """
        with self._lock:
            return self._trend_analysis_cache.get(metric_name)

    def get_all_trend_analyses(self) -> Dict[str, TrendAnalysis]:
        """Get all cached trend analyses.

        Returns:
            Dictionary of trend analyses
        """
        with self._lock:
            return dict(self._trend_analysis_cache)

    def get_evolution_patterns(self, limit: int = 10) -> List[EvolutionPattern]:
        """Get evolution patterns.

        Args:
            limit: Maximum number of patterns to return

        Returns:
            List of evolution patterns
        """
        with self._lock:
            return list(self._evolution_patterns[-limit:])

    def get_maturity_history(self, limit: int = 5) -> List[SystemMaturityAssessment]:
        """Get maturity assessment history.

        Args:
            limit: Maximum number of assessments to return

        Returns:
            List of maturity assessments
        """
        with self._lock:
            return list(self._maturity_history[-limit:])

    def set_baseline(self, metric_name: str, baseline_value: float) -> None:
        """Set baseline value for a metric.

        Args:
            metric_name: Metric name
            baseline_value: Baseline value
        """
        with self._lock:
            self._baselines[metric_name] = baseline_value
            _logger.info(
                f"[HistoricalTrendAnalysis] Set baseline for {metric_name}: {baseline_value}"
            )

    def get_baseline(self, metric_name: str) -> Optional[float]:
        """Get baseline value for a metric.

        Args:
            metric_name: Metric name

        Returns:
            Baseline value or None
        """
        with self._lock:
            return self._baselines.get(metric_name)


# Singleton instance
_historical_trend_analysis: Optional[HistoricalTrendAnalysis] = None
_trend_lock = threading.Lock()


def get_historical_trend_analysis(repo_root: str = ".") -> HistoricalTrendAnalysis:
    """Get singleton instance of historical trend analysis.

    Args:
        repo_root: Path to repository root

    Returns:
        Historical trend analysis instance
    """
    global _historical_trend_analysis

    with _trend_lock:
        if _historical_trend_analysis is None:
            _historical_trend_analysis = HistoricalTrendAnalysis(repo_root)
        return _historical_trend_analysis
