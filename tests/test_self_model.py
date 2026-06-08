"""Self-Model and Discovery integration test."""

from cognitive_engine.discovery_engine.discovery import Discovery, DiscoveryEngine
from self_model.capability_map import SelfModel


class TestSelfModelIntegration:
    def test_record_discovery_raises_capability(self):
        sm = SelfModel()
        d = Discovery(
            discovery_id="d1",
            category="archetype",
            description="novel momentum",
            confidence=0.75,
            discovered_by="cluster_v2",
            ts_ns=0,
        )
        before = sm.get_capability_map().domains.get("archetype", 0.0)
        sm.record_discovery({
            "object_type": d.category,
            "category": d.category,
            "confidence": d.confidence,
        })
        after = sm.get_capability_map().domains.get("archetype", 0.0)
        assert after > before

    def test_record_discoveries_batch(self):
        sm = SelfModel()
        discoveries = [
            {"object_type": "market_structure", "confidence": 0.6},
            {"object_type": "market_structure", "confidence": 0.7},
        ]
        sm.record_discoveries(discoveries)
        assert sm.get_capability_map().domains.get("market_structure", 0.0) > 0.0

    def test_discovery_projection_matches_self_model_input(self):
        de = DiscoveryEngine()
        d = de.record_discovery("archetype", "panic buyer", 0.7, "cluster")
        sm = SelfModel()
        sm.record_discovery({
            "object_id": d.discovery_id,
            "category": d.category,
            "confidence": d.confidence,
        })
        assert "archetype" in sm.get_capability_map().domains
