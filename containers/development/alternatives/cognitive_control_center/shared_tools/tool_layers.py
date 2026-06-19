"""
cognitive_control_center.shared_tools.tool_layers
Shared Tool Layers - Desktop and Browser layers as shared tools for Operator, INDIRA, DYON.

This module implements the shared tool layer infrastructure where Operator, INDIRA, and DYON
all share access to Desktop Agent Layer and Browser Layer as common tools in the cognitive
operating environment.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional

from cognitive_control_center.core.operating_environment import (
    CognitiveEntityType,
    get_cognitive_environment,
)


class ToolLayerType(StrEnum):
    """Types of shared tool layers."""
    DESKTOP_LAYER = "desktop_layer"
    BROWSER_LAYER = "browser_layer"
    KNOWLEDGE_LAYER = "knowledge_layer"


class BrowserType(StrEnum):
    """Browser types for different entities to prevent conflicts."""
    EDGE = "edge"
    CHROME = "chrome"
    FIREFOX = "firefox"
    BRAVE = "brave"


class ToolLayerStatus(StrEnum):
    """Status of tool layer operations."""
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    BUSY = "busy"


@dataclass
class ToolLayerSession:
    """A session where an entity is using a shared tool layer."""
    session_id: str
    entity_type: CognitiveEntityType
    entity_id: str
    layer_type: ToolLayerType
    browser_type: BrowserType | None = None
    started_at: datetime
    last_activity: datetime
    operations: List[str] = field(default_factory=list)
    status: ToolLayerStatus = ToolLayerStatus.ACTIVE


@dataclass
class DesktopLayerActivity:
    """Activity in the Desktop Agent Layer."""
    session_id: str
    entity_type: CognitiveEntityType
    entity_id: str
    activity_type: str  # automation, inspection, interaction
    application: str | None = None
    window_title: str | None = None
    coordinates: tuple[int, int] | None = None
    screenshot_path: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BrowserLayerActivity:
    """Activity in the Browser Layer."""
    session_id: str
    entity_type: CognitiveEntityType
    entity_id: str
    activity_type: str  # research, navigation, interaction, scraping
    url: str | None = None
    page_title: str | None = None
    tab_id: str | None = None
    user_agent: str | None = None
    browser_type: BrowserType | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SharedToolLayers:
    """
    Shared tool layers used by Operator, INDIRA, and DYON.
    
    Implements Desktop Agent Layer and Browser Layer as shared tools where all three parties
    can use the same infrastructure for their respective operations.
    
    Browser Conflict Resolution: Each entity uses a dedicated browser to prevent conflicts:
        - Operator: Edge (primary operator browser)
        - INDIRA: Chrome (trading operations)
        - DYON: Firefox (system engineering tasks)
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._active_sessions: Dict[str, ToolLayerSession] = {}
        self._desktop_activities: List[DesktopLayerActivity] = []
        self._browser_activities: List[BrowserLayerActivity] = []
        self._layer_availability: Dict[ToolLayerType, bool] = {
            ToolLayerType.DESKTOP_LAYER: True,
            ToolLayerType.BROWSER_LAYER: True,
            ToolLayerType.KNOWLEDGE_LAYER: True,
        }
        
        # Entity-specific browser assignments to prevent conflicts
        self._entity_browser_map: Dict[CognitiveEntityType, BrowserType] = {
            CognitiveEntityType.OPERATOR: BrowserType.EDGE,
            CognitiveEntityType.INDIRA: BrowserType.CHROME,
            CognitiveEntityType.DYON: BrowserType.FIREFOX,
        }

    def get_entity_browser(self, entity_type: CognitiveEntityType) -> BrowserType:
        """Get the assigned browser for a specific entity."""
        return self._entity_browser_map.get(entity_type, BrowserType.CHROME)

    def start_session(
        self,
        entity_type: CognitiveEntityType,
        entity_id: str,
        layer_type: ToolLayerType,
        browser_type: BrowserType | None = None,
    ) -> str:
        """Start a new session using a shared tool layer."""
        # Assign browser automatically if using browser layer and none specified
        if layer_type == ToolLayerType.BROWSER_LAYER and browser_type is None:
            browser_type = self.get_entity_browser(entity_type)
        
        session_id = f"{layer_type.value}_{entity_id}_{datetime.utcnow().timestamp()}"
        
        with self._lock:
            session = ToolLayerSession(
                session_id=session_id,
                entity_type=entity_type,
                entity_id=entity_id,
                layer_type=layer_type,
                browser_type=browser_type,
                started_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                status=ToolLayerStatus.ACTIVE,
            )
            self._active_sessions[session_id] = session
            
            # Mark layer as busy (but allow concurrent browser sessions with different browsers)
            if layer_type == ToolLayerType.BROWSER_LAYER and browser_type:
                # For browser layer, only mark this specific browser as busy
                pass  # Individual browser instances allow concurrency
            elif layer_type in self._layer_availability:
                self._layer_availability[layer_type] = False
        
        return session_id

    def end_session(self, session_id: str) -> None:
        """End a tool layer session."""
        with self._lock:
            if session_id in self._active_sessions:
                session = self._active_sessions[session_id]
                session.status = ToolLayerStatus.IDLE
                session.last_activity = datetime.utcnow()
                
                # Mark layer as available (except for browser layers which are per-browser)
                if session.layer_type != ToolLayerType.BROWSER_LAYER:
                    if session.layer_type in self._layer_availability:
                        self._layer_availability[session.layer_type] = True

    def get_browser_availability(self) -> Dict[str, Any]:
        """Get availability status for each browser."""
        with self._lock:
            browser_sessions = {
                browser_type: [
                    s for s in self._active_sessions.values()
                    if s.layer_type == ToolLayerType.BROWSER_LAYER 
                    and s.browser_type == browser_type 
                    and s.status == ToolLayerStatus.ACTIVE
                ]
                for browser_type in BrowserType
            }
            
            return {
                browser_type.value: {
                    "available": len(sessions) == 0,
                    "active_sessions": len(sessions),
                    "assigned_to": sessions[0].entity_id if sessions else None,
                    "assigned_to_type": sessions[0].entity_type.value if sessions else None,
                }
                for browser_type, sessions in browser_sessions.items()
            }

    def record_desktop_activity(self, activity: DesktopLayerActivity) -> None:
        """Record activity in the Desktop Agent Layer."""
        with self._lock:
            self._desktop_activities.append(activity)
            
            # Update session last activity
            if activity.session_id in self._active_sessions:
                self._active_sessions[activity.session_id].last_activity = datetime.utcnow()
            
            # Keep last 500 activities
            if len(self._desktop_activities) > 500:
                self._desktop_activities = self._desktop_activities[-500:]

    def record_browser_activity(self, activity: BrowserLayerActivity) -> None:
        """Record activity in the Browser Layer."""
        with self._lock:
            # Auto-populate browser_type from session if not provided
            if not activity.browser_type and activity.session_id in self._active_sessions:
                session = self._active_sessions[activity.session_id]
                activity.browser_type = session.browser_type
                
            self._browser_activities.append(activity)
            
            # Update session last activity
            if activity.session_id in self._active_sessions:
                self._active_sessions[activity.session_id].last_activity = datetime.utcnow()
            
            # Keep last 500 activities
            if len(self._browser_activities) > 500:
                self._browser_activities = self._browser_activities[-500:]

    def get_layer_status(self, layer_type: ToolLayerType) -> Dict[str, Any]:
        """Get status of a specific tool layer."""
        with self._lock:
            layer_sessions = [
                s for s in self._active_sessions.values()
                if s.layer_type == layer_type and s.status == ToolLayerStatus.ACTIVE
            ]
            
            if layer_type == ToolLayerType.DESKTOP_LAYER:
                recent_activities = [
                    a for a in self._desktop_activities
                    if a.timestamp >= datetime.utcnow() - __import__('datetime').timedelta(minutes=5)
                ]
            elif layer_type == ToolLayerType.BROWSER_LAYER:
                recent_activities = [
                    a for a in self._browser_activities
                    if a.timestamp >= datetime.utcnow() - __import__('datetime').timedelta(minutes=5)
                ]
            else:
                recent_activities = []
            
            return {
                "layer_type": layer_type.value,
                "available": self._layer_availability.get(layer_type, True),
                "active_sessions": len(layer_sessions),
                "recent_activity_count": len(recent_activities),
                "current_user": layer_sessions[0].entity_id if layer_sessions else None,
                "current_user_type": layer_sessions[0].entity_type.value if layer_sessions else None,
            }

    def get_entity_sessions(
        self,
        entity_type: CognitiveEntityType | None = None,
        entity_id: str | None = None,
    ) -> List[ToolLayerSession]:
        """Get sessions for specific entities."""
        with self._lock:
            sessions = list(self._active_sessions.values())
            
            if entity_type:
                sessions = [s for s in sessions if s.entity_type == entity_type]
            
            if entity_id:
                sessions = [s for s in sessions if s.entity_id == entity_id]
            
            return sessions

    def get_desktop_activities(
        self,
        entity_type: CognitiveEntityType | None = None,
        entity_id: str | None = None,
        limit: int = 50,
    ) -> List[DesktopLayerActivity]:
        """Get desktop layer activities, optionally filtered."""
        with self._lock:
            activities = list(self._desktop_activities)
            
            if entity_type:
                activities = [a for a in activities if a.entity_type == entity_type]
            
            if entity_id:
                activities = [a for a in activities if a.entity_id == entity_id]
            
            return activities[-limit:]

    def get_browser_activities(
        self,
        entity_type: CognitiveEntityType | None = None,
        entity_id: str | None = None,
        limit: int = 50,
    ) -> List[BrowserLayerActivity]:
        """Get browser layer activities, optionally filtered."""
        with self._lock:
            activities = list(self._browser_activities)
            
            if entity_type:
                activities = [a for a in activities if a.entity_type == entity_type]
            
            if entity_id:
                activities = [a for a in activities if a.entity_id == entity_id]
            
            return activities[-limit:]


_tool_layers: SharedToolLayers | None = None
_tool_layers_lock = threading.Lock()


def get_shared_tool_layers() -> SharedToolLayers:
    """Get the singleton shared tool layers instance."""
    global _tool_layers
    if _tool_layers is None:
        with _tool_layers_lock:
            if _tool_layers is None:
                _tool_layers = SharedToolLayers()
    return _tool_layers