"""M-1 Knowledge Layer - Source Conflict Graph.

Tracks and resolves conflicts between knowledge sources.
Provides sophisticated conflict resolution and consensus mechanisms.

Design Principles:
- INV-15: No external dependencies, no IO, no clock
- INV-08: Pure data surface, no engine imports
- Frozen dataclasses for structural hashing
- Thread-safe conflict tracking and resolution
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections import defaultdict
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from intelligence_engine.knowledge.knowledge_validator import (
        KnowledgeSource,
        ValidationResult,
        ConflictReport,
        ValidationSeverity,
    )

# Import ValidationSeverity for runtime use
from intelligence_engine.knowledge.knowledge_validator import ValidationSeverity

_logger = logging.getLogger(__name__)


class ConflictType(str, enum.Enum):
    """Types of conflicts between knowledge sources."""

    DIRECT_CONTENT = "DIRECT_CONTENT"  # Direct value conflicts
    TEMPORAL = "TEMPORAL"  # Time-based conflicts
    SEMANTIC = "SEMANTIC"  # Semantic inconsistencies
    LOGICAL = "LOGICAL"  # Logical contradictions
    ONTOLOGICAL = "ONTOLOGICAL"  # Ontology mismatches
    SOURCE_RELIABILITY = "SOURCE_RELIABILITY"  # Reliability-based conflicts


class ResolutionStrategyType(str, enum.Enum):
    """Strategies for resolving conflicts."""

    MERGE = "MERGE"  # Merge conflicting values
    PRIORITIZE = "PRIORITIZE"  # Prioritize based on reliability/confidence
    CONSENSUS = "CONSENSUS"  # Use consensus mechanism
    DEFER = "DEFER"  # Defer to human operator
    SPLIT = "SPLIT"  # Create separate knowledge branches
    REJECT_ALL = "REJECT_ALL"  # Reject all conflicting sources


class ConsensusMechanism(str, enum.Enum):
    """Mechanisms for achieving consensus."""

    MAJORITY_VOTE = "MAJORITY_VOTE"  # Simple majority
    WEIGHTED_VOTE = "WEIGHTED_VOTE"  # Weighted by reliability
    EXPERT_PANEL = "EXPERT_PANEL"  # Expert source prioritization
    TEMPORAL_PRIORITY = "TEMPORAL_PRIORITY"  # Most recent wins
    SOURCE_HIERARCHY = "SOURCE_HIERARCHY"  # Source type hierarchy


@dataclasses.dataclass(frozen=True, slots=True)
class ConflictNode:
    """A node in the conflict graph representing a knowledge source."""

    source_id: str
    confidence_score: float
    reliability_score: float
    source_type: str
    conflict_count: int
    timestamp_ns: int


@dataclasses.dataclass(frozen=True, slots=True)
class ConflictEdge:
    """An edge in the conflict graph representing a conflict relationship."""

    from_source: str
    to_source: str
    conflict_type: ConflictType
    severity: ValidationSeverity
    conflicting_fields: tuple[str, ...]
    weight: float  # Edge weight based on severity and reliability


@dataclasses.dataclass(frozen=True, slots=True)
class ConflictGraph:
    """Graph structure representing conflicts between knowledge sources.

    The conflict graph is a directed graph where nodes represent knowledge sources
    and edges represent conflicts between them. The graph enables sophisticated
    conflict analysis and resolution strategies.
    """

    nodes: Mapping[str, ConflictNode] = dataclasses.field(
        default_factory=lambda: MappingProxyType({})
    )
    edges: tuple[ConflictEdge, ...] = ()
    graph_id: str = ""
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.nodes, MappingProxyType):
            object.__setattr__(self, "nodes", MappingProxyType(dict(self.nodes)))


@dataclasses.dataclass(frozen=True, slots=True)
class ResolutionStrategy:
    """A strategy for resolving a specific conflict."""

    strategy_id: str
    conflict_id: str
    strategy_type: ResolutionStrategyType
    parameters: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    expected_outcome: str = ""
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.parameters, MappingProxyType):
            object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))


@dataclasses.dataclass(frozen=True, slots=True)
class PropagationMap:
    """Map of conflict propagation through the knowledge graph."""

    propagation_id: str
    source_conflict: str
    affected_nodes: tuple[str, ...]
    propagation_path: tuple[str, ...]
    impact_severity: ValidationSeverity
    cascade_potential: float
    timestamp_ns: int


@dataclasses.dataclass(frozen=True, slots=True)
class ConsensusResult:
    """Result of consensus mechanism on conflicting sources."""

    consensus_id: str
    conflict_id: str
    agreed_value: str | None
    participating_sources: tuple[str, ...]
    agreement_level: float  # 0.0-1.0
    mechanism_used: ConsensusMechanism
    timestamp_ns: int


class SourceConflictGraph:
    """Builds and manages conflict graphs between knowledge sources.

    This component enables sophisticated conflict analysis, resolution,
    and propagation tracking for the M-1 Knowledge Layer.
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._conflict_graphs: dict[str, ConflictGraph] = {}
        self._resolution_strategies: dict[str, ResolutionStrategy] = {}
        self._total_conflicts_resolved: int = 0
        self._consensus_history: dict[str, list[ConsensusResult]] = {}

    def build_conflict_graph(
        self,
        sources: list[KnowledgeSource],
        validation_results: list[ValidationResult],
    ) -> ConflictGraph:
        """Build a conflict graph from knowledge sources and validation results.

        Args:
            sources: List of knowledge sources
            validation_results: Validation results for each source

        Returns:
            ConflictGraph representing conflicts between sources
        """
        # Create conflict nodes
        nodes = self._create_conflict_nodes(sources, validation_results)

        # Create conflict edges
        edges = self._create_conflict_edges(sources, validation_results)

        # Generate graph ID
        graph_id = self._generate_graph_id(sources)

        # Create conflict graph
        graph = ConflictGraph(
            nodes=MappingProxyType(nodes),
            edges=tuple(edges),
            graph_id=graph_id,
            timestamp_ns=self._get_timestamp(),
        )

        # Store the graph
        with self._lock:
            self._conflict_graphs[graph_id] = graph

        _logger.info(
            "Built conflict graph %s with %d nodes and %d edges",
            graph_id,
            len(nodes),
            len(edges),
        )

        return graph

    def resolve_conflicts(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
        strategy: ResolutionStrategy | None = None,
    ) -> ResolutionStrategy:
        """Resolve a specific conflict using appropriate strategy.

        Args:
            conflict: Conflict report to resolve
            graph: Conflict graph containing the conflict
            strategy: Optional resolution strategy (auto-determined if None)

        Returns:
            ResolutionStrategy with resolution details
        """
        # Auto-determine strategy if not provided
        if strategy is None:
            strategy = self._determine_resolution_strategy(conflict, graph)

        # Execute resolution strategy
        resolved_strategy = self._execute_resolution_strategy(conflict, graph, strategy)

        # Store resolution strategy
        with self._lock:
            self._resolution_strategies[strategy.strategy_id] = resolved_strategy
            self._total_conflicts_resolved += 1

        _logger.info(
            "Resolved conflict %s using strategy %s",
            conflict.conflict_id,
            strategy.strategy_type,
        )

        return resolved_strategy

    def conflict_propagation_analysis(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
    ) -> PropagationMap:
        """Analyze how a conflict might propagate through the knowledge graph.

        Args:
            conflict: Conflict to analyze for propagation
            graph: Conflict graph to analyze

        Returns:
            PropagationMap with propagation analysis
        """
        # Identify affected nodes
        affected_nodes = self._identify_affected_nodes(conflict, graph)

        # Determine propagation path
        propagation_path = self._determine_propagation_path(conflict, graph, affected_nodes)

        # Calculate impact severity
        impact_severity = self._calculate_impact_severity(conflict, graph, affected_nodes)

        # Calculate cascade potential
        cascade_potential = self._calculate_cascade_potential(graph, affected_nodes)

        return PropagationMap(
            propagation_id=f"prop_{conflict.conflict_id}",
            source_conflict=conflict.conflict_id,
            affected_nodes=tuple(affected_nodes),
            propagation_path=tuple(propagation_path),
            impact_severity=impact_severity,
            cascade_potential=cascade_potential,
            timestamp_ns=self._get_timestamp(),
        )

    def consensus_mechanism(
        self,
        conflicts: list[ConflictReport],
        graph: ConflictGraph,
        mechanism: ConsensusMechanism = ConsensusMechanism.WEIGHTED_VOTE,
    ) -> ConsensusResult:
        """Apply consensus mechanism to resolve multiple conflicts.

        Args:
            conflicts: List of conflicts to resolve via consensus
            graph: Conflict graph containing the conflicts
            mechanism: Consensus mechanism to use

        Returns:
            ConsensusResult with consensus details
        """
        # Gather all involved sources
        involved_sources = self._gather_involved_sources(conflicts)

        # Apply consensus mechanism
        consensus_result = self._apply_consensus_mechanism(
            conflicts, graph, involved_sources, mechanism
        )

        # Store consensus result
        with self._lock:
            self._consensus_history.setdefault(consensus_result.consensus_id, []).append(
                consensus_result
            )

        _logger.info(
            "Applied consensus mechanism %s for %d conflicts, agreement level: %.2f",
            mechanism,
            len(conflicts),
            consensus_result.agreement_level,
        )

        return consensus_result

    def get_conflict_graph(self, graph_id: str) -> ConflictGraph | None:
        """Retrieve a conflict graph by ID."""
        with self._lock:
            return self._conflict_graphs.get(graph_id)

    def get_all_conflict_graphs(self) -> list[ConflictGraph]:
        """Retrieve all conflict graphs."""
        with self._lock:
            return list(self._conflict_graphs.values())

    def get_conflict_statistics(self) -> dict[str, int]:
        """Get statistics about conflict resolution."""
        with self._lock:
            return {
                "total_graphs": len(self._conflict_graphs),
                "total_resolutions": self._total_conflicts_resolved,
                "total_consensus_decisions": sum(len(h) for h in self._consensus_history.values()),
            }

    # ------------------------------------------------------------------
    # Private methods for conflict graph construction
    # ------------------------------------------------------------------

    def _create_conflict_nodes(
        self,
        sources: list[KnowledgeSource],
        validation_results: list[ValidationResult],
    ) -> dict[str, ConflictNode]:
        """Create conflict nodes from knowledge sources."""
        nodes: dict[str, ConflictNode] = {}

        for source, validation in zip(sources, validation_results):
            conflict_count = sum(
                1 for issue in validation.issues if issue.severity in ("HIGH", "CRITICAL")
            )

            node = ConflictNode(
                source_id=source.source_id,
                confidence_score=validation.confidence_score,
                reliability_score=source.reliability_score,
                source_type=source.source_type.value,
                conflict_count=conflict_count,
                timestamp_ns=source.timestamp_ns,
            )

            nodes[source.source_id] = node

        return nodes

    def _create_conflict_edges(
        self,
        sources: list[KnowledgeSource],
        validation_results: list[ValidationResult],
    ) -> list[ConflictEdge]:
        """Create conflict edges between sources."""
        edges: list[ConflictEdge] = []

        for i, (source1, validation1) in enumerate(zip(sources, validation_results)):
            for source2, validation2 in zip(sources[i + 1 :], validation_results[i + 1 :]):
                # Check for conflicts
                conflict_type, severity, conflicting_fields = self._detect_conflict_type(
                    source1, source2, validation1, validation2
                )

                if conflict_type is not None:
                    # Calculate edge weight
                    weight = self._calculate_edge_weight(severity, validation1, validation2)

                    edge = ConflictEdge(
                        from_source=source1.source_id,
                        to_source=source2.source_id,
                        conflict_type=conflict_type,
                        severity=severity,
                        conflicting_fields=tuple(conflicting_fields),
                        weight=weight,
                    )

                    edges.append(edge)

        return edges

    def _detect_conflict_type(
        self,
        source1: KnowledgeSource,
        source2: KnowledgeSource,
        validation1: ValidationResult,
        validation2: ValidationResult,
    ) -> tuple[ConflictType | None, ValidationSeverity, list[str]]:
        """Detect type and severity of conflict between two sources."""
        # Check for direct content conflicts
        conflicting_fields = self._find_conflicting_fields(source1, source2)
        if conflicting_fields:
            return ConflictType.DIRECT_CONTENT, ValidationSeverity.HIGH, conflicting_fields

        # Check for temporal conflicts
        if self._has_temporal_conflict(source1, source2):
            return ConflictType.TEMPORAL, ValidationSeverity.MEDIUM, []

        # Check for semantic conflicts
        if self._has_semantic_conflict(source1, source2):
            return ConflictType.SEMANTIC, ValidationSeverity.LOW, []

        # Check for reliability-based conflicts
        if self._has_reliability_conflict(source1, source2):
            return ConflictType.SOURCE_RELIABILITY, ValidationSeverity.MEDIUM, []

        return None, ValidationSeverity.INFO, []

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

    def _has_temporal_conflict(
        self,
        source1: KnowledgeSource,
        source2: KnowledgeSource,
    ) -> bool:
        """Check if there's a temporal conflict between sources."""
        # Check if sources have conflicting temporal information
        time1 = source1.content.get("timestamp")
        time2 = source2.content.get("timestamp")

        if time1 and time2 and time1 != time2:
            return True

        return False

    def _has_semantic_conflict(
        self,
        source1: KnowledgeSource,
        source2: KnowledgeSource,
    ) -> bool:
        """Check if there's a semantic conflict between sources."""
        # TODO: Implement sophisticated semantic conflict detection
        return False

    def _has_reliability_conflict(
        self,
        source1: KnowledgeSource,
        source2: KnowledgeSource,
    ) -> bool:
        """Check if there's a reliability-based conflict."""
        # Check if reliability scores differ significantly
        reliability_diff = abs(source1.reliability_score - source2.reliability_score)

        if reliability_diff > 0.3:  # Significant difference threshold
            return True

        return False

    def _calculate_edge_weight(
        self,
        severity: ValidationSeverity,
        validation1: ValidationResult,
        validation2: ValidationResult,
    ) -> float:
        """Calculate edge weight based on severity and validation scores."""
        severity_weights = {
            ValidationSeverity.CRITICAL: 1.0,
            ValidationSeverity.HIGH: 0.8,
            ValidationSeverity.MEDIUM: 0.5,
            ValidationSeverity.LOW: 0.3,
            ValidationSeverity.INFO: 0.1,
        }

        base_weight = severity_weights.get(severity, 0.5)

        # Adjust based on confidence scores
        confidence_factor = (validation1.confidence_score + validation2.confidence_score) / 2

        final_weight = base_weight * confidence_factor
        return max(0.0, min(1.0, final_weight))

    def _generate_graph_id(self, sources: list[KnowledgeSource]) -> str:
        """Generate unique graph ID from sources."""
        source_ids = sorted(s.source_id for s in sources)
        return f"conflict_graph_{'_'.join(source_ids)}"

    # ------------------------------------------------------------------
    # Private methods for conflict resolution
    # ------------------------------------------------------------------

    def _determine_resolution_strategy(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
    ) -> ResolutionStrategy:
        """Determine the best resolution strategy for a conflict."""
        # Analyze conflict characteristics
        severity = conflict.severity
        conflict_type = conflict.conflict_type
        num_sources = len(conflict.sources_involved)

        # Determine strategy based on characteristics
        if severity == ValidationSeverity.CRITICAL:
            strategy_type = ResolutionStrategyType.DEFER  # Defer critical conflicts to operator
        elif num_sources == 2:
            strategy_type = ResolutionStrategyType.PRIORITIZE  # Simple prioritization for 2 sources
        elif num_sources > 5:
            strategy_type = ResolutionStrategyType.CONSENSUS  # Consensus for many sources
        elif conflict_type == "temporal_conflict":
            strategy_type = ResolutionStrategyType.MERGE  # Merge temporal conflicts
        else:
            strategy_type = ResolutionStrategyType.PRIORITIZE  # Default to prioritization

        return ResolutionStrategy(
            strategy_id=f"strategy_{conflict.conflict_id}",
            conflict_id=conflict.conflict_id,
            strategy_type=strategy_type,
            parameters=MappingProxyType(
                {
                    "severity": severity.value,
                    "conflict_type": conflict_type,
                    "num_sources": str(num_sources),
                }
            ),
            expected_outcome=f"Resolve {conflict_type} using {strategy_type.value}",
            confidence=0.7,
        )

    def _execute_resolution_strategy(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
        strategy: ResolutionStrategy,
    ) -> ResolutionStrategy:
        """Execute the resolution strategy."""
        strategy_type = strategy.strategy_type

        if strategy_type == ResolutionStrategyType.PRIORITIZE:
            return self._execute_prioritize_strategy(conflict, graph, strategy)
        elif strategy_type == ResolutionStrategyType.MERGE:
            return self._execute_merge_strategy(conflict, graph, strategy)
        elif strategy_type == ResolutionStrategyType.CONSENSUS:
            return self._execute_consensus_strategy(conflict, graph, strategy)
        elif strategy_type == ResolutionStrategyType.DEFER:
            return self._execute_defer_strategy(conflict, graph, strategy)
        else:
            return self._execute_default_strategy(conflict, graph, strategy)

    def _execute_prioritize_strategy(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
        strategy: ResolutionStrategy,
    ) -> ResolutionStrategy:
        """Execute prioritize strategy - choose highest reliability source."""
        # Get nodes for involved sources
        source_nodes = [
            graph.nodes.get(source_id)
            for source_id in conflict.sources_involved
            if source_id in graph.nodes
        ]

        if not source_nodes:
            return strategy

        # Find highest reliability source
        prioritized_node = max(source_nodes, key=lambda n: n.reliability_score)

        # Update strategy with prioritization result
        return ResolutionStrategy(
            strategy_id=strategy.strategy_id,
            conflict_id=strategy.conflict_id,
            strategy_type=strategy.strategy_type,
            parameters=MappingProxyType(
                {
                    **strategy.parameters,
                    "prioritized_source": prioritized_node.source_id,
                    "prioritized_reliability": str(prioritized_node.reliability_score),
                }
            ),
            expected_outcome=f"Prioritized source {prioritized_node.source_id}",
            confidence=prioritized_node.reliability_score,
        )

    def _execute_merge_strategy(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
        strategy: ResolutionStrategy,
    ) -> ResolutionStrategy:
        """Execute merge strategy - merge conflicting values."""
        # TODO: Implement sophisticated merge logic
        return ResolutionStrategy(
            strategy_id=strategy.strategy_id,
            conflict_id=strategy.conflict_id,
            strategy_type=strategy.strategy_type,
            parameters=MappingProxyType(
                {**strategy.parameters, "merge_method": "weighted_average"}
            ),
            expected_outcome="Merged conflicting values using weighted average",
            confidence=0.6,
        )

    def _execute_consensus_strategy(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
        strategy: ResolutionStrategy,
    ) -> ResolutionStrategy:
        """Execute consensus strategy - use consensus mechanism."""
        # Apply weighted vote consensus
        consensus_result = self.consensus_mechanism(
            [conflict], graph, ConsensusMechanism.WEIGHTED_VOTE
        )

        return ResolutionStrategy(
            strategy_id=strategy.strategy_id,
            conflict_id=strategy.conflict_id,
            strategy_type=strategy.strategy_type,
            parameters=MappingProxyType(
                {
                    **strategy.parameters,
                    "consensus_id": consensus_result.consensus_id,
                    "agreement_level": str(consensus_result.agreement_level),
                }
            ),
            expected_outcome=f"Consensus achieved with {consensus_result.agreement_level:.2f} agreement",
            confidence=consensus_result.agreement_level,
        )

    def _execute_defer_strategy(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
        strategy: ResolutionStrategy,
    ) -> ResolutionStrategy:
        """Execute defer strategy - defer to human operator."""
        return ResolutionStrategy(
            strategy_id=strategy.strategy_id,
            conflict_id=strategy.conflict_id,
            strategy_type=strategy.strategy_type,
            parameters=MappingProxyType(
                {**strategy.parameters, "deferred_to": "human_operator"}
            ),
            expected_outcome="Deferred to human operator for resolution",
            confidence=0.0,
        )

    def _execute_default_strategy(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
        strategy: ResolutionStrategy,
    ) -> ResolutionStrategy:
        """Execute default strategy."""
        return strategy

    # ------------------------------------------------------------------
    # Private methods for propagation analysis
    # ------------------------------------------------------------------

    def _identify_affected_nodes(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
    ) -> list[str]:
        """Identify nodes that might be affected by a conflict."""
        affected_nodes: list[str] = []

        # Direct sources involved
        affected_nodes.extend(conflict.sources_involved)

        # Find connected nodes through conflict edges
        for source_id in conflict.sources_involved:
            for edge in graph.edges:
                if edge.from_source == source_id:
                    affected_nodes.append(edge.to_source)
                elif edge.to_source == source_id:
                    affected_nodes.append(edge.from_source)

        return list(set(affected_nodes))

    def _determine_propagation_path(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
        affected_nodes: list[str],
    ) -> list[str]:
        """Determine the propagation path through the graph."""
        # TODO: Implement sophisticated propagation path analysis
        return affected_nodes

    def _calculate_impact_severity(
        self,
        conflict: ConflictReport,
        graph: ConflictGraph,
        affected_nodes: list[str],
    ) -> ValidationSeverity:
        """Calculate the impact severity of conflict propagation."""
        # Base severity from conflict
        base_severity_score = {
            ValidationSeverity.CRITICAL: 5,
            ValidationSeverity.HIGH: 4,
            ValidationSeverity.MEDIUM: 3,
            ValidationSeverity.LOW: 2,
            ValidationSeverity.INFO: 1,
        }

        impact_score = base_severity_score.get(conflict.severity, 2)

        # Increase impact based on number of affected nodes
        impact_score += min(len(affected_nodes) // 2, 3)

        # Convert back to severity
        if impact_score >= 5:
            return ValidationSeverity.CRITICAL
        elif impact_score >= 4:
            return ValidationSeverity.HIGH
        elif impact_score >= 3:
            return ValidationSeverity.MEDIUM
        elif impact_score >= 2:
            return ValidationSeverity.LOW
        else:
            return ValidationSeverity.INFO

    def _calculate_cascade_potential(
        self,
        graph: ConflictGraph,
        affected_nodes: list[str],
    ) -> float:
        """Calculate the cascade potential of a conflict."""
        # Count edges between affected nodes
        edge_count = 0
        for edge in graph.edges:
            if edge.from_source in affected_nodes and edge.to_source in affected_nodes:
                edge_count += 1

        # Calculate cascade potential based on edge density
        if len(affected_nodes) < 2:
            return 0.0

        max_possible_edges = len(affected_nodes) * (len(affected_nodes) - 1) / 2
        cascade_potential = edge_count / max_possible_edges if max_possible_edges > 0 else 0.0

        return cascade_potential

    # ------------------------------------------------------------------
    # Private methods for consensus mechanism
    # ------------------------------------------------------------------

    def _gather_involved_sources(self, conflicts: list[ConflictReport]) -> list[str]:
        """Gather all sources involved in conflicts."""
        involved_sources: set[str] = set()

        for conflict in conflicts:
            involved_sources.update(conflict.sources_involved)

        return list(involved_sources)

    def _apply_consensus_mechanism(
        self,
        conflicts: list[ConflictReport],
        graph: ConflictGraph,
        involved_sources: list[str],
        mechanism: ConsensusMechanism,
    ) -> ConsensusResult:
        """Apply the specified consensus mechanism."""
        if mechanism == ConsensusMechanism.MAJORITY_VOTE:
            return self._majority_vote_consensus(conflicts, graph, involved_sources)
        elif mechanism == ConsensusMechanism.WEIGHTED_VOTE:
            return self._weighted_vote_consensus(conflicts, graph, involved_sources)
        elif mechanism == ConsensusMechanism.EXPERT_PANEL:
            return self._expert_panel_consensus(conflicts, graph, involved_sources)
        elif mechanism == ConsensusMechanism.TEMPORAL_PRIORITY:
            return self._temporal_priority_consensus(conflicts, graph, involved_sources)
        elif mechanism == ConsensusMechanism.SOURCE_HIERARCHY:
            return self._source_hierarchy_consensus(conflicts, graph, involved_sources)
        else:
            return self._weighted_vote_consensus(conflicts, graph, involved_sources)

    def _majority_vote_consensus(
        self,
        conflicts: list[ConflictReport],
        graph: ConflictGraph,
        involved_sources: list[str],
    ) -> ConsensusResult:
        """Apply majority vote consensus mechanism."""
        # Count votes for each source
        vote_counts: dict[str, int] = defaultdict(int)
        for source_id in involved_sources:
            vote_counts[source_id] = 1  # Each source gets one vote

        # Find source with most votes
        if not vote_counts:
            agreed_value = None
            agreement_level = 0.0
        else:
            winning_source = max(vote_counts.items(), key=lambda x: x[1])[0]
            agreed_value = winning_source
            agreement_level = vote_counts[winning_source] / len(vote_counts)

        return ConsensusResult(
            consensus_id=f"consensus_majority_{len(conflicts)}",
            conflict_id=conflicts[0].conflict_id if conflicts else "",
            agreed_value=agreed_value,
            participating_sources=tuple(involved_sources),
            agreement_level=agreement_level,
            mechanism_used=ConsensusMechanism.MAJORITY_VOTE,
            timestamp_ns=self._get_timestamp(),
        )

    def _weighted_vote_consensus(
        self,
        conflicts: list[ConflictReport],
        graph: ConflictGraph,
        involved_sources: list[str],
    ) -> ConsensusResult:
        """Apply weighted vote consensus mechanism."""
        # Weight votes by reliability
        weighted_votes: dict[str, float] = defaultdict(float)

        for source_id in involved_sources:
            node = graph.nodes.get(source_id)
            if node:
                weighted_votes[source_id] = node.reliability_score

        # Find source with highest weighted vote
        if not weighted_votes:
            agreed_value = None
            agreement_level = 0.0
        else:
            winning_source = max(weighted_votes.items(), key=lambda x: x[1])[0]
            agreed_value = winning_source
            total_weight = sum(weighted_votes.values())
            agreement_level = weighted_votes[winning_source] / total_weight if total_weight > 0 else 0.0

        return ConsensusResult(
            consensus_id=f"consensus_weighted_{len(conflicts)}",
            conflict_id=conflicts[0].conflict_id if conflicts else "",
            agreed_value=agreed_value,
            participating_sources=tuple(involved_sources),
            agreement_level=agreement_level,
            mechanism_used=ConsensusMechanism.WEIGHTED_VOTE,
            timestamp_ns=self._get_timestamp(),
        )

    def _expert_panel_consensus(
        self,
        conflicts: list[ConflictReport],
        graph: ConflictGraph,
        involved_sources: list[str],
    ) -> ConsensusResult:
        """Apply expert panel consensus mechanism."""
        # Prioritize expert sources (high reliability, specific types)
        expert_sources = [
            source_id
            for source_id in involved_sources
            if source_id in graph.nodes and graph.nodes[source_id].reliability_score > 0.8
        ]

        if expert_sources:
            participating_sources = expert_sources
            agreed_value = expert_sources[0]
            agreement_level = 0.8
        else:
            participating_sources = involved_sources
            agreed_value = involved_sources[0] if involved_sources else None
            agreement_level = 0.5

        return ConsensusResult(
            consensus_id=f"consensus_expert_{len(conflicts)}",
            conflict_id=conflicts[0].conflict_id if conflicts else "",
            agreed_value=agreed_value,
            participating_sources=tuple(participating_sources),
            agreement_level=agreement_level,
            mechanism_used=ConsensusMechanism.EXPERT_PANEL,
            timestamp_ns=self._get_timestamp(),
        )

    def _temporal_priority_consensus(
        self,
        conflicts: list[ConflictReport],
        graph: ConflictGraph,
        involved_sources: list[str],
    ) -> ConsensusResult:
        """Apply temporal priority consensus mechanism."""
        # Prioritize most recent sources
        source_timestamps: list[tuple[str, int]] = []

        for source_id in involved_sources:
            node = graph.nodes.get(source_id)
            if node:
                source_timestamps.append((source_id, node.timestamp_ns))

        if source_timestamps:
            # Sort by timestamp (most recent first)
            source_timestamps.sort(key=lambda x: x[1], reverse=True)
            agreed_value = source_timestamps[0][0]
            participating_sources = [s[0] for s in source_timestamps]
            agreement_level = 0.7
        else:
            agreed_value = involved_sources[0] if involved_sources else None
            participating_sources = involved_sources
            agreement_level = 0.5

        return ConsensusResult(
            consensus_id=f"consensus_temporal_{len(conflicts)}",
            conflict_id=conflicts[0].conflict_id if conflicts else "",
            agreed_value=agreed_value,
            participating_sources=tuple(participating_sources),
            agreement_level=agreement_level,
            mechanism_used=ConsensusMechanism.TEMPORAL_PRIORITY,
            timestamp_ns=self._get_timestamp(),
        )

    def _source_hierarchy_consensus(
        self,
        conflicts: list[ConflictReport],
        graph: ConflictGraph,
        involved_sources: list[str],
    ) -> ConsensusResult:
        """Apply source hierarchy consensus mechanism."""
        # Define source type hierarchy
        source_hierarchy = {
            "OPERATOR_INPUT": 10,
            "LEARNING_INFERENCE": 9,
            "STRATEGY_BACKTEST": 8,
            "ON_CHAIN_ANALYSIS": 7,
            "MARKET_DATA": 6,
            "NEWS_SENTIMENT": 5,
            "EXTERNAL_API": 4,
            "SYSTEM_INTERNAL": 3,
        }

        # Rank sources by hierarchy
        ranked_sources: list[tuple[str, int]] = []

        for source_id in involved_sources:
            node = graph.nodes.get(source_id)
            if node:
                hierarchy_level = source_hierarchy.get(node.source_type, 0)
                ranked_sources.append((source_id, hierarchy_level))

        if ranked_sources:
            # Sort by hierarchy level (highest first)
            ranked_sources.sort(key=lambda x: x[1], reverse=True)
            agreed_value = ranked_sources[0][0]
            participating_sources = [s[0] for s in ranked_sources]
            agreement_level = 0.75
        else:
            agreed_value = involved_sources[0] if involved_sources else None
            participating_sources = involved_sources
            agreement_level = 0.5

        return ConsensusResult(
            consensus_id=f"consensus_hierarchy_{len(conflicts)}",
            conflict_id=conflicts[0].conflict_id if conflicts else "",
            agreed_value=agreed_value,
            participating_sources=tuple(participating_sources),
            agreement_level=agreement_level,
            mechanism_used=ConsensusMechanism.SOURCE_HIERARCHY,
            timestamp_ns=self._get_timestamp(),
        )

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # In production, this would use the system time source
        return 0  # TODO: Integrate with proper time source


__all__ = [
    "SourceConflictGraph",
    "ConflictGraph",
    "ConflictNode",
    "ConflictEdge",
    "ResolutionStrategy",
    "PropagationMap",
    "ConsensusResult",
    "ConflictType",
    "ResolutionStrategy",
    "ConsensusMechanism",
]