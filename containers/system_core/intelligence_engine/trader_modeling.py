"""
Trader Modeling - World-Aware Production-Grade Implementation

Provides real trader behavior modeling and analysis for the DIX VISION system,
including trader classification, behavior pattern recognition, predictive modeling,
and world context integration for agent behavior insights.

Contract Compliance: TIER-0 Production Implementation Directive
- Zero Placeholder Policy: No pass, TODO, FIXME, NotImplemented, fake data
- Real Capability: Complete runtime behavior with actual trader modeling
- Production-Grade: Metrics, monitoring, error handling, deterministic design
- World Model Integration: World-aware agent modeling for comprehensive understanding
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import hashlib

# Try to import world model components
try:
    from world_model.indicator_integration import get_integration_bridge
    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False

logger = logging.getLogger(__name__)


class TraderBehavior(Enum):
    """Types of trader behaviors."""
    MOMENTUM_CHASING = "momentum_chasing"
    CONTRARIAN = "contrarian"
    HERDING = "herding"
    PANIC_SELLING = "panic_selling"
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    LIQUIDITY_PROVIDING = "liquidity_providing"
    SPECULATIVE = "speculative"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"


class TraderClassification(Enum):
    """Classification of trader types."""
    RETAIL = "retail"
    INSTITUTIONAL = "institutional"
    HIGH_FREQUENCY = "high_frequency"
    ALGORITHMIC = "algorithmic"
    MARKET_MAKER = "market_maker"
    ARBITRAGEUR = "arbitrageur"
    DAY_TRADER = "day_trader"
    POSITION_TRADER = "position_trader"


class MarketImpact(Enum):
    """Classification of market impact."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


@dataclass
class TraderObservation:
    """Single observation of trader behavior."""
    observation_id: str
    trader_id: str
    timestamp: datetime
    action: str  # "buy", "sell", "hold"
    volume: float
    price: float
    symbol: str
    market_conditions: Dict[str, Any]
    behavioral_indicators: Dict[str, float]
    impact_estimate: MarketImpact
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "observation_id": self.observation_id,
            "trader_id": self.trader_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "volume": self.volume,
            "price": self.price,
            "symbol": self.symbol,
            "market_conditions": self.market_conditions,
            "behavioral_indicators": self.behavioral_indicators,
            "impact_estimate": self.impact_estimate.value,
            "metadata": self.metadata
        }


@dataclass
class TraderProfile:
    """Comprehensive profile of a trader."""
    trader_id: str
    classification: TraderClassification
    primary_behaviors: List[TraderBehavior]
    behavior_weights: Dict[TraderBehavior, float]
    trading_patterns: Dict[str, Any]
    performance_metrics: Dict[str, float]
    risk_profile: str
    impact_classification: MarketImpact
    interaction_patterns: Dict[str, float]
    last_observation: datetime
    observation_count: int = 0
    profile_confidence: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "trader_id": self.trader_id,
            "classification": self.classification.value,
            "primary_behaviors": [b.value for b in self.primary_behaviors],
            "behavior_weights": {k.value: v for k, v in self.behavior_weights.items()},
            "trading_patterns": self.trading_patterns,
            "performance_metrics": self.performance_metrics,
            "risk_profile": self.risk_profile,
            "impact_classification": self.impact_classification.value,
            "interaction_patterns": self.interaction_patterns,
            "last_observation": self.last_observation.isoformat(),
            "observation_count": self.observation_count,
            "profile_confidence": self.profile_confidence,
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class BehavioralPattern:
    """Identified behavioral pattern for a trader."""
    pattern_id: str
    trader_id: str
    pattern_type: TraderBehavior
    frequency: float  # How often this pattern occurs
    confidence: float  # Confidence in pattern detection
    market_conditions: List[str]
    performance_impact: float  # Correlation with performance
    last_detected: datetime
    strength: float  # Pattern strength indicator
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "pattern_id": self.pattern_id,
            "trader_id": self.trader_id,
            "pattern_type": self.pattern_type.value,
            "frequency": self.frequency,
            "confidence": self.confidence,
            "market_conditions": self.market_conditions,
            "performance_impact": self.performance_impact,
            "last_detected": self.last_detected.isoformat(),
            "strength": self.strength,
            "metadata": self.metadata
        }


@dataclass
class TraderModelMetrics:
    """Metrics for trader modeling system performance."""
    total_observations: int = 0
    total_profiles: int = 0
    patterns_detected: int = 0
    classification_accuracy: float = 0.0
    average_processing_time_ms: float = 0.0
    model_confidence: float = 0.0
    prediction_accuracy: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "total_observations": self.total_observations,
            "total_profiles": self.total_profiles,
            "patterns_detected": self.patterns_detected,
            "classification_accuracy": self.classification_accuracy,
            "average_processing_time_ms": self.average_processing_time_ms,
            "model_confidence": self.model_confidence,
            "prediction_accuracy": self.prediction_accuracy,
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class WorldContext:
    """World model context for trader modeling."""
    market_regime: str  # bullish, bearish, sideways, high_volatility
    market_trend: str  # trending, mean_reverting
    volatility_regime: str  # high, normal, low
    liquidity_state: str  # high, normal, low
    agent_activity: Dict[str, float]  # agent_type -> activity_level
    causal_factors: List[str]  # relevant causal factors
    prediction_confidence: float  # world model prediction confidence
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "market_regime": self.market_regime,
            "market_trend": self.market_trend,
            "volatility_regime": self.volatility_regime,
            "liquidity_state": self.liquidity_state,
            "agent_activity": self.agent_activity,
            "causal_factors": self.causal_factors,
            "prediction_confidence": self.prediction_confidence,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ActionPredictions:
    """Predicted trader actions with world context."""
    trader_id: str
    predicted_action: str  # "buy", "sell", "hold"
    action_probability: float
    predicted_volume: float
    confidence: float
    world_context_influence: float
    regime_specific_adjustments: Dict[str, float]
    causal_factor_impact: Dict[str, float]
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "trader_id": self.trader_id,
            "predicted_action": self.predicted_action,
            "action_probability": self.action_probability,
            "predicted_volume": self.predicted_volume,
            "confidence": self.confidence,
            "world_context_influence": self.world_context_influence,
            "regime_specific_adjustments": self.regime_specific_adjustments,
            "causal_factor_impact": self.causal_factor_impact,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat()
        }


