"""Integration tests for cognitive_engine v3.7 new modules.

Tests the 14 new cognitive engines added to bring DIXVISION from
a sophisticated system toward a true cognitive platform.
"""


import pytest

from cognitive_engine.epistemology_engine import (
    EpistemologyEngine,
    get_epistemology_engine,
)


def test_epistemology_register_and_lineage():
    eng = EpistemologyEngine()
    lin = eng.register_belief(
        belief_id="B1",
        domain="market",
        claim="bullish",
        confidence=0.8,
        evidence_ids=["EV1", "EV2"],
        contributor="signal_engine",
    )
    assert lin["evidence_count"] == 2
    assert lin["contributor_chain"] == ("signal_engine",)
    assert lin["revision_count"] == 0


def test_epistemology_add_evidence():
    eng = EpistemologyEngine()
    eng.register_belief("B1", "market", "bullish", 0.8, ["EV1"], "sig")
    eng.add_evidence("B1", "EV2", "trader_model", "signal", 0.5)
    lineage = eng.get_lineage("B1")
    assert lineage["evidence_count"] == 2
    assert "trader_model" in lineage["contributor_chain"]


def test_epistemology_revise_detects_magical_jump():
    eng = EpistemologyEngine()
    eng.register_belief("B1", "market", "bullish", 0.8, ["EV1"], "sig")
    result = eng.revise_belief("B1", 0.2, [], "new evidence")
    assert result.get("violation") == "MAGICAL_BELIEF_JUMP"


def test_epistemology_singleton():
    a = get_epistemology_engine()
    b = get_epistemology_engine()
    assert a is b


def test_epistemology_history():
    eng = EpistemologyEngine()
    eng.register_belief("B1", "market", "bullish", 0.8, [], "sig")
    eng.revise_belief("B1", 0.6, ["EV2"], "correction")
    hist = eng.get_belief_history("B1")
    assert len(hist) >= 1


from cognitive_engine.contradiction_engine import (
    ContradictionEngine,
    get_contradiction_engine,
)


def test_contradiction_exact_opposites():
    eng = ContradictionEngine()
    eng.register_belief("B1", "market", "bullish", 0.9, 1000)
    found2 = eng.register_belief("B2", "market", "bearish", 0.85, 1001)
    assert len(found2) == 1
    c = found2[0]
    assert c["belief_a_id"] == "B1"
    assert c["belief_b_id"] == "B2"
    assert c["claim_a"] == "bullish"
    assert c["claim_b"] == "bearish"


def test_contradiction_resolve():
    eng = ContradictionEngine()
    eng.register_belief("B1", "market", "bullish", 0.9, 1000)
    eng.register_belief("B2", "market", "bearish", 0.85, 1001)
    active = eng.get_active_contradictions()
    assert len(active) == 1
    cid = active[0]["contradiction_id"]
    assert eng.resolve_contradiction(cid, "B1", "accepted B1")
    assert len(eng.get_active_contradictions()) == 0


def test_contradiction_summary():
    eng = ContradictionEngine()
    eng.register_belief("B1", "market", "bullish", 0.9, 1000)
    s = eng.summary()
    assert s["registered_beliefs"] == 1
    assert s["active_contradictions"] == 0


def test_contradiction_singleton():
    a = get_contradiction_engine()
    b = get_contradiction_engine()
    assert a is b


from cognitive_engine.truth_maintenance import (
    TruthMaintenanceEngine,
    get_truth_maintenance,
)


def test_tms_register_belief():
    eng = TruthMaintenanceEngine()
    bf = eng.register_belief("F1", "market", "regime", "trending", 0.7, ["EV1"], 1000)
    assert bf.confidence == 0.7


def test_tms_revision_threshold():
    eng = TruthMaintenanceEngine()
    eng.register_belief("F1", "market", "regime", "trending", 0.7, ["EV1"], 1000)
    rev = eng.add_evidence_and_revise("F1", "EV2", 0.1, 1001)
    assert rev is None  # delta too small
    # Manual revision validates threshold logic
    rev2 = eng.revise_manually("F1", 0.55, "regime weakening")
    assert rev2 is not None
    assert rev2["delta"] >= 0.10


