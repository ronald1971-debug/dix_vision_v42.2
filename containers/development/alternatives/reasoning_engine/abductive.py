from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from reasoning_engine.evidence_graph import EvidenceGraph


@dataclass(frozen=True, slots=True)
class Hypothesis:
    hypothesis_id: str
    description: str
    prior_probability: float = 0.5
    required_evidence: tuple[str, ...] = ()
    supporting_evidence: tuple[str, ...] = ()

    def explanatory_power(self, evidence_graph: EvidenceGraph) -> float:
        supporting_nodes = [
            evidence_graph.get_node(eid)
            for eid in self.supporting_evidence
            if evidence_graph.get_node(eid) is not None
        ]
        if not supporting_nodes:
            return self.prior_probability
        avg_confidence = sum(n.confidence for n in supporting_nodes) / len(supporting_nodes)
        coverage = len(supporting_nodes) / max(len(self.required_evidence), 1)
        return avg_confidence * coverage


@dataclass
class AbductiveResult:
    best_hypothesis: Hypothesis | None = None
    all_hypotheses: tuple[Hypothesis, ...] = ()
    confidence: float = 0.0
    reasoning_trace: tuple[str, ...] = ()
    alternative_explanations: tuple[Hypothesis, ...] = ()


class AbductiveReasoner:
    def __init__(self, evidence_graph: EvidenceGraph | None = None) -> None:
        self._graph = evidence_graph or EvidenceGraph()
        self._hypotheses: dict[str, Hypothesis] = {}

    def register_hypothesis(self, hypothesis: Hypothesis) -> None:
        self._hypotheses[hypothesis.hypothesis_id] = hypothesis

    def reason(self, observation: str, candidate_ids: Sequence[str]) -> AbductiveResult:
        hypotheses = tuple(
            self._hypotheses[hid] for hid in candidate_ids if hid in self._hypotheses
        )
        if not hypotheses:
            return AbductiveResult(
                reasoning_trace=(f"No hypotheses registered for observation: {observation}",)
            )

        scored = [(h, h.explanatory_power(self._graph)) for h in hypotheses]
        scored.sort(key=lambda x: x[1], reverse=True)
        best_hypothesis, best_score = scored[0]
        alternatives = tuple(h for h, _ in scored[1:4])
        trace = (
            f"Observation: {observation}",
            f"Candidates evaluated: {len(hypotheses)}",
            f"Best hypothesis: {best_hypothesis.hypothesis_id} (score: {best_score:.3f})",
        )
        return AbductiveResult(
            best_hypothesis=best_hypothesis,
            all_hypotheses=hypotheses,
            confidence=best_score,
            reasoning_trace=trace,
            alternative_explanations=alternatives,
        )
