"""
Core Contracts Trader Intelligence
Real implementation for trader intelligence contracts
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class IntelligenceLevel(Enum):
    """Intelligence level enumeration"""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class IntelligenceCategory(Enum):
    """Intelligence category enumeration"""

    MARKET_ANALYSIS = "market_analysis"
    STRATEGY_DEVELOPMENT = "strategy_development"
    RISK_MANAGEMENT = "risk_management"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    EXECUTION_OPTIMIZATION = "execution_optimization"
    PERFORMANCE_ANALYSIS = "performance_analysis"


class ConvictionStyle(Enum):
    """Conviction style enumeration"""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    SPECULATIVE = "speculative"


@dataclass
class PhilosophyProfile:
    """Philosophy profile information"""

    profile_id: str
    conviction_style: ConvictionStyle
    risk_tolerance: float
    time_horizon: str
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "profile_id": self.profile_id,
            "conviction_style": self.conviction_style.value,
            "risk_tolerance": self.risk_tolerance,
            "time_horizon": self.time_horizon,
            "description": self.description,
            "metadata": self.metadata,
        }


class RiskAttitude(Enum):
    """Risk attitude enumeration"""

    RISK_AVERSE = "risk_averse"
    RISK_NEUTRAL = "risk_neutral"
    RISK_SEEKING = "risk_seeking"
    BALANCED = "balanced"


class TimeHorizon(Enum):
    """Time horizon enumeration"""

    SCALPING = "scalping"
    DAY_TRADING = "day_trading"
    SWING_TRADING = "swing_trading"
    POSITION_TRADING = "position_trading"
    LONG_TERM = "long_term"


@dataclass
class TraderModel:
    """Trader model information"""

    model_id: str
    trader_id: str
    philosophy: PhilosophyProfile
    risk_attitude: RiskAttitude
    time_horizon: TimeHorizon
    intelligence_level: IntelligenceLevel
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "model_id": self.model_id,
            "trader_id": self.trader_id,
            "philosophy": self.philosophy.to_dict(),
            "risk_attitude": self.risk_attitude.value,
            "time_horizon": self.time_horizon.value,
            "intelligence_level": self.intelligence_level.value,
            "performance_metrics": self.performance_metrics,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


# Intelligence event kinds
TRADER_OBSERVATION_PROFILE_UPDATE = "trader_observation_profile_update"
TRADER_PERFORMANCE_METRIC_UPDATE = "trader_performance_metric_update"
TRADER_INSIGHT_GENERATED = "trader_insight_generated"
TRADER_CAPABILITY_CHANGED = "trader_capability_changed"
TRADER_LEVEL_PROMOTED = "trader_level_promoted"
TRADER_OBSERVATION_SIGNAL_OBSERVED = "trader_observation_signal_observed"
TRADER_OBSERVATION_PATTERN_DETECTED = "trader_observation_pattern_detected"


@dataclass
class TraderInsight:
    """Trader insight information"""

    insight_id: str
    category: IntelligenceCategory
    title: str
    description: str
    confidence: float
    intelligence_level: IntelligenceLevel
    timestamp: float = field(default_factory=time.time)
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_confident(self) -> bool:
        """Check if insight is confident"""
        return self.confidence > 0.7

    def is_high_level(self) -> bool:
        """Check if insight is high-level"""
        return self.intelligence_level in [
            IntelligenceLevel.ADVANCED,
            IntelligenceLevel.EXPERT,
            IntelligenceLevel.MASTER,
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "insight_id": self.insight_id,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "confidence": self.confidence,
            "intelligence_level": self.intelligence_level.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "metadata": self.metadata,
        }


class TraderIntelligence:
    """Trader intelligence information"""

    trader_id: str
    intelligence_level: IntelligenceLevel
    insights: List[TraderInsight] = field(default_factory=list)
    capabilities: List[IntelligenceCategory] = field(default_factory=list)
    performance_score: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.capabilities:
            self.capabilities = [IntelligenceCategory.MARKET_ANALYSIS]

    def has_capability(self, category: IntelligenceCategory) -> bool:
        """Check if trader has a capability"""
        return category in self.capabilities

    def add_insight(self, insight: TraderInsight) -> None:
        """Add an insight"""
        self.insights.append(insight)
        self.timestamp = time.time()

    def get_insights_by_category(self, category: IntelligenceCategory) -> List[TraderInsight]:
        """Get insights by category"""
        return [i for i in self.insights if i.category == category]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "trader_id": self.trader_id,
            "intelligence_level": self.intelligence_level.value,
            "insights": [i.to_dict() for i in self.insights],
            "capabilities": [c.value for c in self.capabilities],
            "performance_score": self.performance_score,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class IntelligenceRegistry:
    """Registry for trader intelligence"""

    def __init__(self):
        self._intelligence: Dict[str, TraderIntelligence] = {}

    def register_intelligence(self, intelligence: TraderIntelligence) -> bool:
        """Register trader intelligence"""
        self._intelligence[intelligence.trader_id] = intelligence
        return True

    def get_intelligence(self, trader_id: str) -> Optional[TraderIntelligence]:
        """Get specific trader intelligence"""
        return self._intelligence.get(trader_id)

    def get_all_intelligence(self) -> List[TraderIntelligence]:
        """Get all trader intelligence"""
        return list(self._intelligence.values())

    def get_by_level(self, level: IntelligenceLevel) -> List[TraderIntelligence]:
        """Get intelligence by level"""
        return [i for i in self._intelligence.values() if i.intelligence_level == level]


# Global intelligence registry
_intelligence_registry: Optional[IntelligenceRegistry] = None


def get_intelligence_registry() -> IntelligenceRegistry:
    """Get the global intelligence registry"""
    global _intelligence_registry
    if _intelligence_registry is None:
        _intelligence_registry = IntelligenceRegistry()
    return _intelligence_registry


def create_trader_intelligence(trader_id: str, level: IntelligenceLevel) -> TraderIntelligence:
    """Create a new trader intelligence"""
    return TraderIntelligence(trader_id=trader_id, intelligence_level=level)


__all__ = [
    "IntelligenceLevel",
    "IntelligenceCategory",
    "ConvictionStyle",
    "PhilosophyProfile",
    "RiskAttitude",
    "TimeHorizon",
    "TraderModel",
    "TRADER_OBSERVATION_PROFILE_UPDATE",
    "TRADER_PERFORMANCE_METRIC_UPDATE",
    "TRADER_INSIGHT_GENERATED",
    "TRADER_CAPABILITY_CHANGED",
    "TRADER_LEVEL_PROMOTED",
    "TRADER_OBSERVATION_SIGNAL_OBSERVED",
    "TRADER_OBSERVATION_PATTERN_DETECTED",
    "TraderInsight",
    "TraderIntelligence",
    "IntelligenceRegistry",
    "get_intelligence_registry",
    "create_trader_intelligence",
]
