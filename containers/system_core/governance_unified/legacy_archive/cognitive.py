"""Cognitive Governance Domain.

Governs INDIRA's reasoning – ensures hypotheses are well-formed,
confidence thresholds are met, and cognitive pipelines follow protocol.
"""

from __future__ import annotations

from dataclasses import dataclass

from governance_unified.policy_rule import PolicyRule


@dataclass
class CognitiveGovernancePolicy:
    """Policies specific to the cognition layer."""

    min_hypothesis_confidence: float = 0.3
    max_active_hypotheses: int = 10
    require_evidence_for_belief: bool = True
    max_reasoning_time_seconds: float = 5.0

    def to_rules(self) -> list[PolicyRule]:
        return [
            PolicyRule(
                name="cognitive_min_confidence",
                domain="cognitive",
                description="Minimum confidence for hypothesis promotion",
                min_confidence=self.min_hypothesis_confidence,
            ),
            PolicyRule(
                name="cognitive_reasoning_budget",
                domain="cognitive",
                description="Maximum time allowed for reasoning cycles",
            ),
        ]
