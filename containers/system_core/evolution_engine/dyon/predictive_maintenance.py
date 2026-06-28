"""evolution_engine.dyon.predictive_maintenance — Predictive Maintenance for DYON.

Predictive maintenance and issue anticipation capabilities for proactive system optimization.

This implementation provides predictive maintenance capabilities:
- Issue anticipation based on historical patterns
- Failure prediction using historical data
- Maintenance scheduling optimization
- Proactive issue detection
- System health forecasting
- Maintenance resource planning
- Root cause prediction
- Performance degradation prediction

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides predictive maintenance for system optimization, never for trading purposes.
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

_logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Issue severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IssueCategory(Enum):
    """Categories of system issues."""

    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SECURITY = "security"
    RESOURCE = "resource"
    ARCHITECTURAL = "architectural"
    INTEGRATION = "integration"
    DATA = "data"


class PredictionConfidence(Enum):
    """Confidence levels for predictions."""

    VERY_LOW = "VERY_LOW"  # < 30%
    LOW = "LOW"  # 30-50%
    MEDIUM = "MEDIUM"  # 50-70%
    HIGH = "HIGH"  # 70-90%
    VERY_HIGH = "VERY_HIGH"  # > 90%


@dataclass
class HistoricalIssue:
    """Historical issue record for pattern learning."""

    issue_id: str
    issue_category: IssueCategory
    severity: IssueSeverity
    component: str
    timestamp: float
    resolution_time: float
    root_cause: str
    affected_metrics: Dict[str, float] = field(default_factory=dict)
    resolution_method: str = ""


@dataclass
class PredictedIssue:
    """Predicted issue based on historical patterns."""

    prediction_id: str
    issue_category: IssueCategory
    predicted_severity: IssueSeverity
    affected_components: List[str]
    prediction_timestamp: float
    predicted_occurrence_time: float
    confidence: PredictionConfidence
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    estimated_impact: str = ""


@dataclass
class MaintenanceRecommendation:
    """Maintenance recommendation based on predictions."""

    recommendation_id: str
    priority: str
    maintenance_type: str
    target_components: List[str]
    estimated_effort: str
    scheduled_time: float
    predicted_avoided_issues: List[PredictedIssue] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealthForecast:
    """Forecast of future system health."""

    forecast_timestamp: float
    forecast_horizon_hours: float
    predicted_health_status: str
    confidence: float
    risk_factors: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    predicted_metrics: Dict[str, List[float]] = field(default_factory=dict)


class PredictiveMaintenanceSystem:
    """Predictive maintenance and issue anticipation system.

    DYON uses this for proactive system issue prevention
    without performing any trading operations.
    """

    def __init__(
        self,
        history_window_size: int = 500,
        prediction_horizon_hours: int = 24,
        confidence_threshold: float = 0.5,
    ):
        """Initialize predictive maintenance system.

        Args:
            history_window_size: Number of historical issues to retain
            prediction_horizon_hours: Hours to predict into the future
            confidence_threshold: Minimum confidence for actionable predictions
        """
        self.history_window_size = history_window_size
        self.prediction_horizon_hours = prediction_horizon_hours
        self.confidence_threshold = confidence_threshold

        # Data storage
        self._historical_issues: deque[HistoricalIssue] = deque(maxlen=history_window_size)
        self._issue_patterns: Dict[str, List[HistoricalIssue]] = defaultdict(list)
        self._current_predictions: List[PredictedIssue] = []
        self._maintenance_recommendations: List[MaintenanceRecommendation] = []

        # Thread management
        self._prediction_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

        _logger.info(
            f"[PredictiveMaintenanceSystem] Initialized with history_size={history_window_size}, "
            f"horizon={prediction_horizon_hours}h, confidence_threshold={confidence_threshold}"
        )

    def start_prediction_service(self, interval_hours: float = 1.0) -> None:
        """Start prediction service in background thread.

        Args:
            interval_hours: Hours between prediction cycles
        """
        if self._running:
            _logger.warning("[PredictiveMaintenanceSystem] Already running")
            return

        self._running = True
        interval_seconds = interval_hours * 3600

        self._prediction_thread = threading.Thread(
            target=self._prediction_loop, daemon=True, name="PredictiveMaintenance"
        )
        self._prediction_thread.start()

        _logger.info(
            f"[PredictiveMaintenanceSystem] Started prediction service (interval={interval_hours}h)"
        )

    def stop_prediction_service(self) -> None:
        """Stop prediction service."""
        self._running = False
        if self._prediction_thread:
            self._prediction_thread.join(timeout=10.0)

        _logger.info("[PredictiveMaintenanceSystem] Stopped prediction service")

    def _prediction_loop(self) -> None:
        """Main prediction loop."""
        while self._running:
            try:
                self._perform_prediction_cycle()
                time.sleep(self._running)  # Will be controlled by interval
            except Exception as e:
                _logger.error(f"[PredictiveMaintenanceSystem] Error in prediction loop: {e}")

    def _perform_prediction_cycle(self) -> None:
        """Perform one prediction cycle."""
        with self._lock:
            # Update issue patterns
            self._update_issue_patterns()

            # Generate predictions
            new_predictions = self._generate_predictions()

            # Update current predictions
            self._current_predictions = new_predictions

            # Generate maintenance recommendations
            recommendations = self._generate_maintenance_recommendations(new_predictions)
            self._maintenance_recommendations = recommendations

    def record_issue(self, issue: HistoricalIssue) -> None:
        """Record a historical issue for pattern learning.

        Args:
            issue: Historical issue to record
        """
        with self._lock:
            self._historical_issues.append(issue)
            self._issue_patterns[f"{issue.component}_{issue.issue_category.value}"].append(issue)

            _logger.debug(
                f"[PredictiveMaintenanceSystem] Recorded issue: {issue.issue_id} "
                f"({issue.component}, {issue.severity.value})"
            )

    def _update_issue_patterns(self) -> None:
        """Update issue patterns based on historical data."""
        # Group issues by component and category
        pattern_data = defaultdict(list)

        for issue in self._historical_issues:
            pattern_key = f"{issue.component}_{issue.issue_category.value}"
            pattern_data[pattern_key].append(issue)

        # Analyze patterns
        for pattern_key, issues in pattern_data.items():
            if len(issues) >= 5:
                # Calculate pattern statistics
                severities = [i.severity for i in issues]
                resolution_times = [i.resolution_time for i in issues]

                self._issue_patterns[pattern_key] = issues

    def _generate_predictions(self) -> List[PredictedIssue]:
        """Generate predictions based on historical patterns.

        Returns:
            List of predicted issues
        """
        predictions = []
        current_time = time.time()

        # Analyze each pattern for prediction
        for pattern_key, historical_issues in self._issue_patterns.items():
            if len(historical_issues) < 5:
                continue

            # Calculate recurrence patterns
            recurrence_interval = self._calculate_recurrence_interval(historical_issues)

            if recurrence_interval:
                # Predict next occurrence
                last_issue = max(historical_issues, key=lambda x: x.timestamp)
                predicted_time = last_issue.timestamp + recurrence_interval

                # Only predict if within horizon
                if predicted_time <= current_time + (self.prediction_horizon_hours * 3600):
                    component, category = pattern_key.rsplit("_", 1)

                    # Calculate confidence based on pattern consistency
                    confidence = self._calculate_prediction_confidence(historical_issues)

                    if confidence >= self.confidence_threshold:
                        prediction = PredictedIssue(
                            prediction_id=f"pred_{int(current_time)}_{pattern_key}",
                            issue_category=IssueCategory(category),
                            predicted_severity=self._predict_severity(historical_issues),
                            affected_components=[component],
                            prediction_timestamp=current_time,
                            predicted_occurrence_time=predicted_time,
                            confidence=confidence,
                            risk_factors=self._identify_risk_factors(historical_issues),
                            mitigation_strategies=self._generate_mitigation_strategies(
                                historical_issues
                            ),
                            estimated_impact=self._estimate_impact(historical_issues),
                        )
                        predictions.append(prediction)

        return predictions

    def _calculate_recurrence_interval(self, issues: List[HistoricalIssue]) -> Optional[float]:
        """Calculate average recurrence interval for issues.

        Args:
            issues: List of historical issues

        Returns:
            Average interval in seconds or None
        """
        if len(issues) < 2:
            return None

        intervals = []
        for i in range(1, len(issues)):
            interval = issues[i].timestamp - issues[i - 1].timestamp
            intervals.append(interval)

        if not intervals:
            return None

        return statistics.mean(intervals)

    def _calculate_prediction_confidence(
        self, issues: List[HistoricalIssue]
    ) -> PredictionConfidence:
        """Calculate confidence level for prediction based on pattern consistency.

        Args:
            issues: Historical issues

        Returns:
            Confidence level
        """
        if len(issues) < 5:
            return PredictionConfidence.LOW

        # Calculate consistency metrics
        severities = [i.severity for i in issues]

        # Check if severity is consistent
        severity_counts = Counter([s.value for s in severities])
        dominant_severity_ratio = max(severity_counts.values()) / len(severities)

        # Calculate confidence based on consistency and sample size
        sample_score = min(len(issues) / 20.0, 1.0)  # More samples = higher confidence
        consistency_score = dominant_severity_ratio

        overall_score = (sample_score + consistency_score) / 2.0

        if overall_score >= 0.9:
            return PredictionConfidence.VERY_HIGH
        elif overall_score >= 0.7:
            return PredictionConfidence.HIGH
        elif overall_score >= 0.5:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW

    def _predict_severity(self, issues: List[HistoricalIssue]) -> IssueSeverity:
        """Predict severity based on historical pattern.

        Args:
            issues: Historical issues

        Returns:
            Predicted severity
        """
        if not issues:
            return IssueSeverity.MEDIUM

        # Use most recent severity as predictor
        recent_issues = sorted(issues, key=lambda x: x.timestamp, reverse=True)[:3]
        severities = [i.severity for i in recent_issues]

        # Return most common recent severity
        severity_counts = Counter([s.value for s in severities])
        most_common = severity_counts.most_common(1)[0][0]

        return IssueSeverity(most_common)

    def _identify_risk_factors(self, issues: List[HistoricalIssue]) -> List[str]:
        """Identify risk factors from historical issues.

        Args:
            issues: Historical issues

        Returns:
            List of risk factors
        """
        risk_factors = []

        # Analyze root causes
        root_causes = [i.root_cause for i in issues if i.root_cause]
        cause_counts = Counter(root_causes)

        for cause, count in cause_counts.most_common(3):
            if count >= 2:
                risk_factors.append(f"Recurring root cause: {cause}")

        # Analyze affected metrics
        metric_patterns = defaultdict(list)
        for issue in issues:
            for metric, value in issue.affected_metrics.items():
                metric_patterns[metric].append(value)

        for metric, values in metric_patterns.items():
            if len(values) >= 2:
                risk_factors.append(f"Recurring metric anomaly: {metric}")

        return risk_factors

    def _generate_mitigation_strategies(self, issues: List[HistoricalIssue]) -> List[str]:
        """Generate mitigation strategies based on historical resolutions.

        Args:
            issues: Historical issues

        Returns:
            List of mitigation strategies
        """
        strategies = []

        # Analyze resolution methods
        resolution_methods = [i.resolution_method for i in issues if i.resolution_method]
        method_counts = Counter(resolution_methods)

        # Recommend most effective methods
        for method, count in method_counts.most_common(3):
            if count >= 2:
                strategies.append(f"Apply successful resolution: {method}")

        # Add general strategies based on category
        if issues:
            category = issues[0].issue_category
            if category == IssueCategory.PERFORMANCE:
                strategies.append("Implement performance monitoring and alerting")
            elif category == IssueCategory.RELIABILITY:
                strategies.append("Add redundancy and failover mechanisms")
            elif category == IssueCategory.RESOURCE:
                strategies.append("Implement resource scaling and optimization")

        return strategies

    def _estimate_impact(self, issues: List[HistoricalIssue]) -> str:
        """Estimate impact of predicted issue.

        Args:
            issues: Historical issues

        Returns:
            Impact description
        """
        if not issues:
            return "Unknown impact"

        # Count high severity issues
        high_severity_count = sum(
            1 for i in issues if i.severity in [IssueSeverity.HIGH, IssueSeverity.CRITICAL]
        )

        if high_severity_count >= 3:
            return "High impact - multiple critical issues"
        elif high_severity_count >= 1:
            return "Medium impact - potential service degradation"
        else:
            return "Low impact - minimal disruption expected"

    def _generate_maintenance_recommendations(
        self, predictions: List[PredictedIssue]
    ) -> List[MaintenanceRecommendation]:
        """Generate maintenance recommendations from predictions.

        Args:
            predictions: Predicted issues

        Returns:
            List of maintenance recommendations
        """
        recommendations = []

        # Group predictions by priority
        high_priority = [
            p
            for p in predictions
            if p.predicted_severity in [IssueSeverity.HIGH, IssueSeverity.CRITICAL]
        ]
        medium_priority = [p for p in predictions if p.predicted_severity == IssueSeverity.MEDIUM]

        # Generate recommendations for high priority
        if high_priority:
            recommendation = MaintenanceRecommendation(
                recommendation_id=f"rec_{int(time.time())}_high",
                priority="HIGH",
                maintenance_type="preventive",
                target_components=list(
                    set([c for p in high_priority for c in p.affected_components])
                ),
                estimated_effort="2-4 hours",
                scheduled_time=time.time() + 3600,  # Schedule 1 hour from now
                predicted_avoided_issues=high_priority,
                resource_requirements={"developers": 1, "testing": True},
            )
            recommendations.append(recommendation)

        # Generate recommendations for medium priority
        if medium_priority:
            recommendation = MaintenanceRecommendation(
                recommendation_id=f"rec_{int(time.time())}_medium",
                priority="MEDIUM",
                maintenance_type="scheduled",
                target_components=list(
                    set([c for p in medium_priority for c in p.affected_components])
                ),
                estimated_effort="1-2 hours",
                scheduled_time=time.time() + 86400,  # Schedule 24 hours from now
                predicted_avoided_issues=medium_priority,
                resource_requirements={"developers": 1, "testing": False},
            )
            recommendations.append(recommendation)

        return recommendations

    def get_system_health_forecast(self, hours_ahead: int = 24) -> SystemHealthForecast:
        """Generate system health forecast.

        Args:
            hours_ahead: Hours to forecast ahead

        Returns:
            System health forecast
        """
        current_time = time.time()

        # Get upcoming predictions within horizon
        upcoming_predictions = [
            p
            for p in self._current_predictions
            if p.predicted_occurrence_time <= current_time + (hours_ahead * 3600)
        ]

        # Calculate forecast metrics
        critical_count = sum(
            1 for p in upcoming_predictions if p.predicted_severity == IssueSeverity.CRITICAL
        )
        high_count = sum(
            1 for p in upcoming_predictions if p.predicted_severity == IssueSeverity.HIGH
        )

        # Determine predicted health status
        if critical_count > 0:
            health_status = "CRITICAL"
        elif high_count > 2:
            health_status = "DEGRADED"
        elif high_count > 0:
            health_status = "WARNING"
        else:
            health_status = "HEALTHY"

        # Calculate confidence
        if upcoming_predictions:
            avg_confidence = statistics.mean(
                [self._confidence_to_float(p.confidence) for p in upcoming_predictions]
            )
            confidence = avg_confidence
        else:
            confidence = 0.5

        # Identify risk factors
        risk_factors = list(set([rf for p in upcoming_predictions for rf in p.risk_factors]))

        # Generate recommended actions
        recommended_actions = self._generate_forecast_actions(upcoming_predictions)

        return SystemHealthForecast(
            forecast_timestamp=current_time,
            forecast_horizon_hours=hours_ahead,
            predicted_health_status=health_status,
            confidence=confidence,
            risk_factors=risk_factors,
            recommended_actions=recommended_actions,
        )

    def _confidence_to_float(self, confidence: PredictionConfidence) -> float:
        """Convert confidence enum to float value.

        Args:
            confidence: Confidence enum

        Returns:
            Float value (0.0 to 1.0)
        """
        confidence_map = {
            PredictionConfidence.VERY_LOW: 0.2,
            PredictionConfidence.LOW: 0.4,
            PredictionConfidence.MEDIUM: 0.6,
            PredictionConfidence.HIGH: 0.8,
            PredictionConfidence.VERY_HIGH: 0.95,
        }
        return confidence_map.get(confidence, 0.5)

    def _generate_forecast_actions(self, predictions: List[PredictedIssue]) -> List[str]:
        """Generate recommended actions based on forecast.

        Args:
            predictions: Predicted issues

        Returns:
            List of recommended actions
        """
        actions = []

        if not predictions:
            return ["Continue normal monitoring, no issues predicted"]

        high_severity = [
            p
            for p in predictions
            if p.predicted_severity in [IssueSeverity.HIGH, IssueSeverity.CRITICAL]
        ]

        if high_severity:
            actions.append(
                f"Prepare emergency response plans for {len(high_severity)} high-severity issues"
            )

        actions.append("Review and update maintenance schedules based on predictions")
        actions.append("Prepare resources for predicted maintenance activities")

        return actions

    def get_maintenance_recommendations(self) -> List[MaintenanceRecommendation]:
        """Get current maintenance recommendations.

        Returns:
            List of maintenance recommendations
        """
        with self._lock:
            return list(self._maintenance_recommendations)

    def get_current_predictions(self) -> List[PredictedIssue]:
        """Get current active predictions.

        Returns:
            List of predicted issues
        """
        with self._lock:
            return list(self._current_predictions)


# Singleton instance
_predictive_maintenance: Optional[PredictiveMaintenanceSystem] = None
_maintenance_lock = threading.Lock()


def get_predictive_maintenance_system(
    history_window_size: int = 500,
    prediction_horizon_hours: int = 24,
    confidence_threshold: float = 0.5,
) -> PredictiveMaintenanceSystem:
    """Get singleton instance of predictive maintenance system.

    Args:
        history_window_size: Number of historical issues to retain
        prediction_horizon_hours: Hours to predict into the future
        confidence_threshold: Minimum confidence for actionable predictions

    Returns:
        Predictive maintenance system instance
    """
    global _predictive_maintenance

    with _maintenance_lock:
        if _predictive_maintenance is None:
            _predictive_maintenance = PredictiveMaintenanceSystem(
                history_window_size=history_window_size,
                prediction_horizon_hours=prediction_horizon_hours,
                confidence_threshold=confidence_threshold,
            )
        return _predictive_maintenance
