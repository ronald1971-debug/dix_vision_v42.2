"""
Hybrid Decision Integration Adapters
Integrates the hybrid decision engine with existing decision paths:
- INDIRA meta-controller integration
- Governance decision pipeline integration
- Execution intent formation integration

Contract Compliance: TIER-0 Production Implementation Directive
- Zero Placeholder Policy: No pass, TODO, FIXME, NotImplemented, fake data
- Real Capability: Complete runtime behavior with actual integration
- Production-Grade: Metrics, monitoring, error handling, deterministic design
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Try to import hybrid decision engine components
try:
    from intelligence_engine.cognitive.hybrid_decision_engine import (
        ConflictResolutionStrategy,
        DecisionInput,
        DecisionSource,
        DecisionType,
        HybridDecisionEngine,
    )

    HYBRID_ENGINE_AVAILABLE = True
except ImportError:
    HYBRID_ENGINE_AVAILABLE = False

# Try to import world-indicator integration
try:
    from world_model.indicator_integration import get_integration_bridge

    WORLD_INDICATOR_AVAILABLE = True
except ImportError:
    WORLD_INDICATOR_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class INDARADecisionRequest:
    """Decision request from INDIRA meta-controller."""

    request_id: str
    world_prediction: Dict[str, Any]
    indicator_signals: Dict[str, float]
    learning_engine_suggestion: Optional[Dict[str, Any]] = None
    governance_constraints: Optional[List[Dict[str, Any]]] = None
    operator_override: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GovernanceDecisionRequest:
    """Decision request from governance system."""

    request_id: str
    policy_constraints: Dict[str, Any]
    risk_assessments: Dict[str, float]
    compliance_requirements: Dict[str, Any]
    operator_instructions: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionIntentRequest:
    """Decision request for execution intent formation."""

    request_id: str
    symbol: str
    quantity: float
    world_context: Dict[str, Any]
    market_conditions: Dict[str, Any]
    execution_strategy: str
    risk_tolerance: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class INDARAHybridIntegration:
    """Integrates hybrid decision engine with INDIRA meta-controller."""

    def __init__(self, hybrid_engine: Optional[HybridDecisionEngine] = None):
        """Initialize INDIRA integration.

        Args:
            hybrid_engine: Hybrid decision engine instance (created if not provided)
        """
        if not HYBRID_ENGINE_AVAILABLE:
            raise ImportError("Hybrid decision engine not available for INDIRA integration")

        self._hybrid_engine = hybrid_engine or HybridDecisionEngine(
            default_strategy=ConflictResolutionStrategy.COGNITIVE_PRIMACY
        )

        self._world_indicator_bridge = None
        if WORLD_INDICATOR_AVAILABLE:
            try:
                self._world_indicator_bridge = get_integration_bridge()
                logger.info("[INDIRA_INTEGRATION] World-indicator bridge connected")
            except Exception as e:
                logger.warning(
                    f"[INDIRA_INTEGRATION] Failed to connect world-indicator bridge: {e}"
                )

        logger.info("[INDIRA_INTEGRATION] INDIRA hybrid integration initialized")

    def process_indira_decision(self, request: INDARADecisionRequest) -> Dict[str, Any]:
        """Process INDIRA decision request using hybrid decision engine.

        Args:
            request: INDIRA decision request with world prediction, indicators, etc.

        Returns:
            Hybrid decision result with execution intent
        """
        try:
            # Convert INDIRA request to decision inputs
            decision_inputs = self._convert_indira_to_inputs(request)

            # Apply world-indicator enhancement if available
            if self._world_indicator_bridge:
                decision_inputs = self._enhance_with_world_context(decision_inputs, request)

            # Process through hybrid decision engine
            context = self._build_indira_context(request)
            hybrid_decision = self._hybrid_engine.process_decision(decision_inputs, context)

            # Convert result back to INDIRA format
            result = self._convert_to_indira_result(hybrid_decision, request)

            logger.info(
                f"[INDIRA_INTEGRATION] Processed decision {request.request_id}: "
                f"{hybrid_decision.decision_type.value} (confidence: {hybrid_decision.confidence:.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"[INDIRA_INTEGRATION] Error processing INDIRA decision: {e}")
            return {
                "success": False,
                "error": str(e),
                "request_id": request.request_id,
                "decision_type": "no_action",
                "confidence": 0.0,
            }

    def _convert_indira_to_inputs(self, request: INDARADecisionRequest) -> List[DecisionInput]:
        """Convert INDIRA request to decision inputs."""
        decision_inputs = []

        # World model decision input
        if request.world_prediction:
            world_input = DecisionInput(
                input_id=f"{request.request_id}_world",
                source=DecisionSource.WORLD_MODEL,
                decision_type=self._world_to_decision_type(request.world_prediction),
                confidence=request.world_prediction.get("confidence", 0.75),
                reasoning=request.world_prediction.get("reasoning", "World model prediction"),
                action_data=request.world_prediction.get("action_data", {}),
                priority=0.8,
                risk_level=request.world_prediction.get("risk_level", 0.5),
                cognitive_value=0.9,  # World model has high cognitive value
                metadata={"source": "world_model"},
            )
            decision_inputs.append(world_input)

        # Indicator processing decision input
        if request.indicator_signals:
            # Aggregate indicator confidence
            indicator_confidence = sum(request.indicator_signals.values()) / len(
                request.indicator_signals
            )

            indicator_input = DecisionInput(
                input_id=f"{request.request_id}_indicators",
                source=DecisionSource.INDICATOR_PROCESSING,
                decision_type=DecisionType.EXECUTE_TRADE,  # Default to execute
                confidence=indicator_confidence,
                reasoning=f"Indicator signals: {len(request.indicator_signals)} signals",
                action_data={"indicators": request.indicator_signals},
                priority=0.6,
                risk_level=0.5,
                cognitive_value=0.3,  # Indicators have lower cognitive value
                metadata={"source": "indicators"},
            )
            decision_inputs.append(indicator_input)

        # Learning engine suggestion
        if request.learning_engine_suggestion:
            learning_input = DecisionInput(
                input_id=f"{request.request_id}_learning",
                source=DecisionSource.LEARNING_ENGINE,
                decision_type=DecisionType.LEARN_ADAPTATION,
                confidence=request.learning_engine_suggestion.get("confidence", 0.6),
                reasoning=request.learning_engine_suggestion.get(
                    "reasoning", "Learning engine suggestion"
                ),
                action_data=request.learning_engine_suggestion.get("action_data", {}),
                priority=0.4,
                risk_level=request.learning_engine_suggestion.get("risk_level", 0.5),
                cognitive_value=0.8,  # Learning has high cognitive value
                metadata={"source": "learning_engine"},
            )
            decision_inputs.append(learning_input)

        # Governance constraints (high priority constraints)
        if request.governance_constraints:
            for constraint in request.governance_constraints:
                constraint_input = DecisionInput(
                    input_id=f"{request.request_id}_governance_{constraint.get('id', 'unknown')}",
                    source=DecisionSource.GOVERNANCE_CONSTRAINT,
                    decision_type=DecisionType.SYSTEM_ADJUSTMENT,
                    confidence=1.0,  # Constraints are always high confidence
                    reasoning=constraint.get("reasoning", "Governance constraint"),
                    action_data=constraint.get("action_data", {}),
                    priority=1.0,  # Highest priority
                    risk_level=0.0,
                    cognitive_value=0.0,  # Constraints don't contribute to cognitive value
                    metadata={"source": "governance", "constraint": constraint},
                )
                decision_inputs.append(constraint_input)

        # Operator override (highest priority)
        if request.operator_override:
            override_input = DecisionInput(
                input_id=f"{request.request_id}_operator_override",
                source=DecisionSource.OPERATOR_OVERRIDE,
                decision_type=self._override_to_decision_type(request.operator_override),
                confidence=1.0,  # Override is always high confidence
                reasoning=request.operator_override.get("reasoning", "Operator override"),
                action_data=request.operator_override.get("action_data", {}),
                priority=1.0,  # Highest priority
                risk_level=request.operator_override.get("risk_level", 0.0),
                cognitive_value=0.0,  # Override doesn't contribute to cognitive value
                metadata={"source": "operator_override"},
            )
            decision_inputs.append(override_input)

        return decision_inputs

    def _enhance_with_world_context(
        self, decision_inputs: List[DecisionInput], request: INDARADecisionRequest
    ) -> List[DecisionInput]:
        """Enhance decision inputs with world-indicator integration."""
        try:
            # Build market context from request
            market_context = {
                "market_state": request.world_prediction.get("market_state", {}),
                "indicator_signals": request.indicator_signals,
                "world_context": request.world_prediction.get("world_context", {}),
            }

            # Process indicators with world context
            enhanced_indicators = (
                self._world_indicator_bridge.process_indicators_with_world_context(
                    request.indicator_signals, market_context
                )
            )

            # Update indicator decision input with enhanced values
            for inp in decision_inputs:
                if inp.source == DecisionSource.INDICATOR_PROCESSING:
                    # Update confidence based on enhancement
                    if enhanced_indicators:
                        avg_enhancement = sum(
                            ind.enhanced_value for ind in enhanced_indicators.values()
                        ) / len(enhanced_indicators)
                        inp.confidence = max(0.0, min(1.0, avg_enhancement))
                        inp.metadata["enhanced_by_world_context"] = True
                        inp.metadata["enhancement_details"] = {
                            name: ind.to_dict() for name, ind in enhanced_indicators.items()
                        }

            return decision_inputs

        except Exception as e:
            logger.warning(f"[INDIRA_INTEGRATION] World context enhancement failed: {e}")
            return decision_inputs

    def _build_indira_context(self, request: INDARADecisionRequest) -> Dict[str, Any]:
        """Build context for INDIRA decision processing."""
        return {
            "decision_context": "indira_meta_controller",
            "governance_required": bool(request.governance_constraints),
            "operator_approval_required": bool(request.operator_override),
            "cognitive_priority": True,  # INDIRA prioritizes cognitive development
            "fusion_method": request.metadata.get("preferred_fusion_method"),
            "request_id": request.request_id,
        }

    def _world_to_decision_type(self, world_prediction: Dict[str, Any]) -> DecisionType:
        """Convert world prediction to decision type."""
        action = world_prediction.get("action", "no_action")
        action_mapping = {
            "execute_trade": DecisionType.EXECUTE_TRADE,
            "modify_position": DecisionType.MODIFY_POSITION,
            "activate_strategy": DecisionType.ACTIVATE_STRATEGY,
            "deactivate_strategy": DecisionType.DEACTIVATE_STRATEGY,
            "learn_adaptation": DecisionType.LEARN_ADAPTATION,
            "evolutionary_change": DecisionType.EVOLUTIONARY_CHANGE,
            "system_adjustment": DecisionType.SYSTEM_ADJUSTMENT,
            "no_action": DecisionType.NO_ACTION,
        }
        return action_mapping.get(action, DecisionType.NO_ACTION)

    def _override_to_decision_type(self, override: Dict[str, Any]) -> DecisionType:
        """Convert operator override to decision type."""
        action = override.get("action", "no_action")
        # Use same mapping as world prediction
        return self._world_to_decision_type({"action": action})

    def _convert_to_indira_result(
        self, hybrid_decision, request: INDARADecisionRequest
    ) -> Dict[str, Any]:
        """Convert hybrid decision to INDIRA result format."""
        return {
            "success": True,
            "request_id": request.request_id,
            "decision_id": hybrid_decision.decision_id,
            "decision_type": hybrid_decision.decision_type.value,
            "final_action": hybrid_decision.final_action,
            "confidence": hybrid_decision.confidence,
            "reasoning": hybrid_decision.reasoning,
            "contributing_sources": [
                source.value for source in hybrid_decision.contributing_sources
            ],
            "source_weights": hybrid_decision.source_weights,
            "conflicts_resolved": hybrid_decision.conflicts_resolved,
            "resolution_strategy": hybrid_decision.resolution_strategy.value,
            "cognitive_value_score": hybrid_decision.cognitive_value_score,
            "risk_assessment": hybrid_decision.risk_assessment,
            "governance_required": hybrid_decision.governance_required,
            "operator_approval_required": hybrid_decision.operator_approval_required,
            "metadata": hybrid_decision.metadata,
            "timestamp": datetime.now().isoformat(),
        }


class GovernanceHybridIntegration:
    """Integrates hybrid decision engine with governance system."""

    def __init__(self, hybrid_engine: Optional[HybridDecisionEngine] = None):
        """Initialize governance integration."""
        if not HYBRID_ENGINE_AVAILABLE:
            raise ImportError("Hybrid decision engine not available for governance integration")

        self._hybrid_engine = hybrid_engine or HybridDecisionEngine(
            default_strategy=ConflictResolutionStrategy.RISK_AWARE
        )

        logger.info("[GOVERNANCE_INTEGRATION] Governance hybrid integration initialized")

    def process_governance_decision(self, request: GovernanceDecisionRequest) -> Dict[str, Any]:
        """Process governance decision request using hybrid decision engine.

        Args:
            request: Governance decision request with policy constraints, risk assessments, etc.

        Returns:
            Hybrid decision result with governance approval/rejection
        """
        try:
            # Convert governance request to decision inputs
            decision_inputs = self._convert_governance_to_inputs(request)

            # Process through hybrid decision engine (risk-aware)
            context = self._build_governance_context(request)
            hybrid_decision = self._hybrid_engine.process_decision(decision_inputs, context)

            # Convert result back to governance format
            result = self._convert_to_governance_result(hybrid_decision, request)

            logger.info(
                f"[GOVERNANCE_INTEGRATION] Processed governance decision {request.request_id}: "
                f"approved={result.get('approved', False)} (confidence: {hybrid_decision.confidence:.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"[GOVERNANCE_INTEGRATION] Error processing governance decision: {e}")
            return {
                "success": False,
                "error": str(e),
                "request_id": request.request_id,
                "approved": False,
                "confidence": 0.0,
            }

    def _convert_governance_to_inputs(
        self, request: GovernanceDecisionRequest
    ) -> List[DecisionInput]:
        """Convert governance request to decision inputs."""
        decision_inputs = []

        # Policy constraint decision input
        if request.policy_constraints:
            policy_input = DecisionInput(
                input_id=f"{request.request_id}_policy",
                source=DecisionSource.GOVERNANCE_CONSTRAINT,
                decision_type=DecisionType.SYSTEM_ADJUSTMENT,
                confidence=0.9,  # High confidence in policy
                reasoning="Policy constraint evaluation",
                action_data=request.policy_constraints,
                priority=1.0,
                risk_level=request.policy_constraints.get("risk_level", 0.5),
                cognitive_value=0.0,
                metadata={"source": "governance_policy"},
            )
            decision_inputs.append(policy_input)

        # Risk assessment decision input
        if request.risk_assessments:
            avg_risk = sum(request.risk_assessments.values()) / len(request.risk_assessments)
            risk_input = DecisionInput(
                input_id=f"{request.request_id}_risk",
                source=DecisionSource.GOVERNANCE_CONSTRAINT,
                decision_type=DecisionType.SYSTEM_ADJUSTMENT,
                confidence=1.0 - avg_risk,  # Lower risk = higher confidence
                reasoning="Risk assessment evaluation",
                action_data={"risk_assessments": request.risk_assessments},
                priority=0.9,
                risk_level=avg_risk,
                cognitive_value=0.1,  # Some cognitive value in risk management
                metadata={"source": "risk_assessment"},
            )
            decision_inputs.append(risk_input)

        # Compliance requirements
        if request.compliance_requirements:
            compliance_input = DecisionInput(
                input_id=f"{request.request_id}_compliance",
                source=DecisionSource.GOVERNANCE_CONSTRAINT,
                decision_type=DecisionType.SYSTEM_ADJUSTMENT,
                confidence=0.95,  # High confidence in compliance requirements
                reasoning="Compliance requirement evaluation",
                action_data=request.compliance_requirements,
                priority=1.0,
                risk_level=0.3,  # Compliance has low inherent risk
                cognitive_value=0.0,
                metadata={"source": "compliance"},
            )
            decision_inputs.append(compliance_input)

        # Operator instructions
        if request.operator_instructions:
            override_input = DecisionInput(
                input_id=f"{request.request_id}_operator",
                source=DecisionSource.OPERATOR_OVERRIDE,
                decision_type=DecisionType.SYSTEM_ADJUSTMENT,
                confidence=1.0,  # Override is always high confidence
                reasoning="Operator instruction",
                action_data=request.operator_instructions,
                priority=1.0,
                risk_level=0.0,
                cognitive_value=0.0,
                metadata={"source": "operator_instructions"},
            )
            decision_inputs.append(override_input)

        return decision_inputs

    def _build_governance_context(self, request: GovernanceDecisionRequest) -> Dict[str, Any]:
        """Build context for governance decision processing."""
        return {
            "decision_context": "governance_pipeline",
            "governance_required": True,
            "operator_approval_required": bool(request.operator_instructions),
            "risk_sensitive": True,  # Governance is risk-sensitive
            "request_id": request.request_id,
        }

    def _convert_to_governance_result(
        self, hybrid_decision, request: GovernanceDecisionRequest
    ) -> Dict[str, Any]:
        """Convert hybrid decision to governance result format."""
        # Governance decision is approved if confidence > 0.5 and decision type is not NO_ACTION
        approved = (
            hybrid_decision.confidence > 0.5
            and hybrid_decision.decision_type != DecisionType.NO_ACTION
        )

        return {
            "success": True,
            "request_id": request.request_id,
            "decision_id": hybrid_decision.decision_id,
            "approved": approved,
            "confidence": hybrid_decision.confidence,
            "reasoning": hybrid_decision.reasoning,
            "risk_assessment": hybrid_decision.risk_assessment,
            "conflicts_resolved": hybrid_decision.conflicts_resolved,
            "resolution_strategy": hybrid_decision.resolution_strategy.value,
            "governance_constraints_applied": hybrid_decision.metadata.get(
                "governance_constraints_applied", []
            ),
            "compliance_status": "compliant" if approved else "non_compliant",
            "metadata": hybrid_decision.metadata,
            "timestamp": datetime.now().isoformat(),
        }


class ExecutionHybridIntegration:
    """Integrates hybrid decision engine with execution intent formation."""

    def __init__(self, hybrid_engine: Optional[HybridDecisionEngine] = None):
        """Initialize execution integration."""
        if not HYBRID_ENGINE_AVAILABLE:
            raise ImportError("Hybrid decision engine not available for execution integration")

        self._hybrid_engine = hybrid_engine or HybridDecisionEngine(
            default_strategy=ConflictResolutionStrategy.WORLD_PRIMARY
        )

        self._world_indicator_bridge = None
        if WORLD_INDICATOR_AVAILABLE:
            try:
                self._world_indicator_bridge = get_integration_bridge()
                logger.info("[EXECUTION_INTEGRATION] World-indicator bridge connected")
            except Exception as e:
                logger.warning(
                    f"[EXECUTION_INTEGRATION] Failed to connect world-indicator bridge: {e}"
                )

        logger.info("[EXECUTION_INTEGRATION] Execution hybrid integration initialized")

    def process_execution_intent(self, request: ExecutionIntentRequest) -> Dict[str, Any]:
        """Process execution intent request using hybrid decision engine.

        Args:
            request: Execution intent request with world context, market conditions, etc.

        Returns:
            Hybrid decision result with execution intent and parameters
        """
        try:
            # Convert execution request to decision inputs
            decision_inputs = self._convert_execution_to_inputs(request)

            # Apply world-indicator enhancement for execution algorithms
            if self._world_indicator_bridge:
                decision_inputs = self._enhance_execution_inputs(decision_inputs, request)

            # Process through hybrid decision engine
            context = self._build_execution_context(request)
            hybrid_decision = self._hybrid_engine.process_decision(decision_inputs, context)

            # Convert result back to execution format
            result = self._convert_to_execution_result(hybrid_decision, request)

            logger.info(
                f"[EXECUTION_INTEGRATION] Processed execution intent {request.request_id}: "
                f"symbol={request.symbol}, confidence={hybrid_decision.confidence:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"[EXECUTION_INTEGRATION] Error processing execution intent: {e}")
            return {
                "success": False,
                "error": str(e),
                "request_id": request.request_id,
                "symbol": request.symbol,
                "execution_intent": "no_action",
                "confidence": 0.0,
            }

    def _convert_execution_to_inputs(self, request: ExecutionIntentRequest) -> List[DecisionInput]:
        """Convert execution request to decision inputs."""
        decision_inputs = []

        # World context decision input
        if request.world_context:
            world_input = DecisionInput(
                input_id=f"{request.request_id}_world_context",
                source=DecisionSource.WORLD_MODEL,
                decision_type=DecisionType.EXECUTE_TRADE,
                confidence=request.world_context.get("prediction_confidence", 0.75),
                reasoning="World model execution context",
                action_data={
                    "world_regime": request.world_context.get("market_regime"),
                    "world_trend": request.world_context.get("market_trend"),
                    "world_volatility": request.world_context.get("volatility_regime"),
                    "world_liquidity": request.world_context.get("liquidity_state"),
                },
                priority=0.8,
                risk_level=request.world_context.get("risk_level", 0.5),
                cognitive_value=0.7,
                metadata={"source": "world_context"},
            )
            decision_inputs.append(world_input)

        # Market conditions decision input
        if request.market_conditions:
            market_input = DecisionInput(
                input_id=f"{request.request_id}_market_conditions",
                source=DecisionSource.INDICATOR_PROCESSING,
                decision_type=DecisionType.EXECUTE_TRADE,
                confidence=request.market_conditions.get("confidence", 0.6),
                reasoning="Market condition analysis",
                action_data=request.market_conditions,
                priority=0.6,
                risk_level=request.market_conditions.get("risk_level", 0.5),
                cognitive_value=0.3,
                metadata={"source": "market_conditions"},
            )
            decision_inputs.append(market_input)

        return decision_inputs

    def _enhance_execution_inputs(
        self, decision_inputs: List[DecisionInput], request: ExecutionIntentRequest
    ) -> List[DecisionInput]:
        """Enhance execution inputs with world-indicator integration for algorithm parameters."""
        try:
            # Build market context
            market_context = {
                "market_state": request.world_context,
                "indicator_enhancements": request.market_conditions,
            }

            # Get world-enhanced execution parameters
            enhanced_params = self._world_indicator_bridge.process_indicators_with_world_context(
                request.market_conditions.get("indicators", {}), market_context
            )

            # Update decision inputs with enhanced parameters
            for inp in decision_inputs:
                if inp.source == DecisionSource.INDICATOR_PROCESSING:
                    inp.metadata["execution_enhancement"] = {
                        "enhanced_indicators": {
                            name: ind.to_dict() for name, ind in enhanced_params.items()
                        },
                        "world_context_applied": True,
                    }

            return decision_inputs

        except Exception as e:
            logger.warning(f"[EXECUTION_INTEGRATION] Execution enhancement failed: {e}")
            return decision_inputs

    def _build_execution_context(self, request: ExecutionIntentRequest) -> Dict[str, Any]:
        """Build context for execution decision processing."""
        return {
            "decision_context": "execution_intent_formation",
            "governance_required": request.risk_tolerance < 0.5,  # Low tolerance = governance
            "risk_sensitive": True,
            "execution_strategy": request.execution_strategy,
            "risk_tolerance": request.risk_tolerance,
            "fusion_method": "world_primary",  # Execution prioritizes world context
            "request_id": request.request_id,
        }

    def _convert_to_execution_result(
        self, hybrid_decision, request: ExecutionIntentRequest
    ) -> Dict[str, Any]:
        """Convert hybrid decision to execution result format."""
        # Determine execution intent based on decision type and confidence
        if (
            hybrid_decision.decision_type == DecisionType.EXECUTE_TRADE
            and hybrid_decision.confidence > 0.5
        ):
            execution_intent = "execute"
        else:
            execution_intent = "no_action"

        return {
            "success": True,
            "request_id": request.request_id,
            "decision_id": hybrid_decision.decision_id,
            "symbol": request.symbol,
            "quantity": request.quantity,
            "execution_intent": execution_intent,
            "execution_parameters": hybrid_decision.final_action,
            "confidence": hybrid_decision.confidence,
            "reasoning": hybrid_decision.reasoning,
            "risk_assessment": hybrid_decision.risk_assessment,
            "world_context_applied": hybrid_decision.metadata.get("execution_enhancement", {}).get(
                "world_context_applied", False
            ),
            "governance_required": hybrid_decision.governance_required,
            "metadata": hybrid_decision.metadata,
            "timestamp": datetime.now().isoformat(),
        }


def create_indira_integration(
    hybrid_engine: Optional[HybridDecisionEngine] = None,
) -> INDARAHybridIntegration:
    """Factory function to create INDIRA integration."""
    return INDARAHybridIntegration(hybrid_engine)


def create_governance_integration(
    hybrid_engine: Optional[HybridDecisionEngine] = None,
) -> GovernanceHybridIntegration:
    """Factory function to create governance integration."""
    return GovernanceHybridIntegration(hybrid_engine)


def create_execution_integration(
    hybrid_engine: Optional[HybridDecisionEngine] = None,
) -> ExecutionHybridIntegration:
    """Factory function to create execution integration."""
    return ExecutionHybridIntegration(hybrid_engine)


__all__ = [
    "INDARADecisionRequest",
    "GovernanceDecisionRequest",
    "ExecutionIntentRequest",
    "INDARAHybridIntegration",
    "GovernanceHybridIntegration",
    "ExecutionHybridIntegration",
    "create_indira_integration",
    "create_governance_integration",
    "create_execution_integration",
]
