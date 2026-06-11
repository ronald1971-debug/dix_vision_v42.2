"""Test cases for new AI providers and Local Devin CLI."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import directly from api_implementations
from data_sources.external import api_implementations


def test_perplexity_adapter():
    """Test Perplexity AI adapter."""
    print("Testing PerplexityAdapter...")
    try:
        adapter = api_implementations.PerplexityAdapter(api_key="test_key")
        # Test without real API key (should return empty results)
        result = adapter.search("test query")
        assert result["provider"] == "perplexity"
        assert "query" in result
        print("[OK] PerplexityAdapter initialized successfully")
        return True
    except Exception as e:
        print(f"[FAIL] PerplexityAdapter: {e}")
        return False


def test_local_devin_adapter():
    """Test Local Devin CLI adapter."""
    print("Testing LocalDevinAdapter...")
    try:
        adapter = api_implementations.LocalDevinAdapter()
        # Test task execution
        result = adapter.execute_task("test task")
        assert result["provider"] == "local_devin"
        assert result["task"] == "test task"
        assert result["status"] == "completed"
        print("[OK] LocalDevinAdapter executed successfully")
        return True
    except Exception as e:
        print(f"[FAIL] LocalDevinAdapter: {e}")
        return False


def test_local_devin_with_context():
    """Test Local Devin CLI adapter with context."""
    print("Testing LocalDevinAdapter with context...")
    try:
        adapter = api_implementations.LocalDevinAdapter()
        context = {"file": "test.py", "line": 10}
        result = adapter.execute_task("test task with context", context=context)
        assert result["provider"] == "local_devin"
        assert result["status"] == "completed"
        print("[OK] LocalDevinAdapter with context executed successfully")
        return True
    except Exception as e:
        print(f"[FAIL] LocalDevinAdapter with context: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing New AI Providers")
    print("=" * 60)
    
    tests = [
        test_perplexity_adapter,
        test_local_devin_adapter,
        test_local_devin_with_context,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
