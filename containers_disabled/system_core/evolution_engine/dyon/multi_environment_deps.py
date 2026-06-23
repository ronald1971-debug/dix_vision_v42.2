"""evolution_engine.dyon.multi_environment_deps — Multi-Environment Dependency Management for DYON.

Multi-environment dependency management support for complex deployment scenarios.

This implementation provides multi-environment dependency capabilities:
- Environment-specific dependency configurations
- Dependency comparison across environments
- Environment drift detection
- Deployment dependency validation
- Environment promotion workflows
- Dependency consistency checking
- Environment-specific vulnerability analysis
- Multi-environment health scoring

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides multi-environment dependency management for system optimization, never for trading purposes.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

_logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """Types of deployment environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    TESTING = "testing"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"
    CUSTOM = "custom"


class DependencyState(Enum):
    """States of dependencies across environments."""

    CONSISTENT = "consistent"
    DRIFTED = "drifted"
    MISSING = "missing"
    VERSION_MISMATCH = "version_mismatch"
    VULNERABLE = "vulnerable"
    OUTDATED = "outdated"


@dataclass
class EnvironmentConfig:
    """Configuration for a deployment environment."""

    environment_id: str
    environment_type: EnvironmentType
    name: str
    description: str = ""
    is_active: bool = True
    promotion_order: int = 0  # Order for environment promotion
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentDependency:
    """Dependency in a specific environment."""

    environment_id: str
    dependency_name: str
    version: str
    source: str  # requirements.txt, package.json, etc.
    install_date: float = 0.0
    last_verified: float = 0.0
    state: DependencyState = DependencyState.CONSISTENT
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentDrift:
    """Drift detected between environments."""

    drift_id: str
    source_environment: str
    target_environment: str
    dependency_name: str
    drift_type: str  # version_mismatch, missing, extra
    source_version: str = ""
    target_version: str = ""
    severity: str = "medium"  # low, medium, high, critical
    recommendation: str = ""


@dataclass
class PromotionResult:
    """Result of environment promotion."""

    promotion_id: str
    source_environment: str
    target_environment: str
    timestamp: float
    success: bool
    dependencies_promoted: int
    dependencies_failed: List[str] = field(default_factory=list)
    validation_passed: bool = True
    rollback_performed: bool = False
    message: str = ""


