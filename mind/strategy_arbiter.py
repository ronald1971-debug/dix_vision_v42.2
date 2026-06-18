"""
Strategy Arbiter - Real Implementation

Provides real strategy selection and arbitration logic for the DIX VISION system,
including conflict resolution, signal combination, and multi-strategy portfolio management.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class ArbitrationMode(Enum):
    """Modes for strategy arbitration."""
    WEIGHTED_AVERAGE = "weighted_average"
    MAJORITY_VOTE = "majority_vote"
    BEST_PERFORMANCE = "best_performance"
    HIGHEST_CONFIDENCE = "highest_confidence"
    RISK_ADJUSTED = "risk_adjusted"
    ENSEMBLE = "ensemble"


class ConflictResolution(Enum):
    """Methods for resolving conflicting signals."""
    PRIORITY = "priority"  # Use highest priority strategy
    VOTE = "vote"  # Use majority vote
    CONFIDENCE = "confidence"  # Use highest confidence
    CANCEL = "cancel"  # Cancel conflicting signals
    COMBINE = "combine"  # Combine signals with weights


@dataclass
class StrategyWeight:
    """Weight assigned to a strategy for arbitration."""
    strategy_id: str
    weight: float  # 0.0 to 1.0
    priority: int  # Lower number = higher priority
    enabled: bool = True
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ArbitrationResult:
    """Result of strategy arbitration."""
    final_signal: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0.0 to 1.0
    contributing_strategies: List[str]
    weights_used: Dict[str, float]
    conflict_resolution: str
    timestamp: datetime = field(default_factory=datetime.now)
    rejected_signals: List[Dict[str, Any]] = field(default_factory=list)


class StrategyArbiter:
    """Real strategy arbiter with conflict resolution and signal combination."""
    
    def __init__(self, arbiter_id: str = "default_arbiter"):
        self._arbiter_id = arbiter_id
        self._arbitration_mode = ArbitrationMode.WEIGHTED_AVERAGE
        self._conflict_resolution = ConflictResolution.CONFIDENCE
        
        # Strategy weights and priorities
        self._strategy_weights: Dict[str, StrategyWeight] = {}
        
        # Performance tracking for adaptive arbitration
        self._strategy_performance: Dict[str, Dict[str, float]] = {}
        
        # Signal history
        self._signal_history: List[Dict[str, Any]] = []
        
        # Conflict statistics
        self._conflict_stats = {
            "total_arbitrations": 0,
            "conflicts_detected": 0,
            "resolutions": {
                "priority": 0,
                "vote": 0,
                "confidence": 0,
                "cancel": 0,
                "combine": 0
            }
        }
        
        logger.info(f"[STRATEGY_ARBITER] Strategy arbiter initialized: {arbiter_id}")
    
    def set_arbitration_mode(self, mode: ArbitrationMode) -> None:
        """Set the arbitration mode."""
        self._arbitration_mode = mode
        logger.info(f"[STRATEGY_ARBITER] Arbitration mode set to: {mode.value}")
    
    def set_conflict_resolution(self, resolution: ConflictResolution) -> None:
        """Set the conflict resolution method."""
        self._conflict_resolution = resolution
        logger.info(f"[STRATEGY_ARBITER] Conflict resolution set to: {resolution.value}")
    
    def set_strategy_weight(self, strategy_id: str, weight: float, 
                           priority: int = 100) -> None:
        """Set weight and priority for a strategy."""
        self._strategy_weights[strategy_id] = StrategyWeight(
            strategy_id=strategy_id,
            weight=max(0.0, min(1.0, weight)),
            priority=priority
        )
        logger.info(f"[STRATEGY_ARBITER] Set weight for {strategy_id}: {weight:.2f}, priority: {priority}")
    
    def update_strategy_performance(self, strategy_id: str, 
                                   performance_metrics: Dict[str, float]) -> None:
        """Update performance metrics for a strategy."""
        self._strategy_performance[strategy_id] = performance_metrics
        logger.debug(f"[STRATEGY_ARBITER] Updated performance for {strategy_id}")
    
    def arbitrate_signals(self, signals: List[Dict[str, Any]]) -> ArbitrationResult:
        """Arbitrate between multiple strategy signals.
        
        Args:
            signals: List of signal dictionaries with keys:
                - strategy_id: str
                - signal_type: str ("BUY", "SELL", "HOLD")
                - confidence: float
                - symbol: str
        
        Returns:
            ArbitrationResult with the final decision
        """
        self._conflict_stats["total_arbitrations"] += 1
        
        if not signals:
            return ArbitrationResult(
                final_signal="HOLD",
                confidence=0.0,
                contributing_strategies=[],
                weights_used={},
                conflict_resolution="no_signals"
            )
        
        # Group signals by type
        buy_signals = [s for s in signals if s.get("signal_type") == "BUY"]
        sell_signals = [s for s in signals if s.get("signal_type") == "SELL"]
        hold_signals = [s for s in signals if s.get("signal_type") == "HOLD"]
        
        # Detect conflicts
        has_conflict = (len(buy_signals) > 0 and len(sell_signals) > 0)
        
        if has_conflict:
            self._conflict_stats["conflicts_detected"] += 1
            return self._resolve_conflict(signals, buy_signals, sell_signals, hold_signals)
        
        # No conflict, use arbitration mode
        if buy_signals:
            return self._arbitrate_no_conflict(buy_signals, "BUY")
        elif sell_signals:
            return self._arbitrate_no_conflict(sell_signals, "SELL")
        else:
            return self._arbitrate_no_conflict(hold_signals, "HOLD")
    
    def _resolve_conflict(self, all_signals: List[Dict[str, Any]], 
                         buy_signals: List[Dict[str, Any]],
                         sell_signals: List[Dict[str, Any]],
                         hold_signals: List[Dict[str, Any]]) -> ArbitrationResult:
        """Resolve conflicting signals based on resolution method."""
        resolution = self._conflict_resolution
        self._conflict_stats["resolutions"][resolution.value] += 1
        
        if resolution == ConflictResolution.PRIORITY:
            return self._resolve_by_priority(all_signals)
        elif resolution == ConflictResolution.VOTE:
            return self._resolve_by_vote(buy_signals, sell_signals, hold_signals)
        elif resolution == ConflictResolution.CONFIDENCE:
            return self._resolve_by_confidence(all_signals)
        elif resolution == ConflictResolution.CANCEL:
            return self._resolve_by_cancel(all_signals, buy_signals, sell_signals)
        elif resolution == ConflictResolution.COMBINE:
            return self._resolve_by_combine(all_signals)
        else:
            return self._resolve_by_confidence(all_signals)
    
    def _resolve_by_priority(self, signals: List[Dict[str, Any]]) -> ArbitrationResult:
        """Resolve conflict by selecting highest priority strategy."""
        sorted_signals = sorted(
            signals,
            key=lambda s: self._strategy_weights.get(s["strategy_id"], StrategyWeight(s["strategy_id"], 0.5, 100)).priority
        )
        
        selected_signal = sorted_signals[0]
        
        return ArbitrationResult(
            final_signal=selected_signal["signal_type"],
            confidence=selected_signal["confidence"],
            contributing_strategies=[selected_signal["strategy_id"]],
            weights_used={selected_signal["strategy_id"]: 1.0},
            conflict_resolution="priority"
        )
    
    def _resolve_by_vote(self, buy_signals: List[Dict[str, Any]], 
                       sell_signals: List[Dict[str, Any]],
                       hold_signals: List[Dict[str, Any]]) -> ArbitrationResult:
        """Resolve conflict by majority vote."""
        buy_count = len(buy_signals)
        sell_count = len(sell_signals)
        hold_count = len(hold_signals)
        
        # Find majority
        max_count = max(buy_count, sell_count, hold_count)
        
        if max_count == buy_count:
            selected_signals = buy_signals
            final_signal = "BUY"
        elif max_count == sell_count:
            selected_signals = sell_signals
            final_signal = "SELL"
        else:
            selected_signals = hold_signals
            final_signal = "HOLD"
        
        # Average confidence
        avg_confidence = np.mean([s["confidence"] for s in selected_signals])
        
        # Equal weights for voting
        weights = {s["strategy_id"]: 1.0 / len(selected_signals) for s in selected_signals}
        
        return ArbitrationResult(
            final_signal=final_signal,
            confidence=avg_confidence,
            contributing_strategies=[s["strategy_id"] for s in selected_signals],
            weights_used=weights,
            conflict_resolution="vote"
        )
    
    def _resolve_by_confidence(self, signals: List[Dict[str, Any]]) -> ArbitrationResult:
        """Resolve conflict by selecting highest confidence signal."""
        sorted_signals = sorted(signals, key=lambda s: s.get("confidence", 0.0), reverse=True)
        selected_signal = sorted_signals[0]
        
        return ArbitrationResult(
            final_signal=selected_signal["signal_type"],
            confidence=selected_signal["confidence"],
            contributing_strategies=[selected_signal["strategy_id"]],
            weights_used={selected_signal["strategy_id"]: 1.0},
            conflict_resolution="confidence"
        )
    
    def _resolve_by_cancel(self, all_signals: List[Dict[str, Any]],
                         buy_signals: List[Dict[str, Any]],
                         sell_signals: List[Dict[str, Any]]) -> ArbitrationResult:
        """Cancel conflicting signals and default to HOLD."""
        rejected = all_signals.copy()
        
        return ArbitrationResult(
            final_signal="HOLD",
            confidence=0.0,
            contributing_strategies=[],
            weights_used={},
            conflict_resolution="cancel",
            rejected_signals=rejected
        )
    
    def _resolve_by_combine(self, signals: List[Dict[str, Any]]) -> ArbitrationResult:
        """Combine signals using weighted average."""
        # Calculate weights based on strategy weights
        weights = {}
        total_weight = 0.0
        
        for signal in signals:
            strategy_id = signal["strategy_id"]
            weight = self._strategy_weights.get(strategy_id, StrategyWeight(strategy_id, 0.5, 100)).weight
            weights[strategy_id] = weight
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        # Calculate weighted signal
        buy_weight = sum(weights.get(s["strategy_id"], 0.0) for s in signals if s["signal_type"] == "BUY")
        sell_weight = sum(weights.get(s["strategy_id"], 0.0) for s in signals if s["signal_type"] == "SELL")
        hold_weight = sum(weights.get(s["strategy_id"], 0.0) for s in signals if s["signal_type"] == "HOLD")
        
        # Determine final signal
        if buy_weight > sell_weight and buy_weight > hold_weight:
            final_signal = "BUY"
            confidence = buy_weight
        elif sell_weight > buy_weight and sell_weight > hold_weight:
            final_signal = "SELL"
            confidence = sell_weight
        else:
            final_signal = "HOLD"
            confidence = max(buy_weight, sell_weight, hold_weight)
        
        return ArbitrationResult(
            final_signal=final_signal,
            confidence=confidence,
            contributing_strategies=list(weights.keys()),
            weights_used=weights,
            conflict_resolution="combine"
        )
    
    def _arbitrate_no_conflict(self, signals: List[Dict[str, Any]], 
                              signal_type: str) -> ArbitrationResult:
        """Arbitrate when there's no conflict (all signals agree)."""
        if self._arbitration_mode == ArbitrationMode.WEIGHTED_AVERAGE:
            return self._weighted_average_arbitration(signals)
        elif self._arbitration_mode == ArbitrationMode.HIGHEST_CONFIDENCE:
            return self._highest_confidence_arbitration(signals)
        elif self._arbitration_mode == ArbitrationMode.BEST_PERFORMANCE:
            return self._best_performance_arbitration(signals)
        else:
            return self._weighted_average_arbitration(signals)
    
    def _weighted_average_arbitration(self, signals: List[Dict[str, Any]]) -> ArbitrationResult:
        """Use weighted average of confidences."""
        total_weight = 0.0
        weighted_confidence = 0.0
        weights = {}
        
        for signal in signals:
            strategy_id = signal["strategy_id"]
            weight = self._strategy_weights.get(strategy_id, StrategyWeight(strategy_id, 0.5, 100)).weight
            confidence = signal["confidence"]
            
            weights[strategy_id] = weight
            weighted_confidence += weight * confidence
            total_weight += weight
        
        final_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.0
        
        return ArbitrationResult(
            final_signal=signals[0]["signal_type"],
            confidence=final_confidence,
            contributing_strategies=[s["strategy_id"] for s in signals],
            weights_used=weights,
            conflict_resolution="none"
        )
    
    def _highest_confidence_arbitration(self, signals: List[Dict[str, Any]]) -> ArbitrationResult:
        """Select signal with highest confidence."""
        best_signal = max(signals, key=lambda s: s.get("confidence", 0.0))
        
        return ArbitrationResult(
            final_signal=best_signal["signal_type"],
            confidence=best_signal["confidence"],
            contributing_strategies=[best_signal["strategy_id"]],
            weights_used={best_signal["strategy_id"]: 1.0},
            conflict_resolution="none"
        )
    
    def _best_performance_arbitration(self, signals: List[Dict[str, Any]]) -> ArbitrationResult:
        """Select signal from best performing strategy."""
        best_signal = None
        best_performance = float('-inf')
        
        for signal in signals:
            strategy_id = signal["strategy_id"]
            performance = self._strategy_performance.get(strategy_id, {}).get("total_return", 0.0)
            
            if performance > best_performance:
                best_performance = performance
                best_signal = signal
        
        if best_signal:
            return ArbitrationResult(
                final_signal=best_signal["signal_type"],
                confidence=best_signal["confidence"],
                contributing_strategies=[best_signal["strategy_id"]],
                weights_used={best_signal["strategy_id"]: 1.0},
                conflict_resolution="none"
            )
        
        # Fallback to highest confidence
        return self._highest_confidence_arbitration(signals)
    
    def get_arbitration_statistics(self) -> Dict[str, Any]:
        """Get arbitration statistics."""
        return {
            "arbitration_mode": self._arbitration_mode.value,
            "conflict_resolution": self._conflict_resolution.value,
            "total_arbitrations": self._conflict_stats["total_arbitrations"],
            "conflicts_detected": self._conflict_stats["conflicts_detected"],
            "conflict_rate": (
                self._conflict_stats["conflicts_detected"] / self._conflict_stats["total_arbitrations"]
                if self._conflict_stats["total_arbitrations"] > 0 else 0.0
            ),
            "resolutions_used": self._conflict_stats["resolutions"],
            "registered_strategies": len(self._strategy_weights)
        }
    
    def get_strategy_weights(self) -> Dict[str, StrategyWeight]:
        """Get all strategy weights."""
        return self._strategy_weights.copy()


# Global strategy arbiter instance
_default_strategy_arbiter = None


def get_arbiter(arbiter_id: str = "default_arbiter", **kwargs: Any) -> StrategyArbiter:
    """Get or create a strategy arbiter instance.
    
    Args:
        arbiter_id: Unique identifier for the arbiter
        **kwargs: Additional configuration parameters
        
    Returns:
        StrategyArbiter instance
    """
    global _default_strategy_arbiter
    
    if _default_strategy_arbiter is None or _default_strategy_arbiter._arbiter_id != arbiter_id:
        _default_strategy_arbiter = StrategyArbiter(arbiter_id)
    
    return _default_strategy_arbiter


__all__ = [
    "ArbitrationMode",
    "ConflictResolution",
    "StrategyWeight",
    "ArbitrationResult",
    "StrategyArbiter",
    "get_arbiter"
]