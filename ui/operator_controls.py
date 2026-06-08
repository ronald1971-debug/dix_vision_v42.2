"""Operator Controls — DASH-06.03.

Comprehensive operator controls for dashboard including manual
intervention, mode switching, emergency controls, approval workflows,
and system governance. Provides operators with granular control
over system behavior and safety mechanisms.
"""

from __future__ import annotations

import dataclasses
import enum
from collections.abc import Callable
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_ENABLE_APPROVAL_REQUIRED: Final[bool] = True
DEFAULT_ENABLE_EMERGENCY_OVERRIDE: Final[bool] = False
DEFAULT_APPROVAL_TIMEOUT_SEC: Final[int] = 300
DEFAULT_MAX_PENDING_APPROVALS: Final[int] = 50
DEFAULT_REQUIRE_MULTI_SIGN: Final[bool] = False
DEFAULT_MIN_SIGNERS: Final[int] = 2

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ControlAction(enum.Enum):
    """Types of operator control actions."""
    EMERGENCY_STOP = "EMERGENCY_STOP"
    EMERGENCY_FREEZE = "EMERGENCY_FREEZE"
    MODE_CHANGE = "MODE_CHANGE"
    STRATEGY_ENABLE = "STRATEGY_ENABLE"
    STRATEGY_DISABLE = "STRATEGY_DISABLE"
    ORDER_CANCEL_ALL = "ORDER_CANCEL_ALL"
    POSITION_CLOSE_ALL = "POSITION_CLOSE_ALL"
    RISK_LIMIT_OVERRIDE = "RISK_LIMIT_OVERRIDE"
    APPROVAL_REQUEST = "APPROVAL_REQUEST"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    APPROVAL_DENIED = "APPROVAL_DENIED"
    MANUAL_INTERVENTION = "MANUAL_INTERVENTION"
    SYSTEM_RESTART = "SYSTEM_RESTART"
    CIRCUIT_BREAKER_RESET = "CIRCUIT_BREAKER_RESET"
    AUDIT_TRAIL_REQUEST = "AUDIT_TRAIL_REQUEST"


