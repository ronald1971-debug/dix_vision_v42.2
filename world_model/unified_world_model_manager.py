"""
world_model.unified_world_model_manager
DIX VISION v42.2 — Unified World Model Manager

Central manager for the unified world model system that serves as the shared
reality layer for all cognitive systems (INDIRA, DYON, Desktop Agent, Governance, etc.).
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from world_model.orchestrator import WorldModelOrchestrator, get_world_model_orchestrator
from world_model.shared_reality_layer import SharedRealityLayer, get_shared_reality_layer, SystemType
from world_model.desktop_agent_integration import get_desktop_agent_integration
from world_model.governance_integration import get_governance_integration
from world_model.execution_integration import get_execution_integration
from world_model.cognitive_os_integration import get_cognitive_os_integration

logger = logging.getLogger(__name__)


@dataclass
class UnifiedWorldModelState:
    """State of the unified world model system."""
    world_model_active: bool = False
    shared_reality_active: bool = False
    desktop_agent_connected: bool = False
    governance_connected: bool = False
    execution_connected: bool = False
    cognitive_os_connected: bool = False
    total_systems_registered: int = 0
    active_subscriptions: int = 0
    conflict_count: int = 0


class UnifiedWorldModelManager:
    """
    Unified manager for the World Model as Shared Reality Layer.
    
    Responsibilities:
    - Initialize world model orchestrator
    - Initialize shared reality layer
    - Connect all cognitive systems to shared reality
    - Manage system registrations
    - Monitor conflicts and resolution
    - Provide unified access point for all systems
    """
    
    def __init__(self):
        self._world_model_orchestrator: Optional[WorldModelOrchestrator] = None
        self._shared_reality: Optional[SharedRealityLayer] = None
        
        # Integration adapters
        self._desktop_agent_integration = None
        self._governance_integration = None
        _execution_integration = None
        self._cognitive_os_integration = None
        
        logger.info("[UNIFIED_WORLD_MODEL_MANAGER] Manager initialized")
    
    def initialize_unified_world_model(self) -> UnifiedWorldModelState:
        """Initialize the unified world model system."""
        logger.info("[UNIFIED_WORLD_MODEL_MANAGER] Initializing unified world model")
        
        # Step 1: Initialize world model orchestrator
        self._world_model_orchestrator = get_world_model_orchestrator()
        logger.info("[UNIFIED_WORLD_MODEL_MANAGER] World model orchestrator initialized")
        
        # Step 2: Initialize shared reality layer
        self._shared_reality = get_shared_reality_layer()
        self._shared_reality.initialize_world_model(self._world_model_orchestrator)
        logger.info("[UNIFIED_WORLD_MODEL_MANAGER] Shared reality layer initialized")
        
        # Step 3: Connect cognitive systems
        self._connect_all_systems()
        
        # Get final state
        state = self.get_system_state()
        
        logger.info(f"[UNIFIED_WORLD_MODEL_MANAGER] Unified world model initialized with {state.total_systems_registered} systems")
        
        return state
    
    def _connect_all_systems(self) -> None:
        """Connect all cognitive systems to shared reality layer."""
        # Connect Desktop Agent
        self._desktop_agent_integration = get_desktop_agent_integration()
        self._desktop_agent_integration.connect_to_shared_reality(self._world_model_orchestrator)
        
        # Connect Governance
        self._governance_integration = get_governance_integration()
        self._governance_integration.connect_to_shared_reality(self._world_model_orchestrator)
        
        # Connect Execution
        self._execution_integration = get_execution_integration()
        self._execution_integration.connect_to_shared_reality(self._world_model_orchestrator)
        
        # Connect Cognitive OS
        self._cognitive_os_integration = get_cognitive_os_integration()
        self._cognitive_os_integration.connect_to_shared_reality(self._world_model_orchestrator)
        
        logger.info("[UNIFIED_WORLD_MODEL_MANAGER] All systems connected to shared reality")
    
    def get_system_state(self) -> UnifiedWorldModelState:
        """Get the state of the unified world model system."""
        shared_reality_stats = self._shared_reality.get_system_statistics() if self._shared_reality else {}
        
        # Calculate total systems registered by summing counts from all system types
        registered_systems = shared_reality_stats.get("registered_systems", {})
        total_systems = sum(system_data.get("count", 0) for system_data in registered_systems.values())
        
        state = UnifiedWorldModelState(
            world_model_active=self._world_model_orchestrator is not None,
            shared_reality_active=self._shared_reality is not None,
            desktop_agent_connected=self._desktop_agent_integration is not None,
            governance_connected=self._governance_integration is not None,
            execution_connected=self._execution_integration is not None,
            cognitive_os_connected=self._cognitive_os_integration is not None,
            total_systems_registered=total_systems,
            active_subscriptions=shared_reality_stats.get("active_subscriptions", 0),
            conflict_count=shared_reality_stats.get("conflict_count", 0)
        )
        
        return state
    
    def get_shared_reality_layer(self) -> SharedRealityLayer:
        """Get the shared reality layer."""
        return self._shared_reality
    
    def get_world_model_orchestrator(self) -> WorldModelOrchestrator:
        """Get the world model orchestrator."""
        return self._world_model_orchestrator


# Singleton instance
_unified_world_model_manager: Optional[UnifiedWorldModelManager] = None
_unified_manager_lock = threading.Lock()

def get_unified_world_model_manager() -> UnifiedWorldModelManager:
    """Get the singleton unified world model manager instance."""
    global _unified_world_model_manager
    if _unified_world_model_manager is None:
        with _unified_manager_lock:
            if _unified_world_model_manager is None:
                _unified_world_model_manager = UnifiedWorldModelManager()
    return _unified_world_model_manager


__all__ = [
    "UnifiedWorldModelState",
    "UnifiedWorldModelManager",
    "get_unified_world_model_manager",
]