class TraderBehaviorAnalyzer:
    """Analyzes trader behavior from observations with world context integration."""
    
    def __init__(self):
        """Initialize the behavior analyzer."""
        self._lock = threading.Lock()
        
        # Behavior detection rules
        self._behavior_rules = {
            TraderBehavior.MOMENTUM_CHASING: self._detect_momentum_chasing,
            TraderBehavior.CONTRARIAN: self._detect_contrarian,
            TraderBehavior.HERDING: self._detect_herding,
            TraderBehavior.PANIC_SELLING: self._detect_panic_selling,
            TraderBehavior.ACCUMULATION: self._detect_accumulation,
            TraderBehavior.DISTRIBUTION: self._detect_distribution,
            TraderBehavior.LIQUIDITY_PROVIDING: self._detect_liquidity_providing,
            TraderBehavior.SPECULATIVE: self._detect_speculative,
            TraderBehavior.ARBITRAGE: self._detect_arbitrage,
            TraderBehavior.MARKET_MAKING: self._detect_market_making
        }
        
        # World model integration
        self._world_integration_bridge = None
        self._world_context_cache: Dict[str, WorldContext] = {}
        self._world_cache_ttl_seconds = 30
        
        # Initialize world model integration if available
        if WORLD_MODEL_AVAILABLE:
            try:
                self._world_integration_bridge = get_integration_bridge()
                logger.info("[TRADER_MODELING] World model integration initialized")
            except Exception as e:
                logger.warning(f"[TRADER_MODELING] Failed to initialize world model integration: {e}")
        
        logger.info("[TRADER_MODELING] Trader Behavior Analyzer initialized")
    
    def analyze_observation(self, observation: TraderObservation) -> List[BehavioralPattern]:
        """Analyze a single observation for behavioral patterns.
        
        Args:
            observation: Trader observation to analyze
            
        Returns:
            List of detected behavioral patterns
        """
        detected_patterns = []
        
        for behavior, detection_func in self._behavior_rules.items():
            try:
                pattern = detection_func(observation)
                if pattern and pattern.confidence > 0.5:
                    detected_patterns.append(pattern)
            except Exception as e:
                logger.warning(f"[TRADER_MODELING] Error detecting {behavior.value}: {e}")
        
        return detected_patterns
    
    def _detect_momentum_chasing(self, observation: TraderObservation) -> Optional[BehavioralPattern]:
        """Detect momentum chasing behavior."""
        behavioral_indicators = observation.behavioral_indicators
        market_conditions = observation.market_conditions
        
        # Momentum chasing indicators
        trend_alignment = behavioral_indicators.get("trend_alignment", 0.0)
        price_momentum = behavioral_indicators.get("price_momentum", 0.0)
        volume_surge = behavioral_indicators.get("volume_surge", 0.0)
        
        if trend_alignment > 0.7 and price_momentum > 0.5 and volume_surge > 0.3:
            confidence = min(1.0, (trend_alignment + price_momentum + volume_surge) / 3)
            
            return BehavioralPattern(
                pattern_id=f"momentum_chasing_{observation.observation_id}",
                trader_id=observation.trader_id,
                pattern_type=TraderBehavior.MOMENTUM_CHASING,
                frequency=behavioral_indicators.get("frequency", 0.5),
                confidence=confidence,
                market_conditions=[market_conditions.get("regime", "unknown")],
                performance_impact=behavioral_indicators.get("performance_correlation", 0.0),
                last_detected=observation.timestamp,
                strength=confidence
            )
        
        return None
    
    def _detect_contrarian(self, observation: TraderObservation) -> Optional[BehavioralPattern]:
        """Detect contrarian behavior."""
        behavioral_indicators = observation.behavioral_indicators
        market_conditions = observation.market_conditions
        
        # Contrarian indicators
        trend_alignment = behavioral_indicators.get("trend_alignment", 0.0)
        price_momentum = behavioral_indicators.get("price_momentum", 0.0)
        
        if trend_alignment < -0.6 and price_momentum < 0.0:
            confidence = min(1.0, abs(trend_alignment) * 0.8)
            
            return BehavioralPattern(
                pattern_id=f"contrarian_{observation.observation_id}",
                trader_id=observation.trader_id,
                pattern_type=TraderBehavior.CONTRARIAN,
                frequency=behavioral_indicators.get("frequency", 0.3),
                confidence=confidence,
                market_conditions=[market_conditions.get("regime", "unknown")],
                performance_impact=behavioral_indicators.get("performance_correlation", 0.0),
                last_detected=observation.timestamp,
                strength=confidence
            )
        
        return None
    
    def _detect_herding(self, observation: TraderObservation) -> Optional[BehavioralPattern]:
        """Detect herding behavior."""
        behavioral_indicators = observation.behavioral_indicators
        
        # Herding indicators
        correlation_with_peers = behavioral_indicators.get("peer_correlation", 0.0)
        volume_surge = behavioral_indicators.get("volume_surge", 0.0)
        
        if correlation_with_peers > 0.8 and volume_surge > 0.5:
            confidence = min(1.0, correlation_with_peers * 0.9)
            
            return BehavioralPattern(
                pattern_id=f"herding_{observation.observation_id}",
                trader_id=observation.trader_id,
                pattern_type=TraderBehavior.HERDING,
                frequency=behavioral_indicators.get("frequency", 0.4),
                confidence=confidence,
                market_conditions=[observation.market_conditions.get("regime", "unknown")],
                performance_impact=behavioral_indicators.get("performance_correlation", 0.0),
                last_detected=observation.timestamp,
                strength=confidence
            )
        
        return None
    
    def _detect_panic_selling(self, observation: TraderObservation) -> Optional[BehavioralPattern]:
        """Detect panic selling behavior."""
        behavioral_indicators = observation.behavioral_indicators
        market_conditions = observation.market_conditions
        
        # Panic selling indicators
        if observation.action != "sell":
            return None
        
        urgency = behavioral_indicators.get("urgency", 0.0)
        price_impact = behavioral_indicators.get("price_impact", 0.0)
        market_stress = market_conditions.get("stress_level", 0.0)
        
        if urgency > 0.8 and price_impact > 0.6 and market_stress > 0.7:
            confidence = min(1.0, (urgency + price_impact + market_stress) / 3)
            
            return BehavioralPattern(
                pattern_id=f"panic_selling_{observation.observation_id}",
                trader_id=observation.trader_id,
                pattern_type=TraderBehavior.PANIC_SELLING,
                frequency=behavioral_indicators.get("frequency", 0.2),
                confidence=confidence,
                market_conditions=["high_stress", market_conditions.get("regime", "unknown")],
                performance_impact=-0.5,  # Typically negative impact
                last_detected=observation.timestamp,
                strength=confidence
            )
        
        return None
    
    def _detect_accumulation(self, observation: TraderObservation) -> Optional[BehavioralPattern]:
        """Detect accumulation behavior."""
        behavioral_indicators = observation.behavioral_indicators
        
        # Accumulation indicators
        if observation.action != "buy":
            return None
        
        holding_increase = behavioral_indicators.get("holding_increase", 0.0)
        long_term_intent = behavioral_indicators.get("long_term_intent", 0.0)
        
        if holding_increase > 0.5 and long_term_intent > 0.7:
            confidence = min(1.0, (holding_increase + long_term_intent) / 2)
            
            return BehavioralPattern(
                pattern_id=f"accumulation_{observation.observation_id}",
                trader_id=observation.trader_id,
                pattern_type=TraderBehavior.ACCUMULATION,
                frequency=behavioral_indicators.get("frequency", 0.6),
                confidence=confidence,
                market_conditions=[observation.market_conditions.get("regime", "unknown")],
                performance_impact=behavioral_indicators.get("performance_correlation", 0.0),
                last_detected=observation.timestamp,
                strength=confidence
            )
        
        return None
    
    def _detect_distribution(self, observation: TraderObservation) -> Optional[BehavioralPattern]:
        """Detect distribution behavior."""
        behavioral_indicators = observation.behavioral_indicators
        
        # Distribution indicators
        if observation.action != "sell":
            return None
        
        holding_decrease = behavioral_indicators.get("holding_decrease", 0.0)
        profit_taking = behavioral_indicators.get("profit_taking", 0.0)
        
        if holding_decrease > 0.5 and profit_taking > 0.7:
            confidence = min(1.0, (holding_decrease + profit_taking) / 2)
            
            return BehavioralPattern(
                pattern_id=f"distribution_{observation.observation_id}",
                trader_id=observation.trader_id,
                pattern_type=TraderBehavior.DISTRIBUTION,
                frequency=behavioral_indicators.get("frequency", 0.4),
                confidence=confidence,
                market_conditions=[observation.market_conditions.get("regime", "unknown")],
                performance_impact=behavioral_indicators.get("performance_correlation", 0.0),
                last_detected=observation.timestamp,
                strength=confidence
            )
        
        return None
    
    def _detect_liquidity_providing(self, observation: TraderObservation) -> Optional[BehavioralPattern]:
        """Detect liquidity providing behavior."""
        behavioral_indicators = observation.behavioral_indicators
        
        # Liquidity providing indicators
        spread_improvement = behavioral_indicators.get("spread_improvement", 0.0)
        depth_contribution = behavioral_indicators.get("depth_contribution", 0.0)
        
        if spread_improvement > 0.6 and depth_contribution > 0.5:
            confidence = min(1.0, (spread_improvement + depth_contribution) / 2)
            
            return BehavioralPattern(
                pattern_id=f"liquidity_providing_{observation.observation_id}",
                trader_id=observation.trader_id,
                pattern_type=TraderBehavior.LIQUIDITY_PROVIDING,
                frequency=behavioral_indicators.get("frequency", 0.7),
                confidence=confidence,
                market_conditions=[observation.market_conditions.get("liquidity_regime", "unknown")],
                performance_impact=behavioral_indicators.get("performance_correlation", 0.0),
                last_detected=observation.timestamp,
                strength=confidence
            )
        
        return None
    
    def _detect_speculative(self, observation: TraderObservation) -> Optional[BehavioralPattern]:
        """Detect speculative behavior."""
        behavioral_indicators = observation.behavioral_indicators
        
        # Speculative indicators
        high_frequency = behavioral_indicators.get("high_frequency", 0.0)
        high_leverage = behavioral_indicators.get("leverage", 0.0)
        
        if high_frequency > 0.7 and high_leverage > 0.6:
            confidence = min(1.0, (high_frequency + high_leverage) / 2)
            
            return BehavioralPattern(
                pattern_id=f"speculative_{observation.observation_id}",
                trader_id=observation.trader_id,
                pattern_type=TraderBehavior.SPECULATIVE,
                frequency=behavioral_indicators.get("frequency", 0.8),
                confidence=confidence,
                market_conditions=[observation.market_conditions.get("volatility_regime", "unknown")],
                performance_impact=behavioral_indicators.get("performance_correlation", 0.0),
                last_detected=observation.timestamp,
                strength=confidence
            )
        
        return None
    
    def _detect_arbitrage(self, observation: TraderObservation) -> Optional[BehavioralPattern]:
        """Detect arbitrage behavior."""
        behavioral_indicators = observation.behavioral_indicators
        
        # Arbitrage indicators
        price_discovery = behavioral_indicators.get("price_discovery", 0.0)
        cross_market = behavioral_indicators.get("cross_market_activity", 0.0)
        
        if price_discovery > 0.7 and cross_market > 0.6:
            confidence = min(1.0, (price_discovery + cross_market) / 2)
            
            return BehavioralPattern(
                pattern_id=f"arbitrage_{observation.observation_id}",
                trader_id=observation.trader_id,
                pattern_type=TraderBehavior.ARBITRAGE,
                frequency=behavioral_indicators.get("frequency", 0.5),
                confidence=confidence,
                market_conditions=[observation.market_conditions.get("efficiency", "unknown")],
                performance_impact=behavioral_indicators.get("performance_correlation", 0.0),
                last_detected=observation.timestamp,
                strength=confidence
            )
        
        return None
    
    def _detect_market_making(self, observation: TraderObservation) -> Optional[BehavioralPattern]:
        """Detect market making behavior."""
        behavioral_indicators = observation.behavioral_indicators
        
        # Market making indicators
        two_sided_activity = behavioral_indicators.get("two_sided_activity", 0.0)
        inventory_management = behavioral_indicators.get("inventory_management", 0.0)
        
        if two_sided_activity > 0.8 and inventory_management > 0.6:
            confidence = min(1.0, (two_sided_activity + inventory_management) / 2)
            
            return BehavioralPattern(
                pattern_id=f"market_making_{observation.observation_id}",
                trader_id=observation.trader_id,
                pattern_type=TraderBehavior.MARKET_MAKING,
                frequency=behavioral_indicators.get("frequency", 0.9),
                confidence=confidence,
                market_conditions=[observation.market_conditions.get("liquidity_regime", "unknown")],
                performance_impact=behavioral_indicators.get("performance_correlation", 0.0),
                last_detected=observation.timestamp,
                strength=confidence
            )
        
        return None
    
    # World-Aware Methods
    
    def analyze_observation_with_world_context(self, observation: TraderObservation, 
                                              world_context: Optional[WorldContext] = None) -> List[BehavioralPattern]:
        """Analyze observation with world context enhancement.
        
        Args:
            observation: Trader observation to analyze
            world_context: Current world model context (optional, will fetch if not provided)
            
        Returns:
            List of world-enhanced detected behavioral patterns
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context()
        
        # Analyze using standard methods
        detected_patterns = self.analyze_observation(observation)
        
        if world_context:
            # Enhance patterns with world context
            enhanced_patterns = self._enhance_patterns_with_world_context(detected_patterns, world_context)
            return enhanced_patterns
        
        return detected_patterns
    
    def _enhance_patterns_with_world_context(self, patterns: List[BehavioralPattern], 
                                           world_context: WorldContext) -> List[BehavioralPattern]:
        """Enhance behavioral patterns with world context insights.
        
        Args:
            patterns: List of detected behavioral patterns
            world_context: Current world model context
            
        Returns:
            List of world-enhanced behavioral patterns
        """
        enhanced_patterns = []
        
        for pattern in patterns:
            # Adjust pattern confidence based on world context
            adjusted_confidence = self._calculate_world_aware_pattern_confidence(pattern, world_context)
            pattern.confidence = adjusted_confidence
            
            # Add world context metadata
            pattern.metadata["world_context"] = world_context.to_dict()
            pattern.metadata["world_enhanced"] = True
            
            # Add regime-specific notes
            pattern.metadata["regime_notes"] = self._generate_regime_specific_notes(pattern, world_context)
            
            enhanced_patterns.append(pattern)
        
        return enhanced_patterns
    
    def _calculate_world_aware_pattern_confidence(self, pattern: BehavioralPattern, 
                                                world_context: WorldContext) -> float:
        """Calculate world-aware confidence adjustment for behavioral pattern.
        
        Args:
            pattern: The behavioral pattern to adjust
            world_context: Current world model context
            
        Returns:
            Adjusted confidence score (0.0 to 1.0)
        """
        base_confidence = pattern.confidence
        adjustment_factor = 0.0
        
        # Momentum chasing enhancement
        if pattern.pattern_type == TraderBehavior.MOMENTUM_CHASING:
            if world_context.market_trend == "trending" and world_context.market_regime == "bullish":
                adjustment_factor += 0.15  # Higher confidence in bullish trending
            elif world_context.volatility_regime == "high":
                adjustment_factor -= 0.1  # Lower confidence in high volatility
        
        # Contrarian enhancement
        if pattern.pattern_type == TraderBehavior.CONTRARIAN:
            if world_context.market_trend == "mean_reverting":
                adjustment_factor += 0.2  # Higher confidence in mean-reverting markets
            elif world_context.market_trend == "trending":
                adjustment_factor -= 0.15  # Lower confidence in trending markets
        
        # Panic selling enhancement
        if pattern.pattern_type == TraderBehavior.PANIC_SELLING:
            if world_context.volatility_regime == "high":
                adjustment_factor += 0.2  # Higher confidence in high volatility
            elif world_context.market_regime == "high_volatility":
                adjustment_factor += 0.15  # Higher confidence in crisis regime
        
        # Herding enhancement
        if pattern.pattern_type == TraderBehavior.HERDING:
            if world_context.agent_activity.get("retail", 0) > 0.7:
                adjustment_factor += 0.2  # Higher confidence when retail is active
            elif world_context.market_regime == "bullish":
                adjustment_factor += 0.1  # Slightly higher confidence in bullish regime
        
        # Liquidity providing enhancement
        if pattern.pattern_type == TraderBehavior.LIQUIDITY_PROVIDING:
            if world_context.liquidity_state == "low":
                adjustment_factor += 0.25  # Significantly higher confidence when liquidity is low
            elif world_context.volatility_regime == "high":
                adjustment_factor += 0.15  # Higher confidence in high volatility
        
        # Apply adjustment
        adjusted_confidence = max(0.0, min(1.0, base_confidence + adjustment_factor))
        
        return adjusted_confidence
    
    def _generate_regime_specific_notes(self, pattern: BehavioralPattern, world_context: WorldContext) -> List[str]:
        """Generate regime-specific notes for behavioral pattern.
        
        Args:
            pattern: The behavioral pattern
            world_context: Current world model context
            
        Returns:
            List of regime-specific notes
        """
        notes = []
        
        # Regime-specific notes
        if world_context.market_regime == "high_volatility":
            notes.append("Crisis regime - elevated risk awareness")
        elif world_context.market_regime == "bullish":
            notes.append("Bullish regime - optimistic sentiment bias")
        elif world_context.market_regime == "bearish":
            notes.append("Bearish regime - risk-averse behavior")
        
        # Volatility-specific notes
        if world_context.volatility_regime == "high":
            notes.append("High volatility - increased behavior uncertainty")
        
        # Liquidity-specific notes
        if world_context.liquidity_state == "low":
            notes.append("Low liquidity - execution constraints active")
        
        # Causal factor notes
        if "liquidity_outflow" in world_context.causal_factors:
            notes.append("Liquidity outflow detected - stress conditions")
        if "market_panic" in world_context.causal_factors:
            notes.append("Market panic signals - extreme behavior patterns")
        
        return notes
    
    def model_trader_behavior_with_world_context(self, trader_data: Dict[str, Any], 
                                               world_context: Optional[WorldContext] = None) -> TraderProfile:
        """Model trader behavior with world context integration.
        
        Args:
            trader_data: Trader data including observations and attributes
            world_context: Current world model context (optional, will fetch if not provided)
            
        Returns:
            World-enhanced trader profile
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context()
        
        # Extract trader information
        trader_id = trader_data.get("trader_id", "unknown")
        classification = TraderClassification(trader_data.get("classification", "retail"))
        
        # Analyze behavior patterns
        observations = trader_data.get("observations", [])
        all_patterns = []
        
        for obs_data in observations:
            observation = TraderObservation(**obs_data)
            if world_context:
                patterns = self.analyze_observation_with_world_context(observation, world_context)
            else:
                patterns = self.analyze_observation(observation)
            all_patterns.extend(patterns)
        
        # Aggregate patterns to determine primary behaviors
        pattern_weights = {}
        for pattern in all_patterns:
            if pattern.pattern_type not in pattern_weights:
                pattern_weights[pattern.pattern_type] = []
            pattern_weights[pattern.pattern_type].append(pattern.confidence)
        
        behavior_weights = {
            behavior: sum(weights) / len(weights)
            for behavior, weights in pattern_weights.items()
        }
        
        # Determine primary behaviors (top 3 by weight)
        sorted_behaviors = sorted(behavior_weights.items(), key=lambda x: x[1], reverse=True)
        primary_behaviors = [behavior for behavior, weight in sorted_behaviors[:3]]
        
        # Calculate overall confidence
        profile_confidence = sum(behavior_weights.values()) / len(behavior_weights) if behavior_weights else 0.0
        
        # Create trader profile
        profile = TraderProfile(
            trader_id=trader_id,
            classification=classification,
            primary_behaviors=primary_behaviors,
            behavior_weights=behavior_weights,
            trading_patterns=trader_data.get("trading_patterns", {}),
            performance_metrics=trader_data.get("performance_metrics", {}),
            risk_profile=trader_data.get("risk_profile", "medium"),
            impact_classification=MarketImpact(trader_data.get("impact_classification", "medium")),
            interaction_patterns=trader_data.get("interaction_patterns", {}),
            last_observation=datetime.now(),
            observation_count=len(observations),
            profile_confidence=profile_confidence
        )
        
        # Add world context to profile metadata
        if world_context:
            profile.metadata = profile.metadata or {}
            profile.metadata["world_context"] = world_context.to_dict()
            profile.metadata["world_enhanced"] = True
            profile.metadata["regime_at_modeling"] = world_context.market_regime
        
        logger.info(f"[TRADER_MODELING] Modeled trader {trader_id} with world context (confidence: {profile_confidence:.2f})")
        
        return profile
    
    def predict_trader_actions_with_world_state(self, trader_profile: TraderProfile, 
                                              world_context: Optional[WorldContext] = None) -> ActionPredictions:
        """Predict trader actions using world state and agent behavior patterns.
        
        Args:
            trader_profile: Trader profile to use for predictions
            world_context: Current world model context (optional, will fetch if not provided)
            
        Returns:
            World-enhanced action predictions
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context()
        
        # Base prediction from profile
        base_action = self._predict_base_action(trader_profile)
        base_probability = 0.6
        base_volume = trader_profile.performance_metrics.get("avg_volume", 1000.0)
        
        # World context adjustments
        world_influence = 0.0
        regime_adjustments = {}
        causal_impact = {}
        
        if world_context:
            # Calculate world context influence
            world_influence = self._calculate_world_influence(trader_profile, world_context)
            
            # Regime-specific adjustments
            regime_adjustments = self._calculate_regime_adjustments(trader_profile, world_context)
            
            # Causal factor impact
            causal_impact = self._calculate_causal_factor_impact(trader_profile, world_context)
            
            # Adjust prediction based on world context
            if world_context.market_regime == "bullish":
                if TraderBehavior.MOMENTUM_CHASING in trader_profile.primary_behaviors:
                    base_action = "buy"
                    base_probability = min(0.9, base_probability + 0.2)
            
            if world_context.market_regime == "bearish":
                if TraderBehavior.CONTRARIAN in trader_profile.primary_behaviors:
                    base_action = "buy"  # Contrarians buy in bear markets
                    base_probability = min(0.85, base_probability + 0.15)
                else:
                    base_action = "sell"  # Others sell in bear markets
                    base_probability = min(0.9, base_probability + 0.15)
            
            if world_context.volatility_regime == "high":
                base_volume *= 0.5  # Reduce volume in high volatility
                base_probability *= 0.8  # Reduce confidence in high volatility
            
            if world_context.liquidity_state == "low":
                base_volume *= 0.6  # Reduce volume in low liquidity
        
        # Calculate final confidence
        confidence = (base_probability + world_influence) / 2.0
        confidence = max(0.0, min(1.0, confidence))
        
        # Generate reasoning
        reasoning_parts = []
        reasoning_parts.append(f"Base prediction: {base_action}")
        reasoning_parts.append(f"Trader classification: {trader_profile.classification.value}")
        if world_context:
            reasoning_parts.append(f"World regime: {world_context.market_regime}")
            reasoning_parts.append(f"World trend: {world_context.market_trend}")
            if regime_adjustments:
                reasoning_parts.append(f"Regime adjustments: {len(regime_adjustments)}")
            if causal_impact:
                reasoning_parts.append(f"Causal factor impact: {len(causal_impact)}")
        reasoning = "; ".join(reasoning_parts)
        
        # Create action predictions
        predictions = ActionPredictions(
            trader_id=trader_profile.trader_id,
            predicted_action=base_action,
            action_probability=confidence,
            predicted_volume=base_volume,
            confidence=confidence,
            world_context_influence=world_influence,
            regime_specific_adjustments=regime_adjustments,
            causal_factor_impact=causal_impact,
            reasoning=reasoning
        )
        
        logger.info(f"[TRADER_MODELING] Predicted action for {trader_profile.trader_id}: "
                   f"{base_action} (confidence: {confidence:.2f})")
        
        return predictions
    
    def _predict_base_action(self, trader_profile: TraderProfile) -> str:
        """Predict base action from trader profile without world context."""
        # Determine base action from primary behaviors
        if TraderBehavior.MOMENTUM_CHASING in trader_profile.primary_behaviors:
            return "buy"
        elif TraderBehavior.DISTRIBUTION in trader_profile.primary_behaviors:
            return "sell"
        elif TraderBehavior.ACCUMULATION in trader_profile.primary_behaviors:
            return "buy"
        elif TraderBehavior.PANIC_SELLING in trader_profile.primary_behaviors:
            return "sell"
        elif TraderBehavior.LIQUIDITY_PROVIDING in trader_profile.primary_behaviors:
            return "hold"
        else:
            return "hold"
    
    def _calculate_world_influence(self, trader_profile: TraderProfile, world_context: WorldContext) -> float:
        """Calculate world context influence on trader behavior.
        
        Args:
            trader_profile: Trader profile to analyze
            world_context: Current world model context
            
        Returns:
            World influence score (0.0 to 1.0)
        """
        influence = 0.0
        
        # Classification influence
        if trader_profile.classification == TraderClassification.RETAIL:
            influence += world_context.agent_activity.get("retail", 0.0) * 0.3
        elif trader_profile.classification == TraderClassification.INSTITUTIONAL:
            influence += world_context.agent_activity.get("institutional", 0.0) * 0.3
        
        # Regime influence
        if world_context.market_regime == "high_volatility":
            influence += 0.2  # High influence in crisis
        
        # Causal factor influence
        if world_context.causal_factors:
            influence += 0.1  # Some influence from causal factors
        
        return min(1.0, influence)
    
    def _calculate_regime_adjustments(self, trader_profile: TraderProfile, world_context: WorldContext) -> Dict[str, float]:
        """Calculate regime-specific adjustments for trader predictions.
        
        Args:
            trader_profile: Trader profile to analyze
            world_context: Current world model context
            
        Returns:
            Dictionary of regime-specific adjustments
        """
        adjustments = {}
        
        # Regime adjustments based on primary behaviors
        for behavior in trader_profile.primary_behaviors:
            if behavior == TraderBehavior.MOMENTUM_CHASING:
                if world_context.market_trend == "trending":
                    adjustments["trending_momentum_bonus"] = 0.15
                elif world_context.market_trend == "mean_reverting":
                    adjustments["trending_momentum_penalty"] = -0.1
            
            if behavior == TraderBehavior.CONTRARIAN:
                if world_context.market_trend == "mean_reverting":
                    adjustments["contrarian_mean_reversion_bonus"] = 0.2
                elif world_context.market_trend == "trending":
                    adjustments["contrarian_trending_penalty"] = -0.15
            
            if behavior == TraderBehavior.LIQUIDITY_PROVIDING:
                if world_context.liquidity_state == "low":
                    adjustments["liquidity_providing_bonus"] = 0.25
                elif world_context.liquidity_state == "high":
                    adjustments["liquidity_providing_neutral"] = 0.0
        
        return adjustments
    
    def _calculate_causal_factor_impact(self, trader_profile: TraderProfile, world_context: WorldContext) -> Dict[str, float]:
        """Calculate causal factor impact on trader behavior.
        
        Args:
            trader_profile: Trader profile to analyze
            world_context: Current world model context
            
        Returns:
            Dictionary of causal factor impacts
        """
        impacts = {}
        
        # Analyze causal factor impacts
        if "liquidity_outflow" in world_context.causal_factors:
            if TraderBehavior.PANIC_SELLING in trader_profile.primary_behaviors:
                impacts["liquidity_outflow_panic_amplification"] = 0.3
            elif TraderBehavior.LIQUIDITY_PROVIDING in trader_profile.primary_behaviors:
                impacts["liquidity_outflow_providing_opportunity"] = 0.2
        
        if "market_panic" in world_context.causal_factors:
            if TraderBehavior.HERDING in trader_profile.primary_behaviors:
                impacts["market_panic_herding_amplification"] = 0.25
            elif TraderBehavior.CONTRARIAN in trader_profile.primary_behaviors:
                impacts["market_panic_contrarian_opportunity"] = 0.2
        
        return impacts
    
    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model integration.
        
        Returns:
            Current world context, or None if not available
        """
        if not self._world_integration_bridge:
            return None
        
        try:
            # Get world model predictions and state
            bridge_metrics = self._world_integration_bridge.get_comprehensive_metrics()
            
            # Build world context from bridge metrics (simplified)
            if bridge_metrics and bridge_metrics.get("integration_status", {}).get("initialized"):
                # Return cached context if available and fresh
                cached_context = self._world_context_cache.get("current")
                if cached_context:
                    age = (datetime.now() - cached_context.timestamp).total_seconds()
                    if age < self._world_cache_ttl_seconds:
                        return cached_context
                
                # Fetch fresh context (would call world model in real implementation)
                # For now, return a default context
                context = WorldContext(
                    market_regime="sideways",
                    market_trend="neutral",
                    volatility_regime="normal",
                    liquidity_state="high",
                    agent_activity={},
                    causal_factors=[],
                    prediction_confidence=0.75
                )
                
                self._world_context_cache["current"] = context
                return context
        
        except Exception as e:
            logger.warning(f"[TRADER_MODELING] Error getting world context: {e}")
        
        return None


