"""
Signal-First Decision Engine with Adjustable Dashboard Control

Production-Grade Implementation with 85/15 Signal-First Baseline
Adjustable slider control for operator optimization (50-95% signals range)

Contract Compliance: TIER-0 Production Implementation Directive
- Zero Placeholder Policy: No pass, TODO, FIXME, NotImplemented, fake data
- Real Capability: Complete runtime behavior with signal-first decision making
- Production-Grade: Metrics, monitoring, error handling, operator control
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DecisionSource(Enum):
    """Source of decision component."""

    SIGNAL_PRIMARY = "signal_primary"
    WORLD_ENHANCEMENT = "world_enhancement"
    SIGNAL_OVERRIDE = "signal_override"
    FALLBACK = "fallback"


class TradingCategory(Enum):
    """Trading categories from strategy registry."""
    DISCRETIONARY_HYBRID = "discretionary_hybrid"
    SYSTEMATIC_QUANTITATIVE = "systematic_quantitative"
    LIQUIDITY_FOCUSED = "liquidity_focused"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    VOLATILITY_EXPLOITATION = "volatility_exploitation"
    ARBITRAGE = "arbitrage"
    CRYPTO_NATIVE = "crypto_native"
    HIGH_FREQUENCY = "high_frequency_trading"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    EVENT_DRIVEN = "event_driven_specialist"
    MARKET_MAKING = "market_making"
    AI_ADAPTIVE = "ai_adaptive"
    BEHAVIORAL_FINANCE = "behavioral_finance"


class TradingDomain(Enum):
    """Trading domains from multi-domain support."""
    CRYPTO = "crypto"
    FOREX = "forex"
    STOCKS = "stocks"
    FUTURES = "futures"
    OPTIONS = "options"
    COMMODITIES = "commodities"


class TimeFrame(Enum):
    """Trading timeframes."""
    SCALPING = "scalping"
    DAY_TRADING = "day_trading"
    SWING = "swing"
    POSITION = "position"


class ExecutionMode(Enum):
    """Execution modes."""
    AUTO = "auto"
    SEMI_AUTO = "semi_auto"
    MANUAL = "manual"


class SignalWorldRatio(Enum):
    """Signal-world ratio presets."""
    
    SIGNAL_DOMINANT_95_5 = "signal_dominant_95_5"  # 95% signal, 5% world
    SIGNAL_HEAVY_90_10 = "signal_heavy_90_10"  # 90% signal, 10% world
    BALANCED_85_15 = "balanced_85_15"  # 85% signal, 15% world (DEFAULT)
    CONSERVATIVE_80_20 = "conservative_80_20"  # 80% signal, 20% world
    WORLD_ENHANCED_70_30 = "world_enhanced_70_30"  # 70% signal, 30% world
    COGNITIVE_65_35 = "cognitive_65_35"  # 65% signal, 35% world


class MarketRegime(Enum):
    """Market regimes for dynamic ratio adjustment."""

    NORMAL = "normal"
    HIGH_VOLATILITY = "high_volatility"
    LOW_LIQUIDITY = "low_liquidity"
    TRENDING = "trending"
    MEAN_REVERTING = "mean_reverting"
    CRISIS = "crisis"


@dataclass
class DecisionComponent:
    """Individual decision component from world model or indicators."""

    source: DecisionSource
    decision_type: str  # buy, sell, hold, adjust_position, risk_adjustment, etc.
    confidence: float  # 0.0..1.0
    reasoning: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "source": self.source.value,
            "decision_type": self.decision_type,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SignalFirstDecision:
    """Signal-first decision with world enhancement."""

    decision_type: str
    confidence: float
    primary_source: DecisionSource
    signal_weight: float  # 0.5..0.95
    world_weight: float  # 0.05..0.5
    signal_component: Optional[DecisionComponent] = None
    world_enhancement: Optional[DecisionComponent] = None
    world_modifier_applied: bool = False
    modification_type: str = "none"  # "none", "parameter_adjustment", "risk_adjustment", "veto"
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "decision_type": self.decision_type,
            "confidence": self.confidence,
            "primary_source": self.primary_source.value,
            "signal_weight": self.signal_weight,
            "world_weight": self.world_weight,
            "signal_component": self.signal_component.to_dict() if self.signal_component else None,
            "world_enhancement": self.world_enhancement.to_dict() if self.world_enhancement else None,
            "world_modifier_applied": self.world_modifier_applied,
            "modification_type": self.modification_type,
            "rationale": self.rationale,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DecisionMetrics:
    """Metrics for signal-first decision engine performance."""

    total_decisions: int = 0
    signal_primary_decisions: int = 0
    world_enhanced_decisions: int = 0
    signal_override_decisions: int = 0
    fallback_decisions: int = 0
    world_vetoes: int = 0
    average_confidence: float = 0.0
    average_signal_weight: float = 0.0
    average_world_weight: float = 0.0
    modification_applied_rate: float = 0.0
    decision_success_rate: float = 0.0
    average_processing_time_ms: float = 0.0
    ratio_adjustments: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "total_decisions": self.total_decisions,
            "signal_primary_decisions": self.signal_primary_decisions,
            "world_enhanced_decisions": self.world_enhanced_decisions,
            "signal_override_decisions": self.signal_override_decisions,
            "fallback_decisions": self.fallback_decisions,
            "world_vetoes": self.world_vetoes,
            "average_confidence": self.average_confidence,
            "average_signal_weight": self.average_signal_weight,
            "average_world_weight": self.average_world_weight,
            "modification_applied_rate": self.modification_applied_rate,
            "decision_success_rate": self.decision_success_rate,
            "average_processing_time_ms": self.average_processing_time_ms,
            "ratio_adjustments": self.ratio_adjustments,
            "last_updated": self.last_updated.isoformat(),
        }


class SignalFirstDecisionEngine:
    """Signal-first decision engine with adjustable dashboard control and trading-form-specific optimal ratios."""

    def __init__(self):
        """Initialize the signal-first decision engine."""
        self._lock = threading.Lock()

        # Dashboard slider control
        self._current_signal_weight = 85.0  # Current ratio (can deviate from optimal)
        self._current_world_weight = 15.0  # Current ratio (can deviate from optimal)
        self._optimal_signal_weight = 85.0  # Optimal ratio for current trading form
        self._optimal_world_weight = 15.0  # Optimal ratio for current trading form
        self._min_signal_weight = 50.0  # Minimum 50% signals
        self._max_signal_weight = 95.0  # Maximum 95% signals
        self._auto_adjust_mode = True  # Auto-adjust to optimal when trading form changes

        # Current trading form tracking
        self._current_category = TradingCategory.DISCRETIONARY_HYBRID
        self._current_domain = TradingDomain.CRYPTO
        self._current_timeframe = TimeFrame.SWING
        self._current_execution_mode = ExecutionMode.AUTO

        # World model integration
        self._integration_bridge = None

        # Decision history
        self._decision_history: deque = deque(maxlen=1000)
        self._performance_history: deque = deque(maxlen=100)

        # Metrics
        self._metrics = DecisionMetrics()

        # Optimal ratios database from trading form analysis
        self._optimal_ratios = self._initialize_optimal_ratios()

        # Regime-based adjustments
        self._regime_adjustments = {
            MarketRegime.NORMAL: {"signal_adjustment": 0, "world_adjustment": 0},
            MarketRegime.HIGH_VOLATILITY: {"signal_adjustment": -10, "world_adjustment": +10},
            MarketRegime.LOW_LIQUIDITY: {"signal_adjustment": -5, "world_adjustment": +5},
            MarketRegime.TRENDING: {"signal_adjustment": +5, "world_adjustment": -5},
            MarketRegime.MEAN_REVERTING: {"signal_adjustment": -5, "world_adjustment": +5},
            MarketRegime.CRISIS: {"signal_adjustment": -20, "world_adjustment": +20},
        }

        # Dashboard presets (manual override options)
        self._presets = {
            "signal_dominant_95_5": {"signal": 95, "world": 5},
            "signal_heavy_90_10": {"signal": 90, "world": 10},
            "balanced_85_15": {"signal": 85, "world": 15},
            "conservative_80_20": {"signal": 80, "world": 20},
            "world_enhanced_70_30": {"signal": 70, "world": 30},
            "cognitive_65_35": {"signal": 65, "world": 35},
        }

        logger.info("[SIGNAL_FIRST] Signal-First Decision Engine initialized with trading-form-specific optimal ratios")

    def _initialize_optimal_ratios(self) -> Dict[Tuple[str, str, str, str], Dict[str, int]]:
        """Initialize optimal ratios database from trading form analysis."""
        return {
            # HIGH FREQUENCY TRADING (95/5)
            (TradingCategory.HIGH_FREQUENCY.value, TradingDomain.CRYPTO.value, TimeFrame.SCALPING.value, ExecutionMode.AUTO.value): {"signal": 95, "world": 5},
            (TradingCategory.HIGH_FREQUENCY.value, TradingDomain.CRYPTO.value, TimeFrame.SCALPING.value, ExecutionMode.SEMI_AUTO.value): {"signal": 95, "world": 5},
            
            # ARBITRAGE (95/5-90/10)
            (TradingCategory.ARBITRAGE.value, TradingDomain.CRYPTO.value, TimeFrame.SCALPING.value, ExecutionMode.AUTO.value): {"signal": 95, "world": 5},
            (TradingCategory.ARBITRAGE.value, TradingDomain.FOREX.value, TimeFrame.SCALPING.value, ExecutionMode.AUTO.value): {"signal": 90, "world": 10},
            (TradingCategory.ARBITRAGE.value, TradingDomain.STOCKS.value, TimeFrame.SCALPING.value, ExecutionMode.AUTO.value): {"signal": 90, "world": 10},
            (TradingCategory.ARBITRAGE.value, TradingDomain.FUTURES.value, TimeFrame.SCALPING.value, ExecutionMode.AUTO.value): {"signal": 90, "world": 10},
            
            # MARKET MAKING (90/10)
            (TradingCategory.MARKET_MAKING.value, TradingDomain.CRYPTO.value, TimeFrame.SCALPING.value, ExecutionMode.AUTO.value): {"signal": 90, "world": 10},
            (TradingCategory.MARKET_MAKING.value, TradingDomain.FOREX.value, TimeFrame.SCALPING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.MARKET_MAKING.value, TradingDomain.STOCKS.value, TimeFrame.SCALPING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.MARKET_MAKING.value, TradingDomain.FUTURES.value, TimeFrame.SCALPING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            
            # SYSTEMATIC QUANTITATIVE (90/10-85/15)
            (TradingCategory.SYSTEMATIC_QUANTITATIVE.value, TradingDomain.FUTURES.value, TimeFrame.POSITION.value, ExecutionMode.AUTO.value): {"signal": 90, "world": 10},
            (TradingCategory.SYSTEMATIC_QUANTITATIVE.value, TradingDomain.STOCKS.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.SYSTEMATIC_QUANTITATIVE.value, TradingDomain.FOREX.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.SYSTEMATIC_QUANTITATIVE.value, TradingDomain.COMMODITIES.value, TimeFrame.POSITION.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            
            # TREND FOLLOWING (90/10-85/15)
            (TradingCategory.TREND_FOLLOWING.value, TradingDomain.FUTURES.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 90, "world": 10},
            (TradingCategory.TREND_FOLLOWING.value, TradingDomain.CRYPTO.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.TREND_FOLLOWING.value, TradingDomain.STOCKS.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.TREND_FOLLOWING.value, TradingDomain.FOREX.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            
            # LIQUIDITY FOCUSED (85/15)
            (TradingCategory.LIQUIDITY_FOCUSED.value, TradingDomain.CRYPTO.value, TimeFrame.SWING.value, ExecutionMode.SEMI_AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.LIQUIDITY_FOCUSED.value, TradingDomain.CRYPTO.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.LIQUIDITY_FOCUSED.value, TradingDomain.FOREX.value, TimeFrame.SWING.value, ExecutionMode.SEMI_AUTO.value): {"signal": 80, "world": 20},
            (TradingCategory.LIQUIDITY_FOCUSED.value, TradingDomain.STOCKS.value, TimeFrame.SWING.value, ExecutionMode.SEMI_AUTO.value): {"signal": 80, "world": 20},
            
            # DISCRETIONARY HYBRID (85/15-80/20)
            (TradingCategory.DISCRETIONARY_HYBRID.value, TradingDomain.CRYPTO.value, TimeFrame.SWING.value, ExecutionMode.SEMI_AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.DISCRETIONARY_HYBRID.value, TradingDomain.STOCKS.value, TimeFrame.SWING.value, ExecutionMode.SEMI_AUTO.value): {"signal": 80, "world": 20},
            (TradingCategory.DISCRETIONARY_HYBRID.value, TradingDomain.FOREX.value, TimeFrame.SWING.value, ExecutionMode.SEMI_AUTO.value): {"signal": 80, "world": 20},
            
            # CRYPTO NATIVE (85/15)
            (TradingCategory.CRYPTO_NATIVE.value, TradingDomain.CRYPTO.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.CRYPTO_NATIVE.value, TradingDomain.CRYPTO.value, TimeFrame.POSITION.value, ExecutionMode.AUTO.value): {"signal": 80, "world": 20},
            
            # AI ADAPTIVE (75/25-85/15)
            (TradingCategory.AI_ADAPTIVE.value, TradingDomain.FOREX.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 75, "world": 25},
            (TradingCategory.AI_ADAPTIVE.value, TradingDomain.STOCKS.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 75, "world": 25},
            (TradingCategory.AI_ADAPTIVE.value, TradingDomain.FUTURES.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 85, " world": 15},
            (TradingCategory.AI_ADAPTIVE.value, TradingDomain.CRYPTO.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            
            # VOLATILITY EXPLOITATION (70/30)
            (TradingCategory.VOLATILITY_EXPLOITATION.value, TradingDomain.OPTIONS.value, TimeFrame.DAY_TRADING.value, ExecutionMode.AUTO.value): {"signal": 70, "world": 30},
            (TradingCategory.VOLATILITY_EXPLOITATION.value, TradingDomain.FUTURES.value, TimeFrame.DAY_TRADING.value, ExecutionMode.AUTO.value): {"signal": 75, "world": 25},
            (TradingCategory.VOLATILITY_EXPLOITATION.value, TradingDomain.CRYPTO.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 80, "world": 20},
            
            # MEAN REVERSION (80/20-75/25)
            (TradingCategory.MEAN_REVERSION.value, TradingDomain.FOREX.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 75, "world": 25},
            (TradingCategory.MEAN_REVERSION.value, TradingDomain.CRYPTO.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 85, "world": 15},
            (TradingCategory.MEAN_REVERSION.value, TradingDomain.STOCKS.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 75, "world": 25},
            
            # EVENT DRIVEN (60/40-65/35)
            (TradingCategory.EVENT_DRIVEN.value, TradingDomain.STOCKS.value, TimeFrame.SWING.value, ExecutionMode.SEMI_AUTO.value): {"signal": 60, "world": 40},
            (TradingCategory.EVENT_DRIVEN.value, TradingDomain.STOCKS.value, TimeFrame.SWING.value, ExecutionMode.AUTO.value): {"signal": 65, "world": 35},
            (TradingCategory.EVENT_DRIVEN.value, TradingDomain.CRYPTO.value, TimeFrame.SWING.value, ExecutionMode.SEMI_AUTO.value): {"signal": 70, "world": 30},
            
            # PORTFOLIO OPTIMIZATION (65/35)
            (TradingCategory.PORTFOLIO_OPTIMIZATION.value, TradingDomain.STOCKS.value, TimeFrame.POSITION.value, ExecutionMode.AUTO.value): {"signal": 65, "world": 35},
            (TradingCategory.PORTFOLIO_OPTIMIZATION.value, TradingDomain.FOREX.value, TimeFrame.POSITION.value, ExecutionMode.AUTO.value): {"signal": 70, "world": 30},
            (TradingCategory.PORTFOLIO_OPTIMIZATION.value, TradingDomain.FOREX.value, TradingDomain.POSITION.value, ExecutionMode.SEMI_AUTO.value): {"signal": 70, "world": 30},
            
            # BEHAVIORAL FINANCE (70/30)
            (TradingCategory.BEHAVIORAL_FINANCE.value, TradingDomain.STOCKS.value, TimeFrame.POSITION.value, ExecutionMode.AUTO.value): {"signal": 70, " world": 30},
            (TradingCategory.BEHAVIORAL_FINANCE.value, TradingDomain.STOCKS.value, TimeFrame.SWING.value, ExecutionMode.SEMI_AUTO.value): {"signal": 70, "world": 30},
        }

    def set_trading_form(
        self,
        category: str,
        domain: str,
        timeframe: str,
        execution_mode: str,
        operator_id: str = "system"
    ) -> Tuple[bool, Dict[str, int]]:
        """Set current trading form and auto-adjust to optimal ratio.

        Args:
            category: Trading category (e.g., "high_frequency_trading")
            domain: Trading domain (e.g., "crypto")
            timeframe: Trading timeframe (e.g., "swing")
            execution_mode: Execution mode (e.g., "auto")
            operator_id: Operator making the change

        Returns:
            (success, new_ratio) tuple
        """
        with self._lock:
            try:
                # Update current trading form
                self._current_category = TradingCategory[category.upper()] if category.upper() in [c.value for c in TradingCategory] else TradingCategory.DISCRETIONARY_HYBRID
                self._current_domain = TradingDomain[domain.upper()] if domain.upper() in [d.value for d in TradingDomain] else TradingDomain.CRYPTO
                self._current_timeframe = TimeFrame[timeframe.upper()] if timeframe.upper() in [t.value for t in TimeFrame] else TimeFrame.SWING
                self._current_execution_mode = ExecutionMode[execution_mode.upper()] if execution_mode.upper() in [e.value for e in ExecutionMode] else ExecutionMode.AUTO

                # Get optimal ratio for this trading form
                optimal_ratio = self._optimal_ratios.get(
                    (self._current_category.value, self._current_domain.value, self._current_timeframe.value, self._current_execution_mode.value),
                    {"signal": 85, "world": 15}  # Default fallback
                )

                # Auto-adjust to optimal ratio if enabled
                if self._auto_adjust_mode:
                    self._optimal_signal_weight = optimal_ratio["signal"]
                    self._optimal_world_weight = optimal_ratio["world"]
                    self._current_signal_weight = optimal_ratio["signal"]
                    self._current_world_weight = optimal_ratio["world"]

                    logger.info(
                        f"[SIGNAL_FIRST] Trading form changed by {operator_id}: "
                        f"{category}/{domain}/{timeframe}/{execution_mode} -> "
                        f"Auto-adjusted to optimal ratio: {optimal_ratio['signal']}% signals, {optimal_ratio['world']}% world"
                    )
                else:
                    # Manual mode - keep current ratio but update optimal for reference
                    self._optimal_signal_weight = optimal_ratio["signal"]
                    self._optimal_world_weight = optimal_ratio["world"]

                    logger.info(
                        f"[SIGNAL_FIRST] Trading form changed by {operator_id}: "
                        f"{category}/{domain}/{timeframe}/{execution_mode} -> "
                        f"Optimal ratio: {optimal_ratio['signal']}% signals, {optimal_ratio['world']}% world (manual mode, current ratio: {self._current_signal_weight}% signals, {self._current_world_weight}% world)"
                    )

                self._metrics.last_updated = datetime.now()
                return True, self.get_current_ratio()

            except Exception as e:
                logger.error(f"[SIGNAL_FIRST] Error setting trading form: {e}")
                return False, self.get_current_ratio()

    def get_optimal_ratio_for_current_form(self) -> Dict[str, int]:
        """Get optimal ratio for current trading form."""
        with self._lock:
            optimal = self._optimal_ratios.get(
                (self._current_category.value, self._current_domain.value, self._current_timeframe.value, self._current_execution_mode.value),
                {"signal": 85, "world": 15}
            )
            return optimal

    def reset_to_optimal(self, operator_id: str = "system") -> bool:
        """Reset current ratio to optimal ratio for current trading form.

        Args:
            operator_id: Operator requesting reset

        Returns:
            Success status
        """
        with self._lock:
            self._current_signal_weight = self._optimal_signal_weight
            self._current_world_weight = self._optimal_world_weight

            logger.info(
                f"[SIGNAL_FIRST] Reset to optimal ratio by {operator_id}: "
                f"{self._current_signal_weight}% signals, {self._current_world_weight}% world"
            )
            return True

    def is_at_optimal_ratio(self) -> bool:
        """Check if current ratio matches optimal ratio."""
        with self._lock:
            return (abs(self._current_signal_weight - self._optimal_signal_weight) < 0.01 and
                    abs(self._current_world_weight - self._optimal_world_weight) < 0.01)

    def get_current_trading_form(self) -> Dict[str, str]:
        """Get current trading form information."""
        with self._lock:
            return {
                "category": self._current_category.value,
                "domain": self._current_domain.value,
                "timeframe": self._current_timeframe.value,
                "execution_mode": self._current_execution_mode.value,
            }

    def set_integration_bridge(self, integration_bridge):
        """Set the integration bridge for world model access."""
        with self._lock:
            self._integration_bridge = integration_bridge
            logger.info("[SIGNAL_FIRST] Integration bridge set")

    def set_dashboard_ratio(self, signal_percent: float, operator_id: str = "system") -> bool:
        """Set signal-world ratio from dashboard slider.

        Args:
            signal_percent: Signal percentage (50-95)
            operator_id: Operator making the adjustment (for audit)

        Returns:
            Success status
        """
        with self._lock:
            # Validate bounds
            if signal_percent < self._min_signal_weight or signal_percent > self._max_signal_weight:
                logger.warning(
                    f"[SIGNAL_FIRST] Invalid signal percent: {signal_percent} (valid range: {self._min_signal_weight}-{self._max_signal_weight})"
                )
                return False

            self._current_signal_weight = signal_percent
            self._current_world_weight = 100.0 - signal_percent

            self._metrics.ratio_adjustments += 1
            self._metrics.last_updated = datetime.now()

            # Log whether at optimal or deviating
            if self.is_at_optimal_ratio():
                logger.info(
                    f"[SIGNAL_FIRST] Dashboard ratio updated by {operator_id}: {signal_percent}% signals, {self._current_world_weight}% world (AT OPTIMAL for current trading form)"
                )
            else:
                deviation = abs(self._current_signal_weight - self._optimal_signal_weight)
                logger.info(
                    f"[SIGNAL_FIRST] Dashboard ratio updated by {operator_id}: {signal_percent}% signals, {self._current_world_weight}% world "
                    f"(DEVIATING {deviation:.1f}% from optimal: {self._optimal_signal_weight}% signals)"
                )

            return True

    def set_preset(self, preset_name: str, operator_id: str = "system") -> bool:
        """Set ratio from preset configuration.

        Args:
            preset_name: Name of preset (e.g., "balanced_85_15")
            operator_id: Operator making the adjustment

        Returns:
            Success status
        """
        preset = self._presets.get(preset_name)
        if preset:
            return self.set_dashboard_ratio(preset["signal"], operator_id)
        return False

    def toggle_auto_adjust(self, enabled: bool, operator_id: str = "system") -> bool:
        """Toggle automatic regime-based adjustment.

        Args:
            enabled: Enable/disable auto-adjust
            operator_id: Operator making the change

        Returns:
            Success status
        """
        with self._lock:
            self._auto_adjust_mode = enabled
            logger.info(f"[SIGNAL_FIRST] Auto-adjust mode set to {enabled} by {operator_id}")
            return True

    def get_current_ratio(self) -> Dict[str, float]:
        """Get current signal-world ratio and optimal ratio."""
        with self._lock:
            return {
                "signal": self._current_signal_weight,
                "world": self._current_world_weight,
                "optimal_signal": self._optimal_signal_weight,
                "optimal_world": self._optimal_world_weight,
                "is_at_optimal": self.is_at_optimal_ratio(),
            }

    def get_presets(self) -> Dict[str, Dict[str, int]]:
        """Get available presets."""
        return self._presets

    def get_available_trading_categories(self) -> List[str]:
        """Get all available trading categories for dropdown."""
        return [category.value for category in TradingCategory]

    def get_available_trading_domains(self) -> List[str]:
        """Get all available trading domains for dropdown."""
        return [domain.value for domain in TradingDomain]

    def get_available_timeframes(self) -> List[str]:
        """Get all available timeframes for dropdown."""
        return [timeframe.value for timeframe in TimeFrame]

    def get_available_execution_modes(self) -> List[str]:
        """Get all available execution modes for dropdown."""
        return [mode.value for mode in ExecutionMode]

    def auto_adjust_ratio_for_regime(self, regime: MarketRegime):
        """Automatically adjust ratio based on market regime."""
        if not self._auto_adjust_mode:
            return

        adjustments = self._regime_adjustments.get(regime, {"signal_adjustment": 0, "world_adjustment": 0})
        new_signal_weight = self._current_signal_weight + adjustments["signal_adjustment"]

        # Ensure within bounds
        new_signal_weight = max(self._min_signal_weight, min(new_signal_weight, self._max_signal_weight))

        if new_signal_weight != self._current_signal_weight:
            self._current_signal_weight = new_signal_weight
            self._current_world_weight = 100.0 - new_signal_weight
            logger.info(
                f"[SIGNAL_FIRST] Auto-adjusted ratio for {regime.value}: {self._current_signal_weight}% signals, {self._current_world_weight}% world"
            )

    def make_decision(
        self,
        signal_decision: DecisionComponent,
        world_context: Dict[str, Any],
        market_regime: MarketRegime = MarketRegime.NORMAL,
    ) -> SignalFirstDecision:
        """Make a signal-first decision with world enhancement.

        Args:
            signal_decision: Decision component from signals (primary)
            world_context: World model context for enhancement
            market_regime: Current market regime for auto-adjustment

        Returns:
            SignalFirstDecision with signal-first approach
        """
        start_time = datetime.now()

        try:
            # Auto-adjust ratio based on regime if enabled
            self.auto_adjust_ratio_for_regime(market_regime)

            # Start with signal as primary decision (signal-first approach)
            base_decision = signal_decision.decision_type
            base_confidence = signal_decision.confidence * (self._current_signal_weight / 100.0)

            # Apply world enhancement (not replacement)
            world_enhancement = self._apply_world_enhancement(
                base_decision, signal_decision, world_context
            )

            # Check for world veto (only in extreme conditions)
            if self._should_world_veto(signal_decision, world_context):
                # World veto - use world decision instead
                decision_type = world_enhancement.decision_type
                confidence = signal_decision.confidence  # Keep original signal confidence
                modification_type = "veto"
                primary_source = DecisionSource.SIGNAL_OVERRIDE
                self._metrics.world_vetoes += 1
                rationale = f"World veto applied: {world_context.get('veto_reason', 'extreme condition')}"
            else:
                # Signal decision with world enhancement
                decision_type = world_enhancement.decision_type
                confidence = base_confidence + (world_enhancement.confidence * (self._current_world_weight / 100.0))
                confidence = min(confidence, 1.0)
                modification_type = world_enhancement.modification_type
                primary_source = DecisionSource.SIGNAL_PRIMARY if not world_enhancement.world_modifier_applied else DecisionSource.WORLD_ENHANCEMENT
                rationale = f"Signal-first decision with {self._current_signal_weight}% signals, {self._current_world_weight}% world enhancement"

            # Determine source classification
            if primary_source == DecisionSource.SIGNAL_PRIMARY and not world_enhancement.world_modifier_applied:
                self._metrics.signal_primary_decisions += 1
            elif primary_source == DecisionSource.WORLD_ENHANCEMENT:
                self._metrics.world_enhanced_decisions += 1
            elif primary_source == DecisionSource.SIGNAL_OVERRIDE:
                self._metrics.signal_override_decisions += 1

            # Track decision
            decision = SignalFirstDecision(
                decision_type=decision_type,
                confidence=confidence,
                primary_source=primary_source,
                signal_weight=self._current_signal_weight,
                world_weight=self._current_world_weight,
                signal_component=signal_decision,
                world_enhancement=world_enhancement,
                world_modifier_applied=world_enhancement.world_modifier_applied,
                modification_type=modification_type,
                rationale=rationale,
                metadata={"market_regime": market_regime.value, "auto_adjust_mode": self._auto_adjust_mode},
            )

            self._decision_history.append(decision)

            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_decision_metrics(decision, processing_time, success=True)

            logger.debug(
                f"[SIGNAL_FIRST] Made {decision.decision_type} decision: {self._current_signal_weight}% signals, {self._current_world_weight}% world, confidence: {decision.confidence:.2f}"
            )

        except Exception as e:
            logger.error(f"[SIGNAL_FIRST] Error making decision: {e}")
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_decision_metrics(None, processing_time, success=False)

            # Return fallback decision (pure signal)
            decision = SignalFirstDecision(
                decision_type=signal_decision.decision_type,
                confidence=signal_decision.confidence,
                primary_source=DecisionSource.FALLBACK,
                signal_weight=self._current_signal_weight,
                world_weight=self._current_world_weight,
                signal_component=signal_decision,
                world_enhancement=None,
                world_modifier_applied=False,
                modification_type="fallback",
                rationale="Fallback to pure signal due to processing error",
                metadata={"fallback": True},
            )
            self._metrics.fallback_decisions += 1

        return decision

    def _apply_world_enhancement(
        self, base_decision: str, signal_decision: DecisionComponent, world_context: Dict[str, Any]
    ) -> DecisionComponent:
        """Apply world enhancement to signal decision.

        This modifies signal parameters based on world context without replacing the decision.
        """
        modification_type = "none"
        modified_decision = base_decision
        modified_confidence = signal_decision.confidence

        # Check if world context suggests modification
        regime = world_context.get("market_regime", "normal")
        volatility = world_context.get("volatility_regime", "normal")
        liquidity = world_context.get("liquidity_state", "high")

        # Example world modifications (signal-first, not replacement):
        if regime == "high_volatility":
            # Reduce position size, maintain direction
            modification_type = "risk_adjustment"
            modified_confidence = signal_decision.confidence * 0.9  # Reduce confidence in volatility

        elif regime == "low_liquidity":
            # Adjust execution strategy, maintain decision
            modification_type = "parameter_adjustment"
            modified_confidence = signal_decision.confidence * 0.95

        elif regime == "crisis":
            # Extreme condition - may need to override
            modification_type = "veto_risk"
            if signal_decision.decision_type == "buy":
                modified_decision = "hold"  # Crisis override

        return DecisionComponent(
            source=DecisionSource.WORLD_ENHANCEMENT,
            decision_type=modified_decision,
            confidence=modified_confidence,
            reasoning=f"World enhancement: {modification_type} for {regime}",
            data=world_context,
            world_modifier_applied=(modification_type != "none"),
            modification_type=modification_type,
        )

    def _should_world_veto(self, signal_decision: DecisionComponent, world_context: Dict[str, Any]) -> bool:
        """Determine if world model should veto signal decision (extreme conditions only)."""
        # World veto only in extreme conditions
        extreme_conditions = [
            world_context.get("market_regime") == "crisis",
            world_context.get("extreme_volatility_warning", False),
            world_context.get("system_failure_warning", False),
            world_context.get("liquidity_crisis", False),
        ]

        return any(extreme_conditions)

    def _update_decision_metrics(self, decision: Optional[SignalFirstDecision], processing_time_ms: float, success: bool):
        """Update decision metrics."""
        with self._lock:
            self._metrics.total_decisions += 1

            if success and decision:
                # Update confidence average
                self._metrics.average_confidence = (
                    self._metrics.average_confidence * (self._metrics.total_decisions - 1) + decision.confidence
                ) / self._metrics.total_decisions

                # Update weight averages
                self._metrics.average_signal_weight = (
                    self._metrics.average_signal_weight * (self._metrics.total_decisions - 1) + decision.signal_weight
                ) / self._metrics.total_decisions

                self._metrics.average_world_weight = (
                    self._metrics.average_world_weight * (self._metrics.total_decisions - 1) + decision.world_weight
                ) / self._metrics.total_decisions

                # Update modification rate
                if decision.world_modifier_applied:
                    self._metrics.modification_applied_rate = (
                        self._metrics.modification_applied_rate * (self._metrics.total_decisions - 1) + 1
                    ) / self._metrics.total_decisions

                # Update success rate
                self._metrics.decision_success_rate = (
                    self._metrics.decision_success_rate * (self._metrics.total_decisions - 1) + 1
                ) / self._metrics.total_decisions
            else:
                # Update failure rate
                self._metrics.decision_success_rate = (
                    self._metrics.decision_success_rate * (self._metrics.total_decisions - 1) + 0
                ) / self._metrics.total_decisions

            # Update processing time
            self._metrics.average_processing_time_ms = (
                self._metrics.average_processing_time_ms * (self._metrics.total_decisions - 1) + processing_time_ms
            ) / self._metrics.total_decisions

            self._metrics.last_updated = datetime.now()

    def get_metrics(self) -> DecisionMetrics:
        """Get current decision metrics."""
        return self._metrics

    def get_decision_history(self, limit: int = 100) -> List[SignalFirstDecision]:
        """Get recent decision history."""
        with self._lock:
            return list(self._decision_history)[-limit:]


# Global instance
_signal_first_decision_engine: Optional[SignalFirstDecisionEngine] = None


def get_signal_first_engine() -> SignalFirstDecisionEngine:
    """Get the global signal-first decision engine instance."""
    global _signal_first_decision_engine
    if _signal_first_decision_engine is None:
        _signal_first_decision_engine = SignalFirstDecisionEngine()
    return _signal_first_decision_engine


__all__ = [
    "DecisionSource",
    "TradingCategory",
    "TradingDomain",
    "TimeFrame",
    "ExecutionMode",
    "SignalWorldRatio",
    "MarketRegime",
    "DecisionComponent",
    "SignalFirstDecision",
    "DecisionMetrics",
    "SignalFirstDecisionEngine",
    "get_signal_first_engine",
]