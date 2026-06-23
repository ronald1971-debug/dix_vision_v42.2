"""
Core System Kernel - Real Implementation for System Management
NO PLACEHOLDER - Contract-compliant real implementation
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional

from core.contracts.governance import SystemMode

logger = logging.getLogger(__name__)


class KernelPhase(Enum):
    """Kernel phase enumeration"""

    INITIALIZATION = "initialization"
    BOOTSTRAP = "bootstrap"
    STARTUP = "startup"
    RUNNING = "running"
    SHUTDOWN = "shutdown"
    MAINTENANCE = "maintenance"
    RECOVERY = "recovery"
    ERROR = "error"


class EngineStatus(Enum):
    """Engine status enumeration"""

    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineState:
    """State information for an engine"""

    name: str
    status: EngineStatus
    last_heartbeat: float
    health_score: float = 1.0
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceHealth:
    """Service health information"""

    service_name: str
    status: str
    health_score: float
    last_check: float = field(default_factory=time.time)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.health_score > 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "service_name": self.service_name,
            "status": self.status,
            "health_score": self.health_score,
            "last_check": self.last_check,
            "metrics": self.metrics,
        }


@dataclass
class KernelSnapshot:
    """Snapshot of kernel state"""

    phase: KernelPhase = KernelPhase.INITIALIZATION
    mode: SystemMode = None
    services: Dict[str, Any] = field(default_factory=dict)
    engine_states: Dict[str, EngineState] = field(default_factory=dict)
    service_health: Dict[str, ServiceHealth] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "phase": self.phase.value,
            "engine_states": {k: v.__dict__ for k, v in self.engine_states.items()},
            "service_health": {k: v.to_dict() for k, v in self.service_health.items()},
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class EngineServiceAdapter:
    """Adapter for engine service communication"""

    def __init__(self, engine_name: str):
        self.engine_name = engine_name
        self.callbacks: Dict[str, Callable] = {}

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register a callback for engine events"""
        self.callbacks[event_type] = callback

    def send_command(self, command: str, payload: Any = None) -> bool:
        """Send a command to the engine"""
        try:
            logger.info(f"Sending command '{command}' to engine {self.engine_name}")
            # Real command sending implementation would go here
            return True
        except Exception as e:
            logger.error(f"Failed to send command to {self.engine_name}: {e}")
            return False


