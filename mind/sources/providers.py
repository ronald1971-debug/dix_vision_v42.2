"""
Market Data Providers - Real Implementation

Provides comprehensive data source providers for market data integration,
critical for indicator processing and world understanding.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
import time
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    RATE_LIMITED = "rate_limited"


class DataType(Enum):
    """Types of data that can be provided."""
    OHLCV = "ohlcv"  # Open, High, Low, Close, Volume
    TICK = "tick"  # Tick-by-tick data
    ORDER_BOOK = "order_book"  # Limit order book data
    TRADES = "trades"  # Individual trades
    FUNDING = "funding"  # Funding rates
    SOCIAL = "social"  # Social sentiment
    NEWS = "news"  # News data
    ON_CHAIN = "on_chain"  # Blockchain data


class ProviderPriority(Enum):
    """Provider priority for data selection."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    FALLBACK = "fallback"


@dataclass
class ProviderConfig:
    """Configuration for a data provider."""
    provider_id: str
    provider_name: str
    provider_type: str  # e.g., "exchange", "aggregator", "custom"
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    priority: ProviderPriority = ProviderPriority.SECONDARY
    supported_data_types: List[DataType] = field(default_factory=list)
    supported_symbols: List[str] = field(default_factory=list)
    rate_limit_per_minute: int = 60
    timeout_seconds: int = 30
    retry_attempts: int = 3
    enabled: bool = True
    last_health_check: Optional[datetime] = None
    health_check_interval_minutes: int = 5


@dataclass
class DataQualityMetrics:
    """Quality metrics for data from a provider."""
    completeness_score: float  # 0.0 to 1.0
    accuracy_score: float  # 0.0 to 1.0
    timeliness_score: float  # 0.0 to 1.0  # Lower latency = higher score
    consistency_score: float  # 0.0 to 1.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ProviderMetrics:
    """Operational metrics for a data provider."""
    provider_id: str
    status: ProviderStatus
    uptime_percentage: float
    average_latency_ms: float
    success_rate: float
    total_requests: int
    failed_requests: int
    last_successful_request: Optional[datetime]
    last_failed_request: Optional[datetime]
    data_quality: Optional[DataQualityMetrics] = None


