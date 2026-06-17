"""
world_model.shared_reality_layer
DIX VISION v42.2 — World Model as Shared Reality Layer

Priority 1 Implementation: World Model Unification

This module creates a unified shared reality layer that makes the world model
accessible to all cognitive systems (INDIRA, DYON, Desktop Agent, Governance, etc.)
as the single source of truth for world state.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SystemType(Enum):
    """Types of systems that can access the shared reality layer."""
    INDIRA = "INDIRA"
    DYON = "DYON"
    DESKTOP_AGENT = "DESKTOP_AGENT"
    GOVERNANCE = "GOVERNANCE"
    EXECUTION = "EXECUTION"
    LEARNING = "LEARNING"
    EVOLUTION = "EVOLUTION"
    COGNITIVE_OS = "COGNITIVE_OS"


@dataclass
class RealitySubscription:
    """Subscription to world model updates for a system."""
    system_type: SystemType
    system_id: str
    subscribed_components: List[str]
    callback: Optional[callable] = None
    last_update: str = ""
    active: bool = True


@dataclass
class RealityUpdate:
    """Update from the world model."""
    component: str  # market_state, agent_state, environment, etc.
    update_type: str  # FULL_UPDATE, INCREMENTAL, CONFLICT
    data: Dict[str, Any]
    timestamp: str
    source_system: Optional[SystemType] = None
    version: int = 0


@dataclass
class SystemWorldView:
    """A system's view of the world through the shared reality layer."""
    system_type: SystemType
    system_id: str
    relevant_components: List[str]
    current_state: Dict[str, Any]
    last_sync: str
    conflict_count: int = 0
    permissions: Dict[str, List[str]] = field(default_factory=dict)


