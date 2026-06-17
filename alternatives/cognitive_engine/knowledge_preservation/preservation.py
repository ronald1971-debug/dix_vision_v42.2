"""Knowledge Preserver - orchestrates knowledge preservation."""

from __future__ import annotations

import hashlib
import time
from typing import Any

from cognitive_engine.knowledge_preservation.archive import KnowledgeArchive
from cognitive_engine.knowledge_preservation.snapshot import KnowledgeSnapshot


class KnowledgePreserver:
    """Orchestrates knowledge preservation across model changes.

    Key risk: Learning → Forgetting

    Creates snapshots before model updates and can restore
    if new models perform worse.
    """

    def __init__(self, archive: KnowledgeArchive | None = None) -> None:
        self._archive = archive or KnowledgeArchive()
        self._last_snapshot: KnowledgeSnapshot | None = None
        self._preservation_events: list[dict[str, Any]] = []

    def capture(
        self,
        trader_knowledge: dict[str, Any] | None = None,
        strategy_knowledge: dict[str, Any] | None = None,
        market_knowledge: dict[str, Any] | None = None,
        regime_knowledge: dict[str, Any] | None = None,
        execution_knowledge: dict[str, Any] | None = None,
        cognitive_knowledge: dict[str, Any] | None = None,
    ) -> KnowledgeSnapshot:
        """Capture current knowledge state as snapshot."""
        combined = {
            "trader": trader_knowledge or {},
            "strategy": strategy_knowledge or {},
            "market": market_knowledge or {},
            "regime": regime_knowledge or {},
            "execution": execution_knowledge or {},
            "cognitive": cognitive_knowledge or {},
        }

        checksum = hashlib.sha256(
            str(combined).encode(),
        ).hexdigest()[:16]

        snapshot = KnowledgeSnapshot(
            trader_knowledge=trader_knowledge or {},
            strategy_knowledge=strategy_knowledge or {},
            market_knowledge=market_knowledge or {},
            regime_knowledge=regime_knowledge or {},
            execution_knowledge=execution_knowledge or {},
            cognitive_knowledge=cognitive_knowledge or {},
            hash_checksum=checksum,
        )

        self._archive.store(snapshot)
        self._last_snapshot = snapshot

        self._preservation_events.append({
            "event": "capture",
            "snapshot_id": snapshot.snapshot_id,
            "entries": snapshot.total_entries(),
            "timestamp": time.time_ns(),
        })

        return snapshot

    def restore(self, snapshot_id: str) -> KnowledgeSnapshot | None:
        """Restore knowledge from a snapshot."""
        snapshot = self._archive.retrieve(snapshot_id)
        if snapshot:
            self._preservation_events.append({
                "event": "restore",
                "snapshot_id": snapshot_id,
                "timestamp": time.time_ns(),
            })
        return snapshot

    def auto_snapshot_before_change(self, source: str = "unknown") -> KnowledgeSnapshot:
        """Create auto-snapshot before model change."""
        return self.capture()

    def get_last_snapshot(self) -> KnowledgeSnapshot | None:
        """Get most recent snapshot."""
        return self._last_snapshot

    def preservation_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get preservation history."""
        return self._preservation_events[-limit:]