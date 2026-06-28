"""
governance_engine.domains.cognitive.cognitive_physics
DIX VISION v42.2 — Cognitive Physics Engine

Migrated from cognitive_governance/cognitive_physics.py

Formal laws describing how knowledge moves through DIXVISION:

  - Belief propagation: how confidence spreads through related beliefs
  - Confidence decay: how certainty erodes over time
  - Knowledge aging: how beliefs evolve and become obsolete
  - Uncertainty propagation: how doubt flows through inference chains

These were implicit in the original architecture. This module makes them
explicit, measurable, and governable.
"""

from __future__ import annotations

import math
import threading
import time as _time
from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from state.ledger.event_store import append_event


class KnowledgeFlow(StrEnum):
    SPREAD = "SPREAD"
    DECAY = "DECAY"
    AGE = "AGE"
    UNCERTAINTY = "UNCERTAINTY"


@dataclass(frozen=True, slots=True)
class BeliefPropagation:
    source_belief_id: str
    target_belief_id: str
    source_confidence: float
    target_confidence_before: float
    target_confidence_after: float
    flow_amount: float
    evidence_overlap: float
    ts_ns: int


@dataclass(frozen=True, slots=True)
class DecayRecord:
    belief_id: str
    confidence_before: float
    confidence_after: float
    decay_amount: float
    decay_reason: str
    ts_ns: int


@dataclass(frozen=True, slots=True)
class UncertaintyPropagation:
    source_belief_id: str
    target_belief_id: str
    source_uncertainty: float
    target_uncertainty: float
    propagation_path: tuple[str, ...]
    ts_ns: int


