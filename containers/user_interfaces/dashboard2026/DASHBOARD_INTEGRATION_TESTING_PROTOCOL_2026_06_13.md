# DIX VISION Dashboard Integration Testing Protocol

**Date:** June 13, 2026  
**Status:** Integration Testing Protocol Created  
**Target:** Dashboard2026 Backend Integration Testing  

---

## Overview

This document provides a comprehensive integration testing protocol for the Dashboard2026 backend APIs that have been integrated with the DIX VISION FastAPI server. Since the system uses container-based deployment, this protocol can be executed in the production environment when containers are running.

---

## Test Environment Requirements

### Prerequisites
1. **DIX VISION v42.2 System Running** - All 101 containers operational
2. **FastAPI Server Container** - UI server container running with dashboard API routers
3. **Network Connectivity** - Inter-container networking functional
4. **Authentication Service** - Authentication middleware available
5. **Cognitive Engines** - INDIRA/DYON cognitive engines operational (optional for basic testing)

### Test Tools Required
- `curl` or `httpie` for API endpoint testing
- `wscat` or similar WebSocket client for WebSocket testing
- Browser with developer tools for WebSocket testing
- Python 3.8+ for script-based testing
- Access to container logs via `docker logs`

---

## Test Phase 1: FastAPI Server Startup and Router Loading

### 1.1 Server Startup Test

**Objective:** Verify that the FastAPI server starts successfully and loads the dashboard API routers.

**Test Steps:**
```bash
# 1. Start or restart the UI server container
docker restart <ui-server-container-name>

# 2. Check container status
docker ps | grep <ui-server-container-name>

# 3. Check server logs for router loading messages
docker logs <ui-server-container-name> | grep "Dashboard Build A API routers"
```

**Expected Results:**
- Container status shows "Up" and "healthy"
- Logs show: "[BOOT] Dashboard Build A API routers loaded successfully"
- No errors related to dashboard API imports
- Container remains stable (no restarts)

**Test Status:** ⏸️ **READY FOR TESTING** (Requires running container)

---

### 1.2 Router Registration Test

**Objective:** Verify that dashboard API routers are properly registered in the FastAPI application.

**Test Steps:**
```bash
# 1. Access FastAPI auto-generated documentation
curl http://localhost:8080/docs

# 2. Check for dashboard API endpoints in OpenAPI spec
curl http://localhost:8080/openapi.json | grep "/api/indira"
curl http://localhost:8080/openapi.json | grep "/api/markets"

# 3. List all registered routes programmatically
python -c "
import httpx
response = httpx.get('http://localhost:8080/openapi.json')
routes = response.json()['paths']
indira_routes = [r for r in routes if '/api/indira' in r]
markets_routes = [r for r in routes if '/api/markets' in r]
print(f'INDIRA routes: {len(indira_routes)}')
print(f'Markets routes: {len(markets_routes)}')
"
```

**Expected Results:**
- OpenAPI documentation accessible
- At least 25 INDIRA API routes registered
- At least 28 Markets API routes registered
- All routes properly documented in OpenAPI spec

**Test Status:** ⏸️ **READY FOR TESTING** (Requires running container)

---

## Test Phase 2: INDIRA Cognitive Center API Testing

### 2.1 Market Intelligence Endpoints

**Test 2.1.1: Market Regimes**
```bash
curl -X GET "http://localhost:8080/api/indira/market/regimes" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array of market regimes
- Each regime contains: regime, confidence, duration, strength
- Response time < 200ms

**Test 2.1.2: Market Narratives**
```bash
curl -X GET "http://localhost:8080/api/indira/market/narratives" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array of market narratives
- Each narrative contains: narrative, sentiment, velocity, sources
- Response time < 200ms

**Test 2.1.3: Liquidity Analysis**
```bash
curl -X GET "http://localhost:8080/api/indira/market/liquidity" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array of liquidity data
- Each entry contains market, flow, depth, spread
- Response time < 200ms

### 2.2 Trader Intelligence Endpoints

**Test 2.2.1: Top Traders**
```bash
curl -X GET "http://localhost:8080/api/indira/traders/top?limit=10" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array of top traders
- Each trader contains: address, profit, win_rate, total_trades
- Limit parameter respected
- Response time < 200ms

