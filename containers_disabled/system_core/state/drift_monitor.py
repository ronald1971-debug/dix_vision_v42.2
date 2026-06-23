"""
state.drift_monitor
DIX VISION v42.2 — Knowledge Drift Monitor

Priority 2 Implementation: Knowledge Layer Completion

Monitors knowledge drift over time to detect when knowledge becomes outdated,
inconsistent with current world state, or statistically different from expected patterns.
"""

from __future__ import annotations

import logging
import statistics
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DriftSeverity(Enum):
    """Severity levels for knowledge drift."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DriftType(Enum):
    """Types of knowledge drift."""

    TEMPORAL = "TEMPORAL"  # Knowledge becomes outdated over time
    CONCEPTUAL = "CONCEPTUAL"  # Underlying concepts change
    DISTRIBUTIONAL = "DISTRIBUTIONAL"  # Statistical distribution changes
    CONTEXTUAL = "CONTEXTUAL"  # Context shifts make knowledge less relevant
    CONSISTENCY = "CONSISTENCY"  # Knowledge becomes inconsistent with world state


@dataclass
class DriftMetric:
    """A metric tracking a specific aspect of knowledge."""

    metric_name: str
    knowledge_id: str
    current_value: float
    baseline_value: float
    drift_score: float  # 0.0 to 1.0, higher means more drift
    timestamp: str = ""


@dataclass
class DriftAlert:
    """An alert triggered when significant drift is detected."""

    drift_type: DriftType
    severity: DriftSeverity
    knowledge_id: str
    description: str
    affected_metrics: List[DriftMetric]
    suggested_actions: List[str] = field(default_factory=list)
    triggered_at: str = ""
    acknowledged: bool = False


@dataclass
class DriftBaseline:
    """Baseline values for knowledge drift monitoring."""

    knowledge_id: str
    metrics: Dict[str, float]
    established_at: str = ""
    valid_until: str = ""
    sample_size: int = 0


class DriftMonitor:
    """
    Monitor for detecting knowledge drift over time.

    Responsibilities:
    - Track knowledge metrics over time
    - Compare current values against baselines
    - Detect statistical distribution changes
    - Monitor temporal decay of knowledge
    - Track consistency with world model
    - Generate drift alerts
    - Suggest corrective actions
    """

    def __init__(self, max_history_size: int = 1000):
        self._lock = threading.Lock()

        # Metric history
        self._metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history_size))

        # Baselines for drift detection
        self._baselines: Dict[str, DriftBaseline] = {}

        # Active drift alerts
        self._active_alerts: List[DriftAlert] = []

        # Alert history
        self._alert_history: List[DriftAlert] = []

        # Drift thresholds
        self._thresholds = {
            "temporal_decay": 0.3,  # 30% degradation over time
            "distributional_change": 0.25,  # 25% distribution change
            "consistency_loss": 0.2,  # 20% consistency loss
            "contextual_relevance": 0.15,  # 15% relevance loss
        }

        # Knowledge freshness tracking
        self._knowledge_timestamps: Dict[str, datetime] = {}

        # World model consistency tracking
        self._consistency_scores: Dict[str, List[float]] = defaultdict(list)

        logger.info("[DRIFT_MONITOR] Knowledge Drift Monitor initialized")

    def record_metric(self, metric_name: str, knowledge_id: str, value: float) -> DriftMetric:
        """
        Record a metric value for knowledge drift monitoring.

        Args:
            metric_name: Name of the metric (e.g., "accuracy", "relevance", "confidence")
            knowledge_id: Identifier for the knowledge
            value: Current metric value

        Returns:
            DriftMetric with drift score calculation
        """
        with self._lock:
            timestamp = datetime.utcnow().isoformat()

            # Get baseline
            baseline_value = 0.5  # Default baseline
            if knowledge_id in self._baselines:
                baseline_value = self._baselines[knowledge_id].metrics.get(metric_name, 0.5)

            # Calculate drift score
            drift_score = abs(value - baseline_value) / max(baseline_value, 0.1)
            drift_score = min(1.0, drift_score)

            # Create metric record
            metric = DriftMetric(
                metric_name=metric_name,
                knowledge_id=knowledge_id,
                current_value=value,
                baseline_value=baseline_value,
                drift_score=drift_score,
                timestamp=timestamp,
            )

            # Store in history
            history_key = f"{knowledge_id}:{metric_name}"
            self._metric_history[history_key].append(metric)

            # Update knowledge timestamp
            self._knowledge_timestamps[knowledge_id] = datetime.utcnow()

            # Check for drift alerts
            self._check_drift_alerts(metric)

            logger.debug(
                f"[DRIFT_MONITOR] Recorded metric {metric_name} for {knowledge_id}: {value:.3f} (drift: {drift_score:.3f})"
            )

            return metric

    def establish_baseline(
        self, knowledge_id: str, metrics: Dict[str, float], valid_days: int = 30
    ) -> DriftBaseline:
        """
        Establish baseline values for knowledge drift monitoring.

        Args:
            knowledge_id: Knowledge identifier
            metrics: Dictionary of metric names and their baseline values
            valid_days: Number of days the baseline is valid

        Returns:
            DriftBaseline with established values
        """
        with self._lock:
            valid_until = (datetime.utcnow() + timedelta(days=valid_days)).isoformat()

            baseline = DriftBaseline(
                knowledge_id=knowledge_id,
                metrics=metrics,
                established_at=str(datetime.utcnow()),
                valid_until=valid_until,
                sample_size=0,
            )

            self._baselines[knowledge_id] = baseline

            logger.info(
                f"[DRIFT_MONITOR] Established baseline for {knowledge_id} with {len(metrics)} metrics, valid until {valid_until}"
            )

            return baseline

    def _check_drift_alerts(self, metric: DriftMetric) -> None:
        """Check if metric triggers any drift alerts."""
        alerts = []

        # Check temporal decay
        if metric.drift_score > self._thresholds["temporal_decay"]:
            alerts.append(
                DriftAlert(
                    drift_type=DriftType.TEMPORAL,
                    severity=self._determine_severity(metric.drift_score),
                    knowledge_id=metric.knowledge_id,
                    description=f"Temporal decay detected in {metric.metric_name}: current {metric.current_value:.3f} vs baseline {metric.baseline_value:.3f}",
                    affected_metrics=[metric],
                    suggested_actions=[
                        "Refresh knowledge source",
                        "Verify if knowledge is still relevant",
                        "Update knowledge if possible",
                    ],
                    triggered_at=str(datetime.utcnow()),
                )
            )

        # Check distributional change
        if self._check_distributional_drift(metric):
            alerts.append(
                DriftAlert(
                    drift_type=DriftType.DISTRIBUTIONAL,
                    severity=DriftSeverity.MEDIUM,
                    knowledge_id=metric.knowledge_id,
                    description=f"Distributional change detected in {metric.metric_name}",
                    affected_metrics=[metric],
                    suggested_actions=[
                        "Recollect statistical baseline",
                        "Analyze distribution shift causes",
                        "Update models if needed",
                    ],
                    triggered_at=str(datetime.utcnow()),
                )
            )

        # Add alerts
        for alert in alerts:
            self._active_alerts.append(alert)
            self._alert_history.append(alert)

            logger.warning(
                f"[DRIFT_MONITOR] Drift alert triggered: {alert.drift_type.value} for {metric.knowledge_id} - {alert.description}"
            )

    def _check_distributional_drift(self, metric: DriftMetric) -> bool:
        """Check if there's a significant distributional change."""
        history_key = f"{metric.knowledge_id}:{metric.metric_name}"
        history = self._metric_history[history_key]

        if len(history) < 10:
            return False

        # Calculate standard deviation of recent values
        recent_values = [m.current_value for m in list(history)[-10:]]
        try:
            std_dev = statistics.stdev(recent_values)
            if std_dev > self._thresholds["distributional_change"]:
                return True
        except statistics.StatisticsError:
            pass

        return False

    def _determine_severity(self, drift_score: float) -> DriftSeverity:
        """Determine severity based on drift score."""
        if drift_score > 0.7:
            return DriftSeverity.CRITICAL
        elif drift_score > 0.5:
            return DriftSeverity.HIGH
        elif drift_score > 0.3:
            return DriftSeverity.MEDIUM
        else:
            return DriftSeverity.LOW

    def check_consistency_with_world_model(
        self, knowledge_id: str, world_model_state: Dict[str, Any]
    ) -> Tuple[float, List[DriftAlert]]:
        """
        Check consistency of knowledge with current world model state.

        Args:
            knowledge_id: Knowledge identifier
            world_model_state: Current world model state

        Returns:
            Tuple of (consistency_score, list of drift alerts)
        """
        with self._lock:
            alerts = []
            consistency_issues = 0
            total_checks = 0

            # Check consistency with market state
            if "market_state" in world_model_state:
                market_state = world_model_state["market_state"]
                consistency_issues += self._check_market_state_consistency(
                    knowledge_id, market_state
                )
                total_checks += 1

            # Check consistency with causal structure
            if "causal_structure" in world_model_state:
                causal_structure = world_model_state["causal_structure"]
                consistency_issues += self._check_causal_consistency(knowledge_id, causal_structure)
                total_checks += 1

            # Calculate consistency score
            consistency_score = 1.0 - (consistency_issues / max(total_checks, 1))
            consistency_score = max(0.0, consistency_score)

            # Store consistency score
            self._consistency_scores[knowledge_id].append(consistency_score)

            # Check if consistency loss triggers alert
            if len(self._consistency_scores[knowledge_id]) > 5:
                avg_consistency = statistics.mean(self._consistency_scores[knowledge_id][-5:])
                recent_consistency = self._consistency_scores[knowledge_id][-1]

                if recent_consistency < avg_consistency - self._thresholds["consistency_loss"]:
                    alerts.append(
                        DriftAlert(
                            drift_type=DriftType.CONSISTENCY,
                            severity=DriftSeverity.MEDIUM,
                            knowledge_id=knowledge_id,
                            description=f"Consistency with world model decreasing: {recent_consistency:.2f} vs avg {avg_consistency:.2f}",
                            affected_metrics=[],
                            suggested_actions=[
                                "Review knowledge for conflicts with current world state",
                                "Update knowledge if inconsistencies found",
                                "Mark knowledge for review",
                            ],
                            triggered_at=str(datetime.utcnow()),
                        )
                    )

            return consistency_score, alerts

    def _check_market_state_consistency(
        self, knowledge_id: str, market_state: Dict[str, Any]
    ) -> int:
        """Check consistency with market state."""
        issues = 0

        # Example: Check if knowledge contradicts market regime
        # This would be enhanced with actual knowledge content analysis

        return issues

    def _check_causal_consistency(self, knowledge_id: str, causal_structure: Dict[str, Any]) -> int:
        """Check consistency with causal structure."""
        issues = 0

        # Example: Check if knowledge contradicts causal relationships
        # This would be enhanced with actual knowledge content analysis

        return issues

    def get_active_alerts(self, knowledge_id: Optional[str] = None) -> List[DriftAlert]:
        """Get active drift alerts, optionally filtered by knowledge."""
        with self._lock:
            if knowledge_id:
                return [
                    alert for alert in self._active_alerts if alert.knowledge_id == knowledge_id
                ]
            return self._active_alerts.copy()

    def acknowledge_alert(self, alert_index: int) -> bool:
        """Acknowledge a drift alert."""
        with self._lock:
            if 0 <= alert_index < len(self._active_alerts):
                self._active_alerts[alert_index].acknowledged = True
                logger.info(f"[DRIFT_MONITOR] Acknowledged alert at index {alert_index}")
                return True
            return False

    def get_drift_statistics(self) -> Dict[str, Any]:
        """Get statistics about knowledge drift monitoring."""
        with self._lock:
            return {
                "active_alerts": len(self._active_alerts),
                "total_alerts": len(self._alert_history),
                "knowledge_monitored": len(self._knowledge_timestamps),
                "baselines_established": len(self._baselines),
                "metrics_tracked": len(self._metric_history),
                "consistency_tracking": len(self._consistency_scores),
            }

    def get_knowledge_drift_report(self, knowledge_id: str) -> Dict[str, Any]:
        """Get comprehensive drift report for specific knowledge."""
        with self._lock:
            # Get all metrics for this knowledge
            metrics = []
            for history_key, history in self._metric_history.items():
                if history_key.startswith(f"{knowledge_id}:"):
                    if history:
                        metrics.append(history[-1])

            # Get alerts for this knowledge
            alerts = [alert for alert in self._active_alerts if alert.knowledge_id == knowledge_id]

            # Get consistency scores
            consistency_scores = self._consistency_scores.get(knowledge_id, [])
            avg_consistency = statistics.mean(consistency_scores) if consistency_scores else 0.0

            # Get baseline if exists
            baseline = self._baselines.get(knowledge_id)

            return {
                "knowledge_id": knowledge_id,
                "metrics": metrics,
                "active_alerts": alerts,
                "average_consistency": avg_consistency,
                "has_baseline": baseline is not None,
                "baseline_valid": baseline.valid_until if baseline else None,
                "last_updated": (
                    self._knowledge_timestamps.get(knowledge_id).isoformat()
                    if knowledge_id in self._knowledge_timestamps
                    else None
                ),
            }


# Singleton instance
_drift_monitor: Optional[DriftMonitor] = None
_drift_monitor_lock = threading.Lock()


def get_drift_monitor(max_history_size: int = 1000) -> DriftMonitor:
    """Get the singleton drift monitor instance."""
    global _drift_monitor
    if _drift_monitor is None:
        with _drift_monitor_lock:
            if _drift_monitor is None:
                _drift_monitor = DriftMonitor(max_history_size)
    return _drift_monitor


__all__ = [
    "DriftSeverity",
    "DriftType",
    "DriftMetric",
    "DriftAlert",
    "DriftBaseline",
    "DriftMonitor",
    "get_drift_monitor",
]