class CognitivePhysicsEngine:
    """
    Formalizes implicit knowledge dynamics into measurable laws.

    Tracks and governs:
      1. Belief propagation rates and evidence overlap
      2. Confidence decay over time and context
      3. Knowledge aging and obsolescence
      4. Uncertainty flow through inference graphs
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_access: dict[str, int] = defaultdict(lambda: _time.time_ns())
        self._age_factor_cache: dict[str, float] = {}
        self._propagation_history: list[BeliefPropagation] = []
        self._decay_history: list[DecayRecord] = defaultdict(list)
        self._uncertainty_graph: dict[str, set[str]] = defaultdict(set)

    def register_dependency(self, source_belief_id: str, target_belief_id: str) -> None:
        """Register that target depends on source for uncertainty propagation."""
        with self._lock:
            self._uncertainty_graph[target_belief_id].add(source_belief_id)

    def propagate_confidence(
        self,
        source_belief_id: str,
        target_belief_id: str,
        source_confidence: float,
        target_confidence: float,
        evidence_overlap: float,
    ) -> float:
        """
        Compute confidence propagation from source to target belief.

        Propagation factor = evidence_overlap * source_confidence
        New confidence = target_confidence + (propagation_factor * 0.3)
        Capped at 1.0 to prevent runaway amplification.
        """
        from system_unified.time_source import wall_ns

        ts_ns = wall_ns()
        flow = evidence_overlap * source_confidence
        new_confidence = min(1.0, target_confidence + flow * 0.3)

        record = BeliefPropagation(
            source_belief_id=source_belief_id,
            target_belief_id=target_belief_id,
            source_confidence=source_confidence,
            target_confidence_before=target_confidence,
            target_confidence_after=new_confidence,
            flow_amount=flow,
            evidence_overlap=evidence_overlap,
            ts_ns=ts_ns,
        )

        with self._lock:
            self._propagation_history.append(record)
            if len(self._propagation_history) > 1000:
                self._propagation_history = self._propagation_history[-500:]

        return new_confidence

    def decay_confidence(
        self,
        belief_id: str,
        current_confidence: float,
        half_life_hours: float = 24.0,
        context: str = "natural",
    ) -> float:
        """
        Apply exponential decay to belief confidence.

        Decay formula: C(t) = C0 * e^(-λt) where λ = ln(2) / half_life
        Returns decayed confidence.
        """
        from system_unified.time_source import wall_ns

        now = wall_ns()

        with self._lock:
            last = self._last_access.get(belief_id, now)
            elapsed_hours = (now - last) / 3_600_000_000_000

        if elapsed_hours <= 0:
            return current_confidence

        decay_rate = math.log(2) / half_life_hours
        decay_factor = math.exp(-decay_rate * elapsed_hours)
        new_confidence = current_confidence * decay_factor

        decay_amount = current_confidence - new_confidence

        if decay_amount > 0.01:
            record = DecayRecord(
                belief_id=belief_id,
                confidence_before=current_confidence,
                confidence_after=new_confidence,
                decay_amount=decay_amount,
                decay_reason=context,
                ts_ns=now,
            )
            with self._lock:
                self._decay_history[belief_id].append(record)

        with self._lock:
            self._last_access[belief_id] = now

        return new_confidence

    def propagate_uncertainty(
        self,
        target_belief_id: str,
        direct_uncertainty: float,
    ) -> float:
        """
        Compute propagated uncertainty through dependency graph.

        Combined uncertainty from all sources (with overlap adjustment):
        U_total = 1 - Π(1 - U_source_i)
        """
        from system_unified.time_source import wall_ns

        now = wall_ns()

        with self._lock:
            sources = self._uncertainty_graph.get(target_belief_id, set())
            if not sources:
                return direct_uncertainty

            source_uncertainties = []
            for src in sources:
                age_factor = self._age_factor_cache.get(src, 1.0)
                source_uncertainties.append(age_factor * 0.5)

        if not source_uncertainties:
            return direct_uncertainty

        uncertainty_product = 1.0
        for u in source_uncertainties:
            uncertainty_product *= 1.0 - u

        propagated = 1.0 - uncertainty_product
        total_uncertainty = min(1.0, propagated + direct_uncertainty)

        if source_uncertainties and propagated > 0.1:
            record = UncertaintyPropagation(
                source_belief_id=",".join(sources),
                target_belief_id=target_belief_id,
                source_uncertainty=sum(source_uncertainties) / len(source_uncertainties),
                target_uncertainty=total_uncertainty,
                propagation_path=target_belief_id,
                ts_ns=now,
            )
            self._emit_uncertainty_event(record)

        return total_uncertainty

    def age_knowledge(self, belief_id: str, age_days: float) -> float:
        """
        Compute knowledge aging factor.

        Returns multiplier: 1.0 for fresh knowledge, decaying toward 0 over time.
        Uses sigmoid decay: age_factor = 1 / (1 + e^(age_days/τ - 2))
        τ (tau) = 7 days half-decay point.
        """
        tau = 7.0
        age_factor = 1.0 / (1.0 + math.exp(age_days / tau - 2))
        self._age_factor_cache[belief_id] = age_factor
        return age_factor

    def get_propagation_stats(self, belief_id: str | None = None) -> dict[str, Any]:
        """Get propagation statistics for a belief or overall."""
        with self._lock:
            if belief_id:
                incoming = [p for p in self._propagation_history if p.target_belief_id == belief_id]
                outgoing = [p for p in self._propagation_history if p.source_belief_id == belief_id]
                return {
                    "belief_id": belief_id,
                    "incoming_propagation_count": len(incoming),
                    "outgoing_propagation_count": len(outgoing),
                    "total_flow": sum(p.flow_amount for p in incoming),
                }
            return {
                "total_propagations": len(self._propagation_history),
                "unique_sources": len(set(p.source_belief_id for p in self._propagation_history)),
                "unique_targets": len(set(p.target_belief_id for p in self._propagation_history)),
            }

    def _emit_uncertainty_event(self, record: UncertaintyPropagation) -> None:
        append_event(
            "COGNITIVE",
            "UNCERTAINTY_PROPAGATION",
            "governance_engine.domains.cognitive.cognitive_physics",
            {
                "target_belief_id": record.target_belief_id,
                "source_uncertainty": record.source_uncertainty,
                "propagated_uncertainty": record.target_uncertainty,
                "propagation_path": list(record.propagation_path),
            },
        )


_instance: CognitivePhysicsEngine | None = None
_lock = threading.Lock()


def get_cognitive_physics() -> CognitivePhysicsEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = CognitivePhysicsEngine()
    return _instance


__all__ = [
    "BeliefPropagation",
    "CognitivePhysicsEngine",
    "DecayRecord",
    "get_cognitive_physics",
    "KnowledgeFlow",
    "UncertaintyPropagation",
]
