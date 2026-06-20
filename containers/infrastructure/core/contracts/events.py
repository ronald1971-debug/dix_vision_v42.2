"""
Core Contracts Events
Real implementation for system events
Based on events.proto from DIX VISION contracts
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
import time
import uuid

class EventKind(Enum):
    """Event kind classification"""
    MARKET = "market"
    SIGNAL = "signal"
    SYSTEM = "system"
    HAZARD = "hazard"
    GOVERNANCE = "governance"
    EXECUTION = "execution"
    LEARNING = "learning"

class SystemEventKind(Enum):
    """Specific system event kinds"""
    ENGINE_STARTUP = "engine_startup"
    ENGINE_SHUTDOWN = "engine_shutdown"
    HEALTH_CHECK = "health_check"
    CONFIGURATION_CHANGE = "configuration_change"
    MODE_CHANGE = "mode_change"

class Side(Enum):
    """Trade side"""
    BUY = "buy"
    SELL = "sell"

@dataclass
class Event:
    """Base event class"""
    kind: EventKind
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HazardEvent(Event):
    """Hazard event for system safety"""
    severity: str = "warning"
    component: str = ""
    description: str = ""
    mitigation_required: bool = True
    
    def __post_init__(self):
        if self.kind != EventKind.HAZARD:
            self.kind = EventKind.HAZARD

@dataclass
class SignalEvent(Event):
    """Signal event for trading signals"""
    strength: float = 0.5
    source: str = ""
    confidence: float = 1.0
    
    def __post_init__(self):
        if self.kind != EventKind.SIGNAL:
            self.kind = EventKind.SIGNAL

@dataclass
class SystemEvent(Event):
    """System event for system operations"""
    system_event_kind: SystemEventKind = SystemEventKind.HEALTH_CHECK
    component: str = ""
    status: str = "ok"
    
    def __post_init__(self):
        if self.kind != EventKind.SYSTEM:
            self.kind = EventKind.SYSTEM

__all__ = [
    "EventKind",
    "SystemEventKind",
    "Side",
    "Event",
    "HazardEvent",
    "SignalEvent",
    "SystemEvent"
]