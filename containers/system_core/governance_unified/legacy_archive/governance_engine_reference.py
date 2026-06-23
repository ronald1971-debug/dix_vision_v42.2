"""Unified Governance Kernel.

Responsibilities:
  - Policy authority: defines what is allowed
  - Promotion authority: gates stage transitions
  - Approval authority: approves/rejects execution intents
  - Emergency authority: master kill switch
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from core.types import ApprovalStatus, ExecutionIntent, PromotionStage, Severity
from governance_unified.engine import BeliefState


@dataclass
class PolicyRule:
    rule_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str = ""
    description: str = ""
    domain: str = ""  # cognitive | financial | operator | system
    condition: str = ""  # human-readable condition
    max_position_pct: float = 1.0
    max_loss_pct: float = 1.0
    min_confidence: float = 0.0
    allowed_regimes: list[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class ApprovalDecision:
    decision_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    intent_id: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    reason: str = ""
    policy_violations: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    governor_id: str = "governance_kernel"


@dataclass
class PromotionRequest:
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    current_stage: PromotionStage = PromotionStage.SIMULATION
    target_stage: PromotionStage = PromotionStage.BACKTEST
    evidence: dict[str, Any] = field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    timestamp: float = field(default_factory=time.time)


class GovernanceKernel:
    """Central governance authority for the entire .

    All execution intents must pass through this kernel.
    All stage promotions must be approved here.
    Emergency halt is controlled here.
    """

    def __init__(self) -> None:
        self._policies: dict[str, PolicyRule] = {}
        self._kill_switch: bool = False
        self._current_stage: PromotionStage = PromotionStage.SIMULATION
        self._audit_log: list[dict[str, Any]] = []
        self._promotion_history: list[PromotionRequest] = []

    @property
    def is_halted(self) -> bool:
        return self._kill_switch

    @property
    def current_stage(self) -> PromotionStage:
        return self._current_stage

    def register_policy(self, rule: PolicyRule) -> None:
        self._policies[rule.rule_id] = rule
        self._log("policy_registered", {"rule_id": rule.rule_id, "name": rule.name})

    def remove_policy(self, rule_id: str) -> bool:
        if rule_id in self._policies:
            del self._policies[rule_id]
            self._log("policy_removed", {"rule_id": rule_id})
            return True
        return False

    def evaluate_intent(self, intent: ExecutionIntent, belief: BeliefState) -> ApprovalDecision:
        """Evaluate an ExecutionIntent against all active policies."""
        if self._kill_switch:
            return ApprovalDecision(
                intent_id=intent.intent_id,
                status=ApprovalStatus.REJECTED,
                reason="System halted – kill switch active",
            )

        if belief.is_halted():
            return ApprovalDecision(
                intent_id=intent.intent_id,
                status=ApprovalStatus.REJECTED,
                reason="BeliefState indicates system halt",
            )

        violations: list[str] = []
        for policy in self._policies.values():
            if not policy.enabled:
                continue
            violations.extend(self._check_policy(intent, belief, policy))

        if violations:
            decision = ApprovalDecision(
                intent_id=intent.intent_id,
                status=ApprovalStatus.REJECTED,
                reason=f"Policy violations: {len(violations)}",
                policy_violations=violations,
            )
        else:
            decision = ApprovalDecision(
                intent_id=intent.intent_id,
                status=ApprovalStatus.APPROVED,
                reason="All policies satisfied",
            )

        self._log(
            "intent_evaluated",
            {
                "intent_id": intent.intent_id,
                "status": decision.status.name,
                "violations": violations,
            },
        )
        return decision

    def _check_policy(
        self, intent: ExecutionIntent, belief: BeliefState, policy: PolicyRule
    ) -> list[str]:
        violations: list[str] = []

        if policy.min_confidence > 0 and intent.confidence < policy.min_confidence:
            violations.append(
                f"{policy.name}: confidence {intent.confidence:.2f} < {policy.min_confidence:.2f}"
            )

        if policy.allowed_regimes and belief.market_view.regime.name.lower() not in [
            r.lower() for r in policy.allowed_regimes
        ]:
            violations.append(
                f"{policy.name}: regime {belief.market_view.regime.name} not in allowed list"
            )

        if intent.quantity > 0 and policy.max_position_pct < 1.0:
            if intent.quantity > policy.max_position_pct * 100:
                violations.append(f"{policy.name}: quantity {intent.quantity} exceeds max position")

        return violations

    def request_promotion(self, request: PromotionRequest) -> PromotionRequest:
        """Evaluate a promotion request through promotion gates."""
        stage_order = list(PromotionStage)
        current_idx = stage_order.index(self._current_stage)
        target_idx = stage_order.index(request.target_stage)

        if target_idx != current_idx + 1:
            request.status = ApprovalStatus.REJECTED
            request.evidence["rejection_reason"] = (
                f"Cannot skip stages: {self._current_stage.value} → {request.target_stage.value}"
            )
        elif self._kill_switch:
            request.status = ApprovalStatus.REJECTED
            request.evidence["rejection_reason"] = "Kill switch active"
        else:
            request.status = ApprovalStatus.APPROVED
            self._current_stage = request.target_stage

        self._promotion_history.append(request)
        self._log(
            "promotion_evaluated",
            {
                "request_id": request.request_id,
                "target": request.target_stage.value,
                "status": request.status.name,
            },
        )
        return request

    def activate_kill_switch(self, reason: str = "") -> None:
        self._kill_switch = True
        self._log("kill_switch_activated", {"reason": reason}, severity=Severity.FATAL)

    def deactivate_kill_switch(self, operator_auth: str = "") -> None:
        if operator_auth:
            self._kill_switch = False
            self._log(
                "kill_switch_deactivated",
                {"operator": operator_auth},
                severity=Severity.CRITICAL,
            )

    def get_audit_log(self) -> list[dict[str, Any]]:
        return list(self._audit_log)

    def _log(
        self,
        action: str,
        details: dict[str, Any],
        severity: Severity = Severity.INFO,
    ) -> None:
        self._audit_log.append(
            {
                "action": action,
                "details": details,
                "severity": severity.name,
                "timestamp": time.time(),
            }
        )
