"""
DIX VISION Alternative Data Integration Service

Integrates alternative data sources including web3/blockchain, satellite imagery,
and IoT sensor data for enhanced market analysis and trading insights.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

# Import existing data integration service
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/runtime/services")
from data_integration_service import get_data_integrator_service, DataSource, DataSourceType

logger = logging.getLogger(__name__)


@dataclass
class AlternativeDataPoint:
    """Data point from alternative source."""
    data_id: str
    source_type: str  # "web3", "satellite", "iot"
    source_name: str
    data_content: Dict[str, Any]
    quality_score: float
    timestamp: datetime
    processing_latency: float


@dataclass
class Web3BlockchainData:
    """Web3/blockchain specific data."""
    chain_id: str
    token_address: str
    on_chain_metrics: Dict[str, float]
    mempool_analysis: Dict[str, Any]
    whale_tracking: List[Dict[str, Any]]
    smart_contract_events: List[Dict[str, Any]]
    timestamp: datetime


@dataclass
class SatelliteImageryData:
    """Satellite imagery specific data."""
    location: str
    imagery_type: str  # "economic_activity", "agriculture", "shipping", "energy"
    activity_metrics: Dict[str, float]
    infrastructure_changes: List[Dict[str, Any]]
    environmental_indicators: Dict[str, float]
    timestamp: datetime


@dataclass
class IoTData:
    """IoT sensor specific data."""
    sensor_id: str
    sensor_type: str  # "industrial", "agricultural", "shipping", "energy"
    location: str
    sensor_readings: Dict[str, float]
    trend_indicators: Dict[str, str]
    anomaly_detections: List[Dict[str, Any]]
    timestamp: datetime


class AlternativeDataIntegration:
    """
    Alternative data integration service.
    
    Integrates:
    - Web3/blockchain data for crypto and on-chain analysis
    - Satellite imagery for economic activity monitoring
    - IoT sensor data for real-world economic indicators
    """
    
    def __init__(self):
        # Initialize existing data integration service
        self._data_integrator = get_data_integrator_service()
        
        # Alternative data sources
        self._alternative_sources: Dict[str, DataSource] = {}
        
        # Data buffers
        self._web3_data_buffer: deque = deque(maxlen=1000)
        self._satellite_data_buffer: deque = deque(maxlen=500)
        self._iot_data_buffer: deque = deque(maxlen=2000)
        
        # Data quality tracking
        self._data_quality_scores: Dict[str, float] = {}
        
        # Integration status
        self._integration_status = {
            "web3": {"connected": False, "last_update": None},
            "satellite": {"connected": False, "last_update": None},
            "iot": {"connected": False, "last_update": None}
        }
        
        self._lock = threading.Lock()
        
        # Initialize alternative data sources
        self._initialize_alternative_sources()
        
        logger.info("Alternative Data Integration Service initialized")
    
    def _initialize_alternative_sources(self):
        """Initialize alternative data sources."""
        # Web3/Blockchain data source
        web3_source = DataSource(
            source_id="web3_blockchain_data",
            source_name="Web3 Blockchain Data",
            source_type=DataSourceType.MARKET_DATA,
            endpoint="https://api.web3.eth/blockchain",
            priority=8
        )
        self._alternative_sources["web3"] = web3_source
        self._data_integrator.add_data_source(web3_source)
        
        # Satellite imagery data source
        satellite_source = DataSource(
            source_id="satellite_imagery",
            source_name="Satellite Imagery Data",
            source_type=DataSourceType.NEWS_FEED,
            endpoint="https://api.satellite.com/imagery",
            priority=7
        )
        self._alternative_sources["satellite"] = satellite_source
        self._data_integrator.add_data_source(satellite_source)
        
        # IoT sensor data source
        iot_source = DataSource(
            source_id="iot_sensors",
            source_name="IoT Sensor Data",
            source_type=DataSourceType.MARKET_DATA,
            endpoint="https://api.iot.com/sensors",
            priority=6
        )
        self._alternative_sources["iot"] = iot_source
        self._data_integrator.add_data_source(iot_source)
        
        logger.info(f"Initialized {len(self._alternative_sources)} alternative data sources")
    
    def ingest_web3_data(self, blockchain_data: Dict[str, Any]) -> Web3BlockchainData:
        """Ingest and process web3/blockchain data."""
        # Extract blockchain metrics
        chain_id = blockchain_data.get("chain_id", "ethereum")
        token_address = blockchain_data.get("token_address", "")
        
        on_chain_metrics = {
            "price": blockchain_data.get("price", 0.0),
            "volume_24h": blockchain_data.get("volume_24h", 0.0),
            "market_cap": blockchain_data.get("market_cap", 0.0),
            "tx_count": blockchain_data.get("tx_count", 0),
            "gas_price": blockchain_data.get("gas_price", 0.0)
        }
        
        # Analyze mempool
        mempool_analysis = {
            "pending_tx_count": blockchain_data.get("pending_tx_count", 0),
            "gas_price_trend": blockchain_data.get("gas_price_trend", "stable"),
            "large_tx_alert": blockchain_data.get("large_tx_alert", False)
        }
        
        # Track whale movements
        whale_tracking = blockchain_data.get("whale_movements", [])
        
        # Extract smart contract events
        smart_contract_events = blockchain_data.get("contract_events", [])
        
        web3_data = Web3BlockchainData(
            chain_id=chain_id,
            token_address=token_address,
            on_chain_metrics=on_chain_metrics,
            mempool_analysis=mempool_analysis,
            whale_tracking=whale_tracking,
            smart_contract_events=smart_contract_events,
            timestamp=datetime.now()
        )
        
        # Calculate quality score
        quality_score = self._calculate_web3_quality(web3_data)
        
        # Create data point
        data_point = AlternativeDataPoint(
            data_id=f"web3_{int(datetime.now().timestamp())}",
            source_type="web3",
            source_name="Web3 Blockchain",
            data_content=web3_data.__dict__,
            quality_score=quality_score,
            timestamp=datetime.now(),
            processing_latency=0.1  # Simulated latency
        )
        
        with self._lock:
            self._web3_data_buffer.append(data_point)
            self._integration_status["web3"]["connected"] = True
            self._integration_status["web3"]["last_update"] = datetime.now().isoformat()
        
        logger.info(f"Ingested web3 data for {chain_id}, quality: {quality_score:.2f}")
        
        return web3_data
    
    def ingest_satellite_data(self, satellite_data: Dict[str, Any]) -> SatelliteImageryData:
        """Ingest and process satellite imagery data."""
        location = satellite_data.get("location", "unknown")
        imagery_type = satellite_data.get("imagery_type", "economic_activity")
        
        # Extract activity metrics
        activity_metrics = {
            "industrial_activity": satellite_data.get("industrial_activity", 0.0),
            "shipping_traffic": satellite_data.get("shipping_traffic", 0.0),
            "energy_consumption": satellite_data.get("energy_consumption", 0.0),
            "agricultural_activity": satellite_data.get("agricultural_activity", 0.0)
        }
        
        # Detect infrastructure changes
        infrastructure_changes = satellite_data.get("infrastructure_changes", [])
        
        # Extract environmental indicators
        environmental_indicators = {
            "cloud_cover": satellite_data.get("cloud_cover", 0.0),
            "night_lights": satellite_data.get("night_lights", 0.0),
            "vegetation_index": satellite_data.get("vegetation_index", 0.0)
        }
        
        satellite_imagery = SatelliteImageryData(
            location=location,
            imagery_type=imagery_type,
            activity_metrics=activity_metrics,
            infrastructure_changes=infrastructure_changes,
            environmental_indicators=environmental_indicators,
            timestamp=datetime.now()
        )
        
        # Calculate quality score
        quality_score = self._calculate_satellite_quality(satellite_imagery)
        
        # Create data point
        data_point = AlternativeDataPoint(
            data_id=f"satellite_{int(datetime.now().timestamp())}",
            source_type="satellite",
            source_name="Satellite Imagery",
            data_content=satellite_imagery.__dict__,
            quality_score=quality_score,
            timestamp=datetime.now(),
            processing_latency=0.5  # Higher latency for satellite data
        )
        
        with self._lock:
            self._satellite_data_buffer.append(data_point)
            self._integration_status["satellite"]["connected"] = True
            self._integration_status["satellite"]["last_update"] = datetime.now().isoformat()
        
        logger.info(f"Ingested satellite data for {location}, quality: {quality_score:.2f}")
        
        return satellite_imagery
    
    def ingest_iot_data(self, iot_data: Dict[str, Any]) -> IoTData:
        """Ingest and process IoT sensor data."""
        sensor_id = iot_data.get("sensor_id", "")
        sensor_type = iot_data.get("sensor_type", "industrial")
        location = iot_data.get("location", "unknown")
        
        # Extract sensor readings
        sensor_readings = {
            "temperature": iot_data.get("temperature", 0.0),
            "pressure": iot_data.get("pressure", 0.0),
            "vibration": iot_data.get("vibration", 0.0),
            "power_consumption": iot_data.get("power_consumption", 0.0),
            "throughput": iot_data.get("throughput", 0.0)
        }
        
        # Analyze trends
        trend_indicators = {
            "temperature_trend": iot_data.get("temperature_trend", "stable"),
            "power_trend": iot_data.get("power_trend", "stable"),
            "throughput_trend": iot_data.get("throughput_trend", "stable")
        }
        
        # Detect anomalies
        anomaly_detections = iot_data.get("anomalies", [])
        
        iot_sensor_data = IoTData(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            location=location,
            sensor_readings=sensor_readings,
            trend_indicators=trend_indicators,
            anomaly_detections=anomaly_detections,
            timestamp=datetime.now()
        )
        
        # Calculate quality score
        quality_score = self._calculate_iot_quality(iot_sensor_data)
        
        # Create data point
        data_point = AlternativeDataPoint(
            data_id=f"iot_{int(datetime.now().timestamp())}",
            source_type="iot",
            source_name="IoT Sensors",
            data_content=iot_sensor_data.__dict__,
            quality_score=quality_score,
            timestamp=datetime.now(),
            processing_latency=0.05  # Low latency for IoT data
        )
        
        with self._lock:
            self._iot_data_buffer.append(data_point)
            self._integration_status["iot"]["connected"] = True
            self._integration_status["iot"]["last_update"] = datetime.now().isoformat()
        
        logger.info(f"Ingested IoT data from {sensor_id}, quality: {quality_score:.2f}")
        
        return iot_sensor_data
    
    def _calculate_web3_quality(self, web3_data: Web3BlockchainData) -> float:
        """Calculate quality score for web3 data."""
        quality_score = 0.5  # Base score
        
        # Check data completeness
        if web3_data.on_chain_metrics.get("price", 0) > 0:
            quality_score += 0.2
        if web3_data.on_chain_metrics.get("volume_24h", 0) > 0:
            quality_score += 0.1
        if len(web3_data.whale_tracking) > 0:
            quality_score += 0.1
        if len(web3_data.smart_contract_events) > 0:
            quality_score += 0.1
        
        return min(1.0, quality_score)
    
    def _calculate_satellite_quality(self, satellite_data: SatelliteImageryData) -> float:
        """Calculate quality score for satellite data."""
        quality_score = 0.5  # Base score
        
        # Check data completeness
        if satellite_data.activity_metrics.get("industrial_activity", 0) > 0:
            quality_score += 0.2
        if len(satellite_data.infrastructure_changes) > 0:
            quality_score += 0.2
        if satellite_data.environmental_indicators.get("night_lights", 0) > 0:
            quality_score += 0.1
        
        return min(1.0, quality_score)
    
    def _calculate_iot_quality(self, iot_data: IoTData) -> float:
        """Calculate quality score for IoT data."""
        quality_score = 0.5  # Base score
        
        # Check data completeness
        valid_readings = sum(1 for v in iot_data.sensor_readings.values() if v > 0)
        quality_score += valid_readings * 0.1
        
        # Check for anomalies (anomalies can indicate data quality issues)
        if len(iot_data.anomaly_detections) == 0:
            quality_score += 0.2
        elif len(iot_data.anomaly_detections) < 3:
            quality_score += 0.1
        
        return min(1.0, quality_score)
    
    def get_integrated_market_insights(self) -> Dict[str, Any]:
        """Get integrated market insights from alternative data sources."""
        with self._lock:
            # Web3 insights
            web3_insights = {
                "total_data_points": len(self._web3_data_buffer),
                "average_quality": np.mean([d.quality_score for d in self._web3_data_buffer]) if self._web3_data_buffer else 0.0,
                "recent_whale_activity": len([d for d in self._web3_data_buffer if d.data_content.get("whale_tracking")])
            }
            
            # Satellite insights
            satellite_insights = {
                "total_data_points": len(self._satellite_data_buffer),
                "average_quality": np.mean([d.quality_score for d in self._satellite_data_buffer]) if self._satellite_data_buffer else 0.0,
                "locations_monitored": len(set([d.data_content.get("location") for d in self._satellite_data_buffer]))
            }
            
            # IoT insights
            iot_insights = {
                "total_data_points": len(self._iot_data_buffer),
                "average_quality": np.mean([d.quality_score for d in self._iot_data_buffer]) if self._iot_data_buffer else 0.0,
                "active_sensors": len(set([d.data_content.get("sensor_id") for d in self._iot_data_buffer])),
                "anomaly_count": sum(len(d.data_content.get("anomaly_detections", [])) for d in self._iot_data_buffer)
            }
            
            return {
                "web3": web3_insights,
                "satellite": satellite_insights,
                "iot": iot_insights,
                "integration_status": self._integration_status,
                "total_sources": len(self._alternative_sources)
            }


# Global instance
_alternative_data_integration: Optional[AlternativeDataIntegration] = None


def get_alternative_data_integration() -> AlternativeDataIntegration:
    """Get global alternative data integration instance."""
    global _alternative_data_integration
    if _alternative_data_integration is None:
        _alternative_data_integration = AlternativeDataIntegration()
    return _alternative_data_integration