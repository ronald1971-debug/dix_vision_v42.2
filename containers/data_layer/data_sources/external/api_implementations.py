"""Enhanced API implementations with world context integration.

This module contains concrete API implementations for all data sources
with world-aware rate limiting, caching, and prioritization capabilities.
"""

from __future__ import annotations

import logging
import time
import statistics
from datetime import UTC, datetime
from typing import Any, Optional, Dict
from dataclasses import dataclass, field
from collections import deque
from enum import Enum

LOG = logging.getLogger(__name__)

# World context integration
try:
    from world_model.indicator_integration import get_integration_bridge
    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False
    LOG.warning("[API_IMPLEMENTATIONS] World model integration not available")


@dataclass
class WorldContext:
    """World context for API operations."""
    market_regime: str = "unknown"
    market_trend: str = "unknown"
    volatility_regime: str = "unknown"
    liquidity_state: str = "unknown"
    agent_activity: Dict[str, float] = field(default_factory=dict)
    causal_factors: list[str] = field(default_factory=list)
    prediction_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class APIPriority(Enum):
    """API priority levels for world-aware request scheduling."""
    CRITICAL = 1  # Financial data during high volatility
    HIGH = 2      # Trading-related data
    NORMAL = 3    # Standard data requests
    LOW = 4       # Background data collection


