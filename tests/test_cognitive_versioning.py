"""Cognitive Versioning tests."""

from core.ontology.cognitive_versioning import CognitiveVersionRegistry, TheoryVersionEntry
from core.ontology.theory import Theory


class TestCognitiveVersionRegistry:
    def test_record_theory_version(self):
        registry = CognitiveVersionRegistry()
        th = Theory.create(object_id="th1", ts_ns=0, theory_name="Theory A", empirical_support=0.7)
        entry = registry.record_theory_version(th)
        assert entry.theory_id == "th1"
        assert entry.empirical_support == 0.7
        assert entry.version == "v1.0.0"

    def test_multiple_versions_increment(self):
        registry = CognitiveVersionRegistry()
        th = Theory.create(object_id="th1", ts_ns=1_000, theory_name="Theory A")
        first = registry.record_theory_version(th)
        second = registry.record_theory_version(th)
        assert first.version == "v1.0.0"
        assert second.version == "v2.0.0"
        history = registry.get_theory_history("th1")
        assert len(history) == 2

    def test_latest_theory_version_returns_last(self):
        registry = CognitiveVersionRegistry()
        th = Theory.create(object_id="th1", ts_ns=0, theory_name="Theory A")
        registry.record_theory_version(th)
        latest = registry.latest_theory_version("th1")
        assert latest is not None
        assert latest.theory_id == "th1"

    def test_missing_theory_history_empty(self):
        registry = CognitiveVersionRegistry()
        assert registry.get_theory_history("missing") == ()
        assert registry.latest_theory_version("missing") is None


class TestTheoryVersionEntry:
    def test_entry_fields(self):
        entry = TheoryVersionEntry(
            theory_id="th1",
            version="v1.0.0",
            empirical_support=0.8,
            falsified=False,
            revision_count=1,
            last_updated_ns=1_000,
            notes="test theory",
        )
        assert entry.theory_id == "th1"
        assert entry.version == "v1.0.0"
        assert entry.empirical_support == 0.8
        assert entry.falsified is False
        assert entry.revision_count == 1
        assert entry.last_updated_ns == 1_000
        assert entry.notes == "test theory"
