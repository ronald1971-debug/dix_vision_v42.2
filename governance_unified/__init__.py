"""governance_unified — Unified Governance System.

Single authoritative governance system consolidating all governance functionality
from the previously fragmented approach (governance/, governance_engine/,
financial_governance/, operator_governance/, cognitive_governance/).

This provides the unified governance layer with comprehensive control plane,
domain-specific governance, security hardening, and operational features.
"""

from .engine import GovernanceEngine
from .policy_compiler import compile_invariant, check_policy_violation
from .kill_switch import get_governance_kill_switch
from .strategy_registry import StrategyRegistry

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
]