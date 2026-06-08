"""Stream Router – routes events to the correct logical stream.

Six logical streams:
  - governance
  - cognition
  - execution
  - system
  - learning
  - evolution
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from core.types import Stream
from state.ledger.mcos_event_store import EventStore, LedgerEvent

Subscriber = Callable[[LedgerEvent], None]


@dataclass
class StreamSubscription:
    stream: Stream
    subscriber: Subscriber
    filter_event_types: list[str] = field(default_factory=list)


class StreamRouter:
    """Routes events to the correct stream and notifies subscribers."""

    VALID_STREAMS = {s.value for s in Stream}

    def __init__(self, store: EventStore) -> None:
        self._store = store
        self._subscriptions: dict[str, list[StreamSubscription]] = {
            s: [] for s in self.VALID_STREAMS
        }

    def route(
        self, stream: str, event_type: str, payload: dict[str, Any]
    ) -> LedgerEvent:
        if stream not in self.VALID_STREAMS:
            raise ValueError(
                f"Invalid stream '{stream}'. Valid: {sorted(self.VALID_STREAMS)}"
            )

        event = self._store.append(stream, event_type, payload)
        self._notify_subscribers(stream, event)
        return event

    def subscribe(
        self,
        stream: Stream,
        subscriber: Subscriber,
        filter_event_types: list[str] | None = None,
    ) -> StreamSubscription:
        sub = StreamSubscription(
            stream=stream,
            subscriber=subscriber,
            filter_event_types=filter_event_types or [],
        )
        self._subscriptions[stream.value].append(sub)
        return sub

    def unsubscribe(self, subscription: StreamSubscription) -> bool:
        subs = self._subscriptions.get(subscription.stream.value, [])
        if subscription in subs:
            subs.remove(subscription)
            return True
        return False

    def get_stream_events(self, stream: Stream) -> list[LedgerEvent]:
        return self._store.get_by_stream(stream.value)

    def get_all_streams_summary(self) -> dict[str, int]:
        return {
            s: len(self._store.get_by_stream(s)) for s in self.VALID_STREAMS
        }

    def _notify_subscribers(self, stream: str, event: LedgerEvent) -> None:
        for sub in self._subscriptions.get(stream, []):
            if sub.filter_event_types and event.event_type not in sub.filter_event_types:
                continue
            sub.subscriber(event)
