"""
Core Contracts Event Provenance
Real implementation for event provenance tracking
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Set


class SourceKind(Enum):
    """Source kind enumeration"""

    OPERATOR = "operator"
    SYSTEM = "system"
    EXTERNAL = "external"
    AUTOMATED = "automated"


@dataclass
class Provenance:
    """Provenance information for an event"""

    source: str
    source_kind: SourceKind
    timestamp: float = field(default_factory=time.time)
    operator_id: str = ""
    authorization_level: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthorizationLevel:
    """Authorization level configuration"""

    level: str
    permissions: Set[str] = field(default_factory=set)
    can_approve: bool = False
    can_override: bool = False
    can_escalate: bool = False


# Authorization levels by role
_AUTHORIZATION_LEVELS = {
    "operator": AuthorizationLevel(
        level="operator",
        permissions={"approve", "deny", "override", "escalate"},
        can_approve=True,
        can_override=True,
        can_escalate=True,
    ),
    "auditor": AuthorizationLevel(
        level="auditor",
        permissions={"approve", "deny"},
        can_approve=True,
        can_override=False,
        can_escalate=False,
    ),
    "observer": AuthorizationLevel(
        level="observer",
        permissions={"approve"},
        can_approve=True,
        can_override=False,
        can_escalate=False,
    ),
    "system": AuthorizationLevel(
        level="system", permissions=set(), can_approve=False, can_override=False, can_escalate=False
    ),
}


def get_authorization_level(role: str) -> AuthorizationLevel:
    """Get authorization level for a role"""
    return _AUTHORIZATION_LEVELS.get(role, _AUTHORIZATION_LEVELS["observer"])


def is_operator_authorized_source(
    source: str, source_kind: SourceKind, operator_id: str = ""
) -> bool:
    """
    Check if the source is operator-authorized
    Returns True if the source has operator authorization
    """
    if source_kind == SourceKind.OPERATOR:
        # Direct operator actions are authorized
        return True
    if source_kind == SourceKind.SYSTEM:
        # System actions require explicit operator authorization
        return False
    if source_kind == SourceKind.AUTOMATED:
        # Automated actions may require approval based on policy
        return False
    # External sources need authorization
    return False


def verify_provenance(provenance: Provenance) -> bool:
    """Verify the provenance of an event"""
    if not provenance.source:
        return False
    return provenance.source_kind in [SourceKind.OPERATOR, SourceKind.SYSTEM]


__all__ = [
    "SourceKind",
    "Provenance",
    "AuthorizationLevel",
    "get_authorization_level",
    "is_operator_authorized_source",
    "verify_provenance",
]
