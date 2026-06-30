"""
DIX VISION System Behavior Analytics Service

Provides system behavior modeling, performance trend analysis, resource utilization patterns,
bottleneck identification, and capacity planning for system optimization.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class BehaviorPattern(Enum):
    """Types of system behavior patterns."""
    SPIKE = "spike"
    DRIFT = "drift"
    CYCLIC = "cyclic"
    ANOMALY = "anomaly"
    NORMAL = "normal"


class ResourceMetric(Enum):
    """Types of resource metrics."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"


@dataclass
class MetricSample:
    """Single metric sample."""
    timestamp: float
    metric_type: ResourceMetric
    service: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehaviorModel:
    """System behavior model."""
    model_id: str
    pattern_type: BehaviorPattern
    metric_type: ResourceMetric
    service: str
    confidence: float
    baseline_value: float
    threshold_upper: float
    threshold_lower: float
    detection_time: float
    description: str = ""


@dataclass
class Bottleneck:
    """System bottleneck identification."""
    bottleneck_id: str
    service: str
    resource: ResourceMetric
    severity: str  # "low", "medium", "high", "critical"
    current_value: float
    threshold_value: float
    impact_score: float
    detected_time: float
    recommendation: str = ""


@dataclass
class CapacityPrediction:
    """Capacity planning prediction."""
    resource: ResourceMetric
    current_capacity: float
    predicted_demand: float
    time_horizon: str  # "1h", "1d", "1w", "1m"
    confidence: float
    action_required: bool
    recommended_action: str = ""


