"""
coordination_layer.learning_gate
DIX VISION v42.2 — Learning Gate Manager

Controls learning operations and provides operator control over system learning.
Addresses critical gap identified in system preservation analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
import threading


class LearningGateState(StrEnum):
    """States of the learning gate."""
    OPEN = "open"  # Learning fully enabled
    RESTRICTED = "restricted"  # Learning with restrictions
    CLOSED = "closed"  # Learning disabled
    MAINTENANCE = "maintenance"  # Learning suspended for maintenance


class LearningOperationType(StrEnum):
    """Types of learning operations."""
    MODEL_TRAINING = "model_training"
    PARAMETER_UPDATE = "parameter_update"
    KNOWLEDGE_ACQUISITION = "knowledge_acquisition"
    HYPOTHESIS_TESTING = "hypothesis_testing"
    PATTERN_DISCOVERY = "pattern_discovery"
    META_LEARNING = "meta_learning"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    CUSTOM = "custom"


@dataclass
class LearningGatePolicy:
    """Policy governing learning gate behavior."""
    policy_id: str
    policy_name: str
    
    # Gate control
    default_state: LearningGateState = LearningGateState.RESTRICTED
    allowed_states: List[LearningGateState] = field(default_factory=lambda: [LearningGateState.OPEN, LearningGateState.RESTRICTED])
    
    # Operation-specific policies
    operation_permissions: Dict[LearningOperationType, bool] = field(default_factory=dict)
    
    # Time-based policies
    learning_windows: List[Dict[str, Any]] = field(default_factory=list)
    blackout_periods: List[Dict[str, Any]] = field(default_factory=list)
    
    # Resource-based policies
    max_cpu_usage: float = 0.8
    max_memory_usage: float = 0.8
    max_concurrent_operations: int = 5
    
    # Safety policies
    require_approval: bool = True
    required_approvers: List[str] = field(default_factory=list)
    approval_timeout_minutes: int = 60
    
    # Risk policies
    max_risk_level: str = "medium"  # low | medium | high
    require_risk_assessment: bool = True
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningOperation:
    """A learning operation request."""
    operation_id: str
    operation_type: LearningOperationType
    
    # Operation details
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_duration_seconds: float = 0.0
    
    # Request information
    requested_by: str = ""
    requested_at: datetime = field(default_factory=datetime.utcnow)
    priority: str = "medium"  # low | medium | high | critical
    
    # Approval status
    requires_approval: bool = True
    approved: bool = False
    approved_by: str = ""
    approved_at: Optional[datetime] = None
    approval_notes: str = ""
    
    # Execution status
    status: str = "pending"  # pending | approved | rejected | executing | completed | failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_result: Optional[Dict[str, Any]] = None
    
    # Risk assessment
    risk_level: str = "medium"
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningGateMetrics:
    """Metrics for learning gate operations."""
    metrics_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Operation counts
    total_operations_requested: int = 0
    total_operations_approved: int = 0
    total_operations_rejected: int = 0
    total_operations_completed: int = 0
    total_operations_failed: int = 0
    
    # Operation breakdown by type
    operations_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Resource usage
    current_cpu_usage: float = 0.0
    current_memory_usage: float = 0.0
    current_active_operations: int = 0
    
    # Performance metrics
    average_operation_duration_seconds: float = 0.0
    average_approval_time_minutes: float = 0.0
    
    # Gate state history
    state_changes: List[Dict[str, Any]] = field(default_factory=list)
    
    metadata: Dict[str, Any] = field(default_factory=dict)


class LearningGateManagerInterface(ABC):
    """Interface for learning gate management."""
    
    @abstractmethod
    def get_gate_state(self) -> LearningGateState:
        """Get current learning gate state."""
        pass
    
    @abstractmethod
    def set_gate_state(self, state: LearningGateState, reason: str = "") -> bool:
        """Set learning gate state."""
        pass
    
    @abstractmethod
    def request_learning_operation(
        self,
        operation_type: LearningOperationType,
        description: str,
        parameters: Dict[str, Any],
        requested_by: str
    ) -> LearningOperation:
        """Request a learning operation."""
        pass
    
    @abstractmethod
    def approve_operation(self, operation_id: str, approved_by: str, notes: str = "") -> bool:
        """Approve a learning operation."""
        pass
    
    @abstractmethod
    def reject_operation(self, operation_id: str, reason: str = "") -> bool:
        """Reject a learning operation."""
        pass
    
    @abstractmethod
    def execute_operation(self, operation_id: str) -> bool:
        """Execute an approved learning operation."""
        pass
    
    @abstractmethod
    def get_pending_operations(self) -> List[LearningOperation]:
        """Get pending learning operations."""
        pass
    
    @abstractmethod
    def get_gate_metrics(self) -> LearningGateMetrics:
        """Get learning gate metrics."""
        pass


class LearningGateManager(LearningGateManagerInterface):
    """Concrete implementation of learning gate management."""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Gate state
        self._current_state = LearningGateState.RESTRICTED
        self._state_since = datetime.utcnow()
        
        # Gate policy
        self._policy = LearningGatePolicy(policy_id="default_policy", policy_name="Default Policy")
        self._initialize_default_policy()
        
        # Operations
        self._operations: Dict[str, LearningOperation] = {}
        
        # Metrics
        self._metrics = LearningGateMetrics(metrics_id="learning_gate_metrics")
        
        # Execution hooks
        self._execution_hooks: Dict[LearningOperationType, Callable] = {}
        
        # Approval queue
        self._approval_queue: List[str] = []
    
    def _initialize_default_policy(self):
        """Initialize default learning gate policy."""
        # Set default operation permissions
        self._policy.operation_permissions = {
            LearningOperationType.MODEL_TRAINING: True,
            LearningOperationType.PARAMETER_UPDATE: True,
            LearningOperationType.KNOWLEDGE_ACQUISITION: True,
            LearningOperationType.HYPOTHESIS_TESTING: True,
            LearningOperationType.PATTERN_DISCOVERY: True,
            LearningOperationType.META_LEARNING: True,
            LearningOperationType.REINFORCEMENT_LEARNING: True,
            LearningOperationType.CUSTOM: True
        }
        
        # Set learning windows (e.g., only learn during specific hours)
        self._policy.learning_windows = [
            {
                "start_hour": 0,
                "end_hour": 6,
                "description": "Off-peak learning window"
            },
            {
                "start_hour": 12,
                "end_hour": 14,
                "description": "Midday learning window"
            }
        ]
        
        # Set blackout periods (e.g., during market open)
        self._policy.blackout_periods = [
            {
                "start_hour": 9,
                "end_hour": 10,
                "description": "Market open blackout"
            }
        ]
    
    def get_gate_state(self) -> LearningGateState:
        """Get current learning gate state."""
        with self._lock:
            return self._current_state
    
    def set_gate_state(self, state: LearningGateState, reason: str = "") -> bool:
        """Set learning gate state."""
        with self._lock:
            # Validate state is allowed
            if state not in self._policy.allowed_states:
                return False
            
            # Record state change
            old_state = self._current_state
            self._current_state = state
            self._state_since = datetime.utcnow()
            
            # Update metrics
            self._metrics.state_changes.append({
                "from_state": old_state.value,
                "to_state": state.value,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": reason
            })
            
            # Limit state change history
            if len(self._metrics.state_changes) > 100:
                self._metrics.state_changes = self._metrics.state_changes[-100:]
            
            return True
    
    def request_learning_operation(
        self,
        operation_type: LearningOperationType,
        description: str,
        parameters: Dict[str, Any],
        requested_by: str
    ) -> LearningOperation:
        """Request a learning operation."""
        with self._lock:
            operation_id = f"operation_{int(datetime.utcnow().timestamp())}"
            
            # Check if operation type is permitted
            operation_permitted = self._policy.operation_permissions.get(operation_type, True)
            
            # Check gate state
            if self._current_state == LearningGateState.CLOSED:
                operation_permitted = False
            elif self._current_state == LearningGateState.MAINTENANCE:
                operation_permitted = False
            
            # Check learning windows
            in_learning_window = self._check_learning_window()
            in_blackout_period = self._check_blackout_period()
            
            if in_blackout_period:
                operation_permitted = False
            
            # Determine approval requirement
            requires_approval = (
                self._policy.require_approval or
                not in_learning_window or
                not operation_permitted
            )
            
            # Perform risk assessment if required
            risk_level = "medium"
            risk_assessment = {}
            if self._policy.require_risk_assessment:
                risk_level, risk_assessment = self._assess_operation_risk(
                    operation_type, parameters
                )
            
            # Create operation
            operation = LearningOperation(
                operation_id=operation_id,
                operation_type=operation_type,
                description=description,
                parameters=parameters,
                requested_by=requested_by,
                requires_approval=requires_approval,
                approved=not requires_approval,  # Auto-approve if no approval required
                risk_level=risk_level,
                risk_assessment=risk_assessment
            )
            
            # Update metrics
            self._metrics.total_operations_requested += 1
            if operation_type.value not in self._metrics.operations_by_type:
                self._metrics.operations_by_type[operation_type.value] = 0
            self._metrics.operations_by_type[operation_type.value] += 1
            
            # Add to operations
            self._operations[operation_id] = operation
            
            # Add to approval queue if requires approval
            if requires_approval:
                self._approval_queue.append(operation_id)
                operation.status = "pending"
            elif operation_permitted:
                operation.status = "approved"
                self._metrics.total_operations_approved += 1
            else:
                operation.status = "rejected"
                operation.approval_notes = "Operation not permitted under current gate state"
                self._metrics.total_operations_rejected += 1
            
            return operation
    
    def _check_learning_window(self) -> bool:
        """Check if current time is in a learning window."""
        current_hour = datetime.utcnow().hour
        
        for window in self._policy.learning_windows:
            start_hour = window.get("start_hour", 0)
            end_hour = window.get("end_hour", 24)
            
            if start_hour <= current_hour < end_hour:
                return True
        
        return False
    
    def _check_blackout_period(self) -> bool:
        """Check if current time is in a blackout period."""
        current_hour = datetime.utcnow().hour
        
        for blackout in self._policy.blackout_periods:
            start_hour = blackout.get("start_hour", 0)
            end_hour = blackout.get("end_hour", 24)
            
            if start_hour <= current_hour < end_hour:
                return True
        
        return False
    
    def _assess_operation_risk(
        self,
        operation_type: LearningOperationType,
        parameters: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """Assess risk level for a learning operation."""
        risk_level = "medium"
        risk_assessment = {
            "factors": [],
            "score": 0.5
        }
        
        # Assess based on operation type
        if operation_type == LearningOperationType.MODEL_TRAINING:
            risk_level = "high"
            risk_assessment["factors"].append("Model training can be resource-intensive")
            risk_assessment["score"] = 0.7
        elif operation_type == LearningOperationType.REINFORCEMENT_LEARNING:
            risk_level = "high"
            risk_assessment["factors"].append("Reinforcement learning can affect system behavior")
            risk_assessment["score"] = 0.8
        elif operation_type == LearningOperationType.PARAMETER_UPDATE:
            risk_level = "medium"
            risk_assessment["factors"].append("Parameter updates can affect performance")
            risk_assessment["score"] = 0.5
        
        # Assess based on parameters
        estimated_duration = parameters.get("estimated_duration_seconds", 0)
        if estimated_duration > 3600:  # > 1 hour
            risk_level = "high"
            risk_assessment["factors"].append("Long-running operation")
            risk_assessment["score"] = min(1.0, risk_assessment["score"] + 0.2)
        
        # Check against policy max risk level
        policy_max_risk = self._policy.max_risk_level
        risk_levels = ["low", "medium", "high"]
        if risk_levels.index(risk_level) > risk_levels.index(policy_max_risk):
            risk_level = policy_max_risk
        
        return risk_level, risk_assessment
    
    def approve_operation(self, operation_id: str, approved_by: str, notes: str = "") -> bool:
        """Approve a learning operation."""
        with self._lock:
            operation = self._operations.get(operation_id)
            if not operation:
                return False
            
            if operation.status != "pending":
                return False
            
            operation.approved = True
            operation.approved_by = approved_by
            operation.approved_at = datetime.utcnow()
            operation.approval_notes = notes
            operation.status = "approved"
            
            # Update metrics
            self._metrics.total_operations_approved += 1
            
            # Remove from approval queue
            if operation_id in self._approval_queue:
                self._approval_queue.remove(operation_id)
            
            return True
    
    def reject_operation(self, operation_id: str, reason: str = "") -> bool:
        """Reject a learning operation."""
        with self._lock:
            operation = self._operations.get(operation_id)
            if not operation:
                return False
            
            if operation.status != "pending":
                return False
            
            operation.approved = False
            operation.approval_notes = reason
            operation.status = "rejected"
            
            # Update metrics
            self._metrics.total_operations_rejected += 1
            
            # Remove from approval queue
            if operation_id in self._approval_queue:
                self._approval_queue.remove(operation_id)
            
            return True
    
    def execute_operation(self, operation_id: str) -> bool:
        """Execute an approved learning operation."""
        with self._lock:
            operation = self._operations.get(operation_id)
            if not operation:
                return False
            
            if operation.status != "approved":
                return False
            
            # Check resource constraints
            if self._metrics.current_active_operations >= self._policy.max_concurrent_operations:
                operation.status = "rejected"
                operation.approval_notes = "Maximum concurrent operations reached"
                self._metrics.total_operations_rejected += 1
                return False
            
            # Update operation status
            operation.status = "executing"
            operation.started_at = datetime.utcnow()
            self._metrics.current_active_operations += 1
            
            # Execute via hook or default handler
            execution_hook = self._execution_hooks.get(operation.operation_type)
            if execution_hook:
                try:
                    result = execution_hook(operation)
                    operation.execution_result = {"success": True, "result": result}
                    operation.status = "completed"
                    self._metrics.total_operations_completed += 1
                except Exception as e:
                    operation.execution_result = {"success": False, "error": str(e)}
                    operation.status = "failed"
                    self._metrics.total_operations_failed += 1
            else:
                # Default handler - mark as completed
                operation.execution_result = {"success": True, "message": "No handler, auto-completed"}
                operation.status = "completed"
                self._metrics.total_operations_completed += 1
            
            # Update completion time
            operation.completed_at = datetime.utcnow()
            
            # Update metrics
            self._metrics.current_active_operations -= 1
            
            # Calculate average duration
            if operation.started_at and operation.completed_at:
                duration = (operation.completed_at - operation.started_at).total_seconds()
                total_duration = self._metrics.average_operation_duration_seconds * (self._metrics.total_operations_completed - 1)
                self._metrics.average_operation_duration_seconds = (total_duration + duration) / self._metrics.total_operations_completed
            
            return operation.status == "completed"
    
    def get_pending_operations(self) -> List[LearningOperation]:
        """Get pending learning operations."""
        with self._lock:
            return [
                self._operations[op_id]
                for op_id in self._approval_queue
                if op_id in self._operations
            ]
    
    def get_gate_metrics(self) -> LearningGateMetrics:
        """Get learning gate metrics."""
        with self._lock:
            return self._metrics
    
    def register_execution_hook(self, operation_type: LearningOperationType, hook: Callable) -> None:
        """Register a hook for executing specific operation types."""
        self._execution_hooks[operation_type] = hook
    
    def set_policy(self, policy: LearningGatePolicy) -> bool:
        """Set learning gate policy."""
        with self._lock:
            self._policy = policy
            return True
    
    def get_gate_report(self) -> Dict[str, Any]:
        """Get comprehensive gate report."""
        with self._lock:
            pending_operations = self.get_pending_operations()
            
            return {
                "gate_state": {
                    "current_state": self._current_state.value,
                    "state_since": self._state_since.isoformat()
                },
                "operations_summary": {
                    "total_requested": self._metrics.total_operations_requested,
                    "total_approved": self._metrics.total_operations_approved,
                    "total_rejected": self._metrics.total_operations_rejected,
                    "total_completed": self._metrics.total_operations_completed,
                    "total_failed": self._metrics.total_operations_failed,
                    "approval_rate": (
                        self._metrics.total_operations_approved / self._metrics.total_operations_requested * 100
                        if self._metrics.total_operations_requested > 0 else 0
                    )
                },
                "operations_by_type": self._metrics.operations_by_type,
                "pending_operations": [
                    {
                        "operation_id": op.operation_id,
                        "operation_type": op.operation_type.value,
                        "description": op.description,
                        "requested_by": op.requested_by,
                        "risk_level": op.risk_level,
                        "requested_at": op.requested_at.isoformat()
                    }
                    for op in pending_operations
                ],
                "resource_usage": {
                    "current_active_operations": self._metrics.current_active_operations,
                    "max_concurrent_operations": self._policy.max_concurrent_operations,
                    "utilization": (
                        self._metrics.current_active_operations / self._policy.max_concurrent_operations * 100
                        if self._policy.max_concurrent_operations > 0 else 0
                    )
                },
                "performance_metrics": {
                    "average_operation_duration_seconds": self._metrics.average_operation_duration_seconds,
                    "average_approval_time_minutes": self._metrics.average_approval_time_minutes
                },
                "policy_info": {
                    "policy_id": self._policy.policy_id,
                    "policy_name": self._policy.policy_name,
                    "default_state": self._policy.default_state.value,
                    "requires_approval": self._policy.require_approval,
                    "max_risk_level": self._policy.max_risk_level
                }
            }


# Global instance
_learning_gate_manager: Optional[LearningGateManager] = None
_learning_gate_lock = threading.Lock()


def get_learning_gate_manager() -> LearningGateManager:
    """Get global learning gate manager instance."""
    global _learning_gate_manager
    if _learning_gate_manager is None:
        with _learning_gate_lock:
            if _learning_gate_manager is None:
                _learning_gate_manager = LearningGateManager()
    return _learning_gate_manager


__all__ = [
    "LearningGateState",
    "LearningOperationType",
    "LearningGatePolicy",
    "LearningOperation",
    "LearningGateMetrics",
    "LearningGateManagerInterface",
    "LearningGateManager",
    "get_learning_gate_manager",
]