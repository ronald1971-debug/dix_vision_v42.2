"""Macro structure — economic and macro understanding."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class MacroStructure:
    """Knowledge about macro economic environment.

    Captures:
        - Economic regime (expansion, contraction, inflation, deflation)
        - Sentiment indicators
        - Capital flows
        - Policy environment
    """

    regime: str = "unknown"  # "expansion", "contraction", "inflation", "deflation"
    sentiment_score: float = 0.0  # -1 to 1
    capital_flow_direction: str = "neutral"  # "inflow", "outflow", "neutral"
    policy_stance: str = "neutral"  # "accommodative", "tight", "neutral"
    risk_appetite: str = "moderate"  # "low", "moderate", "high"
    macro_indicators: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0


class MacroStructureBuilder:
    """Builds macro understanding from economic data."""

    def __init__(self) -> None:
        self._structure: MacroStructure | None = None

    def update(
        self,
        regime: str | None = None,
        sentiment_score: float | None = None,
        **kwargs: Any,
    ) -> MacroStructure:
        existing = self._structure

        structure = MacroStructure(
            regime=regime or (existing.regime if existing else "unknown"),
            sentiment_score=(
                sentiment_score
                if sentiment_score is not None
                else (existing.sentiment_score if existing else 0.0)
            ),
            **kwargs,
        )
        self._structure = structure
        return structure

    def get(self) -> MacroStructure | None:
        return self._structure