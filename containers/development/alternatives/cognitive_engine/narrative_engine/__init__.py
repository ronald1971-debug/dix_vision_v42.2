"""Narrative Engine - maintains market narratives.

Markets often move because of stories, not signals.

Examples:
- AI narrative
- Energy narrative
- Election narrative
- Risk-off narrative
"""

from cognitive_engine.narrative_engine.engine import NarrativeEngine
from cognitive_engine.narrative_engine.narrative import Narrative, NarrativeStage

__all__ = [
    "Narrative",
    "NarrativeEngine",
    "NarrativeStage",
]