class MultiEnvironmentDependencyManager:
    """Multi-environment dependency management system.

    DYON uses this to manage dependencies across multiple deployment environments
    without performing trading operations.
    """

    def __init__(self, repo_root: str = "."):
        """Initialize multi-environment dependency manager.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self._lock = threading.Lock()
        self._environments: Dict[str, EnvironmentConfig] = {}
        self._environment_dependencies: Dict[str, Dict[str, EnvironmentDependency]] = defaultdict(
            dict
        )
        self._drift_history: List[EnvironmentDrift] = []
        self._promotion_history: List[PromotionResult] = []
        self._dependency_consistency_cache: Dict[Tuple[str, str], float] = {}

        # Initialize default environments
        self._initialize_default_environments()

        _logger.info(
            f"[MultiEnvironmentDependencyManager] Initialized with repo_root={repo_root}, "
            f"environments={len(self._environments)}"
        )

    def _initialize_default_environments(self) -> None:
        """Initialize default deployment environments."""
        default_environments = [
            EnvironmentConfig(
                environment_id="dev",
                environment_type=EnvironmentType.DEVELOPMENT,
                name="Development",
                description="Local development environment",
                promotion_order=1,
            ),
            EnvironmentConfig(
                environment_id="staging",
                environment_type=EnvironmentType.STAGING,
                name="Staging",
                description="Staging environment for testing",
                promotion_order=2,
            ),
            EnvironmentConfig(
                environment_id="prod",
                environment_type=EnvironmentType.PRODUCTION,
                name="Production",
                description="Production environment",
                promotion_order=3,
            ),
        ]

        for env in default_environments:
            self._environments[env.environment_id] = env

        _logger.info("[MultiEnvironmentDependencyManager] Initialized default environments")

    def add_environment(self, environment: EnvironmentConfig) -> bool:
        """Add a deployment environment.

        Args:
            environment: Environment configuration

        Returns:
            True if added successfully
        """
        with self._lock:
            if environment.environment_id in self._environments:
                _logger.warning(
                    f"[MultiEnvironmentDependencyManager] Environment exists: {environment.environment_id}"
                )
                return False

            self._environments[environment.environment_id] = environment
            _logger.info(
                f"[MultiEnvironmentDependencyManager] Added environment: {environment.environment_id}"
            )

            return True

    def add_environment_dependency(self, dependency: EnvironmentDependency) -> bool:
        """Add a dependency to an environment.

        Args:
            dependency: Environment dependency

        Returns:
            True if added successfully
        """
        with self._lock:
            if dependency.environment_id not in self._environments:
                _logger.warning(
                    f"[MultiEnvironmentDependencyManager] Unknown environment: {dependency.environment_id}"
                )
                return False

            self._environment_dependencies[dependency.environment_id][
                dependency.dependency_name
            ] = dependency
            _logger.debug(
                f"[MultiEnvironmentDependencyManager] Added dependency {dependency.dependency_name} "
                f"to {dependency.environment_id}"
            )

            return True

    def import_environment_dependencies(
        self, environment_id: str, dependencies: Dict[str, str]
    ) -> int:
        """Import dependencies for an environment.

        Args:
            environment_id: Environment identifier
            dependencies: Dictionary mapping dependency names to versions

        Returns:
            Number of dependencies imported
        """
        if environment_id not in self._environments:
            _logger.warning(
                f"[MultiEnvironmentDependencyManager] Unknown environment: {environment_id}"
            )
            return 0

        imported = 0
        for dep_name, version in dependencies.items():
            dependency = EnvironmentDependency(
                environment_id=environment_id,
                dependency_name=dep_name,
                version=version,
                source="imported",
            )

            if self.add_environment_dependency(dependency):
                imported += 1

        _logger.info(
            f"[MultiEnvironmentDependencyManager] Imported {imported} dependencies to {environment_id}"
        )

        return imported

    def detect_environment_drift(self, source_env: str, target_env: str) -> List[EnvironmentDrift]:
        """Detect dependency drift between environments.

        Args:
            source_env: Source environment ID
            target_env: Target environment ID

        Returns:
            List of detected drifts
        """
        with self._lock:
            drifts = []

            if source_env not in self._environments or target_env not in self._environments:
                _logger.warning(
                    f"[MultiEnvironmentDependencyManager] Unknown environment in drift check"
                )
                return drifts

            source_deps = self._environment_dependencies[source_env]
            target_deps = self._environment_dependencies[target_env]

            # Check for version mismatches
            for dep_name, source_dep in source_deps.items():
                if dep_name in target_deps:
                    target_dep = target_deps[dep_name]
                    if source_dep.version != target_dep.version:
                        drift = EnvironmentDrift(
                            drift_id=f"drift_{int(time.time())}_{len(drifts)}",
                            source_environment=source_env,
                            target_environment=target_env,
                            dependency_name=dep_name,
                            drift_type="version_mismatch",
                            source_version=source_dep.version,
                            target_version=target_dep.version,
                            severity=self._determine_drift_severity(
                                "version_mismatch", source_dep.version, target_dep.version
                            ),
                            recommendation=f"Synchronize {dep_name} version between environments",
                        )
                        drifts.append(drift)
                else:
                    # Dependency exists in source but not target
                    drift = EnvironmentDrift(
                        drift_id=f"drift_{int(time.time())}_{len(drifts)}",
                        source_environment=source_env,
                        target_environment=target_env,
                        dependency_name=dep_name,
                        drift_type="missing",
                        source_version=source_dep.version,
                        severity="high",
                        recommendation=f"Add {dep_name} {source_dep.version} to {target_env}",
                    )
                    drifts.append(drift)

            # Check for extra dependencies in target
            for dep_name, target_dep in target_deps.items():
                if dep_name not in source_deps:
                    drift = EnvironmentDrift(
                        drift_id=f"drift_{int(time.time())}_{len(drifts)}",
                        source_environment=source_env,
                        target_environment=target_env,
                        dependency_name=dep_name,
                        drift_type="extra",
                        target_version=target_dep.version,
                        severity="medium",
                        recommendation=f"Consider removing {dep_name} from {target_env} or add to {source_env}",
                    )
                    drifts.append(drift)

            self._drift_history.extend(drifts)

            _logger.info(
                f"[MultiEnvironmentDependencyManager] Detected {len(drifts)} drifts between "
                f"{source_env} and {target_env}"
            )

            return drifts

    def _determine_drift_severity(self, drift_type: str, version1: str, version2: str) -> str:
        """Determine severity of drift.

        Args:
            drift_type: Type of drift
            version1: First version
            version2: Second version

        Returns:
            Severity level
        """
        if drift_type == "version_mismatch":
            # Check for major version differences
            v1_major = version1.split(".")[0] if "." in version1 else version1
            v2_major = version2.split(".")[0] if "." in version2 else version2

            if v1_major != v2_major:
                return "critical"
            else:
                return "high"

        return "medium"

    def calculate_consistency_score(self, source_env: str, target_env: str) -> float:
        """Calculate dependency consistency score between environments.

        Args:
            source_env: Source environment ID
            target_env: Target environment ID

        Returns:
            Consistency score (0.0 to 1.0)
        """
        cache_key = (source_env, target_env)
        if cache_key in self._dependency_consistency_cache:
            return self._dependency_consistency_cache[cache_key]

        with self._lock:
            if source_env not in self._environments or target_env not in self._environments:
                return 0.0

            source_deps = set(self._environment_dependencies[source_env].keys())
            target_deps = set(self._environment_dependencies[target_env].keys())

            if not source_deps and not target_deps:
                return 1.0  # Both empty, consistent

            # Calculate Jaccard similarity
            intersection = len(source_deps & target_deps)
            union = len(source_deps | target_deps)

            if union == 0:
                return 1.0

            jaccard_similarity = intersection / union

            # Factor in version consistency
            version_consistency = self._calculate_version_consistency(source_env, target_env)

            # Combined score
            consistency_score = 0.7 * jaccard_similarity + 0.3 * version_consistency

            self._dependency_consistency_cache[cache_key] = consistency_score

            return consistency_score

    def _calculate_version_consistency(self, source_env: str, target_env: str) -> float:
        """Calculate version consistency between environments.

        Args:
            source_env: Source environment ID
            target_env: Target environment ID

        Returns:
            Version consistency score (0.0 to 1.0)
        """
        source_deps = self._environment_dependencies[source_env]
        target_deps = self._environment_dependencies[target_env]

        common_deps = set(source_deps.keys()) & set(target_deps.keys())

        if not common_deps:
            return 1.0  # No common dependencies to compare

        matching_versions = 0
        for dep_name in common_deps:
            if source_deps[dep_name].version == target_deps[dep_name].version:
                matching_versions += 1

        return matching_versions / len(common_deps)

    def promote_dependencies(
        self, source_env: str, target_env: str, validate_only: bool = False
    ) -> PromotionResult:
        """Promote dependencies from source to target environment.

        Args:
            source_env: Source environment ID
            target_env: Target environment ID
            validate_only: If True, only validate without promoting

        Returns:
            Promotion result
        """
        promotion_id = f"promote_{int(time.time())}_{source_env}_to_{target_env}"

        with self._lock:
            if source_env not in self._environments or target_env not in self._environments:
                return PromotionResult(
                    promotion_id=promotion_id,
                    source_environment=source_env,
                    target_environment=target_env,
                    timestamp=time.time(),
                    success=False,
                    dependencies_promoted=0,
                    validation_passed=False,
                    message="Invalid environment IDs",
                )

            # Check promotion order
            source_env_config = self._environments[source_env]
            target_env_config = self._environments[target_env]

            if source_env_config.promotion_order >= target_env_config.promotion_order:
                return PromotionResult(
                    promotion_id=promotion_id,
                    source_environment=source_env,
                    target_environment=target_env,
                    timestamp=time.time(),
                    success=False,
                    dependencies_promoted=0,
                    validation_passed=False,
                    message="Invalid promotion order",
                )

            # Detect drift first
            drifts = self.detect_environment_drift(source_env, target_env)

            # Validation: check for critical drifts
            critical_drifts = [d for d in drifts if d.severity == "critical"]
            validation_passed = len(critical_drifts) == 0

            if not validation_passed:
                return PromotionResult(
                    promotion_id=promotion_id,
                    source_environment=source_env,
                    target_environment=target_env,
                    timestamp=time.time(),
                    success=False,
                    dependencies_promoted=0,
                    validation_passed=False,
                    message=f"Validation failed: {len(critical_drifts)} critical drifts detected",
                )

            if validate_only:
                return PromotionResult(
                    promotion_id=promotion_id,
                    source_environment=source_env,
                    target_environment=target_env,
                    timestamp=time.time(),
                    success=True,
                    dependencies_promoted=0,
                    validation_passed=True,
                    message="Validation passed (validate only mode)",
                )

            # Perform promotion
            promoted = 0
            failed = []

            source_deps = self._environment_dependencies[source_env]

            for dep_name, source_dep in source_deps.items():
                # Update or add dependency in target
                new_dep = EnvironmentDependency(
                    environment_id=target_env,
                    dependency_name=dep_name,
                    version=source_dep.version,
                    source=f"promoted_from_{source_env}",
                )

                if self.add_environment_dependency(new_dep):
                    promoted += 1
                else:
                    failed.append(dep_name)

            result = PromotionResult(
                promotion_id=promotion_id,
                source_environment=source_env,
                target_environment=target_env,
                timestamp=time.time(),
                success=len(failed) == 0,
                dependencies_promoted=promoted,
                dependencies_failed=failed,
                validation_passed=True,
                message=f"Promoted {promoted} dependencies, {len(failed)} failed",
            )

            self._promotion_history.append(result)

            _logger.info(
                f"[MultiEnvironmentDependencyManager] Promotion {promotion_id}: "
                f"{promoted} promoted, {len(failed)} failed"
            )

            return result

    def get_environment_summary(self, environment_id: str) -> Dict[str, Any]:
        """Get summary of an environment's dependencies.

        Args:
            environment_id: Environment identifier

        Returns:
            Environment summary
        """
        with self._lock:
            if environment_id not in self._environments:
                return {"error": "Unknown environment"}

            env_config = self._environments[environment_id]
            dependencies = self._environment_dependencies[environment_id]

            # Calculate health metrics
            vulnerable_count = sum(
                1 for dep in dependencies.values() if dep.state == DependencyState.VULNERABLE
            )
            outdated_count = sum(
                1 for dep in dependencies.values() if dep.state == DependencyState.OUTDATED
            )

            return {
                "environment_id": environment_id,
                "environment_type": env_config.environment_type.value,
                "name": env_config.name,
                "description": env_config.description,
                "is_active": env_config.is_active,
                "dependency_count": len(dependencies),
                "vulnerable_dependencies": vulnerable_count,
                "outdated_dependencies": outdated_count,
                "health_score": 1.0
                - (vulnerable_count * 0.5 + outdated_count * 0.2) / max(len(dependencies), 1),
            }

    def get_all_environments(self) -> Dict[str, EnvironmentConfig]:
        """Get all environment configurations.

        Returns:
            Dictionary of environments
        """
        with self._lock:
            return dict(self._environments)

    def get_drift_history(self, limit: int = 10) -> List[EnvironmentDrift]:
        """Get drift detection history.

        Args:
            limit: Maximum number of drifts to return

        Returns:
            List of drifts
        """
        with self._lock:
            return list(self._drift_history[-limit:])

    def get_promotion_history(self, limit: int = 10) -> List[PromotionResult]:
        """Get promotion history.

        Args:
            limit: Maximum number of promotions to return

        Returns:
            List of promotion results
        """
        with self._lock:
            return list(self._promotion_history[-limit:])


# Singleton instance
_multi_env_manager: Optional[MultiEnvironmentDependencyManager] = None
_multi_env_lock = threading.Lock()


def get_multi_environment_manager(repo_root: str = ".") -> MultiEnvironmentDependencyManager:
    """Get singleton instance of multi-environment dependency manager.

    Args:
        repo_root: Path to repository root

    Returns:
        Multi-environment dependency manager instance
    """
    global _multi_env_manager

    with _multi_env_lock:
        if _multi_env_manager is None:
            _multi_env_manager = MultiEnvironmentDependencyManager(repo_root)
        return _multi_env_manager
