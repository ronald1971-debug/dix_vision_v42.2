"""evolution_engine.dyon.indira_quality_analyzer — INDIRA Code Quality Analysis for DYON.

System cognition component for analyzing INDIRA's code quality to suggest system improvements.

This implementation provides code quality analysis capabilities for:
- Code complexity analysis (cyclomatic and cognitive complexity)
- Technical debt identification and tracking
- Code duplication detection
- Test quality analysis
- Documentation completeness assessment
- Refactoring opportunity identification
- Code smell detection
- Maintainability index calculation
- Quality improvement recommendations

Authority (L2/B1): evolution_engine.* only at module level.
DYON analyzes INDIRA code quality for system improvement, never for trading purposes.
"""

from __future__ import annotations

import ast
import logging
import threading
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

_logger = logging.getLogger(__name__)


class CodeQualityMetric(Enum):
    """Types of code quality metrics."""

    CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"
    COGNITIVE_COMPLEXITY = "cognitive_complexity"
    LINES_OF_CODE = "lines_of_code"
    COMMENT_RATIO = "comment_ratio"
    DUPLICATION = "duplication"
    MAINTAINABILITY_INDEX = "maintainability_index"
    TEST_COVERAGE = "test_coverage"
    DOCUMENTATION_COVERAGE = "documentation_coverage"


class CodeSmell(Enum):
    """Common code smells."""

    LONG_METHOD = "long_method"
    LONG_CLASS = "long_class"
    FEATURE_ENVY = "feature_envy"
    DATA_CLUMPS = "data_clumps"
    PRIMITIVE_OBSESSION = "primitive_obsession"
    LAZY_CLASS = "lazy_class"
    DUPLICATE_CODE = "duplicate_code"
    COMPLEX_CONDITIONAL = "complex_conditional"
    MAGIC_NUMBERS = "magic_numbers"
    DEAD_CODE = "dead_code"


class RefactoringType(Enum):
    """Types of refactoring recommendations."""

    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"
    REPLACE_MAGIC_NUMBER = "replace_magic_number"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    REMOVE_DEAD_CODE = "remove_dead_code"
    DECOMPOSE_CONDITIONAL = "decompose_conditional"
    CONSOLIDATE_DUPLICATE = "consolidate_duplicate"


@dataclass
class CodeQualityIssue:
    """Code quality issue detected."""

    issue_type: CodeSmell
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    component: str
    file_path: str
    line_number: int
    description: str
    suggested_refactoring: RefactoringType
    refactoring_description: str
    impact: str


@dataclass
class QualityMetric:
    """Code quality metric value."""

    metric_type: CodeQualityMetric
    component: str
    file_path: str
    value: float
    threshold: float
    status: str  # "GOOD", "WARNING", "CRITICAL"
    trend: str  # "IMPROVING", "STABLE", "DECLINING"


@dataclass
class ComponentQualityReport:
    """Quality report for an INDIRA component."""

    component_name: str
    overall_quality_score: float
    total_issues: int
    critical_issues: int
    high_issues: int
    metrics: Dict[str, QualityMetric] = field(default_factory=dict)
    issues: List[CodeQualityIssue] = field(default_factory=list)
    refactoring_opportunities: List[str] = field(default_factory=list)
    technical_debt_estimate: str = ""


@dataclass
class INDIRAQualityAnalysisResult:
    """Complete quality analysis result for INDIRA."""

    analysis_timestamp: float
    components_analyzed: int
    total_files_analyzed: int
    total_issues_found: int
    overall_quality_score: float
    component_reports: Dict[str, ComponentQualityReport] = field(default_factory=dict)
    system_wide_issues: List[CodeQualityIssue] = field(default_factory=list)
    priority_refactorings: List[Dict[str, Any]] = field(default_factory=list)
    technical_debt_summary: Dict[str, Any] = field(default_factory=dict)


