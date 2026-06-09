"""
mission_system
DIX VISION v42.2 — Mission System

Production-grade mission capabilities including mission planning,
mission execution, mission monitoring, objective tracking, resource allocation,
and success evaluation.
"""

from mission_system.orchestrator import (
    Mission,
    MissionSystemOrchestrator,
    get_mission_system_orchestrator,
)

__all__ = [
    "Mission",
    "MissionSystemOrchestrator",
    "get_mission_system_orchestrator",
]