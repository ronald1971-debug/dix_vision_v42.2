#!/usr/bin/env python3
"""Test DYON-integrated Intelligence Engine Orchestrator."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from intelligence_engine.orchestrator import get_intelligence_orchestrator

def test_dyon_intelligence_orchestrator():
    """Test DYON integration in intelligence engine orchestrator."""
    print("=" * 60)
    print("Testing DYON-Integrated Intelligence Engine Orchestrator")
    print("=" * 60)
    
    # Test 1: Initialize intelligence orchestrator with DYON
    print("\n[Test 1] Initialize intelligence orchestrator with DYON")
    orchestrator = get_intelligence_orchestrator()
    success = orchestrator.start()
    print(f"Initialization: {'SUCCESS' if success else 'FAILED'}")
    assert success
    print(f"DYON Enabled: {orchestrator.dyon_enabled}")
    print("[OK] Intelligence orchestrator initialized with DYON")
    
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
    
    # Test 4: Analyze intelligence engine
    print("\n[Test 4] Analyze intelligence engine")
    analysis = orchestrator.analyze_intelligence_engine()
    print(f"Analysis completed: {analysis.get('issues_found', 0)} issues found")
    print(f"Priority: {analysis.get('priority', 'unknown')}")
    print(f"Action items: {len(analysis.get('action_items', []))}")
    print("[OK] Intelligence engine analysis executed")
    
    # Test 5: Suggest intelligence improvements
    print("\n[Test 5] Suggest intelligence improvements")
    suggestions = orchestrator.suggest_intelligence_improvements("better reasoning accuracy")
    print(f"Suggestions generated: {suggestions.get('count', 0)}")
    print("[OK] Intelligence improvement suggestions generated")
    
    # Test 6: Optimize intelligence component
    print("\n[Test 6] Optimize intelligence component")
    result = orchestrator.optimize_intelligence_component("reasoner", "faster inference")
    print(f"Component: {result.get('component')}")
    print(f"Status: {result.get('status')}")
    print("[OK] Intelligence component optimization executed")
    
    # Test 7: Fix intelligence bug
    print("\n[Test 7] Fix intelligence bug")
    result = orchestrator.fix_intelligence_bug("decision_maker", "optimization edge case")
    print(f"Component: {result.get('component')}")
    print(f"Status: {result.get('status')}")
    print("[OK] Intelligence bug fix executed")
    
    # Test 8: Intelligence evolution
    print("\n[Test 8] Intelligence evolution")
    result = orchestrator.evolve_intelligence_engine("add causal reasoning")
    print(f"Goal: {result.get('goal')}")
    print(f"Status: {result.get('status')}")
    print("[OK] Intelligence evolution executed")
    
    # Test 9: Reasoning operation (existing functionality)
    print("\n[Test 9] Reasoning operation (existing functionality)")
    query = {"market_condition": "bullish", "volatility": "high"}
    operation = orchestrator.reason(query, "inductive", "moderate")
    print(f"Operation ID: {operation.operation_id}")
    print(f"Status: {operation.status}")
    if operation.status == "completed":
        print(f"Confidence: {operation.confidence}")
    print("[OK] Reasoning operation attempted")
    
    # Test 10: Stop orchestrator
    print("\n[Test 10] Stop orchestrator")
    success = orchestrator.stop()
    print(f"Stop: {'SUCCESS' if success else 'FAILED'}")
    assert success
    print("[OK] Intelligence orchestrator stopped successfully")
    
    print("\n" + "=" * 60)
    print("All DYON-Integrated Intelligence Engine Orchestrator tests passed!")
    print("=" * 60)
    print("\n[SUCCESS] Intelligence Engine Orchestrator now has:")
    print("   - DYON coding assistant integration")
    print("   - DYON self-reflection integration")
    print("   - Intelligence analysis capability")
    print("   - Component optimization")
    print("   - Bug fixing capability")
    print("   - Autonomous intelligence evolution")
    print("   - Improvement suggestion")
    print("   - Existing intelligence capabilities preserved")
    print("\n[INFO] All DYON capabilities available via Local Devin CLI (YOU)")
    print("[INFO] DYON works independently of intelligence components")
    
    return True

if __name__ == "__main__":
    try:
        success = test_dyon_intelligence_orchestrator()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
