"""
Signal-World Ratio Analyzer for Different Trading Forms
Analyzes optimal signal/world processing ratios for different trading strategies, domains, and execution modes.

Based on system analysis of:
- 15+ trading categories from strategy registry
- 7 multi-domain trading environments (crypto, forex, stocks, futures, options, commodities)
- Multiple execution modes (AUTO, SEMI_AUTO, MANUAL)
- Different timeframes (scalping, swing, position, day trading)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple


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


class MarketRegime(Enum):
    """Market regimes for dynamic adjustment."""
    NORMAL = "normal"
    HIGH_VOLATILITY = "high_volatility"
    LOW_LIQUIDITY = "low_liquidity"
    TRENDING = "trending"
    MEAN_REVERTING = "mean_reverting"
    CRISIS = "crisis"


@dataclass
class TradingForm:
    """Complete trading form configuration."""
    category: TradingCategory
    domain: TradingDomain
    timeframe: TimeFrame
    execution_mode: ExecutionMode
    
    # Derived characteristics
    latency_requirement: str  # "ultra_low", "low", "medium", "high"
    signal_dependency: str  # "critical", "high", "medium", "low"
    world_context_value: str  # "minimal", "low", "medium", "high", "critical"
    profit_optimization: str  # "signal_focused", "balanced", "context_enhanced"


@dataclass
class RatioConfiguration:
    """Optimal signal/world ratio configuration for a trading form."""
    trading_form: TradingForm
    signal_percent: int
    world_percent: int
    rationale: str
    performance_expectation: str
    risk_level: str
    
    # Dynamic adjustment parameters
    allow_regime_adjustment: bool = True
    min_signal_percent: int = 50
    max_signal_percent: int = 95
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "category": self.trading_form.category.value,
            "domain": self.trading_form.domain.value,
            "timeframe": self.trading_form.timeframe.value,
            "execution_mode": self.trading_form.execution_mode.value,
            "signal_percent": self.signal_percent,
            "world_percent": self.world_percent,
            "rationale": self.rationale,
            "performance_expectation": self.performance_expectation,
            "risk_level": self.risk_level,
            "allow_regime_adjustment": self.allow_regime_adjustment,
            "min_signal_percent": self.min_signal_percent,
            "max_signal_percent": self.max_signal_percent,
        }


class SignalWorldRatioAnalyzer:
    """Analyzer for determining optimal signal/world ratios across trading forms."""
    
    def __init__(self):
        self._ratio_database = self._initialize_ratio_database()
        self._regime_adjustments = self._initialize_regime_adjustments()
    
    def _initialize_ratio_database(self) -> Dict[Tuple[str, str, str, str], RatioConfiguration]:
        """Initialize database of optimal ratios for different trading forms."""
        database = {}
        
        # === HIGH FREQUENCY TRADING ===
        # Crypto scalping (ultra-fast, signal-critical)
        database[(
            TradingCategory.HIGH_FREQUENCY.value,
            TradingDomain.CRYPTO.value,
            TimeFrame.SCALPING.value,
            ExecutionMode.AUTO.value
        )] = RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory.HIGH_FREQUENCY,
                domain=TradingDomain.CRYPTO,
                timeframe=TimeFrame.SCALPING,
                execution_mode=ExecutionMode.AUTO,
                latency_requirement="ultra_low",
                signal_dependency="critical",
                world_context_value="minimal",
                profit_optimization="signal_focused"
            ),
            signal_percent=95,
            world_percent=5,
            rationale="HFT requires maximum signal processing speed. World context is minimal overhead for millisecond-level decisions.",
            performance_expectation="High profit from signal speed and volume",
            risk_level="HIGH (signal dependency)",
            allow_regime_adjustment=False  # No regime adjustment for HFT
            min_signal_percent=95,
            max_signal_percent=95
        )
        
        # === LIQUIDITY-FOCUSED TRADING ===
        # Crypto discretionary hybrid swing (liquidity sweep detection)
        database[(
            TradingCategory.LIQUIDITY_FOCUSED.value,
            TradingDomain.CRYPTO.value,
            TimeFrame.SWING.value,
            ExecutionMode.SEMI_AUTO.value
        )] = RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory.LIQUIDITY_FOCUSED,
                domain=TradingDomain.CRYPTO,
                timeframe=TimeFrame.SWING,
                execution_mode=ExecutionMode.SEMI_AUTO,
                latency_requirement="low",
                signal_dependency="high",
                world_context_value="medium",
                profit_optimization="balanced"
            ),
            signal_percent=85,
            world_percent=15,
            rationale="Liquidity signals are critical but world context (regime, volatility) provides essential risk enhancement.",
            performance_expectation="High profit from liquidity sweeps with regime awareness",
            risk_level="MEDIUM",
            allow_regime_adjustment=True,
            min_signal_percent=70,
            max_signal_percent=90
        )
        
        # === SYSTEMATIC QUANTITATIVE TRADING ===
        # Futures trend-following (Turtle Trading style)
        database[(
            TradingCategory.SYSTEMATIC_QUANTITATIVE.value,
            TradingDomain.FUTURES.value,
            TimeFrame.POSITION.value,
            ExecutionMode.AUTO.value
        )] = RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory.SYSTEMATIC_QUANTITATIVE,
                domain=TradingDomain.FUTURES,
                timeframe=TimeFrame.POSITION,
                execution_mode=ExecutionMode.AUTO,
                latency_requirement="medium",
                signal_dependency="high",
                world_context_value="low",
                profit_optimization="signal_focused"
            ),
            signal_percent=90,
            world_percent=10,
            rationale="Systematic trend following relies on proven signal rules. World context provides regime awareness.",
            performance_expectation="Consistent profit from trend signals with minimal overhead",
            risk_level="MEDIUM-HIGH",
            allow_regime_adjustment=True,
            min_signal_percent=85,
            max_signal_percent=95
        )
        
        # === VOLATILITY EXPLOITATION ===
        # Options volatility trading (world-aware)
        database[(
            TradingCategory.VOLATILITY_EXPLOITATION.value,
            TradingDomain.OPTIONS.value,
            TimeFrame.DAY_TRADING.value,
            ExecutionMode.AUTO.value
        )] = RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory.VOLATILITY_EXPLOITATION,
                domain=TradingDomain.OPTIONS,
                timeframe=TimeFrame.DAY_TRADING,
                execution_mode=ExecutionMode.AUTO,
                latency_requirement="medium",
                signal_dependency="high",
                world_context_value="high",
                profit_optimization="context_enhanced"
            ),
            signal_percent=70,
            world_percent=30,
            rationale="Volatility trading requires significant world context (regime, events, correlation) for effective risk management.",
            performance_expectation="High profit with superior risk management from world context",
            risk_level="MEDIUM-LOW",
            allow_regime_adjustment=True,
            min_signal_percent=60,
            max_signal_percent=80
        )
        
        # === ARBITRAGE ===
        # Cross-exchange arbitrage (signal-critical)
        database[(
            TradingCategory.ARBITRAGE.value,
            TradingDomain.CRYPTO.value,
            TimeFrame.SCALPING.value,
            ExecutionMode.AUTO.value
        )] = RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory.ARBITRAGE,
                domain=TradingDomain.CRYPTO,
                timeframe=TimeFrame.SCALPING,
                execution_mode=ExecutionMode.AUTO,
                latency_requirement="ultra_low",
                signal_dependency="critical",
                world_context_value="minimal",
                profit_optimization="signal_focused"
            ),
            signal_percent=95,
            world_percent=5,
            rationale="Arbitrage is purely signal-driven (price differences). World context is unnecessary overhead.",
            performance_expectation="Risk-free profit from price differences (theoretical)",
            risk_level="LOW (execution risk)",
            allow_regime_adjustment=False,
            min_signal_percent=95,
            max_signal_percent=95
        )
        
        # === EVENT-DRIVEN TRADING ===
        # News/event-driven trading (world-critical)
        database[(
            TradingCategory.EVENT_DRIVEN.value,
            TradingDomain.STOCKS.value,
            TimeFrame.SWING.value,
            ExecutionMode.SEMI_AUTO.value
        )] = RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory.EVENT_DRIVEN,
                domain=TradingDomain.STOCKS,
                timeframe=TimeFrame.SWING,
                execution_mode=ExecutionMode.SEMI_AUTO,
                latency_requirement="medium",
                signal_dependency="medium",
                world_context_value="critical",
                profit_optimization="context_enhanced"
            ),
            signal_percent=60,
            world_percent=40,
            rationale="Event-driven trading is fundamentally about understanding world events. World context is primary.",
            performance_expectation="High profit from correctly interpreting events",
            risk_level="MEDIUM",
            allow_regime_adjustment=True,
            min_signal_percent=50,
            max_signal_percent=75
        )
        
        # === PORTFOLIO OPTIMIZATION ===
        # Multi-asset portfolio management (world-enhanced)
        database[(
            TradingCategory.PORTFOLIO_OPTIMIZATION.value,
            TradingDomain.STOCKS.value,
            TimeFrame.POSITION.value,
            ExecutionMode.AUTO.value
        )] = RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory.PORTFOLIO_OPTIMIZATION,
                domain=TradingDomain.STOCKS,
                timeframe=TimeFrame.POSITION,
                execution_mode=ExecutionMode.AUTO,
                latency_requirement="high",
                signal_dependency="medium",
                world_context_value="high",
                profit_optimization="context_enhanced"
            ),
            signal_percent=65,
            world_percent=35,
            rationale="Portfolio optimization requires broad world context (macro, correlation, regime) for optimal allocation.",
            performance_expectation="Steady profit with superior risk-adjusted returns",
            risk_level="LOW",
            allow_regime_adjustment=True,
            min_signal_percent=50,
            max_signal_percent=75
        )
        
        # === MARKET MAKING ===
        # Market making (signal-critical for inventory)
        database[(
            TradingCategory.MARKET_MAKING.value,
            TradingDomain.CRYPTO.value,
            TimeFrame.SCALPING.value,
            ExecutionMode.AUTO.value
        )] = RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory.MARKET_MAKING,
                domain=TradingDomain.CRYPTO,
                timeframe=TimeFrame.SCALPING,
                execution_mode=ExecutionMode.AUTO,
                latency_requirement="ultra_low",
                signal_dependency="critical",
                world_context_value="low",
                profit_optimization="signal_focused"
            ),
            signal_percent=90,
            world_percent=10,
            rationale="Market making is inventory-critical (signal-driven). World context provides regime awareness for risk.",
            performance_expectment="Profit from bid-ask spread with inventory optimization",
            risk_level="MEDIUM",
            allow_regime_adjustment=True,
            min_signal_percent=80,
            max_signal_percent=95
        )
        
        # === AI ADAPTIVE ===
        # AI-powered adaptive strategies (balanced)
        database[(
            TradingCategory.AI_ADAPTIVE.value,
            TradingDomain.FOREX.value,
            TimeFrame.SWING.value,
            ExecutionMode.AUTO.value
        )] = RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory.AI_ADAPTIVE,
                domain=TradingDomain.FOREX,
                timeframe=TimeFrame.SWING,
                execution_mode=ExecutionMode.AUTO,
                latency_requirement="low",
                signal_dependency="medium",
                world_context_value="medium",
                profit_optimization="balanced"
            ),
            signal_percent=75,
            world_percent=25,
            rationale="AI adaptive systems benefit from balanced signal/world integration for learning and adaptation.",
            performance_expectation="Adaptive profit with continuous improvement",
            risk_level="MEDIUM",
            allow_regime_adjustment=True,
            min_signal_percent=60,
            max_signal_percent=85
        )
        
        return database
    
    def _initialize_regime_adjustments(self) -> Dict[MarketRegime, Dict[str, int]]:
        """Initialize regime-based dynamic adjustments."""
        return {
            MarketRegime.NORMAL: {"signal_adjustment": 0, "world_adjustment": 0},
            MarketRegime.HIGH_VOLATILITY: {"signal_adjustment": -10, "world_adjustment": +10},  # More world in volatility
            MarketRegime.LOW_LIQUIDITY: {"signal_adjustment": -5, "world_adjustment": +5},  # More world for liquidity risk
            MarketRegime.TRENDING: {"signal_adjustment": +5, "world_adjustment": -5},  # More signal in trends
            MarketRegime.MEAN_REVERTING: {"signal_adjustment": -5, "world_adjustment": +5},  # More world for mean reversion
            MarketRegime.CRISIS: {"signal_adjustment": -20, "world_adjustment": +20},  # Equal in crisis
        }
    
    def get_optimal_ratio(
        self,
        category: str,
        domain: str,
        timeframe: str,
        execution_mode: str,
        regime: MarketRegime = MarketRegime.NORMAL
    ) -> RatioConfiguration:
        """Get optimal ratio for a specific trading form."""
        # Base configuration
        base_config = self._ratio_database.get(
            (category, domain, timeframe, execution_mode),
            self._get_default_configuration(category, domain)
        )
        
        # Apply regime adjustment if allowed
        if base_config.allow_regime_adjustment and regime != MarketRegime.NORMAL:
            return self._apply_regime_adjustment(base_config, regime)
        
        return base_config
    
    def _get_default_configuration(self, category: str, domain: str) -> RatioConfiguration:
        """Get default configuration when specific form not found."""
        # Conservative defaults
        return RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory[category.upper()] if category.upper() in [c.value for c in TradingCategory] else TradingCategory.SYSTEMATIC_QUANTITATIVE,
                domain=TradingDomain[domain.upper()] if domain.upper() in [d.value for d in TradingDomain] else TradingDomain.CRYPTO,
                timeframe=TimeFrame.SWING,
                execution_mode=ExecutionMode.AUTO,
                latency_requirement="medium",
                signal_dependency="high",
                world_context_value="medium",
                profit_optimization="balanced"
            ),
            signal_percent=85,
            world_percent=15,
            rationale="Default balanced configuration for unspecified trading forms.",
            performance_expectation="Balanced profit with reasonable risk",
            risk_level="MEDIUM",
            allow_regime_adjustment=True,
            min_signal_percent=70,
            max_signal_percent=90
        )
    
    def _apply_regime_adjustment(self, config: RatioConfiguration, regime: MarketRegime) -> RatioConfiguration:
        """Apply regime-based adjustment to configuration."""
        adjustments = self._regime_adjustments.get(regime, {"signal_adjustment": 0, "world_adjustment": 0})
        
        adjusted_signal = config.signal_percent + adjustments["signal_adjustment"]
        adjusted_world = config.world_percent + adjustments["world_adjustment"]
        
        # Ensure within bounds
        adjusted_signal = max(config.min_signal_percent, min(adjusted_signal, config.max_signal_percent))
        adjusted_world = 100 - adjusted_signal
        
        return RatioConfiguration(
            trading_form=config.trading_form,
            signal_percent=adjusted_signal,
            world_percent=adjusted_world,
            rationale=f"{config.rationale} (Regime-adjusted: {regime.value})",
            performance_expectation=config.performance_expectation,
            risk_level=config.risk_level,
            allow_regime_adjustment=config.allow_regime_adjustment,
            min_signal_percent=config.min_signal_percent,
            max_signal_percent=config.max_signal_percent
        )
    
    def get_all_configurations(self) -> Dict[str, RatioConfiguration]:
        """Get all ratio configurations organized by key."""
        return {f"{k[0]}_{k[1]}_{k[2]}_{k[3]}": v for k, v in self._ratio_database.items()}
    
    def get_universal_baseline(self) -> RatioConfiguration:
        """Get universal baseline configuration for all trading forms."""
        return RatioConfiguration(
            trading_form=TradingForm(
                category=TradingCategory.SYSTEMATIC_QUANTITATIVE,
                domain=TradingDomain.CRYPTO,
                timeframe=TimeFrame.SWING,
                execution_mode=ExecutionMode.AUTO,
                latency_requirement="medium",
                signal_dependency="high",
                world_context_value="medium",
                profit_optimization="balanced"
            ),
            signal_percent=85,
            world_percent=15,
            rationale="Universal baseline: Signal-dominant with meaningful world context enhancement. Balances profit optimization with risk management across all trading forms.",
            performance_expectation="Strong profit across most strategies with reasonable risk",
            risk_level="MEDIUM",
            allow_regime_adjustment=True,
            min_signal_percent=70,
            max_signal_percent=90
        )


# Global analyzer instance
_ratio_analyzer = None

def get_ratio_analyzer() -> SignalWorldRatioAnalyzer:
    """Get global ratio analyzer instance."""
    global _ratio_analyzer
    if _ratio_analyzer is None:
        _ratio_analyzer = SignalWorldRatioAnalyzer()
    return _ratio_analyzer


# Universal baseline recommendations
UNIVERSAL_BASELINE = {
    "recommended_default": {"signal": 85, "world": 15},
    "conservative_default": {"signal": 80, "world": 20},
    "aggressive_default": {"signal": 90, "world": 10},
    "safety_fallback": {"signal": 70, "world": 30},
    
    # Category-specific baselines
    "high_frequency_baseline": {"signal": 95, "world": 5},
    "signal_trading_baseline": {"signal": 90, "world": 10},
    "balanced_trading_baseline": {"signal": 85, "world": 15},
    "cognitive_trading_baseline": {"signal": 70, "world": 30},
    
    # Domain-specific baselines
    "crypto_baseline": {"signal": 90, "world": 10},
    "forex_baseline": {"signal": 85, "world": 15},
    "stocks_baseline": {"signal": 80, "world": 20},
    "futures_baseline": {"signal": 85, "world": 15},
    "options_baseline": {"signal": 75, "world": 25},
    "commodities_baseline": {"signal": 85, "world": 15},
    
    # Timeframe-specific baselines
    "scalping_baseline": {"signal": 95, "world": 5},
    "day_trading_baseline": {"signal": 90, "world": 10},
    "swing_baseline": {"signal": 85, "world": 15},
    "position_baseline": {"signal": 75, "world": 25},
}


__all__ = [
    "TradingCategory",
    "TradingDomain",
    "TimeFrame",
    "ExecutionMode",
    "MarketRegime",
    "TradingForm",
    "RatioConfiguration",
    "SignalWorldRatioAnalyzer",
    "get_ratio_analyzer",
    "UNIVERSAL_BASELINE",
]