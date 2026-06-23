"""
Operator Governance - Operator-Specific Governance Module
NO LAZY LOADING - All components load directly
"""

import logging

from .authority_escalation import (
    AuthorityEscalation,
    AuthorityEscalationGuard,
    get_authority_escalation_guard,
)
from .consent_router import ConsentRouter

logger = logging.getLogger(__name__)

# Global instance for consent router
_consent_router = None


def get_consent_router() -> ConsentRouter:
    """Get consent router instance"""
    global _consent_router
    if _consent_router is None:
        _consent_router = ConsentRouter()
    return _consent_router


__all__ = [
    "AuthorityEscalation",
    "AuthorityEscalationGuard",
    "get_authority_escalation_guard",
    "ConsentRouter",
    "get_consent_router",
]
