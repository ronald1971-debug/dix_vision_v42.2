"""Full System Integration Tests for All Phases.

These tests verify that ALL phases (1-12) are integrated and wired together
in the complete DIX VISION v42.2 system.
"""

import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import unittest


class TestFullSystemIntegration(unittest.TestCase):
    """Test complete integration of all phases."""

    def setUp(self):
        from dix_vision_unified import get_unified_system

        self.unified_system = get_unified_system()

    def test_system_initialization(self):
        """Test that the unified system initializes with all phases."""
        success = self.unified_system.initialize()

        self.assertTrue(success)
        status = self.unified_system.get_system_status()
        self.assertTrue(status["initialized"])
        self.assertEqual(status["status"], "OPERATIONAL")

    def test_cognitive_os_all_phases_integrated(self):
        """Test that Cognitive OS integrates all phases."""
        from cognitive_os.core import get_cognitive_os_kernel

        kernel = get_cognitive_os_kernel()
        kernel.initialize_system()

        # Check component status includes all phases
        status = kernel.get_component_status()

        # Phase 1-2 (base phases)
        self.assertIn("governance_unified", status)
        self.assertIn("execution_unified", status)
        self.assertIn("m1_knowledge_layer", status)

        # Phase 3 Advanced Modules
        self.assertIn("phase3_rl_optimizer", status)
        self.assertIn("phase3_xai_system", status)
        self.assertIn("phase3_multi_agent_system", status)
        self.assertIn("phase3_temporal_reasoner", status)
        self.assertIn("phase3_dynamic_risk_manager", status)

        # Phase 4 Advanced Modules
        self.assertIn("phase4_neuro_symbolic_ai", status)
        self.assertIn("phase4_meta_cognitive_system", status)
        self.assertIn("phase4_advanced_causal_discovery", status)

        # Phase 5 Neuromorphic
        self.assertIn("phase5_indira_snn", status)
        self.assertIn("phase5_indira_lsm", status)
        self.assertIn("phase5_dyon_snn", status)
        self.assertIn("phase5_dyon_lsm", status)

    def test_neuromorphic_trading_integration(self):
        """Test that neuromorphic trading is fully integrated."""
        self.unified_system.initialize()

        market_state = {"signal": 0.6, "volatility": 0.25, "regime": "BULLISH", "price": 50000.0}

        result = self.unified_system.execute_trading_decision(market_state, "BTC")

        # Verify success
        self.assertTrue(result["success"])
        self.assertIn("decision", result)

        # Verify neuromorphic integration
        decision = result["decision"]
        self.assertTrue(decision["neuromorphic_enhanced"])
        self.assertGreater(decision["neuromorphic_latency_ms"], 0.0)
        self.assertIn("confidence_breakdown", decision)
        self.assertIn("snn_confidence", decision["confidence_breakdown"])
        self.assertIn("lsm_confidence", decision["confidence_breakdown"])

    def test_neuromorphic_system_monitoring_integration(self):
        """Test that neuromorphic system monitoring is fully integrated."""
        self.unified_system.initialize()

        system_metrics = {
            "cpu_usage": 75.0,
            "memory_usage": 65.0,
            "latency_p99": 300.0,
            "error_rate": 0.05,
            "event_rate": 150.0,
        }

        result = self.unified_system.analyze_system_with_neuromorphic(
            system_metrics, "execution_engine"
        )

        # Verify success
        self.assertTrue(result["success"])
        self.assertIn("analysis", result)

        # Verify neuromorphic integration
        analysis = result["analysis"]
        self.assertTrue(analysis["neuromorphic_enhanced"])
        self.assertIn("neuromorphic_anomaly_score", analysis)

    def test_configuration_system_integration(self):
        """Test that configuration management is integrated."""
        from cognitive_os.config import get_config_manager

        config_manager = get_config_manager()
        config = config_manager.get_config()

        # Verify configuration includes all phases
        self.assertIsNotNone(config.neuromorphic)
        self.assertIsNotNone(config.phase3)
        self.assertIsNotNone(config.phase4)

        # Verify neuromorphic configuration
        self.assertIsNotNone(config.neuromorphic.indira_snn_enabled)
        self.assertIsNotNone(config.neuromorphic.dyon_snn_enabled)

        # Verify Phase 3 configuration
        self.assertIsNotNone(config.phase3.rl_enabled)
        self.assertIsNotNone(config.phase3.xai_enabled)

        # Verify Phase 4 configuration
        self.assertIsNotNone(config.phase4.neuro_symbolic_enabled)
        self.assertIsNotNone(config.phase4.meta_cognitive_enabled)

    def test_system_status_comprehensive(self):
        """Test that system status includes all phases."""
        self.unified_system.initialize()

        status = self.unified_system.get_system_status()

        # Verify comprehensive status
        self.assertTrue(status["initialized"])
        self.assertIn("cognitive_os", status)
        self.assertIn("neuromorphic", status)
        self.assertIn("performance", status)
        self.assertIn("configuration", status)

        # Verify Cognitive OS status
        cognitive_os = status["cognitive_os"]
        self.assertIn("health_score", cognitive_os)
        self.assertIn("components", cognitive_os)

        # Verify all components are tracked
        components = cognitive_os["components"]
        self.assertGreater(len(components), 15)  # Should have 19 components total

    def test_cross_phase_integration(self):
        """Test that phases work together across boundaries."""
        self.unified_system.initialize()

        # Execute trading decision (INDIRA neuromorphic)
        market_state = {"signal": 0.5, "volatility": 0.2, "regime": "BULLISH"}
        trading_result = self.unified_system.execute_trading_decision(market_state, "BTC")

        # Execute system analysis (DYON neuromorphic)
        system_metrics = {
            "cpu_usage": 70.0,
            "memory_usage": 60.0,
            "latency_p99": 250.0,
            "error_rate": 0.02,
            "event_rate": 120.0,
        }
        analysis_result = self.unified_system.analyze_system_with_neuromorphic(
            system_metrics, "system"
        )

        # Verify both succeeded
        self.assertTrue(trading_result["success"])
        self.assertTrue(analysis_result["success"])

        # Verify both used neuromorphic components
        self.assertTrue(trading_result["decision"]["neuromorphic_enhanced"])
        self.assertTrue(analysis_result["analysis"]["neuromorphic_enhanced"])

    def test_system_shutdown(self):
        """Test that system shuts down gracefully."""
        self.unified_system.initialize()

        # Perform some operations
        market_state = {"signal": 0.5, "volatility": 0.2, "regime": "BULLISH"}
        self.unified_system.execute_trading_decision(market_state, "BTC")

        # Shutdown
        self.unified_system.shutdown()

        # Verify shutdown
        status = self.unified_system.get_system_status()
        self.assertFalse(status["initialized"])


