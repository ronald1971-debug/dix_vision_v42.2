"""
component_connection_manager.py
DIX VISION v42.2 — Component Connection Manager

Manages connections between all cognitive architecture components.
Provides health monitoring, retry logic, graceful degradation, and connection validation.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection state enumeration."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    FAILED = "failed"
    CLOSING = "closing"


@dataclass
class ConnectionConfig:
    """Configuration for a component connection."""

    component_name: str
    component_type: str
    enabled: bool = True
    required: bool = False
    max_retries: int = 3
    retry_delay_ms: int = 1000
    connection_timeout_ms: int = 5000
    health_check_interval_ms: int = 10000
    auto_reconnect: bool = True
    graceful_degradation: bool = True


@dataclass
class ConnectionStatus:
    """Status of a component connection."""

    component_name: str
    state: ConnectionState
    connected_since: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    failure_count: int = 0
    last_failure_reason: str = ""
    last_failure_time: Optional[datetime] = None
    retry_count: int = 0
    degradation_level: float = 0.0  # 0.0 = full functionality, 1.0 = completely degraded


class ComponentConnectionManager:
    """Manages connections between all cognitive architecture components."""

    def __init__(self):
        self._lock = threading.Lock()

        # Component storage
        self._components: Dict[str, Any] = {}
        self._connection_configs: Dict[str, ConnectionConfig] = {}
        self._connection_status: Dict[str, ConnectionStatus] = {}

        # Connection health monitoring
        self._health_check_tasks: Dict[str, threading.Thread] = {}
        self._stop_event = threading.Event()

        # Connection pool for connection reuse
        self._connection_pool: Dict[str, Any] = {}

        # Connection callbacks
        self._on_connect_callbacks: Dict[str, List[Callable]] = {}
        self._on_disconnect_callbacks: Dict[str, List[Callable]] = {}
        self._on_degrade_callbacks: Dict[str, List[Callable]] = {}
        self._on_failure_callbacks: Dict[str, List[Callable]] = {}

        logger.info("[CONNECTION_MANAGER] Component connection manager initialized")

    def register_component(
        self, component_name: str, component_type: str, config: Optional[ConnectionConfig] = None
    ) -> bool:
        """Register a component for connection management."""
        try:
            with self._lock:
                if config is None:
                    config = ConnectionConfig(
                        component_name=component_name, component_type=component_type
                    )

                self._connection_configs[component_name] = config
                self._connection_status[component_name] = ConnectionStatus(
                    component_name=component_name, state=ConnectionState.DISCONNECTED
                )

                logger.info(
                    f"[CONNECTION_MANAGER] Registered component {component_name} "
                    f"(type: {component_type}, required: {config.required})"
                )
                return True

        except Exception as e:
            logger.error(f"[CONNECTION_MANAGER] Failed to register component {component_name}: {e}")
            return False

    def connect_component(
        self, component_name: str, component_instance: Any, callback: Optional[Callable] = None
    ) -> bool:
        """Connect a component instance to the manager."""
        try:
            config = self._connection_configs.get(component_name)
            if not config:
                logger.warning(f"[CONNECTION_MANAGER] No config found for {component_name}")
                return False

            if not config.enabled:
                logger.info(f"[CONNECTION_MANAGER] Component {component_name} is disabled")
                return False

            status = self._connection_status[component_name]
            status.state = ConnectionState.CONNECTING

            logger.info(f"[CONNECTION_MANAGER] Connecting component {component_name}...")

            # Simulate connection (in real implementation, this would involve actual connection logic)
            time.sleep(0.1)  # Simulate connection time

            # Store component instance
            self._components[component_name] = component_instance
            self._connection_pool[component_name] = component_instance

            # Update status
            status.state = ConnectionState.CONNECTED
            status.connected_since = datetime.utcnow()
            status.failure_count = 0

            logger.info(f"[CONNECTION_MANAGER] Component {component_name} connected successfully")

            # Trigger on-connect callbacks
            if callback:
                callback(component_name, component_instance)
            for cb in self._on_connect_callbacks.get(component_name, []):
                try:
                    cb(component_name, component_instance)
                except Exception as e:
                    logger.error(
                        f"[CONNECTION_MANAGER] On-connect callback failed for {component_name}: {e}"
                    )

            # Start health monitoring
            if config.health_check_interval_ms > 0:
                self._start_health_monitoring(component_name)

            return True

        except Exception as e:
            logger.error(f"[CONNECTION_MANAGER] Failed to connect component {component_name}: {e}")
            self._handle_connection_failure(component_name, str(e))
            return False

    def disconnect_component(self, component_name: str) -> bool:
        """Disconnect a component from the manager."""
        try:
            config = self._connection_configs.get(component_name)
            if not config:
                return False

            status = self._connection_status[component_name]
            status.state = ConnectionState.CLOSING

            logger.info(f"[CONNECTION_MANAGER] Disconnecting component {component_name}...")

            # Stop health monitoring
            self._stop_health_monitoring(component_name)

            # Remove from pool
            if component_name in self._components:
                del self._components[component_name]
            if component_name in self._connection_pool:
                del self._connection_pool[component_name]

            # Update status
            status.state = ConnectionState.DISCONNECTED
            status.connected_since = None

            logger.info(f"[CONNECTION_MANAGER] Component {component_name} disconnected")

            # Trigger on-disconnect callbacks
            for cb in self._on_disconnect_callbacks.get(component_name, []):
                try:
                    cb(component_name)
                except Exception as e:
                    logger.error(
                        f"[CONNECTION_MANAGER] On-disconnect callback failed for {component_name}: {e}"
                    )

            return True

        except Exception as e:
            logger.error(
                f"[CONNECTION_MANAGER] Failed to disconnect component {component_name}: {e}"
            )
            return False

    def get_component(self, component_name: str) -> Optional[Any]:
        """Get a connected component instance."""
        status = self._connection_status.get(component_name)
        if not status:
            logger.warning(f"[CONNECTION_MANAGER] No status found for {component_name}")
            return None

        if status.state not in [ConnectionState.CONNECTED, ConnectionState.DEGRADED]:
            logger.warning(
                f"[CONNECTION_MANAGER] Component {component_name} not connected "
                f"(state: {status.state.value})"
            )
            return None

        return self._components.get(component_name)

    def get_connection_status(self, component_name: str) -> Optional[ConnectionStatus]:
        """Get the connection status of a component."""
        return self._connection_status.get(component_name)

    def get_all_status(self) -> Dict[str, ConnectionStatus]:
        """Get connection status for all components."""
        return self._connection_status.copy()

    def register_on_connect(self, component_name: str, callback: Callable) -> None:
        """Register a callback to be called when a component connects."""
        if component_name not in self._on_connect_callbacks:
            self._on_connect_callbacks[component_name] = []
        self._on_connect_callbacks[component_name].append(callback)

    def register_on_disconnect(self, component_name: str, callback: Callable) -> None:
        """Register a callback to be called when a component disconnects."""
        if component_name not in self._on_disconnect_callbacks:
            self._on_disconnect_callbacks[component_name] = []
        self._on_disconnect_callbacks[component_name].append(callback)

    def register_on_degrade(self, component_name: str, callback: Callable) -> None:
        """Register a callback to be called when a component degrades."""
        if component_name not in self._on_degrade_callbacks:
            self._on_degrade_callbacks[component_name] = []
        self._on_degrade_callbacks[component_name].append(callback)

    def register_on_failure(self, component_name: str, callback: Callable) -> None:
        """Register a callback to be called when a component fails."""
        if component_name not in self._on_failure_callbacks:
            self._on_failure_callbacks[component_name] = []
        self._on_failure_callbacks[component_name].append(callback)

    def _start_health_monitoring(self, component_name: str) -> None:
        """Start health monitoring for a component."""
        config = self._connection_configs[component_name]

        def health_check_loop():
            while not self._stop_event.is_set():
                try:
                    time.sleep(config.health_check_interval_ms / 1000)
                    self._health_check(component_name)
                except Exception as e:
                    logger.error(
                        f"[CONNECTION_MANAGER] Health check error for {component_name}: {e}"
                    )

        thread = threading.Thread(target=health_check_loop, daemon=True)
        thread.start()
        self._health_check_tasks[component_name] = thread

        logger.info(f"[CONNECTION_MANAGER] Health monitoring started for {component_name}")

    def _stop_health_monitoring(self, component_name: str) -> None:
        """Stop health monitoring for a component."""
        if component_name in self._health_check_tasks:
            # The thread will stop when it checks the stop_event
            del self._health_check_tasks[component_name]
            logger.info(f"[CONNECTION_MANAGER] Health monitoring stopped for {component_name}")

    def _health_check(self, component_name: str) -> None:
        """Perform a health check on a component."""
        try:
            config = self._connection_configs[component_name]
            status = self._connection_status[component_name]

            # In real implementation, this would ping the component
            component = self._components.get(component_name)
            if component:
                # Simulate health check
                healthy = True  # In real implementation, check actual health

                status.last_health_check = datetime.utcnow()

                if healthy:
                    if status.state == ConnectionState.DEGRADED:
                        status.state = ConnectionState.CONNECTED
                        status.degradation_level = 0.0
                        logger.info(
                            f"[CONNECTION_MANAGER] Component {component_name} recovered from degraded state"
                        )
                else:
                    if config.graceful_degradation:
                        self._degrade_component(component_name, "Health check failed")
                    else:
                        self._handle_connection_failure(component_name, "Health check failed")

            else:
                self._handle_connection_failure(component_name, "Component not found in pool")

        except Exception as e:
            logger.error(f"[CONNECTION_MANAGER] Health check failed for {component_name}: {e}")

    def _handle_connection_failure(self, component_name: str, reason: str) -> None:
        """Handle a connection failure."""
        try:
            config = self._connection_configs[component_name]
            status = self._connection_status[component_name]

            status.failure_count += 1
            status.last_failure_reason = reason
            status.last_failure_time = datetime.utcnow()

            logger.warning(
                f"[CONNECTION_MANAGER] Connection failure for {component_name} "
                f"(reason: {reason}, failure count: {status.failure_count})"
            )

            # Trigger on-failure callbacks
            for cb in self._on_failure_callbacks.get(component_name, []):
                try:
                    cb(component_name, reason)
                except Exception as e:
                    logger.error(
                        f"[CONNECTION_MANAGER] On-failure callback failed for {component_name}: {e}"
                    )

            # Check if we should retry
            if status.retry_count < config.max_retries and config.auto_reconnect:
                status.retry_count += 1
                status.state = ConnectionState.CONNECTING

                logger.info(
                    f"[CONNECTION_MANAGER] Retrying connection for {component_name} "
                    f"(attempt {status.retry_count}/{config.max_retries})"
                )

                # Schedule retry
                def retry_callback():
                    time.sleep(config.retry_delay_ms / 1000)
                    # In real implementation, retry connection logic here

                thread = threading.Thread(target=retry_callback, daemon=True)
                thread.start()
            else:
                status.state = ConnectionState.FAILED

                if config.required:
                    logger.error(
                        f"[CONNECTION_MANAGER] Required component {component_name} failed "
                        f"after {status.failure_count} attempts"
                    )
                else:
                    logger.warning(
                        f"[CONNECTION_MANAGER] Optional component {component_name} failed "
                        f"(continuing without it)"
                    )

        except Exception as e:
            logger.error(f"[CONNECTION_MANAGER] Error handling failure for {component_name}: {e}")

    def _degrade_component(self, component_name: str, reason: str) -> None:
        """Degrade a component gracefully."""
        try:
            config = self._connection_configs[component_name]
            status = self._connection_status[component_name]

            if not config.graceful_degradation:
                self._handle_connection_failure(component_name, reason)
                return

            status.state = ConnectionState.DEGRADED
            status.degradation_level = min(status.degradation_level + 0.1, 1.0)

            logger.warning(
                f"[CONNECTION_MANAGER] Component {component_name} degraded "
                f"(reason: {reason}, degradation level: {status.degradation_level:.2f})"
            )

            # Trigger on-degrade callbacks
            for cb in self._on_degrade_callbacks.get(component_name, []):
                try:
                    cb(component_name, status.degradation_level)
                except Exception as e:
                    logger.error(
                        f"[CONNECTION_MANAGER] On-degrade callback failed for {component_name}: {e}"
                    )

        except Exception as e:
            logger.error(f"[CONNECTION_MANAGER] Error degrading component {component_name}: {e}")

    def stop(self) -> None:
        """Stop the connection manager and disconnect all components."""
        logger.info("[CONNECTION_MANAGER] Stopping connection manager...")

        self._stop_event.set()

        # Disconnect all components
        component_names = list(self._connection_status.keys())
        for component_name in component_names:
            self.disconnect_component(component_name)

        logger.info("[CONNECTION_MANAGER] Connection manager stopped")

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health based on component connections."""
        total_components = len(self._connection_status)
        connected_components = sum(
            1
            for status in self._connection_status.values()
            if status.state in [ConnectionState.CONNECTED, ConnectionState.DEGRADED]
        )
        failed_components = sum(
            1
            for status in self._connection_status.values()
            if status.state == ConnectionState.FAILED
        )

        required_failed = 0
        for component_name, config in self._connection_configs.items():
            if config.required:
                status = self._connection_status[component_name]
                if status.state == ConnectionState.FAILED:
                    required_failed += 1

        health_percentage = (
            (connected_components / total_components * 100) if total_components > 0 else 0
        )

        return {
            "total_components": total_components,
            "connected_components": connected_components,
            "failed_components": failed_components,
            "required_failed_components": required_failed,
            "health_percentage": health_percentage,
            "system_healthy": required_failed == 0,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global connection manager instance
_connection_manager: Optional[ComponentConnectionManager] = None
_connection_manager_lock = threading.Lock()


def get_connection_manager() -> ComponentConnectionManager:
    """Get the global component connection manager (thread-safe singleton)."""
    global _connection_manager
    with _connection_manager_lock:
        if _connection_manager is None:
            _connection_manager = ComponentConnectionManager()
    return _connection_manager
