"""
System Unified State - State Management Infrastructure
Provides state management capabilities
NO LAZY LOADING - All components load directly
"""

import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class State:
    """State data structure"""
    state_id: str
    data: Dict[str, Any]
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = datetime.now().timestamp_ns()

class StateManager:
    """State manager for system state operations"""
    
    def __init__(self):
        self._states: Dict[str, State] = {}
        self._current_state = "initial"
        
    def set_state(self, state_id: str, data: Optional[Dict[str, Any]] = None):
        """Set current state"""
        if data is None:
            data = {}
            
        state = State(
            state_id=state_id,
            data=data
        )
        
        self._states[state_id] = state
        self._current_state = state_id
        
    def get_state(self, state_id: str) -> Optional[State]:
        """Get state by ID"""
        return self._states.get(state_id)
    
    def get_current_state(self) -> str:
        """Get current state ID"""
        return self._current_state
    
    def get_current_state_data(self) -> Dict[str, Any]:
        """Get current state data"""
        state = self._states.get(self._current_state)
        if state:
            return state.data
        return {}
    
    def get_all_states(self) -> Dict[str, State]:
        """Get all states"""
        return self._states.copy()

# Global instance
_state_manager = None

def get_state_manager() -> StateManager:
    """Get global state manager instance"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager

def set_state(state_id: str, data: Optional[Dict[str, Any]] = None):
    """Set state (convenience function)"""
    manager = get_state_manager()
    manager.set_state(state_id, data)

def get_state(state_id: str) -> Optional[State]:
    """Get state (convenience function)"""
    manager = get_state_manager()
    return manager.get_state(state_id)

def get_current_state() -> str:
    """Get current state (convenience function)"""
    manager = get_state_manager()
    return manager.get_current_state()

__all__ = [
    'State',
    'StateManager',
    'get_state_manager',
    'set_state',
    'get_state',
    'get_current_state'
]