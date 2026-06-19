"""
execution_unified.health.health_monitor
DIX VISION v42.2 — Enhanced Health Monitor with World Context

Provides comprehensive health monitoring for all system components with
world-aware threshold adjustment and predictive health assessment.
Enhanced with real-time metrics, anomaly detection, and world understanding.
"""

from __future__ import annotations

import logging
import threading
import time
import psutil
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class WorldContext:
    """World context for health-aware monitoring."""
    market_regime: str = "unknown"
    market_trend: str = "unknown"
    volatility_regime: str = "unknown"
    liquidity_state: str = "unknown"
    agent_activity: Dict[str, float] = field(default_factory=dict)
    causal_factors: List[str] = field(default_factory=list)
    prediction_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

# World context integration
try:
    from world_model.indicator_integration import get_integration_bridge
    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False
    logger.warning("[HEALTH_MONITOR] World model integration not available")


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


@dataclass
class HealthCheck:
    """Individual health check result with enhanced metrics."""
    
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime
    metrics: Dict[str, float] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    confidence_interval: Tuple[float, float] = (0.0, 1.0)  # 95% confidence interval
    world_context_adjusted: bool = False  # Whether thresholds were world-aware
    anomaly_detected: bool = False  # Statistical anomaly detected
    
    @property
    def is_healthy(self) -> bool:
        return self.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
    
    @property
    def confidence_score(self) -> float:
        """Calculate confidence score from interval."""
        if self.confidence_interval[1] == self.confidence_interval[0]:
            return 1.0
        return 1.0 - (self.confidence_interval[1] - self.confidence_interval[0])


@dataclass
class SystemHealthReport:
    """Comprehensive system health report with predictive analysis."""
    
    overall_status: HealthStatus
    component_checks: Dict[str, HealthCheck]
    timestamp: datetime
    total_components: int
    healthy_components: int
    degraded_components: int
    unhealthy_components: int
    critical_components: int
    overall_health_score: float  # 0.0 - 1.0
    health_trend: str = "stable"  # improving, degrading, stable
    predicted_health_score: float = 0.0  # Predicted score for next period
    world_context: Optional[WorldContext] = None  # Current world context
    monitoring_interval: int = 5000  # Current monitoring interval in ms
    confidence_interval: Tuple[float, float] = (0.0, 1.0)  # 95% CI for health score
    
    @property
    def is_healthy(self) -> bool:
        return self.overall_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
    
    @property
    def health_percentage(self) -> float:
        if self.total_components == 0:
            return 100.0
        return (self.healthy_components / self.total_components) * 100
    
    @property
    def health_decline_rate(self) -> float:
        """Calculate rate of health decline."""
        if self.predicted_health_score <= self.overall_health_score:
            return 0.0
        return (self.overall_health_score - self.predicted_health_score) / self.overall_health_score


