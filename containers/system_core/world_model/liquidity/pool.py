"""Liquidity structure — understanding of available depth and execution characteristics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class LiquidityLevel:
    """A liquidity level with depth and expected slippage."""

    price: float
    quantity: float
    expected_slippage: float
    venue: str = ""


@dataclass(frozen=True, slots=True)
class LiquidityStructure:
    """Knowledge about market liquidity.

    Captures:
        - Available depth at key levels
        - Slippage forecasts
        - Venue performance
        - Liquidity regime
    """

    symbol: str
    levels: tuple[LiquidityLevel, ...] = ()
    total_liquidity: float = 0.0
    liquidity_regime: str = "normal"  # "thin", "normal", "deep"
    best_venues: tuple[str, ...] = ()
    confidence: float = 0.0

    @property
    def level_count(self) -> int:
        return len(self.levels)


class LiquidityStructureBuilder:
    """Builds liquidity understanding from order book observations."""

    def __init__(self) -> None:
        self._structures: dict[str, LiquidityStructure] = {}

    def update(
        self,
        symbol: str,
        levels: tuple[LiquidityLevel, ...] | None = None,
        **kwargs: Any,
    ) -> LiquidityStructure:
        existing = self._structures.get(symbol)
        all_levels = list(existing.levels) if existing else []
        if levels:
            all_levels.extend(levels)

        total = sum(level.quantity for level in all_levels) if all_levels else 0.0

        structure = LiquidityStructure(
            symbol=symbol,
            levels=tuple(all_levels[-20:]),
            total_liquidity=total,
            **kwargs,
        )
        self._structures[symbol] = structure
        return structure

    def get(self, symbol: str) -> LiquidityStructure | None:
        return self._structures.get(symbol)

    def get_best_venue(self, symbol: str, regime: str | None = None) -> str | None:
        structure = self._structures.get(symbol)
        if not structure:
            return None
        return structure.best_venues[0] if structure.best_venues else None
