"""
DIX VISION Data Integration Service

Provides additional data source integration, data normalization, quality checks,
pipeline health monitoring, and cost optimization for enhanced data capabilities.
"""

from __future__ import annotations

import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Types of data sources."""
    EXCHANGE_API = "exchange_api"
    MARKET_DATA = "market_data"
    NEWS_FEED = "news_feed"
    SOCIAL_MEDIA = "social_media"
    CUSTOM_API = "custom_api"
    DATABASE = "database"


class DataQuality(Enum):
    """Data quality levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INVALID = "invalid"


@dataclass
class DataSource:
    """Data source configuration."""
    source_id: str
    source_name: str
    source_type: DataSourceType
    endpoint: str
    api_key: str = ""
    enabled: bool = True
    rate_limit: int = 1000  # requests per hour
    priority: int = 5  # 1-10, higher is higher priority
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class DataRecord:
    """Normalized data record."""
    record_id: str
    source_id: str
    symbol: str
    timestamp: float
    data: Dict[str, Any]
    quality: DataQuality = DataQuality.MEDIUM
    normalized: bool = False
    validated: bool = False


@dataclass
class QualityCheck:
    """Data quality check result."""
    check_id: str
    source_id: str
    record_count: int
    passed_count: int
    failed_count: int
    quality_score: float
    issues: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


@dataclass
class PipelineHealth:
    """Data pipeline health status."""
    pipeline_id: str
    source_id: str
    status: str  # "healthy", "degraded", "failed"
    throughput: float = 0.0  # records per second
    latency: float = 0.0  # seconds
    error_rate: float = 0.0
    last_update: float = field(default_factory=time.time)


class DataNormalizer(ABC):
    """Abstract base class for data normalizers."""
    
    @abstractmethod
    def normalize(self, raw_data: Dict[str, Any], source_config: DataSource) -> Dict[str, Any]:
        """Normalize raw data to standard format."""
        pass


