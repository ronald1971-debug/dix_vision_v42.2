"""
DIX VISION Explainable AI for Trading Decisions

Implements explainable AI for trading decisions using the existing
XAI system to provide transparent and interpretable trading reasoning.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

# Import existing XAI system
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/cognitive_os/xai")
from explainable_ai import ExplainableAISystem, ExplanationMethod, ExplanationResult

logger = logging.getLogger(__name__)


@dataclass
class TradingExplanation:
    """Explanation for a trading decision."""
    explanation_id: str
    decision_type: str  # "BUY", "SELL", "HOLD"
    explanation_method: ExplanationMethod
    feature_importance: Dict[str, float]
    decision_path: List[str]
    confidence_breakdown: Dict[str, float]
    alternative_scenarios: List[Dict[str, Any]]
    human_readable_explanation: str
    visualizations: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FeatureContribution:
    """Contribution of a feature to the trading decision."""
    feature_name: str
    feature_value: float
    contribution_score: float
    contribution_direction: str  # "positive", "negative"
    importance_rank: int
    reasoning: str


@dataclass
class DecisionCounterfactual:
    """Counterfactual explanation for trading decision."""
    counterfactual_id: str
    original_decision: str
    counterfactual_decision: str
    changed_features: Dict[str, Any]
    minimal_changes: bool
    confidence_change: float
    explanation: str


class TradingXAIExplainer:
    """
    Explainable AI system for trading decisions.
    
    Provides:
    - Feature importance analysis for trading decisions
    - Decision path visualization
    - Counterfactual explanations
    - Human-readable explanations
    - Visual explanation generation
    """
    
    def __init__(self):
        # Initialize XAI system
        self._xai_system = ExplainableAISystem()
        
        # Trading explanations
        self._trading_explanations: List[TradingExplanation] = []
        
        # Feature contribution history
        self._feature_contributions: Dict[str, List[FeatureContribution]] = defaultdict(list)
        
        # Counterfactual explanations
        self._counterfactuals: List[DecisionCounterfactual] = []
        
        # Trading feature definitions
        self._trading_features = {
            "price": "Current market price",
            "volume": "Trading volume",
            "volatility": "Market volatility",
            "rsi": "Relative Strength Index",
            "macd": "Moving Average Convergence Divergence",
            "momentum": "Price momentum",
            "trend": "Market trend direction",
            "sentiment": "Market sentiment score",
            "order_flow": "Order flow imbalance",
            "spread": "Bid-ask spread"
        }
        
        self._lock = threading.Lock()
        
        logger.info("Trading XAI Explainer initialized")
    
    def explain_trading_decision(self, decision: str, market_data: Dict[str, Any],
                              strategy: str = "general") -> TradingExplanation:
        """Generate explanation for a trading decision."""
        # Calculate feature importance
        feature_importance = self._calculate_feature_importance(decision, market_data, strategy)
        
        # Generate decision path
        decision_path = self._generate_decision_path(decision, market_data, feature_importance)
        
        # Calculate confidence breakdown
        confidence_breakdown = self._calculate_confidence_breakdown(decision, market_data, feature_importance)
        
        # Generate alternative scenarios
        alternative_scenarios = self._generate_alternative_scenarios(decision, market_data)
        
        # Generate human-readable explanation
        human_readable = self._generate_human_readable_explanation(
            decision, feature_importance, decision_path, confidence_breakdown
        )
        
        # Generate visualizations
        visualizations = self._generate_visualizations(feature_importance, decision_path)
        
        explanation = TradingExplanation(
            explanation_id=f"explanation_{int(datetime.now().timestamp())}",
            decision_type=decision,
            explanation_method=ExplanationMethod.FEATURE_IMPORTANCE,
            feature_importance=feature_importance,
            decision_path=decision_path,
            confidence_breakdown=confidence_breakance,
            alternative_scenarios=alternative_scenarios,
            human_readable_explanation=human_readable,
            visualizations=visualizations
        )
        
        # Store feature contributions
        for feature_name, importance in feature_importance.items():
            contribution = FeatureContribution(
                feature_name=feature_name,
                feature_value=market_data.get(feature_name, 0.0),
                contribution_score=importance,
                contribution_direction="positive" if importance > 0 else "negative",
                importance_rank=0,  # Will be set after sorting
                reasoning=self._generate_feature_reasoning(feature_name, importance, decision)
            )
            self._feature_contributions[feature_name].append(contribution)
        
        with self._lock:
            self._trading_explanations.append(explanation)
        
        return explanation
    
    def _calculate_feature_importance(self, decision: str, market_data: Dict[str, Any],
                                   strategy: str) -> Dict[str, float]:
        """Calculate feature importance for the decision."""
        feature_importance = {}
        
        # Strategy-specific feature importance
        if strategy == "momentum":
            base_importance = {
                "momentum": 0.4,
                "trend": 0.3,
                "volume": 0.2,
                "volatility": 0.1
            }
        elif strategy == "mean_reversion":
            base_importance = {
                "rsi": 0.3,
                "volatility": 0.3,
                "spread": 0.2,
                "price": 0.2
            }
        elif strategy == "sentiment":
            base_importance = {
                "sentiment": 0.5,
                "volume": 0.2,
                "trend": 0.2,
                "momentum": 0.1
            }
        else:
            base_importance = {
                "price": 0.2,
                "volume": 0.2,
                "volatility": 0.2,
                "momentum": 0.2,
                "trend": 0.2
            }
        
        # Adjust based on actual market data values
        for feature, base_score in base_importance.items():
            feature_value = market_data.get(feature, 0.0)
            
            # Normalize feature value
            if feature == "volatility":
                normalized_value = min(1.0, feature_value / 0.5)
            elif feature == "rsi":
                normalized_value = abs(feature_value - 50) / 50.0
            elif feature == "sentiment":
                normalized_value = abs(feature_value)
            else:
                normalized_value = min(1.0, abs(feature_value) / 100.0)
            
            # Adjust importance based on decision alignment
            if decision == "BUY":
                if feature in ["momentum", "trend", "sentiment"]:
                    alignment = 1.0 if feature_value > 0 else -0.5
                elif feature in ["volatility", "rsi"]:
                    alignment = 0.5 if feature_value < 0.5 else -0.5
                else:
                    alignment = 0.0
            elif decision == "SELL":
                if feature in ["momentum", "trend", "sentiment"]:
                    alignment = -1.0 if feature_value > 0 else 0.5
                elif feature in ["volatility", "rsi"]:
                    alignment = 0.5 if feature_value > 0.5 else -0.5
                else:
                    alignment = 0.0
            else:  # HOLD
                alignment = 0.0
            
            # Calculate final importance
            adjusted_importance = base_score * normalized_value * (1.0 + alignment * 0.5)
            feature_importance[feature] = max(0.0, min(1.0, adjusted_importance))
        
        # Normalize to sum to 1.0
        total_importance = sum(feature_importance.values())
        if total_importance > 0:
            feature_importance = {k: v / total_importance for k, v in feature_importance.items()}
        
        return feature_importance
    
    def _generate_decision_path(self, decision: str, market_data: Dict[str, Any],
                             feature_importance: Dict[str, float]) -> List[str]:
        """Generate decision path explanation."""
        decision_path = []
        
        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        # Build decision path
        decision_path.append(f"Decision: {decision}")
        decision_path.append("Decision process:")
        
        for feature, importance in sorted_features[:5]:  # Top 5 features
            feature_value = market_data.get(feature, 0.0)
            feature_desc = self._trading_features.get(feature, feature)
            
            if importance > 0.2:
                decision_path.append(f"  1. Analyzed {feature_desc}: {feature_value:.3f} (importance: {importance:.2f})")
            
            # Add reasoning step
            if feature == "momentum" and feature_value > 0.5:
                decision_path.append(f"  2. Strong momentum detected -> supports {decision}")
            elif feature == "volatility" and feature_value > 0.5:
                decision_path.append(f"  2. High volatility detected -> increases risk consideration")
            elif feature == "sentiment" and feature_value > 0.5:
                decision_path.append(f"  2. Positive sentiment detected -> supports BUY decision")
            elif feature == "rsi" and feature_value < 30:
                decision_path.append(f"  2. Oversold condition detected -> supports BUY decision")
            elif feature == "rsi" and feature_value > 70:
                decision_path.append(f"  2. Overbought condition detected -> supports SELL decision")
        
        decision_path.append(f"  Final: {decision} decision based on weighted feature analysis")
        
        return decision_path
    
    def _calculate_confidence_breakdown(self, decision: str, market_data: Dict[str, Any],
                                      feature_importance: Dict[str, float]) -> Dict[str, float]:
        """Calculate confidence breakdown by feature."""
        confidence_breakdown = {}
        
        # Base confidence
        base_confidence = 0.5
        
        # Add feature contributions to confidence
        for feature, importance in feature_importance.items():
            feature_value = market_data.get(feature, 0.0)
            
            # Calculate feature-specific confidence contribution
            if decision == "BUY":
                if feature in ["momentum", "trend", "sentiment"]:
                    feature_confidence = importance * (1.0 if feature_value > 0 else 0.0)
                elif feature in ["volatility", "rsi"]:
                    feature_confidence = importance * (0.5 if feature_value < 0.5 else 0.0)
                else:
                    feature_confidence = importance * 0.5
            elif decision == "SELL":
                if feature in ["momentum", "trend", "sentiment"]:
                    feature_confidence = importance * (1.0 if feature_value < 0 else 0.0)
                elif feature in ["volatility", "rsi"]:
                    feature_confidence = importance * (0.5 if feature_value > 0.5 else 0.0)
                else:
                    feature_confidence = importance * 0.5
            else:  # HOLD
                feature_confidence = importance * 0.3
            
            confidence_breakdown[feature] = feature_confidence
        
        # Calculate overall confidence
        overall_confidence = base_confidence + sum(confidence_breakdown.values()) * 0.5
        confidence_breakdown["overall"] = min(1.0, overall_confidence)
        
        return confidence_breakdown
    
    def _generate_alternative_scenarios(self, decision: str, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alternative decision scenarios."""
        scenarios = []
        
        # Scenario 1: What if key features change?
        if decision == "BUY":
            # What if momentum turns negative?
            alternative_data = market_data.copy()
            alternative_data["momentum"] = -0.5
            alternative_decision = "SELL" if alternative_data["momentum"] < -0.3 else "HOLD"
            
            scenarios.append({
                "scenario": "momentum_reversal",
                "changes": {"momentum": -0.5},
                "alternative_decision": alternative_decision,
                "probability": 0.3
            })
            
            # What if volatility increases significantly?
            alternative_data = market_data.copy()
            alternative_data["volatility"] = 0.8
            alternative_decision = "HOLD"  # High volatility -> caution
            
            scenarios.append({
                "scenario": "volatility_spike",
                "changes": {"volatility": 0.8},
                "alternative_decision": alternative_decision,
                "probability": 0.4
            })
        
        elif decision == "SELL":
            # What if momentum turns positive?
            alternative_data = market_data.copy()
            alternative_data["momentum"] = 0.5
            alternative_decision = "BUY" if alternative_data["momentum"] > 0.3 else "HOLD"
            
            scenarios.append({
                "scenario": "momentum_reversal",
                "changes": {"momentum": 0.5},
                "alternative_decision": alternative_decision,
                "probability": 0.3
            })
        
        else:  # HOLD
            # What if strong signal appears?
            alternative_data = market_data.copy()
            alternative_data["momentum"] = 0.8
            alternative_decision = "BUY"
            
            scenarios.append({
                "scenario": "strong_signal",
                "changes": {"momentum": 0.8},
                "alternative_decision": alternative_decision,
                "probability": 0.4
            })
        
        return scenarios
    
    def _generate_human_readable_explanation(self, decision: str,
                                           feature_importance: Dict[str, float],
                                           decision_path: List[str],
                                           confidence_breakdown: Dict[str, float]) -> str:
        """Generate human-readable explanation."""
        # Get top features
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        top_features = sorted_features[:3]
        
        # Build explanation
        explanation_parts = []
        
        explanation_parts.append(f"Trading Decision: {decision}")
        explanation_parts.append(f"Overall Confidence: {confidence_breakdown.get('overall', 0.0):.2f}")
        explanation_parts.append("")
        
        explanation_parts.append("Key Factors:")
        for feature, importance in top_features:
            feature_desc = self._trading_features.get(feature, feature)
            explanation_parts.append(f"  • {feature_desc}: {importance:.2f} importance")
        
        explanation_parts.append("")
        explanation_parts.append("Reasoning:")
        explanation_parts.extend(decision_path[2:-1])  # Skip first and last lines
        
        explanation_parts.append("")
        explanation_parts.append(f"This {decision} decision is primarily driven by {top_features[0][0] if top_features else 'market conditions'}.")
        
        return "\n".join(explanation_parts)
    
    def _generate_visualizations(self, feature_importance: Dict[str, float],
                               decision_path: List[str]) -> Dict[str, Any]:
        """Generate visualization data for explanations."""
        visualizations = {}
        
        # Feature importance bar chart data
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        visualizations["feature_importance_chart"] = {
            "type": "bar_chart",
            "data": [
                {"feature": feature, "importance": importance}
                for feature, importance in sorted_features
            ],
            "title": "Feature Importance for Trading Decision"
        }
        
        # Decision path flowchart data
        visualizations["decision_path_flowchart"] = {
            "type": "flowchart",
            "nodes": [
                {"id": "start", "label": "Market Data Input"},
                *[{"id": f"step_{i}", "label": step.strip()} for i, step in enumerate(decision_path[1:-1])],
                {"id": "end", "label": f"Decision: {decision_path[0].split(': ')[1]}"}
            ],
            "edges": [
                {"from": "start", "to": "step_0"},
                *[{"from": f"step_{i}", "to": f"step_{i+1}"} for i in range(len(decision_path) - 3)],
                {"from": f"step_{len(decision_path)-3}", "to": "end"}
            ]
        }
        
        # Confidence breakdown pie chart
        confidence_data = {k: v for k, v in feature_importance.items() if k != "overall"}
        visualizations["confidence_breakdown_chart"] = {
            "type": "pie_chart",
            "data": [
                {"feature": feature, "contribution": importance}
                for feature, importance in confidence_data.items()
            ],
            "title": "Confidence Breakdown by Feature"
        }
        
        return visualizations
    
    def _generate_feature_reasoning(self, feature_name: str, importance: float,
                                  decision: str) -> str:
        """Generate reasoning for a feature's contribution."""
        feature_desc = self._trading_features.get(feature_name, feature_name)
        
        if importance > 0.3:
            return f"{feature_desc} is a primary driver for this {decision} decision"
        elif importance > 0.1:
            return f"{feature_desc} contributes moderately to this {decision} decision"
        else:
            return f"{feature_desc} has minimal impact on this {decision} decision"
    
    def generate_counterfactual(self, decision: str, market_data: Dict[str, Any],
                               target_decision: str) -> DecisionCounterfactual:
        """Generate counterfactual explanation."""
        # Find minimal changes to achieve target decision
        changed_features = {}
        minimal_changes = True
        
        # Try changing key features
        if decision == "BUY" and target_decision == "SELL":
            # Flip momentum
            if market_data.get("momentum", 0.0) > 0:
                changed_features["momentum"] = -0.5
            # Flip sentiment
            if market_data.get("sentiment", 0.0) > 0:
                changed_features["sentiment"] = -0.5
            # Increase volatility
            changed_features["volatility"] = 0.8
        
        elif decision == "SELL" and target_decision == "BUY":
            # Flip momentum
            if market_data.get("momentum", 0.0) < 0:
                changed_features["momentum"] = 0.5
            # Flip sentiment
            if market_data.get("sentiment", 0.0) < 0:
                changed_features["sentiment"] = 0.5
        
        # Calculate confidence change
        original_confidence = 0.7  # Simplified
        new_confidence = 0.6  # Simplified
        confidence_change = new_confidence - original_confidence
        
        # Generate explanation
        if changed_features:
            explanation = f"To change from {decision} to {target_decision}, the following minimal changes would be needed: "
            explanation += ", ".join([f"{k} to {v}" for k, v in changed_features.items()])
        else:
            explanation = f"Cannot achieve {target_decision} with minimal feature changes"
            minimal_changes = False
        
        counterfactual = DecisionCounterfactual(
            counterfactual_id=f"counterfactual_{int(datetime.now().timestamp())}",
            original_decision=decision,
            counterfactual_decision=target_decision,
            changed_features=changed_features,
            minimal_changes=minimal_changes,
            confidence_change=confidence_change,
            explanation=explanation
        )
        
        with self._lock:
            self._counterfactuals.append(counterfactual)
        
        return counterfactual
    
    def get_explanation_insights(self) -> Dict[str, Any]:
        """Get insights from trading explanations."""
        with self._lock:
            recent_explanations = self._trading_explanations[-20:] if self._trading_explanations else []
            
            if not recent_explanations:
                return {"status": "No explanations generated yet"}
            
            # Feature importance trends
            feature_trends = {}
            for explanation in recent_explanations:
                for feature, importance in explanation.feature_importance.items():
                    if feature not in feature_trends:
                        feature_trends[feature] = []
                    feature_trends[feature].append(importance)
            
            avg_feature_importance = {
                feature: np.mean(importances)
                for feature, importances in feature_trends.items()
            }
            
            # Decision distribution
            decision_distribution = {}
            for explanation in recent_explanations:
                decision = explanation.decision_type
                decision_distribution[decision] = decision_distribution.get(decision, 0) + 1
            
            return {
                "total_explanations": len(self._trading_explanations),
                "recent_explanations": len(recent_explanations),
                "decision_distribution": decision_distribution,
                "average_feature_importance": dict(sorted(avg_feature_importance.items(), key=lambda x: x[1], reverse=True)),
                "total_counterfactuals": len(self._counterfactuals),
                "explanation_methods_used": list(set([e.explanation_method for e in recent_explanations]))
            }


