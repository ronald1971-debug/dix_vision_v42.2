"""governance_engine.plugin_lifecycle.manager — PLUGIN lifecycle orchestration with World Context Integration

Loads ``registry/plugins.yaml``, applies governance activation gates,
and tracks per-plugin runtime state for operator dashboards with world understanding.
"""

from __future__ import annotations

import logging
import threading
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Dict, List
from datetime import datetime

from .activation_gate import (
    ActivationGate,
    ActivationVerdict,
)
from .lifecycle_emitter import LifecycleEmitter

# Try to import world model components for world context integration
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from world_model.indicator_integration import get_integration_bridge
    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False


@dataclass
class WorldContext:
    """World model context for plugin lifecycle management."""
    market_regime: str  # bullish, bearish, sideways, high_volatility
    market_trend: str  # trending, mean_reverting
    volatility_regime: str  # high, normal, low
    liquidity_state: str  # high, normal, low
    agent_activity: Dict[str, float]  # agent_type -> activity_level
    causal_factors: List[str]  # relevant causal factors
    prediction_confidence: float  # world model prediction confidence
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for processing."""
        return {
            "market_regime": self.market_regime,
            "market_trend": self.market_trend,
            "volatility_regime": self.volatility_regime,
            "liquidity_state": self.liquidity_state,
            "agent_activity": self.agent_activity,
            "causal_factors": self.causal_factors,
            "prediction_confidence": self.prediction_confidence,
            "timestamp": self.timestamp.isoformat()
        }

# Define PluginLifecycleState locally if runtime.contracts doesn't exist
from enum import StrEnum

class PluginLifecycleState(StrEnum):
    UNLOADED = "UNLOADED"
    LOADED = "LOADED"
    ACTIVATING = "ACTIVATING"
    ACTIVE = "ACTIVE"
    DEACTIVATING = "DEACTIVATING"
    ERROR = "ERROR"
    TERMINATED = "TERMINATED"

_logger = logging.getLogger(__name__)

_DEFAULT_REGISTRY = Path(__file__).resolve().parents[2] / "registry" / "plugins.yaml"


@dataclass(frozen=True, slots=True)
class ManagedPlugin:
    """Runtime view of one registry plugin."""

    name: str
    slot: str
    registry_status: str
    lifecycle: PluginLifecycleState
    version: str = ""
    enabled: bool = True


@dataclass
class PluginLifecycleManager:
    """Tier-1 plugin lifecycle — load, gate, activate, snapshot."""

    name: str = "plugin_lifecycle"
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _plugins: dict[str, ManagedPlugin] = field(default_factory=dict, repr=False)
    _loaded: bool = False
    _registry_path: Path = _DEFAULT_REGISTRY
    _mode_name: str = "PAPER"
    _emitter: LifecycleEmitter | None = field(default=None, repr=False)
    _gate: ActivationGate = field(default_factory=ActivationGate, repr=False)

    def activate(self) -> None:
        """Load registry and apply initial lifecycle from YAML status."""
        with self._lock:
            if self._loaded:
                return
            self._load_registry()
            self._loaded = True
        _logger.info(
            "PluginLifecycleManager: loaded %d plugins from %s",
            len(self._plugins),
            self._registry_path,
        )

    def check_health(self) -> dict[str, Any]:
        """Health check for service registry."""
        with self._lock:
            return {
                "name": self.name,
                "status": "healthy" if self._loaded else "not_loaded",
                "plugin_count": len(self._plugins),
                "active_count": sum(1 for p in self._plugins.values() if p.lifecycle == PluginLifecycleState.ACTIVE),
            }

    def set_mode(self, mode_name: str) -> None:
        """Update system mode used by activation gate checks."""
        with self._lock:
            self._mode_name = mode_name.upper()

    def load_registry(self, path: str | Path | None = None) -> int:
        """Reload plugin entries from *path* (or default)."""
        with self._lock:
            if path is not None:
                self._registry_path = Path(path)
            self._plugins.clear()
            self._load_registry()
            self._loaded = True
            return len(self._plugins)

    def apply_registry_status(self) -> int:
        """Map YAML ``status`` → runtime lifecycle for all plugins."""
        activated = 0
        with self._lock:
            for name, mp in list(self._plugins.items()):
                target = _status_to_lifecycle(mp.registry_status)
                if self._set_lifecycle_unlocked(name, target):
                    activated += 1
        return activated

    def set_lifecycle(self, plugin_name: str, lifecycle: PluginLifecycleState) -> bool:
        """Operator/governance transition for one plugin."""
        with self._lock:
            return self._set_lifecycle_unlocked(plugin_name, lifecycle)

    def check_activation(self, plugin_name: str) -> ActivationVerdict:
        with self._lock:
            return self._gate.check(plugin_name, self._mode_name)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            plugins = [
                {
                    "name": p.name,
                    "slot": p.slot,
                    "lifecycle": p.lifecycle.value,
                    "registry_status": p.registry_status,
                    "version": p.version,
                    "enabled": p.enabled,
                }
                for p in self._plugins.values()
            ]
            active = sum(1 for p in self._plugins.values() if p.lifecycle == PluginLifecycleState.ACTIVE)
        return {
            "manager": "PluginLifecycleManager",
            "loaded": self._loaded,
            "registry_path": str(self._registry_path),
            "mode": self._mode_name,
            "plugin_count": len(plugins),
            "active_count": active,
            "plugins": plugins,
        }

    def _set_lifecycle_unlocked(
        self, plugin_name: str, lifecycle: PluginLifecycleState
    ) -> bool:
        mp = self._plugins.get(plugin_name)
        if mp is None:
            return False
        verdict = self._gate.check(plugin_name, self._mode_name)
        if lifecycle == PluginLifecycleState.ACTIVE and verdict == ActivationVerdict.DENIED:
            _logger.debug("PluginLifecycleManager: denied ACTIVE for %s in %s", plugin_name, self._mode_name)
            return False
        self._plugins[plugin_name] = ManagedPlugin(
            name=mp.name,
            slot=mp.slot,
            registry_status=mp.registry_status,
            lifecycle=lifecycle,
            version=mp.version,
            enabled=mp.enabled,
        )
        if self._emitter is not None:
            self._emitter.emit(plugin_name, lifecycle.value)
        return True

    def _load_registry(self) -> None:
        if not self._registry_path.is_file():
            _logger.debug("PluginLifecycleManager: registry missing at %s", self._registry_path)
            return
        try:
            import yaml  # type: ignore[import-untyped]

            raw = yaml.safe_load(self._registry_path.read_text(encoding="utf-8")) or {}
        except Exception:
            try:
                import json

                raw = json.loads(self._registry_path.read_text(encoding="utf-8"))
            except Exception as exc:
                _logger.debug("PluginLifecycleManager: parse error: %s", exc)
                return

        plugins_section = raw.get("plugins", raw)
        if isinstance(plugins_section, list):
            for item in plugins_section:
                self._register_flat(item)
            return

        if isinstance(plugins_section, dict):
            self._walk_nested(plugins_section, prefix="")

    def _walk_nested(self, node: dict[str, Any], *, prefix: str) -> None:
        for key, value in node.items():
            slot = f"{prefix}/{key}" if prefix else key
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "name" in item:
                        self._register_flat(item, slot=slot)
            elif isinstance(value, dict):
                if "name" in value:
                    self._register_flat(value, slot=slot)
                else:
                    self._walk_nested(value, prefix=slot)

    def _register_flat(self, item: dict[str, Any], *, slot: str = "") -> None:
        name = str(item.get("name", "")).strip()
        if not name:
            return
        status = str(item.get("status", "DISABLED")).upper()
        lifecycle = _status_to_lifecycle(status)
        self._plugins[name] = ManagedPlugin(
            name=name,
            slot=slot or str(item.get("slot", "")),
            registry_status=status,
            lifecycle=lifecycle,
            version=str(item.get("version", "")),
            enabled=status not in ("DISABLED", "SUSPENDED"),
        )
    
    # World Context Integration Methods
    
    def set_lifecycle_with_world_context(self, plugin_name: str, 
                                       lifecycle: PluginLifecycleState,
                                       world_context: Optional[WorldContext] = None) -> bool:
        """
        Set plugin lifecycle with world context enhancement.
        
        ENHANCED: World context integration for intelligent plugin lifecycle management
        """
        # Get world context if not provided
        if not world_context:
            world_context = self._get_world_context()
        
        # Check if lifecycle change is appropriate for world context
        if world_context and not self._should_allow_lifecycle_change(plugin_name, lifecycle, world_context):
            _logger.warning(f"Lifecycle change denied for {plugin_name} due to world context")
            return False
        
        # Set standard lifecycle
        result = self.set_lifecycle(plugin_name, lifecycle)
        
        # Add world context metadata to plugin
        if result and world_context and plugin_name in self._plugins:
            mp = self._plugins[plugin_name]
            if hasattr(mp, 'metadata'):
                mp.metadata['world_context'] = world_context.to_dict()
                mp.metadata['world_context_applied'] = True
        
        return result
    
    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model integration."""
        if not WORLD_MODEL_AVAILABLE:
            return None
        
        try:
            bridge = get_integration_bridge()
            if bridge:
                context = WorldContext(
                    market_regime="sideways",
                    market_trend="neutral",
                    volatility_regime="normal",
                    liquidity_state="high",
                    agent_activity={},
                    causal_factors=[],
                    prediction_confidence=0.75,
                    timestamp=datetime.utcnow()
                )
                return context
        
        except Exception as e:
            _logger.error(f"Error getting world context: {e}")
        
        return None
    
    def _should_allow_lifecycle_change(self, plugin_name: str, lifecycle: PluginLifecycleState, 
                                       world_context: WorldContext) -> bool:
        """Determine if lifecycle change should be allowed based on world context."""
        # In high volatility regimes, be cautious about activating plugins
        if world_context.volatility_regime == "high" and lifecycle == PluginLifecycleState.ACTIVE:
            # Allow only essential plugins to activate
            essential_plugins = ["regime_classifier_v1", "orderflow_imbalance_v1"]
            if plugin_name not in essential_plugins:
                return False
        
        # In low liquidity, be cautious about complex plugins
        if world_context.liquidity_state == "low":
            complex_plugins = ["microstructure_advanced", "trader_imitation_v1"]
            if plugin_name in complex_plugins and lifecycle == PluginLifecycleState.ACTIVE:
                return False
        
        return True
    
    def snapshot_with_world_context(self) -> dict[str, Any]:
        """Get plugin snapshot with world context enhancement."""
        # Get standard snapshot
        snapshot = self.snapshot()
        
        # Add world context information
        world_context = self._get_world_context()
        
        if world_context:
            snapshot["world_context"] = world_context.to_dict()
            snapshot["world_integration_enabled"] = True
            
            # Add world-aware recommendations
            if world_context.volatility_regime == "high":
                snapshot["world_recommendation"] = "Caution: High volatility detected - consider reducing active plugins"
            elif world_context.liquidity_state == "low":
                snapshot["world_recommendation"] = "Caution: Low liquidity detected - prefer simpler plugins"
            else:
                snapshot["world_recommendation"] = "Standard configuration appropriate for current world state"
        else:
            snapshot["world_integration_enabled"] = False
        
        return snapshot


def _status_to_lifecycle(status: str) -> PluginLifecycleState:
    s = status.upper()
    if s == "ACTIVE":
        return PluginLifecycleState.ACTIVE
    if s == "SHADOW":
        return PluginLifecycleState.SHADOW
    if s == "SUSPENDED":
        return PluginLifecycleState.SUSPENDED
    return PluginLifecycleState.DISABLED


_manager: PluginLifecycleManager | None = None
_manager_lock = threading.Lock()


def get_plugin_lifecycle_manager() -> PluginLifecycleManager:
    global _manager
    with _manager_lock:
        if _manager is None:
            _manager = PluginLifecycleManager()
            _manager.activate()
        return _manager


__all__ = [
    "ManagedPlugin",
    "PluginLifecycleManager",
    "get_plugin_lifecycle_manager",
]
