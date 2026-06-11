#!/usr/bin/env python3
"""Test free data sources that don't require API keys."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_sources.external.api_implementations import (
    CoinGeckoAdapter,
    FrankfurterAdapter,
    FREDAdapter,
)

def test_coin_gecko():
    """Test CoinGecko (crypto) - no API key required."""
    print("\n[Test 1] CoinGecko Adapter (Crypto - No Key Required)")
    try:
        adapter = CoinGeckoAdapter()
        result = adapter.fetch_price("bitcoin")
        print(f"[OK] Bitcoin Price: ${result.get('price', 0)}")
        print(f"[OK] 24h Change: {result.get('change_24h', 0)}%")
        return True
    except Exception as e:
        print(f"[FAIL] CoinGecko: {e}")
        return False

def test_frankfurter():
    """Test Frankfurter (forex) - no API key required."""
    print("\n[Test 2] Frankfurter Adapter (Forex - No Key Required)")
    try:
        adapter = FrankfurterAdapter()
        result = adapter.fetch_rate("USD", "EUR")
        print(f"[OK] USD to EUR: {result.get('rate', 0)}")
        return True
    except Exception as e:
        print(f"[FAIL] Frankfurter: {e}")
        return False

def test_fred():
    """Test FRED (macro) - no API key required."""
    print("\n[Test 3] FRED Adapter (Macro - No Key Required)")
    try:
        adapter = FREDAdapter()
        result = adapter.fetch_indicator("UNRATE")  # Unemployment rate
        print(f"[OK] FRED Data: Series fetched successfully")
        print(f"[OK] Data points: {len(result.get('data', []))}")
        return True
    except Exception as e:
        print(f"[FAIL] FRED: {e}")
        return False

def main():
    """Run all free source tests."""
    print("=" * 60)
    print("Testing Free Data Sources (No API Key Required)")
    print("=" * 60)
    
    tests = [
        test_coin_gecko,
        test_frankfurter,
        test_fred,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
