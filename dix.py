"""
DIX VISION Runtime Orchestrator Kernel (dix.py)

This is the authoritative entry point for the DIX VISION system.
It serves as the Runtime Orchestrator Kernel, NOT a feature file.

Role:
- Load config
- Initialize runtime engine
- Register services
- Start event loop

Startup Sequence (as per Runtime Specification):
1. Load Config
2. Initialize EventBus
3. Start MemoryService
4. Start Core Runtime
5. Restore Session
6. Start AI Engine
7. Start Execution Engine
8. Start Dashboard (last)
9. Start Monitoring

All services must conform to the Service Interface:
- init()
- start()
- stop()
- health() -> dict
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import unified systems from runtime package
from runtime.config_manager import get_config
from runtime.event_bus import EventBus, Event, EventType, SystemState, get_event_bus
from runtime.platform_abstraction import get_platform_manager
from runtime.failure_handler import get_failure_handler

# Import service implementations from runtime.services package
from runtime.services.core.memory_service import MemoryService
from runtime.services.ai_runtime_engine import AIRuntimeEngine
from runtime.services.execution_engine import ExecutionEngine
from runtime.services.session_restoration import SessionRestorationService
from runtime.services.dashboard_service import DashboardService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("dix")


class ServiceState(Enum):
    """Service states."""
    STOPPED = "STOPPED"
    INITIALIZING = "INITIALIZING"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    ERROR = "ERROR"
    CRASHED = "CRASHED"


@dataclass
class ServiceHealth:
    """Service health information."""
    service: str
    state: ServiceState
    healthy: bool
    message: str
    details: Dict[str, Any]
    timestamp: float


class Service(ABC):
    """Base service interface as per Runtime Specification."""
    
    def __init__(self, name: str):
        self.name = name
        self.state = ServiceState.STOPPED
        self.event_bus: Optional[EventBus] = None
        self.config: Optional[Dict[str, Any]] = None
        
    @abstractmethod
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the service."""
        pass
        
    @abstractmethod
    def start(self) -> bool:
        """Start the service."""
        pass
        
    @abstractmethod
    def stop(self) -> bool:
        """Stop the service."""
        pass
        
    @abstractmethod
    def health(self) -> ServiceHealth:
        """Get service health information."""
        pass
    
    def emit_event(self, event_type: str, payload: Dict[str, Any] = None) -> None:
        """Emit an event through the event bus."""
        if self.event_bus:
            self.event_bus.publish_sync(self.name, event_type, payload or {})



