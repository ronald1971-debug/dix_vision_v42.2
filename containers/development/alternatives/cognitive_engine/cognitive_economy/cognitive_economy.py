"""Cognitive Economy — finite cognitive resource allocation.

Attention and learning resources are finite.

System should allocate: CPU, Memory, Inference, Learning
based on expected knowledge gain.

(Item 38 — cognitive operating system roadmap)
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResourceAllocation:
    resource_type: str
    target: str
    expected_gain: float
    allocated: float
    ts_ns: int


class CognitiveEconomy:
    """Allocates cognitive resources based on expected knowledge gain."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._allocations: list[ResourceAllocation] = []

    def allocate(self, resource_type: str, target: str,
                 expected_gain: float, budget: float = 1.0) -> ResourceAllocation:
        alloc = ResourceAllocation(
            resource_type=resource_type,
            target=target,
            expected_gain=expected_gain,
            allocated=budget,
            ts_ns=_now_ns(),
        )
        with self._lock:
            self._allocations.append(alloc)
        return alloc

    def reallocate(self, to_target: str, from_target: str, amount: float) -> None:
        with self._lock:
            pass

    def report(self) -> dict:
        with self._lock:
            return {
                "total_allocations": len(self._allocations),
                "recent_allocations": len(self._allocations[-100:]),
                "ts_ns": _now_ns(),
            }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns
        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: CognitiveEconomy | None = None
_lock = threading.Lock()


def get_cognitive_economy() -> CognitiveEconomy:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = CognitiveEconomy()
    return _instance


__all__ = [
    "ResourceAllocation",
    "CognitiveEconomy",
    "get_cognitive_economy",
]