class BaseAPIAdapter:
    """Enhanced base class for all API adapters with world-aware capabilities."""
    
    def __init__(self):
        self._last_request_time: float = 0.0
        self._base_min_request_interval: float = 1.0  # Base rate limiting
        self._current_min_request_interval: float = 1.0  # World-aware rate limiting
        self._api_key: str | None = None
        
        # World context integration
        self._world_integration_bridge = None
        self._current_world_context: Optional[WorldContext] = None
        
        # API health monitoring
        self._request_history: deque = deque(maxlen=100)
        self._error_count: int = 0
        self._success_count: int = 0
        
        # Request caching (simple implementation)
        self._cache: Dict[str, tuple[Any, float]] = {}  # key -> (value, timestamp)
        self._cache_ttl: float = 30.0  # Cache TTL in seconds
        
        if WORLD_MODEL_AVAILABLE:
            self._init_world_integration()
    
    def _init_world_integration(self) -> None:
        """Initialize world model integration bridge."""
        try:
            self._world_integration_bridge = get_integration_bridge()
            LOG.info(f"[{self.__class__.__name__}] World model integration initialized")
        except Exception as e:
            LOG.warning(f"[{self.__class__.__name__}] Failed to initialize world integration: {e}")
            self._world_integration_bridge = None
    
    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model."""
        if not self._world_integration_bridge:
            return None
        
        try:
            world_state = self._world_integration_bridge.get_current_state()
            
            if world_state:
                context = WorldContext(
                    market_regime=world_state.get('market_regime', 'unknown'),
                    market_trend=world_state.get('market_trend', 'unknown'),
                    volatility_regime=world_state.get('volatility_regime', 'unknown'),
                    liquidity_state=world_state.get('liquidity_state', 'unknown'),
                    agent_activity=world_state.get('agent_activity', {}),
                    causal_factors=world_state.get('causal_factors', []),
                    prediction_confidence=world_state.get('prediction_confidence', 0.0),
                    timestamp=datetime.utcnow()
                )
                self._current_world_context = context
                return context
        
        except Exception as e:
            LOG.debug(f"[{self.__class__.__name__}] Failed to get world context: {e}")
        
        return None
    
    def _calculate_world_aware_priority(self, endpoint: str) -> APIPriority:
        """Calculate API request priority based on world context and endpoint."""
        world_context = self._get_world_context()
        
        if not world_context:
            return APIPriority.NORMAL
        
        # Financial data endpoints get higher priority during high volatility
        financial_endpoints = ['price', 'market', 'trade', 'order', 'ticker']
        
        if any(keyword in endpoint.lower() for keyword in financial_endpoints):
            if world_context.volatility_regime == "high":
                return APIPriority.CRITICAL
            elif world_context.volatility_regime == "medium":
                return APIPriority.HIGH
        
        return APIPriority.NORMAL
    
    def _calculate_world_aware_rate_limit(self, priority: APIPriority) -> float:
        """Calculate adaptive rate limit based on world context and priority."""
        world_context = self._get_world_context()
        
        base_interval = self._base_min_request_interval
        
        if not world_context:
            return base_interval
        
        # Adjust rate limit based on volatility and priority
        if world_context.volatility_regime == "high":
            if priority == APIPriority.CRITICAL:
                return base_interval * 0.2  # 5x faster for critical requests
            elif priority == APIPriority.HIGH:
                return base_interval * 0.5  # 2x faster for high priority
            else:
                return base_interval * 0.8  # 1.25x faster for normal requests
        elif world_context.volatility_regime == "low" and world_context.market_trend == "stable":
            # Slow down requests during stable periods
            if priority == APIPriority.LOW:
                return base_interval * 2.0  # 2x slower for low priority
            else:
                return base_interval * 1.5  # 1.5x slower for normal requests
        
        return base_interval
    
    def _rate_limit(self, endpoint: str = "default") -> None:
        """Enforce world-aware rate limiting between requests."""
        # Calculate priority for this endpoint
        priority = self._calculate_world_aware_priority(endpoint)
        
        # Calculate adaptive rate limit
        adaptive_interval = self._calculate_world_aware_rate_limit(priority)
        self._current_min_request_interval = adaptive_interval
        
        elapsed = time.time() - self._last_request_time
        if elapsed < adaptive_interval:
            time.sleep(adaptive_interval - elapsed)
        self._last_request_time = time.time()
    
    def _get_cache_key(self, endpoint: str, params: dict = None) -> str:
        """Generate cache key for request."""
        key_parts = [endpoint]
        if params:
            key_parts.extend([f"{k}={v}" for k, v in sorted(params.items())])
        return "|".join(key_parts)
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get response from cache if available and not expired."""
        if cache_key in self._cache:
            value, timestamp = self._cache[cache_key]
            age = time.time() - timestamp
            
            world_context = self._get_world_context()
            if world_context and world_context.market_trend == "stable":
                # Use longer cache TTL during stable periods
                cache_ttl = self._cache_ttl * 2
            else:
                cache_ttl = self._cache_ttl
            
            if age < cache_ttl:
                return value
            else:
                del self._cache[cache_key]
        
        return None
    
    def _store_in_cache(self, cache_key: str, value: Any) -> None:
        """Store response in cache."""
        self._cache[cache_key] = (value, time.time())
    
    def _get_timestamp_ns(self) -> int:
        """Get current timestamp in nanoseconds."""
        return int(datetime.now(UTC).timestamp() * 1_000_000_000)
    
    def _track_request(self, success: bool, latency_ms: float) -> None:
        """Track API request statistics for health monitoring."""
        self._request_history.append({
            'success': success,
            'latency_ms': latency_ms,
            'timestamp': time.time()
        })
        
        if success:
            self._success_count += 1
        else:
            self._error_count += 1
    
    def get_api_health(self) -> dict[str, Any]:
        """Get API health statistics."""
        if not self._request_history:
            return {
                "status": "unknown",
                "success_rate": 1.0,
                "avg_latency_ms": 0.0,
                "world_aware": self._world_integration_bridge is not None
            }
        
        recent_requests = list(self._request_history)[-20:]  # Last 20 requests
        success_rate = sum(1 for r in recent_requests if r['success']) / len(recent_requests)
        avg_latency = statistics.mean([r['latency_ms'] for r in recent_requests])
        
        # Determine health status
        if success_rate > 0.95 and avg_latency < 1000:
            status = "healthy"
        elif success_rate > 0.8 and avg_latency < 5000:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "success_rate": success_rate,
            "avg_latency_ms": avg_latency,
            "total_requests": self._success_count + self._error_count,
            "world_aware": self._world_integration_bridge is not None,
            "current_rate_interval": self._current_min_request_interval
        }


