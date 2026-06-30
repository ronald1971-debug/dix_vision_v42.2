"""
DIX VISION Neuro-Symbolic Trading Strategy Integration

Integrates the existing neuro-symbolic AI capabilities with trading strategies
to enable pattern recognition combined with logical reasoning for trading decisions.
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# Import existing neuro-symbolic AI
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/cognitive_os/neuro_symbolic")
from neuro_symbolic_ai import (
    NeuroSymbolicAI,
    NeuralComponent,
    SymbolicComponent,
    IntegrationType,
    NeuralPattern,
    SymbolicRule,
    NeuroSymbolicMapping,
    NeuroSymbolicReasoning
)

# Import existing trading strategies
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/trading/strategies")
from enhanced_strategies import StrategySignal, MicrostructureStrategy, VolatilityTradingStrategy

logger = logging.getLogger(__name__)


@dataclass
class TradingNeuralPattern:
    """Neural pattern detected in trading data."""
    pattern_id: str
    market_features: np.ndarray
    pattern_type: str  # "momentum", "reversal", "breakout", "volatility"
    confidence: float
    timestamp: float
    neural_component: NeuralComponent


@dataclass
class TradingSymbolicRule:
    """Symbolic rule for trading logic."""
    rule_id: str
    conditions: List[str]  # e.g., ["RSI < 30", "price > MA_200"]
    action: str  # "BUY", "SELL", "HOLD"
    confidence: float
    reasoning: str
    timestamp: float


@dataclass
class NeuroSymbolicTradingDecision:
    """Trading decision combining neural and symbolic reasoning."""
    decision_id: str
    neural_evidence: List[TradingNeuralPattern]
    symbolic_rules: List[TradingSymbolicRule]
    final_action: str
    combined_confidence: float
    neural_weight: float
    symbolic_weight: float
    reasoning_path: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class NeuroSymbolicTradingStrategy:
    """
    Trading strategy enhanced with neuro-symbolic AI.
    
    Combines neural pattern recognition with symbolic trading rules
    for more robust and explainable trading decisions.
    """
    
    def __init__(self):
        # Initialize neuro-symbolic AI
        self._neuro_symbolic_ai = NeuroSymbolicAI()
        
        # Initialize base strategies
        self._microstructure_strategy = MicrostructureStrategy()
        self._volatility_strategy = VolatilityTradingStrategy()
        
        # Trading-specific neural patterns
        self._neural_patterns: Dict[str, TradingNeuralPattern] = {}
        
        # Trading-specific symbolic rules
        self._symbolic_rules: Dict[str, TradingSymbolicRule] = {}
        
        # Decision history
        self._decision_history: List[NeuroSymbolicTradingDecision] = []
        
        # Integration weights
        self._neural_weight = 0.6  # 60% neural, 40% symbolic
        self._symbolic_weight = 0.4
        
        self._lock = threading.Lock()
        
        # Initialize trading rules
        self._initialize_trading_rules()
        
        logger.info("Neuro-Symbolic Trading Strategy initialized")
    
    def _initialize_trading_rules(self):
        """Initialize symbolic trading rules."""
        rules = [
            TradingSymbolicRule(
                rule_id="oversold_rsi",
                conditions=["RSI < 30", "price_decline > 5%"],
                action="BUY",
                confidence=0.85,
                reasoning="Oversold condition with significant price decline",
                timestamp=datetime.now().timestamp()
            ),
            TradingSymbolicRule(
                rule_id="overbought_rsi",
                conditions=["RSI > 70", "price_increase > 5%"],
                action="SELL",
                confidence=0.85,
                reasoning="Overbought condition with significant price increase",
                timestamp=datetime.now().timestamp()
            ),
            TradingSymbolicRule(
                rule_id="trend_following",
                conditions=["price > MA_50", "MA_50 > MA_200", "volume_increasing"],
                action="BUY",
                confidence=0.75,
                reasoning="Strong uptrend with increasing volume",
                timestamp=datetime.now().timestamp()
            ),
            TradingSymbolicRule(
                rule_id="mean_reversion",
                conditions=["price > 2_std_deviations", "volume_spike"],
                action="SELL",
                confidence=0.70,
                reasoning="Price deviation from mean with volume spike",
                timestamp=datetime.now().timestamp()
            ),
        ]
        
        for rule in rules:
            self._symbolic_rules[rule.rule_id] = rule
        
        logger.info(f"Initialized {len(rules)} symbolic trading rules")
    
    def detect_neural_pattern(self, market_data: Dict[str, Any]) -> Optional[TradingNeuralPattern]:
        """Detect neural patterns in market data."""
        # Extract features for neural processing
        features = np.array([
            market_data.get("price_change", 0.0),
            market_data.get("volume_change", 0.0),
            market_data.get("volatility", 0.0),
            market_data.get("momentum", 0.0),
            market_data.get("rsi", 50.0),
        ])
        
        # Normalize features
        features = (features - np.mean(features)) / (np.std(features) + 1e-8)
        
        # Determine pattern type based on features
        pattern_type = self._classify_pattern(features)
        
        # Calculate confidence based on feature strength
        confidence = np.mean(np.abs(features))
        
        if confidence > 0.3:  # Only keep significant patterns
            pattern = TradingNeuralPattern(
                pattern_id=f"pattern_{int(datetime.now().timestamp())}",
                market_features=features,
                pattern_type=pattern_type,
                confidence=confidence,
                timestamp=datetime.now().timestamp(),
                neural_component=NeuralComponent.NEURAL_NETWORK
            )
            
            with self._lock:
                self._neural_patterns[pattern.pattern_id] = pattern
            
            return pattern
        
        return None
    
    def _classify_pattern(self, features: np.ndarray) -> str:
        """Classify pattern type from neural features."""
        price_change = features[0]
        volume_change = features[1]
        volatility = features[2]
        momentum = features[3]
        
        if price_change > 0.5 and volume_change > 0.3:
            return "breakout"
        elif price_change < -0.5 and volume_change > 0.3:
            return "breakdown"
        elif abs(price_change) < 0.2 and volatility > 0.5:
            return "volatility"
        elif momentum > 0.5:
            return "momentum"
        elif momentum < -0.5:
            return "reversal"
        else:
            return "neutral"
    
    def evaluate_symbolic_rules(self, market_data: Dict[str, Any]) -> List[TradingSymbolicRule]:
        """Evaluate symbolic trading rules against market data."""
        applicable_rules = []
        
        for rule in self._symbolic_rules.values():
            if self._rule_matches(rule, market_data):
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def _rule_matches(self, rule: TradingSymbolicRule, market_data: Dict[str, Any]) -> bool:
        """Check if a symbolic rule matches current market conditions."""
        for condition in rule.conditions:
            if not self._evaluate_condition(condition, market_data):
                return False
        return True
    
    def _evaluate_condition(self, condition: str, market_data: Dict[str, Any]) -> bool:
        """Evaluate a single condition."""
        # Parse simple conditions
        if "RSI" in condition:
            rsi = market_data.get("rsi", 50.0)
            if "<" in condition:
                threshold = float(condition.split("<")[1].strip())
                return rsi < threshold
            elif ">" in condition:
                threshold = float(condition.split(">")[1].strip())
                return rsi > threshold
        
        elif "price" in condition:
            price = market_data.get("price", 0.0)
            if "decline" in condition:
                decline = market_data.get("price_decline", 0.0)
                threshold = float(condition.split(">")[1].strip().replace("%", ""))
                return decline > threshold
            elif "increase" in condition:
                increase = market_data.get("price_increase", 0.0)
                threshold = float(condition.split(">")[1].strip().replace("%", ""))
                return increase > threshold
        
        elif "MA" in condition:
            price = market_data.get("price", 0.0)
            ma_50 = market_data.get("MA_50", price)
            ma_200 = market_data.get("MA_200", price)
            
            if "MA_50" in condition and "MA_200" in condition:
                return ma_50 > ma_200
            elif "MA_50" in condition:
                return price > ma_50
        
        elif "volume" in condition:
            volume = market_data.get("volume", 0.0)
            if "increasing" in condition:
                return market_data.get("volume_trend", "neutral") == "increasing"
            elif "spike" in condition:
                return volume > market_data.get("avg_volume", volume) * 2
        
        elif "std_deviations" in condition:
            deviation = market_data.get("price_deviation", 0.0)
            threshold = float(condition.split(">")[1].split("_")[0])
            return deviation > threshold
        
        return False  # Default to false if condition can't be evaluated
    
    def combine_neural_symbolic(self, neural_pattern: Optional[TradingNeuralPattern],
                              symbolic_rules: List[TradingSymbolicRule],
                              market_data: Dict[str, Any]) -> NeuroSymbolicTradingDecision:
        """Combine neural and symbolic reasoning for trading decision."""
        neural_evidence = [neural_pattern] if neural_pattern else []
        
        # Determine action from neural pattern
        neural_action = "HOLD"
        neural_confidence = 0.0
        
        if neural_pattern:
            if neural_pattern.pattern_type in ["breakout", "momentum"]:
                neural_action = "BUY"
                neural_confidence = neural_pattern.confidence
            elif neural_pattern.pattern_type in ["breakdown", "reversal"]:
                neural_action = "SELL"
                neural_confidence = neural_pattern.confidence
        
        # Determine action from symbolic rules
        symbolic_action = "HOLD"
        symbolic_confidence = 0.0
        symbolic_reasoning = []
        
        if symbolic_rules:
            # Use the rule with highest confidence
            best_rule = max(symbolic_rules, key=lambda r: r.confidence)
            symbolic_action = best_rule.action
            symbolic_confidence = best_rule.confidence
            symbolic_reasoning = [best_rule.reasoning]
        
        # Combine actions using weighted voting
        actions = [neural_action, symbolic_action]
        weights = [self._neural_weight, self._symbolic_weight]
        
        action_scores = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}
        
        for action, weight in zip(actions, weights):
            action_scores[action] += weight
        
        final_action = max(action_scores, key=action_scores.get)
        
        # Calculate combined confidence
        combined_confidence = (
            neural_confidence * self._neural_weight +
            symbolic_confidence * self._symbolic_weight
        )
        
        # Build reasoning path
        reasoning_path = []
        if neural_pattern:
            reasoning_path.append(f"Neural: {neural_pattern.pattern_type} pattern detected (confidence: {neural_pattern.confidence:.2f})")
        if symbolic_rules:
            reasoning_path.append(f"Symbolic: {len(symbolic_rules)} rules matched (confidence: {symbolic_confidence:.2f})")
        reasoning_path.append(f"Combined: {final_action} with {combined_confidence:.2f} confidence")
        
        decision = NeuroSymbolicTradingDecision(
            decision_id=f"ns_decision_{int(datetime.now().timestamp())}",
            neural_evidence=neural_evidence,
            symbolic_rules=symbolic_rules,
            final_action=final_action,
            combined_confidence=combined_confidence,
            neural_weight=self._neural_weight,
            symbolic_weight=self._symbolic_weight,
            reasoning_path=reasoning_path
        )
        
        with self._lock:
            self._decision_history.append(decision)
        
        return decision
    
    def generate_signal(self, market_data: Dict[str, Any], 
                      symbol: str) -> StrategySignal:
        """Generate trading signal using neuro-symbolic reasoning."""
        # Detect neural patterns
        neural_pattern = self.detect_neural_pattern(market_data)
        
        # Evaluate symbolic rules
        symbolic_rules = self.evaluate_symbolic_rules(market_data)
        
        # Combine neural and symbolic reasoning
        decision = self.combine_neural_symbolic(neural_pattern, symbolic_rules, market_data)
        
        # Create strategy signal
        current_price = market_data.get("price", 0.0)
        quantity = decision.combined_confidence * 1000 if decision.final_action != "HOLD" else 0.0
        
        signal = StrategySignal(
            action=decision.final_action,
            confidence=decision.combined_confidence,
            entry_price=current_price,
            quantity=quantity,
            reason=" | ".join(decision.reasoning_path),
            metadata={
                "neural_pattern": neural_pattern.pattern_type if neural_pattern else None,
                "symbolic_rules_count": len(symbolic_rules),
                "neural_weight": decision.neural_weight,
                "symbolic_weight": decision.symbolic_weight,
                "neuro_symbolic": True
            }
        )
        
        logger.info(f"Neuro-symbolic signal: {decision.final_action} {symbol} - confidence: {decision.combined_confidence:.2f}")
        
        return signal
    
    def adjust_integration_weights(self, neural_weight: float, symbolic_weight: float):
        """Adjust the weights for neural vs symbolic reasoning."""
        total = neural_weight + symbolic_weight
        if total > 0:
            self._neural_weight = neural_weight / total
            self._symbolic_weight = symbolic_weight / total
            logger.info(f"Adjusted weights: neural={self._neural_weight:.2f}, symbolic={self._symbolic_weight:.2f}")
    
    def get_decision_history(self, limit: int = 100) -> List[NeuroSymbolicTradingDecision]:
        """Get recent neuro-symbolic trading decisions."""
        with self._lock:
            return self._decision_history[-limit:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for neuro-symbolic trading."""
        with self._lock:
            if not self._decision_history:
                return {"total_decisions": 0}
            
            decisions = self._decision_history
            
            return {
                "total_decisions": len(decisions),
                "neural_pattern_usage": sum(1 for d in decisions if d.neural_evidence),
                "symbolic_rule_usage": sum(1 for d in decisions if d.symbolic_rules),
                "average_confidence": np.mean([d.combined_confidence for d in decisions]),
                "action_distribution": {
                    "BUY": sum(1 for d in decisions if d.final_action == "BUY"),
                    "SELL": sum(1 for d in decisions if d.final_action == "SELL"),
                    "HOLD": sum(1 for d in decisions if d.final_action == "HOLD"),
                },
                "integration_weights": {
                    "neural": self._neural_weight,
                    "symbolic": self._symbolic_weight
                }
            }


# Global instance
_neuro_symbolic_trading_strategy: Optional[NeuroSymbolicTradingStrategy] = None


def get_neuro_symbolic_trading_strategy() -> NeuroSymbolicTradingStrategy:
    """Get global neuro-symbolic trading strategy instance."""
    global _neuro_symbolic_trading_strategy
    if _neuro_symbolic_trading_strategy is None:
        _neuro_symbolic_trading_strategy = NeuroSymbolicTradingStrategy()
    return _neuro_symbolic_trading_strategy