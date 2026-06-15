"""M-1 Knowledge Layer - Edge Case Memory.

Captures, stores, and retrieves edge cases for learning and decision improvement.
This component enables the system to learn from rare events and exceptional situations.

Design Principles:
- INV-15: No external dependencies, no IO, no clock
- INV-08: Pure data surface where possible
- Frozen dataclasses for structural hashing
- Thread-safe edge case storage and retrieval
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state.memory.contracts import MemoryRecord

_logger = logging.getLogger(__name__)


class EdgeCaseSeverity(str, enum.Enum):
    """Severity level of edge cases."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class EdgeCaseCategory(str, enum.Enum):
    """Categories of edge cases."""

    MARKET_ANOMALY = "MARKET_ANOMALY"
    SYSTEM_FAILURE = "SYSTEM_FAILURE"
    UNEXPECTED_BEHAVIOR = "UNEXPECTED_BEHAVIOR"
    RARE_EVENT = "RARE_EVENT"
    PERFORMANCE_DEGRADATION = "PERFORMANCE_DEGRADATION"
    DATA_QUALITY = "DATA_QUALITY"
    INTEGRATION_FAILURE = "INTEGRATION_FAILURE"
    SECURITY_INCIDENT = "SECURITY_INCIDENT"
    GOVERNANCE_VIOLATION = "GOVERNANCE_VIOLATION"
    LEARNING_FAILURE = "LEARNING_FAILURE"


class EdgeCaseStatus(str, enum.Enum):
    """Status of edge case handling."""

    DETECTED = "DETECTED"
    ANALYZING = "ANALYZING"
    RESOLVED = "RESOLVED"
    MITIGATED = "MITIGATED"
    IGNORED = "IGNORED"
    RECURRING = "RECURRING"


@dataclasses.dataclass(frozen=True, slots=True)
class EdgeCaseContext:
    """Context information surrounding an edge case."""

    system_state: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    market_conditions: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    operational_context: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    environmental_factors: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not isinstance(self.system_state, MappingProxyType):
            object.__setattr__(self, "system_state", MappingProxyType(dict(self.system_state)))
        if not isinstance(self.market_conditions, MappingProxyType):
            object.__setattr__(self, "market_conditions", MappingProxyType(dict(self.market_conditions)))
        if not isinstance(self.operational_context, MappingProxyType):
            object.__setattr__(self, "operational_context", MappingProxyType(dict(self.operational_context)))
        if not isinstance(self.environmental_factors, MappingProxyType):
            object.__setattr__(
                self, "environmental_factors", MappingProxyType(dict(self.environmental_factors))
            )


@dataclasses.dataclass(frozen=True, slots=True)
class EdgeCase:
    """A captured edge case for learning and improvement.

    Fields:
        case_id: Unique identifier for this edge case
        event_type: Type of event that triggered this edge case
        category: Category of edge case
        severity: Severity level of the edge case
        description: Human-readable description of the edge case
        context: Context information surrounding the edge case
        trigger_event: The original event that triggered detection
        impact_assessment: Assessment of the edge case impact
        detection_timestamp_ns: Timestamp when edge case was detected
        status: Current status of edge case handling
        resolution: Resolution details if resolved/mitigated
        metadata: Additional metadata about the edge case
        occurrence_count: Number of times this edge case has occurred
        last_occurrence_ns: Timestamp of most recent occurrence
        related_cases: IDs of related edge cases
    """

    case_id: str
    event_type: str
    category: EdgeCaseCategory
    severity: EdgeCaseSeverity
    description: str
    context: EdgeCaseContext
    trigger_event: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    impact_assessment: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    detection_timestamp_ns: int = 0
    status: EdgeCaseStatus = EdgeCaseStatus.DETECTED
    resolution: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    metadata: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    occurrence_count: int = 1
    last_occurrence_ns: int = 0
    related_cases: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.case_id:
            raise ValueError("EdgeCase.case_id must be non-empty")
        if not isinstance(self.trigger_event, MappingProxyType):
            object.__setattr__(self, "trigger_event", MappingProxyType(dict(self.trigger_event)))
        if not isinstance(self.impact_assessment, MappingProxyType):
            object.__setattr__(self, "impact_assessment", MappingProxyType(dict(self.impact_assessment)))
        if not isinstance(self.resolution, MappingProxyType):
            object.__setattr__(self, "resolution", MappingProxyType(dict(self.resolution)))
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclasses.dataclass(frozen=True, slots=True)
class PatternInsights:
    """Insights derived from analyzing edge case patterns."""

    pattern_id: str
    pattern_type: str
    frequency: float
    severity_distribution: Mapping[str, int] = dataclasses.field(
        default_factory=lambda: MappingProxyType({})
    )
    common_contexts: tuple[Mapping[str, str], ...] = ()
    temporal_patterns: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    system_patterns: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    recommendations: tuple[str, ...] = ()
    confidence: float = 0.0
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.severity_distribution, MappingProxyType):
            object.__setattr__(
                self, "severity_distribution", MappingProxyType(dict(self.severity_distribution))
            )
        if not isinstance(self.temporal_patterns, MappingProxyType):
            object.__setattr__(self, "temporal_patterns", MappingProxyType(dict(self.temporal_patterns)))
        if not isinstance(self.system_patterns, MappingProxyType):
            object.__setattr__(self, "system_patterns", MappingProxyType(dict(self.system_patterns)))


