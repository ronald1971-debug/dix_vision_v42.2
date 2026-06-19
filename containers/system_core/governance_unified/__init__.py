"""governance_unified — Unified Governance System.

Single authoritative governance system consolidating all governance functionality
from the previously fragmented approach (governance/, governance_engine/,
financial_governance/, operator_governance/, cognitive_governance/).

This provides the unified governance layer with comprehensive control plane,
domain-specific governance, security hardening, and operational features.
"""

# CRITICAL: Import core.contracts first to prevent circular dependency with execution_unified
import core.contracts

from .engine import GovernanceEngine
from .policy_compiler import compile_invariant, check_policy_violation
from .kill_switch import get_governance_kill_switch
from .strategy_registry import StrategyRegistry
from .approval_decision import ApprovalDecision

# Oracle system (from governance/)
from .oracle import (
    approve_l1_fast,
    approve_l2_balanced,
    approve_l3_deep,
)

# Mode system (from governance/)
from .mode import (
    ModeManager,
    OperationalMode,
    FsmMode,
    get_mode_manager,
    enter_safe_mode,
    exit_safe_mode,
    enter_degraded_mode,
    exit_degraded_mode,
    enter_halted_mode,
)

# Signals system (from governance/)
from .signals import (
    get_neuromorphic_risk,
    NeuromorphicRisk,
)

# Production-ready legacy archival components (organized by function)
from . import (
    legacy_archive,
)

# Authority and hazard system (from governance/ - for INDIRA/DYON decision making)
from .authority_graph import AuthorityLevel, AuthorityNode, AuthorityGraph
from .hazard_classifier import classify, HazardClassification
from .hazard_router import HazardRouter, get_hazard_router
from .market_context_projector import MarketContextProjector
from .escalation_matrix import should_escalate, escalate_severity
from .governance_main_charter import GOVERNANCE_CHARTER

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