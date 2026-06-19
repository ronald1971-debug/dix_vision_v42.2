"""Belief snapshots — INV-DIX-02 enforcement.

Snapshot and restore belief state for recovery and versioning.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BeliefSnapshot:
    """A snapshot of belief state at a point in time."""
    ts_ns: int
    version: str
    data: dict  # Serialized belief state


class BeliefSnapshotStore:
    """Store and retrieve belief snapshots."""

    def __init__(self) -> None:
        self._snapshots: dict[int, BeliefSnapshot] = {}

    def save(self, snapshot: BeliefSnapshot) -> None:
        """Save a belief snapshot."""
        self._snapshots[snapshot.ts_ns] = snapshot

    def load(self, ts_ns: int) -> BeliefSnapshot | None:
        """Load a belief snapshot by timestamp."""
        return self._snapshots.get(ts_ns)

    def latest(self) -> BeliefSnapshot | None:
        """Get the most recent snapshot."""
        if not self._snapshots:
            return None
        latest_ts = max(self._snapshots.keys())
        return self._snapshots[latest_ts]


__all__ = [
    "BeliefSnapshot",
    "BeliefSnapshotStore",
]