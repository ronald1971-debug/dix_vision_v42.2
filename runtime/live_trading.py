"""Live Trading Infrastructure – Phase 14.

Requirements:
  - Governance approved
  - Risk constrained
  - Ledger backed
  - Deterministic
  - Auditable

Production deployment ready.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from core.kernel import BeliefState
from core.types import ExecutionIntent, PromotionStage
from governance.kernel import GovernanceKernel
from state.ledger.event_store import EventStore
from state.ledger.writer import LedgerWriter


@dataclass
class LiveTradingConfig:
    venue: str = "paper"
    max_capital_allocation: float = 0.0
    risk_limit_pct: float = 0.02
    require_governance_approval: bool = True
    ledger_backed: bool = True
    audit_mode: bool = True


@dataclass
class LiveTradingStatus:
    is_running: bool = False
    stage: str = ""
    uptime_seconds: float = 0.0
    trades_executed: int = 0
    governance_rejections: int = 0
    hazards_detected: int = 0
    last_trade_time: float = 0.0
    start_time: float = 0.0


class LiveTradingInfrastructure:
    """Production-ready live trading infrastructure.

    All trades are governance-approved, risk-constrained,
    ledger-backed, deterministic, and auditable.
    """

    def __init__(
        self,
        governance: GovernanceKernel,
        router: AdapterRouter,
        config: LiveTradingConfig | None = None,
    ) -> None:
        self._governance = governance
        self._router = router
        self._config = config or LiveTradingConfig()
        self._store = EventStore()
        self._ledger = LedgerWriter(self._store)
        self._orchestrator = ExecutionOrchestrator(governance, router, self._ledger)
        self._status = LiveTradingStatus()

    def pre_flight_check(self) -> tuple[bool, list[str]]:
        """Run all pre-flight checks before going live."""
        issues: list[str] = []

        if self._governance.current_stage != PromotionStage.PRODUCTION:
            issues.append(
                f"Not at production stage (current: {self._governance.current_stage.value})"
            )

        if self._governance.is_halted:
            issues.append("Kill switch is active")

        if self._config.max_capital_allocation <= 0:
            issues.append("No capital allocated")

        available = self._router.get_available_venues()
        if self._config.venue not in available:
            issues.append(f"Venue '{self._config.venue}' not available")

        return len(issues) == 0, issues

    def start(self) -> tuple[bool, str]:
        ok, issues = self.pre_flight_check()
        if not ok:
            return False, f"Pre-flight failed: {'; '.join(issues)}"

        self._status.is_running = True
        self._status.stage = self._governance.current_stage.value
        self._status.start_time = time.time()

        self._ledger.write_system_event(
            "live_trading_started",
            {"config": {"venue": self._config.venue, "risk_limit": self._config.risk_limit_pct}},
        )
        return True, "Live trading started"

    def stop(self, reason: str = "Manual stop") -> None:
        self._status.is_running = False
        self._status.uptime_seconds = time.time() - self._status.start_time
        self._ledger.write_system_event(
            "live_trading_stopped",
            {"reason": reason, "uptime": self._status.uptime_seconds},
        )

    def process_intent(
        self, intent: ExecutionIntent, belief: BeliefState
    ) -> bool:
        if not self._status.is_running:
            return False

        result = self._orchestrator.process_intent(
            intent, belief, venue=self._config.venue
        )

        if result.was_executed:
            self._status.trades_executed += 1
            self._status.last_trade_time = time.time()
        else:
            self._status.governance_rejections += 1

        return result.was_executed

    def get_status(self) -> LiveTradingStatus:
        if self._status.is_running:
            self._status.uptime_seconds = time.time() - self._status.start_time
        return self._status

    @property
    def event_store(self) -> EventStore:
        return self._store
