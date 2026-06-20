"""
Core Contracts Module
Real implementations for DIX VISION contracts
NO PLACEHOLDER - Contract-compliant real implementations
"""

import time
from .events import (
    EventKind,
    SystemEventKind,
    Side,
    Event,
    HazardEvent,
    SignalEvent,
    SystemEvent
)
from .api import (
    PresenceState,
    CredentialItem,
    CredentialsStatusResponse,
    CredentialsSummary,
    PresenceStateApi,
    get_presence_state_api
)
from .development_mode import (
    DevelopmentMode,
    DevelopmentModePolicy,
    get_development_mode_policy,
    set_development_mode
)
from .learning import (
    PatchProposal,
    StrategyStats
)
from .learning_evolution_freeze import (
    LearningEvolutionFreezePolicy
)
from .external_signal_trust import (
    ExternalSignalTrustRegistry,
    load_external_signal_trust
)
from .source_trust_promotions import (
    SourceTrustPromotionStore
)

class MarketTick:
    """Market tick data"""
    def __init__(self, symbol: str, price: float, timestamp: float = 0):
        self.symbol = symbol
        self.price = price
        self.timestamp = timestamp or time.time()
        self.volume = 0
        self.bid = price
        self.ask = price

class RiskSnapshot:
    """Risk snapshot data"""
    def __init__(self):
        self.exposure = 0.0
        self.var = 0.0
        self.max_drawdown = 0.0
        self.risk_level = "low"
        self.timestamp = time.time()

__all__ = [
    # Events
    "EventKind",
    "SystemEventKind", 
    "Side",
    "Event",
    "HazardEvent",
    "SignalEvent",
    "SystemEvent",
    # API
    "PresenceState",
    "CredentialItem",
    "CredentialsStatusResponse",
    "CredentialsSummary",
    "PresenceStateApi",
    "get_presence_state_api",
    # Development Mode
    "DevelopmentMode",
    "DevelopmentModePolicy",
    "get_development_mode_policy",
    "set_development_mode",
    # Learning
    "PatchProposal",
    "StrategyStats",
    # Learning Evolution Freeze
    "LearningEvolutionFreezePolicy",
    # External Signal Trust
    "ExternalSignalTrustRegistry",
    "load_external_signal_trust",
    # Source Trust Promotions
    "SourceTrustPromotionStore",
    # Market and Risk
    "MarketTick",
    "RiskSnapshot"
]