class SharedRealityLayer:
    """
    World Model as Shared Reality Layer
    
    Provides unified access to world model for all cognitive systems.
    Serves as the single source of truth for world state.
    
    Features:
    - Unified world model access
    - System-specific world views
    - Conflict detection and resolution
    - Update subscription system
    - Permission management
    - Version control for state changes
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Core world model reference
        self._world_model_orchestrator = None
        self._shared_state: Dict[str, Any] = {}
        self._state_version = 0
        
        # System registrations
        self._registered_systems: Dict[SystemType, Dict[str, SystemWorldView]] = {}
        self._system_permissions: Dict[SystemType, Dict[str, List[str]]] = {}
        
        # Update subscriptions
        self._subscriptions: List[RealitySubscription] = []
        
        # Conflict tracking
        self._conflict_history: List[Dict[str, Any]] = []
        
        # System-specific adapters for world model integration
        self._system_adapters: Dict[SystemType, callable] = {}
        
        logger.info("[SHARED_REALITY_LAYER] Shared Reality Layer initialized")
    
    def initialize_world_model(self, world_model_orchestrator) -> None:
        """Initialize with the world model orchestrator."""
        with self._lock:
            self._world_model_orchestrator = world_model_orchestrator
            self._shared_state = {
                "market_state": {},
                "agent_models": {},
                "environment_state": {},
                "causal_structure": {},
                "dynamics": {},
                "predictions": {}
            }
            logger.info("[SHARED_REALITY_LAYER] World model initialized as shared reality")
    
    def register_system(
        self,
        system_type: SystemType,
        system_id: str,
        relevant_components: List[str],
        permissions: Optional[Dict[str, List[str]]] = None
    ) -> SystemWorldView:
        """
        Register a system to access the shared reality layer.
        
        Args:
            system_type: Type of system
            system_id: Unique system identifier
            relevant_components: Which world model components this system needs
            permissions: Read/write permissions for components
            
        Returns:
            System's world view
        """
        with self._lock:
            # Create system view
            world_view = SystemWorldView(
                system_type=system_type,
                system_id=system_id,
                relevant_components=relevant_components,
                current_state={},
                last_sync=datetime.utcnow().isoformat(),
                permissions=permissions or {comp: ["read"] for comp in relevant_components}
            )
            
            # Register system
            if system_type not in self._registered_systems:
                self._registered_systems[system_type] = {}
            
            self._registered_systems[system_type][system_id] = world_view
            
            # Set permissions
            if system_type not in self._system_permissions:
                self._system_permissions[system_type] = {}
            
            self._system_permissions[system_type][system_id] = permissions or {}
            
            logger.info(f"[SHARED_REALITY_LAYER] Registered system: {system_type.value}:{system_id}")
            
            return world_view
    
    def get_shared_state(self, system_type: SystemType, system_id: str) -> Dict[str, Any]:
        """
        Get the shared world state for a system.
        
        Args:
            system_type: System requesting the state
            system_id: System identifier
            
        Returns:
            Filtered world state based on permissions
        """
        with self._lock:
            # Check if system is registered
            if system_type not in self._registered_systems:
                logger.warning(f"[SHARED_REALITY_LAYER] System not registered: {system_type.value}")
                return {}
            
            if system_id not in self._registered_systems[system_type]:
                logger.warning(f"[SHARED_REALITY_LAYER] System ID not found: {system_id}")
                return {}
            
            world_view = self._registered_systems[system_type][system_id]
            
            # Get current shared state
            if self._world_model_orchestrator:
                # Sync with actual world model
                self._sync_with_world_model()
            
            # Filter based on permissions
            filtered_state = {}
            permissions = self._system_permissions[system_type].get(system_id, {})
            
            for component in world_view.relevant_components:
                if component in self._shared_state:
                    # Check permissions
                    if "read" in permissions.get(component, []):
                        filtered_state[component] = self._shared_state[component]
            
            # Update sync time
            world_view.last_sync = datetime.utcnow().isoformat()
            
            return filtered_state
    
    def update_shared_state(
        self,
        system_type: SystemType,
        system_id: str,
        component: str,
        update_data: Dict[str, Any],
        update_type: str = "INCREMENTAL"
    ) -> bool:
        """
        Update the shared world state.
        
        Args:
            system_type: System requesting the update
            system_id: System identifier
            component: Component being updated
            update_data: New data for the component
            update_type: Type of update (FULL_UPDATE, INCREMENTAL, CONFLICT)
            
        Returns:
            Success status
        """
        with self._lock:
            # Check permissions
            permissions = self._system_permissions.get(system_type, {}).get(system_id, {})
            if "write" not in permissions.get(component, []):
                logger.warning(f"[SHARED_REALITY_LAYER] No write permission for {system_type.value}:{system_id} on {component}")
                return False
            
            # Detect conflicts
            conflict_detected = False
            if component in self._shared_state:
                current_value = self._shared_state[component]
                if current_value and update_type == "INCREMENTAL":
                    # Check for conflicts
                    if self._detect_conflict(component, current_value, update_data):
                        conflict_detected = True
                        logger.warning(f"[SHARED_REALITY_LAYER] Conflict detected in {component} from {system_type.value}:{system_id}")
                        self._conflict_history.append({
                            "component": component,
                            "conflicting_system": f"{system_type.value}:{system_id}",
                            "timestamp": datetime.utcnow().isoformat(),
                            "current_value": current_value,
                            "new_value": update_data
                        })
            
            # Apply update
            if not conflict_detected or update_type == "FULL_UPDATE":
                if update_type == "FULL_UPDATE":
                    self._shared_state[component] = update_data
                else:
                    # Merge update
                    if component in self._shared_state:
                        self._shared_state[component].update(update_data)
                    else:
                        self._shared_state[component] = update_data
                
                # Increment version
                self._state_version += 1
                
                # Create update notification
                update = RealityUpdate(
                    component=component,
                    update_type=update_type,
                    data=update_data,
                    timestamp=datetime.utcnow().isoformat(),
                    source_system=system_type,
                    version=self._state_version
                )
                
                # Notify subscribers
                self._notify_subscribers(update)
                
                logger.info(f"[SHARED_REALITY_LAYER] Updated {component} from {system_type.value}:{system_id}")
                
                return True
            else:
                return False
    
    def subscribe_to_updates(
        self,
        system_type: SystemType,
        system_id: str,
        components: List[str],
        callback: Optional[callable] = None
    ) -> RealitySubscription:
        """
        Subscribe to world model updates.
        
        Args:
            system_type: System subscribing
            system_id: System identifier
            components: Components to subscribe to
            callback: Callback function for updates
            
        Returns:
            Subscription object
        """
        with self._lock:
            subscription = RealitySubscription(
                system_type=system_type,
                system_id=system_id,
                subscribed_components=components,
                callback=callback,
                last_update=datetime.utcnow().isoformat(),
                active=True
            )
            
            self._subscriptions.append(subscription)
            
            logger.info(f"[SHARED_REALITY_LAYER] Subscription created: {system_type.value}:{system_id} -> {components}")
            
            return subscription
    
    def _detect_conflict(self, component: str, current: Dict[str, Any], new: Dict[str, Any]) -> bool:
        """Detect if there's a conflict between current and new state."""
        # Simple conflict detection - can be enhanced
        for key in new:
            if key in current and current[key] != new[key]:
                return True
        return False
    
    def _notify_subscribers(self, update: RealityUpdate) -> None:
        """Notify subscribers of updates."""
        for subscription in self._subscriptions:
            if subscription.active and update.component in subscription.subscribed_components:
                if subscription.callback:
                    try:
                        subscription.callback(update)
                    except Exception as e:
                        logger.error(f"[SHARED_REALITY_LAYER] Callback error for {subscription.system_id}: {e}")
    
    def _sync_with_world_model(self) -> None:
        """Sync shared state with actual world model."""
        if self._world_model_orchestrator:
            try:
                # Get current world model state
                # This would integrate with the actual world model orchestrator
                world_state = self._world_model_orchestrator._state
                
                # Update shared state
                for component, data in world_state.__dict__.items():
                    if not component.startswith('_') and isinstance(data, dict):
                        self._shared_state[component] = data
                
            except Exception as e:
                logger.error(f"[SHARED_REALITY_LAYER] Sync with world model failed: {e}")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get statistics about the shared reality layer."""
        with self._lock:
            registered_systems = {}
            for system_type, systems in self._registered_systems.items():
                registered_systems[system_type.value] = {
                    "count": len(systems),
                    "system_ids": list(systems.keys())
                }
            
            return {
                "registered_systems": registered_systems,
                "active_subscriptions": len([s for s in self._subscriptions if s.active]),
                "state_version": self._state_version,
                "conflict_count": len(self._conflict_history),
                "shared_components": list(self._shared_state.keys()),
                "last_sync": datetime.utcnow().isoformat()
            }
    
    def get_system_world_view(self, system_type: SystemType, system_id: str) -> Optional[SystemWorldView]:
        """Get a system's world view."""
        with self._lock:
            if system_type in self._registered_systems and system_id in self._registered_systems[system_type]:
                return self._registered_systems[system_type][system_id]
            return None


# Singleton instance
_shared_reality_layer: Optional[SharedRealityLayer] = None
_shared_reality_lock = threading.Lock()

def get_shared_reality_layer() -> SharedRealityLayer:
    """Get the singleton shared reality layer instance."""
    global _shared_reality_layer
    if _shared_reality_layer is None:
        with _shared_reality_lock:
            if _shared_reality_layer is None:
                _shared_reality_layer = SharedRealityLayer()
    return _shared_reality_layer


__all__ = [
    "SystemType",
    "RealitySubscription",
    "RealityUpdate",
    "SystemWorldView",
    "SharedRealityLayer",
    "get_shared_reality_layer",
]