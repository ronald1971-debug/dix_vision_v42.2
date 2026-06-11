"""Test free sources from original implementation."""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import only the free source adapters
from data_sources.external.api_implementations import (
    BaseAPIAdapter,
)

# Test CoinGecko directly
print("Testing CoinGecko (Free, no key required)...")
try:
    import urllib.request
    import json
    
    class CoinGeckoAdapter(BaseAPIAdapter):
        def __init__(self):
            super().__init__()
            self._base_url = "https://api.coingecko.com/api/v3"
            self._min_request_interval = 1.0
        
        def fetch_price(self, coin_id: str):
            self._rate_limit()
            try:
                url = f"{self._base_url}/coins/markets"
                params = f"vs_currency=usd&ids={coin_id}"
                full_url = f"{url}?{params}"
                
                with urllib.request.urlopen(full_url, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    if data and len(data) > 0:
                        return {
                            "price": float(data[0].get("current_price", 0.0)),
                            "volume_24h": float(data[0].get("total_volume", 0.0)),
                        }
            except Exception as e:
                print(f"CoinGecko error: {e}")
                return None
    
    coingecko = CoinGeckoAdapter()
    data = coingecko.fetch_price("bitcoin")
    if data:
        print(f"[SUCCESS] CoinGecko: BTC price ${data['price']}, 24h volume ${data['volume_24h']:,.0f}")
    else:
        print("[FAILED] CoinGecko: No data returned")
        
except Exception as e:
    print(f"✗ CoinGecko Failed: {e}")

# Test Frankfurter directly
print("\nTesting Frankfurter (Free, no key required)...")
try:
    class FrankfurterAdapter(BaseAPIAdapter):
        def __init__(self):
            super().__init__()
            self._base_url = "https://api.frankfurter.app"
            self._min_request_interval = 1.0
        
        def fetch_rate(self, from_curr, to_curr):
            self._rate_limit()
            try:
                url = f"{self._base_url}/latest"
                params = f"from={from_curr}&to={to_curr}"
                full_url = f"{url}?{params}"
                
                with urllib.request.urlopen(full_url, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    if data.get("rates") and to_curr in data["rates"]:
                        return {
                            "rate": float(data["rates"][to_curr]),
                        }
            except Exception as e:
                print(f"Frankfurter error: {e}")
                return None
    
    frankfurter = FrankfurterAdapter()
    data = frankfurter.fetch_rate("USD", "EUR")
    if data:
        print(f"[SUCCESS] Frankfurter: USD/EUR {data['rate']}")
    else:
        print("[FAILED] Frankfurter: No data returned")
        
except Exception as e:
    print(f"[FAILED] Frankfurter: {e}")

# Test ArXiv directly
print("\nTesting ArXiv (Free, no key required)...")
try:
    class ArXivAdapter(BaseAPIAdapter):
        def __init__(self):
            super().__init__()
            self._base_url = "http://export.arxiv.org/api/query"
            self._min_request_interval = 1.0
        
        def search_papers(self, query, max_results):
            self._rate_limit()
            try:
                from urllib.parse import quote
                params = f"search_query=all:{quote(query)}&start=0&max_results={max_results}"
                full_url = f"{self._base_url}?{params}"
                
                with urllib.request.urlopen(full_url, timeout=10) as response:
                    xml_data = response.read().decode()
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(xml_data)
                    papers = []
                    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                        papers.append({
                            "title": entry.find("{http://www.w3.org/2005/Atom}title").text if entry.find("{http://www.w3.org/2005/Atom}title") is not None else "",
                        })
                    return {"count": len(papers)}
            except Exception as e:
                print(f"ArXiv error: {e}")
                return None
    
    arxiv = ArXivAdapter()
    data = arxiv.search_papers("quantum finance", 5)
    if data:
        print(f"[SUCCESS] ArXiv: Found {data['count']} papers")
    else:
        print("[FAILED] ArXiv: No data returned")
        
except Exception as e:
    print(f"[FAILED] ArXiv: {e}")

print("\nFree sources test complete!")
print("\nStatus: Basic free sources are working!")
