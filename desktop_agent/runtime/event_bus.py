"""
Event Bus - Inter-component communication and event routing
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Event:
    """Represents an event in the system."""
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: Optional[str] = None
    correlation_id: Optional[str] = None


class EventBus:
    """
    Async event bus for component communication.
    
    Provides publish-subscribe pattern for inter-component
    messaging with support for filtering, correlation, and
    event history.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.global_subscribers: List[Callable] = []
        self.event_history: List[Event] = []
        self.max_history = 1000
        self.is_initialized = False
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize the event bus."""
        self.is_initialized = True
        self.logger.info("Event Bus initialized")
        
    async def subscribe(
        self,
        event_name: str,
        handler: Callable,
        filter_func: Optional[Callable] = None,
    ) -> None:
        """
        Subscribe to an event.
        
        Args:
            event_name: Event name to subscribe to
            handler: Handler function
            filter_func: Optional filter function
        """
        if filter_func:
            wrapped_handler = self._create_filtered_handler(handler, filter_func)
            self.subscribers[event_name].append(wrapped_handler)
        else:
            self.subscribers[event_name].append(handler)
            
        self.logger.info(f"Subscribed to event: {event_name}")
        
    async def subscribe_all(
        self,
        handler: Callable,
        filter_func: Optional[Callable] = None,
    ) -> None:
        """
        Subscribe to all events.
        
        Args:
            handler: Handler function
            filter_func: Optional filter function
        """
        if filter_func:
            wrapped_handler = self._create_filtered_handler(handler, filter_func)
            self.global_subscribers.append(wrapped_handler)
        else:
            self.global_subscribers.append(handler)
            
        self.logger.info("Subscribed to all events")
        
    async def unsubscribe(
        self,
        event_name: str,
        handler: Callable,
    ) -> None:
        """
        Unsubscribe from an event.
        
        Args:
            event_name: Event name
            handler: Handler function
        """
        if event_name in self.subscribers:
            self.subscribers[event_name] = [
                h for h in self.subscribers[event_name]
                if h.__name__ != handler.__name__
            ]
            
        self.logger.info(f"Unsubscribed from event: {event_name}")
        
    async def emit(
        self,
        event_name: str,
        data: Dict[str, Any] = None,
        source: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Emit an event.
        
        Args:
            event_name: Event name
            data: Event data
            source: Event source
            correlation_id: Correlation ID for tracking
        """
        if data is None:
            data = {}
            
        event = Event(
            name=event_name,
            data=data,
            source=source,
            correlation_id=correlation_id,
        )
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
            
        # Notify subscribers
        await self._notify_subscribers(event)
        
        self.logger.debug(f"Emitted event: {event_name}")
        
    async def _notify_subscribers(self, event: Event) -> None:
        """
        Notify all subscribers of an event.
        
        Args:
            event: Event to notify
        """
        # Notify event-specific subscribers
        for handler in self.subscribers.get(event.name, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                self.logger.error(f"Handler error for {event.name}: {e}")
                
        # Notify global subscribers
        for handler in self.global_subscribers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                self.logger.error(f"Global handler error for {event.name}: {e}")
                
    def _create_filtered_handler(
        self,
        handler: Callable,
        filter_func: Callable,
    ) -> Callable:
        """
        Create a filtered handler.
        
        Args:
            handler: Original handler
            filter_func: Filter function
            
        Returns:
            Filtered handler
        """
        async def filtered_handler(event: Event) -> None:
            if filter_func(event):
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                    
        return filtered_handler
        
    async def get_history(
        self,
        event_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_name: Optional event name filter
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        events = self.event_history
        
        if event_name:
            events = [e for e in events if e.name == event_name]
            
        return events[-limit:]
        
    async def clear_history(self) -> None:
        """Clear event history."""
        self.event_history.clear()
        self.logger.info("Event history cleared")
