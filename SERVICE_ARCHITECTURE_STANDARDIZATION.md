# Service Architecture Standardization Plan

## Overview
This document outlines the standardization of service architecture as specified in P1 #2, moving from script-based services to a unified service architecture.

## Current State (Script-Based Services)

### Existing Service Scripts
1. **start_dix_vision.bat** - Docker startup script
2. **launch_real_backend.bat** - Backend launch script
3. **start_complete_stack.bat** - Complete stack launch
4. **start_dashboard_stack.bat** - Dashboard launch
5. **start_system.bat** - System launch
6. **containers/utilities/start_dix_vision_system.bat** - Utility startup
7. **containers/utilities/stop_dix_vision_system.bat** - Utility stop

### Issues with Current State
- **Inconsistent service management**: Multiple scripts with different patterns
- **No unified service lifecycle**: Each script manages its own start/stop
- **Hard to monitor**: No centralized service status monitoring
- **Error handling varies**: Different error handling across scripts
- **No dependency management**: Services don't know about each other
- **Manual orchestration**: Services started manually in specific order

## Target State (Unified Service Architecture)

### Service Manager
**service_manager.py** - Centralized service lifecycle management

```python
class ServiceManager:
    """Centralized service lifecycle management"""
    
    def __init__(self):
        self.services = {}
        self.dependencies = {}
        self.status = {}
        
    def register_service(self, service: Service)
    def register_dependency(self, service: str, depends_on: str)
    def start_service(self, service: str)
    def stop_service(self, service: str)
    def restart_service(self, service: str)
    def get_service_status(self, service: str) -> ServiceStatus
    def start_all(self)
    def stop_all(self)
```

### Service Interface
```python
class Service(ABC):
    """Base class for all services"""
    
    @abstractmethod
    def start(self) -> bool
    @abstractmethod
    def stop(self) -> bool
    @abstractmethod
    def status(self) -> ServiceStatus
    @abstractmethod
    def health_check(self) -> HealthStatus
```

### Service Types
1. **BackendService** - Python backend service
2. **DashboardService** - React dashboard service
3. **DockerService** - Docker container service
4. **MemoryService** - Memory monitoring service
5. **ConfigService** - Configuration service
6. **DesktopService** - Desktop AgentOS service

## Service Architecture Design

### Core Components

#### 1. Service Manager
```python
class ServiceManager:
    """Centralized service lifecycle management"""
    
    def __init__(self):
        self.services: dict[str, Service] = {}
        self.dependencies: dict[str, list[str]] = {}
        self.status: dict[str, ServiceStatus] = {}
        self._lock = threading.Lock()
        
    def register_service(self, service: Service) -> None:
        """Register a service with the manager"""
        
    def register_dependency(self, service: str, depends_on: str) -> None:
        """Register a service dependency"""
        
    def start_service(self, service: str) -> bool:
        """Start a service with dependency resolution"""
        
    def stop_service(self, service: str) -> bool:
        """Stop a service"""
        
    def restart_service(self, service: str) -> bool:
        """Restart a service"""
        
    def get_service_status(self, service: str) -> ServiceStatus:
        """Get current service status"""
        
    def start_all(self) -> dict[str, bool]:
        """Start all services in dependency order"""
        
    def stop_all(self) -> dict[str, bool]:
        """Stop all services in reverse dependency order"""
```

#### 2. Service Base Class
```python
class Service(ABC):
    """Base class for all services"""
    
    def __init__(self, name: str):
        self.name = name
        self._status = ServiceStatus.STOPPED
        self._process = None
        self._lock = threading.Lock()
        
    @abstractmethod
    def start(self) -> bool:
        """Start the service"""
        pass
        
    @abstractmethod
    def stop(self) -> bool:
        """Stop the service"""
        pass
        
    def status(self) -> ServiceStatus:
        """Get current service status"""
        return self._status
        
    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Perform health check"""
        pass
        
    def _set_status(self, status: ServiceStatus) -> None:
        """Set service status"""
        with self._lock:
            self._status = status
```

#### 3. Service Status
```python
class ServiceStatus(Enum):
    """Service status enumeration"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    CRASHED = "crashed"
```

#### 4. Health Status
```python
@dataclass
class HealthStatus:
    """Health check result"""
    healthy: bool
    message: str
    timestamp: float
    details: dict[str, Any] = field(default_factory=dict)
```

### Service Implementations

#### Backend Service
```python
class BackendService(Service):
    """Python backend service"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        super().__init__("backend")
        self.host = host
        self.port = port
        
    def start(self) -> bool:
        """Start the backend service"""
        # Start FastAPI backend
        pass
        
    def stop(self) -> bool:
        """Stop the backend service"""
        # Stop backend process
        pass
        
    def health_check(self) -> HealthStatus:
        """Check backend health"""
        # Check /health endpoint
        pass
```

#### Dashboard Service
```python
class DashboardService(Service):
    """React dashboard service"""
    
    def __init__(self, port: int = 5173):
        super().__init__("dashboard")
        self.port = port
        
    def start(self) -> bool:
        """Start the dashboard service"""
        # Start React dev server
        pass
        
    def stop(self) -> bool:
        """Stop the dashboard service"""
        # Stop dev server
        pass
        
    def health_check(self) -> HealthStatus:
        """Check dashboard health"""
        # Check if dev server is responding
        pass
```

