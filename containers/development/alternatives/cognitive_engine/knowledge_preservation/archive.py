"""Knowledge Archive - long-term storage of knowledge snapshots."""

from __future__ import annotations

from cognitive_engine.knowledge_preservation.snapshot import KnowledgeSnapshot


class KnowledgeArchive:
    """Long-term archive for knowledge preservation.

    Prevents loss of hard-earned understanding during model changes.
    """

    def __init__(self) -> None:
        self._snapshots: dict[str, KnowledgeSnapshot] = {}
        self._archive_index: list[str] = []

    def store(self, snapshot: KnowledgeSnapshot) -> str:
        """Store a knowledge snapshot."""
        self._snapshots[snapshot.snapshot_id] = snapshot
        self._archive_index.append(snapshot.snapshot_id)
        return snapshot.snapshot_id

    def retrieve(self, snapshot_id: str) -> KnowledgeSnapshot | None:
        """Retrieve a snapshot by ID."""
        return self._snapshots.get(snapshot_id)

    def retrieve_latest(self) -> KnowledgeSnapshot | None:
        """Retrieve most recent snapshot."""
        if not self._archive_index:
            return None
        return self._snapshots.get(self._archive_index[-1])

    def retrieve_by_time(self, target_time: int) -> KnowledgeSnapshot | None:
        """Retrieve snapshot closest to target time."""
        if not self._archive_index:
            return None

        best_match = None
        best_diff = float("inf")

        for sid in self._archive_index:
            snap = self._snapshots[sid]
            diff = abs(snap.created_at - target_time)
            if diff < best_diff:
                best_diff = diff
                best_match = snap

        return best_match

    def snapshot_count(self) -> int:
        """Get total number of archived snapshots."""
        return len(self._snapshots)

    def list_snapshots(self, limit: int = 100) -> list[KnowledgeSnapshot]:
        """List recent snapshots."""
        ids = self._archive_index[-limit:]
        return [self._snapshots[i] for i in ids if i in self._snapshots]
