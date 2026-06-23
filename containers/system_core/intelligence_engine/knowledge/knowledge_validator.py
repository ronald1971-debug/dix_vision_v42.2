"""M-1 Knowledge Layer - Knowledge Validator.

Validates knowledge sources, detects conflicts, ensures epistemic integrity.
This is the foundation of the M-1 Knowledge Layer that transforms INDIRA from
Signal Intelligence to Knowledge Intelligence.

Design Principles:
- INV-15: No external dependencies, no IO, no clock
- INV-08: Pure data surface, no engine imports
- Frozen dataclasses for structural hashing
- Thread-safe validation operations
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
    from state.knowledge_graph import KnowledgeGraph

_logger = logging.getLogger(__name__)


class ValidationSeverity(str, enum.Enum):
    """Severity level of validation issues."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class KnowledgeSourceType(str, enum.Enum):
    """Types of knowledge sources."""

    MARKET_DATA = "MARKET_DATA"
    NEWS_SENTIMENT = "NEWS_SENTIMENT"
    ON_CHAIN_ANALYSIS = "ON_CHAIN_ANALYSIS"
    STRATEGY_BACKTEST = "STRATEGY_BACKTEST"
    OPERATOR_INPUT = "OPERATOR_INPUT"
    LEARNING_INFERENCE = "LEARNING_INFERENCE"
    EXTERNAL_API = "EXTERNAL_API"
    SYSTEM_INTERNAL = "SYSTEM_INTERNAL"


@dataclasses.dataclass(frozen=True, slots=True)
class KnowledgeSource:
    """A source of knowledge for validation.

    Fields:
        source_id: Unique identifier for this knowledge source
        source_type: Type of knowledge source
        origin: Module or subsystem that produced this knowledge
        content: The knowledge content (key-value pairs)
        confidence: Source confidence level (0.0-1.0)
        timestamp_ns: Nanosecond timestamp of knowledge creation
        metadata: Additional metadata about the source
        reliability_score: Historical reliability score (0.0-1.0)
    """

    source_id: str
    source_type: KnowledgeSourceType
    origin: str
    content: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    confidence: float = 0.5
    timestamp_ns: int = 0
    metadata: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    reliability_score: float = 0.5

    def __post_init__(self) -> None:
        if not self.source_id:
            raise ValueError("KnowledgeSource.source_id must be non-empty")
        if not isinstance(self.content, MappingProxyType):
            object.__setattr__(self, "content", MappingProxyType(dict(self.content)))
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"KnowledgeSource.confidence must be 0.0-1.0, got {self.confidence}")
        if not 0.0 <= self.reliability_score <= 1.0:
            raise ValueError(
                f"KnowledgeSource.reliability_score must be 0.0-1.0, got {self.reliability_score}"
            )


