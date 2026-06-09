"""
world_model
DIX VISION v42.2 — World-Model

Production-grade world modeling capabilities including market representation,
agent modeling, environment modeling, causal structure learning, dynamics modeling,
and prediction systems.
"""

from world_model.orchestrator import (
    WorldModelState,
    WorldModelOrchestrator,
    get_world_model_orchestrator,
)

__all__ = [
    "WorldModelState",
    "WorldModelOrchestrator",
    "get_world_model_orchestrator",
]