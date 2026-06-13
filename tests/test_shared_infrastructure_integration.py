"""
test_shared_infrastructure_integration.py
DIX VISION v42.2 — Shared Infrastructure Integration Tests

Tests for the integration of shared infrastructure components:
- Planning engine integration
- Signal processing integration
- Component sharing
- Shared memory functionality
- Backward compatibility
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime

from shared_infrastructure.shared_infrastructure_adapter import (
    SharedInfrastructureAdapter,
    SharedInfrastructureConfig,
    get_shared_infrastructure_adapter
)


class TestSharedInfrastructureAdapter:
    """Tests for the shared infrastructure adapter."""
    
    def test_singleton_pattern(self):
        """Test that adapter follows singleton pattern."""
        adapter1 = get_shared_infrastructure_adapter()
        adapter2 = get_shared_infrastructure_adapter()
        assert adapter1 is adapter2
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        adapter = SharedInfrastructureAdapter()
        result = adapter.initialize()
        assert result is True
    
    def test_plan_creation(self):
        """Test plan creation."""
        adapter = SharedInfrastructureAdapter()
        adapter.initialize()
        
        result = adapter.create_plan(
            plan_type="trading",
            goal="Execute profitable trades within risk limits",
            constraints={"max_risk": 0.5},
            requester="INDIRA"
        )
        
        assert result is not None
        assert result["success"]
        assert "plan_id" in result
        assert "steps" in result
    
    def test_signal_processing(self):
        """Test signal processing."""
        adapter = SharedInfrastructureAdapter()
        adapter.initialize()
        
        signals = [
            {"source": "crypto", "value": 0.8, "asset": "BTC"},
            {"source": "forex", "value": 0.6, "asset": "USD"}
        ]
        
        result = adapter.process_signals(
            signals=signals,
            filters={"min_threshold": 0.5}
        )
        
        assert result is not None
        assert result["success"]
        assert "processed_count" in result
    
    def test_component_registration(self):
        """Test component registration and retrieval."""
        adapter = SharedInfrastructureAdapter()
        adapter.initialize()
        
        mock_component = {"name": "test_component", "data": "test"}
        result = adapter.register_component("test", mock_component)
        
        assert result is True
        
        retrieved = adapter.get_component("test")
        assert retrieved is not None
        assert retrieved["name"] == "test_component"
    
    def test_shared_memory(self):
        """Test shared memory functionality."""
        adapter = SharedInfrastructureAdapter()
        adapter.initialize()
        
        # Set value
        result = adapter.set_shared_memory("test_key", "test_value")
        assert result is True
        
        # Get value
        retrieved = adapter.get_shared_memory("test_key")
        assert retrieved == "test_value"
    
    def test_performance_metrics(self):
        """Test performance metrics tracking."""
        adapter = SharedInfrastructureAdapter()
        adapter.initialize()
        
        # Generate some activity
        for i in range(5):
            adapter.create_plan("trading", f"Goal {i}", {}, "test")
            adapter.process_signals([{"value": 0.5}], {})
        
        metrics = adapter.get_performance_metrics()
        assert metrics["plan_count"] >= 5
        assert metrics["signal_count"] >= 5


class TestBackwardCompatibility:
    """Tests for backward compatibility."""
    
    def test_fallback_planning(self):
        """Test fallback plan creation when planning engine unavailable."""
        config = SharedInfrastructureConfig(
            use_new_planning=False,
            fallback_on_failure=True
        )
        adapter = SharedInfrastructureAdapter(config)
        adapter.initialize()
        
        result = adapter.create_plan(
            plan_type="trading",
            goal="Test fallback",
            constraints={},
            requester="test"
        )
        
        assert result is not None
        assert result["success"]
        assert result["integration_mode"] == "fallback"
    
    def test_fallback_signal_processing(self):
        """Test fallback signal processing."""
        config = SharedInfrastructureConfig(
            use_new_signal_processing=False,
            fallback_on_failure=True
        )
        adapter = SharedInfrastructureAdapter(config)
        adapter.initialize()
        
        signals = [{"value": 0.8}]
        result = adapter.process_signals(signals, {})
        
        assert result is not None
        assert result["success"]
        assert result["integration_mode"] == "fallback"


class TestPerformanceValidation:
    """Tests for performance validation."""
    
    def test_planning_performance(self):
        """Test planning performance."""
        adapter = SharedInfrastructureAdapter()
        adapter.initialize()
        
        latencies = []
        
        for i in range(30):
            start_time = time.time()
            result = adapter.create_plan(
                plan_type="trading",
                goal=f"Performance test {i}",
                constraints={"max_risk": 0.5},
                requester="test"
            )
            end_time = time.time()
            
            if result:
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
        
        # Calculate average latency
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        print(f"  Average planning latency: {avg_latency:.2f}ms")
        print(f"  Max planning latency: {max(latencies):.2f}ms")
        
        # Planning should be reasonably fast (under 100ms)
        assert avg_latency < 100.0, f"Planning too slow: {avg_latency:.2f}ms"
    
    def test_signal_processing_performance(self):
        """Test signal processing performance."""
        adapter = SharedInfrastructureAdapter()
        adapter.initialize()
        
        latencies = []
        
        for i in range(30):
            signals = [{"value": 0.5 + (i % 10) * 0.1} for _ in range(10)]
            
            start_time = time.time()
            result = adapter.process_signals(signals, {"min_threshold": 0.5})
            end_time = time.time()
            
            if result:
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
        
        # Calculate average latency
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        print(f"  Average signal processing latency: {avg_latency:.2f}ms")
        print(f"  Max signal processing latency: {max(latencies):.2f}ms")
        
        # Signal processing should be fast (under 50ms)
        assert avg_latency < 50.0, f"Signal processing too slow: {avg_latency:.2f}ms"


class TestIntegrationScenarios:
    """Tests for integration scenarios."""
    
    def test_planning_for_trading(self):
        """Test planning for trading scenario."""
        adapter = SharedInfrastructureAdapter()
        adapter.initialize()
        
        result = adapter.create_plan(
            plan_type="trading",
            goal="Execute BTC trade with 2% profit target",
            constraints={"max_risk": 0.5, "max_position": 10000},
            requester="INDIRA"
        )
        
        assert result is not None
        assert result["success"]
        # Should have planning steps
        assert len(result["steps"]) > 0
    
    def test_signal_aggregation(self):
        """Test signal aggregation from multiple sources."""
        adapter = SharedInfrastructureAdapter()
        adapter.initialize()
        
        signals = [
            {"source": "crypto_feed", "value": 0.8, "asset": "BTC"},
            {"source": "technical_analysis", "value": 0.7, "asset": "BTC"},
            {"source": "sentiment", "value": 0.6, "asset": "BTC"}
        ]
        
        result = adapter.process_signals(signals, {"min_threshold": 0.6})
        
        assert result is not None
        assert result["success"]
        # Should process signals
        assert result["processed_count"] > 0
    
    def test_component_sharing_between_agents(self):
        """Test component sharing between INDIRA and DYON."""
        adapter = SharedInfrastructureAdapter()
        adapter.initialize()
        
        # INDIRA registers a component
        adapter.register_component("indira_market_context", {"BTC": 65000, "ETH": 3500})
        
        # DYON retrieves it
        context = adapter.get_component("indira_market_context")
        
        assert context is not None
        assert context["BTC"] == 65000


def run_shared_infrastructure_tests():
    """Run all shared infrastructure integration tests."""
    print("\n" + "="*60)
    print("DIX VISION v42.2 - Shared Infrastructure Integration Tests")
    print("="*60 + "\n")
    
    # Test classes
    test_classes = [
        TestSharedInfrastructureAdapter(),
        TestBackwardCompatibility(),
        TestPerformanceValidation(),
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
        print("[SUCCESS] All shared infrastructure integration tests passed!")
    else:
        print("[FAILURE] Some shared infrastructure integration tests failed!")
    print("="*60 + "\n")
    
    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(run_shared_infrastructure_tests())