class SystemBehaviorAnalyticsService(Service):
    """System behavior analytics service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("system_behavior_analytics_service")
        self._metric_samples: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self._behavior_models: Dict[str, BehaviorModel] = {}
        self._bottlenecks: List[Bottleneck] = []
        self._capacity_predictions: Dict[str, CapacityPrediction] = {}
        self._performance_trends: Dict[str, List[float]] = defaultdict(list)
        self._resource_utilization: Dict[ResourceMetric, Dict[str, float]] = defaultdict(dict)
        self._lock = threading.Lock()
        self._analysis_interval = 60  # seconds
        self._thresholds: Dict[ResourceMetric, Dict[str, float]] = {
            ResourceMetric.CPU: {"warning": 0.70, "critical": 0.90},
            ResourceMetric.MEMORY: {"warning": 0.80, "critical": 0.95},
            ResourceMetric.DISK: {"warning": 0.85, "critical": 0.95},
            ResourceMetric.NETWORK: {"warning": 0.75, "critical": 0.90},
            ResourceMetric.GPU: {"warning": 0.80, "critical": 0.95}
        }
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the system behavior analytics service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            analytics_config = config.get("system_behavior_analytics", {})
            self._analysis_interval = analytics_config.get("analysis_interval", 60)
            
            # Customize thresholds if provided
            custom_thresholds = analytics_config.get("thresholds", {})
            for metric, thresholds in custom_thresholds.items():
                if metric in [m.value for m in ResourceMetric]:
                    metric_enum = ResourceMetric(metric)
                    self._thresholds[metric_enum].update(thresholds)
            
            logger.info("System Behavior Analytics Service initialized")
            return True
        except Exception as e:
            logger.error(f"System Behavior Analytics Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the system behavior analytics service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start background behavior analyzer
            self._start_behavior_analyzer()
            
            # Start bottleneck detector
            self._start_bottleneck_detector()
            
            # Start capacity planner
            self._start_capacity_planner()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("System Behavior Analytics Service started")
            return True
        except Exception as e:
            logger.error(f"System Behavior Analytics Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the system behavior analytics service."""
        try:
            self.state = ServiceState.STOPPING
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("System Behavior Analytics Service stopped")
            return True
        except Exception as e:
            logger.error(f"System Behavior Analytics Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get system behavior analytics service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"System Behavior Analytics Service - {len(self._behavior_models)} behavior models",
            details={
                "behavior_models": len(self._behavior_models),
                "active_bottlenecks": len(self._bottlenecks),
                "capacity_predictions": len(self._capacity_predictions),
                "metric_samples": sum(len(samples) for samples in self._metric_samples.values()),
                "services_monitored": len(self._metric_samples)
            },
            timestamp=time.time()
        )
    
    def record_metric(self, sample: MetricSample) -> None:
        """Record a metric sample."""
        key = f"{sample.service}_{sample.metric_type.value}"
        with self._lock:
            self._metric_samples[key].append(sample)
            
            # Update resource utilization
            self._resource_utilization[sample.metric_type][sample.service] = sample.value
            
            # Update performance trend
            self._performance_trends[key].append(sample.value)
            if len(self._performance_trends[key]) > 1000:
                self._performance_trends[key] = self._performance_trends[key][-1000:]
    
    def analyze_behavior_patterns(self, service: str, metric_type: ResourceMetric) -> List[BehaviorModel]:
        """Analyze behavior patterns for a service and metric."""
        key = f"{service}_{metric_type.value}"
        
        with self._lock:
            if key not in self._metric_samples or len(self._metric_samples[key]) < 100:
                return []
            
            samples = list(self._metric_samples[key])
            values = [s.value for s in samples]
            
            # Detect patterns
            patterns = []
            
            # Detect spike
            if self._detect_spike(values):
                patterns.append(BehaviorModel(
                    model_id=self._generate_id(),
                    pattern_type=BehaviorPattern.SPIKE,
                    metric_type=metric_type,
                    service=service,
                    confidence=0.8,
                    baseline_value=statistics.mean(values[:-10]),
                    threshold_upper=max(values),
                    threshold_lower=min(values),
                    detection_time=time.time(),
                    description="Sudden spike detected"
                ))
            
            # Detect drift
            if self._detect_drift(values):
                patterns.append(BehaviorModel(
                    model_id=self._generate_id(),
                    pattern_type=BehaviorPattern.DRIFT,
                    metric_type=metric_type,
                    service=service,
                    confidence=0.7,
                    baseline_value=statistics.mean(values[:len(values)//2]),
                    threshold_upper=statistics.mean(values[len(values)//2:]),
                    threshold_lower=0.0,
                    detection_time=time.time(),
                    description="Gradual drift detected"
                ))
            
            # Detect cyclic pattern
            if self._detect_cyclic(values):
                patterns.append(BehaviorModel(
                    model_id=self._generate_id(),
                    pattern_type=BehaviorPattern.CYCLIC,
                    metric_type=metric_type,
                    service=service,
                    confidence=0.6,
                    baseline_value=statistics.mean(values),
                    threshold_upper=max(values),
                    threshold_lower=min(values),
                    detection_time=time.time(),
                    description="Cyclic pattern detected"
                ))
            
            # Store patterns
            for pattern in patterns:
                self._behavior_models[pattern.model_id] = pattern
            
            return patterns
    
    def identify_bottlenecks(self) -> List[Bottleneck]:
        """Identify system bottlenecks."""
        bottlenecks = []
        
        with self._lock:
            for metric_type, thresholds in self._thresholds.items():
                for service, value in self._resource_utilization[metric_type].items():
                    severity = "low"
                    if value >= thresholds["critical"]:
                        severity = "critical"
                    elif value >= thresholds["warning"]:
                        severity = "medium"
                    else:
                        continue
                    
                    # Calculate impact score
                    impact_score = value * 1.5 if severity == "critical" else value
                    
                    bottleneck = Bottleneck(
                        bottleneck_id=self._generate_id(),
                        service=service,
                        resource=metric_type,
                        severity=severity,
                        current_value=value,
                        threshold_value=thresholds["critical"],
                        impact_score=impact_score,
                        detected_time=time.time(),
                        recommendation=self._generate_recommendation(metric_type, severity, value)
                    )
                    
                    bottlenecks.append(bottleneck)
            
            # Sort by impact score
            bottlenecks.sort(key=lambda b: b.impact_score, reverse=True)
            
            # Store top 10 bottlenecks
            self._bottlenecks = bottlenecks[:10]
        
        return self._bottlenecks
    
    def predict_capacity_needs(self, horizon: str = "1d") -> List[CapacityPrediction]:
        """Predict capacity needs for specified time horizon."""
        predictions = []
        
        with self._lock:
            for metric_type in ResourceMetric:
                # Get recent data for this metric
                all_values = []
                for service_values in self._resource_utilization[metric_type].values():
                    all_values.append(service_values)
                
                if not all_values:
                    continue
                
                current_capacity = statistics.mean(all_values)
                
                # Simple linear prediction
                trend = self._calculate_trend(all_values)
                projected_increase = trend * self._horizon_multiplier(horizon)
                predicted_demand = current_capacity + projected_increase
                
                # Check if action required
                thresholds = self._thresholds.get(metric_type, {})
                action_required = predicted_demand >= thresholds.get("warning", 0.80)
                
                prediction = CapacityPrediction(
                    resource=metric_type,
                    current_capacity=current_capacity,
                    predicted_demand=predicted_demand,
                    time_horizon=horizon,
                    confidence=0.7,
                    action_required=action_required,
                    recommended_action=self._generate_capacity_recommendation(metric_type, predicted_demand)
                )
                
                predictions.append(prediction)
                self._capacity_predictions[f"{metric_type.value}_{horizon}"] = prediction
        
        return predictions
    
    def get_performance_trends(self, service: str, metric_type: ResourceMetric, 
                              period: str = "1h") -> Dict[str, Any]:
        """Get performance trends for a service and metric."""
        key = f"{service}_{metric_type.value}"
        
        with self._lock:
            if key not in self._performance_trends:
                return {}
            
            values = self._performance_trends[key]
            if not values:
                return {}
            
            # Filter by period
            period_seconds = {
                "1h": 3600,
                "6h": 21600,
                "1d": 86400,
                "1w": 604800
            }.get(period, 3600)
            
            cutoff_time = time.time() - period_seconds
            key_samples = self._metric_samples.get(key, deque())
            filtered_values = [s.value for s in key_samples if s.timestamp >= cutoff_time]
            
            if not filtered_values:
                return {}
            
            return {
                "service": service,
                "metric": metric_type.value,
                "period": period,
                "current_value": filtered_values[-1],
                "average": statistics.mean(filtered_values),
                "min": min(filtered_values),
                "max": max(filtered_values),
                "std_dev": statistics.stdev(filtered_values) if len(filtered_values) > 1 else 0.0,
                "trend": self._calculate_trend(filtered_values),
                "sample_count": len(filtered_values)
            }
    
    def get_resource_utilization(self) -> Dict[str, Dict[str, float]]:
        """Get current resource utilization by service."""
        with self._lock:
            return {
                metric_type.value: dict(services)
                for metric_type, services in self._resource_utilization.items()
            }
    
    def get_behavior_models(self, service: str = None) -> List[BehaviorModel]:
        """Get behavior models, optionally filtered by service."""
        with self._lock:
            if service:
                return [m for m in self._behavior_models.values() if m.service == service]
            return list(self._behavior_models.values())
    
    def _detect_spike(self, values: List[float]) -> bool:
        """Detect spike pattern."""
        if len(values) < 10:
            return False
        
        recent = values[-10:]
        baseline = statistics.mean(values[:-10])
        recent_mean = statistics.mean(recent)
        
        # Spike if recent mean is 3x baseline
        return recent_mean > baseline * 3
    
    def _detect_drift(self, values: List[float]) -> bool:
        """Detect drift pattern."""
        if len(values) < 20:
            return False
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_mean = statistics.mean(first_half)
        second_mean = statistics.mean(second_half)
        
        # Drift if means differ by more than 20%
        return abs(second_mean - first_mean) / first_mean > 0.2
    
    def _detect_cyclic(self, values: List[float]) -> bool:
        """Detect cyclic pattern."""
        if len(values) < 20:
            return False
        
        # Simple autocorrelation check
        n = len(values)
        autocorr = []
        
        for lag in range(1, min(10, n//2)):
            correlation = self._calculate_correlation(values[:-lag], values[lag:])
            autocorr.append(abs(correlation))
        
        # Cyclic if strong autocorrelation
        return any(c > 0.7 for c in autocorr)
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate correlation between two lists."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denominator_x = sum((xi - mean_x) ** 2 for xi in x)
        denominator_y = sum((yi - mean_y) ** 2 for yi in y)
        
        if denominator_x == 0 or denominator_y == 0:
            return 0.0
        
        return numerator / (denominator_x * denominator_y) ** 0.5
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend as slope."""
        if len(values) < 2:
            return 0.0
        
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        y = values
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        return slope
    
    def _horizon_multiplier(self, horizon: str) -> float:
        """Get multiplier for time horizon prediction."""
        multipliers = {
            "1h": 1.0,
            "6h": 2.0,
            "1d": 4.0,
            "1w": 8.0,
            "1m": 16.0
        }
        return multipliers.get(horizon, 1.0)
    
    def _generate_recommendation(self, metric_type: ResourceMetric, severity: str, 
                               value: float) -> str:
        """Generate recommendation for bottleneck."""
        recommendations = {
            ResourceMetric.CPU: {
                "medium": "Consider optimizing CPU-intensive operations or scaling horizontally",
                "critical": "Immediate action required: scale horizontally or optimize algorithms"
            },
            ResourceMetric.MEMORY: {
                "medium": "Consider memory optimization or increasing available memory",
                "critical": "Immediate action required: increase memory or optimize memory usage"
            },
            ResourceMetric.DISK: {
                "medium": "Consider disk cleanup or storage expansion",
                "critical": "Immediate action required: free disk space or expand storage"
            },
            ResourceMetric.NETWORK: {
                "medium": "Consider network optimization or bandwidth increase",
                "critical": "Immediate action required: increase bandwidth or optimize network usage"
            },
            ResourceMetric.GPU: {
                "medium": "Consider GPU optimization or additional GPU resources",
                "critical": "Immediate action required: add GPU resources or optimize GPU usage"
            }
        }
        
        return recommendations.get(metric_type, {}).get(severity, "Monitor and investigate")
    
    def _generate_capacity_recommendation(self, metric_type: ResourceMetric, 
                                       predicted_demand: float) -> str:
        """Generate capacity planning recommendation."""
        if predicted_demand < 0.70:
            return "Current capacity sufficient"
        elif predicted_demand < 0.85:
            return f"Consider planning {metric_type.value} capacity expansion"
        else:
            return f"Immediate {metric_type.value} capacity expansion required"
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _start_behavior_analyzer(self) -> None:
        """Start background behavior analyzer."""
        def analyze_behavior():
            while self.state == ServiceState.RUNNING:
                try:
                    # Analyze behavior patterns for all services
                    for key in list(self._metric_samples.keys()):
                        parts = key.split("_")
                        if len(parts) >= 2:
                            service = "_".join(parts[:-1])
                            metric_type = ResourceMetric(parts[-1])
                            self.analyze_behavior_patterns(service, metric_type)
                    
                    time.sleep(self._analysis_interval)
                except Exception as e:
                    logger.error(f"Behavior analysis error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=analyze_behavior, daemon=True)
        thread.start()
        logger.info("Behavior analyzer started")
    
    def _start_bottleneck_detector(self) -> None:
        """Start background bottleneck detector."""
        def detect_bottlenecks():
            while self.state == ServiceState.RUNNING:
                try:
                    self.identify_bottlenecks()
                    time.sleep(self._analysis_interval)
                except Exception as e:
                    logger.error(f"Bottleneck detection error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=detect_bottlenecks, daemon=True)
        thread.start()
        logger.info("Bottleneck detector started")
    
    def _start_capacity_planner(self) -> None:
        """Start background capacity planner."""
        def plan_capacity():
            while self.state == ServiceState.RUNNING:
                try:
                    for horizon in ["1h", "6h", "1d", "1w"]:
                        self.predict_capacity_needs(horizon)
                    time.sleep(300)  # Plan every 5 minutes
                except Exception as e:
                    logger.error(f"Capacity planning error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=plan_capacity, daemon=True)
        thread.start()
        logger.info("Capacity planner started")


# Global instance
_system_behavior_analytics_service: Optional[SystemBehaviorAnalyticsService] = None


def get_system_behavior_analytics_service() -> SystemBehaviorAnalyticsService:
    """Get global system behavior analytics service instance."""
    global _system_behavior_analytics_service
    if _system_behavior_analytics_service is None:
        _system_behavior_analytics_service = SystemBehaviorAnalyticsService()
    return _system_behavior_analytics_service