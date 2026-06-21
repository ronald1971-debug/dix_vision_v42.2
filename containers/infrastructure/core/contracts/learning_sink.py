"""
Core Contracts Learning Sink
Real implementation for learning feedback sink
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time

class FeedbackKind(Enum):
    """Feedback kind enumeration"""
    REWARD = "reward"
    PUNISHMENT = "punishment"
    CORRECTIVE = "corrective"
    REINFORCEMENT = "reinforcement"
    EXPLORATION = "exploration"
    DIAGNOSTIC = "diagnostic"
    POLICY = "policy"
    VALUE = "value"

class FeedbackPriority(Enum):
    """Feedback priority enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class FeedbackStatus(Enum):
    """Feedback status enumeration"""
    PENDING = "pending"
    PROCESSED = "processed"
    IGNORED = "ignored"
    ERROR = "error"

@dataclass
class IntelligenceFeedback:
    """Intelligence feedback information"""
    feedback_id: str
    feedback_kind: FeedbackKind
    priority: FeedbackPriority
    source: str
    status: FeedbackStatus = FeedbackStatus.PENDING
    timestamp: float = field(default_factory=time.time)
    value: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_critical(self) -> bool:
        """Check if feedback is critical"""
        return self.priority == FeedbackPriority.CRITICAL
    
    def is_processed(self) -> bool:
        """Check if feedback is processed"""
        return self.status == FeedbackStatus.PROCESSED
    
    def mark_processed(self) -> None:
        """Mark feedback as processed"""
        self.status = FeedbackStatus.PROCESSED
        self.timestamp = time.time()
    
    def mark_ignored(self) -> None:
        """Mark feedback as ignored"""
        self.status = FeedbackStatus.IGNORED
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "feedback_id": self.feedback_id,
            "feedback_kind": self.feedback_kind.value,
            "priority": self.priority.value,
            "source": self.source,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "value": self.value,
            "context": self.context,
            "metadata": self.metadata
        }

class IntelligenceFeedbackSink:
    """Sink for intelligence feedback"""
    
    def __init__(self):
        self._feedback_buffer: List[IntelligenceFeedback] = []
        self._processed_feedback: List[IntelligenceFeedback] = []
        self._max_buffer_size = 1000
    
    def receive_feedback(self, feedback: IntelligenceFeedback) -> bool:
        """Receive feedback"""
        if len(self._feedback_buffer) >= self._max_buffer_size:
            return False
        self._feedback_buffer.append(feedback)
        return True
    
    def process_feedback(self) -> List[IntelligenceFeedback]:
        """Process all pending feedback"""
        processed = []
        for feedback in self._feedback_buffer:
            feedback.mark_processed()
            processed.append(feedback)
            self._processed_feedback.append(feedback)
        self._feedback_buffer.clear()
        return processed
    
    def get_pending_feedback(self) -> List[IntelligenceFeedback]:
        """Get all pending feedback"""
        return self._feedback_buffer.copy()
    
    def get_processed_feedback(self) -> List[IntelligenceFeedback]:
        """Get all processed feedback"""
        return self._processed_feedback.copy()
    
    def clear_processed(self) -> None:
        """Clear processed feedback"""
        self._processed_feedback.clear()
    
    def get_feedback_count(self) -> Dict[str, int]:
        """Get feedback counts by status"""
        return {
            "pending": len(self._feedback_buffer),
            "processed": len(self._processed_feedback)
        }

# Global feedback sink
_intelligence_feedback_sink: Optional[IntelligenceFeedbackSink] = None

def get_intelligence_feedback_sink() -> IntelligenceFeedbackSink:
    """Get the global intelligence feedback sink"""
    global _intelligence_feedback_sink
    if _intelligence_feedback_sink is None:
        _intelligence_feedback_sink = IntelligenceFeedbackSink()
    return _intelligence_feedback_sink

def create_feedback(feedback_id: str, feedback_kind: FeedbackKind, source: str, value: float) -> IntelligenceFeedback:
    """Create a new intelligence feedback"""
    return IntelligenceFeedback(
        feedback_id=feedback_id,
        feedback_kind=feedback_kind,
        priority=FeedbackPriority.NORMAL,
        source=source,
        value=value
    )

__all__ = [
    "FeedbackKind",
    "FeedbackPriority",
    "FeedbackStatus",
    "IntelligenceFeedback",
    "IntelligenceFeedbackSink",
    "get_intelligence_feedback_sink",
    "create_feedback"
]