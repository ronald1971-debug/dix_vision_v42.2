"""
test_coordination_integration.py
DIX VISION v42.2 — Coordination Layer Integration Tests

Tests for the integration of the new coordination layer with existing governance:
- Mode transition integration
- Cognitive economy integration
- ACL protocol performance
- Fallback behavior
- Backward compatibility
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import threading
from datetime import datetime

from governance.coordination_adapter import (
    CoordinationAdapter,
    CoordinationConfig,
    get_coordination_adapter
)


class TestCoordinationAdapter:
    """Tests for the coordination adapter."""
    
    def test_singleton_pattern(self):
        """Test that adapter follows singleton pattern."""
        adapter1 = get_coordination_adapter()
        adapter2 = get_coordination_adapter()
        assert adapter1 is adapter2
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        adapter = CoordinationAdapter()
        result = adapter.initialize()
        assert result is True
    
    def test_mode_transition_request(self):
        """Test mode transition request."""
        adapter = CoordinationAdapter()
        adapter.initialize()
        
        result = adapter.request_mode_transition(
            new_mode="ACTIVE",
            reason="Test transition",
            initiator="system"
        )
        
        assert result is not None
        assert "success" in result
        assert "from_mode" in result
        assert "to_mode" in result
    
    def test_acl_message_sending(self):
        """Test ACL message sending."""
        adapter = CoordinationAdapter()
        adapter.initialize()
        
        result = adapter.send_acl_message(
            sender="INDIRA",
            receiver="DYON",
            message_type="COORDINATION",
            content={"action": "request_analysis"}
        )
        
        assert result is not None
        assert result["success"]
        assert "message_id" in result
        assert "latency_ms" in result
    
    def test_cognitive_budget_check(self):
        """Test cognitive budget checking."""
        adapter = CoordinationAdapter()
        adapter.initialize()
        
        result = adapter.check_cognitive_budget(
            operation_type="trading_analysis",
            resource_estimate=10.0
        )
        
        assert result is not None
        assert "allowed" in result
        assert "remaining_budget" in result
    
    def test_get_current_mode(self):
        """Test getting current operating mode."""
        adapter = CoordinationAdapter()
        adapter.initialize()
        
        result = adapter.get_current_mode()
        
        assert result is not None
        assert "mode" in result
        assert "mode_system" in result


class TestPerformanceValidation:
    """Tests for performance validation."""
    
    def test_sub_10ms_acl_performance(self):
        """Test that ACL messages meet sub-10ms performance target."""
        adapter = CoordinationAdapter()
        adapter.initialize()
        
        latencies = []
        
        for i in range(100):
            start_time = time.time()
            result = adapter.send_acl_message(
                sender="INDIRA",
                receiver="DYON",
                message_type="COORDINATION",
                content={"test": i}
            )
            end_time = time.time()
            
            if result and result.get("success"):
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
        
        # Calculate average latency
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        print(f"  Average ACL latency: {avg_latency:.2f}ms")
        print(f"  Max ACL latency: {max(latencies):.2f}ms")
        print(f"  Min ACL latency: {min(latencies):.2f}ms")
        
        # All messages should be under 10ms
        under_10ms = sum(1 for lat in latencies if lat < 10.0)
        under_10ms_ratio = under_10ms / len(latencies) if latencies else 0
        
        print(f"  Under 10ms ratio: {under_10ms_ratio:.2%}")
        
        # At least 90% of messages should be under 10ms
        assert under_10ms_ratio > 0.9, f"Only {under_10ms_ratio:.2%} of ACL messages under 10ms target"
    
    def test_mode_transition_performance(self):
        """Test mode transition performance."""
        adapter = CoordinationAdapter()
        adapter.initialize()
        
        latencies = []
        
        for i in range(50):
            start_time = time.time()
            result = adapter.request_mode_transition(
                new_mode="ACTIVE" if i % 2 == 0 else "PASSIVE",
                reason=f"Performance test {i}",
                initiator="test"
            )
            end_time = time.time()
            
            if result:
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
        
        # Calculate average latency
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        print(f"  Average mode transition latency: {avg_latency:.2f}ms")
        print(f"  Max mode transition latency: {max(latencies):.2f}ms")
        print(f"  Min mode transition latency: {min(latencies):.2f}ms")
        
        # Mode transitions should be fast (we don't have a strict target but should be reasonable)
        assert avg_latency < 100.0, f"Mode transitions too slow: {avg_latency:.2f}ms"


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing governance."""
    
    def test_fallback_to_legacy_mode_manager(self):
        """Test fallback to legacy mode manager when new coordination unavailable."""
        config = CoordinationConfig(
            use_new_coordination=False,
            fallback_on_failure=True
        )
        adapter = CoordinationAdapter(config)
        adapter.initialize()
        
        result = adapter.request_mode_transition(
            new_mode="ACTIVE",
            reason="Test fallback",
            initiator="system"
        )
        
        assert result is not None
        assert result["integration_mode"] in ["fallback", "ultimate_fallback"]
    
    def test_mode_mapping_correctness(self):
        """Test that mode mapping between new and old systems is correct."""
        adapter = CoordinationAdapter()
        adapter.initialize()
        
        # Test mode mappings
        mode_mappings = {
            "ACTIVE": "AUTO",
            "PASSIVE": "SAFE", 
            "OBSERVATION": "PAPER",
            "EMERGENCY": "LOCKED"
        }
        
        for new_mode, expected_fsm_mode in mode_mappings.items():
            result = adapter.request_mode_transition(
                new_mode=new_mode,
                reason=f"Testing {new_mode} mapping",
                initiator="test"
            )
            
            assert result is not None
            # In fallback mode, should map to expected FSM mode
            if result["integration_mode"] == "fallback":
                assert expected_fsm_mode in result["to_mode"]


