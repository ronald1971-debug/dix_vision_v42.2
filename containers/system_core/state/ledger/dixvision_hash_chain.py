"""Cryptographic Hash Chain.

Every ledger entry is chained to its predecessor via SHA-256,
ensuring tamper-evidence and deterministic replay.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChainEntry:
    sequence: int
    timestamp: float
    stream: str
    event_type: str
    payload_hash: str
    previous_hash: str
    entry_hash: str


class HashChain:
    """Append-only cryptographic hash chain."""

    GENESIS_HASH = "0" * 64

    def __init__(self) -> None:
        self._entries: list[ChainEntry] = []
        self._head_hash: str = self.GENESIS_HASH
        self._sequence: int = 0

    @property
    def head_hash(self) -> str:
        return self._head_hash

    @property
    def length(self) -> int:
        return len(self._entries)

    def append(self, stream: str, event_type: str, payload: dict[str, Any]) -> ChainEntry:
        payload_hash = self._hash_payload(payload)
        entry_data = f"{self._sequence}:{stream}:{event_type}:{payload_hash}:{self._head_hash}"
        entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()

        entry = ChainEntry(
            sequence=self._sequence,
            timestamp=time.time(),
            stream=stream,
            event_type=event_type,
            payload_hash=payload_hash,
            previous_hash=self._head_hash,
            entry_hash=entry_hash,
        )

        self._entries.append(entry)
        self._head_hash = entry_hash
        self._sequence += 1
        return entry

    def verify_chain(self) -> tuple[bool, str]:
        """Verify the entire chain from genesis."""
        if not self._entries:
            return True, "Empty chain is valid"

        expected_prev = self.GENESIS_HASH
        for entry in self._entries:
            if entry.previous_hash != expected_prev:
                return False, (
                    f"Chain broken at seq {entry.sequence}: "
                    f"expected prev {expected_prev[:16]}..., "
                    f"got {entry.previous_hash[:16]}..."
                )

            recomputed_data = (
                f"{entry.sequence}:{entry.stream}:{entry.event_type}"
                f":{entry.payload_hash}:{entry.previous_hash}"
            )
            recomputed_hash = hashlib.sha256(recomputed_data.encode()).hexdigest()
            if recomputed_hash != entry_hash_value(entry):
                return False, f"Hash mismatch at seq {entry.sequence}"

            expected_prev = entry.entry_hash

        return True, f"Chain valid: {len(self._entries)} entries"

    def get_entries(self, start: int = 0, end: int | None = None) -> list[ChainEntry]:
        return self._entries[start:end]

    @staticmethod
    def _hash_payload(payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()


def entry_hash_value(entry: ChainEntry) -> str:
    return entry.entry_hash
