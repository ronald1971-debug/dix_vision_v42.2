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

# Start with minimal imports and add back gradually
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

# Unified adapters (migrated from legacy systems)
from .adapters.adapter_wrappers import (
    get_binance_adapter,
    get_kraken_adapter,
    get_alpaca_adapter,
    get_ibkr_adapter,
    get_all_available_adapters,
)

# Intelligence features (migrated from execution_engine/)
from .intelligence import (
    LiquidityModel,
    LiquiditySnapshot,
    SmartRouter,
    RouteDecision,
    OrderSplitter,
    SplitPlan,
    SlippagePredictor,
    SlippageEstimate,
)

# Core events (unified event system)
from .core.events import (
    Side,
    ExecutionStatus,
    SignalEvent,
    ExecutionEvent,
    EventKind,
)

# Market data infrastructure (migrated from execution_engine/)
from .market_data import (
    OrderBookAggregator,
    BookBuilder,
    UnifiedOrderBook,
    UnifiedOrderBookSnapshot,
    NormalizedBook,
    NormalizedLevel,
    NormalizedTick,
    LatencyTracker,
    LatencyStats,
    LatencySample,
    orderbook_factory,
)

# Hot path features (migrated from execution_engine/)
from .hot_path import (
    FastExecutor,
    HotPathDecision,
    HotPathOutcome,
    RiskSnapshot,
    FastRiskCache,
    FastStructBackend,
    FastSignal,
    FastExecution,
    TimeAuthority,
)

# Lifecycle features (migrated from execution_engine/)
from .lifecycle import (
    OrderStateMachine,
    FillHandler,
    FillEvent,
    SLTPManager,
    OrderState,
    OrderRecord,
    PartialFillResolver,
    RetryPolicy,
)

# Hazard components (migrated from execution/)
from .hazard import (
    HazardBus,
    get_hazard_bus,
    HazardSeverity,
    HazardType,
    HazardDetector,
    get_hazard_detector,
    HazardEmitter,
    get_hazard_emitter,
    should_halt_trading,
    should_enter_safe_mode,
    classify_severity,
    classify_response,
)

# Emergency executor (migrated from execution/)
from .emergency_executor import (
    EmergencyExecutor,
    get_emergency_executor,
)

# Additional components for INDIRA/DYON decision making (from execution archives)
from .chaos_engine import ChaosEngine, FaultKind, FaultSpec, FaultResult
from .mev_guard import GuardedSwap, private_relay_for, prepare_swap, validate_and_emit
from .system_repair_orchestrator import SystemRepairOrchestrator

# Analysis components (from execution_engine/)
from .analysis import SlippageEstimate as AnalysisSlippageEstimate, estimate, worst_acceptable_price, min_acceptable_price, Fill, TCAReport, analyze

# Memecoin domain (from execution_engine/)
from .memecoin import DEXRouter, MemeRiskPolicy, PaperBrokerMeme, MemeSniper

# Offline trading (from execution_engine/)
from .offline import OfflineLane, OfflineLaneHandler, get_offline_lane

# Semi-auto trading (from execution_engine/)
from .semi_auto import ApprovalQueue, ExitReason, AutoExitDecision, should_auto_exit, ThresholdVerdict, ThresholdContext, evaluate_threshold

# Testing infrastructure (from execution_engine/)
from .testing import ChaosEngine as TestingChaosEngine

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
    # Unified adapters
    "get_binance_adapter",
    "get_kraken_adapter",
    "get_alpaca_adapter",
    "get_ibkr_adapter",
    "get_all_available_adapters",
    # Intelligence features
    "LiquidityModel",
    "LiquiditySnapshot",
    "SmartRouter",
    "RouteDecision",
    "OrderSplitter",
    "SplitPlan",
    "SlippagePredictor",
    "SlippageEstimate",
    # Core events
    "Side",
    "ExecutionStatus",
    "SignalEvent",
    "ExecutionEvent",
    "EventKind",
    # Market data infrastructure
    "OrderBookAggregator",
    "BookBuilder",
    "UnifiedOrderBook",
    "UnifiedOrderBookSnapshot",
    "NormalizedBook",
    "NormalizedLevel",
    "NormalizedTick",
    "LatencyTracker",
    "LatencyStats",
    "LatencySample",
    "orderbook_factory",
    # Hot path features
    "FastExecutor",
    "HotPathDecision",
    "HotPathOutcome",
    "RiskSnapshot",
    "FastRiskCache",
    "FastStructBackend",
    "FastSignal",
    "FastExecution",
    "TimeAuthority",
    # Lifecycle features
    "OrderStateMachine",
    "FillHandler",
    "FillEvent",
    "SLTPManager",
    "OrderState",
    "OrderRecord",
    "PartialFillResolver",
    "RetryPolicy",
    # Hazard components
    "HazardBus",
    "get_hazard_bus",
    "HazardSeverity",
    "HazardType",
    "HazardDetector",
    "get_hazard_detector",
    "HazardEmitter",
    "get_hazard_emitter",
    "should_halt_trading",
    "should_enter_safe_mode",
    "classify_severity",
    "classify_response",
    # Emergency executor
    "EmergencyExecutor",
    "get_emergency_executor",
    # Additional components for INDIRA/DYON decision making
    "ChaosEngine",
    "FaultKind",
    "FaultSpec",
    "FaultResult",
    "GuardedSwap",
    "private_relay_for",
    "prepare_swap",
    "validate_and_emit",
    "SystemRepairOrchestrator",
    # Analysis components
    "AnalysisSlippageEstimate",
    "estimate",
    "worst_acceptable_price",
    "min_acceptable_price",
    "Fill",
    "TCAReport",
    "analyze",
    # Memecoin domain
    "DEXRouter",
    "MemeRiskPolicy",
    "PaperBrokerMeme",
    "MemeSniper",
    # Offline trading
    "OfflineLane",
    "OfflineLaneHandler",
    "get_offline_lane",
    # Semi-auto trading
    "ApprovalQueue",
    "ExitReason",
    "AutoExitDecision",
    "should_auto_exit",
    "ThresholdVerdict",
    "ThresholdContext",
    "evaluate_threshold",
    # Testing infrastructure
    "TestingChaosEngine",
]