class AnomalyDetector:
    """Statistical anomaly detection for health metrics."""
    
    def __init__(self, history_window: int = 100):
        self._history_window = history_window
        self._metric_history: Dict[str, deque] = {}
    
    def update_history(self, component: str, metrics: Dict[str, float]) -> None:
        """Update metric history for anomaly detection."""
        if component not in self._metric_history:
            self._metric_history[component] = {}
        
        for metric_name, value in metrics.items():
            if metric_name not in self._metric_history[component]:
                self._metric_history[component][metric_name] = deque(maxlen=self._history_window)
            self._metric_history[component][metric_name].append(value)
    
    def detect_anomaly(self, component: str, metrics: Dict[str, float], 
                      confidence_threshold: float = 0.95) -> bool:
        """Detect statistical anomaly using z-score analysis."""
        if component not in self._metric_history:
            return False  # No history, can't detect anomaly
        
        anomaly_detected = False
        
        for metric_name, current_value in metrics.items():
            history = self._metric_history[component].get(metric_name)
            if not history or len(history) < 10:
                continue  # Insufficient data
            
            # Calculate z-score
            mean = statistics.mean(history)
            if len(history) > 1:
                stdev = statistics.stdev(history)
            else:
                stdev = 0.0
            
            if stdev == 0:
                continue  # No variance
            
            z_score = abs((current_value - mean) / stdev)
            
            # Check if z-score exceeds threshold (approximately 2 std devs for 95% confidence)
            if z_score > 2.0:
                logger.info(
                    f"[ANOMALY_DETECTOR] Anomaly detected for {component}:{metric_name}, "
                    f"z_score={z_score:.2f}, current={current_value:.2f}, mean={mean:.2f}"
                )
                anomaly_detected = True
        
        return anomaly_detected
    
    def calculate_confidence_interval(self, values: List[float], 
                                     confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for metric values."""
        if len(values) < 2:
            return (0.0, 1.0)
        
        mean = statistics.mean(values)
        if len(values) > 1:
            stdev = statistics.stdev(values)
        else:
            stdev = 0.0
        
        # Use z-score for 95% confidence (1.96)
        z_score = 1.96
        margin_of_error = z_score * (stdev / (len(values) ** 0.5))
        
        return (max(0.0, mean - margin_of_error), min(1.0, mean + margin_of_error))


class HealthCheckProvider:
    """Base class for health check providers."""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
    
    def check_health(self, world_context: Optional[WorldContext] = None) -> HealthCheck:
        """Perform health check for the component."""
        raise NotImplementedError


class HealthMonitor:
    """
    Enhanced health monitoring system with world context integration.
    
    Provides comprehensive health monitoring with world-aware threshold adjustment,
    predictive health assessment, anomaly detection, and adaptive monitoring intervals.
    """
    
    def __init__(self, check_interval_ms: int = 5000):
        self._lock = threading.Lock()
        self._base_check_interval_ms = check_interval_ms
        self._current_check_interval_ms = check_interval_ms
        self._health_check_providers: Dict[str, HealthCheckProvider] = {}
        
        # Health check results cache
        self._health_cache: Dict[str, HealthCheck] = {}
        self._last_health_report: Optional[SystemHealthReport] = None
        
        # Background monitoring
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Metrics
        self._total_checks = 0
        self._total_alerts = 0
        self._system_metrics = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_percent': 0.0,
            'latency_ms': 0.0,
            'error_rate': 0.0
        }
        
        # Health history for trend analysis
        self._health_history: deque = deque(maxlen=200)  # Store last 200 health reports
        
        # World context integration
        self._world_integration_bridge = None
        self._current_world_context: Optional[WorldContext] = None
        if WORLD_MODEL_AVAILABLE:
            self._init_world_integration()
        
        # Anomaly detection
        self._anomaly_detector = AnomalyDetector(history_window=100)
        
        logger.info(f"[HEALTH_MONITOR] Initialized with base check interval: {check_interval_ms}ms")
    
    def _init_world_integration(self) -> None:
        """Initialize world model integration bridge."""
        try:
            self._world_integration_bridge = get_integration_bridge()
            logger.info("[HEALTH_MONITOR] World model integration bridge initialized")
        except Exception as e:
            logger.warning(f"[HEALTH_MONITOR] Failed to initialize world integration: {e}")
            self._world_integration_bridge = None
    
    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model."""
        if not self._world_integration_bridge:
            return None
        
        try:
            # Get world state from integration bridge
            world_state = self._world_integration_bridge.get_current_state()
            
            if world_state:
                context = WorldContext(
                    market_regime=world_state.get('market_regime', 'unknown'),
                    market_trend=world_state.get('market_trend', 'unknown'),
                    volatility_regime=world_state.get('volatility_regime', 'unknown'),
                    liquidity_state=world_state.get('liquidity_state', 'unknown'),
                    agent_activity=world_state.get('agent_activity', {}),
                    causal_factors=world_state.get('causal_factors', []),
                    prediction_confidence=world_state.get('prediction_confidence', 0.0),
                    timestamp=datetime.utcnow()
                )
                self._current_world_context = context
                return context
        
        except Exception as e:
            logger.debug(f"[HEALTH_MONITOR] Failed to get world context: {e}")
        
        return None
    
    def _calculate_adaptive_interval(self, world_context: Optional[WorldContext]) -> int:
        """Calculate adaptive monitoring interval based on world context."""
        base_interval = self._base_check_interval_ms
        
        if not world_context:
            return base_interval
        
        # Increase monitoring frequency during high volatility
        if world_context.volatility_regime == "high":
            return int(base_interval * 0.2)  # 5x faster monitoring (20% of base interval)
        elif world_context.volatility_regime == "medium":
            return int(base_interval * 0.5)  # 2x faster monitoring (50% of base interval)
        
        # Standard interval during stable periods
        return base_interval
    
    def _collect_system_metrics(self) -> Dict[str, float]:
        """Collect real-time system metrics."""
        try:
            metrics = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0.0,
                'latency_ms': 0.0,  # Will be calculated during health checks
                'error_rate': self._calculate_error_rate()
            }
            self._system_metrics.update(metrics)
            return metrics
        except Exception as e:
            logger.error(f"[HEALTH_MONITOR] Failed to collect system metrics: {e}")
            return self._system_metrics
    
    def _calculate_error_rate(self) -> float:
        """Calculate recent error rate from health checks."""
        if self._total_checks == 0:
            return 0.0
        return self._total_alerts / self._total_checks
    
    def register_provider(self, provider: HealthCheckProvider) -> None:
        """Register a health check provider."""
        with self._lock:
            self._health_check_providers[provider.component_name] = provider
            logger.info(f"[HEALTH_MONITOR] Registered health check provider: {provider.component_name}")
    
    def check_component_health(self, component: str, world_context: Optional[WorldContext] = None) -> HealthCheck:
        """Check health of a specific component with world context integration."""
        # Get world context if not provided
        if world_context is None:
            world_context = self._get_world_context()
        
        provider = self._health_check_providers.get(component)
        if provider:
            try:
                # Perform health check with world context
                health_check = provider.check_health(world_context=world_context)
                
                # Update anomaly detection history
                if health_check.metrics:
                    self._anomaly_detector.update_history(component, health_check.metrics)
                
                # Detect anomalies
                if health_check.metrics:
                    health_check.anomaly_detected = self._anomaly_detector.detect_anomaly(
                        component, health_check.metrics
                    )
                
                # Calculate confidence interval
                if health_check.metrics:
                    metric_values = list(health_check.metrics.values())
                    health_check.confidence_interval = self._anomaly_detector.calculate_confidence_interval(metric_values)
                
                # Apply world-aware threshold adjustment
                if world_context and health_check.metrics:
                    health_check = self._apply_world_aware_thresholds(health_check, world_context)
                    health_check.world_context_adjusted = True
                
                self._health_cache[component] = health_check
                self._total_checks += 1
                return health_check
            
            except Exception as e:
                logger.error(f"[HEALTH_MONITOR] Health check failed for {component}: {e}")
                return HealthCheck(
                    component=component,
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check failed: {str(e)}",
                    timestamp=datetime.utcnow(),
                    confidence_interval=(0.0, 0.0),
                    world_context_adjusted=False
                )
        else:
            return HealthCheck(
                component=component,
                status=HealthStatus.UNKNOWN,
                message="No health check provider registered",
                timestamp=datetime.utcnow(),
                confidence_interval=(0.0, 0.0),
                world_context_adjusted=False
            )
    
    def _apply_world_aware_thresholds(self, health_check: HealthCheck, world_context: WorldContext) -> HealthCheck:
        """Apply world-aware threshold adjustments to health check results."""
        # Adjust status based on world conditions
        if world_context.volatility_regime == "high":
            # Relax thresholds during high volatility (allow more degraded status)
            if health_check.status == HealthStatus.UNHEALTHY:
                health_check.status = HealthStatus.DEGRADED
                health_check.message += " (threshold relaxed due to high volatility)"
        elif world_context.volatility_regime == "low" and world_context.market_trend == "stable":
            # Tighten thresholds during stable periods
            if health_check.status == HealthStatus.HEALTHY and health_check.metrics.get('error_rate', 0) > 0.01:
                health_check.status = HealthStatus.DEGRADED
                health_check.message += " (threshold tightened due to stable conditions)"
        
        return health_check
    
    def check_system_health(self) -> SystemHealthReport:
        """Check health of all registered components with enhanced analysis."""
        # Get world context for this health check cycle
        world_context = self._get_world_context()
        
        # Collect system metrics
        system_metrics = self._collect_system_metrics()
        
        # Update adaptive monitoring interval
        adaptive_interval = self._calculate_adaptive_interval(world_context)
        self._current_check_interval_ms = adaptive_interval
        
        component_checks = {}
        
        with self._lock:
            for component in self._health_check_providers.keys():
                try:
                    health_check = self.check_component_health(component, world_context)
                    component_checks[component] = health_check
                except Exception as e:
                    logger.error(f"[HEALTH_MONITOR] Failed to check {component}: {e}")
                    component_checks[component] = HealthCheck(
                        component=component,
                        status=HealthStatus.UNKNOWN,
                        message=f"Check failed: {str(e)}",
                        timestamp=datetime.utcnow(),
                        confidence_interval=(0.0, 0.0),
                        world_context_adjusted=False
                    )
        
        # Calculate overall health
        total_components = len(component_checks)
        healthy = sum(1 for hc in component_checks.values() if hc.status == HealthStatus.HEALTHY)
        degraded = sum(1 for hc in component_checks.values() if hc.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for hc in component_checks.values() if hc.status == HealthStatus.UNHEALTHY)
        critical = sum(1 for hc in component_checks.values() if hc.status == HealthStatus.CRITICAL)
        
        # Determine overall status
        if critical > 0:
            overall_status = HealthStatus.CRITICAL
        elif unhealthy > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded > 0:
            overall_status = HealthStatus.DEGRADED
        elif healthy == total_components:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN
        
        # Calculate health score
        health_score = (healthy + degraded * 0.5) / total_components if total_components > 0 else 0.0
        
        # Calculate trend analysis
        health_trend = self._calculate_health_trend(health_score)
        
        # Calculate predictive health score
        predicted_score = self._predict_health_score(health_score, health_trend, world_context)
        
        # Calculate confidence interval for overall health score
        confidence_interval = self._anomaly_detector.calculate_confidence_interval([health_score])
        
        report = SystemHealthReport(
            overall_status=overall_status,
            component_checks=component_checks,
            timestamp=datetime.utcnow(),
            total_components=total_components,
            healthy_components=healthy,
            degraded_components=degraded,
            unhealthy_components=unhealthy,
            critical_components=critical,
            overall_health_score=health_score,
            health_trend=health_trend,
            predicted_health_score=predicted_score,
            world_context=world_context,
            monitoring_interval=adaptive_interval,
            confidence_interval=confidence_interval
        )
        
        # Store in health history
        self._health_history.append(report)
        
        self._last_health_report = report
        
        # Log if not healthy
        if not report.is_healthy:
            self._total_alerts += 1
            logger.warning(
                f"[HEALTH_MONITOR] System not healthy: {overall_status.value}, "
                f"score={health_score:.2f}, "
                f"critical={critical}, unhealthy={unhealthy}, degraded={degraded}, "
                f"trend={health_trend}, predicted={predicted_score:.2f}"
            )
        
        return report
    
    def _calculate_health_trend(self, current_score: float) -> str:
        """Calculate health trend based on historical data."""
        if len(self._health_history) < 3:
            return "stable"
        
        # Get last 5 health scores
        recent_scores = [report.overall_health_score for report in list(self._health_history)[-5:]]
        recent_scores.append(current_score)
        
        # Calculate trend using linear regression slope
        if len(recent_scores) < 2:
            return "stable"
        
        x = list(range(len(recent_scores)))
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(recent_scores)
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, recent_scores))
        denominator = sum((xi - mean_x) ** 2 for xi in x)
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "degrading"
        else:
            return "stable"
    
    def _predict_health_score(self, current_score: float, trend: str, 
                             world_context: Optional[WorldContext]) -> float:
        """Predict health score for next monitoring period."""
        # Base prediction based on trend
        if trend == "improving":
            predicted = current_score * 1.02  # 2% improvement
        elif trend == "degrading":
            predicted = current_score * 0.98  # 2% degradation
        else:
            predicted = current_score  # No change
        
        # Adjust prediction based on world context
        if world_context:
            if world_context.volatility_regime == "high":
                predicted = max(0.5, predicted * 0.95)  # Potential degradation in high volatility
            elif world_context.market_trend == "stable" and world_context.volatility_regime == "low":
                predicted = min(1.0, predicted * 1.05)  # Improvement in stable conditions
        
        return max(0.0, min(1.0, predicted))
    
    def start_monitoring(self) -> None:
        """Start background health monitoring."""
        if self._monitoring_active:
            logger.warning("[HEALTH_MONITOR] Monitoring already active")
            return
        
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logger.info("[HEALTH_MONITOR] Started background health monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop background health monitoring."""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
            logger.info("[HEALTH_MONITOR] Stopped background health monitoring")
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop with adaptive intervals."""
        while self._monitoring_active:
            try:
                start_time = time.time()
                
                # Check system health (this will update adaptive interval)
                report = self.check_system_health()
                
                # Log adaptive interval changes
                if report.monitoring_interval != self._current_check_interval_ms:
                    self._current_check_interval_ms = report.monitoring_interval
                    logger.info(
                        f"[HEALTH_MONITOR] Adaptive interval adjusted: "
                        f"{self._current_check_interval_ms}ms (volatility: "
                        f"{report.world_context.volatility_regime if report.world_context else 'unknown'})"
                    )
                
                # Calculate sleep time using adaptive interval
                elapsed_ms = (time.time() - start_time) * 1000
                sleep_ms = max(0, self._current_check_interval_ms - elapsed_ms)
                time.sleep(sleep_ms / 1000)
            
            except Exception as e:
                logger.error(f"[HEALTH_MONITOR] Monitoring loop error: {e}")
                time.sleep(1.0)
    
    def get_last_report(self) -> Optional[SystemHealthReport]:
        """Get the last health report."""
        return self._last_health_report
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get enhanced health monitoring statistics."""
        with self._lock:
            stats = {
                "monitoring_active": self._monitoring_active,
                "total_checks": self._total_checks,
                "total_alerts": self._total_alerts,
                "registered_providers": len(self._health_check_providers),
                "base_interval_ms": self._base_check_interval_ms,
                "current_interval_ms": self._current_check_interval_ms,
                "world_integration_available": WORLD_MODEL_AVAILABLE,
                "world_integration_active": self._world_integration_bridge is not None,
                "current_world_context": self._current_world_context.market_regime if self._current_world_context else "unknown",
                "system_metrics": self._system_metrics,
                "health_history_size": len(self._health_history),
                "error_rate": self._calculate_error_rate()
            }
            
            # Add last health report summary if available
            if self._last_health_report:
                stats["last_health_status"] = {
                    "overall_status": self._last_health_report.overall_status.value,
                    "health_score": self._last_health_report.overall_health_score,
                    "health_trend": self._last_health_report.health_trend,
                    "predicted_score": self._last_health_report.predicted_health_score,
                    "confidence_interval": self._last_health_report.confidence_interval
                }
            
            return stats


# Built-in enhanced health check providers with world context

class ExecutionKernelHealthCheck(HealthCheckProvider):
    """Enhanced health check for execution kernel with world context."""
    
    def __init__(self):
        super().__init__("execution_kernel")
    
    def check_health(self, world_context: Optional[WorldContext] = None) -> HealthCheck:
        try:
            from execution_unified import get_unified_execution_kernel
            kernel = get_unified_execution_kernel()
            
            metrics = kernel.get_metrics() if hasattr(kernel, 'get_metrics') else {}
            
            # Determine health based on metrics with world-aware thresholds
            health_score = metrics.get('health_score', 1.0)
            
            # Apply world-aware threshold adjustment
            if world_context and world_context.volatility_regime == "high":
                # Relax thresholds during high volatility
                threshold_healthy = 0.7  # Lowered from 0.8
                threshold_degraded = 0.4  # Lowered from 0.5
            elif world_context and world_context.volatility_regime == "low":
                # Tighten thresholds during low volatility
                threshold_healthy = 0.85  # Raised from 0.8
                threshold_degraded = 0.55  # Raised from 0.5
            else:
                # Standard thresholds
                threshold_healthy = 0.8
                threshold_degraded = 0.5
            
            if health_score > threshold_healthy:
                status = HealthStatus.HEALTHY
                message = f"Execution kernel healthy (score: {health_score:.2f})"
            elif health_score > threshold_degraded:
                status = HealthStatus.DEGRADED
                message = f"Execution kernel degraded (score: {health_score:.2f})"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Execution kernel unhealthy (score: {health_score:.2f})"
            
            return HealthCheck(
                component=self.component_name,
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metrics=metrics,
                confidence_interval=(0.0, 1.0),
                world_context_adjusted=world_context is not None
            )
        except Exception as e:
            return HealthCheck(
                component=self.component_name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                confidence_interval=(0.0, 0.0),
                world_context_adjusted=False
            )


class CognitiveOSHealthCheck(HealthCheckProvider):
    """Health check for Cognitive OS."""
    
    def __init__(self):
        super().__init__("cognitive_os")
    
    def check_health(self) -> HealthCheck:
        try:
            from cognitive_os.core import get_cognitive_os_kernel
            kernel = get_cognitive_os_kernel()
            
            metrics = kernel.get_system_metrics()
            
            health_score = metrics.health_score
            
            if health_score > 0.8:
                status = HealthStatus.HEALTHY
                message = "Cognitive OS healthy"
            elif health_score > 0.6:
                status = HealthStatus.DEGRADED
                message = "Cognitive OS degraded"
            elif health_score > 0.4:
                status = HealthStatus.UNHEALTHY
                message = "Cognitive OS unhealthy"
            else:
                status = HealthStatus.CRITICAL
                message = "Cognitive OS critical"
            
            return HealthCheck(
                component=self.component_name,
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metrics={
                    "health_score": health_score,
                    "performance_score": metrics.performance_score,
                    "active_layers": len(metrics.active_layers)
                }
            )
        except Exception as e:
            return HealthCheck(
                component=self.component_name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                confidence_interval=(0.0, 0.0),
                world_context_adjusted=False
            )


# Singleton instance
_health_monitor: Optional[HealthMonitor] = None
_health_monitor_lock = threading.Lock()

def get_health_monitor(check_interval_ms: int = 5000) -> HealthMonitor:
    """Get the singleton health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        with _health_monitor_lock:
            if _health_monitor is None:
                _health_monitor = HealthMonitor(check_interval_ms)
                
                # Register built-in health check providers
                _health_monitor.register_provider(ExecutionKernelHealthCheck())
                _health_monitor.register_provider(CognitiveOSHealthCheck())
                
    return _health_monitor


__all__ = [
    "HealthStatus",
    "HealthCheck",
    "SystemHealthReport",
    "HealthCheckProvider",
    "HealthMonitor",
    "get_health_monitor",
    "ExecutionKernelHealthCheck",
    "CognitiveOSHealthCheck",
]