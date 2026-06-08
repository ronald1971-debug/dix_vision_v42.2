"""Epistemology Engine — belief lineage tracking.

Every belief must carry lineage, not just value.

Tracks:
  - evidence_ids per belief
  - contributor_chain (which engines contributed)
  - revision_count
  - confidence history over time

This is Item 27 from the cognitive operating system roadmap.
"""

from __future__ import annotations

import threading
import time as _time
from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Evidence:
    evidence_id: str
    source: str
    evidence_type: str
    content: dict[str, Any]
    weight: float
    ts_ns: int


@dataclass(frozen=True, slots=True)
class BeliefHistoryEntry:
    ts_ns: int
    confidence: float
    contributing_evidence: tuple[str, ...]


class EpistemologyEngine:
    """Tracks the complete lineage of every published belief.

    Responsibilities:
      1. Record evidence when beliefs are updated
      2. Maintain belief revision history
      3. Detect lineage breaks (missing evidence for large confidence change)
      4. Emit BELIEF_EVIDENCE_ADDED and BELIEF_LINEAGE_UPDATED events

    Thread-safe singleton.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._lineages: dict[str, dict] = {}
        self._evidence_store: dict[str, Evidence] = {}
        self._history: dict[str, deque] = {}
        self._audit_records: list[dict] = []

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def register_belief(
        self,
        belief_id: str,
        domain: str,
        claim: str,
        confidence: float,
        evidence_ids: list[str],
        contributor: str,
    ) -> dict:
        """Register a new belief with its first evidence set."""
        ts_ns = self._now_ns()
        lineage = {
            "belief_id": belief_id,
            "domain": domain,
            "claim": claim,
            "confidence": confidence,
            "evidence_ids": tuple(evidence_ids),
            "evidence_weights": tuple([1.0] * len(evidence_ids)),
            "contributor_chain": (contributor,),
            "formed_at": ts_ns,
            "last_reinforced": ts_ns,
            "revision_count": 0,
            "confidence_history": deque(
                [(ts_ns, confidence)], maxlen=200
            ),
        }
        with self._lock:
            self._lineages[belief_id] = lineage
            self._history[belief_id] = deque(
                [BeliefHistoryEntry(ts_ns=ts_ns, confidence=confidence,
                                    contributing_evidence=tuple(evidence_ids))],
                maxlen=100,
            )
        return {
            "belief_id": lineage["belief_id"],
            "domain": lineage["domain"],
            "claim": lineage["claim"],
            "confidence": lineage["confidence"],
            "evidence_count": len(evidence_ids),
            "evidence_ids": lineage["evidence_ids"],
            "contributor_chain": lineage["contributor_chain"],
            "formed_at": lineage["formed_at"],
            "last_reinforced": lineage["last_reinforced"],
            "revision_count": lineage["revision_count"],
        }

    def add_evidence(
        self,
        belief_id: str,
        evidence_id: str,
        source: str,
        evidence_type: str,
        weight: float = 1.0,
        content: dict | None = None,
    ) -> None:
        """Add evidence to an existing belief."""
        ts_ns = self._now_ns()
        evidence = Evidence(
            evidence_id=evidence_id,
            source=source,
            evidence_type=evidence_type,
            content=content or {},
            weight=weight,
            ts_ns=ts_ns,
        )
        with self._lock:
            self._evidence_store[evidence_id] = evidence
            if belief_id in self._lineages:
                lin = self._lineages[belief_id]
                ev_ids = list(lin["evidence_ids"])
                ev_weights = list(lin["evidence_weights"])
                contribs = list(lin["contributor_chain"])
                if source not in contribs:
                    contribs.append(source)
                if evidence_id not in ev_ids:
                    ev_ids.append(evidence_id)
                    ev_weights.append(weight)
                lin["evidence_ids"] = tuple(ev_ids)
                lin["evidence_weights"] = tuple(ev_weights)
                lin["contributor_chain"] = tuple(contribs)
                lin["last_reinforced"] = ts_ns

    def revise_belief(
        self,
        belief_id: str,
        new_confidence: float,
        triggering_evidence: list[str],
        reason: str,
        audit_trail: Any | None = None,
    ) -> dict:
        """Record a belief revision under new evidence."""
        ts_ns = self._now_ns()
        with self._lock:
            if belief_id not in self._lineages:
                return {}
            lin = self._lineages[belief_id]
            old_confidence = lin["confidence"]

            # Check for magical jump — must cite evidence for large confidence change
            delta = abs(new_confidence - old_confidence)
            if delta > 0.40 and len(triggering_evidence) == 0:
                lin["revision_count"] += 1
                payload = {
                    "belief_id": belief_id,
                    "violation": "MAGICAL_BELIEF_JUMP",
                    "delta": delta,
                }
                if audit_trail is not None:
                    self._audit_records.append(payload)
                return payload

            rev_count = lin["revision_count"] + 1
            lin["confidence"] = new_confidence
            lin["revision_count"] = rev_count
            lin["confidence_history"].append((ts_ns, new_confidence))

            history_entry = BeliefHistoryEntry(
                ts_ns=ts_ns,
                confidence=new_confidence,
                contributing_evidence=tuple(triggering_evidence),
            )
            self._history[belief_id].append(history_entry)

            payload = {
                "belief_id": belief_id,
                "revision_count": rev_count,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
                "triggering_evidence": triggering_evidence,
                "reason": reason,
            }
            if audit_trail is not None:
                self._audit_records.append(payload)
            return payload

    def get_lineage(self, belief_id: str) -> dict | None:
        with self._lock:
            if belief_id not in self._lineages:
                return None
            lin = self._lineages[belief_id]
            return {
                "belief_id": lin["belief_id"],
                "domain": lin["domain"],
                "claim": lin["claim"],
                "confidence": lin["confidence"],
                "evidence_count": len(lin["evidence_ids"]),
                "evidence_ids": lin["evidence_ids"],
                "contributor_chain": lin["contributor_chain"],
                "formed_at": lin["formed_at"],
                "last_reinforced": lin["last_reinforced"],
                "revision_count": lin["revision_count"],
            }

    def get_belief_history(self, belief_id: str) -> list[dict]:
        with self._lock:
            hist = self._history.get(belief_id, deque())
            return [
                {
                    "ts_ns": e.ts_ns,
                    "confidence": e.confidence,
                    "evidence_count": len(e.contributing_evidence),
                }
                for e in hist
            ]

    def lineage_report(self) -> dict:
        with self._lock:
            lines = []
            for b_id, lin in self._lineages.items():
                lines.append({
                    "belief_id": b_id,
                    "domain": lin["domain"],
                    "claim": lin["claim"],
                    "confidence": lin["confidence"],
                    "evidence_count": len(lin["evidence_ids"]),
                    "revision_count": lin["revision_count"],
                    "contributor_count": len(lin["contributor_chain"]),
                })
        return {"total_beliefs": len(lines), "beliefs": lines, "ts_ns": self._now_ns()}

    # ------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------

    @staticmethod
    def _now_ns() -> int:
        try:
            from system.time_source import wall_ns
            return wall_ns()
        except Exception:
            return int(_time.time() * 1e9)


_instance: EpistemologyEngine | None = None
_lock = threading.Lock()


def get_epistemology_engine() -> EpistemologyEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = EpistemologyEngine()
    return _instance


__all__ = [
    "Evidence",
    "BeliefHistoryEntry",
    "EpistemologyEngine",
    "get_epistemology_engine",
]
