"""
DIX VISION Dashboard Service

Implements the Dashboard service as per Runtime Specification.
Dashboard acts as a client of the runtime, subscribing to events and displaying system state.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

# WebSocket imports (optional - only imported if available)
try:
    from websockets.server import serve
    from websockets.exceptions import ConnectionClosed
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

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
    
    # Event filtering configuration
    # Events that should be filtered out to reduce noise
    FILTERED_EVENTS = {
        # Filter out high-frequency AI state updates to reduce noise
        str(EventType.AI_STATE_UPDATE): True,
        # Filter out memory warnings unless critical
        str(EventType.MEMORY_WARNING): False,  # Allow by default
        # Filter out service health events (too frequent)
        str(EventType.SERVICE_HEALTH): True,
    }
    
    # Priority levels for event processing
    EVENT_PRIORITIES = {
        str(EventType.SERVICE_CRASH): "CRITICAL",
        str(EventType.MEMORY_CRITICAL): "CRITICAL",
        str(EventType.CONTRACT_VIOLATION): "CRITICAL",
        str(EventType.EXECUTION_ERROR): "HIGH",
        str(EventType.AI_ERROR): "HIGH",
        str(EventType.AI_DECISION): "MEDIUM",
        str(EventType.EXECUTION_COMPLETE): "MEDIUM",
        str(EventType.MEMORY_WARNING): "LOW",
        str(EventType.SERVICE_START): "LOW",
        str(EventType.SERVICE_STOP): "LOW",
    }
    
    def __init__(self, port: int = 5173, enable_websocket: bool = True, websocket_port: int = 8765):
        super().__init__("dashboard_service")
        self.port = port
        self.websocket_port = websocket_port
        self.enable_websocket = enable_websocket and WEBSOCKET_AVAILABLE
        self.dashboard_state = DashboardState.STOPPED
        self.event_history: List[Event] = []
        self._event_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.max_history = 1000
        self.filtered_event_count = 0
        self.processed_event_count = 0
        
        # WebSocket support
        self.websocket_clients: List[Any] = []
        self._websocket_server: Optional[Any] = None
        self._websocket_thread: Optional[threading.Thread] = None
        self._websocket_loop: Optional[asyncio.AbstractEventLoop] = None
        
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
        """Subscribe to system events as a client with filtering."""
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
        
        logger.info("Dashboard subscribed to system events with filtering enabled")
    
    def _should_filter_event(self, event: Event) -> bool:
        """Check if an event should be filtered out."""
        # Check if event type is in filtered list
        if event.type in self.FILTERED_EVENTS:
            self.filtered_event_count += 1
            return True
        
        # Additional dynamic filtering based on event history size
        # If history is getting too large, filter out low-priority events
        if len(self.event_history) >= self.max_history * 0.9:
            event_priority = self._get_event_priority(event.type)
            if event_priority == "LOW":
                self.filtered_event_count += 1
                return True
        
        # Filter out events from services that are not critical
        # For example, only keep events from critical services
        return False
    
    def _get_event_priority(self, event_type: str) -> str:
        """Get priority level for an event type."""
        return self.EVENT_PRIORITIES.get(event_type, "LOW")
    
    def update_filtering_config(self, filtered_events: Dict[str, bool] = None) -> None:
        """Update event filtering configuration dynamically."""
        if filtered_events:
            self.FILTERED_EVENTS.update(filtered_events)
            logger.info(f"Updated event filtering config: {filtered_events}")
    
    def get_filtering_stats(self) -> Dict[str, Any]:
        """Get filtering statistics."""
        total_events = self.processed_event_count + self.filtered_event_count
        return {
            "processed_events": self.processed_event_count,
            "filtered_events": self.filtered_event_count,
            "total_events": total_events,
            "filtering_ratio": self.filtered_event_count / max(total_events, 1),
            "filtered_event_types": self.FILTERED_EVENTS,
            "event_history_utilization": len(self.event_history) / self.max_history
        }
    
    def _handle_ai_event(self, event: Event) -> None:
        """Handle AI runtime events with filtering."""
        if self._should_filter_event(event):
            return
        self._add_to_history(event)
        self.processed_event_count += 1
        logger.debug(f"Dashboard received AI event: {event.type}")
    
    def _handle_execution_event(self, event: Event) -> None:
        """Handle execution events with filtering."""
        if self._should_filter_event(event):
            return
        self._add_to_history(event)
        self.processed_event_count += 1
        logger.debug(f"Dashboard received execution event: {event.type}")
    
    def _handle_system_event(self, event: Event) -> None:
        """Handle system events with filtering."""
        if self._should_filter_event(event):
            return
        self._add_to_history(event)
        self.processed_event_count += 1
        logger.info(f"Dashboard received system event: {event.type}")
    
    def _handle_memory_event(self, event: Event) -> None:
        """Handle memory events with filtering."""
        if self._should_filter_event(event):
            return
        self._add_to_history(event)
        self.processed_event_count += 1
        logger.warning(f"Dashboard received memory event: {event.type}")
    
    def _handle_service_event(self, event: Event) -> None:
        """Handle service events with filtering."""
        if self._should_filter_event(event):
            return
        self._add_to_history(event)
        self.processed_event_count += 1
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
            
            # Start WebSocket server if enabled
            if self.enable_websocket:
                self._start_websocket_server()
            
            self.state = ServiceState.RUNNING
            self.dashboard_state = DashboardState.READY
            logger.info(f"Dashboard Service started on port {self.port} (WebSocket: {'enabled' if self.enable_websocket else 'disabled'})")
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
            
            # Stop WebSocket server if running
            if self.enable_websocket:
                self._stop_websocket_server()
            
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
            message=f"Dashboard State: {self.dashboard_state.value} - Events: {self.processed_event_count}/{self.processed_event_count + self.filtered_event_count}",
            details={
                "dashboard_state": self.dashboard_state.value,
                "port": self.port,
                "event_history_size": len(self.event_history),
                "thread_active": self._event_thread and self._event_thread.is_alive(),
                "processed_events": self.processed_event_count,
                "filtered_events": self.filtered_event_count,
                "filtering_ratio": self.filtered_event_count / max(self.processed_event_count + self.filtered_event_count, 1) if (self.processed_event_count + self.filtered_event_count) > 0 else 0.0,
                "websocket_enabled": self.enable_websocket,
                "websocket_port": self.websocket_port if self.enable_websocket else None,
                "websocket_clients": len(self.websocket_clients) if self.enable_websocket else 0,
                "websocket_server_active": self._websocket_thread and self._websocket_thread.is_alive() if self.enable_websocket else False
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
    
    def _start_websocket_server(self) -> None:
        """Start WebSocket server for real-time updates."""
        if not self.enable_websocket:
            logger.warning("WebSocket support not available or disabled")
            return
        
        try:
            # Create a new event loop for WebSocket
            self._websocket_loop = asyncio.new_event_loop()
            
            # Start WebSocket server in a separate thread
            self._websocket_thread = threading.Thread(
                target=self._run_websocket_server,
                daemon=True
            )
            self._websocket_thread.start()
            
            logger.info(f"WebSocket server started on port {self.websocket_port}")
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            self.enable_websocket = False
    
    def _run_websocket_server(self) -> None:
        """Run WebSocket server in asyncio event loop."""
        try:
            asyncio.set_event_loop(self._websocket_loop)
            
            async def websocket_handler(websocket):
                """Handle individual WebSocket connections."""
                try:
                    # Add client to connected clients
                    self.websocket_clients.append(websocket)
                    logger.info(f"WebSocket client connected: {websocket.remote_address}")
                    
                    # Send initial status
                    initial_status = {
                        "type": "INITIAL_STATUS",
                        "data": self.get_system_status()
                    }
                    await websocket.send(json.dumps(initial_status))
                    
                    # Keep connection alive and handle messages
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            # Handle client requests (e.g., filter updates)
                            if data.get("type") == "UPDATE_FILTERS":
                                self.update_filtering_config(data.get("filters"))
                        except Exception as e:
                            logger.error(f"Error handling WebSocket message: {e}")
                            
                except ConnectionClosed:
                    logger.info(f"WebSocket client disconnected: {websocket.remote_address}")
                except Exception as e:
                    logger.error(f"WebSocket handler error: {e}")
                finally:
                    # Remove client from connected clients
                    if websocket in self.websocket_clients:
                        self.websocket_clients.remove(websocket)
            
            async def server():
                """Start WebSocket server."""
                async with serve(websocket_handler, "localhost", self.websocket_port):
                    logger.info(f"WebSocket server listening on ws://localhost:{self.websocket_port}")
                    await asyncio.Future()  # Run forever
            
            self._websocket_loop.run_until_complete(server())
            
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
    
    def _stop_websocket_server(self) -> None:
        """Stop WebSocket server."""
        try:
            if self._websocket_loop:
                self._websocket_loop.call_soon_threadsafe(self._websocket_loop.stop)
            
            if self._websocket_thread and self._websocket_thread.is_alive():
                self._websocket_thread.join(timeout=5.0)
            
            # Close all client connections
            for client in self.websocket_clients:
                try:
                    asyncio.run_coroutine_threadsafe(client.close(), self._websocket_loop)
                except Exception as e:
                    logger.error(f"Error closing WebSocket client: {e}")
            
            self.websocket_clients.clear()
            logger.info("WebSocket server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping WebSocket server: {e}")
    
    async def _broadcast_event(self, event: Event) -> None:
        """Broadcast event to all connected WebSocket clients."""
        if not self.websocket_clients:
            return
        
        event_data = {
            "type": "EVENT",
            "data": {
                "event_type": event.type,
                "source": event.source,
                "timestamp": event.timestamp,
                "data": event.data
            }
        }
        
        message = json.dumps(event_data)
        
        # Send to all connected clients
        for client in self.websocket_clients[:]:  # Copy list to avoid modification during iteration
            try:
                await client.send(message)
            except ConnectionClosed:
                self.websocket_clients.remove(client)
            except Exception as e:
                logger.error(f"Error sending event to WebSocket client: {e}")
                self.websocket_clients.remove(client)
    
    def _add_to_history(self, event: Event) -> None:
        """Add event to dashboard history and broadcast via WebSocket."""
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Broadcast to WebSocket clients if enabled
        if self.enable_websocket and self._websocket_loop:
            try:
                asyncio.run_coroutine_threadsafe(
                    self._broadcast_event(event),
                    self._websocket_loop
                )
            except Exception as e:
                logger.error(f"Error broadcasting event via WebSocket: {e}")


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