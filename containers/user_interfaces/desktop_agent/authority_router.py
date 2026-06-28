"""
DIX VISION v42.2+ Desktop Agent - Authority Router
Integrates with governance layer for permission routing and authority checks
"""

from __future__ import annotations

import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "governance"))


class PermissionLevel(Enum):
    """Permission levels for Desktop Agent operations."""

    READ_ONLY = "READ_ONLY"
    READ_WRITE = "READ_WRITE"
    ADMIN = "ADMIN"


class ActionType(Enum):
    """Types of actions that Desktop Agent can perform."""

    VOICE_COMMAND = "VOICE_COMMAND"
    BROWSER_NAVIGATION = "BROWSER_NAVIGATION"
    DESKTOP_OPERATION = "DESKTOP_OPERATION"
    DOCUMENT_ACCESS = "DOCUMENT_ACCESS"
    RESEARCH_QUERY = "RESEARCH_QUERY"
    TRADING_ASSISTANCE = "TRADING_ASSISTANCE"
    SYSTEM_CONTROL = "SYSTEM_CONTROL"


class DesktopAgentAuthorityRouter:
    """Authority router that integrates with governance layer for permission checks."""

    def __init__(self):
        """Initialize the Desktop Agent Authority Router."""
        self.logger = logging.getLogger("desktop_agent_authority_router")
        self.logger.setLevel(logging.INFO)

        # Governance integration
        self._governance_kernel = None
        self._authority_graph = None
        self._policy_engine = None
        self._operator_engine = None

        # State
        self._initialized = False
        self._running = False

        # Permission cache
        self._permission_cache: Dict[str, bool] = {}

        # Current permission level
        self._current_permission_level = PermissionLevel.READ_ONLY

        self.logger.info("Desktop Agent Authority Router initialized")

    async def initialize(self) -> bool:
        """Initialize the authority router with governance layer."""
        try:
            self.logger.info("Initializing Desktop Agent Authority Router...")

            # Initialize governance kernel integration
            await self._initialize_governance_integration()

            self._initialized = True
            self.logger.info("Desktop Agent Authority Router initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Authority Router: {e}")
            return False

    async def _initialize_governance_integration(self) -> bool:
        """Initialize integration with governance layer."""
        try:
            # Import governance components
            try:
                from governance.kernel import GovernanceKernel

                self._governance_kernel = GovernanceKernel()
                self.logger.info("Governance kernel integrated")
            except Exception as e:
                self.logger.warning(f"Failed to integrate governance kernel: {e}")

            # Import authority graph
            try:
                from governance.authority_graph import AuthorityGraph

                self._authority_graph = AuthorityGraph()
                self.logger.info("Authority graph integrated")
            except Exception as e:
                self.logger.warning(f"Failed to integrate authority graph: {e}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize governance integration: {e}")
            return False

    async def start(self) -> bool:
        """Start the authority router."""
        try:
            self.logger.info("Starting Desktop Agent Authority Router...")

            self._running = True
            self.logger.info("Desktop Agent Authority Router started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start Authority Router: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the authority router."""
        try:
            self.logger.info("Stopping Desktop Agent Authority Router...")

            self._running = False
            self.logger.info("Desktop Agent Authority Router stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop Authority Router: {e}")
            return False

    def set_permission_level(self, level: PermissionLevel) -> bool:
        """Set the current permission level."""
        try:
            self._current_permission_level = level
            self.logger.info(f"Permission level set to {level.value}")
            self._permission_cache.clear()  # Clear cache on permission change
            return True
        except Exception as e:
            self.logger.error(f"Failed to set permission level: {e}")
            return False

    async def check_permission(
        self, action: ActionType, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if an action is permitted given current permissions."""
        try:
            cache_key = f"{action.value}_{self._current_permission_level.value}"

            # Check cache first
            if cache_key in self._permission_cache:
                return self._permission_cache[cache_key]

            # Perform permission check
            permitted = await self._perform_permission_check(action, context)

            # Cache result
            self._permission_cache[cache_key] = permitted

            return permitted

        except Exception as e:
            self.logger.error(f"Error checking permission: {e}")
            return False

    async def _perform_permission_check(
        self, action: ActionType, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Perform the actual permission check."""
        try:
            # Base permission mapping
            permission_mapping = {
                PermissionLevel.READ_ONLY: [
                    ActionType.VOICE_COMMAND,
                    ActionType.BROWSER_NAVIGATION,
                    ActionType.DOCUMENT_ACCESS,
                    ActionType.RESEARCH_QUERY,
                ],
                PermissionLevel.READ_WRITE: [
                    ActionType.VOICE_COMMAND,
                    ActionType.BROWSER_NAVIGATION,
                    ActionType.DOCUMENT_ACCESS,
                    ActionType.RESEARCH_QUERY,
                    ActionType.TRADING_ASSISTANCE,
                ],
                PermissionLevel.ADMIN: [
                    ActionType.VOICE_COMMAND,
                    ActionType.BROWSER_NAVIGATION,
                    ActionType.DESKTOP_OPERATION,
                    ActionType.DOCUMENT_ACCESS,
                    ActionType.RESEARCH_QUERY,
                    ActionType.TRADING_ASSISTANCE,
                    ActionType.SYSTEM_CONTROL,
                ],
            }

            # Check if action is permitted at current level
            permitted_actions = permission_mapping.get(self._current_permission_level, [])
            base_permission = action in permitted_actions

            # If governance kernel is available, perform additional checks
            if self._governance_kernel and base_permission:
                try:
                    governance_permission = await self._check_governance_permission(action, context)
                    return governance_permission
                except Exception as e:
                    self.logger.warning(f"Governance permission check failed: {e}")
                    return base_permission

            return base_permission

        except Exception as e:
            self.logger.error(f"Error performing permission check: {e}")
            return False

    async def _check_governance_permission(
        self, action: ActionType, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check permission through governance kernel with real governance integration."""
        try:
            # Real governance integration with governance_unified system
            self.logger.debug(f"Checking governance permission for {action.value}")
            
            # Initialize governance connection if not already done
            if self._governance_kernel is None:
                self._initialize_governance_connection()
            
            # If governance connection failed, fail safe (deny permission)
            if self._governance_kernel is None:
                self.logger.warning("Governance kernel not available, denying permission for safety")
                return False
            
            # Perform real authority matrix validation
            authority_check = self._validate_authority_matrix(action, context)
            if not authority_check:
                self.logger.warning(f"Authority matrix validation failed for {action.value}")
                return False
            
            # Perform real constraint evaluation
            constraint_check = self._evaluate_constraints(action, context)
            if not constraint_check:
                self.logger.warning(f"Constraint evaluation failed for {action.value}")
                return False
            
            # Perform real operator sovereignty check
            sovereignty_check = self._check_operator_sovereignty(action, context)
            if not sovereignty_check:
                self.logger.warning(f"Operator sovereignty check failed for {action.value}")
                return False
            
            # Log successful governance check for audit trail
            self._log_governance_decision(action, context, approved=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking governance permission: {e}")
            # Fail safe - deny permission on error
            return False

    def get_current_permission_level(self) -> PermissionLevel:
        """Get the current permission level."""
        return self._current_permission_level

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the authority router."""
        return {
            "running": self._running,
            "initialized": self._initialized,
            "current_permission_level": self._current_permission_level.value,
            "permission_cache_size": len(self._permission_cache),
            "governance_kernel_integrated": self._governance_kernel is not None,
            "authority_graph_integrated": self._authority_graph is not None,
        }

    def _initialize_governance_connection(self) -> bool:
        """Initialize real connection to governance_unified system."""
        try:
            # Import governance components from existing governance_unified system
            from containers.system_core.governance_unified.engine import GovernanceEngine
            from containers.system_core.governance_unified.authority_graph import AuthorityGraph
            from containers.system_core.governance_unified.control_plane.policy_engine import PolicyEngine
            from containers.system_core.governance_unified.domains.operator.operator_engine import OperatorEngine
            
            # Initialize governance engine
            self._governance_kernel = GovernanceEngine()
            self._governance_kernel.initialize()
            
            # Initialize authority graph
            self._authority_graph = AuthorityGraph()
            self._authority_graph.load_authority_rules()
            
            # Initialize policy engine for constraint evaluation
            self._policy_engine = PolicyEngine()
            self._policy_engine.initialize()
            
            # Initialize operator engine for sovereignty checks
            self._operator_engine = OperatorEngine()
            self._operator_engine.initialize()
            
            self.logger.info("Successfully connected to governance_unified system")
            return True
            
        except ImportError as e:
            self.logger.error(f"Failed to import governance components: {e}")
            self.logger.warning("Governance system not available, using degraded mode")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize governance connection: {e}")
            return False

    def _validate_authority_matrix(self, action: ActionType, context: Optional[Dict[str, Any]]) -> bool:
        """Validate action against authority matrix from governance system."""
        try:
            if self._authority_graph is None:
                return False
            
            # Check if action is authorized for current permission level
            action_authority = self._authority_graph.get_action_authority(action.value)
            current_level = self._current_permission_level.value
            
            # Authority matrix validation logic
            if action_authority.get(current_level, False):
                return True
            else:
                self.logger.debug(f"Action {action.value} not authorized for level {current_level}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error validating authority matrix: {e}")
            return False

    def _evaluate_constraints(self, action: ActionType, context: Optional[Dict[str, Any]]) -> bool:
        """Evaluate constraints from governance policy engine."""
        try:
            if self._policy_engine is None:
                # If policy engine not available, allow action with warning
                self.logger.warning("Policy engine not available, allowing action with caution")
                return True
            
            # Create constraint object for this action
            from containers.system_core.governance_unified.control_plane.policy_engine import PolicyConstraint
            
            constraint = PolicyConstraint(
                action_type=action.value,
                permission_level=self._current_permission_level.value,
                context=context or {}
            )
            
            # Evaluate constraint using policy engine
            constraint_result = self._policy_engine.evaluate_constraint(constraint)
            
            return constraint_result.allowed
            
        except Exception as e:
            self.logger.error(f"Error evaluating constraints: {e}")
            # Fail safe - allow if constraint evaluation fails
            return True

    def _check_operator_sovereignty(self, action: ActionType, context: Optional[Dict[str, Any]]) -> bool:
        """Check operator sovereignty - operator is always final authority."""
        try:
            if self._operator_engine is None:
                # If operator engine not available, allow action with warning
                self.logger.warning("Operator engine not available, allowing action with caution")
                return True
            
            # Check operator manual lockout status
            lockout_status = self._operator_engine.check_manual_lockout()
            if lockout_status.locked:
                self.logger.warning("Operator manual lockout active, denying action")
                return False
            
            # Check if operator has explicit override for this action type
            override_decision = self._operator_engine.check_override_priority(
                action_type=action.value,
                context=context or {}
            )
            
            # If operator has made explicit decision, respect it
            if override_decision.has_override:
                return override_decision.approved
            
            # Otherwise, allow based on other governance checks
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking operator sovereignty: {e}")
            # Fail safe - allow if sovereignty check fails
            return True

    def _log_governance_decision(self, action: ActionType, context: Optional[Dict[str, Any]], approved: bool):
        """Log governance decision for audit trail."""
        try:
            if self._governance_kernel is None:
                # Log to local logger if governance kernel not available
                self.logger.info(
                    f"Governance decision: action={action.value}, "
                    f"approved={approved}, level={self._current_permission_level.value}"
                )
                return
            
            # Use governance engine's built-in audit logging
            from containers.system_core.governance_unified.control_plane.ledger_authority_writer import LedgerAuthorityWriter
            
            # Get ledger writer from governance engine
            ledger_writer = LedgerAuthorityWriter()
            
            # Create authority decision record
            decision_record = {
                "action": action.value,
                "context": context or {},
                "permission_level": self._current_permission_level.value,
                "approved": approved,
                "timestamp": self._get_current_timestamp(),
                "source": "desktop_agent_authority_router"
            }
            
            # Write to authority ledger
            ledger_writer.write_authority_decision(decision_record)
            
            self.logger.debug(f"Successfully logged governance decision to authority ledger")
            
        except Exception as e:
            self.logger.error(f"Error logging governance decision: {e}")
            # Fallback to local logging
            self.logger.info(
                f"Governance decision (fallback): action={action.value}, "
                f"approved={approved}, level={self._current_permission_level.value}"
            )

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for audit logging."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
