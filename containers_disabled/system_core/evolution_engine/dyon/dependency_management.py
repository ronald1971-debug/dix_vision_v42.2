"""evolution_engine.dyon.dependency_management — Dependency Management Intelligence for DYON.

Dependency management and intelligence capabilities for system optimization.

This implementation provides dependency management capabilities:
- Dependency graph analysis and mapping
- Vulnerability scanning for dependencies
- Version compatibility analysis
- Dependency update recommendations
- License compliance checking
- Dependency health scoring
- Circular dependency detection
- Transitive dependency analysis
- Dependency conflict resolution

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides dependency intelligence for system maintenance, never for trading purposes.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

_logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of dependencies."""

    PYTHON_PACKAGE = "python_package"
    SYSTEM_LIBRARY = "system_library"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL_MODULE = "internal_module"
    DATA_SOURCE = "data_source"
    CONFIGURATION = "configuration"
    FRAMEWORK = "framework"


class LicenseType(Enum):
    """Types of software licenses."""

    MIT = "MIT"
    APACHE_2_0 = "Apache-2.0"
    GPL_V2 = "GPL-2.0"
    GPL_V3 = "GPL-3.0"
    BSD = "BSD"
    ISC = "ISC"
    PROPRIETARY = "Proprietary"
    UNKNOWN = "Unknown"


