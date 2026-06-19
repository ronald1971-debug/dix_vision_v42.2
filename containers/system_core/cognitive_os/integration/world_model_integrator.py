"""World Model Integration with Intelligence Engine - Enhanced Cognitive Intelligence.

This module integrates the world model (operator, platform, workflow understanding) with
the intelligence engine to create enhanced cognitive intelligence that surpasses
basic signal processing or knowledge-based intelligence.
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

logger = logging.getLogger(__name__)


class IntegrationMode(str, Enum):
    """Integration modes for world model with intelligence engine."""
    PASSIVE_MONITORING = "PASSIVE_MONITORING"
    ACTIVE_ENHANCEMENT = "ACTIVE_ENHANCEMENT"
    REALTIME_ADAPTATION = "REALTIME_ADAPTATION"
    PREDICTIVE_GUIDANCE = "PREDICTIVE_GUIDANCE"


@dataclass
class WorldContext:
    """Comprehensive world context for intelligence engine."""
    context_id: str
    timestamp: float
    operator_context: Dict[str, Any]
    platform_context: Dict[str, Any]
    workflow_context: Dict[str, Any]
    market_context: Dict[str, Any]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedDecision:
    """Enhanced decision with world model integration."""
    decision_id: str
    base_decision: Dict[str, Any]
    world_enhancements: Dict[str, Any]
    confidence_adjustment: float
    risk_adjustment: float
    timing_adjustment: float
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeedbackLoop:
    """Feedback loop between intelligence engine and world model."""
    feedback_id: str
    source: str  # "intelligence" or "world_model"
    target: str
    feedback_type: str
    content: Dict[str, Any]
    timestamp: float
    impact_score: float


class WorldModelIntegrator:
    """Integration of world model with intelligence engine."""

    def __init__(self):
        self._lock = threading.Lock()
        self._integration_mode = IntegrationMode.ACTIVE_ENHANCEMENT
        self._operator_understanding = None
        self._platform_understanding = None
        self._workflow_understanding = None
        self._intelligence_engine = None
        self._feedback_loops: List[FeedbackLoop] = []
        self._context_history: deque = deque(maxlen=1000)
        self._enhancement_engine = EnhancementEngine()
        self._adaptive_controller = AdaptiveController()
        self._predictive_guidance = PredictiveGuidance()
        self._initialized = False

    def start(self) -> bool:
        """Start world model integration."""
        logger.info("[WORLD_INTEGRATION] Starting world model integration...")
        
        # Initialize connections to world model components
        try:
            from world_model.operator_understanding import get_operator_understanding
            self._operator_understanding = get_operator_understanding()
            self._operator_understanding.start()
        except ImportError:
            logger.warning("[WORLD_INTEGRATION] Operator understanding not available")
        
        try:
            from world_model.platform_understanding import get_platform_understanding
            self._platform_understanding = get_platform_understanding()
            self._platform_understanding.start()
        except ImportError:
            logger.warning("[WORLD_INTEGRATION] Platform understanding not available")
        
        try:
            from world_model.workflow_understanding import get_workflow_understanding
            self._workflow_understanding = get_workflow_understanding()
            self._workflow_understanding.start()
        except ImportError:
            logger.warning("[WORLD_INTEGRATION] Workflow understanding not available")
        
        # Connect to intelligence engine
        try:
            from intelligence_engine.cognitive.production_intelligence import get_production_intelligence_engine
            self._intelligence_engine = get_production_intelligence_engine()
        except ImportError:
            logger.warning("[WORLD_INTEGRATION] Intelligence engine not available")
        
        self._initialized = True
        logger.info("[WORLD_INTEGRATION] World model integration started")
        return True

    def stop(self) -> bool:
        """Stop world model integration."""
        logger.info("[WORLD_INTEGRATION] Stopping world model integration...")
        
        if self._operator_understanding:
            self._operator_understanding.stop()
        if self._platform_understanding:
            self._platform_understanding.stop()
        if self._workflow_understanding:
            self._workflow_understanding.stop()
        
        self._initialized = False
        logger.info("[WORLD_INTEGRATION] World model integration stopped")
        return True

    def set_integration_mode(self, mode: IntegrationMode) -> None:
        """Set integration mode."""
        with self._lock:
            self._integration_mode = mode
            logger.info(f"[WORLD_INTEGRATION] Integration mode set to {mode}")

    def generate_world_context(self, market_state: Dict[str, Any], operator_id: Optional[str] = None) -> WorldContext:
        """Generate comprehensive world context."""
        logger.debug("[WORLD_INTEGRATION] Generating world context")
        
        context_id = f"ctx_{int(time.time())}_{hash(str(market_state)) % 10000}"
        
        # Gather operator context
        operator_context = {}
        if self._operator_understanding and operator_id:
            operator_profile = self._operator_understanding.get_operator_profile(operator_id)
            if operator_profile:
                operator_context = {
                    "risk_profile": operator_profile.risk_profile.value,
                    "preferred_intents": [i.value for i in operator_profile.preferred_intents],
                    "success_rate": operator_profile.success_rate,
                    "volatility_tolerance": operator_profile.volatility_tolerance
                }
        
        # Gather platform context
        platform_context = {}
        if self._platform_understanding:
            # Assess platform health for default platforms
            for platform in ["binance", "coinbase", "kraken"]:
                platform_health = self._platform_understanding.assess_platform_health(platform)
                platform_context[platform] = platform_health
        
        # Gather workflow context
        workflow_context = {}
        if self._workflow_understanding:
            workflow_stats = self._workflow_understanding.get_workflow_statistics()
            workflow_context = {
                "total_workflows": workflow_stats.get("total_workflows", 0),
                "avg_execution_time": workflow_stats.get("avg_execution_time", 0.0),
                "active_executions": workflow_stats.get("active_executions", 0)
            }
        
        # Market context from input
        market_context = {
            "volatility": market_state.get("volatility", 0.2),
            "trend": market_state.get("trend", 0.0),
            "liquidity": market_state.get("liquidity", 1.0),
            "regime": market_state.get("regime", "neutral")
        }
        
        # Calculate overall confidence
        confidence = self._calculate_context_confidence(operator_context, platform_context, workflow_context, market_context)
        
        world_context = WorldContext(
            context_id=context_id,
            timestamp=time.time(),
            operator_context=operator_context,
            platform_context=platform_context,
            workflow_context=workflow_context,
            market_context=market_context,
            confidence=confidence,
            metadata={"operator_id": operator_id}
        )
        
        # Store in history
        with self._lock:
            self._context_history.append(world_context)
        
        return world_context

    def enhance_intelligence_decision(self, base_decision: Dict[str, Any], world_context: WorldContext) -> EnhancedDecision:
        """Enhance intelligence decision with world model insights."""
        logger.info("[WORLD_INTEGRATION] Enhancing intelligence decision with world context")
        
        decision_id = f"enh_{int(time.time())}_{hash(str(base_decision)) % 10000}"
        
        # Apply enhancement based on integration mode
        if self._integration_mode == IntegrationMode.PASSIVE_MONITORING:
            enhancements = self._passive_enhancement(base_decision, world_context)
        elif self._integration_mode == IntegrationMode.ACTIVE_ENHANCEMENT:
            enhancements = self._enhancement_engine.enhance(base_decision, world_context)
        elif self._integration_mode == IntegrationMode.REALTIME_ADAPTATION:
            enhancements = self._adaptive_controller.adapt(base_decision, world_context)
        elif self._integration_mode == IntegrationMode.PREDICTIVE_GUIDANCE:
            enhancements = self._predictive_guidance.guide(base_decision, world_context, self._context_history)
        else:
            enhancements = {}
        
        # Calculate adjustments
        confidence_adjustment = self._calculate_confidence_adjustment(base_decision, enhancements, world_context)
        risk_adjustment = self._calculate_risk_adjustment(base_decision, enhancements, world_context)
        timing_adjustment = self._calculate_timing_adjustment(base_decision, enhancements, world_context)
        
        # Generate rationale
        rationale = self._generate_enhancement_rationale(enhancements, confidence_adjustment, risk_adjustment, timing_adjustment)
        
        enhanced_decision = EnhancedDecision(
            decision_id=decision_id,
            base_decision=base_decision,
            world_enhancements=enhancements,
            confidence_adjustment=confidence_adjustment,
            risk_adjustment=risk_adjustment,
            timing_adjustment=timing_adjustment,
            rationale=rationale,
            metadata={"context_id": world_context.context_id, "integration_mode": self._integration_mode.value}
        )
        
        # Create feedback loop
        self._create_feedback_loop("world_model", "intelligence_engine", "decision_enhancement", {
            "decision_id": decision_id,
            "enhancements": enhancements,
            "adjustments": {
                "confidence": confidence_adjustment,
                "risk": risk_adjustment,
                "timing": timing_adjustment
            }
        })
        
        return enhanced_decision

    def process_intelligence_feedback(self, execution_result: Dict[str, Any]) -> None:
        """Process feedback from intelligence engine to update world model."""
        logger.info("[WORLD_INTEGRATION] Processing intelligence engine feedback")
        
        # Update operator understanding if applicable
        if "operator_id" in execution_result and self._operator_understanding:
            from world_model.operator_understanding import OperatorAction
            operator_action = OperatorAction(
                action_id=f"act_{int(time.time())}",
                operator_id=execution_result["operator_id"],
                action_type=execution_result.get("action_type", "unknown"),
                symbol=execution_result.get("symbol", ""),
                quantity=execution_result.get("quantity", 0.0),
                price=execution_result.get("price", 0.0),
                timestamp=time.time(),
                market_context=execution_result.get("market_context", {}),
                metadata={"success": execution_result.get("success", False)}
            )
            self._operator_understanding.record_operator_action(operator_action)
        
        # Update workflow understanding if applicable
        if "workflow_id" in execution_result and self._workflow_understanding:
            execution_id = execution_result.get("execution_id")
            if execution_id:
                self._workflow_understanding.complete_workflow_execution(
                    execution_id,
                    self._map_to_workflow_status(execution_result.get("success", True)),
                    execution_result
                )
        
        # Create feedback loop
        self._create_feedback_loop("intelligence_engine", "world_model", "execution_feedback", execution_result)

    def predict_world_state_evolution(self, current_context: WorldContext, time_horizon: float) -> Dict[str, Any]:
        """Predict world state evolution based on current context and history."""
        logger.info(f"[WORLD_INTEGRATION] Predicting world state evolution for {time_horizon}s horizon")
        
        # Use predictive guidance for prediction
        prediction = self._predictive_guidance.predict_evolution(current_context, list(self._context_history), time_horizon)
        
        return prediction

    def optimize_workflow_for_context(self, workflow_id: str, world_context: WorldContext) -> Dict[str, Any]:
        """Optimize workflow execution based on world context."""
        logger.info(f"[WORLD_INTEGRATION] Optimizing workflow {workflow_id} for current context")
        
        if not self._workflow_understanding:
            return {"error": "Workflow understanding not available"}
        
        # Get workflow optimizations
        optimizations = self._workflow_understanding.optimize_workflow(workflow_id)
        
        # Filter and prioritize optimizations based on context
        context_aware_optimizations = self._prioritize_optimizations_for_context(optimizations, world_context)
        
        return {
            "workflow_id": workflow_id,
            "context_aware_optimizations": context_aware_optimizations,
            "estimated_improvement": sum(opp.expected_improvement for opp in context_aware_optimizations),
            "priority_actions": [opp.description for opp in context_aware_optimizations[:3]]
        }

    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get integration statistics."""
        with self._lock:
            return {
                "integration_mode": self._integration_mode.value,
                "context_history_size": len(self._context_history),
                "feedback_loops_size": len(self._feedback_loops),
                "operator_understanding_available": self._operator_understanding is not None,
                "platform_understanding_available": self._platform_understanding is not None,
                "workflow_understanding_available": self._workflow_understanding is not None,
                "intelligence_engine_available": self._intelligence_engine is not None,
                "recent_feedback_count": len([fb for fb in self._feedback_loops if time.time() - fb.timestamp < 3600])
            }

    def _calculate_context_confidence(self, operator_context: Dict, platform_context: Dict, workflow_context: Dict, market_context: Dict) -> float:
        """Calculate overall confidence in world context."""
        confidence_components = []
        
        # Operator context confidence
        if operator_context:
            operator_confidence = operator_context.get("success_rate", 0.5)
            confidence_components.append(operator_confidence)
        else:
            confidence_components.append(0.5)  # Default if no operator context
        
        # Platform context confidence
        if platform_context:
            platform_scores = [pctx.get("health_score", 0.5) for pctx in platform_context.values()]
            platform_confidence = np.mean(platform_scores) if platform_scores else 0.5
            confidence_components.append(platform_confidence)
        else:
            confidence_components.append(0.5)
        
        # Market context confidence
        market_confidence = 1.0 - market_context.get("volatility", 0.2)  # Higher volatility = lower confidence
        confidence_components.append(max(0.0, market_confidence))
        
        # Overall confidence
        return np.mean(confidence_components)

    def _passive_enhancement(self, base_decision: Dict, world_context: WorldContext) -> Dict[str, Any]:
        """Passive enhancement - just add context information."""
        return {
            "context_added": True,
            "operator_risk_considered": bool(world_context.operator_context),
            "platform_health_considered": bool(world_context.platform_context),
            "market_regime_considered": bool(world_context.market_context)
        }

    def _calculate_confidence_adjustment(self, base_decision: Dict, enhancements: Dict, world_context: WorldContext) -> float:
        """Calculate confidence adjustment based on world context."""
        base_confidence = base_decision.get("confidence", 0.5)
        
        # Adjust based on operator risk profile
        if world_context.operator_context:
            risk_profile = world_context.operator_context.get("risk_profile", "MODERATE")
            if risk_profile == "CONSERVATIVE":
                base_confidence *= 0.9
            elif risk_profile == "AGGRESSIVE":
                base_confidence *= 1.1
        
        # Adjust based on platform health
        if world_context.platform_context:
            avg_platform_health = np.mean([pctx.get("health_score", 0.5) for pctx in world_context.platform_context.values()])
            base_confidence *= avg_platform_health
        
        # Adjust based on market regime
        market_regime = world_context.market_context.get("regime", "neutral")
        if market_regime == "volatile":
            base_confidence *= 0.8
        elif market_regime == "stable":
            base_confidence *= 1.1
        
        # Cap adjustment to reasonable range
        adjustment = base_confidence - 0.5  # Adjustment from baseline
        return max(-0.2, min(0.2, adjustment))  # Limit to ±0.2

    def _calculate_risk_adjustment(self, base_decision: Dict, enhancements: Dict, world_context: WorldContext) -> float:
        """Calculate risk adjustment based on world context."""
        base_risk = base_decision.get("risk", 0.5)
        
        # Adjust based on operator profile
        if world_context.operator_context:
            success_rate = world_context.operator_context.get("success_rate", 0.5)
            if success_rate > 0.8:
                base_risk *= 0.7  # Reduce risk for successful operators
            elif success_rate < 0.4:
                base_risk *= 1.3  # Increase risk for unsuccessful operators
        
        # Adjust based on platform anomalies
        if world_context.platform_context:
            anomaly_count = sum(1 for pctx in world_context.platform_context.values() if pctx.get("recent_anomaly_count", 0) > 0)
            base_risk *= (1 + anomaly_count * 0.1)
        
        # Cap adjustment
        adjustment = base_risk - 0.5
        return max(-0.3, min(0.3, adjustment))  # Limit to ±0.3

    def _calculate_timing_adjustment(self, base_decision: Dict, enhancements: Dict, world_context: WorldContext) -> float:
        """Calculate timing adjustment based on world context."""
        base_timing = base_decision.get("timing", 0.0)
        
        # Adjust based on workflow efficiency
        if world_context.workflow_context:
            avg_execution_time = world_context.workflow_context.get("avg_execution_time", 1.0)
            if avg_execution_time > 2.0:
                base_timing += 0.5  # Add delay for slow workflows
            elif avg_execution_time < 0.5:
                base_timing -= 0.2  # Reduce delay for fast workflows
        
        # Adjust based on market volatility
        market_volatility = world_context.market_context.get("volatility", 0.2)
        if market_volatility > 0.5:
            base_timing += 0.3  # Add delay in high volatility
        elif market_volatility < 0.1:
            base_timing -= 0.1  # Reduce delay in low volatility
        
        # Ensure timing is non-negative
        return max(0.0, base_timing)

    def _generate_enhancement_rationale(self, enhancements: Dict, confidence_adj: float, risk_adj: float, timing_adj: float) -> str:
        """Generate rationale for enhancements."""
        rationale_parts = []
        
        if confidence_adj > 0.05:
            rationale_parts.append(f"World context supports increased confidence (+{confidence_adj:.2f})")
        elif confidence_adj < -0.05:
            rationale_parts.append(f"World context suggests reduced confidence ({confidence_adj:.2f})")
        
        if risk_adj > 0.05:
            rationale_parts.append(f"Risk factors identified increase risk level (+{risk_adj:.2f})")
        elif risk_adj < -0.05:
            rationale_parts.append(f"Risk factors support reduced risk ({risk_adj:.2f})")
        
        if timing_adj > 0.1:
            rationale_parts.append(f"Execution timing adjusted for optimal conditions (+{timing_adj:.2f}s)")
        elif timing_adj < -0.1:
            rationale_parts.append(f"Execution can be expedited ({timing_adj:.2f}s)")
        
        return ". ".join(rationale_parts) if rationale_parts else "Standard execution parameters applied"

    def _prioritize_optimizations_for_context(self, optimizations: List, world_context: WorldContext) -> List:
        """Prioritize optimizations based on world context."""
        prioritized = []
        
        for opt in optimizations:
            # Calculate context relevance score
            relevance_score = 0.5  # Base score
            
            # Adjust based on market regime
            market_regime = world_context.market_context.get("regime", "neutral")
            if opt.optimization_type == "parallelization" and market_regime == "volatile":
                relevance_score += 0.3
            elif opt.optimization_type == "caching" and market_regime == "stable":
                relevance_score += 0.3
            
            # Adjust based on platform health
            if world_context.platform_context:
                avg_platform_health = np.mean([pctx.get("health_score", 0.5) for pctx in world_context.platform_context.values()])
                if opt.optimization_type == "batching" and avg_platform_health > 0.8:
                    relevance_score += 0.2
            
            # Add relevance score to optimization
            opt_relevance = {**opt.__dict__, "context_relevance": relevance_score}
            prioritized.append(opt_relevance)
        
        # Sort by context relevance and expected improvement
        prioritized.sort(key=lambda x: (x.get("context_relevance", 0.5), x.get("expected_improvement", 0.0)), reverse=True)
        
        return prioritized

    def _create_feedback_loop(self, source: str, target: str, feedback_type: str, content: Dict) -> None:
        """Create feedback loop entry."""
        feedback_id = f"fb_{int(time.time())}_{hash(str(content)) % 10000}"
        
        feedback = FeedbackLoop(
            feedback_id=feedback_id,
            source=source,
            target=target,
            feedback_type=feedback_type,
            content=content,
            timestamp=time.time(),
            impact_score=0.5  # Initial impact score, updated over time
        )
        
        with self._lock:
            self._feedback_loops.append(feedback)
            # Maintain limited feedback history
            if len(self._feedback_loops) > 1000:
                self._feedback_loops = self._feedback_loops[-1000:]

    def _map_to_workflow_status(self, success: bool) -> str:
        """Map success boolean to workflow status."""
        if success:
            return "COMPLETED"
        return "FAILED"