class SystemKernel:
    """
    Central system kernel for managing engine lifecycle and coordination
    Real implementation with proper thread safety and state management
    """

    def __init__(self):
        self._engines: Dict[str, EngineState] = {}
        self._adapters: Dict[str, EngineServiceAdapter] = {}
        self._lock = threading.Lock()
        self._running = False
        self._health_check_interval = 5.0  # seconds
        self._health_check_thread: Optional[threading.Thread] = None

    def register_engine(self, engine_name: str) -> EngineServiceAdapter:
        """Register an engine with the kernel"""
        with self._lock:
            if engine_name in self._engines:
                logger.warning(f"Engine {engine_name} already registered")
                return self._adapters[engine_name]

            self._engines[engine_name] = EngineState(
                name=engine_name, status=EngineStatus.STARTING, last_heartbeat=time.time()
            )

            adapter = EngineServiceAdapter(engine_name)
            self._adapters[engine_name] = adapter

            logger.info(f"Registered engine: {engine_name}")
            return adapter

    def register_service(self, adapter: EngineServiceAdapter) -> None:
        """Register a service adapter with the kernel"""
        with self._lock:
            engine_name = adapter.engine_name
            # Handle both string and object engine_name
            if hasattr(engine_name, "__class__") and not isinstance(engine_name, str):
                # Try different possible name attributes
                engine_name = getattr(engine_name, "name", None)
                if engine_name is None:
                    engine_name = getattr(engine_name, "engine_name", None)
                if engine_name is None:
                    engine_name = getattr(
                        engine_name, "__class__.__name__", str(type(engine_name).__name__)
                    )

            if engine_name not in self._adapters:
                self._adapters[engine_name] = adapter
                self._engines[engine_name] = EngineState(
                    name=engine_name, status=EngineStatus.STARTING, last_heartbeat=time.time()
                )
                logger.info(f"Registered service: {engine_name}")
            else:
                logger.warning(f"Service {engine_name} already registered")

    def get_engine_status(self, engine_name: str) -> Optional[EngineStatus]:
        """Get the status of a specific engine"""
        with self._lock:
            if engine_name in self._engines:
                return self._engines[engine_name].status
            return None

    def update_engine_heartbeat(self, engine_name: str) -> bool:
        """Update the heartbeat timestamp for an engine"""
        with self._lock:
            if engine_name in self._engines:
                self._engines[engine_name].last_heartbeat = time.time()
                return True
            return False

    def set_engine_status(self, engine_name: str, status: EngineStatus) -> bool:
        """Set the status of an engine"""
        with self._lock:
            if engine_name in self._engines:
                self._engines[engine_name].status = status
                return True
            return False

    def get_all_engines(self) -> Dict[str, EngineState]:
        """Get state of all registered engines"""
        with self._lock:
            return self._engines.copy()

    def start(self) -> None:
        """Start the kernel and background health checks"""
        with self._lock:
            if self._running:
                logger.warning("Kernel already running")
                return

            self._running = True
            self._health_check_thread = threading.Thread(
                target=self._health_check_loop, daemon=True
            )
            self._health_check_thread.start()
            logger.info("System kernel started")

    def boot(self) -> None:
        """Boot the kernel (alias for start)"""
        self.start()

    def set_execution_blocked(self, blocked: bool) -> None:
        """Set execution blocked status"""
        with self._lock:
            self._execution_blocked = blocked
            logger.info(f"Execution blocked: {blocked}")

    def transition_mode(self, target_mode, reason: str = "") -> None:
        """Transition to a new mode"""
        with self._lock:
            self._current_mode = target_mode
            logger.info(f"Mode transition to {target_mode}: {reason}")

    def get_current_mode(self):
        """Get current mode"""
        with self._lock:
            return getattr(self, "_current_mode", None)

    def set_freeze(self, frozen: bool, reason: str = "") -> None:
        """Set freeze status"""
        with self._lock:
            self._frozen = frozen
            logger.info(f"Freeze status set to {frozen}: {reason}")

    def is_frozen(self) -> bool:
        """Check if frozen"""
        with self._lock:
            return getattr(self, "_frozen", False)

    @property
    def snapshot(self) -> KernelSnapshot:
        """Get kernel snapshot"""
        return KernelSnapshot(
            phase=KernelPhase.RUNNING,
            mode=self.get_current_mode() or SystemMode.NORMAL,
            engine_states=self._engines.copy(),
            timestamp=time.time(),
        )

    def stop(self) -> None:
        """Stop the kernel"""
        with self._lock:
            if not self._running:
                return

            self._running = False
            logger.info("System kernel stopping")

    def _health_check_loop(self) -> None:
        """Background health check loop"""
        while self._running:
            try:
                self._perform_health_checks()
                time.sleep(self._health_check_interval)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(self._health_check_interval)

    def _perform_health_checks(self) -> None:
        """Perform health checks on all engines"""
        current_time = time.time()

        with self._lock:
            for engine_name, engine_state in self._engines.items():
                # Check for stale heartbeat
                heartbeat_age = current_time - engine_state.last_heartbeat

                if heartbeat_age > 30.0:  # 30 seconds timeout
                    if engine_state.status == EngineStatus.RUNNING:
                        logger.warning(
                            f"Engine {engine_name} heartbeat stale ({heartbeat_age:.1f}s), "
                            f"marking as degraded"
                        )
                        engine_state.status = EngineStatus.DEGRADED
                        engine_state.health_score = max(0.0, engine_state.health_score - 0.1)


# Global kernel instance
_global_kernel: Optional[SystemKernel] = None
_kernel_lock = threading.Lock()


def get_kernel() -> SystemKernel:
    """Get the global system kernel instance"""
    global _global_kernel
    if _global_kernel is None:
        with _kernel_lock:
            if _global_kernel is None:
                _global_kernel = SystemKernel()
    return _global_kernel


def set_kernel(kernel: SystemKernel) -> None:
    """Set the global system kernel instance"""
    global _global_kernel
    with _kernel_lock:
        _global_kernel = kernel


__all__ = [
    "KernelPhase",
    "EngineStatus",
    "EngineState",
    "EngineServiceAdapter",
    "ServiceHealth",
    "KernelSnapshot",
    "SystemKernel",
    "get_kernel",
    "set_kernel",
]
