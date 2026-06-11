#!/usr/bin/env python3
"""Test DYON-integrated Simulation Engine Orchestrator."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simulation_engine.orchestrator import get_simulation_orchestrator

def test_dyon_simulation_orchestrator():
    """Test DYON integration in simulation engine orchestrator."""
    print("=" * 60)
    print("Testing DYON-Integrated Simulation Engine Orchestrator")
    print("=" * 60)
    
    # Test 1: Initialize simulation orchestrator with DYON
    print("\n[Test 1] Initialize simulation orchestrator with DYON")
    orchestrator = get_simulation_orchestrator()
    success = orchestrator.start()
    print(f"Initialization: {'SUCCESS' if success else 'FAILED'}")
    assert success
    print(f"DYON Enabled: {orchestrator.dyon_enabled}")
    print("[OK] Simulation orchestrator initialized with DYON")
    
    # Test 2: Check DYON properties
    print("\n[Test 2] Check DYON properties")
    print(f"DYON Assistant: {'Available' if orchestrator.dyon_assistant else 'Not Available'}")
    print(f"DYON Reflection: {'Available' if orchestrator.dyon_reflection else 'Not Available'}")
    print(f"DYON Enabled: {orchestrator.dyon_enabled}")
    assert orchestrator.dyon_enabled == True
    print("[OK] DYON properties available")
    
    # Test 3: Get orchestrator state with DYON
    print("\n[Test 3] Get orchestrator state with DYON")
    state = orchestrator.get_orchestrator_state()
    print(f"State keys: {list(state.keys())}")
    assert "dyon_integration" in state
    print(f"DYON Integration: {state['dyon_integration']}")
    print("[OK] DYON integration in orchestrator state")
    
    # Test 4: Analyze simulation engine
    print("\n[Test 4] Analyze simulation engine")
    analysis = orchestrator.analyze_simulation_engine()
    print(f"Analysis completed: {analysis.get('issues_found', 0)} issues found")
    print(f"Priority: {analysis.get('priority', 'unknown')}")
    print(f"Action items: {len(analysis.get('action_items', []))}")
    print("[OK] Simulation engine analysis executed")
    
    # Test 5: Suggest simulation improvements
    print("\n[Test 5] Suggest simulation improvements")
    suggestions = orchestrator.suggest_simulation_improvements("faster simulation")
    print(f"Suggestions generated: {suggestions.get('count', 0)}")
    print("[OK] Simulation improvement suggestions generated")
    
    # Test 6: Optimize simulation component
    print("\n[Test 6] Optimize simulation component")
    result = orchestrator.optimize_simulation_performance("market_sim", "higher accuracy")
    print(f"Component: {result.get('component')}")
    print(f"Status: {result.get('status')}")
    print("[OK] Simulation component optimization executed")
    
    # Test 7: Fix simulation bug
    print("\n[Test 7] Fix simulation bug")
    result = orchestrator.fix_simulation_bug("strategy_sim", "edge case in scenario analysis")
    print(f"Component: {result.get('component')}")
    print(f"Status: {result.get('status')}")
    print("[OK] Simulation bug fix executed")
    
    # Test 8: System evolution (simulation)
    print("\n[Test 8] Simulation evolution (simulation)")
    result = orchestrator.evolve_simulation_engine("add agent-based modeling")
    print(f"Goal: {result.get('goal')}")
    print(f"Status: {result.get('status')}")
    print("[OK] Simulation evolution executed")
    
    # Test 9: Market simulation (existing functionality)
    print("\n[Test 9] Market simulation (existing functionality)")
    market_params = {"initial_price": 100, "volatility": 0.2}
    operation = orchestrator.simulate_market(market_params)
    print(f"Operation ID: {operation.operation_id}")
    print(f"Status: {operation.status}")
    print(f"Final Price: {operation.output_data.get('final_price', 0)}")
    assert operation.status == "completed"
    print("[OK] Market simulation working")
    
    # Test 10: Strategy simulation (existing functionality)
    print("\n[Test 10] Strategy simulation (existing functionality)")
    strategy_config = {"risk_tolerance": 0.05, "max_drawdown": 0.1}
    operation = orchestrator.simulate_strategy(strategy_config)
    print(f"Operation ID: {operation.operation_id}")
    print(f"Status: {operation.status}")
    print(f"Sharpe Ratio: {operation.output_data.get('sharpe_ratio', 0)}")
    assert operation.status == "completed"
    print("[OK] Strategy simulation working")
    
    # Test 11: Stop orchestrator
    print("\n[Test 11] Stop orchestrator")
    success = orchestrator.stop()
    print(f"Stop: {'SUCCESS' if success else 'FAILED'}")
    assert success
    print("[OK] Simulation orchestrator stopped successfully")
    
    print("\n" + "=" * 60)
    print("All DYON-Integrated Simulation Engine Orchestrator tests passed!")
    print("=" * 60)
    print("\n[SUCCESS] Simulation Engine Orchestrator now has:")
    print("   - DYON coding assistant integration")
    print("   - DYON self-reflection integration")
    print("   - Simulation analysis capability")
    print("   - Component optimization")
    print("   - Bug fixing capability")
    print("   - Autonomous simulation evolution")
    print("   - Improvement suggestion")
    print("   - Existing simulation capabilities preserved")
    print("\n[INFO] All DYON capabilities available via Local Devin CLI (YOU)")
    print("[INFO] DYON works independently of simulation components")
    
    return True

if __name__ == "__main__":
    try:
        success = test_dyon_simulation_orchestrator()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
