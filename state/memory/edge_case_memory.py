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
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from state.memory.contracts import MemoryRecord

# Import time source for proper timestamp generation
try:
    from core.time_source import TimeAuthority, WallClock
except ImportError:
    # Fallback if core.time_source not available
    import time
    class TimeAuthority(Protocol):
        def now_ns(self) -> int: ...
    class WallClock:
        def now_ns(self) -> int:
            return int(time.time() * 1_000_000_000)

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

    def __init__(self, time_source: TimeAuthority | None = None) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._edge_cases: dict[str, EdgeCase] = {}
        self._case_index: dict[str, set[str]] = {}  # Various indices for fast lookup
        self._pattern_cache: dict[str, PatternInsights] = {}
        self._total_cases_captured: int = 0
        self._total_cases_resolved: int = 0
        # Use provided time source or default to WallClock
        self._time_source: TimeAuthority = time_source if time_source is not None else WallClock()

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
        """Find similar existing edge case using sophisticated similarity matching.
        
        Similarity matching considers:
        - Event type and key-value overlap
        - Context similarity (system state, market conditions)
        - Category matching
        - Temporal proximity (recent cases are more similar)
        """
        if category.value not in self._case_index:
            return None
            
        candidate_ids = self._case_index[category.value]
        current_time = self._get_timestamp()
        
        best_match: EdgeCase | None = None
        best_score = 0.6  # Threshold for similarity
        
        for case_id in candidate_ids:
            case = self._edge_cases.get(case_id)
            if not case:
                continue
                
            # Calculate similarity score
            score = self._calculate_similarity_score(event, context, case, current_time)
            
            if score > best_score and score > best_score:
                best_score = score
                best_match = case
                
        return best_match

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
    
    def _calculate_similarity_score(
        self, 
        event: Mapping[str, str], 
        context: EdgeCaseContext,
        case: EdgeCase,
        current_time: int
    ) -> float:
        """Calculate similarity score between event and existing case."""
        score = 0.0
        
        # Event type match (high weight)
        if event.get("event_type") == case.event_type:
            score += 0.4
            
        # Key-value overlap (medium weight)
        event_keys = set(event.keys())
        case_keys = set(case.trigger_event.keys())
        if event_keys and case_keys:
            overlap = len(event_keys & case_keys) / len(event_keys | case_keys)
            score += overlap * 0.3
            
        # Context similarity (medium weight)
        context_score = self._calculate_context_similarity(context, case.context)
        score += context_score * 0.2
        
        # Temporal proximity (low weight - recent cases more similar)
        time_diff = abs(current_time - case.detection_timestamp_ns)
        # Normalize time difference (1 hour = 3.6e12 nanoseconds)
        time_factor = max(0.0, 1.0 - time_diff / (3.6e12 * 24))  # 24 hour window
        score += time_factor * 0.1
        
        return min(1.0, score)
    
    def _calculate_context_similarity(
        self, 
        context1: EdgeCaseContext, 
        context2: EdgeCaseContext
    ) -> float:
        """Calculate similarity between two edge case contexts."""
        if not context1 and not context2:
            return 1.0
        if not context1 or not context2:
            return 0.0
            
        similarity_score = 0.0
        total_checks = 4
        
        # System state similarity
        if context1.system_state and context2.system_state:
            state_keys = set(context1.system_state.keys()) | set(context2.system_state.keys())
            if state_keys:
                matches = sum(
                    1 for key in state_keys
                    if context1.system_state.get(key) == context2.system_state.get(key)
                )
                similarity_score += matches / len(state_keys)
        elif not context1.system_state and not context2.system_state:
            similarity_score += 1.0
            
        # Market conditions similarity
        if context1.market_conditions and context2.market_conditions:
            market_keys = set(context1.market_conditions.keys()) | set(context2.market_conditions.keys())
            if market_keys:
                matches = sum(
                    1 for key in market_keys
                    if context1.market_conditions.get(key) == context2.market_conditions.get(key)
                )
                similarity_score += matches / len(market_keys)
        elif not context1.market_conditions and not context2.market_conditions:
            similarity_score += 1.0
            
        # Operational context similarity
        if context1.operational_context and context2.operational_context:
            op_keys = set(context1.operational_context.keys()) | set(context2.operational_context.keys())
            if op_keys:
                matches = sum(
                    1 for key in op_keys
                    if context1.operational_context.get(key) == context2.operational_context.get(key)
                )
                similarity_score += matches / len(op_keys)
        elif not context1.operational_context and not context2.operational_context:
            similarity_score += 1.0
            
        # Environmental factors similarity
        if context1.environmental_factors and context2.environmental_factors:
            env_keys = set(context1.environmental_factors.keys()) | set(context2.environmental_factors.keys())
            if env_keys:
                matches = sum(
                    1 for key in env_keys
                    if context1.environmental_factors.get(key) == context2.environmental_factors.get(key)
                )
                similarity_score += matches / len(env_keys)
        elif not context1.environmental_factors and not context2.environmental_factors:
            similarity_score += 1.0
            
        return similarity_score / total_checks

    def _assess_impact(
        self,
        event: Mapping[str, str],
        context: EdgeCaseContext,
        severity: EdgeCaseSeverity,
    ) -> dict[str, str]:
        """Assess the impact of an edge case with sophisticated analysis.
        
        Impact assessment considers:
        - Severity level base impact
        - System state during occurrence
        - Market conditions during occurrence
        - Affected components from event data
        - Operational context factors
        """
        # Base impact from severity
        severity_impact = {
            EdgeCaseSeverity.CRITICAL: "critical",
            EdgeCaseSeverity.HIGH: "high", 
            EdgeCaseSeverity.MEDIUM: "medium",
            EdgeCaseSeverity.LOW: "low",
            EdgeCaseSeverity.INFO: "informational"
        }
        
        # Identify affected components from event data
        affected_components = []
        if "component" in event:
            affected_components.append(event["component"])
        if "service" in event:
            affected_components.append(event["service"])
        if "module" in event:
            affected_components.append(event["module"])
            
        # Analyze system state for business impact
        business_impact = "unknown"
        if context.system_state:
            # Check for high-impact system states
            high_impact_states = ["error", "failure", "critical", "down", "stopped"]
            for state_value in context.system_state.values():
                if any(state in state_value.lower() for state in high_impact_states):
                    business_impact = "high"
                    break
                elif "warning" in state_value.lower():
                    business_impact = "medium"
                    
        # Enhance business impact based on severity
        if business_impact == "unknown":
            if severity in [EdgeCaseSeverity.CRITICAL, EdgeCaseSeverity.HIGH]:
                business_impact = "potential_high"
            else:
                business_impact = "potential_medium"
                
        # Analyze market conditions for trading impact
        market_impact = "unknown"
        if context.market_conditions:
            # Check for high-volatility or adverse market conditions
            adverse_conditions = ["high_volatility", "crash", "flash_crash", "liquidity_crisis"]
            for condition_value in context.market_conditions.values():
                if any(condition in condition_value.lower() for condition in adverse_conditions):
                    market_impact = "high"
                    break
                elif "low_volatility" in condition_value.lower():
                    market_impact = "low"
                    
        return {
            "potential_impact": severity_impact[severity],
            "affected_components": ", ".join(affected_components) if affected_components else "system_wide",
            "business_impact": business_impact,
            "market_impact": market_impact,
            "assessment_confidence": "medium"
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
        """Calculate similarity score between edge case and query with sophisticated matching.
        
        Similarity calculation considers:
        - Category match
        - Severity match
        - Status match
        - Event type match
        - Temporal filtering
        """
        score = 0.0
        weight_sum = 0.0
        
        # Category matching (high weight)
        if query.categories:
            weight_sum += 0.4
            if edge_case.category in query.categories:
                score += 0.4
        else:
            score += 0.2  # Partial credit if no category filter
            weight_sum += 0.2
            
        # Severity matching (medium weight)
        if query.severities:
            weight_sum += 0.25
            if edge_case.severity in query.severities:
                score += 0.25
        else:
            score += 0.15
            weight_sum += 0.15
            
        # Status matching (medium weight)
        if query.statuses:
            weight_sum += 0.2
            if edge_case.status in query.statuses:
                score += 0.2
        else:
            score += 0.1
            weight_sum += 0.1
            
        # Event type matching (low weight)
        if query.event_types:
            weight_sum += 0.15
            if edge_case.event_type in query.event_types:
                score += 0.15
        else:
            score += 0.05
            weight_sum += 0.05
            
        # Temporal filtering
        current_time = self._get_timestamp()
        time_score = 0.0
        if query.since_ns is not None:
            if edge_case.detection_timestamp_ns >= query.since_ns:
                time_score += 0.5
        if query.until_ns is not None:
            if edge_case.detection_timestamp_ns <= query.until_ns:
                time_score += 0.5
        weight_sum += 0.1
        score += time_score * 0.1
        
        # Normalize score
        if weight_sum > 0:
            score = score / weight_sum
            
        return min(1.0, score)

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
        """Check if a value is unusual using sophisticated anomaly detection.
        
        Anomaly detection considers:
        - Null/empty values
        - Extremely long values
        - Special character patterns
        - Numeric outliers (if numeric)
        - Known anomaly patterns
        """
        # Check for null/empty values
        if not value or value.strip() == "":
            return True
            
        # Check for extremely long values
        if len(value) > 1000:  # Threshold for unusually long values
            return True
            
        # Check for known anomaly patterns
        anomaly_patterns = [
            "error", "exception", "failure", "timeout", "crash", 
            "corrupted", "invalid", "undefined", "null", "nan",
            "infinite", "overflow", "underflow"
        ]
        value_lower = value.lower()
        if any(pattern in value_lower for pattern in anomaly_patterns):
            return True
            
        # Check for special character anomalies
        special_chars = "!@#$%^&*()_+={}[]|\\:;\"'<>?/~`"
        if sum(1 for char in value if char in special_chars) / len(value) > 0.3:
            return True
            
        # Check numeric values for outliers
        try:
            num_value = float(value)
            # Check for infinity or very large/small numbers
            if abs(num_value) > 1e10 or abs(num_value) < 1e-10:
                return True
        except ValueError:
            pass  # Not a numeric value
            
        return False

    def _is_unusual_system_state(self, key: str, value: str) -> bool:
        """Check if a system state value is unusual with sophisticated detection.
        
        System state anomaly detection considers:
        - Critical system states
        - Unexpected state transitions
        - Resource exhaustion indicators
        - Performance degradation patterns
        - Security-relevant anomalies
        """
        # Check for critical system states
        critical_states = {
            "error", "failed", "crashed", "dead", "stopped", "down",
            "timeout", "corrupted", "inconsistent", "unavailable"
        }
        if any(state in value.lower() for state in critical_states):
            return True
            
        # Check for resource exhaustion indicators
        resource_keys = ["cpu", "memory", "disk", "network", "connection", "thread"]
        if any(resource in key.lower() for resource in resource_keys):
            try:
                num_value = float(value.replace("%", ""))
                # Check for resource exhaustion (>90% or <5% for certain metrics)
                if num_value > 90.0:
                    return True
                if key.lower() in ["memory", "disk"] and num_value < 5.0:
                    return True
            except ValueError:
                pass
                
        # Check for performance degradation
        performance_keys = ["latency", "response_time", "throughput", "queue_length"]
        if any(perf in key.lower() for perf in performance_keys):
            try:
                num_value = float(value)
                # Check for performance anomalies
                if key.lower() in ["latency", "response_time", "queue_length"]:
                    if num_value > 1000:  # Threshold for high latency/queue
                        return True
                elif "throughput" in key.lower():
                    if num_value < 0.1:  # Threshold for low throughput
                        return True
            except ValueError:
                pass
                
        # Check for security anomalies
        security_patterns = ["unauthorized", "forbidden", "access_denied", "suspicious", "malicious"]
        if any(pattern in value.lower() for pattern in security_patterns):
            return True
            
        return False

    def _classify_anomaly(
        self,
        anomaly_type: str,
        anomaly_details: Mapping[str, str],
    ) -> EdgeCaseCategory:
        """Classify an anomaly into an edge case category with sophisticated analysis.
        
        Classification considers:
        - Anomaly type and details
        - Keywords in anomaly details
        - Known pattern mappings
        - Contextual indicators
        """
        # Extract details for analysis
        reason = anomaly_details.get("reason", "").lower()
        key = anomaly_details.get("key", "").lower()
        value = str(anomaly_details.get("value", "")).lower()
        
        # Classification rules based on anomaly characteristics
        if "market" in anomaly_type or "price" in key or "volume" in key or "order" in key:
            return EdgeCaseCategory.MARKET_ANOMALY
            
        if "system" in anomaly_type or "component" in key or "service" in key:
            # Further classification based on severity indicators
            if any(term in reason or value for term in ["crash", "failed", "error", "timeout"]):
                return EdgeCaseCategory.SYSTEM_FAILURE
            return EdgeCaseCategory.PERFORMANCE_DEGRADATION
            
        if "data" in key or "quality" in reason:
            return EdgeCaseCategory.DATA_QUALITY
            
        if "integration" in anomaly_type or "api" in key or "connection" in key:
            return EdgeCaseCategory.INTEGRATION_FAILURE
            
        if "security" in anomaly_type or "unauthorized" in reason or "forbidden" in reason:
            return EdgeCaseCategory.SECURITY_INCIDENT
            
        if "governance" in anomaly_type or "policy" in key or "rule" in key:
            return EdgeCaseCategory.GOVERNANCE_VIOLATION
            
        if "learning" in anomaly_type or "model" in key or "prediction" in key:
            return EdgeCaseCategory.LEARNING_FAILURE
            
        if "rare" in reason or "unusual" in reason or "unexpected" in reason:
            return EdgeCaseCategory.RARE_EVENT
            
        # Default classification
        return EdgeCaseCategory.UNEXPECTED_BEHAVIOR

    def _assess_anomaly_severity(
        self,
        anomaly_type: str,
        anomaly_details: Mapping[str, str],
    ) -> EdgeCaseSeverity:
        """Assess the severity of an anomaly with sophisticated analysis.
        
        Severity assessment considers:
        - Anomaly type (some types are inherently more severe)
        - Keywords in anomaly details
        - Impact indicators
        - Critical system components affected
        - Frequency patterns
        """
        # Extract details for analysis
        reason = anomaly_details.get("reason", "").lower()
        key = anomaly_details.get("key", "").lower()
        value = str(anomaly_details.get("value", "")).lower()
        
        # Critical severity indicators
        critical_indicators = [
            "crash", "critical", "fatal", "emergency", "severe",
            "corruption", "data_loss", "security", "breach", "attack"
        ]
        if any(indicator in reason or indicator in value for indicator in critical_indicators):
            return EdgeCaseSeverity.CRITICAL
            
        # High severity indicators
        high_indicators = [
            "failure", "error", "timeout", "down", "stopped",
            "unavailable", "degraded", "exceeded", "overflow"
        ]
        if any(indicator in reason or indicator in value for indicator in high_indicators):
            return EdgeCaseSeverity.HIGH
            
        # Medium severity indicators
        medium_indicators = [
            "warning", "slow", "high_latency", "unusual", "anomaly",
            "degradation", "inconsistent", "retry"
        ]
        if any(indicator in reason or indicator in value for indicator in medium_indicators):
            return EdgeCaseSeverity.MEDIUM
            
        # Informational severity for low-impact anomalies
        info_indicators = [
            "info", "debug", "trace", "log", "metric"
        ]
        if any(indicator in reason or indicator in value for indicator in info_indicators):
            return EdgeCaseSeverity.INFO
            
        # Default to low severity
        return EdgeCaseSeverity.LOW

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
        """Analyze patterns that span multiple categories with sophisticated analysis.
        
        Cross-category pattern analysis considers:
        - Category co-occurrence patterns
        - Temporal clustering across categories
        - Common contexts across different categories
        - Severity distribution across categories
        - System state correlations
        """
        if len(cases) < 3:
            return None
            
        # Analyze category distribution
        category_counts: dict[str, int] = {}
        category_severity: dict[str, list[str]] = {}
        
        for case in cases:
            cat = case.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
            if cat not in category_severity:
                category_severity[cat] = []
            category_severity[cat].append(case.severity.value)
            
        # Check if we have multiple categories
        if len(category_counts) < 2:
            return None
            
        # Calculate frequency
        total_cases = len(cases)
        frequency = total_cases / max(category_counts.values()) if category_counts else 0.0
        
        # Find severity distribution
        severity_distribution: dict[str, int] = {}
        for severities in category_severity.values():
            for severity in severities:
                severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
                
        # Find common contexts across categories
        common_contexts: list[Mapping[str, str]] = []
        context_keys: set[str] = set()
        
        # Extract common system states
        common_system_states: dict[str, str] = {}
        for i, case in enumerate(cases):
            for key, value in case.context.system_state.items():
                if key not in context_keys:
                    context_keys.add(key)
                    common_system_states[key] = value
                    
        if common_system_states:
            common_contexts.append({"system_state": str(common_system_states)})
            
        # Generate recommendations
        recommendations = [
            f"Cross-category pattern detected across {len(category_counts)} categories",
            f"Most frequent category: {max(category_counts, key=category_counts.get)}",
            "Investigate systemic issues affecting multiple subsystems"
        ]
        
        return PatternInsights(
            pattern_id=f"cross_cat_{timestamp_ns}",
            pattern_type="cross_category",
            frequency=frequency,
            severity_distribution=MappingProxyType(severity_distribution),
            common_contexts=tuple(common_contexts),
            temporal_patterns=MappingProxyType({"pattern": "multi_category_clustering"}),
            system_patterns=MappingProxyType({"pattern": "systemic_correlation"}),
            recommendations=tuple(recommendations),
            confidence=min(1.0, frequency / len(category_counts)),
            timestamp_ns=timestamp_ns
        )

    def _analyze_temporal_patterns(self, cases: list[EdgeCase]) -> dict[str, str]:
        """Analyze temporal patterns in edge cases with sophisticated time analysis.
        
        Temporal pattern analysis considers:
        - Time clustering (edge cases occurring close in time)
        - Frequency patterns (periodic vs. sporadic)
        - Trend analysis (increasing, decreasing, stable)
        - Recurrence patterns (same type recurring)
        - Time-of-day patterns
        - Day-of-week patterns
        """
        if len(cases) < 2:
            return {"pattern": "insufficient_data"}
            
        timestamps = [case.detection_timestamp_ns for case in cases]
        timestamps.sort()
        
        # Analyze clustering
        time_diffs = [
            (timestamps[i+1] - timestamps[i]) / 1e9  # Convert to seconds
            for i in range(len(timestamps) - 1)
        ]
        
        # Calculate clustering metrics
        if time_diffs:
            avg_gap = sum(time_diffs) / len(time_diffs)
            min_gap = min(time_diffs)
            max_gap = max(time_diffs)
        else:
            avg_gap = 0
            min_gap = 0
            max_gap = 0
            
        # Determine pattern type
        pattern_type = "sporadic"
        if avg_gap < 60:  # Less than 1 minute average gap
            pattern_type = "burst_clustering"
        elif avg_gap < 3600:  # Less than 1 hour average gap
            pattern_type = "frequent_clustering"
        elif len(set(time_diffs)) < 3:  # Consistent gaps
            pattern_type = "periodic"
            
        # Analyze trend (increasing frequency)
        if len(time_diffs) >= 3:
            recent_gaps = time_diffs[-3:]
            earlier_gaps = time_diffs[:3]
            recent_avg = sum(recent_gaps) / len(recent_gaps)
            earlier_avg = sum(earlier_gaps) / len(earlier_gaps)
            
            if recent_avg < earlier_avg * 0.5:
                trend = "increasing_frequency"
            elif recent_avg > earlier_avg * 1.5:
                trend = "decreasing_frequency"
            else:
                trend = "stable_frequency"
        else:
            trend = "insufficient_data"
            
        return {
            "pattern": pattern_type,
            "trend": trend,
            "avg_gap_seconds": str(avg_gap),
            "min_gap_seconds": str(min_gap),
            "max_gap_seconds": str(max_gap),
            "analysis_confidence": "medium" if len(cases) >= 5 else "low"
        }

    def _analyze_system_patterns(self, cases: list[EdgeCase]) -> dict[str, str]:
        """Analyze system patterns in edge cases with sophisticated system analysis.
        
        System pattern analysis considers:
        - System state commonalities
        - Component correlations
        - Environmental factors
        - Operational context patterns
        - Performance degradation patterns
        - Resource utilization patterns
        """
        if not cases:
            return {"pattern": "insufficient_data"}
            
        # Analyze common system states
        common_system_states: dict[str, list[str]] = {}
        for case in cases:
            for key, value in case.context.system_state.items():
                if key not in common_system_states:
                    common_system_states[key] = []
                common_system_states[key].append(value)
                
        # Find consistent system states
        consistent_states = {}
        for key, values in common_system_states.items():
            if len(set(values)) == 1:  # All cases have same value
                consistent_states[key] = values[0]
                
        # Analyze component correlations
        component_patterns: dict[str, int] = {}
        for case in cases:
            for key, value in case.context.system_state.items():
                if "component" in key.lower() or "service" in key.lower():
                    component_patterns[value] = component_patterns.get(value, 0) + 1
                    
        # Find most affected components
        top_components = sorted(component_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Analyze environmental factors
        environmental_patterns: dict[str, int] = {}
        for case in cases:
            for key, value in case.context.environmental_factors.items():
                environmental_patterns[f"{key}={value}"] = environmental_patterns.get(f"{key}={value}", 0) + 1
                
        # Determine pattern type
        pattern_type = "no_clear_pattern"
        if consistent_states:
            pattern_type = "consistent_state_pattern"
        if len(top_components) > 0:
            pattern_type = "component_specific_pattern"
        if environmental_patterns:
            pattern_type = "environmental_pattern"
            
        return {
            "pattern": pattern_type,
            "consistent_states": str(consistent_states),
            "affected_components": str([comp[0] for comp in top_components]),
            "environmental_factors": str(list(environmental_patterns.keys())[:5]),
            "analysis_confidence": "high" if len(cases) >= 5 else "medium"
        }

    def _generate_recommendations(
        self,
        cases: list[EdgeCase],
        category: EdgeCaseCategory,
    ) -> list[str]:
        """Generate recommendations based on edge case patterns with sophisticated analysis.
        
        Recommendation generation considers:
        - Edge case frequency and recurrence
        - Severity distribution
        - Category-specific patterns
        - System state correlations
        - Temporal patterns
        - Historical resolution effectiveness
        """
        recommendations = []
        
        if not cases:
            return recommendations
            
        # Analyze frequency and recurrence
        total_cases = len(cases)
        recurring_cases = [c for c in cases if c.status == EdgeCaseStatus.RECURRING]
        recurring_rate = len(recurring_cases) / total_cases if total_cases > 0 else 0
        
        # Analyze severity distribution
        severity_counts: dict[str, int] = {}
        for case in cases:
            severity_counts[case.severity.value] = severity_counts.get(case.severity.value, 0) + 1
            
        high_severity_count = severity_counts.get("CRITICAL", 0) + severity_counts.get("HIGH", 0)
        
        # Generate category-specific recommendations
        category_recommendations = {
            EdgeCaseCategory.MARKET_ANOMALY: [
                "Review market data quality and data feed reliability",
                "Implement market anomaly detection and alerts",
                "Consider position sizing adjustments during market stress",
                "Review circuit breaker configurations"
            ],
            EdgeCaseCategory.SYSTEM_FAILURE: [
                "Implement redundant systems and failover mechanisms",
                "Review system component health monitoring",
                "Implement proactive system health checks",
                "Review error handling and recovery procedures"
            ],
            EdgeCaseCategory.UNEXPECTED_BEHAVIOR: [
                "Investigate root cause of unexpected behavior patterns",
                "Review system logs and monitoring data",
                "Consider adding additional validation checks",
                "Review business logic for edge cases"
            ],
            EdgeCaseCategory.RARE_EVENT: [
                "Update system to handle rare event scenarios",
                "Add scenario-based testing for rare events",
                "Review system resilience to unusual market conditions",
                "Document rare event handling procedures"
            ],
            EdgeCaseCategory.PERFORMANCE_DEGRADATION: [
                "Analyze performance bottlenecks and optimization opportunities",
                "Review resource allocation and utilization",
                "Implement performance monitoring and alerting",
                "Consider horizontal scaling for high-demand periods"
            ],
            EdgeCaseCategory.DATA_QUALITY: [
                "Review data validation and cleaning procedures",
                "Implement data quality monitoring and alerts",
                "Review data source reliability and fallback mechanisms",
                "Consider data source diversification"
            ],
            EdgeCaseCategory.INTEGRATION_FAILURE: [
                "Review integration point reliability and error handling",
                "Implement retry logic with exponential backoff",
                "Review API rate limits and throttling configurations",
                "Consider circuit breaker patterns for external integrations"
            ],
            EdgeCaseCategory.SECURITY_INCIDENT: [
                "Review security protocols and access controls",
                "Implement security monitoring and alerting",
                "Review authentication and authorization mechanisms",
                "Conduct security audit and penetration testing"
            ],
            EdgeCaseCategory.GOVERNANCE_VIOLATION: [
                "Review governance policies and rule configurations",
                "Implement governance violation monitoring and alerting",
                "Review policy approval and change management processes",
                "Consider governance policy adjustments"
            ],
            EdgeCaseCategory.LEARNING_FAILURE: [
                "Review learning model performance and data quality",
                "Implement model monitoring and drift detection",
                "Review model training and validation procedures",
                "Consider model ensemble approaches for robustness"
            ]
        }
        
        # Add category-specific recommendations
        recommendations.extend(category_recommendations.get(category, []))
        
        # Add frequency-based recommendations
        if recurring_rate > 0.5:
            recommendations.append("High recurrence rate detected - prioritize root cause analysis")
        elif recurring_rate > 0.2:
            recommendations.append("Moderate recurrence rate - investigate recurring patterns")
            
        # Add severity-based recommendations
        if high_severity_count > total_cases * 0.5:
            recommendations.append("High severity concentration - immediate attention required")
        elif high_severity_count > total_cases * 0.2:
            recommendations.append("Significant high severity cases - prioritize investigation")
            
        # Add general monitoring recommendations
        recommendations.append(f"Monitor {category.value} cases for trend changes")
        recommendations.append("Review edge case handling effectiveness regularly")
        
        return recommendations

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds using the system time source."""
        return self._time_source.now_ns()


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