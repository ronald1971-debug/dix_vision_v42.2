"""
DIX VISION ML Deployment Service

Provides model serving, versioning, A/B testing, monitoring,
and deployment automation for enhanced ML capabilities.
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
import json

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class DeploymentStatus(Enum):
    """Deployment status."""
    PENDING = "pending"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLBACK = "rollback"


class ModelType(Enum):
    """Types of models."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    REINFORCEMENT = "reinforcement"
    TRANSFORMER = "transformer"
    CUSTOM = "custom"


@dataclass
class ModelVersion:
    """Model version information."""
    version_id: str
    model_name: str
    model_type: ModelType
    model_path: str
    metrics: Dict[str, float]
    trained_at: float
    file_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = False


@dataclass
class ModelDeployment:
    """Model deployment configuration."""
    deployment_id: str
    model_version_id: str
    environment: str  # "staging", "production"
    endpoint: str
    status: DeploymentStatus = DeploymentStatus.PENDING
    deployed_at: float = 0.0
    health_check_interval: int = 60  # seconds
    request_count: int = 0
    error_count: int = 0
    avg_latency: float = 0.0


@dataclass
class ABTestConfig:
    """A/B testing configuration for models."""
    test_id: str
    model_a_version: str
    model_b_version: str
    traffic_split: float = 0.5  # 50% to each model
    metric: str = "accuracy"
    enabled: bool = True
    started_at: float = field(default_factory=time.time)
    results_a: Dict[str, float] = field(default_factory=dict)
    results_b: Dict[str, float] = field(default_factory=dict)


