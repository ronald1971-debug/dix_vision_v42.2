"""Execution Feedback Integration — INT-07.03.

Integration system for execution feedback into the intelligence engine.
Captures execution results, trade outcomes, and performance metrics
to provide feedback for strategy improvement and learning.
"""

from __future__ import annotations

import dataclasses
import enum
from collections import deque
from collections.abc import Callable
from decimal import Decimal
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_FEEDBACK_BUFFER_SIZE: Final[int] = 1000
DEFAULT_ENABLE_REAL_TIME_FEEDBACK: Final[bool] = True
DEFAULT_FEEDBACK_AGGREGATION_WINDOW_MS: Final[int] = 5000
DEFAULT_ENABLE_PERFORMANCE_ANALYSIS: Final[bool] = True

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ExecutionFeedbackType(enum.Enum):
    """Types of execution feedback."""
    ORDER_FILLED = "ORDER_FILLED"
    ORDER_PARTIALLY_FILLED = "ORDER_PARTIALLY_FILLED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_REJECTED = "ORDER_REJECTED"
    SLIPPAGE = "SLIPPAGE"
    LATENCY = "LATENCY"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    MARKET_IMPACT = "MARKET_IMPACT"
    PORTFOLIO_IMPACT = "PORTFOLIO_IMPACT"


class FeedbackCategory(enum.Enum):
    """Categories of execution feedback."""
    POSITIVE = "POSITIVE"  - Successful execution
    NEGATIVE = "NEGATIVE"  - Failed or poor execution
    NEUTRAL = "NEUTRAL"  - Normal execution
    WARNING = "WARNING"  - Potential issues


class FeedbackUrgency(enum.Enum):
    """Urgency levels for feedback processing."""
    IMMEDIATE = "IMMEDIATE"  - Process immediately
    HIGH = "HIGH"  - Process within next batch
    NORMAL = "NORMAL"  - Standard processing
    LOW = "LOW"  - Defer processing


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class FeedbackIntegrationConfig:
    """Configuration for execution feedback integration."""
    feedback_buffer_size: int = DEFAULT_FEEDBACK_BUFFER_SIZE
    enable_real_time_feedback: bool = DEFAULT_ENABLE_REAL_TIME_FEEDBACK
    feedback_aggregation_window_ms: int = DEFAULT_FEEDBACK_AGGREGATION_WINDOW_MS
    enable_performance_analysis: bool = DEFAULT_ENABLE_PERFORMANCE_ANALYSIS
    enable_anomaly_detection: bool = True
    enable_trend_analysis: bool = True

    def __post_init__(self) -> None:
        if self.feedback_buffer_size < 1:
            raise ValueError("feedback_buffer_size must be >= 1")
        if self.feedback_aggregation_window_ms < 1:
            raise ValueError("feedback_aggregation_window_ms must be >= 1")


