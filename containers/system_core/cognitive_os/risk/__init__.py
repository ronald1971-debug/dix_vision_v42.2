"""Dynamic Risk Manager."""

from .dynamic_risk_manager import (
    DynamicRiskManager,
    get_risk_manager,
)

# Alias for consistency
get_dynamic_risk_manager = get_risk_manager

__all__ = [
    "DynamicRiskManager",
    "get_risk_manager",
    "get_dynamic_risk_manager",
]