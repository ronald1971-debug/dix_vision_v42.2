"""Regime structure — market regime understanding and transitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RegimeStructure:
    """Knowledge about market regimes and transitions.

    Captures:
        - Current regime
        - Transition probabilities
        - Regime characteristics
        - Duration tracking
    """

    symbol: str
    current_regime: str = "unknown"  # TREND_UP, TREND_DOWN, RANGE, VOL_SPIKE
    regime_confidence: float = 0.0
    transition_probs: dict[str, float] = field(default_factory=dict)  # next_regime -> probability
    expected_duration_seconds: float = 0.0
    regime_characteristics: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0


class RegimeStructureBuilder:
    """Builds regime understanding from market observations."""

    def __init__(self) -> None:
        self._structures: dict[str, RegimeStructure] = {}

    def update(
        self,
        symbol: str,
        regime: str,
        regime_confidence: float = 1.0,
        transition_probs: dict[str, float] | None = None,
        **kwargs: Any,
    ) -> RegimeStructure:
        existing = self._structures.get(symbol)

        structure = RegimeStructure(
            symbol=symbol,
            current_regime=regime,
            regime_confidence=regime_confidence,
            transition_probs=transition_probs or {},
            regime_characteristics={
                **(existing.regime_characteristics if existing else {}),
                "last_regime": existing.current_regime if existing else None,
            },
            **kwargs,
        )
        self._structures[symbol] = structure
        return structure

    def get(self, symbol: str) -> RegimeStructure | None:
        return self._structures.get(symbol)
