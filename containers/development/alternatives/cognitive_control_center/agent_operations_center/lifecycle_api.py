"""
cognitive_control_center.agent_operations_center.lifecycle_api
Agent Lifecycle and Workspace Management API - FastAPI endpoints for agent management.

This module provides REST API endpoints for managing agent lifecycle and workspace transitions,
allowing the Dashboard2026 frontend to control and observe agent behavior in the cognitive environment.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from cognitive_control_center.core.agent_lifecycle import (
    get_agent_lifecycle_manager,
    AgentState,
    AgentLifecycleEvent,
    AgentRegistration,
    CognitiveEntityType,
)
from cognitive_control_center.core.workspace_manager import (
    get_workspace_manager,
    WorkspaceType,
    WorkspaceTransition,
)


router = APIRouter(prefix="/lifecycle", tags=["agent-lifecycle"])


# Pydantic models for API responses
class AgentRegistrationResponse(BaseModel):
    agent_id: str
    agent_type: str
    state: str
    registered_at: datetime
    activated_at: Optional[datetime]
    deactivated_at: Optional[datetime]
    current_workspace: Optional[str]
    metadata: Dict[str, Any]


class LifecycleEventResponse(BaseModel):
    agent_id: str
    agent_type: str
    from_state: Optional[str]
    to_state: str
    timestamp: datetime
    reason: str
    data: Dict[str, Any]


class WorkspaceResponse(BaseModel):
    workspace_type: str
    name: str
    description: str
    active_entities: List[str]
    shared_tools: List[str]
    created_at: datetime
    last_activity: datetime


class WorkspaceTransitionResponse(BaseModel):
    entity_id: str
    from_workspace: Optional[str]
    to_workspace: str
    timestamp: datetime
    reason: str


# API Endpoints

@router.get("/agents/registrations", response_model=Dict[str, AgentRegistrationResponse])
async def get_all_agent_registrations():
    """Get all agent registrations."""
    lifecycle_mgr = get_agent_lifecycle_manager()
    registrations = lifecycle_mgr.get_all_registrations()
    
    return {
        agent_id: AgentRegistrationResponse(
            agent_id=reg.agent_id,
            agent_type=reg.agent_type.value,
            state=reg.state.value,
            registered_at=reg.registered_at,
            activated_at=reg.activated_at,
            deactivated_at=reg.deactivated_at,
            current_workspace=reg.current_workspace.value if reg.current_workspace else None,
            metadata=reg.metadata,
        )
        for agent_id, reg in registrations.items()
    }


@router.get("/agents/{agent_id}/registration", response_model=Optional[AgentRegistrationResponse])
async def get_agent_registration(agent_id: str):
    """Get registration for a specific agent."""
    lifecycle_mgr = get_agent_lifecycle_manager()
    registration = lifecycle_mgr.get_agent_registration(agent_id)
    
    if not registration:
        return None
    
    return AgentRegistrationResponse(
        agent_id=registration.agent_id,
        agent_type=registration.agent_type.value,
        state=registration.state.value,
        registered_at=registration.registered_at,
        activated_at=registration.activated_at,
        deactivated_at=registration.deactivated_at,
        current_workspace=registration.current_workspace.value if registration.current_workspace else None,
        metadata=registration.metadata,
    )


@router.get("/agents/active", response_model=Dict[str, AgentRegistrationResponse])
async def get_active_agents():
    """Get all currently active agents."""
    lifecycle_mgr = get_agent_lifecycle_manager()
    active_agents = lifecycle_mgr.get_active_agents()
    
    return {
        agent_id: AgentRegistrationResponse(
            agent_id=reg.agent_id,
            agent_type=reg.agent_type.value,
            state=reg.state.value,
            registered_at=reg.registered_at,
            activated_at=reg.activated_at,
            deactivated_at=reg.deactivated_at,
            current_workspace=reg.current_workspace.value if reg.current_workspace else None,
            metadata=reg.metadata,
        )
        for agent_id, reg in active_agents.items()
    }


@router.post("/agents/register")
async def register_agent(
    agent_id: str,
    agent_type: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Register a new agent in the cognitive environment."""
    lifecycle_mgr = get_agent_lifecycle_manager()
    
    try:
        agent_type_enum = CognitiveEntityType(agent_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")
    
    registration = lifecycle_mgr.register_agent(agent_id, agent_type_enum, metadata)
    
    return AgentRegistrationResponse(
        agent_id=registration.agent_id,
        agent_type=registration.agent_type.value,
        state=registration.state.value,
        registered_at=registration.registered_at,
        activated_at=registration.activated_at,
        deactivated_at=registration.deactivated_at,
        current_workspace=registration.current_workspace.value if registration.current_workspace else None,
        metadata=registration.metadata,
    )


@router.post("/agents/{agent_id}/activate")
async def activate_agent(
    agent_id: str,
    initial_workspace: str,
    reason: Optional[str] = None,
):
    """Activate an agent and move it to its initial workspace."""
    lifecycle_mgr = get_agent_lifecycle_manager()
    
    try:
        workspace_type = WorkspaceType(initial_workspace)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid workspace type: {initial_workspace}")
    
    event = lifecycle_mgr.activate_agent(agent_id, workspace_type, reason or "")
    
    return LifecycleEventResponse(
        agent_id=event.agent_id,
        agent_type=event.agent_type.value,
        from_state=event.from_state.value if event.from_state else None,
        to_state=event.to_state.value,
        timestamp=event.timestamp,
        reason=event.reason,
        data=event.data,
    )


@router.post("/agents/{agent_id}/deactivate")
async def deactivate_agent(agent_id: str, reason: Optional[str] = None):
    """Deactivate an agent."""
    lifecycle_mgr = get_agent_lifecycle_manager()
    event = lifecycle_mgr.deactivate_agent(agent_id, reason or "")
    
    return LifecycleEventResponse(
        agent_id=event.agent_id,
        agent_type=event.agent_type.value,
        from_state=event.from_state.value if event.from_state else None,
        to_state=event.to_state.value,
        timestamp=event.timestamp,
        reason=event.reason,
        data=event.data,
    )


@router.post("/agents/{agent_id}/pause")
async def pause_agent(agent_id: str, reason: Optional[str] = None):
    """Pause an agent temporarily."""
    lifecycle_mgr = get_agent_lifecycle_manager()
    event = lifecycle_mgr.pause_agent(agent_id, reason or "")
    
    return LifecycleEventResponse(
        agent_id=event.agent_id,
        agent_type=event.agent_type.value,
        from_state=event.from_state.value if event.from_state else None,
        to_state=event.to_state.value,
        timestamp=event.timestamp,
        reason=event.reason,
        data=event.data,
    )


@router.post("/agents/{agent_id}/resume")
async def resume_agent(agent_id: str, reason: Optional[str] = None):
    """Resume a paused agent."""
    lifecycle_mgr = get_agent_lifecycle_manager()
    event = lifecycle_mgr.resume_agent(agent_id, reason or "")
    
    return LifecycleEventResponse(
        agent_id=event.agent_id,
        agent_type=event.agent_type.value,
        from_state=event.from_state.value if event.from_state else None,
        to_state=event.to_state.value,
        timestamp=event.timestamp,
        reason=event.reason,
        data=event.data,
    )


@router.post("/agents/{agent_id}/error")
async def report_agent_error(agent_id: str, error: str, data: Optional[Dict[str, Any]] = None):
    """Report an agent error and transition to error state."""
    lifecycle_mgr = get_agent_lifecycle_manager()
    event = lifecycle_mgr.report_agent_error(agent_id, error, data)
    
    return LifecycleEventResponse(
        agent_id=event.agent_id,
        agent_type=event.agent_type.value,
        from_state=event.from_state.value if event.from_state else None,
        to_state=event.to_state.value,
        timestamp=event.timestamp,
        reason=event.reason,
        data=event.data,
    )


@router.get("/events/lifecycle", response_model=List[LifecycleEventResponse])
async def get_lifecycle_events(limit: int = 50):
    """Get recent agent lifecycle events."""
    lifecycle_mgr = get_agent_lifecycle_manager()
    events = lifecycle_mgr.get_lifecycle_events(limit)
    
    return [
        LifecycleEventResponse(
            agent_id=event.agent_id,
            agent_type=event.agent_type.value,
            from_state=event.from_state.value if event.from_state else None,
            to_state=event.to_state.value,
            timestamp=event.timestamp,
            reason=event.reason,
            data=event.data,
        )
        for event in events
    ]


@router.get("/workspaces", response_model[Dict[str, WorkspaceResponse])
async def get_all_workspaces():
    """Get all workspaces."""
    workspace_mgr = get_workspace_manager()
    workspaces = workspace_mgr.get_all_workspaces()
    
    return {
        ws_type.value: WorkspaceResponse(
            workspace_type=ws.workspace_type.value,
            name=ws.name,
            description=ws.description,
            active_entities=list(ws.active_entities),
            shared_tools=ws.shared_tools,
            created_at=ws.created_at,
            last_activity=ws.last_activity,
        )
        for ws_type, ws in workspaces.items()
    }


@router.get("/workspaces/{workspace_type}", response_model=Optional[WorkspaceResponse])
async def get_workspace(workspace_type: str):
    """Get a specific workspace."""
    workspace_mgr = get_workspace_manager()
    
    try:
        ws_type_enum = WorkspaceType(workspace_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid workspace type: {workspace_type}")
    
    workspace = workspace_mgr.get_workspace(ws_type_enum)
    
    if not workspace:
        return None
    
    return WorkspaceResponse(
        workspace_type=workspace.workspace_type.value,
        name=workspace.name,
        description=workspace.description,
        active_entities=list(workspace.active_entities),
        shared_tools=workspace.shared_tools,
        created_at=workspace.created_at,
        last_activity=workspace.last_activity,
    )


@router.post("/entities/{entity_id}/transition")
async def transition_entity_workspace(
    entity_id: str,
    to_workspace: str,
    reason: Optional[str] = None,
):
    """Transition an entity to a different workspace."""
    workspace_mgr = get_workspace_manager()
    
    try:
        workspace_type = WorkspaceType(to_workspace)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid workspace type: {to_workspace}")
    
    transition = workspace_mgr.transition_entity(entity_id, workspace_type, reason or "")
    
    return WorkspaceTransitionResponse(
        entity_id=transition.entity_id,
        from_workspace=transition.from_workspace.value if transition.from_workspace else None,
        to_workspace=transition.to_workspace.value,
        timestamp=transition.timestamp,
        reason=transition.reason,
    )


@router.get("/entities/{entity_id}/workspace")
async def get_entity_workspace(entity_id: str):
    """Get the current workspace for an entity."""
    workspace_mgr = get_workspace_manager()
    workspace = workspace_mgr.get_entity_workspace(entity_id)
    
    return {
        "entity_id": entity_id,
        "current_workspace": workspace.value if workspace else None,
    }


@router.get("/workspaces/{workspace_type}/entities", response_model=List[str])
async def get_workspace_entities(workspace_type: str):
    """Get all entities currently in a workspace."""
    workspace_mgr = get_workspace_manager()
    
    try:
        ws_type_enum = WorkspaceType(workspace_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid workspace type: {workspace_type}")
    
    entities = workspace_mgr.get_workspace_entities(ws_type_enum)
    return list(entities)


@router.get("/transitions/recent", response_model=List[WorkspaceTransitionResponse])
async def get_recent_transitions(limit: int = 50):
    """Get recent workspace transitions."""
    workspace_mgr = get_workspace_manager()
    transitions = workspace_mgr.get_recent_transitions(limit)
    
    return [
        WorkspaceTransitionResponse(
            entity_id=t.entity_id,
            from_workspace=t.from_workspace.value if t.from_workspace else None,
            to_workspace=t.to_workspace.value,
            timestamp=t.timestamp,
            reason=t.reason,
        )
        for t in transitions
    ]