class DataIntegratorService(Service):
    """Data integration service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("data_integration_service")
        self._data_sources: Dict[str, DataSource] = {}
        self._data_records: deque = deque(maxlen=100000)
        self._normalizers: Dict[DataSourceType, DataNormalizer] = {}
        self._quality_checks: List[QualityCheck] = []
        self._pipeline_health: Dict[str, PipelineHealth] = {}
        self._data_costs: Dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()
        self._auto_quality_check = True
        self._quality_check_interval = 300  # 5 minutes
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the data integration service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            integration_config = config.get("data_integration", {})
            self._auto_quality_check = integration_config.get("auto_quality_check", True)
            self._quality_check_interval = integration_config.get("quality_check_interval", 300)
            
            # Initialize default data sources
            self._init_default_sources()
            
            # Initialize default normalizers
            self._init_default_normalizers()
            
            logger.info("Data Integration Service initialized")
            return True
        except Exception as e:
            logger.error(f"Data Integration Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the data integration service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start background quality checker
            if self._auto_quality_check:
                self._start_quality_checker()
            
            # Start background health monitor
            self._start_health_monitor()
            
            # Start background cost optimizer
            self._start_cost_optimizer()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Data Integration Service started")
            return True
        except Exception as e:
            logger.error(f"Data Integration Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the data integration service."""
        try:
            self.state = ServiceState.STOPPING
            self._auto_quality_check = False
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Data Integration Service stopped")
            return True
        except Exception as e:
            logger.error(f"Data Integration Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get data integration service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Data Integration Service - {len(self._data_sources)} data sources",
            details={
                "total_sources": len(self._data_sources),
                "active_sources": sum(1 for s in self._data_sources.values() if s.enabled),
                "total_records": len(self._data_records),
                "quality_checks": len(self._quality_checks),
                "healthy_pipelines": sum(1 for p in self._pipeline_health.values() if p.status == "healthy"),
                "total_cost": sum(self._data_costs.values())
            },
            timestamp=time.time()
        )
    
    def add_data_source(self, source: DataSource) -> bool:
        """Add a new data source."""
        with self._lock:
            if source.source_id in self._data_sources:
                logger.error(f"Data source {source.source_id} already exists")
                return False
            
            self._data_sources[source.source_id] = source
            logger.info(f"Added data source: {source.source_name}")
            return True
    
    def remove_data_source(self, source_id: str) -> bool:
        """Remove a data source."""
        with self._lock:
            if source_id not in self._data_sources:
                return False
            
            del self._data_sources[source_id]
            logger.info(f"Removed data source: {source_id}")
            return True
    
    def ingest_data(self, source_id: str, raw_data: Dict[str, Any]) -> Optional[DataRecord]:
        """Ingest and normalize data from a source."""
        with self._lock:
            source = self._data_sources.get(source_id)
            if not source or not source.enabled:
                logger.warning(f"Data source {source_id} not found or disabled")
                return None
            
            try:
                # Normalize data
                normalizer = self._normalizers.get(source.source_type)
                if normalizer:
                    normalized_data = normalizer.normalize(raw_data, source)
                else:
                    normalized_data = raw_data
                
                # Create data record
                record = DataRecord(
                    record_id=self._generate_id(),
                    source_id=source_id,
                    symbol=normalized_data.get("symbol", ""),
                    timestamp=normalized_data.get("timestamp", time.time()),
                    data=normalized_data,
                    normalized=normalizer is not None,
                    validated=False
                )
                
                # Add to records
                self._data_records.append(record)
                
                # Update cost
                self._data_costs[source_id] += 0.001  # Small cost per record
                
                return record
                
            except Exception as e:
                logger.error(f"Data ingestion failed for {source_id}: {e}")
                return None
    
    def register_normalizer(self, source_type: DataSourceType, normalizer: DataNormalizer) -> None:
        """Register a data normalizer for a source type."""
        with self._lock:
            self._normalizers[source_type] = normalizer
            logger.info(f"Registered normalizer for {source_type.value}")
    
    def perform_quality_check(self, source_id: str = None) -> QualityCheck:
        """Perform data quality check."""
        with self._lock:
            records = list(self._data_records)
            
            if source_id:
                records = [r for r in records if r.source_id == source_id]
            
            if not records:
                return QualityCheck(
                    check_id=self._generate_id(),
                    source_id=source_id or "all",
                    record_count=0,
                    passed_count=0,
                    failed_count=0,
                    quality_score=0.0,
                    issues=["No records to check"]
                )
            
            passed_count = 0
            failed_count = 0
            issues = []
            
            for record in records:
                # Check for required fields
                required_fields = ["symbol", "timestamp", "data"]
                missing_fields = [f for f in required_fields if f not in record.data or record.data.get(f) is None]
                
                if missing_fields:
                    failed_count += 1
                    issues.append(f"Missing fields: {missing_fields}")
                    record.quality = DataQuality.INVALID
                else:
                    # Check data validity
                    if self._validate_record(record):
                        passed_count += 1
                        record.quality = DataQuality.HIGH
                    else:
                        failed_count += 1
                        issues.append("Data validation failed")
                        record.quality = DataQuality.LOW
            
            quality_score = passed_count / len(records) if records else 0.0
            
            quality_check = QualityCheck(
                check_id=self._generate_id(),
                source_id=source_id or "all",
                record_count=len(records),
                passed_count=passed_count,
                failed_count=failed_count,
                quality_score=quality_score,
                issues=issues[:10]  # Limit to first 10 issues
            )
            
            self._quality_checks.append(quality_check)
            
            return quality_check
    
    def get_pipeline_health(self, source_id: str = None) -> List[PipelineHealth]:
        """Get pipeline health status."""
        with self._lock:
            if source_id:
                return [self._pipeline_health.get(f"{source_id}_pipeline")]
            
            return list(self._pipeline_health.values())
    
    def update_pipeline_health(self, source_id: str, status: str, throughput: float = 0.0,
                             latency: float = 0.0, error_rate: float = 0.0) -> None:
        """Update pipeline health status."""
        pipeline_id = f"{source_id}_pipeline"
        
        with self._lock:
            if pipeline_id not in self._pipeline_health:
                self._pipeline_health[pipeline_id] = PipelineHealth(
                    pipeline_id=pipeline_id,
                    source_id=source_id,
                    status=status
                )
            
            health = self._pipeline_health[pipeline_id]
            health.status = status
            health.throughput = throughput
            health.latency = latency
            health.error_rate = error_rate
            health.last_update = time.time()
    
    def get_data_costs(self) -> Dict[str, float]:
        """Get data costs by source."""
        with self._lock:
            return dict(self._data_costs)
    
    def optimize_costs(self) -> Dict[str, Any]:
        """Optimize data costs."""
        with self._lock:
            recommendations = []
            
            for source_id, cost in self._data_costs.items():
                source = self._data_sources.get(source_id)
                if not source:
                    continue
                
                # Check if source is high cost and low priority
                if cost > 100.0 and source.priority < 5:
                    recommendations.append({
                        "source_id": source_id,
                        "action": "disable",
                        "reason": "High cost with low priority",
                        "current_cost": cost
                    })
                
                # Check if source can be rate-limited
                if cost > 50.0 and source.rate_limit > 100:
                    recommendations.append({
                        "source_id": source_id,
                        "action": "reduce_rate_limit",
                        "reason": "Reduce rate limit to lower costs",
                        "current_rate_limit": source.rate_limit,
                        "suggested_limit": source.rate_limit // 2
                    })
            
            return {
                "total_cost": sum(self._data_costs.values()),
                "recommendations": recommendations,
                "potential_savings": sum(r.get("current_cost", 0) * 0.5 for r in recommendations)
            }
    
    def get_data_records(self, source_id: str = None, symbol: str = None,
                       limit: int = 100) -> List[DataRecord]:
        """Get data records with filters."""
        with self._lock:
            records = list(self._data_records)
            
            if source_id:
                records = [r for r in records if r.source_id == source_id]
            
            if symbol:
                records = [r for r in records if r.symbol == symbol]
            
            return records[-limit:]
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics."""
        with self._lock:
            total_records = len(self._data_records)
            
            # Records by source
            records_by_source = defaultdict(int)
            for record in self._data_records:
                records_by_source[record.source_id] += 1
            
            # Records by quality
            records_by_quality = defaultdict(int)
            for record in self._data_records:
                records_by_quality[record.quality.value] += 1
            
            # Normalization rate
            normalized_count = sum(1 for r in self._data_records if r.normalized)
            normalization_rate = normalized_count / total_records if total_records > 0 else 0.0
            
            return {
                "total_records": total_records,
                "records_by_source": dict(records_by_source),
                "records_by_quality": dict(records_by_quality),
                "normalization_rate": normalization_rate,
                "validation_rate": sum(1 for r in self._data_records if r.validated) / total_records if total_records > 0 else 0.0,
                "total_sources": len(self._data_sources),
                "active_sources": sum(1 for s in self._data_sources.values() if s.enabled)
            }
    
    def _validate_record(self, record: DataRecord) -> bool:
        """Validate a data record."""
        # Check timestamp is reasonable
        if record.timestamp < time.time() - 86400 * 365:  # More than 1 year old
            return False
        
        # Check timestamp is not in future
        if record.timestamp > time.time() + 3600:  # More than 1 hour in future
            return False
        
        # Check numeric fields are valid
        for key, value in record.data.items():
            if isinstance(value, (int, float)):
                if not (-1e10 <= value <= 1e10):  # Reasonable range
                    return False
        
        return True
    
    def _init_default_sources(self) -> None:
        """Initialize default data sources."""
        # Example data sources (would be configured from config in production)
        default_sources = [
            DataSource(
                source_id="market_data_primary",
                source_name="Primary Market Data",
                source_type=DataSourceType.MARKET_DATA,
                endpoint="https://api.example.com/market",
                priority=10
            ),
            DataSource(
                source_id="news_feed_primary",
                source_name="Primary News Feed",
                source_type=DataSourceType.NEWS_FEED,
                endpoint="https://api.example.com/news",
                priority=7
            )
        ]
        
        for source in default_sources:
            self.add_data_source(source)
    
    def _init_default_normalizers(self) -> None:
        """Initialize default data normalizers."""
        # Register default normalizer for market data
        class MarketDataNormalizer(DataNormalizer):
            def normalize(self, raw_data: Dict[str, Any], source_config: DataSource) -> Dict[str, Any]:
                # Normalize market data to standard format
                return {
                    "symbol": raw_data.get("symbol", ""),
                    "timestamp": raw_data.get("timestamp", time.time()),
                    "price": float(raw_data.get("price", 0.0)),
                    "volume": int(raw_data.get("volume", 0)),
                    "bid": float(raw_data.get("bid", 0.0)),
                    "ask": float(raw_data.get("ask", 0.0)),
                    "data": raw_data
                }
        
        self.register_normalizer(DataSourceType.MARKET_DATA, MarketDataNormalizer())
    
    def _start_quality_checker(self) -> None:
        """Start background quality checker."""
        def check_quality():
            while self._auto_quality_check and self.state == ServiceState.RUNNING:
                try:
                    for source_id in self._data_sources.keys():
                        self.perform_quality_check(source_id)
                    
                    time.sleep(self._quality_check_interval)
                except Exception as e:
                    logger.error(f"Quality check error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=check_quality, daemon=True)
        thread.start()
        logger.info("Quality checker started")
    
    def _start_health_monitor(self) -> None:
        """Start background health monitor."""
        def monitor_health():
            while self.state == ServiceState.RUNNING:
                try:
                    with self._lock:
                        for source_id in self._data_sources.keys():
                            source = self._data_sources[source_id]
                            if source.enabled:
                                # Calculate health metrics
                                recent_records = [r for r in self._data_records if r.source_id == source_id]
                                
                                if recent_records:
                                    throughput = len(recent_records) / 3600  # Per second over last hour
                                    error_rate = sum(1 for r in recent_records if r.quality == DataQuality.INVALID) / len(recent_records)
                                    
                                    self.update_pipeline_health(
                                        source_id,
                                        "healthy" if error_rate < 0.05 else "degraded",
                                        throughput,
                                        0.1,  # Simulated latency
                                        error_rate
                                    )
                    
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Health monitor error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=monitor_health, daemon=True)
        thread.start()
        logger.info("Health monitor started")
    
    def _start_cost_optimizer(self) -> None:
        """Start background cost optimizer."""
        def optimize_costs():
            while self.state == ServiceState.RUNNING:
                try:
                    optimization = self.optimize_costs()
                    
                    if optimization["recommendations"]:
                        logger.info(f"Cost optimization: {len(optimization['recommendations'])} recommendations")
                    
                    # Apply recommendations (in production, this would be more sophisticated)
                    for rec in optimization["recommendations"]:
                        if rec["action"] == "disable" and rec["source_id"] in self._data_sources:
                            self._data_sources[rec["source_id"]].enabled = False
                    
                    time.sleep(3600)  # Optimize every hour
                except Exception as e:
                    logger.error(f"Cost optimization error: {e}")
                    time.sleep(300)
        
        thread = threading.Thread(target=optimize_costs, daemon=True)
        thread.start()
        logger.info("Cost optimizer started")
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())


# Global instance
_data_integrator_service: Optional[DataIntegratorService] = None


def get_data_integrator_service() -> DataIntegratorService:
    """Get global data integrator service instance."""
    global _data_integrator_service
    if _data_integrator_service is None:
        _data_integrator_service = DataIntegratorService()
    return _data_integrator_service