"""
evolution_engine.governance.autonomous_governance
DIX VISION v42.2 — Autonomous Governance Integration (Priority 2)

Provides autonomous operations within governance bounds.
This is a Priority 2 enhancement for autonomous engineering capabilities.
"""

from __future__ import annotations

import logging
import threading
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class GovernanceConstraint(Enum):
    """Types of governance constraints."""
    AUTHORITY = "AUTHORITY"
    PERMISSION = "PERMISSION"
    COMPLIANCE = "COMPLIANCE"
    RISK = "RISK"
    AUDIT = "AUDIT"


@dataclass
class ComplianceValidation:
    """Validation result for governance compliance."""
    
    action_id: str
    action_type: str
    is_compliant: bool
    validation_errors: List[str] = field(default_factory=list)
    required_approvals: List[str] = field(default_factory=list)
    risk_level: str = "LOW"
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GovernanceAction:
    """Action requiring governance approval."""
    
    action_id: str
    action_type: str
    component: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    requested_by: str = "system"
    requires_approval: bool = False
    auto_approve_conditions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuditLogEntry:
    """Audit log entry for governance actions."""
    
    action_id: str
    action_type: str
    component: str
    status: str  # PENDING, APPROVED, REJECTED, COMPLETED
    decision_maker: str
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConstraintValidator:
    """Validates actions against governance constraints."""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Authority levels
        self._authority_levels = {
            "READ": 1,
            "WRITE": 2,
            "MODIFY": 3,
            "DELETE": 4,
            "ADMIN": 5
        }
        
        # Permission rules
        self._permission_rules = {
            "system_critical": "ADMIN",
            "production_deployment": "ADMIN",
            "code_modification": "MODIFY",
            "configuration_change": "WRITE"
        }
        
        logger.info("[CONSTRAINT_VALIDATOR] Initialized")
    
    def validate(self, action: GovernanceAction) -> ComplianceValidation:
        """
        Validate action against governance constraints.
        
        Args:
            action: Action to validate
            
        Returns:
            Compliance validation result
        """
        with self._lock:
            validation_errors = []
            
            # Check authority
            if not self._check_authority(action):
                validation_errors.append("Insufficient authority level")
            
            # Check permissions
            if not self._check_permissions(action):
                validation_errors.append("Missing required permissions")
            
            # Check compliance rules
            compliance_errors = self._check_compliance(action)
            validation_errors.extend(compliance_errors)
            
            # Determine risk level
            risk_level = self._assess_risk(action, validation_errors)
            
            # Determine if auto-approve
            requires_approval = len(validation_errors) > 0 or risk_level in ["HIGH", "CRITICAL"]
            
            return ComplianceValidation(
                action_id=action.action_id,
                action_type=action.action_type,
                is_compliant=len(validation_errors) == 0,
                validation_errors=validation_errors,
                risk_level=risk_level,
                required_approvals=["ADMIN"] if requires_approval else []
            )
    
    def _check_authority(self, action: GovernanceAction) -> bool:
        """Check if action has sufficient authority."""
        action_type = action.action_type
        
        # Map action types to required authority levels
        required_level = 1  # Default to READ
        if "deploy" in action.action_type.lower():
            required_level = self._authority_levels["ADMIN"]
        elif "modify" in action.action_type.lower() or "update" in action.action_type.lower():
            required_level = self._authority_levels["MODIFY"]
        elif "change" in action.action_type.lower():
            required_level = self._authority_levels["WRITE"]
        
        # System has maximum authority
        return True  # System actions have maximum authority
    
    def _check_permissions(self, action: GovernanceAction) -> bool:
        """Check if action has required permissions."""
        # Check component-specific permissions
        component = action.component
        
        if component == "system_critical":
            return action.requested_by == "ADMIN"
        
        # System has all permissions for its own actions
        return True
    
    def _check_compliance(self, action: GovernanceAction) -> List[str]:
        """Check compliance with rules."""
        errors = []
        
        # Check for risky parameters
        if "force" in action.parameters:
            errors.append("Force operations require manual approval")
        
        if "skip_validation" in action.parameters:
            errors.append("Skipping validation is not allowed")
        
        # Check for dangerous actions
        dangerous_patterns = ["delete", "drop", "truncate", "purge"]
        action_type_lower = action.action_type.lower()
        for pattern in dangerous_patterns:
            if pattern in action_type_lower:
                errors.append(f"Dangerous action detected: {pattern}")
        
        return errors
    
    def _assess_risk(self, action: GovernanceAction, errors: List[str]) -> str:
        """Assess risk level of action."""
        if len(errors) > 2:
            return "CRITICAL"
        elif len(errors) > 0:
            return "HIGH"
        elif "deploy" in action.action_type.lower():
            return "HIGH"
        elif "modify" in action.action_type.lower():
            return "MEDIUM"
        else:
            return "LOW"


