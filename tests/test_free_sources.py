"""Test free sources individually."""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_sources.external.api_implementations import (
    CoinGeckoAdapter,
    FrankfurterAdapter,
    ArXivAdapter,
)

# Test CoinGecko (Free, no key required)
print("Testing CoinGecko...")
try:
    coingecko = CoinGeckoAdapter()
    data = coingecko.fetch_price("bitcoin")
    print(f"✓ CoinGecko Success: BTC price ${data.get('price', 0)}")
except Exception as e:
    print(f"✗ CoinGecko Failed: {e}")

# Test Frankfurter (Free, no key required)
print("\nTesting Frankfurter...")
try:
    frankfurter = FrankfurterAdapter()
    data = frankfurter.fetch_rate("USD", "EUR")
    print(f"✓ Frankfurter Success: USD/EUR {data.get('rate', 0)}")
except Exception as e:
    print(f"✗ Frankfurter Failed: {e}")

# Test ArXiv (Free, no key required)
print("\nTesting ArXiv...")
try:
    arxiv = ArXivAdapter()
    data = arxiv.search_papers("quantum finance", max_results=5)
    print(f"✓ ArXiv Success: Found {len(data.get('papers', []))} papers")
except Exception as e:
    print(f"✗ ArXiv Failed: {e}")

print("\nFree sources test complete!")
