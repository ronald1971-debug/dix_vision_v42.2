"""Market Theory Layer tests."""

from core.ontology.market_theory_layer import MarketTheoryLayer
from core.ontology.theory import Theory
from self_model.capability_map import SelfModel


class TestMarketTheoryLayer:
    def test_register_and_get_theory(self):
        layer = MarketTheoryLayer()
        th = Theory.create(
            object_id="th1",
            ts_ns=0,
            theory_name="Liquidity Migration Theory",
            domain="market",
            testable_hypotheses=("liq_drop_causes_spread_widen",),
        )
        stored = layer.register_theory(th)
        assert layer.get_theory("Liquidity Migration Theory") is stored

    def test_attach_evidence_increases_support(self):
        layer = MarketTheoryLayer()
        th = Theory.create(
            object_id="th1",
            ts_ns=0,
            theory_name="Liquidity Migration Theory",
            empirical_support=0.5,
        )
        layer.register_theory(th)
        updated = layer.attach_evidence("Liquidity Migration Theory", "ev1")
        assert updated is not None
        assert updated.empirical_support > 0.5
        assert "ev1" in updated.evidence_ids

    def test_falsify_decreases_support(self):
        layer = MarketTheoryLayer()
        th = Theory.create(
            object_id="th1",
            ts_ns=0,
            theory_name="Liquidity Migration Theory",
            empirical_support=0.7,
            falsified=False,
        )
        layer.register_theory(th)
        updated = layer.falsify("Liquidity Migration Theory")
        assert updated is not None
        assert updated.falsified is True
        assert updated.empirical_support < 0.7

    def test_implementing_strategies(self):
        layer = MarketTheoryLayer()
        th = Theory.create(
            object_id="th1",
            ts_ns=0,
            theory_name="Theory A",
            implementing_strategies=("strat_001", "strat_002"),
        )
        layer.register_theory(th)
        assert layer.implementing_strategies("Theory A") == ("strat_001", "strat_002")

    def test_report_counts(self):
        layer = MarketTheoryLayer()
        th1 = Theory.create(object_id="th1", ts_ns=0, theory_name="Theory A", falsified=True)
        th2 = Theory.create(object_id="th2", ts_ns=0, theory_name="Theory B", falsified=False)
        layer.register_theory(th1)
        layer.register_theory(th2)
        report = layer.report()
        assert report["total_theories"] == 2
        assert report["falsified"] == 1
        assert report["supported"] == 0

    def test_self_model_capability_updates(self):
        sm = SelfModel()
        layer = MarketTheoryLayer(self_model=sm)
        th = Theory.create(object_id="th1", ts_ns=0, theory_name="Theory A", empirical_support=0.6)
        layer.register_theory(th)
        assert sm.get_capability_map().domains.get("theory:theory_a", 0.0) > 0.0
        layer.attach_evidence("Theory A", "ev1")
        assert sm.get_capability_map().domains.get("theory:theory_a", 0.0) > 0.0
