"""Unified Governance System - Single Authority Layer.

This is the consolidated governance system that replaces the fragmented
governance/, governance_engine/, financial_governance/, and operator_governance/
modules with a single, coherent governance architecture as specified in the
DIX VISION system vision.

System Vision: "a robust governance layer with permission-based access control"
Implementation: Single unified governance system with domain-specific modules

Architecture:
- Core: Unified governance kernel and authority management
- Domains: Financial, Operator, Cognitive, Execution governance
- Policies: Unified policy engine and compilation
- Modes: System mode management and transitions
- Risk: Unified risk assessment and hazard response
- Integration: External system integration and coordination

This provides the single governance layer called for in the system vision.
"""

# Core governance components
from .core.kernel import (
    UnifiedGovernanceKernel,
    get_unified_governance_kernel,
    GovernanceRequest,
    GovernanceDecision,
    GovernanceOutcome,
    AuthorityRequest,
    AuthorityDecision,
    ModeTransitionRequest,
    ModeTransitionResult,
    RiskAssessment,
    SystemMode,
    IntentType,
)

# Domain-specific governance (module-level imports)
from .domains import financial as financial_domain
from .domains import operator as operator_domain

# Policy management
from .policies.policy_engine import get_policy_engine
from .modes.mode_manager import get_mode_manager

# Risk management
from .risk.risk_engine import get_risk_engine

__all__ = [
    # Core governance
    "UnifiedGovernanceKernel",
    "get_unified_governance_kernel",
    "GovernanceRequest",
    "GovernanceDecision",
    "GovernanceOutcome",
    "AuthorityRequest",
    "AuthorityDecision",
    "ModeTransitionRequest",
    "ModeTransitionResult",
    "RiskAssessment",
    "SystemMode",
    "IntentType",
    # Financial domain
    "financial_domain",
    # Operator domain
    "operator_domain",
    # Policy and mode management
    "get_policy_engine",
    "get_mode_manager",
    "get_risk_engine",
]