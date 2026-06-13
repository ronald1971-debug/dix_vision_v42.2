"""
operational_health_check.py
DIX VISION v42.2 — Operational Health Check System

Comprehensive health monitoring for cognitive architecture operations.
Includes component health checks, system-wide health assessment,
automated alerts, and operational status tracking.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status of a single component."""
    component_name: str
    status: HealthStatus
    last_check: datetime
    check_duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SystemHealthReport:
    """Overall system health report."""
    report_id: str
    overall_status: HealthStatus
    component_health: Dict[str, ComponentHealth] = field(default_factory=dict)
    system_metrics: Dict[str, Any] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class OperationalHealthChecker:
    """
    Operational health checker for cognitive architecture.
    
    Features:
    - Component-level health monitoring
    - Dependency health tracking
    - Performance threshold checking
    - Automated alert generation
    - Health trend analysis
    - Recovery verification
    """
    
    def __init__(self, check_interval_seconds: int = 60):
        self._lock = threading.Lock()
        self._check_interval = check_interval_seconds
        
        # Component registry
        self._components: Dict[str, Dict[str, Any]] = {}
        self._component_dependencies: Dict[str, List[str]] = {}
        
        # Health history
        self._health_history: List[SystemHealthReport] = []
        self._max_history_size = 100
        
        # Thresholds
        self._thresholds = {
            "latency_ms": 10.0,
            "error_rate": 0.05,  # 5% error rate
            "memory_mb": 12000.0,
            "cpu_percent": 80.0
        }
        
        # Monitoring status
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None
        
        logger.info("[HEALTH_CHECK] Operational health checker initialized")
    
    def register_component(
        self,
        component_name: str,
        health_check_func: callable,
        dependencies: List[str] = None
    ) -> bool:
        """Register a component for health monitoring."""
        try:
            self._components[component_name] = {
                "health_check_func": health_check_func,
                "enabled": True,
                "last_check": None,
                "failure_count": 0,
                "success_count": 0
            }
            
            self._component_dependencies[component_name] = dependencies or []
            
            logger.info(f"[HEALTH_CHECK] Component registered: {component_name}")
            return True
            
        except Exception as e:
            logger.error(f"[HEALTH_CHECK] Failed to register component {component_name}: {e}")
            return False
    
    def run_health_check(self) -> SystemHealthReport:
        """Run comprehensive health check on all components."""
        report_id = f"health_{int(datetime.utcnow().timestamp())}"
        component_health = {}
        alerts = []
        recommendations = []
        system_metrics = {}
        
        try:
            # Check all registered components
            for component_name, component_data in self._components.items():
                if not component_data["enabled"]:
                    continue
                
                start_time = time.time()
                try:
                    # Execute component health check
                    health_result = component_data["health_check_func"]()
                    
                    # Calculate check duration
                    check_duration_ms = (time.time() - start_time) * 1000
                    
                    # Determine health status
                    if health_result.get("healthy", True):
                        status = HealthStatus.HEALTHY
                        component_data["success_count"] += 1
                        component_data["failure_count"] = 0
                    else:
                        status = HealthStatus.CRITICAL
                        component_data["failure_count"] += 1
                        alerts.append(f"Component {component_name} is unhealthy")
                    
                    # Check if degraded due to high failure rate
                    if component_data["failure_count"] > 3:
                        status = HealthStatus.DEGRADED
                        recommendations.append(
                            f"Component {component_name} has {component_data['failure_count']} consecutive failures"
                        )
                    
                    # Create component health
                    component_health[component_name] = ComponentHealth(
                        component_name=component_name,
                        status=status,
                        last_check=datetime.utcnow(),
                        check_duration_ms=check_duration_ms,
                        details=health_result,
                        error_message=health_result.get("error", ""),
                        dependencies=self._component_dependencies[component_name]
                    )
                    
                    # Update last check time
                    component_data["last_check"] = datetime.utcnow()
                    
                except Exception as e:
                    check_duration_ms = (time.time() - start_time) * 1000
                    component_health[component_name] = ComponentHealth(
                        component_name=component_name,
                        status=HealthStatus.CRITICAL,
                        last_check=datetime.utcnow(),
                        check_duration_ms=check_duration_ms,
                        error_message=str(e),
                        dependencies=self._component_dependencies[component_name]
                    )
                    alerts.append(f"Component {component_name} health check failed: {e}")
            
            # Determine overall system status
            overall_status = self._determine_overall_status(component_health)
            
            # Generate system metrics
            system_metrics = {
                "components_checked": len(component_health),
                "healthy_components": sum(1 for c in component_health.values() if c.status == HealthStatus.HEALTHY),
                "degraded_components": sum(1 for c in component_health.values() if c.status == HealthStatus.DEGRADED),
                "critical_components": sum(1 for c in component_health.values() if c.status == HealthStatus.CRITICAL),
                "total_failure_count": sum(c["failure_count"] for c in self._components.values())
            }
            
            # Create report
            report = SystemHealthReport(
                report_id=report_id,
                overall_status=overall_status,
                component_health=component_health,
                system_metrics=system_metrics,
                alerts=alerts,
                recommendations=recommendations
            )
            
            # Store in history
            self._add_to_history(report)
            
            logger.info(f"[HEALTH_CHECK] Health check completed: {overall_status.value}")
            
            return report
            
        except Exception as e:
            logger.error(f"[HEALTH_CHECK] Health check failed: {e}")
            return SystemHealthReport(
                report_id=report_id,
                overall_status=HealthStatus.CRITICAL,
                alerts=["Health check system failure"],
                recommendations=["Restart health monitoring system"]
            )
    
    def _determine_overall_status(self, component_health: Dict[str, ComponentHealth]) -> HealthStatus:
        """Determine overall system health from component health."""
        if not component_health:
            return HealthStatus.UNKNOWN
        
        statuses = [c.status for c in component_health.values()]
        
        # If any component is critical, system is critical
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        
        # If any component is degraded, system is degraded
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        
        # If all components are healthy, system is healthy
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN
    
    def _add_to_history(self, report: SystemHealthReport) -> None:
        """Add report to health history."""
        with self._lock:
            self._health_history.append(report)
            
            # Maintain max history size
            if len(self._health_history) > self._max_history_size:
                self._health_history.pop(0)
    
    def start_continuous_monitoring(self) -> bool:
        """Start continuous health monitoring."""
        try:
            if self._monitoring_active:
                logger.warning("[HEALTH_CHECK] Monitoring already active")
                return False
            
            self._monitoring_active = True
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self._monitoring_thread.start()
            
            logger.info(f"[HEALTH_CHECK] Continuous monitoring started (interval: {self._check_interval}s)")
            return True
            
        except Exception as e:
            logger.error(f"[HEALTH_CHECK] Failed to start monitoring: {e}")
            return False
    
    def stop_continuous_monitoring(self) -> bool:
        """Stop continuous health monitoring."""
        try:
            self._monitoring_active = False
            if self._monitoring_thread:
                self._monitoring_thread.join(timeout=5.0)
            
            logger.info("[HEALTH_CHECK] Continuous monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"[HEALTH_CHECK] Failed to stop monitoring: {e}")
            return False
    
    def _monitoring_loop(self) -> None:
        """Monitoring loop for continuous health checks."""
        while self._monitoring_active:
            try:
                report = self.run_health_check()
                
                # Log critical issues
                if report.overall_status == HealthStatus.CRITICAL:
                    logger.critical(f"[HEALTH_CHECK] CRITICAL: System health - {len(report.alerts)} alerts")
                
                # Sleep for check interval
                time.sleep(self._check_interval)
                
            except Exception as e:
                logger.error(f"[HEALTH_CHECK] Monitoring loop error: {e}")
                time.sleep(self._check_interval)
    
    def get_health_trend(self, component_name: Optional[str] = None) -> Dict[str, Any]:
        """Get health trend for a component or overall system."""
        with self._lock:
            if not self._health_history:
                return {"trend": "insufficient_data"}
            
            # Filter for specific component if requested
            relevant_reports = self._health_history
            if component_name:
                relevant_reports = [
                    report for report in self._health_history
                    if component_name in report.component_health
                ]
            
            if len(relevant_reports) < 3:
                return {"trend": "insufficient_data"}
            
            # Analyze trend
            recent_statuses = [
                report.overall_status.value if not component_name
                else report.component_health.get(component_name, ComponentHealth(
                    component_name="unknown", status=HealthStatus.UNKNOWN,
                    last_check=datetime.utcnow(), check_duration_ms=0.0
                )).status.value
                for report in relevant_reports[-10:]
            ]
            
            # Determine trend
            if all(s == "healthy" for s in recent_statuses):
                trend = "improving"
            elif recent_statuses.count("healthy") >= len(recent_statuses) * 0.7:
                trend = "stable"
            elif recent_statuses.count("critical") > len(recent_statuses) * 0.5:
                trend = "degrading"
            else:
                trend = "fluctuating"
            
            return {
                "trend": trend,
                "recent_statuses": recent_statuses[-5:],
                "total_checks": len(relevant_reports)
            }


def register_cognitive_architecture_components(checker: OperationalHealthChecker) -> bool:
    """Register all cognitive architecture components for health monitoring."""
    try:
        # INDIRA Brain Health Check
        def indira_health_check():
            try:
                from indira_cognitive.indira_brain.concrete import ConcreteINDIRABrain
                brain = ConcreteINDIRABrain()
                
                # Quick latency test
                start_time = time.time()
                market_state = {"signal": 0.5, "regime": "TRENDING", "price": 50000.0}
                decision = brain.execute_fast_trading_decision(market_state, "BTC_USDT")
                latency_ms = (time.time() - start_time) * 1000
                
                return {
                    "healthy": latency_ms < 10.0,
                    "latency_ms": latency_ms,
                    "decision_made": decision is not None
                }
            except Exception as e:
                return {"healthy": False, "error": str(e)}
        
        checker.register_component("INDIRA_BRAIN", indira_health_check)
        
        # DYON Brain Health Check
        def dyon_health_check():
            try:
                from dyon_cognitive.dyon_brain.concrete import ConcreteDYONBrain
                brain = ConcreteDYONBrain()
                
                # Quick analysis test
                from dyon_cognitive.dyon_brain import SystemAnalysis
                analysis = SystemAnalysis(
                    analysis_id="health_check",
                    target="test",
                    analysis_type="CODE"
                )
                
                start_time = time.time()
                result = brain.analyze_system(analysis)
                latency_ms = (time.time() - start_time) * 1000
                
                return {
                    "healthy": latency_ms < 50.0,
                    "latency_ms": latency_ms,
                    "analysis_completed": result is not None
                }
            except Exception as e:
                return {"healthy": False, "error": str(e)}
        
        checker.register_component("DYON_BRAIN", dyon_health_check)
        
        # Coordination Layer Health Check
        def coordination_health_check():
            try:
                from coordination_layer.concrete import ConcreteCoordinationLayer
                coord_layer = ConcreteCoordinationLayer()
                
                # Test basic functionality - agent registration
                coord_layer.register_agent("test_agent", {"type": "test", "capabilities": ["health_check"]})
                
                # Test coordination report generation
                report = coord_layer.get_coordination_report()
                
                return {
                    "healthy": report is not None,
                    "coordination_functional": report is not None,
                    "agent_registration": True
                }
            except Exception as e:
                return {"healthy": False, "error": str(e)}
        
        checker.register_component("COORDINATION_LAYER", coordination_health_check)
        
        # Cognitive Economy Health Check
        def economy_health_check():
            try:
                from coordination_layer.cognitive_economy import get_cognitive_economy_manager
                economy = get_cognitive_economy_manager()
                
                # Quick functionality test
                state = economy.get_economy_state()
                
                return {
                    "healthy": state is not None,
                    "economy_state_available": state is not None
                }
            except Exception as e:
                return {"healthy": False, "error": str(e)}
        
        checker.register_component("COGNITIVE_ECONOMY", economy_health_check)
        
        # Shared Infrastructure Health Check
        def infrastructure_health_check():
            try:
                from shared_infrastructure.unified_memory_framework import get_unified_memory_framework
                from shared_infrastructure.planning_engine import get_planning_engine
                
                memory = get_unified_memory_framework()
                planning = get_planning_engine()
                
                return {
                    "healthy": memory is not None or planning is not None,
                    "memory_available": memory is not None,
                    "planning_available": planning is not None
                }
            except Exception as e:
                return {"healthy": False, "error": str(e)}
        
        checker.register_component("SHARED_INFRASTRUCTURE", infrastructure_health_check)
        
        logger.info("[HEALTH_CHECK] All cognitive architecture components registered")
        return True
        
    except Exception as e:
        logger.error(f"[HEALTH_CHECK] Failed to register components: {e}")
        return False


def main():
    """Main function to run health check."""
    logging.basicConfig(level=logging.INFO)
    
    print("=== DIX VISION v42.2 Operational Health Check ===\n")
    
    checker = OperationalHealthChecker()
    
    # Register components
    register_cognitive_architecture_components(checker)
    
    # Run health check
    report = checker.run_health_check()
    
    print(f"\n=== Health Check Results ===")
    print(f"Overall Status: {report.overall_status.value.upper()}")
    print(f"Components Checked: {report.system_metrics['components_checked']}")
    print(f"Healthy: {report.system_metrics['healthy_components']}")
    print(f"Degraded: {report.system_metrics['degraded_components']}")
    print(f"Critical: {report.system_metrics['critical_components']}")
    
    print(f"\n=== Component Health ===")
    for component_name, component_health in report.component_health.items():
        status_symbol = "[OK]" if component_health.status == HealthStatus.HEALTHY else "[FAIL]"
        print(f"{status_symbol} {component_name}: {component_health.status.value.upper()} "
              f"({component_health.check_duration_ms:.2f}ms)")
        if component_health.error_message:
            print(f"  Error: {component_health.error_message}")
    
    if report.alerts:
        print(f"\n=== Alerts ===")
        for alert in report.alerts:
            print(f"! {alert}")
    
    if report.recommendations:
        print(f"\n=== Recommendations ===")
        for i, recommendation in enumerate(report.recommendations, 1):
            print(f"{i}. {recommendation}")
    
    # Get health trend
    print(f"\n=== Health Trend ===")
    trend = checker.get_health_trend()
    print(f"Trend: {trend['trend']}")
    
    return report.overall_status == HealthStatus.HEALTHY


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
