"""
DIXVISION Deployment Automation
Contract-Compliant Real Implementation

Deployment automation and integration phases
"""

from .deployment_automation import (
    AutomatedDeploymentPipeline,
    ComponentHealth,
    DeploymentConfig,
    DeploymentEnvironment,
    DeploymentStatus,
    DeploymentStep,
    SystemHealthChecker,
    get_deployment_pipeline,
    get_health_checker,
)

__all__ = [
    "DeploymentEnvironment",
    "DeploymentStatus",
    "ComponentHealth",
    "DeploymentConfig",
    "DeploymentStep",
    "AutomatedDeploymentPipeline",
    "SystemHealthChecker",
    "get_deployment_pipeline",
    "get_health_checker",
]