class ControlSeverity(enum.Enum):
    """Severity levels for control actions."""
    INFO = "INFO"
    WARNING = "WARNING"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class ApprovalStatus(enum.Enum):
    """Status of approval requests."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class OperatorRole(enum.Enum):
    """Operator roles with different permissions."""
    VIEWER = "VIEWER"  # Read-only access
    OPERATOR = "OPERATOR"  # Basic operational controls
    SUPERVISOR = "SUPERVISOR"  # Can approve major changes
    ADMIN = "ADMIN"  # Full system control
    EMERGENCY_RESPONDER = "EMERGENCY_RESPONDER"  # Emergency actions only


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class OperatorControlsConfig:
    """Configuration for operator controls."""
    enable_approval_required: bool = DEFAULT_ENABLE_APPROVAL_REQUIRED
    enable_emergency_override: bool = DEFAULT_ENABLE_EMERGENCY_OVERRIDE
    approval_timeout_sec: int = DEFAULT_APPROVAL_TIMEOUT_SEC
    max_pending_approvals: int = DEFAULT_MAX_PENDING_APPROVALS
    require_multi_sign: bool = DEFAULT_REQUIRE_MULTI_SIGN
    min_signers: int = DEFAULT_MIN_SIGNERS
    enable_audit_logging: bool = True
    enable_control_validation: bool = True

    def __post_init__(self) -> None:
        if self.approval_timeout_sec < 1:
            raise ValueError("approval_timeout_sec must be >= 1")
        if self.max_pending_approvals < 1:
            raise ValueError("max_pending_approvals must be >= 1")
        if self.min_signers < 1:
            raise ValueError("min_signers must be >= 1")


@dataclasses.dataclass(frozen=True, slots=True)
class Operator:
    """An operator with permissions."""
    operator_id: str
    name: str
    role: OperatorRole
    permissions: list[ControlAction]
    is_active: bool = True
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.operator_id:
            raise ValueError("operator_id must be non-empty")
        if not self.name:
            raise ValueError("name must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class ControlRequest:
    """A control action request."""
    request_id: str
    action: ControlAction
    severity: ControlSeverity
    operator_id: str
    timestamp_ns: int
    parameters: dict[str, Any]
    reason: str = ""
    requires_approval: bool = True
    expires_at_ns: int = 0
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("request_id must be non-empty")
        if not self.operator_id:
            raise ValueError("operator_id must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class ApprovalRequest:
    """An approval request for a control action."""
    request_id: str
    control_request: ControlRequest
    status: ApprovalStatus
    requested_by: str
    approved_by: list[str]
    denied_by: list[str]
    required_signers: int
    current_signers: int
    created_at_ns: int
    expires_at_ns: int
    completed_at_ns: int = 0
    approval_notes: str = ""
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class ControlExecution:
    """Result of a control action execution."""
    execution_id: str
    request_id: str
    action: ControlAction
    status: str  # "SUCCESS", "FAILED", "PARTIAL"
    executed_by: str
    executed_at_ns: int
    result_data: dict[str, Any]
    error_message: str = ""
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class ControlMetrics:
    """Metrics about operator controls."""
    total_requests: int
    approved_requests: int
    denied_requests: int
    expired_requests: int
    active_emergency_controls: int
    control_executions_by_action: dict[str, int]
    average_approval_time_sec: float
    pending_approvals: int
    operators_active: int


# ---------------------------------------------------------------------------
# Operator Controls System
# ---------------------------------------------------------------------------


class OperatorControls:
    """Comprehensive operator controls system.
    
    Provides operators with granular control over system behavior
    including emergency controls, mode changes, approval workflows,
    and manual intervention capabilities. Integrates with
    governance engine for audit trail and compliance.
    """
    
    def __init__(
        self,
        config: OperatorControlsConfig | None = None,
    ) -> None:
        """Initialize the operator controls system.
        
        Args:
            config: Operator controls configuration
        """
        self._config = config or OperatorControlsConfig()
        self._lock = Lock()
        
        # Operator management
        self._operators: dict[str, Operator] = {}
        
        # Control requests and approvals
        self._control_requests: dict[str, ControlRequest] = {}
        self._approval_requests: dict[str, ApprovalRequest] = {}
        
        # Control executions
        self._control_executions: list[ControlExecution] = []
        
        # Emergency state
        self._emergency_mode_active = False
        self._emergency_override_enabled = False
        
        # Event handlers
        self._control_handlers: dict[ControlAction, Callable[[ControlRequest], bool]] = {}
        self._event_handlers: list[Callable[[str, dict[str, Any]], None]] = []
        
        # Metrics
        self._metrics = self._init_metrics()
    
    def register_operator(self, operator: Operator) -> bool:
        """Register an operator with the system.
        
        Args:
            operator: Operator to register
            
        Returns:
            True if registration successful
        """
        with self._lock:
            if operator.operator_id in self._operators:
                return False
            
            self._operators[operator.operator_id] = operator
            self._metrics.operators_active += 1
            return True
    
    def unregister_operator(self, operator_id: str) -> bool:
        """Unregister an operator from the system.
        
        Args:
            operator_id: Operator identifier
            
        Returns:
            True if unregistration successful
        """
        with self._lock:
            if operator_id not in self._operators:
                return False
            
            del self._operators[operator_id]
            self._metrics.operators_active -= 1
            return True
    
    def submit_control_request(
        self,
        action: ControlAction,
        operator_id: str,
        parameters: dict[str, Any],
        reason: str = "",
        severity: ControlSeverity = ControlSeverity.MAJOR,
    ) -> ControlRequest:
        """Submit a control action request.
        
        Args:
            action: Control action to perform
            operator_id: Operator submitting the request
            parameters: Action parameters
            reason: Reason for the action
            severity: Severity level
            
        Returns:
            Control request
        """
        import secrets
        import time
        
        # Verify operator has permission
        operator = self._operators.get(operator_id)
        if not operator:
            raise ValueError(f"Operator {operator_id} not found")
        
        if action not in operator.permissions:
            raise PermissionError(f"Operator {operator_id} does not have permission for {action}")
        
        # Create request
        request_id = secrets.token_hex(16)
        timestamp_ns = time.time_ns()
        
        # Determine if approval required
        requires_approval = self._config.enable_approval_required and (
            severity in (ControlSeverity.CRITICAL, ControlSeverity.EMERGENCY) or
            action in (
                ControlAction.EMERGENCY_STOP,
                ControlAction.EMERGENCY_FREEZE,
                ControlAction.RISK_LIMIT_OVERRIDE,
            )
        )
        
        request = ControlRequest(
            request_id=request_id,
            action=action,
            severity=severity,
            operator_id=operator_id,
            timestamp_ns=timestamp_ns,
            parameters=parameters,
            reason=reason,
            requires_approval=requires_approval,
        )
        
        with self._lock:
            self._control_requests[request_id] = request
            self._metrics.total_requests += 1
            
            # Create approval request if needed
            if requires_approval:
                approval_request = ApprovalRequest(
                    request_id=request_id,
                    control_request=request,
                    status=ApprovalStatus.PENDING,
                    requested_by=operator_id,
                    approved_by=[],
                    denied_by=[],
                    required_signers=self._config.min_signers if self._config.require_multi_sign else 1,
                    current_signers=0,
                    created_at_ns=timestamp_ns,
                    expires_at_ns=timestamp_ns + (self._config.approval_timeout_sec * 1_000_000_000),
                )
                self._approval_requests[request_id] = approval_request
                self._metrics.pending_approvals += 1
            else:
                # Execute immediately if no approval required
                self._execute_control(request, operator_id)
        
        # Emit event
        self._emit_event("CONTROL_REQUESTED", {
            "request_id": request_id,
            "action": action.value,
            "operator_id": operator_id,
            "requires_approval": requires_approval,
        })
        
        return request
    
    def approve_request(
        self,
        request_id: str,
        approver_id: str,
        notes: str = "",
    ) -> bool:
        """Approve a control request.
        
        Args:
            request_id: Request to approve
            approver_id: Approver operator ID
            notes: Approval notes
            
        Returns:
            True if approval successful
        """
        import time
        
        with self._lock:
            approval_request = self._approval_requests.get(request_id)
            if not approval_request:
                return False
            
            if approval_request.status != ApprovalStatus.PENDING:
                return False
            
            # Check if expired
            if time.time_ns() > approval_request.expires_at_ns:
                approval_request = dataclasses.replace(
                    approval_request,
                    status=ApprovalStatus.EXPIRED,
                )
                self._approval_requests[request_id] = approval_request
                self._metrics.pending_approvals -= 1
                self._metrics.expired_requests += 1
                return False
            
            # Check if approver already approved
            if approver_id in approval_request.approved_by:
                return False
            
            # Add approval
            approved_by = list(approval_request.approved_by) + [approver_id]
            current_signers = approval_request.current_signers + 1
            
            # Check if we have enough signatures
            if current_signers >= approval_request.required_signers:
                approval_request = dataclasses.replace(
                    approval_request,
                    status=ApprovalStatus.APPROVED,
                    approved_by=approved_by,
                    current_signers=current_signers,
                    completed_at_ns=time.time_ns(),
                    approval_notes=notes,
                )
                self._approval_requests[request_id] = approval_request
                self._metrics.pending_approvals -= 1
                self._metrics.approved_requests += 1
                
                # Execute the control
                self._execute_control(approval_request.control_request, approver_id)
            else:
                approval_request = dataclasses.replace(
                    approval_request,
                    approved_by=approved_by,
                    current_signers=current_signers,
                )
                self._approval_requests[request_id] = approval_request
            
            return True
    
    def deny_request(
        self,
        request_id: str,
        denier_id: str,
        reason: str = "",
    ) -> bool:
        """Deny a control request.
        
        Args:
            request_id: Request to deny
            denier_id: Denier operator ID
            reason: Denial reason
            
        Returns:
            True if denial successful
        """
        import time
        
        with self._lock:
            approval_request = self._approval_requests.get(request_id)
            if not approval_request:
                return False
            
            if approval_request.status != ApprovalStatus.PENDING:
                return False
            
            approval_request = dataclasses.replace(
                approval_request,
                status=ApprovalStatus.DENIED,
                denied_by=list(approval_request.denied_by) + [denier_id],
                completed_at_ns=time.time_ns(),
                approval_notes=reason,
            )
            self._approval_requests[request_id] = approval_request
            self._metrics.pending_approvals -= 1
            self._metrics.denied_requests += 1
            
            return True
    
    def execute_control(
        self,
        action: ControlAction,
        parameters: dict[str, Any],
        operator_id: str,
    ) -> ControlExecution:
        """Execute a control action directly (for already-approved actions).
        
        Args:
            action: Control action
            parameters: Action parameters
            operator_id: Executing operator
            
        Returns:
            Control execution result
        """
        import secrets
        import time
        
        request = ControlRequest(
            request_id=secrets.token_hex(16),
            action=action,
            severity=ControlSeverity.MAJOR,
            operator_id=operator_id,
            timestamp_ns=time.time_ns(),
            parameters=parameters,
            requires_approval=False,
        )
        
        return self._execute_control(request, operator_id)
    
    def emergency_stop(self, operator_id: str, reason: str = "") -> ControlExecution:
        """Trigger emergency stop.
        
        Args:
            operator_id: Operator triggering emergency stop
            reason: Reason for emergency stop
            
        Returns:
            Control execution result
        """
        return self.execute_control(
            ControlAction.EMERGENCY_STOP,
            {"reason": reason},
            operator_id,
        )
    
    def emergency_freeze(self, operator_id: str, reason: str = "") -> ControlExecution:
        """Trigger emergency freeze.
        
        Args:
            operator_id: Operator triggering emergency freeze
            reason: Reason for emergency freeze
            
        Returns:
            Control execution result
        """
        return self.execute_control(
            ControlAction.EMERGENCY_FREEZE,
            {"reason": reason},
            operator_id,
        )
    
    def set_emergency_mode(self, active: bool) -> None:
        """Set emergency mode state.
        
        Args:
            active: Whether emergency mode is active
        """
        with self._lock:
            self._emergency_mode_active = active
            if active:
                self._metrics.active_emergency_controls += 1
            else:
                self._metrics.active_emergency_controls = max(0, self._metrics.active_emergency_controls - 1)
    
    def register_control_handler(
        self,
        action: ControlAction,
        handler: Callable[[ControlRequest], bool],
    ) -> None:
        """Register a handler for a control action.
        
        Args:
            action: Control action
            handler: Handler callable
        """
        with self._lock:
            self._control_handlers[action] = handler
    
    def register_event_handler(
        self,
        handler: Callable[[str, dict[str, Any]], None],
    ) -> None:
        """Register an event handler.
        
        Args:
            handler: Event handler callable
        """
        with self._lock:
            self._event_handlers.append(handler)
    
    def get_metrics(self) -> ControlMetrics:
        """Get operator controls metrics.
        
        Returns:
            Current metrics
        """
        with self._lock:
            return self._metrics
    
    def _execute_control(
        self,
        request: ControlRequest,
        executor_id: str,
    ) -> ControlExecution:
        """Execute a control request.
        
        Args:
            request: Control request
            executor_id: Executing operator
            
        Returns:
            Control execution result
        """
        import secrets
        import time
        
        execution_id = secrets.token_hex(16)
        timestamp_ns = time.time_ns()
        
        # Get handler for the action
        handler = self._control_handlers.get(request.action)
        
        if handler:
            try:
                success = handler(request)
                status = "SUCCESS" if success else "FAILED"
                error_message = ""
                result_data = {"executed": True, "handler_result": success}
            except Exception as e:
                status = "FAILED"
                error_message = str(e)
                result_data = {"executed": False, "error": error_message}
        else:
            status = "PARTIAL"  # No handler registered
            error_message = f"No handler registered for {request.action}"
            result_data = {"executed": False, "error": error_message}
        
        execution = ControlExecution(
            execution_id=execution_id,
            request_id=request.request_id,
            action=request.action,
            status=status,
            executed_by=executor_id,
            executed_at_ns=timestamp_ns,
            result_data=result_data,
            error_message=error_message,
        )
        
        with self._lock:
            self._control_executions.append(execution)
            
            # Update metrics
            self._metrics.control_executions_by_action[request.action.value] = \
                self._metrics.control_executions_by_action.get(request.action.value, 0) + 1
        
        # Emit event
        self._emit_event("CONTROL_EXECUTED", {
            "execution_id": execution_id,
            "action": request.action.value,
            "status": status,
            "executed_by": executor_id,
        })
        
        return execution
    
    def _emit_event(
        self,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """Emit a control event to handlers.
        
        Args:
            event_type: Type of event
            payload: Event payload
        """
        for handler in self._event_handlers:
            try:
                handler(event_type, payload)
            except Exception:
                pass  # Log error in production
    
    def _init_metrics(self) -> ControlMetrics:
        """Initialize control metrics."""
        return ControlMetrics(
            total_requests=0,
            approved_requests=0,
            denied_requests=0,
            expired_requests=0,
            active_emergency_controls=0,
            control_executions_by_action={},
            average_approval_time_sec=0.0,
            pending_approvals=0,
            operators_active=0,
        )


# ---------------------------------------------------------------------------
# Operator Controls Manager
# ---------------------------------------------------------------------------


class OperatorControlsManager:
    """Manager for operator controls."""
    
    def __init__(self, config: OperatorControlsConfig | None = None) -> None:
        """Initialize the operator controls manager.
        
        Args:
            config: Operator controls configuration
        """
        self._config = config or OperatorControlsConfig()
        self._controls = OperatorControls(config)
    
    def register_operator(self, operator: Operator) -> bool:
        """Register an operator.
        
        Args:
            operator: Operator to register
            
        Returns:
            True if successful
        """
        return self._controls.register_operator(operator)
    
    def submit_control_request(
        self,
        action: ControlAction,
        operator_id: str,
        parameters: dict[str, Any],
        reason: str = "",
        severity: ControlSeverity = ControlSeverity.MAJOR,
    ) -> ControlRequest:
        """Submit a control request.
        
        Args:
            action: Control action
            operator_id: Operator ID
            parameters: Action parameters
            reason: Reason
            severity: Severity
            
        Returns:
            Control request
        """
        return self._controls.submit_control_request(
            action, operator_id, parameters, reason, severity
        )
    
    def approve_request(
        self,
        request_id: str,
        approver_id: str,
        notes: str = "",
    ) -> bool:
        """Approve a request.
        
        Args:
            request_id: Request ID
            approver_id: Approver ID
            notes: Notes
            
        Returns:
            True if successful
        """
        return self._controls.approve_request(request_id, approver_id, notes)
    
    def emergency_stop(self, operator_id: str, reason: str = "") -> ControlExecution:
        """Trigger emergency stop.
        
        Args:
            operator_id: Operator ID
            reason: Reason
            
        Returns:
            Control execution
        """
        return self._controls.emergency_stop(operator_id, reason)
    
    def get_metrics(self) -> ControlMetrics:
        """Get metrics.
        
        Returns:
            Current metrics
        """
        return self._controls.get_metrics()


__all__ = [
    "ControlAction",
    "ControlSeverity",
    "ApprovalStatus",
    "OperatorRole",
    "OperatorControlsConfig",
    "Operator",
    "ControlRequest",
    "ApprovalRequest",
    "ControlExecution",
    "ControlMetrics",
    "OperatorControls",
    "OperatorControlsManager",
]
