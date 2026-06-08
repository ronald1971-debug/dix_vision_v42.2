"""Integration test for Cognitive Object Model and Reasoning Engine.

Tests the minimal set of entities and interactions that prove
DIXVISION's cognitive infrastructure works.
"""

from __future__ import annotations

from core.ontology.audit_trail import AuditTrail, BeliefTransition, CognitiveAuditTrail
from core.ontology.base import CognitiveObject, ObjectKind, ObjectVersion
from core.ontology.belief import CognitiveBelief
from core.ontology.evidence import Evidence
from core.ontology.execution import Execution
from core.ontology.knowledge import Knowledge
from core.ontology.market import Market
from core.ontology.strategy import Strategy
from core.ontology.theory import Theory
from core.ontology.trader import Trader


class TestCognitiveObjectModel:
    def test_object_kind_enum(self):
        assert ObjectKind.TRADER == "TRADER"
        assert ObjectKind.BELIEF == "BELIEF"
        assert ObjectKind.THEORY == "THEORY"

    def test_object_version(self):
        v = ObjectVersion(1, 0, 0)
        assert str(v) == "1.0.0"

    def test_cognitive_object_immutability(self):
        obj = CognitiveObject(
            object_id="test",
            object_type=ObjectKind.MARKET,
            ts_ns=1_000_000_000,
            version=ObjectVersion(),
        )
        replaced = obj.replace(ts_ns=2_000_000_000)
        assert obj.ts_ns == 1_000_000_000
        assert replaced.ts_ns == 2_000_000_000

    def test_with_evidence_chain(self):
        obj = CognitiveObject(
            object_id="obj1",
            object_type=ObjectKind.BELIEF,
            ts_ns=0,
            version=ObjectVersion(),
        )
        obj2 = obj.with_evidence("ev1", "ev2")
        assert obj2.evidence_ids == ("ev1", "ev2")

    def test_with_contributor_chain(self):
        obj = CognitiveObject(
            object_id="obj1",
            object_type=ObjectKind.STRATEGY,
            ts_ns=0,
            version=ObjectVersion(),
        )
        obj2 = obj.with_contributor("INDIRA")
        obj3 = obj2.with_contributor("EVOLUTION")
        assert obj3.contributor_chain == ("INDIRA", "EVOLUTION")


class TestDomainObjects:
    def test_trader_creation(self):
        t = Trader.create(object_id="t1", ts_ns=0, trader_id="TRADER_001", trader_type="SCALPER")
        assert t.object_type == ObjectKind.TRADER
        assert t.is_scalper()
        assert not t.is_momentum()

    def test_strategy_creation(self):
        s = Strategy.create(
            object_id="s1",
            ts_ns=0,
            strategy_id="STRAT_001",
            lifecycle="APPROVED",
        )
        assert s.is_approved()
        assert not s.is_retired()

    def test_market_creation(self):
        m = Market.create(object_id="m1", ts_ns=0, symbol="BTC-USD", regime_confidence=0.85)
        assert m.is_confident()
        assert m.symbol == "BTC-USD"

    def test_belief_creation(self):
        b = CognitiveBelief.create(
            object_id="b1",
            ts_ns=0,
            domain="market",
            claim="BTC bullish",
            confidence=0.75,
        )
        assert b.is_confident()
        assert not b.is_certain()

    def test_knowledge_creation(self):
        k = Knowledge.create(
            object_id="k1",
            ts_ns=0,
            knowledge_domain="trader",
            validation_sources=3,
            maturity="mature",
        )
        assert k.is_validated()

    def test_theory_creation(self):
        th = Theory.create(
            object_id="th1",
            ts_ns=0,
            theory_name="Liquidity Migration Theory",
            domain="market",
            testable_hypotheses=("liq_drop_causes_spread_widen",),
            implementing_strategies=("strat_001",),
        )
        assert th.is_falsifiable()
        assert th.has_implementation()
        assert not th.is_supported()

    def test_execution_creation(self):
        e = Execution.create(
            object_id="e1",
            ts_ns=0,
            intent_id="intent_001",
            symbol="BTC-USD",
            status="FILLED",
        )
        assert e.is_filled()
        assert not e.is_rejected()

    def test_evidence_creation(self):
        ev = Evidence.create(
            object_id="ev1",
            ts_ns=0,
            evidence_type="tick",
            source="binance",
            supports=("b1",),
        )
        assert ev.is_supporting("b1")
        assert not ev.is_contradicting("b1")

    def test_audit_trail(self):
        trail = AuditTrail.create(
            object_id="audit1",
            ts_ns=0,
            audit_type="approval",
            actor="governance",
            outcome="success",
        )
        assert trail.succeeded()
        assert not trail.failed()

    def test_cognitive_audit_trail(self):
        trail = CognitiveAuditTrail.create(
            object_id="cog_audit1",
            ts_ns=0,
            decision_id="dec_001",
            hypothesis="BTC bullish",
            test_result="confirmed",
        )
        assert not trail.has_large_shifts()

    def test_belief_transition(self):
        transition = BeliefTransition(
            belief_id="b1",
            previous_confidence=0.3,
            new_confidence=0.8,
            triggering_evidence_ids=("ev1",),
        )
        assert transition.is_large_shift()
        assert transition.confidence_delta == 0.5


class TestReasoningEngines:
    def test_abductive_reasoner(self):
        from reasoning_engine import AbductiveReasoner, Hypothesis
        r = AbductiveReasoner()
        h1 = Hypothesis(hypothesis_id="h1", description="liq_provider_exit", prior_probability=0.5)
        h2 = Hypothesis(hypothesis_id="h2", description="large_order", prior_probability=0.4)
        r.register_hypothesis(h1)
        r.register_hypothesis(h2)
        result = r.reason("spread_widened", ["h1", "h2"])
        assert result.best_hypothesis is not None
        assert result.confidence > 0.0

    def test_deductive_engine(self):
        from reasoning_engine import DeductiveEngine, Rule
        e = DeductiveEngine()
        rule = Rule(
            rule_id="r1",
            antecedent=("volatile", "liquidity_low"),
            consequent="elevated_risk",
            confidence=1.0,
        )
        e.register_rule(rule)
        conclusions = e.deduce({"volatile", "liquidity_low"})
        assert len(conclusions) == 1
        assert conclusions[0].conclusion == "elevated_risk"

    def test_inductive_engine(self):
        from reasoning_engine import InductiveEngine, ObservedInstance
        e = InductiveEngine()
        observations = [
            ObservedInstance(f"obs_{i}", ("liq_drop", "spread_widen"), "spike", 0, 0.8)
            for i in range(20)
        ]
        pattern = e.induce(observations)
        assert pattern is not None
        assert pattern.is_robust()


