"""
DIXVISION INDIRA Continual Learning
Contract-Compliant Real Implementation
"""

from .continual_learning import (
    LearningTaskType,
    ParameterImportance,
    ContinualLearningResult,
    ElasticWeightConsolidation,
    ProgressNeuralNetworks,
    ExperienceReplayWithImportance,
    DynamicNetworkExpansion,
    KnowledgeDistillation,
    ContinualLearningSystem,
    get_continual_learning_system
)

__all__ = [
    'LearningTaskType',
    'ParameterImportance',
    'ContinualLearningResult',
    'ElasticWeightConsolidation',
    'ProgressNeuralNetworks',
    'ExperienceReplayWithImportance',
    'DynamicNetworkExpansion',
    'KnowledgeDistillation',
    'ContinualLearningSystem',
    'get_continual_learning_system'
]