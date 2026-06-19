"""Contradiction Engine — cross-domain contradiction detection.

One of the hardest problems in intelligence.

Detects when:
  belief A contradicts
  belief B

Contradictions become first-class events.

This is Item 29 from the cognitive operating system roadmap.
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass

# Pre-defined contradiction rules: pairs of claims that cannot both
# hold simultaneously within the same time window.
_RULES: list[tuple[str, str, str]] = [
    ("risk-on", "liquidity-collapsing"),
    ("bullish", "bearish"),
    ("trend-continues", "trend-reversal"),
    ("low-volatility", "high-volatility"),
    ("safe-haven-outflow", "safe-haven-inflow"),
    ("rate-hawkish", "rate-dovish"),
]


@dataclass(frozen=True, slots=True)
class ActiveBelief:
    belief_id: str
    domain: str
    claim: str
    confidence: float
    ts_ns: int


class ContradictionEngine:
    """Detects contradictions between active beliefs across domains.

    Contradictions become first-class events that the system must
    reason about, not ignore.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._beliefs: dict[str, ActiveBelief] = {}
        self._contradictions: list[dict] = []
        self._rules = list(_RULES)

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def register_belief(
        self,
        belief_id: str,
        domain: str,
        claim: str,
        confidence: float,
        ts_ns: int,
    ) -> list[dict]:
        """Register a belief and check for contradictions with existing beliefs."""
        new = ActiveBelief(
            belief_id=belief_id,
            domain=domain,
            claim=self._normalize(claim),
            confidence=confidence,
            ts_ns=ts_ns,
        )
        found = []
        with self._lock:
            for existing_id, existing in list(self._beliefs.items()):
                if existing_id == belief_id:
                    continue
                conflict = self._check_contradiction(new, existing)
                if conflict:
                    record = {
                        "contradiction_id": f"CTRD-{_time.time_ns():x}",
                        "belief_a_id": existing_id,
                        "belief_b_id": belief_id,
                        "domain_a": existing.domain,
                        "domain_b": new.domain,
                        "claim_a": existing.claim,
                        "claim_b": new.claim,
                        "severity": self._severity(existing, new),
                        "ts_ns": ts_ns,
                    }
                    self._contradictions.append(record)
                    found.append(record)
            self._beliefs[belief_id] = new
        return found

    def resolve_contradiction(
        self,
        contradiction_id: str,
        winning_belief_id: str,
        resolution: str,
    ) -> bool:
        """Mark a contradiction as resolved by accepting one belief."""
        with self._lock:
            for c in self._contradictions:
                if c["contradiction_id"] == contradiction_id:
                    c["resolved"] = True
                    c["winning_belief_id"] = winning_belief_id
                    c["resolution"] = resolution
                    return True
        return False

    def get_active_contradictions(self) -> list[dict]:
        with self._lock:
            return [c for c in self._contradictions if not c.get("resolved")]

    def add_rule(self, claim_a: str, claim_b: str, description: str = "") -> None:
        with self._lock:
            self._rules.append((claim_a, claim_b, description))

    def summary(self) -> dict:
        with self._lock:
            total = len(self._contradictions)
            active = [c for c in self._contradictions if not c.get("resolved")]
            return {
                "total_contradictions": total,
                "active_contradictions": len(active),
                "registered_beliefs": len(self._beliefs),
                "rule_count": len(self._rules),
                "ts_ns": _now_ns(),
            }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize(claim: str) -> str:
        return claim.strip().lower().replace(" ", "-")

    def _check_contradiction(self, a: ActiveBelief, b: ActiveBelief) -> bool:
        ca = a.claim
        cb = b.claim
        # Exact opposites
        opposites = {
            "bullish": "bearish",
            "bearish": "bullish",
            "risk-on": "risk-off",
            "risk-off": "risk-on",
            "low-volatility": "high-volatility",
            "high-volatility": "low-volatility",
            "safe-haven-outflow": "safe-haven-inflow",
            "safe-haven-inflow": "safe-haven-outflow",
            "rate-hawkish": "rate-dovish",
            "rate-dovish": "rate-hawkish",
            "trend-continues": "trend-reversal",
            "trend-reversal": "trend-continues",
            "liquidity-collapsing": "liquidity-abundant",
            "liquidity-abundant": "liquidity-collapsing",
        }
        if ca in opposites and opposites[ca] == cb:
            return True
        if cb in opposites and opposites[cb] == ca:
            return True
        for rule_a, rule_b, _desc in self._rules:
            if ca == rule_a and cb == rule_b:
                return True
            if ca == rule_b and cb == rule_a:
                return True
            if ca.replace("-", "_") == rule_a.replace("-", "_") and cb.replace("-", "_") == rule_b.replace("-", "_"):
                return True
        return False

    @staticmethod
    def _severity(a: ActiveBelief, b: ActiveBelief) -> str:
        avg_conf = (a.confidence + b.confidence) / 2.0
        if avg_conf >= 0.80:
            return "CRITICAL"
        if avg_conf >= 0.60:
            return "HIGH"
        return "MEDIUM"


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns
        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: ContradictionEngine | None = None
_lock = threading.Lock()


def get_contradiction_engine() -> ContradictionEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = ContradictionEngine()
    return _instance


__all__ = [
    "ActiveBelief",
    "ContradictionEngine",
    "get_contradiction_engine",
]
