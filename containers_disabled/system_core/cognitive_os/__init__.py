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
- Phase 9: Advanced Cognitive Modules (RL, XAI, Multi-Agent, Temporal, Risk)
- Phase 10: Neuro-Symbolic & Meta-Cognitive Integration
- Phase 11: Advanced Causal Discovery Engine
- Phase 12: Neuromorphic Computing (INDIRA & DYON SNN + LSM)
- Priority 3: Advanced AI Capabilities (Semantic Reasoning, AutoML, Knowledge Graph, Multi-Agent Orchestration, Cross-Modal)

Total Integration: 121+ tests passing across all completed phases + Priority 3 enhancements.
"""

from .agents import (
    get_multi_agent_engine,
)
from .automl import (
    get_automl_engine,
)
from .causal import (
    get_advanced_causal_discovery,
)

# Core Cognitive OS Kernel
from .core import (
    CognitiveOSKernel,
    CognitiveOSMetrics,
    SystemLayer,
    SystemStatus,
    get_cognitive_os_kernel,
)

# Integration Layer
from .integration import (
    get_advanced_ai_integration,
    get_complete_system_integration,
)
from .knowledge import (
    get_advanced_graph_engine,
)
from .meta_cognitive import (
    get_meta_cognitive_system,
)
from .multi_agent import (
    get_multi_agent_system,
)
from .multimodal import (
    get_cross_modal_engine,
)

# Phase 4 Advanced Modules
from .neuro_symbolic import (
    get_neuro_symbolic_ai,
)
from .risk import (
    get_dynamic_risk_manager,
)

# Phase 3 Advanced Modules
from .rl import (
    get_rl_optimizer,
)

# Priority 3 Advanced AI Capabilities
from .semantic import (
    get_semantic_reasoning_engine,
)
from .temporal import (
    get_temporal_reasoner,
)
from .xai import (
    get_xai_system,
)

__all__ = [
    # Core
    "CognitiveOSKernel",
    "get_cognitive_os_kernel",
    "SystemLayer",
    "SystemStatus",
    "CognitiveOSMetrics",
    # Phase 3 (only export get functions for simplicity)
    "get_rl_optimizer",
    "get_xai_system",
    "get_multi_agent_system",
    "get_temporal_reasoner",
    "get_dynamic_risk_manager",
    # Phase 4 (only export get functions for simplicity)
    "get_neuro_symbolic_ai",
    "get_meta_cognitive_system",
    "get_advanced_causal_discovery",
    # Integration Layer
    "get_advanced_ai_integration",
    "get_complete_system_integration",
    # Priority 3 Advanced AI Capabilities
    "get_semantic_reasoning_engine",
    "get_automl_engine",
    "get_advanced_graph_engine",
    "get_multi_agent_engine",
    "get_cross_modal_engine",
]
