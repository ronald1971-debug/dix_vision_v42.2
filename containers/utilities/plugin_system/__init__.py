"""Plugin System - Contract-Compliant Plugin Infrastructure

Provides real, contract-compliant plugin loading, governance integration,
and infrastructure wiring for all DIX VISION v42.2 plugins.
"""

from plugin_system.plugin_loader import (
    PluginLoader,
    PluginConfig,
    PluginSystemMode,
    get_plugin_loader
)

__all__ = [
    "PluginLoader",
    "PluginConfig", 
    "PluginSystemMode",
    "get_plugin_loader",
]