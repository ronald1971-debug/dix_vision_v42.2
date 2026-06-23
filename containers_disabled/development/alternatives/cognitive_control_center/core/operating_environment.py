"""
cognitive_control_center.core.operating_environment
Cognitive Operating Environment - Core infrastructure for unified cognitive control center.

This module implements the core cognitive operating environment where agents live and work,
replacing the fragmented UI systems (cockpit/, dashboard2026/, dash_meme/) with a single
cohesive cognitive operating environment as designed in the original DIX VISION v42.2 plan.

Architecture Philosophy: Dashboard = Cognitive Operating Environment (not UI layer)
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Callable


class CognitiveEntityType(StrEnum):
    """Types of entities in the cognitive environment."""

    OPERATOR = "operator"
    INDIRA = "indira"  # Trading agent
    DYON = "dyon"  # System maintenance agent
    SYSTEM = "system"  # System-level processes


class WorkspaceType(StrEnum):
    """Types of workspaces in the cognitive environment."""

    AGENT_OPERATIONS = "agent_operations"
    OPERATOR_WORKSPACE = "operator_workspace"
    INDIRA_WORKSPACE = "indira_workspace"
    DYON_WORKSPACE = "dyon_workspace"
    TRADING_DOMAIN = "trading_domain"
    MEMECOIN_DOMAIN = "memecoin_domain"
    SYSTEM_MAINTENANCE = "system_maintenance"


@dataclass
class CognitiveEvent:
    """Event within the cognitive environment."""

    entity_type: CognitiveEntityType
    entity_id: str
    event_type: str
    timestamp: datetime
    data: dict[str, Any] = field(default_factory=dict)
    workspace: WorkspaceType | None = None


@dataclass
class AgentActivity:
    """Real-time agent activity for observability."""

    agent_type: CognitiveEntityType
    agent_id: str
    current_goal: str
    current_task: str
    cognitive_process: str
    tools_in_use: list[str] = field(default_factory=list)
    memory_accesses: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # INDIRA-specific fields
    current_research: str | None = None
    current_trader_modeling: str | None = None
    current_strategy_work: str | None = None

    # DYON-specific fields
    current_repository_task: str | None = None
    current_mutation: str | None = None
    current_refactor: str | None = None
    current_build: str | None = None
    current_testing: str | None = None


@dataclass
class AgentAssignment:
    """Agent assignment/task management."""

    assignment_id: str
    agent_type: CognitiveEntityType
    agent_id: str
    title: str
    description: str
    status: str  # pending, in_progress, completed, blocked
    priority: str  # low, medium, high, critical
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


@dataclass
class AgentProject:
    """Agent project management."""

    project_id: str
    title: str
    description: str
    agent_type: CognitiveEntityType
    assigned_agents: list[str] = field(default_factory=list)
    status: str = "active"  # active, completed, archived
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


@dataclass
class AgentMemory:
    """Agent memory for cognitive process visualization."""

    agent_id: str
    memory_type: str  # short_term, long_term, episodic, semantic
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: dict[str, Any] = field(default_factory=dict)


class CognitiveOperatingEnvironment:
    """
    Core cognitive operating environment where agents live and work.

    This replaces the fragmented UI systems with a single cohesive environment where
    Operator, INDIRA, and DYON share unified workspaces and tools.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._active_entities: dict[str, CognitiveEntityType] = {}
        self._active_workspaces: dict[WorkspaceType, dict[str, Any]] = {}
        self._event_stream: list[CognitiveEvent] = []
        self._agent_activities: dict[str, AgentActivity] = {}
        self._subscribers: list[Callable[[CognitiveEvent], None]] = []

        # Agent Operations Center components
        self._assignments: dict[str, AgentAssignment] = {}
        self._projects: dict[str, AgentProject] = {}
        self._task_queue: list[AgentAssignment] = []
        self._agent_memories: list[AgentMemory] = []
        self._agent_timeline: list[CognitiveEvent] = []

    def register_entity(self, entity_id: str, entity_type: CognitiveEntityType) -> None:
        """Register an entity in the cognitive environment."""
        with self._lock:
            self._active_entities[entity_id] = entity_type
            self._emit_event(
                CognitiveEvent(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    event_type="ENTITY_REGISTERED",
                    timestamp=datetime.utcnow(),
                )
            )

    def activate_workspace(
        self, workspace_type: WorkspaceType, config: dict[str, Any] | None = None
    ) -> None:
        """Activate a workspace in the cognitive environment."""
        with self._lock:
            self._active_workspaces[workspace_type] = config or {}
            self._emit_event(
                CognitiveEvent(
                    entity_type=CognitiveEntityType.SYSTEM,
                    entity_id="environment",
                    event_type="WORKSPACE_ACTIVATED",
                    timestamp=datetime.utcnow(),
                    data={"workspace_type": workspace_type, "config": config},
                    workspace=workspace_type,
                )
            )

    def update_agent_activity(self, activity: AgentActivity) -> None:
        """Update real-time agent activity for observability."""
        with self._lock:
            self._agent_activities[activity.agent_id] = activity
            self._emit_event(
                CognitiveEvent(
                    entity_type=activity.agent_type,
                    entity_id=activity.agent_id,
                    event_type="AGENT_ACTIVITY_UPDATE",
                    timestamp=activity.timestamp,
                    data={
                        "current_goal": activity.current_goal,
                        "current_task": activity.current_task,
                        "cognitive_process": activity.cognitive_process,
                        "tools_in_use": activity.tools_in_use,
                        "memory_accesses": activity.memory_accesses,
                    },
                )
            )

    def get_agent_activities(self) -> dict[str, AgentActivity]:
        """Get all current agent activities for observability."""
        with self._lock:
            return dict(self._agent_activities)

    def subscribe_to_events(self, handler: Callable[[CognitiveEvent], None]) -> None:
        """Subscribe to cognitive environment events."""
        with self._lock:
            self._subscribers.append(handler)

    def _emit_event(self, event: CognitiveEvent) -> None:
        """Emit an event to all subscribers."""
        with self._lock:
            self._event_stream.append(event)
            # Keep last 1000 events
            if len(self._event_stream) > 1000:
                self._event_stream = self._event_stream[-1000:]

        # Notify subscribers outside lock
        for handler in self._subscribers:
            try:
                handler(event)
            except Exception:
                pass  # Don't let subscriber errors break the environment

    def get_environment_state(self) -> dict[str, Any]:
        """Get current cognitive environment state."""
        with self._lock:
            return {
                "active_entities": dict(self._active_entities),
                "active_workspaces": {
                    ws.name: config for ws, config in self._active_workspaces.items()
                },
                "agent_count": len(self._agent_activities),
                "workspace_count": len(self._active_workspaces),
                "recent_events": len(self._event_stream),
                "assignments": len(self._assignments),
                "projects": len(self._projects),
                "task_queue_size": len(self._task_queue),
                "memories": len(self._agent_memories),
            }

    # Agent Operations Center Methods

    def create_assignment(self, assignment: AgentAssignment) -> None:
        """Create a new agent assignment."""
        with self._lock:
            self._assignments[assignment.assignment_id] = assignment
            self._task_queue.append(assignment)
            self._emit_event(
                CognitiveEvent(
                    entity_type=assignment.agent_type,
                    entity_id=assignment.agent_id,
                    event_type="ASSIGNMENT_CREATED",
                    timestamp=datetime.utcnow(),
                    data={
                        "assignment_id": assignment.assignment_id,
                        "title": assignment.title,
                        "priority": assignment.priority,
                    },
                )
            )

    def complete_assignment(self, assignment_id: str) -> None:
        """Mark an assignment as completed."""
        with self._lock:
            if assignment_id in self._assignments:
                assignment = self._assignments[assignment_id]
                assignment.status = "completed"
                assignment.completed_at = datetime.utcnow()
                if assignment in self._task_queue:
                    self._task_queue.remove(assignment)
                self._emit_event(
                    CognitiveEvent(
                        entity_type=assignment.agent_type,
                        entity_id=assignment.agent_id,
                        event_type="ASSIGNMENT_COMPLETED",
                        timestamp=datetime.utcnow(),
                        data={"assignment_id": assignment_id},
                    )
                )

    def create_project(self, project: AgentProject) -> None:
        """Create a new agent project."""
        with self._lock:
            self._projects[project.project_id] = project
            self._emit_event(
                CognitiveEvent(
                    entity_type=project.agent_type,
                    entity_id=project.project_id,
                    event_type="PROJECT_CREATED",
                    timestamp=datetime.utcnow(),
                    data={
                        "project_id": project.project_id,
                        "title": project.title,
                        "assigned_agents": project.assigned_agents,
                    },
                )
            )

    def add_agent_memory(self, memory: AgentMemory) -> None:
        """Add a memory entry to agent's cognitive timeline."""
        with self._lock:
            self._agent_memories.append(memory)
            self._agent_timeline.append(
                CognitiveEvent(
                    entity_type=(
                        CognitiveEntityType.INDIRA
                        if "indira" in memory.agent_id.lower()
                        else CognitiveEntityType.DYON
                    ),
                    entity_id=memory.agent_id,
                    event_type="MEMORY_ACCESS",
                    timestamp=memory.timestamp,
                    data={
                        "memory_type": memory.memory_type,
                        "content": memory.content[:100],  # Truncate for event data
                        "context": memory.context,
                    },
                )
            )
            # Keep last 1000 memories
            if len(self._agent_memories) > 1000:
                self._agent_memories = self._agent_memories[-1000:]

    def get_assignments(
        self, agent_type: CognitiveEntityType | None = None
    ) -> list[AgentAssignment]:
        """Get assignments, optionally filtered by agent type."""
        with self._lock:
            assignments = list(self._assignments.values())
            if agent_type:
                assignments = [a for a in assignments if a.agent_type == agent_type]
            return assignments

    def get_projects(self, agent_type: CognitiveEntityType | None = None) -> list[AgentProject]:
        """Get projects, optionally filtered by agent type."""
        with self._lock:
            projects = list(self._projects.values())
            if agent_type:
                projects = [p for p in projects if p.agent_type == agent_type]
            return projects

    def get_task_queue(self) -> list[AgentAssignment]:
        """Get current task queue."""
        with self._lock:
            return list(self._task_queue)

    def get_agent_memories(self, agent_id: str | None = None) -> list[AgentMemory]:
        """Get agent memories, optionally filtered by agent ID."""
        with self._lock:
            memories = list(self._agent_memories)
            if agent_id:
                memories = [m for m in memories if m.agent_id == agent_id]
            return memories

    def get_agent_timeline(
        self, agent_id: str | None = None, limit: int = 50
    ) -> list[CognitiveEvent]:
        """Get agent timeline events, optionally filtered by agent ID."""
        with self._lock:
            events = list(self._agent_timeline)
            if agent_id:
                events = [e for e in events if e.entity_id == agent_id]
            return events[-limit:]


_environment: CognitiveOperatingEnvironment | None = None
_env_lock = threading.Lock()


def get_cognitive_environment() -> CognitiveOperatingEnvironment:
    """Get the singleton cognitive operating environment."""
    global _environment
    if _environment is None:
        with _env_lock:
            if _environment is None:
                _environment = CognitiveOperatingEnvironment()
    return _environment
