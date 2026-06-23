"""Narrative Engine - tracks and reasons over market narratives."""

from __future__ import annotations

from cognitive_engine.narrative_engine.narrative import Narrative, NarrativeStage


class NarrativeEngine:
    """Maintains market_narratives/ and reasons over them.

    Narratives often move markets more than signals.
    """

    def __init__(self) -> None:
        self._narratives: dict[str, Narrative] = {}
        self._asset_index: dict[str, list[str]] = {}

    def register(self, name: str, description: str, assets: tuple[str, ...] = ()) -> Narrative:
        """Register a new narrative."""
        narrative = Narrative(
            name=name,
            description=description,
            affected_assets=assets,
            key_themes=(name.lower().replace(" ", "_"),),
        )
        self._narratives[narrative.narrative_id] = narrative

        for asset in assets:
            self._asset_index.setdefault(asset, []).append(narrative.narrative_id)

        return narrative

    def get(self, narrative_id: str) -> Narrative | None:
        """Get a narrative by ID."""
        return self._narratives.get(narrative_id)

    def narratives_for_asset(self, asset: str) -> list[Narrative]:
        """Get narratives affecting an asset."""
        ids = self._asset_index.get(asset, [])
        return [self._narratives[i] for i in ids if i in self._narratives]

    def dominant(self) -> list[Narrative]:
        """Get dominant narratives."""
        return [n for n in self._narratives.values() if n.stage == NarrativeStage.DOMINANT]

    def emerging(self) -> list[Narrative]:
        """Get emerging narratives."""
        return [n for n in self._narratives.values() if n.stage == NarrativeStage.EMERGING]

    def update_sentiment(
        self, narrative_id: str, sentiment: float, evidence: str | None = None
    ) -> Narrative | None:
        """Update narrative sentiment."""
        narrative = self._narratives.get(narrative_id)
        if narrative:
            narrative.sentiment = max(-1.0, min(1.0, sentiment))
            if evidence:
                narrative.update_evidence(evidence)
            return narrative
        return None

    def get_all(self) -> list[Narrative]:
        """Get all narratives."""
        return list(self._narratives.values())

    def narrative_confidence(self, narrative_id: str) -> float:
        """Get confidence for a narrative."""
        narrative = self._narratives.get(narrative_id)
        return narrative.confidence if narrative else 0.0
