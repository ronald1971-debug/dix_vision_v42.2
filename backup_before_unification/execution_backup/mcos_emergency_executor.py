"""Emergency Executor – immediate position liquidation on kill switch.

Bypasses normal execution queue for emergency situations.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from core.types import ExecutionIntent, TradeResult
from execution.dixvision_adapter_router import AdapterRouter


@dataclass
class EmergencyAction:
    action_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    reason: str = ""
    positions_closed: int = 0
    results: list[TradeResult] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    duration_seconds: float = 0.0


class EmergencyExecutor:
    """Handles emergency position liquidation.

    Activated by the governance kill switch. Closes all open positions
    immediately regardless of normal execution constraints.
    """

    def __init__(self, router: AdapterRouter) -> None:
        self._router = router
        self._actions: list[EmergencyAction] = []

    def emergency_close_all(
        self,
        open_positions: list[dict[str, Any]],
        reason: str = "Kill switch activated",
    ) -> EmergencyAction:
        start = time.time()
        results: list[TradeResult] = []

        for pos in open_positions:
            close_intent = ExecutionIntent(
                intent_id=uuid.uuid4().hex[:12],
                symbol=pos.get("symbol", ""),
                direction="close",
                quantity=pos.get("quantity", 0.0),
                price_limit=None,
                confidence=1.0,
                reasoning=f"Emergency close: {reason}",
                timestamp=time.time(),
            )
            result = self._router.route(close_intent)
            results.append(result)

        action = EmergencyAction(
            reason=reason,
            positions_closed=len(results),
            results=results,
            duration_seconds=time.time() - start,
        )
        self._actions.append(action)
        return action

    def get_actions(self) -> list[EmergencyAction]:
        return list(self._actions)

    @property
    def total_emergency_actions(self) -> int:
        return len(self._actions)
