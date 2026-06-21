"""
Core Contracts API Cognitive Chat Approvals
Real implementation for cognitive chat approval contracts
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time

class ApprovalStatus(Enum):
    """Approval status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    CANCELLED = "cancelled"

class ApprovalKind(Enum):
    """Approval kind enumeration"""
    MESSAGE = "message"
    ACTION = "action"
    TOOL_CALL = "tool_call"
    SYSTEM_CHANGE = "system_change"
    POLICY_CHANGE = "policy_change"

@dataclass
class ApprovalDecisionRequest:
    """Approval decision request"""
    request_id: str
    approval_kind: ApprovalKind
    requester: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    status: ApprovalStatus = ApprovalStatus.PENDING
    priority: str = "normal"
    approvers: List[str] = field(default_factory=list)
    
    def is_pending(self) -> bool:
        """Check if request is pending"""
        return self.status == ApprovalStatus.PENDING
    
    def is_approved(self) -> bool:
        """Check if request is approved"""
        return self.status == ApprovalStatus.APPROVED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "approval_kind": self.approval_kind.value,
            "requester": self.requester,
            "description": self.description,
            "context": self.context,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "priority": self.priority,
            "approvers": self.approvers
        }

@dataclass
class ApprovalDecision:
    """Approval decision"""
    decision_id: str
    request_id: str
    approver: str
    decision: ApprovalStatus
    justification: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_approved(self) -> bool:
        """Check if decision is approved"""
        return self.decision == ApprovalStatus.APPROVED
    
    def is_rejected(self) -> bool:
        """Check if decision is rejected"""
        return self.decision == ApprovalStatus.REJECTED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "decision_id": self.decision_id,
            "request_id": self.request_id,
            "approver": self.approver,
            "decision": self.decision.value,
            "justification": self.justification,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class ApprovalDecisionResponse:
    """Approval decision response"""
    response_id: str
    request_id: str
    decision: ApprovalStatus
    approver: str
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "decision": self.decision.value,
            "approver": self.approver,
            "message": self.message,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class ApprovalsListResponse:
    """Approvals list response"""
    response_id: str
    requests: List[ApprovalDecisionRequest]
    total_count: int = 0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "requests": [r.to_dict() for r in self.requests],
            "total_count": self.total_count,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

class ApprovalRegistry:
    """Registry for approval requests"""
    
    def __init__(self):
        self._requests: Dict[str, ApprovalDecisionRequest] = {}
        self._decisions: Dict[str, List[ApprovalDecision]] = {}
    
    def submit_request(self, request: ApprovalDecisionRequest) -> bool:
        """Submit an approval request"""
        self._requests[request.request_id] = request
        self._decisions[request.request_id] = []
        return True
    
    def get_request(self, request_id: str) -> Optional[ApprovalDecisionRequest]:
        """Get a specific approval request"""
        return self._requests.get(request_id)
    
    def submit_decision(self, decision: ApprovalDecision) -> bool:
        """Submit an approval decision"""
        if decision.request_id in self._requests:
            self._decisions[decision.request_id].append(decision)
            return True
        return False
    
    def get_decisions(self, request_id: str) -> List[ApprovalDecision]:
        """Get all decisions for a request"""
        return self._decisions.get(request_id, [])

# Global approval registry
_approval_registry: Optional[ApprovalRegistry] = None

def get_approval_registry() -> ApprovalRegistry:
    """Get the global approval registry"""
    global _approval_registry
    if _approval_registry is None:
        _approval_registry = ApprovalRegistry()
    return _approval_registry

__all__ = [
    "ApprovalStatus",
    "ApprovalKind",
    "ApprovalDecisionRequest",
    "ApprovalDecision",
    "ApprovalDecisionResponse",
    "ApprovalsListResponse",
    "ApprovalRegistry",
    "get_approval_registry"
]