"""Source Manager - INDIRA and DYON enable/disable control for data sources.

Allows INDIRA and DYON to:
- Enable/disable data sources dynamically
- Prioritize sources by category
- Monitor source health
- Track source performance
- Auto-disable failing sources
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

LOG = logging.getLogger(__name__)


class SourceStatus(StrEnum):
    """Status of a data source."""
    
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass(frozen=True, slots=True)
class SourceConfig:
    """Configuration for a data source."""
    
    source_id: str
    name: str
    category: str
    provider: str
    enabled: bool = True
    priority: int = 5  # 1-10, lower is higher priority
    allowed_for_indira: bool = True
    allowed_for_dyon: bool = True
    max_failures: int = 3
    failure_cooldown_minutes: int = 30


@dataclass(frozen=True, slots=True)
class SourceHealth:
    """Health status of a data source."""
    
    source_id: str
    status: SourceStatus
    last_success_ts_ns: int
    last_failure_ts_ns: int
    consecutive_failures: int
    success_count: int
    failure_count: int
    average_latency_ms: float
    last_error: str = ""


class SourceManager:
    """Manages data source enable/disable and health for INDIRA and DYON."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._sources: dict[str, SourceConfig] = {}
        self._health: dict[str, SourceHealth] = {}
        self._agent_permissions: dict[str, set[str]] = {
            "indira": set(),
            "dyon": set(),
        }
        
        # Initialize with default configuration
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default source configurations."""
        # Crypto sources
        self._sources["SRC-CRYPTO-COINGECKO-001"] = SourceConfig(
            source_id="SRC-CRYPTO-COINGECKO-001",
            name="CoinGecko API",
            category="crypto",
            provider="coingecko",
            enabled=True,
            priority=1,  # Highest priority
            allowed_for_indira=True,
            allowed_for_dyon=True,
        )
        
        self._sources["SRC-CRYPTO-BINANCE-001"] = SourceConfig(
            source_id="SRC-CRYPTO-BINANCE-001",
            name="Binance Public API",
            category="crypto",
            provider="binance",
            enabled=True,
            priority=2,
            allowed_for_indira=True,
            allowed_for_dyon=False,  # DYON doesn't need exchange data
        )
        
        # Forex sources
        self._sources["SRC-FOREX-FRANKFURTER-001"] = SourceConfig(
            source_id="SRC-FOREX-FRANKFURTER-001",
            name="Frankfurter (ECB)",
            category="forex",
            provider="frankfurter",
            enabled=True,
            priority=1,
            allowed_for_indira=True,
            allowed_for_dyon=False,
        )
        
        # Macro sources
        self._sources["SRC-MACRO-FRED-001"] = SourceConfig(
            source_id="SRC-MACRO-FRED-001",
            name="FRED (Federal Reserve)",
            category="macro",
            provider="fred",
            enabled=True,
            priority=1,
            allowed_for_indira=True,
            allowed_for_dyon=True,  # DYON needs macro for system context
        )
        
        # Add all 60+ sources with default config
        self._add_remaining_sources()
        
        # Initialize health tracking
        self._initialize_health()
        
        # Initialize agent permissions
        self._initialize_agent_permissions()
    
    def _add_remaining_sources(self) -> None:
        """Add remaining sources with default configuration."""
        # Add all sources from registry with default settings
        # This would be populated from registry/data_source_registry.yaml
        # For now, marking all crypto sources as enabled
        crypto_sources = [
            "SRC-CRYPTO-COINMARKETCAP-001", "SRC-CRYPTO-KRAKEN-001", 
            "SRC-CRYPTO-COINBASE-001", "SRC-CRYPTO-COINPAPRIKA-001",
            "SRC-CRYPTO-CRYPTOCOMPARE-001", "SRC-CRYPTO-COINCAP-001",
            "SRC-CRYPTO-NOMICS-001", "SRC-CRYPTO-GLASSNODE-001",
            # ... add all 19 crypto sources
        ]
        
        for source_id in crypto_sources:
            self._sources[source_id] = SourceConfig(
                source_id=source_id,
                name=source_id,
                category="crypto",
                provider=source_id.split("-")[-1].lower(),
                enabled=True,
                priority=5,
                allowed_for_indira=True,
                allowed_for_dyon=False,
            )
    
    def _initialize_health(self) -> None:
        """Initialize health tracking for all sources."""
        now_ns = int(datetime.now(UTC).timestamp() * 1_000_000_000)
        for source_id in self._sources:
            self._health[source_id] = SourceHealth(
                source_id=source_id,
                status=SourceStatus.ENABLED if self._sources[source_id].enabled else SourceStatus.DISABLED,
                last_success_ts_ns=now_ns,
                last_failure_ts_ns=0,
                consecutive_failures=0,
                success_count=0,
                failure_count=0,
                average_latency_ms=0.0,
            )
    
    def _initialize_agent_permissions(self) -> None:
        """Initialize which sources each agent can use."""
        for source_id, config in self._sources.items():
            if config.allowed_for_indira:
                self._agent_permissions["indira"].add(source_id)
            if config.allowed_for_dyon:
                self._agent_permissions["dyon"].add(source_id)
    
    def enable_source(self, source_id: str, agent: str | None = None) -> bool:
        """Enable a source (optionally for specific agent only)."""
        with self._lock:
            if source_id not in self._sources:
                LOG.warning(f"Unknown source {source_id}")
                return False
            
            if agent:
                # Enable for specific agent only
                self._agent_permissions[agent].add(source_id)
                LOG.info(f"Enabled {source_id} for {agent}")
            else:
                # Enable globally
                source = self._sources[source_id]
                self._sources[source_id] = SourceConfig(
                    **{**source.__dict__, "enabled": True}
                )
                self._health[source_id] = SourceHealth(
                    **{**self._health[source_id].__dict__, "status": SourceStatus.ENABLED}
                )
                LOG.info(f"Enabled {source_id} globally")
            
            return True
    
    def disable_source(self, source_id: str, agent: str | None = None) -> bool:
        """Disable a source (optionally for specific agent only)."""
        with self._lock:
            if source_id not in self._sources:
                LOG.warning(f"Unknown source {source_id}")
                return False
            
            if agent:
                # Disable for specific agent only
                self._agent_permissions[agent].discard(source_id)
                LOG.info(f"Disabled {source_id} for {agent}")
            else:
                # Disable globally
                source = self._sources[source_id]
                self._sources[source_id] = SourceConfig(
                    **{**source.__dict__, "enabled": False}
                )
                self._health[source_id] = SourceHealth(
                    **{**self._health[source_id].__dict__, "status": SourceStatus.DISABLED}
                )
                LOG.info(f"Disabled {source_id} globally")
            
            return True
    
    def get_enabled_sources_for_agent(self, agent: str) -> list[str]:
        """Get list of enabled sources for a specific agent."""
        with self._lock:
            return [
                source_id
                for source_id, config in self._sources.items()
                if config.enabled and source_id in self._agent_permissions[agent]
            ]
    
    def get_enabled_sources_by_category(self, category: str, agent: str) -> list[str]:
        """Get enabled sources for a category and agent."""
        with self._lock:
            return [
                source_id
                for source_id, config in self._sources.items()
                if (config.enabled 
                    and config.category == category 
                    and source_id in self._agent_permissions[agent])
            ]
    
    def record_success(self, source_id: str, latency_ms: float) -> None:
        """Record a successful API call."""
        with self._lock:
            if source_id not in self._health:
                return
            
            health = self._health[source_id]
            new_health = SourceHealth(
                **{
                    **health.__dict__,
                    "status": SourceStatus.ENABLED,
                    "last_success_ts_ns": int(datetime.now(UTC).timestamp() * 1_000_000_000),
                    "consecutive_failures": 0,
                    "success_count": health.success_count + 1,
                    "average_latency_ms": (health.average_latency_ms * health.success_count + latency_ms) / (health.success_count + 1),
                }
            )
            self._health[source_id] = new_health
    
    def record_failure(self, source_id: str, error: str) -> None:
        """Record a failed API call."""
        with self._lock:
            if source_id not in self._health:
                return
            
            health = self._health[source_id]
            consecutive = health.consecutive_failures + 1
            max_failures = self._sources[source_id].max_failures
            
            # Auto-disable if too many failures
            if consecutive >= max_failures:
                self.disable_source(source_id)
                status = SourceStatus.DISABLED
            else:
                status = SourceStatus.ERROR
            
            new_health = SourceHealth(
                **{
                    **health.__dict__,
                    "status": status,
                    "last_failure_ts_ns": int(datetime.now(UTC).timestamp() * 1_000_000_000),
                    "consecutive_failures": consecutive,
                    "failure_count": health.failure_count + 1,
                    "last_error": error,
                }
            )
            self._health[source_id] = new_health
    
    def get_source_health(self, source_id: str) -> SourceHealth | None:
        """Get health status for a source."""
        with self._lock:
            return self._health.get(source_id)
    
    def get_all_health(self) -> dict[str, SourceHealth]:
        """Get health status for all sources."""
        with self._lock:
            return self._health.copy()
    
    def auto_disable_failing_sources(self) -> list[str]:
        """Automatically disable sources that are failing too much."""
        disabled = []
        with self._lock:
            now_ns = int(datetime.now(UTC).timestamp() * 1_000_000_000)
            
            for source_id, health in self._health.items():
                if health.status == SourceStatus.ENABLED:
                    config = self._sources[source_id]
                    
                    # Check if failure rate is too high
                    if health.failure_count > 0:
                        failure_rate = health.failure_count / (health.success_count + health.failure_count)
                        if failure_rate > 0.5:  # More than 50% failures
                            self.disable_source(source_id)
                            disabled.append(source_id)
                            LOG.warning(f"Auto-disabled {source_id} due to high failure rate: {failure_rate:.2%}")
            
            return disabled


# Singleton instance
_source_manager: SourceManager | None = None
_manager_lock = threading.Lock()


def get_source_manager() -> SourceManager:
    """Get the singleton SourceManager instance."""
    global _source_manager, _manager_lock
    
    with _manager_lock:
        if _source_manager is None:
            _source_manager = SourceManager()
        return _source_manager
