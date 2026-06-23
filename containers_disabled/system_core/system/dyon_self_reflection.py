#!/usr/bin/env python3
"""DYON Self-Reflection Module - Enables DYON to analyze and improve its own code.

This module provides self-reflection capabilities for DYON to:
- Analyze its own code quality
- Identify potential improvements
- Suggest refactoring opportunities
- Detect anti-patterns
- Propose architectural improvements
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

from system.dyon_coding_assistant import CodingTask, get_dyon_assistant

LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CodeIssue:
    """A code issue identified during self-reflection."""

    severity: str  # low, medium, high, critical
    category: str  # performance, security, maintainability, bug, architecture
    description: str
    file_path: str
    line_number: int | None = None
    suggestion: str = ""
    impact: str = ""

    def to_markdown(self) -> str:
        """Convert to markdown for reporting."""
        md = f"### [{self.severity.upper()}] {self.category}\n"
        md += f"**Description**: {self.description}\n"
        md += f"**File**: `{self.file_path}`"
        if self.line_number:
            md += f":{self.line_number}"
        md += "\n"
        if self.suggestion:
            md += f"**Suggestion**: {self.suggestion}\n"
        if self.impact:
            md += f"**Impact**: {self.impact}\n"
        return md


@dataclass(frozen=True, slots=True)
class ReflectionResult:
    """Result of a self-reflection analysis."""

    issues: List[CodeIssue]
    summary: str
    action_items: List[str]
    priority: str  # low, medium, high

    def to_report(self) -> str:
        """Generate a markdown report."""
        report = "# DYON Self-Reflection Report\n\n"
        report += f"## Summary\n{self.summary}\n\n"
        report += f"## Priority: {self.priority.upper()}\n\n"
        report += f"## Issues Found: {len(self.issues)}\n\n"

        # Group by severity
        by_severity = {}
        for issue in self.issues:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)

        for severity in ["critical", "high", "medium", "low"]:
            if severity in by_severity:
                report += f"## {severity.upper()} Issues ({len(by_severity[severity])})\n\n"
                for issue in by_severity[severity]:
                    report += issue.to_markdown() + "\n"

        report += "## Action Items\n\n"
        for i, item in enumerate(self.action_items, 1):
            report += f"{i}. {item}\n"

        return report


class DYONSelfReflection:
    """Self-reflection capabilities for DYON."""

    def __init__(self):
        self._assistant = get_dyon_assistant()
        self._project_root = Path(__file__).parent.parent

    def analyze_codebase(self, focus: str = "general") -> ReflectionResult:
        """Analyze the entire codebase for issues and improvements.

        Args:
            focus: Analysis focus (general, performance, security, maintainability)
        """
        LOG.info(f"DYON analyzing codebase with focus: {focus}")

        # Use Local Devin CLI to analyze the codebase
        task_description = f"""
Analyze the DIX VISION codebase for {focus} improvements.
Focus on:
- Code quality issues
- Performance bottlenecks
- Security vulnerabilities
- Maintainability problems
- Architecture improvements

Provide specific file paths and line numbers where relevant.
"""

        task = CodingTask(
            task_id=f"analyze-codebase-{focus}",
            description=task_description,
            priority="high",
            context={"focus": focus, "type": "codebase_analysis"},
        )

        result = self._assistant.execute_coding_task(task)

        # Parse result into structured format
        issues = self._parse_analysis_result(result)

        # Generate action items
        action_items = self._generate_action_items(issues)

        # Determine priority
        priority = self._determine_priority(issues)

        summary = f"Codebase analysis complete with {len(issues)} issues found. "
        summary += f"Priority: {priority}. {len([i for i in issues if i.severity in ['critical', 'high']])} "
        summary += "critical/high priority issues."

        return ReflectionResult(
            issues=issues, summary=summary, action_items=action_items, priority=priority
        )

    def analyze_module(self, module_name: str) -> ReflectionResult:
        """Analyze a specific module for issues and improvements."""
        LOG.info(f"DYON analyzing module: {module_name}")

        task_description = f"""
Analyze the {module_name} module for:
- Code quality
- Performance issues
- Security vulnerabilities
- Architecture improvements
- Testing coverage

