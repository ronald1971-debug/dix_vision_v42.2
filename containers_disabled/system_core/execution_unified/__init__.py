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

# CRITICAL: Import core.contracts using consolidated system_engine architecture
import sys

sys.path.insert(0, "..")
# Try to import from system_engine first (consolidated approach)
try:
    from system_engine import core as system_engine_core

    sys.modules["core"] = system_engine_core
    sys.modules["core.contracts"] = system_engine_core.contracts
except (ImportError, AttributeError):
    # Fallback to core directory if system_engine not available yet
    from core import contracts as fallback_contracts

    sys.modules["core"] = sys.modules["core"]  # Use existing core module
    sys.modules["core.contracts"] = fallback_contracts

# Production-ready archival submodules (organized by function)
from . import (
    adapters_archive,
    algos_archive,
    confirmations_archive,
    engine_archive,
    execution_archived_20260617_1258,
    hazard_archive,
    live_trading_archive,
    monitoring_archive,
)

# Unified adapters (migrated from legacy systems)
from .adapters.adapter_wrappers import (
    get_all_available_adapters,
    get_alpaca_adapter,
    get_binance_adapter,
    get_ibkr_adapter,
    get_kraken_adapter,
)

# Analysis components (from execution_engine/)
from .analysis import Fill
from .analysis import SlippageEstimate as AnalysisSlippageEstimate
from .analysis import TCAReport, analyze, estimate, min_acceptable_price, worst_acceptable_price

# Additional components for INDIRA/DYON decision making (from execution archives)
from .chaos_engine import ChaosEngine, FaultKind, FaultResult, FaultSpec

# Core events (unified event system)
from .core.events import (
    EventKind,
    ExecutionEvent,
    ExecutionStatus,
    Side,
    SignalEvent,
)

# Start with minimal imports and add back gradually
from .core.kernel import (
    Action,
    ExecutionLane,
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
    ExecutionType,
    Intent,
    UnifiedExecutionKernel,
    get_unified_execution_kernel,
)

# Emergency executor (migrated from execution/)
from .emergency_executor import (
    EmergencyExecutor,
    get_emergency_executor,
)

# Hazard components (migrated from execution/)
from .hazard import (
    HazardBus,
    HazardDetector,
    HazardEmitter,
    HazardSeverity,
    HazardType,
    classify_response,
    classify_severity,
    get_hazard_bus,
    get_hazard_detector,
    get_hazard_emitter,
    should_enter_safe_mode,
    should_halt_trading,
)

# Hot path features (migrated from execution_engine/)
from .hot_path import (
    FastExecution,
    FastExecutor,
    FastRiskCache,
    FastSignal,
    FastStructBackend,
    HotPathDecision,
    HotPathOutcome,
    RiskSnapshot,
    TimeAuthority,
)

# Intelligence features (migrated from execution_engine/)
from .intelligence import (
    LiquidityModel,
    LiquiditySnapshot,
    OrderSplitter,
    RouteDecision,
    SlippageEstimate,
    SlippagePredictor,
    SmartRouter,
    SplitPlan,
)

# Lifecycle features (migrated from execution_engine/)
from .lifecycle import (
    FillEvent,
    FillHandler,
    OrderRecord,
    OrderState,
    OrderStateMachine,
    PartialFillResolver,
    RetryPolicy,
    SLTPManager,
)

# Market data infrastructure (migrated from execution_engine/)
from .market_data import (
    BookBuilder,
    LatencySample,
    LatencyStats,
    LatencyTracker,
    NormalizedBook,
    NormalizedLevel,
    NormalizedTick,
    OrderBookAggregator,
    UnifiedOrderBook,
    UnifiedOrderBookSnapshot,
    orderbook_factory,
)

# Memecoin domain (from execution_engine/)
from .memecoin import DEXRouter, MemeRiskPolicy, MemeSniper, PaperBrokerMeme
from .mev_guard import GuardedSwap, prepare_swap, private_relay_for, validate_and_emit

# Offline trading (from execution_engine/)
from .offline import OfflineLane, OfflineLaneHandler, get_offline_lane
from .production_trading import (
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
    ProductionAutonomousTrader,
    ProductionRiskManager,
    ProductionStrategyExecutor,
    RiskParameters,
    StrategyType,
    get_production_trader,
)

# Semi-auto trading (from execution_engine/)
from .semi_auto import (
    ApprovalQueue,
    AutoExitDecision,
    ExitReason,
    ThresholdContext,
    ThresholdVerdict,
    evaluate_threshold,
    should_auto_exit,
)
from .system_repair_orchestrator import SystemRepairOrchestrator

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
    # Production-ready archival components (organized by function):
    "adapters_archive",
    "algos_archive",
    "confirmations_archive",
    "hazard_archive",
    "live_trading_archive",
    "monitoring_archive",
    "execution_archived_20260617_1258",
    "engine_archive",
    # All archival components available via submodules:
    # - execution_unified.adapters_archive (7 adapter components)
    # - execution_unified.algos_archive (algorithm components)
    # - execution_unified.confirmations_archive (confirmation tracking)
    # - execution_unified.hazard_archive (hazard detection)
    # - execution_unified.live_trading_archive (live trading components)
    # - execution_unified.monitoring_archive (monitoring components)
    # - execution_unified.engine_archive (138 execution engine components)
    # - Individual archived files (21 components)
    # Total: 184 archival components available via submodules
]
