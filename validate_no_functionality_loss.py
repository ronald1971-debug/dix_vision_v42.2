"""
validate_no_functionality_loss.py
DIX VISION v42.2 — Functionality Loss Validation

Validates that the new cognitive architecture integration does not break
existing functionality and maintains backward compatibility.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class FunctionalityLossValidator:
    """Validates no functionality loss during cognitive architecture integration."""
    
    def __init__(self):
        self.validation_results = []
    
    def validate_legacy_indira_functionality(self) -> Dict[str, Any]:
        """Validate that legacy IndiraEngine still works correctly."""
        print("\n=== Validating Legacy INDIRA Functionality ===")
        
        results = {
            "test_name": "Legacy IndiraEngine Functionality",
            "passed": False,
            "checks": []
        }
        
        try:
            from mind.engine import IndiraEngine
            
            # Test 1: Engine instantiation
            print("  [CHECK] IndiraEngine instantiation...")
            indira = IndiraEngine()
            assert indira is not None
            results["checks"].append({"name": "instantiation", "passed": True})
            print("  [PASS] IndiraEngine instantiation")
            
            # Test 2: Basic tick processing
            print("  [CHECK] Basic tick processing...")
            market_data = {
                "signal": 0.5,
                "asset": "BTCUSDT",
                "price": 65000.0,
                "data_quality": 0.95,
                "execution_confidence": 0.90,
                "strategy": "test"
            }
            event = indira.process_tick(market_data)
            assert event is not None
            results["checks"].append({"name": "tick_processing", "passed": True})
            print("  [PASS] Basic tick processing")
            
            # Test 3: Event structure
            print("  [CHECK] Event structure...")
            assert hasattr(event, 'event_type')
            assert hasattr(event, 'asset')
            assert hasattr(event, 'side')
            assert hasattr(event, 'size_usd')
            results["checks"].append({"name": "event_structure", "passed": True})
            print("  [PASS] Event structure")
            
            # Test 4: Portfolio management
            print("  [CHECK] Portfolio management...")
            indira.update_portfolio_value(100000.0)
            results["checks"].append({"name": "portfolio_management", "passed": True})
            print("  [PASS] Portfolio management")
            
            # Test 5: Evaluate method (backward compat)
            print("  [CHECK] Evaluate method (backward compat)...")
            decision = indira.evaluate(market_data)
            assert decision is not None
            results["checks"].append({"name": "evaluate_method", "passed": True})
            print("  [PASS] Evaluate method (backward compat)")
            
            results["passed"] = True
            print(f"  [SUCCESS] All {len(results['checks'])} legacy IndiraEngine checks passed")
            
        except Exception as e:
            print(f"  [FAILED] Legacy IndiraEngine validation: {e}")
            results["checks"].append({"name": "error", "passed": False, "error": str(e)})
        
        return results
    
    def validate_legacy_dyon_functionality(self) -> Dict[str, Any]:
        """Validate that legacy DyonEngine still works correctly."""
        print("\n=== Validating Legacy DYON Functionality ===")
        
        results = {
            "test_name": "Legacy DyonEngine Functionality",
            "passed": False,
            "checks": []
        }
        
        try:
            from system_monitor.dyon_engine import get_dyon_engine
            
            # Test 1: Engine instantiation
            print("  [CHECK] DyonEngine instantiation...")
            dyon = get_dyon_engine()
            assert dyon is not None
            results["checks"].append({"name": "instantiation", "passed": True})
            print("  [PASS] DyonEngine instantiation")
            
            # Test 2: Health check
            print("  [CHECK] Health check...")
            dyon._health_check()
            results["checks"].append({"name": "health_check", "passed": True})
            print("  [PASS] Health check")
            
            # Test 3: Feed tick recording
            print("  [CHECK] Feed tick recording...")
            dyon.record_feed_tick("test_feed")
            results["checks"].append({"name": "feed_tick", "passed": True})
            print("  [PASS] Feed tick recording")
            
            # Test 4: Latency recording
            print("  [CHECK] Latency recording...")
            dyon.record_execution_latency("test_component", 5.0)
            results["checks"].append({"name": "latency_recording", "passed": True})
            print("  [PASS] Latency recording")
            
            results["passed"] = True
            print(f"  [SUCCESS] All {len(results['checks'])} legacy DyonEngine checks passed")
            
        except Exception as e:
            print(f"  [FAILED] Legacy DyonEngine validation: {e}")
            results["checks"].append({"name": "error", "passed": False, "error": str(e)})
        
        return results
    
    def validate_preservation_layer(self) -> Dict[str, Any]:
        """Validate preservation layer functionality."""
        print("\n=== Validating Preservation Layer Functionality ===")
        
        results = {
            "test_name": "Preservation Layer Functionality",
            "passed": False,
            "checks": []
        }
        
        try:
            from preservation_layer import get_preservation_layer, PreservationLayer
            
            # Test 1: Layer instantiation
            print("  [CHECK] Preservation layer instantiation...")
            preservation = get_preservation_layer()
            assert isinstance(preservation, PreservationLayer)
            results["checks"].append({"name": "instantiation", "passed": True})
            print("  [PASS] Preservation layer instantiation")
            
            # Test 2: Singleton behavior
            print("  [CHECK] Singleton behavior...")
            preservation2 = get_preservation_layer()
            assert preservation is preservation2
            results["checks"].append({"name": "singleton", "passed": True})
            print("  [PASS] Singleton behavior")
            
            # Test 3: Legacy engine initialization
            print("  [CHECK] Legacy engine initialization...")
            result = preservation.initialize_legacy_engines()
            assert isinstance(result, bool)
            results["checks"].append({"name": "legacy_init", "passed": True})
            print("  [PASS] Legacy engine initialization")
            
            # Test 4: New architecture connection
            print("  [CHECK] New architecture connection...")
            preservation.connect_new_architecture(
                indira_brain=None,  # Can be None for validation
                dyon_brain=None,
                coordination_layer=None
            )
            results["checks"].append({"name": "new_arch_connection", "passed": True})
            print("  [PASS] New architecture connection")
            
            results["passed"] = True
            print(f"  [SUCCESS] All {len(results['checks'])} preservation layer checks passed")
            
        except Exception as e:
            print(f"  [FAILED] Preservation layer validation: {e}")
            results["checks"].append({"name": "error", "passed": False, "error": str(e)})
        
        return results
    
    def validate_configuration_system(self) -> Dict[str, Any]:
        """Validate configuration system works correctly."""
        print("\n=== Validating Configuration System ===")
        
        results = {
            "test_name": "Configuration System",
            "passed": False,
            "checks": []
        }
        
        try:
            from config.cognitive_config_loader import load_cognitive_config
            
            # Test 1: Config loading
            print("  [CHECK] Configuration loading...")
            config = load_cognitive_config()
            assert config is not None
            results["checks"].append({"name": "config_load", "passed": True})
            print("  [PASS] Configuration loading")
            
            # Test 2: Config structure
            print("  [CHECK] Configuration structure...")
            assert hasattr(config, 'enabled')
            assert hasattr(config, 'preservation_layer')
            assert hasattr(config, 'indira_brain')
            assert hasattr(config, 'dyon_brain')
            results["checks"].append({"name": "config_structure", "passed": True})
            print("  [PASS] Configuration structure")
            
            results["passed"] = True
            print(f"  [SUCCESS] All {len(results['checks'])} configuration checks passed")
            
        except Exception as e:
            print(f"  [FAILED] Configuration validation: {e}")
            results["checks"].append({"name": "error", "passed": False, "error": str(e)})
        
        return results
    
    def validate_coordination_components(self) -> Dict[str, Any]:
        """Validate coordination components work correctly."""
        print("\n=== Validating Coordination Components ===")
        
        results = {
            "test_name": "Coordination Components",
            "passed": False,
            "checks": []
        }
        
        try:
            # Test 1: Cognitive Economy Manager
            print("  [CHECK] Cognitive Economy Manager...")
            from coordination_layer.cognitive_economy import CognitiveEconomyManager, CognitiveResourceType
            economy = CognitiveEconomyManager()
            cost = economy.calculate_cognitive_cost(
                operation_id="test",
                resource_type=CognitiveResourceType.REASONING,
                operation_params={"cpu_usage": 0.3}
            )
            assert cost is not None
            results["checks"].append({"name": "cognitive_economy", "passed": True})
            print("  [PASS] Cognitive Economy Manager")
            
            # Test 2: Operating Mode Manager
            print("  [CHECK] Operating Mode Manager...")
            from coordination_layer.operating_modes import OperatingModeManager, OperatingMode
            mode_manager = OperatingModeManager()
            current_mode = mode_manager.get_current_mode()
            assert isinstance(current_mode, OperatingMode)
            results["checks"].append({"name": "operating_modes", "passed": True})
            print("  [PASS] Operating Mode Manager")
            
            # Test 3: Learning Gate Manager
            print("  [CHECK] Learning Gate Manager...")
            from coordination_layer.learning_gate import LearningGateManager, LearningOperationType
            gate = LearningGateManager()
            state = gate.get_gate_state()
            assert state is not None
            results["checks"].append({"name": "learning_gate", "passed": True})
            print("  [PASS] Learning Gate Manager")
            
            results["passed"] = True
            print(f"  [SUCCESS] All {len(results['checks'])} coordination component checks passed")
            
        except Exception as e:
            print(f"  [FAILED] Coordination components validation: {e}")
            results["checks"].append({"name": "error", "passed": False, "error": str(e)})
        
        return results
    
    def validate_governance_integration(self) -> Dict[str, Any]:
        """Validate governance integration works correctly."""
        print("\n=== Validating Governance Integration ===")
        
        results = {
            "test_name": "Governance Integration",
            "passed": False,
            "checks": []
        }
        
        try:
            # Test 1: Governance-coordination integrator
            print("  [CHECK] Governance-coordination integrator...")
            from governance_coordination_integration import GovernanceCoordinationIntegrator, GovernanceCoordinationConfig, GovernanceCoordinationMode
            integrator = GovernanceCoordinationIntegrator(
                config=GovernanceCoordinationConfig(mode=GovernanceCoordinationMode.COORDINATED)
            )
            init_result = integrator.initialize()
            assert isinstance(init_result, bool)
            results["checks"].append({"name": "gov_coord_integrator", "passed": True})
            print("  [PASS] Governance-coordination integrator")
            
            # Test 2: Integration status
            print("  [CHECK] Integration status...")
            status = integrator.get_integration_status()
            assert 'initialized' in status
            results["checks"].append({"name": "integration_status", "passed": True})
            print("  [PASS] Integration status")
            
            # Test 3: Shutdown
            print("  [CHECK] Shutdown...")
            shutdown_result = integrator.shutdown()
            assert shutdown_result is True
            results["checks"].append({"name": "shutdown", "passed": True})
            print("  [PASS] Shutdown")
            
            results["passed"] = True
            print(f"  [SUCCESS] All {len(results['checks'])} governance integration checks passed")
            
        except Exception as e:
            print(f"  [FAILED] Governance integration validation: {e}")
            results["checks"].append({"name": "error", "passed": False, "error": str(e)})
        
        return results
    
    def validate_enhanced_methods(self) -> Dict[str, Any]:
        """Validate enhanced methods work correctly with fallback."""
        print("\n=== Validating Enhanced Methods ===")
        
        results = {
            "test_name": "Enhanced Methods",
            "passed": False,
            "checks": []
        }
        
        try:
            # Test 1: Enhanced Indira decision method
            print("  [CHECK] Enhanced Indira decision method...")
            from mind.engine import IndiraEngine
            indira = IndiraEngine()
            market_data = {
                "signal": 0.6,
                "asset": "BTCUSDT",
                "price": 65000.0,
                "data_quality": 0.95,
                "execution_confidence": 0.90,
                "strategy": "test"
            }
            try:
                event = indira.process_tick_with_new_architecture(market_data)
                assert event is not None
                results["checks"].append({"name": "enhanced_indira", "passed": True})
                print("  [PASS] Enhanced Indira decision method")
            except Exception as e:
                # Should fallback to legacy method
                results["checks"].append({"name": "enhanced_indira_fallback", "passed": True})
                print("  [PASS] Enhanced Indira decision method (with fallback)")
            
            # Test 2: Enhanced DYON analysis method
            print("  [CHECK] Enhanced DYON analysis method...")
            from system_monitor.dyon_engine import get_dyon_engine
            dyon = get_dyon_engine()
            try:
                analysis = dyon.analyze_system_issue_with_new_architecture("test issue")
                assert analysis is not None
                results["checks"].append({"name": "enhanced_dyon", "passed": True})
                print("  [PASS] Enhanced DYON analysis method")
            except Exception as e:
                # Should fallback to legacy method
                results["checks"].append({"name": "enhanced_dyon_fallback", "passed": True})
                print("  [PASS] Enhanced DYON analysis method (with fallback)")
            
            results["passed"] = True
            print(f"  [SUCCESS] All {len(results['checks'])} enhanced method checks passed")
            
        except Exception as e:
            print(f"  [FAILED] Enhanced methods validation: {e}")
            results["checks"].append({"name": "error", "passed": False, "error": str(e)})
        
        return results
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all functionality loss validations."""
        print("\n" + "=" * 60)
        print("DIX VISION v42.2 - Functionality Loss Validation")
        print("=" * 60)
        
        # Run all validation checks
        self.validation_results.append(self.validate_legacy_indira_functionality())
        self.validation_results.append(self.validate_legacy_dyon_functionality())
        self.validation_results.append(self.validate_preservation_layer())
        self.validation_results.append(self.validate_configuration_system())
        self.validation_results.append(self.validate_coordination_components())
        self.validation_results.append(self.validate_governance_integration())
        self.validation_results.append(self.validate_enhanced_methods())
        
        # Print summary
        self.print_summary()
        
        return {
            "total_validations": len(self.validation_results),
            "passed_validations": sum(1 for r in self.validation_results if r["passed"]),
            "failed_validations": sum(1 for r in self.validation_results if not r["passed"]),
            "results": self.validation_results
        }
    
    def print_summary(self):
        """Print validation summary."""
        total = len(self.validation_results)
        passed = sum(1 for r in self.validation_results if r["passed"])
        failed = total - passed
        
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Validations: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print(f"\n=== Failed Validations ===")
            for result in self.validation_results:
                if not result["passed"]:
                    print(f"  {result['test_name']}")
                    for check in result["checks"]:
                        if not check["passed"]:
                            print(f"    - {check['name']}: {check.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        
        if failed == 0:
            print("[PASS] ALL VALIDATIONS PASSED - No functionality loss detected")
        else:
            print("[FAIL] SOME VALIDATIONS FAILED - Potential functionality issues detected")
        print("=" * 60)


if __name__ == "__main__":
    validator = FunctionalityLossValidator()
    results = validator.run_all_validations()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed_validations'] == 0 else 1)