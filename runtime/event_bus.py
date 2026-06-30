"""
DIX VISION Event Bus System

Formal event-driven communication system as specified in the Runtime Specification.
All communication between services MUST pass through this EventBus.

Usage:
    from runtime.event_bus import EventBus, get_event_bus
    
    event_bus = get_event_bus()
    event_bus.subscribe("MEMORY_WARNING", handler)
    event_bus.publish(Event("memory_monitor", "MEMORY_WARNING", {}))
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Standard event types for the DIX VISION system."""
    
    # Memory events
    MEMORY_WARNING = "MEMORY_WARNING"
    MEMORY_CRITICAL = "MEMORY_CRITICAL"
    MEMORY_RECOVERY = "MEMORY_RECOVERY"
    OOM_PREVENTION = "OOM_PREVENTION"
    
    # AI Runtime events
    AI_INIT = "AI_INIT"
    AI_START = "AI_START"
    AI_STOP = "AI_STOP"
    AI_STATE_UPDATE = "AI_STATE_UPDATE"
    AI_DECISION = "AI_DECISION"
    AI_ERROR = "AI_ERROR"
    
    # Execution events
    EXECUTION_START = "EXECUTION_START"
    EXECUTION_COMPLETE = "EXECUTION_COMPLETE"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    
    # Dashboard events
    DASHBOARD_READY = "DASHBOARD_READY"
    DASHBOARD_ERROR = "DASHBOARD_ERROR"
    
    # System events
    SYSTEM_BOOT = "SYSTEM_BOOT"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    SYSTEM_DEGRADED = "SYSTEM_DEGRADED"
    SYSTEM_RECOVERING = "SYSTEM_RECOVERING"
    
    # Validation events
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # Service events
    SERVICE_START = "SERVICE_START"
    SERVICE_STOP = "SERVICE_STOP"
    SERVICE_CRASH = "SERVICE_CRASH"
    SERVICE_HEALTH = "SERVICE_HEALTH"


class SystemState(str, Enum):
    """System states as specified in the Runtime Specification."""
    BOOTING = "BOOTING"
    RUNNING = "RUNNING"
    DEGRADED = "DEGRADED"
    RECOVERING = "RECOVERING"
    STOPPED = "STOPPED"


class FailureType(str, Enum):
    """Failure types as specified in the Runtime Specification."""
    MEMORY_FAILURE = "MEMORY_FAILURE"
    SERVICE_CRASH = "SERVICE_CRASH"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
    RUNTIME_DESYNC = "RUNTIME_DESYNC"


@dataclass
class Event:
    """Event structure as specified in the Runtime Specification."""
    source: str
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "source": self.source,
            "type": self.type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat()
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class EventHandler:
    """Wrapper for event handlers with metadata."""
    
    def __init__(self, callback: Callable[[Event], None], service: str, priority: int = 0):
        self.callback = callback
        self.service = service
        self.priority = priority
        self.active = True
    
    def __call__(self, event: Event) -> None:
        """Execute the handler callback."""
        if self.active:
            try:
                self.callback(event)
            except Exception as e:
                logger.error(f"Event handler error in {self.service}: {e}")
    
    def disable(self) -> None:
        """Disable this handler."""
        self.active = False
    
    def enable(self) -> None:
        """Enable this handler."""
        self.active = True


class EventBus:
    """Central event bus for all system communication."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[EventHandler]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000
        self._lock = threading.Lock()
        self._async_loop = None
        self._event_queue = None
        self._running = False
        
    def subscribe(self, event_type: str, handler: Callable[[Event], None], 
                  service: str = "unknown", priority: int = 0) -> EventHandler:
        """Subscribe to an event type."""
        with self._lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            
            event_handler = EventHandler(handler, service, priority)
            self.subscribers[event_type].append(event_handler)
            
            # Sort by priority (higher priority first)
            self.subscribers[event_type].sort(key=lambda h: h.priority, reverse=True)
            
            logger.info(f"Service {service} subscribed to {event_type}")
            return event_handler
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> bool:
        """Unsubscribe from an event type."""
        with self._lock:
            if event_type in self.subscribers and handler in self.subscribers[event_type]:
                self.subscribers[event_type].remove(handler)
                logger.info(f"Unsubscribed from {event_type}")
                return True
            return False
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        with self._lock:
            # Add to history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
            
            # Get subscribers for this event type
            subscribers = self.subscribers.get(event.type, []).copy()
        
        # Call handlers outside the lock to prevent deadlocks
        for handler in subscribers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.type}: {e}")
        
        logger.debug(f"Published event {event.type} from {event.source}")
    
    def publish_sync(self, source: str, event_type: str, payload: Dict[str, Any] = None) -> None:
        """Convenience method to publish an event synchronously."""
        event = Event(source=source, type=event_type, payload=payload or {})
        self.publish(event)
    
    async def publish_async(self, source: str, event_type: str, payload: Dict[str, Any] = None) -> None:
        """Convenience method to publish an event asynchronously."""
        event = Event(source=source, type=event_type, payload=payload or {})
        await asyncio.get_event_loop().run_in_executor(None, self.publish, event)
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """Get event history, optionally filtered by type."""
        with self._lock:
            if event_type:
                events = [e for e in self.event_history if e.type == event_type]
            else:
                events = self.event_history.copy()
            
            return events[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self.event_history.clear()
            logger.info("Event history cleared")
    
    def get_subscriber_count(self, event_type: str = None) -> int:
        """Get number of subscribers, optionally filtered by type."""
        with self._lock:
            if event_type:
                return len(self.subscribers.get(event_type, []))
            return sum(len(subs) for subs in self.subscribers.values())
    
    def start_async_processing(self) -> None:
        """Start async event processing loop."""
        if self._running:
            return
        
        self._running = True
        self._async_loop = asyncio.new_event_loop()
        self._event_queue = asyncio.Queue()
        
        def run_loop():
            asyncio.set_event_loop(self._async_loop)
            self._async_loop.run_until_complete(self._process_events())
        
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        logger.info("Async event processing started")
    
    async def _process_events(self) -> None:
        """Process events from the queue."""
        while self._running:
            try:
                event = await self._event_queue.get()
                await asyncio.get_event_loop().run_in_executor(None, self.publish, event)
            except Exception as e:
                logger.error(f"Error processing async event: {e}")
    
    def stop_async_processing(self) -> None:
        """Stop async event processing."""
        self._running = False
        if self._async_loop:
            self._async_loop.stop()
        logger.info("Async event processing stopped")


# Global instance
_event_bus: Optional[EventBus] = None
_lock = threading.Lock()


def get_event_bus() -> EventBus:
    """Get global event bus instance."""
    global _event_bus
    if _event_bus is None:
        with _lock:
            if _event_bus is None:
                _event_bus = EventBus()
    return _event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (mainly for testing)."""
    global _event_bus
    with _lock:
        _event_bus = None


__all__ = [
    "EventBus",
    "Event",
    "EventHandler",
    "EventType",
    "SystemState",
    "FailureType",
    "get_event_bus",
    "reset_event_bus",
]