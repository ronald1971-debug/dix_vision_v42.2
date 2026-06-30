"""
DIX VISION Dashboard Service

Implements the Dashboard service as per Runtime Specification.
Dashboard acts as a client of the runtime, subscribing to events and displaying system state.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class DashboardState(Enum):
    """Dashboard service states."""
    INITIALIZING = "INITIALIZING"
    CONNECTING = "CONNECTING"
    READY = "READY"
    ERROR = "ERROR"
    STOPPED = "STOPPED"


@dataclass
class DashboardMessage:
    """Represents a dashboard message."""
    message_type: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class DashboardService(Service):
    """Dashboard service as per Runtime Specification.
    
    Dashboard Contract:
    - Dashboard is a client of the runtime
    - Dashboard NEVER starts backend logic
    - Dashboard ONLY subscribes to EventBus
    - Dashboard NEVER modifies system state directly
    """
    
    # Service dependencies
    DEPENDENCIES = ["ai_runtime_engine", "execution_engine", "memory_service", "session_restoration"]
    
    def __init__(self, port: int = 5173):
        super().__init__("dashboard_service")
        self.port = port
        self.dashboard_state = DashboardState.STOPPED
        self.event_history: List[Event] = []
        self._event_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.max_history = 1000
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the dashboard service."""
        try:
            self.event_bus = event_bus
            self.config = config
            self.state = ServiceState.INITIALIZING
            self.dashboard_state = DashboardState.INITIALIZING
            
            # Subscribe to relevant events as a client
            self._subscribe_to_events()
            
            logger.info("Dashboard Service initialized")
            return True
        except Exception as e:
            logger.error(f"Dashboard Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            self.dashboard_state = DashboardState.ERROR
            return False
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to system events as a client."""
        if not self.event_bus:
            return
        
        # Subscribe to AI Runtime events
        self.event_bus.subscribe(str(EventType.AI_INIT), self._handle_ai_event, self.name)
        self.event_bus.subscribe(str(EventType.AI_START), self._handle_ai_event, self.name)
        self.event_bus.subscribe(str(EventType.AI_STATE_UPDATE), self._handle_ai_event, self.name)
        self.event_bus.subscribe(str(EventType.AI_DECISION), self._handle_ai_event, self.name)
        self.event_bus.subscribe(str(EventType.AI_ERROR), self._handle_ai_event, self.name)
        
        # Subscribe to Execution events
        self.event_bus.subscribe(str(EventType.EXECUTION_START), self._handle_execution_event, self.name)
        self.event_bus.subscribe(str(EventType.EXECUTION_COMPLETE), self._handle_execution_event, self.name)
        self.event_bus.subscribe(str(EventType.EXECUTION_ERROR), self._handle_execution_event, self.name)
        
        # Subscribe to System events
        self.event_bus.subscribe(str(EventType.SYSTEM_BOOT), self._handle_system_event, self.name)
        self.event_bus.subscribe(str(EventType.SYSTEM_SHUTDOWN), self._handle_system_event, self.name)
        self.event_bus.subscribe(str(EventType.SYSTEM_DEGRADED), self._handle_system_event, self.name)
        self.event_bus.subscribe(str(EventType.SYSTEM_RECOVERING), self._handle_system_event, self.name)
        
        # Subscribe to Memory events
        self.event_bus.subscribe(str(EventType.MEMORY_WARNING), self._handle_memory_event, self.name)
        self.event_bus.subscribe(str(EventType.MEMORY_CRITICAL), self._handle_memory_event, self.name)
        self.event_bus.subscribe(str(EventType.MEMORY_RECOVERY), self._handle_memory_event, self.name)
        
        # Subscribe to Service events
        self.event_bus.subscribe(str(EventType.SERVICE_START), self._handle_service_event, self.name)
        self.event_bus.subscribe(str(EventType.SERVICE_STOP), self._handle_service_event, self.name)
        self.event_bus.subscribe(str(EventType.SERVICE_CRASH), self._handle_service_event, self.name)
        self.event_bus.subscribe(str(EventType.SERVICE_HEALTH), self._handle_service_event, self.name)
        
        logger.info("Dashboard subscribed to system events")
    
    def _handle_ai_event(self, event: Event) -> None:
        """Handle AI runtime events."""
        self._add_to_history(event)
        logger.debug(f"Dashboard received AI event: {event.type}")
    
    def _handle_execution_event(self, event: Event) -> None:
        """Handle execution events."""
        self._add_to_history(event)
        logger.debug(f"Dashboard received execution event: {event.type}")
    
    def _handle_system_event(self, event: Event) -> None:
        """Handle system events."""
        self._add_to_history(event)
        logger.info(f"Dashboard received system event: {event.type}")
    
    def _handle_memory_event(self, event: Event) -> None:
        """Handle memory events."""
        self._add_to_history(event)
        logger.warning(f"Dashboard received memory event: {event.type}")
    
    def _handle_service_event(self, event: Event) -> None:
        """Handle service events."""
        self._add_to_history(event)
        logger.debug(f"Dashboard received service event: {event.type}")
    
    def _add_to_history(self, event: Event) -> None:
        """Add event to dashboard history."""
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
    
    def start(self) -> bool:
        """Start the dashboard service."""
        try:
            self.state = ServiceState.STARTING
            self.dashboard_state = DashboardState.CONNECTING
            
            # Emit dashboard ready event
            self.emit_event(str(EventType.DASHBOARD_READY), {"port": self.port})
            
            # Start event processing thread
            self._stop_event.clear()
            self._event_thread = threading.Thread(target=self._event_processing_loop, daemon=True)
            self._event_thread.start()
            
            self.state = ServiceState.RUNNING
            self.dashboard_state = DashboardState.READY
            logger.info(f"Dashboard Service started on port {self.port}")
            return True
        except Exception as e:
            logger.error(f"Dashboard Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.dashboard_state = DashboardState.ERROR
            self.emit_event(str(EventType.DASHBOARD_ERROR), {"error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the dashboard service."""
        try:
            self.state = ServiceState.STOPPING
            self.dashboard_state = DashboardState.STOPPED
            
            # Signal stop to event processing thread
            self._stop_event.set()
            
            # Wait for event processing thread to stop
            if self._event_thread and self._event_thread.is_alive():
                self._event_thread.join(timeout=5)
            
            self.state = ServiceState.STOPPED
            logger.info("Dashboard Service stopped")
            return True
        except Exception as e:
            logger.error(f"Dashboard Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get dashboard service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Dashboard State: {self.dashboard_state.value}",
            details={
                "dashboard_state": self.dashboard_state.value,
                "port": self.port,
                "event_history_size": len(self.event_history),
                "thread_active": self._event_thread and self._event_thread.is_alive()
            },
            timestamp=time.time()
        )
    
    def _event_processing_loop(self) -> None:
        """Event processing loop for dashboard."""
        try:
            while not self._stop_event.is_set():
                # Process events (in a real implementation, this would update UI)
                # For now, we just maintain the event history
                self._stop_event.wait(1.0)
                
        except Exception as e:
            logger.error(f"Dashboard event processing loop failed: {e}")
            self.dashboard_state = DashboardState.ERROR
    
    def get_recent_events(self, limit: int = 50) -> List[Event]:
        """Get recent events from dashboard history."""
        return self.event_history[-limit:]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status from event history."""
        status = {
            "total_events": len(self.event_history),
            "recent_events": [],
            "system_state": "unknown",
            "last_update": time.time()
        }
        
        # Get recent events
        recent = self.get_recent_events(10)
        status["recent_events"] = [
            {
                "type": event.type,
                "source": event.source,
                "timestamp": event.timestamp
            }
            for event in recent
        ]
        
        # Determine system state from recent events
        for event in reversed(recent):
            if event.type == "SYSTEM_BOOT":
                status["system_state"] = "booted"
                break
            elif event.type == "SYSTEM_SHUTDOWN":
                status["system_state"] = "shutdown"
                break
            elif event.type == "SYSTEM_DEGRADED":
                status["system_state"] = "degraded"
                break
            elif event.type == "SYSTEM_RECOVERING":
                status["system_state"] = "recovering"
                break
        
        return status


class AdvancedDashboardService(DashboardService):
    """Advanced dashboard service with enhanced capabilities."""
    
    def __init__(self, port: int = 5173):
        super().__init__(port)
        self.name = "dashboard_service_advanced"
        self.metrics: Dict[str, Any] = {}
        
    def _handle_ai_event(self, event: Event) -> None:
        """Handle AI events with enhanced metrics."""
        super()._handle_ai_event(event)
        
        # Update metrics
        if event.type == "AI_DECISION":
            self.metrics["ai_decisions"] = self.metrics.get("ai_decisions", 0) + 1
        elif event.type == "AI_ERROR":
            self.metrics["ai_errors"] = self.metrics.get("ai_errors", 0) + 1
    
    def _handle_execution_event(self, event: Event) -> None:
        """Handle execution events with enhanced metrics."""
        super()._handle_execution_event(event)
        
        # Update metrics
        if event.type == "EXECUTION_COMPLETE":
            self.metrics["executions"] = self.metrics.get("executions", 0) + 1
        elif event.type == "EXECUTION_ERROR":
            self.metrics["execution_errors"] = self.metrics.get("execution_errors", 0) + 1
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get enhanced system status with metrics."""
        status = super().get_system_status()
        status["metrics"] = self.metrics
        return status


__all__ = [
    "DashboardService",
    "AdvancedDashboardService",
    "DashboardState",
    "DashboardMessage",
]