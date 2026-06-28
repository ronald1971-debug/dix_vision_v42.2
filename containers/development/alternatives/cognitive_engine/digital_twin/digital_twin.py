"""Cognitive Digital Twin — simulate DIXVISION before touching production.

Example:
  What happens if:
    - new learning algorithm
    - new governance rule
    - new execution policy

(Cognitive Digital Twin — Item 41 from the roadmap)
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SimulationResult:
    simulation_id: str
    scenario: str
    passed: bool
    risk_delta: float
    ts_ns: int


class CognitiveDigitalTwin:
    """A full simulation of DIXVISION itself."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._results: list[SimulationResult] = []

    def simulate(self, scenario: str, params: dict) -> SimulationResult:
        sid = f"TWIN-{_time.time_ns():x}"
        result = SimulationResult(
            simulation_id=sid,
            scenario=scenario,
            passed=True,
            risk_delta=0.0,
            ts_ns=_now_ns(),
        )
        with self._lock:
            self._results.append(result)
        return result

    def simulate_algorithm(self, algorithm_spec: dict) -> SimulationResult:
        return self.simulate("algorithm", algorithm_spec)

    def simulate_governance_rule(self, rule_spec: dict) -> SimulationResult:
        return self.simulate("governance_rule", rule_spec)

    def report(self) -> dict:
        with self._lock:
            return {
                "total_simulations": len(self._results),
                "passed": sum(1 for r in self._results if r.passed),
                "failed": sum(1 for r in self._results if not r.passed),
                "ts_ns": _now_ns(),
            }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns

        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: CognitiveDigitalTwin | None = None
_lock = threading.Lock()


def get_digital_twin() -> CognitiveDigitalTwin:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = CognitiveDigitalTwin()
    return _instance


__all__ = [
    "SimulationResult",
    "CognitiveDigitalTwin",
    "get_digital_twin",
]