@dataclasses.dataclass(frozen=True, slots=True)
class Query:
    """Query for edge case retrieval."""

    query_id: str
    categories: frozenset[EdgeCaseCategory] = frozenset()
    severities: frozenset[EdgeCaseSeverity] = frozenset()
    statuses: frozenset[EdgeCaseStatus] = frozenset()
    event_types: frozenset[str] = frozenset()
    since_ns: int | None = None
    until_ns: int | None = None
    limit: int = 20

    def __post_init__(self) -> None:
        if not self.query_id:
            raise ValueError("Query.query_id must be non-empty")
        if self.limit <= 0:
            raise ValueError(f"Query.limit must be positive, got {self.limit}")


class EdgeCaseMemory:
    """Captures, stores, and retrieves edge cases for learning and decision improvement.

    This component enables the system to learn from rare events and exceptional
    situations that fall outside normal operating parameters. By capturing and
    analyzing edge cases, the system can improve its decision-making and
    resilience.
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._edge_cases: dict[str, EdgeCase] = {}
        self._case_index: dict[str, set[str]] = {}  # Various indices for fast lookup
        self._pattern_cache: dict[str, PatternInsights] = {}
        self._total_cases_captured: int = 0
        self._total_cases_resolved: int = 0

    def capture_edge_case(
        self,
        event: Mapping[str, str],
        context: EdgeCaseContext,
        category: EdgeCaseCategory,
        severity: EdgeCaseSeverity,
        description: str,
        event_type: str = "unknown",
    ) -> EdgeCase:
        """Capture an edge case event for storage and analysis.

        Args:
            event: The triggering event as key-value pairs
            context: Context information surrounding the edge case
            category: Category of the edge case
            severity: Severity level of the edge case
            description: Human-readable description
            event_type: Type of event that triggered detection

        Returns:
            EdgeCase object representing the captured edge case
        """
        # Generate case ID
        case_id = self._generate_case_id(event_type, category)

        # Check if this is a recurring edge case
        existing_case = self._find_similar_case(event, context, category)
        if existing_case:
            # Update existing case
            updated_case = self._update_recurring_case(existing_case, event)
            with self._lock:
                self._edge_cases[existing_case.case_id] = updated_case
            _logger.info("Updated recurring edge case: %s (occurrence count: %d)", existing_case.case_id, updated_case.occurrence_count)
            return updated_case

        # Create new edge case
        timestamp_ns = self._get_timestamp()
        impact_assessment = self._assess_impact(event, context, severity)

        edge_case = EdgeCase(
            case_id=case_id,
            event_type=event_type,
            category=category,
            severity=severity,
            description=description,
            context=context,
            trigger_event=MappingProxyType(dict(event)),
            impact_assessment=MappingProxyType(impact_assessment),
            detection_timestamp_ns=timestamp_ns,
            last_occurrence_ns=timestamp_ns,
        )

        # Store edge case
        with self._lock:
            self._edge_cases[case_id] = edge_case
            self._index_edge_case(edge_case)
            self._total_cases_captured += 1

        _logger.info("Captured edge case: %s - %s", case_id, description)

        return edge_case

    def retrieve_similar_cases(
        self,
        query: Query,
        threshold: float = 0.7,
    ) -> list[EdgeCase]:
        """Retrieve edge cases similar to the query criteria.

        Args:
            query: Query criteria for edge case retrieval
            threshold: Similarity threshold for results

        Returns:
            List of EdgeCase objects matching the query criteria
        """
        with self._lock:
            candidates = self._query_edge_cases(query)

        # Apply similarity filtering
        similar_cases = [case for case in candidates if self._calculate_similarity(case, query) >= threshold]

        # Sort by relevance and limit
        similar_cases.sort(key=lambda c: (c.occurrence_count, c.severity.value), reverse=True)
        return similar_cases[: query.limit]

    def edge_case_pattern_analysis(
        self,
        time_period_ns: int = 86_400_000_000_000,  # 24 hours
        min_occurrences: int = 3,
    ) -> list[PatternInsights]:
        """Analyze patterns in edge cases to derive insights.

        Args:
            time_period_ns: Time period to analyze in nanoseconds
            min_occurrences: Minimum occurrences to consider a pattern

        Returns:
            List of PatternInsights derived from edge case analysis
        """
        timestamp_ns = self._get_timestamp()

        with self._lock:
            # Filter cases within time period
            recent_cases = [
                case
                for case in self._edge_cases.values()
                if timestamp_ns - case.detection_timestamp_ns <= time_period_ns
            ]

        # Analyze patterns by category
        patterns: list[PatternInsights] = []

        for category in EdgeCaseCategory:
            category_cases = [case for case in recent_cases if case.category == category]

            if len(category_cases) >= min_occurrences:
                pattern = self._analyze_category_pattern(category_cases, category, timestamp_ns)
                patterns.append(pattern)

        # Analyze cross-category patterns
        cross_category_pattern = self._analyze_cross_category_patterns(recent_cases, timestamp_ns)
        if cross_category_pattern:
            patterns.append(cross_category_pattern)

        # Cache patterns
        with self._lock:
            for pattern in patterns:
                self._pattern_cache[pattern.pattern_id] = pattern

        return patterns

    def automatic_edge_case_detection(
        self,
        event_stream: list[Mapping[str, str]],
        context_stream: list[EdgeCaseContext],
    ) -> list[EdgeCase]:
        """Automatically detect edge cases from event streams.

        Args:
            event_stream: Stream of events to analyze
            context_stream: Corresponding context information

        Returns:
            List of automatically detected edge cases
        """
        detected_cases: list[EdgeCase] = []

        for event, context in zip(event_stream, context_stream):
            # Detect anomalies in the event
            anomalies = self._detect_anomalies(event, context)

            for anomaly_type, anomaly_details in anomalies:
                # Determine category and severity
                category = self._classify_anomaly(anomaly_type, anomaly_details)
                severity = self._assess_anomaly_severity(anomaly_type, anomaly_details)

                # Create edge case
                edge_case = self.capture_edge_case(
                    event=event,
                    context=context,
                    category=category,
                    severity=severity,
                    description=f"Automatically detected: {anomaly_type}",
                    event_type="automatic_detection",
                )

                detected_cases.append(edge_case)

        _logger.info("Automatically detected %d edge cases from event stream", len(detected_cases))
        return detected_cases

    def update_edge_case_status(
        self,
        case_id: str,
        new_status: EdgeCaseStatus,
        resolution: Mapping[str, str] | None = None,
    ) -> EdgeCase | None:
        """Update the status of an edge case.

        Args:
            case_id: ID of the edge case to update
            new_status: New status for the edge case
            resolution: Optional resolution details

        Returns:
            Updated EdgeCase if found, None otherwise
        """
        with self._lock:
            existing_case = self._edge_cases.get(case_id)
            if not existing_case:
                return None

            # Create updated case
            updated_case = dataclasses.replace(
                existing_case,
                status=new_status,
                resolution=MappingProxyType(dict(resolution)) if resolution else existing_case.resolution,
            )

            # Store updated case
            self._edge_cases[case_id] = updated_case

            # Update resolution counter
            if new_status in (EdgeCaseStatus.RESOLVED, EdgeCaseStatus.MITIGATED):
                self._total_cases_resolved += 1

        _logger.info("Updated edge case %s status to %s", case_id, new_status)
        return updated_case

    def get_edge_case_statistics(self) -> dict[str, int | float]:
        """Get statistics about edge cases in memory."""
        with self._lock:
            total_cases = len(self._edge_cases)

            # Count by status
            status_counts: dict[str, int] = {}
            for case in self._edge_cases.values():
                status_counts[case.status.value] = status_counts.get(case.status.value, 0) + 1

            # Count by severity
            severity_counts: dict[str, int] = {}
            for case in self._edge_cases.values():
                severity_counts[case.severity.value] = severity_counts.get(case.severity.value, 0) + 1

            # Count by category
            category_counts: dict[str, int] = {}
            for case in self._edge_cases.values():
                category_counts[case.category.value] = category_counts.get(case.category.value, 0) + 1

            # Calculate resolution rate
            resolution_rate = (
                self._total_cases_resolved / total_cases if total_cases > 0 else 0.0
            )

            return {
                "total_cases": total_cases,
                "total_captured": self._total_cases_captured,
                "total_resolved": self._total_cases_resolved,
                "resolution_rate": resolution_rate,
                "status_counts": status_counts,
                "severity_counts": severity_counts,
                "category_counts": category_counts,
            }

    # ------------------------------------------------------------------
    # Private helper methods
    # ------------------------------------------------------------------

    def _generate_case_id(self, event_type: str, category: EdgeCaseCategory) -> str:
        """Generate unique case ID."""
        timestamp = self._get_timestamp()
        return f"edge_case_{event_type}_{category.value}_{timestamp}"

    def _find_similar_case(
        self,
        event: Mapping[str, str],
        context: EdgeCaseContext,
        category: EdgeCaseCategory,
    ) -> EdgeCase | None:
        """Find similar existing edge case."""
        # TODO: Implement sophisticated similarity matching
        # For now, return None (always create new case)
        return None

    def _update_recurring_case(
        self,
        existing_case: EdgeCase,
        new_event: Mapping[str, str],
    ) -> EdgeCase:
        """Update a recurring edge case with new occurrence."""
        return dataclasses.replace(
            existing_case,
            occurrence_count=existing_case.occurrence_count + 1,
            last_occurrence_ns=self._get_timestamp(),
            status=EdgeCaseStatus.RECURRING if existing_case.occurrence_count >= 3 else existing_case.status,
        )

    def _assess_impact(
        self,
        event: Mapping[str, str],
        context: EdgeCaseContext,
        severity: EdgeCaseSeverity,
    ) -> dict[str, str]:
        """Assess the impact of an edge case."""
        # TODO: Implement sophisticated impact assessment
        return {
            "potential_impact": severity.value,
            "affected_components": "unknown",
            "business_impact": "unknown",
        }

    def _index_edge_case(self, edge_case: EdgeCase) -> None:
        """Index edge case for fast lookup."""
        # Index by category
        if edge_case.category.value not in self._case_index:
            self._case_index[edge_case.category.value] = set()
        self._case_index[edge_case.category.value].add(edge_case.case_id)

        # Index by severity
        if edge_case.severity.value not in self._case_index:
            self._case_index[edge_case.severity.value] = set()
        self._case_index[edge_case.severity.value].add(edge_case.case_id)

        # Index by status
        if edge_case.status.value not in self._case_index:
            self._case_index[edge_case.status.value] = set()
        self._case_index[edge_case.status.value].add(edge_case.case_id)

        # Index by event type
        if edge_case.event_type not in self._case_index:
            self._case_index[edge_case.event_type] = set()
        self._case_index[edge_case.event_type].add(edge_case.case_id)

    def _query_edge_cases(self, query: Query) -> list[EdgeCase]:
        """Query edge cases based on criteria."""
        candidate_sets: list[set[str]] = []

        # Filter by category
        if query.categories:
            category_set = set()
            for category in query.categories:
                category_set.update(self._case_index.get(category.value, set()))
            candidate_sets.append(category_set)

        # Filter by severity
        if query.severities:
            severity_set = set()
            for severity in query.severities:
                severity_set.update(self._case_index.get(severity.value, set()))
            candidate_sets.append(severity_set)

        # Filter by status
        if query.statuses:
            status_set = set()
            for status in query.statuses:
                status_set.update(self._case_index.get(status.value, set()))
            candidate_sets.append(status_set)

        # Filter by event type
        if query.event_types:
            event_type_set = set()
            for event_type in query.event_types:
                event_type_set.update(self._case_index.get(event_type, set()))
            candidate_sets.append(event_type_set)

        # Intersect all candidate sets
        if candidate_sets:
            candidate_ids = set.intersection(*candidate_sets)
        else:
            candidate_ids = set(self._edge_cases.keys())

        # Convert to edge cases
        candidates = [self._edge_cases[case_id] for case_id in candidate_ids if case_id in self._edge_cases]

        # Filter by time range
        if query.since_ns is not None or query.until_ns is not None:
            candidates = [
                case
                for case in candidates
                if (query.since_ns is None or case.detection_timestamp_ns >= query.since_ns)
                and (query.until_ns is None or case.detection_timestamp_ns <= query.until_ns)
            ]

        return candidates

    def _calculate_similarity(self, edge_case: EdgeCase, query: Query) -> float:
        """Calculate similarity score between edge case and query."""
        # TODO: Implement sophisticated similarity calculation
        # For now, return a default score
        return 0.8

    def _detect_anomalies(
        self,
        event: Mapping[str, str],
        context: EdgeCaseContext,
    ) -> list[tuple[str, Mapping[str, str]]]:
        """Detect anomalies in an event."""
        anomalies: list[tuple[str, Mapping[str, str]]] = []

        # Check for unusual values
        for key, value in event.items():
            if self._is_unusual_value(key, value):
                anomalies.append(
                    (
                        f"unusual_{key}",
                        {"key": key, "value": value, "reason": "unusual_value_detected"},
                    )
                )

        # Check for context anomalies
        if context.system_state:
            for key, value in context.system_state.items():
                if self._is_unusual_system_state(key, value):
                    anomalies.append(
                        (
                            f"system_anomaly_{key}",
                            {"key": key, "value": value, "reason": "system_state_anomaly"},
                        )
                    )

        return anomalies

    def _is_unusual_value(self, key: str, value: str) -> bool:
        """Check if a value is unusual."""
        # TODO: Implement sophisticated anomaly detection
        # For now, return False
        return False

    def _is_unusual_system_state(self, key: str, value: str) -> bool:
        """Check if a system state value is unusual."""
        # TODO: Implement sophisticated system state anomaly detection
        # For now, return False
        return False

    def _classify_anomaly(
        self,
        anomaly_type: str,
        anomaly_details: Mapping[str, str],
    ) -> EdgeCaseCategory:
        """Classify an anomaly into an edge case category."""
        # TODO: Implement sophisticated anomaly classification
        # For now, return a default category
        return EdgeCaseCategory.UNEXPECTED_BEHAVIOR

    def _assess_anomaly_severity(
        self,
        anomaly_type: str,
        anomaly_details: Mapping[str, str],
    ) -> EdgeCaseSeverity:
        """Assess the severity of an anomaly."""
        # TODO: Implement sophisticated severity assessment
        # For now, return a default severity
        return EdgeCaseSeverity.MEDIUM

    def _analyze_category_pattern(
        self,
        cases: list[EdgeCase],
        category: EdgeCaseCategory,
        timestamp_ns: int,
    ) -> PatternInsights:
        """Analyze patterns for a specific category."""
        # Calculate severity distribution
        severity_counts: dict[str, int] = {}
        for case in cases:
            severity_counts[case.severity.value] = severity_counts.get(case.severity.value, 0) + 1

        # Extract common contexts
        common_contexts = tuple(case.context for case in cases[:5])  # Top 5 contexts

        # Analyze temporal patterns
        temporal_patterns = self._analyze_temporal_patterns(cases)

        # Analyze system patterns
        system_patterns = self._analyze_system_patterns(cases)

        # Generate recommendations
        recommendations = self._generate_recommendations(cases, category)

        return PatternInsights(
            pattern_id=f"pattern_{category.value}_{timestamp_ns}",
            pattern_type=category.value,
            frequency=len(cases),
            severity_distribution=MappingProxyType(severity_counts),
            common_contexts=common_contexts,
            temporal_patterns=MappingProxyType(temporal_patterns),
            system_patterns=MappingProxyType(system_patterns),
            recommendations=tuple(recommendations),
            confidence=0.7,
            timestamp_ns=timestamp_ns,
        )

    def _analyze_cross_category_patterns(
        self,
        cases: list[EdgeCase],
        timestamp_ns: int,
    ) -> PatternInsights | None:
        """Analyze patterns that span multiple categories."""
        # TODO: Implement cross-category pattern analysis
        return None

    def _analyze_temporal_patterns(self, cases: list[EdgeCase]) -> dict[str, str]:
        """Analyze temporal patterns in edge cases."""
        # TODO: Implement temporal pattern analysis
        return {"pattern": "insufficient_data"}

    def _analyze_system_patterns(self, cases: list[EdgeCase]) -> dict[str, str]:
        """Analyze system patterns in edge cases."""
        # TODO: Implement system pattern analysis
        return {"pattern": "insufficient_data"}

    def _generate_recommendations(
        self,
        cases: list[EdgeCase],
        category: EdgeCaseCategory,
    ) -> list[str]:
        """Generate recommendations based on edge case patterns."""
        # TODO: Implement sophisticated recommendation generation
        return [f"Monitor {category.value} cases", f"Investigate recurring patterns"]

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # In production, this would use the system time source
        return 0  # TODO: Integrate with proper time source


__all__ = [
    "EdgeCaseMemory",
    "EdgeCase",
    "EdgeCaseContext",
    "PatternInsights",
    "Query",
    "EdgeCaseSeverity",
    "EdgeCaseCategory",
    "EdgeCaseStatus",
]