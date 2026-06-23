"""
Core Contracts API Governance
Real implementation for governance API contracts
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class GovernanceStatus(Enum):
    """Governance status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class GovernanceAction(Enum):
    """Governance action enumeration"""

    APPROVE = "approve"
    REJECT = "reject"
    DEFER = "defer"
    ESCALATE = "escalate"
    OVERRIDE = "override"


@dataclass
class GovernanceRequest:
    """Governance request information"""

    request_id: str
    action: GovernanceAction
    requester: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    status: GovernanceStatus = GovernanceStatus.ACTIVE
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_active(self) -> bool:
        """Check if request is active"""
        return self.status == GovernanceStatus.ACTIVE

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "action": self.action.value,
            "requester": self.requester,
            "description": self.description,
            "context": self.context,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class GovernanceDecision:
    """Governance decision information"""

    decision_id: str
    request_id: str
    decision: GovernanceAction
    decision_maker: str
    justification: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_approval(self) -> bool:
        """Check if decision is an approval"""
        return self.decision == GovernanceAction.APPROVE

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "decision_id": self.decision_id,
            "request_id": self.request_id,
            "decision": self.decision.value,
            "decision_maker": self.decision_maker,
            "justification": self.justification,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class DriftResponse:
    """Drift response information"""

    response_id: str
    drift_type: str
    severity: str
    description: str
    remediation: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "drift_type": self.drift_type,
            "severity": self.severity,
            "description": self.description,
            "remediation": self.remediation,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class HazardsResponse:
    """Hazards response information"""

    response_id: str
    hazard_count: int
    hazards: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "hazard_count": self.hazard_count,
            "hazards": self.hazards,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class PromotionGatesResponse:
    """Promotion gates response information"""

    response_id: str
    gate_status: Dict[str, bool] = field(default_factory=dict)
    all_passed: bool = False
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "gate_status": self.gate_status,
            "all_passed": self.all_passed,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class SourcesResponse:
    """Sources response information"""

    response_id: str
    source_count: int
    sources: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "source_count": self.source_count,
            "sources": self.sources,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class GovernanceRegistry:
    """Registry for governance operations"""

    def __init__(self):
        self._requests: Dict[str, GovernanceRequest] = {}
        self._decisions: Dict[str, List[GovernanceDecision]] = {}

    def submit_request(self, request: GovernanceRequest) -> bool:
        """Submit a governance request"""
        self._requests[request.request_id] = request
        self._decisions[request.request_id] = []
        return True

    def get_request(self, request_id: str) -> Optional[GovernanceRequest]:
        """Get a specific request"""
        return self._requests.get(request_id)

    def submit_decision(self, decision: GovernanceDecision) -> bool:
        """Submit a governance decision"""
        if decision.request_id in self._requests:
            self._decisions[decision.request_id].append(decision)
            return True
        return False

    def get_decisions(self, request_id: str) -> List[GovernanceDecision]:
        """Get decisions for a request"""
        return self._decisions.get(request_id, [])


# Global governance registry
_governance_registry: Optional[GovernanceRegistry] = None


def get_governance_registry() -> GovernanceRegistry:
    """Get the global governance registry"""
    global _governance_registry
    if _governance_registry is None:
        _governance_registry = GovernanceRegistry()
    return _governance_registry


__all__ = [
    "GovernanceStatus",
    "GovernanceAction",
    "GovernanceRequest",
    "GovernanceDecision",
    "DriftResponse",
    "HazardsResponse",
    "PromotionGatesResponse",
    "SourcesResponse",
    "GovernanceRegistry",
    "get_governance_registry",
]
