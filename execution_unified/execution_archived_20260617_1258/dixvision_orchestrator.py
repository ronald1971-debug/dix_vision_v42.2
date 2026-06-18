"""Execution Orchestrator – coordinates the governed execution pipeline.

execution_engine: orchestration only
execution: actual execution

The orchestrator connects Governance approval to the execution layer.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from governance_unified.engine import BeliefState
from core.types import ExecutionIntent, TradeResult
from execution_unified.adapter_router import AdapterRouter
from execution_unified._emergency_executor import EmergencyExecutor
from governance_unified.approval_decision import ApprovalDecision
from governance_unified.engine import GovernanceKernel
from state.ledger.writer import LedgerWriter


@dataclass
class OrchestrationResult:
    intent: ExecutionIntent
    decision: ApprovalDecision
    trade_result: TradeResult | None = None
    timestamp: float = field(default_factory=time.time)

    @property
    def was_executed(self) -> bool:
        return self.trade_result is not None


class ExecutionOrchestrator:
    """Orchestrates the full execution pipeline:
    Intent → Governance Check → Execution → Ledger Recording
    """

    def __init__(
        self,
        governance: GovernanceKernel,
        router: AdapterRouter,
        ledger: LedgerWriter,
    ) -> None:
        self._governance = governance
        self._router = router
        self._ledger = ledger
        self._emergency = EmergencyExecutor(router)
        self._results: list[OrchestrationResult] = []

    def process_intent(
        self,
        intent: ExecutionIntent,
        belief: BeliefState,
        venue: str | None = None,
    ) -> OrchestrationResult:
        """Process an intent through the full governed pipeline."""
        decision = self._governance.evaluate_intent(intent, belief)
        self._ledger.write_governance_event(
            "intent_evaluated",
            {
                "intent_id": intent.intent_id,
                "status": decision.status.name,
                "violations": decision.policy_violations,
            },
        )

        trade_result: TradeResult | None = None
        if decision.status.name == "APPROVED":
            self._ledger.write_execution_intent(intent)
            trade_result = self._router.route(intent, venue)
            self._ledger.write_trade_result(trade_result)

        result = OrchestrationResult(
            intent=intent, decision=decision, trade_result=trade_result
        )
        self._results.append(result)
        return result

    def emergency_halt(
        self,
        open_positions: list[dict[str, Any]],
        reason: str = "Emergency halt",
    ) -> None:
        self._governance.activate_kill_switch(reason)
        action = self._emergency.emergency_close_all(open_positions, reason)
        self._ledger.write_system_event(
            "emergency_halt",
            {
                "reason": reason,
                "positions_closed": action.positions_closed,
                "duration": action.duration_seconds,
            },
        )

    def get_results(self) -> list[OrchestrationResult]:
        return list(self._results)

    @property
    def executed_count(self) -> int:
        return sum(1 for r in self._results if r.was_executed)

    @property
    def rejected_count(self) -> int:
        return sum(1 for r in self._results if not r.was_executed)
