"""
Execution Unified Core Protections Feedback - Feedback Protection Infrastructure
Provides feedback-based protection capabilities
NO LAZY LOADING - All components load directly
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class FeedbackProtection:
    """Feedback-based protection for execution"""

    def __init__(self):
        self._feedback_history = []

    def add_feedback(self, feedback_data: Dict[str, Any]):
        """Add feedback for protection tuning"""
        self._feedback_history.append(feedback_data)

    def get_feedback_count(self) -> int:
        """Get feedback count"""
        return len(self._feedback_history)


class FeedbackCollector:
    """Collector for execution feedback"""

    def __init__(self):
        self._collector = FeedbackProtection()

    def collect(self, feedback_data: Dict[str, Any]):
        """Collect feedback data"""
        self._collector.add_feedback(feedback_data)


__all__ = ["FeedbackProtection", "FeedbackCollector"]