@dataclasses.dataclass(frozen=True, slots=True)
class ExecutionFeedback:
    """Feedback from execution engine."""
    feedback_id: str
    feedback_type: ExecutionFeedbackType
    category: FeedbackCategory
    urgency: FeedbackUrgency
    order_id: str
    strategy_id: str
    symbol: str
    timestamp_ns: int
    execution_details: dict[str, Any]
    performance_metrics: dict[str, Any]
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.feedback_id:
            raise ValueError("feedback_id must be non-empty")
        if not self.order_id:
            raise ValueError("order_id must be non-empty")
        if not self.strategy_id:
            raise ValueError("strategy_id must be non-empty")
        if not self.symbol:
            raise ValueError("symbol must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class ExecutionMetrics:
    """Execution performance metrics."""
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_fill_rate: float
    average_slippage_pct: float
    average_latency_ms: float
    total_volume: Decimal
    total_fees: Decimal
    total_pnl: Decimal
    sharpe_ratio: float
    max_drawdown: float


@dataclasses.dataclass(frozen=True, slots=True)
class StrategyPerformance:
    """Performance metrics for a specific strategy."""
    strategy_id: str
    total_orders: int
    filled_orders: int
    fill_rate: float
    average_slippage_pct: float
    total_pnl: Decimal
    win_rate: float
    average_win: Decimal
    average_loss: Decimal
    profit_factor: float
    max_consecutive_wins: int
    max_consecutive_losses: int
    last_updated_ns: int


@dataclasses.dataclass(frozen=True, slots=True)
class FeedbackAggregation:
    """Aggregated feedback over a time window."""
    aggregation_id: str
    window_start_ns: int
    window_end_ns: int
    strategy_id: str
    feedback_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    average_performance: float
    trends: dict[str, Any]
    anomalies: list[dict[str, Any]]
    recommendations: list[str]


@dataclasses.dataclass(frozen=True, slots=True)
class IntegrationMetrics:
    """Metrics about the feedback integration system."""
    total_feedback: int
    feedback_by_type: dict[str, int]
    feedback_by_category: dict[str, int]
    feedback_processed: int
    feedback_pending: int
    average_processing_time_ms: float
    strategies_tracked: int
    aggregations_generated: int
    anomalies_detected: int


# ---------------------------------------------------------------------------
# Execution Feedback Integrator
# ---------------------------------------------------------------------------


class ExecutionFeedbackIntegrator:
    """Execution feedback integration system.
    
    Integrates execution feedback into the intelligence engine
    for strategy improvement and learning. Captures execution
    results, performance metrics, and provides actionable insights.
    """
    
    def __init__(
        self,
        config: FeedbackIntegrationConfig | None = None,
    ) -> None:
        """Initialize the execution feedback integrator.
        
        Args:
            config: Integration configuration
        """
        self._config = config or FeedbackIntegrationConfig()
        self._lock = Lock()
        
        # Feedback buffer
        self._feedback_buffer: deque[ExecutionFeedback] = deque(
            maxlen=self._config.feedback_buffer_size
        )
        
        # Strategy performance tracking
        self._strategy_performance: dict[str, StrategyPerformance] = {}
        self._execution_history: dict[str, list[ExecutionFeedback]] = {}  # strategy_id -> feedback
        
        # Aggregations
        self._aggregations: list[FeedbackAggregation] = []
        
        # Metrics
        self._metrics = self._init_metrics()
        self._processing_times: deque[int] = deque(maxlen=100)
    
    def add_feedback(
        self,
        feedback: ExecutionFeedback,
    ) -> None:
        """Add execution feedback to the integrator.
        
        Args:
            feedback: Execution feedback
        """
        import time
        
        start_ms = int(time.time() * 1000)
        
        with self._lock:
            self._feedback_buffer.append(feedback)
            self._metrics.total_feedback += 1
            self._metrics.feedback_by_type[feedback.feedback_type.value] = \
                self._metrics.feedback_by_type.get(feedback.feedback_type.value, 0) + 1
            self._metrics.feedback_by_category[feedback.category.value] = \
                self._metrics.feedback_by_category.get(feedback.category.value, 0) + 1
            
            # Track strategy performance
            self._update_strategy_performance(feedback)
            
            # Track execution history
            if feedback.strategy_id not in self._execution_history:
                self._execution_history[feedback.strategy_id] = []
            self._execution_history[feedback.strategy_id].append(feedback)
        
        # Process immediately if real-time feedback enabled
        if self._config.enable_real_time_feedback and feedback.urgency == FeedbackUrgency.IMMEDIATE:
            self.process_feedback(feedback.feedback_id)
        
        # Track processing time
        processing_time_ms = int(time.time() * 1000) - start_ms
        self._processing_times.append(processing_time_ms)
        if len(self._processing_times) > 0:
            self._metrics.average_processing_time_ms = sum(self._processing_times) / len(self._processing_times)
    
    def process_feedback(
        self,
        feedback_id: str,
    ) -> dict[str, Any] | None:
        """Process a specific feedback item.
        
        Args:
            feedback_id: Feedback identifier
            
        Returns:
            Processing results or None if not found
        """
        with self._lock:
            feedback = self._find_feedback(feedback_id)
            if not feedback:
                return None
        
        # Analyze feedback
        analysis = self._analyze_feedback(feedback)
        
        # Detect anomalies if enabled
        anomalies = []
        if self._config.enable_anomaly_detection:
            anomalies = self._detect_anomalies(feedback)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(feedback, analysis, anomalies)
        
        self._metrics.feedback_processed += 1
        
        return {
            "feedback": feedback,
            "analysis": analysis,
            "anomalies": anomalies,
            "recommendations": recommendations,
        }
    
    def aggregate_feedback(
        self,
        strategy_id: str,
        window_ms: int | None = None,
    ) -> FeedbackAggregation | None:
        """Aggregate feedback over a time window.
        
        Args:
            strategy_id: Strategy identifier
            window_ms: Time window in milliseconds
            
        Returns:
            Aggregated feedback or None if no data
        """
        import secrets
        import time
        
        if window_ms is None:
            window_ms = self._config.feedback_aggregation_window_ms
        
        window_end_ns = time.time_ns()
        window_start_ns = window_end_ns - (window_ms * 1_000_000)
        
        with self._lock:
            feedback_list = self._execution_history.get(strategy_id, [])
            
            # Filter feedback within window
            window_feedback = [
                f for f in feedback_list
                if f.timestamp_ns >= window_start_ns and f.timestamp_ns <= window_end_ns
            ]
            
            if not window_feedback:
                return None
            
            # Calculate aggregation metrics
            positive_count = sum(1 for f in window_feedback if f.category == FeedbackCategory.POSITIVE)
            negative_count = sum(1 for f in window_feedback if f.category == FeedbackCategory.NEGATIVE)
            neutral_count = sum(1 for f in window_feedback if f.category == FeedbackCategory.NEUTRAL)
            
            # Calculate average performance
            performances = [
                f.performance_metrics.get("performance_score", 0.5)
                for f in window_feedback
                if "performance_score" in f.performance_metrics
            ]
            average_performance = sum(performances) / len(performances) if performances else 0.5
            
            # Analyze trends
            trends = self._analyze_trends(window_feedback) if self._config.enable_trend_analysis else {}
            
            # Detect anomalies
            anomalies = []
            if self._config.enable_anomaly_detection:
                anomalies = self._detect_aggregation_anomalies(window_feedback)
            
            # Generate recommendations
            recommendations = self._generate_aggregation_recommendations(
                window_feedback, positive_count, negative_count
            )
            
            aggregation = FeedbackAggregation(
                aggregation_id=secrets.token_hex(16),
                window_start_ns=window_start_ns,
                window_end_ns=window_end_ns,
                strategy_id=strategy_id,
                feedback_count=len(window_feedback),
                positive_count=positive_count,
                negative_count=negative_count,
                neutral_count=neutral_count,
                average_performance=average_performance,
                trends=trends,
                anomalies=anomalies,
                recommendations=recommendations,
            )
            
            self._aggregations.append(aggregation)
            self._metrics.aggregations_generated += 1
            
            return aggregation
    
    def get_strategy_performance(
        self,
        strategy_id: str,
    ) -> StrategyPerformance | None:
        """Get performance metrics for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Strategy performance or None if not found
        """
        with self._lock:
            return self._strategy_performance.get(strategy_id)
    
    def get_all_strategy_performance(self) -> dict[str, StrategyPerformance]:
        """Get performance metrics for all strategies.
        
        Returns:
            Dictionary of strategy IDs to performance
        """
        with self._lock:
            return dict(self._strategy_performance)
    
    def get_metrics(self) -> IntegrationMetrics:
        """Get integration metrics.
        
        Returns:
            Current metrics
        """
        with self._lock:
            self._metrics.feedback_pending = len(self._feedback_buffer) - self._metrics.feedback_processed
            self._metrics.strategies_tracked = len(self._strategy_performance)
            
            return self._metrics
    
    def _find_feedback(self, feedback_id: str) -> ExecutionFeedback | None:
        """Find feedback by ID.
        
        Args:
            feedback_id: Feedback identifier
            
        Returns:
            Feedback or None
        """
        for feedback in self._feedback_buffer:
            if feedback.feedback_id == feedback_id:
                return feedback
        return None
    
    def _update_strategy_performance(self, feedback: ExecutionFeedback) -> None:
        """Update strategy performance metrics.
        
        Args:
            feedback: Execution feedback
        """
        import time
        
        strategy_id = feedback.strategy_id
        
        if strategy_id not in self._strategy_performance:
            # Initialize performance tracking
            self._strategy_performance[strategy_id] = StrategyPerformance(
                strategy_id=strategy_id,
                total_orders=1,
                filled_orders=1 if feedback.category == FeedbackCategory.POSITIVE else 0,
                fill_rate=1.0 if feedback.category == FeedbackCategory.POSITIVE else 0.0,
                average_slippage_pct=feedback.performance_metrics.get("slippage_pct", 0.0),
                total_pnl=Decimal(str(feedback.performance_metrics.get("pnl", 0))),
                win_rate=1.0 if feedback.category == FeedbackCategory.POSITIVE else 0.0,
                average_win=Decimal(str(feedback.performance_metrics.get("pnl", 0))),
                average_loss=Decimal('0'),
                profit_factor=0.0,
                max_consecutive_wins=1 if feedback.category == FeedbackCategory.POSITIVE else 0,
                max_consecutive_losses=1 if feedback.category == FeedbackCategory.NEGATIVE else 0,
                last_updated_ns=time.time_ns(),
            )
            return
        
        # Update existing performance
        existing = self._strategy_performance[strategy_id]
        
        total_orders = existing.total_orders + 1
        filled_orders = existing.filled_orders + (1 if feedback.category == FeedbackCategory.POSITIVE else 0)
        fill_rate = filled_orders / total_orders
        
        # Update slippage (running average)
        current_slippage = feedback.performance_metrics.get("slippage_pct", 0.0)
        average_slippage = (existing.average_slippage_pct * existing.total_orders + current_slippage) / total_orders
        
        # Update PnL
        current_pnl = Decimal(str(feedback.performance_metrics.get("pnl", 0)))
        total_pnl = existing.total_pnl + current_pnl
        
        # Update win rate
        is_win = feedback.category == FeedbackCategory.POSITIVE
        if total_orders == 1:
            win_rate = 1.0 if is_win else 0.0
        else:
            win_rate = (existing.win_rate * (existing.total_orders - 1) + (1.0 if is_win else 0.0)) / total_orders
        
        # Update average win/loss
        if is_win:
            avg_win = (existing.average_win * (existing.total_orders - 1) + current_pnl) / existing.total_orders
            avg_loss = existing.average_loss
        else:
            avg_win = existing.average_win
            avg_loss = (existing.average_loss * (existing.total_orders - 1) + abs(current_pnl)) / existing.total_orders
        
        # Update profit factor
        total_wins = sum(
            Decimal(str(f.performance_metrics.get("pnl", 0)))
            for f in self._execution_history.get(strategy_id, [])
            if f.category == FeedbackCategory.POSITIVE
        )
        total_losses = sum(
            abs(Decimal(str(f.performance_metrics.get("pnl", 0))))
            for f in self._execution_history.get(strategy_id, [])
            if f.category == FeedbackCategory.NEGATIVE
        )
        profit_factor = float(total_wins / total_losses) if total_losses > 0 else 0.0
        
        self._strategy_performance[strategy_id] = StrategyPerformance(
            strategy_id=strategy_id,
            total_orders=total_orders,
            filled_orders=filled_orders,
            fill_rate=fill_rate,
            average_slippage_pct=average_slippage,
            total_pnl=total_pnl,
            win_rate=win_rate,
            average_win=avg_win,
            average_loss=avg_loss,
            profit_factor=profit_factor,
            max_consecutive_wins=existing.max_consecutive_wins + (1 if is_win else 0),
            max_consecutive_losses=existing.max_consecutive_losses + (0 if is_win else 1),
            last_updated_ns=time.time_ns(),
        )
    
    def _analyze_feedback(self, feedback: ExecutionFeedback) -> dict[str, Any]:
        """Analyze a feedback item.
        
        Args:
            feedback: Feedback to analyze
            
        Returns:
            Analysis results
        """
        analysis = {
            "category": feedback.category.value,
            "urgency": feedback.urgency.value,
            "timestamp": feedback.timestamp_ns,
        }
        
        # Analyze execution details
        if "fill_rate" in feedback.execution_details:
            analysis["fill_quality"] = "good" if feedback.execution_details["fill_rate"] > 0.9 else "poor"
        
        # Analyze performance metrics
        if "slippage_pct" in feedback.performance_metrics:
            slippage = feedback.performance_metrics["slippage_pct"]
            if slippage < 0.1:
                analysis["slippage_assessment"] = "excellent"
            elif slippage < 0.5:
                analysis["slippage_assessment"] = "good"
            elif slippage < 1.0:
                analysis["slippage_assessment"] = "fair"
            else:
                analysis["slippage_assessment"] = "poor"
        
        return analysis
    
    def _detect_anomalies(self, feedback: ExecutionFeedback) -> list[dict[str, Any]]:
        """Detect anomalies in feedback.
        
        Args:
            feedback: Feedback to analyze
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for excessive slippage
        if "slippage_pct" in feedback.performance_metrics:
            slippage = feedback.performance_metrics["slippage_pct"]
            if slippage > 2.0:
                anomalies.append({
                    "type": "excessive_slippage",
                    "severity": "high",
                    "value": slippage,
                })
        
        # Check for unusual latency
        if "latency_ms" in feedback.performance_metrics:
            latency = feedback.performance_metrics["latency_ms"]
            if latency > 5000:
                anomalies.append({
                    "type": "high_latency",
                    "severity": "medium",
                    "value": latency,
                })
        
        return anomalies
    
    def _generate_recommendations(
        self,
        feedback: ExecutionFeedback,
        analysis: dict[str, Any],
        anomalies: list[dict[str, Any]],
    ) -> list[str]:
        """Generate recommendations based on feedback.
        
        Args:
            feedback: Feedback
            analysis: Analysis results
            anomalies: Detected anomalies
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if feedback.category == FeedbackCategory.NEGATIVE:
            recommendations.append("Review strategy parameters")
            recommendations.append("Consider reducing position size")
        
        for anomaly in anomalies:
            if anomaly["type"] == "excessive_slippage":
                recommendations.append("Reduce order size to minimize slippage")
                recommendations.append("Consider using limit orders")
            elif anomaly["type"] == "high_latency":
                recommendations.append("Check network connectivity")
                recommendations.append("Review adapter performance")
        
        return recommendations
    
    def _analyze_trends(self, feedback_list: list[ExecutionFeedback]) -> dict[str, Any]:
        """Analyze trends in feedback.
        
        Args:
            feedback_list: List of feedback to analyze
            
        Returns:
            Trend analysis results
        """
        if len(feedback_list) < 2:
            return {}
        
        # Calculate trend in performance
        recent = feedback_list[-len(feedback_list) // 2:]
        earlier = feedback_list[:len(feedback_list) // 2]
        
        recent_positive = sum(1 for f in recent if f.category == FeedbackCategory.POSITIVE)
        earlier_positive = sum(1 for f in earlier if f.category == FeedbackCategory.POSITIVE)
        
        positive_trend = (recent_positive - earlier_positive) / len(earlier) if earlier else 0.0
        
        return {
            "performance_trend": "improving" if positive_trend > 0 else "declining",
            "positive_rate_change": positive_trend,
        }
    
    def _detect_aggregation_anomalies(self, feedback_list: list[ExecutionFeedback]) -> list[dict[str, Any]]:
        """Detect anomalies in aggregated feedback.
        
        Args:
            feedback_list: List of feedback to analyze
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for high failure rate
        negative_count = sum(1 for f in feedback_list if f.category == FeedbackCategory.NEGATIVE)
        if negative_count / len(feedback_list) > 0.5:
            anomalies.append({
                "type": "high_failure_rate",
                "severity": "high",
                "value": negative_count / len(feedback_list),
            })
        
        return anomalies
    
    def _generate_aggregation_recommendations(
        self,
        feedback_list: list[ExecutionFeedback],
        positive_count: int,
        negative_count: int,
    ) -> list[str]:
        """Generate recommendations from aggregation.
        
        Args:
            feedback_list: Feedback list
            positive_count: Number of positive feedback items
            negative_count: Number of negative feedback items
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if negative_count > positive_count:
            recommendations.append("Strategy underperforming - consider disabling")
            recommendations.append("Review strategy parameters and market conditions")
        elif positive_count > negative_count * 2:
            recommendations.append("Strategy performing well - consider increasing allocation")
        else:
            recommendations.append("Strategy performance stable - maintain current settings")
        
        return recommendations
    
    def _init_metrics(self) -> IntegrationMetrics:
        """Initialize integration metrics."""
        return IntegrationMetrics(
            total_feedback=0,
            feedback_by_type={},
            feedback_by_category={},
            feedback_processed=0,
            feedback_pending=0,
            average_processing_time_ms=0.0,
            strategies_tracked=0,
            aggregations_generated=0,
            anomalies_detected=0,
        )


# ---------------------------------------------------------------------------
# Execution Feedback Integration Manager
# ---------------------------------------------------------------------------


class ExecutionFeedbackIntegrationManager:
    """Manager for execution feedback integration."""
    
    def __init__(self, config: FeedbackIntegrationConfig | None = None) -> None:
        """Initialize the execution feedback integration manager.
        
        Args:
            config: Integration configuration
        """
        self._config = config or FeedbackIntegrationConfig()
        self._integrator = ExecutionFeedbackIntegrator(config)
    
    def add_feedback(self, feedback: ExecutionFeedback) -> None:
        """Add feedback.
        
        Args:
            feedback: Execution feedback
        """
        self._integrator.add_feedback(feedback)
    
    def process_feedback(self, feedback_id: str) -> dict[str, Any] | None:
        """Process feedback.
        
        Args:
            feedback_id: Feedback ID
            
        Returns:
            Processing results
        """
        return self._integrator.process_feedback(feedback_id)
    
    def aggregate_feedback(
        self,
        strategy_id: str,
        window_ms: int | None = None,
    ) -> FeedbackAggregation | None:
        """Aggregate feedback.
        
        Args:
            strategy_id: Strategy ID
            window_ms: Time window
            
        Returns:
            Aggregation
        """
        return self._integrator.aggregate_feedback(strategy_id, window_ms)
    
    def get_strategy_performance(self, strategy_id: str) -> StrategyPerformance | None:
        """Get strategy performance.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Strategy performance
        """
        return self._integrator.get_strategy_performance(strategy_id)
    
    def get_metrics(self) -> IntegrationMetrics:
        """Get metrics.
        
        Returns:
            Current metrics
        """
        return self._integrator.get_metrics()


__all__ = [
    "ExecutionFeedbackType",
    "FeedbackCategory",
    "FeedbackUrgency",
    "FeedbackIntegrationConfig",
    "ExecutionFeedback",
    "ExecutionMetrics",
    "StrategyPerformance",
    "FeedbackAggregation",
    "IntegrationMetrics",
    "ExecutionFeedbackIntegrator",
    "ExecutionFeedbackIntegrationManager",
]