class EnhancementEngine:
    """Engine for actively enhancing intelligence decisions."""
    
    def enhance(self, base_decision: Dict, world_context: WorldContext) -> Dict[str, Any]:
        """Actively enhance decision with world model insights."""
        enhancements = {}
        
        # Operator-based enhancements
        if world_context.operator_context:
            enhancements["operator_adjustments"] = self._operator_based_enhancements(base_decision, world_context.operator_context)
        
        # Platform-based enhancements
        if world_context.platform_context:
            enhancements["platform_adjustments"] = self._platform_based_enhancements(base_decision, world_context.platform_context)
        
        # Market-based enhancements
        if world_context.market_context:
            enhancements["market_adjustments"] = self._market_based_enhancements(base_decision, world_context.market_context)
        
        # Workflow-based enhancements
        if world_context.workflow_context:
            enhancements["workflow_adjustments"] = self._workflow_based_enhancements(base_decision, world_context.workflow_context)
        
        return enhancements
    
    def _operator_based_enhancements(self, decision: Dict, operator_context: Dict) -> Dict:
        """Operator-based decision enhancements."""
        adjustments = {}
        
        risk_profile = operator_context.get("risk_profile", "MODERATE")
        
        # Adjust position size based on risk profile
        base_position_size = decision.get("position_size", 1.0)
        risk_multipliers = {
            "ULTRA_CONSERVATIVE": 0.2,
            "CONSERVATIVE": 0.4,
            "MODERATE": 0.6,
            "AGGRESSIVE": 0.8,
            "ULTRA_AGGRESSIVE": 1.0
        }
        
        adjustments["position_size_multiplier"] = risk_multipliers.get(risk_profile, 0.6)
        
        # Adjust strategy based on preferred intents
        preferred_intents = operator_context.get("preferred_intents", [])
        if "AGGRESSIVE_TRADING" in preferred_intents:
            adjustments["strategy_bias"] = "aggressive"
        elif "CONSERVATIVE_TRADING" in preferred_intents:
            adjustments["strategy_bias"] = "conservative"
        
        return adjustments
    
    def _platform_based_enhancements(self, decision: Dict, platform_context: Dict) -> Dict:
        """Platform-based decision enhancements."""
        adjustments = {}
        
        # Identify best platform for execution
        best_platform = None
        best_health = 0.0
        
        for platform, health in platform_context.items():
            if health.get("health_score", 0.0) > best_health:
                best_health = health.get("health_score", 0.0)
                best_platform = platform
        
        if best_platform:
            adjustments["recommended_platform"] = best_platform
            adjustments["platform_confidence"] = best_health
        
        return adjustments
    
    def _market_based_enhancements(self, decision: Dict, market_context: Dict) -> Dict:
        """Market-based decision enhancements."""
        adjustments = {}
        
        regime = market_context.get("regime", "neutral")
        volatility = market_context.get("volatility", 0.2)
        
        # Adjust strategy based on regime
        if regime == "bullish":
            adjustments["market_regime_adjustment"] = "bull_market_strategy"
        elif regime == "bearish":
            adjustments["market_regime_adjustment"] = "bear_market_strategy"
        
        # Adjust risk limits based on volatility
        if volatility > 0.5:
            adjustments["volatility_risk_limit"] = "high"
            adjustments["position_size_limit"] = 0.5
        elif volatility < 0.1:
            adjustments["volatility_risk_limit"] = "low"
            adjustments["position_size_limit"] = 1.5
        
        return adjustments
    
    def _workflow_based_enhancements(self, decision: Dict, workflow_context: Dict) -> Dict:
        """Workflow-based decision enhancements."""
        adjustments = {}
        
        avg_execution_time = workflow_context.get("avg_execution_time", 1.0)
        active_executions = workflow_context.get("active_executions", 0)
        
        # Adjust for workflow load
        if active_executions > 50:
            adjustments["workflow_load_adjustment"] = "reduce_complexity"
        elif active_executions < 10:
            adjustments["workflow_load_adjustment"] = "can_increase_complexity"
        
        # Adjust timing expectations
        if avg_execution_time > 2.0:
            adjustments["timing_expectation"] = "slow"
        elif avg_execution_time < 0.5:
            adjustments["timing_expectation"] = "fast"
        
        return adjustments


