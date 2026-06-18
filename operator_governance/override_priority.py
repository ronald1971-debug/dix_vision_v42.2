"""
Operator Governance Override Priority - Override Priority Management
Provides override priority capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class OverridePriority(Enum):
    """Override priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class OverridePriorityManager:
    """Manager for override priority operations"""
    
    def __init__(self):
        self._priorities = {}
        
    def set_priority(self, operation: str, priority: OverridePriority):
        """Set priority for an operation"""
        self._priorities[operation] = priority
        
    def get_priority(self, operation: str) -> Optional[OverridePriority]:
        """Get priority for an operation"""
        return self._priorities.get(operation)
        
    def compare_priorities(self, op_a: str, op_b: str) -> int:
        """Compare priorities of two operations (-1, 0, 1)"""
        priority_a = self.get_priority(op_a)
        priority_b = self.get_priority(op_b)
        if not priority_a or not priority_b:
            return 0
        priority_order = [OverridePriority.LOW, OverridePriority.MEDIUM, OverridePriority.HIGH, OverridePriority.CRITICAL]
        return priority_order.index(priority_a) - priority_order.index(priority_b)

_override_priority_manager = None

def get_override_priority_manager() -> OverridePriorityManager:
    """Get override priority manager instance"""
    global _override_priority_manager
    if _override_priority_manager is None:
        _override_priority_manager = OverridePriorityManager()
    return _override_priority_manager

__all__ = ['OverridePriority', 'OverridePriorityManager', 'get_override_priority_manager']