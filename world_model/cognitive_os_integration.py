"""
world_model.cognitive_os_integration
DIX VISION v42.2 — Cognitive OS World Model Integration

Integration adapter to connect Cognitive OS to the Shared Reality Layer.
Allows Cognitive OS to access world model state for cognitive processing and reasoning.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Optional

from world_model.shared_reality_layer import (
    SharedRealityLayer,
    get_shared_reality_layer,
    SystemType,
    SystemWorldView
)

logger = logging.getLogger(__name__)


class CognitiveOSWorldIntegration:
    """
    Integration layer for Cognitive OS to access Shared Reality Layer.
    
    Provides:
    - Registration with shared reality layer
    - World state access for cognitive processing
    - Cognitive state updates to world model
    - Semantic understanding of world state
    - Memory updates from cognitive processes
    """
    
    def __init__(self, cognitive_os_id: str = "cognitive_os_primary"):
        self._cognitive_os_id = cognitive_os_id
        self._shared_reality: Optional[SharedRealityLayer] = None
        self._world_view: Optional[SystemWorldView] = None
        
        # Cognitive OS-specific components
        self._relevant_components = [
            "market_state",  # Market understanding
            "agent_models",  # Agent mental models
            "causal_structure",  # Causal reasoning
            "environment_state",  # Environment understanding
            "dynamics",  # Temporal reasoning
            "predictions",  # Predictive modeling
        ]
        
        # Cognitive OS permissions
        self._permissions = {
            "market_state": ["read"],
            "agent_models": ["read", "write"],  # Can update mental models
            "causal_structure": ["read", "write"],  # Can update causal understanding
            "environment_state": ["read"],
            "dynamics": ["read"],
            "predictions": ["read", "write"]  # Can update predictions from cognitive processes
        }
        
        logger.info(f"[COGNITIVE_OS_INTEGRATION] Cognitive OS integration initialized for {cognitive_os_id}")
    
    def connect_to_shared_reality(self, world_model_orchestrator) -> None:
        """Connect to the shared reality layer."""
        shared_reality = get_shared_reality_layer()
        
        # Only initialize if not already initialized
        if shared_reality._world_model_orchestrator is None:
            shared_reality.initialize_world_model(world_model_orchestrator)
        
        # Register cognitive OS
        self._world_view = shared_reality.register_system(
            system_type=SystemType.COGNITIVE_OS,
            system_id=self._cognitive_os_id,
            relevant_components=self._relevant_components,
            permissions=self._permissions
        )
        
        self._shared_reality = shared_reality
        logger.info(f"[COGNITIVE_OS_INTEGRATION] Cognitive OS connected to shared reality")
    
    def get_world_state_for_cognitive_processing(self) -> Dict[str, Any]:
        """Get world state needed for cognitive processing."""
        if self._shared_reality:
            return self._shared_reality.get_shared_state(
                SystemType.COGNITIVE_OS,
                self._cognitive_os_id
            )
        return {}
    
    def update_causal_understanding(self, causal_updates: Dict[str, Any]) -> bool:
        """Update world model with new causal understanding."""
        if self._shared_reality:
            return self._shared_reality.update_shared_state(
                system_type=SystemType.COGNITIVE_OS,
                system_id=self._cognitive_os_id,
                component="causal_structure",
                update_data=causal_updates,
                update_type="INCREMENTAL"
            )
        return False
    
    def update_agent_mental_models(self, mental_model_updates: Dict[str, Any]) -> bool:
        """Update world model with refined agent mental models."""
        if self._shared_reality:
            return self._shared_reality.update_shared_state(
                system_type=SystemType.COGNITIVE_OS,
                system_id=self._cognitive_os_id,
                component="agent_models",
                update_data=mental_model_updates,
                update_type="INCREMENTAL"
            )
        return False
    
    def update_cognitive_predictions(self, predictions: Dict[str, Any]) -> bool:
        """Update world model with cognitive predictions."""
        if self._shared_reality:
            return self._shared_reality.update_shared_state(
                system_type=SystemType.COGNITIVE_OS,
                system_id=self._cognitive_os_id,
                component="predictions",
                update_data=predictions,
                update_type="INCREMENTAL"
            )
        return False
    
    def get_causal_dependencies(self) -> Dict[str, Any]:
        """Get causal dependencies for cognitive reasoning."""
        world_state = self.get_world_state_for_cognitive_processing()
        return world_state.get("causal_structure", {})
    
    def get_market_dynamics_for_reasoning(self) -> Dict[str, Any]:
        """Get market dynamics for temporal reasoning."""
        world_state = self.get_world_state_for_cognitive_processing()
        return world_state.get("dynamics", {})
    
    def subscribe_to_world_updates(self, callback: callable) -> None:
        """Subscribe to world model updates for cognitive processing."""
        if self._shared_reality:
            self._shared_reality.subscribe_to_updates(
                system_type=SystemType.COGNITIVE_OS,
                system_id=self._cognitive_os_id,
                components=self._relevant_components,
                callback=callback
            )
            logger.info("[COGNITIVE_OS_INTEGRATION] Subscribed to world updates for cognitive processing")


# Singleton instance
_cognitive_os_integration: Optional[CognitiveOSWorldIntegration] = None
_cognitive_os_lock = threading.Lock()

def get_cognitive_os_integration(cognitive_os_id: str = "cognitive_os_primary") -> CognitiveOSWorldIntegration:
    """Get the singleton cognitive OS integration instance."""
    global _cognitive_os_integration
    if _cognitive_os_integration is None:
        with _cognitive_os_lock:
            if _cognitive_os_integration is None:
                _cognitive_os_integration = CognitiveOSWorldIntegration(cognitive_os_id)
    return _cognitive_os_integration


__all__ = [
    "CognitiveOSWorldIntegration",
    "get_cognitive_os_integration",
]