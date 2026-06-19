"""Cognitive Time System.

Maintains past beliefs, current beliefs, and projected beliefs.

(Cognitive Time — Item 30 from the cognitive operating system roadmap)
"""

from cognitive_engine.cognitive_time.cognitive_time import (
    BeliefRecord,
    CognitiveTime,
    get_cognitive_time,
)

__all__ = [
    "BeliefRecord",
    "CognitiveTime",
    "get_cognitive_time",
]
