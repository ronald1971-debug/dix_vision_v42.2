"""
world_model.governance_integration
DIX VISION v42.2 — Governance World Model Integration

Integration adapter to connect Governance systems to the Shared Reality Layer.
Allows Governance to access world model state for compliance checks and risk assessment.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Optional

from world_model.shared_reality_layer import (
    SharedRealityLayer,
    SystemType,
    SystemWorldView,
    get_shared_reality_layer,
)

logger = logging.getLogger(__name__)


class GovernanceWorldIntegration:
    """
    Integration layer for Governance systems to access Shared Reality Layer.

    Provides:
    - Registration with shared reality layer
    - World state access for governance operations
    - Compliance and risk assessment using world model
    - Policy updates based on world state
    """

    def __init__(self, governance_id: str = "governance_primary"):
        self._governance_id = governance_id
        self._shared_reality: Optional[SharedRealityLayer] = None
        self._world_view: Optional[SystemWorldView] = None

        # Governance-specific components
        self._relevant_components = [
            "market_state",  # Market conditions for compliance
            "causal_structure",  # Risk factors and dependencies
            "environment_state",  # Operating environment
            "predictions",  # Risk predictions
        ]

        # Governance permissions
        self._permissions = {
            "market_state": ["read"],
            "causal_structure": ["read"],
            "environment_state": ["read"],
            "predictions": ["read", "write"],  # Can update risk predictions
        }

        logger.info(
            f"[GOVERNANCE_INTEGRATION] Governance integration initialized for {governance_id}"
        )

    def connect_to_shared_reality(self, world_model_orchestrator) -> None:
        """Connect to the shared reality layer."""
        shared_reality = get_shared_reality_layer()

        # Only initialize if not already initialized
        if shared_reality._world_model_orchestrator is None:
            shared_reality.initialize_world_model(world_model_orchestrator)

        # Register governance system
        self._world_view = shared_reality.register_system(
            system_type=SystemType.GOVERNANCE,
            system_id=self._governance_id,
            relevant_components=self._relevant_components,
            permissions=self._permissions,
        )

        self._shared_reality = shared_reality
        logger.info(f"[GOVERNANCE_INTEGRATION] Governance connected to shared reality")

    def get_world_state_for_compliance(self) -> Dict[str, Any]:
        """Get world state needed for compliance checks."""
        if self._shared_reality:
            return self._shared_reality.get_shared_state(SystemType.GOVERNANCE, self._governance_id)
        return {}

    def assess_risk_from_world_state(self) -> Dict[str, Any]:
        """Assess risk based on world model state."""
        world_state = self.get_world_state_for_compliance()

        risk_assessment = {
            "market_conditions": world_state.get("market_state", {}),
            "risk_factors": world_state.get("causal_structure", {}),
            "environment_risks": world_state.get("environment_state", {}),
            "predicted_risks": world_state.get("predictions", {}),
            "overall_risk_level": "MEDIUM",  # Would calculate from actual data
            "confidence": 0.8,
        }

        return risk_assessment

    def update_risk_predictions(self, risk_data: Dict[str, Any]) -> bool:
        """Update risk predictions in world model."""
        if self._shared_reality:
            return self._shared_reality.update_shared_state(
                system_type=SystemType.GOVERNANCE,
                system_id=self._governance_id,
                component="predictions",
                update_data=risk_data,
                update_type="INCREMENTAL",
            )
        return False

    def get_causal_dependencies(self) -> Dict[str, Any]:
        """Get causal dependencies for risk assessment."""
        world_state = self.get_world_state_for_compliance()
        return world_state.get("causal_structure", {})

    def check_world_state_compliance(self) -> bool:
        """Check if current world state is compliant."""
        risk_assessment = self.assess_risk_from_world_state()

        # Simple compliance check
        market_state = risk_assessment["market_conditions"]

        # Example compliance logic
        if market_state.get("volatility") == "extreme":
            logger.warning("[GOVERNANCE_INTEGRATION] Extreme volatility - compliance check failed")
            return False

        if risk_assessment["overall_risk_level"] == "CRITICAL":
            logger.warning("[GOVERNANCE_INTEGRATION] Critical risk - compliance check failed")
            return False

        return True

    def subscribe_to_world_updates(self, callback: callable) -> None:
        """Subscribe to world model updates for compliance monitoring."""
        if self._shared_reality:
            self._shared_reality.subscribe_to_updates(
                system_type=SystemType.GOVERNANCE,
                system_id=self._governance_id,
                components=self._relevant_components,
                callback=callback,
            )
            logger.info(
                "[GOVERNANCE_INTEGRATION] Subscribed to world updates for compliance monitoring"
            )


# Singleton instance
_governance_integration: Optional[GovernanceWorldIntegration] = None
_governance_lock = threading.Lock()


def get_governance_integration(
    governance_id: str = "governance_primary",
) -> GovernanceWorldIntegration:
    """Get the singleton governance integration instance."""
    global _governance_integration
    if _governance_integration is None:
        with _governance_lock:
            if _governance_integration is None:
                _governance_integration = GovernanceWorldIntegration(governance_id)
    return _governance_integration


__all__ = [
    "GovernanceWorldIntegration",
    "get_governance_integration",
]
