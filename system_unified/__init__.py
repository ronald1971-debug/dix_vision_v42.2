"""
System Unified Module - System Infrastructure
Provides system-level infrastructure and operations
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
from datetime import datetime, timedelta
import os
import sys
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class SystemMode(Enum):
    """System operating mode"""
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TESTING = "testing"
    MAINTENANCE = "maintenance"


class SystemStatus(Enum):
    """System status"""
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    ERROR = "error"


class ComponentStatus(Enum):
    """Component status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_available: float = 0.0
    disk_usage: float = 0.0
    disk_available: float = 0.0
    network_rx: float = 0.0
    network_tx: float = 0.0
    uptime_ns: int = 0
    last_update_ns: int = 0
    
    def __post_init__(self):
        if self.last_update_ns == 0:
            self.last_update_ns = datetime.now().timestamp_ns()


@dataclass
class ComponentMetrics:
    """Component performance metrics"""
    component_id: str
    status: ComponentStatus
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_count: int = 0
    error_count: int = 0
    average_latency_ms: float = 0.0
    last_update_ns: int = 0
    
    def __post_init__(self):
        if self.last_update_ns == 0:
            self.last_update_ns = datetime.now().timestamp_ns()


@dataclass
class SystemConfig:
    """System configuration"""
    system_mode: SystemMode = SystemMode.DEVELOPMENT
    log_level: str = "INFO"
    max_workers: int = 4
    timeout_seconds: int = 30
    enable_metrics: bool = True
    enable_monitoring: bool = True
    health_check_interval: int = 60
    config_path: str = "config/system_config.json"


