"""
cognitive_control_center.agent_operations_center.api
Agent Operations Center API - FastAPI endpoints for cognitive control center frontend.

This module provides REST API endpoints for the Agent Operations Center, allowing
the Dashboard2026 frontend to access real-time agent observability data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from cognitive_control_center.agent_operations_center.activity_feeds import (
    get_activity_feeds,
)
from cognitive_control_center.core.operating_environment import (
    CognitiveEntityType,
    get_cognitive_environment,
)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/agent-ops", tags=["agent-operations"])


# Pydantic models for API responses
class AgentActivityResponse(BaseModel):
    agent_type: str
    agent_id: str
    current_goal: str
    current_task: str
    cognitive_process: str
    tools_in_use: List[str]
    memory_accesses: List[str]
    timestamp: datetime
    current_research: Optional[str] = None
    current_trader_modeling: Optional[str] = None
    current_strategy_work: Optional[str] = None
    current_repository_task: Optional[str] = None
    current_mutation: Optional[str] = None
    current_refactor: Optional[str] = None
    current_build: Optional[str] = None
    current_testing: Optional[str] = None


class AgentSummaryResponse(BaseModel):
    agent_id: str
    agent_type: str
    status: str
    last_activity: Optional[datetime]
    activity_count: int
    recent_errors: int
    current_activity: Optional[str]


class AssignmentResponse(BaseModel):
    assignment_id: str
    agent_type: str
    agent_id: str
    title: str
    description: str
    status: str
    priority: str
    created_at: datetime
    completed_at: Optional[datetime]


class ProjectResponse(BaseModel):
    project_id: str
    title: str
    description: str
    agent_type: str
    assigned_agents: List[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]


class MemoryResponse(BaseModel):
    agent_id: str
    memory_type: str
    content: str
    timestamp: datetime
    context: Dict[str, Any]


class EnvironmentStateResponse(BaseModel):
    active_entities: Dict[str, str]
    active_workspaces: Dict[str, Dict[str, Any]]
    agent_count: int
    workspace_count: int
    recent_events: int
    assignments: int
    projects: int
    task_queue_size: int
    memories: int


# API Endpoints


@router.get("/environment", response_model=EnvironmentStateResponse)
async def get_environment_state():
    """Get current cognitive environment state."""
    env = get_cognitive_environment()
    state = env.get_environment_state()
    return EnvironmentStateResponse(**state)


@router.get("/agents/activities", response_model=List[AgentActivityResponse])
async def get_agent_activities():
    """Get all current agent activities for observability."""
    env = get_cognitive_environment()
    activities = env.get_agent_activities()

    return [
        AgentActivityResponse(
            agent_type=activity.agent_type.value,
            agent_id=activity.agent_id,
            current_goal=activity.current_goal,
            current_task=activity.current_task,
            cognitive_process=activity.cognitive_process,
            tools_in_use=activity.tools_in_use,
            memory_accesses=activity.memory_accesses,
            timestamp=activity.timestamp,
            current_research=activity.current_research,
            current_trader_modeling=activity.current_trader_modeling,
            current_strategy_work=activity.current_strategy_work,
            current_repository_task=activity.current_repository_task,
            current_mutation=activity.current_mutation,
            current_refactor=activity.current_refactor,
            current_build=activity.current_build,
            current_testing=activity.current_testing,
        )
        for activity in activities.values()
    ]


@router.get("/agents/{agent_id}/activity", response_model=Optional[AgentActivityResponse])
async def get_agent_activity(agent_id: str):
    """Get current activity for a specific agent."""
    env = get_cognitive_environment()
    activities = env.get_agent_activities()

    if agent_id not in activities:
        return None

    activity = activities[agent_id]
    return AgentActivityResponse(
        agent_type=activity.agent_type.value,
        agent_id=activity.agent_id,
        current_goal=activity.current_goal,
        current_task=activity.current_task,
        cognitive_process=activity.cognitive_process,
        tools_in_use=activity.tools_in_use,
        memory_accesses=activity.memory_accesses,
        timestamp=activity.timestamp,
        current_research=activity.current_research,
        current_trader_modeling=activity.current_trader_modeling,
        current_strategy_work=activity.current_strategy_work,
        current_repository_task=activity.current_repository_task,
        current_mutation=activity.current_mutation,
        current_refactor=activity.current_refactor,
        current_build=activity.current_build,
        current_testing=activity.current_testing,
    )


@router.get("/agents/summaries", response_model=List[AgentSummaryResponse])
async def get_agent_summaries():
    """Get summaries of all agent activities."""
    feeds = get_activity_feeds()

    # Get all agent IDs from the environment
    env = get_cognitive_environment()
    activities = env.get_agent_activities()

    summaries = []
    for agent_id in activities.keys():
        summary = feeds.get_agent_summary(agent_id)
        summaries.append(AgentSummaryResponse(**summary))

    return summaries


@router.get("/indira/activity", response_model=Optional[AgentActivityResponse])
async def get_indira_activity():
    """Get current INDIRA activity for observability."""
    env = get_cognitive_environment()
    activities = env.get_agent_activities()

    # Find INDIRA agent
    for activity in activities.values():
        if activity.agent_type == CognitiveEntityType.INDIRA:
            return AgentActivityResponse(
                agent_type=activity.agent_type.value,
                agent_id=activity.agent_id,
                current_goal=activity.current_goal,
                current_task=activity.current_task,
                cognitive_process=activity.cognitive_process,
                tools_in_use=activity.tools_in_use,
                memory_accesses=activity.memory_accesses,
                timestamp=activity.timestamp,
                current_research=activity.current_research,
                current_trader_modeling=activity.current_trader_modeling,
                current_strategy_work=activity.current_strategy_work,
            )

    return None


@router.get("/dyon/activity", response_model=Optional[AgentActivityResponse])
async def get_dyon_activity():
    """Get current DYON activity for observability."""
    env = get_cognitive_environment()
    activities = env.get_agent_activities()

    # Find DYON agent
    for activity in activities.values():
        if activity.agent_type == CognitiveEntityType.DYON:
            return AgentActivityResponse(
                agent_type=activity.agent_type.value,
                agent_id=activity.agent_id,
                current_goal=activity.current_goal,
                current_task=activity.current_task,
                cognitive_process=activity.cognitive_process,
                tools_in_use=activity.tools_in_use,
                memory_accesses=activity.memory_accesses,
                timestamp=activity.timestamp,
                current_repository_task=activity.current_repository_task,
                current_mutation=activity.current_mutation,
                current_refactor=activity.current_refactor,
                current_build=activity.current_build,
                current_testing=activity.current_testing,
            )

    return None


@router.get("/assignments", response_model=List[AssignmentResponse])
async def get_assignments(agent_type: Optional[str] = None):
    """Get all assignments, optionally filtered by agent type."""
    env = get_cognitive_environment()

    agent_filter = None
    if agent_type:
        try:
            agent_filter = CognitiveEntityType(agent_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")

    assignments = env.get_assignments(agent_filter)

    return [
        AssignmentResponse(
            assignment_id=a.assignment_id,
            agent_type=a.agent_type.value,
            agent_id=a.agent_id,
            title=a.title,
            description=a.description,
            status=a.status,
            priority=a.priority,
            created_at=a.created_at,
            completed_at=a.completed_at,
        )
        for a in assignments
    ]


@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(agent_type: Optional[str] = None):
    """Get all projects, optionally filtered by agent type."""
    env = get_cognitive_environment()

    agent_filter = None
    if agent_type:
        try:
            agent_filter = CognitiveEntityType(agent_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")

    projects = env.get_projects(agent_filter)

    return [
        ProjectResponse(
            project_id=p.project_id,
            title=p.title,
            description=p.description,
            agent_type=p.agent_type.value,
            assigned_agents=p.assigned_agents,
            status=p.status,
            created_at=p.created_at,
            completed_at=p.completed_at,
        )
        for p in projects
    ]


@router.get("/task-queue", response_model=List[AssignmentResponse])
async def get_task_queue():
    """Get current task queue."""
    env = get_cognitive_environment()
    queue = env.get_task_queue()

    return [
        AssignmentResponse(
            assignment_id=a.assignment_id,
            agent_type=a.agent_type.value,
            agent_id=a.agent_id,
            title=a.title,
            description=a.description,
            status=a.status,
            priority=a.priority,
            created_at=a.created_at,
            completed_at=a.completed_at,
        )
        for a in queue
    ]


@router.get("/memories", response_model=List[MemoryResponse])
async def get_agent_memories(agent_id: Optional[str] = None, limit: int = 50):
    """Get agent memories, optionally filtered by agent ID."""
    env = get_cognitive_environment()
    memories = env.get_agent_memories(agent_id)

    return [
        MemoryResponse(
            agent_id=m.agent_id,
            memory_type=m.memory_type,
            content=m.content,
            timestamp=m.timestamp,
            context=m.context,
        )
        for m in memories[-limit:]
    ]


@router.get("/timeline", response_model=List[Dict[str, Any]])
async def get_agent_timeline(agent_id: Optional[str] = None, limit: int = 50):
    """Get agent timeline events."""
    env = get_cognitive_environment()
    events = env.get_agent_timeline(agent_id, limit)

    return [
        {
            "entity_type": e.entity_type.value,
            "entity_id": e.entity_id,
            "event_type": e.event_type,
            "timestamp": e.timestamp.isoformat(),
            "data": e.data,
            "workspace": e.workspace.value if e.workspace else None,
        }
        for e in events
    ]


@router.get("/activity-feed/recent")
async def get_recent_activity(minutes: int = 5, limit: int = 50):
    """Get recent activity across all agents."""
    feeds = get_activity_feeds()
    recent = feeds.get_recent_activity(minutes=minutes, limit=limit)

    return [
        {
            "agent_type": e.agent_type.value,
            "agent_id": e.agent_id,
            "activity_type": e.activity_type.value,
            "timestamp": e.timestamp.isoformat(),
            "description": e.description,
            "data": e.data,
            "severity": e.severity,
        }
        for e in recent
    ]
