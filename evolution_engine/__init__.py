"""
evolution_engine
DIX VISION v42.2 — Evolution Engine

Production-grade evolution capabilities including strategy evolution,
parameter tuning, adaptation, selection, and fitness evaluation.
"""

from evolution_engine.orchestrator import (
    EvolutionOperation,
    EvolutionState,
    EvolutionOrchestrator,
    get_evolution_orchestrator,
)

__all__ = [
    "EvolutionOperation",
    "EvolutionState",
    "EvolutionOrchestrator",
    "get_evolution_orchestrator",
]