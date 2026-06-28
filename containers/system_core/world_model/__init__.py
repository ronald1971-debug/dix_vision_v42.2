"""
world_model
DIX VISION v42.2 — World-Model

Production-grade world modeling capabilities including market representation,
agent modeling, environment modeling, causal structure learning, dynamics modeling,
and prediction systems.
"""

from world_model.cognitive_os_integration import (
    CognitiveOSWorldIntegration,
    get_cognitive_os_integration,
)
from world_model.desktop_agent_integration import (
    DesktopAgentWorldIntegration,
    get_desktop_agent_integration,
)
from world_model.execution_integration import (
    ExecutionWorldIntegration,
    get_execution_integration,
)
from world_model.governance_integration import (
    GovernanceWorldIntegration,
    get_governance_integration,
)
from world_model.orchestrator import (
    WorldModelOrchestrator,
    WorldModelState,
    get_world_model_orchestrator,
)
from world_model.shared_reality_layer import (
    RealitySubscription,
    RealityUpdate,
    SharedRealityLayer,
    SystemType,
    SystemWorldView,
    get_shared_reality_layer,
)
from world_model.unified_world_model_manager import (
    UnifiedWorldModelManager,
    UnifiedWorldModelState,
    get_unified_world_model_manager,
)

__all__ = [
    "WorldModelState",
    "WorldModelOrchestrator",
    "get_world_model_orchestrator",
    "SystemType",
    "RealitySubscription",
    "RealityUpdate",
    "SystemWorldView",
    "SharedRealityLayer",
    "get_shared_reality_layer",
    "DesktopAgentWorldIntegration",
    "get_desktop_agent_integration",
    "GovernanceWorldIntegration",
    "get_governance_integration",
    "ExecutionWorldIntegration",
    "get_execution_integration",
    "CognitiveOSWorldIntegration",
    "get_cognitive_os_integration",
    "UnifiedWorldModelState",
    "UnifiedWorldModelManager",
    "get_unified_world_model_manager",
]
