"""Operator Understanding Layer - Advanced Operator Intent Classification and Behavior Prediction.

This module provides sophisticated operator understanding capabilities that go beyond
basic intent classification to include behavioral modeling, pattern recognition, and
predictive analytics.
"""

from __future__ import annotations

import logging
import threading
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict, deque
import hashlib

logger = logging.getLogger(__name__)


class OperatorIntent(str, Enum):
    """Advanced operator intent classification."""
    AGGRESSIVE_TRADING = "AGGRESSIVE_TRADING"
    CONSERVATIVE_TRADING = "CONSERVATIVE_TRADING"
    SPECULATIVE_POSITIONING = "SPECULATIVE_POSITIONING"
    HEDGING_STRATEGY = "HEDGING_STRATEGY"
    MARKET_MAKING = "MARKET_MAKING"
    ARBITRAGE_SEEKING = "ARBITRAGE_SEEKING"
    LIQUIDITY_PROVIDING = "LIQUIDITY_PROVIDING"
    RISK_MANAGEMENT = "RISK_MANAGEMENT"
    PORTFOLIO_REBALANCING = "PORTFOLIO_REBALANCING"
    EXPERIMENTAL_TRADING = "EXPERIMENTAL_TRADING"
    UNKNOWN = "UNKNOWN"


class OperatorRiskProfile(str, Enum):
    """Operator risk profile classification."""
    ULTRA_CONSERVATIVE = "ULTRA_CONSERVATIVE"
    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"
    ULTRA_AGGRESSIVE = "ULTRA_AGGRESSIVE"
    UNPREDICTABLE = "UNPREDICTABLE"


@dataclass
class OperatorAction:
    """Represents a single operator action."""
    action_id: str
    operator_id: str
    action_type: str  # "buy", "sell", "adjust_position", "change_strategy"
    symbol: str
    quantity: float
    price: float
    timestamp: float
    market_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperatorProfile:
    """Comprehensive operator profile."""
    operator_id: str
    risk_profile: OperatorRiskProfile
    preferred_intents: List[OperatorIntent]
    average_position_size: float
    average_holding_period: float
    success_rate: float
    volatility_tolerance: float
    market_regime_preference: str
    last_updated: float
    behavior_patterns: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentPrediction:
    """Predicted operator intent with confidence."""
    predicted_intent: OperatorIntent
    confidence: float
    alternative_intents: List[Tuple[OperatorIntent, float]]
    reasoning: str
    features_used: List[str]


@dataclass
class BehaviorPrediction:
    """Predicted operator behavior."""
    predicted_action_type: str
    probability: float
    expected_position_size: float
    expected_timing: float
    risk_level: float
    confidence_interval: Tuple[float, float]


