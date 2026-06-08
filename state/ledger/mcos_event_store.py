"""Append-Only Event Store.

Stores all system events in an immutable, ordered sequence.
Supports replay from any point in history.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from state.ledger.mcos_hash_chain import HashChain


@dataclass(frozen=True)
class LedgerEvent:
    event_id: str
    sequence: int
    stream: str
    event_type: str
    payload: dict[str, Any]
    timestamp: float
    chain_hash: str


class EventStore:
    """Immutable, append-only event store backed by a hash chain."""

    def __init__(self) -> None:
        self._events: list[LedgerEvent] = []
        self._chain = HashChain()
        self._sequence: int = 0
        self._stream_index: dict[str, list[int]] = {}

    @property
    def count(self) -> int:
        return len(self._events)

    @property
    def chain(self) -> HashChain:
        return self._chain

    def append(
        self,
        stream: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> LedgerEvent:
        chain_entry = self._chain.append(stream, event_type, payload)

        event = LedgerEvent(
            event_id=uuid.uuid4().hex[:16],
            sequence=self._sequence,
            stream=stream,
            event_type=event_type,
            payload=payload,
            timestamp=time.time(),
            chain_hash=chain_entry.entry_hash,
        )

        self._events.append(event)

        if stream not in self._stream_index:
            self._stream_index[stream] = []
        self._stream_index[stream].append(self._sequence)

        self._sequence += 1
        return event

    def get_by_sequence(self, sequence: int) -> LedgerEvent | None:
        if 0 <= sequence < len(self._events):
            return self._events[sequence]
        return None

    def get_by_stream(self, stream: str) -> list[LedgerEvent]:
        indices = self._stream_index.get(stream, [])
        return [self._events[i] for i in indices]

    def get_by_type(self, event_type: str) -> list[LedgerEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def replay(self, from_sequence: int = 0) -> Iterator[LedgerEvent]:
        yield from self._events[from_sequence:]

    def verify_integrity(self) -> tuple[bool, str]:
        return self._chain.verify_chain()

    def get_latest(self, count: int = 10) -> list[LedgerEvent]:
        return self._events[-count:]