**Test 2.2.2: Trader Profile**
```bash
curl -X GET "http://localhost:8080/api/indira/traders/profile/0x1234567890abcdef" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON object with trader profile data
- Contains address, performance, strategy, risk metrics
- Response time < 200ms

**Test 2.2.3: Trader Clusters**
```bash
curl -X GET "http://localhost:8080/api/indira/traders/clusters" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array of trader clusters
- Each cluster contains cluster_id, size, characteristics
- Response time < 200ms

### 2.3 Strategy Intelligence Endpoints

**Test 2.3.1: Strategy Creation**
```bash
curl -X GET "http://localhost:8080/api/indira/strategy/creation" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with strategy creation metrics
- Contains creation_count, success_rate, avg_generation_time
- Response time < 200ms

**Test 2.3.2: Strategy Evolution**
```bash
curl -X GET "http://localhost:8080/api/indira/strategy/evolution" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with evolution data across generations
- Contains generation_data, performance_improvements
- Response time < 200ms

### 2.4 Portfolio Intelligence Endpoints

**Test 2.4.1: Portfolio Analysis**
```bash
curl -X GET "http://localhost:8080/api/indira/portfolio/analysis" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with portfolio metrics
- Contains total_value, performance, risk_metrics
- Response time < 200ms

**Test 2.4.2: Portfolio Allocation**
```bash
curl -X GET "http://localhost:8080/api/indira/portfolio/allocation" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with asset allocation data
- Contains allocation_by_asset, allocation_by_strategy
- Response time < 200ms

### 2.5 Research Intelligence Endpoints

**Test 2.5.1: Research Queue**
```bash
curl -X GET "http://localhost:8080/api/indira/research/queue" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with research queue status
- Contains pending_tasks, completed_tasks, processing_time
- Response time < 200ms

**Test 2.5.2: Knowledge Graph**
```bash
curl -X GET "http://localhost:8080/api/indira/research/knowledge-graph" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with knowledge graph statistics
- Contains node_count, edge_count, graph_health
- Response time < 200ms

**Test Status:** ⏸️ **READY FOR TESTING** (Requires running container)

---

## Test Phase 3: Unified Markets API Testing

### 3.1 Market Data Endpoints

**Test 3.1.1: Real-time Quote**
```bash
curl -X GET "http://localhost:8080/api/markets/quote/BTC" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with quote data
- Contains symbol, price, change, volume, timestamp
- Response time < 100ms

**Test 3.1.2: OHLCV Data**
```bash
curl -X GET "http://localhost:8080/api/markets/ohlcv/BTC?timeframe=1m&chartType=candlestick&limit=100" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array of OHLCV data
- Each candle contains time, open, high, low, close, volume
- Limit parameter respected
- Response time < 200ms

**Test 3.1.3: Chart Type Variations**
```bash
# Test different chart types
for chart_type in candlestick heikin_ashi renko range_bars tick line; do
  curl -X GET "http://localhost:8080/api/markets/ohlcv/BTC?chartType=${chart_type}&limit=10" \
    -H "accept: application/json"
done
```

**Expected Results:**
- All chart types return valid responses
- Status code: 200 for all requests
- Data structure appropriate for each chart type
- Response time < 200ms for each request

### 3.2 Order Flow Endpoints

**Test 3.2.1: DOM Ladder**
```bash
curl -X GET "http://localhost:8080/api/markets/orderflow/BTC/dom?depth=20" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with DOM ladder data
- Contains bids and asks with price levels and sizes
- Depth parameter respected
- Response time < 200ms

**Test 3.2.2: Footprint Charts**
```bash
curl -X GET "http://localhost:8080/api/markets/orderflow/BTC/footprint?timeframe=1m&limit=100" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with footprint chart data
- Contains timestamp, price_levels, volume_at_price
- Response time < 200ms

