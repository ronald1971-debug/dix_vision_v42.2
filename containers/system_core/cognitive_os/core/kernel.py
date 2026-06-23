"""Unified Cognitive OS Kernel.

This is the central orchestration layer that wires all the completed components
into the unified Cognitive OS architecture: Operator → Governance → Cognitive Layer → Execution → Capital.

Based on the system evolution described in the analysis, this provides the complete
integration of all phases into a cohesive, production-ready cognitive operating system.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

_logger = logging.getLogger(__name__)


class SystemLayer(str, enum.Enum):
    """Layers of the Cognitive OS architecture."""

    OPERATOR = "OPERATOR"
    GOVERNANCE = "GOVERNANCE"
    COGNITIVE = "COGNITIVE"
    EXECUTION = "EXECUTION"
    CAPITAL = "CAPITAL"


class SystemStatus(str, enum.Enum):
    """Status of the Cognitive OS."""

    INITIALIZING = "INITIALIZING"
    OPERATIONAL = "OPERATIONAL"
    DEGRADED = "DEGRADED"
    MAINTENANCE = "MAINTENANCE"
    CRITICAL = "CRITICAL"


@dataclasses.dataclass(frozen=True, slots=True)
class CognitiveOSMetrics:
    """Metrics for the Cognitive OS system.

    Fields:
        system_id: Unique identifier for the system
        status: Current system status
        active_layers: Layers currently active
        health_score: Overall system health (0.0-1.0)
        performance_score: System performance score (0.0-1.0)
        governance_active: Whether governance is active
        cognitive_engine_active: Whether cognitive engine is active
        execution_active: Whether execution is active
        timestamp_ns: Metrics timestamp
    """

    system_id: str
    status: SystemStatus
    active_layers: tuple[SystemLayer, ...]
    health_score: float
    performance_score: float
    governance_active: bool
    cognitive_engine_active: bool
    execution_active: bool
    timestamp_ns: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.health_score <= 1.0:
            raise ValueError(
                f"CognitiveOSMetrics.health_score must be 0.0-1.0, got {self.health_score}"
            )
        if not 0.0 <= self.performance_score <= 1.0:
            raise ValueError(
                f"CognitiveOSMetrics.performance_score must be 0.0-1.0, got {self.performance_score}"
            )


class CognitiveOSKernel:
    """Unified Cognitive OS Kernel.

    This component provides:
    - Central orchestration of all completed phases
    - Integration of M-1 Knowledge Layer, Governance, Execution, Trust Root, State Layer, Learning Engine, Evolution Engine
    - System-wide health monitoring and metrics
    - Layer activation and management
    - Cognitive OS architecture implementation
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._system_id: str = "cognitive_os_v42.2"
        self._status: SystemStatus = SystemStatus.INITIALIZING
        self._active_layers: set[SystemLayer] = set()
        self._total_integrations: int = 0

        # Component references (initialized during startup)
        self._governance_system: object | None = None
        self._execution_system: object | None = None
        self._knowledge_layer: object | None = None
        self._trust_root: object | None = None
        self._state_layer: object | None = None
        self._learning_engine: object | None = None
        self._evolution_engine: object | None = None

        # Phase 3 Advanced Modules
        self._rl_optimizer: object | None = None
        self._xai_system: object | None = None
        self._multi_agent_system: object | None = None
        self._temporal_reasoner: object | None = None
        self._risk_manager: object | None = None

        # Phase 4 Advanced Modules
        self._neuro_symbolic_ai: object | None = None
        self._meta_cognitive_system: object | None = None
        self._causal_discovery: object | None = None

        # Phase 5 Neuromorphic Modules
        self._indira_snn: object | None = None
        self._indira_lsm: object | None = None
        self._dyon_snn: object | None = None
        self._dyon_lsm: object | None = None

    def initialize_system(self) -> bool:
        """Initialize the complete Cognitive OS system.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            _logger.info("Initializing Cognitive OS v42.2...")

            # Initialize all component layers
            self._initialize_governance_layer()
            self._initialize_execution_layer()
            self._initialize_knowledge_layer()
            self._initialize_trust_root()
            self._initialize_state_layer()
            self._initialize_learning_engine()
            self._initialize_evolution_engine()

            # Initialize Phase 3 Advanced Modules
            self._initialize_phase3_modules()

            # Initialize Phase 4 Advanced Modules
            self._initialize_phase4_modules()

            # Initialize Phase 5 Neuromorphic Modules
            self._initialize_phase5_modules()

            # Activate all layers
            self._active_layers = {
                SystemLayer.GOVERNANCE,
                SystemLayer.COGNITIVE,
                SystemLayer.EXECUTION,
                SystemLayer.CAPITAL,
            }

            self._status = SystemStatus.OPERATIONAL
            self._total_integrations += 1

            _logger.info("Cognitive OS v42.2 initialization complete")
            return True

        except Exception as e:
            _logger.error(f"Cognitive OS initialization failed: {e}")
            self._status = SystemStatus.CRITICAL
            return False

    def _initialize_governance_layer(self) -> None:
        """Initialize the governance layer."""
        try:
            from governance_unified import get_unified_governance_kernel

            self._governance_system = get_unified_governance_kernel()
            _logger.info("Governance layer initialized: governance_unified")
        except ImportError as e:
            _logger.warning(f"Governance layer import failed: {e}")
            self._governance_system = None

    def _initialize_execution_layer(self) -> None:
        """Initialize the execution layer."""
        try:
            from execution_unified import get_unified_execution_kernel

            self._execution_system = get_unified_execution_kernel()
            _logger.info("Execution layer initialized: execution_unified")
        except ImportError as e:
            _logger.warning(f"Execution layer import failed: {e}")
            self._execution_system = None

    def _initialize_knowledge_layer(self) -> None:
        """Initialize the M-1 knowledge layer."""
        try:
            from intelligence_engine.knowledge import (
                KnowledgeDriftMonitor,
                KnowledgeValidator,
                SourceConflictGraph,
            )

            self._knowledge_layer = {
                "validator": KnowledgeValidator(),
                "conflict_graph": SourceConflictGraph(),
                "drift_monitor": KnowledgeDriftMonitor(),
            }
            _logger.info("M-1 Knowledge layer initialized")
        except ImportError as e:
            _logger.warning(f"Knowledge layer import failed: {e}")
            self._knowledge_layer = None

    def _initialize_trust_root(self) -> None:
        """Initialize the trust root."""
        try:
            from trust_root import (
                get_artifact_generator,
                get_foundation_hash_lifecycle,
                get_trust_anchor_manager,
            )

            self._trust_root = {
                "hash_lifecycle": get_foundation_hash_lifecycle(),
                "artifact_generator": get_artifact_generator(),
                "anchor_manager": get_trust_anchor_manager(),
            }
            _logger.info("Trust root initialized")
        except ImportError as e:
            _logger.warning(f"Trust root import failed: {e}")
            self._trust_root = None

    def _initialize_state_layer(self) -> None:
        """Initialize the enhanced state layer."""
        try:
            from state import (
                get_deterministic_verifier,
                get_replay_validator,
            )

            self._state_layer = {
                "replay_validator": get_replay_validator(),
                "deterministic_verifier": get_deterministic_verifier(),
            }
            _logger.info(
                "State layer initialized with replay validation and deterministic verification"
            )
        except ImportError as e:
            _logger.warning(f"State layer import failed: {e}")
            self._state_layer = None

    def _initialize_learning_engine(self) -> None:
        """Initialize the mature learning engine."""
        try:
            from intelligence_engine.learning import (
                get_cognitive_learning_governance,
                get_reinforcement_engine,
            )

            self._learning_engine = {
                "reinforcement": get_reinforcement_engine(),
                "governance": get_cognitive_learning_governance(),
            }
            _logger.info(
                "Learning engine initialized with reinforcement loops and cognitive governance"
            )
        except ImportError as e:
            _logger.warning(f"Learning engine import failed: {e}")
            self._learning_engine = None

    def _initialize_evolution_engine(self) -> None:
        """Initialize the autonomous evolution engine."""
        try:
            from evolution_engine import (
                get_autonomous_evolution_engine,
                get_evolution_orchestrator,
            )

            self._evolution_engine = {
                "orchestrator": get_evolution_orchestrator(),
                "autonomous": get_autonomous_evolution_engine(),
            }
            _logger.info("Evolution engine initialized with autonomous capabilities")
        except ImportError as e:
            _logger.warning(f"Evolution engine import failed: {e}")
            self._evolution_engine = None

    def _initialize_phase3_modules(self) -> None:
        """Initialize Phase 3 Advanced Modules (RL, XAI, Multi-Agent, Temporal, Risk)."""
        try:
            from cognitive_os.rl.rl_optimizer import get_rl_optimizer

            self._rl_optimizer = get_rl_optimizer()
            _logger.info("Phase 3: RL Optimizer initialized")
        except ImportError as e:
            _logger.warning(f"Phase 3 RL Optimizer import failed: {e}")
            self._rl_optimizer = None

        try:
            from cognitive_os.xai.explainable_ai import get_xai_system

            self._xai_system = get_xai_system()
            _logger.info("Phase 3: Explainable AI initialized")
        except ImportError as e:
            _logger.warning(f"Phase 3 XAI import failed: {e}")
            self._xai_system = None

        try:
            from cognitive_os.multi_agent.multi_agent_system import get_multi_agent_system

            self._multi_agent_system = get_multi_agent_system()
            _logger.info("Phase 3: Multi-Agent System initialized")
        except ImportError as e:
            _logger.warning(f"Phase 3 Multi-Agent import failed: {e}")
            self._multi_agent_system = None

        try:
            from cognitive_os.temporal.temporal_reasoning import get_temporal_reasoner

            self._temporal_reasoner = get_temporal_reasoner()
            _logger.info("Phase 3: Temporal Reasoning initialized")
        except ImportError as e:
            _logger.warning(f"Phase 3 Temporal Reasoning import failed: {e}")
            self._temporal_reasoner = None

        try:
            from cognitive_os.risk.dynamic_risk_manager import get_dynamic_risk_manager

            self._risk_manager = get_dynamic_risk_manager()
            _logger.info("Phase 3: Dynamic Risk Manager initialized")
        except ImportError as e:
            _logger.warning(f"Phase 3 Risk Manager import failed: {e}")
            self._risk_manager = None

    def _initialize_phase4_modules(self) -> None:
        """Initialize Phase 4 Advanced Modules (Neuro-Symbolic, Meta-Cognitive, Causal Discovery)."""
        try:
            from cognitive_os.neuro_symbolic.neuro_symbolic_ai import get_neuro_symbolic_ai

            self._neuro_symbolic_ai = get_neuro_symbolic_ai()
            _logger.info("Phase 4: Neuro-Symbolic AI initialized")
        except ImportError as e:
            _logger.warning(f"Phase 4 Neuro-Symbolic AI import failed: {e}")
            self._neuro_symbolic_ai = None

        try:
            from cognitive_os.meta_cognitive.meta_cognitive_system import get_meta_cognitive_system

            self._meta_cognitive_system = get_meta_cognitive_system()
            _logger.info("Phase 4: Meta-Cognitive System initialized")
        except ImportError as e:
            _logger.warning(f"Phase 4 Meta-Cognitive import failed: {e}")
            self._meta_cognitive_system = None

        try:
            from cognitive_os.causal.advanced_causal_discovery import get_advanced_causal_discovery

            self._causal_discovery = get_advanced_causal_discovery()
            _logger.info("Phase 4: Advanced Causal Discovery initialized")
        except ImportError as e:
            _logger.warning(f"Phase 4 Causal Discovery import failed: {e}")
            self._causal_discovery = None

    def _initialize_phase5_modules(self) -> None:
        """Initialize Phase 5 Neuromorphic Modules (INDIRA and DYON SNN + LSM)."""
        try:
            from indira_cognitive.neuromorphic.indira_spiking_network import (
                get_indira_spiking_intelligence,
            )

            self._indira_snn = get_indira_spiking_intelligence()
            self._indira_snn.start()
            _logger.info("Phase 5: INDIRA Spiking Neural Network initialized")
        except ImportError as e:
            _logger.warning(f"Phase 5 INDIRA SNN import failed: {e}")
            self._indira_snn = None

        try:
            from indira_cognitive.neuromorphic.indira_lsm import get_indira_lsm_intelligence

            self._indira_lsm = get_indira_lsm_intelligence()
            self._indira_lsm.start()
            _logger.info("Phase 5: INDIRA Liquid State Machine initialized")
        except ImportError as e:
            _logger.warning(f"Phase 5 INDIRA LSM import failed: {e}")
            self._indira_lsm = None

        try:
            from dyon_cognitive.neuromorphic.dyon_spiking_network import (
                get_dyon_spiking_intelligence,
            )

            self._dyon_snn = get_dyon_spiking_intelligence()
            self._dyon_snn.start()
            _logger.info("Phase 5: DYON Spiking Neural Network initialized")
        except ImportError as e:
            _logger.warning(f"Phase 5 DYON SNN import failed: {e}")
            self._dyon_snn = None

        try:
            from dyon_cognitive.neuromorphic.dyon_lsm_anomaly import (
                get_dyon_lsm_anomaly_intelligence,
            )

            self._dyon_lsm = get_dyon_lsm_anomaly_intelligence()
            self._dyon_lsm.start()
            _logger.info("Phase 5: DYON LSM Anomaly Detector initialized")
        except ImportError as e:
            _logger.warning(f"Phase 5 DYON LSM import failed: {e}")
            self._dyon_lsm = None

    def get_system_metrics(self) -> CognitiveOSMetrics:
        """Get current system metrics.

        Returns:
            CognitiveOSMetrics with current system state
        """
        with self._lock:
            # Calculate health score based on component availability
            components_available = sum(
                [
                    1 if self._governance_system else 0,
                    1 if self._execution_system else 0,
                    1 if self._knowledge_layer else 0,
                    1 if self._trust_root else 0,
                    1 if self._state_layer else 0,
                    1 if self._learning_engine else 0,
                    1 if self._evolution_engine else 0,
                    1 if self._rl_optimizer else 0,
                    1 if self._xai_system else 0,
                    1 if self._multi_agent_system else 0,
                    1 if self._temporal_reasoner else 0,
                    1 if self._risk_manager else 0,
                    1 if self._neuro_symbolic_ai else 0,
                    1 if self._meta_cognitive_system else 0,
                    1 if self._causal_discovery else 0,
                    1 if self._indira_snn else 0,
                    1 if self._indira_lsm else 0,
                    1 if self._dyon_snn else 0,
                    1 if self._dyon_lsm else 0,
                ]
            )
            health_score = components_available / 19.0

            # Calculate performance score (placeholder)
            performance_score = 0.9 if health_score > 0.8 else 0.5

            return CognitiveOSMetrics(
                system_id=self._system_id,
                status=self._status,
                active_layers=tuple(self._active_layers),
                health_score=health_score,
                performance_score=performance_score,
                governance_active=self._governance_system is not None,
                cognitive_engine_active=self._knowledge_layer is not None,
                execution_active=self._execution_system is not None,
                timestamp_ns=self._get_timestamp(),
            )

    def get_component_status(self) -> Mapping[str, str]:
        """Get status of all integrated components.

        Returns:
            Mapping of component names to their status
        """
        with self._lock:
            return MappingProxyType(
                {
                    "governance_unified": "active" if self._governance_system else "inactive",
                    "execution_unified": "active" if self._execution_system else "inactive",
                    "m1_knowledge_layer": "active" if self._knowledge_layer else "inactive",
                    "trust_root": "active" if self._trust_root else "inactive",
                    "state_layer_enhanced": "active" if self._state_layer else "inactive",
                    "learning_engine_mature": "active" if self._learning_engine else "inactive",
                    "evolution_engine_autonomous": (
                        "active" if self._evolution_engine else "inactive"
                    ),
                    # Phase 3 Modules
                    "phase3_rl_optimizer": "active" if self._rl_optimizer else "inactive",
                    "phase3_xai_system": "active" if self._xai_system else "inactive",
                    "phase3_multi_agent_system": (
                        "active" if self._multi_agent_system else "inactive"
                    ),
                    "phase3_temporal_reasoner": "active" if self._temporal_reasoner else "inactive",
                    "phase3_dynamic_risk_manager": "active" if self._risk_manager else "inactive",
                    # Phase 4 Modules
                    "phase4_neuro_symbolic_ai": "active" if self._neuro_symbolic_ai else "inactive",
                    "phase4_meta_cognitive_system": (
                        "active" if self._meta_cognitive_system else "inactive"
                    ),
                    "phase4_advanced_causal_discovery": (
                        "active" if self._causal_discovery else "inactive"
                    ),
                    # Phase 5 Neuromorphic
                    "phase5_indira_snn": "active" if self._indira_snn else "inactive",
                    "phase5_indira_lsm": "active" if self._indira_lsm else "inactive",
                    "phase5_dyon_snn": "active" if self._dyon_snn else "inactive",
                    "phase5_dyon_lsm": "active" if self._dyon_lsm else "inactive",
                }
            )

    def activate_layer(self, layer: SystemLayer) -> bool:
        """Activate a system layer.

        Args:
            layer: Layer to activate

        Returns:
            True if activation successful, False otherwise
        """
        with self._lock:
            if layer in self._active_layers:
                return True

            self._active_layers.add(layer)
            _logger.info("Activated layer: %s", layer)
            return True

    def deactivate_layer(self, layer: SystemLayer) -> bool:
        """Deactivate a system layer.

        Args:
            layer: Layer to deactivate

        Returns:
            True if deactivation successful, False otherwise
        """
        with self._lock:
            if layer not in self._active_layers:
                return False

            self._active_layers.discard(layer)
            _logger.info("Deactivated layer: %s", layer)
            return True

    def get_statistics(self) -> dict[str, int | str]:
        """Get Cognitive OS statistics."""
        with self._lock:
            return {
                "system_id": self._system_id,
                "status": self._status,
                "active_layers": len(self._active_layers),
                "total_integrations": self._total_integrations,
            }

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # In production, this would use the system time source
        return 0  # TODO: Integrate with proper time source


# Singleton instance
_singleton: CognitiveOSKernel | None = None
_lock = threading.Lock()


def get_cognitive_os_kernel() -> CognitiveOSKernel:
    """Get the singleton Cognitive OS kernel instance."""
    global _singleton
    if _singleton is None:
        with _lock:
            if _singleton is None:
                _singleton = CognitiveOSKernel()
    return _singleton


__all__ = [
    "CognitiveOSKernel",
    "get_cognitive_os_kernel",
    "SystemLayer",
    "SystemStatus",
    "CognitiveOSMetrics",
]
