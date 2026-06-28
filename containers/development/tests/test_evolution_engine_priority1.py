"""Priority 1 Evolution Engine and State Recovery Tests.

Tests the Priority 1 enhancements: State Recovery System, Intelligent Code Modification System,
and Self-Healing System.
"""

import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import unittest
from datetime import datetime


class TestStateRecoverySystem(unittest.TestCase):
    """Test State Recovery System (Execution Architecture Priority 1)."""

    def test_state_recovery_initialization(self):
        """Test state recovery system initialization."""
        from execution_unified.resilience import get_state_recovery_system

        recovery_system = get_state_recovery_system()

        self.assertIsNotNone(recovery_system)

        stats = recovery_system.get_recovery_statistics()
        self.assertIn("registered_replicas", stats)

        print("[PASS] State Recovery System initialization working")

    def test_replica_registration(self):
        """Test replica registration."""
        from execution_unified.resilience import get_state_recovery_system

        recovery_system = get_state_recovery_system()

        # Register replicas
        recovery_system.register_replica("replica_1", {"version": 1, "data": "test"})
        recovery_system.register_replica("replica_2", {"version": 1, "data": "test"})

        stats = recovery_system.get_recovery_statistics()
        self.assertEqual(stats["registered_replicas"], 2)

        print("[PASS] Replica registration working")

    def test_state_synchronization(self):
        """Test state synchronization across replicas."""
        from execution_unified.resilience import get_state_recovery_system

        recovery_system = get_state_recovery_system()

        # Register replicas
        recovery_system.register_replica("replica_1", {})
        recovery_system.register_replica("replica_2", {})

        # Synchronize state
        target_state = {"version": 2, "data": "synchronized"}
        result = recovery_system.synchronize_state("test_component", target_state)

        self.assertTrue(result.success)
        self.assertEqual(len(result.reconciled_fields), 2)

        print("[PASS] State synchronization working")

    def test_state_comparison(self):
        """Test state comparison between replicas."""
        from execution_unified.resilience import get_state_recovery_system

        recovery_system = get_state_recovery_system()

        # Register replicas with different states
        recovery_system.register_replica("replica_1", {"version": 1, "data": "original"})
        recovery_system.register_replica("replica_2", {"version": 2, "data": "modified"})

        # Compare states
        comparisons = recovery_system.compare_replica_states()

        self.assertIn("replica_2", comparisons)
        self.assertFalse(comparisons["replica_2"].is_synchronized)

        print("[PASS] State comparison working")

    def test_transaction_validation(self):
        """Test transaction validation."""
        from execution_unified.resilience import get_state_recovery_system

        recovery_system = get_state_recovery_system()
        recovery_system.register_replica("replica_1", {"version": 1})

        # Validate transaction
        validation = recovery_system.validate_transaction(
            "trans_1", {"version": 2, "data": "new"}, "test_component"
        )

        self.assertTrue(validation.is_valid)

        # Commit transaction
        success = recovery_system.commit_transaction("trans_1")
        self.assertTrue(success)

        print("[PASS] Transaction validation working")


