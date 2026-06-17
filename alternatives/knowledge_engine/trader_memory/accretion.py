"""Knowledge accretion — how observations become persistent knowledge.

Knowledge flows from observation → validation → memory.
"""

from __future__ import annotations

from knowledge_engine.trader_memory.store import TraderKnowledgeStore, TraderObservation


class KnowledgeAccretor:
    """Accumulates observations into persistent trader knowledge.

    The accretion engine:
        1. Receives validated trader observations
        2. Updates trader memory records
        3. Adjusts confidence based on prediction accuracy
        4. Maintains regime-specific performance tracking
    """

    def __init__(self, store: TraderKnowledgeStore | None = None) -> None:
        self._store = store or TraderKnowledgeStore()
        self._observation_count = 0

    def observe(self, obs: TraderObservation) -> None:
        self._store.record_observation(obs)
        self._observation_count += 1

    def get_store(self) -> TraderKnowledgeStore:
        return self._store

    @property
    def observation_count(self) -> int:
        return self._observation_count