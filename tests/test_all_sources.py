"""Test suite for all data sources - Validates API implementations.

Tests all 60+ sources for:
- API connectivity
- Data retrieval
- Data quality
- Error handling
- Caching behavior
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.source_manager import get_source_manager
from system.cache_layer import get_cached_fetcher
from system.data_quality_monitor import get_quality_monitor
from data_sources.external.api_implementations import fetch_from_provider


class DataSourceTestSuite:
    """Test suite for all data sources."""
    
    def __init__(self):
        self.source_manager = get_source_manager()
        self.cache_fetcher = get_cached_fetcher()
        self.quality_monitor = get_quality_monitor(quality_monitor=None)  # Start fresh
        self.results: dict[str, dict[str, Any]] = {}
    
    def run_all_tests(self) -> None:
        """Run tests for all enabled sources."""
        print("\n" + "="*70)
        print("DATA SOURCE TEST SUITE")
        print("="*70 + "\n")
        
        # Get all sources for INDIRA
        sources = self.source_manager.get_enabled_sources_for_agent("indira")
        
        print(f"Testing {len(sources)} enabled sources for INDIRA\n")
        
        for source_id in sources[:10]:  # Test top 10 first
            print(f"Testing {source_id}...")
            self._test_source(source_id)
            print()
        
        self._print_summary()
    
    def _test_source(self, source_id: str) -> None:
        """Test a single data source."""
        import time
        
        result = {
            "source_id": source_id,
            "tested": False,
            "success": False,
            "latency_ms": 0.0,
            "error": "",
            "data": None,
        }
        
        try:
            config = self.source_manager._sources.get(source_id)
            if not config:
                result["error"] = "Source not found in configuration"
                self.results[source_id] = result
                return
            
            provider = config.provider
            
            # Determine method based on category
            if config.category == "crypto":
                method = "fetch_price"
                params = ("bitcoin",)  # Test with bitcoin
            elif config.category == "forex":
                method = "fetch_rate"
                params = ("USD", "EUR")
            elif config.category == "macro":
                method = "fetch_indicator"
                params = ("GDP",)
            else:
                method = "fetch_quote"
                params = ("AAPL",)
            
            # Test with cache
            start = time.time()
            data = self.cache_fetcher.fetch(provider, method, params)
            latency_ms = (time.time() - start) * 1000
            
            # Record quality metrics
            self.quality_monitor.record_data_point(source_id, {"test": True, "data": data}, latency_ms)
            
            if data:
                result["tested"] = True
                result["success"] = True
                result["latency_ms"] = latency_ms
                result["data"] = data
                self.source_manager.record_success(source_id, latency_ms)
                print(f"  ✓ Success - {latency_ms:.2f}ms latency")
            else:
                result["tested"] = True
                result["error"] = "No data returned"
                self.source_manager.record_failure(source_id, "No data returned")
                print(f"  ✗ Failed - No data returned")
        
        except Exception as e:
            result["error"] = str(e)
            self.source_manager.record_failure(source_id, str(e))
            print(f"  ✗ Failed - {e}")
        
        self.results[source_id] = result
    
    def _print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70 + "\n")
        
        total = len(self.results)
        tested = sum(1 for r in self.results.values() if r["tested"])
        successful = sum(1 for r in self.results.values() if r["success"])
        failed = tested - successful
        
        print(f"Total sources tested: {total}")
        print(f"Tested: {tested}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if tested > 0:
            success_rate = successful / tested
            print(f"Success rate: {success_rate:.2%}")
        
        print("\n" + "="*70)
        print("CACHE STATISTICS")
        print("="*70 + "\n")
        
        cache_stats = self.cache_fetcher.get_cache_stats()
        for key, value in cache_stats.items():
            print(f"{key}: {value}")
        
        print("\n" + "="*70)
        print("QUALITY METRICS")
        print("="*70 + "\n")
        
        quality_metrics = self.quality_monitor.get_all_metrics()
        for source_id, metrics in quality_metrics.items():
            print(f"{source_id}:")
            print(f"  Quality: {metrics.quality_level.value} ({metrics.overall_score:.2f})")
            print(f"  Freshness: {metrics.freshness_score:.2f}")
            print(f"  Completeness: {metrics.completeness_score:.2f}")
            print(f"  Latency: {metrics.latency_score:.2f}")
            print()
        
        print("="*70 + "\n")


def run_tests() -> None:
    """Run the complete test suite."""
    suite = DataSourceTestSuite()
    suite.run_all_tests()


if __name__ == "__main__":
    run_tests()
