"""
Base Governance Wrapper Template for External Repository Integration

This provides the governance and safety foundation for all external repository
integrations in the DIX VISION system. It enforces operator authority, safety checks,
and audit logging for all external operations.

Author: DIX VISION Governance Engine
Version: 42.2
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict


class GovernanceViolation(Exception):
    """Raised when governance rules are violated"""


class SafetyViolation(Exception):
    """Raised when safety checks fail"""


class PermissionLevel(Enum):
    """Operator permission levels"""

    NONE = "none"
    READ_ONLY = "read_only"
    EXECUTE = "execute"
    ADMIN = "admin"


class BaseExternalRepoGovernanceWrapper(ABC):
    """
    Base class for governance wrappers around external repositories.

    This ensures that all operations through external repositories are:
    - Governed by operator authority
    - Validated for safety
    - Audited for compliance
    - Monitored for performance
    """

    def __init__(
        self, repo_name: str, permission_level: PermissionLevel = PermissionLevel.READ_ONLY
    ):
        self.repo_name = repo_name
        self.permission_level = permission_level
        self.operation_log = []
        self.safety_check_enabled = True
        self.audit_log_enabled = True

        # Setup logging
        self.logger = logging.getLogger(f"governance.{repo_name}")

    def check_permission(self, required_level: PermissionLevel) -> bool:
        """Check if current permission level is sufficient"""
        level_hierarchy = {
            PermissionLevel.NONE: 0,
            PermissionLevel.READ_ONLY: 1,
            PermissionLevel.EXECUTE: 2,
            PermissionLevel.ADMIN: 3,
        }
        return level_hierarchy[self.permission_level] >= level_hierarchy[required_level]

    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """Override to implement specific safety checks for the repository"""
        if not self.safety_check_enabled:
            return True

        # Default safety checks
        if not isinstance(operation, str) or not operation:
            return False

        # Check for dangerous operations
        dangerous_keywords = ["delete", "drop", "destroy", "format", "erase"]
        if any(keyword in operation.lower() for keyword in dangerous_keywords):
            self.logger.warning(f"Potentially dangerous operation blocked: {operation}")
            return False

        return True

    def audit_log(self, operation: str, params: Dict[str, Any], result: Any, success: bool):
        """Log operation for audit trail"""
        if not self.audit_log_enabled:
            return

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "repository": self.repo_name,
            "operation": operation,
            "params": self._sanitize_params(params),
            "success": success,
            "permission_level": self.permission_level.value,
        }

        self.operation_log.append(log_entry)
        self.logger.info(f"Audit: {log_entry}")

    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from params for logging"""
        sanitized = {}
        sensitive_keys = ["password", "token", "secret", "key", "credential"]

        for key, value in params.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value

        return sanitized

    def execute_operation(
        self,
        operation: str,
        params: Dict[str, Any],
        required_permission: PermissionLevel = PermissionLevel.READ_ONLY,
    ) -> Any:
        """
        Execute an operation with governance oversight.

        This is the main entry point for all operations through external repositories.
        It enforces governance rules and safety checks.
        """
        try:
            # Check permission
            if not self.check_permission(required_permission):
                raise GovernanceViolation(
                    f"Insufficient permission. Required: {required_permission.value}, "
                    f"Current: {self.permission_level.value}"
                )

            # Safety check
            if not self.safety_check(operation, params):
                raise SafetyViolation(f"Safety check failed for operation: {operation}")

            # Execute the operation
            self.logger.info(f"Executing operation: {operation} on {self.repo_name}")
            result = self._execute_internal(operation, params)

            # Audit log
            self.audit_log(operation, params, result, success=True)

            return result

        except Exception as e:
            self.logger.error(f"Operation failed: {operation} - {str(e)}")
            self.audit_log(operation, params, None, success=False)
            raise

    @abstractmethod
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method to be implemented by specific repository wrappers.

        This should contain the actual implementation of calling the external repository.
        """

    def get_operation_history(self, limit: int = 100) -> list:
        """Get recent operation history for audit"""
        return self.operation_log[-limit:]

    def set_permission_level(self, level: PermissionLevel):
        """Update permission level (requires higher authorization in production)"""
        self.permission_level = level
        self.logger.info(f"Permission level updated to: {level.value}")

    def enable_safety_checks(self, enabled: bool = True):
        """Enable or disable safety checks"""
        self.safety_check_enabled = enabled
        self.logger.info(f"Safety checks {'enabled' if enabled else 'disabled'}")

    def enable_audit_logging(self, enabled: bool = True):
        """Enable or disable audit logging"""
        self.audit_log_enabled = enabled
        self.logger.info(f"Audit logging {'enabled' if enabled else 'disabled'}")


class ExternalRepositoryMetrics:
    """Metrics collection for external repository operations"""

    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        self.operation_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_execution_time = 0
        self.last_operation_time = None

    def record_operation(self, success: bool, execution_time: float):
        """Record operation metrics"""
        self.operation_count += 1
        self.last_operation_time = datetime.utcnow()
        self.total_execution_time += execution_time

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        success_rate = (
            (self.success_count / self.operation_count * 100) if self.operation_count > 0 else 0
        )
        avg_execution_time = (
            (self.total_execution_time / self.operation_count) if self.operation_count > 0 else 0
        )

        return {
            "repository": self.repo_name,
            "total_operations": self.operation_count,
            "success_rate": success_rate,
            "average_execution_time": avg_execution_time,
            "last_operation": (
                self.last_operation_time.isoformat() if self.last_operation_time else None
            ),
        }


class ExternalRepositoryHealthCheck:
    """Health check for external repository containers"""

    @staticmethod
    def check_repository_health(
        repo_name: str, wrapper: BaseExternalRepoGovernanceWrapper
    ) -> Dict[str, Any]:
        """Perform health check on external repository"""
        try:
            # Test basic operation
            start_time = datetime.utcnow()
            result = wrapper.execute_operation("health_check", {}, PermissionLevel.READ_ONLY)
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "repository": repo_name,
                "healthy": True,
                "response_time": execution_time,
                "last_check": datetime.utcnow().isoformat(),
                "metrics": result,
            }
        except Exception as e:
            return {
                "repository": repo_name,
                "healthy": False,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
            }
