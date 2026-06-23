"""WebSocket Layer – real-time push to dashboard clients.

Provides the transport for live state updates to the operator dashboard.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class WSMessage:
    msg_type: str = ""  # state_update | hazard_alert | governance_event | heartbeat
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def serialize(self) -> str:
        return json.dumps(
            {
                "type": self.msg_type,
                "payload": self.payload,
                "timestamp": self.timestamp,
            }
        )


class WebSocketManager:
    """Manages WebSocket connections for the dashboard."""

    def __init__(self) -> None:
        self._clients: list[Any] = []
        self._message_queue: list[WSMessage] = []
        self._broadcast_count: int = 0

    def register_client(self, client: Any) -> None:
        self._clients.append(client)

    def remove_client(self, client: Any) -> None:
        if client in self._clients:
            self._clients.remove(client)

    def queue_message(self, msg: WSMessage) -> None:
        self._message_queue.append(msg)

    def broadcast_state_update(self, state_json: str) -> int:
        msg = WSMessage(
            msg_type="state_update",
            payload=json.loads(state_json),
        )
        return self._broadcast(msg)

    def broadcast_hazard_alert(self, hazard: dict[str, Any]) -> int:
        msg = WSMessage(msg_type="hazard_alert", payload=hazard)
        return self._broadcast(msg)

    def broadcast_governance_event(self, event: dict[str, Any]) -> int:
        msg = WSMessage(msg_type="governance_event", payload=event)
        return self._broadcast(msg)

    def _broadcast(self, msg: WSMessage) -> int:
        sent = 0
        serialized = msg.serialize()
        for client in self._clients:
            try:
                if hasattr(client, "send"):
                    client.send(serialized)
                sent += 1
            except Exception:
                pass
        self._broadcast_count += 1
        return sent

    @property
    def client_count(self) -> int:
        return len(self._clients)

    @property
    def broadcast_count(self) -> int:
        return self._broadcast_count