class XAITradingStrategy:
    """
    Trading strategy with explainable AI integration.
    
    Provides transparent and interpretable trading decisions.
    """
    
    def __init__(self):
        self._xai_explainer = TradingXAIExplainer()
        self._explained_decisions: List[Dict[str, Any]] = []
        
        self._lock = threading.Lock()
        
        logger.info("XAI Trading Strategy initialized")
    
    def generate_explained_signal(self, market_data: Dict[str, Any],
                                 strategy: str = "general") -> Dict[str, Any]:
        """Generate trading signal with full explanation."""
        # Make base decision (simplified logic)
        momentum = market_data.get("momentum", 0.0)
        sentiment = market_data.get("sentiment", 0.0)
        
        signal_strength = (momentum + sentiment) / 2
        
        if signal_strength > 0.3:
            decision = "BUY"
        elif signal_strength < -0.3:
            decision = "SELL"
        else:
            decision = "HOLD"
        
        # Generate explanation
        explanation = self._xai_explainer.explain_trading_decision(decision, market_data, strategy)
        
        result = {
            "decision": decision,
            "confidence": explanation.confidence_breakdown.get("overall", 0.0),
            "explanation": explanation,
            "explanation_id": explanation.explanation_id,
            "feature_importance": explanation.feature_importance,
            "human_readable": explanation.human_readable_explanation,
            "visualizations": explanation.visualizations
        }
        
        with self._lock:
            self._explained_decisions.append(result)
        
        return result
    
    def get_xai_strategy_status(self) -> Dict[str, Any]:
        """Get XAI strategy status."""
        return self._xai_explainer.get_explanation_insights()


# Global instances
_trading_xai_explainer: Optional[TradingXAIExplainer] = None
_xai_trading_strategy: Optional[XAITradingStrategy] = None


def get_trading_xai_explainer() -> TradingXAIExplainer:
    """Get global trading XAI explainer instance."""
    global _trading_xai_explainer
    if _trading_xai_explainer is None:
        _trading_xai_explainer = TradingXAIExplainer()
    return _trading_xai_explainer


def get_xai_trading_strategy() -> XAITradingStrategy:
    """Get global XAI trading strategy instance."""
    global _xai_trading_strategy
    if _xai_trading_strategy is None:
        _xai_trading_strategy = XAITradingStrategy()
    return _xai_trading_strategy