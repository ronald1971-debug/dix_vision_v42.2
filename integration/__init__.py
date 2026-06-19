"""Integration Package

Provides system-level integration components including:
- World-indicator coordination (equal importance processing)
- System integration management
- Component wiring and data flow
"""

from .world_indicator_coordinator import (
    IntegrationMode,
    IntegratedMarketAnalysis,
    IntegrationPerformanceMetrics,
    WorldIndicatorCoordinator,
    get_world_indicator_coordinator,
)

__all__ = [
    "IntegrationMode",
    "IntegratedMarketAnalysis",
    "IntegrationPerformanceMetrics",
    "WorldIndicatorCoordinator",
    "get_world_indicator_coordinator",
]