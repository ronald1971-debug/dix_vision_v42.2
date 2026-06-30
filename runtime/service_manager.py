"""
DIX VISION Service Manager (Updated for Runtime Specification)

Centralized service lifecycle management system aligned with the
Runtime Specification service contract.

Service Interface (per Runtime Specification):
- init(event_bus, config) -> bool
- start() -> bool
- stop() -> bool
- health() -> ServiceHealth

All services must conform to this interface.
"""

from __future__ import annotations

import logging
import subprocess
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# Import from runtime specification
from runtime.event_bus import EventBus, Event, get_event_bus

logger = logging.getLogger(__name__)


class ServiceState(Enum):
    """Service states as per Runtime Specification."""
    STOPPED = "STOPPED"
    INITIALIZING = "INITIALIZING"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    ERROR = "ERROR"
    CRASHED = "CRASHED"


@dataclass
class ServiceHealth:
    """Service health information as per Runtime Specification."""
    service: str
    state: ServiceState
    healthy: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class Service(ABC):
    """Base service interface as per Runtime Specification."""
    
    # Service dependencies - can be overridden by subclasses
    DEPENDENCIES: list[str] = []
    
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


class ConfigService(Service):
    """Configuration service as per Runtime Specification."""
    
    def __init__(self):
        super().__init__("config_service")
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the configuration service."""
        try:
            self.event_bus = event_bus
            self.config = config
            self.state = ServiceState.INITIALIZING
            
            # Configuration operates on-demand through config_manager
            self.state = ServiceState.STOPPED
            logger.info("Configuration service initialized")
            return True
        except Exception as e:
            logger.error(f"Config service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
        
    def start(self) -> bool:
        """Start the configuration service."""
        try:
            self.state = ServiceState.STARTING
            # Configuration service doesn't need active startup
            self.state = ServiceState.RUNNING
            self.emit_event("SERVICE_START", {"service": self.name})
            logger.info("Configuration service started")
            return True
        except Exception as e:
            logger.error(f"Config service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event("SERVICE_CRASH", {"service": self.name, "error": str(e)})
            return False
        
    def stop(self) -> bool:
        """Stop the configuration service."""
        try:
            self.state = ServiceState.STOPPING
            # Configuration service doesn't need cleanup
            self.state = ServiceState.STOPPED
            self.emit_event("SERVICE_STOP", {"service": self.name})
            logger.info("Configuration service stopped")
            return True
        except Exception as e:
            logger.error(f"Config service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
        
    def health(self) -> ServiceHealth:
        """Check configuration service health."""
        try:
            from runtime.config_manager import get_config
            config = get_config()
            config.get("system.mode")  # Test config access
            return ServiceHealth(
                service=self.name,
                state=self.state,
                healthy=True,
                message="Configuration service healthy",
                details={},
                timestamp=time.time()
            )
        except Exception as e:
            return ServiceHealth(
                service=self.name,
                state=ServiceState.ERROR,
                healthy=False,
                message=f"Configuration service unhealthy: {e}",
                details={},
                timestamp=time.time()
            )


class BackendService(Service):
    """Python backend service as per Runtime Specification."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        super().__init__("backend_service")
        self.host = host
        self.port = port
        self.backend_path = None
        self._process = None
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the backend service."""
        try:
            self.event_bus = event_bus
            self.config = config
            self.state = ServiceState.INITIALIZING
            
            # Find backend path
            project_root = Path.cwd()
            self.backend_path = project_root / "containers" / "user_interfaces" / "ui"
            
            if not self.backend_path.exists():
                raise FileNotFoundError(f"Backend path not found: {self.backend_path}")
            
            self.state = ServiceState.STOPPED
            logger.info("Backend service initialized")
            return True
        except Exception as e:
            logger.error(f"Backend service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
        
    def start(self) -> bool:
        """Start the backend service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start backend as subprocess
            cmd = ["python", "-m", "http.server", str(self.port), "--bind", self.host]
            self._process = subprocess.Popen(
                cmd,
                cwd=str(self.backend_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for startup
            time.sleep(2)
            
            if self._process.poll() is None:
                self.state = ServiceState.RUNNING
                self.emit_event("SERVICE_START", {"service": self.name})
                logger.info(f"Backend service started on {self.host}:{self.port}")
                return True
            else:
                self.state = ServiceState.ERROR
                logger.error("Backend service failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Backend service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event("SERVICE_CRASH", {"service": self.name, "error": str(e)})
            return False
        
    def stop(self) -> bool:
        """Stop the backend service."""
        try:
            self.state = ServiceState.STOPPING
            
            if self._process and self._process.poll() is None:
                self._process.terminate()
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self._process.wait()
            
            self.state = ServiceState.STOPPED
            self.emit_event("SERVICE_STOP", {"service": self.name})
            logger.info("Backend service stopped")
            return True
        except Exception as e:
            logger.error(f"Backend service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
        
    def health(self) -> ServiceHealth:
        """Check backend service health."""
        try:
            if not self._process:
                return ServiceHealth(
                    service=self.name,
                    state=self.state,
                    healthy=False,
                    message="Backend process not running",
                    details={},
                    timestamp=time.time()
                )
            
            if self._process.poll() is not None:
                return ServiceHealth(
                    service=self.name,
                    state=ServiceState.CRASHED,
                    healthy=False,
                    message="Backend process has terminated",
                    details={},
                    timestamp=time.time()
                )
            
            return ServiceHealth(
                service=self.name,
                state=self.state,
                healthy=True,
                message=f"Backend running on {self.host}:{self.port}",
                details={
                    "host": self.host,
                    "port": self.port
                },
                timestamp=time.time()
            )
        except Exception as e:
            return ServiceHealth(
                service=self.name,
                state=ServiceState.ERROR,
                healthy=False,
                message=f"Backend service unhealthy: {e}",
                details={},
                timestamp=time.time()
            )


class DashboardService(Service):
    """React dashboard service as per Runtime Specification."""
    
    def __init__(self, port: int = 5173):
        super().__init__("dashboard_service")
        self.port = port
        self.dashboard_path = None
        self._process = None
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the dashboard service."""
        try:
            self.event_bus = event_bus
            self.config = config
            self.state = ServiceState.INITIALIZING
            
            # Find dashboard path
            project_root = Path.cwd()
            self.dashboard_path = project_root / "containers" / "user_interfaces" / "dashboard2026"
            
            if not self.dashboard_path.exists():
                raise FileNotFoundError(f"Dashboard path not found: {self.dashboard_path}")
            
            self.state = ServiceState.STOPPED
            logger.info("Dashboard service initialized")
            return True
        except Exception as e:
            logger.error(f"Dashboard service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
        
    def start(self) -> bool:
        """Start the dashboard service."""
        try:
            self.state = ServiceState.STARTING
            
            # Install dependencies if needed
            node_modules = self.dashboard_path / "node_modules"
            if not node_modules.exists():
                logger.info("Installing dashboard dependencies...")
                subprocess.run(["npm", "install"], cwd=str(self.dashboard_path), check=True)
            
            # Start dashboard as subprocess
            cmd = ["npm", "run", "dev"]
            self._process = subprocess.Popen(
                cmd,
                cwd=str(self.dashboard_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for startup
            time.sleep(5)
            
            if self._process.poll() is None:
                self.state = ServiceState.RUNNING
                self.emit_event("SERVICE_START", {"service": self.name})
                self.emit_event("DASHBOARD_READY", {"port": self.port})
                logger.info(f"Dashboard service started on port {self.port}")
                return True
            else:
                self.state = ServiceState.ERROR
                logger.error("Dashboard service failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Dashboard service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event("SERVICE_CRASH", {"service": self.name, "error": str(e)})
            return False
        
    def stop(self) -> bool:
        """Stop the dashboard service."""
        try:
            self.state = ServiceState.STOPPING
            
            if self._process and self._process.poll() is None:
                self._process.terminate()
                try:
                    self._process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self._process.wait()
            
            self.state = ServiceState.STOPPED
            self.emit_event("SERVICE_STOP", {"service": self.name})
            logger.info("Dashboard service stopped")
            return True
        except Exception as e:
            logger.error(f"Dashboard service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
        
    def health(self) -> ServiceHealth:
        """Check dashboard service health."""
        try:
            if not self._process:
                return ServiceHealth(
                    service=self.name,
                    state=self.state,
                    healthy=False,
                    message="Dashboard process not running",
                    details={},
                    timestamp=time.time()
                )
            
            if self._process.poll() is not None:
                return ServiceHealth(
                    service=self.name,
                    state=ServiceState.CRASHED,
                    healthy=False,
                    message="Dashboard process has terminated",
                    details={},
                    timestamp=time.time()
                )
            
            return ServiceHealth(
                service=self.name,
                state=self.state,
                healthy=True,
                message=f"Dashboard running on port {self.port}",
                details={
                    "port": self.port
                },
                timestamp=time.time()
            )
        except Exception as e:
            return ServiceHealth(
                service=self.name,
                state=ServiceState.ERROR,
                healthy=False,
                message=f"Dashboard service unhealthy: {e}",
                details={},
                timestamp=time.time()
            )


class DockerService(Service):
    """Docker container service as per Runtime Specification."""
    
    def __init__(self, compose_file: str = "docker-compose.main.yml"):
        super().__init__("docker_service")
        self.compose_file = compose_file
        self.project_root = Path.cwd()
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize Docker service."""
        try:
            self.event_bus = event_bus
            self.config = config
            self.state = ServiceState.INITIALIZING
            
            compose_path = self.project_root / self.compose_file
            if not compose_path.exists():
                raise FileNotFoundError(f"Docker compose file not found: {compose_path}")
            
            self.state = ServiceState.STOPPED
            logger.info("Docker service initialized")
            return True
        except Exception as e:
            logger.error(f"Docker service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
        
    def start(self) -> bool:
        """Start Docker containers."""
        try:
            self.state = ServiceState.STARTING
            
            compose_path = self.project_root / self.compose_file
            subprocess.run(
                ["docker-compose", "-f", str(compose_path), "up", "-d"],
                cwd=str(self.project_root),
                check=True
            )
            
            # Wait for containers to start
            time.sleep(10)
            
            self.state = ServiceState.RUNNING
            self.emit_event("SERVICE_START", {"service": self.name})
            logger.info("Docker service started")
            return True
            
        except Exception as e:
            logger.error(f"Docker service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event("SERVICE_CRASH", {"service": self.name, "error": str(e)})
            return False
        
    def stop(self) -> bool:
        """Stop Docker containers."""
        try:
            self.state = ServiceState.STOPPING
            
            compose_path = self.project_root / self.compose_file
            subprocess.run(
                ["docker-compose", "-f", str(compose_path), "down"],
                cwd=str(self.project_root),
                check=True
            )
            
            self.state = ServiceState.STOPPED
            self.emit_event("SERVICE_STOP", {"service": self.name})
            logger.info("Docker service stopped")
            return True
            
        except Exception as e:
            logger.error(f"Docker service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
        
    def health(self) -> ServiceHealth:
        """Check Docker service health."""
        try:
            compose_path = self.project_root / self.compose_file
            result = subprocess.run(
                ["docker-compose", "-f", str(compose_path), "ps"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            healthy = result.returncode == 0
            return ServiceHealth(
                service=self.name,
                state=self.state,
                healthy=healthy,
                message="Docker containers healthy" if healthy else "Docker containers unhealthy",
                details={
                    "compose_file": self.compose_file
                },
                timestamp=time.time()
            )
        except Exception as e:
            return ServiceHealth(
                service=self.name,
                state=ServiceState.ERROR,
                healthy=False,
                message=f"Docker service unhealthy: {e}",
                details={},
                timestamp=time.time()
            )


class ServiceManager:
    """Centralized service lifecycle management as per Runtime Specification."""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.event_bus: Optional[EventBus] = None
        self.config: Optional[Dict[str, Any]] = None
        self._lock = threading.Lock()
        
    def set_event_bus(self, event_bus: EventBus) -> None:
        """Set the event bus for service communication."""
        self.event_bus = event_bus
        
    def set_config(self, config: Dict[str, Any]) -> None:
        """Set the configuration for services."""
        self.config = config
    
    def register_service(self, service: Service) -> None:
        """Register a service with the manager."""
        with self._lock:
            self.services[service.name] = service
            logger.info(f"Registered service: {service.name}")
    
    def register_dependency(self, service: str, depends_on: str | List[str]) -> None:
        """Register a service dependency."""
        with self._lock:
            if isinstance(depends_on, str):
                depends_on = [depends_on]
            self.dependencies[service] = depends_on
            logger.info(f"Registered dependency: {service} depends on {depends_on}")
    
    def initialize_service(self, service: str) -> bool:
        """Initialize a service with event bus and config."""
        with self._lock:
            if service not in self.services:
                logger.error(f"Service not found: {service}")
                return False
            
            service_obj = self.services[service]
            
            # Initialize dependencies first
            if service in self.dependencies:
                for dep in self.dependencies[service]:
                    if not self.initialize_service(dep):
                        logger.error(f"Failed to initialize dependency: {dep}")
                        return False
            
            # Initialize the service
            logger.info(f"Initializing service: {service}")
            success = service_obj.init(self.event_bus, self.config or {})
            
            return success
    
    def start_service(self, service: str) -> bool:
        """Start a service with dependency resolution."""
        with self._lock:
            if service not in self.services:
                logger.error(f"Service not found: {service}")
                return False
            
            service_obj = self.services[service]
            
            # Check if already running
            if service_obj.state == ServiceState.RUNNING:
                logger.info(f"Service already running: {service}")
                return True
            
            # Start dependencies first
            if service in self.dependencies:
                for dep in self.dependencies[service]:
                    if not self.start_service(dep):
                        logger.error(f"Failed to start dependency: {dep}")
                        return False
            
            # Start the service
            logger.info(f"Starting service: {service}")
            success = service_obj.start()
            
            return success
    
    def stop_service(self, service: str) -> bool:
        """Stop a service."""
        with self._lock:
            if service not in self.services:
                logger.error(f"Service not found: {service}")
                return False
            
            service_obj = self.services[service]
            
            # Stop dependent services first
            dependents = [s for s, deps in self.dependencies.items() if service in deps]
            for dependent in dependents:
                if not self.stop_service(dependent):
                    logger.warning(f"Failed to stop dependent service: {dependent}")
            
            # Stop the service
            logger.info(f"Stopping service: {service}")
            success = service_obj.stop()
            
            return success
    
    def restart_service(self, service: str) -> bool:
        """Restart a service."""
        logger.info(f"Restarting service: {service}")
        if self.stop_service(service):
            time.sleep(2)
            return self.start_service(service)
        return False
    
    def get_service_health(self, service: str) -> ServiceHealth:
        """Get service health status."""
        with self._lock:
            if service in self.services:
                return self.services[service].health()
            return ServiceHealth(
                service=service,
                state=ServiceState.STOPPED,
                healthy=False,
                message=f"Service not found: {service}",
                details={},
                timestamp=time.time()
            )
    
    def start_all(self) -> Dict[str, bool]:
        """Start all services in dependency order."""
        results = {}
        for service in self.services:
            results[service] = self.start_service(service)
        return results
    
    def stop_all(self) -> Dict[str, bool]:
        """Stop all services in reverse dependency order."""
        results = {}
        # Stop in reverse order
        for service in reversed(list(self.services.keys())):
            results[service] = self.stop_service(service)
        return results
    
    def get_all_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all services."""
        status = {}
        for service in self.services:
            health = self.get_service_health(service)
            status[service] = {
                "state": health.state.value,
                "healthy": health.healthy,
                "message": health.message,
                "details": health.details
            }
        return status


# Global instance
_service_manager: Optional[ServiceManager] = None
_lock = threading.Lock()


def get_service_manager() -> ServiceManager:
    """Get global service manager instance."""
    global _service_manager
    if _service_manager is None:
        with _lock:
            if _service_manager is None:
                _service_manager = ServiceManager()
                _initialize_default_services(_service_manager)
    return _service_manager


def _initialize_default_services(service_manager: ServiceManager) -> None:
    """Initialize default services."""
    # Register services
    service_manager.register_service(ConfigService())
    service_manager.register_service(MemoryService())
    service_manager.register_service(BackendService())
    service_manager.register_service(DashboardService())
    service_manager.register_service(DockerService())
    
    # Register dependencies
    service_manager.register_dependency("memory_service", "config_service")
    service_manager.register_dependency("backend_service", ["config_service", "memory_service"])
    service_manager.register_dependency("dashboard_service", "backend_service")
    service_manager.register_dependency("docker_service", ["backend_service", "dashboard_service"])


__all__ = [
    "ServiceManager",
    "Service",
    "ServiceState",
    "ServiceHealth",
    "ConfigService",
    "MemoryService",
    "BackendService",
    "DashboardService",
    "DockerService",
    "get_service_manager",
]