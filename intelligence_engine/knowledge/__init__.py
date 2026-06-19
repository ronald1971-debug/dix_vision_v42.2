"""M-1 Knowledge Layer - Integration Package

Provides integrated access to all knowledge layer components including:
- Knowledge validation and conflict detection
- Drift monitoring and response
- Source conflict graph management
- Integration with INDIRA cognitive engine
"""

from .knowledge_validator import (
    KnowledgeValidator,
    KnowledgeSource,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    KnowledgeSourceType,
    ConflictReport,
    IntegrityScore,
    ReliabilityScore,
    ConsistencyReport,
    get_knowledge_validator,
)

from .drift_monitor import (
    KnowledgeDriftMonitor,
    DriftType,
    DriftSeverity,
    ResponseActionType,
    DriftAlert,
    DriftReport,
    MitigationPlan,
    ResponseAction,
    get_drift_monitor,
)

from .source_conflict_graph import (
    SourceConflictGraph,
    ConflictType,
    ConflictNode,
    ConflictEdge,
    ConflictGraph,
    ResolutionStrategyType,
    ResolutionStrategy,
    PropagationMap,
    ConsensusResult,
    get_source_conflict_graph,
)

__all__ = [
    # Knowledge Validator
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
    "get_knowledge_validator",
    # Drift Monitor
    "KnowledgeDriftMonitor",
    "DriftType",
    "DriftSeverity",
    "ResponseActionType",
    "DriftAlert",
    "DriftReport",
    "MitigationPlan",
    "ResponseAction",
    "get_drift_monitor",
    # Source Conflict Graph
    "SourceConflictGraph",
    "ConflictType",
    "ConflictNode",
    "ConflictEdge",
    "ConflictGraph",
    "ResolutionStrategyType",
    "ResolutionStrategy",
    "PropagationMap",
    "ConsensusResult",
    "get_source_conflict_graph",
]

# Singleton instances
_knowledge_validator_instance = None
_drift_monitor_instance = None
_source_conflict_graph_instance = None


def get_knowledge_validator() -> KnowledgeValidator:
    """Get the singleton knowledge validator instance."""
    global _knowledge_validator_instance
    if _knowledge_validator_instance is None:
        _knowledge_validator_instance = KnowledgeValidator()
    return _knowledge_validator_instance


def get_drift_monitor() -> KnowledgeDriftMonitor:
    """Get the singleton drift monitor instance."""
    global _drift_monitor_instance
    if _drift_monitor_instance is None:
        _drift_monitor_instance = KnowledgeDriftMonitor()
    return _drift_monitor_instance


def get_source_conflict_graph() -> SourceConflictGraph:
    """Get the singleton source conflict graph instance."""
    global _source_conflict_graph_instance
    if _source_conflict_graph_instance is None:
        _source_conflict_graph_instance = SourceConflictGraph()
    return _source_conflict_graph_instance


class KnowledgeLayerIntegration:
    """Integration point for all knowledge layer components."""
    
    def __init__(self):
        self._validator = get_knowledge_validator()
        self._drift_monitor = get_drift_monitor()
        self._conflict_graph = get_source_conflict_graph()
        
    def validate_knowledge(
        self,
        sources: list[KnowledgeSource],
        existing_knowledge = None,
    ) -> ValidationResult:
        """Validate knowledge sources through the complete pipeline."""
        # Validate sources
        validation_results = [
            self._validator.validate_source(source) for source in sources
        ]
        
        # Detect conflicts
        conflicts = self._validator.detect_conflicts(sources, existing_knowledge)
        
        # Check integrity
        if existing_knowledge:
            integrity_score = self._validator.epistemic_integrity_check(existing_knowledge)
        else:
            integrity_score = None
        
        return ValidationResult(
            is_valid=all(result.is_valid for result in validation_results),
            confidence_score=sum(result.confidence_score for result in validation_results) / len(validation_results),
            issues=tuple(
                issue for result in validation_results for issue in result.issues
            ),
            validated_source=sources[0] if sources else None,
            timestamp_ns=self._validator._get_timestamp(),
        )
    
    def monitor_knowledge_health(
        self,
        knowledge,
        check_drift: bool = True,
    ) -> dict:
        """Monitor health of knowledge graph."""
        health_report = {
            "timestamp": self._validator._get_timestamp(),
        }
        
        # Check for drift
        if check_drift:
            concept_drift = self._drift_monitor.detect_concept_drift(knowledge)
            if concept_drift:
                health_report["concept_drift"] = {
                    "detected": True,
                    "severity": concept_drift.severity.value,
                    "magnitude": concept_drift.drift_magnitude,
                }
            else:
                health_report["concept_drift"] = {"detected": False}
        
        return health_report
    
    def resolve_conflicts(
        self,
        conflicts: list[ConflictReport],
        graph: ConflictGraph,
    ) -> list[ResolutionStrategy]:
        """Resolve knowledge conflicts using the conflict graph."""
        resolutions = []
        
        for conflict in conflicts:
            resolution = self._conflict_graph.resolve_conflicts(conflict, graph)
            resolutions.append(resolution)
        
        return resolutions


def get_knowledge_layer_integration() -> KnowledgeLayerIntegration:
    """Get the singleton knowledge layer integration instance."""
    return KnowledgeLayerIntegration()