**Test 3.2.3: Volume Delta**
```bash
curl -X GET "http://localhost:8080/api/markets/orderflow/BTC/volume-delta?timeframe=1m&limit=100" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with volume delta data
- Contains timestamp, cumulative_delta, buying_volume, selling_volume
- Response time < 200ms

**Test 3.2.4: Order Book Heatmap**
```bash
curl -X GET "http://localhost:8080/api/markets/orderflow/BTC/heatmap?levels=20" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON with heatmap data
- Contains price_levels, order_concentration, visualization_data
- Response time < 200ms

### 3.3 Watchlist Endpoints

**Test 3.3.1: Get Watchlist**
```bash
curl -X GET "http://localhost:8080/api/markets/watchlist" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array of watchlist items
- Each item contains symbol, asset_class, added_timestamp
- Response time < 200ms

**Test 3.3.2: Add to Watchlist**
```bash
curl -X POST "http://localhost:8080/api/markets/watchlist?symbol=BTC&assetClass=Crypto" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200 or 201
- Response confirms addition to watchlist
- Subsequent GET request shows the new symbol
- Response time < 200ms

**Test 3.3.3: Remove from Watchlist**
```bash
curl -X DELETE "http://localhost:8080/api/markets/watchlist/BTC" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200 or 204
- Response confirms removal from watchlist
- Subsequent GET request does not show the symbol
- Response time < 200ms

### 3.4 Market Scanner Endpoints

**Test 3.4.1: Custom Scan**
```bash
curl -X GET "http://localhost:8080/api/markets/scanner?assetClass=Crypto&minVolume=1000000&limit=10" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array of scan results
- Each result contains symbol, metrics
- Filters respected
- Response time < 300ms

**Test 3.4.2: Top Gainers**
```bash
curl -X GET "http://localhost:8080/api/markets/scanner/gainers?assetClass=Crypto&limit=10" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array sorted by gain percentage
- Each result contains symbol, gain_percentage, volume
- Response time < 300ms

**Test 3.4.3: Top Losers**
```bash
curl -X GET "http://localhost:8080/api/markets/scanner/losers?assetClass=Crypto&limit=10" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array sorted by loss percentage
- Each result contains symbol, loss_percentage, volume
- Response time < 300ms

### 3.5 News and Events Endpoints

**Test 3.5.1: News Feed**
```bash
curl -X GET "http://localhost:8080/api/markets/news?symbol=BTC&limit=20" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array of news items
- Each item contains title, summary, source, timestamp, sentiment
- Response time < 200ms

**Test 3.5.2: Upcoming Events**
```bash
curl -X GET "http://localhost:8080/api/markets/events?limit=10" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200
- Response format: JSON array of upcoming events
- Each event contains title, timestamp, impact_level
- Response time < 200ms

**Test Status:** ⏸️ **READY FOR TESTING** (Requires running container)

---

## Test Phase 4: WebSocket Connection Testing

### 4.1 Quote Streaming WebSocket

**Test Steps:**
```bash
# Install wscat if not available
npm install -g wscat

# Connect to quote streaming WebSocket
wscat -c "ws://localhost:8080/api/markets/ws/quotes?symbols=BTC,ETH,SOL"
```

**Expected Results:**
- Connection established successfully
- Receive JSON messages every 2 seconds
- Each message contains quote data for specified symbols
- Messages contain timestamp, symbol, price, volume
- Connection remains stable for 60+ seconds
- Graceful handling of disconnection

### 4.2 Order Flow WebSocket

**Test Steps:**
```bash
# Connect to order flow WebSocket
wscat -c "ws://localhost:8080/api/markets/ws/orderflow/BTC"
```

**Expected Results:**
- Connection established successfully
- Receive JSON messages every 1 second
- Each message contains order flow updates
- Messages contain timestamp, dom_changes, volume_changes
- Connection remains stable for 60+ seconds
- Graceful handling of disconnection

### 4.3 Scanner Updates WebSocket

**Test Steps:**
```bash
# Connect to scanner updates WebSocket
wscat -c "ws://localhost:8080/api/markets/ws/scanner"
```

**Expected Results:**
- Connection established successfully
- Receive JSON messages every 30 seconds
- Each message contains scanner result updates
- Messages contain timestamp, updated_symbols, metrics
- Connection remains stable for 60+ seconds
- Graceful handling of disconnection

