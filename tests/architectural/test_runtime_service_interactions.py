"""
Architectural tests for verifying service interactions in the modular runtime structure.

These tests verify that services in the new runtime/ directory structure
interact correctly with each other and conform to the Service interface.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestRuntimeServiceInteractions:
    """Test suite for runtime service interactions."""
    
    def test_memory_service_import(self):
        """Test that MemoryService can be imported from the new location."""
        from runtime.services.core.memory_service import MemoryService
        assert MemoryService is not None
        
    def test_memory_service_conforms_to_interface(self):
        """Test that MemoryService conforms to the Service interface."""
        from runtime.services.core.memory_service import MemoryService
        from runtime.service_manager import Service
        
        service = MemoryService()
        assert isinstance(service, Service)
        assert hasattr(service, 'init')
        assert hasattr(service, 'start')
        assert hasattr(service, 'stop')
        assert hasattr(service, 'health')
        
    def test_event_bus_import(self):
        """Test that EventBus can be imported from runtime."""
        from runtime.event_bus import EventBus
        assert EventBus is not None
        
    def test_service_manager_import(self):
        """Test that ServiceManager can be imported from runtime."""
        from runtime.service_manager import ServiceManager
        assert ServiceManager is not None
        
    def test_config_manager_import(self):
        """Test that config manager functions can be imported from runtime."""
        from runtime.config_manager import get_config
        config = get_config()
        assert config is not None
        
    def test_memory_manager_import(self):
        """Test that MemoryManager can be imported from runtime."""
        from runtime.memory_manager import get_memory_manager
        manager = get_memory_manager()
        assert manager is not None
        
    def test_service_dependency_resolution(self):
        """Test that service dependencies are correctly resolved."""
        from runtime.service_manager import ServiceManager
        from runtime.services.core.memory_service import MemoryService
        from runtime.services.session_restoration import SessionRestorationService
        
        manager = ServiceManager()
        memory_service = MemoryService()
        session_service = SessionRestorationService()
        
        # Register services
        manager.register_service(memory_service)
        manager.register_service(session_service)
        
        # Register dependency
        manager.register_dependency("session_restoration", ["memory_service"])
        
        # Verify dependency is registered
        assert "session_restoration" in manager.dependencies
        assert manager.dependencies["session_restoration"] == ["memory_service"]
        
    def test_event_bus_publish_subscribe(self):
        """Test that EventBus publish/subscribe mechanism works."""
        from runtime.event_bus import EventBus, EventType
        
        event_bus = EventBus()
        received_events = []
        
        def event_handler(event):
            received_events.append(event)
        
        event_bus.subscribe(EventType.SERVICE_START, event_handler)
        event_bus.publish_sync("test_service", EventType.SERVICE_START, {"service": "test"})
        
        assert len(received_events) == 1
        assert received_events[0].type == EventType.SERVICE_START
        
    def test_runtime_services_location(self):
        """Test that all runtime services are in the correct location."""
        import os
        
        runtime_dir = project_root / "runtime"
        services_dir = runtime_dir / "services"
        core_services_dir = services_dir / "core"
        
        assert runtime_dir.exists()
        assert services_dir.exists()
        assert core_services_dir.exists()
        
        # Check for core services
        memory_service = core_services_dir / "memory_service.py"
        assert memory_service.exists()
        
    def test_import_paths_updated(self):
        """Test that import paths have been updated to use runtime package."""
        # Test that we can import from the new modular structure
        from runtime import service_manager, event_bus, config_manager, memory_manager
        from runtime.services import (
            ai_runtime_engine, 
            execution_engine, 
            session_restoration, 
            dashboard_service
        )
        from runtime.services.core import memory_service
        
        # If we get here without ImportError, the paths are correct
        assert True
        
    def test_service_health_interface(self):
        """Test that ServiceHealth dataclass is correctly structured."""
        from runtime.service_manager import ServiceHealth, ServiceState
        import time
        
        health = ServiceHealth(
            service="test_service",
            state=ServiceState.RUNNING,
            healthy=True,
            message="Service is healthy",
            details={"key": "value"},
            timestamp=time.time()
        )
        
        assert health.service == "test_service"
        assert health.healthy is True
        assert health.state == ServiceState.RUNNING
        
    def test_service_state_enum(self):
        """Test that ServiceState enum has all required states."""
        from runtime.service_manager import ServiceState
        
        required_states = [
            ServiceState.STOPPED,
            ServiceState.INITIALIZING,
            ServiceState.STARTING,
            ServiceState.RUNNING,
            ServiceState.STOPPING,
            ServiceState.ERROR,
            ServiceState.CRASHED
        ]
        
        for state in required_states:
            assert state in ServiceState
            
    def test_platform_abstraction_import(self):
        """Test that platform abstraction can be imported from runtime."""
        from runtime.platform_abstraction import get_platform_adapter, Platform
        adapter = get_platform_adapter()
        assert adapter is not None
        assert adapter.detect_platform() in Platform


class TestRuntimeIntegration:
    """Integration tests for the complete runtime system."""
    
    def test_runtime_module_structure(self):
        """Test that the runtime module has the expected structure."""
        runtime_dir = project_root / "runtime"
        
        expected_subdirs = [
            "services",
            "services/core",
        ]
        
        for subdir in expected_subdirs:
            assert (runtime_dir / subdir).exists()
            
    def test_runtime_init_file(self):
        """Test that runtime has an __init__.py file."""
        runtime_init = project_root / "runtime" / "__init__.py"
        assert runtime_init.exists()
        
    def test_services_init_file(self):
        """Test that services directory has an __init__.py file."""
        services_init = project_root / "runtime" / "services" / "__init__.py"
        assert services_init.exists()
        
    def test_core_services_init_file(self):
        """Test that core services directory has an __init__.py file."""
        core_init = project_root / "runtime" / "services" / "core" / "__init__.py"
        assert core_init.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