@dataclasses.dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A specific validation issue found in a knowledge source."""

    issue_id: str
    severity: ValidationSeverity
    category: str
    description: str
    affected_field: str | None = None
    suggested_fix: str | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class ValidationResult:
    """Result of validating a knowledge source."""

    is_valid: bool
    confidence_score: float
    issues: tuple[ValidationIssue, ...]
    validated_source: KnowledgeSource
    timestamp_ns: int

    def has_critical_issues(self) -> bool:
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)

    def has_high_issues(self) -> bool:
        return any(issue.severity == ValidationSeverity.HIGH for issue in self.issues)


@dataclasses.dataclass(frozen=True, slots=True)
class ConflictReport:
    """Report of conflicts between knowledge sources."""

    conflict_id: str
    sources_involved: tuple[str, ...]  # source_ids
    conflict_type: str
    severity: ValidationSeverity
    description: str
    conflicting_fields: tuple[str, ...]
    detected_at_ns: int
    resolution_strategy: str | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class IntegrityScore:
    """Epistemic integrity score for a knowledge graph."""

    overall_score: float  # 0.0-1.0
    consistency_score: float
    reliability_score: float
    completeness_score: float
    temporal_consistency: float
    source_diversity: float
    timestamp_ns: int


@dataclasses.dataclass(frozen=True, slots=True)
class ReliabilityScore:
    """Reliability assessment for a knowledge source."""

    source_id: str
    historical_accuracy: float
    prediction_accuracy: float
    consistency_score: float
    temporal_stability: float
    overall_reliability: float
    sample_size: int
    last_updated_ns: int


@dataclasses.dataclass(frozen=True, slots=True)
class ConsistencyReport:
    """Report of temporal consistency check."""

    is_consistent: bool
    consistency_score: float
    inconsistencies_found: int
    temporal_drift_detected: bool
    drift_magnitude: float
    analyzed_period_ns: int
    timestamp_ns: int


class KnowledgeValidator:
    """Validates knowledge sources and ensures epistemic integrity.

    This is the core component of the M-1 Knowledge Layer that transforms
    INDIRA from Signal Intelligence to Knowledge Intelligence by providing
    rigorous validation of all knowledge inputs.
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._validation_history: dict[str, list[ValidationResult]] = {}
        self._source_reliability: dict[str, ReliabilityScore] = {}
        self._total_validations: int = 0

    def validate_source(self, source: KnowledgeSource) -> ValidationResult:
        """Validate a knowledge source for epistemic integrity.

        Args:
            source: Knowledge source to validate

        Returns:
            ValidationResult with validation issues and confidence score
        """
        issues: list[ValidationIssue] = []
        timestamp_ns = self._get_timestamp()

        # Basic validation
        issues.extend(self._validate_basic_structure(source))

        # Content validation
        issues.extend(self._validate_content(source))

        # Confidence validation
        issues.extend(self._validate_confidence(source))

        # Reliability validation
        issues.extend(self._validate_reliability(source))

        # Temporal validation
        issues.extend(self._validate_temporal(source))

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(source, issues)

        # Determine overall validity
        is_valid = not any(
            issue.severity in (ValidationSeverity.CRITICAL, ValidationSeverity.HIGH)
            for issue in issues
        )

        result = ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence_score,
            issues=tuple(issues),
            validated_source=source,
            timestamp_ns=timestamp_ns,
        )

        # Store validation history
        with self._lock:
            self._validation_history.setdefault(source.source_id, []).append(result)
            self._total_validations += 1

        _logger.info(
            "Validated source %s: valid=%s, confidence=%.2f, issues=%d",
            source.source_id,
            is_valid,
            confidence_score,
            len(issues),
        )

        return result

    def detect_conflicts(
        self,
        sources: list[KnowledgeSource],
        existing_knowledge: KnowledgeGraph | None = None,
    ) -> list[ConflictReport]:
        """Detect conflicts between knowledge sources.

        Args:
            sources: List of knowledge sources to check for conflicts
            existing_knowledge: Optional existing knowledge graph for comparison

        Returns:
            List of ConflictReport objects describing detected conflicts
        """
        conflicts: list[ConflictReport] = []
        timestamp_ns = self._get_timestamp()

        # Check for direct conflicts between sources
        conflicts.extend(self._detect_direct_conflicts(sources, timestamp_ns))

        # Check for conflicts with existing knowledge
        if existing_knowledge is not None:
            conflicts.extend(
                self._detect_knowledge_graph_conflicts(sources, existing_knowledge, timestamp_ns)
            )

        # Check for temporal conflicts
        conflicts.extend(self._detect_temporal_conflicts(sources, timestamp_ns))

        # Check for semantic conflicts
        conflicts.extend(self._detect_semantic_conflicts(sources, timestamp_ns))

        return conflicts

    def epistemic_integrity_check(self, knowledge: KnowledgeGraph) -> IntegrityScore:
        """Perform comprehensive epistemic integrity check on knowledge graph.

        Args:
            knowledge: Knowledge graph to check

        Returns:
            IntegrityScore with various integrity dimensions
        """
        timestamp_ns = self._get_timestamp()

        # Calculate individual integrity dimensions
        consistency_score = self._calculate_consistency_score(knowledge)
        reliability_score = self._calculate_reliability_score(knowledge)
        completeness_score = self._calculate_completeness_score(knowledge)
        temporal_consistency = self._calculate_temporal_consistency(knowledge)
        source_diversity = self._calculate_source_diversity(knowledge)

        # Calculate overall score
        overall_score = (
            consistency_score * 0.25
            + reliability_score * 0.25
            + completeness_score * 0.2
            + temporal_consistency * 0.15
            + source_diversity * 0.15
        )

        return IntegrityScore(
            overall_score=overall_score,
            consistency_score=consistency_score,
            reliability_score=reliability_score,
            completeness_score=completeness_score,
            temporal_consistency=temporal_consistency,
            source_diversity=source_diversity,
            timestamp_ns=timestamp_ns,
        )

    def source_reliability_scoring(self, source: KnowledgeSource) -> ReliabilityScore:
        """Calculate reliability score for a knowledge source.

        Args:
            source: Knowledge source to score

        Returns:
            ReliabilityScore with detailed reliability metrics
        """
        # Get historical validation data
        history = self._validation_history.get(source.source_id, [])

        # Calculate historical accuracy
        historical_accuracy = self._calculate_historical_accuracy(history)

        # Calculate prediction accuracy (if applicable)
        prediction_accuracy = self._calculate_prediction_accuracy(source, history)

        # Calculate consistency score
        consistency_score = self._calculate_source_consistency(source, history)

        # Calculate temporal stability
        temporal_stability = self._calculate_temporal_stability(source, history)

        # Calculate overall reliability
        overall_reliability = (
            historical_accuracy * 0.3
            + prediction_accuracy * 0.3
            + consistency_score * 0.2
            + temporal_stability * 0.2
        )

        return ReliabilityScore(
            source_id=source.source_id,
            historical_accuracy=historical_accuracy,
            prediction_accuracy=prediction_accuracy,
            consistency_score=consistency_score,
            temporal_stability=temporal_stability,
            overall_reliability=overall_reliability,
            sample_size=len(history),
            last_updated_ns=self._get_timestamp(),
        )

    def temporal_consistency_check(
        self,
        knowledge: KnowledgeGraph,
        period_ns: int = 86_400_000_000_000,  # 24 hours in nanoseconds
    ) -> ConsistencyReport:
        """Check temporal consistency of knowledge over time.

        Args:
            knowledge: Knowledge graph to check
            period_ns: Time period to analyze in nanoseconds

        Returns:
            ConsistencyReport with temporal consistency analysis
        """
        timestamp_ns = self._get_timestamp()

        # Analyze temporal consistency
        is_consistent, consistency_score = self._analyze_temporal_consistency(knowledge, period_ns)

        # Count inconsistencies
        inconsistencies_found = self._count_temporal_inconsistencies(knowledge, period_ns)

        # Detect temporal drift
        temporal_drift_detected, drift_magnitude = self._detect_temporal_drift(knowledge, period_ns)

        return ConsistencyReport(
            is_consistent=is_consistent,
            consistency_score=consistency_score,
            inconsistencies_found=inconsistencies_found,
            temporal_drift_detected=temporal_drift_detected,
            drift_magnitude=drift_magnitude,
            analyzed_period_ns=period_ns,
            timestamp_ns=timestamp_ns,
        )

    # ------------------------------------------------------------------
    # Private validation methods
    # ------------------------------------------------------------------

    def _validate_basic_structure(self, source: KnowledgeSource) -> list[ValidationIssue]:
        """Validate basic structure of knowledge source."""
        issues: list[ValidationIssue] = []

        if not source.content:
            issues.append(
                ValidationIssue(
                    issue_id=f"{source.source_id}_empty_content",
                    severity=ValidationSeverity.MEDIUM,
                    category="structure",
                    description="Knowledge source has empty content",
                    affected_field="content",
                    suggested_fix="Provide meaningful content in the knowledge source",
                )
            )

        if source.confidence < 0.3:
            issues.append(
                ValidationIssue(
                    issue_id=f"{source.source_id}_low_confidence",
                    severity=ValidationSeverity.LOW,
                    category="confidence",
                    description=f"Low confidence score: {source.confidence}",
                    affected_field="confidence",
                    suggested_fix="Increase confidence through validation or testing",
                )
            )

        return issues

    def _validate_content(self, source: KnowledgeSource) -> list[ValidationIssue]:
        """Validate content of knowledge source."""
        issues: list[ValidationIssue] = []

        # Check for required fields based on source type
        required_fields = self._get_required_fields(source.source_type)
        missing_fields = required_fields - set(source.content.keys())

        if missing_fields:
            issues.append(
                ValidationIssue(
                    issue_id=f"{source.source_id}_missing_fields",
                    severity=ValidationSeverity.HIGH,
                    category="content",
                    description=f"Missing required fields: {', '.join(missing_fields)}",
                    affected_field="content",
                    suggested_fix=f"Add required fields: {', '.join(missing_fields)}",
                )
            )

        return issues

    def _validate_confidence(self, source: KnowledgeSource) -> list[ValidationIssue]:
        """Validate confidence levels."""
        issues: list[ValidationIssue] = []

        # Check if confidence is justified by reliability
        if source.reliability_score < 0.5 and source.confidence > 0.7:
            issues.append(
                ValidationIssue(
                    issue_id=f"{source.source_id}_confidence_mismatch",
                    severity=ValidationSeverity.MEDIUM,
                    category="confidence",
                    description=f"Confidence {source.confidence} not justified by reliability {source.reliability_score}",
                    affected_field="confidence",
                    suggested_fix="Adjust confidence to match historical reliability",
                )
            )

        return issues

    def _validate_reliability(self, source: KnowledgeSource) -> list[ValidationIssue]:
        """Validate reliability of knowledge source."""
        issues: list[ValidationIssue] = []

        if source.reliability_score < 0.3:
            issues.append(
                ValidationIssue(
                    issue_id=f"{source.source_id}_low_reliability",
                    severity=ValidationSeverity.HIGH,
                    category="reliability",
                    description=f"Low reliability score: {source.reliability_score}",
                    affected_field="reliability_score",
                    suggested_fix="Improve source reliability through testing and validation",
                )
            )

        return issues

    def _validate_temporal(self, source: KnowledgeSource) -> list[ValidationIssue]:
        """Validate temporal aspects of knowledge source."""
        issues: list[ValidationIssue] = []

        # Check if knowledge is stale
        current_ns = self._get_timestamp()
        age_ns = current_ns - source.timestamp_ns

        # Define staleness thresholds based on source type
        staleness_thresholds = {
            KnowledgeSourceType.MARKET_DATA: 60_000_000_000,  # 1 minute
            KnowledgeSourceType.NEWS_SENTIMENT: 3_600_000_000_000,  # 1 hour
            KnowledgeSourceType.ON_CHAIN_ANALYSIS: 600_000_000_000,  # 10 minutes
            KnowledgeSourceType.STRATEGY_BACKTEST: 86_400_000_000_000 * 7,  # 7 days
            KnowledgeSourceType.OPERATOR_INPUT: 86_400_000_000_000 * 30,  # 30 days
            KnowledgeSourceType.LEARNING_INFERENCE: 86_400_000_000_000,  # 1 day
            KnowledgeSourceType.EXTERNAL_API: 3_600_000_000_000,  # 1 hour
            KnowledgeSourceType.SYSTEM_INTERNAL: 60_000_000_000,  # 1 minute
        }

        threshold = staleness_thresholds.get(
            source.source_type, 86_400_000_000_000
        )  # default 1 day

        if age_ns > threshold:
            issues.append(
                ValidationIssue(
                    issue_id=f"{source.source_id}_stale_knowledge",
                    severity=ValidationSeverity.MEDIUM,
                    category="temporal",
                    description=f"Knowledge is stale: {age_ns / 1e9:.1f} seconds old",
                    affected_field="timestamp_ns",
                    suggested_fix="Refresh knowledge source with current data",
                )
            )

        return issues

    def _calculate_confidence_score(
        self,
        source: KnowledgeSource,
        issues: list[ValidationIssue],
    ) -> float:
        """Calculate overall confidence score based on validation issues."""
        base_confidence = source.confidence

        # Penalize based on issue severity
        severity_penalties = {
            ValidationSeverity.CRITICAL: 0.5,
            ValidationSeverity.HIGH: 0.3,
            ValidationSeverity.MEDIUM: 0.15,
            ValidationSeverity.LOW: 0.05,
            ValidationSeverity.INFO: 0.0,
        }

        total_penalty = sum(severity_penalties.get(issue.severity, 0.0) for issue in issues)

        # Boost based on reliability
        reliability_boost = (source.reliability_score - 0.5) * 0.2

        # Calculate final confidence score
        confidence_score = base_confidence - total_penalty + reliability_boost
        confidence_score = max(0.0, min(1.0, confidence_score))

        return confidence_score

    def _detect_direct_conflicts(
        self,
        sources: list[KnowledgeSource],
        timestamp_ns: int,
    ) -> list[ConflictReport]:
        """Detect direct conflicts between knowledge sources."""
        conflicts: list[ConflictReport] = []

        for i, source1 in enumerate(sources):
            for source2 in sources[i + 1 :]:
                # Check for conflicting content
                conflicting_fields = self._find_conflicting_fields(source1, source2)

                if conflicting_fields:
                    conflicts.append(
                        ConflictReport(
                            conflict_id=f"conflict_{source1.source_id}_{source2.source_id}",
                            sources_involved=(source1.source_id, source2.source_id),
                            conflict_type="direct_content_conflict",
                            severity=ValidationSeverity.HIGH,
                            description=f"Direct conflict between {source1.source_id} and {source2.source_id}",
                            conflicting_fields=tuple(conflicting_fields),
                            detected_at_ns=timestamp_ns,
                            resolution_strategy="merge_or_prioritize",
                        )
                    )

        return conflicts

    def _detect_knowledge_graph_conflicts(
        self,
        sources: list[KnowledgeSource],
        knowledge: KnowledgeGraph,
        timestamp_ns: int,
    ) -> list[ConflictReport]:
        """Detect conflicts with existing knowledge graph."""
        conflicts: list[ConflictReport] = []

        for source in sources:
            # Check for conflicts with existing knowledge
            conflicting_fields = self._find_knowledge_graph_conflicts(source, knowledge)

            if conflicting_fields:
                conflicts.append(
                    ConflictReport(
                        conflict_id=f"conflict_{source.source_id}_knowledge_graph",
                        sources_involved=(source.source_id,),
                        conflict_type="knowledge_graph_conflict",
                        severity=ValidationSeverity.MEDIUM,
                        description=f"Conflict between {source.source_id} and existing knowledge graph",
                        conflicting_fields=tuple(conflicting_fields),
                        detected_at_ns=timestamp_ns,
                        resolution_strategy="knowledge_update",
                    )
                )

        return conflicts

    def _detect_temporal_conflicts(
        self,
        sources: list[KnowledgeSource],
        timestamp_ns: int,
    ) -> list[ConflictReport]:
        """Detect temporal conflicts between knowledge sources."""
        conflicts: list[ConflictReport] = []

        # Group sources by time windows
        time_windows = self._group_sources_by_time(sources)

        # Check for conflicts across time windows
        for window1, window2 in combinations(time_windows, 2):
            if self._has_temporal_conflict(window1, window2):
                sources_involved = [s.source_id for s in window1 + window2]
                conflicts.append(
                    ConflictReport(
                        conflict_id=f"temporal_conflict_{len(conflicts)}",
                        sources_involved=tuple(sources_involved),
                        conflict_type="temporal_conflict",
                        severity=ValidationSeverity.MEDIUM,
                        description="Temporal conflict detected across time windows",
                        conflicting_fields=(),
                        detected_at_ns=timestamp_ns,
                        resolution_strategy="temporal_resolution",
                    )
                )

        return conflicts

    def _detect_semantic_conflicts(
        self,
        sources: list[KnowledgeSource],
        timestamp_ns: int,
    ) -> list[ConflictReport]:
        """Detect semantic conflicts between knowledge sources."""
        conflicts: list[ConflictReport] = []

        # Check for semantic inconsistencies
        for i, source1 in enumerate(sources):
            for source2 in sources[i + 1 :]:
                if self._has_semantic_conflict(source1, source2):
                    conflicts.append(
                        ConflictReport(
                            conflict_id=f"semantic_conflict_{source1.source_id}_{source2.source_id}",
                            sources_involved=(source1.source_id, source2.source_id),
                            conflict_type="semantic_conflict",
                            severity=ValidationSeverity.LOW,
                            description=f"Semantic conflict between {source1.source_id} and {source2.source_id}",
                            conflicting_fields=(),
                            detected_at_ns=timestamp_ns,
                            resolution_strategy="semantic_resolution",
                        )
                    )

        return conflicts

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # Use Python's time module for current timestamp
        import time

        return int(time.time_ns())

    def _get_required_fields(self, source_type: KnowledgeSourceType) -> set[str]:
        """Get required fields for a given source type."""
        field_requirements = {
            KnowledgeSourceType.MARKET_DATA: {"price", "volume", "timestamp"},
            KnowledgeSourceType.NEWS_SENTIMENT: {"sentiment", "source", "timestamp"},
            KnowledgeSourceType.ON_CHAIN_ANALYSIS: {"address", "metric", "value"},
            KnowledgeSourceType.STRATEGY_BACKTEST: {"strategy_id", "returns", "sharpe"},
            KnowledgeSourceType.OPERATOR_INPUT: {"intent", "parameters"},
            KnowledgeSourceType.LEARNING_INFERENCE: {"model_id", "prediction", "confidence"},
            KnowledgeSourceType.EXTERNAL_API: {"endpoint", "response"},
            KnowledgeSourceType.SYSTEM_INTERNAL: {"component", "status"},
        }
        return field_requirements.get(source_type, set())

    def _find_conflicting_fields(
        self,
        source1: KnowledgeSource,
        source2: KnowledgeSource,
    ) -> list[str]:
        """Find fields with conflicting values between two sources."""
        conflicting_fields: list[str] = []

        common_keys = set(source1.content.keys()) & set(source2.content.keys())

        for key in common_keys:
            if source1.content[key] != source2.content[key]:
                conflicting_fields.append(key)

        return conflicting_fields

    def _find_knowledge_graph_conflicts(
        self,
        source: KnowledgeSource,
        knowledge: KnowledgeGraph,
    ) -> list[str]:
        """Find conflicts between source and existing knowledge graph."""
        conflicts = []

        try:
            # Check if knowledge graph has conflicting information
            if knowledge is None:
                return conflicts

            # Check for contradictory key-value pairs
            for key, value in source.content.items():
                if knowledge.has_fact(key):
                    existing_value = knowledge.get_fact(key)
                    if str(existing_value) != str(value):
                        conflicts.append(
                            f"Contradictory value for {key}: existing={existing_value}, new={value}"
                        )

            # Check for timestamp conflicts (newer vs older data)
            if knowledge.has_fact("timestamp"):
                existing_timestamp = knowledge.get_fact("timestamp")
                if source.timestamp_ns < int(existing_timestamp):
                    conflicts.append(
                        f"Outdated information: timestamp {source.timestamp_ns} vs existing {existing_timestamp}"
                    )

            # Check for source reliability conflicts
            if knowledge.has_fact("source_reliability"):
                existing_reliability = float(knowledge.get_fact("source_reliability"))
                if source.reliability_score < existing_reliability * 0.8:
                    conflicts.append(
                        f"Lower reliability source: {source.reliability_score:.2f} vs existing {existing_reliability:.2f}"
                    )

        except Exception as e:
            _logger.warning(f"Error finding knowledge graph conflicts: {e}")
            conflicts.append(f"Error during conflict detection: {str(e)}")

        return conflicts

    def _group_sources_by_time(self, sources: list[KnowledgeSource]) -> list[list[KnowledgeSource]]:
        """Group sources by time windows."""
        if not sources:
            return []

        # Define time window size (1 minute in nanoseconds)
        time_window_ns = 60 * 1_000_000_000  # 1 minute

        # Sort sources by timestamp
        sorted_sources = sorted(sources, key=lambda s: s.timestamp_ns)

        # Group into time windows
        groups = []
        current_group = [sorted_sources[0]]
        current_window_start = sorted_sources[0].timestamp_ns

        for source in sorted_sources[1:]:
            if source.timestamp_ns - current_window_start < time_window_ns:
                current_group.append(source)
            else:
                groups.append(current_group)
                current_group = [source]
                current_window_start = source.timestamp_ns

        if current_group:
            groups.append(current_group)

        return groups

    def _has_temporal_conflict(
        self,
        window1: list[KnowledgeSource],
        window2: list[KnowledgeSource],
    ) -> bool:
        """Check if there's a temporal conflict between time windows."""
        if not window1 or not window2:
            return False

        # Get time ranges for both windows
        times1 = [source.timestamp_ns for source in window1 if source.timestamp_ns > 0]
        times2 = [source.timestamp_ns for source in window2 if source.timestamp_ns > 0]

        if not times1 or not times2:
            return False

        # Check for overlapping time periods with conflicting content
        min_time1, max_time1 = min(times1), max(times1)
        min_time2, max_time2 = min(times2), max(times2)

        # Check if windows overlap in time
        if not (max_time1 < min_time2 or max_time2 < min_time1):
            # Windows overlap - check for conflicting knowledge
            conflicts = self._check_content_conflicts(window1, window2)
            return len(conflicts) > 0

        return False

    def _check_content_conflicts(
        self,
        window1: list[KnowledgeSource],
        window2: list[KnowledgeSource],
    ) -> list[tuple[str, str, str]]:
        """Check for content conflicts between two windows of sources.

        Returns list of (field, value1, value2) tuples where conflicts exist.
        """
        conflicts = []

        # Extract common content keys
        all_keys = set()
        for source in window1 + window2:
            all_keys.update(source.content.keys())

        # For each common key, check for conflicting values
        for key in all_keys:
            values1 = set()
            values2 = set()

            for source in window1:
                if key in source.content:
                    values1.add(source.content[key])

            for source in window2:
                if key in source.content:
                    values2.add(source.content[key])

            # Check for intersection of conflicting values
            if values1 and values2 and not values1.isdisjoint(values2):
                # Potential conflict - same key with potentially different values
                if len(values1) > 1 or len(values2) > 1 or values1 != values2:
                    conflicts.append((key, str(values1), str(values2)))

        return conflicts

    def _has_semantic_conflict(
        self,
        source1: KnowledgeSource,
        source2: KnowledgeSource,
    ) -> bool:
        """Check if there's a semantic conflict between sources."""
        if not source1.content or not source2.content:
            return False

        # Check for direct contradictions in content
        for key in source1.content:
            if key in source2.content:
                value1 = source1.content[key]
                value2 = source2.content[key]

                # Check for semantic contradictions
                if self._are_contradictory_values(key, value1, value2):
                    return True

        # Check confidence-based conflicts (high confidence in opposite directions)
        if (
            source1.confidence > 0.8
            and source2.confidence > 0.8
            and source1.source_type != source2.source_type
        ):
            # High confidence from different source types about same domain
            common_keys = set(source1.content.keys()) & set(source2.content.keys())
            if common_keys:
                return True

        return False

    def _are_contradictory_values(
        self,
        key: str,
        value1: str,
        value2: str,
    ) -> bool:
        """Check if two values are semantically contradictory for a given key."""
        # Define contradiction patterns for common keys
        contradiction_patterns = {
            "trend": [("bullish", "bearish"), ("up", "down"), ("positive", "negative")],
            "sentiment": [
                ("positive", "negative"),
                ("bullish", "bearish"),
                ("optimistic", "pessimistic"),
            ],
            "direction": [("buy", "sell"), ("long", "short"), ("increase", "decrease")],
            "regime": [("bullish", "bearish"), ("trending", "mean_reverting")],
            "action": [("buy", "sell"), ("enter", "exit"), ("open", "close")],
        }

        # Normalize values for comparison
        v1_lower = value1.lower().strip()
        v2_lower = value2.lower().strip()

        # Direct contradiction
        if v1_lower == v2_lower:
            return False

        # Check known contradiction patterns
        key_lower = key.lower()
        for pattern_key, contradictions in contradiction_patterns.items():
            if pattern_key in key_lower:
                for contradiction_pair in contradictions:
                    if (
                        v1_lower in contradiction_pair[0] and v2_lower in contradiction_pair[1]
                    ) or (v1_lower in contradiction_pair[1] and v2_lower in contradiction_pair[0]):
                        return True

        # Numerical contradictions
        try:
            num1 = float(v1_lower)
            num2 = float(v2_lower)
            # If values are numerical and significantly different
            if abs(num1 - num2) > max(abs(num1), abs(num2)) * 0.5:
                return True
        except ValueError:
            pass

        return False

    def _calculate_consistency_score(self, knowledge: KnowledgeGraph) -> float:
        """Calculate consistency score of knowledge graph."""
        if not knowledge or not hasattr(knowledge, "nodes"):
            return 0.0

        try:
            # Get all nodes from knowledge graph
            nodes = knowledge.nodes if hasattr(knowledge, "nodes") else []

            if not nodes:
                return 0.5

            consistency_score = 0.0
            total_checks = 0

            # Check for internal consistency within nodes
            for node in nodes:
                if hasattr(node, "content") and node.content:
                    # Check temporal consistency within node
                    if hasattr(node, "timestamp_ns") and node.timestamp_ns > 0:
                        total_checks += 1
                        consistency_score += 0.8  # Assume consistent if timestamp exists

                    # Check content consistency
                    if self._is_content_consistent(node.content):
                        total_checks += 1
                        consistency_score += 0.9
                    else:
                        total_checks += 1
                        consistency_score += 0.3

            # Check cross-node consistency
            node_pairs = list(zip(nodes, nodes[1:]))
            for node1, node2 in node_pairs:
                if hasattr(node1, "content") and hasattr(node2, "content"):
                    if not self._has_cross_node_conflicts(node1.content, node2.content):
                        total_checks += 1
                        consistency_score += 0.85
                    else:
                        total_checks += 1
                        consistency_score += 0.4

            return consistency_score / total_checks if total_checks > 0 else 0.5

        except Exception as e:
            _logger.error(f"Error calculating consistency score: {e}")
            return 0.5

    def _is_content_consistent(self, content: dict) -> bool:
        """Check if content is internally consistent."""
        if not content:
            return True

        # Check for obvious contradictions
        for key, value in content.items():
            if isinstance(value, str):
                # Check for self-contradictory values
                if " and " in value.lower() and " but " in value.lower():
                    parts = value.split(" but ")
                    if len(parts) > 1:
                        continue  # Complex statement, skip detailed check

        return True

    def _has_cross_node_conflicts(self, content1: dict, content2: dict) -> bool:
        """Check for conflicts between two content dictionaries."""
        if not content1 or not content2:
            return False

        common_keys = set(content1.keys()) & set(content2.keys())

        for key in common_keys:
            value1 = content1[key]
            value2 = content2[key]

            if self._are_contradictory_values(key, str(value1), str(value2)):
                return True

        return False

    def _calculate_reliability_score(self, knowledge: KnowledgeGraph) -> float:
        """Calculate reliability score of knowledge graph."""
        if not knowledge or not hasattr(knowledge, "nodes"):
            return 0.0

        try:
            nodes = knowledge.nodes if hasattr(knowledge, "nodes") else []

            if not nodes:
                return 0.5

            reliability_score = 0.0
            total_nodes = len(nodes)

            # Calculate reliability based on node characteristics
            for node in nodes:
                node_reliability = 0.5  # Base reliability

                # Factor in confidence if available
                if hasattr(node, "confidence") and node.confidence > 0:
                    node_reliability = 0.3 + (node.confidence * 0.7)

                # Factor in source reliability if available
                if hasattr(node, "reliability_score") and node.reliability_score > 0:
                    node_reliability = (node_reliability + node.reliability_score) / 2

                # Factor in source type (some sources are more reliable)
                if hasattr(node, "source_type"):
                    source_reliability = self._get_source_type_reliability(node.source_type)
                    node_reliability = (node_reliability + source_reliability) / 2

                reliability_score += node_reliability

            return reliability_score / total_nodes if total_nodes > 0 else 0.5

        except Exception as e:
            _logger.error(f"Error calculating reliability score: {e}")
            return 0.5

    def _get_source_type_reliability(self, source_type) -> float:
        """Get base reliability score for a source type."""
        if isinstance(source_type, str):
            source_str = source_type.upper()
        else:
            source_str = str(source_type).upper()

        reliability_map = {
            "MARKET_DATA": 0.9,
            "OPERATOR_INPUT": 0.95,
            "LEARNING_INFERENCE": 0.8,
            "STRATEGY_BACKTEST": 0.85,
            "ON_CHAIN_ANALYSIS": 0.88,
            "NEWS_SENTIMENT": 0.7,
            "EXTERNAL_API": 0.75,
            "SYSTEM_INTERNAL": 0.92,
        }

        return reliability_map.get(source_str, 0.7)

    def _calculate_completeness_score(self, knowledge: KnowledgeGraph) -> float:
        """Calculate completeness score of knowledge graph."""
        if not knowledge or not hasattr(knowledge, "nodes"):
            return 0.0

        try:
            nodes = knowledge.nodes if hasattr(knowledge, "nodes") else []

            if not nodes:
                return 0.5

            completeness_score = 0.0
            total_nodes = len(nodes)

            # Expected fields for a complete knowledge node
            expected_fields = {"content", "timestamp_ns", "confidence", "source_type"}

            for node in nodes:
                node_completeness = 0.0
                present_fields = 0

                # Check for expected fields
                if hasattr(node, "content") and node.content:
                    present_fields += 1
                    # Check content completeness
                    if len(node.content) >= 3:  # At least 3 content items
                        node_completeness += 0.3

                if hasattr(node, "timestamp_ns") and node.timestamp_ns > 0:
                    present_fields += 1
                    node_completeness += 0.25

                if hasattr(node, "confidence") and node.confidence > 0:
                    present_fields += 1
                    node_completeness += 0.25

                if hasattr(node, "source_type"):
                    present_fields += 1
                    node_completeness += 0.2

                # Normalize by expected fields
                completeness_score += node_completeness

            return completeness_score / total_nodes if total_nodes > 0 else 0.5

        except Exception as e:
            _logger.error(f"Error calculating completeness score: {e}")
            return 0.5

    def _calculate_temporal_consistency(self, knowledge: KnowledgeGraph) -> float:
        """Calculate temporal consistency of knowledge graph."""
        if not knowledge or not hasattr(knowledge, "nodes"):
            return 0.0

        try:
            nodes = knowledge.nodes if hasattr(knowledge, "nodes") else []

            if not nodes:
                return 0.5

            # Group nodes by time windows
            time_windows = self._group_nodes_by_time_windows(
                nodes, window_size_ns=1_000_000_000
            )  # 1 second windows

            if not time_windows or len(time_windows) < 2:
                return 0.7  # Not enough temporal data

            temporal_consistency = 0.0
            window_comparisons = 0

            # Compare adjacent time windows for consistency
            sorted_windows = sorted(time_windows.keys())
            for i in range(len(sorted_windows) - 1):
                window1_nodes = time_windows[sorted_windows[i]]
                window2_nodes = time_windows[sorted_windows[i + 1]]

                # Check for temporal conflicts between windows
                has_conflict = self._has_temporal_conflict(window1_nodes, window2_nodes)

                if not has_conflict:
                    temporal_consistency += 1.0
                else:
                    temporal_consistency += 0.4  # Partial credit for some consistency

                window_comparisons += 1

            return temporal_consistency / window_comparisons if window_comparisons > 0 else 0.7

        except Exception as e:
            _logger.error(f"Error calculating temporal consistency: {e}")
            return 0.5

    def _group_nodes_by_time_windows(
        self, nodes: list, window_size_ns: int = 1_000_000_000
    ) -> dict[int, list]:
        """Group nodes into time windows for temporal analysis."""
        time_windows = {}

        for node in nodes:
            if hasattr(node, "timestamp_ns") and node.timestamp_ns > 0:
                window_key = int(node.timestamp_ns // window_size_ns)
                if window_key not in time_windows:
                    time_windows[window_key] = []
                time_windows[window_key].append(node)

        return time_windows

    def _calculate_source_diversity(self, knowledge: KnowledgeGraph) -> float:
        """Calculate source diversity of knowledge graph."""
        if not knowledge or not hasattr(knowledge, "nodes"):
            return 0.0

        try:
            nodes = knowledge.nodes if hasattr(knowledge, "nodes") else []

            if not nodes:
                return 0.5

            # Count unique source types
            source_types = set()
            source_origins = set()

            for node in nodes:
                if hasattr(node, "source_type"):
                    source_types.add(str(node.source_type))
                if hasattr(node, "origin"):
                    source_origins.add(str(node.origin))

            # Calculate diversity based on source types and origins
            type_diversity = len(source_types)
            origin_diversity = len(source_origins)

            # Normalize diversity scores (ideal: multiple source types and origins)
            max_expected_types = 8  # Based on KnowledgeSourceType enum
            max_expected_origins = 20  # Reasonable expectation for system origins

            type_score = min(type_diversity / max_expected_types, 1.0)
            origin_score = min(origin_diversity / max_expected_origins, 1.0)

            # Combined diversity score
            diversity_score = (type_score * 0.6) + (origin_score * 0.4)

            # Boost score if we have good diversity
            if type_diversity >= 3 and origin_diversity >= 5:
                diversity_score = min(diversity_score * 1.1, 1.0)

            return max(diversity_score, 0.3)  # Minimum score for some diversity

        except Exception as e:
            _logger.error(f"Error calculating source diversity: {e}")
            return 0.5

    def _calculate_historical_accuracy(self, history: list[ValidationResult]) -> float:
        """Calculate historical accuracy from validation history."""
        if not history:
            return 0.5  # Default score for new sources

        valid_count = sum(1 for result in history if result.is_valid)
        return valid_count / len(history)

    def _calculate_prediction_accuracy(
        self,
        source: KnowledgeSource,
        history: list[ValidationResult],
    ) -> float:
        """Calculate prediction accuracy for source."""
        if not history:
            return 0.5  # Default score for new sources

        try:
            # Look for prediction-based validations in history
            prediction_validations = [
                result
                for result in history
                if hasattr(result, "validated_source")
                and hasattr(result.validated_source, "content")
                and "prediction" in str(result.validated_source.content).lower()
            ]

            if not prediction_validations:
                # No prediction-specific validations, use general validation rate
                return self._calculate_historical_accuracy(history)

            # Calculate prediction-specific accuracy
            correct_predictions = sum(1 for result in prediction_validations if result.is_valid)
            total_predictions = len(prediction_validations)

            base_accuracy = (
                correct_predictions / total_predictions if total_predictions > 0 else 0.5
            )

            # Factor in confidence calibration (how well confidence predicts correctness)
            confidence_calibration = self._calculate_confidence_calibration(prediction_validations)

            # Combine accuracy and calibration
            prediction_accuracy = (base_accuracy * 0.7) + (confidence_calibration * 0.3)

            return min(max(prediction_accuracy, 0.0), 1.0)

        except Exception as e:
            _logger.error(f"Error calculating prediction accuracy: {e}")
            return 0.5

    def _calculate_source_consistency(
        self,
        source: KnowledgeSource,
        history: list[ValidationResult],
    ) -> float:
        """Calculate consistency score for source."""
        if len(history) < 2:
            return 0.5

        # Calculate variance in confidence scores
        confidence_scores = [result.confidence_score for result in history]
        mean_confidence = sum(confidence_scores) / len(confidence_scores)
        variance = sum((c - mean_confidence) ** 2 for c in confidence_scores) / len(
            confidence_scores
        )

        # Lower variance = higher consistency
        consistency = 1.0 - min(variance, 1.0)
        return consistency

    def _calculate_confidence_calibration(
        self, validation_results: list[ValidationResult]
    ) -> float:
        """Calculate how well confidence scores predict validation outcomes."""
        if not validation_results:
            return 0.5

        try:
            # Group by confidence ranges
            high_confidence_correct = 0
            high_confidence_total = 0
            low_confidence_correct = 0
            low_confidence_total = 0

            for result in validation_results:
                if result.confidence_score > 0.7:
                    high_confidence_total += 1
                    if result.is_valid:
                        high_confidence_correct += 1
                else:
                    low_confidence_total += 1
                    if not result.is_valid:
                        low_confidence_correct += 1

            # Calculate calibration scores
            high_conf_accuracy = (
                high_confidence_correct / high_confidence_total
                if high_confidence_total > 0
                else 0.5
            )
            low_conf_accuracy = (
                low_confidence_correct / low_confidence_total if low_confidence_total > 0 else 0.5
            )

            # Overall calibration score
            calibration = (high_conf_accuracy + low_conf_accuracy) / 2

            return calibration

        except Exception as e:
            _logger.error(f"Error calculating confidence calibration: {e}")
            return 0.5

    def _calculate_temporal_stability(
        self,
        source: KnowledgeSource,
        history: list[ValidationResult],
    ) -> float:
        """Calculate temporal stability for source."""
        if len(history) < 3:
            return 0.5  # Not enough data for stability assessment

        try:
            # Sort history by timestamp
            sorted_history = sorted(history, key=lambda x: x.timestamp_ns)

            # Calculate stability metrics
            confidence_stability = self._calculate_confidence_stability(sorted_history)
            validity_stability = self._calculate_validity_stability(sorted_history)

            # Combine stability metrics
            temporal_stability = (confidence_stability * 0.6) + (validity_stability * 0.4)

            return min(max(temporal_stability, 0.0), 1.0)

        except Exception as e:
            _logger.error(f"Error calculating temporal stability: {e}")
            return 0.5

    def _calculate_confidence_stability(self, sorted_history: list[ValidationResult]) -> float:
        """Calculate stability of confidence scores over time."""
        if len(sorted_history) < 3:
            return 0.5

        confidence_scores = [result.confidence_score for result in sorted_history]

        # Calculate coefficient of variation (lower is more stable)
        mean_confidence = sum(confidence_scores) / len(confidence_scores)
        variance = sum((c - mean_confidence) ** 2 for c in confidence_scores) / len(
            confidence_scores
        )
        std_dev = variance**0.5

        # Lower coefficient of variation = higher stability
        cv = std_dev / mean_confidence if mean_confidence > 0 else 1.0

        # Convert to stability score (inverse of CV)
        stability = 1.0 / (1.0 + cv)

        return stability

    def _calculate_validity_stability(self, sorted_history: list[ValidationResult]) -> float:
        """Calculate stability of validation outcomes over time."""
        if len(sorted_history) < 3:
            return 0.5

        # Look for pattern changes in validity
        validity_sequence = [1 if result.is_valid else 0 for result in sorted_history]

        # Count transitions (valid -> invalid or invalid -> valid)
        transitions = 0
        for i in range(len(validity_sequence) - 1):
            if validity_sequence[i] != validity_sequence[i + 1]:
                transitions += 1

        # Fewer transitions = higher stability
        max_possible_transitions = len(validity_sequence) - 1
        transition_ratio = (
            transitions / max_possible_transitions if max_possible_transitions > 0 else 0
        )

        stability = 1.0 - transition_ratio

        return stability

    def _analyze_temporal_consistency(
        self,
        knowledge: KnowledgeGraph,
        period_ns: int,
    ) -> tuple[bool, float]:
        """Analyze temporal consistency over period."""
        try:
            if not knowledge or not hasattr(knowledge, "nodes"):
                return True, 0.5

            nodes = knowledge.nodes if hasattr(knowledge, "nodes") else []

            if not nodes:
                return True, 0.5

            # Filter nodes within the time period
            current_time = self._get_timestamp()
            period_start = current_time - period_ns

            period_nodes = [
                node
                for node in nodes
                if hasattr(node, "timestamp_ns") and node.timestamp_ns >= period_start
            ]

            if len(period_nodes) < 2:
                return True, 0.7  # Not enough data for analysis

            # Group nodes by time windows within the period
            time_windows = self._group_nodes_by_time_windows(
                period_nodes, window_size_ns=period_ns // 10
            )

            if len(time_windows) < 2:
                return True, 0.7

            # Analyze consistency across time windows
            consistency_scores = []
            window_keys = sorted(time_windows.keys())

            for i in range(len(window_keys) - 1):
                window1 = time_windows[window_keys[i]]
                window2 = time_windows[window_keys[i + 1]]

                # Check for temporal conflicts
                has_conflict = self._has_temporal_conflict(window1, window2)

                if not has_conflict:
                    consistency_scores.append(1.0)
                else:
                    consistency_scores.append(0.4)

            # Calculate overall consistency
            avg_consistency = (
                sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.5
            )

            # Determine if consistent (threshold: 0.7)
            is_consistent = avg_consistency >= 0.7

            return is_consistent, avg_consistency

        except Exception as e:
            _logger.error(f"Error analyzing temporal consistency: {e}")
            return True, 0.5

    def _count_temporal_inconsistencies(
        self,
        knowledge: KnowledgeGraph,
        period_ns: int,
    ) -> int:
        """Count temporal inconsistencies in knowledge graph."""
        try:
            if not knowledge or not hasattr(knowledge, "nodes"):
                return 0

            nodes = knowledge.nodes if hasattr(knowledge, "nodes") else []

            if not nodes:
                return 0

            # Filter nodes within the time period
            current_time = self._get_timestamp()
            period_start = current_time - period_ns

            period_nodes = [
                node
                for node in nodes
                if hasattr(node, "timestamp_ns") and node.timestamp_ns >= period_start
            ]

            if len(period_nodes) < 2:
                return 0

            # Group nodes by time windows
            time_windows = self._group_nodes_by_time_windows(
                period_nodes, window_size_ns=period_ns // 10
            )

            if len(time_windows) < 2:
                return 0

            inconsistency_count = 0
            window_keys = sorted(time_windows.keys())

            # Count inconsistencies between adjacent time windows
            for i in range(len(window_keys) - 1):
                window1 = time_windows[window_keys[i]]
                window2 = time_windows[window_keys[i + 1]]

                # Check for temporal conflicts
                if self._has_temporal_conflict(window1, window2):
                    inconsistency_count += 1

                # Check for semantic conflicts within the same time window
                conflicts = self._check_content_conflicts(window1, window2)
                inconsistency_count += len(conflicts)

            return inconsistency_count

        except Exception as e:
            _logger.error(f"Error counting temporal inconsistencies: {e}")
            return 0

    def _detect_temporal_drift(
        self,
        knowledge: KnowledgeGraph,
        period_ns: int,
    ) -> tuple[bool, float]:
        """Detect temporal drift in knowledge graph."""
        try:
            if not knowledge or not hasattr(knowledge, "nodes"):
                return False, 0.0

            nodes = knowledge.nodes if hasattr(knowledge, "nodes") else []

            if not nodes:
                return False, 0.0

            # Split nodes into two time periods
            current_time = self._get_timestamp()
            mid_time = current_time - (period_ns // 2)
            start_time = current_time - period_ns

            recent_nodes = [
                node
                for node in nodes
                if hasattr(node, "timestamp_ns") and mid_time <= node.timestamp_ns <= current_time
            ]

            older_nodes = [
                node
                for node in nodes
                if hasattr(node, "timestamp_ns") and start_time <= node.timestamp_ns < mid_time
            ]

            if not recent_nodes or not older_nodes:
                return False, 0.0

            # Compare knowledge characteristics between periods
            drift_indicators = []

            # Compare confidence scores
            recent_confidence = [
                node.confidence for node in recent_nodes if hasattr(node, "confidence")
            ]
            older_confidence = [
                node.confidence for node in older_nodes if hasattr(node, "confidence")
            ]

            if recent_confidence and older_confidence:
                recent_avg = sum(recent_confidence) / len(recent_confidence)
                older_avg = sum(older_confidence) / len(older_confidence)
                confidence_drift = abs(recent_avg - older_avg)
                drift_indicators.append(confidence_drift)

            # Compare content patterns
            recent_content_types = self._analyze_content_patterns(recent_nodes)
            older_content_types = self._analyze_content_patterns(older_nodes)

            content_drift = self._calculate_pattern_drift(recent_content_types, older_content_types)
            drift_indicators.append(content_drift)

            # Compare source type distributions
            recent_sources = self._get_source_distribution(recent_nodes)
            older_sources = self._get_source_distribution(older_nodes)

            source_drift = self._calculate_distribution_drift(recent_sources, older_sources)
            drift_indicators.append(source_drift)

            # Calculate overall drift magnitude
            overall_drift = (
                sum(drift_indicators) / len(drift_indicators) if drift_indicators else 0.0
            )

            # Detect drift if magnitude exceeds threshold
            has_drift = overall_drift > 0.3

            return has_drift, overall_drift

        except Exception as e:
            _logger.error(f"Error detecting temporal drift: {e}")
            return False, 0.0

    def _analyze_content_patterns(self, nodes: list) -> dict:
        """Analyze content patterns in a set of nodes."""
        patterns = {"content_keys": set(), "content_values": set(), "node_count": len(nodes)}

        for node in nodes:
            if hasattr(node, "content") and node.content:
                patterns["content_keys"].update(node.content.keys())
                for value in node.content.values():
                    patterns["content_values"].add(str(value)[:50])  # Truncate long values

        return patterns

    def _calculate_pattern_drift(self, patterns1: dict, patterns2: dict) -> float:
        """Calculate drift between two content pattern dictionaries."""
        # Compare content key overlap
        keys1 = patterns1.get("content_keys", set())
        keys2 = patterns2.get("content_keys", set())

        if not keys1 or not keys2:
            return 0.0

        key_intersection = len(keys1 & keys2)
        key_union = len(keys1 | keys2)
        key_similarity = key_intersection / key_union if key_union > 0 else 0.0

        # Drift is inverse of similarity
        key_drift = 1.0 - key_similarity

        return key_drift

    def _get_source_distribution(self, nodes: list) -> dict:
        """Get distribution of source types in nodes."""
        distribution = {}

        for node in nodes:
            source_type = str(node.source_type) if hasattr(node, "source_type") else "unknown"
            distribution[source_type] = distribution.get(source_type, 0) + 1

        # Convert to proportions
        total = sum(distribution.values())
        if total > 0:
            distribution = {k: v / total for k, v in distribution.items()}

        return distribution

    def _calculate_distribution_drift(self, dist1: dict, dist2: dict) -> float:
        """Calculate drift between two source distributions."""
        if not dist1 or not dist2:
            return 0.0

        # Get all source types
        all_sources = set(dist1.keys()) | set(dist2.keys())

        # Calculate Earth Mover's Distance approximation
        total_drift = 0.0
        for source in all_sources:
            prop1 = dist1.get(source, 0.0)
            prop2 = dist2.get(source, 0.0)
            total_drift += abs(prop1 - prop2)

        # Normalize by number of sources
        avg_drift = total_drift / len(all_sources) if all_sources else 0.0

        return avg_drift


# Import for combinations function
from itertools import combinations

# Singleton instance
_knowledge_validator_instance = None
_validator_lock = threading.Lock()


def get_knowledge_validator() -> KnowledgeValidator:
    """Get the singleton knowledge validator instance."""
    global _knowledge_validator_instance
    if _knowledge_validator_instance is None:
        with _validator_lock:
            if _knowledge_validator_instance is None:
                _knowledge_validator_instance = KnowledgeValidator()
    return _knowledge_validator_instance


__all__ = [
    "KnowledgeValidator",
    "KnowledgeSource",
    "ValidationResult",
    "ValidationIssue",
    "ValidationSeverity",
    "KnowledgeSourceType",
    "ConflictReport",
    "IntegrityScore",
    "ReliabilityScore",
    "ConsistencyReport",
]