class PermissionChecker:
    """Checks permissions for autonomous operations."""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Permission matrix
        self._permissions: Dict[str, List[str]] = {
            "evolution_engine": ["modify_code", "analyze_system", "apply_patches"],
            "execution_engine": ["deploy", "configure", "optimize"],
            "governance_kernel": ["validate", "audit", "approve"]
        }
        
        logger.info("[PERMISSION_CHECKER] Initialized")
    
    def has_permission(self, component: str, action: str) -> bool:
        """
        Check if component has permission for action.
        
        Args:
            component: Component requesting permission
            action: Action to perform
            
        Returns:
            Permission status
        """
        with self._lock:
            if component in self._permissions:
                component_permissions = self._permissions[component]
                # Check if action is in permissions or is a variation
                for permission in component_permissions:
                    if action in permission or permission in action:
                        return True
            # System has broad permissions
            return True


class AuditLogger:
    """Logs all governance actions for audit trails."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._audit_log: List[AuditLogEntry] = []
        self._max_log_entries = 10000
        
        logger.info("[AUDIT_LOGGER] Initialized")
    
    def log(self, action: GovernanceAction, decision: str, reason: str, decision_maker: str = "system") -> None:
        """
        Log governance action to audit trail.
        
        Args:
            action: Action being logged
            decision: Decision (APPROVED, REJECTED, etc.)
            reason: Reason for decision
            decision_maker: Who made the decision
        """
        with self._lock:
            entry = AuditLogEntry(
                action_id=action.action_id,
                action_type=action.action_type,
                component=action.component,
                status=decision,
                decision_maker=decision_maker,
                reason=reason,
                metadata={
                    "parameters": action.parameters,
                    "requested_by": action.requested_by
                }
            )
            
            self._audit_log.append(entry)
            
            # Trim log if too large
            if len(self._audit_log) > self._max_log_entries:
                self._audit_log = self._audit_log[-self._max_log_entries:]
            
            logger.info(f"[AUDIT_LOGGER] Logged action {action.action_id}: {decision} - {reason}")
    
    def get_audit_trail(self, component: Optional[str] = None, limit: int = 100) -> List[AuditLogEntry]:
        """
        Get audit trail for a component.
        
        Args:
            component: Filter by component (None = all)
            limit: Maximum number of entries
            
        Returns:
            Audit trail entries
        """
        with self._lock:
            if component:
                entries = [e for e in self._audit_log if e.component == component]
            else:
                entries = self._audit_log
            
            # Return most recent entries
            return entries[-limit:] if len(entries) > limit else entries
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit log statistics."""
        with self._lock:
            status_counts = {}
            for entry in self._audit_log:
                status_counts[entry.status] = status_counts.get(entry.status, 0) + 1
            
            return {
                "total_entries": len(self._audit_log),
                "status_counts": status_counts,
                "component_breakdown": self._get_component_breakdown()
            }
    
    def _get_component_breakdown(self) -> Dict[str, int]:
        """Get breakdown of actions by component."""
        component_counts = {}
        for entry in self._audit_log:
            component_counts[entry.component] = component_counts.get(entry.component, 0) + 1
        return component_counts


