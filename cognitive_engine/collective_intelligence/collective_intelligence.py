"""Collective Intelligence — individual AND group trader understanding.

Eventually DIXVISION should understand:
  - individual traders
  - groups of traders

Example clusters:
  - Momentum Cluster
  - Options Cluster
  - Quant Cluster
  - Retail Cluster

(Item 37 — cognitive operating system roadmap)
"""

from __future__ import annotations

import threading
import time as _time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TraderProfile:
    trader_id: str
    cluster: str | None = None
    behavior_tags: tuple[str, ...] = ()
    confidence: float = 0.0
    ts_ns: int = 0


@dataclass(frozen=True, slots=True)
class Cluster:
    cluster_id: str
    name: str
    members: tuple[str, ...]
    avg_confidence: float
    ts_ns: int


class CollectiveIntelligenceEngine:
    """Understands both individual traders and groups of traders."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._profiles: dict[str, TraderProfile] = {}
        self._clusters: dict[str, Cluster] = {}

    def index_trader(self, trader_id: str, tags: list[str], cluster: str | None = None) -> TraderProfile:
        prof = TraderProfile(
            trader_id=trader_id,
            cluster=cluster,
            behavior_tags=tuple(tags),
            ts_ns=_now_ns(),
        )
        with self._lock:
            self._profiles[trader_id] = prof
            if cluster:
                self._clusters.setdefault(cluster, []).append(trader_id)
        return prof

    def define_cluster(self, cluster_id: str, name: str,
                       member_ids: list[str]) -> Cluster:
        cl = Cluster(
            cluster_id=cluster_id,
            name=name,
            members=tuple(member_ids),
            avg_confidence=0.5,
            ts_ns=_now_ns(),
        )
        with self._lock:
            self._clusters[cluster_id] = cl
        return cl

    def get_trader_profile(self, trader_id: str) -> dict | None:
        with self._lock:
            prof = self._profiles.get(trader_id)
            if prof is None:
                return None
            return {
                "trader_id": prof.trader_id,
                "cluster": prof.cluster,
                "behavior_tags": prof.behavior_tags,
            }

    def get_cluster(self, cluster_id: str) -> dict | None:
        with self._lock:
            cl = self._clusters.get(cluster_id)
            if cl is None:
                return None
            return {
                "cluster_id": cl.cluster_id,
                "name": cl.name,
                "members": cl.members,
                "member_count": len(cl.members),
            }

    def summary(self) -> dict:
        with self._lock:
            return {
                "total_traders": len(self._profiles),
                "total_clusters": len(self._clusters),
                "cluster_names": list(self._clusters.keys()),
                "ts_ns": _now_ns(),
            }


def _now_ns() -> int:
    try:
        from system.time_source import wall_ns
        return wall_ns()
    except Exception:
        return int(_time.time() * 1e9)


_instance: CollectiveIntelligenceEngine | None = None
_lock = threading.Lock()


def get_collective_intelligence() -> CollectiveIntelligenceEngine:
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = CollectiveIntelligenceEngine()
    return _instance


__all__ = [
    "CollectiveIntelligenceEngine",
    "TraderProfile",
    "Cluster",
    "get_collective_intelligence",
]
