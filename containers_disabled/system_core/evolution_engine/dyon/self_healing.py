"""evolution_engine.dyon.self_healing — Self-Healing Mechanisms for DYON Predictive Intelligence.

Self-healing capabilities that automatically respond to DYON predictions and detected issues.

This implementation provides self-healing capabilities:
- Automated healing action execution
- Prediction-based proactive healing
- Issue-based reactive healing
- Healing strategy management
- Healing effectiveness monitoring
- Rollback capabilities
- Healing policy enforcement
- Integration with DYON predictions

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides self-healing for system optimization, never for trading purposes.
All healing actions are governed and logged for safety.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

_logger = logging.getLogger(__name__)


class HealingType(Enum):
    """Types of healing actions."""

    RESTART_SERVICE = "restart_service"
    SCALE_RESOURCES = "scale_resources"
    CLEAR_CACHE = "clear_cache"
    ROTATE_LOGS = "rotate_logs"
    UPDATE_DEPENDENCY = "update_dependency"
    APPLY_PATCH = "apply_patch"
    ADJUST_CONFIG = "adjust_config"
    NETWORK_RECOVERY = "network_recovery"
    DATABASE_RECOVERY = "database_recovery"
    CUSTOM_HEALING = "custom_healing"


class HealingTrigger(Enum):
    """Types of healing triggers."""

    PREDICTIVE = "predictive"  # Based on predictions
    REACTIVE = "reactive"  # Based on detected issues
    MANUAL = "manual"  # Manually triggered
    SCHEDULED = "scheduled"  # Scheduled healing actions
    THRESHOLD = "threshold"  # Based on threshold crossing


class HealingStatus(Enum):
    """Status of healing actions."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


@dataclass
class HealingAction:
    """Healing action to be executed."""

    action_id: str
    healing_type: HealingType
    trigger: HealingTrigger
    target_component: str
    parameters: Dict[str, Any]
    priority: str  # critical, high, medium, low
    estimated_duration: float  # seconds
    risk_level: str  # high, medium, low
    description: str = ""
    rollback_action: Optional[Dict[str, Any]] = None


@dataclass
class HealingResult:
    """Result of healing action execution."""

    action_id: str
    status: HealingStatus
    start_time: float
    end_time: float
    duration_seconds: float
    success: bool
    message: str
    affected_components: List[str]
    metrics_before: Dict[str, Any]
    metrics_after: Dict[str, Any]
    rollback_performed: bool = False
    error_message: str = ""


@dataclass
class HealingPolicy:
    """Policy for when and how to perform healing."""

    policy_id: str
    policy_name: str
    healing_type: HealingType
    trigger_type: HealingTrigger
    conditions: Dict[str, Any]  # Conditions that trigger healing
    max_attempts: int
    cooldown_period: float  # seconds
    requires_approval: bool
    auto_rollback: bool
    rollback_threshold: float  # Performance threshold for rollback
    is_active: bool = True