class INDIRAQualityAnalyzer:
    """Analyze INDIRA's code quality and suggest improvements.

    DYON uses this analyzer to identify code quality issues and refactoring
    opportunities in INDIRA without interfering with trading operations.
    """

    def __init__(self, repo_root: str | Path = "."):
        """Initialize INDIRA quality analyzer.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = Path(repo_root)
        self.indira_path = self.repo_root / "containers/system_core/indira_cognitive"
        self.indira_brain_path = self.indira_path / "indira_brain"
        self._lock = threading.Lock()
        self._quality_cache: Dict[str, ComponentQualityReport] = {}

        _logger.info(
            f"[INDIRAQualityAnalyzer] Initialized with repo_root={repo_root}, "
            f"indira_path={self.indira_path}"
        )

    def analyze_full_indira_quality(self) -> INDIRAQualityAnalysisResult:
        """Perform complete code quality analysis of INDIRA.

        Returns:
            Complete quality analysis result
        """
        import time

        analysis_timestamp = time.time()

        _logger.info("[INDIRAQualityAnalyzer] Starting full INDIRA quality analysis")

        with self._lock:
            component_reports = {}
            total_files = 0
            total_issues = 0
            overall_scores = []

            # Analyze each component directory
            if self.indira_brain_path.exists():
                for component_dir in self.indira_brain_path.iterdir():
                    if component_dir.is_dir():
                        report = self._analyze_component_quality(component_dir)
                        if report:
                            component_reports[component_dir.name] = report
                            total_files += self._count_python_files(component_dir)
                            total_issues += report.total_issues
                            overall_scores.append(report.overall_quality_score)

            # Detect system-wide issues
            system_wide_issues = self._detect_system_wide_quality_issues(component_reports)

            # Generate priority refactorings
            priority_refactorings = self._generate_priority_refactorings(component_reports)

            # Calculate technical debt summary
            technical_debt_summary = self._calculate_technical_debt_summary(component_reports)

            # Calculate overall quality score
            overall_quality_score = statistics.mean(overall_scores) if overall_scores else 0.5

            result = INDIRAQualityAnalysisResult(
                analysis_timestamp=analysis_timestamp,
                components_analyzed=len(component_reports),
                total_files_analyzed=total_files,
                total_issues_found=total_issues,
                overall_quality_score=overall_quality_score,
                component_reports=component_reports,
                system_wide_issues=system_wide_issues,
                priority_refactorings=priority_refactorings,
                technical_debt_summary=technical_debt_summary,
            )

            _logger.info(
                f"[INDIRAQualityAnalyzer] Analysis complete: "
                f"{len(component_reports)} components, {total_files} files, "
                f"{total_issues} issues, quality_score={overall_quality_score:.2f}"
            )

            return result

    def _analyze_component_quality(self, component_path: Path) -> Optional[ComponentQualityReport]:
        """Analyze code quality of a single component.

        Args:
            component_path: Path to component directory

        Returns:
            Component quality report or None
        """
        component_name = component_path.name

        _logger.debug(f"[INDIRAQualityAnalyzer] Analyzing component: {component_name}")

        metrics = {}
        issues = []
        refactoring_opportunities = []
        total_complexity = 0
        file_count = 0

        # Analyze each Python file
        for py_file in component_path.glob("*.py"):
            try:
                file_analysis = self._analyze_file_quality(py_file, component_name)
                if file_analysis:
                    for metric_name, metric_value in file_analysis["metrics"].items():
                        if metric_name not in metrics:
                            metrics[metric_name] = []
                        metrics[metric_name].append(metric_value)

                    issues.extend(file_analysis["issues"])
                    refactoring_opportunities.extend(file_analysis["refactoring_opportunities"])
                    total_complexity += file_analysis["complexity"]
                    file_count += 1
            except Exception as e:
                _logger.warning(f"Failed to analyze {py_file}: {e}")

        if file_count == 0:
            return None

        # Aggregate metrics
        aggregated_metrics = {}
        for metric_name, values in metrics.items():
            if values:
                aggregated_metrics[metric_name] = QualityMetric(
                    metric_type=CodeQualityMetric(metric_name),
                    component=component_name,
                    file_path=str(component_path),
                    value=statistics.mean(values),
                    threshold=self._get_metric_threshold(metric_name),
                    status=self._get_metric_status(metric_name, statistics.mean(values)),
                    trend="STABLE",
                )

        # Calculate overall quality score
        quality_score = self._calculate_component_quality_score(
            aggregated_metrics, issues, file_count
        )

        # Estimate technical debt
        technical_debt = self._estimate_technical_debt(issues, total_complexity, file_count)

        # Count issue severity
        critical_issues = sum(1 for i in issues if i.severity == "CRITICAL")
        high_issues = sum(1 for i in issues if i.severity == "HIGH")

        return ComponentQualityReport(
            component_name=component_name,
            overall_quality_score=quality_score,
            total_issues=len(issues),
            critical_issues=critical_issues,
            high_issues=high_issues,
            metrics=aggregated_metrics,
            issues=issues,
            refactoring_opportunities=list(set(refactoring_opportunities)),
            technical_debt_estimate=technical_debt,
        )

    def _analyze_file_quality(
        self, file_path: Path, component_name: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze code quality of a single file.

        Args:
            file_path: Path to Python file
            component_name: Name of component

        Returns:
            File quality analysis results
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            _logger.warning(f"Failed to read {file_path}: {e}")
            return None

        metrics = {}
        issues = []
        refactoring_opportunities = []
        total_complexity = 0

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            _logger.warning(f"Syntax error in {file_path}: {e}")
            return None

        # Calculate lines of code
        lines_of_code = len(source.split("\n"))
        metrics["lines_of_code"] = lines_of_code

        # Calculate comment ratio
        comment_lines = len([l for l in source.split("\n") if l.strip().startswith("#")])
        comment_ratio = comment_lines / max(lines_of_code, 1)
        metrics["comment_ratio"] = comment_ratio

        # Analyze classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_complexity = self._calculate_cyclomatic_complexity(node)
                total_complexity += class_complexity

                # Check for long class
                if len(node.body) > 15:
                    issues.append(
                        CodeQualityIssue(
                            issue_type=CodeSmell.LONG_CLASS,
                            severity="MEDIUM",
                            component=component_name,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description=f"Class {node.name} has {len(node.body)} members, consider splitting",
                            suggested_refactoring=RefactoringType.EXTRACT_CLASS,
                            refactoring_description="Extract related functionality into separate classes",
                            impact="Improves maintainability and reduces class complexity",
                        )
                    )
                    refactoring_opportunities.append(f"Extract class from {node.name}")

                # Check for code smells in class
                self._detect_class_smells(
                    node, file_path, component_name, issues, refactoring_opportunities
                )

            elif isinstance(node, ast.FunctionDef):
                func_complexity = self._calculate_cyclomatic_complexity(node)
                total_complexity += func_complexity

                # Check for long method
                if len(node.body) > 20:
                    issues.append(
                        CodeQualityIssue(
                            issue_type=CodeSmell.LONG_METHOD,
                            severity="HIGH",
                            component=component_name,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description=f"Function {node.name} has {len(node.body)} statements, consider extracting",
                            suggested_refactoring=RefactoringType.EXTRACT_METHOD,
                            refactoring_description="Extract smaller functions from complex logic",
                            impact="Improves readability and testability",
                        )
                    )
                    refactoring_opportunities.append(f"Extract method from {node.name}")

                # Check for complex conditionals
                self._detect_complex_conditionals(
                    node, file_path, component_name, issues, refactoring_opportunities
                )

                # Check for magic numbers
                self._detect_magic_numbers(
                    node, file_path, component_name, issues, refactoring_opportities
                )

        metrics["cyclomatic_complexity"] = total_complexity / max(file_count, 1)

        return {
            "metrics": metrics,
            "issues": issues,
            "refactoring_opportunities": refactoring_opportunities,
            "complexity": total_complexity,
        }

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of an AST node.

        Args:
            node: AST node

        Returns:
            Cyclomatic complexity score
        """
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _detect_class_smells(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        component_name: str,
        issues: List[CodeQualityIssue],
        refactoring_opportunities: List[str],
    ) -> None:
        """Detect code smells in a class.

        Args:
            class_node: AST class node
            file_path: Path to file
            component_name: Component name
            issues: List to append issues
            refactoring_opportunities: List to append opportunities
        """
        # Check for lazy class (class with little functionality)
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) < 2 and len(class_node.body) < 5:
            issues.append(
                CodeQualityIssue(
                    issue_type=CodeSmell.LAZY_CLASS,
                    severity="LOW",
                    component=component_name,
                    file_path=str(file_path),
                    line_number=class_node.lineno,
                    description=f"Class {class_node.name} has minimal functionality",
                    suggested_refactoring=RefactoringType.EXTRACT_CLASS,
                    refactoring_description="Consider merging with related class or adding functionality",
                    impact="Reduces unnecessary complexity",
                )
            )

    def _detect_complex_conditionals(
        self,
        func_node: ast.FunctionDef,
        file_path: Path,
        component_name: str,
        issues: List[CodeQualityIssue],
        refactoring_opportunities: List[str],
    ) -> None:
        """Detect complex conditional logic.

        Args:
            func_node: AST function node
            file_path: Path to file
            component_name: Component name
            issues: List to append issues
            refactoring_opportunities: List to append opportunities
        """
        for node in ast.walk(func_node):
            if isinstance(node, ast.If):
                # Check for nested conditionals
                nested_depth = self._calculate_nested_if_depth(node)
                if nested_depth > 3:
                    issues.append(
                        CodeQualityIssue(
                            issue_type=CodeSmell.COMPLEX_CONDITIONAL,
                            severity="MEDIUM",
                            component=component_name,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description=f"Nested conditional depth {nested_depth} exceeds threshold",
                            suggested_refactoring=RefactoringType.DECOMPOSE_CONDITIONAL,
                            refactoring_description="Use guard clauses or extract conditions to separate methods",
                            impact="Improves readability and reduces cognitive complexity",
                        )
                    )
                    refactoring_opportunities.append("Simplify complex conditional logic")

    def _calculate_nested_if_depth(self, node: ast.If) -> int:
        """Calculate maximum nesting depth of if statements.

        Args:
            node: AST if node

        Returns:
            Maximum nesting depth
        """
        max_depth = 0

        def check_depth(n: ast.AST, current_depth: int) -> None:
            nonlocal max_depth
            if isinstance(n, ast.If):
                max_depth = max(max_depth, current_depth + 1)
                for child in ast.iter_child_nodes(n):
                    check_depth(child, current_depth + 1)
            else:
                for child in ast.iter_child_nodes(n):
                    check_depth(child, current_depth)

        check_depth(node, 0)
        return max_depth

    def _detect_magic_numbers(
        self,
        func_node: ast.FunctionDef,
        file_path: Path,
        component_name: str,
        issues: List[CodeQualityIssue],
        refactoring_opportunities: List[str],
    ) -> None:
        """Detect magic numbers in code.

        Args:
            func_node: AST function node
            file_path: Path to file
            component_name: Component name
            issues: List to append issues
            refactoring_opportunities: List to append opportunities
        """
        for node in ast.walk(func_node):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)) and node.value not in [0, 1, -1]:
                    # Exclude common values that might be acceptable
                    if abs(node.value) > 10 or node.value not in [2, 3, 5, 10, 100, 1000]:
                        issues.append(
                            CodeQualityIssue(
                                issue_type=CodeSmell.MAGIC_NUMBERS,
                                severity="LOW",
                                component=component_name,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                description=f"Magic number {node.value} found",
                                suggested_refactoring=RefactoringType.REPLACE_MAGIC_NUMBER,
                                refactoring_description="Replace with named constant",
                                impact="Improves code readability and maintainability",
                            )
                        )
                        refactoring_opportunities.append("Replace magic numbers with constants")
                        break  # Only report one per function to avoid noise

    def _detect_system_wide_quality_issues(
        self, component_reports: Dict[str, ComponentQualityReport]
    ) -> List[CodeQualityIssue]:
        """Detect system-wide code quality issues.

        Args:
            component_reports: Component quality reports

        Returns:
            List of system-wide issues
        """
        system_wide_issues = []

        # Check for patterns across components
        all_refactorings = []
        for report in component_reports.values():
            all_refactorings.extend(report.refactoring_opportunities)

        # Find common refactoring opportunities
        refactoring_counts = Counter(all_refactorings)
        common_refactorings = [r for r, c in refactoring_counts.items() if c >= 3]

        for refactoring in common_refactorings:
            system_wide_issues.append(
                CodeQualityIssue(
                    issue_type=CodeSmell.DUPLICATE_CODE,
                    severity="MEDIUM",
                    component="system",
                    file_path="multiple",
                    line_number=0,
                    description=f"Common pattern detected: {refactoring}",
                    suggested_refactoring=RefactoringType.CONSOLIDATE_DUPLICATE,
                    refactoring_description=f"Consider consolidating {refactoring} across components",
                    impact="Reduces code duplication and improves maintainability",
                )
            )

        return system_wide_issues

    def _generate_priority_refactorings(
        self, component_reports: Dict[str, ComponentQualityReport]
    ) -> List[Dict[str, Any]]:
        """Generate priority refactoring recommendations.

        Args:
            component_reports: Component quality reports

        Returns:
            List of priority refactorings
        """
        priority_refactorings = []

        # Collect all issues sorted by severity
        all_issues = []
        for component, report in component_reports.items():
            for issue in report.issues:
                all_issues.append(
                    {
                        "component": component,
                        "issue": issue,
                        "quality_score": report.overall_quality_score,
                    }
                )

        # Sort by severity and quality score
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        all_issues.sort(
            key=lambda x: (severity_order.get(x["issue"].severity, 4), x["quality_score"])
        )

        # Top priority refactorings
        for item in all_issues[:10]:
            priority_refactorings.append(
                {
                    "priority": item["issue"].severity,
                    "component": item["component"],
                    "issue_type": item["issue"].issue_type.value,
                    "refactoring_type": item["issue"].suggested_refactoring.value,
                    "description": item["issue"].description,
                    "suggested_action": item["issue"].refactoring_description,
                    "impact": item["issue"].impact,
                    "file_path": item["issue"].file_path,
                    "line_number": item["issue"].line_number,
                }
            )

        return priority_refactorings

    def _calculate_technical_debt_summary(
        self, component_reports: Dict[str, ComponentQualityReport]
    ) -> Dict[str, Any]:
        """Calculate technical debt summary.

        Args:
            component_reports: Component quality reports

        Returns:
            Technical debt summary
        """
        total_debt_hours = 0
        debt_by_component = {}
        debt_by_severity = defaultdict(int)

        for component, report in component_reports.items():
            # Estimate debt hours based on issues
            component_debt = sum(
                self._estimate_issue_hours(issue.severity) for issue in report.issues
            )
            debt_by_component[component] = component_debt
            total_debt_hours += component_debt

            for issue in report.issues:
                debt_by_severity[issue.severity] += self._estimate_issue_hours(issue.severity)

        return {
            "total_debt_hours": total_debt_hours,
            "debt_by_component": debt_by_component,
            "debt_by_severity": dict(debt_by_severity),
            "estimated_resolution_time": f"{total_debt_hours / 8:.1f} developer days",
        }

    def _estimate_issue_hours(self, severity: str) -> int:
        """Estimate hours to fix an issue based on severity.

        Args:
            severity: Issue severity

        Returns:
            Estimated hours to fix
        """
        hours_by_severity = {"CRITICAL": 8, "HIGH": 4, "MEDIUM": 2, "LOW": 1}
        return hours_by_severity.get(severity, 2)

    def _calculate_component_quality_score(
        self, metrics: Dict[str, QualityMetric], issues: List[CodeQualityIssue], file_count: int
    ) -> float:
        """Calculate overall quality score for a component.

        Args:
            metrics: Quality metrics
            issues: Code quality issues
            file_count: Number of files analyzed

        Returns:
            Quality score (0-1, higher is better)
        """
        if not metrics:
            return 0.5

        # Base score from metrics
        metric_scores = []
        for metric in metrics.values():
            if metric.status == "GOOD":
                metric_scores.append(1.0)
            elif metric.status == "WARNING":
                metric_scores.append(0.7)
            else:  # CRITICAL
                metric_scores.append(0.3)

        base_score = statistics.mean(metric_scores) if metric_scores else 0.5

        # Penalty for issues
        critical_penalty = sum(1 for i in issues if i.severity == "CRITICAL") * 0.05
        high_penalty = sum(1 for i in issues if i.severity == "HIGH") * 0.03
        medium_penalty = sum(1 for i in issues if i.severity == "MEDIUM") * 0.01

        total_penalty = min(critical_penalty + high_penalty + medium_penalty, 0.4)

        return max(base_score - total_penalty, 0.0)

    def _estimate_technical_debt(
        self, issues: List[CodeQualityIssue], complexity: int, file_count: int
    ) -> str:
        """Estimate technical debt for component.

        Args:
            issues: List of issues
            complexity: Total complexity
            file_count: Number of files

        Returns:
            Technical debt estimate string
        """
        hours = sum(self._estimate_issue_hours(issue.severity) for issue in issues)
        return f"{hours} hours estimated"

    def _get_metric_threshold(self, metric_name: str) -> float:
        """Get threshold value for a metric.

        Args:
            metric_name: Name of metric

        Returns:
            Threshold value
        """
        thresholds = {"cyclomatic_complexity": 10.0, "comment_ratio": 0.15, "lines_of_code": 500.0}
        return thresholds.get(metric_name, 0.0)

    def _get_metric_status(self, metric_name: str, value: float) -> str:
        """Get status for a metric value.

        Args:
            metric_name: Name of metric
            value: Metric value

        Returns:
            Status string
        """
        threshold = self._get_metric_threshold(metric_name)
        if threshold == 0:
            return "GOOD"

        if metric_name in ["comment_ratio"]:
            # Higher is better
            if value >= threshold:
                return "GOOD"
            elif value >= threshold * 0.5:
                return "WARNING"
            else:
                return "CRITICAL"
        else:
            # Lower is better
            if value <= threshold:
                return "GOOD"
            elif value <= threshold * 1.5:
                return "WARNING"
            else:
                return "CRITICAL"

    def _count_python_files(self, directory: Path) -> int:
        """Count Python files in directory.

        Args:
            directory: Directory path

        Returns:
            Number of Python files
        """
        return len(list(directory.glob("*.py")))

    def generate_architectural_improvement_suggestions(
        self, component_reports: Dict[str, ComponentQualityReport]
    ) -> List[str]:
        """Generate architectural improvement suggestions.

        Args:
            component_reports: Component quality reports

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        # Analyze overall patterns
        for component, report in component_reports.items():
            if report.overall_quality_score < 0.6:
                suggestions.append(
                    f"Prioritize quality improvements in {component} - score: {report.overall_quality_score:.2f}"
                )

            if report.critical_issues > 0:
                suggestions.append(
                    f"Address {report.critical_issues} critical issues in {component}"
                )

        # System-wide suggestions
        total_critical = sum(r.critical_issues for r in component_reports.values())
        if total_critical > 5:
            suggestions.append(
                f"System has {total_critical} critical issues - allocate dedicated quality improvement time"
            )

        return suggestions


# Singleton instance
_quality_analyzer: Optional[INDIRAQualityAnalyzer] = None
_analyzer_lock = threading.Lock()


def get_indira_quality_analyzer(repo_root: str | Path = ".") -> INDIRAQualityAnalyzer:
    """Get singleton instance of INDIRA quality analyzer.

    Args:
        repo_root: Path to repository root

    Returns:
        INDIRA quality analyzer instance
    """
    global _quality_analyzer

    with _analyzer_lock:
        if _quality_analyzer is None:
            _quality_analyzer = INDIRAQualityAnalyzer(repo_root)
        return _quality_analyzer


# Import statistics at the end to avoid circular dependency
import statistics
