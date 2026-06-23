"""Hypothesis Tracker - manages hypothesis lifecycle."""

from __future__ import annotations

from typing import Any

from cognitive_engine.hypothesis_engine.hypothesis import (
    Hypothesis,
    HypothesisResult,
    HypothesisStatus,
)


class HypothesisTracker:
    """Tracks and manages hypotheses through their lifecycle.

    Lifecycle:
        Proposed → Testing → Valid/Invalid → Learned From
    """

    def __init__(self) -> None:
        self._hypotheses: dict[str, Hypothesis] = {}
        self._by_domain: dict[str, list[str]] = {}

    def propose(
        self,
        statement: str,
        domain: str,
        evidence: str | tuple[str, ...] = (),
        metadata: dict[str, Any] | None = None,
    ) -> Hypothesis:
        """Propose a new hypothesis."""
        if isinstance(evidence, str):
            evidence = (evidence,)

        hyp = Hypothesis(
            statement=statement,
            domain=domain,
            evidence=evidence,
            metadata=metadata or {},
        )
        self._hypotheses[hyp.hypothesis_id] = hyp
        self._by_domain.setdefault(domain, []).append(hyp.hypothesis_id)
        return hyp

    def get(self, hypothesis_id: str) -> Hypothesis | None:
        """Get a hypothesis by ID."""
        return self._hypotheses.get(hypothesis_id)

    def get_by_domain(self, domain: str) -> list[Hypothesis]:
        """Get hypotheses for a domain."""
        ids = self._by_domain.get(domain, [])
        return [self._hypotheses[i] for i in ids if i in self._hypotheses]

    def testing(self) -> list[Hypothesis]:
        """Get hypotheses currently being tested."""
        return [h for h in self._hypotheses.values() if h.status == HypothesisStatus.TESTING]

    def validated(self) -> list[Hypothesis]:
        """Get validated hypotheses."""
        return [h for h in self._hypotheses.values() if h.status == HypothesisStatus.VALIDATED]

    def invalidated(self) -> list[Hypothesis]:
        """Get invalidated hypotheses."""
        return [h for h in self._hypotheses.values() if h.status == HypothesisStatus.INVALIDATED]

    def record_result(self, result: HypothesisResult) -> None:
        """Record test result for a hypothesis."""
        hyp = self._hypotheses.get(result.hypothesis_id)
        if hyp is None:
            return

        hyp.transition_to_testing()
        if result.validated:
            hyp.validate()
        else:
            hyp.invalidate()

        for e in result.evidence_gathered:
            hyp.add_evidence(e)

    def to_learned(self, hypothesis_id: str, insights: str | tuple[str, ...] = ()) -> None:
        """Mark hypothesis as learned from."""
        hyp = self._hypotheses.get(hypothesis_id)
        if hyp and isinstance(insights, str):
            hyp.metadata["insights"] = insights
