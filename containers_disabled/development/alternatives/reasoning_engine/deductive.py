from __future__ import annotations

from dataclasses import dataclass

from core.ontology.base import CognitiveObject, ObjectKind


@dataclass(frozen=True, slots=True)
class Rule:
    rule_id: str = ""
    antecedent: tuple[str, ...] = ()
    consequent: str = ""
    confidence: float = 1.0
    exceptions: tuple[str, ...] = ()

    def applies(self, active_conditions: set[str]) -> bool:
        return all(c in active_conditions for c in self.antecedent)


@dataclass(frozen=True, slots=True)
class DeductiveConclusion(CognitiveObject):
    rule_id: str = ""
    conclusion: str = ""

    def __init__(self, *, object_id: str, ts_ns: int, rule_id: str, conclusion: str, **kwargs):
        object.__setattr__(self, "object_id", object_id)
        object.__setattr__(self, "object_type", ObjectKind.BELIEF)
        object.__setattr__(self, "ts_ns", ts_ns)
        object.__setattr__(self, "rule_id", rule_id)
        object.__setattr__(self, "conclusion", conclusion)
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)


class DeductiveEngine:
    def __init__(self) -> None:
        self._rules: dict[str, Rule] = {}

    def register_rule(self, rule: Rule) -> None:
        self._rules[rule.rule_id] = rule

    def deduce(self, active_conditions: set[str]) -> tuple[DeductiveConclusion, ...]:
        conclusions = []
        for rule in self._rules.values():
            if rule.applies(active_conditions) and not any(
                e in active_conditions for e in rule.exceptions
            ):
                conclusions.append(
                    DeductiveConclusion(
                        object_id=f"DEDUCE-{rule.rule_id}",
                        ts_ns=0,
                        rule_id=rule.rule_id,
                        conclusion=rule.consequent,
                        contributor_chain=("deductive_engine",),
                    )
                )
        return tuple(conclusions)