class TestPhaseSpecificIntegration(unittest.TestCase):
    """Test specific phase integrations."""

    def test_phase3_modules_available(self):
        """Test that Phase 3 modules are available and functional."""
        from cognitive_os import get_multi_agent_system, get_rl_optimizer, get_xai_system

        # These should not raise import errors
        try:
            rl = get_rl_optimizer()
            self.assertIsNotNone(rl)
        except:
            self.fail("RL Optimizer import failed")

        try:
            xai = get_xai_system()
            self.assertIsNotNone(xai)
        except:
            self.fail("XAI System import failed")

        try:
            ma = get_multi_agent_system()
            self.assertIsNotNone(ma)
        except:
            self.fail("Multi-Agent System import failed")

    def test_phase4_modules_available(self):
        """Test that Phase 4 modules are available and functional."""
        from cognitive_os import (
            get_advanced_causal_discovery,
            get_meta_cognitive_system,
            get_neuro_symbolic_ai,
        )

        try:
            ns = get_neuro_symbolic_ai()
            self.assertIsNotNone(ns)
        except:
            self.fail("Neuro-Symbolic AI import failed")

        try:
            mc = get_meta_cognitive_system()
            self.assertIsNotNone(mc)
        except:
            self.fail("Meta-Cognitive System import failed")

        try:
            cd = get_advanced_causal_discovery()
            self.assertIsNotNone(cd)
        except:
            self.fail("Advanced Causal Discovery import failed")


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
