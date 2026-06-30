"""
DIX VISION Cognitive OS Strategy Selector

Connects the existing Cognitive OS with strategy selection to enable
cognitive reasoning for choosing optimal trading strategies.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

# Import existing Cognitive OS
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/cognitive_os/core")
from kernel import CognitiveOSKernel, SystemLayer, SystemStatus

# Import existing strategies
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/trading/strategies")
from enhanced_strategies import StrategySignal, MicrostructureStrategy, VolatilityTradingStrategy

logger = logging.getLogger(__name__)


@dataclass
class CognitiveStrategyEvaluation:
    """Cognitive evaluation of a trading strategy."""
    strategy_id: str
    strategy_name: str
    cognitive_fit_score: float
    market_match_score: float
    resource_efficiency: float
    risk_alignment: float
    overall_cognitive_score: float
    cognitive_reasoning: List[str]
    timestamp: float


@dataclass
class CognitiveStrategySelection:
    """Strategy selection made by cognitive reasoning."""
    selection_id: str
    selected_strategy: str
    cognitive_process: str
    market_state_analysis: Dict[str, Any]
    cognitive_rationale: List[str]
    confidence: float
    alternative_strategies: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class CognitiveOSStrategySelector:
    """
    Cognitive OS-based strategy selector.
    
    Uses cognitive layers to:
    - Analyze market state with cognitive reasoning
    - Evaluate strategies based on cognitive fit
    - Select optimal strategy using cognitive processes
    - Provide cognitive rationale for selection
    """
    
    def __init__(self):
        # Initialize Cognitive OS Kernel
        self._cognitive_os = CognitiveOSKernel()
        self._cognitive_os.initialize_system()
        
        # Available strategies
        self._available_strategies = {
            "microstructure": MicrostructureStrategy(),
            "volatility": VolatilityTradingStrategy()
        }
        
        # Strategy evaluations
        self._strategy_evaluations: Dict[str, CognitiveStrategyEvaluation] = {}
        
        # Selection history
        self._selection_history: List[CognitiveStrategySelection] = []
        
        # Cognitive state tracking
        self._cognitive_state = {
            "attention_level": 0.8,
            "processing_mode": "analytical",
            "confidence_level": 0.7,
            "resource_allocation": {
                "strategy_analysis": 0.3,
                "market_analysis": 0.4,
                "risk_assessment": 0.3
            }
        }
        
        self._lock = threading.Lock()
        
        logger.info("Cognitive OS Strategy Selector initialized")
    
    def analyze_market_state_cognitively(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market state using cognitive processes."""
        # Extract market features
        volatility = market_data.get("volatility", 0.2)
        trend = market_data.get("trend", "NEUTRAL")
        signal_strength = abs(market_data.get("signal", 0.0))
        liquidity = market_data.get("liquidity", 0.8)
        
        # Cognitive analysis
        cognitive_analysis = {
            "market_regime": self._determine_market_regime(volatility, trend),
            "complexity_level": self._assess_complexity(market_data),
            "information_quality": self._assess_information_quality(market_data),
            "cognitive_load": self._calculate_cognitive_load(market_data),
            "attention_requirements": self._determine_attention_requirements(market_data),
            "processing_mode": self._determine_processing_mode(market_data)
        }
        
        return cognitive_analysis
    
    def _determine_market_regime(self, volatility: float, trend: str) -> str:
        """Determine market regime using cognitive classification."""
        if volatility > 0.5:
            return "HIGH_VOLATILITY"
        elif volatility > 0.3:
            return "MODERATE_VOLATILITY"
        elif trend in ["BULLISH", "BEARISH"]:
            return f"{trend}_TRENDING"
        else:
            return "SIDEWAYS"
    
    def _assess_complexity(self, market_data: Dict[str, Any]) -> float:
        """Assess market complexity (0.0-1.0)."""
        factors = [
            abs(market_data.get("signal", 0.0)),
            market_data.get("volatility", 0.2),
            market_data.get("data_complexity", 0.5)
        ]
        return min(1.0, np.mean(factors))
    
    def _assess_information_quality(self, market_data: Dict[str, Any]) -> float:
        """Assess information quality (0.0-1.0)."""
        quality_factors = [
            market_data.get("data_completeness", 0.8),
            market_data.get("data_freshness", 0.9),
            market_data.get("signal_quality", 0.7)
        ]
        return np.mean(quality_factors)
    
    def _calculate_cognitive_load(self, market_data: Dict[str, Any]) -> float:
        """Calculate cognitive load required for market analysis."""
        complexity = self._assess_complexity(market_data)
        information_quality = self._assess_information_quality(market_data)
        
        # Higher complexity and lower information quality = higher cognitive load
        cognitive_load = complexity * (1.0 - information_quality) + 0.2
        return min(1.0, cognitive_load)
    
    def _determine_attention_requirements(self, market_data: Dict[str, Any]) -> float:
        """Determine attention level required (0.0-1.0)."""
        volatility = market_data.get("volatility", 0.2)
        signal_strength = abs(market_data.get("signal", 0.0))
        
        # Higher volatility and signal strength require more attention
        attention = (volatility + signal_strength) / 2
        return min(1.0, attention)
    
    def _determine_processing_mode(self, market_data: Dict[str, Any]) -> str:
        """Determine cognitive processing mode."""
        complexity = self._assess_complexity(market_data)
        cognitive_load = self._calculate_cognitive_load(market_data)
        
        if cognitive_load > 0.7:
            return "focused"
        elif complexity > 0.6:
            return "analytical"
        else:
            return "automatic"
    
    def evaluate_strategy_cognitively(self, strategy_id: str, 
                                    market_data: Dict[str, Any],
                                    cognitive_analysis: Dict[str, Any]) -> CognitiveStrategyEvaluation:
        """Evaluate a strategy using cognitive reasoning."""
        strategy = self._available_strategies.get(strategy_id)
        if not strategy:
            return None
        
        # Cognitive fit evaluation
        cognitive_fit = self._evaluate_cognitive_fit(strategy_id, cognitive_analysis)
        
        # Market match evaluation
        market_match = self._evaluate_market_match(strategy_id, market_data, cognitive_analysis)
        
        # Resource efficiency evaluation
        resource_efficiency = self._evaluate_resource_efficiency(strategy_id, cognitive_analysis)
        
        # Risk alignment evaluation
        risk_alignment = self._evaluate_risk_alignment(strategy_id, market_data)
        
        # Overall cognitive score
        overall_score = (
            cognitive_fit * 0.3 +
            market_match * 0.3 +
            resource_efficiency * 0.2 +
            risk_alignment * 0.2
        )
        
        # Generate cognitive reasoning
        cognitive_reasoning = self._generate_cognitive_reasoning(
            strategy_id, cognitive_fit, market_match, resource_efficiency, risk_alignment
        )
        
        evaluation = CognitiveStrategyEvaluation(
            strategy_id=strategy_id,
            strategy_name=strategy_id.replace("_", " ").title(),
            cognitive_fit_score=cognitive_fit,
            market_match_score=market_match,
            resource_efficiency=resource_efficiency,
            risk_alignment=risk_alignment,
            overall_cognitive_score=overall_score,
            cognitive_reasoning=cognitive_reasoning,
            timestamp=datetime.now().timestamp()
        )
        
        with self._lock:
            self._strategy_evaluations[strategy_id] = evaluation
        
        return evaluation
    
    def _evaluate_cognitive_fit(self, strategy_id: str, 
                             cognitive_analysis: Dict[str, Any]) -> float:
        """Evaluate how well strategy fits cognitive state."""
        processing_mode = cognitive_analysis["processing_mode"]
        cognitive_load = cognitive_analysis["cognitive_load"]
        
        # Strategy-specific cognitive requirements
        strategy_requirements = {
            "microstructure": {"complexity": 0.4, "speed": 0.9, "attention": 0.7},
            "volatility": {"complexity": 0.6, "speed": 0.5, "attention": 0.8}
        }
        
        requirements = strategy_requirements.get(strategy_id, {})
        
        # Calculate fit based on processing mode match
        mode_fit = 0.8 if processing_mode == "analytical" else 0.6
        
        # Calculate fit based on cognitive load
        load_fit = 1.0 - abs(cognitive_load - 0.5)  # Optimal at moderate load
        
        return (mode_fit + load_fit) / 2
    
    def _evaluate_market_match(self, strategy_id: str, market_data: Dict[str, Any],
                            cognitive_analysis: Dict[str, Any]) -> float:
        """Evaluate how well strategy matches current market conditions."""
        market_regime = cognitive_analysis["market_regime"]
        volatility = market_data.get("volatility", 0.2)
        
        # Strategy-market compatibility
        strategy_regime_compatibility = {
            "microstructure": ["SIDEWAYS", "MODERATE_VOLATILITY"],
            "volatility": ["HIGH_VOLATILITY", "MODERATE_VOLATILITY"]
        }
        
        compatible_regimes = strategy_regime_compatibility.get(strategy_id, [])
        regime_match = 1.0 if market_regime in compatible_regimes else 0.5
        
        # Volatility match
        if strategy_id == "volatility":
            volatility_match = min(1.0, volatility / 0.5)  # Better in higher volatility
        else:
            volatility_match = 1.0 - min(1.0, volatility / 0.5)  # Better in lower volatility
        
        return (regime_match + volatility_match) / 2
    
    def _evaluate_resource_efficiency(self, strategy_id: str,
                                    cognitive_analysis: Dict[str, Any]) -> float:
        """Evaluate resource efficiency of strategy."""
        cognitive_load = cognitive_analysis["cognitive_load"]
        
        # Strategy resource requirements
        strategy_resources = {
            "microstructure": 0.4,  # Lower resource requirements
            "volatility": 0.6     # Higher resource requirements
        }
        
        required_resources = strategy_resources.get(strategy_id, 0.5)
        
        # Efficiency is higher when cognitive load is well-matched to requirements
        efficiency = 1.0 - abs(cognitive_load - required_resources)
        
        return efficiency
    
    def _evaluate_risk_alignment(self, strategy_id: str, market_data: Dict[str, Any]) -> float:
        """Evaluate strategy alignment with risk profile."""
        volatility = market_data.get("volatility", 0.2)
        signal_strength = abs(market_data.get("signal", 0.0))
        
        # Strategy risk profiles
        strategy_risk_profiles = {
            "microstructure": {"risk_tolerance": 0.6, "preferred_volatility": 0.3},
            "volatility": {"risk_tolerance": 0.8, "preferred_volatility": 0.5}
        }
        
        risk_profile = strategy_risk_profiles.get(strategy_id, {})
        risk_tolerance = risk_profile.get("risk_tolerance", 0.7)
        preferred_volatility = risk_profile.get("preferred_volatility", 0.3)
        
        # Risk alignment based on volatility match
        volatility_alignment = 1.0 - abs(volatility - preferred_volatility)
        
        # Risk alignment based on signal strength
        signal_alignment = min(1.0, signal_strength / risk_tolerance)
        
        return (volatility_alignment + signal_alignment) / 2
    
    def _generate_cognitive_reasoning(self, strategy_id: str, cognitive_fit: float,
                                    market_match: float, resource_efficiency: float,
                                    risk_alignment: float) -> List[str]:
        """Generate cognitive reasoning for strategy evaluation."""
        reasoning = []
        
        if cognitive_fit > 0.7:
            reasoning.append(f"Strong cognitive fit - strategy aligns with current cognitive state")
        elif cognitive_fit < 0.5:
            reasoning.append(f"Weak cognitive fit - strategy may not match cognitive requirements")
        
        if market_match > 0.7:
            reasoning.append(f"Excellent market match - strategy suits current market regime")
        elif market_match < 0.5:
            reasoning.append(f"Poor market match - strategy not ideal for current conditions")
        
        if resource_efficiency > 0.7:
            reasoning.append(f"High resource efficiency - optimal resource utilization")
        elif resource_efficiency < 0.5:
            reasoning.append(f"Low resource efficiency - may require excessive resources")
        
        if risk_alignment > 0.7:
            reasoning.append(f"Strong risk alignment - strategy matches risk profile")
        elif risk_alignment < 0.5:
            reasoning.append(f"Weak risk alignment - strategy may not align with risk tolerance")
        
        return reasoning
    
    def select_strategy_cognitively(self, market_data: Dict[str, Any]) -> CognitiveStrategySelection:
        """Select optimal strategy using cognitive reasoning."""
        # Analyze market state cognitively
        cognitive_analysis = self.analyze_market_state_cognitively(market_data)
        
        # Evaluate all available strategies
        strategy_evaluations = {}
        for strategy_id in self._available_strategies.keys():
            evaluation = self.evaluate_strategy_cognitively(
                strategy_id, market_data, cognitive_analysis
            )
            strategy_evaluations[strategy_id] = evaluation
        
        # Select best strategy
        best_strategy_id = max(
            strategy_evaluations.keys(),
            key=lambda k: strategy_evaluations[k].overall_cognitive_score
        )
        
        best_evaluation = strategy_evaluations[best_strategy_id]
        
        # Generate alternative strategies
        sorted_strategies = sorted(
            strategy_evaluations.keys(),
            key=lambda k: strategy_evaluations[k].overall_cognitive_score,
            reverse=True
        )
        alternatives = [s for s in sorted_strategies if s != best_strategy_id][:2]
        
        # Create cognitive rationale
        cognitive_rationale = [
            f"Selected {best_strategy_id} based on cognitive analysis",
            f"Overall cognitive score: {best_evaluation.overall_cognitive_score:.2f}",
            f"Market regime: {cognitive_analysis['market_regime']}",
            f"Processing mode: {cognitive_analysis['processing_mode']}"
        ]
        cognitive_rationale.extend(best_evaluation.cognitive_reasoning)
        
        selection = CognitiveStrategySelection(
            selection_id=f"cognitive_selection_{int(datetime.now().timestamp())}",
            selected_strategy=best_strategy_id,
            cognitive_process="multi_criteria_analysis",
            market_state_analysis=cognitive_analysis,
            cognitive_rationale=cognitive_rationale,
            confidence=best_evaluation.overall_cognitive_score,
            alternative_strategies=alternatives
        )
        
        with self._lock:
            self._selection_history.append(selection)
        
        logger.info(f"Cognitive strategy selection: {best_strategy_id} (confidence: {best_evaluation.overall_cognitive_score:.2f})")
        
        return selection
    
    def get_cognitive_selection_insights(self) -> Dict[str, Any]:
        """Get insights from cognitive strategy selections."""
        with self._lock:
            recent_selections = self._selection_history[-10:] if self._selection_history else []
            
            if not recent_selections:
                return {"status": "No selections made yet"}
            
            strategy_distribution = {}
            for selection in recent_selections:
                strategy = selection.selected_strategy
                strategy_distribution[strategy] = strategy_distribution.get(strategy, 0) + 1
            
            average_confidence = np.mean([s.confidence for s in recent_selections])
            
            return {
                "total_selections": len(self._selection_history),
                "recent_selections": len(recent_selections),
                "strategy_distribution": strategy_distribution,
                "average_confidence": average_confidence,
                "cognitive_state": self._cognitive_state,
                "available_strategies": list(self._available_strategies.keys())
            }


# Global instance
_cognitive_os_strategy_selector: Optional[CognitiveOSStrategySelector] = None


def get_cognitive_os_strategy_selector() -> CognitiveOSStrategySelector:
    """Get global cognitive OS strategy selector instance."""
    global _cognitive_os_strategy_selector
    if _cognitive_os_strategy_selector is None:
        _cognitive_os_strategy_selector = CognitiveOSStrategySelector()
    return _cognitive_os_strategy_selector