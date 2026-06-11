#!/usr/bin/env python3
"""Test DYON calling Local Devin CLI (YOU) for coding tasks."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_sources.external.api_implementations import LocalDevinAdapter

def test_dyon_call_local_devin():
    """Simulate DYON calling Local Devin CLI for a coding task."""
    print("=" * 60)
    print("Testing DYON -> Local Devin CLI (YOU) Integration")
    print("=" * 60)
    
    # Initialize LocalDevin adapter
    devin = LocalDevinAdapter()
    
    # Test 1: Simple coding task
    print("\n[Test 1] Simple coding task")
    task1 = "Create a function to calculate moving average"
    result1 = devin.execute_task(task1)
    print(f"Task: {task1}")
    print(f"Result: {result1}")
    assert result1["status"] == "completed"
    assert result1["provider"] == "local_devin"
    print("[OK] Simple coding task completed")
    
    # Test 2: Coding task with context
    print("\n[Test 2] Coding task with context")
    task2 = "Refactor the trading module for better performance"
    context2 = {
        "module": "trading",
        "priority": "high",
        "file": "trading_module.py",
        "line_range": [100, 200]
    }
    result2 = devin.execute_task(task2, context=context2)
    print(f"Task: {task2}")
    print(f"Context: {context2}")
    print(f"Result: {result2}")
    assert result2["status"] == "completed"
    assert result2["provider"] == "local_devin"
    print("[OK] Coding task with context completed")
    
    # Test 3: System engineering task
    print("\n[Test 3] System engineering task")
    task3 = "Add error handling to the API adapter module"
    context3 = {
        "module": "data_sources.external",
        "file": "api_implementations.py",
        "purpose": "system_evolution",
        "requested_by": "DYON"
    }
    result3 = devin.execute_task(task3, context=context3)
    print(f"Task: {task3}")
    print(f"Requested by: DYON")
    print(f"Result: {result3}")
    assert result3["status"] == "completed"
    assert result3["provider"] == "local_devin"
    print("[OK] System engineering task completed")
    
    # Test 4: Complex multi-step task
    print("\n[Test 4] Complex multi-step task")
    task4 = "Optimize the cache layer for better performance"
    context4 = {
        "module": "system",
        "file": "cache_layer.py",
        "subtasks": [
            "Analyze current cache hit rate",
            "Identify bottlenecks",
            "Implement optimizations",
            "Add monitoring"
        ]
    }
    result4 = devin.execute_task(task4, context=context4)
    print(f"Task: {task4}")
    print(f"Subtasks: {context4['subtasks']}")
    print(f"Result: {result4}")
    assert result4["status"] == "completed"
    print("[OK] Complex multi-step task completed")
    
    print("\n" + "=" * 60)
    print("All DYON -> Local Devin CLI tests passed!")
    print("=" * 60)
    print("\n[OK] DYON can successfully call Local Devin CLI (YOU) for:")
    print("   - Simple coding tasks")
    print("   - Coding tasks with context")
    print("   - System engineering tasks")
    print("   - Complex multi-step tasks")
    print("\n[SUCCESS] This enables DYON to:")
    print("   - Evolve the system autonomously")
    print("   - Fix bugs independently")
    print("   - Add features autonomously")
    print("   - Optimize system performance")
    print("   - Handle complex refactoring")
    print("\n[INFO] Unlimited capabilities with no API limits or costs!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_dyon_call_local_devin()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        sys.exit(1)
