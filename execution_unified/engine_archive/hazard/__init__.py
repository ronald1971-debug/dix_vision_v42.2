"""execution_engine.hazard — SYSTEM_HAZARD event pipeline.

Migrated from execution/hazard/

This package provides hazard detection and event processing for the execution engine.
"""

from execution_unified.core.hazard.async_bus import (
    HazardEvent,
    HazardSeverity,
    HazardType,
    get_hazard_bus,
)
from execution_unified.core.hazard.detector import get_hazard_detector
from execution_unified.core.hazard.event_emitter import get_hazard_emitter
from execution_unified.core.hazard.severity_classifier import (
    classify_response,
    should_enter_safe_mode,
    should_halt_trading,
)

__all__ = [
    "HazardEvent",
    "HazardSeverity",
    "HazardType",
    "get_hazard_bus",
    "get_hazard_detector",
    "get_hazard_emitter",
    "classify_response",
    "should_enter_safe_mode",
    "should_halt_trading",
]