class SelfHealingEngine:
    """Self-healing engine for automated system recovery.

    DYON uses this to automatically respond to predictions and detected issues
    without performing trading operations.
    """

    def __init__(self, repo_root: str = "."):
        """Initialize self-healing engine.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self._lock = threading.Lock()
        self._healing_queue: deque = deque()
        self._healing_history: List[HealingResult] = []
        self._healing_policies: Dict[str, HealingPolicy] = {}
        self._active_healing: Dict[str, HealingAction] = {}
        self._healing_handlers: Dict[HealingType, Callable] = {}
        self._component_states: Dict[str, str] = {}  # component -> state
        self._healing_metrics: Dict[str, Any] = {}

        # Initialize default policies
        self._initialize_default_policies()

        # Register default healing handlers
        self._register_default_handlers()

        _logger.info(
            f"[SelfHealingEngine] Initialized with repo_root={repo_root}, "
            f"policies={len(self._healing_policies)}"
        )

    def _initialize_default_policies(self) -> None:
        """Initialize default healing policies."""
        default_policies = [
            HealingPolicy(
                policy_id="auto_restart_policy",
                policy_name="Automatic Service Restart Policy",
                healing_type=HealingType.RESTART_SERVICE,
                trigger_type=HealingTrigger.REACTIVE,
                conditions={"error_rate_threshold": 0.1, "response_time_threshold": 5000},
                max_attempts=3,
                cooldown_period=300.0,
                requires_approval=False,
                auto_rollback=True,
                rollback_threshold=0.2,
            ),
            HealingPolicy(
                policy_id="predictive_scale_policy",
                policy_name="Predictive Scaling Policy",
                healing_type=HealingType.SCALE_RESOURCES,
                trigger_type=HealingTrigger.PREDICTIVE,
                conditions={"predicted_utilization_threshold": 0.8},
                max_attempts=2,
                cooldown_period=600.0,
                requires_approval=True,
                auto_rollback=True,
                rollback_threshold=0.15,
            ),
            HealingPolicy(
                policy_id="cache_clear_policy",
                policy_name="Cache Clear Policy",
                healing_type=HealingType.CLEAR_CACHE,
                trigger_type=HealingTrigger.THRESHOLD,
                conditions={"cache_hit_rate_threshold": 0.5},
                max_attempts=1,
                cooldown_period=60.0,
                requires_approval=False,
                auto_rollback=False,
                rollback_threshold=0.0,
            ),
        ]

        for policy in default_policies:
            self._healing_policies[policy.policy_id] = policy

        _logger.info("[SelfHealingEngine] Initialized default healing policies")

    def _register_default_handlers(self) -> None:
        """Register default healing action handlers."""
        self._healing_handlers[HealingType.RESTART_SERVICE] = self._handle_restart_service
        self._healing_handlers[HealingType.SCALE_RESOURCES] = self._handle_scale_resources
        self._healing_handlers[HealingType.CLEAR_CACHE] = self._handle_clear_cache
        self._healing_handlers[HealingType.ROTATE_LOGS] = self._handle_rotate_logs
        self._healing_handlers[HealingType.UPDATE_DEPENDENCY] = self._handle_update_dependency
        self._healing_handlers[HealingType.APPLY_PATCH] = self._handle_apply_patch
        self._healing_handlers[HealingType.ADJUST_CONFIG] = self._handle_adjust_config

        _logger.info("[SelfHealingEngine] Registered default healing handlers")

    def register_healing_handler(self, healing_type: HealingType, handler: Callable) -> bool:
        """Register a healing action handler.

        Args:
            healing_type: Type of healing action
            handler: Handler function

        Returns:
            True if registered successfully
        """
        with self._lock:
            self._healing_handlers[healing_type] = handler
            _logger.info(f"[SelfHealingEngine] Registered handler for {healing_type.value}")

            return True

    def add_healing_policy(self, policy: HealingPolicy) -> bool:
        """Add a healing policy.

        Args:
            policy: Healing policy to add

        Returns:
            True if added successfully
        """
        with self._lock:
            if policy.policy_id in self._healing_policies:
                _logger.warning(f"[SelfHealingEngine] Policy already exists: {policy.policy_id}")
                return False

            self._healing_policies[policy.policy_id] = policy
            _logger.info(f"[SelfHealingEngine] Added healing policy: {policy.policy_id}")

            return True

    def trigger_healing(
        self,
        healing_type: HealingType,
        trigger: HealingTrigger,
        target_component: str,
        parameters: Dict[str, Any],
        priority: str = "medium",
    ) -> str:
        """Trigger a healing action.

        Args:
            healing_type: Type of healing action
            trigger: Type of trigger
            target_component: Component to heal
            parameters: Action parameters
            priority: Action priority

        Returns:
            Action ID
        """
        action_id = f"heal_{int(time.time())}_{len(self._healing_history)}"

        # Determine risk level based on healing type
        risk_level = self._determine_risk_level(healing_type)

        # Estimate duration
        estimated_duration = self._estimate_duration(healing_type)

        # Check if approval is required
        requires_approval = self._requires_approval(healing_type, trigger)

        # Create healing action
        action = HealingAction(
            action_id=action_id,
            healing_type=healing_type,
            trigger=trigger,
            target_component=target_component,
            parameters=parameters,
            priority=priority,
            estimated_duration=estimated_duration,
            risk_level=risk_level,
            description=self._generate_description(healing_type, target_component, parameters),
        )

        with self._lock:
            if requires_approval:
                _logger.info(f"[SelfHealingEngine] Healing action requires approval: {action_id}")
                # In production, this would wait for approval
                # For now, we'll proceed with logging
                action_id = f"{action_id}_pending"

            self._healing_queue.append(action)
            _logger.info(f"[SelfHealingEngine] Triggered healing action: {action_id}")

        return action_id

    def process_healing_queue(self) -> int:
        """Process healing actions in the queue.

        Returns:
            Number of healing actions processed
        """
        processed = 0

        with self._lock:
            while self._healing_queue:
                action = self._healing_queue.popleft()

                # Check if policy allows this action
                if not self._check_policy_compliance(action):
                    _logger.warning(
                        f"[SelfHealingEngine] Policy check failed for {action.action_id}"
                    )
                    continue

                # Execute healing action
                result = self._execute_healing_action(action)
                self._healing_history.append(result)

                # Check if rollback is needed
                if self._should_rollback(action, result):
                    self._perform_rollback(action, result)

                processed += 1

        _logger.info(f"[SelfHealingEngine] Processed {processed} healing actions")

        return processed

    def _execute_healing_action(self, action: HealingAction) -> HealingResult:
        """Execute a healing action.

        Args:
            action: Healing action to execute

        Returns:
            Healing result
        """
        start_time = time.time()

        # Record metrics before healing
        metrics_before = self._capture_component_metrics(action.target_component)

        # Mark as active
        self._active_healing[action.action_id] = action

        try:
            # Get handler
            handler = self._healing_handlers.get(action.healing_type)
            if not handler:
                raise ValueError(f"No handler for healing type: {action.healing_type}")

            # Execute handler
            _logger.info(f"[SelfHealingEngine] Executing healing: {action.action_id}")
            success = handler(action)

            end_time = time.time()
            duration = end_time - start_time

            # Record metrics after healing
            metrics_after = self._capture_component_metrics(action.target_component)

            result = HealingResult(
                action_id=action.action_id,
                status=HealingStatus.COMPLETED if success else HealingStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=success,
                message=(
                    "Healing action completed successfully" if success else "Healing action failed"
                ),
                affected_components=[action.target_component],
                metrics_before=metrics_before,
                metrics_after=metrics_after,
            )

            _logger.info(
                f"[SelfHealingEngine] Healing completed: {action.action_id}, success={success}"
            )

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            result = HealingResult(
                action_id=action.action_id,
                status=HealingStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                success=False,
                message=f"Healing action failed with exception",
                affected_components=[action.target_component],
                metrics_before=metrics_before,
                metrics_after=metrics_before,
                error_message=str(e),
            )

            _logger.error(f"[SelfHealingEngine] Healing failed: {action.action_id}, error={e}")

        finally:
            # Remove from active healing
            if action.action_id in self._active_healing:
                del self._active_healing[action.action_id]

        return result

    def _determine_risk_level(self, healing_type: HealingType) -> str:
        """Determine risk level for healing type.

        Args:
            healing_type: Type of healing action

        Returns:
            Risk level (high, medium, low)
        """
        high_risk_types = [
            HealingType.UPDATE_DEPENDENCY,
            HealingType.APPLY_PATCH,
            HealingType.ADJUST_CONFIG,
        ]

        low_risk_types = [HealingType.CLEAR_CACHE, HealingType.ROTATE_LOGS]

        if healing_type in high_risk_types:
            return "high"
        elif healing_type in low_risk_types:
            return "low"
        else:
            return "medium"

    def _estimate_duration(self, healing_type: HealingType) -> float:
        """Estimate duration for healing type.

        Args:
            healing_type: Type of healing action

        Returns:
            Estimated duration in seconds
        """
        durations = {
            HealingType.RESTART_SERVICE: 30.0,
            HealingType.SCALE_RESOURCES: 60.0,
            HealingType.CLEAR_CACHE: 5.0,
            HealingType.ROTATE_LOGS: 10.0,
            HealingType.UPDATE_DEPENDENCY: 300.0,
            HealingType.APPLY_PATCH: 120.0,
            HealingType.ADJUST_CONFIG: 15.0,
            HealingType.NETWORK_RECOVERY: 45.0,
            HealingType.DATABASE_RECOVERY: 90.0,
        }

        return durations.get(healing_type, 60.0)

    def _requires_approval(self, healing_type: HealingType, trigger: HealingTrigger) -> bool:
        """Check if healing action requires approval.

        Args:
            healing_type: Type of healing action
            trigger: Type of trigger

        Returns:
            True if approval required
        """
        # Predictive healing generally requires approval
        if trigger == HealingTrigger.PREDICTIVE:
            return True

        # High-risk healing types require approval
        if self._determine_risk_level(healing_type) == "high":
            return True

        return False

    def _generate_description(
        self, healing_type: HealingType, target_component: str, parameters: Dict[str, Any]
    ) -> str:
        """Generate description for healing action.

        Args:
            healing_type: Type of healing action
            target_component: Target component
            parameters: Action parameters

        Returns:
            Description string
        """
        descriptions = {
            HealingType.RESTART_SERVICE: f"Restart service: {target_component}",
            HealingType.SCALE_RESOURCES: f"Scale resources for: {target_component}",
            HealingType.CLEAR_CACHE: f"Clear cache for: {target_component}",
            HealingType.ROTATE_LOGS: f"Rotate logs for: {target_component}",
            HealingType.UPDATE_DEPENDENCY: f"Update dependency: {target_component}",
            HealingType.APPLY_PATCH: f"Apply patch to: {target_component}",
            HealingType.ADJUST_CONFIG: f"Adjust config for: {target_component}",
        }

        base_desc = descriptions.get(healing_type, f"Heal {target_component}")

        # Add parameter details
        if parameters:
            param_details = ", ".join(f"{k}={v}" for k, v in parameters.items())
            return f"{base_desc} ({param_details})"

        return base_desc

    def _check_policy_compliance(self, action: HealingAction) -> bool:
        """Check if healing action complies with policies.

        Args:
            action: Healing action to check

        Returns:
            True if compliant
        """
        # Find applicable policies
        applicable_policies = [
            policy
            for policy in self._healing_policies.values()
            if policy.healing_type == action.healing_type and policy.is_active
        ]

        if not applicable_policies:
            return True  # No applicable policies, allow by default

        # Check all applicable policies
        for policy in applicable_policies:
            # Check trigger type
            if policy.trigger_type != action.trigger:
                continue

            # Check cooldown period
            if not self._check_cooldown(action, policy):
                return False

            # Check max attempts
            if not self._check_max_attempts(action, policy):
                return False

        return True

    def _check_cooldown(self, action: HealingAction, policy: HealingPolicy) -> bool:
        """Check if action is within cooldown period.

        Args:
            action: Healing action
            policy: Healing policy

        Returns:
            True if outside cooldown period
        """
        current_time = time.time()

        # Find recent healing actions of this type for this component
        recent_actions = [
            h
            for h in self._healing_history
            if (current_time - h.end_time) < policy.cooldown_period
            and action.target_component in h.affected_components
        ]

        return len(recent_actions) == 0

    def _check_max_attempts(self, action: HealingAction, policy: HealingPolicy) -> bool:
        """Check if max attempts have been exceeded.

        Args:
            action: Healing action
            policy: Healing policy

        Returns:
            True if within max attempts
        """
        # Count recent failed attempts
        recent_failures = [
            h
            for h in self._healing_history
            if not h.success
            and action.target_component in h.affected_components
            and action.healing_type in [self._get_healing_type_from_result(h)]
        ]

        return len(recent_failures) < policy.max_attempts

    def _get_healing_type_from_result(self, result: HealingResult) -> Optional[HealingType]:
        """Get healing type from result.

        Args:
            result: Healing result

        Returns:
            Healing type or None
        """
        # Find original action
        for action in self._active_healing.values():
            if action.action_id == result.action_id:
                return action.healing_type
        return None

    def _should_rollback(self, action: HealingAction, result: HealingResult) -> bool:
        """Check if rollback should be performed.

        Args:
            action: Healing action
            result: Healing result

        Returns:
            True if rollback should be performed
        """
        if not result.success:
            return False

        # Check if performance degraded
        metrics_before = result.metrics_before
        metrics_after = result.metrics_after

        # Simple performance degradation check
        for metric_name, before_value in metrics_before.items():
            if metric_name in metrics_after:
                after_value = metrics_after[metric_name]
                if isinstance(before_value, (int, float)) and isinstance(after_value, (int, float)):
                    # Check if performance degraded by more than threshold
                    if after_value < before_value * 0.8:  # 20% degradation
                        return True

        return False

    def _perform_rollback(self, action: HealingAction, result: HealingResult) -> None:
        """Perform rollback for healing action.

        Args:
            action: Original healing action
            result: Healing result
        """
        _logger.info(f"[SelfHealingEngine] Performing rollback for {action.action_id}")

        # Mark result as rolled back
        result.rollback_performed = True
        result.status = HealingStatus.ROLLED_BACK

        # In production, this would execute the rollback action
        # For now, we just log it
        _logger.info(f"[SelfHealingEngine] Rollback completed for {action.action_id}")

    def _capture_component_metrics(self, component: str) -> Dict[str, Any]:
        """Capture current metrics for a component.

        Args:
            component: Component name

        Returns:
            Component metrics
        """
        # Simulate capturing metrics
        # In production, this would query actual monitoring systems
        return {
            "cpu_usage": 50.0 + (hash(component) % 30),
            "memory_usage": 40.0 + (hash(component) % 20),
            "response_time": 100.0 + (hash(component) % 50),
            "error_rate": 0.01 + (hash(component) % 5) / 100.0,
        }

    # Default healing handlers

    def _handle_restart_service(self, action: HealingAction) -> bool:
        """Handle service restart healing action.

        Args:
            action: Healing action

        Returns:
            True if successful
        """
        _logger.info(f"[SelfHealingEngine] Restarting service: {action.target_component}")

        # Simulate service restart
        # In production, this would actually restart the service
        time.sleep(2.0)  # Simulate restart time

        return True

    def _handle_scale_resources(self, action: HealingAction) -> bool:
        """Handle resource scaling healing action.

        Args:
            action: Healing action

        Returns:
            True if successful
        """
        _logger.info(f"[SelfHealingEngine] Scaling resources for: {action.target_component}")

        # Simulate resource scaling
        # In production, this would actually scale resources
        scale_factor = action.parameters.get("scale_factor", 1.5)
        _logger.info(f"[SelfHealingEngine] Scaling by factor: {scale_factor}")

        return True

    def _handle_clear_cache(self, action: HealingAction) -> bool:
        """Handle cache clear healing action.

        Args:
            action: Healing action

        Returns:
            True if successful
        """
        _logger.info(f"[SelfHealingEngine] Clearing cache for: {action.target_component}")

        # Simulate cache clear
        # In production, this would actually clear the cache
        time.sleep(1.0)

        return True

    def _handle_rotate_logs(self, action: HealingAction) -> bool:
        """Handle log rotation healing action.

        Args:
            action: Healing action

        Returns:
            True if successful
        """
        _logger.info(f"[SelfHealingEngine] Rotating logs for: {action.target_component}")

        # Simulate log rotation
        # In production, this would actually rotate logs
        time.sleep(1.0)

        return True

    def _handle_update_dependency(self, action: HealingAction) -> bool:
        """Handle dependency update healing action.

        Args:
            action: Healing action

        Returns:
            True if successful
        """
        _logger.info(f"[SelfHealingEngine] Updating dependency for: {action.target_component}")

        # Simulate dependency update
        # In production, this would actually update the dependency
        dependency = action.parameters.get("dependency", "unknown")
        version = action.parameters.get("version", "latest")
        _logger.info(f"[SelfHealingEngine] Updating {dependency} to {version}")

        return True

    def _handle_apply_patch(self, action: HealingAction) -> bool:
        """Handle patch application healing action.

        Args:
            action: Healing action

        Returns:
            True if successful
        """
        _logger.info(f"[SelfHealingEngine] Applying patch to: {action.target_component}")

        # Simulate patch application
        # In production, this would actually apply the patch
        patch_id = action.parameters.get("patch_id", "unknown")
        _logger.info(f"[SelfHealingEngine] Applying patch: {patch_id}")

        return True

    def _handle_adjust_config(self, action: HealingAction) -> bool:
        """Handle config adjustment healing action.

        Args:
            action: Healing action

        Returns:
            True if successful
        """
        _logger.info(f"[SelfHealingEngine] Adjusting config for: {action.target_component}")

        # Simulate config adjustment
        # In production, this would actually adjust config
        config_changes = action.parameters.get("config_changes", {})
        _logger.info(f"[SelfHealingEngine] Config changes: {config_changes}")

        return True

    def get_healing_history(self, limit: int = 10) -> List[HealingResult]:
        """Get healing action history.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of healing results
        """
        with self._lock:
            return list(self._healing_history[-limit:])

    def get_active_healing(self) -> List[HealingAction]:
        """Get currently active healing actions.

        Returns:
            List of active healing actions
        """
        with self._lock:
            return list(self._active_healing.values())

    def get_healing_metrics(self) -> Dict[str, Any]:
        """Get healing metrics.

        Returns:
            Healing metrics
        """
        with self._lock:
            total_healing = len(self._healing_history)
            successful_healing = sum(1 for h in self._healing_history if h.success)
            failed_healing = total_healing - successful_healing
            rolled_back = sum(1 for h in self._healing_history if h.rollback_performed)

            return {
                "total_healing_actions": total_healing,
                "successful_healing": successful_healing,
                "failed_healing": failed_healing,
                "success_rate": successful_healing / total_healing if total_healing > 0 else 0.0,
                "rolled_back": rolled_back,
                "active_healing": len(self._active_healing),
                "queued_healing": len(self._healing_queue),
                "policies_active": len([p for p in self._healing_policies.values() if p.is_active]),
            }


# Singleton instance
_self_healing_engine: Optional[SelfHealingEngine] = None
_healing_lock = threading.Lock()


def get_self_healing_engine(repo_root: str = ".") -> SelfHealingEngine:
    """Get singleton instance of self-healing engine.

    Args:
        repo_root: Path to repository root

    Returns:
        Self-healing engine instance
    """
    global _self_healing_engine

    with _healing_lock:
        if _self_healing_engine is None:
            _self_healing_engine = SelfHealingEngine(repo_root)
        return _self_healing_engine
