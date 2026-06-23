"""
Standard Learning Interface - Optional Adoption for Domains

Production-Grade Implementation for DIX VISION v42.2+ Phase 2
Creates standard interfaces while allowing domain-specific implementations

Signal-First Architecture: 85/15 universal baseline maintained
Zero-Loss Guarantee: Interfaces are optional, not mandatory
Contract Compliance: Tier-0 Production Implementation
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class TrainingDataFormat(Enum):
    """Supported training data formats."""

    TABULAR = "tabular"
    TIME_SERIES = "time_series"
    SEQUENTIAL = "sequential"
    IMAGE = "image"
    TEXT = "text"
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"


class ModelType(Enum):
    """Model types."""

    NEURAL_NETWORK = "neural_network"
    DECISION_TREE = "decision_tree"
    ENSEMBLE = "ensemble"
    LINEAR_MODEL = "linear_model"
    SUPPORT_VECTOR_MACHINE = "support_vector_machine"
    BAYESIAN_MODEL = "bayesian_model"
    REINFORCEMENT_LEARNING_AGENT = "reinforcement_learning_agent"
    TRANSFORMER = "transformer"
    CUSTOM = "custom"


class EvaluationMetric(Enum):
    """Evaluation metrics."""

    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    MEAN_SQUARED_ERROR = "mean_squared_error"
    MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
    ROOT_MEAN_SQUARED_ERROR = "root_mean_squared_error"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    CUSTOM = "custom"


class DeploymentStatus(Enum):
    """Deployment status."""

    NOT_DEPLOYED = "not_deployed"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    DEPLOYMENT_FAILED = "deployment_failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class TrainingConfig:
    """Configuration for training process."""

    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    random_seed: Optional[int] = None
    signal_world_ratio: float = 0.85  # Signal-first architecture (85% signals)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetadata:
    """Metadata about a model."""

    model_id: str
    model_type: ModelType
    trained_at: datetime
    training_config: TrainingConfig
    signal_world_ratio_used: float = 0.85
    performance_metrics: Dict[EvaluationMetric, float] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Result of model evaluation."""

    model_id: str
    evaluation_metrics: Dict[EvaluationMetric, float]
    evaluated_at: datetime
    test_data_size: int
    passed_governance_check: bool = False
    governance_comments: List[str] = field(default_factory=list)