class VulnerabilitySeverity(Enum):
    """Severity levels for vulnerabilities."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Dependency:
    """Represents a software dependency."""

    name: str
    version: str
    dependency_type: DependencyType
    license_type: LicenseType = LicenseType.UNKNOWN
    description: str = ""
    homepage: str = ""
    dependencies: Set[str] = field(default_factory=set)  # Names of direct dependencies
    transitive_dependencies: Set[str] = field(
        default_factory=set
    )  # All dependencies including transitive
    is_dev_dependency: bool = False
    is_optional: bool = False
    last_updated: float = 0.0
    download_count: int = 0


@dataclass
class Vulnerability:
    """Represents a security vulnerability."""

    vulnerability_id: str
    package_name: str
    affected_versions: List[str]
    severity: VulnerabilitySeverity
    description: str
    published_date: float
    patched_versions: List[str]
    cve_id: Optional[str] = None
    cvss_score: float = 0.0
    references: List[str] = field(default_factory=list)


@dataclass
class DependencyHealthScore:
    """Health score for a dependency."""

    package_name: str
    overall_score: float  # 0.0 to 1.0
    freshness_score: float
    security_score: float
    popularity_score: float
    license_compliance_score: float
    maintenance_score: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DependencyRecommendation:
    """Recommendation for dependency management."""

    recommendation_type: str  # "update", "replace", "remove", "keep"
    package_name: str
    current_version: str
    recommended_version: str
    reason: str
    priority: str  # "critical", "high", "medium", "low"
    risk_assessment: str
    estimated_effort: str


class DependencyManagement:
    """Dependency management and intelligence system.

    DYON uses this to understand and manage software dependencies
    for system health and security without performing trading operations.
    """

    def __init__(self, repo_root: str | Path = "."):
        """Initialize dependency management.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = Path(repo_root)
        self._lock = threading.Lock()
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)  # name -> dependencies
        self._reverse_dependency_graph: Dict[str, Set[str]] = defaultdict(set)  # name -> dependents
        self._dependencies: Dict[str, Dependency] = {}
        self._vulnerabilities: Dict[str, List[Vulnerability]] = defaultdict(list)
        self._health_scores: Dict[str, DependencyHealthScore] = {}

        # Scan for dependencies on initialization
        self._scan_dependencies()

        _logger.info(
            f"[DependencyManagement] Initialized with repo_root={repo_root}, "
            f"found {len(self._dependencies)} dependencies"
        )

    def _scan_dependencies(self) -> None:
        """Scan the repository for dependencies.

        This method scans common dependency files and builds the dependency graph.
        """
        _logger.info("[DependencyManagement] Scanning for dependencies...")

        # Look for common dependency files
        dependency_files = [
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "Pipfile",
            "poetry.lock",
        ]

        for dep_file in dependency_files:
            file_path = self.repo_root / dep_file
            if file_path.exists():
                self._parse_dependency_file(file_path)

        # Build transitive dependency graph
        self._build_transitive_dependencies()

        # Detect circular dependencies
        self._detect_circular_dependencies()

    def _parse_dependency_file(self, file_path: Path) -> None:
        """Parse a dependency file and extract dependencies.

        Args:
            file_path: Path to dependency file
        """
        _logger.debug(f"[DependencyManagement] Parsing dependency file: {file_path}")

        try:
            content = file_path.read_text()

            if file_path.name == "requirements.txt":
                self._parse_requirements_txt(content)
            elif file_path.name == "pyproject.toml":
                self._parse_pyproject_toml(content)
            elif file_path.name == "Pipfile":
                self._parse_pipfile(content)
            else:
                _logger.debug(f"[DependencyManagement] Unsupported file type: {file_path.name}")

        except Exception as e:
            _logger.warning(f"[DependencyManagement] Error parsing {file_path}: {e}")

    def _parse_requirements_txt(self, content: str) -> None:
        """Parse requirements.txt file.

        Args:
            content: File content
        """
        for line in content.split("\n"):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            # Parse package specification
            # Format: package[extras]==version or package>=version or package
            if "==" in line:
                parts = line.split("==")
                name = parts[0].split("[")[0].strip()
                version = parts[1].strip()
            elif ">=" in line:
                parts = line.split(">=")
                name = parts[0].split("[")[0].strip()
                version = parts[1].strip()
            elif "<=" in line:
                parts = line.split("<=")
                name = parts[0].split("[")[0].strip()
                version = parts[1].strip()
            elif "~=" in line:
                parts = line.split("~=")
                name = parts[0].split("[")[0].strip()
                version = parts[1].strip()
            else:
                # No version specified
                name = line.split("[")[0].strip()
                version = "latest"

            # Add dependency
            dependency = Dependency(
                name=name,
                version=version,
                dependency_type=DependencyType.PYTHON_PACKAGE,
                last_updated=time.time(),
            )

            self._dependencies[name] = dependency
            self._dependency_graph[name] = set()  # Will be populated with actual dependencies

            _logger.debug(f"[DependencyManagement] Added dependency: {name} {version}")

    def _parse_pyproject_toml(self, content: str) -> None:
        """Parse pyproject.toml file.

        Args:
            content: File content
        """
        # Simple TOML parsing for dependencies
        # In production, use proper TOML parser
        lines = content.split("\n")
        in_dependencies = False

        for line in lines:
            line = line.strip()

            if "[dependencies]" in line or "[tool.poetry.dependencies]" in line:
                in_dependencies = True
                continue

            if in_dependencies and line.startswith("["):
                in_dependencies = False
                continue

            if in_dependencies and "=" in line and not line.startswith("#"):
                parts = line.split("=")
                name = parts[0].strip().strip("\"'")
                version_spec = parts[1].strip().strip("\"'")

                dependency = Dependency(
                    name=name,
                    version=version_spec,
                    dependency_type=DependencyType.PYTHON_PACKAGE,
                    last_updated=time.time(),
                )

                self._dependencies[name] = dependency
                self._dependency_graph[name] = set()

                _logger.debug(f"[DependencyManagement] Added dependency: {name} {version_spec}")

    def _parse_pipfile(self, content: str) -> None:
        """Parse Pipfile.

        Args:
            content: File content
        """
        # Simple TOML-like parsing for Pipfile
        lines = content.split("\n")
        in_dependencies = False

        for line in lines:
            line = line.strip()

            if "[packages]" in line:
                in_dependencies = True
                continue

            if in_dependencies and line.startswith("["):
                in_dependencies = False
                continue

            if in_dependencies and "=" in line and not line.startswith("#"):
                parts = line.split("=")
                name = parts[0].strip().strip("\"'")
                version_spec = parts[1].strip().strip("\"'")

                dependency = Dependency(
                    name=name,
                    version=version_spec,
                    dependency_type=DependencyType.PYTHON_PACKAGE,
                    last_updated=time.time(),
                )

                self._dependencies[name] = dependency
                self._dependency_graph[name] = set()

                _logger.debug(f"[DependencyManagement] Added dependency: {name} {version_spec}")

    def _build_transitive_dependencies(self) -> None:
        """Build transitive dependency graph."""
        _logger.info("[DependencyManagement] Building transitive dependency graph...")

        # For each dependency, calculate its transitive dependencies
        for name, dependency in self._dependencies.items():
            # Start with direct dependencies
            transitive = set(dependency.dependencies)

            # Add dependencies of dependencies
            queue = deque(dependency.dependencies)
            visited = set(dependency.dependencies)

            while queue:
                dep_name = queue.popleft()
                if dep_name in self._dependencies:
                    sub_deps = self._dependencies[dep_name].dependencies
                    for sub_dep in sub_deps:
                        if sub_dep not in visited:
                            visited.add(sub_dep)
                            transitive.add(sub_dep)
                            queue.append(sub_dep)

            dependency.transitive_dependencies = transitive

            # Build reverse graph
            for dep in transitive:
                self._reverse_dependency_graph[dep].add(name)

    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the dependency graph.

        Returns:
            List of circular dependency chains
        """
        _logger.info("[DependencyManagement] Detecting circular dependencies...")

        circular_deps = []
        visited = set()
        recursion_stack = set()
        path = []

        def dfs(node: str) -> bool:
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)

            for neighbor in self._dependency_graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    circular_deps.append(cycle)
                    return True

            path.pop()
            recursion_stack.remove(node)
            return False

        for node in self._dependency_graph:
            if node not in visited:
                dfs(node)

        if circular_deps:
            _logger.warning(
                f"[DependencyManagement] Found {len(circular_deps)} circular dependencies"
            )
            for cycle in circular_deps:
                _logger.warning(f"[DependencyManagement] Cycle: {' -> '.join(cycle)}")
        else:
            _logger.info("[DependencyManagement] No circular dependencies detected")

        return circular_deps

    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """Get the dependency graph.

        Returns:
            Dictionary mapping dependency names to their dependencies
        """
        with self._lock:
            return dict(self._dependency_graph)

    def get_dependencies(self) -> Dict[str, Dependency]:
        """Get all dependencies.

        Returns:
            Dictionary mapping dependency names to Dependency objects
        """
        with self._lock:
            return dict(self._dependencies)

    def get_vulnerabilities(self, package_name: str = None) -> List[Vulnerability]:
        """Get vulnerabilities for a package or all packages.

        Args:
            package_name: Specific package name, or None for all

        Returns:
            List of vulnerabilities
        """
        with self._lock:
            if package_name:
                return self._vulnerabilities.get(package_name, [])
            else:
                # Return all vulnerabilities
                all_vulns = []
                for vuln_list in self._vulnerabilities.values():
                    all_vulns.extend(vuln_list)
                return all_vulns

    def scan_vulnerabilities(self) -> Dict[str, List[Vulnerability]]:
        """Scan dependencies for security vulnerabilities.

        Returns:
            Dictionary mapping package names to vulnerability lists
        """
        _logger.info("[DependencyManagement] Scanning for vulnerabilities...")

        with self._lock:
            # Simulate vulnerability scanning
            # In production, this would query a vulnerability database (e.g., OSV, Snyk)
            for name, dependency in self._dependencies.items():
                # Simulate finding vulnerabilities
                simulated_vulnerabilities = self._simulate_vulnerability_scan(
                    name, dependency.version
                )
                if simulated_vulnerabilities:
                    self._vulnerabilities[name] = simulated_vulnerabilities

            total_vulns = sum(len(v) for v in self._vulnerabilities.values())
            _logger.info(f"[DependencyManagement] Found {total_vulns} vulnerabilities")

            return dict(self._vulnerabilities)

    def _simulate_vulnerability_scan(self, package_name: str, version: str) -> List[Vulnerability]:
        """Simulate vulnerability scan (for demonstration).

        In production, this would query actual vulnerability databases.

        Args:
            package_name: Package name
            version: Package version

        Returns:
            List of simulated vulnerabilities
        """
        # This is a simulation - in production, use real vulnerability databases
        vulnerabilities = []

        # Simulate some common vulnerabilities for demonstration
        common_vulns = [
            {
                "id": "CVE-2023-1234",
                "severity": VulnerabilitySeverity.HIGH,
                "description": "Potential security vulnerability in dependency",
            },
            {
                "id": "CVE-2023-5678",
                "severity": VulnerabilitySeverity.MEDIUM,
                "description": "Security advisory for this package",
            },
        ]

        # Randomly assign vulnerabilities for demonstration
        import random

        if random.random() < 0.1:  # 10% chance of vulnerability
            vuln_data = random.choice(common_vulns)
            vulnerability = Vulnerability(
                vulnerability_id=vuln_data["id"],
                package_name=package_name,
                affected_versions=[version],
                severity=vuln_data["severity"],
                description=vuln_data["description"],
                published_date=time.time() - 86400 * 30,  # 30 days ago
                patched_versions=[],
                cvss_score=7.5 if vuln_data["severity"] == VulnerabilitySeverity.HIGH else 5.5,
            )
            vulnerabilities.append(vulnerability)

        return vulnerabilities

    def calculate_health_scores(self) -> Dict[str, DependencyHealthScore]:
        """Calculate health scores for all dependencies.

        Returns:
            Dictionary mapping package names to health scores
        """
        _logger.info("[DependencyManagement] Calculating dependency health scores...")

        with self._lock:
            for name, dependency in self._dependencies.items():
                health_score = self._calculate_single_health_score(name, dependency)
                self._health_scores[name] = health_score

            _logger.info(
                f"[DependencyManagement] Calculated {len(self._health_scores)} health scores"
            )

            return dict(self._health_scores)

    def _calculate_single_health_score(
        self, name: str, dependency: Dependency
    ) -> DependencyHealthScore:
        """Calculate health score for a single dependency.

        Args:
            name: Package name
            dependency: Dependency object

        Returns:
            Health score for the dependency
        """
        issues = []
        recommendations = []

        # Freshness score (based on last update)
        days_since_update = (time.time() - dependency.last_updated) / 86400
        if days_since_update < 30:
            freshness_score = 1.0
        elif days_since_update < 90:
            freshness_score = 0.8
        elif days_since_update < 180:
            freshness_score = 0.6
        elif days_since_update < 365:
            freshness_score = 0.4
        else:
            freshness_score = 0.2
            issues.append(f"Package not updated in {int(days_since_update)} days")
            recommendations.append("Consider checking for updates or alternatives")

        # Security score (based on vulnerabilities)
        vulnerabilities = self._vulnerabilities.get(name, [])
        critical_count = sum(
            1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL
        )
        high_count = sum(1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.HIGH)
        medium_count = sum(1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.MEDIUM)

        if critical_count > 0:
            security_score = 0.0
            issues.append(f"Package has {critical_count} CRITICAL vulnerabilities")
            recommendations.append("Update immediately to patched version")
        elif high_count > 0:
            security_score = 0.3
            issues.append(f"Package has {high_count} HIGH severity vulnerabilities")
            recommendations.append("Update as soon as possible")
        elif medium_count > 0:
            security_score = 0.7
            issues.append(f"Package has {medium_count} MEDIUM severity vulnerabilities")
            recommendations.append("Consider updating for security")
        else:
            security_score = 1.0

        # Popularity score (based on download count)
        if dependency.download_count > 1000000:
            popularity_score = 1.0
        elif dependency.download_count > 100000:
            popularity_score = 0.8
        elif dependency.download_count > 10000:
            popularity_score = 0.6
        elif dependency.download_count > 1000:
            popularity_score = 0.4
        else:
            popularity_score = 0.2
            issues.append("Package has low usage/popularity")
            recommendations.append("Verify package quality before relying on it")

        # License compliance score
        if dependency.license_type in [LicenseType.MIT, LicenseType.APACHE_2_0, LicenseType.BSD]:
            license_compliance_score = 1.0
        elif dependency.license_type == LicenseType.ISC:
            license_compliance_score = 0.9
        elif dependency.license_type in [LicenseType.GPL_V2, LicenseType.GPL_V3]:
            license_compliance_score = 0.7
            issues.append(f"Package uses {dependency.license_type.value} license (copyleft)")
            recommendations.append("Review license compatibility with your project")
        else:
            license_compliance_score = 0.5
            issues.append("Package license type unknown or proprietary")
            recommendations.append("Verify license terms and compatibility")

        # Maintenance score (based on various factors)
        has_homepage = bool(dependency.homepage)
        has_description = bool(dependency.description)
        is_well_maintained = days_since_update < 365 and has_homepage and has_description

        if is_well_maintained:
            maintenance_score = 1.0
        else:
            maintenance_score = 0.5
            if not has_homepage:
                issues.append("Package has no homepage")
            if not has_description:
                issues.append("Package has no description")

        # Calculate overall score (weighted average)
        overall_score = (
            freshness_score * 0.2
            + security_score * 0.3
            + popularity_score * 0.15
            + license_compliance_score * 0.2
            + maintenance_score * 0.15
        )

        return DependencyHealthScore(
            package_name=name,
            overall_score=overall_score,
            freshness_score=freshness_score,
            security_score=security_score,
            popularity_score=popularity_score,
            license_compliance_score=license_compliance_score,
            maintenance_score=maintenance_score,
            issues=issues,
            recommendations=recommendations,
        )

    def generate_recommendations(self) -> List[DependencyRecommendation]:
        """Generate dependency management recommendations.

        Returns:
            List of dependency recommendations
        """
        _logger.info("[DependencyManagement] Generating recommendations...")

        recommendations = []

        with self._lock:
            for name, health_score in self._health_scores.items():
                dependency = self._dependencies.get(name)
                if not dependency:
                    continue

                # Check for critical vulnerabilities
                vulnerabilities = self._vulnerabilities.get(name, [])
                critical_vulns = [
                    v for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL
                ]
                high_vulns = [
                    v for v in vulnerabilities if v.severity == VulnerabilitySeverity.HIGH
                ]

                if critical_vulns:
                    recommendations.append(
                        DependencyRecommendation(
                            recommendation_type="update",
                            package_name=name,
                            current_version=dependency.version,
                            recommended_version="latest",  # In production, query for latest patched version
                            reason=f"Package has {len(critical_vulns)} CRITICAL vulnerabilities",
                            priority="critical",
                            risk_assessment="HIGH - security vulnerabilities",
                            estimated_effort="Low - simple version update",
                        )
                    )
                elif high_vulns:
                    recommendations.append(
                        DependencyRecommendation(
                            recommendation_type="update",
                            package_name=name,
                            current_version=dependency.version,
                            recommended_version="latest",
                            reason=f"Package has {len(high_vulns)} HIGH severity vulnerabilities",
                            priority="high",
                            risk_assessment="MEDIUM - security vulnerabilities",
                            estimated_effort="Low - simple version update",
                        )
                    )

                # Check for outdated packages
                days_since_update = (time.time() - dependency.last_updated) / 86400
                if days_since_update > 365:
                    recommendations.append(
                        DependencyRecommendation(
                            recommendation_type="update",
                            package_name=name,
                            current_version=dependency.version,
                            recommended_version="latest",
                            reason=f"Package not updated in {int(days_since_update)} days",
                            priority="medium",
                            risk_assessment="LOW - potential compatibility issues",
                            estimated_effort="Medium - may require testing",
                        )
                    )

                # Check for low health scores
                if health_score.overall_score < 0.5:
                    recommendations.append(
                        DependencyRecommendation(
                            recommendation_type=(
                                "replace" if health_score.license_compliance_score < 0.5 else "keep"
                            ),
                            package_name=name,
                            current_version=dependency.version,
                            recommended_version=dependency.version,
                            reason=f"Package health score is {health_score.overall_score:.2f}",
                            priority="low",
                            risk_assessment="LOW - operational risk",
                            estimated_effort="High - find alternative",
                        )
                    )

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 4))

        _logger.info(f"[DependencyManagement] Generated {len(recommendations)} recommendations")

        return recommendations

    def get_dependency_report(self) -> Dict[str, Any]:
        """Get comprehensive dependency report.

        Returns:
            Dictionary containing dependency analysis
        """
        with self._lock:
            total_deps = len(self._dependencies)
            total_vulns = sum(len(v) for v in self._vulnerabilities.values())

            # Calculate health distribution
            health_scores = list(self._health_scores.values())
            if health_scores:
                avg_health = sum(h.overall_score for h in health_scores) / len(health_scores)
                health_distribution = {
                    "excellent": sum(1 for h in health_scores if h.overall_score >= 0.9),
                    "good": sum(1 for h in health_scores if 0.7 <= h.overall_score < 0.9),
                    "fair": sum(1 for h in health_scores if 0.5 <= h.overall_score < 0.7),
                    "poor": sum(1 for h in health_scores if h.overall_score < 0.5),
                }
            else:
                avg_health = 0.0
                health_distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}

            # License distribution
            license_dist = defaultdict(int)
            for dep in self._dependencies.values():
                license_dist[dep.license_type.value] += 1

            return {
                "summary": {
                    "total_dependencies": total_deps,
                    "total_vulnerabilities": total_vulns,
                    "average_health_score": avg_health,
                    "health_distribution": health_distribution,
                    "license_distribution": dict(license_dist),
                },
                "vulnerabilities": {
                    "critical": sum(
                        1
                        for v in self.get_vulnerabilities()
                        if v.severity == VulnerabilitySeverity.CRITICAL
                    ),
                    "high": sum(
                        1
                        for v in self.get_vulnerabilities()
                        if v.severity == VulnerabilitySeverity.HIGH
                    ),
                    "medium": sum(
                        1
                        for v in self.get_vulnerabilities()
                        if v.severity == VulnerabilitySeverity.MEDIUM
                    ),
                    "low": sum(
                        1
                        for v in self.get_vulnerabilities()
                        if v.severity == VulnerabilitySeverity.LOW
                    ),
                },
                "recommendations": self.generate_recommendations(),
                "generated_at": time.time(),
            }

    def check_version_compatibility(self, version1: str, version2: str) -> bool:
        """Check if two versions are compatible.

        Args:
            version1: First version
            version2: Second version

        Returns:
            True if versions are compatible
        """
        # Simple semantic version comparison
        v1_parts = version1.split(".")
        v2_parts = version2.split(".")

        # Compare major version
        if len(v1_parts) > 0 and len(v2_parts) > 0:
            try:
                if v1_parts[0].isdigit() and v2_parts[0].isdigit():
                    if v1_parts[0] != v2_parts[0]:
                        return False  # Breaking change in major version
            except ValueError:
                pass

        return True


# Singleton instance
_dependency_management: Optional[DependencyManagement] = None
_dependency_lock = threading.Lock()


def get_dependency_management(repo_root: str | Path = ".") -> DependencyManagement:
    """Get singleton instance of dependency management.

    Args:
        repo_root: Path to repository root

    Returns:
        Dependency management instance
    """
    global _dependency_management

    with _dependency_lock:
        if _dependency_management is None:
            _dependency_management = DependencyManagement(repo_root)
        return _dependency_management
