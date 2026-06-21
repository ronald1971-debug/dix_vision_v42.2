"""
Execution Unified Core Semi-Auto Approval Queue
Real implementation for approval queue management
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
import time
from queue import Queue, Empty
import threading

class ApprovalStatus(Enum):
    """Approval status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

@dataclass
class ApprovalItem:
    """Approval item in queue"""
    item_id: str
    request_type: str
    request_data: Dict[str, Any] = field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    priority: int = 0
    submitted_by: str = ""
    submitted_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ApprovalDecision:
    """Approval decision"""
    decision_id: str
    item_id: str
    approved: bool
    approver: str = ""
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ApprovalQueue:
    """Approval queue manager"""
    
    def __init__(self):
        self._queue: Queue = Queue()
        self._items: Dict[str, ApprovalItem] = {}
        self._decisions: Dict[str, ApprovalDecision] = {}
        self._lock = threading.Lock()
    
    def submit(self, item: ApprovalItem) -> str:
        """Submit item for approval"""
        with self._lock:
            self._items[item.item_id] = item
            self._queue.put(item)
            return item.item_id
    
    def get_next(self) -> Optional[ApprovalItem]:
        """Get next item from queue"""
        try:
            return self._queue.get(timeout=1.0)
        except Empty:
            return None
    
    def approve(self, decision: ApprovalDecision) -> bool:
        """Approve or reject an item"""
        with self._lock:
            if decision.item_id not in self._items:
                return False
            
            item = self._items[decision.item_id]
            item.status = ApprovalStatus.APPROVED if decision.approved else ApprovalStatus.REJECTED
            self._decisions[decision.decision_id] = decision
            return True
    
    def get_status(self, item_id: str) -> Optional[ApprovalStatus]:
        """Get approval status for an item"""
        with self._lock:
            item = self._items.get(item_id)
            return item.status if item else None
    
    def get_pending_items(self) -> List[ApprovalItem]:
        """Get all pending items"""
        with self._lock:
            return [item for item in self._items.values() if item.status == ApprovalStatus.PENDING]
    
    def cancel(self, item_id: str) -> bool:
        """Cancel a pending approval"""
        with self._lock:
            if item_id not in self._items:
                return False
            
            item = self._items[item_id]
            if item.status == ApprovalStatus.PENDING:
                item.status = ApprovalStatus.CANCELLED
                return True
            return False

def get_approval_queue() -> ApprovalQueue:
    """Get the global approval queue"""
    return ApprovalQueue()

__all__ = [
    "ApprovalStatus",
    "ApprovalItem",
    "ApprovalDecision",
    "ApprovalQueue",
    "get_approval_queue"
]
