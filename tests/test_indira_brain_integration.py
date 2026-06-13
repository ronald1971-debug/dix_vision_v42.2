"""
test_indira_brain_integration.py
DIX VISION v42.2 — INDIRA Brain Integration Tests

Tests for the integration of the new INDIRA brain with the existing trading engine:
- Adapter initialization
- Trading decision processing
- Performance validation (<5ms target)
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

from mind.indira_brain_adapter import (
    IndiraBrainAdapter,
    BrainIntegrationConfig,
    get_indira_brain_adapter
)
from mind.engine import IndiraEngine, ExecutionEvent


class TestIndiraBrainAdapter:
    """Tests for the INDIRA brain adapter."""
    
    def test_singleton_pattern(self):
        """Test that adapter follows singleton pattern."""
        adapter1 = get_indira_brain_adapter()
        adapter2 = get_indira_brain_adapter()
        assert adapter1 is adapter2
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        adapter = IndiraBrainAdapter()
        result = adapter.initialize()
        assert result is True
    
    def test_trading_decision_processing(self):
        """Test basic trading decision processing."""
        adapter = IndiraBrainAdapter()
        adapter.initialize()
        
        # Mock market data
        market_data = {
            "signal": 0.8,
            "price": 65000.0,
            "data_quality": 0.95,
            "execution_confidence": 0.90,
            "strategy": "regime_adaptive",
            "volatility": 0.3,
            "regime": "BULL"
        }
        
        # Mock risk constraints
        class MockRiskConstraints:
            def allows_trade(self, size_usd, portfolio_usd):
                return True, ""
            max_order_size_usd = 10000.0
        
        constraints = MockRiskConstraints()
        portfolio_usd = 100000.0
        
        result = adapter.process_trading_decision(
            market_data=market_data,
            asset="BTCUSDT",
            risk_constraints=constraints,
            portfolio_usd=portfolio_usd
        )
        
        assert result is not None
        assert "decision_type" in result
        assert "side" in result
        assert "size_usd" in result
        assert "confidence" in result
        assert "latency_ms" in result
    
    def test_performance_metrics(self):
        """Test performance metrics tracking."""
        adapter = IndiraBrainAdapter()
        adapter.initialize()
        
        # Process some decisions
        for i in range(10):
            market_data = {
                "signal": 0.5 if i % 2 == 0 else -0.5,
                "price": 65000.0,
                "data_quality": 0.95,
                "execution_confidence": 0.90,
                "strategy": "regime_adaptive",
                "volatility": 0.3,
                "regime": "BULL"
            }
            
            class MockRiskConstraints:
                def allows_trade(self, size_usd, portfolio_usd):
                    return True, ""
                max_order_size_usd = 10000.0
            
            adapter.process_trading_decision(
                market_data=market_data,
                asset="BTCUSDT",
                risk_constraints=MockRiskConstraints(),
                portfolio_usd=100000.0
            )
        
        metrics = adapter.get_performance_metrics()
        assert metrics["total_decisions"] >= 10
        assert "average_latency_ms" in metrics
        assert "new_brain_ratio" in metrics


class TestIndiraEngineIntegration:
    """Tests for INDIRA engine integration with new brain."""
    
    def test_engine_initialization_with_adapter(self):
        """Test that engine initializes with brain adapter."""
        engine = IndiraEngine()
        
        # Engine should have adapter attribute
        assert hasattr(engine, '_indira_brain_adapter')
    
    def test_engine_process_tick_with_new_brain(self):
        """Test that engine can process ticks with new brain integration."""
        engine = IndiraEngine()
        
        # Mock market data
        market_data = {
            "signal": 0.8,
            "asset": "BTCUSDT",
            "price": 65000.0,
            "data_quality": 0.95,
            "execution_confidence": 0.90,
            "strategy": "regime_adaptive",
            "volatility": 0.3,
            "regime": "BULL"
        }
        
        # Process tick
        event = engine.process_tick(market_data)
        
        assert event is not None
        assert isinstance(event, ExecutionEvent)
        assert event.asset == "BTCUSDT"
        assert event.latency_ns > 0
    
    def test_fallback_behavior(self):
        """Test fallback behavior when new brain fails."""
        config = BrainIntegrationConfig(
            use_new_brain=True,
            fallback_on_failure=True
        )
        adapter = IndiraBrainAdapter(config)
        adapter.initialize()
        
        # Disable new brain to force fallback
        adapter.disable_new_brain()
        
        market_data = {
            "signal": 0.8,
            "price": 65000.0,
            "data_quality": 0.95,
            "execution_confidence": 0.90,
            "strategy": "regime_adaptive",
            "volatility": 0.3,
            "regime": "BULL"
        }
        
        class MockRiskConstraints:
            def allows_trade(self, size_usd, portfolio_usd):
                return True, ""
            max_order_size_usd = 10000.0
        
        result = adapter.process_trading_decision(
            market_data=market_data,
            asset="BTCUSDT",
            risk_constraints=MockRiskConstraints(),
            portfolio_usd=100000.0
        )
        
        assert result is not None
        assert result["source"] in ["fallback", "ultimate_fallback"]
    
    def test_cache_functionality(self):
        """Test decision caching for fast path optimization."""
        config = BrainIntegrationConfig(
            use_new_brain=False,  # Use fallback to ensure caching works
            enable_cache=True,
            cache_ttl_ms=1000.0
        )
        adapter = IndiraBrainAdapter(config)
        adapter.initialize()
        
        market_data = {
            "signal": 0.8,
            "price": 65000.0,
            "data_quality": 0.95,
            "execution_confidence": 0.90,
            "strategy": "regime_adaptive",
            "volatility": 0.3,
            "regime": "BULL"
        }
        
        class MockRiskConstraints:
            def allows_trade(self, size_usd, portfolio_usd):
                return True, ""
            max_order_size_usd = 10000.0
        
        # Process multiple decisions to test cache
        for i in range(5):
            result = adapter.process_trading_decision(
                market_data=market_data,
                asset="BTCUSDT",
                risk_constraints=MockRiskConstraints(),
                portfolio_usd=100000.0
            )
            assert result is not None
        
        # Clear cache and verify it's cleared
        adapter.clear_cache()
        
        metrics = adapter.get_performance_metrics()
        assert metrics["cache_size"] == 0


class TestPerformanceValidation:
    """Tests for performance validation."""
    
    def test_sub_5ms_performance_target(self):
        """Test that decisions meet sub-5ms performance target."""
        adapter = IndiraBrainAdapter()
        adapter.initialize()
        
        latencies = []
        
        for i in range(100):
            market_data = {
                "signal": 0.5 if i % 2 == 0 else -0.5,
                "price": 65000.0,
                "data_quality": 0.95,
                "execution_confidence": 0.90,
                "strategy": "regime_adaptive",
                "volatility": 0.3,
                "regime": "BULL"
            }
            
            class MockRiskConstraints:
                def allows_trade(self, size_usd, portfolio_usd):
                    return True, ""
                max_order_size_usd = 10000.0
            
            start_time = time.time()
            result = adapter.process_trading_decision(
                market_data=market_data,
                asset="BTCUSDT",
                risk_constraints=MockRiskConstraints(),
                portfolio_usd=100000.0
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
        
        # Most decisions should be under 5ms
        under_5ms = sum(1 for lat in latencies if lat < 5.0)
        under_5ms_ratio = under_5ms / len(latencies) if latencies else 0
        
        print(f"  Under 5ms ratio: {under_5ms_ratio:.2%}")
        
        # At least 80% of decisions should be under 5ms
        assert under_5ms_ratio > 0.8, f"Only {under_5ms_ratio:.2%} of decisions under 5ms target"
    
    def test_engine_sub_5ms_performance(self):
        """Test that engine process_tick meets sub-5ms target."""
        engine = IndiraEngine()
        
        latencies = []
        
        for i in range(50):
            market_data = {
                "signal": 0.5 if i % 2 == 0 else -0.5,
                "asset": "BTCUSDT",
                "price": 65000.0,
                "data_quality": 0.95,
                "execution_confidence": 0.90,
                "strategy": "regime_adaptive",
                "volatility": 0.3,
                "regime": "BULL"
            }
            
            event = engine.process_tick(market_data)
            latency_ms = event.latency_ns / 1_000_000
            latencies.append(latency_ms)
        
        # Calculate average latency
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        print(f"  Engine average latency: {avg_latency:.2f}ms")
        print(f"  Engine max latency: {max(latencies):.2f}ms")
        print(f"  Engine min latency: {min(latencies):.2f}ms")
        
        # Most decisions should be under 5ms
        under_5ms = sum(1 for lat in latencies if lat < 5.0)
        under_5ms_ratio = under_5ms / len(latencies) if latencies else 0
        
        print(f"  Engine under 5ms ratio: {under_5ms_ratio:.2%}")
        
        # At least 90% of decisions should be under 5ms for engine
        assert under_5ms_ratio > 0.9, f"Only {under_5ms_ratio:.2%} of engine decisions under 5ms target"


def run_indira_integration_tests():
    """Run all INDIRA brain integration tests."""
    print("\n" + "="*60)
    print("DIX VISION v42.2 - INDIRA Brain Integration Tests")
    print("="*60 + "\n")
    
    # Test classes
    test_classes = [
        TestIndiraBrainAdapter(),
        TestIndiraEngineIntegration(),
        TestPerformanceValidation()
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
        print("[SUCCESS] All INDIRA brain integration tests passed!")
    else:
        print("[FAILURE] Some INDIRA brain integration tests failed!")
    print("="*60 + "\n")
    
    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(run_indira_integration_tests())
