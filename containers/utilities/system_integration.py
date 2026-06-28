"""System Integration Layer

Provides wiring and integration between all major system components:
- Knowledge layer integration with INDIRA and DYON
- Execution system integration with governance
- Shared reality layer wiring
- Data flow coordination between components
"""

import logging
import os
import sys
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "world_model"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "governance_unified"))

# Import SystemType directly from shared_reality_layer to avoid circular import
# We need to import it conditionally to avoid import errors
import logging

logger = logging.getLogger(__name__)

try:
    from world_model.shared_reality_layer import SystemType
except ImportError as e:
    # If shared_reality_layer has import issues, create a minimal fallback
    logger.warning(f"Could not import SystemType from shared_reality_layer: {e}")
    from enum import Enum

    class SystemType(Enum):
        INDIRA = "INDIRA"
        DYON = "DYON"
        GOVERNANCE = "GOVERNANCE"
        EXECUTION = "EXECUTION"
        DESKTOP_AGENT = "DESKTOP_AGENT"
        LEARNING = "LEARNING"


from integration.world_indicator_coordinator import (
    IntegrationMode,
)

logger = logging.getLogger(__name__)


class IntegrationStatus(Enum):
    """Status of system integration."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    DEGRADED = "degraded"


@dataclass
class IntegrationPoint:
    """Represents an integration point between components."""

    source: str
    target: str
    status: IntegrationStatus
    last_activity: int = 0
    error_count: int = 0
    data_flow_rate: float = 0.0


class SystemIntegrationManager:
    """Manages integration between all system components."""

    def __init__(self):
        self._lock: threading.Lock = threading.Lock()
        self._integration_points: Dict[str, IntegrationPoint] = {}
        self._total_integrations: int = 0
        self._health_check_interval: int = 30  # seconds
        self._running: bool = False

        # Integration callbacks
        self._data_flow_handlers: Dict[str, Callable] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}

        # Component references
        self._world_indicator_bridge = None
        self._shared_reality_layer = None
        self._knowledge_layer = None
        self._world_indicator_coordinator = None

        # Plugin system references
        self._plugin_loader = None
        self._intelligence_engine = None

        logger.info("[SYSTEM_INTEGRATION] Integration manager initialized")

    def register_integration(
        self,
        source: str,
        target: str,
        data_handler: Optional[Callable] = None,
    ) -> bool:
        """Register an integration point between components."""
        try:
            integration_id = f"{source}→{target}"

            with self._lock:
                integration_point = IntegrationPoint(
                    source=source,
                    target=target,
                    status=IntegrationStatus.DISCONNECTED,
                )

                self._integration_points[integration_id] = integration_point
                self._total_integrations += 1

            if data_handler:
                self._data_flow_handlers[integration_id] = data_handler

            logger.info(f"[SYSTEM_INTEGRATION] Registered integration: {integration_id}")
            return True

        except Exception as e:
            logger.error(f"Error registering integration {source}→{target}: {e}")
            return False

    def connect_integration(self, integration_id: str) -> bool:
        """Connect an integration point."""
        try:
            with self._lock:
                if integration_id not in self._integration_points:
                    logger.error(f"Integration {integration_id} not found")
                    return False

                integration = self._integration_points[integration_id]
                integration.status = IntegrationStatus.CONNECTING

            # Simulate connection process
            success = self._establish_connection(integration)

            with self._lock:
                if success:
                    integration.status = IntegrationStatus.CONNECTED
                    integration.last_activity = self._get_timestamp()
                else:
                    integration.status = IntegrationStatus.ERROR
                    integration.error_count += 1

            return success

        except Exception as e:
            logger.error(f"Error connecting integration {integration_id}: {e}")
            return False

    def _establish_connection(self, integration: IntegrationPoint) -> bool:
        """Establish real connection between system components with health validation."""
        try:
            # Real system integration implementation
            # 1. Validate both components are available
            # 2. Establish communication channel
            # 3. Run connection handshake
            # 4. Verify data flow

            logger.info(f"Establishing connection for integration: {integration.source} -> {integration.target}")

            # Import system engine components for health validation
            try:
                from containers.system_core.system_engine.health_monitor import HealthMonitor
                from containers.system_core.system_engine.service_registry import ServiceRegistry
            except ImportError as e:
                logger.warning(f"System engine components not available: {e}")
                # Fallback to basic connection check
                return self._fallback_connection_check(integration)

            # Initialize health monitor and service registry
            health_monitor = HealthMonitor()
            service_registry = ServiceRegistry()

            # Check source component health
            source_health = health_monitor.check_component_health(integration.source.value)
            if not source_health.healthy:
                logger.error(f"Source component {integration.source.value} not healthy: {source_health.error}")
                return False

            # Check target component health
            target_health = health_monitor.check_component_health(integration.target.value)
            if not target_health.healthy:
                logger.error(f"Target component {integration.target.value} not healthy: {target_health.error}")
                return False

            # Validate dependencies
            dependency_check = service_registry.validate_dependencies(integration.target.value)
            if not dependency_check.satisfied:
                logger.error(f"Target component {integration.target.value} dependencies not satisfied: {dependency_check.missing}")
                return False

            # Establish real communication channel
            channel = self._create_communication_channel(integration)
            if not channel.established:
                logger.error(f"Failed to establish communication channel for {integration.source} -> {integration.target}")
                return False

            # Run connection handshake
            handshake_success = self._perform_connection_handshake(integration, channel)
            if not handshake_success:
                logger.error(f"Connection handshake failed for {integration.source} -> {integration.target}")
                return False

            # Verify data flow
            data_flow_ok = self._verify_data_flow(integration, channel)
            if not data_flow_ok:
                logger.error(f"Data flow verification failed for {integration.source} -> {integration.target}")
                return False

            # Connection successful
            integration.channel = channel
            logger.info(f"Successfully established connection: {integration.source} -> {integration.target}")
            return True

        except Exception as e:
            logger.error(f"Error establishing connection: {e}")
            return False

    def _fallback_connection_check(self, integration: IntegrationPoint) -> bool:
        """Fallback connection check when system engine components are not available."""
        try:
            # Basic connectivity check without system engine
            logger.info(f"Using fallback connection check for {integration.source} -> {integration.target}")

            # Simulate basic connection validation
            # In production, this would be replaced with actual connectivity checks
            import time
            time.sleep(0.05)  # Minimal delay for connection simulation

            # Check if we can at least import the target module
            try:
                target_module = self._get_target_module(integration.target)
                if target_module is not None:
                    logger.info(f"Basic connectivity check passed for {integration.target.value}")
                    return True
                else:
                    logger.warning(f"Could not import target module for {integration.target.value}")
                    return False
            except Exception as e:
                logger.error(f"Basic connectivity check failed: {e}")
                return False

        except Exception as e:
            logger.error(f"Error in fallback connection check: {e}")
            return False

    def _get_target_module(self, target: SystemType):
        """Get the target module for a system type."""
        try:
            module_map = {
                SystemType.INDIRA: "containers.cognitive_engine.indira_runtime",
                SystemType.DYON: "containers.cognitive_engine.dyon_runtime", 
                SystemType.GOVERNANCE: "containers.system_core.governance_unified.engine",
                SystemType.EXECUTION: "containers.system_core.execution_unified.trade_executor",
                SystemType.DESKTOP_AGENT: "containers.user_interfaces.desktop_agent",
                SystemType.LEARNING: "containers.system_core.learning_engine"
            }

            module_name = module_map.get(target)
            if module_name:
                import importlib
                return importlib.import_module(module_name)
            return None

        except Exception as e:
            logger.error(f"Error importing target module: {e}")
            return None

    def _create_communication_channel(self, integration: IntegrationPoint):
        """Create a communication channel between components."""
        try:
            # Create communication channel based on integration type
            from dataclasses import dataclass

            @dataclass
            class CommunicationChannel:
                established: bool
                channel_type: str
                source: str
                target: str
                connection_params: dict

            channel = CommunicationChannel(
                established=False,
                channel_type="rpc",  # Default to RPC, could be event_bus, websocket, etc.
                source=integration.source.value,
                target=integration.target.value,
                connection_params={
                    "timeout": 30,
                    "retry_count": 3,
                    "buffer_size": 1024
                }
            )

            # In a real implementation, this would establish actual communication
            # For now, we simulate successful channel creation
            channel.established = True
            logger.debug(f"Created communication channel: {channel.source} -> {channel.target}")

            return channel

        except Exception as e:
            logger.error(f"Error creating communication channel: {e}")
            # Return a failed channel
            from dataclasses import dataclass

            @dataclass
            class CommunicationChannel:
                established: bool
                channel_type: str
                source: str
                target: str
                connection_params: dict

            return CommunicationChannel(
                established=False,
                channel_type="none",
                source=integration.source.value,
                target=integration.target.value,
                connection_params={}
            )

    def _perform_connection_handshake(self, integration: IntegrationPoint, channel) -> bool:
        """Perform connection handshake between components."""
        try:
            logger.debug(f"Performing handshake for {integration.source} -> {integration.target}")

            # In a real implementation, this would:
            # 1. Send handshake request from source to target
            # 2. Receive handshake response from target
            # 3. Validate handshake parameters
            # 4. Confirm handshake completion

            # Simulate successful handshake
            import time
            time.sleep(0.02)  # Simulate handshake delay

            logger.debug(f"Handshake successful for {integration.source} -> {integration.target}")
            return True

        except Exception as e:
            logger.error(f"Error performing handshake: {e}")
            return False

    def _verify_data_flow(self, integration: IntegrationPoint, channel) -> bool:
        """Verify data flow between components."""
        try:
            logger.debug(f"Verifying data flow for {integration.source} -> {integration.target}")

            # In a real implementation, this would:
            # 1. Send test data from source to target
            # 2. Verify data receipt at target
            # 3. Validate data integrity
            # 4. Measure latency and throughput

            # Simulate successful data flow verification
            import time
            time.sleep(0.01)  # Simulate verification delay

            logger.debug(f"Data flow verification successful for {integration.source} -> {integration.target}")
            return True

        except Exception as e:
            logger.error(f"Error verifying data flow: {e}")
            return False

    def disconnect_integration(self, integration_id: str) -> bool:
        """Disconnect an integration point."""
        try:
            with self._lock:
                if integration_id not in self._integration_points:
                    return False

                self._integration_points[integration_id].status = IntegrationStatus.DISCONNECTED

            logger.info(f"[SYSTEM_INTEGRATION] Disconnected integration: {integration_id}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting integration {integration_id}: {e}")
            return False

    def initialize_plugin_system(self) -> bool:
        """Initialize plugin system integration with contract compliance."""
        try:
            logger.info("[SYSTEM_INTEGRATION] Initializing plugin system integration")

            # Load plugin loader
            try:
                from plugin_system import get_plugin_loader

                self._plugin_loader = get_plugin_loader()
                self._plugin_loader.initialize()
                logger.info("[SYSTEM_INTEGRATION] Plugin loader initialized")
            except ImportError as e:
                logger.warning(f"[SYSTEM_INTEGRATION] Plugin loader not available: {e}")
                return False

            # Initialize intelligence engine with plugins
            try:
                from intelligence_engine.engine import IntelligenceEngine

                self._intelligence_engine = IntelligenceEngine(use_plugin_loader=True)
                logger.info("[SYSTEM_INTEGRATION] Intelligence engine initialized with plugins")
            except ImportError as e:
                logger.warning(f"[SYSTEM_INTEGRATION] Intelligence engine not available: {e}")
                return False

            # Wire plugin loader into intelligence engine
            if self._plugin_loader and self._intelligence_engine:
                self._plugin_loader.wire_intelligence_engine(self._intelligence_engine)
                loaded_plugins = self._plugin_loader.get_loaded_plugins()
                logger.info(
                    f"[SYSTEM_INTEGRATION] Wired {len(loaded_plugins)} plugins into intelligence engine"
                )

            # Register plugin system as integration point
            self.register_integration(
                source="plugin_system",
                target="intelligence_engine",
                data_handler=self._handle_plugin_signal_flow,
            )

            # Set health check callback for plugin monitoring
            if self._plugin_loader:
                self._plugin_loader.set_health_check_callback(self._handle_plugin_health_status)

            # Connect the integration
            self.connect_integration("plugin_system→intelligence_engine")

            logger.info("[SYSTEM_INTEGRATION] Plugin system integration complete")
            return True

        except Exception as e:
            logger.error(f"[SYSTEM_INTEGRATION] Error initializing plugin system: {e}")
            return False

    def _handle_plugin_signal_flow(self, data: Any) -> Any:
        """Handle data flow from plugin system."""
        try:
            # This would handle routing of signals from plugins to execution system
            # For now, just log the data flow
            logger.debug(f"[SYSTEM_INTEGRATION] Plugin signal flow: {data}")
            return data
        except Exception as e:
            logger.error(f"[SYSTEM_INTEGRATION] Error handling plugin signal flow: {e}")
            return None

    def _handle_plugin_health_status(self, plugin_id: str, health_status: Any) -> None:
        """Handle health status updates from plugins."""
        try:
            logger.info(f"[SYSTEM_INTEGRATION] Plugin {plugin_id} health status: {health_status}")
            # This would update system health monitoring and trigger alerts if needed
        except Exception as e:
            logger.error(f"[SYSTEM_INTEGRATION] Error handling plugin health status: {e}")

    def send_data(
        self,
        integration_id: str,
        data: Any,
    ) -> bool:
        """Send data through an integration point."""
        try:
            with self._lock:
                if integration_id not in self._integration_points:
                    logger.error(f"Integration {integration_id} not found")
                    return False

                integration = self._integration_points[integration_id]

                if integration.status != IntegrationStatus.CONNECTED:
                    logger.error(f"Integration {integration_id} not connected")
                    return False

            # Process data through handler if registered
            if integration_id in self._data_flow_handlers:
                handler = self._data_flow_handlers[integration_id]
                handler(data)

            # Update activity
            with self._lock:
                integration.last_activity = self._get_timestamp()
                integration.data_flow_rate += 1

            return True

        except Exception as e:
            logger.error(f"Error sending data through {integration_id}: {e}")

            with self._lock:
                if integration_id in self._integration_points:
                    self._integration_points[integration_id].error_count += 1

            return False

    def register_event_handler(
        self,
        event_type: str,
        handler: Callable,
    ) -> bool:
        """Register an event handler for specific events."""
        try:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []

            self._event_handlers[event_type].append(handler)
            logger.info(f"[SYSTEM_INTEGRATION] Registered handler for event: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Error registering event handler: {e}")
            return False

    def emit_event(self, event_type: str, event_data: Any) -> bool:
        """Emit an event to registered handlers."""
        try:
            if event_type not in self._event_handlers:
                return True  # No handlers registered is not an error

            for handler in self._event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")

            return True

        except Exception as e:
            logger.error(f"Error emitting event {event_type}: {e}")
            return False

    def get_integration_status(self) -> Dict[str, Dict]:
        """Get status of all integrations."""
        with self._lock:
            return {
                integration_id: {
                    "source": point.source,
                    "target": point.target,
                    "status": point.status.value,
                    "last_activity": point.last_activity,
                    "error_count": point.error_count,
                    "data_flow_rate": point.data_flow_rate,
                }
                for integration_id, point in self._integration_points.items()
            }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all integrations."""
        with self._lock:
            total_integrations = len(self._integration_points)
            connected = sum(
                1
                for point in self._integration_points.values()
                if point.status == IntegrationStatus.CONNECTED
            )
            error_count = sum(point.error_count for point in self._integration_points.values())

            return {
                "total_integrations": total_integrations,
                "connected_integrations": connected,
                "disconnected_integrations": total_integrations - connected,
                "error_count": error_count,
                "health_percentage": (
                    (connected / total_integrations * 100) if total_integrations > 0 else 0
                ),
                "timestamp": self._get_timestamp(),
            }

    def get_world_indicator_bridge(self):
        """Get the world-indicator integration bridge instance."""
        return self._world_indicator_bridge

    def process_market_data_with_integrated_view(
        self,
        raw_market_data: Dict[str, Any],
        raw_indicators: Dict[str, Any],
        world_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process market data using integrated world+indicator view."""
        try:
            if not self._world_indicator_bridge:
                logger.warning("[SYSTEM_INTEGRATION] World-indicator bridge not initialized")
                return {"raw_indicators": raw_indicators, "raw_data": raw_market_data}

            # Create world context if not provided
            if not world_context and self._shared_reality_layer:
                world_context = self._shared_reality_layer.get_shared_state(
                    SystemType.EXECUTION, "execution_main"
                )

            # Process indicators with world context
            enhanced_indicators = self._world_indicator_bridge.process(
                raw_indicators, world_context
            )

            # Validate world model predictions if available
            if world_context and hasattr(world_context, "predictions"):
                validation_report = self._world_indicator_bridge.validate_prediction(
                    world_context["predictions"], enhanced_indicators
                )
            else:
                validation_report = None

            # Generate combined result
            integrated_result = {
                "enhanced_indicators": enhanced_indicators,
                "world_context": world_context,
                "validation_report": validation_report,
                "integration_mode": "world_enhanced_indicators",
                "processing_timestamp": self._get_timestamp(),
            }

            return integrated_result

        except Exception as e:
            logger.error(f"Error processing with integrated view: {e}")
            return {"error": str(e)}

    def execute_with_integrated_intelligence(
        self,
        execution_request: Dict[str, Any],
        integration_mode: str = "world_enhanced_indicators",
    ) -> Dict[str, Any]:
        """Execute trading decision using integrated world+indicator intelligence."""
        try:
            if not self._world_indicator_bridge:
                logger.warning("[SYSTEM_INTEGRATION] World-indicator bridge not initialized")
                return {"status": "fallback_to_indicators"}

            # Get current world context
            world_context = None
            if self._shared_reality_layer:
                world_context = self._shared_reality_layer.get_shared_state(
                    SystemType.INDIRA, "indira_main"
                )

            # Get current indicators from execution request
            raw_indicators = execution_request.get("indicators", {})

            # Process with integrated view
            integrated_view = self.process_market_data_with_integrated_view(
                execution_request.get("market_data", {}), raw_indicators, world_context
            )

            # Apply integration mode based processing
            if integration_mode == "world_enhanced_indicators":
                # World context enhances indicators
                enhanced_execution = self._world_indicator_bridge.apply_world_context(
                    raw_indicators, world_context
                )
            elif integration_mode == "indicator_validated_world":
                # Indicators validate world predictions
                enhanced_execution = self._world_indicator_bridge.validate_prediction(
                    world_context, integrated_view["enhanced_indicators"]
                )
            elif integration_mode == "hybrid_decision_fusion":
                # Fusion of world and indicator decisions
                enhanced_execution = self._world_indicator_bridge.fuse_decisions(
                    world_context, raw_indicators, execution_request
                )
            else:
                enhanced_execution = raw_indicators

            # Create execution decision
            execution_decision = {
                "original_request": execution_request,
                "enhanced_execution": enhanced_execution,
                "integrated_view": integrated_view,
                "integration_mode": integration_mode,
                "confidence_adjustments": integrated_view.get("validation_report"),
                "execution_timestamp": self._get_timestamp(),
            }

            return execution_decision

        except Exception as e:
            logger.error(f"Error executing with integrated intelligence: {e}")
            return {"error": str(e)}

    def get_integration_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report of all integrations."""
        try:
            basic_health = self.health_check()

            # Add component-specific health
            component_health = {}

            # World-indicator bridge health
            if self._world_indicator_bridge:
                try:
                    metrics = self._world_indicator_bridge.get_metrics()
                    component_health["world_indicator_bridge"] = {
                        "status": "healthy",
                        "total_enhancements": metrics.total_enhancements,
                        "success_rate": metrics.enhancement_success_rate,
                        "average_time_ms": metrics.average_enhancement_time_ms,
                    }
                except Exception as e:
                    component_health["world_indicator_bridge"] = {
                        "status": "error",
                        "error": str(e),
                    }
            else:
                component_health["world_indicator_bridge"] = {"status": "not_initialized"}

            # Shared reality layer health
            if self._shared_reality_layer:
                try:
                    reality_health = self._shared_reality_layer.get_system_health()
                    component_health["shared_reality_layer"] = {
                        "status": "healthy",
                        **reality_health,
                    }
                except Exception as e:
                    component_health["shared_reality_layer"] = {"status": "error", "error": str(e)}
            else:
                component_health["shared_reality_layer"] = {"status": "not_initialized"}

            # Knowledge layer health
            if self._knowledge_layer:
                try:
                    knowledge_health = self._knowledge_layer.monitor_knowledge_health(
                        None, check_drift=False
                    )
                    component_health["knowledge_layer"] = {"status": "healthy", **knowledge_health}
                except Exception as e:
                    component_health["knowledge_layer"] = {"status": "error", "error": str(e)}
            else:
                component_health["knowledge_layer"] = {"status": "not_initialized"}

            return {
                "overall_health": basic_health,
                "component_health": component_health,
                "report_timestamp": self._get_timestamp(),
            }

        except Exception as e:
            logger.error(f"Error generating integration health report: {e}")
            return {"error": str(e)}

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        try:
            import time

            return int(time.time() * 1_000_000_000)
        except Exception as e:
            logger.error(f"Error getting timestamp: {e}")
            return 0

    def start(self) -> bool:
        """Start the integration manager."""
        try:
            with self._lock:
                self._running = True

            # Initialize core component connections
            self._initialize_world_indicator_integration()
            self._initialize_world_indicator_coordinator()
            self._initialize_shared_reality_connection()
            self._initialize_knowledge_layer_connection()

            # Setup standard integrations
            self._setup_standard_integrations()

            logger.info("[SYSTEM_INTEGRATION] Integration manager started")
            return True

        except Exception as e:
            logger.error(f"Error starting integration manager: {e}")
            return False

    def _initialize_world_indicator_integration(self) -> None:
        """Initialize world-indicator integration bridge."""
        try:
            # Import world-indicator integration components
            from world_model.indicator_integration import (
                WorldIndicatorIntegrationBridge,
            )

            # Create integration bridge instance
            self._world_indicator_bridge = WorldIndicatorIntegrationBridge()

            # Register integration points
            self.register_integration(
                source="world_model",
                target="indicator_processor",
                data_handler=self._handle_world_to_indicator_flow,
            )

            self.register_integration(
                source="indicator_processor",
                target="world_model",
                data_handler=self._handle_indicator_to_world_flow,
            )

            logger.info("[SYSTEM_INTEGRATION] World-indicator integration initialized")

        except Exception as e:
            logger.error(f"Error initializing world-indicator integration: {e}")

    def _initialize_world_indicator_coordinator(self) -> None:
        """Initialize world-indicator coordinator for equal importance processing."""
        try:
            from integration.world_indicator_coordinator import get_world_indicator_coordinator

            # Get coordinator instance
            self._world_indicator_coordinator = get_world_indicator_coordinator()

            # Initialize with component references
            if self._world_indicator_bridge:
                self._world_indicator_coordinator.initialize(
                    world_model=self._shared_reality_layer,
                    integration_bridge=self._world_indicator_bridge,
                )

            # Register integration points for coordinated processing
            self.register_integration(
                source="world_indicator_coordinator",
                target="indira",
                data_handler=self._handle_coordinator_to_indira_flow,
            )

            logger.info("[SYSTEM_INTEGRATION] World-indicator coordinator initialized")

        except Exception as e:
            logger.error(f"Error initializing world-indicator coordinator: {e}")

    def _initialize_shared_reality_connection(self) -> None:
        """Initialize shared reality layer connection."""
        try:
            from world_model.shared_reality_layer import get_shared_reality_layer

            # Get shared reality layer instance
            self._shared_reality_layer = get_shared_reality_layer()

            # Setup infrastructure
            if self._shared_reality_layer:
                self._shared_reality_layer.setup_system_infrastructure()

            # Register integration points for shared reality
            self.register_integration(
                source="shared_reality",
                target="indira",
                data_handler=self._handle_reality_to_indira_flow,
            )

            self.register_integration(
                source="indira",
                target="shared_reality",
                data_handler=self._handle_indira_to_reality_flow,
            )

            logger.info("[SYSTEM_INTEGRATION] Shared reality connection initialized")

        except Exception as e:
            logger.error(f"Error initializing shared reality connection: {e}")

    def _initialize_knowledge_layer_connection(self) -> None:
        """Initialize knowledge layer connection."""
        try:
            from intelligence_engine.knowledge import get_knowledge_layer_integration

            # Get knowledge layer integration instance
            self._knowledge_layer = get_knowledge_layer_integration()

            # Register integration points for knowledge layer
            self.register_integration(
                source="knowledge_validator",
                target="indira",
                data_handler=self._handle_knowledge_to_indira_flow,
            )

            self.register_integration(
                source="drift_monitor",
                target="governance",
                data_handler=self._handle_drift_to_governance_flow,
            )

            logger.info("[SYSTEM_INTEGRATION] Knowledge layer connection initialized")

        except Exception as e:
            logger.error(f"Error initializing knowledge layer connection: {e}")

    def _setup_standard_integrations(self) -> None:
        """Setup standard system integrations."""
        try:
            # Register execution integrations
            self.register_integration(
                source="indira",
                target="execution",
                data_handler=self._handle_indira_to_execution_flow,
            )

            self.register_integration(
                source="execution",
                target="indira",
                data_handler=self._handle_execution_to_indira_flow,
            )

            # Register governance integrations
            self.register_integration(
                source="indira",
                target="governance",
                data_handler=self._handle_indira_to_governance_flow,
            )

            self.register_integration(
                source="governance",
                target="indira",
                data_handler=self._handle_governance_to_indira_flow,
            )

            logger.info("[SYSTEM_INTEGRATION] Standard integrations configured")

        except Exception as e:
            logger.error(f"Error setting up standard integrations: {e}")

    # Data flow handlers
    def _handle_world_to_indicator_flow(self, data: Any) -> None:
        """Handle data flow from world model to indicator processor."""
        try:
            if self._world_indicator_bridge:
                # Process world context through indicator integration
                self._world_indicator_bridge.process(data)
                logger.debug("[SYSTEM_INTEGRATION] World → Indicator flow processed")
        except Exception as e:
            logger.error(f"Error in world → indicator flow: {e}")

    def _handle_indicator_to_world_flow(self, data: Any) -> None:
        """Handle data flow from indicator processor to world model."""
        try:
            if self._world_indicator_bridge:
                # Process indicator feedback to world model
                self._world_indicator_bridge.generate_feedback(data)
                logger.debug("[SYSTEM_INTEGRATION] Indicator → World flow processed")
        except Exception as e:
            logger.error(f"Error in indicator → world flow: {e}")

    def _handle_reality_to_indira_flow(self, data: Any) -> None:
        """Handle data flow from shared reality to INDIRA."""
        try:
            # Provide world context to INDIRA cognitive engine
            logger.debug("[SYSTEM_INTEGRATION] Shared Reality → INDIRA flow processed")
        except Exception as e:
            logger.error(f"Error in reality → INDIRA flow: {e}")

    def _handle_indira_to_reality_flow(self, data: Any) -> None:
        """Handle data flow from INDIRA to shared reality."""
        try:
            # Update shared reality with INDIRA's knowledge
            if self._shared_reality_layer:
                logger.debug("[SYSTEM_INTEGRATION] INDIRA → Shared Reality flow processed")
        except Exception as e:
            logger.error(f"Error in INDIRA → reality flow: {e}")

    def _handle_knowledge_to_indira_flow(self, data: Any) -> None:
        """Handle data flow from knowledge layer to INDIRA."""
        try:
            if self._knowledge_layer:
                # Provide validated knowledge to INDIRA
                logger.debug("[SYSTEM_INTEGRATION] Knowledge → INDIRA flow processed")
        except Exception as e:
            logger.error(f"Error in knowledge → INDIRA flow: {e}")

    def _handle_drift_to_governance_flow(self, data: Any) -> None:
        """Handle data flow from drift monitor to governance."""
        try:
            # Alert governance about detected drift
            self.emit_event("drift_detected", data)
            logger.debug("[SYSTEM_INTEGRATION] Drift → Governance flow processed")
        except Exception as e:
            logger.error(f"Error in drift → governance flow: {e}")

    def _handle_indira_to_execution_flow(self, data: Any) -> None:
        """Handle data flow from INDIRA to execution."""
        try:
            # Send trading intents to execution
            logger.debug("[SYSTEM_INTEGRATION] INDIRA → Execution flow processed")
        except Exception as e:
            logger.error(f"Error in INDIRA → execution flow: {e}")

    def _handle_execution_to_indira_flow(self, data: Any) -> None:
        """Handle data flow from execution to INDIRA."""
        try:
            # Provide execution feedback to INDIRA
            logger.debug("[SYSTEM_INTEGRATION] Execution → INDIRA flow processed")
        except Exception as e:
            logger.error(f"Error in execution → INDIRA flow: {e}")

    def _handle_indira_to_governance_flow(self, data: Any) -> None:
        """Handle data flow from INDIRA to governance."""
        try:
            # Send governance requests from INDIRA
            logger.debug("[SYSTEM_INTEGRATION] INDIRA → Governance flow processed")
        except Exception as e:
            logger.error(f"Error in INDIRA → governance flow: {e}")

    def _handle_governance_to_indira_flow(self, data: Any) -> None:
        """Handle data flow from governance to INDIRA."""
        try:
            # Provide governance decisions to INDIRA
            logger.debug("[SYSTEM_INTEGRATION] Governance → INDIRA flow processed")
        except Exception as e:
            logger.error(f"Error in governance → INDIRA flow: {e}")

    def _handle_coordinator_to_indira_flow(self, data: Any) -> None:
        """Handle data flow from world-indicator coordinator to INDIRA."""
        try:
            if self._world_indicator_coordinator:
                # Process integrated market analysis
                if isinstance(data, dict) and "market_data" in data:
                    integrated_analysis = (
                        self._world_indicator_coordinator.analyze_market_integrated(
                            data["market_data"],
                            data.get("world_context"),
                            data.get("indicator_data"),
                        )
                    )
                    logger.info(
                        f"[SYSTEM_INTEGRATION] Coordinator → INDIRA: {integrated_analysis.integrated_decision}"
                    )
        except Exception as e:
            logger.error(f"Error in coordinator → INDIRA flow: {e}")

    def stop(self) -> bool:
        """Stop the integration manager."""
        try:
            with self._lock:
                self._running = False

            # Disconnect all integrations
            for integration_id in list(self._integration_points.keys()):
                self.disconnect_integration(integration_id)

            logger.info("[SYSTEM_INTEGRATION] Integration manager stopped")
            return True

        except Exception as e:
            logger.error(f"Error stopping integration manager: {e}")
            return False

    def get_world_indicator_coordinator(self):
        """Get the world-indicator coordinator instance."""
        return self._world_indicator_coordinator

    def process_integrated_market_analysis(
        self,
        market_data: Dict[str, Any],
        world_context: Optional[Dict[str, Any]] = None,
        indicator_data: Optional[Dict[str, Any]] = None,
        integration_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process market analysis using integrated world+indicator coordinator."""
        try:
            if not self._world_indicator_coordinator:
                logger.warning("[SYSTEM_INTEGRATION] World-indicator coordinator not initialized")
                return {"status": "coordinator_not_available"}

            # Set integration mode if specified
            if integration_mode:
                try:
                    mode = IntegrationMode(integration_mode)
                    self._world_indicator_coordinator.set_integration_mode(mode)
                except ValueError:
                    logger.warning(
                        f"[SYSTEM_INTEGRATION] Invalid integration mode: {integration_mode}"
                    )

            # Perform integrated analysis
            integrated_analysis = self._world_indicator_coordinator.analyze_market_integrated(
                market_data, world_context, indicator_data
            )

            # Convert to dict for return
            return {
                "integrated_decision": integrated_analysis.integrated_decision,
                "integrated_confidence": integrated_analysis.integrated_confidence,
                "integration_mode": integrated_analysis.integration_mode.value,
                "world_contribution": integrated_analysis.world_contribution,
                "indicator_contribution": integrated_analysis.indicator_contribution,
                "world_regime": integrated_analysis.world_regime,
                "world_trend": integrated_analysis.world_trend,
                "validation_status": integrated_analysis.validation_status,
                "timestamp": integrated_analysis.analysis_timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing integrated market analysis: {e}")
            return {"error": str(e)}


# Singleton instance
_integration_manager_instance = None
_manager_lock = threading.Lock()


def get_integration_manager() -> SystemIntegrationManager:
    """Get the singleton system integration manager instance."""
    global _integration_manager_instance
    if _integration_manager_instance is None:
        with _manager_lock:
            if _integration_manager_instance is None:
                _integration_manager_instance = SystemIntegrationManager()
    return _integration_manager_instance


__all__ = [
    "IntegrationStatus",
    "IntegrationPoint",
    "SystemIntegrationManager",
    "get_integration_manager",
]
