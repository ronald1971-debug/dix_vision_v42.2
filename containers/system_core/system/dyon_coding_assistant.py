#!/usr/bin/env python3
"""DYON Coding Assistant - Enhanced interface for DYON to call Local Devin CLI.

This module provides specialized methods for DYON to use Local Devin CLI
for system engineering tasks with context-aware capabilities.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from data_sources.external.api_implementations import LocalDevinAdapter

LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CodingTask:
    """A coding task for DYON to execute via Local Devin CLI."""

    task_id: str
    description: str
    module: str | None = None
    file_path: str | None = None
    priority: str = "medium"  # low, medium, high, critical
    context: dict[str, Any] = field(default_factory=dict)
    subtasks: list[str] = field(default_factory=list)

    def to_task_string(self) -> str:
        """Convert to task string for LocalDevinAdapter."""
        parts = [f"Task ID: {self.task_id}"]
        parts.append(f"Description: {self.description}")

        if self.module:
            parts.append(f"Module: {self.module}")
        if self.file_path:
            parts.append(f"File: {self.file_path}")
        if self.priority:
            parts.append(f"Priority: {self.priority}")

        if self.subtasks:
            parts.append("Subtasks:")
            for subtask in self.subtasks:
                parts.append(f"  - {subtask}")

        if self.context:
            parts.append("Context:")
            for key, value in self.context.items():
                parts.append(f"  {key}: {value}")

        return "\n".join(parts)


class DYONCodingAssistant:
    """Enhanced coding assistant for DYON's system engineering needs."""

    def __init__(self):
        self._devin = LocalDevinAdapter()
        self._task_history: list[dict[str, Any]] = []
        self._project_root = Path(__file__).parent.parent

    def execute_coding_task(self, task: CodingTask) -> dict[str, Any]:
        """Execute a coding task via Local Devin CLI."""
        LOG.info(f"DYON executing coding task: {task.task_id}")

        task_string = task.to_task_string()
        result = self._devin.execute_task(task_string, context=task.context)

        # Add to history
        self._task_history.append(
            {
                "task_id": task.task_id,
                "description": task.description,
                "result": result,
                "timestamp": result.get("timestamp_ns", 0),
            }
        )

        return result

    def refactor_module(self, module_name: str, goal: str) -> dict[str, Any]:
        """Refactor a module for a specific goal."""
        task = CodingTask(
            task_id=f"refactor-{module_name}-{self._generate_id()}",
            description=f"Refactor {module_name} for: {goal}",
            module=module_name,
            priority="high",
            context={"goal": goal, "type": "refactoring"},
        )
        return self.execute_coding_task(task)

    def add_feature(self, module_name: str, feature: str) -> dict[str, Any]:
        """Add a feature to a module."""
        task = CodingTask(
            task_id=f"feature-{module_name}-{self._generate_id()}",
            description=f"Add feature to {module_name}: {feature}",
            module=module_name,
            priority="medium",
            context={"feature": feature, "type": "feature_addition"},
        )
        return self.execute_coding_task(task)

    def fix_bug(self, file_path: str, bug_description: str) -> dict[str, Any]:
        """Fix a bug in a file."""
        task = CodingTask(
            task_id=f"bugfix-{self._generate_id()}",
            description=f"Fix bug in {file_path}: {bug_description}",
            file_path=file_path,
            priority="critical",
            context={"bug": bug_description, "type": "bug_fix"},
        )
        return self.execute_coding_task(task)

    def write_tests(self, module_name: str, test_type: str = "unit") -> dict[str, Any]:
        """Write tests for a module."""
        task = CodingTask(
            task_id=f"test-{module_name}-{self._generate_id()}",
            description=f"Write {test_type} tests for {module_name}",
            module=module_name,
            priority="medium",
            context={"test_type": test_type, "type": "test_writing"},
        )
        return self.execute_coding_task(task)

    def optimize_performance(self, module_name: str, metric: str) -> dict[str, Any]:
        """Optimize a module for a specific performance metric."""
        task = CodingTask(
            task_id=f"optimize-{module_name}-{self._generate_id()}",
            description=f"Optimize {module_name} for: {metric}",
            module=module_name,
            priority="high",
            context={"metric": metric, "type": "performance_optimization"},
            subtasks=[
                "Analyze current performance",
                "Identify bottlenecks",
                "Implement optimizations",
                "Add performance monitoring",
            ],
        )
        return self.execute_coding_task(task)

    def add_documentation(self, file_path: str, doc_type: str = "inline") -> dict[str, Any]:
        """Add documentation to a file."""
        task = CodingTask(
            task_id=f"docs-{self._generate_id()}",
            description=f"Add {doc_type} documentation to {file_path}",
            file_path=file_path,
            priority="low",
            context={"doc_type": doc_type, "type": "documentation"},
        )
        return self.execute_coding_task(task)

    def evolve_system(self, goal: str) -> dict[str, Any]:
        """Evolve the system for a specific goal (high-level system evolution)."""
        task = CodingTask(
            task_id=f"evolve-{self._generate_id()}",
            description=f"Evolve system for: {goal}",
            priority="critical",
            context={"goal": goal, "type": "system_evolution"},
            subtasks=[
                "Analyze current system architecture",
                "Identify required changes",
                "Implement system modifications",
                "Test and validate changes",
                "Update documentation",
            ],
        )
        return self.execute_coding_task(task)

    def get_task_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent task history."""
        return self._task_history[-limit:]

    def _generate_id(self) -> str:
        """Generate a unique task ID."""
        import time

        return str(int(time.time() * 1000))


# Singleton instance for DYON
_dyon_assistant: DYONCodingAssistant | None = None


def get_dyon_assistant() -> DYONCodingAssistant:
    """Get the DYON coding assistant singleton."""
    global _dyon_assistant
    if _dyon_assistant is None:
        _dyon_assistant = DYONCodingAssistant()
    return _dyon_assistant
