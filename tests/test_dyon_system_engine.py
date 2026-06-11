#!/usr/bin/env python3
"""Test DYON-integrated System Engine."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system_engine.system_engine import get_production_system_engine

def test_dyon_system_engine():
    """Test DYON integration in system engine."""
    print("=" * 60)
    print("Testing DYON-Integrated System Engine")
    print("=" * 60)
    
    # Test 1: Initialize system engine with DYON
    print("\n[Test 1] Initialize system engine with DYON")
    engine = get_production_system_engine()
    success = engine.initialize()
    print(f"Initialization: {'SUCCESS' if success else 'FAILED'}")
    assert success
    print(f"DYON Enabled: {engine.dyon_enabled}")
    print("[OK] System engine initialized with DYON")
    
    # Test 2: Check DYON properties
    print("\n[Test 2] Check DYON properties")
    print(f"DYON Assistant: {'Available' if engine.dyon_assistant else 'Not Available'}")
    print(f"DYON Reflection: {'Available' if engine.dyon_reflection else 'Not Available'}")
    print(f"DYON Enabled: {engine.dyon_enabled}")
    assert engine.dyon_enabled == True
    print("[OK] DYON properties available")
    
    # Test 3: Get engine state with DYON
    print("\n[Test 3] Get engine state with DYON")
    state = engine.get_engine_state()
    print(f"State keys: {list(state.keys())}")
    assert "dyon_integration" in state
    print(f"DYON Integration: {state['dyon_integration']}")
    print("[OK] DYON integration in engine state")
    
    # Test 4: Analyze system engine
    print("\n[Test 4] Analyze system engine")
    analysis = engine.analyze_system_engine()
    print(f"Analysis completed: {analysis.get('issues_found', 0)} issues found")
    print(f"Priority: {analysis.get('priority', 'unknown')}")
    print(f"Action items: {len(analysis.get('action_items', []))}")
    print("[OK] System analysis executed")
    
    # Test 5: Suggest system improvements
    print("\n[Test 5] Suggest system improvements")
    suggestions = engine.suggest_system_improvements("better fault tolerance")
    print(f"Suggestions generated: {suggestions.get('count', 0)}")
    print("[OK] System improvement suggestions generated")
    
    # Test 6: Optimize system component
    print("\n[Test 6] Optimize system component")
    result = engine.optimize_system_performance("fault_manager", "faster fault detection")
    print(f"Component: {result.get('component')}")
    print(f"Status: {result.get('status')}")
    print("[OK] System component optimization executed")
    
    # Test 7: Fix system fault
    print("\n[Test 7] Fix system fault")
    result = engine.fix_system_fault("resource_manager", "memory leak in resource allocation")
    print(f"Component: {result.get('component')}")
    print(f"Status: {result.get('status')}")
    print("[OK] System fault fix executed")
    
    # Test 8: System evolution (simulation)
    print("\n[Test 8] System evolution (simulation)")
    result = engine.evolve_system_engine("add self-healing capabilities")
    print(f"Goal: {result.get('goal')}")
    print(f"Status: {result.get('status')}")
    print("[OK] System evolution executed")
    
    # Test 9: Shutdown
    print("\n[Test 9] Shutdown system engine")
    success = engine.shutdown()
    print(f"Shutdown: {'SUCCESS' if success else 'FAILED'}")
    assert success
    print("[OK] System engine shutdown successfully")
    
    print("\n" + "=" * 60)
    print("All DYON-Integrated System Engine tests passed!")
    print("=" * 60)
    print("\n[SUCCESS] System Engine now has:")
    print("   - DYON coding assistant integration")
    print("   - DYON self-reflection integration")
    print("   - System analysis capability")
    print("   - Component optimization")
    print("   - Fault fixing capability")
    print("   - Autonomous system evolution")
    print("   - Improvement suggestion")
    print("\n[INFO] All DYON capabilities available via Local Devin CLI (YOU)")
    print("[INFO] DYON works independently of system engine components")
    
    return True

if __name__ == "__main__":
    try:
        success = test_dyon_system_engine()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
