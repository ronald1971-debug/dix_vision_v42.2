"""
governance_engine.domains.operator
Operator sovereignty and human-in-the-loop governance guards.

This module contains guards migrated from operator_governance/ to ensure
operator authority, consent management, and human oversight.
"""

from __future__ import annotations

from .authority_escalation import AuthorityEscalationGuard, get_authority_escalation_guard
from .consent_router import ConsentRouter, get_consent_router
from .governance_visibility import GovernanceVisibilityMonitor, get_governance_visibility_monitor
from .manual_lockout import ManualLockoutGuard, get_manual_lockout_guard
from .operator_constitution import OperatorConstitution, get_operator_constitution
from .override_priority import OverridePriorityManager, get_override_priority_manager

__all__ = [
    "AuthorityEscalationGuard",
    "get_authority_escalation_guard",
    "ConsentRouter",
    "get_consent_router",
    "GovernanceVisibilityMonitor",
    "get_governance_visibility_monitor",
    "ManualLockoutGuard",
    "get_manual_lockout_guard",
    "OperatorConstitution",
    "get_operator_constitution",
    "OverridePriorityManager",
    "get_override_priority_manager",
]