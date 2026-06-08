"""State Synchronization – keeps dashboard in sync with runtime.

Dashboard reflects actual runtime state, never cached/stale data.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from runtime.observability import ObservabilityHub


@dataclass
class DashboardState:
    """Serializable dashboard state for the frontend."""
    connected: bool = False
    last_sync: float = 0.0
    belief_count: int = 0
    hypothesis_count: int = 0
    active_hazards: int = 0
    governance_stage: str = "simulation"
    kill_switch_active: bool = False
    total_trades: int = 0
    total_pnl: float = 0.0
    system_health: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "connected": self.connected,
                "last_sync": self.last_sync,
                "belief_count": self.belief_count,
                "hypothesis_count": self.hypothesis_count,
                "active_hazards": self.active_hazards,
                "governance_stage": self.governance_stage,
                "kill_switch_active": self.kill_switch_active,
                "total_trades": self.total_trades,
                "total_pnl": self.total_pnl,
                "system_health": self.system_health,
            }
        )


class StateSync:
    """Synchronizes runtime state to the dashboard."""

    def __init__(self, hub: ObservabilityHub) -> None:
        self._hub = hub
        self._state = DashboardState()
        self._sync_count = 0

    def sync(self) -> DashboardState:
        snapshot = self._hub.get_latest()
        if snapshot:
            self._state.connected = True
            self._state.last_sync = time.time()
            self._state.belief_count = len(snapshot.beliefs)
            self._state.hypothesis_count = len(snapshot.hypotheses)
            self._state.active_hazards = len(snapshot.hazards)
            self._state.system_health = snapshot.system_health
        self._sync_count += 1
        return self._state

    def get_state(self) -> DashboardState:
        return self._state

    @property
    def sync_count(self) -> int:
        return self._sync_count
