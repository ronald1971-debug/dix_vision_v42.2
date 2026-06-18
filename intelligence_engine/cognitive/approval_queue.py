"""
Approval Queue Management - Real Implementation

Provides real approval queue management for governance workflows,
operator approvals, and cognitive decision validation.
"""

from typing import Any, List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
from datetime import datetime, timedelta
from collections import deque
import uuid
import json

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Status of approval requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    IN_REVIEW = "in_review"


class ApprovalPriority(Enum):
    """Priority levels for approval requests."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class ApprovalType(Enum):
    """Types of approvals that can be requested."""
    TRADE_EXECUTION = "trade_execution"
    STRATEGY_DEPLOYMENT = "strategy_deployment"
    SYSTEM_MODE_CHANGE = "system_mode_change"
    PARAMETER_UPDATE = "parameter_update"
    LEARNING_ACTIVATION = "learning_activation"
    EVOLUTION_PROPOSAL = "evolution_proposal"
    EMERGENCY_ACTION = "emergency_action"


@dataclass
class ApprovalRequest:
    """Represents an approval request."""
    request_id: str
    approval_type: ApprovalType
    requester_id: str
    request_data: Dict[str, Any]
    priority: ApprovalPriority = ApprovalPriority.NORMAL
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    timeout_seconds: float = 3600.0  # Default 1 hour
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    approval_conditions: List[str] = field(default_factory=list)
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate expiration time if not set."""
        if self.expires_at is None and self.timeout_seconds:
            self.expires_at = self.created_at + timedelta(seconds=self.timeout_seconds)
    
    def is_expired(self) -> bool:
        """Check if the request has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def is_pending(self) -> bool:
        """Check if the request is still pending."""
        return self.status == ApprovalStatus.PENDING and not self.is_expired()
    
    def time_until_expiry(self) -> Optional[timedelta]:
        """Get time remaining until expiration."""
        if self.expires_at is None:
            return None
        remaining = self.expires_at - datetime.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)


@dataclass
class ApprovalDecision:
    """Represents an approval decision."""
    decision_id: str
    request_id: str
    approver_id: str
    approved: bool
    timestamp: datetime = field(default_factory=datetime.now)
    conditions: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    decision_weight: float = 1.0  # Weight of this decision in final outcome


@dataclass
class ApprovalPolicy:
    """Policy for handling approval requests."""
    policy_id: str
    approval_types: List[ApprovalType]
    required_approvers: int
    approval_threshold: float  # Fraction of approvals required
    auto_approve_conditions: List[str] = field(default_factory=list)
    auto_reject_conditions: List[str] = field(default_factory=list)
    timeout_policy: str = "reject"  # or "approve", "escalate"
    escalation_handlers: List[str] = field(default_factory=list)


class ApprovalQueue:
    """Real approval queue with workflow management and governance integration."""
    
    def __init__(self, queue_id: str = "default", max_size: int = 1000, **kwargs: Any):
        self._queue_id = queue_id
        self._max_size = max_size
        self._requests: deque = deque(maxlen=max_size)
        self._request_index: Dict[str, ApprovalRequest] = {}
        self._decisions: Dict[str, List[ApprovalDecision]] = {}
        self._policies: Dict[str, ApprovalPolicy] = {}
        self._approvers: Dict[str, Dict[str, Any]] = {}  # approver_id -> approver info
        self._statistics = {
            "total_requests": 0,
            "approved": 0,
            "rejected": 0,
            "expired": 0,
            "cancelled": 0
        }
        
        # Load default policies
        self._initialize_default_policies()
        
        logger.info(f"[APPROVAL_QUEUE] Approval queue initialized: {queue_id} (max_size: {max_size})")
    
    def _initialize_default_policies(self):
        """Initialize default approval policies."""
        # Trade execution policy
        trade_policy = ApprovalPolicy(
            policy_id="trade_execution_policy",
            approval_types=[ApprovalType.TRADE_EXECUTION],
            required_approvers=1,
            approval_threshold=0.5,
            auto_approve_conditions=["small_trade", "low_risk"],
            auto_reject_conditions=["large_trade", "high_risk", "unknown_counterparty"],
            timeout_policy="reject"
        )
        self._policies[trade_policy.policy_id] = trade_policy
        
        # System mode change policy
        mode_policy = ApprovalPolicy(
            policy_id="mode_change_policy",
            approval_types=[ApprovalType.SYSTEM_MODE_CHANGE],
            required_approvers=2,
            approval_threshold=0.7,
            auto_approve_conditions=["downgrade_mode"],
            auto_reject_conditions=["upgrade_to_auto", "upgrade_to_live"],
            timeout_policy="reject"
        )
        self._policies[mode_policy.policy_id] = mode_policy
        
        # Learning activation policy
        learning_policy = ApprovalPolicy(
            policy_id="learning_activation_policy",
            approval_types=[ApprovalType.LEARNING_ACTIVATION],
            required_approvers=1,
            approval_threshold=0.8,
            auto_approve_conditions=["simulation_learning", "low_impact"],
            auto_reject_conditions=["live_learning", "high_impact"],
            timeout_policy="reject"
        )
        self._policies[learning_policy.policy_id] = learning_policy
    
    def enqueue(self, item: Any, **kwargs: Any) -> str:
        """Enqueue an approval request.
        
        Args:
            item: ApprovalRequest or dict with request data
            **kwargs: Additional parameters
            
        Returns:
            The request_id of the enqueued request
        """
        # Convert dict to ApprovalRequest if needed
        if isinstance(item, dict):
            request_data = item
            request_id = request_data.get("request_id", str(uuid.uuid4()))
            
            request = ApprovalRequest(
                request_id=request_id,
                approval_type=ApprovalType(request_data.get("approval_type", "trade_execution")),
                requester_id=request_data.get("requester_id", "system"),
                request_data=request_data.get("request_data", {}),
                priority=ApprovalPriority(request_data.get("priority", "normal")),
                timeout_seconds=request_data.get("timeout_seconds", 3600.0)
            )
        elif isinstance(item, ApprovalRequest):
            request = item
            request_id = request.request_id
        else:
            raise ValueError(f"Invalid item type for approval queue: {type(item)}")
        
        # Check queue capacity
        if len(self._requests) >= self._max_size:
            logger.warning(f"[APPROVAL_QUEUE] Queue at capacity ({self._max_size}), cannot enqueue request")
            raise Exception("Approval queue at capacity")
        
        # Check for auto-approve/auto-reject conditions
        policy = self._get_policy_for_request(request)
        if policy:
            auto_decision = self._check_auto_decision_conditions(request, policy)
            if auto_decision:
                request.status = ApprovalStatus.APPROVED if auto_decision == "approve" else ApprovalStatus.REJECTED
                request.reviewed_by = "system_auto_decision"
                request.reviewed_at = datetime.now()
        
        # Add to queue
        self._requests.append(request)
        self._request_index[request.request_id] = request
        self._decisions[request.request_id] = []
        
        # Update statistics
        self._statistics["total_requests"] += 1
        
        logger.info(f"[APPROVAL_QUEUE] Enqueued request {request_id} (type: {request.approval_type.value}, status: {request.status.value})")
        
        return request_id
    
    def dequeue(self, **kwargs: Any) -> Optional[ApprovalRequest]:
        """Dequeue the next approval request.
        
        Returns:
            The next approval request, or None if queue is empty
        """
        # Process expired requests first
        self._process_expired_requests()
        
        if not self._requests:
            return None
        
        # Get next request (priority-based if specified)
        if kwargs.get("priority_based", False):
            request = self._dequeue_by_priority()
        else:
            request = self._requests.popleft()
        
        # Remove from index
        if request.request_id in self._request_index:
            del self._request_index[request.request_id]
        
        logger.info(f"[APPROVAL_QUEUE] Dequeued request {request.request_id}")
        return request
    
    def _dequeue_by_priority(self) -> ApprovalRequest:
        """Dequeue based on priority ordering."""
        # Sort by priority (critical first)
        priority_order = {
            ApprovalPriority.CRITICAL: 0,
            ApprovalPriority.HIGH: 1,
            ApprovalPriority.NORMAL: 2,
            ApprovalPriority.LOW: 3
        }
        
        sorted_requests = sorted(self._requests, key=lambda r: priority_order.get(r.priority, 999))
        request = sorted_requests[0]
        
        # Remove from queue
        self._requests = deque([r for r in self._requests if r.request_id != request.request_id])
        
        return request
    
    def _process_expired_requests(self):
        """Process expired requests according to timeout policy."""
        expired_requests = []
        
        for request in self._requests:
            if request.is_expired() and request.status == ApprovalStatus.PENDING:
                expired_requests.append(request)
        
        for request in expired_requests:
            policy = self._get_policy_for_request(request)
            if policy:
                if policy.timeout_policy == "reject":
                    request.status = ApprovalStatus.REJECTED
                    request.rejection_reason = "Request expired"
                elif policy.timeout_policy == "approve":
                    request.status = ApprovalStatus.APPPROVED
                    request.reviewed_by = "system_timeout_approve"
                    request.reviewed_at = datetime.now()
                elif policy.timeout_policy == "escalate":
                    self._escalate_request(request)
                
                self._statistics["expired"] += 1
                logger.info(f"[APPROVAL_QUEUE] Request {request.request_id} expired (policy: {policy.timeout_policy})")
    
    def _escalate_request(self, request: ApprovalRequest):
        """Escalate a request to higher-level approvers."""
        policy = self._get_policy_for_request(request)
        if policy and policy.escalation_handlers:
            # In real implementation, would send notifications to escalation handlers
            logger.info(f"[APPROVAL_QUEUE] Escalating request {request.request_id} to {policy.escalation_handlers}")
            request.status = ApprovalStatus.IN_REVIEW
    
    def is_empty(self, **kwargs: Any) -> bool:
        """Check if the queue is empty."""
        return len(self._requests) == 0
    
    def size(self, **kwargs: Any) -> int:
        """Get the current queue size."""
        return len(self._requests)
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a specific request by ID."""
        return self._request_index.get(request_id)
    
    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get all pending requests."""
        return [r for r in self._requests if r.is_pending()]
    
    def get_requests_by_status(self, status: ApprovalStatus) -> List[ApprovalRequest]:
        """Get all requests with a specific status."""
        return [r for r in self._requests if r.status == status]
    
    def get_requests_by_type(self, approval_type: ApprovalType) -> List[ApprovalRequest]:
        """Get all requests of a specific type."""
        return [r for r in self._requests if r.approval_type == approval_type]
    
    def approve_request(self, request_id: str, approver_id: str, 
                      conditions: Optional[List[str]] = None,
                      notes: Optional[str] = None) -> bool:
        """Approve a specific request.
        
        Args:
            request_id: ID of the request to approve
            approver_id: ID of the approver
            conditions: Optional conditions for approval
            notes: Optional notes about the approval
            
        Returns:
            True if approval was successful, False otherwise
        """
        request = self._request_index.get(request_id)
        if not request:
            logger.warning(f"[APPROVAL_QUEUE] Request {request_id} not found")
            return False
        
        if not request.is_pending():
            logger.warning(f"[APPROVAL_QUEUE] Request {request_id} is not pending (status: {request.status.value})")
            return False
        
        # Create approval decision
        decision = ApprovalDecision(
            decision_id=str(uuid.uuid4()),
            request_id=request_id,
            approver_id=approver_id,
            approved=True,
            conditions=conditions or [],
            notes=notes
        )
        
        self._decisions[request_id].append(decision)
        
        # Check if request is fully approved
        if self._check_approval_status(request):
            request.status = ApprovalStatus.APPROVED
            request.reviewed_by = approver_id
            request.reviewed_at = datetime.now()
            request.approval_conditions.extend(conditions or [])
            self._statistics["approved"] += 1
            logger.info(f"[APPROVAL_QUEUE] Request {request_id} approved by {approver_id}")
        
        return True
    
    def reject_request(self, request_id: str, approver_id: str, 
                      reason: Optional[str] = None) -> bool:
        """Reject a specific request.
        
        Args:
            request_id: ID of the request to reject
            approver_id: ID of the approver
            reason: Reason for rejection
            
        Returns:
            True if rejection was successful, False otherwise
        """
        request = self._request_index.get(request_id)
        if not request:
            logger.warning(f"[APPROVAL_QUEUE] Request {request_id} not found")
            return False
        
        if not request.is_pending():
            logger.warning(f"[APPROVAL_QUEUE] Request {request_id} is not pending (status: {request.status.value})")
            return False
        
        # Create rejection decision
        decision = ApprovalDecision(
            decision_id=str(uuid.uuid4()),
            request_id=request_id,
            approver_id=approver_id,
            approved=False,
            notes=reason
        )
        
        self._decisions[request_id].append(decision)
        
        # Check if request should be rejected (single rejection can reject)
        policy = self._get_policy_for_request(request)
        if policy and policy.required_approvers == 1:
            request.status = ApprovalStatus.REJECTED
            request.rejection_reason = reason
            request.reviewed_by = approver_id
            request.reviewed_at = datetime.now()
            self._statistics["rejected"] += 1
            logger.info(f"[APPROVAL_QUEUE] Request {request_id} rejected by {approver_id}: {reason}")
        
        return True
    
    def cancel_request(self, request_id: str, reason: Optional[str] = None) -> bool:
        """Cancel a pending approval request.
        
        Args:
            request_id: ID of the request to cancel
            reason: Reason for cancellation
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        request = self._request_index.get(request_id)
        if not request:
            logger.warning(f"[APPROVAL_QUEUE] Request {request_id} not found")
            return False
        
        if not request.is_pending():
            logger.warning(f"[APPROVAL_QUEUE] Request {request_id} is not pending (status: {request.status.value})")
            return False
        
        request.status = ApprovalStatus.CANCELLED
        request.rejection_reason = reason
        self._statistics["cancelled"] += 1
        
        logger.info(f"[APPROVAL_QUEUE] Request {request_id} cancelled: {reason}")
        return True
    
    def _check_approval_status(self, request: ApprovalRequest) -> bool:
        """Check if a request has sufficient approvals to be approved."""
        decisions = self._decisions.get(request.request_id, [])
        policy = self._get_policy_for_request(request)
        
        if not policy:
            # No policy = simple majority of required approvers
            required = len(decisions)  # All decisions required
        else:
            required = policy.required_approvers
            threshold = policy.approval_threshold
        
        approved_decisions = [d for d in decisions if d.approved]
        
        if len(approved_decisions) >= required:
            # Check threshold if needed
            if threshold < 1.0:
                total_weight = sum(d.decision_weight for d in decisions)
                approved_weight = sum(d.decision_weight for d in approved_decisions)
                if approved_weight / total_weight >= threshold:
                    return True
            else:
                return True
        
        return False
    
    def _get_policy_for_request(self, request: ApprovalRequest) -> Optional[ApprovalPolicy]:
        """Get the applicable policy for a request."""
        for policy in self._policies.values():
            if request.approval_type in policy.approval_types:
                return policy
        return None
    
    def _check_auto_decision_conditions(self, request: ApprovalRequest, 
                                      policy: ApprovalPolicy) -> Optional[str]:
        """Check if request matches auto-approve or auto-reject conditions."""
        request_conditions = request.request_data.get("conditions", [])
        
        # Check auto-approve conditions
        for condition in policy.auto_approve_conditions:
            if condition in request_conditions:
                logger.info(f"[APPROVAL_QUEUE] Auto-approving request {request.request_id} (condition: {condition})")
                return "approve"
        
        # Check auto-reject conditions
        for condition in policy.auto_reject_conditions:
            if condition in request_conditions:
                logger.info(f"[APPROVAL_QUEUE] Auto-rejecting request {request.request_id} (condition: {condition})")
                return "reject"
        
        return None
    
    def add_policy(self, policy: ApprovalPolicy) -> None:
        """Add or update an approval policy."""
        self._policies[policy.policy_id] = policy
        logger.info(f"[APPROVAL_QUEUE] Added/updated policy: {policy.policy_id}")
    
    def get_policy(self, policy_id: str) -> Optional[ApprovalPolicy]:
        """Get a specific approval policy."""
        return self._policies.get(policy_id)
    
    def register_approver(self, approver_id: str, approver_info: Dict[str, Any]) -> None:
        """Register an approver with their information and permissions."""
        self._approvers[approver_id] = {
            "approver_id": approver_id,
            "permissions": approver_info.get("permissions", []),
            "authority_level": approver_info.get("authority_level", "normal"),
            "registered_at": datetime.now(),
            **approver_info
        }
        logger.info(f"[APPROVAL_QUEUE] Registered approver: {approver_id}")
    
    def get_approver(self, approver_id: str) -> Optional[Dict[str, Any]]:
        """Get approver information."""
        return self._approvers.get(approver_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get approval queue statistics."""
        pending_count = len(self._get_pending_requests())
        approved_count = len(self._get_requests_by_status(ApprovalStatus.APPROVED))
        rejected_count = len(self._get_requests_by_status(ApprovalStatus.REJECTED))
        
        return {
            "queue_id": self._queue_id,
            "total_requests": self._statistics["total_requests"],
            "pending_requests": pending_count,
            "approved_requests": approved_count,
            "rejected_requests": rejected_count,
            "expired_requests": self._statistics["expired"],
            "cancelled_requests": self._statistics["cancelled"],
            "queue_size": len(self._requests),
            "utilization": len(self._requests) / self._max_size if self._max_size > 0 else 0.0,
            "total_approvers": len(self._approvers),
            "total_policies": len(self._policies)
        }
    
    def get_queue_summary(self) -> Dict[str, Any]:
        """Get comprehensive queue summary."""
        by_type = {}
        for approval_type in ApprovalType:
            type_count = len(self._get_requests_by_type(approval_type))
            by_type[approval_type.value] = type_count
        
        by_status = {}
        for status in ApprovalStatus:
            status_count = len(self._get_requests_by_status(status))
            by_status[status.value] = status_count
        
        return {
            "queue_id": self._queue_id,
            "queue_size": len(self._requests),
            "requests_by_type": by_type,
            "requests_by_status": by_status,
            "statistics": self.get_statistics(),
            "timestamp": datetime.now()
        }
    
    def rehydrate(self, rows: list, **kwargs: Any) -> None:
        """Rehydrate the approval queue from persisted rows.
        
        Args:
            rows: List of persisted approval request rows
            **kwargs: Additional parameters
        """
        try:
            for row in rows:
                # Convert row to ApprovalRequest
                if isinstance(row, dict):
                    request = ApprovalRequest(
                        request_id=row.get("request_id", str(uuid.uuid4())),
                        approval_type=ApprovalType(row.get("approval_type", "trade_execution")),
                        requester_id=row.get("requester_id", "system"),
                        request_data=row.get("request_data", {}),
                        priority=ApprovalPriority(row.get("priority", "normal")),
                        status=ApprovalStatus(row.get("status", "pending")),
                        timeout_seconds=row.get("timeout_seconds", 3600.0),
                        created_at=datetime.fromisoformat(row.get("created_at", datetime.now().isoformat()))
                    )
                    
                    # Restore decisions if present
                    if "decisions" in row:
                        for dec in row["decisions"]:
                            decision = ApprovalDecision(
                                decision_id=dec.get("decision_id", str(uuid.uuid4())),
                                request_id=request.request_id,
                                approver_id=dec.get("approver_id", "unknown"),
                                approved=dec.get("approved", True),
                                timestamp=datetime.fromisoformat(dec.get("timestamp", datetime.now().isoformat())),
                                conditions=dec.get("conditions", []),
                                notes=dec.get("notes")
                            )
                            self._decisions[request.request_id].append(decision)
                    
                    self._requests.append(request)
                    self._request_index[request.request_id] = request
            
            logger.info(f"[APPROVAL_QUEUE] Rehydrated {len(rows)} requests from persistent storage")
            
        except Exception as e:
            logger.error(f"[APPROVAL_QUEUE] Error during rehydration: {e}")
            raise
    
    def persist_state(self) -> List[Dict[str, Any]]:
        """Persist the current state of the approval queue.
        
        Returns:
            List of serializable request data
        """
        persisted_data = []
        
        for request in self._requests:
            request_data = {
                "request_id": request.request_id,
                "approval_type": request.approval_type.value,
                "requester_id": request.requester_id,
                "request_data": request.request_data,
                "priority": request.priority.value,
                "status": request.status.value,
                "created_at": request.created_at.isoformat(),
                "expires_at": request.expires_at.isoformat() if request.expires_at else None,
                "timeout_seconds": request.timeout_seconds,
                "reviewed_by": request.reviewed_by,
                "reviewed_at": request.reviewed_at.isoformat() if request.reviewed_at else None,
                "review_notes": request.review_notes,
                "approval_conditions": request.approval_conditions,
                "rejection_reason": request.rejection_reason,
                "metadata": request.metadata,
                "decisions": [
                    {
                        "decision_id": d.decision_id,
                        "approver_id": d.approver_id,
                        "approved": d.approved,
                        "timestamp": d.timestamp.isoformat(),
                        "conditions": d.conditions,
                        "notes": d.notes,
                        "decision_weight": d.decision_weight
                    }
                    for d in self._decisions.get(request.request_id, [])
                ]
            }
            persisted_data.append(request_data)
        
        return persisted_data


# Global approval queue instance
_default_approval_queue = None


def get_approval_queue(queue_id: str = "default", **kwargs: Any) -> ApprovalQueue:
    """Get or create the default approval queue instance.
    
    Args:
        queue_id: Unique identifier for the approval queue
        **kwargs: Additional configuration parameters
        
    Returns:
        ApprovalQueue instance
    """
    global _default_approval_queue
    
    if _default_approval_queue is None or _default_approval_queue._queue_id != queue_id:
        _default_approval_queue = ApprovalQueue(queue_id, **kwargs)
    
    return _default_approval_queue


__all__ = [
    "ApprovalStatus",
    "ApprovalPriority",
    "ApprovalType",
    "ApprovalRequest",
    "ApprovalDecision",
    "ApprovalPolicy",
    "ApprovalQueue",
    "get_approval_queue"
]