"""
intelligence_engine.orchestrator
DIX VISION v42.2 — Intelligence Engine Orchestrator

Central coordination for intelligence operations including reasoning,
decision-making, planning, evaluation, inference, and knowledge integration.
Production-grade implementation with all advanced intelligence components.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional
import threading

from system.time_source import now

# Import production-grade components
from intelligence_engine.reasoner import (
    ProductionReasoner,
    ReasoningType,
    ReasoningComplexity,
    get_production_reasoner
)
from intelligence_engine.decision_maker import (
    ProductionDecisionMaker,
    DecisionType,
    DecisionAlternative,
    DecisionContext,
    DecisionCriteriaWeights,
    get_production_decision_maker
)
from intelligence_engine.planner import (
    ProductionPlanner,
    PlanType,
    PlanningHorizon,
    PlanningGoal,
    PlanningConstraint,
    get_production_planner
)
from intelligence_engine.evaluator import (
    ProductionEvaluator,
    EvaluationCategory,
    EvaluationContext,
    get_production_evaluator
)
from intelligence_engine.inference import (
    ProductionInferenceEngine,
    InferenceType,
    InferenceInput,
    InferenceModel,
    get_production_inference_engine
)
from intelligence_engine.knowledge_integrator import (
    ProductionKnowledgeIntegrator,
    KnowledgeSourceType,
    KnowledgeQuery,
    get_production_knowledge_integrator
)

logger = logging.getLogger(__name__)


@dataclass
class IntelligenceOperation:
    """An intelligence operation."""
    
    operation_id: str
    operation_type: str  # "reasoning" | "decision" | "planning" | "evaluation" | "inference" | "knowledge"
    input_data: dict[str, Any]
    output_data: dict[str, Any] = None
    confidence: float = 0.0
    timestamp: str = ""
    status: str = "pending"  # "pending" | "processing" | "completed" | "failed"
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.timestamp:
            self.timestamp = now().utc_time.isoformat()
        if self.output_data is None:
            self.output_data = {}


class IntelligenceOrchestrator:
    """Orchestrates intelligence operations.
    
    Production-grade orchestrator that coordinates:
    - Reasoning capabilities (via ProductionReasoner)
    - Decision-making capabilities (via ProductionDecisionMaker)
    - Planning capabilities (via ProductionPlanner)
    - Evaluation capabilities (via ProductionEvaluator)
    - Inference capabilities (via ProductionInferenceEngine)
    - Knowledge integration (via ProductionKnowledgeIntegrator)
    """
    
    def __init__(self) -> None:
        self._operations: list[IntelligenceOperation] = []
        self._operation_queue: list[IntelligenceOperation] = []
        
        # Initialize production-grade components
        self._reasoner: Optional[ProductionReasoner] = None
        self._decision_maker: Optional[ProductionDecisionMaker] = None
        self._planner: Optional[ProductionPlanner] = None
        self._evaluator: Optional[ProductionEvaluator] = None
        self._inference_engine: Optional[ProductionInferenceEngine] = None
        self._knowledge_integrator: Optional[ProductionKnowledgeIntegrator] = None
        
        self._lock = threading.Lock()
        
    def start(self) -> bool:
        """Start the intelligence orchestrator and all components."""
        try:
            # Initialize all production-grade components
            self._reasoner = get_production_reasoner()
            self._decision_maker = get_production_decision_maker()
            self._planner = get_production_planner()
            self._evaluator = get_production_evaluator()
            self._inference_engine = get_production_inference_engine()
            self._knowledge_integrator = get_production_knowledge_integrator()
            
            # Start all components
            self._reasoner.start()
            self._decision_maker.start()
            self._planner.start()
            self._evaluator.start()
            self._inference_engine.start()
            self._knowledge_integrator.start()
            
            logger.info("[INTELLIGENCE] Intelligence orchestrator started with production-grade components")
            return True
        except Exception as e:
            logger.error(f"[INTELLIGENCE] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the intelligence orchestrator and all components."""
        try:
            # Stop all components
            if self._reasoner:
                self._reasoner.stop()
            if self._decision_maker:
                self._decision_maker.stop()
            if self._planner:
                self._planner.stop()
            if self._evaluator:
                self._evaluator.stop()
            if self._inference_engine:
                self._inference_engine.stop()
            if self._knowledge_integrator:
                self._knowledge_integrator.stop()
            
            logger.info("[INTELLIGENCE] Intelligence orchestrator stopped")
            return True
        except Exception as e:
            logger.error(f"[INTELLIGENCE] Failed to stop: {e}")
            return False
    
    # Reasoning Operations
    def reason(self, query: dict[str, Any], 
               reasoning_type: str = "deductive",
               complexity: str = "moderate") -> IntelligenceOperation:
        """Perform reasoning using production-grade reasoner."""
        if not self._reasoner:
            return self._create_disabled_operation("reasoning")
        
        try:
            reasoning_type_enum = ReasoningType(reasoning_type)
            complexity_enum = ReasoningComplexity(complexity)
            
            result = self._reasoner.reason(query, reasoning_type_enum, complexity_enum)
            
            operation = IntelligenceOperation(
                operation_id=f"reason_{now().sequence}",
                operation_type="reasoning",
                input_data=query,
                output_data={
                    "conclusion": result.conclusion,
                    "confidence": result.confidence,
                    "reasoning_type": result.reasoning_type.value,
                    "reasoning_chain": str(result.reasoning_chain) if result.reasoning_chain else None
                },
                confidence=result.confidence,
                status="completed"
            )
            
            with self._lock:
                self._operations.append(operation)
            
            return operation
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE] Reasoning failed: {e}")
            return self._create_error_operation("reasoning", str(e))
    
    # Decision Operations
    def make_decision(self, alternatives: list[dict[str, Any]], 
                     context: dict[str, Any],
                     decision_type: str = "operational") -> IntelligenceOperation:
        """Make a decision using production-grade decision-maker."""
        if not self._decision_maker:
            return self._create_disabled_operation("decision")
        
        try:
            decision_type_enum = DecisionType(decision_type)
            
            # Convert dict alternatives to DecisionAlternative objects
            decision_alternatives = [
                DecisionAlternative(
                    alternative_id=alt.get("alternative_id", f"alt_{i}"),
                    description=alt.get("description", ""),
                    criteria_scores={
                        DecisionCriteria(k): v 
                        for k, v in alt.get("criteria_scores", {}).items()
                        if k in [e.value for e in DecisionCriteria]
                    } if isinstance(alt.get("criteria_scores", {}), dict) else {},
                    estimated_outcomes=alt.get("estimated_outcomes", {}),
                    risk_factors=alt.get("risk_factors", []),
                    metadata=alt.get("metadata", {})
                )
                for i, alt in enumerate(alternatives)
            ]
            
            # Convert context to DecisionContext
            decision_context = DecisionContext(
                context_id=f"context_{now().sequence}",
                market_conditions=context.get("market_conditions", {}),
                system_state=context.get("system_state", {}),
                risk_environment=context.get("risk_environment", {}),
                temporal_constraints=context.get("temporal_constraints", {}),
                resource_constraints=context.get("resource_constraints", {})
            )
            
            result = self._decision_maker.make_decision(
                decision_alternatives, decision_context, decision_type_enum
            )
            
            operation = IntelligenceOperation(
                operation_id=f"decision_{now().sequence}",
                operation_type="decision",
                input_data={"alternatives": alternatives, "context": context},
                output_data={
                    "chosen_alternative": result.chosen_alternative.description,
                    "decision_score": result.decision_score,
                    "confidence": result.confidence,
                    "recommendation": result.recommendation
                },
                confidence=result.confidence,
                status="completed"
            )
            
            with self._lock:
                self._operations.append(operation)
            
            return operation
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE] Decision making failed: {e}")
            return self._create_error_operation("decision", str(e))
    
    # Planning Operations
    def create_plan(self, goals: list[dict[str, Any]], 
                   plan_type: str = "operational",
                   constraints: Optional[list[dict[str, Any]]] = None,
                   horizon: str = "short_term") -> IntelligenceOperation:
        """Create a plan using production-grade planner."""
        if not self._planner:
            return self._create_disabled_operation("planning")
        
        try:
            plan_type_enum = PlanType(plan_type)
            horizon_enum = PlanningHorizon(horizon)
            
            # Convert goals to PlanningGoal objects
            planning_goals = [
                PlanningGoal(
                    goal_id=goal.get("goal_id", f"goal_{i}"),
                    description=goal.get("description", ""),
                    priority=goal.get("priority", 1.0),
                    deadline=goal.get("deadline"),
                    success_criteria=goal.get("success_criteria", {}),
                    constraints=goal.get("constraints", []),
                    metadata=goal.get("metadata", {})
                )
                for i, goal in enumerate(goals)
            ]
            
            # Convert constraints to PlanningConstraint objects
            planning_constraints = [
                PlanningConstraint(
                    constraint_id=const.get("constraint_id", f"const_{i}"),
                    constraint_type=const.get("constraint_type", "general"),
                    description=const.get("description", ""),
                    severity=const.get("severity", 1.0),
                    metadata=const.get("metadata", {})
                )
                for i, const in enumerate(constraints or [])
            ]
            
            result = self._planner.create_plan(
                planning_goals, plan_type_enum, planning_constraints, horizon_enum
            )
            
            operation = IntelligenceOperation(
                operation_id=f"planning_{now().sequence}",
                operation_type="planning",
                input_data={"goals": goals, "constraints": constraints, "horizon": horizon},
                output_data={
                    "plan_id": result.generated_plan.plan_id if result.generated_plan else None,
                    "success_probability": result.planning_confidence,
                    "task_count": len(result.generated_plan.tasks) if result.generated_plan else 0,
                    "recommendations": result.recommendations
                },
                confidence=result.planning_confidence,
                status="completed" if result.generated_plan else "failed"
            )
            
            with self._lock:
                self._operations.append(operation)
            
            return operation
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE] Planning failed: {e}")
            return self._create_error_operation("planning", str(e))
    
    # Evaluation Operations
    def evaluate(self, data: dict[str, Any], 
                context: dict[str, Any],
                categories: Optional[list[str]] = None) -> IntelligenceOperation:
        """Perform evaluation using production-grade evaluator."""
        if not self._evaluator:
            return self._create_disabled_operation("evaluation")
        
        try:
            # Convert context to EvaluationContext
            evaluation_context = EvaluationContext(
                context_id=f"context_{now().sequence}",
                evaluation_purpose=context.get("purpose", "general"),
                time_window=context.get("time_window", {}),
                scope=context.get("scope", []),
                benchmark=context.get("benchmark"),
                constraints=context.get("constraints", []),
                metadata=context.get("metadata", {})
            )
            
            # Convert categories to enums
            evaluation_categories = []
            if categories:
                for cat in categories:
                    try:
                        evaluation_categories.append(EvaluationCategory(cat))
                    except ValueError:
                        pass
            
            result = self._evaluator.evaluate(data, evaluation_context, evaluation_categories)
            
            operation = IntelligenceOperation(
                operation_id=f"evaluation_{now().sequence}",
                operation_type="evaluation",
                input_data={"data": data, "context": context},
                output_data={
                    "overall_score": result.overall_score,
                    "category_scores": {k.value: v for k, v in result.category_scores.items()},
                    "metric_count": len(result.metrics),
                    "recommendations": result.recommendations
                },
                confidence=result.confidence,
                status="completed"
            )
            
            with self._lock:
                self._operations.append(operation)
            
            return operation
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE] Evaluation failed: {e}")
            return self._create_error_operation("evaluation", str(e))
    
    # Inference Operations
    def infer(self, data: dict[str, Any], 
             inference_type: str = "deterministic",
             model: Optional[dict[str, Any]] = None) -> IntelligenceOperation:
        """Perform inference using production-grade inference engine."""
        if not self._inference_engine:
            return self._create_disabled_operation("inference")
        
        try:
            inference_type_enum = InferenceType(inference_type)
            
            # Create input
            inference_input = InferenceInput(
                input_id=f"input_{now().sequence}",
                data=data,
                input_type=data.get("input_type", "generic"),
                metadata=data.get("metadata", {})
            )
            
            # Create model if specified
            inference_model = None
            if model:
                inference_model = InferenceModel(
                    model_id=model.get("model_id", f"model_{now().sequence}"),
                    model_name=model.get("model_name", "Default Model"),
                    model_type=inference_type_enum,
                    version=model.get("version", "1.0"),
                    parameters=model.get("parameters", {}),
                    performance_metrics=model.get("performance_metrics", {}),
                    metadata=model.get("metadata", {})
                )
            
            result = self._inference_engine.infer(inference_input, inference_model, inference_type_enum)
            
            operation = IntelligenceOperation(
                operation_id=f"inference_{now().sequence}",
                operation_type="inference",
                input_data={"data": data},
                output_data={
                    "result": result.output_data.result,
                    "confidence": result.confidence,
                    "inference_time_ms": result.timing_info.get("total_time_ms", 0),
                    "cache_hit": result.cache_hit
                },
                confidence=result.confidence,
                status="completed"
            )
            
            with self._lock:
                self._operations.append(operation)
            
            return operation
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE] Inference failed: {e}")
            return self._create_error_operation("inference", str(e))
    
    # Knowledge Operations
    def query_knowledge(self, query_type: str, 
                      parameters: dict[str, Any],
                      constraints: Optional[list[str]] = None) -> IntelligenceOperation:
        """Query knowledge graph using production-grade knowledge integrator."""
        if not self._knowledge_integrator:
            return self._create_disabled_operation("knowledge")
        
        try:
            # Create knowledge query
            knowledge_query = KnowledgeQuery(
                query_id=f"query_{now().sequence}",
                query_type=query_type,
                parameters=parameters,
                constraints=constraints or [],
                metadata={}
            )
            
            result = self._knowledge_integrator.query(knowledge_query)
            
            operation = IntelligenceOperation(
                operation_id=f"knowledge_{now().sequence}",
                operation_type="knowledge",
                input_data={"query_type": query_type, "parameters": parameters},
                output_data={
                    "result_type": result.result_type,
                    "entity_count": len(result.entities),
                    "relationship_count": len(result.relationships),
                    "path_count": len(result.paths),
                    "explanation": result.explanation
                },
                confidence=result.confidence,
                status="completed"
            )
            
            with self._lock:
                self._operations.append(operation)
            
            return operation
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE] Knowledge query failed: {e}")
            return self._create_error_operation("knowledge", str(e))
    
    def get_reasoning(self) -> Optional[ProductionReasoner]:
        """Get the reasoner component."""
        return self._reasoner
    
    def get_decision_maker(self) -> Optional[ProductionDecisionMaker]:
        """Get the decision-maker component."""
        return self._decision_maker
    
    def get_planner(self) -> Optional[ProductionPlanner]:
        """Get the planner component."""
        return self._planner
    
    def get_evaluator(self) -> Optional[ProductionEvaluator]:
        """Get the evaluator component."""
        return self._evaluator
    
    def get_inference_engine(self) -> Optional[ProductionInferenceEngine]:
        """Get the inference engine component."""
        return self._inference_engine
    
    def get_knowledge_integrator(self) -> Optional[ProductionKnowledgeIntegrator]:
        """Get the knowledge integrator component."""
        return self._knowledge_integrator
    
    def get_operations(self, limit: int = 100) -> list[IntelligenceOperation]:
        """Get operation history."""
        with self._lock:
            return self._operations[-limit:]
    
    def clear_operations(self) -> None:
        """Clear operation history."""
        with self._lock:
            self._operations.clear()
        logger.info("[INTELLIGENCE] Operation history cleared")
    
    def _create_disabled_operation(self, operation_type: str) -> IntelligenceOperation:
        """Create operation for disabled component."""
        return IntelligenceOperation(
            operation_id=f"{operation_type}_{now().sequence}",
            operation_type=operation_type,
            input_data={},
            output_data={"status": "disabled", "message": f"{operation_type} component not available"},
            confidence=0.0,
            status="failed"
        )
    
    def _create_error_operation(self, operation_type: str, error: str) -> IntelligenceOperation:
        """Create operation for failed operation."""
        return IntelligenceOperation(
            operation_id=f"{operation_type}_{now().sequence}",
            operation_type=operation_type,
            input_data={},
            output_data={"status": "error", "message": error},
            confidence=0.0,
            status="failed"
        )


# Import the DecisionCriteria enum for use in make_decision
from intelligence_engine.decision_maker import DecisionCriteria


def get_intelligence_orchestrator() -> IntelligenceOrchestrator:
    """Get the singleton intelligence orchestrator instance."""
    if not hasattr(get_intelligence_orchestrator, "_instance"):
        get_intelligence_orchestrator._instance = IntelligenceOrchestrator()
    return get_intelligence_orchestrator._instance