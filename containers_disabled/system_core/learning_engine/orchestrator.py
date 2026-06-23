"""
learning_engine.orchestrator
DIX VISION v42.2 — Learning Engine Orchestrator

Central coordination for learning operations including supervised learning,
unsupervised learning, reinforcement learning, deep learning, and adaptive learning.
Production-grade implementation with all advanced ML components.
Integrated with DYON for autonomous evolution and self-reflection.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any, Optional

from learning_engine.adaptive_learning import (
    ProductionAdaptiveLearner,
    get_production_adaptive_learner,
)
from learning_engine.deep_learning import (
    ArchitectureType,
    NetworkArchitecture,
    ProductionDeepLearner,
    TrainingConfig,
    get_production_deep_learner,
)
from learning_engine.model_deployment import ProductionModelDeployer, get_production_model_deployer
from learning_engine.model_training import ProductionModelTrainer, get_production_model_trainer
from learning_engine.model_validation import (
    ProductionModelValidator,
    get_production_model_validator,
)
from learning_engine.reinforcement_learning import (
    ProductionReinforcementLearner,
    get_production_reinforcement_learner,
)

# Import production-grade components
from learning_engine.supervised_learning import (
    ModelConfig,
    ProductionSupervisedLearner,
    SupervisedLearningType,
    TrainingData,
    get_production_supervised_learner,
)
from learning_engine.unsupervised_learning import (
    ProductionUnsupervisedLearner,
    UnsupervisedData,
    get_production_unsupervised_learner,
)
from system_unified.time_source import now

# Delay DYON imports to avoid circular dependency
# DYON will be initialized separately


logger = logging.getLogger(__name__)


@dataclass
class LearningOperation:
    """A learning operation."""

    operation_id: str
    operation_type: str  # "training" | "prediction" | "adaptation" | "evaluation"
    model_name: str
    input_data: dict[str, Any] = None
    output_data: dict[str, Any] = None
    accuracy: float = 0.0
    timestamp: str = ""
    status: str = "pending"  # "pending" | "training" | "completed" | "failed"
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.timestamp:
            self.timestamp = now().utc_time.isoformat()
        if self.input_data is None:
            self.input_data = {}
        if self.output_data is None:
            self.output_data = {}


@dataclass
class ModelState:
    """State of the learning model."""

    model_type: str
    performance_metrics: dict[str, float]
    training_history: list[dict[str, Any]]
    current_accuracy: float
    model_status: str
    parameters: dict[str, Any]
    last_updated: str = ""

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = now().utc_time.isoformat()


class LearningOrchestrator:
    """Orchestrates learning operations.

    Production-grade orchestrator that coordinates:
    - Supervised learning (via ProductionSupervisedLearner)
    - Unsupervised learning (via ProductionUnsupervisedLearner)
    - Reinforcement learning (via ProductionReinforcementLearner)
    - Deep learning (via ProductionDeepLearner)
    - Model training (via ProductionModelTrainer)
    - Model validation (via ProductionModelValidator)
    - Model deployment (via ProductionModelDeployer)
    - Adaptive learning (via ProductionAdaptiveLearner)
    """

    def __init__(self) -> None:
        self._operations: list[LearningOperation] = []

        # Initialize production-grade components
        self._supervised_learner: Optional[ProductionSupervisedLearner] = None
        self._unsupervised_learner: Optional[ProductionUnsupervisedLearner] = None
        self._reinforcement_learner: Optional[ProductionReinforcementLearner] = None
        self._deep_learner: Optional[ProductionDeepLearner] = None
        self._model_trainer: Optional[ProductionModelTrainer] = None
        self._model_validator: Optional[ProductionModelValidator] = None
        self._model_deployer: Optional[ProductionModelDeployer] = None
        self._adaptive_learner: Optional[ProductionAdaptiveLearner] = None

        # DYON integration
        self._dyon_assistant = None
        self._dyon_reflection = None
        self._dyon_enabled: bool = False

        self._lock = threading.Lock()

    def start(self) -> bool:
        """Start the learning orchestrator with production-grade components and DYON integration."""
        try:
            # Try to initialize production-grade components
            self._supervised_learner = get_production_supervised_learner()
            self._unsupervised_learner = get_production_unsupervised_learner()
            self._reinforcement_learner = get_production_reinforcement_learner()
            self._deep_learner = get_production_deep_learner()
            self._model_trainer = get_production_model_trainer()
            self._model_validator = get_production_model_validator()
            self._model_deployer = get_production_model_deployer()
            self._adaptive_learner = get_production_adaptive_learner()

            # Start all components
            if self._supervised_learner:
                self._supervised_learner.start()
            if self._unsupervised_learner:
                self._unsupervised_learner.start()
            if self._reinforcement_learner:
                self._reinforcement_learner.start()
            if self._deep_learner:
                self._deep_learner.start()
            if self._model_trainer:
                self._model_trainer.start()
            if self._model_validator:
                self._model_validator.start()
            if self._model_deployer:
                self._model_deployer.start()
            if self._adaptive_learner:
                self._adaptive_learner.start()

            logger.info("[LEARNING] Production-grade components initialized")
        except Exception as e:
            logger.warning(f"[LEARNING] Could not initialize production-grade components: {e}")
            logger.info("[LEARNING] Continuing with DYON-only mode")

        # Always initialize DYON capabilities (independent of learning components)
        try:
            from system_unified.dyon_coding_assistant import get_dyon_assistant
            from system_unified.dyon_self_reflection import get_self_reflection

            self._dyon_assistant = get_dyon_assistant()
            self._dyon_reflection = get_self_reflection()
            self._dyon_enabled = True
            logger.info("[LEARNING] DYON integration enabled for autonomous learning evolution")
        except ImportError as e:
            logger.warning(f"[LEARNING] Could not initialize DYON: {e}")
            self._dyon_enabled = False

        logger.info("[LEARNING] Learning orchestrator started")
        return True

    def stop(self) -> bool:
        """Stop the learning orchestrator and all components."""
        try:
            # Stop all components (gracefully handle missing stop methods)
            if self._supervised_learner and hasattr(self._supervised_learner, "stop"):
                self._supervised_learner.stop()
            if self._unsupervised_learner and hasattr(self._unsupervised_learner, "stop"):
                self._unsupervised_learner.stop()
            if self._reinforcement_learner and hasattr(self._reinforcement_learner, "stop"):
                self._reinforcement_learner.stop()
            if self._deep_learner and hasattr(self._deep_learner, "stop"):
                self._deep_learner.stop()
            if self._model_trainer and hasattr(self._model_trainer, "stop"):
                self._model_trainer.stop()
            if self._model_validator and hasattr(self._model_validator, "stop"):
                self._model_validator.stop()
            if self._model_deployer and hasattr(self._model_deployer, "stop"):
                self._model_deployer.stop()
            if self._adaptive_learner and hasattr(self._adaptive_learner, "stop"):
                self._adaptive_learner.stop()

            logger.info("[LEARNING] Learning orchestrator stopped")
            return True
        except Exception as e:
            logger.warning(f"[LEARNING] Failed to stop some components: {e}")
            logger.info("[LEARNING] Continuing with graceful shutdown")
            return True

    # Supervised Learning Operations
    def train_supervised(
        self, features: list[list[float]], labels: list[any], model_type: str = "classification"
    ) -> LearningOperation:
        """Train a supervised learning model."""
        if not self._supervised_learner:
            return self._create_disabled_operation("supervised_training")

        try:
            training_data = TrainingData(
                data_id=f"data_{now().sequence}", features=features, labels=labels
            )

            model_config = ModelConfig(
                config_id=f"config_{now().sequence}",
                model_type=(
                    SupervisedLearningType.CLASSIFICATION
                    if model_type == "classification"
                    else SupervisedLearningType.REGRESSION
                ),
            )

            result = self._supervised_learner.train_model(training_data, model_config)

            operation = LearningOperation(
                operation_id=f"supervised_train_{now().sequence}",
                operation_type="training",
                model_name=f"supervised_{model_type}",
                input_data={"n_samples": len(features)},
                output_data={
                    "accuracy": result.metrics.get("accuracy", 0.0),
                    "training_time": result.training_time_seconds,
                },
                accuracy=result.metrics.get("accuracy", 0.0),
                status="completed",
            )

            with self._lock:
                self._operations.append(operation)

            return operation

        except Exception as e:
            logger.error(f"[LEARNING] Supervised training failed: {e}")
            return self._create_error_operation("supervised_training", str(e))

    # Unsupervised Learning Operations
    def cluster_data(
        self, features: list[list[float]], n_clusters: int = 5, algorithm: str = "kmeans"
    ) -> LearningOperation:
        """Perform clustering on data."""
        if not self._unsupervised_learner:
            return self._create_disabled_operation("clustering")

        try:
            data = UnsupervisedData(data_id=f"data_{now().sequence}", features=features)

            result = self._unsupervised_learner.cluster(data, n_clusters, algorithm)

            operation = LearningOperation(
                operation_id=f"clustering_{now().sequence}",
                operation_type="evaluation",
                model_name=f"cluster_{algorithm}",
                input_data={"n_samples": len(features)},
                output_data={
                    "silhouette_score": result.silhouette_score,
                    "n_clusters": len(set(result.cluster_assignments)),
                },
                accuracy=result.silhouette_score,
                status="completed",
            )

            with self._lock:
                self._operations.append(operation)

            return operation

        except Exception as e:
            logger.error(f"[LEARNING] Clustering failed: {e}")
            return self._create_error_operation("clustering", str(e))

    # Reinforcement Learning Operations
    def train_rl(self, env_id: str, n_states: int, n_actions: int) -> LearningOperation:
        """Train a reinforcement learning agent."""
        if not self._reinforcement_learner:
            return self._create_disabled_operation("rl_training")

        try:
            result = self._reinforcement_learner.train_q_learning(env_id, n_states, n_actions)

            operation = LearningOperation(
                operation_id=f"rl_train_{now().sequence}",
                operation_type="training",
                model_name=f"rl_{env_id}",
                input_data={"n_states": n_states, "n_actions": n_actions},
                output_data={
                    "average_reward": result.average_reward,
                    "final_reward": result.final_reward,
                },
                accuracy=result.average_reward,
                status="completed",
            )

            with self._lock:
                self._operations.append(operation)

            return operation

        except Exception as e:
            logger.error(f"[LEARNING] RL training failed: {e}")
            return self._create_error_operation("rl_training", str(e))

    # Deep Learning Operations
    def train_deep_model(
        self, features: list[list[float]], labels: list[float], architecture: str = "mlp"
    ) -> LearningOperation:
        """Train a deep learning model."""
        if not self._deep_learner:
            return self._create_disabled_operation("deep_learning")

        try:
            arch = NetworkArchitecture(
                arch_id=f"arch_{now().sequence}",
                arch_type=ArchitectureType.MLP if architecture == "mlp" else ArchitectureType.CNN,
                layers=[{"units": 64, "activation": "relu"}, {"units": 32, "activation": "relu"}],
                input_size=len(features[0]) if features else 1,
                output_size=1,
            )

            config = TrainingConfig(config_id=f"config_{now().sequence}")

            result = self._deep_learner.train_model(arch, features, labels, config)

            operation = LearningOperation(
                operation_id=f"deep_train_{now().sequence}",
                operation_type="training",
                model_name=f"deep_{architecture}",
                input_data={"n_samples": len(features)},
                output_data={
                    "final_accuracy": result.final_val_accuracy,
                    "training_time": result.training_time_seconds,
                },
                accuracy=result.final_val_accuracy,
                status="completed",
            )

            with self._lock:
                self._operations.append(operation)

            return operation

        except Exception as e:
            logger.error(f"[LEARNING] Deep learning training failed: {e}")
            return self._create_error_operation("deep_learning", str(e))

    # Model Management
    def validate_model(self, model_id: str, test_data: any) -> LearningOperation:
        """Validate a model."""
        if not self._model_validator:
            return self._create_disabled_operation("validation")

        try:
            report = self._model_validator.validate_model(model_id, test_data)

            operation = LearningOperation(
                operation_id=f"validation_{now().sequence}",
                operation_type="evaluation",
                model_name=model_id,
                input_data={},
                output_data={"validation_passed": report.passed, "warnings": report.warnings},
                accuracy=report.metrics.get("accuracy", 0.0),
                status="completed",
            )

            with self._lock:
                self._operations.append(operation)

            return operation

        except Exception as e:
            logger.error(f"[LEARNING] Validation failed: {e}")
            return self._create_error_operation("validation", str(e))

    def deploy_model(self, model_id: str, version: str = "1.0") -> LearningOperation:
        """Deploy a model."""
        if not self._model_deployer:
            return self._create_disabled_operation("deployment")

        try:
            deployment_id = self._model_deployer.deploy_model(model_id, version)

            operation = LearningOperation(
                operation_id=f"deployment_{now().sequence}",
                operation_type="adaptation",
                model_name=model_id,
                input_data={"version": version},
                output_data={"deployment_id": deployment_id},
                accuracy=0.0,
                status="completed",
            )

            with self._lock:
                self._operations.append(operation)

            return operation

        except Exception as e:
            logger.error(f"[LEARNING] Deployment failed: {e}")
            return self._create_error_operation("deployment", str(e))

    # Component Access
    def get_supervised_learner(self) -> Optional[ProductionSupervisedLearner]:
        """Get the supervised learner component."""
        return self._supervised_learner

    def get_unsupervised_learner(self) -> Optional[ProductionUnsupervisedLearner]:
        """Get the unsupervised learner component."""
        return self._unsupervised_learner

    def get_reinforcement_learner(self) -> Optional[ProductionReinforcementLearner]:
        """Get the reinforcement learner component."""
        return self._reinforcement_learner

    def get_deep_learner(self) -> Optional[ProductionDeepLearner]:
        """Get the deep learner component."""
        return self._deep_learner

    def get_model_trainer(self) -> Optional[ProductionModelTrainer]:
        """Get the model trainer component."""
        return self._model_trainer

    def get_model_validator(self) -> Optional[ProductionModelValidator]:
        """Get the model validator component."""
        return self._model_validator

    def get_model_deployer(self) -> Optional[ProductionModelDeployer]:
        """Get the model deployer component."""
        return self._model_deployer

    def get_adaptive_learner(self) -> Optional[ProductionAdaptiveLearner]:
        """Get the adaptive learner component."""
        return self._adaptive_learner

    # DYON Integration Properties
    @property
    def dyon_assistant(self):
        """Get DYON coding assistant for autonomous coding tasks."""
        return self._dyon_assistant

    @property
    def dyon_reflection(self):
        """Get DYON self-reflection for learning analysis."""
        return self._dyon_reflection

    @property
    def dyon_enabled(self) -> bool:
        """Check if DYON integration is enabled."""
        return self._dyon_enabled

    # DYON Integration Methods

    def analyze_learning_engine(self) -> dict[str, Any]:
        """Analyze the learning engine using DYON self-reflection."""
        if not self._dyon_enabled or not self._dyon_reflection:
            return {"error": "DYON self-reflection not enabled", "dyon_enabled": self._dyon_enabled}

        logger.info("[LEARNING] DYON analyzing learning engine...")
        result = self._dyon_reflection.analyze_codebase(focus="learning_engine")
        return {
            "analysis": result.to_report(),
            "issues_found": len(result.issues),
            "priority": result.priority,
            "action_items": result.action_items,
        }

    def optimize_learning_component(self, component: str, goal: str) -> dict[str, Any]:
        """Optimize a learning component using DYON.

        Args:
            component: Component name (supervised, unsupervised, reinforcement, deep, trainer, validator, deployer, adaptive)
            goal: Optimization goal
        """
        if not self._dyon_enabled or not self._dyon_assistant:
            return {
                "error": "DYON coding assistant not enabled",
                "dyon_enabled": self._dyon_enabled,
            }

        logger.info(f"[LEARNING] DYON optimizing {component} for: {goal}")
        result = self._dyon_assistant.optimize_performance(component, goal)
        return {
            "component": component,
            "goal": goal,
            "result": result,
            "status": result.get("status", "unknown"),
        }

    def evolve_learning_engine(self, goal: str) -> dict[str, Any]:
        """Evolve the learning engine for a specific goal using DYON.

        This is a high-level autonomous operation for learning evolution.
        """
        if not self._dyon_enabled or not self._dyon_assistant:
            return {
                "error": "DYON coding assistant not enabled",
                "dyon_enabled": self._dyon_enabled,
            }

        logger.warning(f"[LEARNING] DYON evolving learning engine for: {goal}")
        result = self._dyon_assistant.evolve_system(goal)
        return {
            "goal": goal,
            "result": result,
            "status": result.get("status", "unknown"),
            "warning": "Autonomous learning evolution executed",
        }

    def fix_learning_bug(self, component: str, bug_description: str) -> dict[str, Any]:
        """Fix a learning bug using DYON.

        Args:
            component: Component name
            bug_description: Description of the bug
        """
        if not self._dyon_enabled or not self._dyon_assistant:
            return {
                "error": "DYON coding assistant not enabled",
                "dyon_enabled": self._dyon_enabled,
            }

        logger.info(f"[LEARNING] DYON fixing bug in {component}: {bug_description}")
        result = self._dyon_assistant.fix_bug(f"learning_engine/{component}.py", bug_description)
        return {
            "component": component,
            "bug": bug_description,
            "result": result,
            "status": result.get("status", "unknown"),
        }

    def suggest_learning_improvements(self, goal: str) -> dict[str, Any]:
        """Suggest learning engine improvements using DYON reflection.

        Args:
            goal: Improvement goal
        """
        if not self._dyon_enabled or not self._dyon_reflection:
            return {"error": "DYON self-reflection not enabled", "dyon_enabled": self._dyon_enabled}

        logger.info(f"[LEARNING] DYON suggesting learning improvements for: {goal}")
        suggestions = self._dyon_reflection.suggest_improvements(goal)
        return {"goal": goal, "suggestions": suggestions, "count": len(suggestions)}

    def get_orchestrator_state(self) -> dict[str, Any]:
        """Get comprehensive orchestrator state including DYON."""
        return {
            "supervised_learner": {"status": "active" if self._supervised_learner else "inactive"},
            "unsupervised_learner": {
                "status": "active" if self._unsupervised_learner else "inactive"
            },
            "reinforcement_learner": {
                "status": "active" if self._reinforcement_learner else "inactive"
            },
            "deep_learner": {"status": "active" if self._deep_learner else "inactive"},
            "model_trainer": {"status": "active" if self._model_trainer else "inactive"},
            "model_validator": {"status": "active" if self._model_validator else "inactive"},
            "model_deployer": {"status": "active" if self._model_deployer else "inactive"},
            "adaptive_learner": {"status": "active" if self._adaptive_learner else "inactive"},
            "dyon_integration": {
                "enabled": self._dyon_enabled,
                "assistant": "active" if self._dyon_assistant else "inactive",
                "reflection": "active" if self._dyon_reflection else "inactive",
                "capabilities": (
                    ["coding", "self_reflection", "autonomous_evolution"]
                    if self._dyon_enabled
                    else []
                ),
            },
            "operations_count": len(self._operations),
            "status": "ready",
        }

    def get_operations(self, limit: int = 100) -> list[LearningOperation]:
        """Get operation history."""
        with self._lock:
            return self._operations[-limit:]

    def clear_operations(self) -> None:
        """Clear operation history."""
        with self._lock:
            self._operations.clear()
        logger.info("[LEARNING] Operation history cleared")

    def _create_disabled_operation(self, operation_type: str) -> LearningOperation:
        """Create operation for disabled component."""
        return LearningOperation(
            operation_id=f"{operation_type}_{now().sequence}",
            operation_type=operation_type,
            model_name="disabled",
            input_data={},
            output_data={"status": "disabled"},
            accuracy=0.0,
            status="failed",
        )

    def _create_error_operation(self, operation_type: str, error: str) -> LearningOperation:
        """Create operation for failed operation."""
        return LearningOperation(
            operation_id=f"{operation_type}_{now().sequence}",
            operation_type=operation_type,
            model_name="error",
            input_data={},
            output_data={"status": "error", "message": error},
            accuracy=0.0,
            status="failed",
        )


def get_learning_orchestrator() -> LearningOrchestrator:
    """Get the singleton learning orchestrator instance."""
    if not hasattr(get_learning_orchestrator, "_instance"):
        get_learning_orchestrator._instance = LearningOrchestrator()
    return get_learning_orchestrator._instance
