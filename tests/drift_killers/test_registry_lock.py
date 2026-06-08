"""Drift killer — registry file lock guard.

Ensures that canonical registry YAML files exist, are parseable,
and contain required top-level keys. Prevents silent deletion or
structural corruption of governance-critical config.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_REGISTRY_ROOT = Path(__file__).parents[2] / "registry"

_REQUIRED_KEYS: dict[str, list[str]] = {
    "strategies/definitions.yaml": ["strategies"],
    "strategies/lifecycle.yaml": ["states", "valid_transitions"],
    "strategies/performance.yaml": ["performance"],
    "agent_context_keys.yaml": ["allowed_keys"],
    "regime_hysteresis.yaml": ["persistence_ticks", "confidence_delta"],
    "reward_components.yaml": ["allowed_components"],
    "calibration.yaml": ["window_ns", "thresholds"],
    "meta_controller.yaml": ["shadow_policy", "fallback_lane"],
}

_CONTRACTS_ROOT = Path(__file__).parents[2] / "contracts"
_CONTRACTS_REQUIRED_KEYS: dict[str, list[str]] = {
    "ownership_registry.yaml": ["engines", "version"],
}


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        pytest.skip("pyyaml not installed")
    with path.open() as fh:
        return yaml.safe_load(fh) or {}


class TestRegistryLock:
    @pytest.mark.parametrize("rel_path,required", list(_REQUIRED_KEYS.items()))
    def test_registry_file_exists(self, rel_path: str, required: list[str]) -> None:
        full = _REGISTRY_ROOT / rel_path
        assert full.exists(), f"Registry file missing: {full}"

    @pytest.mark.parametrize("rel_path,required", list(_REQUIRED_KEYS.items()))
    def test_registry_file_has_required_keys(self, rel_path: str, required: list[str]) -> None:
        full = _REGISTRY_ROOT / rel_path
        if not full.exists():
            pytest.skip(f"File not present: {full}")
        data = _load_yaml(full)
        for key in required:
            assert key in data, (
                f"Registry file {rel_path!r} missing required key {key!r}"
            )


class TestContractsRegistry:
    """Invariant contract files must exist and be properly structured."""

    @pytest.mark.parametrize("rel_path,required", list(_CONTRACTS_REQUIRED_KEYS.items()))
    def test_contracts_file_exists(self, rel_path: str, required: list[str]) -> None:
        full = _CONTRACTS_ROOT / rel_path
        assert full.exists(), f"Contracts file missing: {full}"

    @pytest.mark.parametrize("rel_path,required", list(_CONTRACTS_REQUIRED_KEYS.items()))
    def test_contracts_file_has_required_keys(self, rel_path: str, required: list[str]) -> None:
        full = _CONTRACTS_ROOT / rel_path
        if not full.exists():
            pytest.skip(f"File not present: {full}")
        data = _load_yaml(full)
        for key in required:
            assert key in data, (
                f"Contracts file {rel_path!r} missing required key {key!r}"
            )


class TestOwnershipRegistryStructure:
    """ownership_registry.yaml must define all required engines."""

    REQUIRED_ENGINES = ("indira", "dyon", "governance", "execution", "learning", "evolution", "belief_engine")

    def test_all_engines_defined(self) -> None:
        full = _CONTRACTS_ROOT / "ownership_registry.yaml"
        if not full.exists():
            pytest.skip("ownership_registry.yaml not present")
        data = _load_yaml(full)
        engines = data.get("engines", {})
        for engine in self.REQUIRED_ENGINES:
            assert engine in engines, f"Ownership registry missing engine: {engine}"
            assert "owns" in engines[engine], f"Engine {engine} missing 'owns' key"
            assert "module" in engines[engine], f"Engine {engine} missing 'module' key"
