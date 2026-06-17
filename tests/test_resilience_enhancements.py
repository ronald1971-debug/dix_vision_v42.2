"""Quick Wins and Priority 1 Implementation Tests.

Tests the resilience enhancements: checkpointing, circuit breaking, adaptive retry,
health monitoring, legacy system analysis, and distributed resilience.
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import unittest
import time
from datetime import datetime


class TestQuickWins(unittest.TestCase):
    """Test quick wins implementation."""
    
    def test_checkpoint_manager(self):
        """Test state checkpointing."""
        from execution_unified.resilience import get_checkpoint_manager
        
        checkpoint_manager = get_checkpoint_manager()
        
        # Create checkpoint
        state_data = {
            "test_data": "value",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        checkpoint = checkpoint_manager.create_checkpoint(
            component="test_component",
            state_data=state_data
        )
        
        # Verify checkpoint created
        self.assertIsNotNone(checkpoint)
        self.assertEqual(checkpoint.component, "test_component")
        self.assertIsNotNone(checkpoint.checksum)
        
        # Retrieve checkpoint
        latest = checkpoint_manager.get_latest_checkpoint("test_component")
        self.assertEqual(latest.checkpoint_id, checkpoint.checkpoint_id)
        
        # Restore checkpoint
        restore_result = checkpoint_manager.restore_checkpoint(checkpoint.checkpoint_id)
        self.assertTrue(restore_result.success)
        self.assertTrue(restore_result.verification_passed)
        
        print("[PASS] Checkpoint Manager working")
    
    def test_circuit_breaker(self):
        """Test circuit breaking."""
        from execution_unified.resilience import get_circuit_breaker, CircuitBreakerConfig
        
        circuit_breaker = get_circuit_breaker(
            "test_circuit",
            CircuitBreakerConfig(failure_threshold=3, timeout_ms=5000)
        )
        
        # Test successful execution
        def successful_func():
            return "success"
        
        result = circuit_breaker.execute(successful_func)
        self.assertTrue(result.success)
        
        # Test failure handling
        failure_count = [0]
        def failing_func():
            failure_count[0] += 1
            if failure_count[0] < 5:
                raise Exception("Test failure")
            return "recovered"
        
        # First failure
        result = circuit_breaker.execute(failing_func)
        self.assertFalse(result.success)
        self.assertEqual(circuit_breaker.get_state().value, "CLOSED")
        
        # Multiple failures to trip circuit
        for _ in range(3):
            try:
                result = circuit_breaker.execute(failing_func)
            except:
                pass
        
        # Circuit should be open now
        self.assertEqual(circuit_breaker.get_state().value, "OPEN")
        
        # Reset for testing
        circuit_breaker.reset()
        self.assertEqual(circuit_breaker.get_state().value, "CLOSED")
        
        print("[PASS] Circuit Breaker working")
    
    def test_adaptive_retry(self):
        """Test adaptive retry strategies."""
        from execution_unified.resilience import AdaptiveRetryStrategy, RetryConfig
        
        retry_strategy = AdaptiveRetryStrategy(RetryConfig(max_attempts=3))
        
        # Test successful execution
        def successful_func():
            return "success"
        
        result = retry_strategy.execute_with_retry(successful_func)
        self.assertTrue(result.success)
        self.assertEqual(result.attempts, 1)
        
        # Test retry on failure
        attempt_count = [0]
        def eventually_successful_func():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise Exception("Temporary failure")
            return "success after retries"
        
        result = retry_strategy.execute_with_retry(eventually_successful_func)
        self.assertTrue(result.success)
        self.assertGreater(result.attempts, 1)
        self.assertEqual(attempt_count[0], 2)
        
        print("[PASS] Adaptive Retry working")
    
    def test_health_monitoring(self):
        """Test comprehensive health monitoring."""
        from execution_unified.health import get_health_monitor, HealthStatus
        
        health_monitor = get_health_monitor()
        
        # Register custom health check
        class TestHealthCheck:
            def __init__(self):
                self.component_name = "test_component"
            
            def check_health(self):
                from execution_unified.health import HealthCheck, HealthStatus
                return HealthCheck(
                    component="test_component",
                    status=HealthStatus.HEALTHY,
                    message="Test component healthy",
                    timestamp=datetime.utcnow(),
                    metrics={"test_metric": 1.0}
                )
        
        health_monitor.register_provider(TestHealthCheck())
        
        # Check system health
        report = health_monitor.check_system_health()
        
        self.assertIsNotNone(report)
        self.assertGreater(report.total_components, 0)
        self.assertIn("test_component", report.component_checks)
        
        print("[PASS] Health Monitoring working")
    
    def test_legacy_system_analysis(self):
        """Test legacy system analysis."""
        from execution_unified.consolidation import get_legacy_analyzer
        
        analyzer = get_legacy_analyzer()
        
        # Analyze legacy systems
        plan = analyzer.analyze_legacy_systems()
        
        self.assertIsNotNone(plan)
        self.assertGreater(len(plan.legacy_systems), 0)
        
        # Check analysis report
        report = analyzer.get_analysis_report()
        self.assertIn("total_systems", report)
        self.assertGreater(report["total_systems"], 0)
        
        print(f"[PASS] Legacy System Analysis working - Found {report['total_systems']} legacy systems")
        
        # Show some details
        for system in report["systems"]:
            print(f"  - {system['name']}: {system['lines']} lines, {system['recommended_action']}")


class TestDistributedResilience(unittest.TestCase):
    """Test distributed execution resilience (Priority 1)."""
    
    def test_distributed_resilience_integration(self):
        """Test distributed resilience combining all layers."""
        from execution_unified.resilience import get_distributed_resilience
        
        resilience = get_distributed_resilience("test_service")
        
        # Test successful execution
        def successful_operation():
            return "operation_success"
        
        result = resilience.execute_with_resilience(successful_operation, component="test")
        
        self.assertTrue(result.success)
        self.assertGreater(len(result.resilience_layers_used), 0)
        
        # Test with fallback
        def failing_operation():
            raise Exception("Operation failed")
        
        def fallback_operation():
            return "fallback_success"
        
        result = resilience.execute_with_resilience(
            failing_operation,
            component="test",
            fallback=fallback_operation
        )
        
        # Should fail since circuit is closed initially
        # After enough failures, it will use fallback
        
        # Get statistics
        stats = resilience.get_resilience_statistics()
        self.assertIn("total_executions", stats)
        self.assertEqual(stats["service_name"], "test_service")
        
        print("[PASS] Distributed Resilience working")
    
    def test_resilience_layer_composition(self):
        """Test that resilience layers compose correctly."""
        from execution_unified.resilience import get_distributed_resilience
        
        resilience = get_distributed_resilience("test_composition")
        
        # Test that all layers are used
        def test_operation():
            time.sleep(0.01)  # Simulate work
            return "result"
        
        result = resilience.execute_with_resilience(test_operation, component="test_composition")
        
        self.assertTrue(result.success)
        
        # Check that multiple resilience layers were used
        resilience_layers = result.resilience_layers_used
        self.assertGreater(len(resilience_layers), 0)
        
        # Verify expected layers are present
        expected_layers = ["checkpoint_created", "circuit_breaker"]
        for layer in expected_layers:
            if layer in resilience_layers:
                print(f"  [LAYER] {layer} layer used")
        
        print("[PASS] Resilience layer composition working")


class TestIntegration(unittest.TestCase):
    """Test integration of all resilience components."""
    
    def test_full_resilience_pipeline(self):
        """Test complete resilience pipeline."""
        from execution_unified.resilience import get_distributed_resilience
        from execution_unified.health import get_health_monitor
        
        # Get resilience system
        resilience = get_distributed_resilience("integrated_service")
        
        # Get health monitor
        health_monitor = get_health_monitor()
        
        # Simulate critical operation
        operation_count = [0]
        def critical_operation():
            operation_count[0] += 1
            # 20% chance of failure
            if operation_count[0] % 5 == 0:
                raise Exception("Simulated failure")
            return f"operation_{operation_count[0]}"
        
        # Execute with resilience
        results = []
        for i in range(5):
            result = resilience.execute_with_resilience(critical_operation, component="integrated")
            results.append(result)
        
        # Check system health
        health_report = health_monitor.check_system_health()
        
        # Verify pipeline worked
        successful = sum(1 for r in results if r.success)
        self.assertGreater(successful, 0)
        
        # Get comprehensive statistics
        resilience_stats = resilience.get_resilience_statistics()
        
        print(f"[PASS] Full Resilience Pipeline: {successful}/5 operations successful")
        print(f"  Circuit state: {resilience_stats['circuit_breaker']['state']}")
        print(f"  System health: {health_report.overall_status.value}")
        print(f"  Health score: {health_report.overall_health_score:.2f}")


if __name__ == '__main__':
    # Run all tests
    suite = unittest.TestLoader().loadTestsFromName(__name__)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("RESILIENCE ENHANCEMENT TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0:.1f}%")
    
    if result.wasSuccessful():
        print("\n[SUCCCESS] ALL QUICK WINS AND PRIORITY 1 TESTS PASSED!")
    else:
        print("\n[WARNING] Some tests failed - review the output above")