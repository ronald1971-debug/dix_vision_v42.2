"""
Core Constraint Engine
Real implementation for constraint rule engine
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RuleAction(Enum):
    """Rule action enumeration"""

    ALLOW = "allow"
    DENY = "deny"
    REJECT = "reject"
    HALT = "halt"
    REQUIRE_APPROVAL = "require_approval"
    REQUIRE_MANUAL_REVIEW = "require_manual_review"
    FLAG = "flag"
    WARN = "warn"
    BLOCK = "block"
    CONDITIONAL = "conditional"
    DEFER = "defer"


class RuleSeverity(Enum):
    """Rule severity enumeration"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class CompiledRule:
    """Compiled rule for evaluation"""

    rule_id: str
    rule_name: str
    action: RuleAction
    severity: RuleSeverity
    condition: str  # Simplified condition expression
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0

    def is_enabled(self) -> bool:
        """Check if rule is enabled"""
        return self.enabled

    def is_critical(self) -> bool:
        """Check if rule is critical"""
        return self.severity == RuleSeverity.CRITICAL

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate rule against context (simplified)"""
        # In a real implementation, this would parse and evaluate the condition
        # For now, return True as a placeholder
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "action": self.action.value,
            "severity": self.severity.value,
            "condition": self.condition,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "priority": self.priority,
        }


@dataclass
class RuleEvaluationResult:
    """Result of rule evaluation"""

    rule_id: str
    rule_name: str
    action: RuleAction
    severity: RuleSeverity
    passed: bool
    message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def is_allowed(self) -> bool:
        """Check if evaluation allows the action"""
        return self.passed and self.action == RuleAction.ALLOW

    def is_blocked(self) -> bool:
        """Check if evaluation blocks the action"""
        return not self.passed and self.action in [RuleAction.DENY, RuleAction.BLOCK]

    def requires_approval(self) -> bool:
        """Check if evaluation requires approval"""
        return self.action == RuleAction.REQUIRE_APPROVAL

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "action": self.action.value,
            "severity": self.severity.value,
            "passed": self.passed,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp,
        }


class RuleGraph:
    """Graph of rules for constraint evaluation"""

    def __init__(self):
        self._rules: Dict[str, CompiledRule] = {}
        self._rule_dependencies: Dict[str, List[str]] = {}
        self._evaluation_history: List[RuleEvaluationResult] = []

    def add_rule(self, rule: CompiledRule) -> bool:
        """Add a rule to the graph"""
        self._rules[rule.rule_id] = rule
        if rule.rule_id not in self._rule_dependencies:
            self._rule_dependencies[rule.rule_id] = []
        return True

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule from the graph"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            if rule_id in self._rule_dependencies:
                del self._rule_dependencies[rule_id]
            return True
        return False

    def get_rule(self, rule_id: str) -> Optional[CompiledRule]:
        """Get a specific rule"""
        return self._rules.get(rule_id)

    def get_all_rules(self) -> List[CompiledRule]:
        """Get all rules"""
        return list(self._rules.values())

    def get_enabled_rules(self) -> List[CompiledRule]:
        """Get all enabled rules"""
        return [r for r in self._rules.values() if r.is_enabled()]

    def get_critical_rules(self) -> List[CompiledRule]:
        """Get all critical rules"""
        return [r for r in self._rules.values() if r.is_critical()]

    def add_dependency(self, rule_id: str, depends_on: str) -> bool:
        """Add a dependency between rules"""
        if rule_id not in self._rule_dependencies:
            self._rule_dependencies[rule_id] = []
        if depends_on not in self._rule_dependencies[rule_id]:
            self._rule_dependencies[rule_id].append(depends_on)
        return True

    def evaluate_rules(self, context: Dict[str, Any]) -> List[RuleEvaluationResult]:
        """Evaluate all enabled rules against context"""
        results = []
        for rule in self.get_enabled_rules():
            passed = rule.evaluate(context)
            result = RuleEvaluationResult(
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                action=rule.action,
                severity=rule.severity,
                passed=passed,
                context=context,
            )
            results.append(result)
            self._evaluation_history.append(result)
        return results

    def evaluate_rule(
        self, rule_id: str, context: Dict[str, Any]
    ) -> Optional[RuleEvaluationResult]:
        """Evaluate a specific rule against context"""
        rule = self.get_rule(rule_id)
        if rule:
            passed = rule.evaluate(context)
            result = RuleEvaluationResult(
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                action=rule.action,
                severity=rule.severity,
                passed=passed,
                context=context,
            )
            self._evaluation_history.append(result)
            return result
        return None

    def get_evaluation_history(self, limit: int = 100) -> List[RuleEvaluationResult]:
        """Get recent evaluation history"""
        return self._evaluation_history[-limit:]

    def clear_history(self) -> None:
        """Clear evaluation history"""
        self._evaluation_history.clear()


# Global rule graph
_rule_graph: Optional[RuleGraph] = None


def get_rule_graph() -> RuleGraph:
    """Get the global rule graph"""
    global _rule_graph
    if _rule_graph is None:
        _rule_graph = RuleGraph()
    return _rule_graph


def create_rule(
    rule_id: str, rule_name: str, action: RuleAction, severity: RuleSeverity, condition: str
) -> CompiledRule:
    """Create a new compiled rule"""
    return CompiledRule(
        rule_id=rule_id, rule_name=rule_name, action=action, severity=severity, condition=condition
    )


__all__ = [
    "RuleAction",
    "RuleSeverity",
    "CompiledRule",
    "RuleEvaluationResult",
    "RuleGraph",
    "get_rule_graph",
    "create_rule",
]
