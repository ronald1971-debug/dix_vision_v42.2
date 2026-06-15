"""State Layer - Enhanced with Replay Validation and Deterministic Verification.

This is the comprehensive state layer implementation that provides:
- Replay validation for event sourcing
- Deterministic verification for system components
- Enhanced state consistency checks
"""

# Existing state layer components
from .memory.edge_case_memory import EdgeCaseMemory
from .memory.contracts import MemoryRecord, MemoryKind

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

__all__ = [
    # Existing components
    "EdgeCaseMemory",
    "MemoryRecord",
    "MemoryKind",
    # Enhanced validation
    "ReplayValidator",
    "get_replay_validator",
    "ReplayResult",
    "ReplayStatus",
    "DeterministicVerifier",
    "get_deterministic_verifier",
    "DeterminismReport",
]