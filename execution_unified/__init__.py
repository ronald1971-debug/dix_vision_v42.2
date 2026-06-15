"""Unified Execution System - Single Execution Layer.

This is the consolidated execution system that replaces the fragmented
execution/ and execution_engine/ modules with a single, coherent execution
architecture as specified in the DIX VISION comprehensive integration plan.

Architecture:
- Core: Unified execution kernel and orchestration
- Strategic: Portfolio-level, macro decisions
- Tactical: Individual trade execution
- Adapters: Venue and protocol adapters
- Protections: Execution protection mechanisms
- Lanes: Execution lane management
- Audit: Execution auditing and monitoring

This provides the single execution layer called for in the comprehensive plan.
"""

# Core execution components
from .core.kernel import (
    UnifiedExecutionKernel,
    get_unified_execution_kernel,
    ExecutionRequest,
    ExecutionResult,
    ExecutionType,
    ExecutionLane,
    ExecutionStatus,
    Intent,
    Action,
)

# Production-grade autonomous trading
from .production_trading import (
    Order,
    Position,
    OrderType,
    OrderSide,
    OrderStatus,
    StrategyType,
    RiskParameters,
    ProductionRiskManager,
    ProductionStrategyExecutor,
    ProductionAutonomousTrader,
    get_production_trader,
)

__all__ = [
    # Core execution
    "UnifiedExecutionKernel",
    "get_unified_execution_kernel",
    "ExecutionRequest",
    "ExecutionResult",
    "ExecutionType",
    "ExecutionLane",
    "ExecutionStatus",
    "Intent",
    "Action",
    # Production trading
    "Order",
    "Position",
    "OrderType",
    "OrderSide",
    "OrderStatus",
    "StrategyType",
    "RiskParameters",
    "ProductionRiskManager",
    "ProductionStrategyExecutor",
    "ProductionAutonomousTrader",
    "get_production_trader",
]