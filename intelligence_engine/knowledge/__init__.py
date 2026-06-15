"""M-1 Knowledge Layer - Complete knowledge validation and management.

This module provides the foundational M-1 Knowledge Layer components that
transform INDIRA from Signal Intelligence to Knowledge Intelligence.

Components:
- KnowledgeValidator: Validates knowledge sources and ensures epistemic integrity
- SourceConflictGraph: Tracks and resolves conflicts between knowledge sources
- KnowledgeDriftMonitor: Monitors knowledge drift and triggers appropriate responses
"""

from .news_knowledge import NewsKnowledgeIndex
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
)
from .source_conflict_graph import (
    SourceConflictGraph,
    ConflictGraph,
    ConflictNode,
    ConflictEdge,
    ResolutionStrategy,
    ResolutionStrategyType,
    PropagationMap,
    ConsensusResult,
    ConflictType,
    ConsensusMechanism,
)
from .drift_monitor import (
    KnowledgeDriftMonitor,
    DriftAlert,
    DriftReport,
    MitigationPlan,
    ResponseAction,
    DriftType,
    DriftSeverity,
    ResponseActionType,
)

__all__ = [
    # Legacy component
    "NewsKnowledgeIndex",
    # M-1 Knowledge Layer components
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
    "SourceConflictGraph",
    "ConflictGraph",
    "ConflictNode",
    "ConflictEdge",
    "ResolutionStrategy",
    "ResolutionStrategyType",
    "PropagationMap",
    "ConsensusResult",
    "ConflictType",
    "ConsensusMechanism",
    "KnowledgeDriftMonitor",
    "DriftAlert",
    "DriftReport",
    "MitigationPlan",
    "ResponseAction",
    "DriftType",
    "DriftSeverity",
    "ResponseActionType",
]