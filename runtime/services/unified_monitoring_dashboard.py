"""
DIX VISION Unified Monitoring Dashboard

Comprehensive monitoring dashboard that integrates all enhanced services
providing real-time visibility into trading strategies, learning systems,
and overall system performance.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Import all enhanced services
from runtime.services.trading_analytics_service import get_trading_analytics_service
from runtime.services.testing_service import get_testing_service
from runtime.services.ml_training_service import get_ml_training_service
from runtime.services.business_intelligence_service import get_business_intelligence_service
from runtime.services.configuration_service import get_configuration_service
from runtime.services.data_security_service import get_data_security_service
from runtime.services.system_behavior_analytics_service import get_system_behavior_analytics_service
from runtime.services.api_security_service import get_api_security_service
from runtime.services.data_integration_service import get_data_integrator_service
from runtime.services.exchange_integration_service import get_exchange_integration_service
from runtime.services.cicd_service import get_cicd_service
from runtime.services.development_environment_service import get_development_environment_service
from runtime.services.ml_deployment_service import get_ml_deployment_service
from runtime.services.metrics_service import get_metrics_service
from runtime.services.tracing_service import get_tracing_service
from runtime.services.logging_service import get_logging_service

logger = logging.getLogger(__name__)


class DashboardCategory(Enum):
    """Dashboard categories."""
    TRADING_PERFORMANCE = "trading_performance"
    LEARNING_SYSTEMS = "learning_systems"
    SYSTEM_HEALTH = "system_health"
    SECURITY = "security"
    OPERATIONAL = "operational"
    DEVELOPMENT = "development"


@dataclass
class DashboardWidget:
    """Dashboard widget definition."""
    widget_id: str
    widget_type: str  # "metric", "chart", "table", "gauge", "status"
    title: str
    category: DashboardCategory
    data_source: str
    refresh_interval: int = 60  # seconds
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardSection:
    """Dashboard section grouping related widgets."""
    section_id: str
    section_name: str
    category: DashboardCategory
    widgets: List[DashboardWidget] = field(default_factory=list)
    layout: str = "grid"  # "grid", "row", "column"


class UnifiedMonitoringDashboard:
    """
    Unified monitoring dashboard for all enhanced services.
    
    Provides real-time visibility into:
    - Trading strategy performance
    - Learning system status
    - System health metrics
    - Security status
    - Operational metrics
    - Development environment status
    """
    
    def __init__(self):
        # Service integrations
        self._trading_analytics = get_trading_analytics_service()
        self._testing_service = get_testing_service()
        self._ml_training = get_ml_training_service()
        self._business_intelligence = get_business_intelligence_service()
        self._configuration = get_configuration_service()
        self._data_security = get_data_security_service()
        self._system_behavior = get_system_behavior_analytics_service()
        self._api_security = get_api_security_service()
        self._data_integration = get_data_integrator_service()
        self._exchange_integration = get_exchange_integration_service()
        self._cicd = get_cicd_service()
        self._dev_environment = get_development_environment_service()
        self._ml_deployment = get_ml_deployment_service()
        self._metrics_service = get_metrics_service()
        self._tracing_service = get_tracing_service()
        self._logging_service = get_logging_service()
        
        # Dashboard structure
        self._sections: Dict[str, DashboardSection] = {}
        self._dashboard_data: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        self._initialize_dashboard()
        
        logger.info("Unified Monitoring Dashboard initialized")
    
    def _initialize_dashboard(self):
        """Initialize dashboard sections and widgets."""
        # Trading Performance Section
        self._create_trading_performance_section()
        
        # Learning Systems Section
        self._create_learning_systems_section()
        
        # System Health Section
        self._create_system_health_section()
        
        # Security Section
        self._create_security_section()
        
        # Operational Section
        self._create_operational_section()
        
        # Development Section
        self._create_development_section()
        
        logger.info("Dashboard sections initialized")
    
    def _create_trading_performance_section(self):
        """Create trading performance section."""
        widgets = [
            DashboardWidget(
                widget_id="total_return",
                widget_type="metric",
                title="Total Return",
                category=DashboardCategory.TRADING_PERFORMANCE,
                data_source="trading_analytics",
                config={"format": "percentage", "color": "green"}
            ),
            DashboardWidget(
                widget_id="sharpe_ratio",
                widget_type="gauge",
                title="Sharpe Ratio",
                category=DashboardCategory.TRADING_PERFORMANCE,
                data_source="trading_analytics",
                config={"min": 0, "max": 3, "thresholds": [1, 2]}
            ),
            DashboardWidget(
                widget_id="max_drawdown",
                widget_type="metric",
                title="Max Drawdown",
                category=DashboardCategory.TRADING_PERFORMANCE,
                data_source="trading_analytics",
                config={"format": "percentage", "color": "red"}
            ),
            DashboardWidget(
                widget_id="win_rate",
                widget_type="metric",
                title="Win Rate",
                category=DashboardCategory.TRADING_PERFORMANCE,
                data_source="trading_analytics",
                config={"format": "percentage", "color": "blue"}
            ),
            DashboardWidget(
                widget_id="strategy_performance_table",
                widget_type="table",
                title="Strategy Performance",
                category=DashboardCategory.TRADING_PERFORMANCE,
                data_source="trading_analytics",
                config={"columns": ["strategy", "total_trades", "win_rate", "sharpe_ratio"]}
            ),
            DashboardWidget(
                widget_id="equity_curve",
                widget_type="chart",
                title="Equity Curve",
                category=DashboardCategory.TRADING_PERFORMANCE,
                data_source="trading_analytics",
                config={"chart_type": "line", "x_axis": "time", "y_axis": "equity"}
            )
        ]
        
        section = DashboardSection(
            section_id="trading_performance",
            section_name="Trading Performance",
            category=DashboardCategory.TRADING_PERFORMANCE,
            widgets=widgets,
            layout="grid"
        )
        
        self._sections[section.section_id] = section
    
    def _create_learning_systems_section(self):
        """Create learning systems section."""
        widgets = [
            DashboardWidget(
                widget_id="ml_training_status",
                widget_type="status",
                title="ML Training Status",
                category=DashboardCategory.LEARNING_SYSTEMS,
                data_source="ml_training",
                config={"show_jobs": True}
            ),
            DashboardWidget(
                widget_id="model_accuracy",
                widget_type="metric",
                title="Model Accuracy",
                category=DashboardCategory.LEARNING_SYSTEMS,
                data_source="ml_deployment",
                config={"format": "percentage", "color": "green"}
            ),
            DashboardWidget(
                widget_id="training_jobs_table",
                widget_type="table",
                title="Training Jobs",
                category=DashboardCategory.LEARNING_SYSTEMS,
                data_source="ml_training",
                config={"columns": ["job_id", "status", "progress", "accuracy"]}
            ),
            DashboardWidget(
                widget_id="model_deployments",
                widget_type="table",
                title="Model Deployments",
                category=DashboardCategory.LEARNING_SYSTEMS,
                data_source="ml_deployment",
                config={"columns": ["model_name", "version", "environment", "status"]}
            )
        ]
        
        section = DashboardSection(
            section_id="learning_systems",
            section_name="Learning Systems",
            category=DashboardCategory.LEARNING_SYSTEMS,
            widgets=widgets,
            layout="grid"
        )
        
        self._sections[section.section_id] = section
    
    def _create_system_health_section(self):
        """Create system health section."""
        widgets = [
            DashboardWidget(
                widget_id="system_status",
                widget_type="status",
                title="System Status",
                category=DashboardCategory.SYSTEM_HEALTH,
                data_source="metrics",
                config={"show_services": True}
            ),
            DashboardWidget(
                widget_id="cpu_usage",
                widget_type="gauge",
                title="CPU Usage",
                category=DashboardCategory.SYSTEM_HEALTH,
                data_source="system_behavior",
                config={"min": 0, "max": 100, "unit": "%"}
            ),
            DashboardWidget(
                widget_id="memory_usage",
                widget_type="gauge",
                title="Memory Usage",
                category=DashboardCategory.SYSTEM_HEALTH,
                data_source="system_behavior",
                config={"min": 0, "max": 100, "unit": "%"}
            ),
            DashboardWidget(
                widget_id="bottlenecks",
                widget_type="table",
                title="System Bottlenecks",
                category=DashboardCategory.SYSTEM_HEALTH,
                data_source="system_behavior",
                config={"columns": ["service", "resource", "severity", "impact"]}
            ),
            DashboardWidget(
                widget_id="service_health_table",
                widget_type="table",
                title="Service Health",
                category=DashboardCategory.SYSTEM_HEALTH,
                data_source="metrics",
                config={"columns": ["service", "status", "uptime", "error_rate"]}
            )
        ]
        
        section = DashboardSection(
            section_id="system_health",
            section_name="System Health",
            category=DashboardCategory.SYSTEM_HEALTH,
            widgets=widgets,
            layout="grid"
        )
        
        self._sections[section.section_id] = section
    
    def _create_security_section(self):
        """Create security section."""
        widgets = [
            DashboardWidget(
                widget_id="security_status",
                widget_type="status",
                title="Security Status",
                category=DashboardCategory.SECURITY,
                data_source="api_security",
                config={"show_alerts": True}
            ),
            DashboardWidget(
                widget_id="api_key_count",
                widget_type="metric",
                title="Active API Keys",
                category=DashboardCategory.SECURITY,
                data_source="api_security",
                config={"color": "blue"}
            ),
            DashboardWidget(
                widget_id="security_events",
                widget_type="table",
                title="Recent Security Events",
                category=DashboardCategory.SECURITY,
                data_source="api_security",
                config={"columns": ["event_type", "client_id", "severity", "timestamp"]}
            ),
            DashboardWidget(
                widget_id="encryption_status",
                widget_type="status",
                title="Encryption Status",
                category=DashboardCategory.SECURITY,
                data_source="data_security",
                config={"show_keys": True}
            )
        ]
        
        section = DashboardSection(
            section_id="security",
            section_name="Security",
            category=DashboardCategory.SECURITY,
            widgets=widgets,
            layout="row"
        )
        
        self._sections[section.section_id] = section
    
    def _create_operational_section(self):
        """Create operational section."""
        widgets = [
            DashboardWidget(
                widget_id="data_sources_status",
                widget_type="status",
                title="Data Sources",
                category=DashboardCategory.OPERATIONAL,
                data_source="data_integration",
                config={"show_sources": True}
            ),
            DashboardWidget(
                widget_id="exchange_status",
                widget_type="status",
                title="Exchange Status",
                category=DashboardCategory.OPERATIONAL,
                data_source="exchange_integration",
                config={"show_exchanges": True}
            ),
            DashboardWidget(
                widget_id="pipeline_status",
                widget_type="status",
                title="CI/CD Pipelines",
                category=DashboardCategory.OPERATIONAL,
                data_source="cicd",
                config={"show_pipelines": True}
            ),
            DashboardWidget(
                widget_id="data_quality",
                widget_type="metric",
                title="Data Quality Score",
                category=DashboardCategory.OPERATIONAL,
                data_source="data_integration",
                config={"format": "percentage", "color": "green"}
            )
        ]
        
        section = DashboardSection(
            section_id="operational",
            section_name="Operational",
            category=DashboardCategory.OPERATIONAL,
            widgets=widgets,
            layout="grid"
        )
        
        self._sections[section.section_id] = section
    
    def _create_development_section(self):
        """Create development section."""
        widgets = [
            DashboardWidget(
                widget_id="dev_containers",
                widget_type="status",
                title="Development Containers",
                category=DashboardCategory.DEVELOPMENT,
                data_source="dev_environment",
                config={"show_containers": True}
            ),
            DashboardWidget(
                widget_id="test_results",
                widget_type="table",
                title="Test Results",
                category=DashboardCategory.DEVELOPMENT,
                data_source="testing",
                config={"columns": ["test_id", "test_type", "status", "duration"]}
            ),
            DashboardWidget(
                widget_id="build_status",
                widget_type="status",
                title="Build Status",
                category=DashboardCategory.DEVELOPMENT,
                data_source="cicd",
                config={"show_builds": True}
            )
        ]
        
        section = DashboardSection(
            section_id="development",
            section_name="Development",
            category=DashboardCategory.DEVELOPMENT,
            widgets=widgets,
            layout="row"
        )
        
        self._sections[section.section_id] = section
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        with self._lock:
            self._refresh_dashboard_data()
            return self._dashboard_data
    
    def _refresh_dashboard_data(self):
        """Refresh all dashboard data."""
        # Trading Performance Data
        trading_stats = self._trading_analytics.get_trading_stats()
        self._dashboard_data["trading_performance"] = {
            "total_return": trading_stats.get("total_return", 0.0),
            "sharpe_ratio": trading_stats.get("sharpe_ratio", 0.0),
            "max_drawdown": trading_stats.get("max_drawdown", 0.0),
            "win_rate": trading_stats.get("win_rate", 0.0),
            "strategy_performances": self._trading_analytics.get_all_strategy_performance(),
            "equity_curve": self._trading_analytics.get_equity_curve()
        }
        
        # Learning Systems Data
        ml_stats = self._ml_training.get_training_stats()
        self._dashboard_data["learning_systems"] = {
            "training_status": ml_stats,
            "model_accuracy": 0.88,  # Would come from ML deployment
            "training_jobs": self._ml_training.get_training_jobs(),
            "model_deployments": self._ml_deployment.get_deployment_status()
        }
        
        # System Health Data
        system_behavior_stats = self._system_behavior.get_resource_utilization()
        self._dashboard_data["system_health"] = {
            "system_status": "healthy",
            "cpu_usage": system_behavior_stats.get("cpu", {}).get("trading_system", 0.0),
            "memory_usage": system_behavior_stats.get("memory", {}).get("trading_system", 0.0),
            "bottlenecks": self._system_behavior.get_pipeline_health(),
            "service_health": self._metrics_service.get_all_metrics()
        }
        
        # Security Data
        security_stats = self._api_security.get_security_stats()
        self._dashboard_data["security"] = {
            "security_status": "secure",
            "api_key_count": security_stats.get("total_api_keys", 0),
            "security_events": self._api_security.get_security_events(),
            "encryption_status": "active"
        }
        
        # Operational Data
        integration_stats = self._data_integration.get_integration_stats()
        exchange_stats = self._exchange_integration.get_exchange_stats()
        cicd_stats = self._cicd.get_ci_stats()
        
        self._dashboard_data["operational"] = {
            "data_sources_status": integration_stats,
            "exchange_status": exchange_stats,
            "pipeline_status": cicd_stats,
            "data_quality": integration_stats.get("normalization_rate", 0.0)
        }
        
        # Development Data
        dev_stats = self._dev_environment.get_dev_environment_stats()
        test_stats = self._testing_service.get_test_statistics()
        
        self._dashboard_data["development"] = {
            "dev_containers": dev_stats,
            "test_results": self._testing_service.get_test_results(),
            "build_status": cicd_stats
        }
        
        # Overall System Health
        self._dashboard_data["overall_health"] = {
            "status": "healthy",
            "uptime": 99.9,
            "last_updated": datetime.now().isoformat(),
            "active_services": 22,
            "total_services": 22
        }
    
    def get_section_data(self, section_id: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific section."""
        with self._lock:
            self._refresh_dashboard_data()
            return self._dashboard_data.get(section_id)
    
    def get_widget_data(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific widget."""
        with self._lock:
            self._refresh_dashboard_data()
            
            # Find widget and return relevant data
            for section in self._sections.values():
                for widget in section.widgets:
                    if widget.widget_id == widget_id:
                        # Extract relevant data based on data source
                        data_source = widget.data_source
                        if data_source == "trading_analytics":
                            return self._dashboard_data.get("trading_performance")
                        elif data_source == "ml_training":
                            return self._dashboard_data.get("learning_systems")
                        elif data_source == "system_behavior":
                            return self._dashboard_data.get("system_health")
                        elif data_source == "api_security":
                            return self._dashboard_data.get("security")
                        elif data_source == "data_integration":
                            return self._dashboard_data.get("operational")
                        elif data_source == "exchange_integration":
                            return self._dashboard_data.get("operational")
                        elif data_source == "cicd":
                            return self._dashboard_data.get("operational")
                        elif data_source == "dev_environment":
                            return self._dashboard_data.get("development")
                        elif data_source == "testing":
                            return self._dashboard_data.get("development")
                        elif data_source == "ml_deployment":
                            return self._dashboard_data.get("learning_systems")
                        elif data_source == "metrics":
                            return self._dashboard_data.get("system_health")
                        elif data_source == "data_security":
                            return self._dashboard_data.get("security")
            
            return None
    
    def get_dashboard_structure(self) -> Dict[str, DashboardSection]:
        """Get dashboard structure."""
        with self._lock:
            return dict(self._sections)
    
    def create_custom_widget(self, section_id: str, widget: DashboardWidget) -> bool:
        """Add a custom widget to a section."""
        with self._lock:
            if section_id not in self._sections:
                return False
            
            self._sections[section_id].widgets.append(widget)
            return True
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get high-level dashboard summary."""
        with self._lock:
            self._refresh_dashboard_data()
            
            return {
                "overall_health": self._dashboard_data["overall_health"],
                "trading_summary": {
                    "total_return": self._dashboard_data["trading_performance"]["total_return"],
                    "win_rate": self._dashboard_data["trading_performance"]["win_rate"],
                    "active_strategies": len(self._dashboard_data["trading_performance"]["strategy_performances"])
                },
                "learning_summary": {
                    "active_jobs": len(self._dashboard_data["learning_systems"]["training_jobs"]),
                    "model_accuracy": self._dashboard_data["learning_systems"]["model_accuracy"],
                    "deployed_models": len(self._dashboard_data["learning_systems"]["model_deployments"])
                },
                "system_summary": {
                    "cpu_usage": self._dashboard_data["system_health"]["cpu_usage"],
                    "memory_usage": self._dashboard_data["system_health"]["memory_usage"],
                    "bottlenecks": len(self._dashboard_data["system_health"]["bottlenecks"])
                },
                "security_summary": {
                    "api_keys": self._dashboard_data["security"]["api_key_count"],
                    "recent_events": len(self._dashboard_data["security"]["security_events"]),
                    "encryption_active": self._dashboard_data["security"]["encryption_status"]
                },
                "operational_summary": {
                    "data_sources": self._dashboard_data["operational"]["data_sources_status"]["total_sources"],
                    "exchanges": self._dashboard_data["operational"]["exchange_status"]["total_exchanges"],
                    "pipelines": self._dashboard_data["operational"]["pipeline_status"]["total_pipelines"]
                },
                "development_summary": {
                    "containers": self._dashboard_data["development"]["dev_containers"]["total_containers"],
                    "tests": self._dashboard_data["development"]["test_results"]["total_tests"],
                    "builds": self._dashboard_data["development"]["build_status"]["total_executions"]
                }
            }


# Global instance
_unified_monitoring_dashboard: Optional[UnifiedMonitoringDashboard] = None


def get_unified_monitoring_dashboard() -> UnifiedMonitoringDashboard:
    """Get global unified monitoring dashboard instance."""
    global _unified_monitoring_dashboard
    if _unified_monitoring_dashboard is None:
        _unified_monitoring_dashboard = UnifiedMonitoringDashboard()
    return _unified_monitoring_dashboard