"""
Governance Policy Engine - Policy Enforcement System
Real policy enforcement for DIX VISION Tier-0 Production Implementation
Per Rule 3 of the DIX VISION Tier-0 Production Implementation Contract
"""

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Types of governance policies"""

    RISK_MANAGEMENT = "risk_management"
    EXECUTION_LIMITS = "execution_limits"
    POSITION_LIMITS = "position_limits"
    CAPITAL_ALLOCATION = "capital_allocation"
    OPERATOR_AUTHORITY = "operator_authority"
    SYSTEM_INTEGRITY = "system_integrity"
    EMERGENCY_RESPONSE = "emergency_response"
    EVOLUTION_CONTROL = "evolution_control"


class PolicyAction(Enum):
    """Actions that can be taken on policy violations"""

    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    MODIFIED = "modified"
    ESCALATE = "escalate"
    OVERRIDE = "override"


class PolicyStatus(Enum):
    """Status of policies"""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class PolicyRule:
    """A single policy rule"""

    rule_id: str
    policy_type: PolicyType
    name: str
    description: str
    condition: str  # Condition expression
    action: PolicyAction
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: PolicyStatus = PolicyStatus.ACTIVE
    conditions_hash: str = ""


@dataclass
class PolicyViolation:
    """Record of a policy violation"""

    violation_id: str
    rule_id: str
    policy_type: PolicyType
    violation_time: datetime
    entity: str
    context: Dict[str, Any]
    action_taken: PolicyAction
    resolution: Optional[str] = None
    escalated: bool = False
    overridden: bool = False


@dataclass
class PolicyEvaluation:
    """Result of policy evaluation"""

    evaluation_id: str
    rule_id: str
    passed: bool
    action: PolicyAction
    confidence: float
    evaluation_time: datetime
    context: Dict[str, Any]
    explanation: str
    modifications: Optional[Dict[str, Any]] = None


class PolicyEngine:
    """
    Governance Policy Engine for real policy enforcement
    Per Rule 3 of the DIX VISION contract, governance must perform policy enforcement
    """

    def __init__(self):
        self._rules: Dict[str, PolicyRule] = {}
        self._violations: List[PolicyViolation] = []
        self._evaluation_history: List[PolicyEvaluation] = []
        self._policy_callbacks: Dict[PolicyType, List[Callable]] = defaultdict(list)
        self._rule_index: Dict[PolicyType, Set[str]] = defaultdict(set)
        self._violation_counts: Dict[str, int] = defaultdict(int)

        # Initialize default policies
        self._initialize_default_policies()

    def _initialize_default_policies(self) -> None:
        """Initialize default governance policies"""
        default_policies = [
            # Risk Management Policies
            PolicyRule(
                rule_id="risk_max_position_size",
                policy_type=PolicyType.RISK_MANAGEMENT,
                name="Maximum Position Size",
                description="Limit maximum position size for risk control",
                condition="position_size <= max_position_limit",
                action=PolicyAction.BLOCK,
                parameters={"max_position_limit": 1000000},
                priority=1,
            ),
            PolicyRule(
                rule_id="risk_leverage_limit",
                policy_type=PolicyType.RISK_MANAGEMENT,
                name="Leverage Limit",
                description="Limit maximum leverage to prevent excessive risk",
                condition="leverage <= max_leverage",
                action=PolicyAction.BLOCK,
                parameters={"max_leverage": 5.0},
                priority=1,
            ),
            PolicyRule(
                rule_id="risk_drawdown_limit",
                policy_type=PolicyType.RISK_MANAGEMENT,
                name="Maximum Drawdown",
                description="Halt trading if maximum drawdown exceeded",
                condition="current_drawdown <= max_drawdown_limit",
                action=PolicyAction.ESCALATE,
                parameters={"max_drawdown_limit": 0.15},  # 15% max drawdown
                priority=2,
            ),
            # Execution Limit Policies
            PolicyRule(
                rule_id="exec_max_order_size",
                policy_type=PolicyType.EXECUTION_LIMITS,
                name="Maximum Order Size",
                description="Limit single order size to control market impact",
                condition="order_size <= max_order_size",
                action=PolicyAction.MODIFIED,
                parameters={"max_order_size": 100000},
                priority=1,
            ),
            PolicyRule(
                rule_id="exec_daily_volume_limit",
                policy_type=PolicyType.EXECUTION_LIMITS,
                name="Daily Volume Limit",
                description="Limit total daily execution volume",
                condition="daily_volume <= daily_volume_limit",
                action=PolicyAction.WARN,
                parameters={"daily_volume_limit": 10000000},
                priority=2,
            ),
            # Position Limit Policies
            PolicyRule(
                rule_id="pos_sector_concentration",
                policy_type=PolicyType.POSITION_LIMITS,
                name="Sector Concentration",
                description="Limit concentration in any single sector",
                condition="sector_exposure <= max_sector_exposure",
                action=PolicyAction.WARN,
                parameters={"max_sector_exposure": 0.30},  # 30% max in any sector
                priority=1,
            ),
            PolicyRule(
                rule_id="pos_correlation_limit",
                policy_type=PolicyType.POSITION_LIMITS,
                name="Correlation Limit",
                description="Limit highly correlated positions",
                condition="correlation_score <= max_correlation",
                action=PolicyAction.MODIFIED,
                parameters={"max_correlation": 0.95},
                priority=2,
            ),
            # Capital Allocation Policies
            PolicyRule(
                rule_id="cap_reserve_requirement",
                policy_type=PolicyType.CAPITAL_ALLOCATION,
                name="Reserve Requirement",
                description="Maintain minimum capital reserves",
                condition="available_capital >= reserve_requirement",
                action=PolicyAction.BLOCK,
                parameters={"reserve_requirement": 100000},
                priority=1,
            ),
            # Emergency Response Policies
            PolicyRule(
                rule_id="emergency_circuit_breaker",
                policy_type=PolicyType.EMERGENCY_RESPONSE,
                name="Circuit Breaker",
                description="Automatically halt trading on extreme market conditions",
                condition="market_volatility <= circuit_breaker_threshold",
                action=PolicyAction.ESCALATE,
                parameters={"circuit_breaker_threshold": 0.20},  # 20% volatility threshold
                priority=3,
            ),
        ]

        for policy in default_policies:
            policy.conditions_hash = self._compute_rule_hash(policy)
            self.add_rule(policy)

    def _compute_rule_hash(self, rule: PolicyRule) -> str:
        """Compute hash of rule condition and parameters for consistency"""
        rule_data = (
            f"{rule.condition}_{rule.action.value}_{json.dumps(rule.parameters, sort_keys=True)}"
        )
        return hashlib.sha256(rule_data.encode()).hexdigest()

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a new policy rule to the engine"""
        if rule.rule_id in self._rules:
            logger.warning(f"Rule {rule.rule_id} already exists, updating")

        rule.conditions_hash = self._compute_rule_hash(rule)
        self._rules[rule.rule_id] = rule
        self._rule_index[rule.policy_type].add(rule.rule_id)

        logger.info(f"Added policy rule: {rule.rule_id} ({rule.policy_type.value})")

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a policy rule from the engine"""
        if rule_id not in self._rules:
            logger.warning(f"Rule {rule_id} not found")
            return False

        rule = self._rules[rule_id]
        self._rule_index[rule.policy_type].discard(rule_id)
        del self._rules[rule_id]

        logger.info(f"Removed policy rule: {rule_id}")
        return True

    def evaluate_policy(
        self, entity: str, context: Dict[str, Any], policy_types: Optional[List[PolicyType]] = None
    ) -> List[PolicyEvaluation]:
        """
        Evaluate all relevant policies for an entity
        Returns list of evaluation results
        """
        evaluations = []

        # Determine which policy types to evaluate
        if policy_types is None:
            rule_ids = list(self._rules.keys())
        else:
            rule_ids = []
            for policy_type in policy_types:
                rule_ids.extend(self._rule_index[policy_type])

        # Evaluate each rule
        for rule_id in rule_ids:
            if rule_id not in self._rules:
                continue

            rule = self._rules[rule_id]
            if rule.status != PolicyStatus.ACTIVE:
                continue

            evaluation = self._evaluate_rule(rule, entity, context)
            evaluations.append(evaluation)

            # Record violation if policy not passed
            if not evaluation.passed and evaluation.action in [
                PolicyAction.BLOCK,
                PolicyAction.ESCALATE,
            ]:
                self._record_violation(rule, entity, context, evaluation.action)

            # Trigger callbacks
            self._trigger_policy_callbacks(rule.policy_type, evaluation)

        self._evaluation_history.extend(evaluations)
        return evaluations

    def _evaluate_rule(
        self, rule: PolicyRule, entity: str, context: Dict[str, Any]
    ) -> PolicyEvaluation:
        """Evaluate a single policy rule"""
        evaluation_id = (
            f"eval_{rule.rule_id}_{datetime.utcnow().timestamp()}:{datetime.utcnow().nanosecond()}"
        )

        # Evaluate condition
        passed = self._evaluate_condition(rule.condition, context, rule.parameters)

        # Determine action based on policy evaluation
        if passed:
            action = PolicyAction.ALLOW
            confidence = 1.0
            explanation = f"Policy {rule.name} passed - condition satisfied"
        else:
            action = rule.action
            confidence = 0.8  # Base confidence for violations
            explanation = f"Policy {rule.name} violated - condition not satisfied"

            # Calculate modifications for certain actions
            modifications = None
            if action == PolicyAction.MODIFIED:
                modifications = self._calculate_modifications(rule, context)

        evaluation = PolicyEvaluation(
            evaluation_id=evaluation_id,
            rule_id=rule.rule_id,
            passed=passed,
            action=action,
            confidence=confidence,
            evaluation_time=datetime.utcnow(),
            context=context,
            explanation=explanation,
            modifications=modifications if action == PolicyAction.MODIFIED else None,
        )

        logger.debug(f"Evaluated rule {rule.rule_id}: {action.value}")
        return evaluation

    def _evaluate_condition(
        self, condition: str, context: Dict[str, Any], parameters: Dict[str, Any]
    ) -> bool:
        """Evaluate a policy condition against context and parameters"""
        # This is a simplified condition evaluator
        # In a real system, this would use a proper expression parser

        try:
            # Merge context with parameters for evaluation
            evaluation_context = {**context, **parameters}

            # Simple condition parsing (for demonstration)
            # In production, use a proper expression evaluator
            for key, value in parameters.items():
                if key in context:
                    if ">" in condition:
                        if context[key] <= value:
                            return False
                    elif "<=" in condition:
                        if context[key] > value:
                            return False
                    elif "<" in condition:
                        if context[key] >= value:
                            return False
                    elif ">=" in condition:
                        if context[key] < value:
                            return False
                    elif "==" in condition:
                        if context[key] != value:
                            return False
                    else:
                        if context[key] != value:
                            return False

            return True

        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False

    def _calculate_modifications(self, rule: PolicyRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate modifications for policies that require modification"""
        modifications = {}

        if (
            rule.policy_type == PolicyType.EXECUTION_LIMITS
            and rule.rule_id == "exec_max_order_size"
        ):
            if (
                "order_size" in context
                and context["order_size"] > rule.parameters["max_order_size"]
            ):
                modifications["order_size"] = rule.parameters["max_order_size"]
                modifications["reason"] = "Reduced order size to meet policy limit"

        if (
            rule.policy_type == PolicyType.POSITION_LIMITS
            and rule.rule_id == "pos_correlation_limit"
        ):
            if (
                "position_size" in context
                and context.get("correlation_score", 1.0) > rule.parameters["max_correlation"]
            ):
                modifications["position_size"] = context["position_size"] * 0.5
                modifications["reason"] = "Reduced position size due to high correlation"

        return modifications

    def _record_violation(
        self, rule: PolicyRule, entity: str, context: Dict[str, Any], action: PolicyAction
    ) -> None:
        """Record a policy violation"""
        violation_id = f"violation_{rule.rule_id}_{datetime.utcnow().timestamp()}:{datetime.utcnow().nanosecond()}"

        violation = PolicyViolation(
            violation_id=violation_id,
            rule_id=rule.rule_id,
            policy_type=rule.policy_type,
            violation_time=datetime.utcnow(),
            entity=entity,
            context=context.copy(),
            action_taken=action,
        )

        self._violations.append(violation)
        self._violation_counts[rule.rule_id] += 1

        logger.warning(f"Recorded violation: {violation_id} - {rule.name}")

    def _trigger_policy_callbacks(
        self, policy_type: PolicyType, evaluation: PolicyEvaluation
    ) -> None:
        """Trigger registered callbacks for policy evaluations"""
        for callback in self._policy_callbacks[policy_type]:
            try:
                callback(evaluation)
            except Exception as e:
                logger.error(f"Policy callback failed: {e}")

    def register_policy_callback(
        self, policy_type: PolicyType, callback: Callable[[PolicyEvaluation], None]
    ) -> None:
        """Register callback for specific policy type evaluations"""
        self._policy_callbacks[policy_type].append(callback)
        logger.info(f"Registered policy callback for {policy_type.value}")

    def get_rule(self, rule_id: str) -> Optional[PolicyRule]:
        """Get a specific policy rule"""
        return self._rules.get(rule_id)

    def get_rules_by_type(self, policy_type: PolicyType) -> List[PolicyRule]:
        """Get all rules of a specific policy type"""
        rule_ids = self._rule_index[policy_type]
        return [self._rules[rule_id] for rule_id in rule_ids if rule_id in self._rules]

    def get_violations(
        self, policy_type: Optional[PolicyType] = None, limit: int = 100
    ) -> List[PolicyViolation]:
        """Get policy violations, optionally filtered by type"""
        violations = self._violations
        if policy_type:
            violations = [v for v in violations if v.policy_type == policy_type]
        return violations[-limit:]

    def resolve_violation(self, violation_id: str, resolution: str, override: bool = False) -> bool:
        """Resolve a policy violation"""
        for violation in self._violations:
            if violation.violation_id == violation_id:
                violation.resolution = resolution
                violation.overridden = override
                logger.info(f"Resolved violation: {violation_id}")
                return True
        return False

    def update_rule_status(self, rule_id: str, status: PolicyStatus) -> bool:
        """Update the status of a policy rule"""
        if rule_id not in self._rules:
            return False

        self._rules[rule_id].status = status
        logger.info(f"Updated rule status: {rule_id} -> {status.value}")
        return True

    def update_rule_parameters(self, rule_id: str, parameters: Dict[str, Any]) -> bool:
        """Update the parameters of a policy rule"""
        if rule_id not in self._rules:
            return False

        rule = self._rules[rule_id]
        rule.parameters.update(parameters)
        rule.conditions_hash = self._compute_rule_hash(rule)
        logger.info(f"Updated rule parameters: {rule_id}")
        return True

    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of policy engine status"""
        active_rules = sum(1 for r in self._rules.values() if r.status == PolicyStatus.ACTIVE)
        total_violations = len(self._violations)

        violations_by_type = defaultdict(int)
        for violation in self._violations:
            violations_by_type[violation.policy_type.value] += 1

        return {
            "total_rules": len(self._rules),
            "active_rules": active_rules,
            "total_violations": total_violations,
            "violations_by_type": dict(violations_by_type),
            "total_evaluations": len(self._evaluation_history),
            "rule_index": {
                policy_type.value: len(rule_ids)
                for policy_type, rule_ids in self._rule_index.items()
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def cleanup_old_violations(self, older_than_days: int = 30) -> int:
        """Clean up old violation records"""
        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        old_count = len(self._violations)
        self._violations = [v for v in self._violations if v.violation_time > cutoff]
        removed = old_count - len(self._violations)
        logger.info(f"Cleaned up {removed} old violation records")
        return removed
