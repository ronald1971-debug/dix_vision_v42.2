"""End-to-end cognitive system integration test.

Wires:
  DiscoveryEngine -> MarketTheoryLayer -> ReasoningEngine
  -> EpistemologyEngine -> CognitiveAuditTrail
  -> CognitiveVersionRegistry -> SelfModel

Avoids UI/route drift by staying in the cognitive stack only.
"""

from __future__ import annotations

from cognitive_engine.discovery_engine.discovery import DiscoveryEngine
from cognitive_engine.epistemology_engine.epistemology_engine import (
    get_epistemology_engine,
)
from core.ontology.cognitive_audit_trail import CognitiveAuditRecorder
from core.ontology.cognitive_versioning import CognitiveVersionRegistry
from core.ontology.market_theory_layer import MarketTheoryLayer
from core.ontology.theory import Theory
from reasoning_engine import AbductiveReasoner, InductiveEngine, ObservedInstance
from self_model.capability_map import SelfModel


def test_full_cognitive_pipeline() -> None:
    discovery = DiscoveryEngine()
    self_model = SelfModel()
    theory_layer = MarketTheoryLayer(self_model=self_model)
    epistemology = get_epistemology_engine()
    audit_recorder = CognitiveAuditRecorder()
    versioning = CognitiveVersionRegistry()
    abductive = AbductiveReasoner()
    inductive = InductiveEngine()

    theory = Theory.create(
        object_id="theory_liquidity_migration",
        ts_ns=1_000,
        theory_name="Liquidity Migration Theory",
        domain="market",
        testable_hypotheses=("liquidity_drop_implies_spread_widen",),
        implementing_strategies=("strategy_liquidity_v1",),
    )
    theory_layer.register_theory(theory)

    d = discovery.record_discovery(
        category="market_structure",
        description="spread widening detected",
        confidence=0.8,
        discovered_by=" microstructure",
    )
    theory_layer.attach_evidence("Liquidity Migration Theory", d.discovery_id)

    posterior = abductive.reason(
        observation="spread_widened",
        candidate_ids=["unknown"],
    )
    assert posterior.best_hypothesis is None

    observations = [
        ObservedInstance("obs1", ("liquidity_drop", "spread_widen"), "spike", 0, 0.75),
        ObservedInstance("obs2", ("liquidity_drop", "spread_widen"), "spike", 0, 0.82),
    ]
    pattern = inductive.induce(observations)
    assert pattern is not None
    assert pattern.pattern_confidence == 1.0
    assert pattern.instance_count == 2

    epistemology.register_belief(
        belief_id="b_liquidity_migration",
        domain="market",
        claim="Liquidity migration underway",
        confidence=0.78,
        evidence_ids=[d.discovery_id],
        contributor="inductive_engine",
    )
    epistemology.revise_belief(
        belief_id="b_liquidity_migration",
        new_confidence=0.85,
        triggering_evidence=[d.discovery_id],
        reason="pattern confirmation",
    )

    beliefs = ()
    knowledge = ()
    audit_recorder.capture(
        trail_id="trail_full_system",
        beliefs=beliefs,
        knowledge=knowledge,
        ts_ns=1_001,
    )
    restored = audit_recorder.restore("trail_full_system")
    assert restored is not None
    assert restored.trail_id == "trail_full_system"

    version_entry = versioning.record_theory_version(theory)
    assert version_entry.theory_id == "theory_liquidity_migration"
    assert version_entry.version == "v1.0.0"

    capabilities = self_model.get_capability_map().domains
    assert any("theory:" in key for key in capabilities)
    assert capabilities.get("theory:liquidity_migration_theory", 0.0) > 0.0
