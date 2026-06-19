"""State Layer - Enhanced with Replay Validation and Deterministic Verification.

This is the comprehensive state layer implementation that provides:
- Replay validation for event sourcing
- Deterministic verification for system components
- Enhanced state consistency checks
- Knowledge validation and drift monitoring (Priority 2)
"""

# Existing state layer components
from .memory.edge_case_memory import EdgeCaseMemory
from .memory.contracts import MemoryRecord, MemoryKind
from .memory.index import MemoryIndex

# Enhanced validation components
from .replay_validator import (
    ReplayValidator,
    get_replay_validator,
    ReplayResult,
    ReplayStatus,
)
from .deterministic_verifier import (
    DeterministicVerifier,
    get_deterministic_verifier,
    DeterminismReport,
)

# Knowledge layer components (Priority 2)
from .knowledge_validator import (
    ValidationSeverity,
    ValidationStatus,
    ValidationIssue,
    ValidationResult,
    KnowledgeEntry,
    KnowledgeValidator,
    get_knowledge_validator,
)
from .source_conflict_graph import (
    ConflictSeverity,
    ConflictType,
    ConflictNode,
    ConflictEdge,
    ConflictResolution,
    SourceConflictGraph,
    get_source_conflict_graph,
)
from .drift_monitor import (
    DriftSeverity,
    DriftType,
    DriftMetric,
    DriftAlert,
    DriftBaseline,
    DriftMonitor,
    get_drift_monitor,
)

__all__ = [
    # Existing components
    "EdgeCaseMemory",
    "MemoryRecord",
    "MemoryKind",
    "MemoryIndex",
    # Enhanced validation
    "ReplayValidator",
    "get_replay_validator",
    "ReplayResult",
    "ReplayStatus",
    "DeterministicVerifier",
    "get_deterministic_verifier",
    "DeterminismReport",
    # Knowledge layer (Priority 2)
    "ValidationSeverity",
    "ValidationStatus",
    "ValidationIssue",
    "ValidationResult",
    "KnowledgeEntry",
    "KnowledgeValidator",
    "get_knowledge_validator",
    "ConflictSeverity",
    "ConflictType",
    "ConflictNode",
    "ConflictEdge",
    "ConflictResolution",
    "SourceConflictGraph",
    "get_source_conflict_graph",
    "DriftSeverity",
    "DriftType",
    "DriftMetric",
    "DriftAlert",
    "DriftBaseline",
    "DriftMonitor",
    "get_drift_monitor",
]