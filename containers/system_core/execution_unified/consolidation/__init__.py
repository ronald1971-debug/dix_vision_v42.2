"""System Consolidation Module."""

from .legacy_system_analyzer import (
    ConsolidationPlan,
    LegacySystemAnalysis,
    LegacySystemAnalyzer,
    LegacySystemType,
    get_legacy_analyzer,
)

__all__ = [
    "LegacySystemType",
    "LegacySystemAnalysis",
    "ConsolidationPlan",
    "LegacySystemAnalyzer",
    "get_legacy_analyzer",
]