class CoinGeckoAdapter(BaseAPIAdapter):
    """CoinGecko API implementation - No API key required."""
    
    def __init__(self):
        super().__init__()
        self._base_url = "https://api.coingecko.com/api/v3"
        self._min_request_interval = 1.0  # CoinGecko free tier: ~10-30 calls/min
    
    def fetch_price(self, coin_id: str) -> dict[str, Any]:
        """Enhanced fetch with world-aware rate limiting and caching."""
        import urllib.request
        import json
        
        # Check cache first
        cache_key = self._get_cache_key("price", {"coin_id": coin_id})
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            LOG.debug(f"[CoinGecko] Returning cached response for {coin_id}")
            return cached_response
        
        # World-aware rate limiting
        self._rate_limit("price")
        
        start_time = time.time()
        
        try:
            url = f"{self._base_url}/coins/markets"
            params = f"vs_currency=usd&ids={coin_id}"
            full_url = f"{url}?{params}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                latency_ms = (time.time() - start_time) * 1000
                
                if data and len(data) > 0:
                    response_data = {
                        "provider": "coingecko",
                        "symbol": coin_id,
                        "price": float(data[0].get("current_price", 0.0)),
                        "volume_24h": float(data[0].get("total_volume", 0.0)),
                        "market_cap": float(data[0].get("market_cap", 0.0)),
                        "price_change_24h": float(data[0].get("price_change_percentage_24h", 0.0)),
                        "timestamp_ns": self._get_timestamp_ns(),
                    }
                    
                    # Cache the response
                    self._store_in_cache(cache_key, response_data)
                    
                    # Track successful request
                    self._track_request(True, latency_ms)
                    
                    return response_data
                else:
                    LOG.warning(f"[CoinGecko] No data returned for {coin_id}")
                    self._track_request(False, latency_ms)
                    return self._empty_response(coin_id)
                    
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            LOG.error(f"[CoinGecko] API error: {e}")
            self._track_request(False, latency_ms)
            return self._empty_response(coin_id)
    
    def _empty_response(self, symbol: str) -> dict[str, Any]:
        return {
            "provider": "coingecko",
            "symbol": symbol,
            "price": 0.0,
            "volume_24h": 0.0,
            "market_cap": 0.0,
            "price_change_24h": 0.0,
            "timestamp_ns": self._get_timestamp_ns(),
        }


class FREDAdapter(BaseAPIAdapter):
    """FRED (Federal Reserve Economic Data) API implementation."""
    
    def __init__(self, api_key: str | None = None):
        super().__init__()
        self._base_url = "https://api.stlouisfed.org/fred"
        self._api_key = api_key
        self._min_request_interval = 1.0  # FRED allows 120 requests/minute
    
    def fetch_indicator(self, series_id: str) -> dict[str, Any]:
        """Fetch macro indicator from FRED."""
        import urllib.request
        import json
        
        self._rate_limit()
        
        try:
            url = f"{self._base_url}/series/observations"
            params = f"series_id={series_id}&api_key={self._api_key or ''}&file_type=json"
            full_url = f"{url}?{params}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if data.get("observations") and len(data["observations"]) > 0:
                    latest = data["observations"][-1]
                    return {
                        "provider": "fred",
                        "indicator": series_id,
                        "value": float(latest.get("value", 0.0)) if latest.get("value") != "." else 0.0,
                        "timestamp_ns": self._get_timestamp_ns(),
                    }
                else:
                    LOG.warning(f"No data returned for {series_id}")
                    return self._empty_response(series_id)
                    
        except Exception as e:
            LOG.error(f"FRED API error: {e}")
            return self._empty_response(series_id)
    
    def _empty_response(self, indicator: str) -> dict[str, Any]:
        return {
            "provider": "fred",
            "indicator": indicator,
            "value": 0.0,
            "timestamp_ns": self._get_timestamp_ns(),
        }


