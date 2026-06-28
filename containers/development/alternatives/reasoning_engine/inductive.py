from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from core.ontology.base import CognitiveObject


@dataclass(frozen=True, slots=True)
class ObservedInstance:
    instance_id: str
    features: tuple[str, ...]
    outcome: str
    timestamp_ns: int
    confidence: float


@dataclass(frozen=True, slots=True)
class InductivePattern(CognitiveObject):
    pattern_name: str = ""
    features: tuple[str, ...] = ()
    predicted_outcome: str = ""
    instance_count: int = 0
    pattern_confidence: float = 0.0
    counterexamples: tuple[ObservedInstance, ...] = ()
    domain: str = "market"

    def is_robust(self, min_instances: int = 10, min_confidence: float = 0.7) -> bool:
        return self.instance_count >= min_instances and self.pattern_confidence >= min_confidence


class InductiveEngine:
    def __init__(self) -> None:
        self._patterns: dict[str, InductivePattern] = {}

    def induce(
        self, observations: Sequence[ObservedInstance], min_confidence: float = 0.6
    ) -> InductivePattern | None:
        if not observations:
            return None
        feature_counts: dict[str, dict[str, int]] = {}
        outcome_counts: dict[str, int] = {}
        for obs in observations:
            for feat in obs.features:
                feature_counts.setdefault(feat, {}).setdefault(obs.outcome, 0)
                feature_counts[feat][obs.outcome] += 1
            outcome_counts[obs.outcome] = outcome_counts.get(obs.outcome, 0) + 1
        dominant_outcome = max(outcome_counts, key=lambda k: outcome_counts[k])
        dominant_features = [
            feat
            for feat, outcomes in feature_counts.items()
            if outcomes.get(dominant_outcome, 0) / sum(outcomes.values()) >= min_confidence
        ]
        confidence = outcome_counts[dominant_outcome] / len(observations)
        return InductivePattern(
            object_id=f"PATTERN-{dominant_outcome}-{abs(hash(tuple(dominant_features))):08x}",
            ts_ns=0,
            pattern_name=f"Induced: {dominant_outcome}",
            features=tuple(sorted(dominant_features)),
            predicted_outcome=dominant_outcome,
            instance_count=len(observations),
            pattern_confidence=confidence,
            contributor_chain=("inductive_engine",),
        )
