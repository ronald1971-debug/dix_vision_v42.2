"""execution_unified.hazard — SYSTEM_HAZARD event pipeline.

Hazard detection and event management for the unified execution system.
"""

from .async_bus import (
    HazardBus,
    get_hazard_bus,
    HazardSeverity,
    HazardType,
)

from .detector import (
    HazardDetector,
    get_hazard_detector,
)

from .event_emitter import (
    HazardEmitter,
    get_hazard_emitter,
)

from .severity_classifier import (
    should_halt_trading,
    should_enter_safe_mode,
    classify_severity,
    classify_response,
)

__all__ = [
    "HazardBus",
    "get_hazard_bus",
    "HazardSeverity",
    "HazardType",
    "HazardDetector",
    "get_hazard_detector",
    "HazardEmitter",
    "get_hazard_emitter",
    "should_halt_trading",
    "should_enter_safe_mode",
    "classify_severity",
    "classify_response",
]