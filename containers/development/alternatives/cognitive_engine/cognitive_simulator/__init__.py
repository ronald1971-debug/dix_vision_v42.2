"""Cognitive Simulator - scenario reasoning engine.

Before strategy deployment, INDIRA can ask: What happens if...

Examples:
- Fed surprise
- Exchange failure
- Liquidity collapse
- Volatility explosion
"""

from cognitive_engine.cognitive_simulator.engine import CognitiveSimulator
from cognitive_engine.cognitive_simulator.result import RiskLevel, SimulationResult
from cognitive_engine.cognitive_simulator.scenario import Scenario, ScenarioType

__all__ = [
    "CognitiveSimulator",
    "RiskLevel",
    "Scenario",
    "ScenarioType",
    "SimulationResult",
]