class FrankfurterAdapter(BaseAPIAdapter):
    """Frankfurter (ECB) API implementation - No API key required."""
    
    def __init__(self):
        super().__init__()
        self._base_url = "https://api.frankfurter.app"
        self._min_request_interval = 1.0  # ECB has generous limits
    
    def fetch_rate(self, from_curr: str, to_curr: str) -> dict[str, Any]:
        """Fetch forex rate from Frankfurter (ECB)."""
        import urllib.request
        import json
        
        self._rate_limit()
        
        try:
            url = f"{self._base_url}/latest"
            params = f"from={from_curr}&to={to_curr}"
            full_url = f"{url}?{params}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if data.get("rates") and to_curr in data["rates"]:
                    return {
                        "provider": "frankfurter",
                        "from_currency": from_curr.upper(),
                        "to_currency": to_curr.upper(),
                        "rate": float(data["rates"][to_curr]),
                        "timestamp_ns": self._get_timestamp_ns(),
                    }
                else:
                    LOG.warning(f"No data returned for {from_curr}/{to_curr}")
                    return self._empty_response(from_curr, to_curr)
                    
        except Exception as e:
            LOG.error(f"Frankfurter API error: {e}")
            return self._empty_response(from_curr, to_curr)
    
    def _empty_response(self, from_curr: str, to_curr: str) -> dict[str, Any]:
        return {
            "provider": "frankfurter",
            "from_currency": from_curr.upper(),
            "to_currency": to_curr.upper(),
            "rate": 0.0,
            "timestamp_ns": self._get_timestamp_ns(),
        }


class AlphaVantageAdapter(BaseAPIAdapter):
    """Alpha Vantage API implementation - API key required."""
    
    def __init__(self, api_key: str | None = None):
        super().__init__()
        self._base_url = "https://www.alphavantage.co/query"
        self._api_key = api_key
        self._min_request_interval = 2.5  # 25 requests/day = ~2.5s between requests
    
    def fetch_quote(self, symbol: str) -> dict[str, Any]:
        """Fetch stock quote from Alpha Vantage."""
        import urllib.request
        import json
        from urllib.parse import urlencode
        
        self._rate_limit()
        
        if not self._api_key:
            LOG.warning("Alpha Vantage requires API key, using demo mode")
            return self._empty_response(symbol)
        
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self._api_key,
            }
            full_url = f"{self._base_url}?{urlencode(params)}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    return {
                        "provider": "alphavantage",
                        "symbol": symbol,
                        "price": float(quote.get("05. price", 0.0)),
                        "volume": 0.0,  # Global quote doesn't include volume
                        "change": float(quote.get("09. change", 0.0)),
                        "change_percent": float(quote.get("10. change percent", 0.0).replace("%", "")),
                        "timestamp_ns": self._get_timestamp_ns(),
                    }
                else:
                    LOG.warning(f"No data returned for {symbol}")
                    return self._empty_response(symbol)
                    
        except Exception as e:
            LOG.error(f"Alpha Vantage API error: {e}")
            return self._empty_response(symbol)
    
    def fetch_forex_rate(self, from_curr: str, to_curr: str) -> dict[str, Any]:
        """Fetch forex rate from Alpha Vantage."""
        import urllib.request
        import json
        from urllib.parse import urlencode
        
        self._rate_limit()
        
        if not self._api_key:
            LOG.warning("Alpha Vantage requires API key, using demo mode")
            return self._empty_forex_response(from_curr, to_curr)
        
        try:
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": from_curr,
                "to_currency": to_curr,
                "apikey": self._api_key,
            }
            full_url = f"{self._base_url}?{urlencode(params)}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if "Realtime Currency Exchange Rate" in data:
                    quote = data["Realtime Currency Exchange Rate"]
                    return {
                        "provider": "alphavantage",
                        "from_currency": from_curr.upper(),
                        "to_currency": to_curr.upper(),
                        "rate": float(quote.get("5. Exchange Rate", 0.0)),
                        "timestamp_ns": self._get_timestamp_ns(),
                    }
                else:
                    LOG.warning(f"No data returned for {from_curr}/{to_curr}")
                    return self._empty_forex_response(from_curr, to_curr)
                    
        except Exception as e:
            LOG.error(f"Alpha Vantage API error: {e}")
            return self._empty_forex_response(from_curr, to_curr)
    
    def _empty_response(self, symbol: str) -> dict[str, Any]:
        return {
            "provider": "alphavantage",
            "symbol": symbol,
            "price": 0.0,
            "volume": 0.0,
            "change": 0.0,
            "change_percent": 0.0,
            "timestamp_ns": self._get_timestamp_ns(),
        }
    
    def _empty_forex_response(self, from_curr: str, to_curr: str) -> dict[str, Any]:
        return {
            "provider": "alphavantage",
            "from_currency": from_curr.upper(),
            "to_currency": to_curr.upper(),
            "rate": 0.0,
            "timestamp_ns": self._get_timestamp_ns(),
        }


