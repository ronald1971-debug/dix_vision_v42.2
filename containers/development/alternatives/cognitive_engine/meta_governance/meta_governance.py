"""Meta-Governance - observability of governance itself."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from cognitive_engine.meta_governance.rules import GovernanceRule


@dataclass
class GovernanceQuestion:
    """Questions about governance effectiveness."""

    question_id: str = field(default_factory=lambda: f"governance_{time.time_ns()}")
    question: str = ""
    rule_id: str = ""
    asked_at: int = field(default_factory=lambda: time.time_ns())
    answered: bool = False


class MetaGovernance:
    """Governance becomes observable, not untouchable.

    Questions to ask:
    - Are approval rules too strict?
    - Too loose?
    - Blocking useful evolution?
    - Allowing harmful evolution?
    """

    def __init__(self) -> None:
        self._rules: dict[str, GovernanceRule] = {}
        self._questions: list[GovernanceQuestion] = []
        self._decisions: list[dict[str, Any]] = []

    def register_rule(self, rule: GovernanceRule) -> None:
        """Register a rule for monitoring."""
        self._rules[rule.rule_id] = rule

    def get_rule(self, rule_id: str) -> GovernanceRule | None:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def ask_question(self, question: str, rule_id: str = "") -> GovernanceQuestion:
        """Ask a governance question."""
        q = GovernanceQuestion(question=question, rule_id=rule_id)
        self._questions.append(q)
        return q

    def is_too_strict(self, rule_id: str, threshold: float = 0.9) -> bool:
        """Check if rule is being triggered too often (blocking evolution)."""
        rule = self._rules.get(rule_id)
        if rule and rule.times_triggered > 100:
            return rule.effectiveness() > threshold
        return False

    def is_too_lenient(self, rule_id: str, threshold: float = 0.1) -> bool:
        """Check if rule is not enforcing enough."""
        rule = self._rules.get(rule_id)
        if rule and rule.times_triggered > 50:
            return rule.effectiveness() < threshold
        return False

    def get_rule_report(self, rule_id: str) -> dict[str, Any]:
        """Get effectiveness report for a rule."""
        rule = self._rules.get(rule_id)
        if not rule:
            return {}

        return {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "times_triggered": rule.times_triggered,
            "times_bypassed": rule.times_bypassed,
            "effectiveness": rule.effectiveness(),
            "is_strict": self.is_too_strict(rule_id),
            "is_lenient": self.is_too_lenient(rule_id),
        }

    def suggest_adjustment(self, rule_id: str) -> str:
        """Suggest adjustment for a rule."""
        rule = self._rules.get(rule_id)
        if not rule:
            return ""

        if self.is_too_strict(rule_id):
            return f"Consider lowering threshold for {rule.name}"
        if self.is_too_lenient(rule_id):
            return f"Consider raising threshold for {rule.name}"
        return f"{rule.name} appears well-calibrated"

    def record_decision(self, rule_id: str, decision: dict[str, Any]) -> None:
        """Record a governance decision."""
        self._decisions.append(
            {"rule_id": rule_id, "decision": decision, "timestamp": time.time_ns()}
        )

    def get_questions(self, unanswered_only: bool = False) -> list[GovernanceQuestion]:
        """Get governance questions."""
        if unanswered_only:
            return [q for q in self._questions if not q.answered]
        return self._questions
