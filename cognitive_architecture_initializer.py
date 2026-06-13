"""
cognitive_architecture_initializer.py
DIX VISION v42.2 — Cognitive Architecture Initializer

Initializes the new cognitive architecture components with proper configuration
and integration with the existing system.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.cognitive_config_loader import (
    CognitiveConfigLoader,
    load_cognitive_config,
    is_cognitive_architecture_enabled,
    is_component_enabled
)
from preservation_layer import PreservationLayer
from indira_cognitive.indira_brain.concrete import ConcreteINDIRABrain
from dyon_cognitive.dyon_brain.concrete import ConcreteDYONBrain
from coordination_layer.concrete import ConcreteCoordinationLayer
from coordination_layer.cognitive_economy import CognitiveEconomyManager, get_cognitive_economy_manager
from coordination_layer.operating_modes import OperatingModeManager, get_operating_mode_manager
from coordination_layer.learning_gate import LearningGateManager, get_learning_gate_manager
from shared_infrastructure.planning_engine import PlanningEngine
from shared_infrastructure.signal_processing import SignalProcessingService

logger = logging.getLogger(__name__)


class CognitiveArchitectureInitializer:
    """Initializes cognitive architecture components."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the cognitive architecture initializer.
        
        Args:
            config_path: Optional path to configuration file.
        """
        self.config_loader = CognitiveConfigLoader(config_path)
        self.config = None
        
        # Component instances
        self.preservation_layer: Optional[PreservationLayer] = None
        self.indira_brain: Optional[ConcreteINDIRABrain] = None
        self.dyon_brain: Optional[ConcreteDYONBrain] = None
        self.coordination_layer: Optional[ConcreteCoordinationLayer] = None
        self.cognitive_economy: Optional[CognitiveEconomyManager] = None
        self.operating_modes: Optional[OperatingModeManager] = None
        self.learning_gate: Optional[LearningGateManager] = None
        self.planning_engine: Optional[PlanningEngine] = None
        self.signal_processing: Optional[SignalProcessingService] = None
        
        # Shared infrastructure (placeholders for actual connections)
        self.shared_infrastructure: Dict[str, Any] = {}
        
        logger.info("[INIT] Cognitive architecture initializer created")
    
    def initialize(self) -> bool:
        """Initialize all cognitive architecture components.
        
        Returns:
            bool: True if initialization successful.
        """
        try:
            logger.info("[INIT] Starting cognitive architecture initialization")
            
            # Load configuration
            self.config = self.config_loader.load_config()
            
            if not self.config.enabled:
                logger.info("[INIT] Cognitive architecture disabled in configuration")
                return True
            
            # Initialize preservation layer first
            if not self._initialize_preservation_layer():
                logger.error("[INIT] Failed to initialize preservation layer")
                return False
            
            # Initialize coordination components
            if not self._initialize_coordination_components():
                logger.error("[INIT] Failed to initialize coordination components")
                return False
            
            # Initialize shared infrastructure
            if not self._initialize_shared_infrastructure():
                logger.error("[INIT] Failed to initialize shared infrastructure")
                return False
            
            # Initialize brains
            if not self._initialize_brains():
                logger.error("[INIT] Failed to initialize brains")
                return False
            
            # Initialize coordination layer
            if not self._initialize_coordination_layer():
                logger.error("[INIT] Failed to initialize coordination layer")
                return False
            
            # Connect components
            if not self._connect_components():
                logger.error("[INIT] Failed to connect components")
                return False
            
            # Set operating mode
            if not self._set_initial_operating_mode():
                logger.error("[INIT] Failed to set initial operating mode")
                return False
            
            logger.info("[INIT] Cognitive architecture initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"[INIT] Error during initialization: {e}")
            return False
    
    def _initialize_preservation_layer(self) -> bool:
        """Initialize preservation layer.
        
        Returns:
            bool: True if successful.
        """
        try:
            if not is_component_enabled('preservation_layer'):
                logger.info("[INIT] Preservation layer disabled, skipping")
                return True
            
            self.preservation_layer = PreservationLayer()
            
            # Initialize legacy engines
            if self.config.preservation_layer.get('migration_mode', True):
                success = self.preservation_layer.initialize_legacy_engines()
                if not success:
                    logger.warning("[INIT] Some legacy engines failed to initialize")
            
            logger.info("[INIT] Preservation layer initialized")
            return True
            
        except Exception as e:
            logger.error(f"[INIT] Error initializing preservation layer: {e}")
            return False
    
    def _initialize_coordination_components(self) -> bool:
        """Initialize coordination components.
        
        Returns:
            bool: True if successful.
        """
        try:
            # Cognitive Economy
            if is_component_enabled('cognitive_economy'):
                self.cognitive_economy = get_cognitive_economy_manager()
                logger.info("[INIT] Cognitive economy manager initialized")
            
            # Operating Modes
            if is_component_enabled('operating_modes'):
                self.operating_modes = get_operating_mode_manager()
                logger.info("[INIT] Operating mode manager initialized")
            
            # Learning Gate
            if is_component_enabled('learning_gate'):
                self.learning_gate = get_learning_gate_manager()
                logger.info("[INIT] Learning gate manager initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"[INIT] Error initializing coordination components: {e}")
            return False
    
    def _initialize_shared_infrastructure(self) -> bool:
        """Initialize shared infrastructure components.
        
        Returns:
            bool: True if successful.
        """
        try:
            # Planning Engine
            if is_component_enabled('planning_engine'):
                self.planning_engine = PlanningEngine()
                self.shared_infrastructure['planning_engine'] = self.planning_engine
                logger.info("[INIT] Planning engine initialized")
            
            # Signal Processing
            if is_component_enabled('signal_processing'):
                self.signal_processing = SignalProcessingService()
                self.shared_infrastructure['signal_processing'] = self.signal_processing
                logger.info("[INIT] Signal processing service initialized")
            
            # Placeholder connections for memory, vector DB, knowledge graph, LLM
            # These would be connected to actual infrastructure in production
            self.shared_infrastructure['memory_framework'] = None  # TODO: Connect to actual memory
            self.shared_infrastructure['vector_database'] = None  # TODO: Connect to actual vector DB
            self.shared_infrastructure['knowledge_graph'] = None  # TODO: Connect to actual knowledge graph
            self.shared_infrastructure['llm_client'] = None  # TODO: Connect to actual LLM
            
            logger.info("[INIT] Shared infrastructure initialized (with placeholder connections)")
            return True
            
        except Exception as e:
            logger.error(f"[INIT] Error initializing shared infrastructure: {e}")
            return False
    
    def _initialize_brains(self) -> bool:
        """Initialize INDIRA and DYON brains.
        
        Returns:
            bool: True if successful.
        """
        try:
            # INDIRA Brain
            if is_component_enabled('indira_brain'):
                self.indira_brain = ConcreteINDIRABrain()
                
                # Connect to shared infrastructure
                self.indira_brain.connect_to_shared_infrastructure(
                    memory_framework=self.shared_infrastructure.get('memory_framework'),
                    vector_database=self.shared_infrastructure.get('vector_database'),
                    knowledge_graph=self.shared_infrastructure.get('knowledge_graph'),
                    llm_client=self.shared_infrastructure.get('llm_client')
                )
                
                # Connect to preservation layer
                if self.preservation_layer:
                    self.indira_brain.connect_to_preservation_layer(self.preservation_layer)
                
                logger.info("[INIT] INDIRA brain initialized")
            
            # DYON Brain
            if is_component_enabled('dyon_brain'):
                self.dyon_brain = ConcreteDYONBrain()
                
                # Connect to shared infrastructure
                self.dyon_brain.connect_to_shared_infrastructure(
                    memory_framework=self.shared_infrastructure.get('memory_framework'),
                    knowledge_graph=self.shared_infrastructure.get('knowledge_graph'),
                    llm_client=self.shared_infrastructure.get('llm_client'),
                    planning_engine=self.shared_infrastructure.get('planning_engine')
                )
                
                # Connect to preservation layer
                if self.preservation_layer:
                    self.dyon_brain.connect_to_preservation_layer(self.preservation_layer)
                
                logger.info("[INIT] DYON brain initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"[INIT] Error initializing brains: {e}")
            return False
    
    def _initialize_coordination_layer(self) -> bool:
        """Initialize coordination layer.
        
        Returns:
            bool: True if successful.
        """
        try:
            if not is_component_enabled('coordination_layer'):
                logger.info("[INIT] Coordination layer disabled, skipping")
                return True
            
            self.coordination_layer = ConcreteCoordinationLayer()
            
            # Connect coordination components
            self.coordination_layer.connect_coordination_components(
                cognitive_economy=self.cognitive_economy,
                operating_modes=self.operating_modes,
                learning_gate=self.learning_gate
            )
            
            logger.info("[INIT] Coordination layer initialized")
            return True
            
        except Exception as e:
            logger.error(f"[INIT] Error initializing coordination layer: {e}")
            return False
    
    def _connect_components(self) -> bool:
        """Connect all components together.
        
        Returns:
            bool: True if successful.
        """
        try:
            # Connect preservation layer to new architecture
            if self.preservation_layer:
                self.preservation_layer.connect_new_architecture(
                    indira_brain=self.indira_brain,
                    dyon_brain=self.dyon_brain,
                    coordination_layer=self.coordination_layer
                )
                logger.info("[INIT] Preservation layer connected to new architecture")
            
            # Register agents with coordination layer
            if self.coordination_layer:
                if self.indira_brain:
                    self.coordination_layer.register_agent(
                        "INDIRA",
                        {"type": "trading", "capabilities": ["market_analysis", "trading", "risk_management"]}
                    )
                
                if self.dyon_brain:
                    self.coordination_layer.register_agent(
                        "DYON",
                        {"type": "engineering", "capabilities": ["system_analysis", "debugging", "planning"]}
                    )
                
                logger.info("[INIT] Agents registered with coordination layer")
            
            return True
            
        except Exception as e:
            logger.error(f"[INIT] Error connecting components: {e}")
            return False
    
    def _set_initial_operating_mode(self) -> bool:
        """Set initial operating mode.
        
        Returns:
            bool: True if successful.
        """
        try:
            if self.operating_modes:
                default_mode = self.config.operating_modes.get('default_mode', 'active')
                
                from coordination_layer.operating_modes import OperatingMode
                from coordination_layer.operating_modes import ModeTransitionReason
                
                try:
                    mode_enum = OperatingMode(default_mode)
                    self.operating_modes.transition_to_mode(
                        target_mode=mode_enum,
                        reason=ModeTransitionReason.SYSTEM_INITIATED,
                        initiator="system"
                    )
                    logger.info(f"[INIT] Operating mode set to {default_mode}")
                except ValueError:
                    logger.warning(f"[INIT] Invalid operating mode: {default_mode}, using default")
            
            return True
            
        except Exception as e:
            logger.error(f"[INIT] Error setting operating mode: {e}")
            return False
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get status of all components.
        
        Returns:
            Dict[str, Any]: Component status information.
        """
        status = {
            "cognitive_architecture_enabled": self.config.enabled if self.config else False,
            "components": {}
        }
        
        # Check each component
        components = {
            "preservation_layer": self.preservation_layer,
            "indira_brain": self.indira_brain,
            "dyon_brain": self.dyon_brain,
            "coordination_layer": self.coordination_layer,
            "cognitive_economy": self.cognitive_economy,
            "operating_modes": self.operating_modes,
            "learning_gate": self.learning_gate,
            "planning_engine": self.planning_engine,
            "signal_processing": self.signal_processing
        }
        
        for name, component in components.items():
            status["components"][name] = {
                "initialized": component is not None,
                "enabled": is_component_enabled(name)
            }
        
        # Add operating mode if available
        if self.operating_modes:
            status["current_operating_mode"] = self.operating_modes.get_current_mode().value
        
        # Add learning gate state if available
        if self.learning_gate:
            status["learning_gate_state"] = self.learning_gate.get_gate_state().value
        
        return status
    
    def shutdown(self) -> bool:
        """Shutdown all components gracefully.
        
        Returns:
            bool: True if shutdown successful.
        """
        try:
            logger.info("[INIT] Starting cognitive architecture shutdown")
            
            # Shutdown coordination layer first
            if self.coordination_layer:
                # Unregister agents
                if self.indira_brain:
                    self.coordination_layer.unregister_agent("INDIRA")
                if self.dyon_brain:
                    self.coordination_layer.unregister_agent("DYON")
                logger.info("[INIT] Agents unregistered from coordination layer")
            
            # Set operating mode to offline
            if self.operating_modes:
                from coordination_layer.operating_modes import OperatingMode, ModeTransitionReason
                self.operating_modes.transition_to_mode(
                    target_mode=OperatingMode.OFFLINE,
                    reason=ModeTransitionReason.SYSTEM_INITIATED,
                    initiator="system"
                )
                logger.info("[INIT] Operating mode set to OFFLINE")
            
            # Close learning gate
            if self.learning_gate:
                from coordination_layer.learning_gate import LearningGateState
                self.learning_gate.set_gate_state(
                    LearningGateState.CLOSED,
                    reason="System shutdown"
                )
                logger.info("[INIT] Learning gate closed")
            
            logger.info("[INIT] Cognitive architecture shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"[INIT] Error during shutdown: {e}")
            return False


def initialize_cognitive_architecture(config_path: Optional[str] = None) -> CognitiveArchitectureInitializer:
    """Initialize cognitive architecture with configuration.
    
    Args:
        config_path: Optional path to configuration file.
        
    Returns:
        CognitiveArchitectureInitializer: Initialized architecture.
    """
    initializer = CognitiveArchitectureInitializer(config_path)
    success = initializer.initialize()
    
    if not success:
        logger.error("[INIT] Cognitive architecture initialization failed")
    
    return initializer


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize cognitive architecture
    initializer = initialize_cognitive_architecture()
    
    # Print status
    status = initializer.get_component_status()
    print("\n=== Cognitive Architecture Status ===")
    print(f"Enabled: {status['cognitive_architecture_enabled']}")
    print("\nComponents:")
    for name, component_status in status['components'].items():
        print(f"  {name}: initialized={component_status['initialized']}, enabled={component_status['enabled']}")
    
    if 'current_operating_mode' in status:
        print(f"\nCurrent Operating Mode: {status['current_operating_mode']}")
    
    if 'learning_gate_state' in status:
        print(f"Learning Gate State: {status['learning_gate_state']}")