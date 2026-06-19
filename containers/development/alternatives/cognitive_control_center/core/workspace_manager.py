"""
cognitive_control_center.core.workspace_manager
Unified Workspace Manager - Replaces page-based navigation with workspace-based cognitive model.

This module implements the unified workspace model where Operator, INDIRA, and DYON
share workspaces rather than navigating between separate pages. This is fundamental to
the cognitive operating environment philosophy.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Callable
from datetime import datetime

from cognitive_control_center.core.operating_environment import (
    WorkspaceType,
    CognitiveEntityType,
    CognitiveEvent,
    get_cognitive_environment,
)


@dataclass
class Workspace:
    """A cognitive workspace shared by entities."""
    workspace_type: WorkspaceType
    name: str
    description: str
    active_entities: set[str] = field(default_factory=set)
    shared_tools: list[str] = field(default_factory=list)
    activity_log: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkspaceTransition:
    """Record of a workspace transition."""
    entity_id: str
    from_workspace: WorkspaceType | None
    to_workspace: WorkspaceType
    timestamp: datetime
    reason: str = ""


class UnifiedWorkspaceManager:
    """
    Manages unified workspaces for the cognitive operating environment.

    Replaces page-based navigation with workspace-based cognitive model where
    entities (Operator, INDIRA, DYON) move between workspaces rather than
    navigating to separate pages.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._workspaces: dict[WorkspaceType, Workspace] = {}
        self._entity_workspace: dict[str, WorkspaceType] = {}  # entity_id -> current workspace
        self._transition_log: list[WorkspaceTransition] = []
        self._environment = get_cognitive_environment()

        # Initialize default workspaces
        self._initialize_default_workspaces()

    def _initialize_default_workspaces(self) -> None:
        """Initialize the default cognitive workspaces."""
        default_workspaces = [
            Workspace(
                workspace_type=WorkspaceType.AGENT_OPERATIONS,
                name="Agent Operations Center",
                description="Central hub for observing and directing agent activities",
                shared_tools=["activity_feeds", "task_management", "cognitive_observability"],
            ),
            Workspace(
                workspace_type=WorkspaceType.OPERATOR_WORKSPACE,
                name="Operator Workspace",
                description="Primary workspace for operator activities and collaboration with agents",
                shared_tools=["desktop", "browser", "knowledge", "chat"],
            ),
            Workspace(
                workspace_type=WorkspaceType.INDIRA_WORKSPACE,
                name="INDIRA Trading Workspace",
                description="INDIRA's cognitive workspace for trading activities and learning",
                shared_tools=["market_analysis", "strategy_development", "risk_assessment", "learning"],
            ),
            Workspace(
                workspace_type=WorkspaceType.DYON_WORKSPACE,
                name="DYON System Workspace",
                description="DYON's cognitive workspace for system maintenance and hazard detection",
                shared_tools=["system_monitoring", "hazard_analysis", "automation", "learning"],
            ),
            Workspace(
                workspace_type=WorkspaceType.TRADING_DOMAIN,
                name="Trading Domain",
                description="General trading activities and market analysis",
                shared_tools=["market_data", "execution", "portfolio_management"],
            ),
            Workspace(
                workspace_type=WorkspaceType.MEMECOIN_DOMAIN,
                name="Memecoin Trading Domain",
                description="Specialized domain for memecoin trading activities (formerly dash_meme)",
                shared_tools=["dex_analysis", "token_sniping", "liquidity_provision"],
            ),
            Workspace(
                workspace_type=WorkspaceType.SYSTEM_MAINTENANCE,
                name="System Maintenance Domain",
                description="System maintenance, updates, and automation activities",
                shared_tools=["repository_management", "patch_management", "automation"],
            ),
        ]

        for workspace in default_workspaces:
            self._workspaces[workspace.workspace_type] = workspace
            self._environment.activate_workspace(workspace.workspace_type, {
                "name": workspace.name,
                "description": workspace.description,
                "shared_tools": workspace.shared_tools,
            })

    def transition_entity(
        self,
        entity_id: str,
        to_workspace: WorkspaceType,
        reason: str = "",
    ) -> WorkspaceTransition:
        """
        Transition an entity to a different workspace.

        This replaces page navigation with cognitive workspace transitions.
        """
        with self._lock:
            from_workspace = self._entity_workspace.get(entity_id)
            transition = WorkspaceTransition(
                entity_id=entity_id,
                from_workspace=from_workspace,
                to_workspace=to_workspace,
                timestamp=datetime.utcnow(),
                reason=reason,
            )

            # Update entity workspace mapping
            self._entity_workspace[entity_id] = to_workspace

            # Update workspace entity sets
            if from_workspace and from_workspace in self._workspaces:
                self._workspaces[from_workspace].active_entities.discard(entity_id)

            if to_workspace in self._workspaces:
                self._workspaces[to_workspace].active_entities.add(entity_id)
                self._workspaces[to_workspace].last_activity = datetime.utcnow()
                self._workspaces[to_workspace].activity_log.append({
                    "entity_id": entity_id,
                    "action": "joined",
                    "timestamp": datetime.utcnow().isoformat(),
                    "reason": reason,
                })

            # Log transition
            self._transition_log.append(transition)
            if len(self._transition_log) > 1000:  # Keep last 1000 transitions
                self._transition_log = self._transition_log[-1000:]

            return transition

    def get_entity_workspace(self, entity_id: str) -> WorkspaceType | None:
        """Get the current workspace for an entity."""
        with self._lock:
            return self._entity_workspace.get(entity_id)

    def get_workspace(self, workspace_type: WorkspaceType) -> Workspace | None:
        """Get a workspace by type."""
        with self._lock:
            return self._workspaces.get(workspace_type)

    def get_all_workspaces(self) -> dict[WorkspaceType, Workspace]:
        """Get all workspaces."""
        with self._lock:
            return dict(self._workspaces)

    def get_workspace_entities(self, workspace_type: WorkspaceType) -> set[str]:
        """Get all entities currently in a workspace."""
        with self._lock:
            workspace = self._workspaces.get(workspace_type)
            return set(workspace.active_entities) if workspace else set()

    def get_recent_transitions(self, limit: int = 50) -> list[WorkspaceTransition]:
        """Get recent workspace transitions."""
        with self._lock:
            return list(self._transition_log[-limit:])


_workspace_manager: UnifiedWorkspaceManager | None = None
_manager_lock = threading.Lock()


def get_workspace_manager() -> UnifiedWorkspaceManager:
    """Get the singleton unified workspace manager."""
    global _workspace_manager
    if _workspace_manager is None:
        with _manager_lock:
            if _workspace_manager is None:
                _workspace_manager = UnifiedWorkspaceManager()
    return _workspace_manager