"""
world_model.execution_integration
DIX VISION v42.2 — Execution World Model Integration

Integration adapter to connect Execution systems to the Shared Reality Layer.
Allows Execution to access world model state for trading decisions and strategy.
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


class ExecutionWorldIntegration:
    """
    Integration layer for Execution systems to access Shared Reality Layer.
    
    Provides:
    - Registration with shared reality layer
    - World state access for execution decisions
    - Market state for trading strategies
    - Agent coordination through shared reality
    - Performance feedback to world model
    """
    
    def __init__(self, execution_id: str = "execution_primary"):
        self._execution_id = execution_id
        self._shared_reality: Optional[SharedRealityLayer] = None
        self._world_view: Optional[SystemWorldView] = None
        
        # Execution-specific components
        self._relevant_components = [
            "market_state",  # Market conditions for trading
            "agent_models",  # Trading agent states
            "causal_structure",  # Market dependencies
            "dynamics",  # Market dynamics
            "predictions",  # Market predictions
        ]
        
        # Execution permissions
        self._permissions = {
            "market_state": ["read", "write"],  # Can update market state from execution
            "agent_models": ["read", "write"],  # Can update agent states
            "causal_structure": ["read"],
            "dynamics": ["read", "write"],
            "predictions": ["read"]
        }
        
        logger.info(f"[EXECUTION_INTEGRATION] Execution integration initialized for {execution_id}")
    
    def connect_to_shared_reality(self, world_model_orchestrator) -> None:
        """Connect to the shared reality layer."""
        shared_reality = get_shared_reality_layer()
        
        # Only initialize if not already initialized
        if shared_reality._world_model_orchestrator is None:
            shared_reality.initialize_world_model(world_model_orchestrator)
        
        # Register execution system
        self._world_view = shared_reality.register_system(
            system_type=SystemType.EXECUTION,
            system_id=self._execution_id,
            relevant_components=self._relevant_components,
            permissions=self._permissions
        )
        
        self._shared_reality = shared_reality
        logger.info(f"[EXECUTION_INTEGRATION] Execution connected to shared reality")
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get market state from world model for execution decisions."""
        if self._shared_reality:
            world_state = self._shared_reality.get_shared_state(
                SystemType.EXECUTION,
                self._execution_id
            )
            return world_state.get("market_state", {})
        return {}
    
    def get_agent_states(self) -> Dict[str, Any]:
        """Get trading agent states from world model."""
        if self._shared_reality:
            world_state = self._shared_reality.get_shared_state(
                SystemType.EXECUTION,
                self._execution_id
            )
            return world_state.get("agent_models", {})
        return {}
    
    def get_market_dynamics(self) -> Dict[str, Any]:
        """Get market dynamics for strategy selection."""
        if self._shared_reality:
            world_state = self._shared_reality.get_shared_state(
                SystemType.EXECUTION,
                self._execution_id
            )
            return world_state.get("dynamics", {})
        return {}
    
    def update_execution_performance(self, performance_data: Dict[str, Any]) -> bool:
        """Update world model with execution performance."""
        if self._shared_reality:
            # Update agent_models component with execution performance
            return self._shared_reality.update_shared_state(
                system_type=SystemType.EXECUTION,
                system_id=self._execution_id,
                component="agent_models",
                update_data=performance_data,
                update_type="INCREMENTAL"
            )
        return False
    
    def update_market_state_from_execution(self, market_data: Dict[str, Any]) -> bool:
        """Update world model with market state from execution observations."""
        if self._shared_reality:
            return self._shared_reality.update_shared_state(
                system_type=SystemType.EXECUTION,
                system_id=self._execution_id,
                component="market_state",
                update_data=market_data,
                update_type="INCREMENTAL"
            )
        return False
    
    def get_market_predictions(self) -> Dict[str, Any]:
        """Get market predictions from world model."""
        world_state = self.get_market_state()
        return world_state.get("predictions", {})
    
    def subscribe_to_world_updates(self, callback: callable) -> None:
        """Subscribe to world model updates for execution strategies."""
        if self._shared_reality:
            self._shared_reality.subscribe_to_updates(
                system_type=SystemType.EXECUTION,
                system_id=self._execution_id,
                components=self._relevant_components,
                callback=callback
            )
            logger.info("[EXECUTION_INTEGRATION] Subscribed to world updates for execution strategies")


# Singleton instance
_execution_integration: Optional[ExecutionWorldIntegration] = None
_execution_lock = threading.Lock()

def get_execution_integration(execution_id: str = "execution_primary") -> ExecutionWorldIntegration:
    """Get the singleton execution integration instance."""
    global _execution_integration
    if _execution_integration is None:
        with _execution_lock:
            if _execution_integration is None:
                _execution_integration = ExecutionWorldIntegration(execution_id)
    return _execution_integration


__all__ = [
    "ExecutionWorldIntegration",
    "get_execution_integration",
]