Provide specific recommendations with file paths.
"""

        task = CodingTask(
            task_id=f"analyze-module-{module_name}",
            description=task_description,
            module=module_name,
            priority="medium",
            context={"module": module_name, "type": "module_analysis"},
        )

        result = self._assistant.execute_coding_task(task)

        issues = self._parse_analysis_result(result)
        action_items = self._generate_action_items(issues)
        priority = self._determine_priority(issues)

        summary = f"Module {module_name} analysis complete with {len(issues)} issues found."

        return ReflectionResult(
            issues=issues, summary=summary, action_items=action_items, priority=priority
        )

    def suggest_improvements(self, goal: str) -> List[str]:
        """Suggest improvements to achieve a specific goal."""
        LOG.info(f"DYON suggesting improvements for: {goal}")

        task_description = f"""
Suggest improvements to the DIX VISION system to achieve: {goal}

Consider:
- Architecture changes
- Performance optimizations
- Feature additions
- Code quality improvements
- Testing improvements
- Documentation improvements

Provide actionable suggestions with priorities.
"""

        task = CodingTask(
            task_id=f"suggest-improvements-{goal}",
            description=task_description,
            priority="medium",
            context={"goal": goal, "type": "improvement_suggestions"},
        )

        result = self._assistant.execute_coding_task(task)

        suggestions = self._parse_suggestions(result.get("output", ""))
        return suggestions

    def implement_reflection_results(self, reflection: ReflectionResult) -> dict[str, Any]:
        """Implement the results of a self-reflection analysis.

        This is a high-level autonomous operation that should be used carefully.
        """
        LOG.warning(
            f"DYON implementing reflection results: {len(reflection.action_items)} action items"
        )

        # Start with critical/high priority issues
        critical_issues = [i for i in reflection.issues if i.severity in ["critical", "high"]]

        results = {"fixed_issues": [], "failed_issues": [], "summary": ""}

        for issue in critical_issues:
            try:
                if issue.category == "performance":
                    result = self._assistant.optimize_performance(
                        Path(issue.file_path).stem, issue.description
                    )
                    results["fixed_issues"].append(issue)
                elif issue.category == "bug":
                    result = self._assistant.fix_bug(issue.file_path, issue.description)
                    results["fixed_issues"].append(issue)
                elif issue.category == "maintainability":
                    result = self._assistant.refactor_module(
                        Path(issue.file_path).stem, issue.description
                    )
                    results["fixed_issues"].append(issue)
            except Exception as e:
                LOG.error(f"Failed to fix issue: {issue.description}: {e}")
                results["failed_issues"].append(issue)

        results["summary"] = (
            f"Fixed {len(results['fixed_issues'])} issues, {len(results['failed_issues'])} failed."
        )
        return results

    def _parse_analysis_result(self, result: dict[str, Any]) -> list[CodeIssue]:
        """Parse the analysis result into structured CodeIssue objects."""
        # For now, return empty list - in production, this would parse
        # the actual output from Local Devin CLI
        return []

    def _generate_action_items(self, issues: List[CodeIssue]) -> List[str]:
        """Generate action items from identified issues."""
        action_items = []
        for issue in issues:
            if issue.suggestion:
                action_items.append(issue.suggestion)
            else:
                action_items.append(f"Fix {issue.category} issue in {issue.file_path}")
        return action_items

    def _determine_priority(self, issues: list[CodeIssue]) -> str:
        """Determine the overall priority based on issues."""
        critical_count = sum(1 for i in issues if i.severity == "critical")
        high_count = sum(1 for i in issues if i.severity == "high")

        if critical_count > 0:
            return "critical"
        elif high_count > 2:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"

    def _parse_suggestions(self, output: str) -> List[str]:
        """Parse suggestions from output."""
        # For now, return a simple split by newlines
        # In production, this would be more sophisticated
        lines = output.split("\n")
        suggestions = [line.strip() for line in lines if line.strip()]
        return suggestions


# Singleton instance
_self_reflection: DYONSelfReflection | None = None


def get_self_reflection() -> DYONSelfReflection:
    """Get the DYON self-reflection singleton."""
    global _self_reflection
    if _self_reflection is None:
        _self_reflection = DYONSelfReflection()
    return _self_reflection
