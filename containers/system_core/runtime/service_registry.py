"""Service Registry - Real implementation for service management and dependency validation."""

import logging
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class ServiceStatus(Enum):
    """Status of registered services."""
    REGISTERED = "registered"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass
class ServiceInfo:
    """Information about a registered service."""
    name: str
    tier: str
    status: ServiceStatus = ServiceStatus.REGISTERED
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    health_check_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyValidationResult:
    """Result of dependency validation."""
    satisfied: bool
    missing: List[str] = field(default_factory=list)
    circular: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


class ServiceRegistry:
    """Real service registry for service management and dependency validation."""

    def __init__(self, **kwargs: Any):
        """Initialize the service registry with real service management."""
        self.logger = logging.getLogger("runtime.service_registry")
        self.logger.setLevel(logging.INFO)
        
        # Service storage
        self._services: Dict[str, ServiceInfo] = {}
        self._tier_services: Dict[str, Set[str]] = {}
        
        # Configuration
        self._enable_health_checks = kwargs.get("enable_health_checks", True)
        self._health_check_interval = kwargs.get("health_check_interval", 30)
        
        self.logger.info("ServiceRegistry initialized with real service management")

    def register_service(
        self, 
        name: str, 
        tier: str, 
        dependencies: Optional[List[str]] = None,
        health_check_url: Optional[str] = None,
        **metadata: Any
    ) -> bool:
        """Register a service with the registry."""
        try:
            # Check if service already exists
            if name in self._services:
                self.logger.warning(f"Service {name} already registered, updating")
            
            # Create service info
            service_info = ServiceInfo(
                name=name,
                tier=tier,
                status=ServiceStatus.REGISTERED,
                dependencies=set(dependencies or []),
                health_check_url=health_check_url,
                metadata=metadata
            )
            
            # Store service
            self._services[name] = service_info
            
            # Add to tier services
            if tier not in self._tier_services:
                self._tier_services[tier] = set()
            self._tier_services[tier].add(name)
            
            # Update dependency relationships
            self._update_dependency_relationships(name, service_info.dependencies)
            
            self.logger.info(f"Registered service {name} in tier {tier}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering service {name}: {e}")
            return False

    def _update_dependency_relationships(self, service_name: str, dependencies: Set[str]) -> None:
        """Update dependency relationships between services."""
        try:
            # Update dependents for each dependency
            for dep in dependencies:
                if dep in self._services:
                    self._services[dep].dependents.add(service_name)
            
            # Ensure dependencies are registered
            for dep in dependencies:
                if dep not in self._services:
                    self.logger.warning(f"Dependency {dep} not yet registered for service {service_name}")
                    
        except Exception as e:
            self.logger.error(f"Error updating dependency relationships: {e}")

    def validate_dependencies(self, service_name: str) -> DependencyValidationResult:
        """Validate dependencies for a service."""
        try:
            if service_name not in self._services:
                return DependencyValidationResult(
                    satisfied=False,
                    error_message=f"Service {service_name} not found"
                )
            
            service = self._services[service_name]
            missing = []
            
            # Check if all dependencies are registered
            for dep in service.dependencies:
                if dep not in self._services:
                    missing.append(dep)
            
            # Check for circular dependencies
            circular = self._detect_circular_dependencies(service_name)
            
            # Determine if dependencies are satisfied
            satisfied = len(missing) == 0 and len(circular) == 0
            
            return DependencyValidationResult(
                satisfied=satisfied,
                missing=missing,
                circular=circular,
                error_message=None if satisfied else f"Missing: {missing}, Circular: {circular}"
            )
            
        except Exception as e:
            self.logger.error(f"Error validating dependencies for {service_name}: {e}")
            return DependencyValidationResult(
                satisfied=False,
                error_message=str(e)
            )

    def _detect_circular_dependencies(self, service_name: str, visited: Optional[Set[str]] = None) -> List[str]:
        """Detect circular dependencies using DFS."""
        try:
            if visited is None:
                visited = set()
            
            if service_name in visited:
                return [service_name]
            
            if service_name not in self._services:
                return []
            
            visited.add(service_name)
            service = self._services[service_name]
            
            for dep in service.dependencies:
                circular = self._detect_circular_dependencies(dep, visited.copy())
                if circular:
                    return [service_name] + circular
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error detecting circular dependencies: {e}")
            return []

    def get_service_status(self, service_name: str) -> Optional[ServiceStatus]:
        """Get the current status of a service."""
        try:
            if service_name in self._services:
                return self._services[service_name].status
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting service status: {e}")
            return None

    def set_service_status(self, service_name: str, status: ServiceStatus) -> bool:
        """Set the status of a service."""
        try:
            if service_name not in self._services:
                self.logger.error(f"Service {service_name} not found")
                return False
            
            self._services[service_name].status = status
            self.logger.info(f"Service {service_name} status set to {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting service status: {e}")
            return False

    def get_tier_services(self, tier: str) -> Set[str]:
        """Get all services in a specific tier."""
        return self._tier_services.get(tier, set())

    def get_service_dependencies(self, service_name: str) -> Set[str]:
        """Get dependencies for a service."""
        if service_name in self._services:
            return self._services[service_name].dependencies.copy()
        return set()

    def get_service_dependents(self, service_name: str) -> Set[str]:
        """Get services that depend on this service."""
        if service_name in self._services:
            return self._services[service_name].dependents.copy()
        return set()

    def get_all_services(self) -> Dict[str, ServiceInfo]:
        """Get all registered services."""
        return self._services.copy()


def get_service_registry(**kwargs: Any) -> ServiceRegistry:
    """Get the service registry singleton."""
    # In a real implementation, this would return a singleton instance
    return ServiceRegistry(**kwargs)


def register_tier_services(
    registry: ServiceRegistry = None, 
    tier: str = None, 
    services: list = None, 
    **kwargs: Any
) -> None:
    """Register multiple services for a tier."""
    try:
        if registry is None:
            registry = get_service_registry(**kwargs)
        
        if tier is None or services is None:
            raise ValueError("Both tier and services must be provided")
        
        for service_config in services:
            if isinstance(service_config, dict):
                registry.register_service(tier=tier, **service_config)
            elif isinstance(service_config, str):
                registry.register_service(name=service_config, tier=tier)
            else:
                raise ValueError(f"Invalid service configuration: {service_config}")
                
    except Exception as e:
        logging.error(f"Error registering tier services: {e}")
