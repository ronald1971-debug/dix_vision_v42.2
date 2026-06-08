from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RealityDomain(Enum):
    MARKET = "market"
    TRADER = "trader"
    STRATEGY = "strategy"
    PORTFOLIO = "portfolio"
    EXECUTION = "execution"
    REGIME = "regime"
    SYSTEM = "system"
    RISK = "risk"

@dataclass(frozen=True)
class Belief:
    """A single unit of cognition within the MCOS."""
    domain: RealityDomain
    contributor: str  # Engine name
    content: dict[str, Any]
    confidence: float  # 0.0 to 1.0
    uncertainty: float # 0.0 to 1.0
    timestamp: float
    consensus_weight: float = 1.0

@dataclass
class BeliefState:
    """
    The central cognitive substrate of DIX VISION.
    Single source of truth for all engines.
    """
    market_reality: dict[str, Any] = field(default_factory=dict)
    trader_reality: dict[str, Any] = field(default_factory=dict)
    strategy_reality: dict[str, Any] = field(default_factory=dict)
    portfolio_reality: dict[str, Any] = field(default_factory=dict)
    execution_reality: dict[str, Any] = field(default_factory=dict)
    regime_reality: dict[str, Any] = field(default_factory=dict)
    system_reality: dict[str, Any] = field(default_factory=dict)
    
    confidence_metrics: dict[str, float] = field(default_factory=dict)
    uncertainty_metrics: dict[str, float] = field(default_factory=dict)
    consensus_metrics: dict[str, float] = field(default_factory=dict)
    
    def update_belief(self, belief: Belief):
        """
        Updates the state based on a new engine contribution.
        In production, this would be handled by a Projector following the Event Ledger.
        """
        target_map = {
            RealityDomain.MARKET: self.market_reality,
            RealityDomain.TRADER: self.trader_reality,
            RealityDomain.STRATEGY: self.strategy_reality,
            RealityDomain.PORTFOLIO: self.portfolio_reality,
            RealityDomain.EXECUTION: self.execution_reality,
            RealityDomain.REGIME: self.regime_reality,
            RealityDomain.SYSTEM: self.system_reality,
        }.get(belief.domain)

        if target_map is not None:
            target_map.update(belief.content)
            self.confidence_metrics[belief.contributor] = belief.confidence
            self.uncertainty_metrics[belief.contributor] = belief.uncertainty

    def get_view(self, domain: RealityDomain) -> dict[str, Any]:
        """Returns the authoritative view for a specific domain."""
        return {
            RealityDomain.MARKET: self.market_reality,
            RealityDomain.TRADER: self.trader_reality,
            RealityDomain.STRATEGY: self.strategy_reality,
            RealityDomain.PORTFOLIO: self.portfolio_reality,
            RealityDomain.EXECUTION: self.execution_reality,
            RealityDomain.REGIME: self.regime_reality,
            RealityDomain.SYSTEM: self.system_reality,
        }.get(domain, {})