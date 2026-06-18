"""
System Unified Engine Coupling - Coupling Management
Provides system coupling capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CouplingManager:
    """Manager for system coupling and decoupling operations"""
    
    def __init__(self):
        self._coupled_components = {}
        self._decoupled_components = {}
        
    def couple_components(self, component_a: str, component_b: str, coupling_strength: float = 1.0):
        """Couple two system components"""
        coupling_id = f"{component_a}_{component_b}"
        self._coupled_components[coupling_id] = {
            'component_a': component_a,
            'component_b': component_b,
            'strength': coupling_strength
        }
        
    def decouple_components(self, component_a: str, component_b: str):
        """Decouple two system components"""
        coupling_id = f"{component_a}_{component_b}"
        if coupling_id in self._coupled_components:
            del self._coupled_components[coupling_id]
            self._decoupled_components[coupling_id] = True

_coupling_manager = None

def get_coupling_manager() -> CouplingManager:
    """Get coupling manager instance"""
    global _coupling_manager
    if _coupling_manager is None:
        _coupling_manager = CouplingManager()
    return _coupling_manager

class HazardThrottleAdapter:
    """Adapter for hazard throttling operations"""
    
    def __init__(self):
        self._throttle_active = False
        self._throttle_threshold = 1.0
        
    def set_throttle_threshold(self, threshold: float):
        """Set throttle threshold"""
        self._throttle_threshold = threshold
        
    def should_throttle(self, hazard_level: float) -> bool:
        """Check if operation should be throttled"""
        return hazard_level > self._throttle_threshold

__all__ = ['CouplingManager', 'get_coupling_manager', 'HazardThrottleAdapter']