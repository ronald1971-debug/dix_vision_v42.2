"""Causal reasoning — correlation to causation.

Wraps the canonical causal-graph data structures from core.coherence
so reasoning engines can reason over causal structure without
re-implementing graph logic.
"""

from __future__ import annotations

from core.coherence.causal_graph import CausalEdge, CausalGraph, CausalNode


class CausalStrength:
    """Placeholder for learned causal strength value."""

    def __init__(self, value: float = 0.0) -> None:
        self.value = float(value)


class CausalMechanism:
    """Placeholder for mechanism descriptor."""

    def __init__(self, mechanism_id: str, description: str = "") -> None:
        self.mechanism_id = mechanism_id
        self.description = description


class CausalHypothesis:
    """Simple hypothesis about a causal link."""

    def __init__(self, cause: str, effect: str, strength: CausalStrength | None = None) -> None:
        self.cause = cause
        self.effect = effect
        self.strength = strength or CausalStrength(0.0)


class CausalInferenceResult:
    """Result produced by CausalEngine.infer."""

    def __init__(self, graph: CausalGraph, hypothesis: CausalHypothesis | None = None) -> None:
        self.graph = graph
        self.hypothesis = hypothesis


class CausalEngine:
    """Thin integration layer around CausalGraph.

    The core graph implementation lives in core.coherence.causal_graph.
    This engine provides a higher-level interface for reasoning modules.
    """

    def __init__(self) -> None:
        self._graph = CausalGraph()
        self._hypotheses: dict[str, CausalHypothesis] = {}

    def register_node(self, node: CausalNode) -> None:
        self._graph.add_node(node)

    def register_edge(self, edge: CausalEdge) -> None:
        self._graph.add_edge(edge)

    def register_hypothesis(self, hypothesis: CausalHypothesis) -> None:
        key = f"{hypothesis.cause}->{hypothesis.effect}"
        self._hypotheses[key] = hypothesis

    def infer(self, cause: str, effect: str) -> CausalInferenceResult:
        key = f"{cause}->{effect}"
        hypothesis = self._hypotheses.get(key)
        return CausalInferenceResult(graph=self._graph, hypothesis=hypothesis)

    def detect_ghosts(self, active_nodes: frozenset[str]) -> tuple[str, ...]:
        from core.coherence.causal_graph import detect_ghost_causality  # noqa: PLC0415

        return detect_ghost_causality(self._graph, active_nodes)


__all__ = [
    "CausalEdge",
    "CausalEngine",
    "CausalGraph",
    "CausalHypothesis",
    "CausalInferenceResult",
    "CausalMechanism",
    "CausalNode",
    "CausalStrength",
]
