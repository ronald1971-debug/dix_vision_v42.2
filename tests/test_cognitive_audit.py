"""Cognitive Audit Trail integration tests."""

from core.ontology.audit_trail import BeliefTransition, CognitiveAuditTrail
from core.ontology.belief import CognitiveBelief
from core.ontology.cognitive_audit_trail import CognitiveAuditRecorder
from core.ontology.knowledge import Knowledge


class TestCognitiveAuditRecorder:
    def test_capture_stores_snapshot(self):
        recorder = CognitiveAuditRecorder()
        beliefs = (CognitiveBelief.create(object_id="b1", ts_ns=0, domain="market", claim="bullish", confidence=0.8),)
        knowledge = (Knowledge.create(object_id="k1", ts_ns=0, knowledge_domain="trader", validation_sources=2),)
        capture = recorder.capture("trail_1", beliefs, knowledge, ts_ns=1_000_000_000)
        assert capture.belief_snapshot_count == 1
        assert capture.knowledge_snapshot_count == 1

    def test_restore_returns_capture(self):
        recorder = CognitiveAuditRecorder()
        beliefs = (CognitiveBelief.create(object_id="b1", ts_ns=0, domain="market", claim="bullish", confidence=0.8),)
        knowledge = (Knowledge.create(object_id="k1", ts_ns=0, knowledge_domain="trader", validation_sources=2),)
        recorder.capture("trail_1", beliefs, knowledge, ts_ns=1_000_000_000)
        restored = recorder.restore("trail_1")
        assert restored is not None
        assert restored.trail_id == "trail_1"

    def test_restore_missing_returns_none(self):
        recorder = CognitiveAuditRecorder()
        assert recorder.restore("missing") is None


class TestCognitiveAuditTrailIntegration:
    def test_cognitive_audit_trail_with_transitions(self):
        transition = BeliefTransition(
            belief_id="b1",
            previous_confidence=0.3,
            new_confidence=0.8,
            triggering_evidence_ids=("ev1",),
        )
        trail = CognitiveAuditTrail.create(
            object_id="trail1",
            ts_ns=0,
            transitions=(transition,),
        )
        assert trail.has_large_shifts()

    def test_involves_belief(self):
        transition = BeliefTransition(
            belief_id="b1",
            previous_confidence=0.3,
            new_confidence=0.8,
        )
        trail = CognitiveAuditTrail.create(
            object_id="trail1",
            ts_ns=0,
            transitions=(transition,),
        )
        assert trail.involves_belief("b1")
        assert not trail.involves_belief("b2")

class TestCognitiveAuditRecorderMultiple:
    def test_multiple_captures_restore(self):
        recorder = CognitiveAuditRecorder()
        beliefs = (CognitiveBelief.create(object_id="b1", ts_ns=0, domain="market", claim="bullish", confidence=0.8),)
        knowledge = (Knowledge.create(object_id="k1", ts_ns=0, knowledge_domain="trader", validation_sources=2),)
        recorder.capture("trail_1", beliefs, knowledge, ts_ns=1_000_000_000)
        beliefs2 = (CognitiveBelief.create(object_id="b2", ts_ns=0, domain="market", claim="bearish", confidence=0.6),)
        knowledge2 = (Knowledge.create(object_id="k2", ts_ns=0, knowledge_domain="trader", validation_sources=1),)
        recorder.capture("trail_2", beliefs2, knowledge2, ts_ns=2_000_000_000)
        assert recorder.restore("trail_1") is not None
        assert recorder.restore("trail_2") is not None
        assert recorder.restore("trail_1").trail_id == "trail_1"
        assert recorder.restore("trail_2").trail_id == "trail_2"
