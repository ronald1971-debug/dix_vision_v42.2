"""
system.dynamic_enabler
DIX VISION v42.2 — Dynamic Capability Manager

Manages dynamic enable/disable of system components based on
learning orchestrator decisions. Implements the autonomy capability
for the system to switch components on/off as needed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from system.feature_flags import CognitiveFeatureFlags, FeatureFlagManager, FeatureStatus
from system.learning_orchestrator import CapabilityDecision, get_learning_orchestrator
from system.time_source import now

logger = logging.getLogger(__name__)


@dataclass
class CapabilityState:
    """Current state of a capability."""
    
    name: str
    enabled: bool
    last_decision: str = ""
    last_change_time: str = ""
    decision_count: int = 0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DynamicCapabilityManager:
    """Manages dynamic enable/disable of system capabilities.
    
    Enables the system to:
    - Dynamically enable/disable components
    - Execute decisions from learning orchestrator
    - Track capability state changes
    - Maintain dependency constraints
    - Implement safe transition logic
    """
    
    def __init__(self) -> None:
        self._capability_states: dict[str, CapabilityState] = {}
        self._learning_orchestrator = get_learning_orchestrator()
        self._auto_apply_enabled = True
        self._dependency_constraints: dict[str, set[str]] = {}
        
        # Initialize with current feature flag states
        self._initialize_from_feature_flags()
    
    def _initialize_from_feature_flags(self) -> None:
        """Initialize capability states from current feature flags."""
        try:
            # Initialize cognitive feature flags
            for attr_name in dir(CognitiveFeatureFlags):
                if not attr_name.startswith('_'):
                    flag = getattr(CognitiveFeatureFlags, attr_name)
                    status = FeatureFlagManager.get_status(flag)
                    enabled = status == FeatureStatus.ENABLED
                    
                    self._capability_states[flag.name] = CapabilityState(
                        name=flag.name,
                        enabled=enabled,
                        last_decision="initial",
                        last_change_time=now().utc_time.isoformat(),
                        decision_count=0
                    )
                    
                    logger.debug(f"[DYNAMIC] Initialized {flag.name} as {'enabled' if enabled else 'disabled'}")
            
            logger.info(f"[DYNAMIC] Initialized {len(self._capability_states)} capabilities")
            
        except Exception as e:
            logger.error(f"[DYNAMIC] Failed to initialize from feature flags: {e}")
    
    def enable_auto_apply(self) -> None:
        """Enable automatic application of decisions."""
        self._auto_apply_enabled = True
        logger.info("[DYNAMIC] Auto apply enabled")
    
    def disable_auto_apply(self) -> None:
        """Disable automatic application of decisions."""
        self._auto_apply_enabled = False
        logger.info("[DYNAMIC] Auto apply disabled")
    
    def add_dependency_constraint(self, capability: str, depends_on: str) -> None:
        """Add a dependency constraint.
        
        If capability A depends on capability B, A cannot be enabled unless B is enabled.
        """
        if capability not in self._dependency_constraints:
            self._dependency_constraints[capability] = set()
        
        self._dependency_constraints[capability].add(depends_on)
        
        # Record this in the learning orchestrator
        self._learning_orchestrator.record_capability_dependency(capability, depends_on)
        
        logger.debug(f"[DYNAMIC] Added constraint: {capability} depends on {depends_on}")
    
    def execute_decision(self, decision: CapabilityDecision) -> bool:
        """Execute a capability decision.
        
        Returns True if the decision was executed, False otherwise.
        """
        if not self._auto_apply_enabled:
            logger.info(f"[DYNAMIC] Auto apply disabled, not executing decision for {decision.capability_name}")
            return False
        
        try:
            capability_name = decision.capability_name
            current_state = self._capability_states.get(capability_name)
            
            if current_state is None:
                logger.warning(f"[DYNAMIC] Unknown capability: {capability_name}")
                return False
            
            # Check if decision matches current state
            if decision.decision == "enable" and current_state.enabled:
                logger.debug(f"[DYNAMIC] {capability_name} already enabled")
                return True
            
            if decision.decision == "disable" and not current_state.enabled:
                logger.debug(f"[DYNAMIC] {capability_name} already disabled")
                return True
            
            # Check dependency constraints before disabling
            if decision.decision == "disable":
                if not self._check_safe_to_disable(capability_name):
                    logger.warning(f"[DYNAMIC] {capability_name} cannot be disabled (dependencies)")
                    return False
            
            # Execute the decision
            if decision.decision == "enable":
                success = self._enable_capability(capability_name)
            elif decision.decision == "disable":
                success = self._disable_capability(capability_name)
            else:  # maintain
                success = True
            
            if success:
                # Update state
                current_state.enabled = (decision.decision == "enable")
                current_state.last_decision = decision.decision
                current_state.last_change_time = now().utc_time.isoformat()
                current_state.decision_count += 1
                current_state.metadata.update(decision.metadata)
                
                logger.info(
                    f"[DYNAMIC] Executed decision: {decision.decision} {capability_name} "
                    f"(confidence: {decision.confidence:.2f})"
                )
            else:
                logger.error(f"[DYNAMIC] Failed to execute decision for {capability_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"[DYNAMIC] Failed to execute decision: {e}")
            return False
    
    def execute_all_pending_decisions(self) -> int:
        """Execute all pending decisions from learning orchestrator.
        
        Returns the number of decisions executed.
        """
        decisions = self._learning_orchestrator.make_capability_decisions()
        
        executed_count = 0
        for decision in decisions:
            if self.execute_decision(decision):
                executed_count += 1
        
        logger.info(f"[DYNAMIC] Executed {executed_count}/{len(decisions)} pending decisions")
        return executed_count
    
    def _enable_capability(self, capability_name: str) -> bool:
        """Enable a capability."""
        try:
            # Find corresponding feature flag
            for attr_name in dir(CognitiveFeatureFlags):
                if not attr_name.startswith('_'):
                    flag = getattr(CognitiveFeatureFlags, attr_name)
                    if flag.name == capability_name:
                        FeatureFlagManager.set_status(flag, FeatureStatus.ENABLED)
                        return True
            
            logger.warning(f"[DYNAMIC] No feature flag found for {capability_name}")
            return False
            
        except Exception as e:
            logger.error(f"[DYNAMIC] Failed to enable {capability_name}: {e}")
            return False
    
    def _disable_capability(self, capability_name: str) -> bool:
        """Disable a capability."""
        try:
            # Find corresponding feature flag
            for attr_name in dir(CognitiveFeatureFlags):
                if not attr_name.startswith('_'):
                    flag = getattr(CognitiveFeatureFlags, attr_name)
                    if flag.name == capability_name:
                        FeatureFlagManager.set_status(flag, FeatureStatus.DISABLED)
                        return True
            
            logger.warning(f"[DYNAMIC] No feature flag found for {capability_name}")
            return False
            
        except Exception as e:
            logger.error(f"[DYNAMIC] Failed to disable {capability_name}: {e}")
            return False
    
    def _check_safe_to_disable(self, capability_name: str) -> bool:
        """Check if it's safe to disable a capability.
        
        A capability is safe to disable if no other enabled capability depends on it.
        """
        # Check if any enabled capability depends on this one
        for dependent, dependencies in self._dependency_constraints.items():
            if capability_name in dependencies:
                dependent_state = self._capability_states.get(dependent)
                if dependent_state and dependent_state.enabled:
                    logger.warning(
                        f"[DYNAMIC] {dependent} (enabled) depends on {capability_name}, "
                        f"cannot disable safely"
                    )
                    return False
        
        return True
    
    def get_capability_state(self, capability_name: str) -> CapabilityState | None:
        """Get the current state of a capability."""
        return self._capability_states.get(capability_name)
    
    def get_all_capability_states(self) -> dict[str, CapabilityState]:
        """Get the state of all capabilities."""
        return self._capability_states.copy()
    
    def get_enabled_capabilities(self) -> list[str]:
        """Get list of enabled capabilities."""
        return [
            name for name, state in self._capability_states.items()
            if state.enabled
        ]
    
    def get_disabled_capabilities(self) -> list[str]:
        """Get list of disabled capabilities."""
        return [
            name for name, state in self._capability_states.items()
            if not state.enabled
        ]
    
    def force_enable_capability(self, capability_name: str) -> bool:
        """Force enable a capability (override learning)."""
        logger.info(f"[DYNAMIC] Force enabling {capability_name}")
        return self._enable_capability(capability_name)
    
    def force_disable_capability(self, capability_name: str) -> bool:
        """Force disable a capability (override learning)."""
        logger.info(f"[DYNAMIC] Force disabling {capability_name}")
        
        if not self._check_safe_to_disable(capability_name):
            logger.warning(f"[DYNAMIC] Force disable of {capability_name} blocked by dependencies")
            return False
        
        return self._disable_capability(capability_name)
    
    def reset_to_defaults(self) -> None:
        """Reset all capabilities to default states."""
        logger.info("[DYNAMIC] Resetting all capabilities to defaults")
        
        # Re-initialize from feature flags
        self._capability_states.clear()
        self._initialize_from_feature_flags()
        
        logger.info("[DYNAMIC] Reset complete")


# Global instance
_dynamic_capability_manager: DynamicCapabilityManager | None = None


def get_dynamic_capability_manager() -> DynamicCapabilityManager:
    """Get the global dynamic capability manager instance."""
    global _dynamic_capability_manager
    if _dynamic_capability_manager is None:
        _dynamic_capability_manager = DynamicCapabilityManager()
    return _dynamic_capability_manager


__all__ = [
    "CapabilityState",
    "DynamicCapabilityManager",
    "get_dynamic_capability_manager",
]