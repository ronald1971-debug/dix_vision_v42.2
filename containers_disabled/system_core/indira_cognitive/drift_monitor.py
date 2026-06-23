"""
INDIRA Drift Monitor - Knowledge Layer Component
Monitors and detects concept drift in market conditions and knowledge sources
Per Rule 6 of the DIX VISION Tier-0 Production Implementation Contract
"""

import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DriftType(Enum):
    """Types of drift to monitor"""

    CONCEPT_DRIFT = "concept_drift"
    DATA_DRIFT = "data_drift"
    PERFORMANCE_DRIFT = "performance_drift"
    RELATIONSHIP_DRIFT = "relationship_drift"
    SOURCE_QUALITY_DRIFT = "source_quality_drift"
    REGIME_DRIFT = "regime_drift"


class DriftSeverity(Enum):
    """Severity levels for detected drift"""

    NEGLIGIBLE = "negligible"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"


@dataclass
class DriftMeasurement:
    """Measurement of drift at a specific time"""

    drift_id: str
    drift_type: DriftType
    measurement_time: datetime
    metric_name: str
    baseline_value: float
    current_value: float
    drift_magnitude: float
    severity: DriftSeverity
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DriftAlert:
    """Alert generated when drift exceeds threshold"""

    alert_id: str
    drift_measurement: DriftMeasurement
    alert_time: datetime
    threshold_exceeded: float
    action_suggested: str
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class DriftBaseline:
    """Baseline values for drift detection"""

    metric_name: str
    baseline_value: float
    standard_deviation: float
    last_updated: datetime
    sample_size: int
    confidence_interval: Tuple[float, float]