@dataclass
class DeploymentRequest:
    """Request for model deployment."""

    model_id: str
    requested_by: str  # Operator or system ID
    deployment_target: str  # Where to deploy
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    requires_governance_approval: bool = True
    requested_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeploymentResponse:
    """Response to deployment request."""

    request_id: str
    model_id: str
    status: DeploymentStatus
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    deployment_url: Optional[str] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class StandardLearningInterface(ABC):
    """Standard learning interface that domains can optionally implement.

    This interface provides a common contract for learning systems while allowing
    domain-specific implementations. Domains can adopt these interfaces at their
    own pace without forcing changes to existing implementations.
    """

    @abstractmethod
    def train(self, data: Any, config: TrainingConfig) -> ModelMetadata:
        """Train model with data.

        Args:
            data: Training data (format depends on domain)
            config: Training configuration

        Returns:
            ModelMetadata with training results
        """
        pass

    @abstractmethod
    def evaluate(self, model_id: str, test_data: Any) -> EvaluationResult:
        """Evaluate model performance.

        Args:
            model_id: Model identifier
            test_data: Test data for evaluation

        Returns:
            EvaluationResult with performance metrics
        """
        pass

    @abstractmethod
    def deploy(self, request: DeploymentRequest) -> DeploymentResponse:
        """Deploy model (requires governance approval).

        Args:
            request: Deployment request with model and target information

        Returns:
            DeploymentResponse with deployment status
        """
        pass

    @abstractmethod
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata.

        Args:
            model_id: Model identifier

        Returns:
            ModelMetadata if found, None otherwise
        """
        pass


class StandardLearningInterfaceV2(StandardLearningInterface):
    """Extended standard learning interface with additional methods.

    This extends the base interface with additional methods for advanced
    learning capabilities that domains can optionally implement.
    """

    @abstractmethod
    def continual_train(self, model_id: str, new_data: Any, config: TrainingConfig) -> ModelMetadata:
        """Continually train existing model with new data.

        Args:
            model_id: Existing model identifier
            new_data: New training data
            config: Training configuration

        Returns:
            Updated ModelMetadata
        """
        pass

    @abstractmethod
    def transfer_learn(self, source_model_id: str, target_data: Any, config: TrainingConfig) -> ModelMetadata:
        """Transfer learning from source model to target domain.

        Args:
            source_model_id: Source model identifier
            target_data: Target domain data
            config: Training configuration

        Returns:
            ModelMetadata for transferred model
        """
        pass

    @abstractmethod
    def meta_train(self, meta_data: List[Any], config: TrainingConfig) -> ModelMetadata:
        """Meta-learning across multiple tasks.

        Args:
            meta_data: List of training data from multiple tasks
            config: Training configuration

        Returns:
            ModelMetadata for meta-learned model
        """
        pass


class GovernanceAwareLearningInterface(StandardLearningInterfaceV2):
    """Governance-aware learning interface with mandatory governance checks.

    This interface adds governance requirements that must be implemented
    for systems that require governance approval for learning operations.
    """

    @abstractmethod
    def request_training_approval(self, config: TrainingConfig) -> bool:
        """Request approval for training operation.

        Args:
            config: Proposed training configuration

        Returns:
            True if approved, False otherwise
        """
        pass

    @abstractmethod
    def log_learning_operation(self, operation: str, model_id: str, operator_id: str) -> bool:
        """Log learning operation for audit trail.

        Args:
            operation: Type of operation (train, evaluate, deploy, etc.)
            model_id: Model identifier
            operator_id: Operator or system ID performing operation

        Returns:
            True if logged successfully, False otherwise
        """
        pass

    @abstractmethod
    def check_signal_first_compliance(self, config: TrainingConfig) -> bool:
        """Check compliance with signal-first architecture.

        Args:
            config: Training configuration to check

        Returns:
            True if compliant with signal-first architecture (85% signals, 15% world)
        """
        pass


class InterfaceAdoptionStatus(Enum):
    """Status of interface adoption by domain."""

    NOT_ADOPTED = "not_adopted"
    IN_PROGRESS = "in_progress"
    ADOPTED = "adopted"
    CUSTOM_IMPLEMENTATION = "custom_implementation"


@dataclass
class DomainInterfaceCompliance:
    """Compliance status for a domain's interface implementation."""

    domain: str
    base_interface: InterfaceAdoptionStatus
    extended_interface: InterfaceAdoptionStatus
    governance_interface: InterfaceAdoptionStatus
    last_updated: datetime = field(default_factory=datetime.now)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "domain": self.domain,
            "base_interface": self.base_interface.value,
            "extended_interface": self.extended_interface.value,
            "governance_interface": self.governance_interface.value,
            "last_updated": self.last_updated.isoformat(),
            "notes": self.notes,
        }


