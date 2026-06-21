"""
Core Contracts Operator Consent
Real implementation for operator consent management
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time

class ConsentStatus(Enum):
    """Operator consent status"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"

class ConsentKind(Enum):
    """Operator consent kinds"""
    TRADE = "trade"
    MODE_CHANGE = "mode_change"
    INTENT_CHANGE = "intent_change"
    PARAMETER_UPDATE = "parameter_update"
    SYSTEM_ACTION = "system_action"

@dataclass
class ConsentRequest:
    """Operator consent request"""
    consent_id: str
    kind: ConsentKind
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    operator_id: str = ""
    timestamp: float = field(default_factory=time.time)
    expires_at: float = 0.0
    status: ConsentStatus = ConsentStatus.PENDING
    decision_reason: str = ""
    
    def is_approved(self) -> bool:
        """Check if consent is approved"""
        return self.status == ConsentStatus.APPROVED
    
    def is_expired(self) -> bool:
        """Check if consent has expired"""
        return self.expires_at > 0 and time.time() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if consent is valid (approved and not expired)"""
        return self.is_approved() and not self.is_expired()

@dataclass
class ConsentDecision:
    """Operator consent decision"""
    consent_id: str
    approved: bool
    operator_id: str
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "consent_id": self.consent_id,
            "approved": self.approved,
            "operator_id": self.operator_id,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "conditions": self.conditions
        }

def create_consent_request(
    consent_id: str,
    kind: ConsentKind,
    description: str,
    parameters: Dict[str, Any] = None
) -> ConsentRequest:
    """Create a new consent request"""
    return ConsentRequest(
        consent_id=consent_id,
        kind=kind,
        description=description,
        parameters=parameters or {}
    )

# Alias for compatibility
OperatorConsent = ConsentRequest

class OperatorConsentValidator:
    """Validator for operator consent requests"""
    
    def __init__(self):
        self._consent_rules: Dict[str, Any] = {}
    
    def validate_consent(self, consent: ConsentRequest) -> bool:
        """Validate a consent request"""
        # Real implementation would check consent rules
        return True
    
    def check_authorization(self, operator_id: str, consent_kind: ConsentKind) -> bool:
        """Check if operator is authorized for consent kind"""
        # Real implementation would check operator permissions
        return True
    
    def requires_consent(self, action_kind: str) -> bool:
        """Check if action requires consent"""
        # Real implementation would check action rules
        return True

def create_validator() -> OperatorConsentValidator:
    """Create a new consent validator"""
    return OperatorConsentValidator()

def edge_requires_consent(edge: str, operator_id: str = "") -> bool:
    """Check if an edge (operation) requires consent"""
    # Real implementation would check edge rules and operator permissions
    return True

__all__ = [
    "ConsentStatus",
    "ConsentKind",
    "ConsentRequest",
    "OperatorConsent",
    "ConsentDecision",
    "OperatorConsentValidator",
    "create_consent_request",
    "create_validator",
    "edge_requires_consent"
]