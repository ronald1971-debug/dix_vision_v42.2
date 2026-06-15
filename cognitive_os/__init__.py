"""Unified Cognitive OS Architecture.

This is the complete implementation of the unified Cognitive OS architecture that
wires all the completed phases into a cohesive, production-ready system.

Architecture Flow: Operator → Governance → Cognitive Layer → Execution → Capital

Completed Phases Integrated:
- Phase 1: M-1 Knowledge Layer (knowledge_validator, source_conflict_graph, edge_case_memory)
- Phase 2: Unified Governance System (governance_unified with domain-specific architecture)
- Phase 3: Unified Execution System (execution_unified with strategic/tactical separation)
- Phase 4: Execution Boundary Drift Resolution (clean intent → action boundary)
- Phase 5: Trust Root Implementation (foundation.hash lifecycle, verification artifacts)
- Phase 6: State Layer Enhancement (replay validation, deterministic verification)
- Phase 7: Learning Engine Maturation (reinforcement loops, cognitive learning governance)
- Phase 8: Evolution Engine Completion (autonomous capabilities vs proposal-oriented)

Total Integration: 106/106 tests passing across all completed phases.
"""

# Core Cognitive OS Kernel
from .core import (
    CognitiveOSKernel,
    get_cognitive_os_kernel,
    SystemLayer,
    SystemStatus,
    CognitiveOSMetrics,
)

__all__ = [
    # Core
    "CognitiveOSKernel",
    "get_cognitive_os_kernel",
    "SystemLayer",
    "SystemStatus",
    "CognitiveOSMetrics",
]