class OperatorUnderstanding:
    """Advanced operator understanding with sophisticated behavioral analysis."""

    def __init__(self, history_window: int = 1000):
        self._lock = threading.Lock()
        self._history_window = history_window
        self._action_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_window))
        self._operator_profiles: Dict[str, OperatorProfile] = {}
        self._intent_classifier = IntentClassifier()
        self._behavior_predictor = BehaviorPredictor()
        self._pattern_detector = PatternDetector()
        self._risk_assessor = RiskAssessor()
        self._anomaly_detector = AnomalyDetector()
        self._initialized = False

    def start(self) -> bool:
        """Start operator understanding system."""
        logger.info("[OPERATOR_UNDERSTANDING] Starting advanced operator understanding...")
        self._initialized = True
        logger.info("[OPERATOR_UNDERSTANDING] Advanced operator understanding started")
        return True

    def stop(self) -> bool:
        """Stop operator understanding system."""
        logger.info("[OPERATOR_UNDERSTANDING] Stopping advanced operator understanding...")
        self._initialized = False
        logger.info("[OPERATOR_UNDERSTANDING] Advanced operator understanding stopped")
        return True

    def record_operator_action(self, action: OperatorAction) -> None:
        """Record an operator action for analysis."""
        with self._lock:
            self._action_history[action.operator_id].append(action)
            
            # Update operator profile periodically
            if len(self._action_history[action.operator_id]) % 10 == 0:
                self._update_operator_profile(action.operator_id)

    def classify_operator_intent(self, operator_id: str, recent_actions: List[OperatorAction]) -> IntentPrediction:
        """Classify operator intent with advanced analysis."""
        logger.info(f"[OPERATOR_UNDERSTANDING] Classifying intent for operator {operator_id}")
        
        if not recent_actions:
            return IntentPrediction(
                predicted_intent=OperatorIntent.UNKNOWN,
                confidence=0.0,
                alternative_intents=[],
                reasoning="No action history available",
                features_used=[]
            )

        # Extract features for classification
        features = self._extract_intent_features(recent_actions)
        
        # Classify intent using multiple methods
        primary_intent, confidence, alternatives = self._intent_classifier.classify(features, recent_actions)
        
        # Generate reasoning
        reasoning = self._generate_intent_reasoning(primary_intent, features, recent_actions)
        
        return IntentPrediction(
            predicted_intent=primary_intent,
            confidence=confidence,
            alternative_intents=alternatives,
            reasoning=reasoning,
            features_used=list(features.keys())
        )

    def predict_operator_behavior(self, operator_id: str, market_state: Dict[str, Any]) -> BehaviorPrediction:
        """Predict operator behavior with advanced modeling."""
        logger.info(f"[OPERATOR_UNDERSTANDING] Predicting behavior for operator {operator_id}")
        
        with self._lock:
            if operator_id not in self._operator_profiles:
                return BehaviorPrediction(
                    predicted_action_type="unknown",
                    probability=0.0,
                    expected_position_size=0.0,
                    expected_timing=0.0,
                    risk_level=0.0,
                    confidence_interval=(0.0, 0.0)
                )
            
            profile = self._operator_profiles[operator_id]
            recent_actions = list(self._action_history[operator_id])
            
            if not recent_actions:
                return BehaviorPrediction(
                    predicted_action_type="unknown",
                    probability=0.0,
                    expected_position_size=profile.average_position_size,
                    expected_timing=0.0,
                    risk_level=0.5,
                    confidence_interval=(0.0, 1.0)
                )

        # Predict behavior using multiple models
        prediction = self._behavior_predictor.predict(profile, recent_actions, market_state)
        
        return prediction

    def detect_operator_patterns(self, operator_id: str) -> Dict[str, Any]:
        """Detect patterns in operator activity with advanced pattern recognition."""
        logger.info(f"[OPERATOR_UNDERSTANDING] Detecting patterns for operator {operator_id}")
        
        with self._lock:
            if operator_id not in self._action_history:
                return {"error": "No action history available"}
            
            actions = list(self._action_history[operator_id])
        
        if len(actions) < 5:
            return {"error": "Insufficient action history"}
        
        # Detect various patterns
        temporal_patterns = self._pattern_detector.detect_temporal_patterns(actions)
        size_patterns = self._pattern_detector.detect_size_patterns(actions)
        symbol_patterns = self._pattern_detector.detect_symbol_patterns(actions)
        market_condition_patterns = self._pattern_detector.detect_market_condition_patterns(actions)
        
        return {
            "operator_id": operator_id,
            "temporal_patterns": temporal_patterns,
            "size_patterns": size_patterns,
            "symbol_patterns": symbol_patterns,
            "market_condition_patterns": market_condition_patterns,
            "overall_pattern_strength": self._calculate_pattern_strength(temporal_patterns, size_patterns, symbol_patterns)
        }

    def assess_operator_risk(self, operator_id: str, current_market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive operator risk assessment."""
        logger.info(f"[OPERATOR_UNDERSTANDING] Assessing risk for operator {operator_id}")
        
        with self._lock:
            if operator_id not in self._operator_profiles:
                return {"risk_level": "unknown", "confidence": 0.0}
            
            profile = self._operator_profiles[operator_id]
            recent_actions = list(self._action_history[operator_id])
        
        # Multi-dimensional risk assessment
        risk_assessment = self._risk_assessor.assess_risk(profile, recent_actions, current_market_state)
        
        return risk_assessment

    def detect_operator_anomalies(self, operator_id: str) -> List[Dict[str, Any]]:
        """Detect anomalous operator behavior."""
        logger.info(f"[OPERATOR_UNDERSTANDING] Detecting anomalies for operator {operator_id}")
        
        with self._lock:
            if operator_id not in self._action_history:
                return []
            
            actions = list(self._action_history[operator_id])
        
        if len(actions) < 10:
            return []
        
        anomalies = self._anomaly_detector.detect_anomalies(actions)
        
        return anomalies

    def _extract_intent_features(self, actions: List[OperatorAction]) -> Dict[str, float]:
        """Extract advanced features for intent classification."""
        if not actions:
            return {}
        
        features = {}
        
        # Basic temporal features
        timestamps = [a.timestamp for a in actions]
        features["action_frequency"] = len(actions) / (max(timestamps) - min(timestamps) + 1)
        features["time_between_actions"] = np.mean([timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)])
        
        # Position size features
        quantities = [a.quantity for a in actions]
        features["avg_quantity"] = np.mean(quantities)
        features["std_quantity"] = np.std(quantities)
        features["max_quantity"] = max(quantities)
        features["quantity_trend"] = self._calculate_trend(quantities)
        
        # Price features
        prices = [a.price for a in actions]
        features["avg_price"] = np.mean(prices)
        features["price_volatility"] = np.std(prices) / np.mean(prices)
        
        # Action type distribution
        action_types = [a.action_type for a in actions]
        for action_type in set(action_types):
            features[f"action_type_{action_type}"] = action_types.count(action_type) / len(actions)
        
        # Symbol diversity
        symbols = [a.symbol for a in actions]
        features["symbol_diversity"] = len(set(symbols)) / len(symbols)
        
        # Market context features
        market_contexts = [a.market_context for a in actions if a.market_context]
        if market_contexts:
            features["avg_volatility"] = np.mean([ctx.get("volatility", 0) for ctx in market_contexts])
            features["avg_trend"] = np.mean([ctx.get("trend", 0) for ctx in market_contexts])
        
        return features

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend as linear regression slope."""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Linear regression
        slope = np.polyfit(x, y, 1)[0]
        return slope

    def _update_operator_profile(self, operator_id: str) -> None:
        """Update operator profile with latest behavior analysis."""
        actions = list(self._action_history[operator_id])
        
        if len(actions) < 5:
            return
        
        # Calculate profile metrics
        quantities = [a.quantity for a in actions]
        holding_periods = []
        for i in range(1, len(actions)):
            if actions[i].action_type == "sell" and actions[i-1].action_type == "buy":
                holding_periods.append(actions[i].timestamp - actions[i-1].timestamp)
        
        # Assess risk profile
        risk_profile = self._assess_risk_profile(actions)
        
        # Determine preferred intents
        recent_actions = actions[-20:] if len(actions) >= 20 else actions
        intent_prediction = self.classify_operator_intent(operator_id, recent_actions)
        preferred_intents = [intent_prediction.predicted_intent]
        preferred_intents.extend([intent for intent, _ in intent_prediction.alternative_intents[:2]])
        
        # Calculate success rate (simplified)
        successful_actions = sum(1 for a in actions if a.metadata.get("success", False))
        success_rate = successful_actions / len(actions) if actions else 0.0
        
        # Update profile
        self._operator_profiles[operator_id] = OperatorProfile(
            operator_id=operator_id,
            risk_profile=risk_profile,
            preferred_intents=preferred_intents,
            average_position_size=np.mean(quantities),
            average_holding_period=np.mean(holding_periods) if holding_periods else 0.0,
            success_rate=success_rate,
            volatility_tolerance=np.std(quantities) / np.mean(quantities) if quantities else 0.0,
            market_regime_preference=self._determine_regime_preference(actions),
            last_updated=time.time(),
            behavior_patterns={}
        )

    def _assess_risk_profile(self, actions: List[OperatorAction]) -> OperatorRiskProfile:
        """Assess operator risk profile based on behavior."""
        if len(actions) < 5:
            return OperatorRiskProfile.MODERATE
        
        quantities = [a.quantity for a in actions]
        avg_quantity = np.mean(quantities)
        std_quantity = np.std(quantities)
        
        # Calculate volatility tolerance
        volatility_tolerance = std_quantity / avg_quantity if avg_quantity > 0 else 0.0
        
        # Assess action frequency
        timestamps = [a.timestamp for a in actions]
        action_frequency = len(actions) / (max(timestamps) - min(timestamps) + 1)
        
        # Determine risk profile
        if volatility_tolerance < 0.1 and action_frequency < 0.1:
            return OperatorRiskProfile.ULTRA_CONSERVATIVE
        elif volatility_tolerance < 0.2 and action_frequency < 0.2:
            return OperatorRiskProfile.CONSERVATIVE
        elif volatility_tolerance < 0.4 and action_frequency < 0.5:
            return OperatorRiskProfile.MODERATE
        elif volatility_tolerance < 0.6 and action_frequency < 1.0:
            return OperatorRiskProfile.AGGRESSIVE
        elif volatility_tolerance < 1.0:
            return OperatorRiskProfile.ULTRA_AGGRESSIVE
        else:
            return OperatorRiskProfile.UNPREDICTABLE

    def _determine_regime_preference(self, actions: List[OperatorAction]) -> str:
        """Determine preferred market regime based on historical performance."""
        # Simplified regime preference determination
        market_contexts = [a.market_context for a in actions if a.market_context]
        if not market_contexts:
            return "neutral"
        
        # Count actions in different regimes
        regime_counts = defaultdict(int)
        for ctx in market_contexts:
            regime = ctx.get("regime", "neutral")
            regime_counts[regime] += 1
        
        # Return most preferred regime
        if regime_counts:
            return max(regime_counts.items(), key=lambda x: x[1])[0]
        return "neutral"

    def _generate_intent_reasoning(self, intent: OperatorIntent, features: Dict[str, float], actions: List[OperatorAction]) -> str:
        """Generate human-readable reasoning for intent classification."""
        reasoning_parts = []
        
        # Action-based reasoning
        if intent == OperatorIntent.AGGRESSIVE_TRADING:
            reasoning_parts.append(f"High action frequency ({features.get('action_frequency', 0):.2f}) and large position sizes")
        elif intent == OperatorIntent.CONSERVATIVE_TRADING:
            reasoning_parts.append(f"Low action frequency ({features.get('action_frequency', 0):.2f}) and conservative position sizing")
        elif intent == OperatorIntent.SPECULATIVE_POSITIONING:
            reasoning_parts.append("High symbol diversity and experimental trading patterns")
        elif intent == OperatorIntent.HEDGING_STRATEGY:
            reasoning_parts.append("Balanced buy/sell ratio with correlation-based positioning")
        
        # Add feature-based insights
        if features.get('quantity_trend', 0) > 0:
            reasoning_parts.append("Increasing position sizes over time")
        elif features.get('quantity_trend', 0) < 0:
            reasoning_parts.append("Decreasing position sizes over time")
        
        if features.get('price_volatility', 0) > 0.5:
            reasoning_parts.append("High price volatility tolerance")
        
        # Action type distribution
        buy_ratio = features.get('action_type_buy', 0)
        if buy_ratio > 0.7:
            reasoning_parts.append("Predominantly buying activity")
        elif buy_ratio < 0.3:
            reasoning_parts.append("Predominantly selling activity")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "Based on overall behavioral patterns"

    def _calculate_pattern_strength(self, temporal_patterns: Dict, size_patterns: Dict, symbol_patterns: Dict) -> float:
        """Calculate overall pattern strength."""
        strengths = []
        
        # Extract pattern strengths
        for pattern_dict in [temporal_patterns, size_patterns, symbol_patterns]:
            if "pattern_strength" in pattern_dict:
                strengths.append(pattern_dict["pattern_strength"])
        
        return np.mean(strengths) if strengths else 0.0

    def get_operator_profile(self, operator_id: str) -> Optional[OperatorProfile]:
        """Get operator profile."""
        with self._lock:
            return self._operator_profiles.get(operator_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get operator understanding statistics."""
        with self._lock:
            return {
                "total_operators": len(self._operator_profiles),
                "total_actions": sum(len(history) for history in self._action_history.values()),
                "profiles_by_risk": self._count_by_risk_profile(),
                "avg_actions_per_operator": np.mean([len(h) for h in self._action_history.values()]) if self._action_history else 0.0
            }

    def _count_by_risk_profile(self) -> Dict[str, int]:
        """Count operators by risk profile."""
        counts = defaultdict(int)
        for profile in self._operator_profiles.values():
            counts[profile.risk_profile.value] += 1
        return dict(counts)


class IntentClassifier:
    """Advanced intent classification using multiple techniques."""
    
    def classify(self, features: Dict[str, float], actions: List[OperatorAction]) -> Tuple[OperatorIntent, float, List[Tuple[OperatorIntent, float]]]:
        """Classify intent using ensemble of methods."""
        # Use rule-based classification
        primary_intent, confidence = self._rule_based_classification(features, actions)
        
        # Generate alternative intents
        alternatives = self._generate_alternatives(primary_intent, features, confidence)
        
        return primary_intent, confidence, alternatives
    
    def _rule_based_classification(self, features: Dict[str, float], actions: List[OperatorAction]) -> Tuple[OperatorIntent, float]:
        """Rule-based intent classification."""
        action_frequency = features.get('action_frequency', 0)
        avg_quantity = features.get('avg_quantity', 0)
        buy_ratio = features.get('action_type_buy', 0)
        symbol_diversity = features.get('symbol_diversity', 0)
        
        # Determine primary intent
        if action_frequency > 0.8 and avg_quantity > features.get('avg_quantity', 0) * 1.5:
            return OperatorIntent.AGGRESSIVE_TRADING, 0.8
        elif action_frequency < 0.2 and avg_quantity < features.get('avg_quantity', 0) * 0.8:
            return OperatorIntent.CONSERVATIVE_TRADING, 0.8
        elif symbol_diversity > 0.7:
            return OperatorIntent.SPECULATIVE_POSITIONING, 0.7
        elif 0.4 <= buy_ratio <= 0.6:
            return OperatorIntent.HEDGING_STRATEGY, 0.7
        elif buy_ratio > 0.8:
            return OperatorIntent.LIQUIDITY_PROVIDING, 0.6
        elif buy_ratio < 0.2:
            return OperatorIntent.ARBITRAGE_SEEKING, 0.6
        else:
            return OperatorIntent.UNKNOWN, 0.5
    
    def _generate_alternatives(self, primary_intent: OperatorIntent, features: Dict[str, float], confidence: float) -> List[Tuple[OperatorIntent, float]]:
        """Generate alternative intents with lower confidence."""
        alternatives = []
        
        # Generate alternatives based on features
        if primary_intent != OperatorIntent.AGGRESSIVE_TRADING and features.get('action_frequency', 0) > 0.5:
            alternatives.append((OperatorIntent.AGGRESSIVE_TRADING, confidence * 0.7))
        
        if primary_intent != OperatorIntent.CONSERVATIVE_TRADING and features.get('action_frequency', 0) < 0.3:
            alternatives.append((OperatorIntent.CONSERVATIVE_TRADING, confidence * 0.7))
        
        return alternatives[:3]


class BehaviorPredictor:
    """Advanced behavior prediction using multiple models."""
    
    def predict(self, profile: OperatorProfile, recent_actions: List[OperatorAction], market_state: Dict[str, Any]) -> BehaviorPrediction:
        """Predict operator behavior using ensemble prediction."""
        # Base prediction on profile
        predicted_action_type = self._predict_action_type(profile, recent_actions)
        probability = self._calculate_probability(profile, predicted_action_type)
        expected_position_size = self._predict_position_size(profile, recent_actions, market_state)
        expected_timing = self._predict_timing(profile, recent_actions)
        risk_level = self._assess_risk_level(profile, market_state)
        
        return BehaviorPrediction(
            predicted_action_type=predicted_action_type,
            probability=probability,
            expected_position_size=expected_position_size,
            expected_timing=expected_timing,
            risk_level=risk_level,
            confidence_interval=(probability * 0.8, probability * 1.2)
        )
    
    def _predict_action_type(self, profile: OperatorProfile, recent_actions: List[OperatorAction]) -> str:
        """Predict next action type."""
        if not recent_actions:
            return "buy"  # Default to buy
        
        # Analyze recent action patterns
        action_types = [a.action_type for a in recent_actions[-5:]]
        most_common = max(set(action_types), key=action_types.count)
        
        # Add some randomness for unpredictability
        if profile.risk_profile == OperatorRiskProfile.UNPREDICTABLE:
            import random
            return random.choice(["buy", "sell", "adjust_position"])
        
        return most_common
    
    def _calculate_probability(self, profile: OperatorProfile, action_type: str) -> float:
        """Calculate probability of predicted action."""
        base_probability = 0.7  # Base probability
        
        # Adjust based on success rate
        if profile.success_rate > 0.8:
            base_probability += 0.2
        elif profile.success_rate < 0.4:
            base_probability -= 0.2
        
        # Adjust based on risk profile
        if profile.risk_profile == OperatorRiskProfile.CONSERVATIVE:
            base_probability += 0.1
        elif profile.risk_profile == OperatorRiskProfile.AGGRESSIVE:
            base_probability -= 0.1
        
        return max(0.0, min(1.0, base_probability))
    
    def _predict_position_size(self, profile: OperatorProfile, recent_actions: List[OperatorAction], market_state: Dict[str, Any]) -> float:
        """Predict position size."""
        base_size = profile.average_position_size
        
        # Adjust based on market volatility
        market_volatility = market_state.get("volatility", 0.2)
        if market_volatility > 0.5:
            base_size *= 0.8  # Reduce size in high volatility
        elif market_volatility < 0.1:
            base_size *= 1.2  # Increase size in low volatility
        
        # Adjust based on risk profile
        if profile.risk_profile == OperatorRiskProfile.CONSERVATIVE:
            base_size *= 0.7
        elif profile.risk_profile == OperatorRiskProfile.AGGRESSIVE:
            base_size *= 1.3
        
        return base_size
    
    def _predict_timing(self, profile: OperatorProfile, recent_actions: List[OperatorAction]) -> float:
        """Predict timing of next action."""
        if len(recent_actions) < 2:
            return 3600.0  # Default 1 hour
        
        # Calculate average time between actions
        time_diffs = [recent_actions[i].timestamp - recent_actions[i-1].timestamp for i in range(1, len(recent_actions))]
        avg_time_diff = np.mean(time_diffs)
        
        # Adjust based on risk profile
        if profile.risk_profile == OperatorRiskProfile.AGGRESSIVE:
            avg_time_diff *= 0.5
        elif profile.risk_profile == OperatorRiskProfile.CONSERVATIVE:
            avg_time_diff *= 2.0
        
        return max(60.0, avg_time_diff)  # Minimum 1 minute
    
    def _assess_risk_level(self, profile: OperatorProfile, market_state: Dict[str, Any]) -> float:
        """Assess risk level of predicted action."""
        base_risk = 0.5
        
        # Adjust based on risk profile
        risk_multipliers = {
            OperatorRiskProfile.ULTRA_CONSERVATIVE: 0.2,
            OperatorRiskProfile.CONSERVATIVE: 0.4,
            OperatorRiskProfile.MODERATE: 0.6,
            OperatorRiskProfile.AGGRESSIVE: 0.8,
            OperatorRiskProfile.ULTRA_AGGRESSIVE: 0.9,
            OperatorRiskProfile.UNPREDICTABLE: 0.7
        }
        
        base_risk *= risk_multipliers.get(profile.risk_profile, 0.6)
        
        # Adjust based on market conditions
        market_volatility = market_state.get("volatility", 0.2)
        base_risk *= (1 + market_volatility)
        
        return max(0.0, min(1.0, base_risk))


class PatternDetector:
    """Advanced pattern detection in operator behavior."""
    
    def detect_temporal_patterns(self, actions: List[OperatorAction]) -> Dict[str, Any]:
        """Detect temporal patterns in operator actions."""
        if len(actions) < 5:
            return {"pattern_type": "insufficient_data"}
        
        timestamps = [a.timestamp for a in actions]
        time_diffs = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        # Detect regularity
        regularity = np.std(time_diffs) / np.mean(time_diffs) if time_diffs else 0
        
        # Detect clustering
        clustered = self._detect_clustering(time_diffs)
        
        return {
            "pattern_type": "temporal",
            "action_regularity": 1.0 - regularity,  # Higher is more regular
            "action_clustering": clustered,
            "avg_time_between_actions": np.mean(time_diffs),
            "pattern_strength": 1.0 - regularity
        }
    
    def detect_size_patterns(self, actions: List[OperatorAction]) -> Dict[str, Any]:
        """Detect patterns in position sizing."""
        if len(actions) < 5:
            return {"pattern_type": "insufficient_data"}
        
        quantities = [a.quantity for a in actions]
        
        # Detect trend
        trend = self._calculate_trend(quantities)
        
        # Detect consistency
        consistency = 1.0 - (np.std(quantities) / np.mean(quantities)) if quantities else 0
        
        return {
            "pattern_type": "size",
            "quantity_trend": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
            "size_consistency": consistency,
            "pattern_strength": consistency
        }
    
    def detect_symbol_patterns(self, actions: List[OperatorAction]) -> Dict[str, Any]:
        """Detect patterns in symbol selection."""
        if len(actions) < 5:
            return {"pattern_type": "insufficient_data"}
        
        symbols = [a.symbol for a in actions]
        symbol_counts = {symbol: symbols.count(symbol) for symbol in set(symbols)}
        
        # Detect concentration
        concentration = max(symbol_counts.values()) / len(symbols)
        
        return {
            "pattern_type": "symbol",
            "symbol_concentration": concentration,
            "preferred_symbols": sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "pattern_strength": concentration
        }
    
    def detect_market_condition_patterns(self, actions: List[OperatorAction]) -> Dict[str, Any]:
        """Detect patterns related to market conditions."""
        market_contexts = [a.market_context for a in actions if a.market_context]
        
        if not market_contexts:
            return {"pattern_type": "insufficient_data"}
        
        # Analyze market condition preferences
        regimes = [ctx.get("regime", "neutral") for ctx in market_contexts]
        regime_counts = {regime: regimes.count(regime) for regime in set(regimes)}
        
        return {
            "pattern_type": "market_condition",
            "preferred_regimes": sorted(regime_counts.items(), key=lambda x: x[1], reverse=True),
            "pattern_strength": max(regime_counts.values()) / len(regimes) if regimes else 0.0
        }
    
    def _detect_clustering(self, time_diffs: List[float]) -> bool:
        """Detect if actions are clustered in time."""
        if len(time_diffs) < 3:
            return False
        
        # Simple clustering detection: look for groups of short time differences
        short_diffs = sum(1 for diff in time_diffs if diff < np.mean(time_diffs) * 0.5)
        return short_diffs / len(time_diffs) > 0.3
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend as linear regression slope."""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        slope = np.polyfit(x, y, 1)[0]
        return slope


class RiskAssessor:
    """Comprehensive risk assessment for operator behavior."""
    
    def assess_risk(self, profile: OperatorProfile, recent_actions: List[OperatorAction], market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive multi-dimensional risk assessment."""
        # Behavioral risk
        behavioral_risk = self._assess_behavioral_risk(profile, recent_actions)
        
        # Market risk
        market_risk = self._assess_market_risk(profile, market_state)
        
        # Concentration risk
        concentration_risk = self._assess_concentration_risk(profile, recent_actions)
        
        # Overall risk score
        overall_risk = (behavioral_risk * 0.4 + market_risk * 0.3 + concentration_risk * 0.3)
        
        return {
            "overall_risk_score": overall_risk,
            "risk_level": self._categorize_risk(overall_risk),
            "behavioral_risk": behavioral_risk,
            "market_risk": market_risk,
            "concentration_risk": concentration_risk,
            "confidence": profile.success_rate
        }
    
    def _assess_behavioral_risk(self, profile: OperatorProfile, recent_actions: List[OperatorAction]) -> float:
        """Assess behavioral risk based on operator profile."""
        risk_score = 0.5  # Base risk
        
        # Adjust based on risk profile
        risk_multipliers = {
            OperatorRiskProfile.ULTRA_CONSERVATIVE: 0.2,
            OperatorRiskProfile.CONSERVATIVE: 0.3,
            OperatorRiskProfile.MODERATE: 0.5,
            OperatorRiskProfile.AGGRESSIVE: 0.7,
            OperatorRiskProfile.ULTRA_AGGRESSIVE: 0.9,
            OperatorRiskProfile.UNPREDICTABLE: 0.8
        }
        
        risk_score *= risk_multipliers.get(profile.risk_profile, 0.5)
        
        # Adjust based on success rate
        if profile.success_rate > 0.8:
            risk_score *= 0.7
        elif profile.success_rate < 0.4:
            risk_score *= 1.3
        
        return max(0.0, min(1.0, risk_score))
    
    def _assess_market_risk(self, profile: OperatorProfile, market_state: Dict[str, Any]) -> float:
        """Assess market-related risk."""
        market_volatility = market_state.get("volatility", 0.2)
        market_trend = market_state.get("trend", 0)
        
        # Base market risk
        risk_score = market_volatility
        
        # Adjust based on regime preference
        if profile.market_regime_preference == market_state.get("regime", "neutral"):
            risk_score *= 0.8  # Lower risk if trading in preferred regime
        else:
            risk_score *= 1.2  # Higher risk if trading in non-preferred regime
        
        return max(0.0, min(1.0, risk_score))
    
    def _assess_concentration_risk(self, profile: OperatorProfile, recent_actions: List[OperatorAction]) -> float:
        """Assess concentration risk."""
        if not recent_actions:
            return 0.5
        
        symbols = [a.symbol for a in recent_actions]
        symbol_counts = {symbol: symbols.count(symbol) for symbol in set(symbols)}
        
        # Calculate concentration
        concentration = max(symbol_counts.values()) / len(symbols)
        
        # Higher concentration = higher risk
        risk_score = concentration
        
        return max(0.0, min(1.0, risk_score))
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk score into levels."""
        if risk_score < 0.2:
            return "very_low"
        elif risk_score < 0.4:
            return "low"
        elif risk_score < 0.6:
            return "moderate"
        elif risk_score < 0.8:
            return "high"
        else:
            return "very_high"


class AnomalyDetector:
    """Advanced anomaly detection in operator behavior."""
    
    def detect_anomalies(self, actions: List[OperatorAction]) -> List[Dict[str, Any]]:
        """Detect various types of anomalies in operator behavior."""
        anomalies = []
        
        if len(actions) < 10:
            return anomalies
        
        # Detect position size anomalies
        size_anomalies = self._detect_size_anomalies(actions)
        anomalies.extend(size_anomalies)
        
        # Detect timing anomalies
        timing_anomalies = self._detect_timing_anomalies(actions)
        anomalies.extend(timing_anomalies)
        
        # Detect symbol anomalies
        symbol_anomalies = self._detect_symbol_anomalies(actions)
        anomalies.extend(symbol_anomalies)
        
        return anomalies
    
    def _detect_size_anomalies(self, actions: List[OperatorAction]) -> List[Dict[str, Any]]:
        """Detect anomalies in position sizing."""
        quantities = [a.quantity for a in actions]
        mean_qty = np.mean(quantities)
        std_qty = np.std(quantities)
        
        anomalies = []
        for action in actions:
            # Use z-score for anomaly detection
            z_score = abs((action.quantity - mean_qty) / std_qty) if std_qty > 0 else 0
            
            if z_score > 2.5:  # More than 2.5 standard deviations
                anomalies.append({
                    "anomaly_type": "size_anomaly",
                    "action_id": action.action_id,
                    "timestamp": action.timestamp,
                    "z_score": z_score,
                    "description": f"Position size {action.quantity} is {z_score:.1f} standard deviations from mean"
                })
        
        return anomalies
    
    def _detect_timing_anomalies(self, actions: List[OperatorAction]) -> List[Dict[str, Any]]:
        """Detect anomalies in action timing."""
        timestamps = [a.timestamp for a in actions]
        time_diffs = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        if not time_diffs:
            return []
        
        mean_diff = np.mean(time_diffs)
        std_diff = np.std(time_diffs)
        
        anomalies = []
        for i, action in enumerate(actions[1:], 1):
            time_diff = action.timestamp - actions[i-1].timestamp
            
            if std_diff > 0:
                z_score = abs((time_diff - mean_diff) / std_diff)
                
                if z_score > 2.5:
                    anomalies.append({
                        "anomaly_type": "timing_anomaly",
                        "action_id": action.action_id,
                        "timestamp": action.timestamp,
                        "z_score": z_score,
                        "description": f"Action timing {time_diff:.1f}s is {z_score:.1f} standard deviations from mean"
                    })
        
        return anomalies
    
    def _detect_symbol_anomalies(self, actions: List[OperatorAction]) -> List[Dict[str, Any]]:
        """Detect anomalies in symbol selection."""
        symbols = [a.symbol for a in actions]
        symbol_counts = {symbol: symbols.count(symbol) for symbol in set(symbols)}
        
        # Check for suddenly trading new symbols
        recent_symbols = [a.symbol for a in actions[-5:]]
        historical_symbols = set(symbols[:-5]) if len(symbols) > 5 else set()
        new_symbols = set(recent_symbols) - historical_symbols
        
        anomalies = []
        for action in actions[-5:]:
            if action.symbol in new_symbols:
                anomalies.append({
                    "anomaly_type": "symbol_anomaly",
                    "action_id": action.action_id,
                    "timestamp": action.timestamp,
                    "description": f"Trading new symbol {action.symbol} not seen in recent history"
                })
        
        return anomalies


# Singleton instance
_operator_understanding: Optional[OperatorUnderstanding] = None
_operator_understanding_lock = threading.Lock()


def get_operator_understanding(history_window: int = 1000) -> OperatorUnderstanding:
    """Get the singleton operator understanding instance."""
    global _operator_understanding
    if _operator_understanding is None:
        with _operator_understanding_lock:
            if _operator_understanding is None:
                _operator_understanding = OperatorUnderstanding(history_window)
    return _operator_understanding


__all__ = [
    "OperatorUnderstanding",
    "get_operator_understanding",
    "OperatorIntent",
    "OperatorRiskProfile",
    "OperatorAction",
    "OperatorProfile",
    "IntentPrediction",
    "BehaviorPrediction",
]