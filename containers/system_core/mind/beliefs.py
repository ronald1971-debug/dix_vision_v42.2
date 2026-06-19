"""
Mind Beliefs - Belief System Module
Provides belief system capabilities for cognitive operations
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Belief:
    """Belief data structure"""
    belief_id: str
    content: str
    confidence: float
    source: str = ""
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = int(__import__('datetime').datetime.now().timestamp() * 1_000_000_000)

class BeliefSystem:
    """Belief system for managing beliefs"""
    
    def __init__(self):
        self._beliefs: Dict[str, Belief] = {}
        
    def add_belief(self, belief: Belief):
        """Add belief to system"""
        self._beliefs[belief.belief_id] = belief
        
    def get_belief(self, belief_id: str) -> Optional[Belief]:
        """Get belief by ID"""
        return self._beliefs.get(belief_id)
        
    def get_all_beliefs(self) -> List[Belief]:
        """Get all beliefs"""
        return list(self._beliefs.values())

# Global instance
_belief_system = None

def get_belief_system() -> BeliefSystem:
    """Get belief system instance"""
    global _belief_system
    if _belief_system is None:
        _belief_system = BeliefSystem()
    return _belief_system

__all__ = ['Belief', 'BeliefSystem', 'get_belief_system']