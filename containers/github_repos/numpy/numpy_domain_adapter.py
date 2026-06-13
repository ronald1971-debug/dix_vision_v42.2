"""
NumPy Domain Adapter for DIX VISION Integration

This adapter translates NumPy numerical computing concepts into DIX VISION's
cognitive architecture, ensuring proper domain mapping and data transformation.

Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

from base_domain_adapter import (
    SystemDomainAdapter,
    DomainType,
    DataFormat
)

class NumPyDomainAdapter(SystemDomainAdapter):
    """
    Domain adapter for NumPy numerical computing data.
    
    This adapter handles:
    - Numerical concept mapping
    - Array data transformation
    - Matrix operations integration
    - Computational results standardization
    - Numerical data enhancement
    """
    
    def __init__(self):
        super().__init__("numpy")
        
        # NumPy-specific concept mappings
        self.register_concept_mapping('array', 'numerical_matrix')
        self.register_concept_mapping('matrix', 'computational_grid')
        self.register_concept_mapping('scalar', 'single_value')
        self.register_concept_mapping('computation', 'numerical_operation')
        self.register_concept_mapping('dimension', 'data_axis')
        
        # Data type mappings
        self.dtype_mappings = {
            'float64': 'high_precision_float',
            'float32': 'standard_float',
            'int64': 'large_integer',
            'int32': 'standard_integer',
            'bool': 'logical_value',
            'complex128': 'complex_number'
        }
        
    def adapt_array_data(self, array_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt NumPy array data to DIX VISION format"""
        try:
            adapted = {
                'numerical_matrix': {
                    'matrix_id': array_data.get('array_id', 'unknown'),
                    'data_type': self.dtype_mappings.get(array_data.get('dtype', 'float64'), 'unknown'),
                    'dimensions': array_data.get('shape', []),
                    'element_count': array_data.get('size', 0),
                    'created_at': datetime.utcnow().isoformat()
                },
                'matrix_metadata': {
                    'dtype': array_data.get('dtype', 'float64'),
                    'shape': array_data.get('shape', []),
                    'size': array_data.get('size', 0),
                    'memory_usage': array_data.get('nbytes', 0),
                    'flags': array_data.get('flags', {})
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'matrix_class': self._classify_matrix(array_data),
                'complexity': self._assess_complexity(array_data),
                'computational_efficiency': self._assess_efficiency(array_data),
                'memory_optimization': self._assess_memory_optimization(array_data)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'numpy_array',
                'source': 'numpy',
                'cognitive_layer': 'numerical_computing'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt array data: {str(e)}")
            raise
    
    def adapt_computation_data(self, computation: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt NumPy computation data to DIX VISION format"""
        try:
            adapted = {
                'numerical_operation': {
                    'operation_type': computation.get('operation', 'unknown'),
                    'operation_id': computation.get('computation_id', 'unknown'),
                    'executed_at': datetime.utcnow().isoformat()
                },
                'operation_metadata': {
                    'input_shape': computation.get('input_shape', []),
                    'output_value': computation.get('result', None),
                    'execution_time': computation.get('execution_time', 0),
                    'memory_used': computation.get('memory_used', 0)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'operation_class': self._classify_computation(computation),
                'performance': self._assess_performance(computation),
                'data_integrity': self._assess_data_integrity(computation),
                'cognitive_insight': self._extract_cognitive_insight(computation)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'numpy_computation',
                'source': 'numpy',
                'cognitive_layer': 'numerical_operations'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt computation data: {str(e)}")
            raise
    
    def _classify_matrix(self, array_data: Dict[str, Any]) -> str:
        """Classify the type of matrix"""
        ndim = len(array_data.get('shape', []))
        dtype = array_data.get('dtype', 'float64')
        
        if ndim == 0:
            return 'scalar'
        elif ndim == 1:
            return 'vector'
        elif ndim == 2:
            return 'matrix'
        else:
            return 'tensor'
    
    def _assess_complexity(self, array_data: Dict[str, Any]) -> str:
        """Assess the complexity of the matrix"""
        size = array_data.get('size', 0)
        ndim = len(array_data.get('shape', []))
        
        if size > 100000 or ndim > 3:
            return 'high_complexity'
        elif size > 10000 or ndim > 2:
            return 'moderate_complexity'
        else:
            return 'low_complexity'
    
    def _assess_efficiency(self, array_data: Dict[str, Any]) -> str:
        """Assess the computational efficiency"""
        memory_usage = array_data.get('nbytes', 0)
        size = array_data.get('size', 0)
        
        if size > 0:
            bytes_per_element = memory_usage / size
            if bytes_per_element <= 4:
                return 'high_efficiency'
            elif bytes_per_element <= 8:
                return 'standard_efficiency'
            else:
                return 'low_efficiency'
        return 'unknown_efficiency'
    
    def _assess_memory_optimization(self, array_data: Dict[str, Any]) -> str:
        """Assess memory optimization level"""
        flags = array_data.get('flags', {})
        dtype = array_data.get('dtype', 'float64')
        
        is_c_contiguous = flags.get('c_contiguous', True)
        is_fortran_contiguous = flags.get('f_contiguous', False)
        
        if dtype in ['float32', 'int32'] and is_c_contiguous:
            return 'optimized'
        elif is_c_contiguous:
            return 'standard'
        else:
            return 'suboptimal'
    
    def _classify_computation(self, computation: Dict[str, Any]) -> str:
        """Classify the type of computation"""
        operation = computation.get('operation', '').lower()
        
        if operation in ['mean', 'sum', 'std', 'var']:
            return 'statistical_computation'
        elif operation in ['dot', 'matmul', 'multiply']:
            return 'linear_algebra'
        elif operation in ['fft', 'convolve']:
            return 'signal_processing'
        else:
            return 'general_computation'
    
    def _assess_performance(self, computation: Dict[str, Any]) -> str:
        """Assess the performance of the computation"""
        execution_time = computation.get('execution_time', 0)
        
        if execution_time < 0.01:
            return 'excellent_performance'
        elif execution_time < 0.1:
            return 'good_performance'
        elif execution_time < 1.0:
            return 'acceptable_performance'
        else:
            return 'poor_performance'
    
    def _assess_data_integrity(self, computation: Dict[str, Any]) -> str:
        """Assess data integrity of computation"""
        result = computation.get('result')
        
        if result is not None:
            return 'integrity_verified'
        else:
            return 'integrity_questionable'
    
    def _extract_cognitive_insight(self, computation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cognitive insight from computation"""
        operation = computation.get('operation', '')
        execution_time = computation.get('execution_time', 0)
        
        return {
            'computational_complexity': 'high' if execution_time > 0.1 else 'low',
            'result_precision': 'standard',
            'optimization_potential': 'analyzed'
        }
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        """Main adaptation method for NumPy data"""
        if isinstance(data, dict):
            if 'dtype' in data or 'shape' in data:
                return self.adapt_array_data(data)
            elif 'operation' in data or 'result' in data:
                return self.adapt_computation_data(data)
        
        return self.enhance_data(data)
    
    def reverse_adapt_data(self, internal_data: Any, target_format: DataFormat) -> Any:
        """Reverse adaptation for NumPy data"""
        if isinstance(internal_data, dict) and 'data' in internal_data:
            data = internal_data['data']
        else:
            data = internal_data
        
        if target_format == DataFormat.JSON:
            return self._reverse_json_numpy_data(data)
        
        return data
    
    def _reverse_json_numpy_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse JSON NumPy data adaptation"""
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
    adapter = NumPyDomainAdapter()
    
    sample_array = {
        'array_id': 'array_12345',
        'dtype': 'float64',
        'shape': [10, 10],
        'size': 100,
        'nbytes': 800
    }
    
    adapted_array = adapter.adapt_array_data(sample_array)
    print("Adapted array:", adapted_array)
    
    print("NumPy Domain Adapter initialized successfully")
