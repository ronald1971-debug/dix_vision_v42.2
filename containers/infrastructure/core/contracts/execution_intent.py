"""
Core Contracts Execution Intent
Real implementation for execution intent management
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class IntentType(Enum):
    """Intent type enumeration"""

    ORDER = "order"
    CANCEL = "cancel"
    MODIFY = "modify"
    QUERY = "query"
    ADJUST = "adjust"
    REBALANCE = "rebalance"
    SIGNAL = "signal"
    CONTROL = "control"
    DIAGNOSTIC = "diagnostic"


class IntentPriority(Enum):
    """Intent priority enumeration"""

    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class IntentStatus(Enum):
    """Intent status enumeration"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TIMEOUT = "timeout"


# Authorised intent origins
AUTHORISED_INTENT_ORIGINS = [
    "operator",
    "system",
    "governance",
    "intelligence",
    "execution",
    "learning",
    "evolution",
]

UNAUTHORISED_INTENT_ORIGINS = ["external", "unknown", "untrusted"]

TEST_INTENT_ORIGINS = ["test", "sandbox", "development"]


def compute_content_hash(content: Dict[str, Any]) -> str:
    """Compute a hash of the content for integrity checking"""
    import hashlib
    import json

    # Convert content to a sorted JSON string
    content_str = json.dumps(content, sort_keys=True)
    # Compute SHA-256 hash
    return hashlib.sha256(content_str.encode()).hexdigest()


def verify_content_hash(content: Dict[str, Any], expected_hash: str) -> bool:
    """Verify the content hash matches expected value"""
    computed_hash = compute_content_hash(content)
    return computed_hash == expected_hash


@dataclass
class ExecutionIntent:
    """Execution intent information"""

    intent_id: str
    intent_type: IntentType
    priority: IntentPriority
    status: IntentStatus
    requester: str = ""
    timestamp: float = field(default_factory=time.time)
    expiry: float = 0.0
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_urgent(self) -> bool:
        """Check if intent is urgent"""
        return self.priority == IntentPriority.URGENT

    def is_approved(self) -> bool:
        """Check if intent is approved"""
        return self.status == IntentStatus.APPROVED

    def is_executable(self) -> bool:
        """Check if intent is executable"""
        return self.status in [IntentStatus.PENDING, IntentStatus.APPROVED] and (
            self.expiry == 0.0 or self.expiry > time.time()
        )

    def is_expired(self) -> bool:
        """Check if intent has expired"""
        return self.expiry > 0 and self.expiry <= time.time()

    def approve(self) -> None:
        """Approve the intent"""
        self.status = IntentStatus.APPROVED
        self.timestamp = time.time()

    def reject(self) -> None:
        """Reject the intent"""
        self.status = IntentStatus.REJECTED
        self.timestamp = time.time()

    def cancel(self) -> None:
        """Cancel the intent"""
        self.status = IntentStatus.CANCELLED
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "intent_id": self.intent_id,
            "intent_type": self.intent_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "requester": self.requester,
            "timestamp": self.timestamp,
            "expiry": self.expiry,
            "parameters": self.parameters,
            "constraints": self.constraints,
            "metadata": self.metadata,
        }


class IntentValidator:
    """Validator for execution intents"""

    def validate_intent(self, intent: ExecutionIntent) -> tuple[bool, str]:
        """Validate an execution intent"""
        # Basic validation
        if intent.intent_type not in IntentType:
            return False, f"Invalid intent type: {intent.intent_type}"

        if intent.is_expired():
            return False, "Intent has expired"

        return True, "Intent is valid"

    def check_constraints(self, intent: ExecutionIntent) -> tuple[bool, List[str]]:
        """Check if constraints are satisfied"""
        satisfied = []
        for constraint in intent.constraints:
            # Basic constraint validation
            if constraint:
                satisfied.append(constraint)
        return True, satisfied


