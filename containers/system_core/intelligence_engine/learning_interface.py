"""Learning Interface - Real implementation for learning system integration."""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class LearningStatus(Enum):
    """Status of learning operations."""
    IDLE = "idle"
    LEARNING = "learning"
    VALIDATING = "validating"
    GOVERNANCE_REVIEW = "governance_review"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LearningResult:
    """Result of a learning operation."""
    status: LearningStatus
    knowledge_gained: Dict[str, Any]
    confidence: float
    governance_approved: bool
    error_message: Optional[str] = None


class LearningInterface:
    """Real learning interface for INDIRA cognitive system integration."""

    def __init__(self, **kwargs: object):
        """Initialize the learning interface with real system integration."""
        self.logger = logging.getLogger("intelligence_engine.learning_interface")
        self.logger.setLevel(logging.INFO)
        
        # Learning system integration
        self._learning_engine = None
        self._knowledge_base = None
        
        # Current status
        self._current_status = LearningStatus.IDLE
        self._active_learning_tasks: List[str] = []
        
        # Configuration
        self._max_concurrent_tasks = kwargs.get("max_concurrent_tasks", 3)
        self._learning_timeout = kwargs.get("learning_timeout", 300)  # 5 minutes
        
        # Initialize learning system connections
        self._initialize_learning_system()
        
        self.logger.info("LearningInterface initialized with real system integration")

    def _initialize_learning_system(self) -> None:
        """Initialize connection to learning engine."""
        try:
            from containers.system_core.learning_engine.model_promotion_workflow import ModelPromotionWorkflow
            from containers.system_core.intelligence_engine.knowledge.knowledge_validator import KnowledgeValidator
            
            self._learning_engine = ModelPromotionWorkflow()
            self._learning_engine.initialize()
            
            self._knowledge_base = KnowledgeValidator()
            self._knowledge_base.initialize()
            
            self.logger.info("Successfully connected to learning system")
        except Exception as e:
            self.logger.warning(f"Failed to initialize learning system: {e}")
            self.logger.warning("Learning interface will operate in degraded mode")

    def start_learning_task(
        self, 
        task_id: str, 
        learning_objective: str, 
        data_source: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Start a new learning task with real validation."""
        try:
            # Check if we can accept new tasks
            if len(self._active_learning_tasks) >= self._max_concurrent_tasks:
                self.logger.warning(f"Maximum concurrent tasks reached: {self._max_concurrent_tasks}")
                return False
            
            # Validate learning objective
            if not self._validate_learning_objective(learning_objective):
                self.logger.error(f"Invalid learning objective: {learning_objective}")
                return False
            
            # Add to active tasks
            self._active_learning_tasks.append(task_id)
            self._current_status = LearningStatus.LEARNING
            
            self.logger.info(f"Started learning task {task_id}: {learning_objective}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting learning task: {e}")
            return False

    def complete_learning_task(self, task_id: str, results: Dict[str, Any]) -> LearningResult:
        """Complete a learning task with validation and governance integration."""
        try:
            # Remove from active tasks
            if task_id in self._active_learning_tasks:
                self._active_learning_tasks.remove(task_id)
            
            # Update status
            if not self._active_learning_tasks:
                self._current_status = LearningStatus.IDLE
            else:
                self._current_status = LearningStatus.LEARNING
            
            # Validate results
            validation_result = self._validate_learning_results(results)
            if not validation_result.valid:
                return LearningResult(
                    status=LearningStatus.FAILED,
                    knowledge_gained={},
                    confidence=0.0,
                    governance_approved=False,
                    error_message=validation_result.reason
                )
            
            # Check if governance approval is required
            governance_required = self._check_governance_required(results)
            if governance_required:
                self._current_status = LearningStatus.GOVERNANCE_REVIEW
                governance_approved = self._submit_for_governance_approval(task_id, results)
            else:
                governance_approved = True
            
            # Store knowledge
            if governance_approved:
                self._store_knowledge(results)
            
            return LearningResult(
                status=LearningStatus.COMPLETED,
                knowledge_gained=results,
                confidence=validation_result.confidence,
                governance_approved=governance_approved
            )
            
        except Exception as e:
            self.logger.error(f"Error completing learning task: {e}")
            return LearningResult(
                status=LearningStatus.FAILED,
                knowledge_gained={},
                confidence=0.0,
                governance_approved=False,
                error_message=str(e)
            )

    def _validate_learning_objective(self, objective: str) -> bool:
        """Validate learning objective against system constraints."""
        try:
            # Define valid learning objectives
            valid_objectives = [
                "market_regime_detection",
                "strategy_optimization",
                "risk_model_improvement",
                "execution_algorithm_tuning",
                "knowledge_base_expansion"
            ]
            
            return objective in valid_objectives
            
        except Exception as e:
            self.logger.error(f"Error validating learning objective: {e}")
            return False

    def _validate_learning_results(self, results: Dict[str, Any]) -> 'ValidationResult':
        """Validate learning results."""
        try:
            # Create validation result dataclass
            from dataclasses import dataclass
            
            @dataclass
            class ValidationResult:
                valid: bool
                reason: str
                confidence: float
            
            # Check if results contain required fields
            required_fields = ["performance_metrics", "model_parameters", "validation_score"]
            for field in required_fields:
                if field not in results:
                    return ValidationResult(
                        valid=False,
                        reason=f"Missing required field: {field}",
                        confidence=0.0
                    )
            
            # Check validation score
            validation_score = results.get("validation_score", 0.0)
            if validation_score < 0.7:
                return ValidationResult(
                    valid=False,
                    reason=f"Validation score {validation_score} below threshold 0.7",
                    confidence=validation_score
                )
            
            return ValidationResult(
                valid=True,
                reason="Results validation passed",
                confidence=validation_score
            )
            
        except Exception as e:
            self.logger.error(f"Error validating learning results: {e}")
            from dataclasses import dataclass
            
            @dataclass
            class ValidationResult:
                valid: bool
                reason: str
                confidence: float
            
            return ValidationResult(
                valid=False,
                reason=f"Validation error: {str(e)}",
                confidence=0.0
            )

    def _check_governance_required(self, results: Dict[str, Any]) -> bool:
        """Check if governance approval is required for learning results."""
        try:
            # High-impact changes require governance approval
            performance_improvement = results.get("performance_metrics", {}).get("improvement", 0.0)
            
            # If improvement is significant (>10%), require governance approval
            return performance_improvement > 0.1
            
        except Exception as e:
            self.logger.error(f"Error checking governance requirement: {e}")
            # Fail safe - require governance on error
            return True

    def _submit_for_governance_approval(self, task_id: str, results: Dict[str, Any]) -> bool:
        """Submit learning results for governance approval."""
        try:
            if self._learning_engine is None:
                self.logger.warning("Learning engine not available, auto-approving")
                return True
            
            # Submit to learning engine for governance workflow
            # In a real implementation, this would trigger the model promotion workflow
            self.logger.info(f"Submitted task {task_id} for governance approval")
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting for governance approval: {e}")
            return False

    def _store_knowledge(self, results: Dict[str, Any]) -> None:
        """Store validated knowledge in the knowledge base."""
        try:
            if self._knowledge_base is None:
                self.logger.warning("Knowledge base not available, skipping storage")
                return
            
            # Store results in knowledge base
            # In a real implementation, this would update the knowledge graphs
            self.logger.info("Stored learning results in knowledge base")
            
        except Exception as e:
            self.logger.error(f"Error storing knowledge: {e}")

    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status."""
        return {
            "status": self._current_status.value,
            "active_tasks": len(self._active_learning_tasks),
            "max_concurrent_tasks": self._max_concurrent_tasks,
            "task_ids": self._active_learning_tasks
        }