def test_tms_manual_revise():
    eng = TruthMaintenanceEngine()
    eng.register_belief("F1", "market", "regime", "trending", 0.7, [], 1000)
    rev = eng.revise_manually("F1", 0.3, "regime change")
    assert rev["old_confidence"] == 0.7
    assert rev["new_confidence"] == 0.3


def test_tms_singleton():
    a = get_truth_maintenance()
    b = get_truth_maintenance()
    assert a is b


from cognitive_engine.failure_engine import (
    FailureEngine,
    get_failure_engine,
)


def test_failure_classify_and_resolve():
    eng = FailureEngine()
    rec = eng.classify("F1", "strategy", "S1", "P1", "slippage", "HIGH")
    assert rec.category == "strategy"
    assert eng.mark_resolved("F1")
    r = eng.get_record("F1")
    assert r["resolved"] is True


def test_failure_pattern_report():
    eng = FailureEngine()
    eng.classify("F1", "strategy", "S1", "P1", "slippage")
    eng.classify("F2", "prediction", "S2", "P2", "wrong_direction")
    rep = eng.pattern_report()
    assert rep["total_failures"] >= 2


def test_failure_singleton():
    a = get_failure_engine()
    b = get_failure_engine()
    assert a is b


from cognitive_engine.meta_learning import (
    MetaLearner,
    get_meta_learner,
)


def test_meta_learning_record():
    ml = MetaLearner()
    perf = ml.record_sample("L1", "online", 0.9, 0.1)
    assert perf.knowledge_gain == 0.9
    assert perf.compute_cost == 0.1


def test_meta_learning_best_approach():
    ml = MetaLearner()
    ml.record_sample("L1", "online", 0.5, 0.1)
    ml.record_sample("L2", "batch", 0.9, 0.05)
    best = ml.best_approach()
    assert best is not None
    assert best["lane_id"] == "L2"


def test_meta_learning_singleton():
    a = get_meta_learner()
    b = get_meta_learner()
    assert a is b


from cognitive_engine.self_awareness import (
    SelfAwarenessEngine,
    get_self_awareness,
)


def test_self_awareness_capabilities():
    sa = SelfAwarenessEngine()
    sa.register_capability("C1", "signal_processing", 0.8)
    rep = sa.report()
    assert "C1" in rep["known_capabilities"]


def test_self_awareness_gap_raises_recommendation():
    sa = SelfAwarenessEngine()
    sa.raise_gap("G1", "liquidity modeling", "HIGH")
    rep = sa.report()
    assert "G1" in rep["knowledge_gaps"]
    assert len(rep["recommended_improvements"]) >= 1


def test_self_awareness_confidence():
    sa = SelfAwarenessEngine()
    c = sa._self_model_confidence()
    assert c == 0.0
    sa.register_capability("C1", "x", 0.5)
    c2 = sa._self_model_confidence()
    assert c2 > 0.0


def test_self_awareness_singleton():
    a = get_self_awareness()
    b = get_self_awareness()
    assert a is b


from cognitive_engine.cognitive_time import (
    CognitiveTime,
    get_cognitive_time,
)


def test_cognitive_time_history():
    ct = CognitiveTime()
    ct.record_belief("B1", "market", "bullish", 0.8, "signal")
    ct.record_belief("B1", "market", "bearish", 0.7, "trader")
    hist = ct.get_history("B1")
    assert len(hist) == 2
    assert hist[0]["confidence"] == 0.8


def test_cognitive_time_projection():
    ct = CognitiveTime()
    proj = ct.project_belief("B1", "bullish", 0.6, 3600)
    assert proj["projected_confidence"] == 0.6
    assert proj["horizon_ns"] == 3600


def test_cognitive_time_singleton():
    a = get_cognitive_time()
    b = get_cognitive_time()
    assert a is b


from cognitive_engine.discovery_engine import (
    DiscoveryEngine,
    get_discovery_engine,
)


def test_discovery_record():
    de = DiscoveryEngine()
    d = de.record_discovery("archetype", "novel momentum trader", 0.75, "cluster_v2")
    assert d.category == "archetype"
    results = de.search()
    assert len(results) >= 1


def test_discovery_filter():
    de = DiscoveryEngine()
    de.record_discovery("market_structure", "hidden range", 0.6, "regime")
    de.record_discovery("archetype", "panic buyer", 0.7, "cluster")
    archs = de.get_discoveries("archetype")
    assert len(archs) == 1
    assert archs[0]["category"] == "archetype"