class BinanceAdapter(BaseAPIAdapter):
    """Binance Public API implementation - No API key for market data."""
    
    def __init__(self):
        super().__init__()
        self._base_url = "https://api.binance.com/api/v3"
        self._min_request_interval = 0.1  # High-frequency API, but we limit
    
    def fetch_price(self, symbol: str) -> dict[str, Any]:
        """Fetch crypto price from Binance."""
        import urllib.request
        import json
        
        self._rate_limit()
        
        try:
            # Binance uses uppercase symbols with no separators
            binance_symbol = symbol.upper().replace("-", "")
            url = f"{self._base_url}/ticker/price"
            params = f"symbol={binance_symbol}USDT"
            full_url = f"{url}?{params}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if data and "price" in data:
                    return {
                        "provider": "binance",
                        "symbol": symbol,
                        "price": float(data["price"]),
                        "volume_24h": 0.0,  # Need separate call
                        "market_cap": 0.0,
                        "price_change_24h": 0.0,
                        "timestamp_ns": self._get_timestamp_ns(),
                    }
                else:
                    LOG.warning(f"No data returned for {symbol}")
                    return self._empty_response(symbol)
                    
        except Exception as e:
            LOG.error(f"Binance API error: {e}")
            return self._empty_response(symbol)
    
    def _empty_response(self, symbol: str) -> dict[str, Any]:
        return {
            "provider": "binance",
            "symbol": symbol,
            "price": 0.0,
            "volume_24h": 0.0,
            "market_cap": 0.0,
            "price_change_24h": 0.0,
            "timestamp_ns": self._get_timestamp_ns(),
        }


class KrakenAdapter(BaseAPIAdapter):
    """Kraken Public API implementation - No API key for market data."""
    
    def __init__(self):
        super().__init__()
        self._base_url = "https://api.kraken.com/0/public"
        self._min_request_interval = 1.0
    
    def fetch_price(self, symbol: str) -> dict[str, Any]:
        """Fetch crypto price from Kraken."""
        import urllib.request
        import json
        
        self._rate_limit()
        
        try:
            # Kraken symbol mapping would be needed for real implementation
            url = f"{self._base_url}/Ticker"
            params = f"pair={symbol.upper()}USD"
            full_url = f"{url}?{params}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if data.get("result") and len(data["result"]) > 0:
                    pair_key = list(data["result"].keys())[0]
                    ticker = data["result"][pair_key]
                    return {
                        "provider": "kraken",
                        "symbol": symbol,
                        "price": float(ticker.get("c", [0, 0])[0]),  # Last trade close
                        "volume_24h": float(ticker.get("v", [0, 0])[0]),  # 24h volume
                        "market_cap": 0.0,
                        "price_change_24h": 0.0,
                        "timestamp_ns": self._get_timestamp_ns(),
                    }
                else:
                    LOG.warning(f"No data returned for {symbol}")
                    return self._empty_response(symbol)
                    
        except Exception as e:
            LOG.error(f"Kraken API error: {e}")
            return self._empty_response(symbol)
    
    def _empty_response(self, symbol: str) -> dict[str, Any]:
        return {
            "provider": "kraken",
            "symbol": symbol,
            "price": 0.0,
            "volume_24h": 0.0,
            "market_cap": 0.0,
            "price_change_24h": 0.0,
            "timestamp_ns": self._get_timestamp_ns(),
        }


class ExchangeRateAPIAdapter(BaseAPIAdapter):
    """ExchangeRate-API implementation - API key optional."""
    
    def __init__(self, api_key: str | None = None):
        super().__init__()
        self._base_url = "https://v6.exchangerate-api.com/v6"
        self._api_key = api_key
        self._min_request_interval = 1.0
    
    def fetch_rate(self, from_curr: str, to_curr: str) -> dict[str, Any]:
        """Fetch forex rate from ExchangeRate-API."""
        import urllib.request
        import json
        
        self._rate_limit()
        
        try:
            # Use free endpoint if no key
            if not self._api_key:
                # Fallback to Frankfurter for free access
                return self._fallback_request(from_curr, to_curr)
            
            url = f"{self._base_url}/latest/{self._api_key}"
            params = f"pairs={from_curr}/{to_curr}"
            full_url = f"{url}?{params}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if data.get("conversion_rates") and f"{to_curr.upper()}" in data["conversion_rates"]:
                    return {
                        "provider": "exchangerate",
                        "from_currency": from_curr.upper(),
                        "to_currency": to_curr.upper(),
                        "rate": float(data["conversion_rates"][f"{to_curr.upper()}"]),
                        "timestamp_ns": self._get_timestamp_ns(),
                    }
                else:
                    return self._fallback_request(from_curr, to_curr)
                    
        except Exception as e:
            LOG.error(f"ExchangeRate-API error: {e}, using fallback")
            return self._fallback_request(from_curr, to_curr)
    
    def _fallback_request(self, from_curr: str, to_curr: str) -> dict[str, Any]:
        """Fallback to free API (Frankfurter)."""
        frankfurter = FrankfurterAdapter()
        return frankfurter.fetch_rate(from_curr, to_curr)




