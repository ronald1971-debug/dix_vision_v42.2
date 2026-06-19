#!/usr/bin/env python3
"""
Automated Dashboard Integration Testing Script
Tests Dashboard2026 backend API integration with DIX VISION FastAPI server
"""

import asyncio
import httpx
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import sys

@dataclass
class TestResult:
    """Single test result."""
    endpoint: str
    method: str
    status_code: Optional[int] = None
    expected_status: int = 200
    response_time: float = 0.0
    success: bool = False
    error: Optional[str] = None
    timestamp: float = 0.0
    details: Optional[Dict[str, Any]] = None

class DashboardIntegrationTester:
    """Automated dashboard integration testing."""
    
    def __init__(self, base_url: str = "http://localhost:8080", timeout: float = 10.0):
        self.base_url = base_url
        self.timeout = timeout
        self.results: List[TestResult] = []
        self.start_time: Optional[float] = None
        
    async def test_endpoint(self, method: str, endpoint: str, 
                          params: Dict = None, data: Dict = None,
                          expected_status: int = 200) -> TestResult:
        """Test a single API endpoint."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        result = TestResult(
            endpoint=endpoint,
            method=method,
            expected_status=expected_status,
            timestamp=time.time()
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(url, params=params)
                elif method == "POST":
                    response = await client.post(url, json=data or params)
                elif method == "DELETE":
                    response = await client.delete(url, params=params)
                else:
                    raise ValueError(f"Unsupported method: {method}")
            
            result.response_time = time.time() - start_time
            result.status_code = response.status_code
            result.success = response.status_code == expected_status
            result.details = {
                "response_length": len(response.content),
                "content_type": response.headers.get("content-type"),
                "status_text": response.status_phrase if hasattr(response, 'status_phrase') else str(response.status_code)
            }
            
            if not result.success:
                result.error = f"Expected status {expected_status}, got {response.status_code}"
            
        except httpx.TimeoutException as e:
            result.response_time = time.time() - start_time
            result.error = f"Timeout after {self.timeout}s"
            result.success = False
            
        except httpx.ConnectError as e:
            result.response_time = time.time() - start_time
            result.error = f"Connection error: {str(e)}"
            result.success = False
            
        except Exception as e:
            result.response_time = time.time() - start_time
            result.error = str(e)
            result.success = False
        
        self.results.append(result)
        return result
    
    async def test_indira_api(self) -> List[TestResult]:
        """Test INDIRA Cognitive Center API endpoints."""
        print("\nTesting INDIRA Cognitive Center API...")
        
        # Market Intelligence
        print("  Testing Market Intelligence...")
        await self.test_endpoint("GET", "/api/indira/market/regimes")
        await self.test_endpoint("GET", "/api/indira/market/narratives")
        await self.test_endpoint("GET", "/api/indira/market/liquidity")
        await self.test_endpoint("GET", "/api/indira/market/volatility")
        await self.test_endpoint("GET", "/api/indira/market/orderflow")
        await self.test_endpoint("GET", "/api/indira/market/crossasset")
        
        # Trader Intelligence
        print("  Testing Trader Intelligence...")
        await self.test_endpoint("GET", "/api/indira/traders/top", {"limit": 10})
        await self.test_endpoint("GET", "/api/indira/traders/profile/0x1234567890abcdef")
        await self.test_endpoint("GET", "/api/indira/traders/clusters")
        await self.test_endpoint("GET", "/api/indira/traders/relationships")
        await self.test_endpoint("GET", "/api/indira/traders/similarity/0x1234567890abcdef")
        await self.test_endpoint("GET", "/api/indira/traders/performance/overview")
        
        # Strategy Intelligence
        print("  Testing Strategy Intelligence...")
        await self.test_endpoint("GET", "/api/indira/strategy/creation")
        await self.test_endpoint("GET", "/api/indira/strategy/evolution")
        await self.test_endpoint("GET", "/api/indira/strategy/optimization")
        await self.test_endpoint("GET", "/api/indira/strategy/backtesting")
        await self.test_endpoint("GET", "/api/indira/strategy/deployment")
        
        # Portfolio Intelligence
        print("  Testing Portfolio Intelligence...")
        await self.test_endpoint("GET", "/api/indira/portfolio/analysis")
        await self.test_endpoint("GET", "/api/indira/portfolio/allocation")
        await self.test_endpoint("GET", "/api/indira/portfolio/risk")
        await self.test_endpoint("GET", "/api/indira/portfolio/performance")
        await self.test_endpoint("GET", "/api/indira/portfolio/attribution")
        
        # Research Intelligence
        print("  Testing Research Intelligence...")
        await self.test_endpoint("GET", "/api/indira/research/queue")
        await self.test_endpoint("GET", "/api/indira/research/knowledge-graph")
        await self.test_endpoint("GET", "/api/indira/research/learning")
        await self.test_endpoint("GET", "/api/indira/research/publications")
        await self.test_endpoint("GET", "/api/indira/research/collaboration")
        
        return [r for r in self.results if "/api/indira" in r.endpoint]
    
    async def test_markets_api(self) -> List[TestResult]:
        """Test Unified Markets API endpoints."""
        print("\nTesting Unified Markets API...")
        
        # Market Data
        print("  Testing Market Data...")
        await self.test_endpoint("GET", "/api/markets/quote/BTC")
        await self.test_endpoint("GET", "/api/markets/quote/ETH")
        await self.test_endpoint("GET", "/api/markets/ohlcv/BTC", {"timeframe": "1m", "limit": 10})
        await self.test_endpoint("GET", "/api/markets/ohlcv/BTC", {"chartType": "heikin_ashi", "limit": 10})
        await self.test_endpoint("GET", "/api/markets/ohlcv/BTC", {"chartType": "renko", "limit": 10})
        await self.test_endpoint("GET", "/api/markets/quotes/Crypto", {"limit": 10})
        
        # Order Flow
        print("  Testing Order Flow...")
        await self.test_endpoint("GET", "/api/markets/orderflow/BTC/dom", {"depth": 10})
        await self.test_endpoint("GET", "/api/markets/orderflow/BTC/footprint", {"limit": 10})
        await self.test_endpoint("GET", "/api/markets/orderflow/BTC/volume-delta", {"limit": 10})
        await self.test_endpoint("GET", "/api/markets/orderflow/BTC/heatmap", {"levels": 10})
        await self.test_endpoint("GET", "/api/markets/orderflow/BTC/liquidity-heatmap", {"levels": 10})
        
        # Watchlist
        print("  Testing Watchlist...")
        await self.test_endpoint("GET", "/api/markets/watchlist")
        await self.test_endpoint("POST", "/api/markets/watchlist", {"symbol": "BTC", "assetClass": "Crypto"})
        await self.test_endpoint("DELETE", "/api/markets/watchlist/BTC")
        
        # Scanner
        print("  Testing Market Scanner...")
        await self.test_endpoint("GET", "/api/markets/scanner", {"assetClass": "Crypto", "limit": 10})
        await self.test_endpoint("GET", "/api/markets/scanner/gainers", {"assetClass": "Crypto", "limit": 10})
        await self.test_endpoint("GET", "/api/markets/scanner/losers", {"assetClass": "Crypto", "limit": 10})
        await self.test_endpoint("GET", "/api/markets/scanner/volume", {"assetClass": "Crypto", "limit": 10})
        await self.test_endpoint("GET", "/api/markets/scanner/volatility", {"assetClass": "Crypto", "limit": 10})
        
        # News & Events
        print("  Testing News & Events...")
        await self.test_endpoint("GET", "/api/markets/news", {"symbol": "BTC", "limit": 10})
        await self.test_endpoint("GET", "/api/markets/news/Crypto", {"limit": 10})
        await self.test_endpoint("GET", "/api/markets/events", {"limit": 10})
        
        return [r for r in self.results if "/api/markets" in r.endpoint]
    
    async def test_error_handling(self) -> List[TestResult]:
        """Test error handling and edge cases."""
        print("\nTesting Error Handling...")
        
        # Invalid symbols
        print("  Testing invalid inputs...")
        await self.test_endpoint("GET", "/api/markets/quote/INVALID_SYMBOL", expected_status=200)  # Should handle gracefully
        await self.test_endpoint("GET", "/api/indira/traders/profile/invalid", expected_status=200)  # Should handle gracefully
        
        # Invalid parameters
        await self.test_endpoint("GET", "/api/markets/scanner", {"assetClass": "INVALID"}, expected_status=200)
        await self.test_endpoint("GET", "/api/markets/ohlcv/BTC", {"timeframe": "invalid"}, expected_status=200)
        
        return [r for r in self.results if "invalid" in r.endpoint.lower() or r.error]
    
    async def test_concurrent_requests(self) -> List[TestResult]:
        """Test concurrent request handling."""
        print("\nTesting Concurrent Requests...")
        
        endpoints_to_test = [
            ("/api/indira/market/regimes", "GET", {}),
            ("/api/markets/quote/BTC", "GET", {}),
            ("/api/indira/traders/top?limit=5", "GET", {}),
            ("/api/markets/orderflow/BTC/dom?depth=5", "GET", {}),
            ("/api/markets/scanner/gainers?assetClass=Crypto&limit=5", "GET", {}),
        ]
        
        # Create concurrent tasks
        tasks = []
        for endpoint, method, params in endpoints_to_test * 5:  # Test each endpoint 5 times concurrently
            tasks.append(self.test_endpoint(method, endpoint, params=params))
        
        await asyncio.gather(*tasks)
        
        return [r for r in self.results if any(ep in r.endpoint for ep, _, _ in endpoints_to_test)]
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        self.start_time = time.time()
        print("Starting Dashboard Integration Tests...")
        print(f"Testing endpoint: {self.base_url}")
        print(f"Timeout: {self.timeout}s")
        
        try:
            # Test server availability
            print("\nTesting server availability...")
            await self.test_endpoint("GET", "/api/health", expected_status=200)
            
            if not self.results[-1].success and "health" in self.results[-1].endpoint:
                print("Server health check failed, but continuing with API tests...")
            
            # Run test suites
            indira_results = await self.test_indira_api()
            markets_results = await self.test_markets_api()
            error_results = await self.test_error_handling()
            concurrent_results = await self.test_concurrent_requests()
            
        except Exception as e:
            print(f"\nFatal error during testing: {e}")
            return {"error": str(e)}
        
        # Calculate statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        successful_tests_with_times = [r.response_time for r in self.results if r.success]
        avg_response_time = sum(successful_tests_with_times) / len(successful_tests_with_times) if successful_tests_with_times else 0
        max_response_time = max(successful_tests_with_times) if successful_tests_with_times else 0
        min_response_time = min(successful_tests_with_times) if successful_tests_with_times else 0
        
        total_time = time.time() - self.start_time
        
        summary = {
            "test_metadata": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "total_duration": total_time,
                "timeout": self.timeout
            },
            "test_statistics": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": round(success_rate, 2),
                "average_response_time": round(avg_response_time, 3),
                "max_response_time": round(max_response_time, 3),
                "min_response_time": round(min_response_time, 3),
                "total_test_duration": round(total_time, 2)
            },
            "test_results": [
                {
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "status_code": r.status_code,
                    "expected_status": r.expected_status,
                    "response_time": round(r.response_time, 3),
                    "success": r.success,
                    "error": r.error,
                    "details": r.details,
                    "timestamp": datetime.fromtimestamp(r.timestamp).isoformat()
                }
                for r in self.results
            ]
        }
        
        # Print summary
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Average Response Time: {avg_response_time:.3f}s")
        print(f"Max Response Time: {max_response_time:.3f}s")
        print(f"Min Response Time: {min_response_time:.3f}s")
        print(f"Total Duration: {total_time:.2f}s")
        print(f"{'='*60}")
        
        # Print failed tests
        if failed_tests > 0:
            print(f"\nFailed Tests:")
            for r in self.results:
                if not r.success:
                    print(f"  - {r.method} {r.endpoint}: {r.error or f'Status {r.status_code}'}")
        
        return summary
    
    def save_results(self, summary: Dict[str, Any], filename: str = "integration_test_results.json"):
        """Save test results to file."""
        try:
            with open(filename, "w") as f:
                json.dump(summary, f, indent=2)
            print(f"\nResults saved to {filename}")
            return True
        except Exception as e:
            print(f"\nFailed to save results: {e}")
            return False

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dashboard Integration Testing")
    parser.add_argument("--url", default="http://localhost:8080", help="Base URL for testing")
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds")
    parser.add_argument("--output", default="integration_test_results.json", help="Output file for results")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    tester = DashboardIntegrationTester(base_url=args.url, timeout=args.timeout)
    
    try:
        results = asyncio.run(tester.run_all_tests())
        
        if "error" not in results:
            tester.save_results(results, args.output)
            
            # Exit with appropriate code
            success_rate = results["test_statistics"]["success_rate"]
            if success_rate >= 95:
                print(f"\nIntegration tests PASSED ({success_rate:.1f}% success rate)")
                sys.exit(0)
            elif success_rate >= 80:
                print(f"\nIntegration tests PARTIAL ({success_rate:.1f}% success rate)")
                sys.exit(1)
            else:
                print(f"\nIntegration tests FAILED ({success_rate:.1f}% success rate)")
                sys.exit(2)
        else:
            print(f"\nIntegration tests FAILED: {results['error']}")
            sys.exit(3)
            
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(4)

if __name__ == "__main__":
    main()
