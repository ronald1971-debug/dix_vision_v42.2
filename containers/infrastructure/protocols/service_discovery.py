"""
Container Service Discovery and API Interfaces

This module defines service discovery mechanisms and standardized API interfaces
for DIX VISION container communication.

Author: DIX VISION Service Discovery Framework
Version: 42.2
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import requests


class ServiceStatus(Enum):
    """Service health status"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class APIInterface:
    """
    Standardized API interface definition for container services.

    Each container exposes a standardized API with common endpoints
    for health checks, metrics, configuration, and operations.
    """

    def __init__(self, service_name: str, base_url: str):
        self.service_name = service_name
        self.base_url = base_url
        self.logger = logging.getLogger(f"api_interface_{service_name}")

    def get_health(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.json() if response.status_code == 200 else {"status": "error"}
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=5)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            self.logger.error(f"Metrics retrieval failed: {str(e)}")
            return {}

    def get_configuration(self) -> Dict[str, Any]:
        """Get service configuration"""
        try:
            response = requests.get(f"{self.base_url}/config", timeout=5)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            self.logger.error(f"Configuration retrieval failed: {str(e)}")
            return {}

    def execute_operation(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a service operation"""
        try:
            response = requests.post(
                f"{self.base_url}/operations/{operation}", json=parameters, timeout=30
            )
            return response.json() if response.status_code == 200 else {"error": response.text}
        except Exception as e:
            self.logger.error(f"Operation execution failed: {str(e)}")
            return {"error": str(e)}


class ServiceDiscovery:
    """
    Service discovery mechanism for DIX VISION containers.

    This provides automatic service registration, health monitoring,
    and load balancing for container communication.
    """

    def __init__(self):
        self.services = {}
        self.logger = logging.getLogger("service_discovery")
        self.health_check_interval = 30  # seconds

    def register_service(
        self,
        service_name: str,
        endpoint: str,
        health_check_path: str = "/health",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Register a new service"""
        try:
            self.services[service_name] = {
                "endpoint": endpoint,
                "health_check_path": health_check_path,
                "metadata": metadata or {},
                "registered_at": datetime.utcnow().isoformat(),
                "status": ServiceStatus.UNKNOWN,
                "last_health_check": None,
                "health_check_failures": 0,
            }

            # Initial health check
            self._check_service_health(service_name)

            self.logger.info(f"Registered service: {service_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register service {service_name}: {str(e)}")
            return False

    def unregister_service(self, service_name: str) -> bool:
        """Unregister a service"""
        if service_name in self.services:
            del self.services[service_name]
            self.logger.info(f"Unregistered service: {service_name}")
            return True
        return False

    def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service information"""
        return self.services.get(service_name)

    def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self.services.keys())

    def get_healthy_services(self) -> List[str]:
        """Get list of healthy services"""
        return [
            name
            for name, service in self.services.items()
            if service["status"] == ServiceStatus.HEALTHY
        ]

    def check_all_services(self) -> Dict[str, bool]:
        """Check health of all registered services"""
        results = {}
        for service_name in self.services.keys():
            results[service_name] = self._check_service_health(service_name)
        return results

    def _check_service_health(self, service_name: str) -> bool:
        """Check health of a specific service"""
        service = self.services.get(service_name)
        if not service:
            return False

        try:
            health_check_url = f"{service['endpoint']}{service['health_check_path']}"
            response = requests.get(health_check_url, timeout=5)

            if response.status_code == 200:
                service["status"] = ServiceStatus.HEALTHY
                service["last_health_check"] = datetime.utcnow().isoformat()
                service["health_check_failures"] = 0
                return True
            else:
                service["status"] = ServiceStatus.UNHEALTHY
                service["health_check_failures"] += 1
                return False

        except Exception as e:
            self.logger.error(f"Health check failed for {service_name}: {str(e)}")
            service["status"] = ServiceStatus.UNHEALTHY
            service["health_check_failures"] += 1
            service["last_health_check"] = datetime.utcnow().isoformat()
            return False

    def get_service_endpoint(self, service_name: str) -> Optional[str]:
        """Get the endpoint for a service (only if healthy)"""
        service = self.services.get(service_name)
        if service and service["status"] == ServiceStatus.HEALTHY:
            return service["endpoint"]
        return None

    def get_api_interface(self, service_name: str) -> Optional[APIInterface]:
        """Get API interface for a service"""
        endpoint = self.get_service_endpoint(service_name)
        if endpoint:
            return APIInterface(service_name, endpoint)
        return None


# Standard API endpoint definitions for DIX VISION containers
class APIEndpoints:
    """Standard API endpoints for all DIX VISION containers"""

    HEALTH = "/health"
    METRICS = "/metrics"
    CONFIG = "/config"
    OPERATIONS = "/operations"
    STATUS = "/status"
    GOVERNANCE = "/governance"
    LOGS = "/logs"


# Service registration configuration for DIX VISION containers
DIX_VISION_SERVICES = {
    "ccxt-service": {
        "endpoint": "http://dix-ccxt-service:8080",
        "health_check_path": "/health",
        "description": "Trading execution service",
        "category": "trading",
        "priority": "critical",
    },
    "langchain-service": {
        "endpoint": "http://dix-langchain-service:8081",
        "health_check_path": "/health",
        "description": "Cognitive enhancement service",
        "category": "cognitive",
        "priority": "critical",
    },
    "fastapi-service": {
        "endpoint": "http://dix-fastapi-service:8000",
        "health_check_path": "/health",
        "description": "Dashboard backend API service",
        "category": "api",
        "priority": "critical",
    },
    "celery-service": {
        "endpoint": "http://dix-celery-service:5555",
        "health_check_path": "/health",
        "description": "Background task queue service",
        "category": "processing",
        "priority": "critical",
    },
    "requests-service": {
        "endpoint": "http://dix-requests-service:8888",
        "health_check_path": "/health",
        "description": "HTTP client service",
        "category": "networking",
        "priority": "high",
    },
    "playwright-service": {
        "endpoint": "http://dix-playwright-service:9222",
        "health_check_path": "/health",
        "description": "Browser automation service",
        "category": "automation",
        "priority": "high",
    },
    "redis-service": {
        "endpoint": "http://redis-service:6379",
        "health_check_path": "/",
        "description": "Redis cache service",
        "category": "infrastructure",
        "priority": "critical",
    },
    "postgresql-service": {
        "endpoint": "http://postgresql-service:5432",
        "health_check_path": "/",
        "description": "PostgreSQL database service",
        "category": "infrastructure",
        "priority": "critical",
    },
}


# Example usage
if __name__ == "__main__":
    # Initialize service discovery
    discovery = ServiceDiscovery()

    # Register DIX VISION services
    for service_name, config in DIX_VISION_SERVICES.items():
        discovery.register_service(
            service_name=service_name,
            endpoint=config["endpoint"],
            health_check_path=config["health_check_path"],
            metadata=config,
        )

    # Check all services
    health_results = discovery.check_all_services()
    print(f"Health check results: {health_results}")

    # Get healthy services
    healthy_services = discovery.get_healthy_services()
    print(f"Healthy services: {healthy_services}")

    # Get API interface for a service
    ccxt_interface = discovery.get_api_interface("ccxt-service")
    if ccxt_interface:
        print(f"CCXT API interface created successfully")

    print("Service Discovery initialized successfully")