### 4.4 WebSocket Error Handling

**Test Steps:**
```bash
# Test invalid WebSocket connection
wscat -c "ws://localhost:8080/api/markets/ws/invalid-endpoint"

# Test with invalid symbols
wscat -c "ws://localhost:8080/api/markets/ws/quotes?symbols=INVALID"

# Test connection interruption (CTRL+C after connection established)
wscat -c "ws://localhost:8080/api/markets/ws/quotes?symbols=BTC"
# Press CTRL+C to interrupt
```

**Expected Results:**
- Invalid endpoints return appropriate error messages
- Invalid symbols handled gracefully
- Connection interruptions handled cleanly
- No server crashes or unstable behavior
- Clean connection termination

**Test Status:** ⏸️ **READY FOR TESTING** (Requires running container)

---

## Test Phase 5: Authentication and Authorization Testing

### 5.1 No Authentication Required (Optional Auth)

**Test Steps:**
```bash
# Test endpoints without authentication
curl -X GET "http://localhost:8080/api/indira/market/regimes" \
  -H "accept: application/json"
```

**Expected Results:**
- Status code: 200 (endpoints work without auth)
- Optional auth dependency is functioning
- Graceful degradation when auth unavailable
- Response time not significantly impacted

### 5.2 With Authentication (If Available)

**Test Steps:**
```bash
# Get authentication token (method depends on auth system)
TOKEN=$(curl -X POST "http://localhost:8080/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | jq -r '.token')

# Test endpoints with authentication
curl -X GET "http://localhost:8080/api/indira/market/regimes" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Results:**
- Status code: 200 (endpoints work with auth)
- Authentication token validated successfully
- User context properly propagated
- Response time not significantly impacted

### 5.3 Authorization Testing

**Test Steps:**
```bash
# Test with different user roles if available
# (Depends on specific authorization implementation)
```

**Expected Results:**
- Role-based access control enforced
- Unauthorized requests properly rejected
- Appropriate error messages for unauthorized access
- No security vulnerabilities exposed

**Test Status:** ⏸️ **READY FOR TESTING** (Requires running container and auth system)

---

## Test Phase 6: Cognitive Engine Integration Testing

### 6.1 Cognitive Engine Availability Check

**Test Steps:**
```bash
# Check cognitive engine status through API
curl -X GET "http://localhost:8080/api/indira/market/regimes" \
  -H "accept: application/json" | jq
```

**Expected Results:**
- If cognitive engines available: real cognitive engine data returned
- If cognitive engines unavailable: fallback mock data returned
- Response format consistent regardless of engine availability
- No errors or crashes when engines unavailable

### 6.2 Cognitive Router Integration

**Test Steps:**
```bash
# Check server logs for cognitive engine activity
docker logs <ui-server-container-name> | grep "Cognitive engine"
```

**Expected Results:**
- Logs show cognitive engine integration attempts
- Provider selection logged when available
- Fallback mechanisms logged when engines unavailable
- No errors related to cognitive router integration

### 6.3 AI Provider Selection

**Test Steps:**
```bash
# Test different task types to trigger different AI providers
# (Depends on cognitive engine implementation)
```

**Expected Results:**
- Appropriate AI providers selected for different tasks
- Provider fallback working when primary unavailable
- Selection based on capabilities matching
- Response quality appropriate for selected provider

**Test Status:** ⏸️ **READY FOR TESTING** (Requires running container and cognitive engines)

---

## Test Phase 7: Error Handling and Edge Cases

### 7.1 Invalid Parameters

**Test Steps:**
```bash
# Test with invalid parameters
curl -X GET "http://localhost:8080/api/markets/quote/INVALID_SYMBOL"
curl -X GET "http://localhost:8080/api/indira/traders/profile/invalid_address"
curl -X GET "http://localhost:8080/api/markets/scanner?assetClass=INVALID"
```

**Expected Results:**
- Status code: 400 or 404
- Error messages clear and helpful
- No server crashes or unstable behavior
- Error handling consistent across endpoints

### 7.2 Missing Required Parameters

**Test Steps:**
```bash
# Test endpoints without required parameters
curl -X GET "http://localhost:8080/api/indira/traders/profile"
curl -X GET "http://localhost:8080/api/markets/ohlcv/BTC?timeframe=invalid"
```

**Expected Results:**
- Status code: 400 or 422
- Error messages specify missing/invalid parameters
- No server crashes or unstable behavior
- Parameter validation working correctly

### 7.3 Rate Limiting (If Implemented)

**Test Steps:**
```bash
# Make rapid consecutive requests
for i in {1..100}; do
  curl -X GET "http://localhost:8080/api/indira/market/regimes" &
