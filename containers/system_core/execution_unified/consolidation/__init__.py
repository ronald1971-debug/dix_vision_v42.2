"""System Consolidation Module."""

from .legacy_system_analyzer import (
    LegacySystemType,
    LegacySystemAnalysis,
    ConsolidationPlan,
    LegacySystemAnalyzer,
    get_legacy_analyzer,
)

__all__ = [
    "LegacySystemType",
    "LegacySystemAnalysis",
    "ConsolidationPlan",
    "LegacySystemAnalyzer",
    "get_legacy_analyzer",
]