"""Real intelligence engine plugins for DIX VISION v42.2.

All plugins are real implementations with ACTIVE lifecycle.
Stubs have been replaced with concrete trading signal generators.
"""

from intelligence_engine.plugins.footprint_delta.v1 import FootprintDeltaV1
from intelligence_engine.plugins.liquidity_physics.v1 import LiquidityPhysicsV1
from intelligence_engine.plugins.microstructure.microstructure_v1 import MicrostructureV1
from intelligence_engine.plugins.news_reaction.v1 import NewsReactionV1
from intelligence_engine.plugins.on_chain_pulse.v1 import OnChainPulseV1
from intelligence_engine.plugins.order_book_pressure.v1 import OrderBookPressureV1
from intelligence_engine.plugins.orderflow_imbalance.v1 import OrderflowImbalanceV1
from intelligence_engine.plugins.regime_classifier.v1 import RegimeClassifierV1
from intelligence_engine.plugins.sentiment_aggregator.v1 import SentimentAggregatorV1
from intelligence_engine.plugins.trader_imitation.v1 import TraderImitationV1
from intelligence_engine.plugins.vpin_imbalance.v1 import VpinImbalanceV1

__all__ = [
    "FootprintDeltaV1",
    "LiquidityPhysicsV1",
    "MicrostructureV1",
    "NewsReactionV1",
    "OnChainPulseV1",
    "OrderBookPressureV1",
    "OrderflowImbalanceV1",
    "RegimeClassifierV1",
    "SentimentAggregatorV1",
    "TraderImitationV1",
    "VpinImbalanceV1",
]