class DataProvider(ABC):
    """Abstract base class for data providers."""
    
    def __init__(self, config: ProviderConfig):
        self._config = config
        self._status = ProviderStatus.INACTIVE
        self._metrics = ProviderMetrics(
            provider_id=config.provider_id,
            status=ProviderStatus.INACTIVE,
            uptime_percentage=0.0,
            average_latency_ms=0.0,
            success_rate=0.0,
            total_requests=0,
            failed_requests=0,
            last_successful_request=None,
            last_failed_request=None
        )
        self._request_count_last_minute = 0
        self._last_minute_reset = time.time()
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the data provider."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection to the data provider."""
        pass
    
    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, timeframe: str, 
                          start: datetime, end: datetime) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data."""
        pass
    
    @abstractmethod
    async def fetch_tick_data(self, symbol: str, 
                             start: datetime, end: datetime) -> Optional[pd.DataFrame]:
        """Fetch tick-by-tick data."""
        pass
    
    @abstractmethod
    async def fetch_order_book(self, symbol: str, depth: int = 10) -> Optional[Dict[str, Any]]:
        """Fetch current order book."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and accessible."""
        pass
    
    def get_config(self) -> ProviderConfig:
        """Get provider configuration."""
        return self._config
    
    def get_metrics(self) -> ProviderMetrics:
        """Get provider metrics."""
        return self._metrics
    
    def get_status(self) -> ProviderStatus:
        """Get current provider status."""
        return self._status
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit has been exceeded."""
        current_time = time.time()
        if current_time - self._last_minute_reset >= 60:
            self._request_count_last_minute = 0
            self._last_minute_reset = current_time
            return True
        
        if self._request_count_last_minute >= self._config.rate_limit_per_minute:
            self._status = ProviderStatus.RATE_LIMITED
            logger.warning(f"[PROVIDER] Rate limit exceeded for {self._config.provider_id}")
            return False
        
        return True
    
    def _increment_request_count(self, success: bool, latency_ms: float):
        """Update metrics after a request."""
        self._metrics.total_requests += 1
        self._request_count_last_minute += 1
        
        if success:
            self._metrics.last_successful_request = datetime.now()
            # Update success rate using exponential moving average
            if self._metrics.total_requests == 1:
                self._metrics.success_rate = 1.0
            else:
                self._metrics.success_rate = 0.95 * self._metrics.success_rate + 0.05 * 1.0
            
            # Update average latency
            if self._metrics.total_requests == 1:
                self._metrics.average_latency_ms = latency_ms
            else:
                self._metrics.average_latency_ms = (
                    0.9 * self._metrics.average_latency_ms + 0.1 * latency_ms
                )
        else:
            self._metrics.failed_requests += 1
            self._metrics.last_failed_request = datetime.now()
            if self._metrics.total_requests == 1:
                self._metrics.success_rate = 0.0
            else:
                self._metrics.success_rate = 0.95 * self._metrics.success_rate + 0.05 * 0.0


class CCXTExchangeProvider(DataProvider):
    """Real CCXT-backed exchange provider for market data.
    
    This provider connects to real exchanges via CCXT library to fetch
    actual market data (OHLCV, tick data, order book). No mock data -
    all data is from live exchange connections.
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._data_cache: Dict[str, List[Dict]] = {}
        self._ccxt_exchange = None
        self._connected = False
        
        # Extract exchange name from config (default to binance)
        self._exchange_name = config.extra_config.get('exchange', 'binance').lower()
        
        # CCXT credentials
        self._api_key = config.extra_config.get('api_key', '')
        self._api_secret = config.extra_config.get('api_secret', '')
        
        try:
            import ccxt
            self._ccxt_module = ccxt
        except ImportError:
            raise ImportError(
                "CCXT library is required for CCXTExchangeProvider. "
                "Install with: pip install ccxt"
            )
        
        logger.info(f"[PROVIDER] Initializing CCXTExchangeProvider for {self._exchange_name}")
    
    def _timeframe_to_ccxt(self, timeframe: str) -> str:
        """Convert timeframe string to CCXT format."""
        timeframe_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1w',
            '1M': '1M',
        }
        return timeframe_map.get(timeframe, timeframe)
        
    async def connect(self) -> bool:
        """Connect to real exchange via CCXT."""
        try:
            # Initialize CCXT exchange
            exchange_class = getattr(self._ccxt_module, self._exchange_name, None)
            if exchange_class is None:
                raise ValueError(f"Exchange {self._exchange_name} not supported by CCXT")
            
            # Create exchange instance with credentials
            self._ccxt_exchange = exchange_class({
                'apiKey': self._api_key,
                'secret': self._api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
            
            # Load markets
            await self._ccxt_exchange.load_markets()
            
            # Test connection with ping
            await self._ccxt_exchange.fetch_ticker('BTC/USDT')
            
            self._connected = True
            self._status = ProviderStatus.ACTIVE
            logger.info(f"[PROVIDER] Connected to real exchange {self._exchange_name}")
            return True
            
        except Exception as e:
            logger.error(f"[PROVIDER] Failed to connect to {self._exchange_name}: {e}")
            self._status = ProviderStatus.ERROR
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from exchange."""
        try:
            if self._ccxt_exchange:
                await self._ccxt_exchange.close()
            self._connected = False
            self._status = ProviderStatus.INACTIVE
            logger.info(f"[PROVIDER] Disconnected from {self._exchange_name}")
            return True
        except Exception as e:
            logger.error(f"[PROVIDER] Error disconnecting from {self._exchange_name}: {e}")
            return False
    
    async def fetch_ohlcv(self, symbol: str, timeframe: str, 
                          start: datetime, end: datetime) -> Optional[pd.DataFrame]:
        """Fetch real OHLCV data from exchange via CCXT."""
        if not self._check_rate_limit():
            return None
        
        if not self._connected:
            logger.error("[PROVIDER] Not connected to exchange")
            return None
        
        start_time = time.time()
        
        try:
            # Convert datetime to CCXT timestamp format (milliseconds)
            since = int(start.timestamp() * 1000)
            
            # Map timeframe string to CCXT format
            ccxt_timeframe = self._timeframe_to_ccxt(timeframe)
            
            # Fetch OHLCV data from exchange
            ohlcv = await self._ccxt_exchange.fetch_ohlcv(
                symbol, 
                timeframe=ccxt_timeframe, 
                since=since,
                limit=1000  # CCXT default limit
            )
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Filter by end time
            df = df[df['timestamp'] <= end]
            
            if df.empty:
                logger.warning(f"[PROVIDER] No OHLCV data returned for {symbol}")
                return None
            
            latency_ms = (time.time() - start_time) * 1000
            self._increment_request_count(True, latency_ms)
            
            logger.debug(f"[PROVIDER] Fetched {len(df)} OHLCV candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"[PROVIDER] Error fetching OHLCV from {self._exchange_name}: {e}")
            self._increment_request_count(False, 0)
            return None
    
    async def fetch_tick_data(self, symbol: str, 
                             start: datetime, end: datetime) -> Optional[pd.DataFrame]:
        """Fetch real tick data from exchange via CCXT.
        
        Note: Not all exchanges support tick data. Falls back to trade data if available.
        """
        if not self._check_rate_limit():
            return None
        
        if not self._connected:
            logger.error("[PROVIDER] Not connected to exchange")
            return None
        
        start_time = time.time()
        
        try:
            # Convert datetime to CCXT timestamp format
            since = int(start.timestamp() * 1000)
            
            # Fetch trades (closest to tick data available)
            trades = await self._ccxt_exchange.fetch_trades(
                symbol, 
                since=since, 
                limit=1000
            )
            
            if not trades:
                logger.warning(f"[PROVIDER] No trade data returned for {symbol}")
                return None
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Filter by end time
            df = df[df['timestamp'] <= end]
            
            if df.empty:
                logger.warning(f"[PROVIDER] No tick data in time range for {symbol}")
                return None
            
            # Rename columns to match expected format
            df = df.rename(columns={'amount': 'volume'})
            
            latency_ms = (time.time() - start_time) * 1000
            self._increment_request_count(True, latency_ms)
            
            logger.debug(f"[PROVIDER] Fetched {len(df)} tick/trade records for {symbol}")
            return df[['timestamp', 'price', 'volume', 'side']]
            
        except Exception as e:
            logger.error(f"[PROVIDER] Error fetching tick data from {self._exchange_name}: {e}")
            self._increment_request_count(False, 0)
            return None
    
    async def fetch_order_book(self, symbol: str, depth: int = 10) -> Optional[Dict[str, Any]]:
        """Fetch real order book from exchange via CCXT."""
        if not self._check_rate_limit():
            return None
        
        if not self._connected:
            logger.error("[PROVIDER] Not connected to exchange")
            return None
        
        start_time = time.time()
        
        try:
            # Fetch order book from exchange
            order_book = await self._ccxt_exchange.fetch_order_book(symbol, limit=depth)
            
            # Format response
            result = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'bids': order_book.get('bids', [])[:depth],
                'asks': order_book.get('asks', [])[:depth],
                'spread': 0.0
            }
            
            # Calculate spread
            if result['bids'] and result['asks']:
                result['spread'] = result['asks'][0][0] - result['bids'][0][0]
            
            latency_ms = (time.time() - start_time) * 1000
            self._increment_request_count(True, latency_ms)
            
            logger.debug(f"[PROVIDER] Fetched order book for {symbol} with depth {depth}")
            return result
            
        except Exception as e:
            logger.error(f"[PROVIDER] Error fetching order book from {self._exchange_name}: {e}")
            self._increment_request_count(False, 0)
            return None
    
    async def health_check(self) -> bool:
        """Perform real health check on exchange connection."""
        try:
            if not self._connected or not self._ccxt_exchange:
                return False
            
            # Fetch a ticker to test connection
            await self._ccxt_exchange.fetch_ticker('BTC/USDT')
            
            self._config.last_health_check = datetime.now()
            self._status = ProviderStatus.ACTIVE
            return True
            
        except Exception as e:
            logger.error(f"[PROVIDER] Health check failed: {e}")
            self._status = ProviderStatus.ERROR
            return False
            
            # Update uptime percentage
            total_minutes = (datetime.now() - self._config.last_health_check).total_seconds() / 60
            if total_minutes > 0:
                self._metrics.uptime_percentage = min(100.0, self._metrics.uptime_percentage + 0.1)
            
            return True
        except Exception:
            return False
    
    def _timeframe_to_seconds(self, timeframe: str) -> int:
        """Convert timeframe string to seconds."""
        timeframe_map = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400,
            '1w': 604800
        }
        return timeframe_map.get(timeframe, 3600)


class ProviderManager:
    """Manages multiple data providers with failover and load balancing."""
    
    def __init__(self):
        self._providers: Dict[str, DataProvider] = {}
        self._provider_configs: Dict[str, ProviderConfig] = {}
        self._initialized = False
        
    def register_provider(self, provider: DataProvider, config: ProviderConfig) -> None:
        """Register a data provider."""
        self._providers[config.provider_id] = provider
        self._provider_configs[config.provider_id] = config
        logger.info(f"[PROVIDER_MANAGER] Registered provider {config.provider_id}")
    
    def unregister_provider(self, provider_id: str) -> None:
        """Unregister a data provider."""
        if provider_id in self._providers:
            del self._providers[provider_id]
            del self._provider_configs[provider_id]
            logger.info(f"[PROVIDER_MANAGER] Unregistered provider {provider_id}")
    
    async def bootstrap_all_providers(self, **kwargs: Any) -> Dict[str, bool]:
        """Bootstrap all registered providers.
        
        Returns:
            Dictionary mapping provider_id to connection success status
        """
        bootstrap_results = {}
        
        for provider_id, provider in self._providers.items():
            config = self._provider_configs[provider_id]
            
            if not config.enabled:
                bootstrap_results[provider_id] = False
                logger.info(f"[PROVIDER_MANAGER] Skipping disabled provider {provider_id}")
                continue
            
            try:
                success = await provider.connect()
                bootstrap_results[provider_id] = success
                
                if success:
                    logger.info(f"[PROVIDER_MANAGER] Successfully bootstrapped {provider_id}")
                else:
                    logger.warning(f"[PROVIDER_MANAGER] Failed to bootstrap {provider_id}")
                    
            except Exception as e:
                bootstrap_results[provider_id] = False
                logger.error(f"[PROVIDER_MANAGER] Error bootstrapping {provider_id}: {e}")
        
        self._initialized = True
        successful_count = sum(1 for success in bootstrap_results.values() if success)
        logger.info(f"[PROVIDER_MANAGER] Bootstrap complete: {successful_count}/{len(bootstrap_results)} successful")
        
        return bootstrap_results
    
    async def shutdown_all_providers(self) -> Dict[str, bool]:
        """Shutdown all registered providers.
        
        Returns:
            Dictionary mapping provider_id to shutdown success status
        """
        shutdown_results = {}
        
        for provider_id, provider in self._providers.items():
            try:
                success = await provider.disconnect()
                shutdown_results[provider_id] = success
                logger.info(f"[PROVIDER_MANAGER] Shutdown {provider_id}: {success}")
            except Exception as e:
                shutdown_results[provider_id] = False
                logger.error(f"[PROVIDER_MANAGER] Error shutting down {provider_id}: {e}")
        
        self._initialized = False
        return shutdown_results
    
    def get_provider(self, provider_id: str) -> Optional[DataProvider]:
        """Get specific provider by ID."""
        return self._providers.get(provider_id)
    
    def get_providers_by_type(self, provider_type: str) -> List[DataProvider]:
        """Get all providers of a specific type."""
        return [
            provider for provider_id, provider in self._providers.items()
            if self._provider_configs[provider_id].provider_type == provider_type
        ]
    
    def get_providers_by_data_type(self, data_type: DataType) -> List[DataProvider]:
        """Get all providers that support a specific data type."""
        return [
            provider for provider_id, provider in self._providers.items()
            if data_type in self._provider_configs[provider_id].supported_data_types
        ]
    
    def get_primary_provider(self, data_type: DataType) -> Optional[DataProvider]:
        """Get the primary provider for a specific data type."""
        candidates = self.get_providers_by_data_type(data_type)
        
        # Filter by priority
        primary_candidates = [
            provider for provider in candidates
            if self._provider_configs[provider._config.provider_id].priority == ProviderPriority.PRIMARY
        ]
        
        if primary_candidates:
            # Return the healthiest primary provider
            return max(primary_candidates, key=lambda p: p.get_metrics().success_rate)
        
        # Fallback to secondary
        secondary_candidates = [
            provider for provider in candidates
            if self._provider_configs[provider._config.provider_id].priority == ProviderPriority.SECONDARY
        ]
        
        if secondary_candidates:
            return max(secondary_candidates, key=lambda p: p.get_metrics().success_rate)
        
        # Final fallback
        if candidates:
            return max(candidates, key=lambda p: p.get_metrics().success_rate)
        
        return None
    
    async def fetch_with_failover(self, data_type: DataType, fetch_func, 
                                  *args, **kwargs) -> Optional[Any]:
        """Fetch data with automatic failover between providers.
        
        Args:
            data_type: Type of data being requested
            fetch_func: Function to call on each provider
            *args: Arguments to pass to fetch_func
            **kwargs: Keyword arguments to pass to fetch_func
            
        Returns:
            Data from the first successful provider, or None if all fail
        """
        providers = self.get_providers_by_data_type(data_type)
        
        if not providers:
            logger.error(f"[PROVIDER_MANAGER] No providers available for data type {data_type}")
            return None
        
        # Sort by priority and health
        providers.sort(key=lambda p: (
            self._provider_configs[p._config.provider_id].priority.value,
            -p.get_metrics().success_rate
        ))
        
        last_error = None
        for provider in providers:
            if provider.get_status() != ProviderStatus.ACTIVE:
                continue
                
            try:
                result = await fetch_func(provider, *args, **kwargs)
                if result is not None:
                    logger.debug(f"[PROVIDER_MANAGER] Successfully fetched data from {provider._config.provider_id}")
                    return result
            except Exception as e:
                last_error = e
                logger.warning(f"[PROVIDER_MANAGER] Provider {provider._config.provider_id} failed: {e}")
                continue
        
        logger.error(f"[PROVIDER_MANAGER] All providers failed for data type {data_type}")
        return None
    
    def provider_summary(self, **kwargs: Any) -> Dict[str, Any]:
        """Get comprehensive summary of all providers."""
        summary = {
            "total_providers": len(self._providers),
            "initialized": self._initialized,
            "providers": {},
            "by_type": {},
            "by_status": {},
            "by_priority": {}
        }
        
        for provider_id, provider in self._providers.items():
            config = self._provider_configs[provider_id]
            metrics = provider.get_metrics()
            
            summary["providers"][provider_id] = {
                "name": config.provider_name,
                "type": config.provider_type,
                "priority": config.priority.value,
                "status": metrics.status.value,
                "uptime_percentage": metrics.uptime_percentage,
                "average_latency_ms": metrics.average_latency_ms,
                "success_rate": metrics.success_rate,
                "total_requests": metrics.total_requests,
                "failed_requests": metrics.failed_requests,
                "supported_data_types": [dt.value for dt in config.supported_data_types],
                "supported_symbols": config.supported_symbols[:10],  # Limit display
                "enabled": config.enabled
            }
            
            # Group by type
            if config.provider_type not in summary["by_type"]:
                summary["by_type"][config.provider_type] = []
            summary["by_type"][config.provider_type].append(provider_id)
            
            # Group by status
            if metrics.status.value not in summary["by_status"]:
                summary["by_status"][metrics.status.value] = []
            summary["by_status"][metrics.status.value].append(provider_id)
            
            # Group by priority
            if config.priority.value not in summary["by_priority"]:
                summary["by_priority"][config.priority.value] = []
            summary["by_priority"][config.priority.value].append(provider_id)
        
        # Calculate aggregate statistics
        if self._providers:
            total_requests = sum(p.get_metrics().total_requests for p in self._providers.values())
            total_failed = sum(p.get_metrics().failed_requests for p in self._providers.values())
            avg_success_rate = np.mean([p.get_metrics().success_rate for p in self._providers.values()])
            avg_latency = np.mean([p.get_metrics().average_latency_ms for p in self._providers.values()])
            
            summary["aggregate_statistics"] = {
                "total_requests": total_requests,
                "total_failed_requests": total_failed,
                "overall_success_rate": avg_success_rate,
                "average_latency_ms": avg_latency,
                "active_providers": len([p for p in self._providers.values() if p.get_status() == ProviderStatus.ACTIVE])
            }
        
        summary["timestamp"] = datetime.now()
        return summary
    
    async def perform_health_checks(self) -> Dict[str, bool]:
        """Perform health checks on all providers.
        
        Returns:
            Dictionary mapping provider_id to health check result
        """
        health_results = {}
        
        for provider_id, provider in self._providers.items():
            try:
                is_healthy = await provider.health_check()
                health_results[provider_id] = is_healthy
                
                if not is_healthy:
                    logger.warning(f"[PROVIDER_MANAGER] Health check failed for {provider_id}")
                    
            except Exception as e:
                health_results[provider_id] = False
                logger.error(f"[PROVIDER_MANAGER] Health check error for {provider_id}: {e}")
        
        return health_results


# Global provider manager instance
_provider_manager = ProviderManager()


def bootstrap_all_providers(**kwargs: Any) -> Dict[str, bool]:
    """Bootstrap all registered data providers.
    
    Args:
        **kwargs: Additional configuration parameters
        
    Returns:
        Dictionary mapping provider_id to connection success status
    """
    global _provider_manager
    
    # Set up default mock providers if no real ones are registered
    if not _provider_manager._providers:
        logger.info("[PROVIDERS] Setting up default mock providers")
        
        mock_config = ProviderConfig(
            provider_id="mock_exchange_1",
            provider_name="Mock Exchange 1",
            provider_type="exchange",
            priority=ProviderPriority.PRIMARY,
            supported_data_types=[DataType.OHLCV, DataType.TICK, DataType.ORDER_BOOK],
            supported_symbols=["BTC/USD", "ETH/USD", "SOL/USD"],
            rate_limit_per_minute=120
        )
        
        mock_provider = CCXTExchangeProvider(mock_config)
        _provider_manager.register_provider(mock_provider, mock_config)
    
    # Run async bootstrap
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_provider_manager.bootstrap_all_providers(**kwargs))


def provider_summary(**kwargs: Any) -> Dict[str, Any]:
    """Get comprehensive summary of all data providers.
    
    Args:
        **kwargs: Additional query parameters
        
    Returns:
        Comprehensive provider summary dictionary
    """
    global _provider_manager
    return _provider_manager.provider_summary(**kwargs)


def get_provider_manager() -> ProviderManager:
    """Get the global provider manager instance."""
    return _provider_manager


def register_provider(provider: DataProvider, config: ProviderConfig) -> None:
    """Register a new data provider.
    
    Args:
        provider: DataProvider instance
        config: ProviderConfig for the provider
    """
    get_provider_manager().register_provider(provider, config)


__all__ = [
    "ProviderStatus",
    "DataType",
    "ProviderPriority",
    "ProviderConfig",
    "DataQualityMetrics",
    "ProviderMetrics",
    "DataProvider",
    "CCXTExchangeProvider",
    "ProviderManager",
    "bootstrap_all_providers",
    "provider_summary",
    "get_provider_manager",
    "register_provider"
]