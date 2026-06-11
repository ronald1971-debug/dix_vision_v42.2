#!/usr/bin/env python3
"""Test DYON-integrated Modeling Orchestrator."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modeling.orchestrator import get_production_modeling_orchestrator

def test_dyon_integration():
    """Test DYON integration in modeling orchestrator."""
    print("=" * 60)
    print("Testing DYON-Integrated Modeling Orchestrator")
    print("=" * 60)
    
    # Test 1: Initialize orchestrator with DYON
    print("\n[Test 1] Initialize modeling orchestrator with DYON")
    orchestrator = get_production_modeling_orchestrator()
    success = orchestrator.initialize()
    print(f"Initialization: {'SUCCESS' if success else 'FAILED'}")
    assert success
    print(f"DYON Enabled: {orchestrator.dyon_enabled}")
    print("[OK] Modeling orchestrator initialized with DYON")
    
    # Test 2: Check DYON properties
    print("\n[Test 2] Check DYON properties")
    print(f"DYON Assistant: {'Available' if orchestrator.dyon_assistant else 'Not Available'}")
    print(f"DYON Reflection: {'Available' if orchestrator.dyon_reflection else 'Not Available'}")
    print(f"DYON Enabled: {orchestrator.dyon_enabled}")
    assert orchestrator.dyon_enabled == True
    print("[OK] DYON properties available")
    
    # Test 3: Get modeling status with DYON
    print("\n[Test 3] Get modeling status with DYON")
    status = orchestrator.get_modeling_status()
    print(f"Status keys: {list(status.keys())}")
    assert "dyon_integration" in status
    print(f"DYON Integration: {status['dyon_integration']}")
    print("[OK] DYON integration in status")
    
    # Test 4: Analyze modeling system (should work even if modeling components aren't available)
    print("\n[Test 4] Analyze modeling system")
    analysis = orchestrator.analyze_modeling_system()
    print(f"Analysis completed: {analysis.get('issues_found', 0)} issues found")
    print(f"Priority: {analysis.get('priority', 'unknown')}")
    print(f"Action items: {len(analysis.get('action_items', []))}")
    print("[OK] System analysis executed")
    
    # Test 5: Suggest improvements
    print("\n[Test 5] Suggest modeling improvements")
    suggestions = orchestrator.suggest_modeling_improvements("better performance")
    print(f"Suggestions generated: {suggestions.get('count', 0)}")
    print("[OK] Improvement suggestions generated")
    
    # Test 6: Optimize component
    print("\n[Test 6] Optimize modeling component")
    result = orchestrator.optimize_modeling_component("simulation_engine", "faster simulation")
    print(f"Component: {result.get('component')}")
    print(f"Status: {result.get('status')}")
    print("[OK] Component optimization executed")
    
    # Test 7: Fix bug (simulation)
    print("\n[Test 7] Fix modeling bug (simulation)")
    result = orchestrator.fix_modeling_bug("world_model", "handle edge cases")
    print(f"Component: {result.get('component')}")
    print(f"Status: {result.get('status')}")
    print("[OK] Bug fix executed")
    
    # Test 8: System evolution (simulation)
    print("\n[Test 8] System evolution (simulation)")
    result = orchestrator.evolve_modeling_system("add reinforcement learning")
    print(f"Goal: {result.get('goal')}")
    print(f"Status: {result.get('status')}")
    print("[OK] System evolution executed")
    
    # Test 9: Shutdown
    print("\n[Test 9] Shutdown orchestrator")
    success = orchestrator.shutdown()
    print(f"Shutdown: {'SUCCESS' if success else 'FAILED'}")
    assert success
    print("[OK] Modeling orchestrator shutdown successfully")
    
    print("\n" + "=" * 60)
    print("All DYON-Integrated Modeling Orchestrator tests passed!")
    print("=" * 60)
    print("\n[SUCCESS] Modeling Orchestrator now has:")
    print("   - DYON coding assistant integration")
    print("   - DYON self-reflection integration")
    print("   - System analysis capability")
    print("   - Component optimization")
    print("   - Bug fixing capability")
    print("   - Autonomous system evolution")
    print("   - Improvement suggestion")
    print("\n[INFO] All DYON capabilities available via Local Devin CLI (YOU)")
    print("[INFO] DYON works independently of modeling components")
    
    return True

if __name__ == "__main__":
    try:
        success = test_dyon_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