class AdaptiveController:
    """Real-time adaptive control based on world model feedback."""
    
    def adapt(self, base_decision: Dict, world_context: WorldContext) -> Dict[str, Any]:
        """Adapt decision in real-time based on world model feedback."""
        adaptations = {}
        
        # Real-time risk adaptation
        adaptations["risk_adaptation"] = self._adaptive_risk_control(base_decision, world_context)
        
        # Real-time strategy adaptation
        adaptations["strategy_adaptation"] = self._adaptive_strategy_selection(base_decision, world_context)
        
        # Real-time timing adaptation
        adaptations["timing_adaptation"] = self._adaptive_timing_optimization(base_decision, world_context)
        
        return adaptations
    
    def _adaptive_risk_control(self, decision: Dict, world_context: WorldContext) -> Dict:
        """Adaptive risk control based on real-time conditions."""
        risk_control = {}
        
        market_volatility = world_context.market_context.get("volatility", 0.2)
        context_confidence = world_context.confidence
        
        # Dynamic risk limits
        if market_volatility > 0.6 or context_confidence < 0.3:
            risk_control["risk_limit"] = "emergency"
            risk_control["position_limit"] = 0.1
        elif market_volatility > 0.4 or context_confidence < 0.5:
            risk_control["risk_limit"] = "high"
            risk_control["position_limit"] = 0.3
        else:
            risk_control["risk_limit"] = "normal"
            risk_control["position_limit"] = 1.0
        
        return risk_control
    
    def _adaptive_strategy_selection(self, decision: Dict, world_context: WorldContext) -> Dict:
        """Adaptive strategy selection based on real-time conditions."""
        strategy_selection = {}
        
        market_regime = world_context.market_context.get("regime", "neutral")
        
        # Dynamic strategy selection
        if market_regime == "volatile":
            strategy_selection["primary_strategy"] = "risk_averse"
            strategy_selection["secondary_strategy"] = "range_trading"
        elif market_regime == "trending":
            strategy_selection["primary_strategy"] = "momentum"
            strategy_selection["secondary_strategy"] = "breakout"
        else:
            strategy_selection["primary_strategy"] = "mean_reversion"
            strategy_selection["secondary_strategy"] = "balanced"
        
        return strategy_selection
    
    def _adaptive_timing_optimization(self, decision: Dict, world_context: WorldContext) -> Dict:
        """Adaptive timing optimization based on real-time conditions."""
        timing_optimization = {}
        
        workflow_load = world_context.workflow_context.get("active_executions", 0)
        market_liquidity = world_context.market_context.get("liquidity", 1.0)
        
        # Dynamic timing
        if workflow_load > 100 or market_liquidity < 0.5:
            timing_optimization["execution_delay"] = 2.0  # Add delay
        elif workflow_load < 20 and market_liquidity > 0.9:
            timing_optimization["execution_delay"] = -0.5  # Expedite
        else:
            timing_optimization["execution_delay"] = 0.0  # Normal timing
        
        return timing_optimization


