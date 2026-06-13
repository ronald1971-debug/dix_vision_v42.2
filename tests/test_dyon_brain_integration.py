"""
test_dyon_brain_integration.py
DIX VISION v42.2 — DYON Brain Integration Tests

Tests for the integration of the new DYON brain with the existing system monitoring:
- Adapter initialization
- System analysis with multiple reasoning modes
- Performance validation (<100ms target)
- Fallback behavior
- Preservation layer integration
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import threading
from datetime import datetime

from system_monitor.dyon_brain_adapter import (
    DyonBrainAdapter,
    DYONBrainConfig,
    get_dyon_brain_adapter
)
from system_monitor.dyon_engine import DyonEngine


class TestDyonBrainAdapter:
    """Tests for the DYON brain adapter."""
    
    def test_singleton_pattern(self):
        """Test that adapter follows singleton pattern."""
        adapter1 = get_dyon_brain_adapter()
        adapter2 = get_dyon_brain_adapter()
        assert adapter1 is adapter2
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        adapter = DyonBrainAdapter()
        result = adapter.initialize()
        assert result is True
    
    def test_system_issue_analysis(self):
        """Test basic system issue analysis."""
        adapter = DyonBrainAdapter()
        adapter.initialize()
        
        # Mock system issue
        issue = "High latency detected in trading component"
        context = {
            "component": "trading_engine",
            "latency_ms": 150.0,
            "health_status": "degraded"
        }
        
        result = adapter.analyze_system_issue(
            issue=issue,
            context=context,
            reasoning_mode="causal"
        )
        
        assert result is not None
        assert "analysis_type" in result
        assert "conclusion" in result
        assert "confidence" in result
        assert "latency_ms" in result
    
    def test_multiple_reasoning_modes(self):
        """Test analysis with different reasoning modes."""
        adapter = DyonBrainAdapter()
        adapter.initialize()
        
        issue = "Memory usage spike in system"
        context = {"component": "memory_manager", "memory_usage_mb": 8192}
        
        reasoning_modes = ["causal", "deductive", "inductive", "abductive"]
        
        for mode in reasoning_modes:
            result = adapter.analyze_system_issue(
                issue=issue,
                context=context,
                reasoning_mode=mode
            )
            
            assert result is not None
            assert "reasoning_mode" in result
    
    def test_performance_metrics(self):
        """Test performance metrics tracking."""
        adapter = DyonBrainAdapter()
        adapter.initialize()
        
        # Process some analyses
        for i in range(10):
            issue = f"Test issue {i}"
            context = {"test": True}
            
            adapter.analyze_system_issue(
                issue=issue,
                context=context,
                reasoning_mode="causal"
            )
        
        metrics = adapter.get_performance_metrics()
        assert metrics["total_analyses"] >= 10
        assert "average_latency_ms" in metrics
        assert "reasoning_mode_usage" in metrics


class TestDyonEngineIntegration:
    """Tests for DYON engine integration with new brain."""
    
    def test_engine_initialization_with_adapter(self):
        """Test that engine initializes with brain adapter."""
        engine = DyonEngine()
        
        # Engine should have adapter attribute
        assert hasattr(engine, '_dyon_brain_adapter')
    
    def test_engine_system_issue_analysis(self):
        """Test that engine can analyze system issues with new brain integration."""
        engine = DyonEngine()
        
        # Mock system issue
        issue = "Connection failure to data source"
        context = {
            "source": "crypto_feed",
            "error": "timeout",
            "retry_count": 3
        }
        
        # Analyze system issue
        result = engine.analyze_system_issue_with_new_architecture(issue, context)
        
        assert result is not None
        assert "analysis_type" in result
        assert "conclusion" in result
        assert "issue" in result
    
    def test_fallback_behavior(self):
        """Test fallback behavior when new brain fails."""
        config = DYONBrainConfig(
            use_new_brain=True,
            fallback_on_failure=True
        )
        adapter = DyonBrainAdapter(config)
        adapter.initialize()
        
        # Disable new brain to force fallback
        adapter.disable_new_brain()
        
        issue = "Test issue"
        context = {"test": True}
        
        result = adapter.analyze_system_issue(
            issue=issue,
            context=context,
            reasoning_mode="causal"
        )
        
        assert result is not None
        assert result["analysis_type"] in ["legacy", "ultimate_fallback"]
    
    def test_reasoning_mode_selection(self):
        """Test that different reasoning modes can be selected."""
        engine = DyonEngine()
        
        issue = "System performance degradation"
        context = {"performance_metric": "latency", "value": "high"}
        
        # Test with explicit reasoning mode
        result = engine.analyze_system_issue_with_new_architecture(issue, context)
        
        assert result is not None
        # The reasoning mode should be set (either by new brain or fallback)
        assert "reasoning_mode" in result


class TestPerformanceValidation:
    """Tests for performance validation."""
    
    def test_sub_100ms_performance_target(self):
        """Test that analyses meet sub-100ms performance target."""
        adapter = DyonBrainAdapter()
        adapter.initialize()
        
        latencies = []
        
        for i in range(50):
            issue = f"Performance test issue {i}"
            context = {"test": True, "iteration": i}
            
            start_time = time.time()
            result = adapter.analyze_system_issue(
                issue=issue,
                context=context,
                reasoning_mode="causal"
            )
            end_time = time.time()
            
            if result:
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
        
        # Calculate average latency
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        print(f"  Average latency: {avg_latency:.2f}ms")
        print(f"  Max latency: {max(latencies):.2f}ms")
        print(f"  Min latency: {min(latencies):.2f}ms")
        
        # Most analyses should be under 100ms
        under_100ms = sum(1 for lat in latencies if lat < 100.0)
        under_100ms_ratio = under_100ms / len(latencies) if latencies else 0
        
        print(f"  Under 100ms ratio: {under_100ms_ratio:.2%}")
        
        # At least 90% of analyses should be under 100ms
        assert under_100ms_ratio > 0.9, f"Only {under_100ms_ratio:.2%} of analyses under 100ms target"
    
    def test_engine_performance_target(self):
        """Test that engine analysis meets performance targets."""
        engine = DyonEngine()
        
        latencies = []
        
        for i in range(30):
            issue = f"Engine performance test {i}"
            context = {"test": True, "iteration": i}
            
            start_time = time.time()
            result = engine.analyze_system_issue_with_new_architecture(issue, context)
            end_time = time.time()
            
            if result and "latency_ms" in result:
                latency_ms = result["latency_ms"] if result["latency_ms"] > 0 else (end_time - start_time) * 1000
                latencies.append(latency_ms)
        
        # Calculate average latency
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        print(f"  Engine average latency: {avg_latency:.2f}ms")
        print(f"  Engine max latency: {max(latencies):.2f}ms")
        print(f"  Engine min latency: {min(latencies):.2f}ms")
        
        # Most analyses should be under 100ms
        under_100ms = sum(1 for lat in latencies if lat < 100.0)
        under_100ms_ratio = under_100ms / len(latencies) if latencies else 0
        
        print(f"  Engine under 100ms ratio: {under_100ms_ratio:.2%}")
        
        # At least 90% of analyses should be under 100ms
        assert under_100ms_ratio > 0.9, f"Only {under_100ms_ratio:.2%} of engine analyses under 100ms target"


class TestRealWorldScenarios:
    """Tests for real-world system analysis scenarios."""
    
    def test_latency_spike_analysis(self):
        """Test analysis of latency spike issue."""
        adapter = DyonBrainAdapter()
        adapter.initialize()
        
        issue = "Latency spike in trading decisions"
        context = {
            "component": "indira_engine",
            "normal_latency_ms": 2.0,
            "current_latency_ms": 15.0,
            "spike_duration_seconds": 30
        }
        
        result = adapter.analyze_system_issue(
            issue=issue,
            context=context,
            reasoning_mode="causal"
        )
        
        assert result is not None
        assert result["conclusion"]
        # Should provide recommendations about latency
        assert len(result["recommendations"]) > 0
    
    def test_memory_leak_analysis(self):
        """Test analysis of memory leak issue."""
        adapter = DyonBrainAdapter()
        adapter.initialize()
        
        issue = "Memory usage steadily increasing"
        context = {
            "component": "cognitive_system",
            "initial_memory_mb": 1024,
            "current_memory_mb": 4096,
            "time_window_hours": 24
        }
        
        result = adapter.analyze_system_issue(
            issue=issue,
            context=context,
            reasoning_mode="causal"
        )
        
        assert result is not None
        # Should provide memory-related recommendations
        assert any("memory" in rec.lower() for rec in result["recommendations"])
    
    def test_connection_failure_analysis(self):
        """Test analysis of connection failure issue."""
        adapter = DyonBrainAdapter()
        adapter.initialize()
        
        issue = "Repeated connection failures to external API"
        context = {
            "api_endpoint": "crypto_data_feed",
            "failure_count": 15,
            "time_window_minutes": 30,
            "error_type": "timeout"
        }
        
        result = adapter.analyze_system_issue(
            issue=issue,
            context=context,
            reasoning_mode="causal"
        )
        
        assert result is not None
        # Should provide connectivity-related recommendations
        assert len(result["recommendations"]) > 0


def run_dyon_integration_tests():
    """Run all DYON brain integration tests."""
    print("\n" + "="*60)
    print("DIX VISION v42.2 - DYON Brain Integration Tests")
    print("="*60 + "\n")
    
    # Test classes
    test_classes = [
        TestDyonBrainAdapter(),
        TestDyonEngineIntegration(),
        TestPerformanceValidation(),
        TestRealWorldScenarios()
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
        print("[SUCCESS] All DYON brain integration tests passed!")
    else:
        print("[FAILURE] Some DYON brain integration tests failed!")
    print("="*60 + "\n")
    
    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(run_dyon_integration_tests())
