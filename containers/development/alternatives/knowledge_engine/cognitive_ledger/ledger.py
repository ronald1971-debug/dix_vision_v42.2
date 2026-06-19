"""Cognitive ledger — records cognitive events for replayability.

Records:
    - Belief Created
    - Belief Changed  
    - Strategy Proposed
    - Trader Reclassified
    - Confidence Increased/Decreased
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class CognitiveEventType(StrEnum):
    BELIEF_CREATED = "BELIEF_CREATED"
    BELIEF_CHANGED = "BELIEF_CHANGED"
    STRATEGY_PROPOSED = "STRATEGY_PROPOSED"
    TRADER_RECLASSIFIED = "TRADER_RECLASSIFIED"
    CONFIDENCE_INCREASED = "CONFIDENCE_INCREASED"
    CONFIDENCE_DECREASED = "CONFIDENCE_DECREASED"
    KNOWLEDGE_ACQUIRED = "KNOWLEDGE_ACQUIRED"
    REGIME_SHIFT = "REGIME_SHIFT"
    # Layer 44 — Knowledge Lifecycle events
    KNOWLEDGE_BIRTH = "KNOWLEDGE_BIRTH"
    KNOWLEDGE_GROWTH = "KNOWLEDGE_GROWTH"
    KNOWLEDGE_VALIDATION = "KNOWLEDGE_VALIDATION"
    KNOWLEDGE_CHALLENGE = "KNOWLEDGE_CHALLENGE"
    KNOWLEDGE_DECAY = "KNOWLEDGE_DECAY"
    KNOWLEDGE_RETIREMENT = "KNOWLEDGE_RETIREMENT"


@dataclass(frozen=True, slots=True)
class CognitiveEvent:
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    ts_ns: int = field(default_factory=lambda: time.time_ns())
    event_type: CognitiveEventType = CognitiveEventType.BELIEF_CREATED
    subject: str = ""
    old_value: Any = None
    new_value: Any = None
    confidence_delta: float = 0.0
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class CognitiveLedger:
    """Persistent record of cognitive state changes.

    All cognitive events are recorded here for:
        - Replay and auditing
        - Learning from past decisions
        - Cognitive integrity validation
    """

    def __init__(self) -> None:
        self._events: list[CognitiveEvent] = []
        self._index_by_subject: dict[str, list[str]] = {}

    def record(self, event: CognitiveEvent) -> None:
        self._events.append(event)
        if event.subject not in self._index_by_subject:
            self._index_by_subject[event.subject] = []
        self._index_by_subject[event.subject].append(event.event_id)

    def query(self, event_type: CognitiveEventType | None = None,
              subject: str | None = None) -> list[CognitiveEvent]:
        result = self._events
        if event_type:
            result = [e for e in result if e.event_type == event_type]
        if subject:
            event_ids = self._index_by_subject.get(subject, [])
            result = [e for e in result if e.event_id in event_ids]
        return result

    def get_timeline(self, subject: str) -> list[CognitiveEvent]:
        return [e for e in self._events if e.subject == subject]

    def export_timeline(self, subject: str) -> list[dict[str, Any]]:
        return [
            {
                "event_id": e.event_id,
                "ts_ns": e.ts_ns,
                "event_type": e.event_type.value,
                "subject": e.subject,
                "old_value": e.old_value,
                "new_value": e.new_value,
                "confidence_delta": e.confidence_delta,
                "source": e.source,
            }
            for e in self.get_timeline(subject)
        ]

    def record_lifecycle_event(
        self,
        phase: str,
        knowledge_id: str,
        confidence_delta: float = 0.0,
        source: str = "knowledge_lifecycle",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a knowledge lifecycle event to the cognitive ledger."""
        phase_to_event = {
            "birth": CognitiveEventType.KNOWLEDGE_BIRTH,
            "growth": CognitiveEventType.KNOWLEDGE_GROWTH,
            "validation": CognitiveEventType.KNOWLEDGE_VALIDATION,
            "challenge": CognitiveEventType.KNOWLEDGE_CHALLENGE,
            "decay": CognitiveEventType.KNOWLEDGE_DECAY,
            "retirement": CognitiveEventType.KNOWLEDGE_RETIREMENT,
        }
        event_type = phase_to_event.get(phase.lower(), CognitiveEventType.KNOWLEDGE_BIRTH)
        event = CognitiveEvent(
            event_type=event_type,
            subject=knowledge_id,
            confidence_delta=confidence_delta,
            source=source,
            metadata=metadata or {},
        )
        self.record(event)

    @property
    def event_count(self) -> int:
        return len(self._events)

    def get_knowledge_timeline(self, knowledge_id: str) -> list[CognitiveEvent]:
        """Get all lifecycle events for a specific knowledge item."""
        return [
            e for e in self._events
            if e.event_type.name.startswith("KNOWLEDGE_") and e.subject == knowledge_id
        ]