#### Docker Service
```python
class DockerService(Service):
    """Docker container service"""
    
    def __init__(self, compose_file: str):
        super().__init__("docker")
        self.compose_file = compose_file
        
    def start(self) -> bool:
        """Start Docker containers"""
        # Run docker-compose up
        pass
        
    def stop(self) -> bool:
        """Stop Docker containers"""
        # Run docker-compose down
        pass
        
    def health_check(self) -> HealthStatus:
        """Check container health"""
        # Check container status
        pass
```

## Service Orchestration

### Dependency Graph
```
config_service (no dependencies)
    ↓
memory_service (depends on config_service)
    ↓
backend_service (depends on config_service, memory_service)
    ↓
dashboard_service (depends on backend_service)
    ↓
docker_service (depends on backend_service, dashboard_service)
```

### Startup Sequence
1. Start config service
2. Start memory service
3. Start backend service
4. Start dashboard service
5. Start docker service

### Shutdown Sequence
1. Stop docker service
2. Stop dashboard service
3. Stop backend service
4. Stop memory service
5. Stop config service

## Integration with Bootstrap

### Bootstrap Integration
```python
# bootstrap.py
from service_manager import ServiceManager, get_service_manager

class DIXVisionBootstrap:
    def __init__(self):
        self.service_manager = get_service_manager()
        self._register_services()
        
    def _register_services(self):
        """Register all services"""
        # Register services with dependencies
        self.service_manager.register_dependency("memory", "config")
        self.service_manager.register_dependency("backend", ["config", "memory"])
        self.service_manager.register_dependency("dashboard", "backend")
        self.service_manager.register_dependency("docker", ["backend", "dashboard"])
        
    async def launch_dashboard(self, args):
        """Launch dashboard using service manager"""
        self.service_manager.start_all()
```

## Service Configuration

### Service Configuration File
```yaml
# config/services.yaml
services:
  config:
    enabled: true
    auto_start: true
    
  memory:
    enabled: true
    auto_start: true
    monitoring_interval: 5
    
  backend:
    enabled: true
    auto_start: true
    host: "127.0.0.1"
    port: 8000
    
  dashboard:
    enabled: true
    auto_start: true
    port: 5173
    
  docker:
    enabled: false  # Disabled by default
    auto_start: false
    compose_file: "docker-compose.main.yml"
```

## Monitoring and Logging

### Service Monitoring
```python
class ServiceMonitor:
    """Monitor service health and status"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.monitors = {}
        
    def start_monitoring(self):
        """Start monitoring all services"""
        
    def stop_monitoring(self):
        """Stop monitoring all services"""
        
    def get_service_metrics(self, service: str) -> dict:
        """Get service metrics"""
```

### Service Logging
```python
class ServiceLogger:
    """Centralized service logging"""
    
    def __init__(self):
        self.loggers = {}
        
    def get_service_logger(self, service: str) -> logging.Logger:
        """Get logger for a specific service"""
```

## Migration Strategy

### Phase 1: Service Interface
- [ ] Create Service base class
- [ ] Create ServiceManager
- [ ] Define service status enums
- [ ] Create health check interface

### Phase 2: Service Implementations
- [ ] Implement BackendService
- [ ] Implement DashboardService
- [ ] Implement DockerService
- [ ] Implement MemoryService
- [ ] Implement ConfigService

### Phase 3: Integration
- [ ] Integrate with bootstrap system
- [ ] Create service configuration
- [ ] Update existing launch scripts
- [ ] Add service monitoring

### Phase 4: Cleanup
- [ ] Remove old launch scripts
- [ ] Update documentation
- [ ] Archive removed code

## Benefits

### Technical Benefits
- **Unified service lifecycle**: All services managed consistently
- **Dependency management**: Automatic dependency resolution
- **Health monitoring**: Centralized health checks
- **Better error handling**: Consistent error handling across services
- **Easier testing**: Mock service interface for testing

### Operational Benefits
- **Simplified operations**: Single service manager
- **Better visibility**: Centralized service status
- **Improved reliability**: Dependency-aware startup/shutdown
- **Easier debugging**: Centralized logging and monitoring
- **Scalability**: Easy to add new services

## Testing Plan

### Unit Tests
- [ ] Service lifecycle tests
- [ ] Dependency resolution tests
- [ ] Health check tests
- [ ] Error handling tests

### Integration Tests
- [ ] Service manager integration
- [ ] Bootstrap integration
- [ ] Configuration loading
- [ ] Service monitoring

### System Tests
- [ ] Full stack startup
- [ ] Full stack shutdown
- [ ] Service restart
- [ ] Error recovery

## Timeline

- **Phase 1**: 2-3 days (service interface and manager)
- **Phase 2**: 3-4 days (service implementations)
- **Phase 3**: 2-3 days (integration and configuration)
- **Phase 4**: 1-2 days (cleanup and documentation)

**Total**: 8-12 days for complete service architecture standardization

## Next Steps

1. Create Service base class and ServiceManager
2. Implement core service types
3. Integrate with bootstrap system
4. Create service configuration
5. Update existing launch scripts to use service manager