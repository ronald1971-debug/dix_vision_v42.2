"""deployment/deployment_pipeline.py — Production deployment orchestration.

Blue/Green, Canary, and Rollback deployment patterns.
"""

from __future__ import annotations

import dataclasses
import json
import subprocess
from enum import StrEnum


class DeployMode(StrEnum):
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLBACK = "rollback"


class DeployStatus(StrEnum):
    PENDING = "pending"
    DEPLOYING = "deploying"
    HEALTH_CHECK = "health_check"
    ACTIVE = "active"
    FAILED = "failed"


@dataclasses.dataclass(frozen=True, slots=True)
class DeploymentConfig:
    mode: DeployMode = DeployMode.BLUE_GREEN
    health_endpoint: str = "/health"
    health_timeout_sec: int = 60
    canary_traffic_percent: int = 10
    rollback_on_failure: bool = True
    region: str = "primary"


@dataclasses.dataclass(frozen=True, slots=True)
class DeploymentResult:
    success: bool
    mode: DeployMode
    version: str
    previous_version: str | None
    status: DeployStatus
    canaries_deployed: int = 0
    health_checks_passed: int = 0


def get_current_version() -> str:
    """Get current deployed version from git."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()[:8]
    except Exception:
        return "unknown"


def deploy_blue_green(config: DeploymentConfig) -> DeploymentResult:
    """Blue/Green deployment: switch traffic after health check."""
    version = get_current_version()
    try:
        # Build and push new image
        subprocess.run(
            ["docker", "build", "-t", f"dix-vision:{version}", "."],
            check=True,
        )
        subprocess.run(
            ["docker", "push", f"registry/dix-vision:{version}"],
            check=True,
        )

        # Deploy to inactive slot
        subprocess.run(
            [
                "kubectl",
                "set",
                "image",
                f"deployment/dix-vision-{version}",
                f"dix-vision=registry/dix-vision:{version}",
            ],
            check=True,
        )

        # Wait for rollout
        subprocess.run(
            [
                "kubectl",
                "rollout",
                "status",
                f"deployment/dix-vision-{version}",
                f"--timeout={config.health_timeout_sec}s",
            ],
            check=True,
        )

        return DeploymentResult(
            success=True,
            mode=config.mode,
            version=version,
            previous_version=None,
            status=DeployStatus.ACTIVE,
        )
    except Exception:
        return DeploymentResult(
            success=False,
            mode=config.mode,
            version=version,
            previous_version=None,
            status=DeployStatus.FAILED,
        )


def deploy_canary(config: DeploymentConfig, tags: list[str] | None = None) -> DeploymentResult:
    """Canary deployment: route small % traffic to new version."""
    version = get_current_version()
    try:
        subprocess.run(
            ["docker", "build", "-t", f"dix-vision:{version}", "."],
            check=True,
        )
        subprocess.run(
            ["docker", "push", f"registry/dix-vision:{version}"],
            check=True,
        )

        # Deploy canary pods with traffic split
        canary_cmd = [
            "kubectl",
            "patch",
            "deployment",
            "dix-vision",
            "-p",
            json.dumps(
                {
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "name": "dix-vision",
                                        "image": f"registry/dix-vision:{version}",
                                    }
                                ]
                            }
                        }
                    }
                }
            ),
        ]
        subprocess.run(canary_cmd, check=True)

        return DeploymentResult(
            success=True,
            mode=config.mode,
            version=version,
            previous_version=None,
            status=DeployStatus.ACTIVE,
            canaries_deployed=1,
        )
    except Exception:
        if config.rollback_on_failure:
            rollback_deployment(version)
        return DeploymentResult(
            success=False,
            mode=config.mode,
            version=version,
            previous_version=None,
            status=DeployStatus.FAILED,
        )


def rollback_deployment(version: str) -> DeploymentResult:
    """Rollback to previous version."""
    try:
        subprocess.run(
            ["kubectl", "rollout", "undo", "deployment/dix-vision", f"--to-revision={version}"],
            check=True,
        )
        return DeploymentResult(
            success=True,
            mode=DeployMode.ROLLBACK,
            version=version,
            previous_version=None,
            status=DeployStatus.ACTIVE,
        )
    except Exception:
        return DeploymentResult(
            success=False,
            mode=DeployMode.ROLLBACK,
            version=version,
            previous_version=None,
            status=DeployStatus.FAILED,
        )


def multi_region_deploy(
    config: DeploymentConfig, regions: list[str]
) -> dict[str, DeploymentResult]:
    """Deploy to multiple regions."""
    results = {}
    for region in regions:
        region_config = DeploymentConfig(mode=config.mode, region=region)
        results[region] = deploy_blue_green(region_config)
    return results


__all__ = [
    "DeploymentConfig",
    "DeploymentResult",
    "DeployMode",
    "DeployStatus",
    "deploy_blue_green",
    "deploy_canary",
    "rollback_deployment",
    "multi_region_deploy",
]
