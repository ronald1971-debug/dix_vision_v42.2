"""
governance_unified.domains.financial
Financial risk management and capital protection governance guards.

This module contains guards to ensure financial integrity, capital
protection, and risk management.
"""

from __future__ import annotations

# Core financial governance components
from .capital_throttle import CapitalThrottle, get_capital_throttle
from .execution_hazard import ExecutionHazardDetector, get_execution_hazard_detector
from .exposure_guard import ExposureGuard, get_exposure_guard

# Domain-specific financial governance components
from .financial_charter import FINANCIAL_GOVERNANCE_CHARTER
from .financial_engine import FinancialGovernanceEngine
from .kill_switch import KillSwitch, get_kill_switch
from .leverage_monitor import LeverageMonitor, get_leverage_monitor
from .liquidation_sentinel import LiquidationSentinel, get_liquidation_sentinel

__all__ = [
    # Core components
    "CapitalThrottle",
    "get_capital_throttle",
    "ExecutionHazardDetector",
    "get_execution_hazard_detector",
    "ExposureGuard",
    "get_exposure_guard",
    "KillSwitch",
    "get_kill_switch",
    "LeverageMonitor",
    "get_leverage_monitor",
    "LiquidationSentinel",
    "get_liquidation_sentinel",
    # Domain-specific financial governance components
    "FINANCIAL_GOVERNANCE_CHARTER",
    "FinancialGovernanceEngine",
]
