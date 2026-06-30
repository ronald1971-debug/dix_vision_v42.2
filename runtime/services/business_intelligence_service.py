"""
DIX VISION Business Intelligence Service

Provides performance dashboards, risk analytics, cost optimization,
decision support, and business insights for enhanced BI capabilities.
"""

from __future__ import annotations

import logging
import random
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


class MetricType(Enum):
    """Types of BI metrics."""
    PERFORMANCE = "performance"
    RISK = "risk"
    COST = "cost"
    OPERATIONAL = "operational"
    TRADING = "trading"


class RiskLevel(Enum):
    """Risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DashboardWidget:
    """Dashboard widget configuration."""
    widget_id: str
    widget_type: str  # "chart", "metric", "table", "gauge"
    title: str
    metric_type: MetricType
    data_source: str
    config: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 300  # seconds


@dataclass
class BusinessMetric:
    """Business metric value."""
    metric_id: str
    metric_name: str
    metric_type: MetricType
    value: float
    unit: str = ""
    timestamp: float = field(default_factory=time.time)
    trend: str = "stable"  # "up", "down", "stable"
    change_pct: float = 0.0


@dataclass
class RiskMetric:
    """Risk analysis metric."""
    risk_id: str
    risk_name: str
    risk_level: RiskLevel
    value: float
    threshold: float
    mitigation: str = ""
    detected_at: float = field(default_factory=time.time)


@dataclass
class CostAnalysis:
    """Cost analysis result."""
    analysis_id: str
    category: str
    current_cost: float
    projected_cost: float
    savings_potential: float
    recommendations: List[str] = field(default_factory=list)
    analyzed_at: float = field(default_factory=time.time)


class BusinessIntelligenceService(Service):
    """Business intelligence service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("business_intelligence_service")
        self._dashboards: Dict[str, List[DashboardWidget]] = defaultdict(list)
        self._metrics: Dict[str, BusinessMetric] = {}
        self._risk_metrics: Dict[str, RiskMetric] = {}
        self._cost_analyses: List[CostAnalysis] = []
        self._metric_history: deque = deque(maxlen=10000)
        self._lock = threading.Lock()
        self._auto_refresh_enabled = True
        self._refresh_interval = 300  # 5 minutes
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the business intelligence service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            bi_config = config.get("business_intelligence", {})
            self._auto_refresh_enabled = bi_config.get("auto_refresh", True)
            self._refresh_interval = bi_config.get("refresh_interval", 300)
            
            # Initialize default dashboards
            self._init_default_dashboards()
            
            # Initialize default metrics
            self._init_default_metrics()
            
            logger.info("Business Intelligence Service initialized")
            return True
        except Exception as e:
            logger.error(f"Business Intelligence Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the business intelligence service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start metric refresh
            if self._auto_refresh_enabled:
                self._start_metric_refresh()
            
            # Start risk analyzer
            self._start_risk_analyzer()
            
            # Start cost analyzer
            self._start_cost_analyzer()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Business Intelligence Service started")
            return True
        except Exception as e:
            logger.error(f"Business Intelligence Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the business intelligence service."""
        try:
            self.state = ServiceState.STOPPING
            self._auto_refresh_enabled = False
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Business Intelligence Service stopped")
            return True
        except Exception as e:
            logger.error(f"Business Intelligence Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get business intelligence service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Business Intelligence Service - {len(self._metrics)} metrics",
            details={
                "total_metrics": len(self._metrics),
                "risk_metrics": len(self._risk_metrics),
                "cost_analyses": len(self._cost_analyses),
                "dashboards": len(self._dashboards),
                "auto_refresh": self._auto_refresh_enabled
            },
            timestamp=time.time()
        )
    
    def create_dashboard(self, dashboard_id: str, widgets: List[DashboardWidget]) -> bool:
        """Create a new dashboard."""
        with self._lock:
            self._dashboards[dashboard_id] = widgets
            logger.info(f"Created dashboard: {dashboard_id}")
            return True
    
    def add_widget_to_dashboard(self, dashboard_id: str, widget: DashboardWidget) -> bool:
        """Add a widget to a dashboard."""
        with self._lock:
            if dashboard_id not in self._dashboards:
                self._dashboards[dashboard_id] = []
            
            self._dashboards[dashboard_id].append(widget)
            logger.info(f"Added widget to dashboard: {dashboard_id}")
            return True
    
    def update_metric(self, metric: BusinessMetric) -> bool:
        """Update a business metric."""
        with self._lock:
            # Calculate trend
            if metric.metric_id in self._metrics:
                old_value = self._metrics[metric.metric_id].value
                change = (metric.value - old_value) / old_value if old_value != 0 else 0.0
                metric.change_pct = change * 100
                
                if change > 0.05:
                    metric.trend = "up"
                elif change < -0.05:
                    metric.trend = "down"
                else:
                    metric.trend = "stable"
            
            self._metrics[metric.metric_id] = metric
            self._metric_history.append(metric)
            
            return True
    
    def analyze_risk(self, risk_metric: RiskMetric) -> bool:
        """Analyze and record a risk metric."""
        with self._lock:
            # Determine risk level
            if risk_metric.value >= risk_metric.threshold * 1.5:
                risk_metric.risk_level = RiskLevel.CRITICAL
            elif risk_metric.value >= risk_metric.threshold:
                risk_metric.risk_level = RiskLevel.HIGH
            elif risk_metric.value >= risk_metric.threshold * 0.7:
                risk_metric.risk_level = RiskLevel.MEDIUM
            else:
                risk_metric.risk_level = RiskLevel.LOW
            
            self._risk_metrics[risk_metric.risk_id] = risk_metric
            
            # Alert on high/critical risks
            if risk_metric.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                self.emit_event(str(EventType.AI_DECISION), {
                    "service": self.name,
                    "risk_level": risk_metric.risk_level.value,
                    "risk_name": risk_metric.risk_name,
                    "value": risk_metric.value,
                    "threshold": risk_metric.threshold
                })
            
            return True
    
    def analyze_costs(self, category: str, current_cost: float, 
                    projected_cost: float = None) -> CostAnalysis:
        """Analyze costs for a category."""
        if projected_cost is None:
            projected_cost = current_cost * 1.1  # Default 10% growth
        
        recommendations = []
        savings_potential = 0.0
        
        # Simple cost analysis logic
        if projected_cost > current_cost * 1.2:
            recommendations.append("Consider optimizing resource usage")
            savings_potential = projected_cost * 0.15
        
        if current_cost > 1000:
            recommendations.append("Review unused resources")
            savings_potential += current_cost * 0.1
        
        analysis = CostAnalysis(
            analysis_id=self._generate_id(),
            category=category,
            current_cost=current_cost,
            projected_cost=projected_cost,
            savings_potential=savings_potential,
            recommendations=recommendations
        )
        
        with self._lock:
            self._cost_analyses.append(analysis)
        
        return analysis
    
    def get_dashboard(self, dashboard_id: str) -> Optional[List[DashboardWidget]]:
        """Get dashboard widgets."""
        with self._lock:
            return self._dashboards.get(dashboard_id)
    
    def get_all_dashboards(self) -> Dict[str, List[DashboardWidget]]:
        """Get all dashboards."""
        with self._lock:
            return dict(self._dashboards)
    
    def get_metric(self, metric_id: str) -> Optional[BusinessMetric]:
        """Get a specific metric."""
        with self._lock:
            return self._metrics.get(metric_id)
    
    def get_metrics_by_type(self, metric_type: MetricType) -> List[BusinessMetric]:
        """Get metrics by type."""
        with self._lock:
            return [m for m in self._metrics.values() if m.metric_type == metric_type]
    
    def get_risk_metrics(self, risk_level: RiskLevel = None) -> List[RiskMetric]:
        """Get risk metrics, optionally filtered by level."""
        with self._lock:
            risks = list(self._risk_metrics.values())
            
            if risk_level:
                risks = [r for r in risks if r.risk_level == risk_level]
            
            return risks
    
    def get_cost_analyses(self, category: str = None) -> List[CostAnalysis]:
        """Get cost analyses."""
        with self._lock:
            analyses = self._cost_analyses
            
            if category:
                analyses = [a for a in analyses if a.category == category]
            
            return analyses[-20:]  # Return last 20 analyses
    
    def get_bi_summary(self) -> Dict[str, Any]:
        """Get comprehensive BI summary."""
        with self._lock:
            # Calculate key metrics
            total_risks = len(self._risk_metrics)
            critical_risks = sum(1 for r in self._risk_metrics.values() if r.risk_level == RiskLevel.CRITICAL)
            high_risks = sum(1 for r in self._risk_metrics.values() if r.risk_level == RiskLevel.HIGH)
            
            # Calculate cost summary
            total_cost = sum(a.current_cost for a in self._cost_analyses)
            projected_cost = sum(a.projected_cost for a in self._cost_analyses)
            total_savings = sum(a.savings_potential for a in self._cost_analyses)
            
            # Metric trends
            up_trends = sum(1 for m in self._metrics.values() if m.trend == "up")
            down_trends = sum(1 for m in self._metrics.values() if m.trend == "down")
            
            return {
                "total_metrics": len(self._metrics),
                "metric_trends": {
                    "up": up_trends,
                    "down": down_trends,
                    "stable": len(self._metrics) - up_trends - down_trends
                },
                "risk_summary": {
                    "total": total_risks,
                    "critical": critical_risks,
                    "high": high_risks,
                    "medium": sum(1 for r in self._risk_metrics.values() if r.risk_level == RiskLevel.MEDIUM),
                    "low": sum(1 for r in self._risk_metrics.values() if r.risk_level == RiskLevel.LOW)
                },
                "cost_summary": {
                    "current_total": total_cost,
                    "projected_total": projected_cost,
                    "savings_potential": total_savings,
                    "categories_analyzed": len(self._cost_analyses)
                },
                "dashboards": len(self._dashboards),
                "widget_count": sum(len(widgets) for widgets in self._dashboards.values())
            }
    
    def _init_default_dashboards(self) -> None:
        """Initialize default dashboards."""
        # Performance dashboard
        performance_widgets = [
            DashboardWidget(
                widget_id="perf_total_return",
                widget_type="metric",
                title="Total Return",
                metric_type=MetricType.PERFORMANCE,
                data_source="trading_analytics"
            ),
            DashboardWidget(
                widget_id="perf_sharpe_ratio",
                widget_type="gauge",
                title="Sharpe Ratio",
                metric_type=MetricType.PERFORMANCE,
                data_source="trading_analytics"
            )
        ]
        
        self.create_dashboard("performance", performance_widgets)
        
        # Risk dashboard
        risk_widgets = [
            DashboardWidget(
                widget_id="risk_drawdown",
                widget_type="chart",
                title="Max Drawdown",
                metric_type=MetricType.RISK,
                data_source="trading_analytics"
            ),
            DashboardWidget(
                widget_id="risk_var",
                widget_type="metric",
                title="Value at Risk",
                metric_type=MetricType.RISK,
                data_source="risk_analytics"
            )
        ]
        
        self.create_dashboard("risk", risk_widgets)
    
    def _init_default_metrics(self) -> None:
        """Initialize default metrics."""
        default_metrics = [
            BusinessMetric(
                metric_id="total_return",
                metric_name="Total Return",
                metric_type=MetricType.PERFORMANCE,
                value=0.15,
                unit="%"
            ),
            BusinessMetric(
                metric_id="sharpe_ratio",
                metric_name="Sharpe Ratio",
                metric_type=MetricType.PERFORMANCE,
                value=1.5
            ),
            BusinessMetric(
                metric_id="max_drawdown",
                metric_name="Max Drawdown",
                metric_type=MetricType.RISK,
                value=0.08,
                unit="%"
            ),
            BusinessMetric(
                metric_id="daily_volume",
                metric_name="Daily Trading Volume",
                metric_type=MetricType.TRADING,
                value=1000000,
                unit="USD"
            )
        ]
        
        for metric in default_metrics:
            self.update_metric(metric)
    
    def _start_metric_refresh(self) -> None:
        """Start background metric refresh."""
        def refresh_metrics():
            while self._auto_refresh_enabled and self.state == ServiceState.RUNNING:
                try:
                    # Simulate metric updates
                    for metric_id, metric in self._metrics.items():
                        # Add small random variation
                        variation = random.uniform(-0.01, 0.01)
                        new_value = metric.value * (1 + variation)
                        
                        updated_metric = BusinessMetric(
                            metric_id=metric.metric_id,
                            metric_name=metric.metric_name,
                            metric_type=metric.metric_type,
                            value=new_value,
                            unit=metric.unit
                        )
                        
                        self.update_metric(updated_metric)
                    
                    time.sleep(self._refresh_interval)
                except Exception as e:
                    logger.error(f"Metric refresh error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=refresh_metrics, daemon=True)
        thread.start()
        logger.info("Metric refresh started")
    
    def _start_risk_analyzer(self) -> None:
        """Start background risk analyzer."""
        def analyze_risks():
            while self.state == ServiceState.RUNNING:
                try:
                    # Analyze existing metrics for risk
                    for metric in self._metrics.values():
                        if metric.metric_type == MetricType.RISK:
                            risk_metric = RiskMetric(
                                risk_id=f"risk_{metric.metric_id}",
                                risk_name=metric.metric_name,
                                risk_level=RiskLevel.LOW,
                                value=metric.value,
                                threshold=0.1  # Default threshold
                            )
                            
                            self.analyze_risk(risk_metric)
                    
                    time.sleep(600)  # Analyze every 10 minutes
                except Exception as e:
                    logger.error(f"Risk analysis error: {e}")
                    time.sleep(120)
        
        thread = threading.Thread(target=analyze_risks, daemon=True)
        thread.start()
        logger.info("Risk analyzer started")
    
    def _start_cost_analyzer(self) -> None:
        """Start background cost analyzer."""
        def analyze_costs():
            while self.state == ServiceState.RUNNING:
                try:
                    # Analyze costs for different categories
                    categories = ["compute", "storage", "network", "licensing"]
                    
                    for category in categories:
                        current_cost = random.uniform(100, 1000)  # Simulated cost
                        self.analyze_costs(category, current_cost)
                    
                    time.sleep(3600)  # Analyze every hour
                except Exception as e:
                    logger.error(f"Cost analysis error: {e}")
                    time.sleep(300)
        
        thread = threading.Thread(target=analyze_costs, daemon=True)
        thread.start()
        logger.info("Cost analyzer started")
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())


# Global instance
_business_intelligence_service: Optional[BusinessIntelligenceService] = None


def get_business_intelligence_service() -> BusinessIntelligenceService:
    """Get global business intelligence service instance."""
    global _business_intelligence_service
    if _business_intelligence_service is None:
        _business_intelligence_service = BusinessIntelligenceService()
    return _business_intelligence_service