"""
intelligence_engine.decision_maker
DIX VISION v42.2 — Production-Grade Decision-Making Engine

Real-time decision-making engine with multi-criteria decision analysis,
risk assessment, utility optimization, and decision confidence calibration.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import json
from collections import defaultdict

from system.time_source import now

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions."""
    STRATEGIC = "strategic"  # Long-term strategic decisions
    TACTICAL = "tactical"  # Medium-term tactical decisions
    OPERATIONAL = "operational"  # Short-term operational decisions
    REACTIVE = "reactive"  # Immediate response decisions
    PREEMPTIVE = "preemptive"  # Proactive decisions


class DecisionCriteria(Enum):
    """Decision criteria."""
    PROFITABILITY = "profitability"  # Profit potential
    RISK = "risk"  # Risk exposure
    CONFIDENCE = "confidence"  # Decision confidence
    TIMING = "timing"  # Timing appropriateness
    COST = "cost"  # Cost/expense
    RETURN = "return"  # Expected return
    REGULATORY = "regulatory"  # Regulatory compliance
    REPUTATION = "reputation"  # Reputation impact


@dataclass
class DecisionAlternative:
    """A decision alternative."""
    alternative_id: str
    description: str
    criteria_scores: Dict[DecisionCriteria, float] = field(default_factory=dict)
    estimated_outcomes: Dict[str, Any] = field(default_factory=dict)
    risk_factors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionContext:
    """Context for a decision."""
    context_id: str
    market_conditions: Dict[str, Any] = field(default_factory=dict)
    system_state: Dict[str, Any] = field(default_factory=dict)
    risk_environment: Dict[str, Any] = field(default_factory=dict)
    temporal_constraints: Dict[str, Any] = field(default_factory=dict)
    resource_constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionCriteriaWeights:
    """Weights for decision criteria."""
    weights: Dict[DecisionCriteria, float] = field(default_factory=dict)
    
    def __post_init__(self):
        # Default weights if not specified
        if not self.weights:
            self.weights = {
                DecisionCriteria.PROFITABILITY: 0.25,
                DecisionCriteria.RISK: 0.20,
                DecisionCriteria.CONFIDENCE: 0.15,
                DecisionCriteria.TIMING: 0.15,
                DecisionCriteria.COST: 0.10,
                DecisionCriteria.RETURN: 0.10,
                DecisionCriteria.REGULATORY: 0.05,
                DecisionCriteria.REPUTATION: 0.00
            }


@dataclass
class DecisionResult:
    """Result of a decision-making process."""
    decision_id: str
    decision_type: DecisionType
    chosen_alternative: DecisionAlternative
    decision_score: float
    confidence: float
    reasoning: str
    alternative_scores: Dict[str, float] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""
    timestamp: str = ""


