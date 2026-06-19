"""
sensory
DIX VISION v42.2 — Sensory System

Complete sensory array implementation including market data sensors,
news sensors, social sentiment sensors, macro economic sensors, on-chain
data sensors, and multi-sensor fusion.
"""

from sensory.orchestrator import (
    SensorData,
    SensorHealth,
    SensoryOrchestrator,
    get_sensory_orchestrator,
)

__all__ = [
    "SensorData",
    "SensorHealth",
    "SensoryOrchestrator",
    "get_sensory_orchestrator",
]