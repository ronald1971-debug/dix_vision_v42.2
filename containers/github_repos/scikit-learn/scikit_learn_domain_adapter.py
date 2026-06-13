"""
Scikit-Learn Domain Adapter for DIX VISION Integration

This adapter translates Scikit-Learn ML concepts into DIX VISION's
cognitive architecture, ensuring proper domain mapping and data transformation.

Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import sys
import os
sys.path.append('/app/adapters')

from base_domain_adapter import (
    SystemDomainAdapter,
    DomainType,
    DataFormat
)

class ScikitLearnDomainAdapter(SystemDomainAdapter):
    """
    Domain adapter for Scikit-Learn machine learning data.
    
    This adapter handles ML concept mapping, model data transformation,
    training results integration, and prediction standardization.
    """
    
    def __init__(self):
        super().__init__("scikit-learn")
        
        # Scikit-Learn-specific concept mappings
        self.register_concept_mapping('model', 'cognitive_algorithm')
        self.register_concept_mapping('features', 'input_characteristics')
        self.register_concept_mapping('labels', 'target_outcomes')
        self.register_concept_mapping('training', 'learning_process')
        self.register_concept_mapping('prediction', 'inference_result')
        
        # Algorithm mappings
        self.algorithm_mappings = {
            'linear_regression': 'linear_cognitive',
            'decision_tree': 'tree_cognitive',
            'random_forest': 'ensemble_cognitive',
            'svm': 'boundary_cognitive',
            'neural_network': 'deep_cognitive'
        }
        
    def adapt_model_data(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt ML model data to DIX VISION format"""
        try:
            adapted = {
                'cognitive_algorithm': {
                    'algorithm_id': model_data.get('model_id', 'unknown'),
                    'algorithm_type': self.algorithm_mappings.get(model_data.get('model_type', 'unknown'), 'unknown_cognitive'),
                    'trained_samples': model_data.get('n_samples', 0),
                    'features': model_data.get('n_features', 0),
                    'trained_at': datetime.utcnow().isoformat()
                },
                'algorithm_metadata': {
                    'hyperparameters': model_data.get('hyperparameters', {}),
                    'feature_importance': model_data.get('feature_importance', {}),
                    'model_size': model_data.get('model_size', 0)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'model_class': self._classify_model(model_data),
                'complexity': self._assess_complexity(model_data),
                'cognitive_capability': self._assess_cognitive_capability(model_data),
                'generalization': self._assess_generalization(model_data)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'sklearn_model',
                'source': 'scikit-learn',
                'cognitive_layer': 'machine_learning'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt model data: {str(e)}")
            raise
    
    def adapt_training_data(self, training: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt training process data to DIX VISION format"""
        try:
            adapted = {
                'learning_process': {
                    'training_id': training.get('training_id', 'unknown'),
                    'algorithm': training.get('algorithm', 'unknown'),
                    'iterations': training.get('iterations', 0),
                    'completed_at': datetime.utcnow().isoformat()
                },
                'process_metadata': {
                    'training_time': training.get('training_time', 0),
                    'memory_used': training.get('memory_used', 0),
                    'convergence': training.get('convergence', True),
                    'final_loss': training.get('final_loss', 0)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'learning_class': self._classify_learning(training),
                'efficiency': self._assess_efficiency(training),
                'data_quality': self._assess_data_quality(training),
                'cognitive_insight': self._extract_cognitive_insight(training)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'sklearn_training',
                'source': 'scikit-learn',
                'cognitive_layer': 'learning_process'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt training data: {str(e)}")
            raise
    
    def _classify_model(self, model_data: Dict[str, Any]) -> str:
        """Classify the type of model"""
        model_type = model_data.get('model_type', '').lower()
        features = model_data.get('n_features', 0)
        
        if 'linear' in model_type or 'regression' in model_type:
            return 'linear_cognitive'
        elif 'tree' in model_type or 'forest' in model_type:
            return 'ensemble_cognitive'
        elif 'neural' in model_type or 'network' in model_type:
            return 'deep_cognitive'
        elif features > 1000:
            return 'high_dimensional_cognitive'
        else:
            return 'standard_cognitive'
    
    def _assess_complexity(self, model_data: Dict[str, Any]) -> str:
        """Assess the complexity of the model"""
        features = model_data.get('n_features', 0)
        hyperparameters = model_data.get('hyperparameters', {})
        
        if features > 1000 or len(hyperparameters) > 10:
            return 'high_complexity'
        elif features > 100 or len(hyperparameters) > 5:
            return 'moderate_complexity'
        else:
            return 'low_complexity'
    
    def _assess_cognitive_capability(self, model_data: Dict[str, Any]) -> str:
        """Assess the cognitive capability of the model"""
        model_type = model_data.get('model_type', '').lower()
        
        if any(hint in model_type for hint in ['deep', 'neural', 'ensemble']):
            return 'high_capability'
        elif any(hint in model_type for hint in ['linear', 'tree', 'svm']):
            return 'standard_capability'
        else:
            return 'basic_capability'
    
    def _assess_generalization(self, model_data: Dict[str, Any]) -> str:
        """Assess the generalization capability"""
        model_size = model_data.get('model_size', 0)
        
        if model_size < 1000000:
            return 'good_generalization'
        elif model_size < 10000000:
            return 'standard_generalization'
        else:
            return 'overfitting_risk'
    
    def _classify_learning(self, training: Dict[str, Any]) -> str:
        """Classify the type of learning"""
        algorithm = training.get('algorithm', '').lower()
        iterations = training.get('iterations', 0)
        
        if iterations > 1000:
            return 'deep_learning'
        elif 'ensemble' in algorithm:
            return 'ensemble_learning'
        elif 'tree' in algorithm:
            return 'symbolic_learning'
        else:
            return 'statistical_learning'
    
    def _assess_efficiency(self, training: Dict[str, Any]) -> str:
        """Assess the efficiency of training"""
        training_time = training.get('training_time', 0)
        convergence = training.get('convergence', True)
        
        if convergence and training_time < 60:
            return 'high_efficiency'
        elif convergence:
            return 'standard_efficiency'
        else:
            return 'low_efficiency'
    
    def _assess_data_quality(self, training: Dict[str, Any]) -> str:
        """Assess the quality of training data"""
        final_loss = training.get('final_loss', 0)
        
        if final_loss < 0.1:
            return 'high_quality'
        elif final_loss < 0.5:
            return 'standard_quality'
        else:
            return 'low_quality'
    
    def _extract_cognitive_insight(self, training: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cognitive insight from training"""
        algorithm = training.get('algorithm', '')
        convergence = training.get('convergence', True)
        
        return {
            'learning_pattern': 'converged' if convergence else 'unconverged',
            'algorithm_suitability': 'analyzed',
            'cognitive_depth': 'standard'
        }
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        """Main adaptation method for Scikit-Learn data"""
        if isinstance(data, dict):
            if 'model_type' in data or 'n_features' in data:
                return self.adapt_model_data(data)
            elif 'algorithm' in data or 'training_id' in data:
                return self.adapt_training_data(data)
        
        return self.enhance_data(data)
    
    def reverse_adapt_data(self, internal_data: Any, target_format: DataFormat) -> Any:
        """Reverse adaptation for Scikit-Learn data"""
        if isinstance(internal_data, dict) and 'data' in internal_data:
            data = internal_data['data']
        else:
            data = internal_data
        
        if target_format == DataFormat.JSON:
            return self._reverse_json_sklearn_data(data)
        
        return data
    
    def _reverse_json_sklearn_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse JSON Scikit-Learn data adaptation"""
        reverse_mappings = {v: k for k, v in self.concept_mappings.items()}
        adapted = {}
        
        for key, value in data.items():
            external_key = reverse_mappings.get(key, key)
            
            if isinstance(value, dict):
                adapted[external_key] = {reverse_mappings.get(k, k): v for k, v in value.items()}
            elif isinstance(value, list):
                adapted[external_key] = [
                    {reverse_mappings.get(k, k): v for k, v in item.items()} if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                adapted[external_key] = value
        
        return adapted


# Example usage
if __name__ == "__main__":
    adapter = ScikitLearnDomainAdapter()
    
    sample_model = {
        'model_id': 'model_12345',
        'model_type': 'random_forest',
        'n_samples': 10000,
        'n_features': 50
    }
    
    adapted_model = adapter.adapt_model_data(sample_model)
    print("Adapted model:", adapted_model)
    
    print("Scikit-Learn Domain Adapter initialized successfully")
