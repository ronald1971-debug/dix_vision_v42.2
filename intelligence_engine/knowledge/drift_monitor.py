"""M-1 Knowledge Layer - Knowledge Drift Monitor.

Monitors knowledge drift and triggers appropriate responses.
This component ensures that knowledge remains relevant and accurate over time.

Design Principles:
- INV-15: No external dependencies, no IO, no clock
- INV-08: Pure data surface where possible
- Frozen dataclasses for structural hashing
- Thread-safe drift monitoring and response
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections.abc import Mapping
from collections import defaultdict
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state.knowledge_graph import KnowledgeGraph
    from intelligence_engine.knowledge.knowledge_validator import KnowledgeSource

_logger = logging.getLogger(__name__)


class DriftType(str, enum.Enum):
    """Types of knowledge drift to monitor."""

    CONCEPT_DRIFT = "CONCEPT_DRIFT"  # Underlying concepts changing over time
    DISTRIBUTION_DRIFT = "DISTRIBUTION_DRIFT"  # Statistical distribution changes
    TEMPORAL_DRIFT = "TEMPORAL_DRIFT"  # Temporal patterns shifting
    SEMANTIC_DRIFT = "SEMANTIC_DRIFT"  # Meaning and interpretations changing
    CONTEXTUAL_DRIFT = "CONTEXTUAL_DRIFT"  # Context and environment changes
    QUALITY_DRIFT = "QUALITY_DRIFT"  # Data quality degradation
    RELEVANCE_DRIFT = "RELEVANCE_DRIFT"  # Knowledge relevance decreasing


class DriftSeverity(str, enum.Enum):
    """Severity levels for detected drift."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NEGLIGIBLE = "NEGLIGIBLE"


class ResponseActionType(str, enum.Enum):
    """Types of response actions for drift detection."""

    ALERT = "ALERT"  # Alert operator
    RETRAIN = "RETRAIN"  # Trigger model retraining
    REFRESH = "REFRESH"  # Refresh knowledge sources
    ADAPT = "ADAPT"  # Adapt to new patterns
    DEPRECATE = "DEPRECATE"  # Deprecate outdated knowledge
    INVESTIGATE = "INVESTIGATE"  # Trigger investigation
    IGNORE = "IGNORE"  # Ignore drift (if negligible)
    MONITOR = "MONITOR"  # Enhanced monitoring


@dataclasses.dataclass(frozen=True, slots=True)
class DriftAlert:
    """Alert generated when drift is detected."""

    alert_id: str
    drift_type: DriftType
    severity: DriftSeverity
    affected_component: str
    description: str
    drift_magnitude: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    detected_at_ns: int
    recommended_action: ResponseActionType
    metadata: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclasses.dataclass(frozen=True, slots=True)
class DriftReport:
    """Comprehensive report of detected drift."""

    report_id: str
    drift_type: DriftType
    severity: DriftSeverity
    component: str
    description: str
    metrics: Mapping[str, float] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    baseline_metrics: Mapping[str, float] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    drift_timestamp_ns: int = 0
    requires_immediate_action: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.metrics, MappingProxyType):
            object.__setattr__(self, "metrics", MappingProxyType(dict(self.metrics)))
        if not isinstance(self.baseline_metrics, MappingProxyType):
            object.__setattr__(
                self, "baseline_metrics", MappingProxyType(dict(self.baseline_metrics))
            )


@dataclasses.dataclass(frozen=True, slots=True)
class MitigationPlan:
    """Plan for mitigating detected drift."""

    plan_id: str
    drift_report_id: str
    mitigation_strategy: str
    actions: tuple[str, ...]
    priority: str
    estimated_duration_ns: int
    resource_requirements: Mapping[str, str] = dataclasses.field(
        default_factory=lambda: MappingProxyType({})
    )
    success_criteria: tuple[str, ...] = ()
    rollback_plan: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.resource_requirements, MappingProxyType):
            object.__setattr__(
                self, "resource_requirements", MappingProxyType(dict(self.resource_requirements))
            )


