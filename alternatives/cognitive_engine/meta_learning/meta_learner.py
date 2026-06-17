"""Meta-Learning — learning about learning.

Not: What did I learn?
But: Which learning process works best?

Tracks lane_id, approach, knowledge_gain, compute_cost, gain_per_cost.
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LanePerformance:
    lane_id: str
    approach: str
    knowledge_gain: float
    compute_cost: float
    gain_per_cost: float
    samples_processed: int
    ts_ns: int


class MetaLearner:
    """Reports which learning approach is performing best."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._lanes: dict[str, list[LanePerformance]] = {}

    def record_sample(
        self,
        lane_id: str,
        approach: str,
        knowledge_gain: float,
        compute_cost: float,
    ) -> LanePerformance:
        samples = 1
        gpc = knowledge_gain / compute_cost if compute_cost > 0 else float("inf")
        perf = LanePerformance(
            lane_id=lane_id,
            approach=approach,
            knowledge_gain=knowledge_gain,
            compute_cost=compute_cost,
            gain_per_cost=gpc,
            samples_processed=1,
            ts_ns=_now_ns(),
        )
        with self._lock:
            if lane_id not in self._lanes:
                self._lanes[lane_id] = []
            self._lanes[lane_id].append(perf)
            # Running totals
            existing = self._lanes[lane_id]
            perf2 = LanePerformance(
                lane_id=lane_id,
                approach=approach,
                knowledge_gain=sum(p.knowledge_gain for p in existing),
                compute_cost=sum(p.compute_cost for p in existing),
                gain_per_cost=(
                    sum(p.knowledge_gain for p in existing)
                    / sum(p.compute_cost for p in existing)
                    if sum(p.compute_cost for p in existing) > 0
                    else float("inf")
                ),
                samples_processed=len(existing),
                ts_ns=_now_ns(),
            )
        return perf2

    def lane_performance(self, lane_id: str) -> dict | None:
        with self._lock:
            if lane_id not in self._lanes or not self._lanes[lane_id]:
                return None
            samples = self._lanes[lane_id]
            return {
                "lane_id": lane_id,
                "approach": samples[-1].approach,
                "total_knowledge_gain": sum(p.knowledge_gain for p in samples),
                "total_compute_cost": sum(p.compute_cost for p in samples),
                "gain_per_cost": (
                    sum(p.knowledge_gain for p in samples)
                    / sum(p.compute_cost for p in samples)
                    if sum(p.compute_cost for p in samples) > 0
                    else float("inf")
                ),
                "samples_processed": len(samples),
                "ts_ns": _now_ns(),
            }

    def best_approach(self) -> dict | None:
        with self._lock:
            best_lane = None
            best_gpc = -1.0
            for lid, samples in self._lanes.items():
                if not samples:
                    continue
                total_gain = sum(p.knowledge_gain for p in samples)
                total_cost = sum(p.compute_cost for p in samples)
                gpc = (total_gain / total_cost) if total_cost > 0 else float("inf")
                if gpc > best_gpc:
                    best_gpc = gpc
                    best_lane = lid
            if best_lane is None:
                return None
            samples = self._lanes[best_lane]
            total_gain = sum(p.knowledge_gain for p in samples)
            total_cost = sum(p.compute_cost for p in samples)
            return {
                "lane_id": best_lane,
                "approach": samples[-1].approach,
                "total_knowledge_gain": total_gain,
                "total_compute_cost": total_cost,
                "gain_per_cost": (total_gain / total_cost) if total_cost > 0 else float("inf"),
                "samples_processed": len(samples),
                "ts_ns": _now_ns(),
            }

    def all_lanes(self) -> dict:
        with self._lock:
            return {
                "lanes": list(self._lanes.keys()),
                "count": len(self._lanes),
                "ts_ns": _now_ns(),
            }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns
        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: MetaLearner | None = None
_lock = threading.Lock()


def get_meta_learner() -> MetaLearner:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = MetaLearner()
    return _instance


__all__ = [
    "LanePerformance",
    "MetaLearner",
    "get_meta_learner",
]
