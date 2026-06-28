"""MAC-02 — Advanced regime transition prediction and smooth adaptation.

Enhances INDIRA's ability to predict regime transitions and adapt smoothly
to changing market conditions, reducing whipsaw and improving decision quality.

Pure computation. No clocks, no I/O. INV-15 deterministic.
B1: No imports from execution_engine/governance_engine/learning_engine/evolution_engine.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum


class RegimeTransitionType(Enum):
    """Types of regime transitions."""

    BULL_TO_BEAR = "bull_to_bear"
    BEAR_TO_BULL = "bear_to_bull"
    RANGING_TO_TREND = "ranging_to_trend"
    TREND_TO_RANGING = "trend_to_ranging"
    VOLATILITY_EXPANSION = "volatility_expansion"
    VOLATILITY_CONTRACTION = "volatility_contraction"
    REGIME_SHIFT = "regime_shift"


@dataclass(frozen=True, slots=True)
class RegimeTransitionSignal:
    """Early warning signal for regime transition."""

    signal_id: str
    transition_type: RegimeTransitionType
    current_regime: str
    predicted_regime: str
    confidence: float  # 0.0 to 1.0
    time_horizon_bars: int  # Expected time until transition
    leading_indicators: tuple[str, ...]  # Indicators suggesting this transition
    risk_implications: tuple[str, ...]  # Potential risks if transition occurs
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class RegimeAdaptationStrategy:
    """Strategy for adapting to regime transition."""

    adaptation_id: str
    transition_type: RegimeTransitionType
    pre_transition_actions: tuple[str, ...]  # Actions to take before transition
    post_transition_actions: tuple[str, ...]  # Actions to take after transition
    position_adjustments: dict[str, float]  # Position size adjustments by asset class
    risk_adjustments: dict[str, float]  # Risk parameter adjustments
    confidence_threshold: float  # Minimum confidence to execute strategy


@dataclass(frozen=True, slots=True)
class SmoothTransitionState:
    """State for smooth regime transition handling."""

    current_regime: str
    target_regime: str
    transition_progress: float  # 0.0 to 1.0
    adaptation_speed: float  # Speed of adaptation
    signal_confidence: float
    estimated_completion_bars: int
    active_adjustments: dict[str, float]  # Current active parameter adjustments
    timestamp_ns: int


class RegimeTransitionPredictor:
    """Predicts regime transitions using leading indicators and pattern recognition.

    Analyzes market conditions to identify early warning signals of regime
    changes, allowing INDIRA to prepare and adapt smoothly rather than
    reacting abruptly.
    """

    def __init__(
        self,
        lookback_window: int = 100,
        prediction_horizon: int = 20,
        confidence_threshold: float = 0.6,
    ) -> None:
        self._lookback_window = lookback_window
        self._prediction_horizon = prediction_horizon
        self._confidence_threshold = confidence_threshold

        self._regime_history: deque[str] = deque(maxlen=lookback_window)
        self._indicator_history: dict[str, deque[float]] = {}
        self._transition_signals: deque[RegimeTransitionSignal] = deque(maxlen=20)

    def update_regime(self, regime: str, timestamp_ns: int) -> None:
        """Update current regime."""
        self._regime_history.append(regime)

    def update_indicator(self, indicator_name: str, value: float) -> None:
        """Update indicator value."""
        if indicator_name not in self._indicator_history:
            self._indicator_history[indicator_name] = deque(maxlen=self._lookback_window)
        self._indicator_history[indicator_name].append(value)

    def predict_transitions(self, timestamp_ns: int) -> tuple[RegimeTransitionSignal, ...]:
        """Predict potential regime transitions.

        Args:
            timestamp_ns: Current timestamp

        Returns:
            Tuple of predicted regime transitions
        """
        if len(self._regime_history) < 10:
            return ()

        current_regime = self._regime_history[-1]
        signals = []

        # Analyze for different transition types
        signals.extend(self._check_volatility_expansion(current_regime, timestamp_ns))
        signals.extend(self._check_volatility_contraction(current_regime, timestamp_ns))
        signals.extend(self._check_trend_exhaustion(current_regime, timestamp_ns))
        signals.extend(self._check_range_breakout(current_regime, timestamp_ns))

        # Filter by confidence threshold
        high_confidence_signals = [s for s in signals if s.confidence >= self._confidence_threshold]

        # Store signals
        for signal in high_confidence_signals:
            self._transition_signals.append(signal)

        return tuple(high_confidence_signals)

    def _check_volatility_expansion(
        self, current_regime: str, timestamp_ns: int
    ) -> list[RegimeTransitionSignal]:
        """Check for volatility expansion signals."""
        signals = []

        if "volatility" not in self._indicator_history:
            return signals

        vol_history = list(self._indicator_history["volatility"])
        if len(vol_history) < 20:
            return signals

        recent_vol = vol_history[-10:]
        historical_vol = vol_history[-20:-10]

        avg_recent = sum(recent_vol) / len(recent_vol)
        avg_historical = sum(historical_vol) / len(historical_vol)

        vol_increase = (avg_recent - avg_historical) / avg_historical if avg_historical > 0 else 0.0

        if vol_increase > 0.5:  # 50% increase in volatility
            confidence = min(0.9, vol_increase)

            predicted_regime = "volatile" if current_regime != "volatile" else current_regime

            signal = RegimeTransitionSignal(
                signal_id=f"vol_expansion_{timestamp_ns}",
                transition_type=RegimeTransitionType.VOLATILITY_EXPANSION,
                current_regime=current_regime,
                predicted_regime=predicted_regime,
                confidence=confidence,
                time_horizon_bars=5,
                leading_indicators=("volatility_spike", "range_expansion"),
                risk_implications=("increased_whipsaw_risk", "position_sizing_reduction"),
                timestamp_ns=timestamp_ns,
            )
            signals.append(signal)

        return signals

    def _check_volatility_contraction(
        self, current_regime: str, timestamp_ns: int
    ) -> list[RegimeTransitionSignal]:
        """Check for volatility contraction signals."""
        signals = []

        if "volatility" not in self._indicator_history:
            return signals

        vol_history = list(self._indicator_history["volatility"])
        if len(vol_history) < 20:
            return signals

        recent_vol = vol_history[-10:]
        historical_vol = vol_history[-20:-10]

        avg_recent = sum(recent_vol) / len(recent_vol)
        avg_historical = sum(historical_vol) / len(historical_vol)

        vol_decrease = (avg_historical - avg_recent) / avg_historical if avg_historical > 0 else 0.0

        if vol_decrease > 0.3:  # 30% decrease in volatility
            confidence = min(0.85, vol_decrease + 0.3)

            if current_regime == "volatile":
                predicted_regime = "ranging"
            else:
                predicted_regime = current_regime

            signal = RegimeTransitionSignal(
                signal_id=f"vol_contraction_{timestamp_ns}",
                transition_type=RegimeTransitionType.VOLATILITY_CONTRACTION,
                current_regime=current_regime,
                predicted_regime=predicted_regime,
                confidence=confidence,
                time_horizon_bars=8,
                leading_indicators=("volatility_contraction", "range_contraction"),
                risk_implications=("trend_following_opportunity", "position_sizing_increase"),
                timestamp_ns=timestamp_ns,
            )
            signals.append(signal)

        return signals

    def _check_trend_exhaustion(
        self, current_regime: str, timestamp_ns: int
    ) -> list[RegimeTransitionSignal]:
        """Check for trend exhaustion signals."""
        signals = []

        if current_regime not in ("bull", "bear"):
            return signals

        if "trend_strength" not in self._indicator_history:
            return signals

        trend_history = list(self._indicator_history["trend_strength"])
        if len(trend_history) < 15:
            return signals

        recent_trend = trend_history[-5:]
        earlier_trend = trend_history[-15:-5]

        avg_recent = sum(recent_trend) / len(recent_trend)
        avg_earlier = sum(earlier_trend) / len(earlier_trend)

        trend_decline = (avg_earlier - avg_recent) / avg_earlier if avg_earlier > 0 else 0.0

        if trend_decline > 0.4:  # 40% decline in trend strength
            confidence = min(0.8, trend_decline + 0.2)

            if current_regime == "bull":
                predicted_regime = "bear"
            else:
                predicted_regime = "bull"

            signal = RegimeTransitionSignal(
                signal_id=f"trend_exhaustion_{timestamp_ns}",
                transition_type=(
                    RegimeTransitionType.BULL_TO_BEAR
                    if current_regime == "bull"
                    else RegimeTransitionType.BEAR_TO_BULL
                ),
                current_regime=current_regime,
                predicted_regime=predicted_regime,
                confidence=confidence,
                time_horizon_bars=10,
                leading_indicators=("trend_weakness", "momentum_divergence"),
                risk_implications=("trend_reversal_risk", "position_reversal_consideration"),
                timestamp_ns=timestamp_ns,
            )
            signals.append(signal)

        return signals

    def _check_range_breakout(
        self, current_regime: str, timestamp_ns: int
    ) -> list[RegimeTransitionSignal]:
        """Check for range breakout signals."""
        signals = []

        if current_regime != "ranging":
            return signals

        if "price_momentum" not in self._indicator_history:
            return signals

        momentum_history = list(self._indicator_history["price_momentum"])
        if len(momentum_history) < 10:
            return signals

        recent_momentum = momentum_history[-5:]
        avg_momentum = sum(recent_momentum) / len(recent_momentum)

        if abs(avg_momentum) > 0.3:  # Strong momentum breakout
            confidence = min(0.85, abs(avg_momentum) + 0.3)

            predicted_regime = "bull" if avg_momentum > 0 else "bear"

            signal = RegimeTransitionSignal(
                signal_id=f"range_breakout_{timestamp_ns}",
                transition_type=RegimeTransitionType.RANGING_TO_TREND,
                current_regime=current_regime,
                predicted_regime=predicted_regime,
                confidence=confidence,
                time_horizon_bars=5,
                leading_indicators=("momentum_breakout", "volume_increase"),
                risk_implications=("trend_following_opportunity", "breakout_failure_risk"),
                timestamp_ns=timestamp_ns,
            )
            signals.append(signal)

        return signals


class SmoothRegimeAdapter:
    """Handles smooth regime transitions to avoid whipsaw and improve stability.

    Instead of abrupt regime changes, uses gradual adaptation with
    confidence-based blending of strategies and parameters.
    """

    def __init__(
        self,
        adaptation_speed: float = 0.1,  # Speed of transition (0.0 to 1.0)
        min_confidence: float = 0.7,  # Minimum confidence to trigger adaptation
    ) -> None:
        self._adaptation_speed = adaptation_speed
        self._min_confidence = min_confidence

        self._current_state: SmoothTransitionState | None = None
        self._adaptation_strategies: dict[RegimeTransitionType, RegimeAdaptationStrategy] = {}
        self._state_history: deque[SmoothTransitionState] = deque(maxlen=10)

        # Initialize default adaptation strategies
        self._initialize_default_strategies()

    def _initialize_default_strategies(self) -> None:
        """Initialize default adaptation strategies for each transition type."""
        strategies = {
            RegimeTransitionType.BULL_TO_BEAR: RegimeAdaptationStrategy(
                adaptation_id="bull_to_bear_default",
                transition_type=RegimeTransitionType.BULL_TO_BEAR,
                pre_transition_actions=("reduce_exposure", "hedge_positions"),
                post_transition_actions=("increase_short_exposure", "reduce_long_exposure"),
                position_adjustments={"equity": -0.3, "fixed_income": 0.1},
                risk_adjustments={"position_sizing": 0.7, "stop_loss": 0.8},
                confidence_threshold=0.75,
            ),
            RegimeTransitionType.BEAR_TO_BULL: RegimeAdaptationStrategy(
                adaptation_id="bear_to_bull_default",
                transition_type=RegimeTransitionType.BEAR_TO_BULL,
                pre_transition_actions=("reduce_shorts", "accumulate_cash"),
                post_transition_actions=("increase_long_exposure", "reduce_hedges"),
                position_adjustments={"equity": 0.3, "fixed_income": -0.1},
                risk_adjustments={"position_sizing": 1.2, "stop_loss": 1.0},
                confidence_threshold=0.75,
            ),
            RegimeTransitionType.VOLATILITY_EXPANSION: RegimeAdaptationStrategy(
                adaptation_id="vol_expansion_default",
                transition_type=RegimeTransitionType.VOLATILITY_EXPANSION,
                pre_transition_actions=("reduce_position_sizes", "increase_cash_buffer"),
                post_transition_actions=("maintain_conservative_sizing", "widen_stops"),
                position_adjustments={"equity": -0.2, "cash": 0.2},
                risk_adjustments={"position_sizing": 0.6, "stop_loss": 0.7},
                confidence_threshold=0.65,
            ),
            RegimeTransitionType.VOLATILITY_CONTRACTION: RegimeAdaptationStrategy(
                adaptation_id="vol_contraction_default",
                transition_type=RegimeTransitionType.VOLATILITY_CONTRACTION,
                pre_transition_actions=("prepare_for_expansion", "test_strategy_validity"),
                post_transition_actions=("gradual_sizing_increase", "normalize_stops"),
                position_adjustments={"equity": 0.1, "cash": -0.1},
                risk_adjustments={"position_sizing": 1.1, "stop_loss": 1.0},
                confidence_threshold=0.60,
            ),
        }

        self._adaptation_strategies = strategies

    def process_transition_signal(
        self, signal: RegimeTransitionSignal, current_regime: str, timestamp_ns: int
    ) -> SmoothTransitionState:
        """Process a regime transition signal and initiate smooth adaptation.

        Args:
            signal: Transition signal
            current_regime: Current regime
            timestamp_ns: Current timestamp

        Returns:
            Current smooth transition state
        """
        if signal.confidence < self._min_confidence:
            # Not confident enough to trigger adaptation
            if self._current_state:
                # Continue existing transition if any
                self._current_state = self._advance_transition(self._current_state, timestamp_ns)
            return self._current_state or self._create_neutral_state(current_regime, timestamp_ns)

        # Check if this matches our current transition
        if self._current_state and self._current_state.target_regime == signal.predicted_regime:
            # Reinforce existing transition
            self._current_state = self._advance_transition(self._current_state, timestamp_ns)
            return self._current_state

        # New transition - initiate smooth adaptation
        strategy = self._adaptation_strategies.get(
            signal.transition_type,
            self._adaptation_strategies[RegimeTransitionType.REGIME_SHIFT],  # Fallback
        )

        self._current_state = SmoothTransitionState(
            current_regime=current_regime,
            target_regime=signal.predicted_regime,
            transition_progress=0.0,
            adaptation_speed=self._adaptation_speed * signal.confidence,
            signal_confidence=signal.confidence,
            estimated_completion_bars=signal.time_horizon_bars,
            active_adjustments=self._calculate_initial_adjustments(strategy),
            timestamp_ns=timestamp_ns,
        )

        self._state_history.append(self._current_state)

        return self._current_state

    def _advance_transition(
        self, state: SmoothTransitionState, timestamp_ns: int
    ) -> SmoothTransitionState:
        """Advance an existing smooth transition."""
        new_progress = min(1.0, state.transition_progress + state.adaptation_speed)

        if new_progress >= 1.0:
            # Transition complete
            return self._create_neutral_state(state.target_regime, timestamp_ns)

        # Calculate new adjustments based on progress
        strategy = self._adaptation_strategies.get(
            self._infer_transition_type(state.current_regime, state.target_regime),
            self._adaptation_strategies[RegimeTransitionType.REGIME_SHIFT],
        )

        new_adjustments = self._calculate_progressive_adjustments(strategy, new_progress)

        return SmoothTransitionState(
            current_regime=state.current_regime,
            target_regime=state.target_regime,
            transition_progress=new_progress,
            adaptation_speed=state.adaptation_speed,
            signal_confidence=state.signal_confidence,
            estimated_completion_bars=max(0, state.estimated_completion_bars - 1),
            active_adjustments=new_adjustments,
            timestamp_ns=timestamp_ns,
        )

    def _infer_transition_type(
        self, current_regime: str, target_regime: str
    ) -> RegimeTransitionType:
        """Infer transition type from regime names."""
        if current_regime == "bull" and target_regime == "bear":
            return RegimeTransitionType.BULL_TO_BEAR
        elif current_regime == "bear" and target_regime == "bull":
            return RegimeTransitionType.BEAR_TO_BULL
        elif current_regime == "ranging" and target_regime in ("bull", "bear"):
            return RegimeTransitionType.RANGING_TO_TREND
        elif current_regime in ("bull", "bear") and target_regime == "ranging":
            return RegimeTransitionType.TREND_TO_RANGING
        else:
            return RegimeTransitionType.REGIME_SHIFT

    def _calculate_initial_adjustments(
        self, strategy: RegimeAdaptationStrategy
    ) -> dict[str, float]:
        """Calculate initial parameter adjustments."""
        return dict(strategy.position_adjustments)

    def _calculate_progressive_adjustments(
        self, strategy: RegimeAdaptationStrategy, progress: float
    ) -> dict[str, float]:
        """Calculate parameter adjustments based on transition progress."""
        adjustments = {}

        for key, target_value in strategy.position_adjustments.items():
            adjustments[key] = target_value * progress

        for key, target_value in strategy.risk_adjustments.items():
            # Risk adjustments are applied more conservatively
            base_value = 1.0
            adjustment = (target_value - base_value) * progress * 0.5  # More conservative
            adjustments[f"risk_{key}"] = base_value + adjustment

        return adjustments

    def _create_neutral_state(self, regime: str, timestamp_ns: int) -> SmoothTransitionState:
        """Create a neutral state (no active transition)."""
        return SmoothTransitionState(
            current_regime=regime,
            target_regime=regime,
            transition_progress=1.0,
            adaptation_speed=0.0,
            signal_confidence=1.0,
            estimated_completion_bars=0,
            active_adjustments={},
            timestamp_ns=timestamp_ns,
        )

    def get_current_adjustments(self) -> dict[str, float]:
        """Get current parameter adjustments."""
        if not self._current_state:
            return {}
        return self._current_state.active_adjustments

    def is_in_transition(self) -> bool:
        """Check if currently in a regime transition."""
        return self._current_state and self._current_state.transition_progress < 1.0


__all__ = [
    "RegimeTransitionType",
    "RegimeTransitionSignal",
    "RegimeAdaptationStrategy",
    "SmoothTransitionState",
    "RegimeTransitionPredictor",
    "SmoothRegimeAdapter",
]
