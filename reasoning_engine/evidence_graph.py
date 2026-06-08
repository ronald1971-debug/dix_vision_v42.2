"""Reasoning engine — explains why decisions happen.

Current:
    Signal → Trade

Production cognitive systems need:
    Signal → Reason → Evidence → Confidence → Decision

Every decision should answer: Why?
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class EvidenceNode:
    """An evidence node in the reasoning graph."""

    node_id: str
    content: str
    source: str
    timestamp: int
    confidence: float
    supports: tuple[str, ...] = ()  # node IDs this supports


@dataclass(frozen=True, slots=True)
class Explanation:
    """Complete explanation for a decision."""

    decision_id: str
    reason: str
    evidence_chain: tuple[EvidenceNode, ...] = ()
    confidence_trace: dict[str, float] = field(default_factory=dict)
    contributing_factors: tuple[str, ...] = ()


class EvidenceGraph:
    """Graph of evidence supporting decisions.

    Tracks:
        - Evidence nodes and their relationships
        - Supporting evidence chains
        - Confidence propagation
    """

    def __init__(self) -> None:
        self._nodes: dict[str, EvidenceNode] = {}
        self._edges: dict[str, list[str]] = {}

    def add_node(self, node: EvidenceNode) -> None:
        self._nodes[node.node_id] = node
        for supported in node.supports:
            if supported not in self._edges:
                self._edges[supported] = []
            self._edges[supported].append(node.node_id)

    def get_evidence_chain(self, decision_id: str) -> tuple[EvidenceNode, ...]:
        ids = self._edges.get(decision_id, [])
        return tuple(self._nodes.get(nid) for nid in ids if nid in self._nodes)


class ExplanationBuilder:
    """Builds explanations for decisions.

    Constructs:
        - Reason string
        - Evidence chain
        - Confidence trace
    """

    def __init__(self) -> None:
        self._graph = EvidenceGraph()

    def explain(
        self, decision_id: str, reason: str,
        evidence: tuple[EvidenceNode, ...] = ()
    ) -> Explanation:
        for node in evidence:
            self._graph.add_node(node)

        confidence_trace = {node.source: node.confidence for node in evidence}

        return Explanation(
            decision_id=decision_id,
            reason=reason,
            evidence_chain=evidence,
            confidence_trace=confidence_trace,
            contributing_factors=tuple(e.source for e in evidence),
        )

    def get_evidence_chain(self, decision_id: str) -> tuple[EvidenceNode, ...]:
        return self._graph.get_evidence_chain(decision_id)


__all__ = [
    "EvidenceGraph",
    "EvidenceNode",
    "Explanation",
    "ExplanationBuilder",
]