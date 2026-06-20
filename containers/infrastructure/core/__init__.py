"""
Core Infrastructure Module
Contains real implementations for core system components
NO PLACEHOLDER - Contract-compliant real implementations
"""

from core.cognitive_router import (
    TaskClass,
    AIProvider,
    ProviderConfig,
    enabled_ai_providers,
    select_providers,
    get_provider_config,
    enable_provider,
    set_provider_api_key
)
from core.kernel import (
    EngineStatus,
    EngineState,
    EngineServiceAdapter,
    SystemKernel,
    get_kernel
)

__all__ = [
    # Cognitive Router
    "TaskClass",
    "AIProvider", 
    "ProviderConfig",
    "enabled_ai_providers",
    "select_providers",
    "get_provider_config",
    "enable_provider",
    "set_provider_api_key",
    # Kernel
    "EngineStatus",
    "EngineState",
    "EngineServiceAdapter",
    "SystemKernel",
    "get_kernel"
]