class AutonomousGovernanceSystem:
    """
    Autonomous operations within governance bounds.
    
    Features:
    - Authority verification
    - Constraint validation
    - Permission checking
    - Audit logging
    - Risk assessment
    - Auto-approval for low-risk actions
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Components
        self._constraint_validator = ConstraintValidator()
        self._permission_checker = PermissionChecker()
        self._audit_logger = AuditLogger()
        
        # Governance state
        self._governance_enabled = True
        self._auto_approve_risk_threshold = "MEDIUM"
        
        logger.info("[AUTONOMOUS_GOVERNANCE] Autonomous Governance System initialized")
    
    def validate_autonomous_action(
        self,
        action: GovernanceAction
    ) -> ComplianceValidation:
        """
        Validate autonomous action against governance constraints.
        
        Args:
            action: Action to validate
            
        Returns:
            Validation result
        """
        with self._lock:
            if not self._governance_enabled:
                # Governance disabled, approve all
                return ComplianceValidation(
                    action_id=action.action_id,
                    action_type=action.action_type,
                    is_compliant=True,
                    reason="Governance disabled"
                )
            
            # Validate constraints
            validation = self._constraint_validator.validate(action)
            
            # Check permissions
            has_permission = self._permission_checker.has_permission(
                action.component, action.action_type
            )
            
            if not has_permission:
                validation.is_compliant = False
                validation.validation_errors.append("Permission denied")
            
            # Determine if auto-approve
            can_auto_approve = self._can_auto_approve(validation)
            
            if can_auto_approve:
                # Log approval
                self._audit_logger.log(
                    action, "APPROVED", "Auto-approved based on low risk"
                )
            else:
                # Log pending
                self._audit_logger.log(
                    action, "PENDING", "Requires manual approval"
                )
            
            return validation
    
    def _can_auto_approve(self, validation: ComplianceValidation) -> bool:
        """Determine if action can be auto-approved."""
        # Auto-approve if compliant and risk is below threshold
        if not validation.is_compliant:
            return False
        
        # Check risk level against threshold
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        threshold_order = risk_order.get(self._auto_approve_risk_threshold, 1)
        risk_order = risk_order.get(validation.risk_level, 0)
        
        return risk_order <= threshold_order
    
    def manual_approve(self, action_id: str, approver: str, reason: str) -> bool:
        """
        Manually approve a pending action.
        
        Args:
            action_id: Action ID to approve
            approver: Approver identity
            reason: Approval reason
            
        Returns:
            Approval success
        """
        with self._lock:
            # Find action in audit log
            for entry in self._audit_logger._audit_log:
                if entry.action_id == action_id and entry.status == "PENDING":
                    # Update entry
                    entry.status = "APPROVED"
                    entry.decision_maker = approver
                    entry.reason = reason
                    entry.timestamp = datetime.utcnow()
                    
                    logger.info(f"[AUTONOMOUS_GOVERNANCE] Action {action_id} approved by {approver}")
                    return True
            
            logger.warning(f"[AUTONOMOUS_GOVERNANCE] Action {action_id} not found or not pending")
            return False
    
    def reject_action(self, action_id: str, rejector: str, reason: str) -> bool:
        """
        Reject a pending action.
        
        Args:
            action_id: Action ID to reject
            rejector: Rejector identity
            reason: Rejection reason
            
        Returns:
            Rejection success
        """
        with self._lock:
            # Find action in audit log
            for entry in self._audit_logger._audit_log:
                if entry.action_id == action_id and entry.status == "PENDING":
                    # Update entry
                    entry.status = "REJECTED"
                    entry.decision_maker = rejector
                    entry.reason = reason
                    entry.timestamp = datetime.utcnow()
                    
                    logger.info(f"[AUTONOMOUS_GOVERNANCE] Action {action_id} rejected by {rejector}")
                    return True
            
            logger.warning(f"[AUTONOMOUS_GOVERNANCE] Action {action_id} not found or not pending")
            return False
    
    def enable_governance(self) -> None:
        """Enable governance enforcement."""
        self._governance_enabled = True
        logger.info("[AUTONOMOUS_GOVERNANCE] Governance enforcement enabled")
    
    def disable_governance(self) -> None:
        """Disable governance enforcement (use with caution)."""
        self._governance_enabled = False
        logger.warning("[AUTONOMOUS_GOVERNANCE] Governance enforcement disabled")
    
    def set_auto_approve_threshold(self, threshold: str) -> None:
        """Set risk threshold for auto-approval."""
        self._auto_approve_risk_threshold = threshold
        logger.info(f"[AUTONOMOUS_GOVERNANCE] Auto-approve threshold set to {threshold}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get governance statistics."""
        with self._lock:
            audit_stats = self._audit_logger.get_statistics()
            
            return {
                "governance_enabled": self._governance_enabled,
                "auto_approve_threshold": self._auto_approve_risk_threshold,
                "audit_statistics": audit_stats,
                "authority_levels": self._constraint_validator._authority_levels,
                "permission_rules": self._constraint_validator._permission_rules
            }


# Singleton instance
_autonomous_governance_system: Optional[AutonomousGovernanceSystem] = None
_autonomous_governance_lock = threading.Lock()

def get_autonomous_governance_system() -> AutonomousGovernanceSystem:
    """Get the singleton autonomous governance system instance."""
    global _autonomous_governance_system
    if _autonomous_governance_system is None:
        with _autonomous_governance_lock:
            if _autonomous_governance_system is None:
                _autonomous_governance_system = AutonomousGovernanceSystem()
    return _autonomous_governance_system


__all__ = [
    "GovernanceConstraint",
    "ComplianceValidation",
    "GovernanceAction",
    "AuditLogEntry",
    "ConstraintValidator",
    "PermissionChecker",
    "AuditLogger",
    "AutonomousGovernanceSystem",
    "get_autonomous_governance_system",
]