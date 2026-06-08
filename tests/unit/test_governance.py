"""Tests for governance kernel, authority graph, and constraint compiler."""

from core.mcos_kernel import BeliefState
from core.types import ApprovalStatus, ExecutionIntent, PromotionStage
from governance.authority_graph import AuthorityGraph, AuthorityLevel
from governance.mcos_constraint_compiler import ConstraintCompiler
from governance.mcos_kernel import GovernanceKernel, PolicyRule, PromotionRequest


def test_governance_kernel_approve():
    gk = GovernanceKernel()
    intent = ExecutionIntent(intent_id="t1", symbol="BTC/USD", direction="long", confidence=0.8)
    belief = BeliefState()
    decision = gk.evaluate_intent(intent, belief)
    assert decision.status == ApprovalStatus.APPROVED


def test_governance_kernel_reject_halted():
    gk = GovernanceKernel()
    gk.activate_kill_switch("test")
    intent = ExecutionIntent(intent_id="t2", symbol="BTC/USD", direction="long")
    belief = BeliefState()
    decision = gk.evaluate_intent(intent, belief)
    assert decision.status == ApprovalStatus.REJECTED


def test_governance_policy_violation():
    gk = GovernanceKernel()
    gk.register_policy(PolicyRule(name="min_conf", min_confidence=0.7))
    intent = ExecutionIntent(intent_id="t3", symbol="BTC/USD", direction="long", confidence=0.3)
    belief = BeliefState()
    decision = gk.evaluate_intent(intent, belief)
    assert decision.status == ApprovalStatus.REJECTED
    assert len(decision.policy_violations) > 0


def test_authority_graph():
    ag = AuthorityGraph()
    assert ag.can_override(AuthorityLevel.OPERATOR, AuthorityLevel.GOVERNANCE)
    assert ag.can_override(AuthorityLevel.GOVERNANCE, AuthorityLevel.EXECUTION)
    assert not ag.can_override(AuthorityLevel.EXECUTION, AuthorityLevel.OPERATOR)


def test_authority_graph_validate_action():
    ag = AuthorityGraph()
    ok, _ = ag.validate_action(AuthorityLevel.OPERATOR, "halt")
    assert ok
    ok, _ = ag.validate_action(AuthorityLevel.COGNITION, "halt")
    assert not ok


def test_authority_chain_order():
    ag = AuthorityGraph()
    path = ag.authority_path()
    assert path == ["Operator", "Governance", "Cognition", "Execution", "Capital"]


def test_constraint_compiler():
    gk = GovernanceKernel()
    gk.register_policy(PolicyRule(name="pos_limit", max_position_pct=0.05, min_confidence=0.5))
    compiler = ConstraintCompiler(gk)
    cs = compiler.compile()
    assert cs.max_position_pct == 0.05
    assert cs.min_confidence == 0.5
    assert cs.allows_execution()


def test_promotion_sequential():
    gk = GovernanceKernel()
    req = PromotionRequest(
        current_stage=PromotionStage.SIMULATION,
        target_stage=PromotionStage.BACKTEST,
    )
    result = gk.request_promotion(req)
    assert result.status == ApprovalStatus.APPROVED
    assert gk.current_stage == PromotionStage.BACKTEST


def test_promotion_no_skip():
    gk = GovernanceKernel()
    req = PromotionRequest(
        current_stage=PromotionStage.SIMULATION,
        target_stage=PromotionStage.PAPER,
    )
    result = gk.request_promotion(req)
    assert result.status == ApprovalStatus.REJECTED
