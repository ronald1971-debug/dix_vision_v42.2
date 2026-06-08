"""GovernanceKillSwitch — single kill-switch primitive owned by GovernanceEngine.

Wraps the existing governance kill path so every caller (operator, hazard,
financial, system) funnels through one chokepoint owned by ENGINE-06.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from core.contracts.governance import SystemMode


class KillTrigger(StrEnum):
    OPERATOR = "operator"
    HAZARD = "hazard"
    FINANCIAL = "financial"
    SYSTEM = "system"
    EXTERNAL = "external"


@dataclass(frozen=True, slots=True)
class KillSwitchRecord:
    ts_ns: int
    trigger: KillTrigger
    from_mode: SystemMode
    to_mode: SystemMode = SystemMode.LOCKED
    reason: str = ""
    requested_by: str = "unknown"


class GovernanceKillSwitch:
    """Single authority for all kill engagement.

    Delegates to the owner-provided mode manager (the canonical path for
    system transitions) so the kill switch is journaled and FSM-checked
    consistently regardless of caller.
    """

    def __init__(self, *, mode_manager: Any) -> None:
        self._mode_manager = mode_manager
        self._last: KillSwitchRecord | None = None

    def engage(
        self,
        *,
        trigger: KillTrigger,
        reason: str,
        ts_ns: int,
        requested_by: str = "unknown",
    ) -> KillSwitchRecord:
        current = self._mode_manager.current_fsm_mode()
        record = KillSwitchRecord(
            ts_ns=ts_ns,
            trigger=trigger,
            from_mode=current,
            to_mode=SystemMode.LOCKED,
            reason=reason,
            requested_by=requested_by,
        )
        accepted = self._mode_manager.transition(
            SystemMode.LOCKED,
            reason=f"[{trigger.value}] {reason}",
        )
        if not accepted:
            record = KillSwitchRecord(
                ts_ns=record.ts_ns,
                trigger=trigger,
                from_mode=current,
                to_mode=current,
                reason=f"denied: {reason}",
                requested_by=requested_by,
            )
        self._last = record
        return record

    def last_record(self) -> KillSwitchRecord | None:
        return self._last


def get_governance_kill_switch(*, mode_manager: Any | None = None) -> GovernanceKillSwitch:
    if mode_manager is None:
        from governance.mode_manager import get_mode_manager
        mode_manager = get_mode_manager()
    return GovernanceKillSwitch(mode_manager=mode_manager)
