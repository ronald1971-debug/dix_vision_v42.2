"""
governance_engine.domains.cognitive.knowledge_lifecycle
DIX VISION v42.2 — Knowledge Lifecycle Manager

Migrated from cognitive_governance/knowledge_lifecycle.py

Not all knowledge should live forever. This module governs the complete
lifecycle of beliefs and hypotheses:

  44. Knowledge Lifecycle

Knowledge should have:
  - birth: initialization with provenance
  - growth: confidence accumulation through evidence
  - validation: grounding checks and calibration
  - challenge: adversarial testing and falsification attempts
  - decay: systematic confidence reduction over time
  - retirement: archival when no longer relevant or trusted

Integrated with LongHorizonMemory for cross-temporal tracking.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from core.contracts.cognitive_governance import CognitiveViolationKind
from state.ledger.event_store import append_event


class KnowledgePhase(StrEnum):
    BIRTH = "BIRTH"
    GROWTH = "GROWTH"
    VALIDATION = "VALIDATION"
    CHALLENGE = "CHALLENGE"
    DECAY = "DECAY"
    RETIREMENT = "RETIREMENT"


@dataclass(frozen=True, slots=True)
class KnowledgeEvent:
    """A lifecycle event for a knowledge item."""
    knowledge_id: str
    phase: KnowledgePhase
    ts_ns: int
    evidence_count: int = 0
    confidence_before: float = 0.0
    confidence_after: float = 0.0
    challenger: str = ""
    outcome: str = ""
    detail: str = ""


@dataclass(frozen=True, slots=True)
class KnowledgeState:
    """Current lifecycle state for a knowledge item."""
    knowledge_id: str
    phase: KnowledgePhase
    birth_ts_ns: int
    last_updated_ts_ns: int
    confidence: float
    evidence_count: int
    challenge_count: int
    has_passed_validation: bool
    is_challenged: bool
    age_days: float
    retirement_reason: str | None = None


class KnowledgeLifecycleManager:
    """
    Manages the complete lifecycle of beliefs and hypotheses.

    Ensures knowledge does not accumulate unchecked; implements systematic
    retirement of outdated or untrustworthy beliefs.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._states: dict[str, KnowledgeState] = {}
        self._ledger: Any = None

    def _get_ledger(self) -> Any:
        """Lazy-init cognitive ledger if available."""
        if self._ledger is None:
            try:
                from knowledge_engine.cognitive_ledger.ledger import (
                    CognitiveLedger,  # noqa: PLC0415
                )
                self._ledger = CognitiveLedger()
            except ImportError:
                self._ledger = False  # type: ignore[assignment]
        return self._ledger if self._ledger is not True else None

    def birth(self, knowledge_id: str, initial_confidence: float = 0.5) -> KnowledgeState:
        """Initialize a new knowledge item."""
        from system.time_source import wall_ns

        ts_ns = wall_ns()
        state = KnowledgeState(
            knowledge_id=knowledge_id,
            phase=KnowledgePhase.BIRTH,
            birth_ts_ns=ts_ns,
            last_updated_ts_ns=ts_ns,
            confidence=initial_confidence,
            evidence_count=0,
            challenge_count=0,
            has_passed_validation=False,
            is_challenged=False,
            age_days=0.0,
        )
        with self._lock:
            self._states[knowledge_id] = state
        self._emit_event(knowledge_id, KnowledgePhase.BIRTH, detail="knowledge initialized")
        return state

    def grow(
        self,
        knowledge_id: str,
        evidence_delta: int = 1,
        confidence_boost: float = 0.1,
    ) -> KnowledgeState | None:
        """Add evidence and increase confidence."""
        from system.time_source import wall_ns

        ts_ns = wall_ns()
        with self._lock:
            state = self._states.get(knowledge_id)
            if state is None:
                return None

            new_confidence = min(1.0, state.confidence + confidence_boost)
            age_days = (ts_ns - state.birth_ts_ns) / 86_400_000_000_000

            new_state = KnowledgeState(
                knowledge_id=knowledge_id,
                phase=KnowledgePhase.GROWTH,
                birth_ts_ns=state.birth_ts_ns,
                last_updated_ts_ns=ts_ns,
                confidence=new_confidence,
                evidence_count=state.evidence_count + evidence_delta,
                challenge_count=state.challenge_count,
                has_passed_validation=state.has_passed_validation,
                is_challenged=state.is_challenged,
                age_days=age_days,
            )
            self._states[knowledge_id] = new_state
        self._emit_event(knowledge_id, KnowledgePhase.GROWTH,
                         evidence_count=state.evidence_count + evidence_delta,
                         confidence_after=new_confidence)
        return new_state

    def validate(self, knowledge_id: str, passed: bool) -> KnowledgeState | None:
        """Mark validation status."""
        from system.time_source import wall_ns

        ts_ns = wall_ns()
        with self._lock:
            state = self._states.get(knowledge_id)
            if state is None:
                return None

            new_state = KnowledgeState(
                knowledge_id=knowledge_id,
                phase=KnowledgePhase.VALIDATION,
                birth_ts_ns=state.birth_ts_ns,
                last_updated_ts_ns=ts_ns,
                confidence=state.confidence,
                evidence_count=state.evidence_count,
                challenge_count=state.challenge_count,
                has_passed_validation=passed,
                is_challenged=state.is_challenged,
                age_days=(ts_ns - state.birth_ts_ns) / 86_400_000_000_000,
            )
            self._states[knowledge_id] = new_state
        self._emit_event(knowledge_id, KnowledgePhase.VALIDATION,
                         outcome="passed" if passed else "failed",
                         detail=f"validation {'passed' if passed else 'failed'}")
        return new_state

    def challenge(self, knowledge_id: str, challenger: str) -> KnowledgeState | None:
        """Record a challenge attempt against knowledge."""
        from system.time_source import wall_ns

        ts_ns = wall_ns()
        with self._lock:
            state = self._states.get(knowledge_id)
            if state is None:
                return None

            new_state = KnowledgeState(
                knowledge_id=knowledge_id,
                phase=KnowledgePhase.CHALLENGE,
                birth_ts_ns=state.birth_ts_ns,
                last_updated_ts_ns=ts_ns,
                confidence=max(0.0, state.confidence - 0.1),
                evidence_count=state.evidence_count,
                challenge_count=state.challenge_count + 1,
                has_passed_validation=state.has_passed_validation,
                is_challenged=True,
                age_days=(ts_ns - state.birth_ts_ns) / 86_400_000_000_000,
            )
            self._states[knowledge_id] = new_state
        self._emit_event(knowledge_id, KnowledgePhase.CHALLENGE,
                         challenger=challenger,
                         detail=f"challenged by {challenger}")
        return new_state

    def decay(self, knowledge_id: str, reason: str = "age") -> KnowledgeState | None:
        """Apply decay to knowledge confidence."""
        from system.time_source import wall_ns

        ts_ns = wall_ns()
        with self._lock:
            state = self._states.get(knowledge_id)
            if state is None:
                return None

            decay_amount = 0.05 if reason == "age" else 0.2
            new_confidence = max(0.0, state.confidence - decay_amount)

            new_state = KnowledgeState(
                knowledge_id=knowledge_id,
                phase=KnowledgePhase.DECAY,
                birth_ts_ns=state.birth_ts_ns,
                last_updated_ts_ns=ts_ns,
                confidence=new_confidence,
                evidence_count=state.evidence_count,
                challenge_count=state.challenge_count,
                has_passed_validation=state.has_passed_validation,
                is_challenged=state.is_challenged,
                age_days=(ts_ns - state.birth_ts_ns) / 86_400_000_000_000,
            )
            self._states[knowledge_id] = new_state
        self._emit_event(knowledge_id, KnowledgePhase.DECAY,
                         confidence_before=state.confidence,
                         confidence_after=new_confidence,
                         detail=f"decayed due to {reason}")

        if new_confidence < 0.1:
            self.retire(knowledge_id, reason="low_confidence")
        return new_state

    def retire(self, knowledge_id: str, reason: str = "superseded") -> KnowledgeState | None:
        """Retire knowledge from active use."""
        from system.time_source import wall_ns

        ts_ns = wall_ns()
        with self._lock:
            state = self._states.get(knowledge_id)
            if state is None:
                return None

            new_state = KnowledgeState(
                knowledge_id=knowledge_id,
                phase=KnowledgePhase.RETIREMENT,
                birth_ts_ns=state.birth_ts_ns,
                last_updated_ts_ns=ts_ns,
                confidence=state.confidence,
                evidence_count=state.evidence_count,
                challenge_count=state.challenge_count,
                has_passed_validation=state.has_passed_validation,
                is_challenged=state.is_challenged,
                age_days=(ts_ns - state.birth_ts_ns) / 86_400_000_000_000,
                retirement_reason=reason,
            )
            self._states[knowledge_id] = new_state

        self._emit_event(knowledge_id, KnowledgePhase.RETIREMENT,
                         detail=f"retired: {reason}")

        lifecycle_violation = None
        if reason == "failed_challenge":
            lifecycle_violation = CognitiveViolationKind.LEARNING_NOT_GROUNDED
        elif reason == "low_confidence":
            lifecycle_violation = CognitiveViolationKind.CALIBRATION_DRIFT

        if lifecycle_violation:
            payload = {
                "knowledge_id": knowledge_id,
                "reason": reason,
                "violation": lifecycle_violation.value,
            }
            append_event(
                "GOVERNANCE",
                "COGOV_KNOWLEDGE_LIFECYCLE_VIOLATION",
                "governance_engine.domains.cognitive.knowledge_lifecycle",
                payload,
            )
        return new_state

    def get_state(self, knowledge_id: str) -> KnowledgeState | None:
        """Get current lifecycle state for a knowledge item."""
        with self._lock:
            return self._states.get(knowledge_id)

    def get_retired(self, limit: int = 50) -> list[KnowledgeState]:
        """Get recently retired knowledge items."""
        with self._lock:
            retired = [s for s in self._states.values()
                      if s.phase == KnowledgePhase.RETIREMENT]
            return retired[-limit:] if retired else []

    def get_active(self, limit: int = 100) -> list[KnowledgeState]:
        """Get active (non-retired) knowledge items."""
        with self._lock:
            active = [s for s in self._states.values()
                     if s.phase != KnowledgePhase.RETIREMENT]
            return active[-limit:] if active else []

    def _emit_event(
        self,
        knowledge_id: str,
        phase: KnowledgePhase,
        evidence_count: int = 0,
        confidence_before: float = 0.0,
        confidence_after: float = 0.0,
        challenger: str = "",
        outcome: str = "",
        detail: str = "",
    ) -> None:
        append_event(
            "COGNITIVE",
            "KNOWLEDGE_LIFECYCLE_EVENT",
            "governance_engine.domains.cognitive.knowledge_lifecycle",
            {
                "knowledge_id": knowledge_id,
                "phase": phase.value,
                "confidence_before": confidence_before,
                "confidence_after": confidence_after,
                "challenger": challenger,
                "outcome": outcome,
                "detail": detail,
            },
        )
        # Also record to cognitive ledger
        ledger = self._get_ledger()
        if ledger:
            ledger.record_lifecycle_event(
                phase=phase.value.lower(),
                knowledge_id=knowledge_id,
                confidence_delta=confidence_after - confidence_before,
                metadata={"detail": detail, "challenger": challenger, "outcome": outcome},
            )


_instance: KnowledgeLifecycleManager | None = None
_lock = threading.Lock()


def get_knowledge_lifecycle() -> KnowledgeLifecycleManager:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = KnowledgeLifecycleManager()
    return _instance


__all__ = [
    "get_knowledge_lifecycle",
    "KnowledgeEvent",
    "KnowledgeLifecycleManager",
    "KnowledgePhase",
    "KnowledgeState",
]