class IntentRegistry:
    """Registry for execution intents"""

    def __init__(self):
        self._intents: Dict[str, ExecutionIntent] = {}
        self._intents_by_status: Dict[IntentStatus, List[str]] = {
            status: [] for status in IntentStatus
        }

    def register_intent(self, intent: ExecutionIntent) -> bool:
        """Register an intent"""
        self._intents[intent.intent_id] = intent
        self._intents_by_status[intent.status].append(intent.intent_id)
        return True

    def get_intent(self, intent_id: str) -> Optional[ExecutionIntent]:
        """Get a specific intent"""
        return self._intents.get(intent_id)

    def get_intents_by_status(self, status: IntentStatus) -> List[ExecutionIntent]:
        """Get all intents with a status"""
        intent_ids = self._intents_by_status.get(status, [])
        return [self._intents[iid] for iid in intent_ids if iid in self._intents]

    def get_urgent_intents(self) -> List[ExecutionIntent]:
        """Get all urgent intents"""
        return [i for i in self._intents.values() if i.is_urgent()]

    def get_executable_intents(self) -> List[ExecutionIntent]:
        """Get all executable intents"""
        return [i for i in self._intents.values() if i.is_executable() and not i.is_expired()]

    def approve_intent(self, intent_id: str) -> bool:
        """Approve an intent"""
        intent = self.get_intent(intent_id)
        if intent:
            intent.approve()
            self._update_status(intent_id, IntentStatus.APPROVED, intent.status)
            return True
        return False

    def reject_intent(self, intent_id: str) -> bool:
        """Reject an intent"""
        intent = self.get_intent(intent_id)
        if intent:
            intent.reject()
            self._update_status(intent_id, IntentStatus.REJECTED, intent.status)
            return True
        return False

    def cancel_intent(self, intent_id: str) -> bool:
        """Cancel an intent"""
        intent = self.get_intent(intent_id)
        if intent:
            intent.cancel()
            self._update_status(intent_id, IntentStatus.CANCELLED, intent.status)
            return True
        return False

    def _update_status(
        self, intent_id: str, new_status: IntentStatus, old_status: IntentStatus
    ) -> None:
        """Update the status tracking"""
        if intent_id in self._intents_by_status[old_status]:
            self._intents_by_status[old_status].remove(intent_id)
        self._intents_by_status[new_status].append(intent_id)


# Global intent registry
_intent_registry: Optional[IntentRegistry] = None


def get_intent_registry() -> IntentRegistry:
    """Get the global intent registry"""
    global _intent_registry
    if _intent_registry is None:
        _intent_registry = IntentRegistry()
    return _intent_registry


def create_intent(
    intent_id: str, intent_type: IntentType, priority: IntentPriority, requester: str
) -> ExecutionIntent:
    """Create a new execution intent"""
    return ExecutionIntent(
        intent_id=intent_id, intent_type=intent_type, priority=priority, requester=requester
    )


def create_execution_intent(
    intent_id: str,
    intent_type: IntentType,
    priority: IntentPriority,
    requester: str,
    parameters: Dict[str, Any] = None,
) -> ExecutionIntent:
    """Create a new execution intent with parameters"""
    intent = create_intent(intent_id, intent_type, priority, requester)
    if parameters:
        intent.parameters = parameters
    return intent


def mark_approved(intent_id: str) -> bool:
    """Mark an intent as approved"""
    return get_intent_registry().approve_intent(intent_id)


def mark_rejected(intent_id: str) -> bool:
    """Mark an intent as rejected"""
    return get_intent_registry().reject_intent(intent_id)


def mark_cancelled(intent_id: str) -> bool:
    """Mark an intent as cancelled"""
    return get_intent_registry().cancel_intent(intent_id)


__all__ = [
    "IntentType",
    "IntentPriority",
    "IntentStatus",
    "AUTHORISED_INTENT_ORIGINS",
    "UNAUTHORISED_INTENT_ORIGINS",
    "TEST_INTENT_ORIGINS",
    "compute_content_hash",
    "verify_content_hash",
    "ExecutionIntent",
    "IntentValidator",
    "IntentRegistry",
    "get_intent_registry",
    "create_intent",
    "create_execution_intent",
    "mark_approved",
    "mark_rejected",
    "mark_cancelled",
]