class SystemManager:
    """
    System Manager - Core system infrastructure component
    
    Provides system-level operations, configuration, monitoring, and lifecycle management
    Required by archival components for system operations
    """
    
    def __init__(self, config: Optional[SystemConfig] = None):
        self._config = config or SystemConfig()
        self._status = SystemStatus.STOPPED
        self._start_time_ns = 0
        self._components: Dict[str, Dict[str, Any]] = {}
        self._component_metrics: Dict[str, ComponentMetrics] = {}
        self._system_metrics = SystemMetrics()
        self._callbacks: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
        self._health_check_task = None
        self._metrics_task = None
        self._initialized = False
        
    async def initialize(self) -> bool:
        """Initialize system manager"""
        if self._initialized:
            logger.warning("System manager already initialized")
            return True
        
        try:
            # Load configuration
            await self._load_configuration()
            
            # Setup logging
            self._setup_logging()
            
            self._initialized = True
            logger.info("System manager initialized")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize system manager: {e}")
            return False
    
    async def start(self) -> bool:
        """Start system manager"""
        if not self._initialized:
            logger.error("System manager not initialized")
            return False
        
        if self._status == SystemStatus.RUNNING:
            logger.warning("System manager already running")
            return True
        
        try:
            self._status = SystemStatus.STARTING
            self._start_time_ns = datetime.now().timestamp_ns()
            
            # Start health check task
            if self._config.enable_monitoring:
                self._health_check_task = asyncio.create_task(self._health_check_loop())
            
            # Start metrics collection task
            if self._config.enable_metrics:
                self._metrics_task = asyncio.create_task(self._metrics_collection_loop())
            
            self._status = SystemStatus.RUNNING
            logger.info("System manager started")
            
            # Trigger callbacks
            await self._trigger_callbacks("system_started")
            
            return True
        except Exception as e:
            logger.error(f"Failed to start system manager: {e}")
            self._status = SystemStatus.ERROR
            return False
    
    async def stop(self) -> bool:
        """Stop system manager"""
        if self._status == SystemStatus.STOPPED:
            logger.warning("System manager already stopped")
            return True
        
        try:
            self._status = SystemStatus.STOPPED
            
            # Stop background tasks
            if self._health_check_task:
                self._health_check_task.cancel()
            if self._metrics_task:
                self._metrics_task.cancel()
            
            logger.info("System manager stopped")
            
            # Trigger callbacks
            await self._trigger_callbacks("system_stopped")
            
            return True
        except Exception as e:
            logger.error(f"Failed to stop system manager: {e}")
            self._status = SystemStatus.ERROR
            return False
    
    async def register_component(self, component_id: str, component: Any, 
                                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Register a system component"""
        async with self._lock:
            self._components[component_id] = {
                'component': component,
                'metadata': metadata or {},
                'registered_at': datetime.now().timestamp_ns(),
                'status': ComponentStatus.ACTIVE
            }
            
            # Initialize component metrics
            self._component_metrics[component_id] = ComponentMetrics(
                component_id=component_id,
                status=ComponentStatus.ACTIVE
            )
        
        logger.info(f"Registered component: {component_id}")
        
        # Trigger callbacks
        await self._trigger_callbacks(f"component_registered_{component_id}")
        
        return True
    
    async def unregister_component(self, component_id: str) -> bool:
        """Unregister a system component"""
        async with self._lock:
            if component_id in self._components:
                del self._components[component_id]
            if component_id in self._component_metrics:
                del self._component_metrics[component_id]
        
        logger.info(f"Unregistered component: {component_id}")
        
        # Trigger callbacks
        await self._trigger_callbacks(f"component_unregistered_{component_id}")
        
        return True
    
    async def get_component(self, component_id: str) -> Optional[Any]:
        """Get registered component"""
        component_info = self._components.get(component_id)
        return component_info['component'] if component_info else None
    
    async def get_component_status(self, component_id: str) -> Optional[ComponentStatus]:
        """Get component status"""
        component_info = self._components.get(component_id)
        return component_info['status'] if component_info else None
    
    async def update_component_status(self, component_id: str, 
                                      status: ComponentStatus) -> bool:
        """Update component status"""
        if component_id not in self._components:
            logger.error(f"Component {component_id} not found")
            return False
        
        async with self._lock:
            self._components[component_id]['status'] = status
            self._component_metrics[component_id].status = status
        
        logger.info(f"Updated component {component_id} to {status.value}")
        
        # Trigger callbacks
        await self._trigger_callbacks(f"component_status_updated_{component_id}")
        
        return True
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        return self._system_metrics
    
    async def get_component_metrics(self, component_id: str) -> Optional[ComponentMetrics]:
        """Get component metrics"""
        return self._component_metrics.get(component_id)
    
    async def get_status(self) -> SystemStatus:
        """Get current system status"""
        return self._status
    
    async def get_mode(self) -> SystemMode:
        """Get current system mode"""
        return self._config.system_mode
    
    async def set_mode(self, mode: SystemMode) -> bool:
        """Set system mode"""
        old_mode = self._config.system_mode
        self._config.system_mode = mode
        
        logger.info(f"System mode changed: {old_mode.value} -> {mode.value}")
        
        # Trigger callbacks
        await self._trigger_callbacks("mode_changed")
        
        return True
    
    async def register_callback(self, event: str, callback: Callable):
        """Register callback for system events"""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
    
    async def _trigger_callbacks(self, event: str):
        """Trigger registered callbacks for system events"""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Callback error for {event}: {e}")
    
    async def _load_configuration(self) -> bool:
        """Load system configuration"""
        try:
            config_path = Path(self._config.config_path)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    # Update config with loaded values
                    for key, value in config_data.items():
                        if hasattr(self._config, key):
                            setattr(self._config, key, value)
                logger.info(f"Loaded configuration from {config_path}")
            return True
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}")
            return False
    
    def _setup_logging(self):
        """Setup logging configuration"""
        import logging.config
        
        logging.basicConfig(
            level=getattr(logging, self._config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def _health_check_loop(self):
        """Health check loop"""
        while self._status == SystemStatus.RUNNING:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self._config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(10.0)
    
    async def _perform_health_check(self):
        """Perform health check on all components"""
        for component_id, component_info in self._components.items():
            try:
                # Check if component is responsive
                component = component_info['component']
                if hasattr(component, 'health_check'):
                    is_healthy = await component.health_check()
                    status = ComponentStatus.ACTIVE if is_healthy else ComponentStatus.ERROR
                    await self.update_component_status(component_id, status)
            except Exception as e:
                logger.error(f"Health check failed for {component_id}: {e}")
                await self.update_component_status(component_id, ComponentStatus.ERROR)
    
    async def _metrics_collection_loop(self):
        """Metrics collection loop"""
        while self._status == SystemStatus.RUNNING:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(5.0)  # Collect metrics every 5 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(10.0)
    
    async def _collect_system_metrics(self):
        """Collect system metrics"""
        import psutil
        
        try:
            # CPU usage
            self._system_metrics.cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self._system_metrics.memory_usage = memory.percent
            self._system_metrics.memory_available = memory.available / (1024 ** 3)  # GB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self._system_metrics.disk_usage = disk.percent
            self._system_metrics.disk_available = disk.free / (1024 ** 3)  # GB
            
            # Network usage
            network = psutil.net_io_counters()
            self._system_metrics.network_rx = network.bytes_recv
            self._system_metrics.network_tx = network.bytes_sent
            
            # Uptime
            self._system_metrics.uptime_ns = datetime.now().timestamp_ns() - self._start_time_ns
            self._system_metrics.last_update_ns = datetime.now().timestamp_ns()
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")


# Global system manager instance
_system_manager = None

def get_system_manager() -> SystemManager:
    """Get global system manager instance"""
    global _system_manager
    if _system_manager is None:
        _system_manager = SystemManager()
    return _system_manager


async def initialize_system() -> bool:
    """Initialize system (convenience function)"""
    manager = get_system_manager()
    return await manager.initialize()


async def start_system() -> bool:
    """Start system (convenience function)"""
    manager = get_system_manager()
    return await manager.start()


async def stop_system() -> bool:
    """Stop system (convenience function)"""
    manager = get_system_manager()
    return await manager.stop()


# Import new submodules
from system_unified.time_source import (
    TimeSource,
    get_time_source,
    get_current_time_ns,
    get_current_time_s
)

from system_unified.kill_switch import (
    KillSwitchState,
    KillReason,
    KillSwitchEvent,
    KillSwitch,
    get_kill_switch,
    trigger_kill_switch,
    arm_kill_switch,
    reset_kill_switch
)


__all__ = [
    'SystemMode',
    'SystemStatus',
    'ComponentStatus',
    'SystemMetrics',
    'ComponentMetrics',
    'SystemConfig',
    'SystemManager',
    'get_system_manager',
    'initialize_system',
    'start_system',
    'stop_system',
    'TimeSource',
    'get_time_source',
    'get_current_time_ns',
    'get_current_time_s',
    'KillSwitchState',
    'KillReason',
    'KillSwitchEvent',
    'KillSwitch',
    'get_kill_switch',
    'trigger_kill_switch',
    'arm_kill_switch',
    'reset_kill_switch'
]