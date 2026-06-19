"""
Trading Knowledge Module - Real Implementation

Provides comprehensive trading knowledge representation, expertise modeling,
and trader behavior analysis for world understanding and agent modeling.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TradingStyle(Enum):
    """Trading style classifications."""
    DAY_TRADER = "day_trader"
    SWING_TRADER = "swing_trader"
    POSITION_TRADER = "position_trader"
    SCALPER = "scalper"
    ARBITRAGEUR = "arbitrageur"
    MARKET_MAKER = "market_maker"
    ALGORITHMIC_TRADER = "algorithmic_trader"
    QUANTITATIVE_TRADER = "quantitative_trader"


class RiskTolerance(Enum):
    """Risk tolerance levels."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    SPECULATIVE = "speculative"


class MarketRegime(Enum):
    """Market regime classifications."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    TRENDING = "trending"
    MEAN_REVERTING = "mean_reverting"


@dataclass
class TradingExpertise:
    """Represents specific trading expertise areas."""
    domain: str  # e.g., "equities", "crypto", "forex", "derivatives"
    instruments: List[str] = field(default_factory=list)
    strategies: List[str] = field(default_factory=list)
    proficiency_level: float = 0.0  # 0.0 to 1.0
    years_experience: float = 0.0
    success_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class BehavioralPattern:
    """Represents identified behavioral patterns of a trader."""
    pattern_id: str
    pattern_type: str  # e.g., "herding", "contrarian", "momentum_chasing", "panic_selling"
    frequency: float  # How often this pattern occurs
    confidence: float  # Confidence in pattern detection
    market_conditions: List[MarketRegime] = field(default_factory=list)
    impact_on_performance: float = 0.0  # -1.0 to 1.0, negative = harmful, positive = beneficial
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class KnowledgeSource:
    """Represents a source of trading knowledge."""
    source_id: str
    source_type: str  # e.g., "experience", "education", "research", "data_analysis"
    credibility: float  # 0.0 to 1.0
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    knowledge_domains: List[str] = field(default_factory=list)


@dataclass
class TradingBelief:
    """Represents a trading belief or hypothesis."""
    belief_id: str
    belief_statement: str
    domain: str  # e.g., "market_efficiency", "trend_persistence", "volatility_clustering"
    confidence: float  # 0.0 to 1.0
    evidence_count: int = 0
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    effectiveness_score: float = 0.0  # -1.0 to 1.0


class TraderKnowledge:
    """Comprehensive trader knowledge representation system."""
    
    def __init__(self, trader_id: str = "default"):
        self._trader_id = trader_id
        self._expertise_areas: Dict[str, TradingExpertise] = {}
        self._behavioral_patterns: Dict[str, BehavioralPattern] = {}
        self._knowledge_sources: Dict[str, KnowledgeSource] = {}
        self._trading_beliefs: Dict[str, TradingBelief] = {}
        self._historical_decisions: List[Dict[str, Any]] = []
        self._performance_history: List[Dict[str, Any]] = []
        
        # Trader profile characteristics
        self._trading_style = TradingStyle.MODERATE
        self._risk_tolerance = RiskTolerance.MODERATE
        self._preferred_timeframes = ["1h", "4h", "1d"]
        self._max_position_size = 1.0  # As percentage of portfolio
        self._max_positions = 10
        self._preferred_instruments = []
        
        # Market regime preferences
        self._regime_performance: Dict[MarketRegime, float] = {
            regime: 0.0 for regime in MarketRegime
        }
        
        logger.info(f"[TRADER_KNOWLEDGE] Initialized trader knowledge for {trader_id}")
    
    def add_expertise(self, expertise: TradingExpertise) -> None:
        """Add or update trading expertise area."""
        expertise.last_updated = datetime.now()
        self._expertise_areas[expertise.domain] = expertise
        logger.info(f"[TRADER_KNOWLEDGE] Added expertise in {expertise.domain} (proficiency: {expertise.proficiency_level:.2f})")
    
    def get_expertise(self, domain: str) -> Optional[TradingExpertise]:
        """Get expertise for a specific domain."""
        return self._expertise_areas.get(domain)
    
    def get_all_expertise(self) -> List[TradingExpertise]:
        """Get all expertise areas."""
        return list(self._expertise_areas.values())
    
    def record_behavioral_pattern(self, pattern: BehavioralPattern) -> None:
        """Record a behavioral pattern."""
        self._behavioral_patterns[pattern.pattern_id] = pattern
        logger.info(f"[TRADER_KNOWLEDGE] Recorded pattern {pattern.pattern_type} (confidence: {pattern.confidence:.2f})")
    
    def get_behavioral_patterns(self, pattern_type: Optional[str] = None) -> List[BehavioralPattern]:
        """Get behavioral patterns, optionally filtered by type."""
        patterns = list(self._behavioral_patterns.values())
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        return patterns
    
    def add_knowledge_source(self, source: KnowledgeSource) -> None:
        """Add a knowledge source."""
        source.last_accessed = datetime.now()
        self._knowledge_sources[source.source_id] = source
        logger.info(f"[TRADER_KNOWLEDGE] Added knowledge source {source.source_type}")
    
    def access_knowledge_source(self, source_id: str) -> Optional[KnowledgeSource]:
        """Access and update knowledge source."""
        source = self._knowledge_sources.get(source_id)
        if source:
            source.last_accessed = datetime.now()
            source.access_count += 1
        return source
    
    def form_belief(self, belief: TradingBelief) -> None:
        """Form or update a trading belief."""
        belief.last_updated = datetime.now()
        self._trading_beliefs[belief.belief_id] = belief
        logger.info(f"[TRADER_KNOWLEDGE] Formed belief: {belief.belief_statement[:50]}... (confidence: {belief.confidence:.2f})")
    
    def update_belief_confidence(self, belief_id: str, evidence: str, 
                                 supporting: bool, effectiveness: float = 0.0) -> None:
        """Update belief confidence with new evidence."""
        belief = self._trading_beliefs.get(belief_id)
        if not belief:
            return
        
        belief.evidence_count += 1
        if supporting:
            belief.supporting_evidence.append(evidence)
            # Increase confidence for supporting evidence
            belief.confidence = min(1.0, belief.confidence + 0.05)
        else:
            belief.contradicting_evidence.append(evidence)
            # Decrease confidence for contradicting evidence
            belief.confidence = max(0.0, belief.confidence - 0.05)
        
        # Update effectiveness score using exponential moving average
        if belief.effectiveness_score == 0.0:
            belief.effectiveness_score = effectiveness
        else:
            belief.effectiveness_score = 0.9 * belief.effectiveness_score + 0.1 * effectiveness
        
        belief.last_updated = datetime.now()
        logger.debug(f"[TRADER_KNOWLEDGE] Updated belief {belief_id} confidence: {belief.confidence:.2f}")
    
    def get_beliefs(self, domain: Optional[str] = None) -> List[TradingBelief]:
        """Get beliefs, optionally filtered by domain."""
        beliefs = list(self._trading_beliefs.values())
        if domain:
            beliefs = [b for b in beliefs if b.domain == domain]
        # Sort by confidence
        beliefs.sort(key=lambda b: b.confidence, reverse=True)
        return beliefs
    
    def record_decision(self, decision: Dict[str, Any]) -> None:
        """Record a trading decision for learning."""
        decision["timestamp"] = datetime.now()
        decision["trader_id"] = self._trader_id
        self._historical_decisions.append(decision)
        
        # Keep only recent decisions (last 1000)
        if len(self._historical_decisions) > 1000:
            self._historical_decisions = self._historical_decisions[-1000:]
    
    def record_performance(self, performance: Dict[str, Any]) -> None:
        """Record performance data for analysis."""
        performance["timestamp"] = datetime.now()
        performance["trader_id"] = self._trader_id
        self._performance_history.append(performance)
        
        # Update regime performance if regime is specified
        regime = performance.get("regime")
        if regime and isinstance(regime, MarketRegime):
            return_value = performance.get("return_value", 0.0)
            # Update exponential moving average for regime performance
            alpha = 0.1
            self._regime_performance[regime] = (
                alpha * return_value + (1 - alpha) * self._regime_performance[regime]
            )
        
        # Keep only recent performance (last 500)
        if len(self._performance_history) > 500:
            self._performance_history = self._performance_history[-500:]
    
    def get_regime_performance(self) -> Dict[MarketRegime, float]:
        """Get performance across different market regimes."""
        return self._regime_performance.copy()
    
    def get_best_regimes(self, top_n: int = 3) -> List[Tuple[MarketRegime, float]]:
        """Get the best performing regimes."""
        sorted_regimes = sorted(self._regime_performance.items(), key=lambda x: x[1], reverse=True)
        return sorted_regimes[:top_n]
    
    def analyze_behavioral_patterns(self) -> Dict[str, Any]:
        """Analyze behavioral patterns and their impact."""
        pattern_analysis = {}
        
        for pattern_id, pattern in self._behavioral_patterns.items():
            pattern_analysis[pattern_id] = {
                "pattern_type": pattern.pattern_type,
                "frequency": pattern.frequency,
                "confidence": pattern.confidence,
                "impact_on_performance": pattern.impact_on_performance,
                "harmful": pattern.impact_on_performance < 0,
                "beneficial": pattern.impact_on_performance > 0
            }
        
        # Identify most problematic patterns
        harmful_patterns = [
            p for p in self._behavioral_patterns.values() if p.impact_on_performance < -0.2
        ]
        
        # Identify most beneficial patterns
        beneficial_patterns = [
            p for p in self._behavioral_patterns.values() if p.impact_on_performance > 0.2
        ]
        
        return {
            "pattern_analysis": pattern_analysis,
            "total_patterns": len(self._behavioral_patterns),
            "harmful_patterns": len(harmful_patterns),
            "beneficial_patterns": len(beneficial_patterns),
            "most_harmful": harmful_patterns[:3] if harmful_patterns else [],
            "most_beneficial": beneficial_patterns[:3] if beneficial_patterns else []
        }
    
    def get_trading_profile(self) -> Dict[str, Any]:
        """Get comprehensive trading profile."""
        return {
            "trader_id": self._trader_id,
            "trading_style": self._trading_style.value,
            "risk_tolerance": self._risk_tolerance.value,
            "preferred_timeframes": self._preferred_timeframes,
            "max_position_size": self._max_position_size,
            "max_positions": self._max_positions,
            "preferred_instruments": self._preferred_instruments,
            "expertise_areas": {
                domain: {
                    "proficiency_level": expertise.proficiency_level,
                    "years_experience": expertise.years_experience,
                    "success_rate": expertise.success_rate
                }
                for domain, expertise in self._expertise_areas.items()
            },
            "regime_performance": {
                regime.value: performance 
                for regime, performance in self._regime_performance.items()
            },
            "total_decisions": len(self._historical_decisions),
            "total_performance_records": len(self._performance_history),
            "belief_count": len(self._trading_beliefs),
            "pattern_count": len(self._behavioral_patterns)
        }
    
    def recommend_regime_strategy(self, current_regime: MarketRegime) -> Dict[str, Any]:
        """Recommend strategy based on current market regime and historical performance."""
        regime_performance = self._regime_performance.get(current_regime, 0.0)
        
        # Get best performing regimes
        best_regimes = self.get_best_regimes(3)
        
        # Adjust risk based on regime performance
        if regime_performance > 0.01:  # Good performance in this regime
            recommended_action = "maintain_position"
            recommended_risk = "normal"
        elif regime_performance > -0.01:  # Neutral performance
            recommended_action = "reduce_position"
            recommended_risk = "conservative"
        else:  # Poor performance
            recommended_action = "minimize_exposure"
            recommended_risk = "defensive"
        
        # Get relevant beliefs for this regime
        relevant_beliefs = self.get_beliefs(domain="regime_analysis")
        
        # Get relevant behavioral patterns
        regime_patterns = self.get_behavioral_patterns()
        harmful_in_regime = [p for p in regime_patterns if p.impact_on_performance < -0.2]
        
        return {
            "current_regime": current_regime.value,
            "regime_performance": regime_performance,
            "recommended_action": recommended_action,
            "recommended_risk": recommended_risk,
            "best_alternative_regimes": [r.value for r, p in best_regimes if p > regime_performance],
            "relevant_beliefs": [b.belief_statement for b in relevant_beliefs[:5]],
            "patterns_to_avoid": [p.pattern_type for p in harmful_in_regime],
            "confidence": min(1.0, abs(regime_performance) * 10) if regime_performance != 0 else 0.5
        }


# Global knowledge base instance
_trader_knowledge_base: Dict[str, TraderKnowledge] = {}


def get_trader_knowledge(trader_id: str = "default", **kwargs: Any) -> TraderKnowledge:
    """Get or create trader knowledge instance.
    
    Args:
        trader_id: Unique identifier for the trader
        **kwargs: Additional configuration parameters
        
    Returns:
        TraderKnowledge instance for the specified trader
    """
    global _trader_knowledge_base
    
    if trader_id not in _trader_knowledge_base:
        _trader_knowledge_base[trader_id] = TraderKnowledge(trader_id)
        logger.info(f"[TRADER_KNOWLEDGE] Created new trader knowledge instance for {trader_id}")
    
    return _trader_knowledge_base[trader_id]


def get_all_trader_knowledge() -> Dict[str, TraderKnowledge]:
    """Get all trader knowledge instances."""
    return _trader_knowledge_base.copy()


def analyze_collective_behavior() -> Dict[str, Any]:
    """Analyze behavioral patterns across all traders."""
    all_patterns = {}
    all_regime_performance = {regime: [] for regime in MarketRegime}
    
    for trader_id, knowledge in _trader_knowledge_base.items():
        # Collect patterns
        for pattern in knowledge.get_behavioral_patterns():
            if pattern.pattern_type not in all_patterns:
                all_patterns[pattern.pattern_type] = []
            all_patterns[pattern.pattern_type].append({
                "trader_id": trader_id,
                "frequency": pattern.frequency,
                "confidence": pattern.confidence,
                "impact": pattern.impact_on_performance
            })
        
        # Collect regime performance
        for regime, performance in knowledge.get_regime_performance().items():
            all_regime_performance[regime].append(performance)
    
    # Calculate aggregate statistics
    pattern_stats = {}
    for pattern_type, pattern_data in all_patterns.items():
        if pattern_data:
            avg_frequency = np.mean([p["frequency"] for p in pattern_data])
            avg_confidence = np.mean([p["confidence"] for p in pattern_data])
            avg_impact = np.mean([p["impact"] for p in pattern_data])
            pattern_stats[pattern_type] = {
                "trader_count": len(pattern_data),
                "average_frequency": avg_frequency,
                "average_confidence": avg_confidence,
                "average_impact": avg_impact
            }
    
    regime_stats = {}
    for regime, performances in all_regime_performance.items():
        if performances:
            regime_stats[regime.value] = {
                "average_performance": np.mean(performances),
                "std_performance": np.std(performances),
                "trader_count": len(performances)
            }
    
    return {
        "total_traders": len(_trader_knowledge_base),
        "pattern_statistics": pattern_stats,
        "regime_statistics": regime_stats,
        "timestamp": datetime.now()
    }


__all__ = [
    "TradingStyle",
    "RiskTolerance", 
    "MarketRegime",
    "TradingExpertise",
    "BehavioralPattern",
    "KnowledgeSource",
    "TradingBelief",
    "TraderKnowledge",
    "get_trader_knowledge",
    "get_all_trader_knowledge",
    "analyze_collective_behavior"
]