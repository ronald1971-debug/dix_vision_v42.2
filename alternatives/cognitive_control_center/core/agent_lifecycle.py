"""
cognitive_control_center.core.agent_lifecycle
Agent Lifecycle Management - Manage agent lifecycle within cognitive operating environment.

This module manages the lifecycle of agents (INDIRA, DYON) within the cognitive operating
environment, from registration and activation to deactivation and cleanup.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Callable

from cognitive_control_center.core.operating_environment import (
    CognitiveEntityType,
    get_cognitive_environment,
)
from cognitive_control_center.core.workspace_manager import (
    WorkspaceType,
    get_workspace_manager,
)


class AgentState(StrEnum):
    """States in the agent lifecycle."""
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    DEACTIVATING = "deactivating"
    INACTIVE = "inactive"
    ERROR = "error"


@dataclass
class AgentLifecycleEvent:
    """Event in agent lifecycle."""
    agent_id: str
    agent_type: CognitiveEntityType
    from_state: AgentState | None
    to_state: AgentState
    timestamp: datetime
    reason: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRegistration:
    """Agent registration in the cognitive environment."""
    agent_id: str
    agent_type: CognitiveEntityType
    state: AgentState
    registered_at: datetime
    activated_at: datetime | None = None
    deactivated_at: datetime | None = None
    current_workspace: WorkspaceType | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentLifecycleManager:
    """
    Manage agent lifecycle within the cognitive operating environment.

    Handles registration, activation, deactivation, and state transitions for
    INDIRA and DYON agents.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._registrations: dict[str, AgentRegistration] = {}
        self._lifecycle_events: list[AgentLifecycleEvent] = []
        self._environment = get_cognitive_environment()
        self._workspace_manager = get_workspace_manager()
        self._state_change_subscribers: list[Callable[[AgentLifecycleEvent], None]] = []

    def register_agent(
        self,
        agent_id: str,
        agent_type: CognitiveEntityType,
        metadata: dict[str, Any] | None = None,
    ) -> AgentRegistration:
        """Register a new agent in the cognitive environment."""
        with self._lock:
            if agent_id in self._registrations:
                raise ValueError(f"Agent {agent_id} already registered")

            registration = AgentRegistration(
                agent_id=agent_id,
                agent_type=agent_type,
                state=AgentState.REGISTERED,
                registered_at=datetime.utcnow(),
                metadata=metadata or {},
            )

            self._registrations[agent_id] = registration
            self._environment.register_entity(agent_id, agent_type)
            self._record_lifecycle_event(
                AgentLifecycleEvent(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    from_state=None,
                    to_state=AgentState.REGISTERED,
                    timestamp=datetime.utcnow(),
                    reason="agent_registered",
                )
            )

            return registration

    def activate_agent(
        self,
        agent_id: str,
        initial_workspace: WorkspaceType,
        reason: str = "",
    ) -> AgentLifecycleEvent:
        """Activate an agent and move it to its initial workspace."""
        with self._lock:
            if agent_id not in self._registrations:
                raise ValueError(f"Agent {agent_id} not registered")

            registration = self._registrations[agent_id]

            # Transition state
            event = self._transition_state(
                agent_id,
                AgentState.ACTIVE,
                reason=reason or "agent_activation",
            )

            # Move to workspace
            self._workspace_manager.transition_entity(
                agent_id,
                initial_workspace,
                reason=reason or "initial_workspace",
            )
            registration.current_workspace = initial_workspace
            registration.activated_at = datetime.utcnow()

            return event

    def deactivate_agent(self, agent_id: str, reason: str = "") -> AgentLifecycleEvent:
        """Deactivate an agent."""
        with self._lock:
            if agent_id not in self._registrations:
                raise ValueError(f"Agent {agent_id} not registered")

            registration = self._registrations[agent_id]

            # Transition state
            event = self._transition_state(
                agent_id,
                AgentState.INACTIVE,
                reason=reason or "agent_deactivation",
            )

            # Remove from workspace
            registration.current_workspace = None
            registration.deactivated_at = datetime.utcnow()

            return event

    def pause_agent(self, agent_id: str, reason: str = "") -> AgentLifecycleEvent:
        """Pause an agent temporarily."""
        with self._lock:
            return self._transition_state(
                agent_id,
                AgentState.PAUSED,
                reason=reason or "agent_paused",
            )

    def resume_agent(self, agent_id: str, reason: str = "") -> AgentLifecycleEvent:
        """Resume a paused agent."""
        with self._lock:
            return self._transition_state(
                agent_id,
                AgentState.ACTIVE,
                reason=reason or "agent_resumed",
            )

    def report_agent_error(self, agent_id: str, error: str, data: dict[str, Any] | None = None) -> AgentLifecycleEvent:
        """Report an agent error and transition to error state."""
        with self._lock:
            return self._transition_state(
                agent_id,
                AgentState.ERROR,
                reason=error,
                data=data or {},
            )

    def _transition_state(
        self,
        agent_id: str,
        to_state: AgentState,
        reason: str = "",
        data: dict[str, Any] | None = None,
    ) -> AgentLifecycleEvent:
        """Internal method to transition agent state."""
        if agent_id not in self._registrations:
            raise ValueError(f"Agent {agent_id} not registered")

        registration = self._registrations[agent_id]
        from_state = registration.state
        registration.state = to_state

        event = AgentLifecycleEvent(
            agent_id=agent_id,
            agent_type=registration.agent_type,
            from_state=from_state,
            to_state=to_state,
            timestamp=datetime.utcnow(),
            reason=reason,
            data=data or {},
        )

        self._lifecycle_events.append(event)
        if len(self._lifecycle_events) > 1000:  # Keep last 1000 events
            self._lifecycle_events = self._lifecycle_events[-1000:]

        # Notify subscribers
        for subscriber in self._state_change_subscribers:
            try:
                subscriber(event)
            except Exception:
                pass

        return event

    def get_agent_registration(self, agent_id: str) -> AgentRegistration | None:
        """Get agent registration."""
        with self._lock:
            return self._registrations.get(agent_id)

    def get_all_registrations(self) -> dict[str, AgentRegistration]:
        """Get all agent registrations."""
        with self._lock:
            return dict(self._registrations)

    def get_active_agents(self) -> dict[str, AgentRegistration]:
        """Get all currently active agents."""
        with self._lock:
            return {
                aid: reg
                for aid, reg in self._registrations.items()
                if reg.state == AgentState.ACTIVE
            }

    def subscribe_to_state_changes(self, handler: Callable[[AgentLifecycleEvent], None]) -> None:
        """Subscribe to agent state change events."""
        with self._lock:
            self._state_change_subscribers.append(handler)

    def get_lifecycle_events(
        self,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[AgentLifecycleEvent]:
        """Get lifecycle events, optionally filtered by agent."""
        with self._lock:
            events = self._lifecycle_events
            if agent_id:
                events = [e for e in events if e.agent_id == agent_id]
            return list(events[-limit:])


_lifecycle_manager: AgentLifecycleManager | None = None
_lifecycle_lock = threading.Lock()


def get_agent_lifecycle_manager() -> AgentLifecycleManager:
    """Get the singleton agent lifecycle manager."""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        with _lifecycle_lock:
            if _lifecycle_manager is None:
                _lifecycle_manager = AgentLifecycleManager()
    return _lifecycle_manager