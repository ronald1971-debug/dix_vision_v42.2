"""
Execution Unified Hazard - Hazard Detection and Management
Provides hazard detection, classification, and management capabilities
NO LAZY LOADING - All components load directly
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class HazardSeverity(Enum):
    """Hazard severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HazardType(Enum):
    """Hazard type classification"""
    MARKET = "market"
    SYSTEM = "system"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    SECURITY = "security"

@dataclass
class HazardEvent:
    """Hazard event data structure"""
    hazard_id: str
    hazard_type: HazardType
    severity: HazardSeverity
    description: str
    source: str
    timestamp_ns: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    
    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = datetime.now().timestamp_ns()
    
    def resolve(self):
        """Mark hazard as resolved"""
        self.resolved = True
    
    def is_resolved(self) -> bool:
        """Check if hazard is resolved"""
        return self.resolved

class HazardDetector:
    """Hazard detector for identifying potential hazards"""
    
    def __init__(self):
        self._detected_hazards: Dict[str, HazardEvent] = {}
        self._active = True
        
    def detect_hazard(self, hazard_type: HazardType, severity: HazardSeverity, 
                     description: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> HazardEvent:
        """Detect and register a hazard"""
        hazard_id = f"hazard_{datetime.now().timestamp_ns()}"
        
        hazard = HazardEvent(
            hazard_id=hazard_id,
            hazard_type=hazard_type,
            severity=severity,
            description=description,
            source=source,
            metadata=metadata or {}
        )
        
        self._detected_hazards[hazard_id] = hazard
        return hazard
    
    def get_hazard(self, hazard_id: str) -> Optional[HazardEvent]:
        """Get hazard by ID"""
        return self._detected_hazards.get(hazard_id)
    
    def get_active_hazards(self) -> List[HazardEvent]:
        """Get all active (unresolved) hazards"""
        return [h for h in self._detected_hazards.values() if not h.resolved]
    
    def resolve_hazard(self, hazard_id: str) -> bool:
        """Resolve a hazard"""
        hazard = self._detected_hazards.get(hazard_id)
        if hazard:
            hazard.resolve()
            return True
        return False

# Global instance
_hazard_detector = None

def get_hazard_detector() -> HazardDetector:
    """Get global hazard detector instance"""
    global _hazard_detector
    if _hazard_detector is None:
        _hazard_detector = HazardDetector()
    return _hazard_detector

def detect_hazard(hazard_type: HazardType, severity: HazardSeverity, 
                 description: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> HazardEvent:
    """Detect hazard (convenience function)"""
    detector = get_hazard_detector()
    return detector.detect_hazard(hazard_type, severity, description, source, metadata)

__all__ = [
    'HazardSeverity',
    'HazardType',
    'HazardEvent',
    'HazardDetector',
    'get_hazard_detector',
    'detect_hazard'
]