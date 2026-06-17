"""
world_model.desktop_agent_integration
DIX VISION v42.2 — Desktop Agent World Model Integration

Integration adapter to connect Desktop Agent to the Shared Reality Layer.
Allows Desktop Agent to access world model state and contribute updates.
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


class DesktopAgentWorldIntegration:
    """
    Integration layer for Desktop Agent to access Shared Reality Layer.
    
    Provides:
    - Registration with shared reality layer
    - World state access for desktop operations
    - Desktop activity updates to world model
    - Permission management for desktop operations
    """
    
    def __init__(self, agent_id: str = "desktop_agent_primary"):
        self._agent_id = agent_id
        self._shared_reality: Optional[SharedRealityLayer] = None
        self._world_view: Optional[SystemWorldView] = None
        
        # Desktop-specific components
        self._relevant_components = [
            "agent_models",  # Desktop agent model
            "environment_state",  # Desktop environment
            "predictions",  # User activity predictions
        ]
        
        # Desktop permissions
        self._permissions = {
            "agent_models": ["read", "write"],
            "environment_state": ["read", "write"],
            "predictions": ["read"]
        }
        
        logger.info(f"[DESKTOP_AGENT_INTEGRATION] Desktop Agent integration initialized for {agent_id}")
    
    def connect_to_shared_reality(self, world_model_orchestrator) -> None:
        """Connect to the shared reality layer."""
        shared_reality = get_shared_reality_layer()
        
        # Only initialize if not already initialized
        if shared_reality._world_model_orchestrator is None:
            shared_reality.initialize_world_model(world_model_orchestrator)
        
        # Register desktop agent
        self._world_view = shared_reality.register_system(
            system_type=SystemType.DESKTOP_AGENT,
            system_id=self._agent_id,
            relevant_components=self._relevant_components,
            permissions=self._permissions
        )
        
        self._shared_reality = shared_reality
        logger.info(f"[DESKTOP_AGENT_INTEGRATION] Desktop agent connected to shared reality")
    
    def get_world_state(self) -> Dict[str, Any]:
        """Get world state relevant to desktop agent."""
        if self._shared_reality:
            return self._shared_reality.get_shared_state(
                SystemType.DESKTOP_AGENT,
                self._agent_id
            )
        return {}
    
    def update_desktop_activity(self, activity_data: Dict[str, Any]) -> bool:
        """Update world model with desktop activity."""
        if self._shared_reality:
            # Update agent_models component with desktop activity
            return self._shared_reality.update_shared_state(
                system_type=SystemType.DESKTOP_AGENT,
                system_id=self._agent_id,
                component="agent_models",
                update_data=activity_data,
                update_type="INCREMENTAL"
            )
        return False
    
    def get_user_predictions(self) -> Dict[str, Any]:
        """Get predictions about user activity from world model."""
        world_state = self.get_world_state()
        return world_state.get("predictions", {})
    
    def report_desktop_environment(self, env_data: Dict[str, Any]) -> bool:
        """Report desktop environment state to world model."""
        if self._shared_reality:
            return self._shared_reality.update_shared_state(
                system_type=SystemType.DESKTOP_AGENT,
                system_id=self._agent_id,
                component="environment_state",
                update_data=env_data,
                update_type="INCREMENTAL"
            )
        return False
    
    def subscribe_to_world_updates(self, callback: callable) -> None:
        """Subscribe to world model updates."""
        if self._shared_reality:
            self._shared_reality.subscribe_to_updates(
                system_type=SystemType.DESKTOP_AGENT,
                system_id=self._agent_id,
                components=self._relevant_components,
                callback=callback
            )
            logger.info("[DESKTOP_AGENT_INTEGRATION] Subscribed to world updates")


# Singleton instance
_desktop_agent_integration: Optional[DesktopAgentWorldIntegration] = None
_desktop_agent_lock = threading.Lock()

def get_desktop_agent_integration(agent_id: str = "desktop_agent_primary") -> DesktopAgentWorldIntegration:
    """Get the singleton desktop agent integration instance."""
    global _desktop_agent_integration
    if _desktop_agent_integration is None:
        with _desktop_agent_lock:
            if _desktop_agent_integration is None:
                _desktop_agent_integration = DesktopAgentWorldIntegration(agent_id)
    return _desktop_agent_integration


__all__ = [
    "DesktopAgentWorldIntegration",
    "get_desktop_agent_integration",
]