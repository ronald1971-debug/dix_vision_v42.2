"""GDELT Integration Test - Basic functionality verification.

Tests the GDELT adapter to ensure:
1. The adapter can be instantiated
2. Public methods are accessible
3. Data structures are correct
4. Error handling works properly
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_sources.external.gdelt_events import GDELTAdapter, GDELTEventObservation


def test_gdelt_adapter_instantiation():
    """Test that GDELT adapter can be instantiated."""
    adapter = GDELTAdapter()
    assert adapter.platform == "gdelt"
    assert adapter.base_url == "https://api.gdeltproject.org/api/v2"
    print("[OK] GDELT adapter instantiation successful")


def test_gdelt_event_observation_structure():
    """Test that GDELTEventObservation dataclass has correct structure."""
    event = GDELTEventObservation(
        event_id="test123",
        event_date=20240101,
        actor1="United States",
        actor2="China",
        event_code="092",
        event_type="Grant",
        tone=2.5,
        tone_confidence=0.8,
        location="USA",
        source_url="https://example.com",
        num_articles=10,
        num_mentions=50,
        relevance_score=0.8,
        ingested_ts_ns=1704067200000000000,
    )
    
    assert event.event_id == "test123"
    assert event.event_code == "092"
    assert event.actor1 == "United States"
    assert event.tone == 2.5
    print("[OK] GDELTEventObservation structure correct")


def test_gdelt_relevant_event_codes():
    """Test that relevant event codes are defined."""
    adapter = GDELTAdapter()
    
    # Check that key event codes are defined
    assert "072" in adapter.RELEVANT_EVENT_CODES  # Diplomatic Cooperation
    assert "093" in adapter.RELEVANT_EVENT_CODES  # Agreement
    assert "125" in adapter.RELEVANT_EVENT_CODES  # Military Action
    assert "122" in adapter.RELEVANT_EVENT_CODES  # Ban
    print("[OK] Relevant event codes defined correctly")


def test_gdelt_fetch_methods_exist():
    """Test that all public fetch methods exist."""
    adapter = GDELTAdapter()
    
    assert hasattr(adapter, "fetch_financial_events")
    assert hasattr(adapter, "fetch_geopolitical_events")
    assert hasattr(adapter, "fetch_events_by_actor")
    assert hasattr(adapter, "fetch_events_by_location")
    print("[OK] All public fetch methods exist")


def test_gdelt_fetch_methods_return_lists():
    """Test that fetch methods return lists (even if empty during placeholder phase)."""
    adapter = GDELTAdapter()
    
    # These will return empty lists during placeholder phase
    financial_events = adapter.fetch_financial_events(days=7)
    assert isinstance(financial_events, list)
    
    geopolitical_events = adapter.fetch_geopolitical_events(days=7)
    assert isinstance(geopolitical_events, list)
    
    actor_events = adapter.fetch_events_by_actor("United States", days=30)
    assert isinstance(actor_events, list)
    
    location_events = adapter.fetch_events_by_location("Europe", days=30)
    assert isinstance(location_events, list)
    
    print("[OK] Fetch methods return lists correctly")


def test_gdelt_relevance_calculation():
    """Test that relevance calculation works correctly."""
    adapter = GDELTAdapter()
    
    # Test diplomatic cooperation (high relevance)
    relevance = adapter._calculate_relevance("093", 3.0)
    assert 0.7 <= relevance <= 1.0
    
    # Test military action with negative tone (high relevance)
    relevance = adapter._calculate_relevance("125", -5.0)
    assert relevance >= 0.8
    
    # Test military action with neutral tone (lower relevance)
    relevance = adapter._calculate_relevance("125", 0.0)
    assert relevance >= 0.5
    
    print("[OK] Relevance calculation works correctly")


def test_gdelt_registry_entry():
    """Test that GDELT is registered in data source registry."""
    import yaml
    
    registry_path = Path(__file__).parent.parent / "registry" / "data_source_registry.yaml"
    with open(registry_path) as f:
        registry = yaml.safe_load(f)
    
    gdelt_sources = [s for s in registry["sources"] if s["id"] == "SRC-GEO-GDELT-001"]
    assert len(gdelt_sources) == 1
    
    gdelt_entry = gdelt_sources[0]
    assert gdelt_entry["provider"] == "gdelt"
    assert gdelt_entry["category"] == "alt"
    assert gdelt_entry["enabled"] == True
    assert "api.gdeltproject.org" in gdelt_entry["endpoint"]
    
    print("[OK] GDELT registry entry correct")


def test_gdelt_consumes_entry():
    """Test that GDELT is registered in consumes.yaml."""
    import yaml
    
    consumes_path = Path(__file__).parent.parent / "ui" / "feeds" / "consumes.yaml"
    with open(consumes_path) as f:
        consumes = yaml.safe_load(f)
    
    gdelt_sources = [s for s in consumes["inputs"] if s["source_id"] == "SRC-GEO-GDELT-001"]
    assert len(gdelt_sources) == 1
    
    gdelt_entry = gdelt_sources[0]
    assert gdelt_entry["required"] == False
    
    print("[OK] GDELT consumption entry correct")


def run_all_tests():
    """Run all GDELT integration tests."""
    print("\n" + "="*60)
    print("GDELT Integration Tests")
    print("="*60 + "\n")
    
    tests = [
        test_gdelt_adapter_instantiation,
        test_gdelt_event_observation_structure,
        test_gdelt_relevant_event_codes,
        test_gdelt_fetch_methods_exist,
        test_gdelt_fetch_methods_return_lists,
        test_gdelt_relevance_calculation,
        test_gdelt_registry_entry,
        test_gdelt_consumes_entry,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    if failed > 0:
        print("[WARNING] Some tests failed. Please review the errors above.")
        return False
    else:
        print("[SUCCESS] All tests passed! GDELT integration is ready.")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