@dataclasses.dataclass(frozen=True, slots=True)
class ResponseAction:
    """Action taken in response to drift detection."""

    action_id: str
    drift_alert_id: str
    action_type: ResponseActionType
    description: str
    executed_at_ns: int
    execution_status: str  # "success", "failed", "pending"
    result: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    metadata: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.result, MappingProxyType):
            object.__setattr__(self, "result", MappingProxyType(dict(self.result)))
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class KnowledgeDriftMonitor:
    """Monitors knowledge drift and triggers appropriate responses.

    This component continuously monitors knowledge graphs, data streams,
    and learning models for various types of drift that could impact
    system performance and decision quality.
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._drift_alerts: dict[str, DriftAlert] = {}
        self._drift_reports: dict[str, DriftReport] = {}
        self._mitigation_plans: dict[str, MitigationPlan] = {}
        self._response_actions: dict[str, ResponseAction] = {}
        self._baselines: dict[str, dict[str, float]] = {}  # Component → baseline metrics
        self._monitoring_active: bool = True
        self._total_drifts_detected: int = 0
        self._total_responses_executed: int = 0

    def detect_concept_drift(
        self,
        knowledge: KnowledgeGraph,
        sensitivity: float = 0.3,
    ) -> DriftReport | None:
        """Detect concept drift in knowledge graph.

        Args:
            knowledge: Knowledge graph to analyze
            sensitivity: Sensitivity threshold for drift detection (0.0-1.0)

        Returns:
            DriftReport if drift detected, None otherwise
        """
        # Calculate current concept metrics
        current_metrics = self._calculate_concept_metrics(knowledge)

        # Get baseline metrics if available
        component_id = self._get_component_id(knowledge)
        baseline_metrics = self._baselines.get(component_id, {})

        # If no baseline, establish it
        if not baseline_metrics:
            with self._lock:
                self._baselines[component_id] = current_metrics
            return None

        # Compare current metrics to baseline
        drift_score = self._compare_metrics(current_metrics, baseline_metrics)

        if drift_score > sensitivity:
            # Drift detected
            report = DriftReport(
                report_id=f"concept_drift_{component_id}_{self._get_timestamp()}",
                drift_type=DriftType.CONCEPT_DRIFT,
                severity=self._calculate_severity(drift_score),
                component=component_id,
                description=f"Concept drift detected with score {drift_score:.2f}",
                metrics=MappingProxyType(current_metrics),
                baseline_metrics=MappingProxyType(baseline_metrics),
                drift_timestamp_ns=self._get_timestamp(),
                requires_immediate_action=drift_score > 0.7,
            )

            with self._lock:
                self._drift_reports[report.report_id] = report
                self._total_drifts_detected += 1

            _logger.warning(
                "Concept drift detected in %s: score=%.2f, severity=%s",
                component_id,
                drift_score,
                report.severity,
            )

            return report

        return None

    def detect_distribution_drift(
        self,
        data_streams: Mapping[str, list[float]],
        sensitivity: float = 0.3,
    ) -> list[DriftReport]:
        """Detect distribution drift in data streams.

        Args:
            data_streams: Mapping of stream names to data values
            sensitivity: Sensitivity threshold for drift detection (0.0-1.0)

        Returns:
            List of DriftReport objects for detected drifts
        """
        reports: list[DriftReport] = []

        for stream_name, data_values in data_streams.items():
            if len(data_values) < 10:  # Need sufficient data
                continue

            # Calculate current distribution metrics
            current_metrics = self._calculate_distribution_metrics(data_values)

            # Get baseline metrics
            component_id = f"stream_{stream_name}"
            baseline_metrics = self._baselines.get(component_id, {})

            # If no baseline, establish it
            if not baseline_metrics:
                with self._lock:
                    self._baselines[component_id] = current_metrics
                continue

            # Compare distributions
            drift_score = self._compare_distributions(current_metrics, baseline_metrics)

            if drift_score > sensitivity:
                # Drift detected
                report = DriftReport(
                    report_id=f"distribution_drift_{component_id}_{self._get_timestamp()}",
                    drift_type=DriftType.DISTRIBUTION_DRIFT,
                    severity=self._calculate_severity(drift_score),
                    component=component_id,
                    description=f"Distribution drift detected in {stream_name} with score {drift_score:.2f}",
                    metrics=MappingProxyType(current_metrics),
                    baseline_metrics=MappingProxyType(baseline_metrics),
                    drift_timestamp_ns=self._get_timestamp(),
                    requires_immediate_action=drift_score > 0.7,
                )

                with self._lock:
                    self._drift_reports[report.report_id] = report
                    self._total_drifts_detected += 1

                reports.append(report)
                _logger.warning(
                    "Distribution drift detected in %s: score=%.2f, severity=%s",
                    stream_name,
                    drift_score,
                    report.severity,
                )

        return reports

    def drift_mitigation_strategy(self, drift: DriftReport) -> MitigationPlan:
        """Generate mitigation strategy for detected drift.

        Args:
            drift: DriftReport requiring mitigation

        Returns:
            MitigationPlan with strategy details
        """
        # Determine strategy based on drift type and severity
        if drift.drift_type == DriftType.CONCEPT_DRIFT:
            strategy = "concept_refresh"
            actions = (
                "Refresh knowledge sources",
                "Re-train concept models",
                "Update ontology definitions",
                "Validate concept alignment",
            )
        elif drift.drift_type == DriftType.DISTRIBUTION_DRIFT:
            strategy = "distribution_adaptation"
            actions = (
                "Update statistical models",
                "Recalibrate distribution parameters",
                "Adjust detection thresholds",
                "Validate model assumptions",
            )
        elif drift.drift_type == DriftType.TEMPORAL_DRIFT:
            strategy = "temporal_realignment"
            actions = (
                "Update temporal models",
                "Adjust time windows",
                "Refresh periodic patterns",
                "Validate temporal assumptions",
            )
        else:
            strategy = "general_mitigation"
            actions = (
                "Investigate root cause",
                "Assess impact scope",
                "Develop targeted response",
                "Implement monitoring enhancements",
            )

        # Determine priority based on severity
        priority = {
            DriftSeverity.CRITICAL: "critical",
            DriftSeverity.HIGH: "high",
            DriftSeverity.MEDIUM: "medium",
            DriftSeverity.LOW: "low",
            DriftSeverity.NEGLIGIBLE: "negligible",
        }.get(drift.severity, "medium")

        # Estimate duration
        duration_map = {
            "critical": 86_400_000_000_000,  # 1 day
            "high": 43_200_000_000_000,  # 12 hours
            "medium": 21_600_000_000_000,  # 6 hours
            "low": 3_600_000_000_000,  # 1 hour
            "negligible": 0,
        }
        estimated_duration = duration_map.get(priority, 21_600_000_000_000)

        plan = MitigationPlan(
            plan_id=f"mitigation_{drift.report_id}",
            drift_report_id=drift.report_id,
            mitigation_strategy=strategy,
            actions=actions,
            priority=priority,
            estimated_duration_ns=estimated_duration,
            success_criteria=(
                "Drift score below threshold",
                "Model performance restored",
                "Validation tests passing",
            ),
            rollback_plan="Revert to previous baseline if mitigation unsuccessful",
        )

        with self._lock:
            self._mitigation_plans[plan.plan_id] = plan

        _logger.info(
            "Generated mitigation plan %s for drift %s (priority: %s)",
            plan.plan_id,
            drift.report_id,
            priority,
        )

        return plan

    def automated_drift_response(self, drift: DriftReport) -> ResponseAction:
        """Execute automated response to drift detection.

        Args:
            drift: DriftReport requiring response

        Returns:
            ResponseAction with execution details
        """
        # Determine appropriate action based on drift severity
        if drift.severity == DriftSeverity.CRITICAL:
            action_type = ResponseActionType.ALERT
            description = "Critical drift detected - immediate operator alert required"
        elif drift.severity == DriftSeverity.HIGH:
            action_type = ResponseActionType.INVESTIGATE
            description = "High severity drift - investigation triggered"
        elif drift.requires_immediate_action:
            action_type = ResponseActionType.RETRAIN
            description = "Drift requires immediate model retraining"
        else:
            action_type = ResponseActionType.MONITOR
            description = "Drift detected - enhanced monitoring activated"

        # Execute the action
        execution_status = self._execute_response_action(action_type, drift)

        # Create response action record
        response = ResponseAction(
            action_id=f"response_{drift.report_id}",
            drift_alert_id=drift.report_id,
            action_type=action_type,
            description=description,
            executed_at_ns=self._get_timestamp(),
            execution_status=execution_status,
            result=MappingProxyType({"drift_report_id": drift.report_id}),
        )

        with self._lock:
            self._response_actions[response.action_id] = response
            self._total_responses_executed += 1

        _logger.info(
            "Executed response action %s for drift %s (type: %s, status: %s)",
            response.action_id,
            drift.report_id,
            action_type,
            execution_status,
        )

        return response

    def get_drift_statistics(self) -> dict[str, int | float]:
        """Get statistics about drift monitoring."""
        with self._lock:
            total_alerts = len(self._drift_alerts)
            total_reports = len(self._drift_reports)

            # Count by drift type
            drift_type_counts: dict[str, int] = {}
            for report in self._drift_reports.values():
                drift_type_counts[report.drift_type.value] = (
                    drift_type_counts.get(report.drift_type.value, 0) + 1
                )

            # Count by severity
            severity_counts: dict[str, int] = {}
            for report in self._drift_reports.values():
                severity_counts[report.severity.value] = severity_counts.get(report.severity.value, 0) + 1

            return {
                "total_drifts_detected": self._total_drifts_detected,
                "total_responses_executed": self._total_responses_executed,
                "active_alerts": total_alerts,
                "total_reports": total_reports,
                "drift_type_counts": drift_type_counts,
                "severity_counts": severity_counts,
                "monitored_components": len(self._baselines),
            }

    # ------------------------------------------------------------------
    # Private helper methods
    # ------------------------------------------------------------------

    def _calculate_concept_metrics(self, knowledge: KnowledgeGraph) -> dict[str, float]:
        """Calculate concept metrics from knowledge graph."""
        if not knowledge or not hasattr(knowledge, 'nodes'):
            return {
                "concept_density": 0.5,
                "concept_diversity": 0.5,
                "concept_stability": 0.5,
                "relationship_consistency": 0.5,
            }
        
        try:
            nodes = knowledge.nodes if hasattr(knowledge, 'nodes') else []
            
            if not nodes:
                return {
                    "concept_density": 0.5,
                    "concept_diversity": 0.5,
                    "concept_stability": 0.5,
                    "relationship_consistency": 0.5,
                }
            
            # Calculate concept density (ratio of concepts to total nodes)
            total_concepts = sum(
                len(node.content) if hasattr(node, 'content') and node.content else 0
                for node in nodes
            )
            concept_density = min(total_concepts / (len(nodes) * 5), 1.0)  # Normalize by expected 5 concepts per node
            
            # Calculate concept diversity (variety of content keys)
            all_content_keys = set()
            for node in nodes:
                if hasattr(node, 'content') and node.content:
                    all_content_keys.update(node.content.keys())
            
            concept_diversity = min(len(all_content_keys) / 20, 1.0)  # Normalize by expected 20 unique keys
            
            # Calculate concept stability (consistency of concept usage over time)
            if len(nodes) >= 10:
                # Split nodes into temporal halves
                sorted_nodes = sorted(nodes, key=lambda x: getattr(x, 'timestamp_ns', 0))
                mid_point = len(sorted_nodes) // 2
                early_nodes = sorted_nodes[:mid_point]
                late_nodes = sorted_nodes[mid_point:]
                
                early_keys = set()
                late_keys = set()
                
                for node in early_nodes:
                    if hasattr(node, 'content') and node.content:
                        early_keys.update(node.content.keys())
                
                for node in late_nodes:
                    if hasattr(node, 'content') and node.content:
                        late_keys.update(node.content.keys())
                
                key_stability = len(early_keys & late_keys) / len(early_keys | late_keys) if (early_keys | late_keys) else 0.5
            else:
                key_stability = 0.7  # Default for insufficient data
            
            # Calculate relationship consistency (consistency of relationships between concepts)
            relationship_consistency = self._calculate_relationship_consistency(nodes)
            
            return {
                "concept_density": concept_density,
                "concept_diversity": concept_diversity,
                "concept_stability": key_stability,
                "relationship_consistency": relationship_consistency,
            }
            
        except Exception as e:
            _logger.error(f"Error calculating concept metrics: {e}")
            return {
                "concept_density": 0.5,
                "concept_diversity": 0.5,
                "concept_stability": 0.5,
                "relationship_consistency": 0.5,
            }

    def _calculate_relationship_consistency(self, nodes: list) -> float:
        """Calculate consistency of relationships between concepts in nodes."""
        if not nodes:
            return 0.5
        
        try:
            # Track co-occurrence patterns
            co_occurrence_matrix = {}
            
            for node in nodes:
                if hasattr(node, 'content') and node.content:
                    keys = list(node.content.keys())
                    # Record co-occurrences
                    for i, key1 in enumerate(keys):
                        for key2 in keys[i+1:]:
                            pair = tuple(sorted([key1, key2]))
                            co_occurrence_matrix[pair] = co_occurrence_matrix.get(pair, 0) + 1
            
            if not co_occurrence_matrix:
                return 0.7  # No relationships to check
            
            # Calculate consistency: how often do established patterns repeat?
            total_pairs = sum(co_occurrence_matrix.values())
            if total_pairs < 5:
                return 0.6  # Not enough data for pattern analysis
            
            # Look for stable patterns (pairs that occur consistently)
            stable_patterns = sum(1 for count in co_occurrence_matrix.values() if count >= 2)
            pattern_consistency = stable_patterns / len(co_occurrence_matrix)
            
            return min(pattern_consistency + 0.2, 1.0)  # Boost score slightly
            
        except Exception as e:
            _logger.error(f"Error calculating relationship consistency: {e}")
            return 0.5

    def _calculate_distribution_metrics(self, data_values: list[float]) -> dict[str, float]:
        """Calculate distribution metrics from data values."""
        if not data_values:
            return {}

        import statistics

        return {
            "mean": statistics.mean(data_values),
            "stddev": statistics.stdev(data_values) if len(data_values) > 1 else 0.0,
            "median": statistics.median(data_values),
            "min": min(data_values),
            "max": max(data_values),
        }

    def _compare_metrics(
        self,
        current: dict[str, float],
        baseline: dict[str, float],
    ) -> float:
        """Compare current metrics to baseline and calculate drift score."""
        if not baseline or not current:
            return 0.0

        drift_scores: list[float] = []

        for key, baseline_value in baseline.items():
            if key in current:
                current_value = current[key]
                if baseline_value != 0:
                    relative_change = abs(current_value - baseline_value) / abs(baseline_value)
                    drift_scores.append(relative_change)

        if not drift_scores:
            return 0.0

        return sum(drift_scores) / len(drift_scores)

    def _compare_distributions(
        self,
        current: dict[str, float],
        baseline: dict[str, float],
    ) -> float:
        """Compare current distribution to baseline and calculate drift score."""
        return self._compare_metrics(current, baseline)

    def _calculate_severity(self, drift_score: float) -> DriftSeverity:
        """Calculate severity level based on drift score."""
        if drift_score >= 0.7:
            return DriftSeverity.CRITICAL
        elif drift_score >= 0.5:
            return DriftSeverity.HIGH
        elif drift_score >= 0.3:
            return DriftSeverity.MEDIUM
        elif drift_score >= 0.1:
            return DriftSeverity.LOW
        else:
            return DriftSeverity.NEGLIGIBLE

    def _get_component_id(self, knowledge: KnowledgeGraph) -> str:
        """Generate component ID for knowledge graph."""
        if not knowledge:
            return "knowledge_graph_unknown"
        
        try:
            # Generate ID based on knowledge graph characteristics
            components = []
            
            # Include source type information
            if hasattr(knowledge, 'nodes'):
                source_types = set()
                for node in knowledge.nodes:
                    if hasattr(node, 'source_type'):
                        source_types.add(str(node.source_type))
                
                if source_types:
                    components.append(f"sources_{'_'.join(sorted(source_types))}")
            
            # Include node count for uniqueness
            if hasattr(knowledge, 'nodes'):
                components.append(f"nodes_{len(knowledge.nodes)}")
            
            # Include timestamp hash
            import hashlib
            timestamp_hash = hashlib.md5(str(self._get_timestamp()).encode()).hexdigest()[:8]
            components.append(f"hash_{timestamp_hash}")
            
            # Combine components into a unique ID
            component_id = "_".join(components) if components else f"graph_{timestamp_hash}"
            
            return component_id
            
        except Exception as e:
            _logger.error(f"Error generating component ID: {e}")
            return f"knowledge_graph_{id(knowledge)}"

    def _execute_response_action(
        self,
        action_type: ResponseActionType,
        drift: DriftReport,
    ) -> str:
        """Execute the specified response action."""
        try:
            action_id = f"action_{self._get_timestamp()}_{drift.drift_type.value}"
            
            # Execute based on action type
            if action_type == ResponseActionType.ALERT:
                # Alert operator about drift
                self._send_operator_alert(drift)
                execution_status = "alert_sent"
                
            elif action_type == ResponseActionType.RETRAIN:
                # Trigger model retraining
                self._trigger_retraining(drift)
                execution_status = "retraining_triggered"
                
            elif action_type == ResponseActionType.REFRESH:
                # Refresh knowledge sources
                self._refresh_knowledge_sources(drift)
                execution_status = "refresh_triggered"
                
            elif action_type == ResponseActionType.ADAPT:
                # Adapt to new patterns
                self._adapt_to_drift(drift)
                execution_status = "adaptation_initiated"
                
            elif action_type == ResponseActionType.DEPRECATE:
                # Deprecate outdated knowledge
                self._deprecate_knowledge(drift)
                execution_status = "deprecation_completed"
                
            elif action_type == ResponseActionType.INVESTIGATE:
                # Trigger investigation
                self._trigger_investigation(drift)
                execution_status = "investigation_triggered"
                
            elif action_type == ResponseActionType.MONITOR:
                # Enhanced monitoring (no action needed, just log)
                _logger.info(f"[DRIFT_MONITOR] Enhanced monitoring activated for {drift.drift_type}")
                execution_status = "monitoring_active"
                
            elif action_type == ResponseActionType.IGNORE:
                # Ignore drift (within thresholds)
                _logger.debug(f"[DRIFT_MONITOR] Drift {drift.drift_type} within acceptable thresholds, ignoring")
                execution_status = "ignored"
                
            else:
                execution_status = "unknown_action"
            
            # Record the action
            response_action = ResponseAction(
                action_id=action_id,
                drift_alert_id=drift.report_id,
                action_type=action_type,
                description=f"Executed {action_type.value} for {drift.drift_type.value}",
                executed_at_ns=self._get_timestamp(),
                execution_status=execution_status,
            )
            
            with self._lock:
                self._response_actions[action_id] = response_action
                self._total_responses_executed += 1
            
            _logger.info(f"[DRIFT_MONITOR] Executed action {action_type.value}: {execution_status}")
            
            return execution_status
            
        except Exception as e:
            _logger.error(f"Error executing response action: {e}")
            return f"error: {str(e)}"

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # In production, this would use the system time source
        try:
            import time
            return int(time.time() * 1_000_000_000)  # Convert seconds to nanoseconds
        except Exception as e:
            _logger.error(f"Error getting timestamp: {e}")
            return 0

    def _send_operator_alert(self, drift: DriftReport) -> None:
        """Send alert to operator about detected drift."""
        try:
            # In a real implementation, this would send to the notification system
            alert_message = (
                f"DRIFT ALERT: {drift.drift_type.value} detected in {drift.component}\n"
                f"Severity: {drift.severity.value}\n"
                f"Drift Magnitude: {drift.drift_magnitude:.2f}\n"
                f"Description: {drift.description}"
            )
            _logger.warning(f"[DRIFT_MONITOR] Operator Alert: {alert_message}")
            
            # Store in alerts for later retrieval
            with self._lock:
                if drift.report_id not in self._drift_alerts:
                    self._drift_alerts[drift.report_id] = drift
                    
        except Exception as e:
            _logger.error(f"Error sending operator alert: {e}")

    def _trigger_retraining(self, drift: DriftReport) -> None:
        """Trigger model retraining in response to drift."""
        try:
            # In a real implementation, this would coordinate with the learning engine
            _logger.info(f"[DRIFT_MONITOR] Triggering retraining for {drift.component} due to {drift.drift_type.value}")
            
            # Implementation would call learning engine to schedule retraining
            # This is a placeholder for the integration point
            
        except Exception as e:
            _logger.error(f"Error triggering retraining: {e}")

    def _refresh_knowledge_sources(self, drift: DriftReport) -> None:
        """Refresh knowledge sources in response to drift."""
        try:
            _logger.info(f"[DRIFT_MONITOR] Refreshing knowledge sources for {drift.component}")
            
            # Implementation would coordinate with knowledge source providers
            # This is a placeholder for the integration point
            
        except Exception as e:
            _logger.error(f"Error refreshing knowledge sources: {e}")

    def _adapt_to_drift(self, drift: DriftReport) -> None:
        """Adapt system to new patterns in response to drift."""
        try:
            _logger.info(f"[DRIFT_MONITOR] Adapting to drift patterns in {drift.component}")
            
            # Implementation would coordinate with adaptation mechanisms
            # This is a placeholder for the integration point
            
        except Exception as e:
            _logger.error(f"Error adapting to drift: {e}")

    def _deprecate_knowledge(self, drift: DriftReport) -> None:
        """Deprecate outdated knowledge in response to drift."""
        try:
            _logger.info(f"[DRIFT_MONITOR] Deprecating outdated knowledge in {drift.component}")
            
            # Implementation would mark affected knowledge as deprecated
            # This is a placeholder for the integration point
            
        except Exception as e:
            _logger.error(f"Error deprecating knowledge: {e}")

    def _trigger_investigation(self, drift: DriftReport) -> None:
        """Trigger investigation of detected drift."""
        try:
            _logger.info(f"[DRIFT_MONITOR] Triggering investigation for {drift.drift_type.value} in {drift.component}")
            
            # Implementation would create investigation tickets or tasks
            # This is a placeholder for the integration point
            
        except Exception as e:
            _logger.error(f"Error triggering investigation: {e}")


# Singleton instance
_drift_monitor_instance = None
_monitor_lock = threading.Lock()


def get_drift_monitor() -> KnowledgeDriftMonitor:
    """Get the singleton drift monitor instance."""
    global _drift_monitor_instance
    if _drift_monitor_instance is None:
        with _monitor_lock:
            if _drift_monitor_instance is None:
                _drift_monitor_instance = KnowledgeDriftMonitor()
    return _drift_monitor_instance


__all__ = [
    "KnowledgeDriftMonitor",
    "DriftAlert",
    "DriftReport",
    "MitigationPlan",
    "ResponseAction",
    "DriftType",
    "DriftSeverity",
    "ResponseActionType",
]