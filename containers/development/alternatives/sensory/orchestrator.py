"""
sensory.orchestrator
DIX VISION v42.2 — Sensory Orchestrator

Central coordination for sensory operations including market data sensors,
news sensors, social sentiment sensors, macro economic sensors, and on-chain
data sensors. Provides complete sensory array implementation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from system.time_source import now

logger = logging.getLogger(__name__)


@dataclass
class SensorData:
    """Data from a sensor."""
    
    sensor_name: str
    sensor_type: str  # "market" | "news" | "social" | "macro" | "onchain" | "alternative"
    data: dict[str, Any]
    confidence: float
    timestamp: str
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.timestamp:
            self.timestamp = now().utc_time.isoformat()


@dataclass
class SensorHealth:
    """Health status of a sensor."""

    sensor_name: str
    sensor_type: str  # "market" | "news" | "social" | "macro" | "onchain" | "alternative"
    is_active: bool
    last_update: str = ""
    data_points_received: int = 0
    error_count: int = 0
    health_score: float = 1.0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SensoryOrchestrator:
    """Orchestrates sensory operations.
    
    Provides:
    - Market data sensing
    - News and narrative sensing
    - Social sentiment sensing
    - Macro economic sensing
    - On-chain data sensing
    - Alternative data sensing
    - Multi-sensor fusion
    """
    
    def __init__(self) -> None:
        self._sensors: dict[str, SensorHealth] = {}
        self._sensor_data: list[SensorData] = []
        self._fusion_enabled = True
        self._market_sensor_enabled = True
        self._news_sensor_enabled = True
        self._social_sensor_enabled = True
        self._macro_sensor_enabled = True
        self._onchain_sensor_enabled = True
        self._alternative_sensor_enabled = True
        
        # Initialize sensors
        self._initialize_sensors()
    
    def _initialize_sensors(self) -> None:
        """Initialize all sensors."""
        sensors = [
            SensorHealth(sensor_name="market_sensor", sensor_type="market", is_active=True),
            SensorHealth(sensor_name="news_sensor", sensor_type="news", is_active=True),
            SensorHealth(sensor_name="social_sensor", sensor_type="social", is_active=True),
            SensorHealth(sensor_name="macro_sensor", sensor_type="macro", is_active=True),
            SensorHealth(sensor_name="onchain_sensor", sensor_type="onchain", is_active=True),
            SensorHealth(sensor_name="alternative_sensor", sensor_type="alternative", is_active=True)
        ]
        
        for sensor in sensors:
            self._sensors[sensor.sensor_name] = sensor
        
        logger.info(f"[SENSORY] Initialized {len(sensors)} sensors")
    
    def start(self) -> bool:
        """Start the sensory orchestrator."""
        try:
            logger.info("[SENSORY] Sensory orchestrator started")
            return True
        except Exception as e:
            logger.error(f"[SENSORY] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the sensory orchestrator."""
        try:
            logger.info("[SENSORY] Sensory orchestrator stopped")
            return True
        except Exception as e:
            logger.error(f"[SENSORY] Failed to stop: {e}")
            return False
    
    def enable_market_sensor(self) -> None:
        """Enable market sensor."""
        self._market_sensor_enabled = True
        if "market_sensor" in self._sensors:
            self._sensors["market_sensor"].is_active = True
        logger.info("[SENSORY] Market sensor enabled")
    
    def disable_market_sensor(self) -> None:
        """Disable market sensor."""
        self._market_sensor_enabled = False
        if "market_sensor" in self._sensors:
            self._sensors["market_sensor"].is_active = False
        logger.info("[SENSORY] Market sensor disabled")
    
    def enable_news_sensor(self) -> None:
        """Enable news sensor."""
        self._news_sensor_enabled = True
        if "news_sensor" in self._sensors:
            self._sensors["news_sensor"].is_active = True
        logger.info("[SENSORY] News sensor enabled")
    
    def disable_news_sensor(self) -> None:
        """Disable news sensor."""
        self._news_sensor_enabled = False
        if "news_sensor" in self._sensors:
            self._sensors["news_sensor"].is_active = False
        logger.info("[SENSORY] News sensor disabled")
    
    def enable_social_sensor(self) -> None:
        """Enable social sensor."""
        self._social_sensor_enabled = True
        if "social_sensor" in self._sensors:
            self._sensors["social_sensor"].is_active = True
        logger.info("[SENSORY] Social sensor enabled")
    
    def disable_social_sensor(self) -> None:
        """Disable social sensor."""
        self._social_sensor_enabled = False
        if "social_sensor" in self._sensors:
            self._sensors["social_sensor"].is_active = False
        logger.info("[SENSORY] Social sensor disabled")
    
    def enable_macro_sensor(self) -> None:
        """Enable macro sensor."""
        self._macro_sensor_enabled = True
        if "macro_sensor" in self._sensors:
            self._sensors["macro_sensor"].is_active = True
        logger.info("[SENSORY] Macro sensor enabled")
    
    def disable_macro_sensor(self) -> None:
        """Disable macro sensor."""
        self._macro_sensor_enabled = False
        if "macro_sensor" in self._sensors:
            self._sensors["macro_sensor"].is_active = False
        logger.info("[SENSORY] Macro sensor disabled")
    
    def enable_onchain_sensor(self) -> None:
        """Enable on-chain sensor."""
        self._onchain_sensor_enabled = True
        if "onchain_sensor" in self._sensors:
            self._sensors["onchain_sensor"].is_active = True
        logger.info("[SENSORY] On-chain sensor enabled")
    
    def disable_onchain_sensor(self) -> None:
        """Disable on-chain sensor."""
        self._onchain_sensor_enabled = False
        if "onchain_sensor" in self._sensors:
            self._sensors["onchain_sensor"].is_active = False
        logger.info("[SENSORY] On-chain sensor disabled")
    
    def enable_alternative_sensor(self) -> None:
        """Enable alternative sensor."""
        self._alternative_sensor_enabled = True
        if "alternative_sensor" in self._sensors:
            self._sensors["alternative_sensor"].is_active = True
        logger.info("[SENSORY] Alternative sensor enabled")
    
    def disable_alternative_sensor(self) -> None:
        """Disable alternative sensor."""
        self._alternative_sensor_enabled = False
        if "alternative_sensor" in self._sensors:
            self._sensors["alternative_sensor"].is_active = False
        logger.info("[SENSORY] Alternative sensor disabled")
    
    def enable_fusion(self) -> None:
        """Enable multi-sensor fusion."""
        self._fusion_enabled = True
        logger.info("[SENSORY] Sensor fusion enabled")
    
    def disable_fusion(self) -> None:
        """Disable multi-sensor fusion."""
        self._fusion_enabled = False
        logger.info("[SENSORY] Sensor fusion disabled")
    
    def sense_market(self, market_context: dict[str, Any]) -> SensorData:
        """Sense market data."""
        if not self._market_sensor_enabled:
            logger.warning("[SENSORY] Market sensor disabled, returning empty data")
            return SensorData(
                sensor_name="market_sensor",
                sensor_type="market",
                data={},
                confidence=0.0
            )
        
        try:
            # Simulate market sensing (production implementation would connect to real data sources)
            data = self._sense_market_data(market_context)
            
            sensor_data = SensorData(
                sensor_name="market_sensor",
                sensor_type="market",
                data=data,
                confidence=0.9,
                timestamp=now().utc_time.isoformat()
            )
            
            self._sensor_data.append(sensor_data)
            self._update_sensor_health("market_sensor", success=True)
            
            logger.debug(f"[SENSORY] Market sensing completed")
            return sensor_data
            
        except Exception as e:
            logger.error(f"[SENSORY] Market sensing failed: {e}")
            self._update_sensor_health("market_sensor", success=False)
            return SensorData(
                sensor_name="market_sensor",
                sensor_type="market",
                data={},
                confidence=0.0
            )
    
    def sense_news(self, news_context: dict[str, Any]) -> SensorData:
        """Sense news and narratives."""
        if not self._news_sensor_enabled:
            logger.warning("[SENSORY] News sensor disabled, returning empty data")
            return SensorData(
                sensor_name="news_sensor",
                sensor_type="news",
                data={},
                confidence=0.0
            )
        
        try:
            data = self._sense_news_data(news_context)
            
            sensor_data = SensorData(
                sensor_name="news_sensor",
                sensor_type="news",
                data=data,
                confidence=0.85,
                timestamp=now().utc_time.isoformat()
            )
            
            self._sensor_data.append(sensor_data)
            self._update_sensor_health("news_sensor", success=True)
            
            logger.debug(f"[SENSORY] News sensing completed")
            return sensor_data
            
        except Exception as e:
            logger.error(f"[SENSORY] News sensing failed: {e}")
            self._update_sensor_health("news_sensor", success=False)
            return SensorData(
                sensor_name="news_sensor",
                sensor_type="news",
                data={},
                confidence=0.0
            )
    
    def sense_social(self, social_context: dict[str, Any]) -> SensorData:
        """Sense social sentiment."""
        if not self._social_sensor_enabled:
            logger.warning("[SENSORY] Social sensor disabled, returning empty data")
            return SensorData(
                sensor_name="social_sensor",
                sensor_type="social",
                data={},
                confidence=0.0
            )
        
        try:
            data = self._sense_social_data(social_context)
            
            sensor_data = SensorData(
                sensor_name="social_sensor",
                sensor_type="social",
                data=data,
                confidence=0.8,
                timestamp=now().utc_time.isoformat()
            )
            
            self._sensor_data.append(sensor_data)
            self._update_sensor_health("social_sensor", success=True)
            
            logger.debug(f"[SENSORY] Social sensing completed")
            return sensor_data
            
        except Exception as e:
            logger.error(f"[SENSORY] Social sensing failed: {e}")
            self._update_sensor_health("social_sensor", success=False)
            return SensorData(
                sensor_name="social_sensor",
                sensor_type="social",
                data={},
                confidence=0.0
            )
    
    def sense_macro(self, macro_context: dict[str, Any]) -> SensorData:
        """Sense macro economic data."""
        if not self._macro_sensor_enabled:
            logger.warning("[SENSORY] Macro sensor disabled, returning empty data")
            return SensorData(
                sensor_name="macro_sensor",
                sensor_type="macro",
                data={},
                confidence=0.0
            )
        
        try:
            data = self._sense_macro_data(macro_context)
            
            sensor_data = SensorData(
                sensor_name="macro_sensor",
                sensor_type="macro",
                data=data,
                confidence=0.95,
                timestamp=now().utc_time.isoformat()
            )
            
            self._sensor_data.append(sensor_data)
            self._update_sensor_health("macro_sensor", success=True)
            
            logger.debug(f"[SENSORY] Macro sensing completed")
            return sensor_data
            
        except Exception as e:
            logger.error(f"[SENSORY] Macro sensing failed: {e}")
            self._update_sensor_health("macro_sensor", success=False)
            return SensorData(
                sensor_name="macro_sensor",
                sensor_type="macro",
                data={},
                confidence=0.0
            )
    
    def sense_onchain(self, onchain_context: dict[str, Any]) -> SensorData:
        """Sense on-chain data."""
        if not self._onchain_sensor_enabled:
            logger.warning("[SENSORY] On-chain sensor disabled, returning empty data")
            return SensorData(
                sensor_name="onchain_sensor",
                sensor_type="onchain",
                data={},
                confidence=0.0
            )
        
        try:
            data = self._sense_onchain_data(onchain_context)
            
            sensor_data = SensorData(
                sensor_name="onchain_sensor",
                sensor_type="onchain",
                data=data,
                confidence=0.9,
                timestamp=now().utc_time.isoformat()
            )
            
            self._sensor_data.append(sensor_data)
            self._update_sensor_health("onchain_sensor", success=True)
            
            logger.debug(f"[SENSORY] On-chain sensing completed")
            return sensor_data
            
        except Exception as e:
            logger.error(f"[SENSORY] On-chain sensing failed: {e}")
            self._update_sensor_health("onchain_sensor", success=False)
            return SensorData(
                sensor_name="onchain_sensor",
                sensor_type="onchain",
                data={},
                confidence=0.0
            )
    
    def sense_alternative(self, alternative_context: dict[str, Any]) -> SensorData:
        """Sense alternative data."""
        if not self._alternative_sensor_enabled:
            logger.warning("[SENSORY] Alternative sensor disabled, returning empty data")
            return SensorData(
                sensor_name="alternative_sensor",
                sensor_type="alternative",
                data={},
                confidence=0.0
            )
        
        try:
            data = self._sense_alternative_data(alternative_context)
            
            sensor_data = SensorData(
                sensor_name="alternative_sensor",
                sensor_type="alternative",
                data=data,
                confidence=0.75,
                timestamp=now().utc_time.isoformat()
            )
            
            self._sensor_data.append(sensor_data)
            self._update_sensor_health("alternative_sensor", success=True)
            
            logger.debug(f"[SENSORY] Alternative sensing completed")
            return sensor_data
            
        except Exception as e:
            logger.error(f"[SENSORY] Alternative sensing failed: {e}")
            self._update_sensor_health("alternative_sensor", success=False)
            return SensorData(
                sensor_name="alternative_sensor",
                sensor_type="alternative",
                data={},
                confidence=0.0
            )
    
    def fuse_sensors(self, sensor_data_list: list[SensorData]) -> dict[str, Any]:
        """Fuse data from multiple sensors."""
        if not self._fusion_enabled:
            logger.warning("[SENSORY] Sensor fusion disabled, returning raw data")
            return {"fused_data": False, "raw_data": [d.data for d in sensor_data_list]}
        
        try:
            # Simplified fusion logic (production implementation would use advanced fusion algorithms)
            fused_data = {
                "fused_data": True,
                "sensor_count": len(sensor_data_list),
                "confidence_average": sum(d.confidence for d in sensor_data_list) / len(sensor_data_list) if sensor_data_list else 0.0,
                "combined_insights": self._combine_insights(sensor_data_list),
                "fusion_timestamp": now().utc_time.isoformat()
            }
            
            logger.debug(f"[SENSORY] Sensor fusion completed for {len(sensor_data_list)} sensors")
            return fused_data
            
        except Exception as e:
            logger.error(f"[SENSORY] Sensor fusion failed: {e}")
            return {"fused_data": False, "error": str(e)}
    
    def _sense_market_data(self, context: dict[str, Any]) -> dict[str, Any]:
        """Simulate market data sensing."""
        return {
            "price": context.get("price", 0.0),
            "volume": context.get("volume", 0.0),
            "volatility": context.get("volatility", 0.0),
            "trend": context.get("trend", "neutral"),
            "liquidity": context.get("liquidity", "high")
        }
    
    def _sense_news_data(self, context: dict[str, Any]) -> dict[str, Any]:
        """Simulate news data sensing."""
        return {
            "headline": context.get("headline", ""),
            "sentiment": context.get("sentiment", 0.0),
            "relevance": context.get("relevance", 0.0),
            "source": context.get("source", ""),
            "category": context.get("category", "general")
        }
    
    def _sense_social_data(self, context: dict[str, Any]) -> dict[str, Any]:
        """Simulate social sentiment sensing."""
        return {
            "sentiment_score": context.get("sentiment_score", 0.0),
            "volume": context.get("volume", 0),
            "engagement": context.get("engagement", 0.0),
            "trending_topics": context.get("trending_topics", [])
        }
    
    def _sense_macro_data(self, context: dict[str, Any]) -> dict[str, Any]:
        """Simulate macro economic data sensing."""
        return {
            "gdp_growth": context.get("gdp_growth", 0.0),
            "inflation_rate": context.get("inflation_rate", 0.0),
            "interest_rate": context.get("interest_rate", 0.0),
            "unemployment_rate": context.get("unemployment_rate", 0.0),
            "economic_cycle": context.get("economic_cycle", "expansion")
        }
    
    def _sense_onchain_data(self, context: dict[str, Any]) -> dict[str, Any]:
        """Simulate on-chain data sensing."""
        return {
            "tx_volume": context.get("tx_volume", 0.0),
            "active_addresses": context.get("active_addresses", 0),
            "gas_usage": context.get("gas_usage", 0.0),
            "network_hashrate": context.get("network_hashrate", 0.0),
            "whale_activity": context.get("whale_activity", "normal")
        }
    
    def _sense_alternative_data(self, context: dict[str, Any]) -> dict[str, Any]:
        """Simulate alternative data sensing."""
        return {
            "data_type": context.get("data_type", ""),
            "value": context.get("value", 0.0),
            "confidence": context.get("confidence", 0.0),
            "source": context.get("source", "")
        }
    
    def _combine_insights(self, sensor_data_list: list[SensorData]) -> list[dict[str, Any]]:
        """Combine insights from multiple sensors."""
        insights = []
        for sensor_data in sensor_data_list:
            insights.append({
                "sensor": sensor_data.sensor_name,
                "type": sensor_data.sensor_type,
                "key_data": sensor_data.data
            })
        return insights
    
    def _update_sensor_health(self, sensor_name: str, success: bool) -> None:
        """Update sensor health."""
        if sensor_name in self._sensors:
            sensor = self._sensors[sensor_name]
            if success:
                sensor.data_points_received += 1
                sensor.last_update = now().utc_time.isoformat()
                sensor.health_score = min(sensor.health_score + 0.01, 1.0)
            else:
                sensor.error_count += 1
                sensor.health_score = max(sensor.health_score - 0.05, 0.0)
    
    def get_sensors(self) -> dict[str, SensorHealth]:
        """Get all sensors."""
        return self._sensors.copy()
    
    def get_sensor_health(self, sensor_name: str) -> SensorHealth | None:
        """Get health of a specific sensor."""
        return self._sensors.get(sensor_name)
    
    def get_sensor_data(self) -> list[SensorData]:
        """Get all sensor data."""
        return self._sensor_data.copy()
    
    def get_status(self) -> dict[str, Any]:
        """Get sensory orchestrator status."""
        active_sensors = len([s for s in self._sensors.values() if s.is_active])
        
        return {
            "market_sensor_enabled": self._market_sensor_enabled,
            "news_sensor_enabled": self._news_sensor_enabled,
            "social_sensor_enabled": self._social_sensor_enabled,
            "macro_sensor_enabled": self._macro_sensor_enabled,
            "onchain_sensor_enabled": self._onchain_sensor_enabled,
            "alternative_sensor_enabled": self._alternative_sensor_enabled,
            "fusion_enabled": self._fusion_enabled,
            "total_sensors": len(self._sensors),
            "active_sensors": active_sensors,
            "total_sensor_data": len(self._sensor_data)
        }


# Global instance
_sensory_orchestrator: SensoryOrchestrator | None = None


def get_sensory_orchestrator() -> SensoryOrchestrator:
    """Get the global sensory orchestrator instance."""
    global _sensory_orchestrator
    if _sensory_orchestrator is None:
        _sensory_orchestrator = SensoryOrchestrator()
    return _sensory_orchestrator


__all__ = [
    "SensorData",
    "SensorHealth",
    "SensoryOrchestrator",
    "get_sensory_orchestrator",
]