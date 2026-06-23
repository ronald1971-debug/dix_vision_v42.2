"""
Phase 11.1 Dashboard Update - Integration Script

This script contains the exact code that needs to be added to ui/cockpit_routes.py
to integrate the Phase 11.1 API endpoints.

Usage:
1. Manually add the import statement at the top of ui/cockpit_routes.py
2. Manually add the function call before return router
3. Or use this script as reference for manual integration
"""

# 1. ADD THIS IMPORT AFTER LINE 52 (after the system_monitor imports)
# Add this line:
# from ui.cockpit_routes_phase11_1 import add_phase_11_1_endpoints

# 2. ADD THIS FUNCTION CALL BEFORE LINE 1126 (before return router)
# Add this line:
# add_phase_11_1_endpoints(router)

# 3. ADD THESE PYDANTIC MODELS TO THE EXISTING MODELS SECTION (after line 112)
# Add these models to the existing Pydantic models section:


class OrderSubmitIn(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: str
    price: float | None = None
    time_in_force: str = "GTC"
    operator_id: str = "operator"
    reason: str = ""


class OrderCancelIn(BaseModel):
    order_id: str
    operator_id: str = "operator"
    reason: str = ""


class OrderCancelAllIn(BaseModel):
    symbol: str | None = None
    operator_id: str = "operator"
    reason: str = ""


class StrategyActionIn(BaseModel):
    strategy_id: str
    operator_id: str = "operator"
    reason: str = ""


class PositionCloseIn(BaseModel):
    position_id: str
    operator_id: str = "operator"
    reason: str = ""


class LedgerReplayIn(BaseModel):
    from_sequence: int
    to_sequence: int | None = None
    stream: str = ""


# 4. ADD THESE EXPORTS TO __all__ SECTION (after line 1142)
# Add these to the __all__ list:
# "OrderSubmitIn",
# "OrderCancelIn",
# "OrderCancelAllIn",
# "StrategyActionIn",
# "PositionCloseIn",
# "LedgerReplayIn",
