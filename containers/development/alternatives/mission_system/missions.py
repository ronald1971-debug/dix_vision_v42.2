"""Mission system — INDIRA works toward objectives.

Right now engines operate.

Future:
    Mission Layer

Examples:
    - Find profitable traders
    - Find hidden alpha
    - Understand market manipulation
    - Improve execution quality

INDIRA works toward missions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class MissionStatus(StrEnum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


class MissionPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Mission:
    """A cognitive mission for INDIRA to pursue."""

    mission_id: str
    title: str
    description: str
    status: MissionStatus = MissionStatus.PROPOSED
    priority: MissionPriority = MissionPriority.MEDIUM
    progress: float = 0.0  # 0.0 to 1.0
    target_completion: int = 0  # nanosecond timestamp
    results: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)


class MissionSystem:
    """Manages cognitive missions for INDIRA.

    Missions drive:
        - Trader discovery
        - Alpha search
        - Manipulation detection
        - Execution optimization
    """

    def __init__(self) -> None:
        self._missions: dict[str, Mission] = {}
        self._active_missions: list[str] = []

    def create_mission(self, mission_id: str, title: str, description: str,
                       priority: MissionPriority = MissionPriority.MEDIUM) -> Mission:
        mission = Mission(
            mission_id=mission_id,
            title=title,
            description=description,
            priority=priority,
        )
        self._missions[mission_id] = mission
        self._active_missions.append(mission_id)
        return mission

    def get_mission(self, mission_id: str) -> Mission | None:
        return self._missions.get(mission_id)

    def update_progress(self, mission_id: str, progress: float,
                      result: str | None = None, value: float = 0.0) -> bool:
        mission = self._missions.get(mission_id)
        if mission is None:
            return False
        mission.progress = max(0.0, min(1.0, progress))
        if result:
            mission.results[result] = value
        if progress >= 1.0:
            mission.status = MissionStatus.COMPLETED
            self._active_missions = [m for m in self._active_missions if m != mission_id]
        return True

    def active_missions(self) -> tuple[Mission, ...]:
        return tuple(self._missions[mid] for mid in self._active_missions if mid in self._missions)


__all__ = [
    "Mission",
    "MissionPriority",
    "MissionStatus",
    "MissionSystem",
]