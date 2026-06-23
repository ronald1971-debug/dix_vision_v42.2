"""governance_unified — Unified Governance System.

Single authoritative governance system consolidating all governance functionality
from the previously fragmented approach (governance/, governance_engine/,
financial_governance/, operator_governance/, cognitive_governance/).

This provides the unified governance layer with comprehensive control plane,
domain-specific governance, security hardening, and operational features.
"""

# CRITICAL: Import core.contracts first to prevent circular dependency with execution_unified

# Production-ready legacy archival components (organized by function)
from . import (
    legacy_archive,
)

# Authority and hazard system (from governance/ - for INDIRA/DYON decision making)
from .authority_graph import AuthorityGraph, AuthorityLevel, AuthorityNode
from .engine import GovernanceEngine
from .escalation_matrix import escalate_severity, should_escalate
from .governance_main_charter import GOVERNANCE_CHARTER
from .hazard_classifier import HazardClassification, classify
from .hazard_router import HazardRouter, get_hazard_router
from .kill_switch import get_governance_kill_switch
from .market_context_projector import MarketContextProjector

# Mode system (from governance/)
from .mode import (
    FsmMode,
    ModeManager,
    OperationalMode,
    enter_degraded_mode,
    enter_halted_mode,
    enter_safe_mode,
    exit_degraded_mode,
    exit_safe_mode,
    get_mode_manager,
)

# Oracle system (from governance/)
from .oracle import (
    approve_l1_fast,
    approve_l2_balanced,
    approve_l3_deep,
)
from .policy_compiler import check_policy_violation, compile_invariant

# Signals system (from governance/)
from .signals import (
    NeuromorphicRisk,
    get_neuromorphic_risk,
)
from .strategy_registry import StrategyRegistry

__all__ = [
    "GovernanceEngine",
    "compile_invariant",
    "check_policy_violation",
    "get_governance_kill_switch",
    "StrategyRegistry",
    "approve_l1_fast",
    "approve_l2_balanced",
    "approve_l3_deep",
    "ModeManager",
    "OperationalMode",
    "FsmMode",
    "get_mode_manager",
    "enter_safe_mode",
    "exit_safe_mode",
    "enter_degraded_mode",
    "exit_degraded_mode",
    "enter_halted_mode",
    "get_neuromorphic_risk",
    "NeuromorphicRisk",
    "legacy_archive",
    "AuthorityLevel",
    "AuthorityNode",
    "AuthorityGraph",
    "classify",
    "HazardClassification",
    "HazardRouter",
    "get_hazard_router",
    "MarketContextProjector",
    "should_escalate",
    "escalate_severity",
    "GOVERNANCE_CHARTER",
    # All archival components available via submodules:
    # - governance_unified.legacy_archive (162 governance legacy components)
    # Including: cognitive_governance, financial_governance, governance_engine
    # and all their subdomains (cognitive, financial, operator, system)
    # Total: 162 archival components available via submodules
]