def test_discovery_singleton():
    a = get_discovery_engine()
    b = get_discovery_engine()
    assert a is b


from cognitive_engine.concept_formation import (
    ConceptFormationEngine,
    get_concept_formation,
)


def test_concept_formation():
    cf = ConceptFormationEngine()
    c = cf.form_concept(
        "Liquidity Trap",
        "Price stalls at a level where liquidity is concentrated",
        ["low_volume", "consolidation", "order_cluster"],
        ["BTC 2024-01 range"],
        0.85,
    )
    assert c.name == "Liquidity Trap"
    assert c.usage_count == 0
    cf.use_concept(c.concept_id)
    c2 = cf.get_concept(c.concept_id)
    assert c2.usage_count == 1


def test_concept_find_by_name():
    cf = ConceptFormationEngine()
    cf.form_concept("False Breakout", "Breakout that immediately reverses",
                    ["spike", "rejection"], ["ETH 2024-03"], 0.7)
    found = cf.find_by_name("false breakout")
    assert found is not None
    assert found.name == "False Breakout"


def test_concept_formation_singleton():
    a = get_concept_formation()
    b = get_concept_formation()
    assert a is b


from cognitive_engine.institutional_memory import (
    InstitutionalMemory,
    get_institutional_memory,
)


def test_institutional_memory_store_recall():
    im = InstitutionalMemory()
    e = im.store("discovery", "Novel Archetype", "New momentum cluster found", 0.9)
    assert e.category == "discovery"
    items = im.recall("discovery")
    assert len(items) >= 1
    assert items[-1]["title"] == "Novel Archetype"


def test_institutional_memory_summary():
    im = InstitutionalMemory()
    im.store("mistake", "Bad Trade", "Oversized", 0.5)
    im.store("evolution", "Strategy Mut", "New param set", 0.7)
    s = im.summary()
    assert "mistake" in s["by_category"]
    assert "evolution" in s["by_category"]


def test_institutional_memory_singleton():
    a = get_institutional_memory()
    b = get_institutional_memory()
    assert a is b


from cognitive_engine.collective_intelligence import (
    CollectiveIntelligenceEngine,
    get_collective_intelligence,
)


def test_collective_index_trader():
    ci = CollectiveIntelligenceEngine()
    p = ci.index_trader("T1", ["momentum", "aggressive"], cluster="momentum")
    assert p.trader_id == "T1"
    assert p.cluster == "momentum"


def test_collective_clusters():
    ci = CollectiveIntelligenceEngine()
    ci.index_trader("T1", ["momentum"], "momentum")
    ci.index_trader("T2", ["momentum"], "momentum")
    ci.index_trader("T3", ["value"], "value")
    ci.define_cluster("C1", "Momentum Cluster", ["T1", "T2"])
    cl = ci.get_cluster("C1")
    assert cl["member_count"] == 2


def test_collective_singleton():
    a = get_collective_intelligence()
    b = get_collective_intelligence()
    assert a is b


from cognitive_engine.cognitive_economy import (
    CognitiveEconomy,
    get_cognitive_economy,
)


def test_cognitive_economy_allocate():
    ce = CognitiveEconomy()
    a = ce.allocate("cpu", "trader_cluster_v2", 0.85)
    assert a.resource_type == "cpu"
    assert a.expected_gain == 0.85


def test_cognitive_economy_report():
    ce = CognitiveEconomy()
    ce.allocate("cpu", "X", 0.5)
    ce.allocate("memory", "Y", 0.3)
    r = ce.report()
    assert r["total_allocations"] == 2


def test_cognitive_economy_singleton():
    a = get_cognitive_economy()
    b = get_cognitive_economy()
    assert a is b


from cognitive_engine.recursive_governance import (
    RecursiveGovernance,
    get_recursive_governance,
)


def test_recursive_governance_approve():
    rg = RecursiveGovernance()
    g = rg.gate_improvement("P1", 0.2, 0.15)
    assert g.approved is True


def test_recursive_governance_reject():
    rg = RecursiveGovernance()
    g = rg.gate_improvement("P2", 0.2, 0.25)
    assert g.approved is False


