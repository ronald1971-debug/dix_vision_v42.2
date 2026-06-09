"""
cognitive_engine.hypothesis_engine.auto_generator
DIX VISION v42.2 — Automated Hypothesis Generation

Automatically generates testable hypotheses from detected patterns, anomalies,
and market behavior. Enables continuous learning and adaptation.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from cognitive_engine.hypothesis_engine.hypothesis import Hypothesis, HypothesisStatus
from cognitive_engine.hypothesis_engine.hypothesis_tracker import HypothesisTracker
from system.time_source import now

logger = logging.getLogger(__name__)


@dataclass
class Anomaly:
    """Detected anomaly that may warrant hypothesis generation."""
    
    anomaly_type: str  # "price_spike" | "volume_anomaly" | "sentiment_divergence" | "correlation_break"
    asset: str
    severity: float  # 0.0 to 1.0
    description: str
    timestamp: str
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class HypothesisAutoGenerator:
    """Automatically generates hypotheses from detected patterns and anomalies.
    
    Enables continuous learning by:
    - Detecting anomalies and patterns in market data
    - Generating testable hypotheses
    - Automatically validating hypotheses using backtesting
    - Learning from validated/invalidated hypotheses
    """

    def __init__(self, hypothesis_tracker: HypothesisTracker) -> None:
        self._tracker = hypothesis_tracker
        self._anomalies: list[Anomaly] = []
        self._generation_count = 0
        self._last_generation_time = None

    def generate_from_anomalies(self, anomalies: list[Anomaly]) -> list[Hypothesis]:
        """Generate hypotheses from detected anomalies.
        
        Each anomaly triggers hypothesis generation about:
        - Causal relationships
        - Predictive patterns
        - Market inefficiencies
        - Strategy improvements
        """
        hypotheses = []
        
        for anomaly in anomalies:
            try:
                # Generate hypothesis based on anomaly type
                hypothesis = self._create_hypothesis_from_anomaly(anomaly)
                
                if hypothesis:
                    self._tracker.propose(hypothesis)
                    hypotheses.append(hypothesis)
                    self._generation_count += 1
                    
                    logger.info(
                        f"[HYP_AUTO] Generated hypothesis from {anomaly.anomaly_type}: "
                        f"{hypothesis.statement[:50]}..."
                    )
                    
            except Exception as e:
                logger.error(f"[HYP_AUTO] Failed to generate hypothesis from anomaly: {e}")
        
        self._last_generation_time = now().utc_time.isoformat()
        return hypotheses

    def generate_from_pattern(self, pattern_data: dict[str, Any]) -> Hypothesis | None:
        """Generate hypothesis from detected pattern.
        
        Patterns can include:
        - Recurring price movements
        - Volume patterns
        - Sentiment cycles
        - Cross-asset relationships
        """
        try:
            pattern_type = pattern_data.get("type", "unknown")
            description = pattern_data.get("description", "")
            confidence = pattern_data.get("confidence", 0.5)
            
            # Generate hypothesis statement
            statement = self._generate_pattern_statement(pattern_type, description)
            
            if not statement:
                return None
            
            hypothesis = Hypothesis(
                statement=statement,
                domain="pattern_analysis",
                confidence=confidence,
                metadata={
                    "pattern_type": pattern_type,
                    "pattern_data": pattern_data,
                    "source": "auto_generator",
                    "generation_method": "pattern_detection"
                }
            )
            
            self._tracker.propose(hypothesis)
            self._generation_count += 1
            
            logger.info(f"[HYP_AUTO] Generated hypothesis from pattern: {statement[:50]}...")
            
            return hypothesis
            
        except Exception as e:
            logger.error(f"[HYP_AUTO] Failed to generate hypothesis from pattern: {e}")
            return None

    def generate_from_performance(self, performance_data: dict[str, Any]) -> list[Hypothesis]:
        """Generate hypotheses from strategy performance data.
        
        Identifies:
        - Underperforming strategies
        - Overperforming strategies
        - Market condition dependencies
        - Execution quality issues
        """
        hypotheses = []
        
        try:
            strategy = performance_data.get("strategy", "unknown")
            performance = performance_data.get("performance", {})
            sharpe_ratio = performance.get("sharpe_ratio", 0.0)
            max_drawdown = performance.get("max_drawdown", 0.0)
            
            # Generate hypotheses based on performance metrics
            if sharpe_ratio < 1.0:
                hyp = Hypothesis(
                    statement=f"Strategy {strategy} underperforms in current market conditions",
                    domain="performance_analysis",
                    confidence=0.7,
                    evidence=(f"Sharpe ratio {sharpe_ratio:.2f} below threshold 1.0",),
                    metadata={
                        "strategy": strategy,
                        "performance_data": performance_data,
                        "source": "auto_generator"
                    }
                )
                self._tracker.propose(hyp)
                hypotheses.append(hyp)
                self._generation_count += 1
            
            if max_drawdown > 0.1:
                hyp = Hypothesis(
                    statement=f"Strategy {strategy} experiences excessive drawdown during stress periods",
                    domain="risk_analysis",
                    confidence=0.8,
                    evidence=(f"Max drawdown {max_drawdown:.2%} exceeds 10% threshold",),
                    metadata={
                        "strategy": strategy,
                        "performance_data": performance_data,
                        "source": "auto_generator"
                    }
                )
                self._tracker.propose(hyp)
                hypotheses.append(hyp)
                self._generation_count += 1
            
            self._last_generation_time = now().utc_time.isoformat()
            
        except Exception as e:
            logger.error(f"[HYP_AUTO] Failed to generate hypotheses from performance: {e}")
        
        return hypotheses

    def _create_hypothesis_from_anomaly(self, anomaly: Anomaly) -> Hypothesis | None:
        """Create a hypothesis from a detected anomaly."""
        
        anomaly_type = anomaly.anomaly_type
        asset = anomaly.asset
        severity = anomaly.severity
        
        if anomaly_type == "price_spike":
            statement = f"Price spikes in {asset} predict subsequent mean reversion within 24 hours"
            domain = "price_action"
            confidence = severity * 0.8
            
        elif anomaly_type == "volume_anomaly":
            statement = f"Volume anomalies in {asset} precede directional price movements"
            domain = "volume_analysis"
            confidence = severity * 0.7
            
        elif anomaly_type == "sentiment_divergence":
            statement = f"Sentiment divergence in {asset} signals regime change"
            domain = "sentiment_analysis"
            confidence = severity * 0.9
            
        elif anomaly_type == "correlation_break":
            statement = f"Correlation breakdowns involving {asset} indicate market stress"
            domain = "correlation_analysis"
            confidence = severity * 0.85
            
        else:
            # Generic hypothesis for unknown anomaly types
            statement = f"Anomaly type '{anomaly_type}' in {asset} has predictive value for future price action"
            domain = "anomaly_analysis"
            confidence = severity * 0.6
        
        if not statement or confidence < 0.5:
            return None
        
        hypothesis = Hypothesis(
            statement=statement,
            domain=domain,
            confidence=confidence,
            evidence=(anomaly.description,),
            metadata={
                "anomaly_type": anomaly_type,
                "asset": asset,
                "severity": severity,
                "anomaly_metadata": anomaly.metadata,
                "source": "auto_generator"
            }
        )
        
        # Automatically transition to testing if confidence is high
        if confidence > 0.8:
            hypothesis.transition_to_testing()
        
        return hypothesis

    def _generate_pattern_statement(self, pattern_type: str, description: str) -> str:
        """Generate hypothesis statement from pattern data."""
        
        if pattern_type == "reversal_pattern":
            return f"Reversal patterns as described ('{description}') predict successful counter-trend trades"
        
        elif pattern_type == "trend_continuation":
            return f"Trend continuation patterns ('{description}') predict sustained directional movement"
        
        elif pattern_type == "volatility_regime":
            return f"Volatility regime patterns ('{description}') predict optimal position sizing adjustments"
        
        elif pattern_type == "session_pattern":
            return f"Session-based patterns ('{description}') have predictive value for intraday performance"
        
        else:
            return f"Pattern type '{pattern_type}' ('{description}') has predictive value for trading decisions"

    def validate_with_backtest(self, hypothesis: Hypothesis, backtest_results: dict[str, Any]) -> bool:
        """Validate a hypothesis using backtesting results."""
        
        try:
            # Extract key metrics from backtest results
            total_return = backtest_results.get("total_return", 0.0)
            sharpe_ratio = backtest_results.get("sharpe_ratio", 0.0)
            max_drawdown = backtest_results.get("max_drawdown", 1.0)
            
            # Validation criteria
            is_profitable = total_return > 0.0
            has_acceptable_risk = max_drawdown < 0.2  # Less than 20% drawdown
            has_good_risk_reward = sharpe_ratio > 1.0
            
            # Determine validation outcome
            if is_profitable and has_acceptable_risk and has_good_risk_reward:
                hypothesis.validate()
                hypothesis.add_evidence(f"Backtest validated: return={total_return:.2%}, sharpe={sharpe_ratio:.2f}")
                logger.info(f"[HYP_AUTO] Hypothesis validated: {hypothesis.statement[:50]}...")
                return True
            else:
                hypothesis.invalidate()
                hypothesis.add_evidence(f"Backtest rejected: return={total_return:.2%}, sharpe={sharpe_ratio:.2f}")
                logger.info(f"[HYP_AUTO] Hypothesis invalidated: {hypothesis.statement[:50]}...")
                return False
                
        except Exception as e:
            logger.error(f"[HYP_AUTO] Failed to validate hypothesis with backtest: {e}")
            return False

    def get_statistics(self) -> dict[str, Any]:
        """Get auto-generation statistics."""
        active_hypotheses = len(self._tracker.get_all()) if self._tracker else 0
        validated_hypotheses = len([h for h in self._tracker.get_all() if h.status == HypothesisStatus.VALIDATED]) if self._tracker else 0
        
        return {
            "generation_count": self._generation_count,
            "last_generation_time": self._last_generation_time,
            "active_hypotheses": active_hypotheses,
            "validated_hypotheses": validated_hypotheses,
            "anomalies_detected": len(self._anomalies),
        }


def get_auto_generator(hypothesis_tracker: HypothesisTracker) -> HypothesisAutoGenerator:
    """Get or create auto-generator for hypothesis engine."""
    return HypothesisAutoGenerator(hypothesis_tracker)


__all__ = [
    "Anomaly",
    "HypothesisAutoGenerator",
    "get_auto_generator",
]