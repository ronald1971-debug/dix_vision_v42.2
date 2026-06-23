"""
self_model.mental_state_model
DIX VISION v42.2 — Production-Grade Mental State Model

Mental state representation with cognitive state tracking, emotional state modeling,
and production-ready mental state management.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import List

from system.time_source import now

logger = logging.getLogger(__name__)


class CognitiveState(Enum):
    """Cognitive states."""

    FOCUSED = "focused"
    DIVERGENT = "divergent"
    REFLECTIVE = "reflective"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"


class EmotionalState(Enum):
    """Emotional states."""

    CALM = "calm"
    CURIOUS = "curious"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    EXCITED = "excited"


@dataclass
class MentalStateSnapshot:
    """Mental state at a point in time."""

    snapshot_id: str
    cognitive_state: CognitiveState
    emotional_state: EmotionalState
    confidence: float = 0.5
    arousal: float = 0.5
    timestamp: str = ""


class ProductionMentalStateModel:
    """Production-grade mental state model."""

    def __init__(self) -> None:
        self._mental_states: List[MentalStateSnapshot] = []
        self._current_state = MentalStateSnapshot(
            snapshot_id=f"initial_{now().sequence}",
            cognitive_state=CognitiveState.ANALYTICAL,
            emotional_state=EmotionalState.CALM,
            timestamp=now().utc_time.isoformat(),
        )

    def start(self) -> bool:
        logger.info("[MENTAL_STATE] Production mental state model started")
        return True

    def stop(self) -> bool:
        logger.info("[MENTAL_STATE] Production mental state model stopped")
        return True

    def update_mental_state(
        self, cognitive_state: CognitiveState, emotional_state: EmotionalState
    ) -> MentalStateSnapshot:
        """Update mental state."""
        snapshot = MentalStateSnapshot(
            snapshot_id=f"mental_{now().sequence}",
            cognitive_state=cognitive_state,
            emotional_state=emotional_state,
            confidence=0.7,
            arousal=0.6,
            timestamp=now().utc_time.isoformat(),
        )
        self._mental_states.append(snapshot)
        self._current_state = snapshot
        return snapshot


def get_production_mental_state_model() -> ProductionMentalStateModel:
    """Get the singleton production mental state model instance."""
    if not hasattr(get_production_mental_state_model, "_instance"):
        get_production_mental_state_model._instance = ProductionMentalStateModel()
    return get_production_mental_state_model._instance
