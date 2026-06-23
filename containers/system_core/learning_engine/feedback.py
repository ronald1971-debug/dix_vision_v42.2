"""Feedback Loops – connects trade outcomes back to the cognitive pipeline.

Learning updates beliefs without mutating governance.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from learning_engine.attribution import Attribution, AttributionEngine
from learning_engine.error_analysis import ErrorAnalyzer
from mind.beliefs import BeliefSystem


@dataclass
class FeedbackSignal:
    signal_type: str = ""  # reinforce | weaken | invalidate
    target_belief_id: str = ""
    confidence_delta: float = 0.0
    reason: str = ""
    timestamp: float = field(default_factory=time.time)


class FeedbackLoop:
    """Connects outcomes back to the belief and hypothesis systems.

    Key rule: Learning updates beliefs but NEVER mutates governance policies.
    """

    def __init__(
        self,
        attribution_engine: AttributionEngine,
        error_analyzer: ErrorAnalyzer,
        belief_system: BeliefSystem,
    ) -> None:
        self._attribution = attribution_engine
        self._errors = error_analyzer
        self._beliefs = belief_system
        self._signals: list[FeedbackSignal] = []

    def process_attribution(self, attribution: Attribution) -> list[FeedbackSignal]:
        signals: list[FeedbackSignal] = []

        for belief_id, pnl_share in attribution.attribution_factors.items():
            if pnl_share > 0:
                signal = FeedbackSignal(
                    signal_type="reinforce",
                    target_belief_id=belief_id,
                    confidence_delta=min(0.1, pnl_share / 100),
                    reason=f"Positive PnL from trade {attribution.trade_id}",
                )
            else:
                signal = FeedbackSignal(
                    signal_type="weaken",
                    target_belief_id=belief_id,
                    confidence_delta=max(-0.2, pnl_share / 100),
                    reason=f"Negative PnL from trade {attribution.trade_id}",
                )
            signals.append(signal)

        self._signals.extend(signals)
        return signals

    def apply_signals(self, signals: list[FeedbackSignal]) -> int:
        """Apply feedback signals to the belief system."""
        applied = 0
        for signal in signals:
            beliefs = self._beliefs.get_beliefs()
            for belief in beliefs:
                if belief.belief_id == signal.target_belief_id:
                    new_conf = belief.confidence + signal.confidence_delta
                    self._beliefs.update_belief(belief.belief_id, new_conf)
                    applied += 1
                    break
        return applied

    def run_feedback_cycle(self) -> int:
        """Process all pending attributions and apply feedback."""
        total_applied = 0
        for attr in self._attribution.get_attributions():
            signals = self.process_attribution(attr)
            total_applied += self.apply_signals(signals)
        return total_applied

    def get_signals(self) -> list[FeedbackSignal]:
        return list(self._signals)


# Export for import compatibility
FeedbackEngine = FeedbackLoop