class ProductionDecisionMaker:
    """Production-grade decision-making engine.
    
    Provides:
    - Multi-criteria decision analysis (MCDA)
    - Real-time decision optimization
    - Risk-adjusted decision scoring
    - Decision confidence calibration
    - Alternative ranking and selection
    """
    
    def __init__(self) -> None:
        self._decision_history: List[DecisionResult] = []
        self._criteria_weights = DecisionCriteriaWeights()
        self._confidence_threshold = 0.6
        self._risk_tolerance = 0.5
        self._decision_timeouts = {
            DecisionType.STRATEGIC: 10000,  # 10 seconds
            DecisionType.TACTICAL: 5000,     # 5 seconds
            DecisionType.OPERATIONAL: 1000,   # 1 second
            DecisionType.REACTIVE: 500,       # 500ms
            DecisionType.PREEMPTIVE: 2000     # 2 seconds
        }
        
    def start(self) -> bool:
        """Start the decision-making engine."""
        try:
            logger.info("[DECISION_MAKER] Production decision-maker started")
            return True
        except Exception as e:
            logger.error(f"[DECISION_MAKER] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the decision-making engine."""
        try:
            logger.info("[DECISION_MAKER] Production decision-maker stopped")
            return True
        except Exception as e:
            logger.error(f"[DECISION_MAKER] Failed to stop: {e}")
            return False
    
    def set_criteria_weights(self, weights: Dict[DecisionCriteria, float]) -> None:
        """Set custom criteria weights."""
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.01:
            # Normalize weights
            weights = {k: v / total_weight for k, v in weights.items()}
        
        self._criteria_weights.weights = weights
        logger.info(f"[DECISION_MAKER] Criteria weights updated")
    
    def set_risk_tolerance(self, tolerance: float) -> None:
        """Set risk tolerance (0.0 to 1.0)."""
        self._risk_tolerance = max(0.0, min(1.0, tolerance))
        logger.info(f"[DECISION_MAKER] Risk tolerance set to {self._risk_tolerance:.2f}")
    
    def make_decision(self, 
                     alternatives: List[DecisionAlternative],
                     context: DecisionContext,
                     decision_type: DecisionType = DecisionType.OPERATIONAL,
                     criteria_weights: Optional[DecisionCriteriaWeights] = None) -> DecisionResult:
        """Make a decision using multi-criteria analysis.
        
        Args:
            alternatives: List of decision alternatives
            context: Decision context
            decision_type: Type of decision
            criteria_weights: Optional custom criteria weights
            
        Returns:
            DecisionResult with chosen alternative and confidence
        """
        try:
            decision_id = f"decision_{now().sequence}"
            logger.info(f"[DECISION_MAKER] Making {decision_type.value} decision: {decision_id}")
            
            # Use custom weights if provided
            weights = criteria_weights if criteria_weights else self._criteria_weights
            
            # Score each alternative
            alternative_scores = {}
            for alternative in alternatives:
                score = self._score_alternative(alternative, context, weights)
                alternative_scores[alternative.alternative_id] = score
            
            # Select best alternative
            best_alternative_id = max(alternative_scores, key=alternative_scores.get)
            best_alternative = next((alt for alt in alternatives 
                                    if alt.alternative_id == best_alternative_id), alternatives[0])
            
            # Calculate decision confidence
            confidence = self._calculate_decision_confidence(
                alternative_scores, best_alternative_id, context
            )
            
            # Risk assessment
            risk_assessment = self._assess_decision_risk(best_alternative, context)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                best_alternative, confidence, risk_assessment
            )
            
            # Create decision result
            result = DecisionResult(
                decision_id=decision_id,
                decision_type=decision_type,
                chosen_alternative=best_alternative,
                decision_score=alternative_scores[best_alternative_id],
                confidence=confidence,
                reasoning=self._generate_reasoning(alternative_scores, best_alternative),
                alternative_scores=alternative_scores,
                risk_assessment=risk_assessment,
                recommendation=recommendation,
                timestamp=now().utc_time.isoformat()
            )
            
            # Store in history
            self._decision_history.append(result)
            
            logger.info(f"[DECISION_MAKER] Decision made: {decision_id} with confidence {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"[DECISION_MAKER] Decision making failed: {e}")
            return self._create_error_result(decision_type, str(e))
    
    def _score_alternative(self, alternative: DecisionAlternative,
                          context: DecisionContext,
                          weights: DecisionCriteriaWeights) -> float:
        """Score an alternative using weighted criteria."""
        total_score = 0.0
        
        for criterion, weight in weights.weights.items():
            # Get score for this criterion
            criterion_score = alternative.criteria_scores.get(criterion, 0.5)
            
            # Apply context adjustments
            context_adjustment = self._apply_context_adjustment(
                criterion, criterion_score, context
            )
            
            # Apply risk adjustment
            risk_adjustment = self._apply_risk_adjustment(
                criterion, alternative.risk_factors, context
            )
            
            # Calculate final score for this criterion
            adjusted_score = criterion_score * context_adjustment * risk_adjustment
            
            # Add weighted contribution
            total_score += adjusted_score * weight
        
        return total_score
    
    def _apply_context_adjustment(self, criterion: DecisionCriteria,
                                 base_score: float,
                                 context: DecisionContext) -> float:
        """Apply context-based score adjustments."""
        adjustment = 1.0
        
        # Market condition adjustments
        if criterion == DecisionCriteria.TIMING:
            market_trend = context.market_conditions.get("trend", "neutral")
            if market_trend == "bullish":
                adjustment *= 1.1
            elif market_trend == "bearish":
                adjustment *= 0.9
        
        # System state adjustments
        if criterion == DecisionCriteria.RISK:
            system_load = context.system_state.get("load", 0.5)
            if system_load > 0.8:
                adjustment *= 0.8  # Reduce risk when system is heavily loaded
        
        return adjustment
    
    def _apply_risk_adjustment(self, criterion: DecisionCriteria,
                              risk_factors: List[str],
                              context: DecisionContext) -> float:
        """Apply risk-based score adjustments."""
        adjustment = 1.0
        
        if criterion == DecisionCriteria.RISK:
            # Penalize alternatives with high risk factors
            risk_count = len(risk_factors)
            adjustment *= max(0.5, 1.0 - (risk_count * 0.1))
        
        # Apply risk tolerance
        if criterion == DecisionCriteria.PROFITABILITY:
            # Higher risk tolerance allows more aggressive profitability weighting
            adjustment *= (0.8 + (self._risk_tolerance * 0.4))
        
        return adjustment
    
    def _calculate_decision_confidence(self, 
                                    alternative_scores: Dict[str, float],
                                    best_alternative_id: str,
                                    context: DecisionContext) -> float:
        """Calculate confidence in the decision."""
        if not alternative_scores:
            return 0.0
        
        # Calculate margin of victory
        scores = sorted(alternative_scores.values(), reverse=True)
        if len(scores) > 1:
            margin = scores[0] - scores[1]
            confidence_from_margin = min(margin, 1.0)
        else:
            confidence_from_margin = 1.0
        
        # Calculate score distribution
        if len(scores) > 1:
            std_dev = (max(scores) - min(scores)) / len(scores)
            confidence_from_distribution = min(std_dev, 1.0)
        else:
            confidence_from_distribution = 1.0
        
        # Context-based confidence
        context_confidence = self._calculate_context_confidence(context)
        
        # Combine confidence factors
        overall_confidence = (
            confidence_from_margin * 0.4 +
            confidence_from_distribution * 0.3 +
            context_confidence * 0.3
        )
        
        return overall_confidence
    
    def _calculate_context_confidence(self, context: DecisionContext) -> float:
        """Calculate confidence based on context quality."""
        confidence = 1.0
        
        # Reduce confidence if market conditions are unclear
        if context.market_conditions.get("uncertainty", 0) > 0.7:
            confidence *= 0.7
        
        # Reduce confidence if risk environment is high
        if context.risk_environment.get("risk_level", 0) > 0.8:
            confidence *= 0.8
        
        return confidence
    
    def _assess_decision_risk(self, alternative: DecisionAlternative,
                             context: DecisionContext) -> Dict[str, Any]:
        """Assess the risk of the decision."""
        risk_factors = []
        
        # Analyze alternative risk factors
        for risk in alternative.risk_factors:
            risk_factors.append({
                "factor": risk,
                "severity": self._assess_risk_severity(risk, context)
            })
        
        # Calculate overall risk score
        if risk_factors:
            overall_risk = sum(r["severity"] for r in risk_factors) / len(risk_factors)
        else:
            overall_risk = 0.0
        
        # Risk vs tolerance comparison
        risk_acceptable = overall_risk <= self._risk_tolerance
        
        return {
            "risk_factors": risk_factors,
            "overall_risk": overall_risk,
            "risk_acceptable": risk_acceptable,
            "risk_tolerance": self._risk_tolerance
        }
    
    def _assess_risk_severity(self, risk: str, context: DecisionContext) -> float:
        """Assess severity of a risk factor."""
        # Production-grade risk severity assessment
        severity = 0.5  # Base severity
        
        # Adjust based on context
        risk_keywords = ["market", "liquidity", "operational", "regulatory", "technical"]
        for keyword in risk_keywords:
            if keyword in risk.lower():
                if keyword == "market":
                    severity += 0.2
                elif keyword == "liquidity":
                    severity += 0.3
                elif keyword == "operational":
                    severity += 0.1
                elif keyword == "regulatory":
                    severity += 0.4
                elif keyword == "technical":
                    severity += 0.15
        
        return min(severity, 1.0)
    
    def _generate_recommendation(self, alternative: DecisionAlternative,
                                confidence: float,
                                risk_assessment: Dict[str, Any]) -> str:
        """Generate decision recommendation."""
        if confidence > 0.8 and risk_assessment["risk_acceptable"]:
            return f"Strong recommendation: {alternative.description}"
        elif confidence > 0.6 and risk_assessment["risk_acceptable"]:
            return f"Recommendation: {alternative.description}"
        elif risk_assessment["risk_acceptable"]:
            return f"Cautious recommendation: {alternative.description}"
        else:
            return f"Not recommended: {alternative.description} - risk exceeds tolerance"
    
    def _generate_reasoning(self, alternative_scores: Dict[str, float],
                            best_alternative: DecisionAlternative) -> str:
        """Generate reasoning explanation."""
        sorted_alternatives = sorted(
            alternative_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        reasoning = f"Selected alternative scored {alternative_scores[best_alternative.alternative_id]:.2f}. "
        
        if len(sorted_alternatives) > 1:
            second_best = sorted_alternatives[1]
            margin = alternative_scores[best_alternative.alternative_id] - second_best[1]
            reasoning += f"Margin over next best: {margin:.2f}. "
        
        if best_alternative.risk_factors:
            reasoning += f"Considerations: {len(best_alternative.risk_factors)} risk factors identified."
        
        return reasoning
    
    def _create_error_result(self, decision_type: DecisionType, 
                            error: str) -> DecisionResult:
        """Create error decision result."""
        error_alternative = DecisionAlternative(
            alternative_id="error",
            description="Error in decision making"
        )
        
        return DecisionResult(
            decision_id=f"decision_{now().sequence}",
            decision_type=decision_type,
            chosen_alternative=error_alternative,
            decision_score=0.0,
            confidence=0.0,
            reasoning=f"Error: {error}",
            timestamp=now().utc_time.isoformat()
        )
    
    def make_batch_decision(self, 
                          decision_requests: List[Tuple[List[DecisionAlternative], 
                                                        DecisionContext, 
                                                        DecisionType]]) -> List[DecisionResult]:
        """Make multiple decisions in batch."""
        results = []
        for alternatives, context, decision_type in decision_requests:
            result = self.make_decision(alternatives, context, decision_type)
            results.append(result)
        return results
    
    def get_decision_history(self, limit: int = 100) -> List[DecisionResult]:
        """Get decision history."""
        return self._decision_history[-limit:]
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """Get decision-making statistics."""
        if not self._decision_history:
            return {"message": "No decisions made yet"}
        
        by_type = defaultdict(list)
        total_confidence = 0.0
        
        for decision in self._decision_history:
            by_type[decision.decision_type.value].append(decision)
            total_confidence += decision.confidence
        
        avg_confidence = total_confidence / len(self._decision_history)
        
        return {
            "total_decisions": len(self._decision_history),
            "average_confidence": avg_confidence,
            "decisions_by_type": {k: len(v) for k, v in by_type.items()},
            "recent_decisions": len(self._decision_history[-10:])
        }
    
    def clear_history(self) -> None:
        """Clear decision history."""
        self._decision_history.clear()
        logger.info("[DECISION_MAKER] Decision history cleared")


def get_production_decision_maker() -> ProductionDecisionMaker:
    """Get the singleton production decision-maker instance."""
    if not hasattr(get_production_decision_maker, "_instance"):
        get_production_decision_maker._instance = ProductionDecisionMaker()
    return get_production_decision_maker._instance