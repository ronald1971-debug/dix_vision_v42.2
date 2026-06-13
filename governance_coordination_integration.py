"""
governance_coordination_integration.py
DIX VISION v42.2 — Governance and Coordination Layer Integration

Integrates the new coordination layer with existing governance components
to provide unified agent coordination and governance.
"""

import logging
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from enum import StrEnum

logger = logging.getLogger(__name__)


class GovernanceCoordinationMode(StrEnum):
    """Mode for governance and coordination integration."""
    SEPARATE = "separate"  # Governance and coordination operate independently
    COORDINATED = "coordinated"  # Coordination layer informs governance
    UNIFIED = "unified"  # Single unified governance-coordination system
    GOVERNANCE_PRIMARY = "governance_primary"  # Governance has priority
    COORDINATION_PRIMARY = "coordination_primary"  # Coordination has priority


@dataclass
class GovernanceCoordinationConfig:
    """Configuration for governance-coordination integration."""
    mode: GovernanceCoordinationMode = GovernanceCoordinationMode.COORDINATED
    enable_conflict_resolution: bool = True
    enable_shared_mental_models: bool = True
    enable_governance_policy_sync: bool = True
    conflict_timeout_seconds: int = 30


class GovernanceCoordinationIntegrator:
    """
    Integrates governance kernel with coordination layer.
    
    This integrator provides:
    - Conflict resolution between governance and coordination decisions
    - Shared mental model synchronization
    - Policy synchronization between systems
    - Unified agent behavior oversight
    """
    
    def __init__(self, config: Optional[GovernanceCoordinationConfig] = None):
        """Initialize the governance-coordination integrator.
        
        Args:
            config: Integration configuration. If None, uses defaults.
        """
        self.config = config or GovernanceCoordinationConfig()
        self._initialized = False
        
        # Component references
        self._governance_kernel = None
        self._coordination_layer = None
        self._mode_manager = None
        
        # Integration state
        self._conflict_history = []
        self._shared_mental_model_state = {}
        self._policy_sync_state = {}
        
        logger.info("[GOV_COORD] Governance-coordination integrator created")
    
    def initialize(self) -> bool:
        """Initialize the governance-coordination integrator.
        
        Returns:
            bool: True if initialization successful.
        """
        try:
            logger.info("[GOV_COORD] Initializing governance-coordination integrator")
            
            # Connect to governance kernel
            if not self._connect_governance():
                logger.warning("[GOV_COORD] Governance kernel connection failed")
            
            # Connect to coordination layer
            if not self._connect_coordination():
                logger.warning("[GOV_COORD] Coordination layer connection failed")
            
            # Connect to mode manager
            if not self._connect_mode_manager():
                logger.warning("[GOV_COORD] Mode manager connection failed")
            
            # Setup integration hooks based on mode
            self._setup_integration_hooks()
            
            self._initialized = True
            logger.info(f"[GOV_COORD] Governance-coordination integrator initialized in {self.config.mode} mode")
            return True
            
        except Exception as e:
            logger.error(f"[GOV_COORD] Initialization failed: {e}")
            return False
    
    def _connect_governance(self) -> bool:
        """Connect to governance kernel.
        
        Returns:
            bool: True if successful.
        """
        try:
            from governance.kernel import get_kernel
            
            self._governance_kernel = get_kernel()
            logger.info("[GOV_COORD] Connected to governance kernel")
            return True
            
        except Exception as e:
            logger.error(f"[GOV_COORD] Governance kernel connection error: {e}")
            return False
    
    def _connect_coordination(self) -> bool:
        """Connect to coordination layer.
        
        Returns:
            bool: True if successful.
        """
        try:
            from cognitive_architecture_adapter import get_cognitive_adapter
            from config.cognitive_config_loader import is_component_enabled
            
            if is_component_enabled('coordination_layer'):
                adapter = get_cognitive_adapter()
                self._coordination_layer = adapter._coordination_layer
                logger.info("[GOV_COORD] Connected to coordination layer")
                return True
            else:
                logger.info("[GOV_COORD] Coordination layer disabled in config")
                return True
                
        except Exception as e:
            logger.error(f"[GOV_COORD] Coordination layer connection error: {e}")
            return False
    
    def _connect_mode_manager(self) -> bool:
        """Connect to mode manager.
        
        Returns:
            bool: True if successful.
        """
        try:
            from governance.mode_manager import get_mode_manager
            
            self._mode_manager = get_mode_manager()
            logger.info("[GOV_COORD] Connected to mode manager")
            return True
            
        except Exception as e:
            logger.error(f"[GOV_COORD] Mode manager connection error: {e}")
            return False
    
    def _setup_integration_hooks(self):
        """Setup integration hooks based on configuration mode."""
        if self.config.mode == GovernanceCoordinationMode.COORDINATED:
            self._setup_coordinated_hooks()
        elif self.config.mode == GovernanceCoordinationMode.UNIFIED:
            self._setup_unified_hooks()
        elif self.config.mode == GovernanceCoordinationMode.GOVERNANCE_PRIMARY:
            self._setup_governance_primary_hooks()
        elif self.config.mode == GovernanceCoordinationMode.COORDINATION_PRIMARY:
            self._setup_coordination_primary_hooks()
    
    def _setup_coordinated_hooks(self):
        """Setup hooks for coordinated mode."""
        logger.info("[GOV_COORD] Setting up coordinated integration hooks")
        
        # Coordination layer informs governance decisions
        if self._coordination_layer and self._governance_kernel:
            # Hook coordination conflict detection into governance
            self._coordination_integration_hook = self._coordination_conflict_hook
    
    def _setup_unified_hooks(self):
        """Setup hooks for unified mode."""
        logger.info("[GOV_COORD] Setting up unified integration hooks")
        # TODO: Implement unified hooks
    
    def _setup_governance_primary_hooks(self):
        """Setup hooks for governance-primary mode."""
        logger.info("[GOV_COORD] Setting up governance-primary integration hooks")
        # TODO: Implement governance-primary hooks
    
    def _setup_coordination_primary_hooks(self):
        """Setup hooks for coordination-primary mode."""
        logger.info("[GOV_COORD] Setting up coordination-primary integration hooks")
        # TODO: Implement coordination-primary hooks
    
    def _coordination_conflict_hook(self, governance_decision: Any, 
                                    coordination_conflicts: list) -> Dict[str, Any]:
        """Hook for coordination conflict resolution.
        
        Args:
            governance_decision: Decision from governance kernel.
            coordination_conflicts: Conflicts detected by coordination layer.
            
        Returns:
            Dict[str, Any]: Resolution decision.
        """
        if not self.config.enable_conflict_resolution:
            return {"resolution": "governance_priority", "reason": "Conflict resolution disabled"}
        
        # Implement conflict resolution logic
        # For now, defer to governance in coordinated mode
        return {
            "resolution": "governance_priority",
            "reason": "Coordinated mode - governance has priority",
            "conflicts_noted": len(coordination_conflicts)
        }
    
    def sync_operating_modes(self) -> bool:
        """Synchronize operating modes between coordination and governance.
        
        Returns:
            bool: True if synchronization successful.
        """
        if not self._mode_manager or not self._coordination_layer:
            logger.warning("[GOV_COORD] Cannot sync modes - components not connected")
            return False
        
        try:
            # Get current governance mode
            gov_mode = self._mode_manager.get_current_mode()
            
            # Get coordination operating mode
            from coordination_layer.operating_modes import OperatingModeManager, get_operating_mode_manager
            coord_mode_manager = get_operating_mode_manager()
            coord_mode = coord_mode_manager.get_current_mode()
            
            # Map between modes
            mode_mapping = {
                "NORMAL": "active",
                "SAFE": "passive", 
                "DEGRADED": "observation",
                "HALTED": "offline"
            }
            
            # Sync coordination mode to match governance mode
            if gov_mode.name in mode_mapping:
                target_coord_mode = mode_mapping[gov_mode.name]
                from coordination_layer.operating_modes import OperatingMode, ModeTransitionReason
                
                coord_mode_manager.transition_to_mode(
                    target_mode=OperatingMode(target_coord_mode),
                    reason=ModeTransitionReason.SYSTEM_INITIATED,
                    initiator="governance_sync"
                )
                
                logger.info(f"[GOV_COORD] Synced coordination mode to {target_coord_mode}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[GOV_COORD] Mode sync error: {e}")
            return False
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status.
        
        Returns:
            Dict[str, Any]: Integration status information.
        """
        return {
            "initialized": self._initialized,
            "mode": self.config.mode,
            "components_connected": {
                "governance_kernel": self._governance_kernel is not None,
                "coordination_layer": self._coordination_layer is not None,
                "mode_manager": self._mode_manager is not None
            },
            "features_enabled": {
                "conflict_resolution": self.config.enable_conflict_resolution,
                "shared_mental_models": self.config.enable_shared_mental_models,
                "policy_sync": self.config.enable_governance_policy_sync
            },
            "conflict_history_count": len(self._conflict_history)
        }
    
    def shutdown(self) -> bool:
        """Shutdown the governance-coordination integrator.
        
        Returns:
            bool: True if shutdown successful.
        """
        try:
            logger.info("[GOV_COORD] Shutting down governance-coordination integrator")
            self._initialized = False
            logger.info("[GOV_COORD] Governance-coordination integrator shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"[GOV_COORD] Shutdown error: {e}")
            return False


# Global integrator instance
_global_integrator: Optional[GovernanceCoordinationIntegrator] = None


def get_governance_coordination_integrator(config: Optional[GovernanceCoordinationConfig] = None) -> GovernanceCoordinationIntegrator:
    """Get global governance-coordination integrator instance.
    
    Args:
        config: Optional integration configuration.
        
    Returns:
        GovernanceCoordinationIntegrator: Global integrator instance.
    """
    global _global_integrator
    if _global_integrator is None:
        _global_integrator = GovernanceCoordinationIntegrator(config)
    return _global_integrator


def initialize_governance_coordination(config: Optional[GovernanceCoordinationConfig] = None) -> bool:
    """Initialize governance-coordination integration.
    
    Args:
        config: Optional integration configuration.
        
    Returns:
        bool: True if initialization successful.
    """
    integrator = get_governance_coordination_integrator(config)
    return integrator.initialize()


if __name__ == "__main__":
    # Test the integrator
    logging.basicConfig(level=logging.INFO)
    
    config = GovernanceCoordinationConfig(mode=GovernanceCoordinationMode.COORDINATED)
    integrator = GovernanceCoordinationIntegrator(config)
    
    if integrator.initialize():
        print("Governance-coordination integrator initialized successfully")
        print(f"Integration status: {integrator.get_integration_status()}")
    else:
        print("Governance-coordination integrator initialization failed")