"""Operator Governance Domain.

Domain-specific governance for operator interactions including
authority management, consent routing, override priorities, and
manual control mechanisms.
"""

# Import the modules themselves rather than specific functions
from . import authority_escalation
from . import consent_router
from . import governance_visibility
from . import manual_lockout
from . import override_priority
from . import operator_constitution

__all__ = [
    "authority_escalation",
    "consent_router",
    "governance_visibility",
    "manual_lockout",
    "override_priority",
    "operator_constitution",
]