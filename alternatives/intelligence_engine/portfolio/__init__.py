"""Portfolio brain — intelligence-side capital allocator + exposure tracker.

This namespace was empty on ``main`` despite the spec calling for a
portfolio brain (allocator, exposure manager, correlation engine, risk
parity, capital scheduler). PR E ships the first two modules; the rest
land in follow-ups.
"""

from intelligence_engine.portfolio.allocator import (
    PortfolioAllocator,
    PortfolioAllocatorConfig,
    load_portfolio_allocator_config,
)
from intelligence_engine.portfolio.exposure_manager import ExposureManager
from intelligence_engine.portfolio.advanced_risk_management import (
    RiskMetric,
    VaRResult,
    CVaRResult,
    StressTestResult,
    RiskBudget,
    AdvancedRiskCalculator,
    DynamicRiskBudgeter,
)

__all__ = [
    "PortfolioAllocator",
    "PortfolioAllocatorConfig",
    "load_portfolio_allocator_config",
    "ExposureManager",
    "RiskMetric",
    "VaRResult",
    "CVaRResult",
    "StressTestResult",
    "RiskBudget",
    "AdvancedRiskCalculator",
    "DynamicRiskBudgeter",
]