def test_recursive_governance_audit():
    rg = RecursiveGovernance()
    rg.gate_improvement("P1", 0.2, 0.15)
    rg.gate_improvement("P2", 0.2, 0.25)
    a = rg.audit()
    assert a["total_gates"] == 2
    assert a["approved"] == 1
    assert a["rejected"] == 1


def test_recursive_governance_singleton():
    a = get_recursive_governance()
    b = get_recursive_governance()
    assert a is b


from cognitive_engine.constitution_v2 import (
    ConstitutionV2,
    get_constitution_v2,
)


def test_constitution_record_case():
    c2 = ConstitutionV2()
    cl = c2.record_case("INC-341", "system failure", "limit retries to 3")
    assert cl.outcome == "system failure"
    assert cl.rule_added in c2._rules


def test_constitution_lookup():
    c2 = ConstitutionV2()
    c2.record_case("INC-1", "memory leak", "add pool limit")
    c2.record_case("INC-2", "timeout", "add circuit breaker")
    results = c2.lookup("memory")
    assert len(results) == 1
    assert results[0]["incident_id"] == "INC-1"


def test_constitution_singleton():
    a = get_constitution_v2()
    b = get_constitution_v2()
    assert a is b


from cognitive_engine.digital_twin import (
    CognitiveDigitalTwin,
    get_digital_twin,
)


def test_digital_twin_simulate():
    dt = CognitiveDigitalTwin()
    r = dt.simulate("new_algorithm", {"type": "momentum", "threshold": 0.7})
    assert r.scenario == "new_algorithm"
    assert r.passed is True


def test_digital_twin_report():
    dt = CognitiveDigitalTwin()
    dt.simulate("algorithm", {"x": 1})
    dt.simulate("governance_rule", {"y": 2})
    rep = dt.report()
    assert rep["total_simulations"] == 2


def test_digital_twin_singleton():
    a = get_digital_twin()
    b = get_digital_twin()
    assert a is b


# ------------------------------------------------------------------
# End-to-end: verify CognitiveGovernanceEngine exposes all new engines
# ------------------------------------------------------------------

def test_governance_engine_exposes_all_new_engines():
    from cognitive_governance.engine import get_cognitive_governance

    gov = get_cognitive_governance()

    expected = [
        "epistemology",
        "contradiction",
        "truth_maintenance",
        "failure_engine",
        "self_awareness",
        "meta_learner",
        "discovery",
        "concept_formation",
        "institutional_memory",
        "collective_intelligence",
        "cognitive_economy",
        "recursive_governance",
        "constitution_v2",
        "digital_twin",
    ]

    for attr in expected:
        assert hasattr(gov, attr), f"Missing attribute: {attr}"
        obj = getattr(gov, attr)
        assert obj is not None, f"Attribute {attr} is None"


def test_contracts_have_new_violation_kinds():
    from core.contracts.cognitive_governance import CognitiveViolationKind

    required = {
        "BELIEF_LINEAGE_MISSING",
        "BELIEF_LINEAGE_BROKEN",
        "BELIEF_REVISION_TRIGGERED",
        "BELIEF_CONTRADICTION",
        "SELF_AWARENESS_VIOLATION",
        "FAILURE_CLASSIFICATION_PENDING",
        "FAILURE_REPEAT",
        "META_LEARNING_SIGNAL",
    }
    for k in required:
        assert k in CognitiveViolationKind.__members__, f"Missing violation: {k}"


def test_events_have_new_types():
    from core.contracts.events import SystemEventKind

    required = {
        "BELIEF_EVIDENCE_ADDED",
        "BELIEF_LINEAGE_UPDATED",
        "BELIEF_CONTRADICTION_DETECTED",
        "BELIEF_CONTRADICTION_RESOLVED",
        "BELIEF_REVISED",
        "EVIDENCE_REWEIGHED",
        "FAILURE_CLASSIFIED",
        "FAILURE_PATTERN_DETECTED",
        "META_LEARNING_REPORT",
        "LEARNING_PROCESS_OPTIMIZED",
        "SELF_MODEL_UPDATED",
        "KNOWLEDGE_GAP_RAISED",
    }
    for k in required:
        assert k in SystemEventKind.__members__, f"Missing event: {k}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