class DriftMonitor:
    """
    System to monitor and detect drift in market conditions and knowledge sources
    Ensures INDIRA cognitive system maintains accuracy over time
    """

    def __init__(self):
        self._baselines: Dict[str, DriftBaseline] = {}
        self._measurements: List[DriftMeasurement] = []
        self._alerts: List[DriftAlert] = []
        self._drift_thresholds: Dict[str, float] = {
            "negligible": 0.10,  # 10% deviation
            "moderate": 0.25,  # 25% deviation
            "significant": 0.50,  # 50% deviation
            "severe": 0.75,  # 75% deviation
        }
        self._drift_callbacks: Dict[DriftType, List[Callable]] = defaultdict(list)
        self._correlation_tracking: Dict[Tuple[str, str], List[Tuple[datetime, float]]] = (
            defaultdict(list)
        )
        self._regime_tracking: Dict[str, List[Tuple[datetime, Dict[str, Any]]]] = defaultdict(list)

    def establish_baseline(
        self, metric_name: str, values: List[float], confidence_level: float = 0.95
    ) -> DriftBaseline:
        """Establish baseline for drift monitoring"""
        if not values:
            raise ValueError("Cannot establish baseline with empty values")

        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0.0

        # Calculate confidence interval
        margin = 1.96 * std_dev / (len(values) ** 0.5)  # 95% CI using z-score
        confidence_interval = (mean_value - margin, mean_value + margin)

        baseline = DriftBaseline(
            metric_name=metric_name,
            baseline_value=mean_value,
            standard_deviation=std_dev,
            last_updated=datetime.utcnow(),
            sample_size=len(values),
            confidence_interval=confidence_interval,
        )

        self._baselines[metric_name] = baseline
        logger.info(f"Established baseline for {metric_name}: {mean_value:.4f} (±{margin:.4f})")

        return baseline

    def measure_drift(
        self,
        metric_name: str,
        current_value: float,
        drift_type: DriftType = DriftType.DATA_DRIFT,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[DriftMeasurement]:
        """Measure drift from baseline for a specific metric"""
        if metric_name not in self._baselines:
            logger.warning(f"No baseline established for {metric_name}")
            return None

        baseline = self._baselines[metric_name]

        # Calculate drift magnitude
        baseline_value = baseline.baseline_value
        if baseline_value == 0:
            drift_magnitude = abs(current_value) if current_value != 0 else 0
        else:
            drift_magnitude = abs(current_value - baseline_value) / abs(baseline_value)

        # Determine severity
        if drift_magnitude <= self._drift_thresholds["negligible"]:
            severity = DriftSeverity.NEGLIGIBLE
        elif drift_magnitude <= self._drift_thresholds["moderate"]:
            severity = DriftSeverity.MODERATE
        elif drift_magnitude <= self._drift_thresholds["significant"]:
            severity = DriftSeverity.SIGNIFICANT
        else:
            severity = DriftSeverity.SEVERE

        # Calculate confidence based on deviation from confidence interval
        if baseline.confidence_interval[0] <= current_value <= baseline.confidence_interval[1]:
            confidence = 0.95
        else:
            confidence = max(0.0, 1.0 - drift_magnitude)

        measurement = DriftMeasurement(
            drift_id=f"{metric_name}_{drift_type.value}_{datetime.utcnow().timestamp()}:{datetime.utcnow().nanosecond()}",
            drift_type=drift_type,
            measurement_time=datetime.utcnow(),
            metric_name=metric_name,
            baseline_value=baseline_value,
            current_value=current_value,
            drift_magnitude=drift_magnitude,
            severity=severity,
            confidence=confidence,
            metadata=metadata or {},
        )

        self._measurements.append(measurement)

        # Check if drift exceeds alert threshold
        if severity in [DriftSeverity.SIGNIFICANT, DriftSeverity.SEVERE]:
            self._generate_drift_alert(measurement)
            self._trigger_drift_callbacks(drift_type, measurement)

        logger.info(f"Measured drift for {metric_name}: {drift_magnitude:.2%} ({severity.value})")

        return measurement

    def _generate_drift_alert(self, measurement: DriftMeasurement) -> DriftAlert:
        """Generate alert for significant drift"""
        threshold_exceeded = measurement.drift_magnitude
        action_suggested = self._suggest_action(measurement)

        alert = DriftAlert(
            alert_id=f"alert_{measurement.drift_id}",
            drift_measurement=measurement,
            alert_time=datetime.utcnow(),
            threshold_exceeded=threshold_exceeded,
            action_suggested=action_suggested,
        )

        self._alerts.append(alert)
        logger.warning(f"Drift alert generated: {alert.alert_id} - {action_suggested}")

        return alert

    def _suggest_action(self, measurement: DriftMeasurement) -> str:
        """Suggest action based on drift type and severity"""
        actions = {
            DriftType.CONCEPT_DRIFT: "Rebuild knowledge models with recent data",
            DriftType.DATA_DRIFT: "Update data pipelines and validation rules",
            DriftType.PERFORMANCE_DRIFT: "Review and reoptimize strategy parameters",
            DriftType.RELATIONSHIP_DRIFT: "Reassess correlation and causal relationships",
            DriftType.SOURCE_QUALITY_DRIFT: "Reevaluate knowledge source reliability",
            DriftType.REGIME_DRIFT: "Activate regime-specific strategies",
        }

        if measurement.severity == DriftSeverity.SEVERE:
            return actions.get(measurement.drift_type, "Immediate investigation required")
        else:
            return actions.get(measurement.drift_type, "Monitor for continued drift")

    def _trigger_drift_callbacks(
        self, drift_type: DriftType, measurement: DriftMeasurement
    ) -> None:
        """Trigger registered callbacks for drift events"""
        for callback in self._drift_callbacks[drift_type]:
            try:
                callback(measurement)
            except Exception as e:
                logger.error(f"Drift callback failed: {e}")

    def register_drift_callback(
        self, drift_type: DriftType, callback: Callable[[DriftMeasurement], None]
    ) -> None:
        """Register callback for specific drift type"""
        self._drift_callbacks[drift_type].append(callback)
        logger.info(f"Registered drift callback for {drift_type.value}")

    def track_correlation_drift(self, metric_a: str, metric_b: str, correlation: float) -> None:
        """Track correlation drift between two metrics"""
        key = (metric_a, metric_b)
        self._correlation_tracking[key].append((datetime.utcnow(), correlation))

        # Keep only recent measurements
        if len(self._correlation_tracking[key]) > 100:
            self._correlation_tracking[key] = self._correlation_tracking[key][-100:]

        # Check for correlation drift if we have enough data
        if len(self._correlation_tracking[key]) >= 10:
            self._check_correlation_drift(key)

    def _check_correlation_drift(self, key: Tuple[str, str]) -> None:
        """Check if correlation between metrics has drifted"""
        measurements = self._correlation_tracking[key]
        recent_correlations = [corr for _, corr in measurements[-10:]]

        # Establish baseline from earlier measurements
        if len(measurements) > 20:
            baseline_correlations = [corr for _, corr in measurements[:-10]]
            baseline_mean = statistics.mean(baseline_correlations)
            current_mean = statistics.mean(recent_correlations)

            if baseline_mean != 0:
                drift_magnitude = abs(current_mean - baseline_mean) / abs(baseline_mean)
                if drift_magnitude > 0.30:  # 30% drift threshold
                    self.measure_drift(
                        metric_name=f"correlation_{key[0]}_{key[1]}",
                        current_value=current_mean,
                        drift_type=DriftType.RELATIONSHIP_DRIFT,
                        metadata={
                            "baseline_correlation": baseline_mean,
                            "recent_correlations": recent_correlations,
                            "metrics": key,
                        },
                    )

    def track_regime_drift(self, regime_name: str, regime_state: Dict[str, Any]) -> None:
        """Track regime-specific drift"""
        self._regime_tracking[regime_name].append((datetime.utcnow(), regime_state))

        # Check for regime drift based on key metrics
        if "volatility" in regime_state and "momentum" in regime_state:
            volatility = float(regime_state["volatility"])
            momentum = float(regime_state["momentum"])

            # Simple regime drift detection
            regime_key = f"regime_{regime_name}_volatility"
            if regime_key in self._baselines:
                self.measure_drift(
                    metric_name=regime_key,
                    current_value=volatility,
                    drift_type=DriftType.REGIME_DRIFT,
                    metadata={"regime": regime_name, "momentum": momentum},
                )

    def get_drift_history(self, metric_name: str, limit: int = 100) -> List[DriftMeasurement]:
        """Get drift measurement history for a specific metric"""
        history = [m for m in self._measurements if m.metric_name == metric_name]
        return history[-limit:]

    def get_active_alerts(self) -> List[DriftAlert]:
        """Get all unacknowledged alerts"""
        return [alert for alert in self._alerts if not alert.acknowledged]

    def acknowledge_alert(self, alert_id: str) -> None:
        """Acknowledge a drift alert"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"Acknowledged alert: {alert_id}")
                return
        logger.warning(f"Alert not found: {alert_id}")

    def resolve_alert(self, alert_id: str) -> None:
        """Resolve a drift alert"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.acknowledged = True
                logger.info(f"Resolved alert: {alert_id}")
                return
        logger.warning(f"Alert not found: {alert_id}")

    def update_drift_threshold(self, severity_name: str, threshold: float) -> None:
        """Update drift threshold for a severity level"""
        if severity_name in self._drift_thresholds:
            self._drift_thresholds[severity_name] = threshold
            logger.info(f"Updated drift threshold for {severity_name}: {threshold:.2%}")
        else:
            logger.warning(f"Invalid severity name: {severity_name}")

    def get_drift_summary(self) -> Dict[str, Any]:
        """Get summary of drift monitoring status"""
        total_measurements = len(self._measurements)
        active_alerts = len(self.get_active_alerts())

        # Calculate drift statistics by type
        drift_by_type = defaultdict(int)
        for measurement in self._measurements:
            drift_by_type[measurement.drift_type.value] += 1

        # Calculate drift statistics by severity
        drift_by_severity = defaultdict(int)
        for measurement in self._measurements:
            drift_by_severity[measurement.severity.value] += 1

        return {
            "total_baselines": len(self._baselines),
            "total_measurements": total_measurements,
            "active_alerts": active_alerts,
            "drift_by_type": dict(drift_by_type),
            "drift_by_severity": dict(drift_by_severity),
            "tracked_correlations": len(self._correlation_tracking),
            "tracked_regimes": len(self._regime_tracking),
            "drift_thresholds": self._drift_thresholds,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def cleanup_old_measurements(self, older_than_hours: int = 24) -> int:
        """Clean up old drift measurements"""
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        old_count = len(self._measurements)
        self._measurements = [m for m in self._measurements if m.measurement_time > cutoff]

        # Also clean up resolved alerts older than cutoff
        old_alert_count = len(self._alerts)
        self._alerts = [a for a in self._alerts if not a.resolved or a.alert_time > cutoff]

        removed = old_count - len(self._measurements) + (old_alert_count - len(self._alerts))
        logger.info(f"Cleaned up {removed} old drift measurements and alerts")
        return removed
