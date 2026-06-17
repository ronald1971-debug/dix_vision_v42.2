"""
governance/mode_manager.py
DIX VISION v42.2 — System Mode Manager

Controls: GOVERNANCE_FSM transitions (SAFE → PAPER → CANARY → LIVE → AUTO → SAFE_LOCKED)
plus OPERATIONAL overlays (NORMAL, DEGRADED, EMERGENCY_HALT).

Transitions are governance-gated and ledger-logged.

ARCHITECTURAL ALIGNMENT (P1 authority consolidation):
  - Canonical FSM states live in core.contracts.governance.SystemMode.
  - This module's OperationalMode maps 1:1 to the canonical states;
    the old local SystemMode has been REMOVED to prevent enum divergence.
"""

from __future__ import annotations

import threading
from enum import StrEnum

from core.contracts.governance import SystemMode as FsmMode
from state.ledger.event_store import append_event
from system.fast_risk_cache import get_risk_cache
from system.state import get_state_manager


class OperationalMode(StrEnum):
    """Operational overlay states (reflected into the FSM via mode_manager)."""

    INIT           = "INIT"
    NORMAL         = "NORMAL"
    DEGRADED       = "DEGRADED"
    SAFE_MODE      = "SAFE_MODE"
    EMERGENCY_HALT = "EMERGENCY_HALT"

    @property
    def fsm_target(self) -> FsmMode:
        """Map this operational overlay onto the canonical FSM mode."""
        mapping = {
            OperationalMode.INIT:           FsmMode.SAFE,
            OperationalMode.NORMAL:         FsmMode.PAPER,
            OperationalMode.DEGRADED:       FsmMode.PAPER,
            OperationalMode.SAFE_MODE:      FsmMode.SAFE,
            OperationalMode.EMERGENCY_HALT: FsmMode.LOCKED,
        }
        return mapping[self]


_VALID_TRANSITIONS: dict[FsmMode, set[FsmMode]] = {
    FsmMode.SAFE: {FsmMode.PAPER, FsmMode.LOCKED},
    FsmMode.PAPER: {FsmMode.CANARY, FsmMode.SAFE, FsmMode.LOCKED},
    FsmMode.CANARY: {FsmMode.LIVE, FsmMode.PAPER, FsmMode.SAFE, FsmMode.LOCKED},
    FsmMode.LIVE: {FsmMode.AUTO, FsmMode.CANARY, FsmMode.SAFE, FsmMode.LOCKED},
    FsmMode.AUTO: {FsmMode.LIVE, FsmMode.CANARY, FsmMode.SAFE, FsmMode.LOCKED},
    FsmMode.LOCKED: {FsmMode.SAFE},
}


class ModeManager:
    def __init__(self) -> None:
        self._state_mgr = get_state_manager()
        self._cache = get_risk_cache()
        self._lock = threading.Lock()

    def current_fsm_mode(self) -> FsmMode:
        raw = self._state_mgr.get().governance_mode
        try:
            return FsmMode[raw]
        except KeyError:
            try:
                return FsmMode(raw)
            except ValueError:
                return FsmMode.SAFE

    def current_operational_mode(self) -> OperationalMode:
        fsm = self.current_fsm_mode()
        reverse = {
            FsmMode.SAFE:         OperationalMode.SAFE_MODE,
            FsmMode.PAPER:        OperationalMode.NORMAL,
            FsmMode.CANARY:       OperationalMode.NORMAL,
            FsmMode.LIVE:         OperationalMode.NORMAL,
            FsmMode.AUTO:         OperationalMode.NORMAL,
            FsmMode.LOCKED: OperationalMode.EMERGENCY_HALT,
        }
        return reverse.get(fsm, OperationalMode.SAFE_MODE)

    def transition(
        self,
        target: FsmMode,
        *,
        operational: OperationalMode | None = None,
        reason: str = "",
    ) -> bool:
        """Atomic check-then-act FSM transition.

        `operational` is the caller's operational overlay; it is
        recorded in the ledger for audit but the FSM legality check
        runs against `target` only.
        """
        with self._lock:
            current = self.current_fsm_mode()
            if target not in _VALID_TRANSITIONS.get(current, set()):
                return False
            self._state_mgr.update(governance_mode=target.name)
            if target is FsmMode.LOCKED:
                self._cache.halt_trading(reason=reason or "mode_transition")
            elif target is FsmMode.SAFE:
                self._cache.enter_safe_mode()
            else:
                self._cache.resume_trading()
            try:
                append_event(
                    "GOVERNANCE",
                    "MODE_CHANGE",
                    "mode_manager",
                    {
                        "from": current.name,
                        "to": target.name,
                        "operational_overlay": operational.name if operational else "",
                        "reason": reason,
                    },
                )
            except Exception:
                pass
            return True

    def halt(self, reason: str = "") -> None:
        """Force LOCKED (emergency halt)."""
        self._enter_lockdown(
            FsmMode.LOCKED,
            OperationalMode.EMERGENCY_HALT,
            reason=reason or "mode_manager_halt",
            forced=True,
        )

    def safe_mode(self, reason: str = "") -> None:
        """Force SAFE (recovery)."""
        self._enter_lockdown(
            FsmMode.SAFE,
            OperationalMode.SAFE_MODE,
            reason=reason or "mode_manager_safe_mode",
            forced=False,
        )

    def enter_degraded_mode(self, reason: str = "") -> None:
        """Enter DEGRADED operational mode (reduced functionality)."""
        with self._lock:
            prev = self.current_fsm_mode()
            # DEGRADED maps to PAPER in FSM but indicates reduced system health
            self._state_mgr.update(
                governance_mode=FsmMode.PAPER.name,
                operational_mode=OperationalMode.DEGRADED.name,
            )
            try:
                append_event(
                    "GOVERNANCE",
                    "MODE_CHANGE",
                    "mode_manager",
                    {
                        "from": prev.name,
                        "to": FsmMode.PAPER.name,
                        "operational_overlay": OperationalMode.DEGRADED.name,
                        "reason": reason or "mode_manager_degraded",
                    },
                )
            except Exception:
                pass

    def _enter_lockdown(
        self,
        target: FsmMode,
        operational: OperationalMode,
        *,
        reason: str,
        forced: bool,
    ) -> None:
        with self._lock:
            prev = self.current_fsm_mode()
            if target is FsmMode.LOCKED:
                self._cache.halt_trading(reason=reason)
                self._state_mgr.update(
                    governance_mode=target.name,
                    trading_allowed=False,
                )
            else:
                self._cache.enter_safe_mode()
                self._state_mgr.update(
                    governance_mode=target.name,
                    trading_allowed=False,
                )
            try:
                append_event(
                    "GOVERNANCE",
                    "MODE_CHANGE",
                    "mode_manager",
                    {
                        "from": prev.name,
                        "to": target.name,
                        "operational_overlay": operational.name,
                        "reason": reason,
                        "forced": forced,
                    },
                )
            except Exception:
                pass


_mgr: ModeManager | None = None
_mgr_lock = threading.Lock()


def get_mode_manager() -> ModeManager:
    global _mgr
    if _mgr is None:
        with _mgr_lock:
            if _mgr is None:
                _mgr = ModeManager()
    return _mgr


__all__ = [
    "ModeManager",
    "OperationalMode",
    "FsmMode",
    "get_mode_manager",
]