done
wait
```

**Expected Results:**
- Rate limiting enforced if configured
- Appropriate 429 status codes when limit exceeded
- Server remains stable under load
- No degradation in response quality

### 7.4 Large Response Handling

**Test Steps:**
```bash
# Test endpoints with large limit parameters
curl -X GET "http://localhost:8080/api/markets/ohlcv/BTC?limit=10000"
curl -X GET "http://localhost:8080/api/indira/traders/top?limit=1000"
```

**Expected Results:**
- Status code: 200 (or 400 if limit exceeded)
- Large responses handled efficiently
- No memory issues or timeouts
- Response time scales appropriately with data size

**Test Status:** ⏸️ **READY FOR TESTING** (Requires running container)

---

## Test Phase 8: Performance and Load Testing

### 8.1 Response Time Testing

**Test Steps:**
```bash
# Measure response times for multiple endpoints
for endpoint in \
  "/api/indira/market/regimes" \
  "/api/markets/quote/BTC" \
  "/api/markets/orderflow/BTC/dom" \
  "/api/indira/traders/top?limit=10"; do
  echo "Testing $endpoint"
  time curl -X GET "http://localhost:8080$endpoint"
done
```

**Expected Results:**
- Simple endpoints: < 100ms
- Complex endpoints: < 300ms
- WebSocket message latency: < 10ms
- Consistent response times across multiple requests

### 8.2 Concurrent Request Testing

**Test Steps:**
```bash
# Test concurrent requests using a script
python << EOF
import asyncio
import httpx

async def test_endpoint(endpoint):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8080{endpoint}")
        return response.status_code

async def main():
    endpoints = [
        "/api/indira/market/regimes",
        "/api/markets/quote/BTC",
        "/api/indira/traders/top?limit=10",
    ]
    tasks = [test_endpoint(endpoint) for endpoint in endpoints * 10]
    results = await asyncio.gather(*tasks)
    print(f"Success rate: {sum(1 for r in results if r == 200)}/{len(results)}")

asyncio.run(main())
EOF
```

**Expected Results:**
- 100% success rate for concurrent requests
- No request failures or timeouts
- Response times remain consistent
- Server remains stable under load

### 8.3 WebSocket Connection Stress Testing

**Test Steps:**
```bash
# Test multiple simultaneous WebSocket connections
# (Script needed for this test)
```

**Expected Results:**
- Multiple concurrent connections supported
- No connection drops or instability
- Message delivery remains reliable
- Server resources managed efficiently

**Test Status:** ⏸️ **READY FOR TESTING** (Requires running container and load testing tools)

---

## Test Execution Summary

### Current Test Status

| Test Phase | Status | Notes |
|------------|--------|-------|
| Phase 1: Server Startup | ⏸️ Ready | Requires running container |
| Phase 2: INDIRA API | ⏸️ Ready | Requires running container |
| Phase 3: Markets API | ⏸️ Ready | Requires running container |
| Phase 4: WebSocket | ⏸️ Ready | Requires running container |
| Phase 5: Authentication | ⏸️ Ready | Requires running container |
| Phase 6: Cognitive Engine | ⏸️ Ready | Requires running container |
| Phase 7: Error Handling | ⏸️ Ready | Requires running container |
| Phase 8: Performance | ⏸️ Ready | Requires running container |

### Pre-Testing Checklist

Before executing integration tests, ensure:

- [ ] DIX VISION v42.2 system is running
- [ ] All 101 containers are operational
- [ ] UI server container is healthy
- [ ] Network connectivity between containers
- [ ] Test tools installed (curl, wscat, Python)
- [ ] Access to container logs
- [ ] Authentication system available (optional)
- [ ] Cognitive engines available (optional)

---

## Automated Test Script

For automated testing, create the following Python script:

```python
#!/usr/bin/env python3
"""
Automated Dashboard Integration Testing Script
"""

