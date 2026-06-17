"""Intent Alignment - aligns engines with objectives."""

from __future__ import annotations

from typing import Any

from cognitive_engine.identity_layer.identity import Identity
from cognitive_engine.operator_intent.intent import IntentPriority, OperatorIntent


class IntentAlignment:
    """Aligns cognitive engines with operator objectives.

    When operator sets:
    - "Improve trader modeling"
    - "Improve execution quality"

    Engines align their behavior accordingly.
    """

    def __init__(self, identity: Identity | None = None) -> None:
        self._identity = identity or Identity()
        self._intents: list[OperatorIntent] = []
        self._alignment_scores: dict[str, float] = {}

    def register_intent(self, intent: OperatorIntent) -> None:
        """Register an operator intent."""
        self._intents.append(intent)

    def get_active_intents(self) -> list[OperatorIntent]:
        """Get active intents."""
        return [i for i in self._intents if i.active]

    def get_intents_by_domain(self, domain: str) -> list[OperatorIntent]:
        """Get intents for a domain."""
        return [i for i in self._intents if i.domain == domain and i.active]

    def get_intents_by_priority(self, priority: IntentPriority) -> list[OperatorIntent]:
        """Get intents with specific priority."""
        return [i for i in self._intents if i.priority == priority and i.active]

    def compute_alignment(self, domain: str, action: Any) -> float:
        """Compute alignment score for a domain/action against intents."""
        relevant_intents = [i for i in self.get_active_intents() if i.domain in (domain, "any")]

        if not relevant_intents:
            return 1.0

        total = sum(self._intent_alignment(i, action) for i in relevant_intents)
        return total / len(relevant_intents)

    def _intent_alignment(self, intent: OperatorIntent, action: Any) -> float:
        """Compute alignment for a single intent."""
        cached = self._alignment_scores.get(intent.intent_id)
        if cached is not None:
            return cached

        score = intent.progress  # Base alignment on progress
        self._alignment_scores[intent.intent_id] = score
        return score

    def get_critical_intents(self) -> list[OperatorIntent]:
        """Get critical priority intents."""
        return self.get_intents_by_priority(IntentPriority.CRITICAL)

    def is_aligned(self, domain: str, min_score: float = 0.7) -> bool:
        """Check if domain is aligned with intents."""
        return self.compute_alignment(domain, None) >= min_score