class LearningInterfaceRegistry:
    """Registry for tracking domain adoption of standard learning interfaces."""

    def __init__(self):
        """Initialize the learning interface registry."""
        self._domain_compliance: Dict[str, DomainInterfaceCompliance] = {}
        self._initialize_known_domains()

    def _initialize_known_domains(self):
        """Initialize known domain compliance status."""
        domains = [
            "infrastructure",
            "market",
            "runtime_cognitive",
            "control",
            "research_experimental",
            "independent",
        ]

        for domain in domains:
            self._domain_compliance[domain] = DomainInterfaceCompliance(
                domain=domain,
                base_interface=InterfaceAdoptionStatus.NOT_ADOPTED,
                extended_interface=InterfaceAdoptionStatus.NOT_ADOPTED,
                governance_interface=InterfaceAdoptionStatus.NOT_ADOPTED,
                notes=["Interfaces are optional - domains can adopt at their own pace"]
            )

        logger.info("[LEARNING_INTERFACE] Learning Interface Registry initialized with domain compliance tracking")

    def update_compliance_status(
        self,
        domain: str,
        interface_type: str,
        status: InterfaceAdoptionStatus,
        note: Optional[str] = None
    ) -> bool:
        """Update compliance status for a domain.

        Args:
            domain: Domain to update
            interface_type: Type of interface (base, extended, governance)
            status: New compliance status
            note: Optional note about the update

        Returns:
            True if updated successfully, False otherwise
        """
        if domain not in self._domain_compliance:
            logger.warning(f"[LEARNING_INTERFACE] Unknown domain: {domain}")
            return False

        compliance = self._domain_compliance[domain]

        if interface_type == "base":
            compliance.base_interface = status
        elif interface_type == "extended":
            compliance.extended_interface = status
        elif interface_type == "governance":
            compliance.governance_interface = status
        else:
            logger.warning(f"[LEARNING_INTERFACE] Unknown interface type: {interface_type}")
            return False

        compliance.last_updated = datetime.now()
        if note:
            compliance.notes.append(note)

        logger.info(f"[LEARNING_INTERFACE] Updated {domain} {interface_type} interface to {status.value}")
        return True

    def get_domain_compliance(self, domain: str) -> Optional[DomainInterfaceCompliance]:
        """Get compliance status for a domain.

        Args:
            domain: Domain to get compliance for

        Returns:
            DomainInterfaceCompliance if found, None otherwise
        """
        return self._domain_compliance.get(domain)

    def get_all_compliance(self) -> Dict[str, DomainInterfaceCompliance]:
        """Get compliance status for all domains.

        Returns:
            Dictionary mapping domains to their compliance status
        """
        return self._domain_compliance.copy()

    def get_adoption_summary(self) -> Dict[str, Any]:
        """Get summary of interface adoption across domains.

        Returns:
            Summary statistics
        """
        base_adopted = sum(1 for c in self._domain_compliance.values() if c.base_interface == InterfaceAdoptionStatus.ADOPTED)
        extended_adopted = sum(1 for c in self._domain_compliance.values() if c.extended_interface == InterfaceAdoptionStatus.ADOPTED)
        governance_adopted = sum(1 for c in self._domain_compliance.values() if c.governance_interface == InterfaceAdoptionStatus.ADOPTED)

        return {
            "total_domains": len(self._domain_compliance),
            "base_interface_adopted": base_adopted,
            "extended_interface_adopted": extended_adopted,
            "governance_interface_adopted": governance_adopted,
            "adoption_rate_base": base_adopted / len(self._domain_compliance) if self._domain_compliance else 0,
            "adoption_rate_extended": extended_adopted / len(self._domain_compliance) if self._domain_compliance else 0,
            "adoption_rate_governance": governance_adopted / len(self._domain_compliance) if self._domain_compliance else 0,
            "last_updated": datetime.now().isoformat(),
        }


# Global interface registry instance
_learning_interface_registry: Optional[LearningInterfaceRegistry] = None


def get_learning_interface_registry() -> LearningInterfaceRegistry:
    """Get the global learning interface registry instance."""
    global _learning_interface_registry
    if _learning_interface_registry is None:
        _learning_interface_registry = LearningInterfaceRegistry()
    return _learning_interface_registry


__all__ = [
    "TrainingDataFormat",
    "ModelType",
    "EvaluationMetric",
    "DeploymentStatus",
    "TrainingConfig",
    "ModelMetadata",
    "EvaluationResult",
    "DeploymentRequest",
    "DeploymentResponse",
    "StandardLearningInterface",
    "StandardLearningInterfaceV2",
    "GovernanceAwareLearningInterface",
    "InterfaceAdoptionStatus",
    "DomainInterfaceCompliance",
    "LearningInterfaceRegistry",
    "get_learning_interface_registry",
]