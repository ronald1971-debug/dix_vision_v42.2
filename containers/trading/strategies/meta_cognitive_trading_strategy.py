"""
DIX VISION Meta-Cognitive Trading System

Integrates the existing meta-cognitive system with trading to enable
self-awareness, self-reflection, and self-improvement in trading decisions.
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

# Import existing meta-cognitive system
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/cognitive_os/meta_cognitive")
from meta_cognitive_system import (
    MetaCognitiveSystem,
    MetaCognitiveProcess,
    CognitiveState,
    SelfModel,
    CognitiveProcess,
    SelfReflection,
    MetaCognitiveDecision
)

# Import existing trading strategies
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/trading/strategies")
from enhanced_strategies import StrategySignal

logger = logging.getLogger(__name__)


@dataclass
class TradingSelfModel:
    """Self-model of the trading system."""
    model_id: str
    trading_capabilities: List[str]
    trading_limitations: List[str]
    confidence_profile: Dict[str, float]
    performance_history: List[float]
    learning_rate: float
    adaptability: float
    cognitive_load: float
    market_states_trained: List[str]
    last_updated: float


@dataclass
class TradingCognitiveProcess:
    """Active cognitive process in trading."""
    process_id: str
    process_type: MetaCognitiveProcess
    trading_state: CognitiveState
    resource_allocation: Dict[str, float]
    confidence: float
    market_context: Dict[str, Any]
    start_time: float
    expected_completion_time: float


@dataclass
class TradingSelfReflection:
    """Self-reflection on trading performance."""
    reflection_id: str
    topic: str
    trading_insights: List[str]
    confidence: float
    self_criticism: List[str]
    improvement_suggestions: List[str]
    performance_impact: str
    timestamp: float


@dataclass
class MetaCognitiveTradingDecision:
    """Meta-cognitive trading decision with self-awareness."""
    decision_id: str
    base_decision: StrategySignal
    meta_cognitive_analysis: Dict[str, Any]
    self_awareness_level: float
    confidence_adjustment: float
    reasoning_enhancement: List[str]
    self_criticism: List[str]
    final_confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


class MetaCognitiveTradingSystem:
    """
    Meta-cognitive trading system with self-awareness and self-improvement.
    
    Enables the trading system to:
    - Reflect on its own trading decisions
    - Monitor its cognitive state during trading
    - Self-critique and improve trading strategies
    - Adapt its behavior based on self-awareness
    """
    
    def __init__(self):
        # Initialize meta-cognitive system
        self._meta_cognitive_system = MetaCognitiveSystem()
        
        # Trading-specific self-model
        self._trading_self_model = TradingSelfModel(
            model_id="trading_self_model",
            trading_capabilities=[
                "pattern_recognition",
                "causal_analysis",
                "risk_assessment",
                "strategy_selection",
                "order_execution"
            ],
            trading_limitations=[
                "emotional_bias",
                "overfitting_risk",
                "latency_constraints",
                "data_quality_dep"
            ],
            confidence_profile={
                "pattern_recognition": 0.85,
                "causal_analysis": 0.75,
                "risk_assessment": 0.90,
                "strategy_selection": 0.80,
                "order_execution": 0.95
            },
            performance_history=[],
            learning_rate=0.01,
            adaptability=0.7,
            cognitive_load=0.5,
            market_states_trained=[],
            last_updated=datetime.now().timestamp()
        )
        
        # Active cognitive processes
        self._cognitive_processes: Dict[str, TradingCognitiveProcess] = {}
        
        # Trading reflections
        self._trading_reflections: List[TradingSelfReflection] = []
        
        # Decision history with meta-cognitive analysis
        self._meta_cognitive_decisions: List[MetaCognitiveTradingDecision] = []
        
        # Performance tracking
        self._performance_metrics: Dict[str, float] = {
            "total_decisions": 0,
            "self_corrected_decisions": 0,
            "average_self_awareness": 0.0,
            "confidence_improvement": 0.0,
            "reflection_count": 0
        }
        
        self._lock = threading.Lock()
        
        logger.info("Meta-Cognitive Trading System initialized")
    
    def assess_cognitive_state(self, market_data: Dict[str, Any]) -> CognitiveState:
        """Assess current cognitive state based on market conditions."""
        volatility = market_data.get("volatility", 0.2)
        signal_strength = abs(market_data.get("signal", 0.0))
        information_load = market_data.get("data_complexity", 0.5)
        
        # Determine cognitive state
        if volatility > 0.5 and signal_strength > 0.7:
            return CognitiveState.CONCENTRATED
        elif volatility > 0.6:
            return CognitiveState.UNCERTAIN
        elif signal_strength > 0.8 and volatility < 0.3:
            return CognitiveState.CONFIDENT
        elif information_load > 0.7:
            return CognitiveState.LEARNING
        elif self._trading_self_model.cognitive_load > 0.8:
            return CognitiveState.REFLECTING
        else:
            return CognitiveState.NORMAL
    
    def initiate_self_monitoring(self, market_data: Dict[str, Any]) -> TradingCognitiveProcess:
        """Initiate self-monitoring cognitive process."""
        cognitive_state = self.assess_cognitive_state(market_data)
        
        process = TradingCognitiveProcess(
            process_id=f"self_monitor_{int(datetime.now().timestamp())}",
            process_type=MetaCognitiveProcess.SELF_MONITORING,
            trading_state=cognitive_state,
            resource_allocation={
                "attention": 0.3,
                "working_memory": 0.4,
                "long_term_memory": 0.3
            },
            confidence=0.8,
            market_context=market_data,
            start_time=datetime.now().timestamp(),
            expected_completion_time=datetime.now().timestamp() + 0.1  # 100ms
        )
        
        with self._lock:
            self._cognitive_processes[process.process_id] = process
            self._trading_self_model.cognitive_load = 0.3 + (0.2 if cognitive_state == CognitiveState.CONCENTRATED else 0.0)
        
        return process
    
    def evaluate_self_model(self, recent_performance: List[float]) -> SelfModel:
        """Evaluate and update the trading self-model."""
        # Update performance history
        self._trading_self_model.performance_history.extend(recent_performance)
        
        # Keep only recent history
        if len(self._trading_self_model.performance_history) > 100:
            self._trading_self_model.performance_history = \
                self._trading_self_model.performance_history[-100:]
        
        # Update learning rate based on performance trend
        if len(recent_performance) > 10:
            recent_avg = np.mean(recent_performance[-10:])
            historical_avg = np.mean(self._trading_self_model.performance_history)
            
            if recent_avg > historical_avg:
                self._trading_self_model.learning_rate = min(0.05, self._trading_self_model.learning_rate * 1.1)
            else:
                self._trading_self_model.learning_rate = max(0.001, self._trading_self_model.learning_rate * 0.9)
        
        # Update adaptability based on market state changes
        self._trading_self_model.adaptability = min(1.0, self._trading_self_model.adaptability + 0.01)
        
        self._trading_self_model.last_updated = datetime.now().timestamp()
        
        # Return standard self-model format
        return SelfModel(
            model_id=self._trading_self_model.model_id,
            capabilities=self._trading_self_model.trading_capabilities,
            limitations=self._trading_self_model.trading_limitations,
            confidence_profile=self._trading_self_model.confidence_profile,
            performance_history=self._trading_self_model.performance_history,
            learning_rate=self._trading_self_model.learning_rate,
            adaptability=self._trading_self_model.adaptability,
            cognitive_load=self._trading_self_model.cognitive_load,
            last_updated=self._trading_self_model.last_updated
        )
    
    def perform_self_reflection(self, decision: StrategySignal, 
                              outcome: float, market_data: Dict[str, Any]) -> TradingSelfReflection:
        """Perform self-reflection on a trading decision."""
        # Generate insights based on decision and outcome
        insights = []
        self_criticism = []
        improvement_suggestions = []
        
        if outcome > 0:
            insights.append(f"Successful {decision.action} decision")
            if decision.confidence > 0.8:
                insights.append("High confidence was justified")
            else:
                improvement_suggestions.append("Consider increasing confidence for similar patterns")
        else:
            self_criticism.append(f"Unsuccessful {decision.action} decision")
            if decision.confidence > 0.8:
                self_criticism.append("Overconfidence detected - recalibrate confidence levels")
                improvement_suggestions.append("Implement confidence calibration mechanism")
            else:
                insights.append("Low confidence correctly predicted uncertainty")
        
        # Analyze reasoning
        if "pattern" in decision.reason.lower():
            insights.append("Pattern-based reasoning used")
        else:
            improvement_suggestions.append("Consider incorporating pattern recognition")
        
        # Determine performance impact
        if outcome > 0.01:
            performance_impact = "positive"
        elif outcome < -0.01:
            performance_impact = "negative"
        else:
            performance_impact = "neutral"
        
        reflection = TradingSelfReflection(
            reflection_id=f"reflection_{int(datetime.now().timestamp())}",
            topic=f"Trading decision analysis: {decision.action}",
            trading_insights=insights,
            confidence=0.8,
            self_criticism=self_criticism,
            improvement_suggestions=improvement_suggestions,
            performance_impact=performance_impact,
            timestamp=datetime.now().timestamp()
        )
        
        with self._lock:
            self._trading_reflections.append(reflection)
            self._performance_metrics["reflection_count"] += 1
        
        return reflection
    
    def apply_meta_cognitive_analysis(self, base_decision: StrategySignal,
                                     market_data: Dict[str, Any]) -> MetaCognitiveTradingDecision:
        """Apply meta-cognitive analysis to a trading decision."""
        # Initiate self-monitoring
        cognitive_process = self.initiate_self_monitoring(market_data)
        
        # Analyze decision confidence based on self-model
        capability_confidence = self._trading_self_model.confidence_profile.get(
            "pattern_recognition", 0.8
        )
        
        # Adjust confidence based on cognitive state
        confidence_adjustment = 0.0
        reasoning_enhancement = []
        self_criticism = []
        
        if cognitive_process.trading_state == CognitiveState.UNCERTAIN:
            confidence_adjustment = -0.1
            reasoning_enhancement.append("High uncertainty detected - reducing confidence")
            self_criticism.append("Decision made in uncertain conditions")
        elif cognitive_process.trading_state == CognitiveState.CONFIDENT:
            confidence_adjustment = 0.05
            reasoning_enhancement.append("High confidence state - slight confidence boost")
        elif cognitive_process.trading_state == CognitiveState.CONCENTRATED:
            reasoning_enhancement.append("Focused cognitive state - optimal decision conditions")
        
        # Check for cognitive overload
        if self._trading_self_model.cognitive_load > 0.8:
            confidence_adjustment -= 0.15
            self_criticism.append("Cognitive overload detected - decision quality may be reduced")
            reasoning_enhancement.append("High cognitive load - recommend risk reduction")
        
        # Apply confidence adjustment
        final_confidence = max(0.0, min(1.0, base_decision.confidence + confidence_adjustment))
        
        # Calculate self-awareness level
        self_awareness_level = (
            (1.0 - abs(confidence_adjustment)) * 
            (1.0 - self._trading_self_model.cognitive_load)
        )
        
        # Create meta-cognitive decision
        meta_decision = MetaCognitiveTradingDecision(
            decision_id=f"meta_decision_{int(datetime.now().timestamp())}",
            base_decision=base_decision,
            meta_cognitive_analysis={
                "cognitive_state": cognitive_process.trading_state.value,
                "cognitive_load": self._trading_self_model.cognitive_load,
                "capability_confidence": capability_confidence,
                "confidence_adjustment": confidence_adjustment
            },
            self_awareness_level=self_awareness_level,
            confidence_adjustment=confidence_adjustment,
            reasoning_enhancement=reasoning_enhancement,
            self_criticism=self_criticism,
            final_confidence=final_confidence
        )
        
        with self._lock:
            self._meta_cognitive_decisions.append(meta_decision)
            self._performance_metrics["total_decisions"] += 1
            self._performance_metrics["average_self_awareness"] = (
                (self._performance_metrics["average_self_awareness"] * 
                 (self._performance_metrics["total_decisions"] - 1) + self_awareness_level) /
                self._performance_metrics["total_decisions"]
            )
        
        # Apply self-correction if confidence adjustment is significant
        if abs(confidence_adjustment) > 0.1:
            self._performance_metrics["self_corrected_decisions"] += 1
            logger.info(f"Meta-cognitive self-correction applied: {confidence_adjustment:.2f}")
        
        return meta_decision
    
    def improve_from_reflection(self, reflection: TradingSelfReflection) -> None:
        """Improve trading system based on self-reflection."""
        # Update confidence profile based on reflection
        if "confidence" in reflection.performance_impact:
            # Calibrate confidence based on performance
            if reflection.performance_impact == "positive":
                # Reinforce current confidence levels
                for capability in self._trading_self_model.confidence_profile:
                    self._trading_self_model.confidence_profile[capability] = min(
                        1.0, self._trading_self_model.confidence_profile[capability] + 0.01
                    )
            elif reflection.performance_impact == "negative":
                # Reduce confidence levels
                for capability in self._trading_self_model.confidence_profile:
                    self._trading_self_model.confidence_profile[capability] = max(
                        0.5, self._trading_self_model.confidence_profile[capability] - 0.02
                    )
        
        # Implement improvement suggestions
        for suggestion in reflection.improvement_suggestions:
            if "confidence" in suggestion.lower():
                logger.info(f"Implementing confidence calibration: {suggestion}")
            elif "pattern" in suggestion.lower():
                logger.info(f"Enhancing pattern recognition: {suggestion}")
            elif "risk" in suggestion.lower():
                logger.info(f"Adjusting risk management: {suggestion}")
        
        # Update cognitive load
        self._trading_self_model.cognitive_load = max(0.3, self._trading_self_model.cognitive_load - 0.05)
    
    def get_meta_cognitive_insights(self) -> Dict[str, Any]:
        """Get comprehensive meta-cognitive insights."""
        with self._lock:
            recent_reflections = self._trading_reflections[-10:] if self._trading_reflections else []
            recent_decisions = self._meta_cognitive_decisions[-10:] if self._meta_cognitive_decisions else []
            
            return {
                "self_model": {
                    "capabilities": self._trading_self_model.trading_capabilities,
                    "limitations": self._trading_self_model.trading_limitations,
                    "confidence_profile": self._trading_self_model.confidence_profile,
                    "learning_rate": self._trading_self_model.learning_rate,
                    "adaptability": self._trading_self_model.adaptability,
                    "cognitive_load": self._trading_self_model.cognitive_load
                },
                "performance_metrics": self._performance_metrics,
                "recent_reflections": [
                    {
                        "topic": r.topic,
                        "performance_impact": r.performance_impact,
                        "insight_count": len(r.trading_insights),
                        "criticism_count": len(r.self_criticism)
                    }
                    for r in recent_reflections
                ],
                "cognitive_processes": len(self._cognitive_processes),
                "average_self_awareness": self._performance_metrics["average_self_awareness"],
                "self_correction_rate": (
                    self._performance_metrics["self_corrected_decisions"] /
                    self._performance_metrics["total_decisions"]
                    if self._performance_metrics["total_decisions"] > 0 else 0.0
                )
            }


class MetaCognitiveTradingStrategy:
    """
    Trading strategy enhanced with meta-cognitive capabilities.
    
    Combines base trading decisions with self-awareness and self-improvement.
    """
    
    def __init__(self):
        self._meta_cognitive_system = MetaCognitiveTradingSystem()
        self._decision_outcomes: Dict[str, float] = {}
        
        self._lock = threading.Lock()
        
        logger.info("Meta-Cognitive Trading Strategy initialized")
    
    def generate_meta_cognitive_signal(self, base_signal: StrategySignal,
                                     market_data: Dict[str, Any]) -> StrategySignal:
        """Generate trading signal with meta-cognitive enhancement."""
        # Apply meta-cognitive analysis
        meta_decision = self._meta_cognitive_system.apply_meta_cognitive_analysis(
            base_signal, market_data
        )
        
        # Create enhanced signal
        enhanced_signal = StrategySignal(
            action=meta_decision.base_decision.action,
            confidence=meta_decision.final_confidence,
            entry_price=meta_decision.base_decision.entry_price,
            quantity=meta_decision.base_decision.quantity * meta_decision.final_confidence,
            reason=f"{meta_decision.base_decision.reason} | Meta-cognitive: {'; '.join(meta_decision.reasoning_enhancement)}",
            metadata={
                **meta_decision.base_decision.metadata,
                "meta_cognitive": True,
                "self_awareness_level": meta_decision.self_awareness_level,
                "confidence_adjustment": meta_decision.confidence_adjustment,
                "cognitive_state": meta_decision.meta_cognitive_analysis["cognitive_state"]
            }
        )
        
        return enhanced_signal
    
    def record_outcome(self, signal: StrategySignal, outcome: float,
                     market_data: Dict[str, Any]) -> None:
        """Record trading outcome for self-reflection."""
        # Perform self-reflection
        reflection = self._meta_cognitive_system.perform_self_reflection(
            signal, outcome, market_data
        )
        
        # Improve from reflection
        self._meta_cognitive_system.improve_from_reflection(reflection)
        
        # Update self-model
        self._meta_cognitive_system.evaluate_self_model([outcome])
        
        with self._lock:
            self._decision_outcomes[signal.reason] = outcome
    
    def get_meta_cognitive_status(self) -> Dict[str, Any]:
        """Get current meta-cognitive status."""
        return self._meta_cognitive_system.get_meta_cognitive_insights()


# Global instance
_meta_cognitive_trading_strategy: Optional[MetaCognitiveTradingStrategy] = None


def get_meta_cognitive_trading_strategy() -> MetaCognitiveTradingStrategy:
    """Get global meta-cognitive trading strategy instance."""
    global _meta_cognitive_trading_strategy
    if _meta_cognitive_trading_strategy is None:
        _meta_cognitive_trading_strategy = MetaCognitiveTradingStrategy()
    return _meta_cognitive_trading_strategy