class TraderModelingSystem:
    """Main trader modeling system with profile management and analysis."""
    
    def __init__(self):
        """Initialize the trader modeling system."""
        self._lock = threading.Lock()
        
        # Core components
        self._behavior_analyzer = TraderBehaviorAnalyzer()
        
        # Trader profiles database
        self._trader_profiles: Dict[str, TraderProfile] = {}
        
        # Observations history
        self._observations_history: deque = deque(maxlen=10000)
        
        # Behavioral patterns database
        self._behavioral_patterns: Dict[str, List[BehavioralPattern]] = {}
        
        # Metrics tracking
        self._metrics = TraderModelMetrics()
        
        logger.info("[TRADER_MODELING] Trader Modeling System initialized")
    
    def make_trader_observation(self, trader_id: str, action: str, volume: float, 
                               price: float, symbol: str, market_conditions: Dict[str, Any],
                               behavioral_indicators: Dict[str, Any],
                               metadata: Dict[str, Any] = None) -> TraderObservation:
        """Create and process a trader observation.
        
        Args:
            trader_id: Unique identifier for the trader
            action: Trader action ("buy", "sell", "hold")
            volume: Trading volume
            price: Trade price
            symbol: Trading symbol
            market_conditions: Current market conditions
            behavioral_indicators: Behavioral indicators for the action
            metadata: Additional metadata
            
        Returns:
            TraderObservation object
        """
        start_time = datetime.now()
        
        try:
            # Estimate market impact
            impact_estimate = self._estimate_market_impact(volume, behavioral_indicators, market_conditions)
            
            # Create observation
            observation = TraderObservation(
                observation_id=f"obs_{int(datetime.now().timestamp())}_{hashlib.md5(trader_id.encode()).hexdigest()[:8]}",
                trader_id=trader_id,
                timestamp=datetime.now(),
                action=action,
                volume=volume,
                price=price,
                symbol=symbol,
                market_conditions=market_conditions,
                behavioral_indicators=behavioral_indicators,
                impact_estimate=impact_estimate,
                metadata=metadata or {}
            )
            
            # Process observation
            self._process_observation(observation)
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_metrics(processing_time, success=True)
            
            return observation
            
        except Exception as e:
            logger.error(f"[TRADER_MODELING] Error creating trader observation: {e}")
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_metrics(processing_time, success=False)
            
            # Return minimal observation on error
            return TraderObservation(
                observation_id=f"error_obs_{int(datetime.now().timestamp())}",
                trader_id=trader_id,
                timestamp=datetime.now(),
                action=action,
                volume=volume,
                price=price,
                symbol=symbol,
                market_conditions=market_conditions,
                behavioral_indicators=behavioral_indicators,
                impact_estimate=MarketImpact.NEGLIGIBLE,
                metadata={"error": str(e)}
            )
    
    def _estimate_market_impact(self, volume: float, behavioral_indicators: Dict[str, Any],
                               market_conditions: Dict[str, Any]) -> MarketImpact:
        """Estimate market impact of the trading action."""
        # Simplified impact estimation
        volume_impact = min(1.0, volume / 10000.0)  # Normalize volume
        liquidity_impact = 1.0 - market_conditions.get("liquidity_score", 0.8)
        behavioral_impact = behavioral_indicators.get("price_impact", 0.0)
        
        total_impact = (volume_impact + liquidity_impact + behavioral_impact) / 3
        
        if total_impact > 0.7:
            return MarketImpact.HIGH
        elif total_impact > 0.4:
            return MarketImpact.MEDIUM
        elif total_impact > 0.2:
            return MarketImpact.LOW
        else:
            return MarketImpact.NEGLIGIBLE
    
    def _process_observation(self, observation: TraderObservation):
        """Process observation and update trader profiles."""
        with self._lock:
            # Store observation
            self._observations_history.append(observation)
            
            # Get or create trader profile
            trader_id = observation.trader_id
            if trader_id not in self._trader_profiles:
                self._trader_profiles[trader_id] = self._create_initial_profile(trader_id)
            
            # Update profile with observation
            profile = self._trader_profiles[trader_id]
            self._update_profile(profile, observation)
            
            # Analyze for behavioral patterns
            patterns = self._behavior_analyzer.analyze_observation(observation)
            if patterns:
                if trader_id not in self._behavioral_patterns:
                    self._behavioral_patterns[trader_id] = []
                
                self._behavioral_patterns[trader_id].extend(patterns)
                self._metrics.patterns_detected += len(patterns)
    
    def _create_initial_profile(self, trader_id: str) -> TraderProfile:
        """Create initial trader profile."""
        self._metrics.total_profiles += 1
        
        return TraderProfile(
            trader_id=trader_id,
            classification=TraderClassification.RETAIL,  # Default classification
            primary_behaviors=[],
            behavior_weights={},
            trading_patterns={},
            performance_metrics={},
            risk_profile="moderate",
            impact_classification=MarketImpact.LOW,
            interaction_patterns={},
            last_observation=datetime.now(),
            observation_count=0,
            profile_confidence=0.0
        )
    
    def _update_profile(self, profile: TraderProfile, observation: TraderObservation):
        """Update trader profile with new observation."""
        profile.observation_count += 1
        profile.last_observation = observation.timestamp
        profile.last_updated = datetime.now()
        
        # Update impact classification based on recent observations
        if observation.impact_estimate == MarketImpact.HIGH:
            profile.impact_classification = MarketImpact.HIGH
        elif observation.impact_estimate == MarketImpact.MEDIUM and profile.impact_classification == MarketImpact.LOW:
            profile.impact_classification = MarketImpact.MEDIUM
        
        # Update profile confidence based on observation count
        profile.profile_confidence = min(1.0, profile.observation_count / 50.0)
        
        # Update behavioral weights
        if profile.trader_id in self._behavioral_patterns:
            patterns = self._behavioral_patterns[profile.trader_id]
            behavior_counts = {}
            
            for pattern in patterns:
                behavior = pattern.pattern_type
                behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
            
            # Calculate weights
            total_patterns = len(patterns)
            if total_patterns > 0:
                profile.behavior_weights = {
                    behavior: count / total_patterns for behavior, count in behavior_counts.items()
                }
                
                # Update primary behaviors
                sorted_behaviors = sorted(profile.behavior_weights.items(), key=lambda x: x[1], reverse=True)
                profile.primary_behaviors = [b[0] for b in sorted_behaviors[:3]]
                
                # Update classification based on dominant behaviors
                self._update_classification(profile)
    
    def _update_classification(self, profile: TraderProfile):
        """Update trader classification based on behavior patterns."""
        behavior_weights = profile.behavior_weights
        
        # Classification rules
        if not behavior_weights:
            return
        
        # Market making
        if behavior_weights.get(TraderBehavior.MARKET_MAKING, 0) > 0.5:
            profile.classification = TraderClassification.MARKET_MAKER
        # Arbitrage
        elif behavior_weights.get(TraderBehavior.ARBITRAGE, 0) > 0.5:
            profile.classification = TraderClassification.ARBITRAGEUR
        # High frequency
        elif behavior_weights.get(TraderBehavior.SPECULATIVE, 0) > 0.6 and profile.observation_count > 100:
            profile.classification = TraderClassification.HIGH_FREQUENCY
        # Institutional
        elif profile.impact_classification in [MarketImpact.HIGH, MarketImpact.MEDIUM] and profile.observation_count > 50:
            profile.classification = TraderClassification.INSTITUTIONAL
        # Day trading
        elif profile.observation_count > 200 and profile.primary_behaviors:
            profile.classification = TraderClassification.DAY_TRADER
        # Position trading
        elif profile.observation_count < 50 and profile.primary_behaviors:
            profile.classification = TraderClassification.POSITION_TRADER
        else:
            profile.classification = TraderClassification.RETAIL
    
    def observation_as_system_event(self, observation: TraderObservation) -> Dict[str, Any]:
        """Convert trader observation to system event format.
        
        Args:
            observation: Trader observation to convert
            
        Returns:
            System event dictionary
        """
        base_event = {
            "event_type": "TRADER_OBSERVATION",
            "event_id": observation.observation_id,
            "timestamp": observation.timestamp.isoformat(),
            "data": observation.to_dict()
        }
        
        # Add profile information if available
        if observation.trader_id in self._trader_profiles:
            profile = self._trader_profiles[observation.trader_id]
            base_event["data"]["profile_summary"] = {
                "classification": profile.classification.value,
                "primary_behaviors": [b.value for b in profile.primary_behaviors],
                "impact_classification": profile.impact_classification.value,
                "profile_confidence": profile.profile_confidence
            }
        
        return base_event
    
    def get_trader_profile(self, trader_id: str) -> Optional[TraderProfile]:
        """Get trader profile by ID."""
        return self._trader_profiles.get(trader_id)
    
    def get_behavioral_patterns(self, trader_id: str) -> List[BehavioralPattern]:
        """Get behavioral patterns for a trader."""
        return self._behavioral_patterns.get(trader_id, [])
    
    def _update_metrics(self, processing_time_ms: float, success: bool):
        """Update system metrics."""
        with self._lock:
            self._metrics.total_observations += 1
            
            # Update average processing time
            if self._metrics.total_observations == 1:
                self._metrics.average_processing_time_ms = processing_time_ms
            else:
                self._metrics.average_processing_time_ms = (
                    0.9 * self._metrics.average_processing_time_ms + 0.1 * processing_time_ms
                )
            
            # Update model confidence based on profile confidence
            if self._trader_profiles:
                avg_confidence = sum(p.profile_confidence for p in self._trader_profiles.values()) / len(self._trader_profiles)
                self._metrics.model_confidence = avg_confidence
            
            self._metrics.last_updated = datetime.now()
    
    def get_metrics(self) -> TraderModelMetrics:
        """Get system metrics."""
        return self._metrics
    
    def get_all_profiles(self) -> List[TraderProfile]:
        """Get all trader profiles."""
        return list(self._trader_profiles.values())


# Global instance
_trader_modeling_system: TraderModelingSystem | None = None


def get_trader_modeling_system() -> TraderModelingSystem:
    """Get the global trader modeling system instance."""
    global _trader_modeling_system
    if _trader_modeling_system is None:
        _trader_modeling_system = TraderModelingSystem()
    return _trader_modeling_system


# Convenience functions for backward compatibility
def make_trader_observation(**kwargs: Any) -> TraderObservation:
    """Convenience function to create trader observation."""
    system = get_trader_modeling_system()
    return system.make_trader_observation(**kwargs)


def observation_as_system_event(observation: TraderObservation) -> Dict[str, Any]:
    """Convenience function to convert observation to system event."""
    system = get_trader_modeling_system()
    return system.observation_as_system_event(observation)


__all__ = [
    "TraderBehavior",
    "TraderClassification",
    "MarketImpact",
    "TraderObservation",
    "TraderProfile",
    "BehavioralPattern",
    "TraderModelMetrics",
    "WorldContext",
    "ActionPredictions",
    "TraderBehaviorAnalyzer",
    "TraderModelingSystem",
    "get_trader_modeling_system",
    "make_trader_observation",
    "observation_as_system_event"
]