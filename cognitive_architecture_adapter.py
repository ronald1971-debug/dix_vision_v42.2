"""
cognitive_architecture_adapter.py
DIX VISION v42.2 — Cognitive Architecture Integration Adapter

Integrates the new cognitive architecture (INDIRA/DYON brains, coordination layer)
with the existing DIX VISION system components (IndiraEngine, DyonEngine, etc.).
"""

import logging
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from enum import StrEnum

logger = logging.getLogger(__name__)


class IntegrationMode(StrEnum):
    """Integration mode for cognitive architecture."""
    LEGACY_ONLY = "legacy_only"  # Use only legacy components
    NEW_ARCHITECTURE = "new_architecture"  # Use only new architecture
    HYBRID = "hybrid"  # Use both with fallback
    PRESERVATION_MODE = "preservation_mode"  # Preservation layer manages transition


@dataclass
class IntegrationConfig:
    """Configuration for cognitive architecture integration."""
    mode: IntegrationMode = IntegrationMode.PRESERVATION_MODE
    enable_indira_brain: bool = True
    enable_dyon_brain: bool = True
    enable_coordination: bool = True
    fallback_on_error: bool = True
    performance_monitoring: bool = True


class CognitiveArchitectureAdapter:
    """
    Adapter that integrates new cognitive architecture with existing system.
    
    This adapter provides a bridge between:
    - Existing IndiraEngine and new ConcreteINDIRABrain
    - Existing DyonEngine and new ConcreteDYONBrain
    - Existing governance and new CoordinationLayer
    """
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        """Initialize the cognitive architecture adapter.
        
        Args:
            config: Integration configuration. If None, uses defaults.
        """
        self.config = config or IntegrationConfig()
        self._initialized = False
        
        # New architecture components
        self._indira_brain = None
        self._dyon_brain = None
        self._coordination_layer = None
        self._preservation_layer = None
        
        # Existing system components
        self._legacy_indira_engine = None
        self._legacy_dyon_engine = None
        
        # Integration state
        self._integration_health = {
            "indira_integration": "unknown",
            "dyon_integration": "unknown",
            "coordination_integration": "unknown",
            "preservation_integration": "unknown"
        }
        
        logger.info("[ADAPTER] Cognitive architecture adapter created")
    
    def initialize(self) -> bool:
        """Initialize the cognitive architecture adapter.
        
        Returns:
            bool: True if initialization successful.
        """
        try:
            logger.info("[ADAPTER] Initializing cognitive architecture adapter")
            
            # Load preservation layer first
            if self.config.mode in [IntegrationMode.PRESERVATION_MODE, IntegrationMode.NEW_ARCHITECTURE, IntegrationMode.HYBRID]:
                if not self._initialize_preservation_layer():
                    logger.warning("[ADAPTER] Preservation layer initialization failed")
                    if self.config.mode == IntegrationMode.PRESERVATION_MODE:
                        return False
            
            # Initialize new components based on mode
            if self.config.mode in [IntegrationMode.NEW_ARCHITECTURE, IntegrationMode.HYBRID]:
                if self.config.enable_indira_brain:
                    if not self._initialize_indira_brain():
                        logger.warning("[ADAPTER] INDIRA brain initialization failed")
                
                if self.config.enable_dyon_brain:
                    if not self._initialize_dyon_brain():
                        logger.warning("[ADAPTER] DYON brain initialization failed")
                
                if self.config.enable_coordination:
                    if not self._initialize_coordination_layer():
                        logger.warning("[ADAPTER] Coordination layer initialization failed")
            
            # Connect to existing system
            if not self._connect_to_legacy_system():
                logger.warning("[ADAPTER] Legacy system connection failed")
            
            self._initialized = True
            logger.info(f"[ADAPTER] Cognitive architecture adapter initialized in {self.config.mode} mode")
            return True
            
        except Exception as e:
            logger.error(f"[ADAPTER] Initialization failed: {e}")
            return False
    
    def _initialize_preservation_layer(self) -> bool:
        """Initialize preservation layer.
        
        Returns:
            bool: True if successful.
        """
        try:
            from preservation_layer import get_preservation_layer
            
            self._preservation_layer = get_preservation_layer()
            
            # Initialize legacy engines
            if self.config.mode == IntegrationMode.PRESERVATION_MODE:
                success = self._preservation_layer.initialize_legacy_engines()
                self._integration_health["preservation_integration"] = "healthy" if success else "degraded"
                return success
            else:
                self._integration_health["preservation_integration"] = "enabled"
                return True
                
        except Exception as e:
            logger.error(f"[ADAPTER] Preservation layer initialization error: {e}")
            self._integration_health["preservation_integration"] = "failed"
            return False
    
    def _initialize_indira_brain(self) -> bool:
        """Initialize INDIRA brain.
        
        Returns:
            bool: True if successful.
        """
        try:
            from indira_cognitive.indira_brain.concrete import ConcreteINDIRABrain
            
            self._indira_brain = ConcreteINDIRABrain()
            
            # Connect to preservation layer if available
            if self._preservation_layer:
                self._indira_brain.connect_to_preservation_layer(self._preservation_layer)
            
            # Connect to shared infrastructure
            try:
                from shared_infrastructure.unified_memory_framework import get_unified_memory_framework
                from shared_infrastructure.vector_database_adapter import get_vector_database_adapter
                from shared_infrastructure.knowledge_graph_adapter import get_knowledge_graph_adapter
                from shared_infrastructure.planning_engine import get_planning_engine
                
                memory_framework = get_unified_memory_framework()
                vector_database = get_vector_database_adapter()
                knowledge_graph = get_knowledge_graph_adapter()
                planning_engine = get_planning_engine()
                
                # LLM client - placeholder for now (would need actual LLM integration)
                llm_client = None
                
                self._indira_brain.connect_to_shared_infrastructure(
                    memory_framework=memory_framework,
                    vector_database=vector_database,
                    knowledge_graph=knowledge_graph,
                    llm_client=llm_client
                )
                
                logger.info("[ADAPTER] INDIRA brain connected to shared infrastructure")
            except Exception as e:
                logger.warning(f"[ADAPTER] Shared infrastructure connection failed for INDIRA: {e}")
                self._indira_brain.connect_to_shared_infrastructure(
                    memory_framework=None,
                    vector_database=None,
                    knowledge_graph=None,
                    llm_client=None
                )
            
            self._integration_health["indira_integration"] = "healthy"
            logger.info("[ADAPTER] INDIRA brain initialized")
            return True
            
        except Exception as e:
            logger.error(f"[ADAPTER] INDIRA brain initialization error: {e}")
            self._integration_health["indira_integration"] = "failed"
            return False
    
    def _initialize_dyon_brain(self) -> bool:
        """Initialize DYON brain.
        
        Returns:
            bool: True if successful.
        """
        try:
            from dyon_cognitive.dyon_brain.concrete import ConcreteDYONBrain
            
            self._dyon_brain = ConcreteDYONBrain()
            
            # Connect to preservation layer if available
            if self._preservation_layer:
                self._dyon_brain.connect_to_preservation_layer(self._preservation_layer)
            
            # Connect to shared infrastructure
            try:
                from shared_infrastructure.unified_memory_framework import get_unified_memory_framework
                from shared_infrastructure.vector_database_adapter import get_vector_database_adapter
                from shared_infrastructure.knowledge_graph_adapter import get_knowledge_graph_adapter
                from shared_infrastructure.planning_engine import get_planning_engine
                
                memory_framework = get_unified_memory_framework()
                vector_database = get_vector_database_adapter()
                knowledge_graph = get_knowledge_graph_adapter()
                planning_engine = get_planning_engine()
                
                # LLM client - placeholder for now (would need actual LLM integration)
                llm_client = None
                
                self._dyon_brain.connect_to_shared_infrastructure(
                    memory_framework=memory_framework,
                    vector_database=vector_database,
                    knowledge_graph=knowledge_graph,
                    llm_client=llm_client,
                    planning_engine=planning_engine
                )
                
                logger.info("[ADAPTER] DYON brain connected to shared infrastructure")
            except Exception as e:
                logger.warning(f"[ADAPTER] Shared infrastructure connection failed for DYON: {e}")
                self._dyon_brain.connect_to_shared_infrastructure(
                    memory_framework=None,
                    vector_database=None,
                    knowledge_graph=None,
                    llm_client=None,
                    planning_engine=None
                )
            
            self._integration_health["dyon_integration"] = "healthy"
            logger.info("[ADAPTER] DYON brain initialized")
            return True
            
        except Exception as e:
            logger.error(f"[ADAPTER] DYON brain initialization error: {e}")
            self._integration_health["dyon_integration"] = "failed"
            return False
    
    def _initialize_coordination_layer(self) -> bool:
        """Initialize coordination layer.
        
        Returns:
            bool: True if successful.
        """
        try:
            from coordination_layer.concrete import ConcreteCoordinationLayer
            from coordination_layer.cognitive_economy import get_cognitive_economy_manager
            from coordination_layer.operating_modes import get_operating_mode_manager
            from coordination_layer.learning_gate import get_learning_gate_manager
            
            self._coordination_layer = ConcreteCoordinationLayer()
            
            # Connect coordination components
            self._coordination_layer.connect_coordination_components(
                cognitive_economy=get_cognitive_economy_manager(),
                operating_modes=get_operating_mode_manager(),
                learning_gate=get_learning_gate_manager()
            )
            
            # Register agents
            if self._indira_brain:
                self._coordination_layer.register_agent(
                    "INDIRA",
                    {"type": "trading", "capabilities": ["market_analysis", "trading", "risk_management"]}
                )
            
            if self._dyon_brain:
                self._coordination_layer.register_agent(
                    "DYON",
                    {"type": "engineering", "capabilities": ["system_analysis", "debugging", "planning"]}
                )
            
            self._integration_health["coordination_integration"] = "healthy"
            logger.info("[ADAPTER] Coordination layer initialized")
            return True
            
        except Exception as e:
            logger.error(f"[ADAPTER] Coordination layer initialization error: {e}")
            self._integration_health["coordination_integration"] = "failed"
            return False
    
    def _connect_to_legacy_system(self) -> bool:
        """Connect to existing legacy system components.
        
        Returns:
            bool: True if successful.
        """
        try:
            # Try to connect to legacy IndiraEngine
            try:
                from mind.engine import IndiraEngine
                self._legacy_indira_engine = IndiraEngine
                logger.info("[ADAPTER] Connected to legacy IndiraEngine")
            except Exception as e:
                logger.warning(f"[ADAPTER] Could not connect to legacy IndiraEngine: {e}")
            
            # Try to connect to legacy DyonEngine
            try:
                from system_monitor.dyon_engine import get_dyon_engine
                self._legacy_dyon_engine = get_dyon_engine
                logger.info("[ADAPTER] Connected to legacy DyonEngine")
            except Exception as e:
                logger.warning(f"[ADAPTER] Could not connect to legacy DyonEngine: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"[ADAPTER] Legacy system connection error: {e}")
            return False
    
    def enhance_indira_decision(self, market_data: Dict[str, Any], 
                                legacy_event: Any) -> Dict[str, Any]:
        """Enhance Indira decision with new cognitive architecture.
        
        Args:
            market_data: Market data dictionary.
            legacy_event: Legacy execution event from IndiraEngine.
            
        Returns:
            Dict[str, Any]: Enhanced decision data.
        """
        if not self._initialized or not self._indira_brain:
            return {"enhanced": False, "reason": "Cognitive architecture not available"}
        
        try:
            # Use new INDIRA brain for enhanced decision
            asset = market_data.get("asset", "UNKNOWN")
            
            enhanced_decision = self._indira_brain.execute_fast_trading_decision(
                market_state=market_data,
                asset=asset
            )
            
            return {
                "enhanced": True,
                "legacy_event": legacy_event,
                "enhanced_decision": enhanced_decision,
                "integration_mode": self.config.mode,
                "confidence_boost": enhanced_decision.confidence - legacy_event.confidence if hasattr(legacy_event, 'confidence') else 0.0
            }
            
        except Exception as e:
            logger.error(f"[ADAPTER] Indira decision enhancement error: {e}")
            if self.config.fallback_on_error:
                return {"enhanced": False, "reason": f"Enhancement failed: {e}"}
            raise
    
    def enhance_dyon_analysis(self, system_data: Dict[str, Any],
                              legacy_analysis: Any) -> Dict[str, Any]:
        """Enhance DYON analysis with new cognitive architecture.
        
        Args:
            system_data: System data dictionary.
            legacy_analysis: Legacy analysis from DyonEngine.
            
        Returns:
            Dict[str, Any]: Enhanced analysis data.
        """
        if not self._initialized or not self._dyon_brain:
            return {"enhanced": False, "reason": "Cognitive architecture not available"}
        
        try:
            # Use new DYON brain for enhanced analysis
            issue = system_data.get("issue", "System analysis request")
            
            from dyon_cognitive.dyon_brain import ReasoningMode
            enhanced_analysis = self._dyon_brain.reason_about_system(
                issue=issue,
                reasoning_mode=ReasoningMode.ABDUCTIVE
            )
            
            return {
                "enhanced": True,
                "legacy_analysis": legacy_analysis,
                "enhanced_analysis": enhanced_analysis,
                "integration_mode": self.config.mode,
                "reasoning_quality": enhanced_analysis.confidence
            }
            
        except Exception as e:
            logger.error(f"[ADAPTER] DYON analysis enhancement error: {e}")
            if self.config.fallback_on_error:
                return {"enhanced": False, "reason": f"Enhancement failed: {e}"}
            raise
    
    def get_integration_health(self) -> Dict[str, Any]:
        """Get integration health status.
        
        Returns:
            Dict[str, Any]: Health status information.
        """
        return {
            "initialized": self._initialized,
            "mode": self.config.mode,
            "components": self._integration_health,
            "components_enabled": {
                "indira_brain": self.config.enable_indira_brain,
                "dyon_brain": self.config.enable_dyon_brain,
                "coordination": self.config.enable_coordination,
                "preservation": self.config.mode != IntegrationMode.LEGACY_ONLY
            }
        }
    
    def shutdown(self) -> bool:
        """Shutdown the cognitive architecture adapter.
        
        Returns:
            bool: True if shutdown successful.
        """
        try:
            logger.info("[ADAPTER] Shutting down cognitive architecture adapter")
            
            # Shutdown coordination layer
            if self._coordination_layer:
                try:
                    if self._indira_brain:
                        self._coordination_layer.unregister_agent("INDIRA")
                    if self._dyon_brain:
                        self._coordination_layer.unregister_agent("DYON")
                except Exception as e:
                    logger.warning(f"[ADAPTER] Coordination layer shutdown warning: {e}")
            
            self._initialized = False
            logger.info("[ADAPTER] Cognitive architecture adapter shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"[ADAPTER] Shutdown error: {e}")
            return False


# Global adapter instance
_global_adapter: Optional[CognitiveArchitectureAdapter] = None


def get_cognitive_adapter(config: Optional[IntegrationConfig] = None) -> CognitiveArchitectureAdapter:
    """Get global cognitive architecture adapter instance.
    
    Args:
        config: Optional integration configuration.
        
    Returns:
        CognitiveArchitectureAdapter: Global adapter instance.
    """
    global _global_adapter
    if _global_adapter is None:
        _global_adapter = CognitiveArchitectureAdapter(config)
    return _global_adapter


def initialize_cognitive_integration(config: Optional[IntegrationConfig] = None) -> bool:
    """Initialize cognitive architecture integration.
    
    Args:
        config: Optional integration configuration.
        
    Returns:
        bool: True if initialization successful.
    """
    adapter = get_cognitive_adapter(config)
    return adapter.initialize()


if __name__ == "__main__":
    # Test the adapter
    logging.basicConfig(level=logging.INFO)
    
    config = IntegrationConfig(mode=IntegrationMode.PRESERVATION_MODE)
    adapter = CognitiveArchitectureAdapter(config)
    
    if adapter.initialize():
        print("Cognitive architecture adapter initialized successfully")
        print(f"Integration health: {adapter.get_integration_health()}")
    else:
        print("Cognitive architecture adapter initialization failed")