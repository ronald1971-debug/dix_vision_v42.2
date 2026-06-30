"""
DIX VISION Advanced Metrics Service

Provides real-time system metrics, custom dashboards, alert management,
and performance profiling for enhanced system observability.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
import statistics

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricConfig:
    """Configuration for metric collection."""
    metric_name: str
    metric_type: MetricType
    description: str = ""
    labels: List[str] = field(default_factory=list)
    buckets: List[float] = field(default_factory=lambda: [0.1, 0.5, 1.0, 5.0, 10.0])
    quantiles: List[float] = field(default_factory=lambda: [0.5, 0.9, 0.95, 0.99])


@dataclass
class AlertConfig:
    """Configuration for alert management."""
    alert_name: str
    condition: Callable[[float], bool]
    severity: AlertSeverity
    message: str = ""
    enabled: bool = True
    cooldown: int = 60  # seconds


@dataclass
class DashboardConfig:
    """Configuration for custom dashboards."""
    dashboard_name: str
    metrics: List[str]
    refresh_interval: int = 5  # seconds
    layout: str = "grid"
    enabled: bool = True


@dataclass
class MetricValue:
    """Metric value with timestamp."""
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert with metadata."""
    alert_name: str
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False


class MetricsService(Service):
    """Advanced metrics service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("metrics_service")
        self._metrics: Dict[str, Dict[str, MetricValue]] = defaultdict(dict)
        self._metric_configs: Dict[str, MetricConfig] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._summaries: Dict[str, List[float]] = defaultdict(list)
        self._alerts: Dict[str, AlertConfig] = {}
        self._active_alerts: List[Alert] = []
        self._dashboards: Dict[str, DashboardConfig] = {}
        self._metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.Lock()
        self._alert_cooldowns: Dict[str, float] = {}
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the metrics service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Initialize default metrics
            self._init_default_metrics()
            
            # Initialize default alerts
            self._init_default_alerts()
            
            # Initialize default dashboards
            self._init_default_dashboards()
            
            logger.info("Metrics Service initialized")
            return True
        except Exception as e:
            logger.error(f"Metrics Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the metrics service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start background alert checker
            self._start_alert_checker()
            
            # Start background metrics collector
            self._start_metrics_collector()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Metrics Service started")
            return True
        except Exception as e:
            logger.error(f"Metrics Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the metrics service."""
        try:
            self.state = ServiceState.STOPPING
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Metrics Service stopped")
            return True
        except Exception as e:
            logger.error(f"Metrics Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get metrics service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Metrics Service - {len(self._metrics)} metrics, {len(self._active_alerts)} active alerts",
            details={
                "total_metrics": len(self._metrics),
                "total_metric_configs": len(self._metric_configs),
                "active_alerts": len(self._active_alerts),
                "total_dashboards": len(self._dashboards),
                "metric_history_size": sum(len(h) for h in self._metric_history.values())
            },
            timestamp=time.time()
        )
    
    def register_metric(self, config: MetricConfig) -> None:
        """Register a metric configuration."""
        with self._lock:
            self._metric_configs[config.metric_name] = config
            logger.info(f"Registered metric: {config.metric_name}")
    
    def increment(self, metric_name: str, value: float = 1.0, labels: Dict[str, str] = None) -> None:
        """Increment a counter metric."""
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = {}
            
            label_key = self._label_key(labels or {})
            if label_key not in self._metrics[metric_name]:
                self._metrics[metric_name][label_key] = MetricValue(value=0.0, labels=labels or {})
            
            self._metrics[metric_name][label_key].value += value
            self._metrics[metric_name][label_key].timestamp = time.time()
            
            # Add to history
            self._metric_history[metric_name].append(self._metrics[metric_name][label_key].value)
    
    def set_gauge(self, metric_name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Set a gauge metric value."""
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = {}
            
            label_key = self._label_key(labels or {})
            self._metrics[metric_name][label_key] = MetricValue(value=value, labels=labels or {})
            
            # Add to history
            self._metric_history[metric_name].append(value)
    
    def observe_histogram(self, metric_name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Observe a value for histogram metric."""
        with self._lock:
            self._histograms[metric_name].append(value)
            if len(self._histograms[metric_name]) > 10000:
                self._histograms[metric_name] = self._histograms[metric_name][-10000:]
    
    def observe_summary(self, metric_name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Observe a value for summary metric."""
        with self._lock:
            self._summaries[metric_name].append(value)
            if len(self._summaries[metric_name]) > 10000:
                self._summaries[metric_name] = self._summaries[metric_name][-10000:]
    
    def register_alert(self, config: AlertConfig) -> None:
        """Register an alert configuration."""
        with self._lock:
            self._alerts[config.alert_name] = config
            logger.info(f"Registered alert: {config.alert_name}")
    
    def register_dashboard(self, config: DashboardConfig) -> None:
        """Register a dashboard configuration."""
        with self._lock:
            self._dashboards[config.dashboard_name] = config
            logger.info(f"Registered dashboard: {config.dashboard_name}")
    
    def get_metric(self, metric_name: str, labels: Dict[str, str] = None) -> Optional[float]:
        """Get current metric value."""
        with self._lock:
            if metric_name not in self._metrics:
                return None
            
            label_key = self._label_key(labels or {})
            if label_key not in self._metrics[metric_name]:
                return None
            
            return self._metrics[metric_name][label_key].value
    
    def get_histogram(self, metric_name: str) -> Dict[str, Any]:
        """Get histogram statistics."""
        with self._lock:
            if metric_name not in self._histograms:
                return {}
            
            values = self._histograms[metric_name]
            if not values:
                return {}
            
            config = self._metric_configs.get(metric_name)
            buckets = config.buckets if config else [0.1, 0.5, 1.0, 5.0, 10.0]
            
            bucket_counts = {f"le_{bucket}": sum(1 for v in values if v <= bucket) for bucket in buckets}
            
            return {
                "count": len(values),
                "sum": sum(values),
                "mean": statistics.mean(values),
                "stddev": statistics.stdev(values) if len(values) > 1 else 0.0,
                "min": min(values),
                "max": max(values),
                "buckets": bucket_counts
            }
    
    def get_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get summary statistics."""
        with self._lock:
            if metric_name not in self._summaries:
                return {}
            
            values = self._summaries[metric_name]
            if not values:
                return {}
            
            config = self._metric_configs.get(metric_name)
            quantiles = config.quantiles if config else [0.5, 0.9, 0.95, 0.99]
            
            sorted_values = sorted(values)
            quantile_values = {f"quantile_{q}": sorted_values[int(len(sorted_values) * q)] for q in quantiles}
            
            return {
                "count": len(values),
                "sum": sum(values),
                "mean": statistics.mean(values),
                "quantiles": quantile_values
            }
    
    def get_dashboard_data(self, dashboard_name: str) -> Dict[str, Any]:
        """Get data for a dashboard."""
        with self._lock:
            if dashboard_name not in self._dashboards:
                return {}
            
            dashboard = self._dashboards[dashboard_name]
            data = {}
            
            for metric_name in dashboard.metrics:
                metric_config = self._metric_configs.get(metric_name)
                if metric_config:
                    if metric_config.metric_type == MetricType.HISTOGRAM:
                        data[metric_name] = self.get_histogram(metric_name)
                    elif metric_config.metric_type == MetricType.SUMMARY:
                        data[metric_name] = self.get_summary(metric_name)
                    else:
                        data[metric_name] = self.get_metric(metric_name)
            
            return {
                "dashboard_name": dashboard_name,
                "layout": dashboard.layout,
                "refresh_interval": dashboard.refresh_interval,
                "metrics": data,
                "timestamp": time.time()
            }
    
    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts."""
        with self._lock:
            return [alert for alert in self._active_alerts if not alert.resolved]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        with self._lock:
            result = {}
            for metric_name, label_values in self._metrics.items():
                result[metric_name] = {label_key: metric_value.value for label_key, metric_value in label_values.items()}
            return result
    
    def _label_key(self, labels: Dict[str, str]) -> str:
        """Generate a key from labels."""
        return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
    
    def _init_default_metrics(self) -> None:
        """Initialize default metrics."""
        default_metrics = [
            MetricConfig("requests_total", MetricType.COUNTER, "Total number of requests"),
            MetricConfig("request_duration_seconds", MetricType.HISTOGRAM, "Request duration in seconds"),
            MetricConfig("active_connections", MetricType.GAUGE, "Number of active connections"),
            MetricConfig("memory_usage_bytes", MetricType.GAUGE, "Memory usage in bytes"),
            MetricConfig("cpu_usage_percent", MetricType.GAUGE, "CPU usage percentage"),
            MetricConfig("error_count", MetricType.COUNTER, "Total number of errors"),
        ]
        
        for metric_config in default_metrics:
            self.register_metric(metric_config)
    
    def _init_default_alerts(self) -> None:
        """Initialize default alerts."""
        default_alerts = [
            AlertConfig("high_error_rate", lambda x: x > 10, AlertSeverity.ERROR, "Error rate is too high"),
            AlertConfig("high_memory_usage", lambda x: x > 0.9, AlertSeverity.WARNING, "Memory usage is high"),
            AlertConfig("high_cpu_usage", lambda x: x > 0.8, AlertSeverity.WARNING, "CPU usage is high"),
        ]
        
        for alert_config in default_alerts:
            self.register_alert(alert_config)
    
    def _init_default_dashboards(self) -> None:
        """Initialize default dashboards."""
        default_dashboards = [
            DashboardConfig("system_overview", ["memory_usage_bytes", "cpu_usage_percent", "active_connections"]),
            DashboardConfig("request_metrics", ["requests_total", "request_duration_seconds", "error_count"]),
        ]
        
        for dashboard_config in default_dashboards:
            self.register_dashboard(dashboard_config)
    
    def _start_alert_checker(self) -> None:
        """Start background alert checker."""
        def check_alerts():
            while self.state == ServiceState.RUNNING:
                try:
                    self._check_alerts()
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    logger.error(f"Alert checker error: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=check_alerts, daemon=True)
        thread.start()
        logger.info("Alert checker started")
    
    def _check_alerts(self) -> None:
        """Check all alerts."""
        with self._lock:
            current_time = time.time()
            
            for alert_name, alert_config in self._alerts.items():
                if not alert_config.enabled:
                    continue
                
                # Check cooldown
                if alert_name in self._alert_cooldowns:
                    if current_time - self._alert_cooldowns[alert_name] < alert_config.cooldown:
                        continue
                
                # Get metric value
                metric_value = self.get_metric(alert_name)
                if metric_value is None:
                    continue
                
                # Check condition
                if alert_config.condition(metric_value):
                    alert = Alert(
                        alert_name=alert_name,
                        severity=alert_config.severity,
                        message=alert_config.message,
                        value=metric_value,
                        threshold=0.0,  # Would need to extract from condition
                        timestamp=current_time
                    )
                    self._active_alerts.append(alert)
                    self._alert_cooldowns[alert_name] = current_time
                    
                    logger.warning(f"Alert triggered: {alert_name} - {alert_config.message}")
                    self.emit_event(str(EventType.AI_DECISION), {
                        "service": self.name,
                        "alert_name": alert_name,
                        "severity": alert_config.severity.value,
                        "value": metric_value
                    })
    
    def _start_metrics_collector(self) -> None:
        """Start background metrics collector."""
        def collect_metrics():
            while self.state == ServiceState.RUNNING:
                try:
                    # Collect system metrics
                    self._collect_system_metrics()
                    time.sleep(10)  # Collect every 10 seconds
                except Exception as e:
                    logger.error(f"Metrics collection error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
        logger.info("Metrics collector started")
    
    def _collect_system_metrics(self) -> None:
        """Collect system metrics."""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.set_gauge("memory_usage_bytes", memory.used)
            self.set_gauge("memory_usage_percent", memory.percent)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.set_gauge("cpu_usage_percent", cpu_percent / 100.0)
            
            # Active connections (placeholder)
            self.set_gauge("active_connections", len(self._metrics))
            
        except ImportError:
            logger.warning("psutil not available for system metrics collection")
        except Exception as e:
            logger.error(f"System metrics collection error: {e}")


# Global instance
_metrics_service: Optional[MetricsService] = None


def get_metrics_service() -> MetricsService:
    """Get global metrics service instance."""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
    return _metrics_service