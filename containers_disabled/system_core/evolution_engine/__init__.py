"""
evolution_engine
DIX VISION v42.2 — Evolution Engine

Production-grade evolution capabilities including strategy evolution,
parameter tuning, adaptation, selection, and fitness evaluation.
"""

# New autonomous capabilities
from evolution_engine.autonomous_engine import (
    AutonomousEvolutionEngine,
    AutonomousEvolutionResult,
    AutonomyDecision,
    AutonomyLevel,
    AutonomyScope,
    get_autonomous_evolution_engine,
)
from evolution_engine.orchestrator import (
    EvolutionOperation,
    EvolutionOrchestrator,
    EvolutionState,
    get_evolution_orchestrator,
)

__all__ = [
    # Original orchestrator
    "EvolutionOperation",
    "EvolutionState",
    "EvolutionOrchestrator",
    "get_evolution_orchestrator",
    # Autonomous capabilities
    "AutonomousEvolutionEngine",
    "get_autonomous_evolution_engine",
    "AutonomyLevel",
    "AutonomyScope",
    "AutonomyDecision",
    "AutonomousEvolutionResult",
]