import asyncio
import httpx
import json
import time
from typing import Dict, List, Any

class DashboardIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
    
    async def test_endpoint(self, method: str, endpoint: str, 
                          params: Dict = None, expected_status: int = 200) -> bool:
        """Test a single API endpoint."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if method == "GET":
                    response = await client.get(url, params=params)
                elif method == "POST":
                    response = await client.post(url, json=params)
                elif method == "DELETE":
                    response = await client.delete(url)
                else:
                    raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            success = response.status_code == expected_status
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "response_time": response_time,
                "success": success,
                "timestamp": time.time()
            }
            
            self.results.append(result)
            return success
            
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "error": str(e),
                "success": False,
                "timestamp": time.time()
            }
            self.results.append(result)
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        print("Starting Dashboard Integration Tests...")
        
        # Test INDIRA API endpoints
        print("Testing INDIRA Cognitive Center API...")
        await self.test_endpoint("GET", "/api/indira/market/regimes")
        await self.test_endpoint("GET", "/api/indira/market/narratives")
        await self.test_endpoint("GET", "/api/indira/market/liquidity")
        await self.test_endpoint("GET", "/api/indira/traders/top", {"limit": 10})
        await self.test_endpoint("GET", "/api/indira/traders/profile/test_address")
        await self.test_endpoint("GET", "/api/indira/traders/clusters")
        await self.test_endpoint("GET", "/api/indira/strategy/creation")
        await self.test_endpoint("GET", "/api/indira/strategy/evolution")
        await self.test_endpoint("GET", "/api/indira/portfolio/analysis")
        await self.test_endpoint("GET", "/api/indira/portfolio/allocation")
        await self.test_endpoint("GET", "/api/indira/research/queue")
        await self.test_endpoint("GET", "/api/indira/research/knowledge-graph")
        
        # Test Markets API endpoints
        print("Testing Unified Markets API...")
        await self.test_endpoint("GET", "/api/markets/quote/BTC")
        await self.test_endpoint("GET", "/api/markets/ohlcv/BTC", {"timeframe": "1m", "limit": 10})
        await self.test_endpoint("GET", "/api/markets/orderflow/BTC/dom", {"depth": 10})
        await self.test_endpoint("GET", "/api/markets/orderflow/BTC/footprint", {"limit": 10})
        await self.test_endpoint("GET", "/api/markets/watchlist")
        await self.test_endpoint("GET", "/api/markets/scanner/gainers", {"assetClass": "Crypto", "limit": 10})
        await self.test_endpoint("GET", "/api/markets/news", {"limit": 10})
        await self.test_endpoint("GET", "/api/markets/events", {"limit": 10})
        
        # Calculate statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        avg_response_time = sum(r.get("response_time", 0) for r in self.results) / total_tests
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": success_rate,
            "average_response_time": avg_response_time,
            "results": self.results
        }
        
        print(f"\nTest Summary:")
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Average Response Time: {avg_response_time:.3f}s")
        
        return summary

if __name__ == "__main__":
    tester = DashboardIntegrationTester()
    results = asyncio.run(tester.run_all_tests())
    
    # Save results to file
    with open("integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to integration_test_results.json")
```

---

## Conclusion

This integration testing protocol provides a comprehensive framework for testing the Dashboard2026 backend APIs. All tests are designed to verify:

1. **Functionality** - All endpoints work as specified
2. **Performance** - Response times meet expectations
3. **Reliability** - System remains stable under load
4. **Integration** - All components work together correctly
5. **Error Handling** - Graceful degradation when components unavailable

The tests are ready to execute once the DIX VISION system is running with the UI server container operational.

**Status:** Integration Testing Protocol Complete - Ready for Execution  
**Next Step:** Execute tests when system is running with all containers operational
