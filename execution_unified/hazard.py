"""
Hazard Detection - Core Hazard Detection Infrastructure
Provides hazard detection capabilities
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

class HazardSeverity(Enum):
    """Hazard severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HazardType(Enum):
    """Hazard types"""
    MARKET = "market"
    SYSTEM = "system"
    OPERATOR = "operator"
    NETWORK = "network"
    DATA = "data"

@dataclass
class HazardEvent:
    """Hazard event data structure"""
    event_id: str
    hazard_type: HazardType
    severity: HazardSeverity
    description: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = __import__('datetime').datetime.now().timestamp_ns()

class HazardDetector:
    """Hazard detection system"""
    
    def __init__(self):
        self._active_hazards = []
        self._detection_rules = {}
        
    def detect_hazard(self, event_data: Dict[str, Any]) -> Optional[HazardEvent]:
        """Detect hazard from event data"""
        if event_data.get("severity") in ["high", "critical"]:
            return HazardEvent(
                event_id=f"hazard_{len(self._active_hazards)}",
                hazard_type=HazardType[event_data.get("type", "SYSTEM").upper()],
                severity=HazardSeverity[event_data.get("severity", "MEDIUM").upper()],
                description=event_data.get("description", "Unknown hazard"),
                source=event_data.get("source", "unknown")
            )
        return None
    
    def register_detection_rule(self, rule_id: str, rule_config: Dict[str, Any]):
        """Register hazard detection rule"""
        self._detection_rules[rule_id] = rule_config

# Global instance
_hazard_detector = None

def get_hazard_detector() -> HazardDetector:
    """Get hazard detector instance"""
    global _hazard_detector
    if _hazard_detector is None:
        _hazard_detector = HazardDetector()
    return _hazard_detector

def detect_hazard(event_data: Dict[str, Any]) -> Optional[HazardEvent]:
    """Detect hazard using global detector"""
    return get_hazard_detector().detect_hazard(event_data)

__all__ = [
    'HazardSeverity',
    'HazardType', 
    'HazardEvent',
    'HazardDetector',
    'get_hazard_detector',
    'detect_hazard'
]