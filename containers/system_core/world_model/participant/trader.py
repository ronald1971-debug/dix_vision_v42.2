"""Participant structure — understanding of trader types and behavioral clusters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class TraderParticipant:
    """A participant in the market with behavioral characteristics."""

    trader_id: str
    archetype: str = "unknown"  # Scalper, Momentum, MeanReversion, etc.
    influence_score: float = 0.0  # Market impact potential
    active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ParticipantStructure:
    """Knowledge about market participants.

    Captures:
        - Trader types and archetypes
        - Influence clusters
        - Behavior patterns
        - Participation intensity
    """

    symbol: str
    traders: tuple[TraderParticipant, ...] = ()
    clusters: dict[str, list[str]] = field(default_factory=dict)
    participation_rate: float = 0.0
    confidence: float = 0.0

    @property
    def trader_count(self) -> int:
        return len([t for t in self.traders if t.active])


class ParticipantStructureBuilder:
    """Builds participant understanding from flow analysis."""

    def __init__(self) -> None:
        self._structures: dict[str, ParticipantStructure] = {}

    def update(
        self,
        symbol: str,
        traders: tuple[TraderParticipant, ...] | None = None,
        **kwargs: Any,
    ) -> ParticipantStructure:
        existing = self._structures.get(symbol)
        all_traders = list(existing.traders) if existing else []
        if traders:
            all_traders.extend(traders)

        structure = ParticipantStructure(
            symbol=symbol,
            traders=tuple(all_traders[-100:]),
            **kwargs,
        )
        self._structures[symbol] = structure
        return structure

    def get(self, symbol: str) -> ParticipantStructure | None:
        return self._structures.get(symbol)