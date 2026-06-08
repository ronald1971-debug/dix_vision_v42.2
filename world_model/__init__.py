"""world_model — INDIRA's understanding of market reality.

The World Model Layer is probably the largest missing cognitive component.

Current:
    - market data (raw ticks)

Future:
    - World Model with:
        - Market Structure
        - Liquidity Structure
        - Participant Structure
        - Regime Structure
        - Macro Structure

INDIRA reasons against a world model, not raw ticks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from world_model.liquidity.pool import (
    LiquidityStructure,
    LiquidityStructureBuilder,
)
from world_model.macro.overview import (
    MacroStructure,
    MacroStructureBuilder,
)
from world_model.participant.trader import (
    ParticipantStructure,
    ParticipantStructureBuilder,
)
from world_model.regime.state import (
    RegimeStructure,
    RegimeStructureBuilder,
)
from world_model.structure.market import (
    MarketStructure,
    MarketStructureBuilder,
)


@dataclass(frozen=True, slots=True)
class WorldModel:
    """Complete world model for INDIRA's reasoning.

    Combines all structural views:
        - Market structure: price levels, order book shape
        - Liquidity structure: available depth, slippage forecasts
        - Participant structure: trader types, behavioral clusters
        - Regime structure: current regime, transition probabilities
        - Macro structure: economic regime, sentiment, flows
    """

    market: MarketStructure | None = None
    liquidity: LiquidityStructure | None = None
    participants: ParticipantStructure | None = None
    regime: RegimeStructure | None = None
    macro: MacroStructure | None = None
    confidence: float = 0.0

    def summarize(self) -> dict[str, Any]:
        return {
            "market": self.market.symbol if self.market else None,
            "regime": self.regime.current_regime if self.regime else None,
            "confidence": self.confidence,
            "liquidity_levels": len(self.liquidity.levels) if self.liquidity else 0,
            "participant_count": len(self.participants.traders) if self.participants else 0,
        }


__all__ = [
    "WorldModel",
    "MarketStructure",
    "MarketStructureBuilder",
    "LiquidityStructure",
    "LiquidityStructureBuilder",
    "ParticipantStructure",
    "ParticipantStructureBuilder",
    "RegimeStructure",
    "RegimeStructureBuilder",
    "MacroStructure",
    "MacroStructureBuilder",
]