class TestRealWorldScenarios:
    """Tests for real-world coordination scenarios."""
    
    def test_agent_communication_scenario(self):
        """Test realistic agent communication scenario."""
        adapter = CoordinationAdapter()
        adapter.initialize()
        
        # Simulate INDIRA requesting analysis from DYON
        result = adapter.send_acl_message(
            sender="INDIRA",
            receiver="DYON",
            message_type="ANALYSIS_REQUEST",
            content={
                "asset": "BTCUSDT",
                "urgency": "high",
                "context": "latency_spike"
            }
        )
        
        assert result["success"]
        assert result["latency_ms"] < 10.0  # Should be under 10ms target
        
        # Verify message was queued
        metrics = adapter.get_performance_metrics()
        assert metrics["acl_message_count"] > 0
    
    def test_emergency_mode_transition(self):
        """Test emergency mode transition scenario."""
        adapter = CoordinationAdapter()
        adapter.initialize()
        
        # Use SAFE mode as emergency fallback
        result = adapter.request_mode_transition(
            new_mode="SAFE",
            reason="Critical system failure detected",
            initiator="system"
        )
        
        assert result is not None
        # Emergency-like transitions should succeed
        assert result["success"]
    
    def test_cognitive_budget_for_trading_operation(self):
        """Test cognitive budget check for trading operation."""
        adapter = CoordinationAdapter()
        adapter.initialize()
        
        result = adapter.check_cognitive_budget(
            operation_type="trading_execution",
            resource_estimate=25.0  # Typical trading operation cost
        )
        
        assert result is not None
        assert "allowed" in result


def run_coordination_integration_tests():
    """Run all coordination integration tests."""
    print("\n" + "="*60)
    print("DIX VISION v42.2 - Coordination Layer Integration Tests")
    print("="*60 + "\n")
    
    # Test classes
    test_classes = [
        TestCoordinationAdapter(),
        TestPerformanceValidation(),
        TestBackwardCompatibility(),
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
        print("[SUCCESS] All coordination integration tests passed!")
    else:
        print("[FAILURE] Some coordination integration tests failed!")
    print("="*60 + "\n")
    
    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(run_coordination_integration_tests())
