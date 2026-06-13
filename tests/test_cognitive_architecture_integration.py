"""
test_cognitive_architecture_integration.py
DIX VISION v42.2 — Cognitive Architecture Integration Tests

Comprehensive integration tests for the new cognitive architecture components:
- Preservation layer integration
- Component connection manager
- Configuration loading
- Health monitoring
- Graceful degradation
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import threading
from datetime import datetime

from preservation_layer import PreservationLayer, get_preservation_layer
from system.component_connection_manager import (
    ComponentConnectionManager,
    get_connection_manager,
    ConnectionState,
    ConnectionConfig,
    ConnectionStatus
)


class TestPreservationLayer:
    """Tests for the preservation layer."""
    
    def test_singleton_pattern(self):
        """Test that preservation layer follows singleton pattern."""
        layer1 = get_preservation_layer()
        layer2 = get_preservation_layer()
        assert layer1 is layer2
    
    def test_legacy_engines_initialization(self):
        """Test legacy engines initialization."""
        layer = PreservationLayer()
        result = layer.initialize_legacy_engines()
        # Should succeed even if some engines fail to import
        assert result is True
    
    def test_new_architecture_connection(self):
        """Test connecting new architecture components."""
        layer = PreservationLayer()
        
        # Mock components
        mock_indira = {"name": "INDIRA"}
        mock_dyon = {"name": "DYON"}
        mock_coordination = {"name": "Coordination"}
        
        result = layer.connect_new_architecture(
            indira_brain=mock_indira,
            dyon_brain=mock_dyon,
            coordination_layer=mock_coordination
        )
        
        assert result is True
    
    def test_migration_status_tracking(self):
        """Test migration status tracking."""
        layer = PreservationLayer()
        
        # Check that migration status dictionary exists
        assert hasattr(layer, '_migration_status')
        assert isinstance(layer._migration_status, dict)


class TestComponentConnectionManager:
    """Tests for the component connection manager."""
    
    def test_singleton_pattern(self):
        """Test that connection manager follows singleton pattern."""
        manager1 = get_connection_manager()
        manager2 = get_connection_manager()
        assert manager1 is manager2
    
    def test_component_registration(self):
        """Test component registration."""
        manager = ComponentConnectionManager()
        
        config = ConnectionConfig(
            component_name="test_component",
            component_type="brain",
            enabled=True,
            required=True
        )
        
        result = manager.register_component("test_component", "brain", config)
        assert result is True
        
        status = manager.get_connection_status("test_component")
        assert status is not None
        assert status.state == ConnectionState.DISCONNECTED
    
    def test_component_connection(self):
        """Test component connection."""
        manager = ComponentConnectionManager()
        
        manager.register_component("test_component", "brain")
        
        mock_component = {"name": "test"}
        result = manager.connect_component("test_component", mock_component)
        
        assert result is True
        status = manager.get_connection_status("test_component")
        assert status.state == ConnectionState.CONNECTED
    
    def test_component_retrieval(self):
        """Test retrieving connected components."""
        manager = ComponentConnectionManager()
        
        manager.register_component("test_component", "brain")
        
        mock_component = {"name": "test"}
        manager.connect_component("test_component", mock_component)
        
        retrieved = manager.get_component("test_component")
        assert retrieved is not None
        assert retrieved["name"] == "test"
    
    def test_component_disconnection(self):
        """Test component disconnection."""
        manager = ComponentConnectionManager()
        
        manager.register_component("test_component", "brain")
        
        mock_component = {"name": "test"}
        manager.connect_component("test_component", mock_component)
        
        result = manager.disconnect_component("test_component")
        assert result is True
        
        status = manager.get_connection_status("test_component")
        assert status.state == ConnectionState.DISCONNECTED
    
    def test_health_monitoring(self):
        """Test health monitoring of components."""
        manager = ComponentConnectionManager()
        
        config = ConnectionConfig(
            component_name="test_component",
            component_type="brain",
            health_check_interval_ms=100
        )
        manager.register_component("test_component", "brain", config)
        
        mock_component = {"name": "test"}
        manager.connect_component("test_component", mock_component)
        
        # Wait for at least one health check
        time.sleep(0.2)
        
        status = manager.get_connection_status("test_component")
        assert status.last_health_check is not None
    
    def test_graceful_degradation(self):
        """Test graceful degradation on component failure."""
        manager = ComponentConnectionManager()
        
        config = ConnectionConfig(
            component_name="test_component",
            component_type="brain",
            graceful_degradation=True
        )
        manager.register_component("test_component", "brain", config)
        
        mock_component = {"name": "test"}
        manager.connect_component("test_component", mock_component)
        
        # Simulate degradation
        manager._degrade_component("test_component", "Simulated failure")
        
        status = manager.get_connection_status("test_component")
        assert status.state == ConnectionState.DEGRADED
        assert status.degradation_level > 0
    
    def test_connection_failure_handling(self):
        """Test connection failure handling."""
        manager = ComponentConnectionManager()
        
        config = ConnectionConfig(
            component_name="test_component",
            component_type="brain",
            max_retries=2,
            retry_delay_ms=100
        )
        manager.register_component("test_component", "brain", config)
        
        # Simulate connection failure
        manager._handle_connection_failure("test_component", "Simulated failure")
        
        status = manager.get_connection_status("test_component")
        assert status.failure_count > 0
        assert status.last_failure_time is not None
    
    def test_on_connect_callback(self):
        """Test on-connect callback."""
        manager = ComponentConnectionManager()
        
        callback_called = threading.Event()
        callback_data = []
        
        def callback(component_name, component_instance):
            callback_data.append((component_name, component_instance))
            callback_called.set()
        
        manager.register_on_connect("test_component", callback)
        manager.register_component("test_component", "brain")
        
        mock_component = {"name": "test"}
        manager.connect_component("test_component", mock_component, callback)
        
        callback_called.wait(timeout=1.0)
        assert callback_called.is_set()
        assert len(callback_data) > 0
    
    def test_on_disconnect_callback(self):
        """Test on-disconnect callback."""
        manager = ComponentConnectionManager()
        
        callback_called = threading.Event()
        callback_data = []
        
        def callback(component_name):
            callback_data.append(component_name)
            callback_called.set()
        
        manager.register_on_disconnect("test_component", callback)
        manager.register_component("test_component", "brain")
        
        mock_component = {"name": "test"}
        manager.connect_component("test_component", mock_component)
        manager.disconnect_component("test_component")
        
        callback_called.wait(timeout=1.0)
        assert callback_called.is_set()
        assert "test_component" in callback_data
    
    def test_system_health(self):
        """Test system health reporting."""
        manager = ComponentConnectionManager()
        
        # Register multiple components
        for i in range(3):
            manager.register_component(f"component_{i}", "brain")
            mock_component = {"name": f"test_{i}"}
            manager.connect_component(f"component_{i}", mock_component)
        
        health = manager.get_system_health()
        
        assert health["total_components"] == 3
        assert health["connected_components"] == 3
        assert health["health_percentage"] == 100.0
        assert health["system_healthy"] is True
    
    def test_required_component_failure(self):
        """Test that required component is marked as required."""
        manager = ComponentConnectionManager()
        
        config = ConnectionConfig(
            component_name="required_component",
            component_type="brain",
            required=True
        )
        manager.register_component("required_component", "brain", config)
        
        # Check that the component is registered as required
        status = manager.get_connection_status("required_component")
        assert status is not None
        
        # Check the config is stored correctly
        stored_config = manager._connection_configs["required_component"]
        assert stored_config.required is True


class TestConfigurationLoading:
    """Tests for configuration loading."""
    
    def test_config_file_exists(self):
        """Test that the configuration file exists."""
        import os
        config_path = "config/cognitive_architecture_config.yaml"
        assert os.path.exists(config_path)
    
    def test_config_structure(self):
        """Test that configuration has required structure."""
        import yaml
        
        config_path = "config/cognitive_architecture_config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "cognitive_architecture" in config
        assert config["cognitive_architecture"]["enabled"] is True
        
        # Check required sections
        required_sections = [
            "preservation_layer",
            "indira_brain",
            "dyon_brain",
            "coordination_layer",
            "cognitive_economy",
            "operating_modes",
            "learning_gate",
            "planning_engine",
            "signal_processing"
        ]
        
        for section in required_sections:
            assert section in config["cognitive_architecture"]
    
    def test_config_values(self):
        """Test that configuration values are reasonable."""
        import yaml
        
        config_path = "config/cognitive_architecture_config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check some key values
        assert config["cognitive_architecture"]["preservation_layer"]["enabled"] is True
        assert config["cognitive_architecture"]["indira_brain"]["sub_5ms_target"] is True
        assert config["cognitive_architecture"]["operating_modes"]["default_mode"] == "active"


class TestIntegrationScenarios:
    """Integration scenario tests."""
    
    def test_bootstrap_integration(self):
        """Test that preservation layer integrates with bootstrap."""
        # This would test the actual bootstrap integration
        # For now, just verify the files are in place
        import os
        
        bootstrap_file = "bootstrap_kernel.py"
        preservation_file = "preservation_layer.py"
        
        assert os.path.exists(bootstrap_file)
        assert os.path.exists(preservation_file)
        
        # Check that bootstrap imports preservation layer
        with open(bootstrap_file, 'r') as f:
            bootstrap_content = f.read()
        
        assert "preservation_layer" in bootstrap_content.lower()
    
    def test_component_workflow(self):
        """Test complete component workflow."""
        manager = ComponentConnectionManager()
        
        # Register
        manager.register_component("test_component", "brain")
        
        # Connect
        mock_component = {"name": "test"}
        manager.connect_component("test_component", mock_component)
        
        # Retrieve
        retrieved = manager.get_component("test_component")
        assert retrieved is not None
        
        # Disconnect
        manager.disconnect_component("test_component")
        
        # Verify disconnected
        status = manager.get_connection_status("test_component")
        assert status.state == ConnectionState.DISCONNECTED
    
    def test_multiple_components(self):
        """Test managing multiple components."""
        manager = ComponentConnectionManager()
        
        components = []
        for i in range(5):
            component_name = f"component_{i}"
            manager.register_component(component_name, "brain")
            mock_component = {"name": f"test_{i}"}
            manager.connect_component(component_name, mock_component)
            components.append(component_name)
        
        # Verify all connected
        for component_name in components:
            status = manager.get_connection_status(component_name)
            assert status.state == ConnectionState.CONNECTED
        
        # Check system health
        health = manager.get_system_health()
        assert health["total_components"] == 5
        assert health["connected_components"] == 5
        
        # Disconnect all
        for component_name in components:
            manager.disconnect_component(component_name)
        
        # Verify all disconnected
        health = manager.get_system_health()
        assert health["connected_components"] == 0


def run_integration_tests():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("DIX VISION v42.2 - Cognitive Architecture Integration Tests")
    print("="*60 + "\n")
    
    # Test classes
    test_classes = [
        TestPreservationLayer(),
        TestComponentConnectionManager(),
        TestConfigurationLoading(),
        TestIntegrationScenarios()
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\nTesting {class_name}:")
        print("-" * 60)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith("test_")]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_class, method_name)
                method()
                passed_tests += 1
                print(f"  [PASS] {method_name}")
            except Exception as e:
                failed_tests += 1
                print(f"  [FAIL] {method_name}: {e}")
    
    print("\n" + "="*60)
    print(f"Test Results: {passed_tests}/{total_tests} passed, {failed_tests} failed")
    if failed_tests == 0:
        print("[SUCCESS] All integration tests passed!")
    else:
        print("[FAILURE] Some integration tests failed!")
    print("="*60 + "\n")
    
    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(run_integration_tests())
