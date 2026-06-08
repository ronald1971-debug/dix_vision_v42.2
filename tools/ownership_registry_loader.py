"""ownership_registry_loader.py — Load ownership_registry.yaml for enforcement.

This module centralizes domain ownership definitions so they can be shared
across authority_lint.py, runtime_graph_validator.py, and policy_compiler.py.

The registry at contracts/ownership_registry.yaml is the single source of
truth. Changes to domain ownership must be made there first.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

_REGISTRY_PATH = Path(__file__).parent.parent / "contracts" / "ownership_registry.yaml"


def _load_yaml() -> dict[str, Any]:
    """Load and parse the ownership registry YAML."""
    try:
        import yaml
    except ImportError:
        # Fallback: return minimal hardcoded defaults if pyyaml unavailable
        return _get_defaults()

    if not _REGISTRY_PATH.exists():
        return _get_defaults()

    with _REGISTRY_PATH.open() as f:
        return yaml.safe_load(f) or {}


def _get_defaults() -> dict[str, Any]:
    """Fallback defaults matching the current registry structure."""
    return {
        "version": "v42.2-arch",
        "dyon_charter": {
            "owns_truth": ["repository_intelligence", "architecture_intelligence",
                           "runtime_intelligence", "infrastructure_intelligence"],
        },
        "engines": {
            "indira": {
                "module": "intelligence_engine",
                "owns": ["market_intelligence", "trader_intelligence",
                        "strategy_intelligence", "portfolio_intelligence",
                        "allocation_intelligence", "position_intelligence",
                        "execution_feedback_intelligence"],
            },
            "dyon": {
                "module": "system_engine",
                "owns": ["repository_intelligence", "architecture_intelligence",
                        "runtime_intelligence", "infrastructure_intelligence"],
            },
        },
    }


_cached_registry: dict[str, Any] | None = None


def load_registry() -> dict[str, Any]:
    """Return the parsed ownership registry."""
    global _cached_registry
    if _cached_registry is None:
        _cached_registry = _load_yaml()
    return _cached_registry


def owns_truth_domains() -> tuple[str, ...]:
    """Return DYON's positive ownership domains (Truth domains)."""
    registry = load_registry()
    dyon_charter = registry.get("dyon_charter", {})
    return tuple(dyon_charter.get("owns_truth", [
        "repository_intelligence",
        "architecture_intelligence",
        "runtime_intelligence",
        "infrastructure_intelligence",
    ]))


def indira_owned_domains() -> tuple[str, ...]:
    """Return INDIRA's owned domains."""
    registry = load_registry()
    indira = registry.get("engines", {}).get("indira", {})
    return tuple(indira.get("owns", [
        "market_intelligence",
        "trader_intelligence",
        "strategy_intelligence",
        "portfolio_intelligence",
        "allocation_intelligence",
        "position_intelligence",
        "execution_feedback_intelligence",
    ]))


def dyon_owned_domains() -> tuple[str, ...]:
    """Return DYON's owned domains."""
    registry = load_registry()
    dyon = registry.get("engines", {}).get("dyon", {})
    return tuple(dyon.get("owns", [
        "repository_intelligence",
        "architecture_intelligence",
        "runtime_intelligence",
        "infrastructure_intelligence",
    ]))


def get_engine_module(engine_name: str) -> str | None:
    """Return the module path for an engine (e.g., 'system_engine' for 'dyon')."""
    registry = load_registry()
    engine = registry.get("engines", {}).get(engine_name, {})
    return engine.get("module")


__all__ = [
    "owns_truth_domains",
    "indira_owned_domains",
    "dyon_owned_domains",
    "get_engine_module",
    "load_registry",
]