class MLDeploymentService(Service):
    """ML deployment service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("ml_deployment_service")
        self._model_versions: Dict[str, ModelVersion] = {}
        self._deployments: Dict[str, ModelDeployment] = {}
        self._ab_tests: Dict[str, ABTestConfig] = {}
        self._deployment_history: deque = deque(maxlen=1000)
        self._request_metrics: deque = deque(maxlen=10000)
        self._lock = threading.Lock()
        self._auto_deploy_enabled = False
        self._health_check_enabled = True
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the ML deployment service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            deployment_config = config.get("ml_deployment", {})
            self._auto_deploy_enabled = deployment_config.get("auto_deploy", False)
            self._health_check_enabled = deployment_config.get("health_check", True)
            
            logger.info("ML Deployment Service initialized")
            return True
        except Exception as e:
            logger.error(f"ML Deployment Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the ML deployment service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start health checker
            if self._health_check_enabled:
                self._start_health_checker()
            
            # Start metrics collector
            self._start_metrics_collector()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("ML Deployment Service started")
            return True
        except Exception as e:
            logger.error(f"ML Deployment Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the ML deployment service."""
        try:
            self.state = ServiceState.STOPPING
            self._health_check_enabled = False
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("ML Deployment Service stopped")
            return True
        except Exception as e:
            logger.error(f"ML Deployment Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get ML deployment service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"ML Deployment Service - {len(self._deployments)} deployments",
            details={
                "total_models": len(self._model_versions),
                "active_models": sum(1 for m in self._model_versions.values() if m.is_active),
                "total_deployments": len(self._deployments),
                "deployed_models": sum(1 for d in self._deployments.values() if d.status == DeploymentStatus.DEPLOYED),
                "ab_tests": len(self._ab_tests),
                "total_requests": len(self._request_metrics)
            },
            timestamp=time.time()
        )
    
    def register_model_version(self, version: ModelVersion) -> bool:
        """Register a new model version."""
        with self._lock:
            if version.version_id in self._model_versions:
                logger.error(f"Model version {version.version_id} already exists")
                return False
            
            self._model_versions[version.version_id] = version
            logger.info(f"Registered model version: {version.version_id}")
            return True
    
    def deploy_model(self, model_version_id: str, environment: str, 
                   endpoint: str) -> Optional[ModelDeployment]:
        """Deploy a model version to an environment."""
        with self._lock:
            model_version = self._model_versions.get(model_version_id)
            if not model_version:
                logger.error(f"Model version {model_version_id} not found")
                return None
            
            # Deactivate other models for this model name
            for version in self._model_versions.values():
                if version.model_name == model_version.model_name and version.is_active:
                    version.is_active = False
            
            model_version.is_active = True
            
            deployment = ModelDeployment(
                deployment_id=self._generate_id(),
                model_version_id=model_version_id,
                environment=environment,
                endpoint=endpoint,
                status=DeploymentStatus.DEPLOYING,
                deployed_at=time.time()
            )
            
            self._deployments[deployment.deployment_id] = deployment
            
            # Simulate deployment
            self._deploy_async(deployment)
            
            return deployment
    
    def rollback_deployment(self, deployment_id: str) -> bool:
        """Rollback a deployment."""
        with self._lock:
            deployment = self._deployments.get(deployment_id)
            if not deployment:
                return False
            
            deployment.status = DeploymentStatus.ROLLBACK
            
            # Reactivate previous model version
            model_version = self._model_versions.get(deployment.model_version_id)
            if model_version:
                model_version.is_active = False
            
            logger.info(f"Rolled back deployment: {deployment_id}")
            return True
    
    def create_ab_test(self, test: ABTestConfig) -> bool:
        """Create an A/B test for model comparison."""
        with self._lock:
            if test.test_id in self._ab_tests:
                logger.error(f"A/B test {test.test_id} already exists")
                return False
            
            self._ab_tests[test.test_id] = test
            logger.info(f"Created A/B test: {test.test_id}")
            return True
    
    def record_inference(self, model_version_id: str, input_data: Dict[str, Any],
                       output_data: Dict[str, Any], latency: float) -> None:
        """Record an inference request."""
        with self._lock:
            metric = {
                "model_version_id": model_version_id,
                "timestamp": time.time(),
                "latency": latency,
                "input_size": len(str(input_data)),
                "output_size": len(str(output_data))
            }
            
            self._request_metrics.append(metric)
            
            # Update deployment metrics
            for deployment in self._deployments.values():
                if deployment.model_version_id == model_version_id:
                    deployment.request_count += 1
                    deployment.avg_latency = (deployment.avg_latency * (deployment.request_count - 1) + latency) / deployment.request_count
                    break
    
    def get_model_version(self, version_id: str) -> Optional[ModelVersion]:
        """Get model version details."""
        with self._lock:
            return self._model_versions.get(version_id)
    
    def get_active_model(self, model_name: str) -> Optional[ModelVersion]:
        """Get active model version for a model name."""
        with self._lock:
            for version in self._model_versions.values():
                if version.model_name == model_name and version.is_active:
                    return version
            return None
    
    def get_deployment_status(self, deployment_id: str = None) -> List[ModelDeployment]:
        """Get deployment status."""
        with self._lock:
            if deployment_id:
                return [self._deployments.get(deployment_id)] if deployment_id in self._deployments else []
            
            return list(self._deployments.values())
    
    def get_ab_test_results(self, test_id: str) -> Optional[ABTestConfig]:
        """Get A/B test results."""
        with self._lock:
            return self._ab_tests.get(test_id)
    
    def get_deployment_stats(self) -> Dict[str, Any]:
        """Get deployment statistics."""
        with self._lock:
            total_requests = len(self._request_metrics)
            
            # Calculate average latency
            latencies = [m["latency"] for m in self._request_metrics]
            avg_latency = statistics.mean(latencies) if latencies else 0.0
            
            # Requests by model
            requests_by_model = defaultdict(int)
            for metric in self._request_metrics:
                requests_by_model[metric["model_version_id"]] += 1
            
            # Deployment success rate
            deployed = sum(1 for d in self._deployments.values() if d.status == DeploymentStatus.DEPLOYED)
            total_deployments = len(self._deployments)
            success_rate = deployed / total_deployments if total_deployments > 0 else 0.0
            
            return {
                "total_models": len(self._model_versions),
                "active_models": sum(1 for m in self._model_versions.values() if m.is_active),
                "total_deployments": total_deployments,
                "deployed_models": deployed,
                "success_rate": success_rate,
                "total_requests": total_requests,
                "avg_latency": avg_latency,
                "requests_by_model": dict(requests_by_model),
                "ab_tests": len(self._ab_tests)
            }
    
    def _deploy_async(self, deployment: ModelDeployment) -> None:
        """Deploy model in background."""
        def deploy():
            try:
                # Simulate deployment process
                time.sleep(2)  # Simulate deployment time
                
                deployment.status = DeploymentStatus.DEPLOYED
                logger.info(f"Deployment completed: {deployment.deployment_id}")
                
            except Exception as e:
                deployment.status = DeploymentStatus.FAILED
                logger.error(f"Deployment failed: {deployment.deployment_id} - {e}")
        
        thread = threading.Thread(target=deploy, daemon=True)
        thread.start()
    
    def _start_health_checker(self) -> None:
        """Start background health checker."""
        def check_health():
            while self._health_check_enabled and self.state == ServiceState.RUNNING:
                try:
                    with self._lock:
                        for deployment in self._deployments.values():
                            if deployment.status == DeploymentStatus.DEPLOYED:
                                # Simulate health check
                                # In production, this would make actual health check requests
                                deployment.request_count += 0  # Update counter
                                deployment.avg_latency = deployment.avg_latency * 0.99 + 0.01 * 0.1  # Decay latency
                    
                    time.sleep(deployment.health_check_interval if deployment.health_check_interval else 60)
                except Exception as e:
                    logger.error(f"Health check error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=check_health, daemon=True)
        thread.start()
        logger.info("Health checker started")
    
    def _start_metrics_collector(self) -> None:
        """Start background metrics collector."""
        def collect_metrics():
            while self.state == ServiceState.RUNNING:
                try:
                    with self._lock:
                        # Keep only recent metrics (last hour)
                        cutoff_time = time.time() - 3600
                        while self._request_metrics and self._request_metrics[0]["timestamp"] < cutoff_time:
                            self._request_metrics.popleft()
                    
                    time.sleep(300)  # Collect every 5 minutes
                except Exception as e:
                    logger.error(f"Metrics collection error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
        logger.info("Metrics collector started")
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())


# Global instance
_ml_deployment_service: Optional[MLDeploymentService] = None


def get_ml_deployment_service() -> MLDeploymentService:
    """Get global ML deployment service instance."""
    global _ml_deployment_service
    if _ml_deployment_service is None:
        _ml_deployment_service = MLDeploymentService()
    return _ml_deployment_service