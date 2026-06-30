"""
DIX VISION Development Environment Service

Provides development containers, hot reload, debugging tools, 
and development workflow automation for enhanced developer experience.
"""

from __future__ import annotations

import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json
import hashlib

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class ContainerStatus(Enum):
    """Container status."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    BUILDING = "building"


class DevTool(Enum):
    """Development tools."""
    DEBUGGER = "debugger"
    PROFILER = "profiler"
    LINTER = "linter"
    TEST_RUNNER = "test_runner"
    HOT_RELOAD = "hot_reload"


@dataclass
class DevContainer:
    """Development container configuration."""
    container_id: str
    container_name: str
    image: str
    status: ContainerStatus = ContainerStatus.STOPPED
    ports: Dict[str, str] = field(default_factory=dict)
    volumes: Dict[str, str] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    command: str = ""
    auto_start: bool = False
    created_at: float = field(default_factory=time.time)


@dataclass
class HotReloadConfig:
    """Hot reload configuration."""
    reload_id: str
    watch_paths: List[str]
    reload_command: str
    debounce_interval: float = 1.0  # seconds
    enabled: bool = True
    last_reload: float = 0.0


@dataclass
class DebugSession:
    """Debug session information."""
    session_id: str
    service_name: str
    breakpoint_file: str
    breakpoint_line: int
    variables: Dict[str, Any] = field(default_factory=dict)
    call_stack: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "active"  # "active", "paused", "completed"
    created_at: float = field(default_factory=time.time)


class DevelopmentEnvironmentService(Service):
    """Development environment service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("development_environment_service")
        self._containers: Dict[str, DevContainer] = {}
        self._hot_reload_configs: Dict[str, HotReloadConfig] = {}
        self._debug_sessions: Dict[str, DebugSession] = {}
        self._dev_tools: Dict[DevTool, bool] = defaultdict(bool)
        self._build_queue: deque = deque(maxlen=100)
        self._lock = threading.Lock()
        self._docker_available = False
        self._auto_start_containers = False
        self._auto_hot_reload = False
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the development environment service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            dev_config = config.get("development_environment", {})
            self._auto_start_containers = dev_config.get("auto_start_containers", False)
            self._auto_hot_reload = dev_config.get("auto_hot_reload", False)
            
            # Check Docker availability
            self._docker_available = self._check_docker_available()
            
            # Initialize default containers
            self._init_default_containers()
            
            # Initialize default hot reload configs
            self._init_default_hot_reload()
            
            logger.info("Development Environment Service initialized")
            return True
        except Exception as e:
            logger.error(f"Development Environment Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the development environment service."""
        try:
            self.state = ServiceState.STARTING
            
            # Auto-start containers if enabled
            if self._auto_start_containers and self._docker_available:
                self._start_containers()
            
            # Start hot reload if enabled
            if self._auto_hot_reload:
                self._start_hot_reload_monitor()
            
            # Start build queue processor
            self._start_build_processor()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Development Environment Service started")
            return True
        except Exception as e:
            logger.error(f"Development Environment Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the development environment service."""
        try:
            self.state = ServiceState.STOPPING
            self._auto_hot_reload = False
            
            # Stop all containers
            for container_id in list(self._containers.keys()):
                self.stop_container(container_id)
            
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Development Environment Service stopped")
            return True
        except Exception as e:
            logger.error(f"Development Environment Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get development environment service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Development Environment Service - {len(self._containers)} containers",
            details={
                "total_containers": len(self._containers),
                "running_containers": sum(1 for c in self._containers.values() if c.status == ContainerStatus.RUNNING),
                "docker_available": self._docker_available,
                "hot_reload_configs": len(self._hot_reload_configs),
                "active_debug_sessions": len(self._debug_sessions),
                "dev_tools_enabled": sum(1 for enabled in self._dev_tools.values() if enabled)
            },
            timestamp=time.time()
        )
    
    def create_container(self, container: DevContainer) -> bool:
        """Create a development container."""
        if not self._docker_available:
            logger.warning("Docker not available, container creation simulated")
            container.status = ContainerStatus.RUNNING
            with self._lock:
                self._containers[container.container_id] = container
            return True
        
        with self._lock:
            if container.container_id in self._containers:
                logger.error(f"Container {container.container_id} already exists")
                return False
            
            self._containers[container.container_id] = container
            self._build_queue.append(("create", container))
            
            logger.info(f"Created container: {container.container_name}")
            return True
    
    def start_container(self, container_id: str) -> bool:
        """Start a container."""
        if not self._docker_available:
            with self._lock:
                if container_id in self._containers:
                    self._containers[container_id].status = ContainerStatus.RUNNING
            return True
        
        with self._lock:
            container = self._containers.get(container_id)
            if not container:
                return False
            
            try:
                # In production, this would use Docker SDK
                # For now, simulate container start
                container.status = ContainerStatus.RUNNING
                logger.info(f"Started container: {container.container_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to start container {container_id}: {e}")
                container.status = ContainerStatus.ERROR
                return False
    
    def stop_container(self, container_id: str) -> bool:
        """Stop a container."""
        if not self._docker_available:
            with self._lock:
                if container_id in self._containers:
                    self._containers[container_id].status = ContainerStatus.STOPPED
            return True
        
        with self._lock:
            container = self._containers.get(container_id)
            if not container:
                return False
            
            try:
                # In production, this would use Docker SDK
                container.status = ContainerStatus.STOPPED
                logger.info(f"Stopped container: {container.container_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to stop container {container_id}: {e}")
                return False
    
    def setup_hot_reload(self, config: HotReloadConfig) -> bool:
        """Setup hot reload for a project."""
        with self._lock:
            self._hot_reload_configs[config.reload_id] = config
            logger.info(f"Setup hot reload: {config.reload_id}")
            return True
    
    def trigger_hot_reload(self, reload_id: str) -> bool:
        """Trigger hot reload for a specific configuration."""
        with self._lock:
            config = self._hot_reload_configs.get(reload_id)
            if not config or not config.enabled:
                return False
            
            try:
                # Execute reload command
                subprocess.run(config.reload_command, shell=True, check=True)
                
                config.last_reload = time.time()
                logger.info(f"Hot reload triggered: {reload_id}")
                return True
                
            except Exception as e:
                logger.error(f"Hot reload failed for {reload_id}: {e}")
                return False
    
    def start_debug_session(self, service_name: str, breakpoint_file: str, 
                         breakpoint_line: int) -> DebugSession:
        """Start a debug session."""
        session_id = self._generate_id()
        
        debug_session = DebugSession(
            session_id=session_id,
            service_name=service_name,
            breakpoint_file=breakpoint_file,
            breakpoint_line=breakpoint_line
        )
        
        with self._lock:
            self._debug_sessions[session_id] = debug_session
            self._dev_tools[DevTool.DEBUGGER] = True
        
        logger.info(f"Started debug session: {session_id}")
        return debug_session
    
    def stop_debug_session(self, session_id: str) -> bool:
        """Stop a debug session."""
        with self._lock:
            if session_id not in self._debug_sessions:
                return False
            
            self._debug_sessions[session_id].status = "completed"
            del self._debug_sessions[session_id]
            
            if not self._debug_sessions:
                self._dev_tools[DevTool.DEBUGGER] = False
            
            logger.info(f"Stopped debug session: {session_id}")
            return True
    
    def enable_dev_tool(self, tool: DevTool) -> bool:
        """Enable a development tool."""
        with self._lock:
            self._dev_tools[tool] = True
            logger.info(f"Enabled dev tool: {tool.value}")
            return True
    
    def disable_dev_tool(self, tool: DevTool) -> bool:
        """Disable a development tool."""
        with self._lock:
            self._dev_tools[tool] = False
            logger.info(f"Disabled dev tool: {tool.value}")
            return True
    
    def get_container_status(self, container_id: str = None) -> List[DevContainer]:
        """Get container status."""
        with self._lock:
            if container_id:
                return [self._containers.get(container_id)] if container_id in self._containers else []
            
            return list(self._containers.values())
    
    def get_hot_reload_status(self, reload_id: str = None) -> List[HotReloadConfig]:
        """Get hot reload status."""
        with self._lock:
            if reload_id:
                return [self._hot_reload_configs.get(reload_id)] if reload_id in self._hot_reload_configs else []
            
            return list(self._hot_reload_configs.values())
    
    def get_debug_sessions(self) -> List[DebugSession]:
        """Get all debug sessions."""
        with self._lock:
            return list(self._debug_sessions.values())
    
    def get_dev_environment_stats(self) -> Dict[str, Any]:
        """Get development environment statistics."""
        with self._lock:
            return {
                "total_containers": len(self._containers),
                "running_containers": sum(1 for c in self._containers.values() if c.status == ContainerStatus.RUNNING),
                "stopped_containers": sum(1 for c in self._containers.values() if c.status == ContainerStatus.STOPPED),
                "hot_reload_configs": len(self._hot_reload_configs),
                "active_hot_reloads": sum(1 for c in self._hot_reload_configs.values() if c.enabled),
                "debug_sessions": len(self._debug_sessions),
                "dev_tools": {tool.value: enabled for tool, enabled in self._dev_tools.items()},
                "docker_available": self._docker_available,
                "build_queue_size": len(self._build_queue)
            }
    
    def _check_docker_available(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
        except Exception:
            return False
    
    def _init_default_containers(self) -> None:
        """Initialize default development containers."""
        if not self._docker_available:
            logger.warning("Docker not available, skipping container initialization")
            return
        
        # Example development containers
        default_containers = [
            DevContainer(
                container_id="dev_primary",
                container_name="DIX VISION Development",
                image="python:3.9-slim",
                ports={"8000": "8000"},
                volumes={"./src": "/app/src"},
                environment={"PYTHONPATH": "/app"},
                command="python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
            ),
            DevContainer(
                container_id="dev_database",
                container_name="DIX VISION Database",
                image="postgres:13",
                ports={"5432": "5432"},
                volumes={"./data": "/var/lib/postgresql/data"},
                environment={"POSTGRES_PASSWORD": "dev_password"}
            )
        ]
        
        for container in default_containers:
            self.create_container(container)
    
    def _init_default_hot_reload(self) -> None:
        """Initialize default hot reload configurations."""
        default_configs = [
            HotReloadConfig(
                reload_id="python_hot_reload",
                watch_paths=["./src", "./runtime"],
                reload_command="pkill -f -HUP uvicorn || echo 'Hot reload triggered'",
                debounce_interval=1.0
            )
        ]
        
        for config in default_configs:
            self.setup_hot_reload(config)
    
    def _start_containers(self) -> None:
        """Start all containers marked for auto-start."""
        for container_id, container in self._containers.items():
            if container.auto_start:
                self.start_container(container_id)
    
    def _start_hot_reload_monitor(self) -> None:
        """Start background hot reload monitor."""
        def monitor_hot_reload():
            while self._auto_hot_reload and self.state == ServiceState.RUNNING:
                try:
                    current_time = time.time()
                    
                    for reload_id, config in self._hot_reload_configs.items():
                        if not config.enabled:
                            continue
                        
                        # Check for file changes
                        for watch_path in config.watch_paths:
                            if os.path.exists(watch_path):
                                # Get latest modification time
                                latest_mtime = self._get_latest_mtime(watch_path)
                                
                                if latest_mtime and current_time - latest_mtime > config.debounce_interval:
                                    if current_time - config.last_reload > config.debounce_interval:
                                        self.trigger_hot_reload(reload_id)
                    
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    logger.error(f"Hot reload monitor error: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=monitor_hot_reload, daemon=True)
        thread.start()
        logger.info("Hot reload monitor started")
    
    def _start_build_processor(self) -> None:
        """Start background build processor."""
        def process_builds():
            while self.state == ServiceState.RUNNING:
                try:
                    if self._build_queue:
                        action, container = self._build_queue.popleft()
                        
                        if action == "create":
                            if self._docker_available:
                                # Simulate build process
                                container.status = ContainerStatus.BUILDING
                                time.sleep(2)  # Simulate build time
                                container.status = ContainerStatus.RUNNING
                            else:
                                container.status = ContainerStatus.RUNNING
                    
                    time.sleep(1)  # Process builds every second
                except Exception as e:
                    logger.error(f"Build processor error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=process_builds, daemon=True)
        thread.start()
        logger.info("Build processor started")
    
    def _get_latest_mtime(self, path: str) -> float:
        """Get latest modification time for a path."""
        if os.path.isfile(path):
            return os.path.getmtime(path)
        elif os.path.isdir(path):
            latest_mtime = 0
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    mtime = os.path.getmtime(file_path)
                    if mtime > latest_mtime:
                        latest_mtime = mtime
            return latest_mtime
        return 0.0
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())


# Global instance
_development_environment_service: Optional[DevelopmentEnvironmentService] = None


def get_development_environment_service() -> DevelopmentEnvironmentService:
    """Get global development environment service instance."""
    global _development_environment_service
    if _development_environment_service is None:
        _development_environment_service = DevelopmentEnvironmentService()
    return _development_environment_service