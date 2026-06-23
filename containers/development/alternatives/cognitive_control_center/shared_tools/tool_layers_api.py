"""
cognitive_control_center.shared_tools.tool_layers_api
Shared Tool Layers API - FastAPI endpoints for shared tool layer management.

This module provides REST API endpoints for the shared tool layers (Desktop, Browser, Knowledge),
allowing the Dashboard2026 frontend to manage and monitor tool layer usage by Operator, INDIRA, and DYON.
"""

from datetime import datetime
from typing import Dict, List, Optional

from cognitive_control_center.shared_tools.tool_layers import (
    BrowserLayerActivity,
    BrowserType,
    CognitiveEntityType,
    DesktopLayerActivity,
    ToolLayerType,
    get_shared_tool_layers,
)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/shared-tools", tags=["shared-tools"])


# Pydantic models for API responses
class ToolLayerSessionResponse(BaseModel):
    session_id: str
    entity_type: str
    entity_id: str
    layer_type: str
    browser_type: Optional[str]
    started_at: datetime
    last_activity: datetime
    status: str
    operations: List[str]


class DesktopActivityResponse(BaseModel):
    session_id: str
    entity_type: str
    entity_id: str
    activity_type: str
    application: Optional[str]
    window_title: Optional[str]
    coordinates: Optional[tuple]
    screenshot_path: Optional[str]
    timestamp: datetime


class BrowserActivityResponse(BaseModel):
    session_id: str
    entity_type: str
    entity_id: str
    activity_type: str
    url: Optional[str]
    page_title: Optional[str]
    tab_id: Optional[str]
    user_agent: Optional[str]
    browser_type: Optional[str]
    timestamp: datetime


class LayerStatusResponse(BaseModel):
    layer_type: str
    available: bool
    active_sessions: int
    recent_activity_count: int
    current_user: Optional[str]
    current_user_type: Optional[str]


class BrowserAvailabilityResponse(BaseModel):
    browser_type: str
    available: bool
    active_sessions: int
    assigned_to: Optional[str]
    assigned_to_type: Optional[str]


# API Endpoints


@router.get("/layers/status", response_model=Dict[str, LayerStatusResponse])
async def get_all_layer_status():
    """Get status of all shared tool layers."""
    tool_layers = get_shared_tool_layers()

    return {
        layer_type.value: LayerStatusResponse(**tool_layers.get_layer_status(layer_type))
        for layer_type in ToolLayerType
    }


