"""Integration test – full cognitive pipeline end-to-end."""

from core.mcos_kernel import BeliefState
from governance.authority_graph import AuthorityGraph
from governance.mcos_constraint_compiler import ConstraintCompiler
from governance.mcos_kernel import GovernanceKernel, PolicyRule
from governance.unified_graph import UnifiedGovernanceGraph
from mind.beliefs import BeliefSystem
from mind.hypotheses import HypothesisEngine
from mind.intent import IntentGenerator
from mind.knowledge import KnowledgeBase
from mind.observation import Observation, ObservationProcessor, ObservationType
from runtime.certification import ProductionCertifier
from runtime.mcos_cognitive_spine import CognitiveSpine
from state.ledger.mcos_event_store import EventStore
from state.ledger.mcos_writer import LedgerWriter


def test_full_cognitive_cycle():
    """End-to-end: observations → knowledge → beliefs → hypotheses → intents."""
    governance = GovernanceKernel()
    compiler = ConstraintCompiler(governance)
    constraints = compiler.compile()

    observer = ObservationProcessor()
    knowledge = KnowledgeBase()
    beliefs = BeliefSystem()
    hypotheses = HypothesisEngine()
    intent_gen = IntentGenerator()

    spine = CognitiveSpine(
        observation_processor=observer,
        knowledge_base=knowledge,
        belief_system=beliefs,
        hypothesis_engine=hypotheses,
        intent_generator=intent_gen,
        constraints=constraints,
    )

    observations = [
        Observation(
            obs_type=ObservationType.PRICE_TICK,
            symbol="BTC/USD",
            value=50000.0,
            confidence=0.9,
        ),
        Observation(
            obs_type=ObservationType.REGIME_SIGNAL,
            value=0.8,
            confidence=0.8,
            context={"regime": "trending_up"},
        ),
    ]

    result = spine.run_cycle(observations)
    assert result.success
    assert len(result.stages_completed) == 10  # all 10 stages
    assert result.observations_processed == 2
    assert result.knowledge_acquired >= 1


def test_governed_execution_pipeline():
    """End-to-end: intent → governance → execution → ledger."""
    governance = GovernanceKernel()
    governance.register_policy(PolicyRule(name="min_conf", min_confidence=0.5))

    store = EventStore()
    ledger = LedgerWriter(store)

    from core.types import ExecutionIntent
    from execution.mcos_adapter_router import AdapterRouter
    from execution.mcos_orchestrator import ExecutionOrchestrator

    router = AdapterRouter()
    orchestrator = ExecutionOrchestrator(governance, router, ledger)

    intent = ExecutionIntent(
        intent_id="test_intent",
        symbol="BTC/USD",
        direction="long",
        quantity=1.0,
        confidence=0.8,
        reasoning="Test trade",
    )
    belief = BeliefState()
    result = orchestrator.process_intent(intent, belief)

    assert result.was_executed
    assert result.trade_result is not None
    assert store.count >= 2  # governance event + execution events


def test_unified_governance():
    """Test unified governance graph with all domains."""
    unified = UnifiedGovernanceGraph()
    kernel = unified.kernel

    assert unified.get_total_rule_count() > 0
    assert len(unified.get_all_domains()) == 4

    from core.types import ExecutionIntent
    intent = ExecutionIntent(
        intent_id="ug_test",
        symbol="BTC/USD",
        direction="long",
        confidence=0.9,
        quantity=1.0,
    )
    belief = BeliefState()
    decision = kernel.evaluate_intent(intent, belief)
    assert decision.status.name in ("APPROVED", "REJECTED")


def test_certification_report():
    """Test production certification audit."""
    governance = GovernanceKernel()
    governance.register_policy(PolicyRule(name="test_policy"))
    authority = AuthorityGraph()
    store = EventStore()
    store.append("governance", "test", {"init": True})

    certifier = ProductionCertifier(governance, authority, store)
    report = certifier.certify()

    assert len(report.checks) >= 8
    assert report.passed_count > 0
    chain_check = [c for c in report.checks if "Authority chain" in c.name]
    assert len(chain_check) == 1
    assert chain_check[0].result.name == "PASSED"