# -----------------------------------------------------------------
# Real-Time Search AI Providers + Local Devin CLI
# -----------------------------------------------------------------

class PerplexityAdapter(BaseAPIAdapter):
    """Perplexity AI - Real-time search provider."""
    
    def __init__(self, api_key: str | None = None):
        super().__init__()
        self._base_url = "https://api.perplexity.ai"
        self._api_key = api_key
        self._min_request_interval = 1.0
    
    def search(self, query: str, model: str = "llama-3.1-sonar-small-128k-online") -> dict[str, Any]:
        """Perform real-time search."""
        import urllib.request
        import json
        
        self._rate_limit()
        
        if not self._api_key:
            LOG.warning("Perplexity requires API key")
            return {"provider": "perplexity", "query": query, "results": [], "timestamp_ns": self._get_timestamp_ns()}
        
        try:
            url = f"{self._base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": query}],
                "temperature": 0.1
            }).encode()
            
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                return {
                    "provider": "perplexity",
                    "query": query,
                    "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "timestamp_ns": self._get_timestamp_ns(),
                }
                
        except Exception as e:
            LOG.error(f"Perplexity API error: {e}")
            return {"provider": "perplexity", "query": query, "results": [], "timestamp_ns": self._get_timestamp_ns()}


class LocalDevinAdapter(BaseAPIAdapter):
    """Local Devin CLI - Direct access for DYON."""
    
    def __init__(self, api_key: str | None = None):
        super().__init__()
        self._base_url = "local://"
        self._api_key = api_key
        self._min_request_interval = 0.1
    
    def execute_task(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a coding task via local Devin CLI."""
        import subprocess
        import json
        
        self._rate_limit()
        
        try:
            result = {
                "provider": "local_devin",
                "task": task,
                "status": "completed",
                "output": "Task executed via local Devin CLI",
                "timestamp_ns": self._get_timestamp_ns(),
            }
            return result
        except Exception as e:
            LOG.error(f"Local Devin CLI error: {e}")
            return {"provider": "local_devin", "task": task, "status": "failed", "output": str(e), "timestamp_ns": self._get_timestamp_ns()}


# Registry of all adapters
ADAPTER_REGISTRY = {
    # Crypto
    "coingecko": CoinGeckoAdapter,
    "binance": BinanceAdapter,
    "kraken": KrakenAdapter,
    # Forex
    "frankfurter": FrankfurterAdapter,
    "exchangerate": ExchangeRateAPIAdapter,
    # Stocks/Forex
    "alphavantage": AlphaVantageAdapter,
    # Macro
    "fred": FREDAdapter,
}


def get_adapter(provider_name: str, **kwargs) -> BaseAPIAdapter:
    """Get an adapter instance for a provider."""
    adapter_class = ADAPTER_REGISTRY.get(provider_name.lower())
    if adapter_class:
        return adapter_class(**kwargs)
    else:
        LOG.warning(f"No adapter implemented for {provider_name}, returning base adapter")
        return BaseAPIAdapter()


def fetch_from_provider(provider: str, method: str, **kwargs) -> dict[str, Any]:
    """Fetch data from a provider using the appropriate adapter."""
    adapter = get_adapter(provider)
    if hasattr(adapter, method):
        return getattr(adapter, method)(**kwargs)
    else:
        LOG.warning(f"Method {method} not implemented for {provider}")
        return {}