@router.get("/layers/{layer_type}/status", response_model=LayerStatusResponse)
async def get_layer_status(layer_type: str):
    """Get status of a specific tool layer."""
    tool_layers = get_shared_tool_layers()

    try:
        layer_type_enum = ToolLayerType(layer_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid layer type: {layer_type}")

    status = tool_layers.get_layer_status(layer_type_enum)
    return LayerStatusResponse(**status)


@router.get("/browsers/availability", response_model=Dict[str, BrowserAvailabilityResponse])
async def get_browser_availability():
    """Get availability status for each browser type (Operator=Edge, INDIRA=Chrome, DYON=Firefox)."""
    tool_layers = get_shared_tool_layers()

    availability = tool_layers.get_browser_availability()

    return {
        browser_type: BrowserAvailabilityResponse(**status)
        for browser_type, status in availability.items()
    }


@router.post("/sessions/start")
async def start_tool_layer_session(
    entity_type: str,
    entity_id: str,
    layer_type: str,
    browser_type: Optional[str] = None,
):
    """Start a new session using a shared tool layer."""
    tool_layers = get_shared_tool_layers()

    try:
        entity_type_enum = CognitiveEntityType(entity_type)
        layer_type_enum = ToolLayerType(layer_type)
        browser_type_enum = BrowserType(browser_type) if browser_type else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    session_id = tool_layers.start_session(
        entity_type_enum, entity_id, layer_type_enum, browser_type_enum
    )

    return {
        "session_id": session_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "layer_type": layer_type,
        "browser_type": browser_type,
        "status": "active",
    }


@router.post("/sessions/{session_id}/end")
async def end_tool_layer_session(session_id: str):
    """End a tool layer session."""
    tool_layers = get_shared_tool_layers()
    tool_layers.end_session(session_id)

    return {"session_id": session_id, "status": "ended"}


@router.get("/sessions", response_model=List[ToolLayerSessionResponse])
async def get_tool_layer_sessions(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
):
    """Get tool layer sessions, optionally filtered by entity."""
    tool_layers = get_shared_tool_layers()

    entity_filter = None
    if entity_type:
        try:
            entity_filter = CognitiveEntityType(entity_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity_type}")

    sessions = tool_layers.get_entity_sessions(entity_filter, entity_id)

    return [
        ToolLayerSessionResponse(
            session_id=s.session_id,
            entity_type=s.entity_type.value,
            entity_id=s.entity_id,
            layer_type=s.layer_type.value,
            browser_type=s.browser_type.value if s.browser_type else None,
            started_at=s.started_at,
            last_activity=s.last_activity,
            status=s.status.value,
            operations=s.operations,
        )
        for s in sessions
    ]


@router.post("/desktop/record")
async def record_desktop_activity(
    session_id: str,
    entity_type: str,
    entity_id: str,
    activity_type: str,
    application: Optional[str] = None,
    window_title: Optional[str] = None,
    coordinates: Optional[tuple] = None,
    screenshot_path: Optional[str] = None,
):
    """Record activity in the Desktop Agent Layer."""
    tool_layers = get_shared_tool_layers()

    try:
        entity_type_enum = CognitiveEntityType(entity_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity_type}")

    activity = DesktopLayerActivity(
        session_id=session_id,
        entity_type=entity_type_enum,
        entity_id=entity_id,
        activity_type=activity_type,
        application=application,
        window_title=window_title,
        coordinates=coordinates,
        screenshot_path=screenshot_path,
    )

    tool_layers.record_desktop_activity(activity)

    return {"status": "recorded", "activity_type": activity_type}


@router.get("/desktop/activities", response_model=List[DesktopActivityResponse])
async def get_desktop_activities(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 50,
):
    """Get desktop layer activities, optionally filtered."""
    tool_layers = get_shared_tool_layers()

    entity_filter = None
    if entity_type:
        try:
            entity_filter = CognitiveEntityType(entity_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity_type}")

    activities = tool_layers.get_desktop_activities(entity_filter, entity_id, limit)

    return [
        DesktopActivityResponse(
            session_id=a.session_id,
            entity_type=a.entity_type.value,
            entity_id=a.entity_id,
            activity_type=a.activity_type,
            application=a.application,
            window_title=a.window_title,
            coordinates=a.coordinates,
            screenshot_path=a.screenshot_path,
            timestamp=a.timestamp,
        )
        for a in activities
    ]


@router.post("/browser/record")
async def record_browser_activity(
    session_id: str,
    entity_type: str,
    entity_id: str,
    activity_type: str,
    url: Optional[str] = None,
    page_title: Optional[str] = None,
    tab_id: Optional[str] = None,
    user_agent: Optional[str] = None,
    browser_type: Optional[str] = None,
):
    """Record activity in the Browser Layer."""
    tool_layers = get_shared_tool_layers()

    try:
        entity_type_enum = CognitiveEntityType(entity_type)
        browser_type_enum = BrowserType(browser_type) if browser_type else None
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid entity type or browser type")

    activity = BrowserLayerActivity(
        session_id=session_id,
        entity_type=entity_type_enum,
        entity_id=entity_id,
        activity_type=activity_type,
        url=url,
        page_title=page_title,
        tab_id=tab_id,
        user_agent=user_agent,
        browser_type=browser_type_enum,
    )

    tool_layers.record_browser_activity(activity)

    return {"status": "recorded", "activity_type": activity_type}


@router.get("/browser/activities", response_model=List[BrowserActivityResponse])
async def get_browser_activities(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 50,
):
    """Get browser layer activities, optionally filtered."""
    tool_layers = get_shared_tool_layers()

    entity_filter = None
    if entity_type:
        try:
            entity_filter = CognitiveEntityType(entity_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity_type}")

    activities = tool_layers.get_browser_activities(entity_filter, entity_id, limit)

    return [
        BrowserActivityResponse(
            session_id=a.session_id,
            entity_type=a.entity_type.value,
            entity_id=a.entity_id,
            activity_type=a.activity_type,
            url=a.url,
            page_title=a.page_title,
            tab_id=a.tab_id,
            user_agent=a.user_agent,
            browser_type=a.browser_type.value if a.browser_type else None,
            timestamp=a.timestamp,
        )
        for a in activities
    ]
