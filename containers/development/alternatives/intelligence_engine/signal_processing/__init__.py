"""Advanced signal processing for INDIRA intelligence.

This module provides enhanced signal processing capabilities including
filtering, noise reduction, signal quality assessment, and multi-signal fusion.
"""

from intelligence_engine.signal_processing.advanced_processor import (
    SignalQuality,
    FilterType,
    SignalMetrics,
    FilteredSignal,
    FusedSignal,
    AdvancedSignalProcessor,
)
from intelligence_engine.signal_processing.multi_modal_fusion import (
    MultiModalSignalFusion,
    CausalSignalFusion,
    SignalModality,
    FusionMethod,
    ModalitySignal,
    ModalityWeight,
    FusionResult,
    ModalityConflict,
    SignalPerformanceTracker,
)

__all__ = [
    "SignalQuality",
    "FilterType",
    "SignalMetrics",
    "FilteredSignal",
    "FusedSignal",
    "AdvancedSignalProcessor",
    "MultiModalSignalFusion",
    "CausalSignalFusion",
    "SignalModality",
    "FusionMethod",
    "ModalitySignal",
    "ModalityWeight",
    "FusionResult",
    "ModalityConflict",
    "SignalPerformanceTracker",
]
