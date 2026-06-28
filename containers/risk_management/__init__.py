"""
DIXVISION Phase 12: Advanced Risk Management
Contract-Compliant Real Implementation

Advanced risk management system
"""

from .advanced_risk import (
    AdvancedRiskManager,
    ConcentrationLimitManager,
    CorrelationRiskManager,
    DynamicPositionSizer,
    MonteCarloRiskModel,
    RiskLimit,
    RiskLimitType,
    RiskMetric,
    RiskPosition,
    StressTestResult,
    StressTestScenario,
    get_advanced_risk_manager,
)

__all__ = [
    "RiskMetric",
    "StressTestScenario",
    "RiskLimitType",
    "RiskPosition",
    "RiskLimit",
    "StressTestResult",
    "MonteCarloRiskModel",
    "DynamicPositionSizer",
    "CorrelationRiskManager",
    "ConcentrationLimitManager",
    "AdvancedRiskManager",
    "get_advanced_risk_manager",
]
