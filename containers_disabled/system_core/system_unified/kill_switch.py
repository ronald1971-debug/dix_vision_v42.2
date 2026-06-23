"""
System Unified Kill Switch - Emergency Shutdown Infrastructure
Provides emergency shutdown and kill switch capabilities
NO LAZY LOADING - All components load directly
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class KillSwitchState(Enum):
    """Kill switch state"""

    ARMED = "armed"
    TRIGGERED = "triggered"
    RESET = "reset"
    DISABLED = "disabled"


class KillReason(Enum):
    """Kill reason enumeration"""

    MANUAL = "manual"
    RISK_LIMIT = "risk_limit"
    SYSTEM_ERROR = "system_error"
    EMERGENCY = "emergency"
    GOVERNANCE = "governance"


@dataclass
class KillSwitchEvent:
    """Kill switch event data structure"""

    event_id: str
    state: KillSwitchState
    reason: KillReason
    triggered_by: str
    timestamp_ns: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = datetime.now().timestamp_ns()


class KillSwitch:
    """
    Kill Switch - Emergency shutdown infrastructure

    Provides emergency shutdown capabilities with governance oversight
    Required by archival components for emergency operations
    """

    def __init__(self):
        self._state = KillSwitchState.ARMED
        self._events: List[KillSwitchEvent] = []
        self._callbacks: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
        self._authorized_triggers = set()

    async def arm(self, authorized_by: str) -> bool:
        """Arm the kill switch"""
        async with self._lock:
            self._state = KillSwitchState.ARMED

        event = KillSwitchEvent(
            event_id=f"kill_event_{datetime.now().timestamp_ns()}",
            state=self._state,
            reason=KillReason.MANUAL,
            triggered_by=authorized_by,
            metadata={"action": "arm"},
        )
        self._events.append(event)

        logger.info(f"Kill switch armed by {authorized_by}")
        await self._trigger_callbacks("kill_switch_armed")

        return True

    async def trigger(
        self, reason: KillReason, triggered_by: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Trigger the kill switch"""
        async with self._lock:
            self._state = KillSwitchState.TRIGGERED

        event = KillSwitchEvent(
            event_id=f"kill_event_{datetime.now().timestamp_ns()}",
            state=self._state,
            reason=reason,
            triggered_by=triggered_by,
            metadata=metadata or {},
        )
        self._events.append(event)

        logger.warning(f"Kill switch TRIGGERED by {triggered_by} - reason: {reason.value}")
        await self._trigger_callbacks("kill_switch_triggered")

        return True

    async def reset(self, authorized_by: str) -> bool:
        """Reset the kill switch to armed state"""
        async with self._lock:
            self._state = KillSwitchState.RESET
            self._state = KillSwitchState.ARMED

        event = KillSwitchEvent(
            event_id=f"kill_event_{datetime.now().timestamp_ns()}",
            state=self._state,
            reason=KillReason.MANUAL,
            triggered_by=authorized_by,
            metadata={"action": "reset"},
        )
        self._events.append(event)

        logger.info(f"Kill switch reset by {authorized_by}")
        await self._trigger_callbacks("kill_switch_reset")

        return True

    async def disable(self, authorized_by: str) -> bool:
        """Disable the kill switch"""
        async with self._lock:
            self._state = KillSwitchState.DISABLED

        event = KillSwitchEvent(
            event_id=f"kill_event_{datetime.now().timestamp_ns()}",
            state=self._state,
            reason=KillReason.MANUAL,
            triggered_by=authorized_by,
            metadata={"action": "disable"},
        )
        self._events.append(event)

        logger.info(f"Kill switch disabled by {authorized_by}")
        await self._trigger_callbacks("kill_switch_disabled")

        return True

    async def get_state(self) -> KillSwitchState:
        """Get current kill switch state"""
        async with self._lock:
            return self._state

    async def get_events(self, limit: int = 10) -> List[KillSwitchEvent]:
        """Get recent kill switch events"""
        return self._events[-limit:]

    async def register_callback(self, event: str, callback: Callable):
        """Register callback for kill switch events"""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    async def _trigger_callbacks(self, event: str):
        """Trigger registered callbacks"""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Kill switch callback error: {e}")


# Global instance
_kill_switch = None


def get_kill_switch() -> KillSwitch:
    """Get global kill switch instance"""
    global _kill_switch
    if _kill_switch is None:
        _kill_switch = KillSwitch()
    return _kill_switch


async def trigger_kill_switch(
    reason: KillReason, triggered_by: str, metadata: Optional[Dict[str, Any]] = None
):
    """Trigger kill switch (convenience function)"""
    kill_switch = get_kill_switch()
    return await kill_switch.trigger(reason, triggered_by, metadata)


async def arm_kill_switch(authorized_by: str):
    """Arm kill switch (convenience function)"""
    kill_switch = get_kill_switch()
    return await kill_switch.arm(authorized_by)


async def reset_kill_switch(authorized_by: str):
    """Reset kill switch (convenience function)"""
    kill_switch = get_kill_switch()
    return await kill_switch.reset(authorized_by)


__all__ = [
    "KillSwitchState",
    "KillReason",
    "KillSwitchEvent",
    "KillSwitch",
    "get_kill_switch",
    "trigger_kill_switch",
    "arm_kill_switch",
    "reset_kill_switch",
]