class PredictiveGuidance:
    """Predictive guidance using world model insights."""
    
    def guide(self, base_decision: Dict, world_context: WorldContext, context_history: deque) -> Dict[str, Any]:
        """Provide predictive guidance for decision making."""
        guidance = {}
        
        # Predictive risk guidance
        guidance["risk_prediction"] = self._predict_risk_evolution(world_context, context_history)
        
        # Predictive opportunity guidance
        guidance["opportunity_prediction"] = self._predict_opportunities(world_context, context_history)
        
        # Predictive timing guidance
        guidance["timing_prediction"] = self._predict_optimal_timing(world_context, context_history)
        
        return guidance
    
    def predict_evolution(self, current_context: WorldContext, context_history: deque, time_horizon: float) -> Dict[str, Any]:
        """Predict world state evolution."""
        if len(context_history) < 5:
            return {"prediction_confidence": 0.0, "evolution_prediction": "insufficient_history"}
        
        # Extract trends from context history
        volatility_trend = self._extract_trend([ctx.market_context.get("volatility", 0.2) for ctx in context_history])
        regime_trend = self._extract_regime_trend([ctx.market_context.get("regime", "neutral") for ctx in context_history])
        
        # Predict evolution
        prediction = {
            "volatility_prediction": current_context.market_context.get("volatility", 0.2) + volatility_trend * time_horizon / 3600,
            "regime_prediction": regime_trend,
            "confidence": min(1.0, len(context_history) / 20.0),
            "time_horizon": time_horizon
        }
        
        return prediction
    
    def _predict_risk_evolution(self, world_context: WorldContext, context_history: deque) -> Dict:
        """Predict risk evolution based on context history."""
        if len(context_history) < 3:
            return {"prediction_confidence": 0.0}
        
        # Calculate risk trend
        recent_risks = []
        for ctx in context_history[-5:]:
            risk_factors = []
            if ctx.operator_context and ctx.operator_context.get("risk_profile") == "AGGRESSIVE":
                risk_factors.append(0.3)
            if ctx.platform_context:
                risk_factors.extend([1.0 - pctx.get("health_score", 0.5) for pctx in ctx.platform_context.values()])
            if ctx.market_context and ctx.market_context.get("volatility", 0.2) > 0.4:
                risk_factors.append(0.4)
            
            recent_risks.append(np.mean(risk_factors) if risk_factors else 0.5)
        
        risk_trend = self._extract_trend(recent_risks)
        
        return {
            "current_risk": recent_risks[-1] if recent_risks else 0.5,
            "risk_trend": risk_trend,
            "predicted_risk": max(0.0, min(1.0, recent_risks[-1] + risk_trend)) if recent_risks else 0.5,
            "confidence": min(1.0, len(context_history) / 15.0)
        }
    
    def _predict_opportunities(self, world_context: WorldContext, context_history: deque) -> Dict:
        """Predict trading opportunities based on context."""
        # Simple opportunity prediction based on regime
        market_regime = world_context.market_context.get("regime", "neutral")
        
        if market_regime == "bullish":
            return {
                "opportunity_type": "long_positions",
                "confidence": 0.7,
                "expected_duration": "medium_term"
            }
        elif market_regime == "bearish":
            return {
                "opportunity_type": "short_positions",
                "confidence": 0.7,
                "expected_duration": "short_term"
            }
        else:
            return {
                "opportunity_type": "range_trading",
                "confidence": 0.5,
                "expected_duration": "variable"
            }
    
    def _predict_optimal_timing(self, world_context: WorldContext, context_history: deque) -> Dict:
        """Predict optimal timing for execution."""
        # Optimal timing based on market conditions
        market_volatility = world_context.market_context.get("volatility", 0.2)
        market_liquidity = world_context.market_context.get("liquidity", 1.0)
        
        if market_volatility < 0.2 and market_liquidity > 0.8:
            return {
                "timing_recommendation": "immediate",
                "reason": "favorable_conditions"
            }
        elif market_volatility > 0.6 or market_liquidity < 0.4:
            return {
                "timing_recommendation": "delay",
                "reason": "unfavorable_conditions"
            }
        else:
            return {
                "timing_recommendation": "monitor",
                "reason": "uncertain_conditions"
            }
    
    def _extract_trend(self, values: List[float]) -> float:
        """Extract trend from values."""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        y = np.array(values)
        slope = np.polyfit(x, y, 1)[0]
        return slope
    
    def _extract_regime_trend(self, regimes: List[str]) -> str:
        """Extract regime trend."""
        if len(regimes) < 3:
            return regimes[-1] if regimes else "neutral"
        
        # Count regime occurrences
        regime_counts = {regime: regimes.count(regime) for regime in set(regimes)}
        
        # Return most common regime
        return max(regime_counts.items(), key=lambda x: x[1])[0]


# Singleton instance
_world_model_integrator: Optional[WorldModelIntegrator] = None
_world_model_integrator_lock = threading.Lock()


def get_world_model_integrator() -> WorldModelIntegrator:
    """Get the singleton world model integrator instance."""
    global _world_model_integrator
    if _world_model_integrator is None:
        with _world_model_integrator_lock:
            if _world_model_integrator is None:
                _world_model_integrator = WorldModelIntegrator()
    return _world_model_integrator


__all__ = [
    "WorldModelIntegrator",
    "get_world_model_integrator",
    "IntegrationMode",
    "WorldContext",
    "EnhancedDecision",
    "FeedbackLoop",
]