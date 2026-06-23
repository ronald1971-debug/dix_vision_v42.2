"""Narrative - defines market narratives."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NarrativeStage(Enum):
    """Stages of a market narrative lifecycle."""

    EMERGING = "emerging"
    DEVELOPING = "developing"
    DOMINANT = "dominant"
    DECLINING = "declining"
    EXHAUSTED = "exhausted"


@dataclass
class Narrative:
    """A market narrative that drives price action."""

    narrative_id: str = field(default_factory=lambda: f"narrative_{time.time_ns()}")
    name: str = ""
    description: str = ""
    stage: NarrativeStage = NarrativeStage.EMERGING
    confidence: float = 0.5
    sentiment: float = 0.0  # -1 to 1
    affected_assets: tuple[str, ...] = ()
    key_themes: tuple[str, ...] = ()
    created_at: int = field(default_factory=lambda: time.time_ns())
    last_updated: int = field(default_factory=lambda: time.time_ns())
    evidence: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def advance_stage(self) -> None:
        """Advance narrative to next stage."""
        order = [
            NarrativeStage.EMERGING,
            NarrativeStage.DEVELOPING,
            NarrativeStage.DOMINANT,
            NarrativeStage.DECLINING,
            NarrativeStage.EXHAUSTED,
        ]
        current_idx = order.index(self.stage)
        if current_idx < len(order) - 1:
            self.stage = order[current_idx + 1]
            self.last_updated = time.time_ns()

    def update_evidence(self, evidence: str) -> None:
        """Add evidence supporting the narrative."""
        self.evidence = (*self.evidence, evidence)
        self.last_updated = time.time_ns()