class ValidationService(Service):
    """Validation Service as per Runtime Specification."""
    
    def __init__(self):
        super().__init__("validation_service")
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize validation service."""
        try:
            self.event_bus = event_bus
            self.config = config
            self.state = ServiceState.INITIALIZING
            
            # Subscribe to relevant events
            event_bus.subscribe(EventType.CONTRACT_VIOLATION, self._handle_violation, self.name)
            
            logger.info("Validation service initialized")
            return True
        except Exception as e:
            logger.error(f"Validation service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def _handle_violation(self, event: Event) -> None:
        """Handle contract violation events."""
        logger.warning(f"Contract violation detected: {event.payload}")
        # Validation service is a passive observer, not a controller
        # It only logs and reports violations
    
    def start(self) -> bool:
        """Start validation service."""
        try:
            self.state = ServiceState.STARTING
            self.state = ServiceState.RUNNING
            self.emit_event(EventType.SERVICE_START, {"service": self.name})
            logger.info("Validation service started")
            return True
        except Exception as e:
            logger.error(f"Validation service start failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def stop(self) -> bool:
        """Stop validation service."""
        try:
            self.state = ServiceState.STOPPING
            self.state = ServiceState.STOPPED
            self.emit_event(EventType.SERVICE_STOP, {"service": self.name})
            logger.info("Validation service stopped")
            return True
        except Exception as e:
            logger.error(f"Validation service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get validation service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message="Validation service operational",
            details={},
            timestamp=time.time()
        )


class RuntimeOrchestrator:
    """Runtime Orchestrator Kernel as per Runtime Specification."""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.event_bus: Optional[EventBus] = None
        self.config: Optional[Dict[str, Any]] = None
        self.system_state = SystemState.BOOTING
        self.platform_manager = get_platform_manager()
        self.failure_handler = None
        self._running = False
        self._shutdown_requested = False
        
    def load_config(self) -> bool:
        """Step 1: Load Configuration."""
        try:
            logger.info("Step 1: Loading configuration...")
            self.config = get_config().get_all()
            logger.info("Configuration loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            return False
    
    def initialize_event_bus(self) -> bool:
        """Step 2: Initialize EventBus."""
        try:
            logger.info("Step 2: Initializing EventBus...")
            self.event_bus = get_event_bus()
            self.event_bus.start_async_processing()
            
            # Initialize failure handler
            self.failure_handler = get_failure_handler()
            self.failure_handler.set_event_bus(self.event_bus)
            
            # Subscribe to system events
            self.event_bus.subscribe(EventType.SERVICE_CRASH, self._handle_service_crash, "orchestrator")
            self.event_bus.subscribe(EventType.CONTRACT_VIOLATION, self._handle_contract_violation, "orchestrator")
            
            logger.info("EventBus initialized successfully")
            return True
        except Exception as e:
            logger.error(f"EventBus initialization failed: {e}")
            return False
    
    def register_service(self, service: Service) -> bool:
        """Register a service with the orchestrator."""
        try:
            self.services[service.name] = service
            logger.info(f"Service registered: {service.name}")
            return True
        except Exception as e:
            logger.error(f"Service registration failed for {service.name}: {e}")
            return False
    
    def register_dependency(self, service: str, depends_on: str | List[str]) -> None:
        """Register a service dependency for startup sequence."""
        if isinstance(depends_on, str):
            depends_on = [depends_on]
        self.dependencies[service] = depends_on
        logger.info(f"Registered dependency: {service} depends on {depends_on}")
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service with dependency resolution."""
        if service_name not in self.services:
            logger.error(f"Service not found: {service_name}")
            return False
        
        service = self.services[service_name]
        
        # Check if already running
        if service.state == ServiceState.RUNNING:
            logger.info(f"Service already running: {service_name}")
            return True
        
        # Start dependencies first
        if service_name in self.dependencies:
            for dep in self.dependencies[service_name]:
                if dep in self.services:
                    if not self.start_service(dep):
                        logger.error(f"Failed to start dependency: {dep}")
                        return False
        
        try:
            # Initialize with event bus and config
            service.init(self.event_bus, self.config or {})
            
            # Start the service
            success = service.start()
            
            if success:
                logger.info(f"Service started successfully: {service_name}")
            else:
                logger.error(f"Service failed to start: {service_name}")
            
            return success
        except Exception as e:
            logger.error(f"Service start error for {service_name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service."""
        if service_name not in self.services:
            logger.error(f"Service not found: {service_name}")
            return False
        
        service = self.services[service_name]
        return service.stop()
    
    def _handle_service_crash(self, event: Event) -> None:
        """Handle service crash events."""
        logger.error(f"Service crash detected: {event.payload}")
        self.system_state = SystemState.DEGRADED
        self.emit_system_event(EventType.SYSTEM_DEGRADED, {"crashed_service": event.payload.get("service")})
    
    def _handle_contract_violation(self, event: Event) -> None:
        """Handle contract violation events."""
        logger.warning(f"Contract violation detected: {event.payload}")
        # Validation service handles the actual logging
    
    def emit_system_event(self, event_type: str, payload: Dict[str, Any] = None) -> None:
        """Emit a system-level event."""
        if self.event_bus:
            self.event_bus.publish_sync("orchestrator", event_type, payload or {})
    
    def execute_startup_sequence(self) -> bool:
        """Execute the formal startup sequence as per Runtime Specification."""
        try:
            logger.info("=== DIX VISION Runtime Startup Sequence ===")
            
            # Step 1: Load Config
            if not self.load_config():
                logger.error("Startup failed: Configuration loading")
                return False
            
            # Step 2: Initialize EventBus
            if not self.initialize_event_bus():
                logger.error("Startup failed: EventBus initialization")
                return False
            
            # Register core services in startup order
            self.register_service(MemoryService())
            self.register_service(ValidationService())
            self.register_service(SessionRestorationService())
            self.register_service(AIRuntimeEngine())
            self.register_service(ExecutionEngine())
            self.register_service(DashboardService())
            
            # Register dependencies for startup sequence
            self.register_dependency("session_restoration", "memory_service")
            self.register_dependency("ai_runtime_engine", ["memory_service", "session_restoration"])
            self.register_dependency("execution_engine", ["ai_runtime_engine"])
            self.register_dependency("dashboard_service", ["execution_engine"])
            
            # Step 3: Start MemoryService
            logger.info("Step 3: Starting MemoryService...")
            if not self.start_service("memory_service"):
                logger.error("Startup failed: MemoryService")
                return False
            
            # Step 4: Start Core Runtime
            logger.info("Step 4: Starting Core Runtime...")
            # Core Runtime is composed of the registered services
            # Individual services are started in their respective steps
            logger.info("Core Runtime initialized - services will be started in sequence")
            
            # Step 5: Restore Session
            logger.info("Step 5: Restoring Session...")
            if not self.start_service("session_restoration"):
                logger.error("Startup failed: Session Restoration")
                return False
            logger.info("Session restoration completed")
            
            # Step 6: Start AI Engine
            logger.info("Step 6: Starting AI Engine...")
            if not self.start_service("ai_runtime_engine"):
                logger.error("Startup failed: AI Engine")
                return False
            logger.info("AI Engine started")
            
            # Step 7: Start Execution Engine
            logger.info("Step 7: Starting Execution Engine...")
            if not self.start_service("execution_engine"):
                logger.error("Startup failed: Execution Engine")
                return False
            logger.info("Execution Engine started")
            
            # Step 8: Start Dashboard (must be last)
            logger.info("Step 8: Starting Dashboard (last)...")
            if not self.start_service("dashboard_service"):
                logger.error("Startup failed: Dashboard Service")
                return False
            logger.info("Dashboard Service started")
            
            # Step 9: Start Monitoring
            logger.info("Step 9: Starting Monitoring...")
            if not self.start_service("validation_service"):
                logger.error("Startup failed: Validation Service")
                return False
            
            # Transition to running state
            self.system_state = SystemState.RUNNING
            self.emit_system_event(EventType.SYSTEM_BOOT, {"state": self.system_state.value})
            
            logger.info("=== DIX VISION Runtime Startup Complete ===")
            logger.info(f"System State: {self.system_state.value}")
            return True
            
        except Exception as e:
            logger.error(f"Startup sequence failed: {e}")
            self.system_state = SystemState.DEGRADED
            return False
    
    def execute_shutdown_sequence(self) -> bool:
        """Execute the shutdown sequence in reverse startup order."""
        try:
            logger.info("=== DIX VISION Runtime Shutdown Sequence ===")
            
            self.system_state = SystemState.STOPPED
            self.emit_system_event(EventType.SYSTEM_SHUTDOWN, {"state": self.system_state.value})
            
            # Stop services in reverse dependency order
            # Dashboard first (last to start), then others
            shutdown_order = [
                "dashboard_service",
                "validation_service", 
                "execution_engine",
                "ai_runtime_engine",
                "session_restoration",
                "memory_service"
            ]
            
            for service_name in shutdown_order:
                if service_name in self.services:
                    logger.info(f"Stopping {service_name}...")
                    self.stop_service(service_name)
                else:
                    logger.debug(f"Service {service_name} not found, skipping")
            
            # Stop event bus
            if self.event_bus:
                self.event_bus.stop_async_processing()
            
            logger.info("=== DIX VISION Runtime Shutdown Complete ===")
            return True
            
        except Exception as e:
            logger.error(f"Shutdown sequence failed: {e}")
            return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        health_report = {
            "system_state": self.system_state.value,
            "services": {},
            "timestamp": time.time()
        }
        
        for service_name, service in self.services.items():
            health = service.health()
            health_report["services"][service_name] = {
                "state": health.state.value,
                "healthy": health.healthy,
                "message": health.message,
                "details": health.details
            }
        
        return health_report
    
    def run(self) -> None:
        """Main runtime loop."""
        try:
            self._running = True
            
            # Execute startup sequence
            if not self.execute_startup_sequence():
                logger.error("Runtime startup failed")
                return
            
            # Main event loop
            logger.info("Entering main runtime loop...")
            
            while self._running and not self._shutdown_requested:
                try:
                    # Periodic health checks
                    health = self.get_system_health()
                    
                    # Check for degraded state
                    if self.system_state == SystemState.DEGRADED:
                        logger.warning("System in degraded state, attempting recovery...")
                        self.system_state = SystemState.RECOVERING
                        # TODO: Implement recovery logic
                    
                    # Sleep for next cycle
                    time.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Runtime loop error: {e}")
                    time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
        finally:
            # Execute shutdown sequence
            self.execute_shutdown_sequence()
    
    def shutdown(self) -> None:
        """Request graceful shutdown."""
        logger.info("Shutdown requested")
        self._shutdown_requested = True


def main() -> int:
    """Main entry point for the DIX VISION Runtime."""
    logger.info("=== DIX VISION Runtime Orchestrator Kernel ===")
    logger.info("Authoritative Entry Point: dix.py")
    
    # Setup signal handlers
    orchestrator = RuntimeOrchestrator()
    
    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} received")
        orchestrator.shutdown()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the orchestrator
    try:
        orchestrator.run()
        return 0
    except Exception as e:
        logger.error(f"Runtime failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())