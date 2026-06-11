#!/usr/bin/env python3
"""Test DYON Coding Assistant - Enhanced Local Devin CLI integration."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.dyon_coding_assistant import (
    DYONCodingAssistant,
    CodingTask,
    get_dyon_assistant,
)

def test_dyon_coding_assistant():
    """Test DYON Coding Assistant capabilities."""
    print("=" * 60)
    print("Testing DYON Coding Assistant")
    print("=" * 60)
    
    assistant = DYONCodingAssistant()
    
    # Test 1: Basic coding task
    print("\n[Test 1] Basic coding task")
    task = CodingTask(
        task_id="TASK-001",
        description="Create a function to calculate Fibonacci sequence",
        module="utils",
        priority="medium"
    )
    result = assistant.execute_coding_task(task)
    print(f"Task ID: {task.task_id}")
    print(f"Status: {result.get('status', 'unknown')}")
    assert result["status"] == "completed"
    print("[OK] Basic coding task executed")
    
    # Test 2: Refactor module
    print("\n[Test 2] Refactor module")
    result = assistant.refactor_module(
        "trading",
        "improve performance and reduce latency"
    )
    print(f"Status: {result.get('status', 'unknown')}")
    assert result["status"] == "completed"
    print("[OK] Module refactor executed")
    
    # Test 3: Add feature
    print("\n[Test 3] Add feature")
    result = assistant.add_feature(
        "cache_layer",
        "implement LRU cache eviction"
    )
    print(f"Status: {result.get('status', 'unknown')}")
    assert result["status"] == "completed"
    print("[OK] Feature addition executed")
    
    # Test 4: Fix bug
    print("\n[Test 4] Fix bug")
    result = assistant.fix_bug(
        "api_implementations.py",
        "handle rate limit errors gracefully"
    )
    print(f"Status: {result.get('status', 'unknown')}")
    assert result["status"] == "completed"
    print("[OK] Bug fix executed")
    
    # Test 5: Write tests
    print("\n[Test 5] Write tests")
    result = assistant.write_tests(
        "data_sources",
        "unit tests"
    )
    print(f"Status: {result.get('status', 'unknown')}")
    assert result["status"] == "completed"
    print("[OK] Test writing executed")
    
    # Test 6: Optimize performance
    print("\n[Test 6] Optimize performance")
    result = assistant.optimize_performance(
        "cache_layer",
        "cache hit rate"
    )
    print(f"Status: {result.get('status', 'unknown')}")
    assert result["status"] == "completed"
    print("[OK] Performance optimization executed")
    
    # Test 7: Add documentation
    print("\n[Test 7] Add documentation")
    result = assistant.add_documentation(
        "dyon_coding_assistant.py",
        "inline documentation"
    )
    print(f"Status: {result.get('status', 'unknown')}")
    assert result["status"] == "completed"
    print("[OK] Documentation addition executed")
    
    # Test 8: System evolution
    print("\n[Test 8] System evolution")
    result = assistant.evolve_system(
        "add autonomous learning capabilities"
    )
    print(f"Status: {result.get('status', 'unknown')}")
    assert result["status"] == "completed"
    print("[OK] System evolution executed")
    
    # Test 9: Task history
    print("\n[Test 9] Task history")
    history = assistant.get_task_history()
    print(f"Tasks in history: {len(history)}")
    assert len(history) >= 8
    print("[OK] Task history tracked")
    
    # Test 10: Singleton pattern
    print("\n[Test 10] Singleton pattern")
    assistant1 = get_dyon_assistant()
    assistant2 = get_dyon_assistant()
    assert assistant1 is assistant2
    print("[OK] Singleton pattern working")
    
    print("\n" + "=" * 60)
    print("All DYON Coding Assistant tests passed!")
    print("=" * 60)
    print("\n[SUCCESS] DYON can now:")
    print("   - Execute coding tasks with context")
    print("   - Refactor modules")
    print("   - Add features")
    print("   - Fix bugs")
    print("   - Write tests")
    print("   - Optimize performance")
    print("   - Add documentation")
    print("   - Evolve system autonomously")
    print("   - Track task history")
    print("\n[INFO] All capabilities work via Local Devin CLI (YOU)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_dyon_coding_assistant()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
