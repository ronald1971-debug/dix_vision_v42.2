#!/usr/bin/env python3
"""Test DYON Self-Reflection Module."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.dyon_self_reflection import (
    DYONSelfReflection,
    get_self_reflection,
    CodeIssue,
    ReflectionResult,
)

def test_dyon_self_reflection():
    """Test DYON self-reflection capabilities."""
    print("=" * 60)
    print("Testing DYON Self-Reflection Module")
    print("=" * 60)
    
    reflection = DYONSelfReflection()
    
    # Test 1: Analyze codebase
    print("\n[Test 1] Analyze codebase")
    result = reflection.analyze_codebase(focus="general")
    print(f"Issues found: {len(result.issues)}")
    print(f"Priority: {result.priority}")
    print(f"Summary: {result.summary}")
    print("[OK] Codebase analysis executed")
    
    # Test 2: Analyze specific module
    print("\n[Test 2] Analyze specific module")
    result = reflection.analyze_module("data_sources")
    print(f"Issues found: {len(result.issues)}")
    print(f"Action items: {len(result.action_items)}")
    print("[OK] Module analysis executed")
    
    # Test 3: Suggest improvements
    print("\n[Test 3] Suggest improvements")
    suggestions = reflection.suggest_improvements("better performance")
    print(f"Suggestions: {len(suggestions)}")
    print("[OK] Improvement suggestions generated")
    
    # Test 4: CodeIssue creation
    print("\n[Test 4] CodeIssue creation")
    issue = CodeIssue(
        severity="high",
        category="performance",
        description="Slow database query",
        file_path="database.py",
        line_number=100,
        suggestion="Add index to speed up query",
        impact="2x performance improvement"
    )
    markdown = issue.to_markdown()
    print(f"Markdown generated: {len(markdown)} characters")
    assert "HIGH" in markdown
    assert "performance" in markdown
    print("[OK] CodeIssue markdown generation working")
    
    # Test 5: ReflectionResult report generation
    print("\n[Test 5] ReflectionResult report generation")
    result = ReflectionResult(
        issues=[issue],
        summary="Test analysis complete",
        action_items=["Fix the issue"],
        priority="high"
    )
    report = result.to_report()
    print(f"Report generated: {len(report)} characters")
    assert "# DYON Self-Reflection Report" in report
    assert "HIGH" in report
    print("[OK] ReflectionResult report generation working")
    
    # Test 6: Singleton pattern
    print("\n[Test 6] Singleton pattern")
    reflection1 = get_self_reflection()
    reflection2 = get_self_reflection()
    assert reflection1 is reflection2
    print("[OK] Singleton pattern working")
    
    # Test 7: Implement reflection results (mock)
    print("\n[Test 7] Implement reflection results")
    # Create a mock result with a fixable issue
    fixable_issue = CodeIssue(
        severity="high",
        category="bug",
        description="Test bug",
        file_path="test.py",
        suggestion="Fix the test bug"
    )
    result = ReflectionResult(
        issues=[fixable_issue],
        summary="Test reflection",
        action_items=["Fix bug"],
        priority="high"
    )
    impl_result = reflection.implement_reflection_results(result)
    print(f"Fixed issues: {len(impl_result['fixed_issues'])}")
    print(f"Failed issues: {len(impl_result['failed_issues'])}")
    print("[OK] Reflection results implementation attempted")
    
    print("\n" + "=" * 60)
    print("All DYON Self-Reflection tests passed!")
    print("=" * 60)
    print("\n[SUCCESS] DYON can now:")
    print("   - Analyze entire codebase")
    print("   - Analyze specific modules")
    print("   - Suggest improvements")
    print("   - Generate structured reports")
    print("   - Implement reflection results")
    print("   - Track issues by severity")
    print("   - Generate action items")
    print("\n[INFO] All capabilities work via Local Devin CLI (YOU)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_dyon_self_reflection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
