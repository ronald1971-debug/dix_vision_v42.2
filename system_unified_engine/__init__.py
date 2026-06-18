"""
System Unified Engine - System Engine Infrastructure
Provides system engine capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class SystemUnifiedEngine:
    """System unified engine for system operations"""
    
    def __init__(self):
        self._running = False
        self._components = {}
        
    async def start(self) -> bool:
        """Start system engine"""
        self._running = True
        return True
    
    async def stop(self):
        """Stop system engine"""
        self._running = False
    
    def register_component(self, component_id: str, component: Any) -> bool:
        """Register system component"""
        self._components[component_id] = component
        return True
    
    def get_component(self, component_id: str) -> Optional[Any]:
        """Get system component"""
        return self._components.get(component_id)
    
    def is_running(self) -> bool:
        """Check if engine is running"""
        return self._running

from .authority import SystemAuthority, get_system_authority
from .authority_matrix import AuthorityMatrix
from .coupling import CouplingManager, get_coupling_manager, HazardThrottleAdapter

# Global instance
_system_authority = None

def get_system_authority() -> SystemAuthority:
    """Get system authority instance"""
    global _system_authority
    if _system_authority is None:
        _system_authority = SystemAuthority()
    return _system_authority

__all__ = [
    'SystemUnifiedEngine',
    'SystemAuthority',
    'AuthorityMatrix',
    'get_system_authority'
]