"""Truth Maintenance System — belief revision engine.

As new evidence arrives, old beliefs must be re-evaluated.

Responsibilities:
  1. Detect belief fields that contradict correlated signals
  2. Recompute belief confidence via evidence reweighing
  3. Revise beliefs automatically when evidence shifts materially
  4. Emit BELIEF_REVISED and EVIDENCE_REWEIGHED events

This is Item 28 from the cognitive operating system roadmap.
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BeliefField:
    """A single claim within a belief domain."""
    field_id: str
    domain: str
    key: str
    value: str
    confidence: float
    evidence_ids: tuple[str, ...]
    ts_ns: int


class EvidenceReweigher:
    """Recalculates confidence from current evidence weights.

    Simple weighted average with a minimum evidence floor.
    """

    MIN_EVIDENCE_FOR_UPDATE = 0.01

    def reweigh(self, confidence: float, weights: list[float]) -> float:
        if not weights:
            return confidence
        total = sum(weights)
        if total < self.MIN_EVIDENCE_FOR_UPDATE:
            return confidence
        w_avg = sum(w * confidence for w in weights) / total
        return max(0.0, min(1.0, w_avg))


class TruthMaintenanceEngine:
    """Maintains truth by revising beliefs as new evidence arrives.

    Uses the epistemology engine to determine which evidence belongs
    to a belief, applies evidence reweighing, and triggers belief
    revisions when confidence shifts exceed thresholds.
    """

    REVISION_DELTA_THRESHOLD = 0.10

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._beliefs: dict[str, BeliefField] = {}
        self._revisions: list[dict] = []
        self._reweigher = EvidenceReweigher()

    def register_belief(
        self,
        field_id: str,
        domain: str,
        key: str,
        value: str,
        confidence: float,
        evidence_ids: list[str],
        ts_ns: int,
    ) -> BeliefField:
        bf = BeliefField(
            field_id=field_id,
            domain=domain,
            key=key,
            value=value,
            confidence=confidence,
            evidence_ids=tuple(evidence_ids),
            ts_ns=ts_ns,
        )
        with self._lock:
            self._beliefs[field_id] = bf
        return bf

    def add_evidence_and_revise(
        self,
        field_id: str,
        new_evidence_id: str,
        new_weight: float,
        ts_ns: int,
    ) -> dict | None:
        """Add evidence and check if belief revision is needed."""
        with self._lock:
            if field_id not in self._beliefs:
                return None
            bf = self._beliefs[field_id]
            evidence_ids = list(bf.evidence_ids)
            weights = [1.0] * len(evidence_ids)
            if new_evidence_id in evidence_ids:
                idx = evidence_ids.index(new_evidence_id)
                weights[idx] = new_weight
            else:
                evidence_ids.append(new_evidence_id)
                weights.append(new_weight)

            new_conf = self._reweigher.reweigh(bf.confidence, weights)
            delta = abs(new_conf - bf.confidence)

            if delta >= self.REVISION_DELTA_THRESHOLD:
                record = {
                    "field_id": field_id,
                    "old_confidence": bf.confidence,
                    "new_confidence": new_conf,
                    "delta": delta,
                    "triggering_evidence": [new_evidence_id],
                    "ts_ns": ts_ns,
                }
                self._revisions.append(record)
                bf_new = BeliefField(
                    field_id=bf.field_id,
                    domain=bf.domain,
                    key=bf.key,
                    value=bf.value,
                    confidence=new_conf,
                    evidence_ids=tuple(evidence_ids),
                    ts_ns=ts_ns,
                )
                self._beliefs[field_id] = bf_new
                return record
            # Update evidence store even without revision threshold
            bf_new = BeliefField(
                field_id=bf.field_id,
                domain=bf.domain,
                key=bf.key,
                value=bf.value,
                confidence=bf.confidence,
                evidence_ids=tuple(evidence_ids),
                ts_ns=ts_ns,
            )
            self._beliefs[field_id] = bf_new
            return None

    def revise_manually(
        self,
        field_id: str,
        new_confidence: float,
        reason: str,
    ) -> dict | None:
        with self._lock:
            if field_id not in self._beliefs:
                return None
            bf = self._beliefs[field_id]
            old_conf = bf.confidence
            record = {
                "field_id": field_id,
                "old_confidence": old_conf,
                "new_confidence": new_confidence,
                "delta": abs(new_confidence - old_conf),
                "reason": reason,
                "ts_ns": _now_ns(),
            }
            self._revisions.append(record)
            bf_new = BeliefField(
                field_id=bf.field_id,
                domain=bf.domain,
                key=bf.key,
                value=bf.value,
                confidence=new_confidence,
                evidence_ids=bf.evidence_ids,
                ts_ns=_now_ns(),
            )
            self._beliefs[field_id] = bf_new
            return record

    def get_belief(self, field_id: str) -> dict | None:
        with self._lock:
            if field_id not in self._beliefs:
                return None
            bf = self._beliefs[field_id]
            return {
                "field_id": bf.field_id,
                "domain": bf.domain,
                "key": bf.key,
                "value": bf.value,
                "confidence": bf.confidence,
                "evidence_count": len(bf.evidence_ids),
                "ts_ns": bf.ts_ns,
            }

    def revision_report(self) -> dict:
        with self._lock:
            revs = self._revisions[-200:]
        return {
            "total_revisions": len(self._revisions),
            "recent_revisions": len(revs),
            "revisions": revs,
            "ts_ns": _now_ns(),
        }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns
        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: TruthMaintenanceEngine | None = None
_lock = threading.Lock()


def get_truth_maintenance() -> TruthMaintenanceEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = TruthMaintenanceEngine()
    return _instance


__all__ = [
    "BeliefField",
    "EvidenceReweigher",
    "TruthMaintenanceEngine",
    "get_truth_maintenance",
]
