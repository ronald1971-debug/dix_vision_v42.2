"""Cognitive Digital Twin.

Simulates DIXVISION itself before touching production.

(Item 41 — cognitive operating system roadmap)
"""

from cognitive_engine.digital_twin.digital_twin import (
    CognitiveDigitalTwin,
    SimulationResult,
    get_digital_twin,
)

__all__ = [
    "CognitiveDigitalTwin",
    "SimulationResult",
    "get_digital_twin",
]
