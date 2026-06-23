"""
Mind Observation - Observation Module
Provides observation capabilities for cognitive operations
NO LAZY LOADING - All components load directly
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ObservationType(Enum):
    """Observation type enumeration"""

    MARKET_DATA = "market_data"
    EXECUTION_EVENT = "execution_event"
    SYSTEM_STATE = "system_state"
    EXTERNAL_SIGNAL = "external_signal"
    INTERNAL_EVENT = "internal_event"


@dataclass
class Observation:
    """Observation data structure"""

    observation_id: str
    data: Dict[str, Any]
    confidence: float
    source: str = ""
    observation_type: ObservationType = ObservationType.SYSTEM_STATE
    timestamp_ns: int = 0

    def __post_init__(self):
        if self.timestamp_ns == 0:
            self.timestamp_ns = int(
                __import__("datetime").datetime.now().timestamp() * 1_000_000_000
            )


class ObservationSystem:
    """Observation system for managing observations"""

    def __init__(self):
        self._observations: Dict[str, Observation] = {}

    def add_observation(self, observation: Observation):
        """Add observation to system"""
        self._observations[observation.observation_id] = observation

    def get_observation(self, observation_id: str) -> Optional[Observation]:
        """Get observation by ID"""
        return self._observations.get(observation_id)


__all__ = ["Observation", "ObservationSystem"]
