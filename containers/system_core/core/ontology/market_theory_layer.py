"""Market Theory Layer — theories governing INDIRA's understanding.

Integrates with:
  core.ontology.theory.Theory (unified theory object)
  core.ontology.knowledge.Knowledge (theory validation)
  reasoning_engine.causal.CausalEngine (causal grounding)
  self_model (theory confidence contributes to system self-awareness)
  cognitive_engine.truth_maintenance (theory revision tracking)
"""

from __future__ import annotations

from typing import Any

from core.ontology.theory import Theory
from self_model.capability_map import SelfModel


class MarketTheoryLayer:
    """Manage the portfolio of theories INDIRA holds.

    Responsibilities:
      - Register new theories
      - Attach evidence to theories (increasing empirical_support)
      - Falsify theories when contradictory evidence accumulates
      - Track which strategies implement which theories
      - Report theory portfolio health to self_model
    """

    def __init__(self, self_model: SelfModel | None = None) -> None:
        self._lock = _NoOpLock()
        self._theory_store: dict[str, Theory] = {}
        self._theory_id_index: dict[str, str] = {}
        self._self_model = self_model

    def register_theory(self, theory: Theory) -> Theory:
        key = theory.theory_name.lower().replace(" ", "_")
        self._theory_store[key] = theory
        self._theory_id_index[key] = theory.object_id
        if self._self_model is not None:
            self._self_model.update_capability(f"theory:{key}", 0.5)
        return theory

    def get_theory(self, theory_name: str) -> Theory | None:
        return self._theory_store.get(theory_name.lower().replace(" ", "_"))

    def attach_evidence(self, theory_name: str, evidence_id: str) -> Theory | None:
        theory = self.get_theory(theory_name)
        if theory is None:
            return None
        updated = theory.replace(
            evidence_ids=theory.evidence_ids + (evidence_id,),
            empirical_support=min(1.0, theory.empirical_support + 0.05),
        )
        self._theory_store[theory_name.lower().replace(" ", "_")] = updated
        if self._self_model is not None:
            self._self_model.update_capability(f"theory:{theory_name}", updated.empirical_support)
        return updated

    def falsify(self, theory_name: str) -> Theory | None:
        theory = self.get_theory(theory_name)
        if theory is None:
            return None
        updated = theory.replace(
            falsified=True,
            falsification_attempts=theory.falsification_attempts + 1,
            empirical_support=max(0.0, theory.empirical_support - 0.3),
        )
        self._theory_store[theory_name.lower().replace(" ", "_")] = updated
        if self._self_model is not None:
            self._self_model.update_capability(f"theory:{theory_name}", updated.empirical_support)
        return updated

    def implementing_strategies(self, theory_name: str) -> tuple[str, ...]:
        theory = self.get_theory(theory_name)
        if theory is None:
            return ()
        return theory.implementing_strategies

    def list_theories(self) -> tuple[Theory, ...]:
        return tuple(self._theory_store.values())

    def report(self) -> dict[str, Any]:
        theories = self.list_theories()
        return {
            "total_theories": len(theories),
            "falsified": sum(1 for t in theories if t.falsified),
            "supported": sum(1 for t in theories if t.is_supported()),
            "falsifiable": sum(1 for t in theories if t.is_falsifiable()),
        }


class _NoOpLock:
    def __enter__(self) -> _NoOpLock:
        return self

    def __exit__(self, *_exc: Any) -> None:
        return None


__all__ = ["MarketTheoryLayer"]