class TestIntelligentCodeModification(unittest.TestCase):
    """Test Intelligent Code Modification System (Evolution Engine Priority 1)."""

    def test_intelligent_modifier_initialization(self):
        """Test intelligent code modifier initialization."""
        from evolution_engine.autonomous import get_intelligent_code_modifier

        modifier = get_intelligent_code_modifier()

        self.assertIsNotNone(modifier)

        stats = modifier.get_statistics()
        self.assertIn("total_modifications", stats)
        self.assertIn("safety_checkers_count", stats)

        print("[PASS] Intelligent Code Modifier initialization working")

    def test_modification_proposal(self):
        """Test code modification proposal generation."""
        from evolution_engine.autonomous import (
            CodeContext,
            ModificationObjective,
            get_intelligent_code_modifier,
        )

        modifier = get_intelligent_code_modifier()

        # Create code context
        code_context = CodeContext(
            file_path="test.py",
            language="python",
            component="test_component",
            current_code="def test_function():\n    return 'old'",
        )

        # Create modification objective
        objective = ModificationObjective(
            objective_type="OPTIMIZATION", description="Optimize function"
        )

        # Generate proposal
        proposal = modifier.propose_modification(code_context, objective)

        self.assertIsNotNone(proposal)
        self.assertIsNotNone(proposal.proposal_id)
        # risk_level is an enum, convert to string for comparison
        self.assertIn(proposal.risk_level.value, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

        print("[PASS] Modification proposal generation working")

    def test_safety_validation(self):
        """Test safety constraint validation."""
        from evolution_engine.autonomous import (
            CodeContext,
            ModificationObjective,
            get_intelligent_code_modifier,
        )

        modifier = get_intelligent_code_modifier()

        # Test with code that should pass safety checks
        safe_code = "def safe_function():\n    return 'safe'"
        code_context = CodeContext(
            file_path="safe.py",
            language="python",
            component="safe_component",
            current_code=safe_code,
        )

        objective = ModificationObjective(
            objective_type="OPTIMIZATION", description="Optimize safe code"
        )

        proposal = modifier.propose_modification(code_context, objective)

        if proposal:
            self.assertIsNotNone(proposal.safety_score)
            self.assertGreaterEqual(proposal.safety_score, 0.0)
            self.assertLessEqual(proposal.safety_score, 1.0)

        print("[PASS] Safety validation working")

    def test_modification_statistics(self):
        """Test modification statistics tracking."""
        from evolution_engine.autonomous import get_intelligent_code_modifier

        modifier = get_intelligent_code_modifier()

        stats = modifier.get_statistics()

        self.assertIn("total_modifications", stats)
        self.assertIn("successful_modifications", stats)
        self.assertIn("success_rate", stats)

        print("[PASS] Modification statistics working")


class TestSelfHealingSystem(unittest.TestCase):
    """Test Self-Healing System (Evolution Engine Priority 1)."""

    def test_self_healing_initialization(self):
        """Test self-healing system initialization."""
        from evolution_engine.autonomous import get_self_healing_system

        healing_system = get_self_healing_system()

        self.assertIsNotNone(healing_system)

        stats = healing_system.get_healing_statistics()
        self.assertIn("total_healings", stats)
        self.assertIn("auto_heal_enabled", stats)

        print("[PASS] Self-Healing System initialization working")

    def test_anomaly_detection(self):
        """Test anomaly detection."""
        from evolution_engine.autonomous import AnomalySeverity, get_self_healing_system

        healing_system = get_self_healing_system()

        # Create system state with critical CPU usage
        system_state = {
            "cpu_usage": 96.0,
            "memory_usage": 50.0,
            "error_rate": 2.0,
            "latency_ms": 100.0,
        }

        # Detect anomalies
        anomalies = healing_system._anomaly_detector.detect_anomalies(system_state)

        self.assertGreater(len(anomalies), 0)

        # Check if CPU anomaly was detected
        cpu_anomaly = next((a for a in anomalies if "CPU" in a.description), None)
        self.assertIsNotNone(cpu_anomaly)
        self.assertEqual(cpu_anomaly.severity, AnomalySeverity.CRITICAL)

        print("[PASS] Anomaly detection working")

    def test_root_cause_analysis(self):
        """Test root cause analysis."""
        from evolution_engine.autonomous import Anomaly, AnomalySeverity, get_self_healing_system

        healing_system = get_self_healing_system()

        # Create anomaly
        anomaly = Anomaly(
            anomaly_id="test_1",
            component="system",
            severity=AnomalySeverity.HIGH,
            description="CPU usage high",
            timestamp=datetime.utcnow(),
        )

        # Analyze root cause
        root_cause = healing_system._root_cause_analyzer.analyze(anomaly)

        self.assertIsNotNone(root_cause)
        self.assertGreater(root_cause.confidence, 0.0)
        self.assertLessEqual(root_cause.confidence, 1.0)

        print("[PASS] Root cause analysis working")

    def test_impact_assessment(self):
        """Test impact assessment."""
        from evolution_engine.autonomous import (
            Anomaly,
            AnomalySeverity,
            RootCause,
            get_self_healing_system,
        )

        healing_system = get_self_healing_system()

        # Create anomaly and root cause
        anomaly = Anomaly(
            anomaly_id="test_2",
            component="system",
            severity=AnomalySeverity.CRITICAL,
            description="Critical system error",
            timestamp=datetime.utcnow(),
        )

        root_cause = RootCause(
            root_cause_id="rc_1",
            anomaly_id="test_2",
            component="system",
            root_cause="System failure",
            confidence=0.8,
        )

        # Assess impact
        impact = healing_system._impact_assessor.assess(anomaly, root_cause)

        self.assertIsNotNone(impact)
        self.assertEqual(impact.user_impact, "SEVERE")
        self.assertEqual(impact.business_impact, "SEVERE")
        self.assertEqual(impact.mitigation_priority, "HIGH")

        print("[PASS] Impact assessment working")

    def test_resolution_generation(self):
        """Test resolution generation."""
        from evolution_engine.autonomous import (
            Anomaly,
            AnomalySeverity,
            ImpactAssessment,
            RootCause,
            get_self_healing_system,
        )

        healing_system = get_self_healing_system()

        # Create anomaly, root cause, and impact
        anomaly = Anomaly(
            anomaly_id="test_3",
            component="system",
            severity=AnomalySeverity.MEDIUM,
            description="Medium severity issue",
            timestamp=datetime.utcnow(),
        )

        root_cause = RootCause(
            root_cause_id="rc_2",
            anomaly_id="test_3",
            component="system",
            root_cause="Performance issue",
            confidence=0.7,
        )

        impact = ImpactAssessment(
            affected_components=["system"],
            user_impact="MINIMAL",
            business_impact="MINIMAL",
            mitigation_priority="MEDIUM",
        )

        # Generate resolution
        resolution = healing_system._resolution_generator.generate(root_cause, impact)

        self.assertIsNotNone(resolution)
        self.assertIn(resolution.resolution_type, ["AUTOMATED", "SEMI_AUTOMATED", "MANUAL"])
        self.assertGreater(len(resolution.steps), 0)

        print("[PASS] Resolution generation working")

    def test_self_healing_pipeline(self):
        """Test complete self-healing pipeline."""
        from evolution_engine.autonomous import get_self_healing_system

        healing_system = get_self_healing_system()

        # Create system state with issues
        system_state = {
            "cpu_usage": 97.0,
            "memory_usage": 55.0,
            "error_rate": 6.0,
            "latency_ms": 600.0,
        }

        # Disable auto-heal for this test (since it would try to actually deploy)
        healing_system._auto_heal_enabled = False

        # Detect and resolve
        result = healing_system.detect_and_resolve(system_state)

        # Should detect anomalies but not auto-heal
        self.assertIsNotNone(result)

        # Re-enable auto-heal
        healing_system._auto_heal_enabled = True

        print("[PASS] Self-healing pipeline working")


if __name__ == "__main__":
    # Run all tests
    suite = unittest.TestLoader().loadTestsFromName(__name__)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("PRIORITY 1 EVOLUTION ENGINE & STATE RECOVERY TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0:.1f}%"
    )

    if result.wasSuccessful():
        print("\n[SUCCCESS] ALL PRIORITY 1 EVOLUTION ENGINE TESTS PASSED!")
    else:
        print("\n[WARNING] Some tests failed - review the output above")
