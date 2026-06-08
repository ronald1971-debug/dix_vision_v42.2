"""Constitution V2 — invariant document + case law.

Eventually the invariant document becomes:
  Constitution
Then later:
  Case Law

Example:
  Incident #341
    Outcome
    Rule Added

Governance accumulates precedent.

(Item 40 — cognitive operating system roadmap)
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CaseLaw:
    case_id: str
    incident_id: str
    outcome: str
    rule_added: str
    ts_ns: int


class ConstitutionV2:
    """Invariant document + case law."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._rules: list[str] = []
        self._case_law: dict[str, CaseLaw] = {}

    def record_case(self, incident_id: str, outcome: str,
                    rule_added: str) -> CaseLaw:
        case_id = f"CASE-{_time.time_ns():x}"
        cl = CaseLaw(
            case_id=case_id,
            incident_id=incident_id,
            outcome=outcome,
            rule_added=rule_added,
            ts_ns=_now_ns(),
        )
        with self._lock:
            self._case_law[case_id] = cl
            if rule_added not in self._rules:
                self._rules.append(rule_added)
        return cl

    def lookup(self, query: str) -> list[dict]:
        with self._lock:
            return [
                {
                    "case_id": c.case_id,
                    "incident_id": c.incident_id,
                    "outcome": c.outcome,
                    "rule_added": c.rule_added,
                    "ts_ns": c.ts_ns,
                }
                for c in self._case_law.values()
                if query.lower() in c.rule_added.lower()
                or query.lower() in c.outcome.lower()
            ]

    def get_case_law(self) -> dict:
        with self._lock:
            return {
                "case_count": len(self._case_law),
                "rule_count": len(self._rules),
                "ts_ns": _now_ns(),
            }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns
        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: ConstitutionV2 | None = None
_lock = threading.Lock()


def get_constitution_v2() -> ConstitutionV2:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = ConstitutionV2()
    return _instance


__all__ = [
    "CaseLaw",
    "ConstitutionV2",
    "get_constitution_v2",
]
