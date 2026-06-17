"""intelligence_engine.cross_asset — cross-asset coupling layer (NEW v3-P10)."""

from __future__ import annotations

from intelligence_engine.cross_asset.basket_constructor import BasketConstructor, SyntheticBasket
from intelligence_engine.cross_asset.contagion_detector import ContagionDetector, ContagionEvent
from intelligence_engine.cross_asset.correlation_matrix import CorrelationMatrix, RollingCorrelation
from intelligence_engine.cross_asset.lead_lag import LeadLagDetector, LeadLagResult
from intelligence_engine.cross_asset.dynamic_correlation_clustering import (
    CorrelationCluster,
    CorrelationRegime,
    DynamicCorrelationClusterer
)
from intelligence_engine.cross_asset.volatility_transmission import (
    VolatilitySpillover,
    VolatilityNetwork,
    VolatilityTransmissionEvent,
    VolatilityTransmissionAnalyzer
)

__all__ = [
    "BasketConstructor", "SyntheticBasket",
    "ContagionDetector", "ContagionEvent",
    "CorrelationMatrix", "RollingCorrelation",
    "LeadLagDetector", "LeadLagResult",
    "CorrelationCluster", "CorrelationRegime", "DynamicCorrelationClusterer",
    "VolatilitySpillover", "VolatilityNetwork", "VolatilityTransmissionEvent", "VolatilityTransmissionAnalyzer",
]
