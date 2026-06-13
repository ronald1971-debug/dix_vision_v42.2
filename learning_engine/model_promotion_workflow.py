"""Model Promotion Workflow — LEARN-08.02.

Model promotion workflow for the learning engine to manage the
lifecycle of models from training to production deployment.
Provides approval stages, rollback capabilities, and promotion
tracking.
"""

from __future__ import annotations

import dataclasses
import enum
import time
from collections import deque
from collections.abc import Callable
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_ENABLE_ROLLBACK: Final[bool] = True
DEFAULT_ROLLBACK_WINDOW_DAYS: Final[int] = 7
DEFAULT_APPROVAL_TIMEOUT_SEC: Final[int] = 86400  # 24 hours
DEFAULT_ENABLE_AUTOMATIC_PROMOTION: Final[bool] = False
DEFAULT_MIN_APPROVALS: Final[int] = 1

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PromotionStage(enum.Enum):
    """Stages in the model promotion pipeline."""
    TRAINING = "TRAINING"
    VALIDATION = "VALIDATION"
    STAGING = "STAGING"
    APPROVAL = "APPROVAL"
    PRODUCTION = "PRODUCTION"
    ROLLBACK = "ROLLBACK"
    RETIREMENT = "RETIREMENT"


class PromotionStatus(enum.Enum):
    """Status of a promotion request."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ApprovalDecision(enum.Enum):
    """Approval decision types."""
    APPROVE = "APPROVE"
    DENY = "DENY"
    REQUEST_CHANGES = "REQUEST_CHANGES"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class PromotionWorkflowConfig:
    """Configuration for model promotion workflow."""
    enable_rollback: bool = DEFAULT_ENABLE_ROLLBACK
    rollback_window_days: int = DEFAULT_ROLLBACK_WINDOW_DAYS
    approval_timeout_sec: int = DEFAULT_APPROVAL_TIMEOUT_SEC
    enable_automatic_promotion: bool = DEFAULT_ENABLE_AUTOMATIC_PROMOTION
    min_approvals: int = DEFAULT_MIN_APPROVALS
    require_testing: bool = True
    require_signoff: bool = True
    enable_canary_deployment: bool = False

    def __post_init__(self) -> None:
        if self.rollback_window_days < 1:
            raise ValueError("rollback_window_days must be >= 1")
        if self.approval_timeout_sec < 1:
            raise ValueError("approval_timeout_sec must be >= 1")
        if self.min_approvals < 1:
            raise ValueError("min_approvals must be >= 1")


@dataclasses.dataclass(frozen=True, slots=True)
class PromotionRequest:
    """A request to promote a model."""
    request_id: str
    model_id: str
    target_stage: PromotionStage
    current_stage: PromotionStage
    requester: str
    timestamp_ns: int
    evaluation_result: dict[str, Any] | None = None
    requested_by: str = ""
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("request_id must be non-empty")
        if not self.model_id:
            raise ValueError("model_id must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class ApprovalRecord:
    """An approval record for a promotion."""
    approval_id: str
    request_id: str
    approver: str
    decision: ApprovalDecision
    timestamp_ns: int
    comments: str = ""
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.approval_id:
            raise ValueError("approval_id must be non-empty")
        if not self.request_id:
            raise ValueError("request_id must be non-empty")
        if not self.approver:
            raise ValueError("approver must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class PromotionExecution:
    """Result of a promotion execution."""
    execution_id: str
    request_id: str
    model_id: str
    from_stage: PromotionStage
    to_stage: PromotionStage
    status: PromotionStatus
    started_at_ns: int
    completed_at_ns: int = 0
    rollback_available: bool = False
    error_message: str = ""
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.execution_id:
            raise ValueError("execution_id must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class RollbackRecord:
    """Record of a rollback operation."""
    rollback_id: str
    execution_id: str
    model_id: str
    from_stage: PromotionStage
    to_stage: PromotionStage
    reason: str
    timestamp_ns: int
    success: bool
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.rollback_id:
            raise ValueError("rollback_id must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class WorkflowMetrics:
    """Metrics about promotion workflow."""
    total_requests: int
    requests_by_stage: dict[str, int]
    requests_by_status: dict[str, int]
    total_approvals: int
    total_denials: int
    total_executions: int
    successful_promotions: int
    failed_promotions: int
    total_rollbacks: int
    average_promotion_time_sec: float
    pending_approvals: int


# ---------------------------------------------------------------------------
# Model Promotion Workflow
# ---------------------------------------------------------------------------


class ModelPromotionWorkflow:
    """Model promotion workflow system.
    
    Manages the lifecycle of models from training to production
    deployment with:
    
    - Stage-based promotion pipeline (training -> validation -> staging -> approval -> production)
    - Approval workflow with multiple approvers
    - Rollback capabilities with configurable windows
    - Execution tracking and metrics
    - Automatic promotion options for qualified models
    - Canary deployment support
    """
    
    def __init__(
        self,
        config: PromotionWorkflowConfig | None = None,
    ) -> None:
        """Initialize the promotion workflow.
        
        Args:
            config: Workflow configuration
        """
        self._config = config or PromotionWorkflowConfig()
        self._lock = Lock()
        
        # Promotion storage
        self._promotion_requests: dict[str, PromotionRequest] = {}
        self._approval_records: dict[str, list[ApprovalRecord]] = {}  # request_id -> approvals
        self._executions: dict[str, PromotionExecution] = {}
        self._rollbacks: list[RollbackRecord] = []
        
        # Stage tracking
        self._model_stages: dict[str, PromotionStage] = {}  # model_id -> current stage
        
        # Event handlers
        self._approval_handlers: list[Callable[[ApprovalRecord], None]] = []
        self._execution_handlers: list[Callable[[PromotionExecution], None]] = []
        self._rollback_handlers: list[Callable[[RollbackRecord], None]] = []
        
        # Metrics
        self._metrics = self._init_metrics()
        self._promotion_times: deque[int] = deque(maxlen=100)
    
    def submit_promotion_request(
        self,
        model_id: str,
        target_stage: PromotionStage,
        requester: str,
        evaluation_result: dict[str, Any] | None = None,
    ) -> PromotionRequest:
        """Submit a promotion request for a model.
        
        Args:
            model_id: Model identifier
            target_stage: Target promotion stage
            requester: Person requesting promotion
            evaluation_result: Evaluation results
            
        Returns:
            Promotion request
        """
        import secrets
        import time
        
        current_stage = self._model_stages.get(model_id, PromotionStage.TRAINING)
        
        request = PromotionRequest(
            request_id=secrets.token_hex(16),
            model_id=model_id,
            target_stage=target_stage,
            current_stage=current_stage,
            requester=requester,
            timestamp_ns=time.time_ns(),
            evaluation_result=evaluation_result,
        )
        
        with self._lock:
            self._promotion_requests[request.request_id] = request
            self._approval_records[request.request_id] = []
            
            # Update metrics
            self._metrics.total_requests += 1
            self._metrics.requests_by_stage[target_stage.value] = \
                self._metrics.requests_by_stage.get(target_stage.value, 0) + 1
            self._metrics.requests_by_status[PromotionStatus.PENDING.value] += 1
        
        # Auto-approve if automatic promotion enabled
        if self._config.enable_automatic_promotion:
            self._auto_approve_request(request)
        
        return request
    
    def approve_request(
        self,
        request_id: str,
        approver: str,
        decision: ApprovalDecision,
        comments: str = "",
    ) -> bool:
        """Approve or deny a promotion request.
        
        Args:
            request_id: Request identifier
            approver: Approver identifier
            decision: Approval decision
            comments: Approval comments
            
        Returns:
            True if approval processed successfully
        """
        import secrets
        import time
        
        with self._lock:
            request = self._promotion_requests.get(request_id)
            if not request:
                return False
            
            approval = ApprovalRecord(
                approval_id=secrets.token_hex(16),
                request_id=request_id,
                approver=approver,
                decision=decision,
                timestamp_ns=time.time_ns(),
                comments=comments,
            )
            
            self._approval_records[request_id].append(approval)
            
            # Update metrics
            if decision == ApprovalDecision.APPROVE:
                self._metrics.total_approvals += 1
            else:
                self._metrics.total_denials += 1
            
            # Notify handlers
            for handler in self._approval_handlers:
                try:
                    handler(approval)
                except Exception:
                    pass
        
        # Check if we have enough approvals to proceed
        if decision == ApprovalDecision.APPROVE:
            approvals = [a for a in self._approval_records[request_id] if a.decision == ApprovalDecision.APPROVE]
            if len(approvals) >= self._config.min_approvals:
                self.execute_promotion(request_id)
        
        return True
    
    def execute_promotion(
        self,
        request_id: str,
    ) -> PromotionExecution | None:
        """Execute a promotion request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Promotion execution or None
        """
        import secrets
        import time
        
        with self._lock:
            request = self._promotion_requests.get(request_id)
            if not request:
                return None
            
            execution = PromotionExecution(
                execution_id=secrets.token_hex(16),
                request_id=request_id,
                model_id=request.model_id,
                from_stage=request.current_stage,
                to_stage=request.target_stage,
                status=PromotionStatus.IN_PROGRESS,
                started_at_ns=time.time_ns(),
                rollback_available=self._config.enable_rollback,
            )
            
            self._executions[execution.execution_id] = execution
            self._metrics.total_executions += 1
        
        # Simulate promotion execution (would integrate with deployment system)
        success = self._perform_promotion(execution)
        
        with self._lock:
            execution = PromotionExecution(
                execution_id=execution.execution_id,
                request_id=request_id,
                model_id=request.model_id,
                from_stage=request.from_stage,
                to_stage=request.to_stage,
                status=PromotionStatus.COMPLETED if success else PromotionStatus.FAILED,
                started_at_ns=execution.started_at_ns,
                completed_at_ns=time.time_ns(),
                rollback_available=self._config.enable_rollback and success,
                error_message="" if success else "Deployment failed",
            )
            
            self._executions[execution.execution_id] = execution
            
            # Update model stage if successful
            if success:
                self._model_stages[execution.model_id] = execution.to_stage
                self._metrics.successful_promotions += 1
            else:
                self._metrics.failed_promotions += 1
            
            # Track promotion time
            promotion_time_sec = (execution.completed_at_ns - execution.started_at_ns) / 1_000_000_000
            self._promotion_times.append(promotion_time_sec)
            if len(self._promotion_times) > 0:
                self._metrics.average_promotion_time_sec = sum(self._promotion_times) / len(self._promotion_times)
        
        # Notify handlers
        for handler in self._execution_handlers:
            try:
                handler(execution)
            except Exception:
                pass
        
        return execution
    
    def rollback_model(
        self,
        model_id: str,
        reason: str,
        rollback_to_stage: PromotionStage | None = None,
    ) -> RollbackRecord | None:
        """Rollback a model to a previous stage.
        
        Args:
            model_id: Model identifier
            reason: Reason for rollback
            rollback_to_stage: Target stage (defaults to previous stage)
            
        Returns:
            Rollback record or None
        """
        import secrets
        import time
        
        if not self._config.enable_rollback:
            return None
        
        with self._lock:
            current_stage = self._model_stages.get(model_id)
            if not current_stage:
                return None
            
            if rollback_to_stage is None:
                # Roll back to previous stage
                stages = list(PromotionStage)
                current_index = stages.index(current_stage)
                if current_index > 0:
                    rollback_to_stage = stages[current_index - 1]
                else:
                    return None
            
            rollback = RollbackRecord(
                rollback_id=secrets.token_hex(16),
                execution_id="",  # Would link to original promotion
                model_id=model_id,
                from_stage=current_stage,
                to_stage=rollback_to_stage,
                reason=reason,
                timestamp_ns=time.time_ns(),
                success=True,  # Simplified
            )
            
            # Update model stage
            self._model_stages[model_id] = rollback_to_stage
            self._rollbacks.append(rollback)
            self._metrics.total_rollbacks += 1
        
        # Notify handlers
        for handler in self._rollback_handlers:
            try:
                handler(rollback)
            except Exception:
                pass
        
        return rollback
    
    def get_model_stage(self, model_id: str) -> PromotionStage | None:
        """Get current stage of a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Current stage or None
        """
        with self._lock:
            return self._model_stages.get(model_id)
    
    def get_request_status(
        self,
        request_id: str,
    ) -> PromotionRequest | None:
        """Get status of a promotion request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Promotion request or None
        """
        with self._lock:
            return self._promotion_requests.get(request_id)
    
    def get_approvals(
        self,
        request_id: str,
    ) -> list[ApprovalRecord] | None:
        """Get approvals for a request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            List of approvals or None
        """
        with self._lock:
            return list(self._approval_records.get(request_id, []))
    
    def get_metrics(self) -> WorkflowMetrics:
        """Get workflow metrics.
        
        Returns:
            Current metrics
        """
        with self._lock:
            # Count pending approvals
            pending_approvals = sum(
                1 for req in self._promotion_requests.values()
                if len(self._approval_records[req.request_id]) < self._config.min_approvals
            )
            self._metrics.pending_approvals = pending_approvals
            
            return self._metrics
    
    def register_approval_handler(
        self,
        handler: Callable[[ApprovalRecord], None],
    ) -> None:
        """Register an approval event handler.
        
        Args:
            handler: Handler callable
        """
        with self._lock:
            self._approval_handlers.append(handler)
    
    def register_execution_handler(
        self,
        handler: Callable[[PromotionExecution], None],
    ) -> None:
        """Register an execution event handler.
        
        Args:
            handler: Handler callable
        """
        with self._lock:
            self._execution_handlers.append(handler)
    
    def register_rollback_handler(
        self,
        handler: Callable[[RollbackRecord], None],
    ) -> None:
        """Register a rollback event handler.
        
        Args:
            handler: Handler callable
        """
        with self._lock:
            self._rollback_handlers.append(handler)
    
    def _auto_approve_request(self, request: PromotionRequest) -> None:
        """Auto-approve a request if criteria met.
        
        Args:
            request: Promotion request
        """
        # Auto-approve if evaluation result shows excellent performance
        if request.evaluation_result:
            overall_score = request.evaluation_result.get("overall_score", 0.0)
            if overall_score >= 0.8:
                self.approve_request(
                    request.request_id,
                    "system",
                    ApprovalDecision.APPROVE,
                    "Auto-approved due to excellent performance score",
                )
    
    def _perform_promotion(self, execution: PromotionExecution) -> bool:
        """Perform the actual promotion (placeholder).
        
        Args:
            execution: Promotion execution
            
        Returns:
            True if successful
        """
        # Placeholder - would integrate with actual deployment system
        return True
    
    def _init_metrics(self) -> WorkflowMetrics:
        """Initialize workflow metrics."""
        return WorkflowMetrics(
            total_requests=0,
            requests_by_stage={},
            requests_by_status={},
            total_approvals=0,
            total_denials=0,
            total_executions=0,
            successful_promotions=0,
            failed_promotions=0,
            total_rollbacks=0,
            average_promotion_time_sec=0.0,
            pending_approvals=0,
        )


# ---------------------------------------------------------------------------
# Model Promotion Workflow Manager
# ---------------------------------------------------------------------------


class ModelPromotionWorkflowManager:
    """Manager for model promotion workflow."""
    
    def __init__(self, config: PromotionWorkflowConfig | None = None) -> None:
        """Initialize the promotion workflow manager.
        
        Args:
            config: Workflow configuration
        """
        self._config = config or PromotionWorkflowConfig()
        self._workflow = ModelPromotionWorkflow(config)
    
    def submit_promotion_request(
        self,
        model_id: str,
        target_stage: PromotionStage,
        requester: str,
        evaluation_result: dict[str, Any] | None = None,
    ) -> PromotionRequest:
        """Submit a promotion request.
        
        Args:
            model_id: Model ID
            target_stage: Target stage
            requester: Requester
            evaluation_result: Evaluation result
            
        Returns:
            Promotion request
        """
        return self._workflow.submit_promotion_request(model_id, target_stage, requester, evaluation_result)
    
    def approve_request(
        self,
        request_id: str,
        approver: str,
        decision: ApprovalDecision,
        comments: str = "",
    ) -> bool:
        """Approve a request.
        
        Args:
            request_id: Request ID
            approver: Approver
            decision: Decision
            comments: Comments
            
        Returns:
            True if successful
        """
        return self._workflow.approve_request(request_id, approver, decision, comments)
    
    def execute_promotion(self, request_id: str) -> PromotionExecution | None:
        """Execute promotion.
        
        Args:
            request_id: Request ID
            
        Returns:
            Execution result
        """
        return self._workflow.execute_promotion(request_id)
    
    def rollback_model(
        self,
        model_id: str,
        reason: str,
        rollback_to_stage: PromotionStage | None = None,
    ) -> RollbackRecord | None:
        """Rollback a model.
        
        Args:
            model_id: Model ID
            reason: Reason
            rollback_to_stage: Target stage
            
        Returns:
            Rollback record
        """
        return self._workflow.rollback_model(model_id, reason, rollback_to_stage)
    
    def get_model_stage(self, model_id: str) -> PromotionStage | None:
        """Get model stage.
        
        Args:
            model_id: Model ID
            
        Returns:
            Current stage
        """
        return self._workflow.get_model_stage(model_id)
    
    def get_metrics(self) -> WorkflowMetrics:
        """Get metrics.
        
        Returns:
            Current metrics
        """
        return self._workflow.get_metrics()


__all__ = [
    "PromotionStage",
    "PromotionStatus",
    "ApprovalDecision",
    "PromotionWorkflowConfig",
    "PromotionRequest",
    "ApprovalRecord",
    "PromotionExecution",
    "RollbackRecord",
    "WorkflowMetrics",
    "ModelPromotionWorkflow",
    "ModelPromotionWorkflowManager",
]
