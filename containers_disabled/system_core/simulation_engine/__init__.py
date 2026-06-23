"""
simulation_engine
DIX VISION v42.2 — Simulation Engine

Production-grade simulation capabilities including market simulation,
strategy simulation, scenario simulation, Monte Carlo simulation, agent-based
modeling, and stress testing.
"""

from simulation_engine.orchestrator import (
    SimulationOperation,
    SimulationOrchestrator,
    get_simulation_orchestrator,
)

__all__ = [
    "SimulationOperation",
    "SimulationOrchestrator",
    "get_simulation_orchestrator",
]
