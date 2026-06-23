"""State Layer - Enhanced with Replay Validation and Deterministic Verification.

This is the comprehensive state layer implementation that provides:
- Replay validation for event sourcing
- Deterministic verification for system components
- Enhanced state consistency checks
- Knowledge validation and drift monitoring (Priority 2)
"""

from .deterministic_verifier import (
    DeterminismReport,
    DeterministicVerifier,
    get_deterministic_verifier,
)
from .drift_monitor import (
    DriftAlert,
    DriftBaseline,
    DriftMetric,
    DriftMonitor,
    DriftSeverity,
    DriftType,
    get_drift_monitor,
)

# Knowledge layer components (Priority 2)
from .knowledge_validator import (
    KnowledgeEntry,
    KnowledgeValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    ValidationStatus,
    get_knowledge_validator,
)
from .memory.contracts import MemoryKind, MemoryRecord

# Existing state layer components
from .memory.edge_case_memory import EdgeCaseMemory
from .memory.index import MemoryIndex

# Enhanced validation components
from .replay_validator import (
    ReplayResult,
    ReplayStatus,
    ReplayValidator,
    get_replay_validator,
)
from .source_conflict_graph import (
    ConflictEdge,
    ConflictNode,
    ConflictResolution,
    ConflictSeverity,
    ConflictType,
    SourceConflictGraph,
    get_source_conflict_graph,
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
