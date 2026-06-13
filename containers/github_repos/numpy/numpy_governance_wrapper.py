"""
NumPy Governance Wrapper for DIX VISION Integration

This wrapper provides governance oversight for NumPy numerical computing operations,
ensuring operator authority, computational safety, and compliance with DIX VISION's
constitutional governance for numerical operations.

Author: DIX VISION Numerical Computing Governance
Version: 42.2
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import time

import sys
import os
sys.path.append('/app/governance')

from base_external_repo_wrapper import (
    BaseExternalRepoGovernanceWrapper,
    PermissionLevel,
    GovernanceViolation,
    SafetyViolation,
    ExternalRepositoryMetrics,
    ExternalRepositoryHealthCheck
)

class NumPyGovernanceWrapper(BaseExternalRepoGovernanceWrapper):
    """
    Governance wrapper for NumPy numerical computing operations.
    
    This ensures that all numerical operations are:
    - Governed by operator authority (operator has ultimate authority)
    - Validated for computational safety (memory limits, array size limits)
    - Audited for compliance (operation logging, resource tracking)
    - Monitored for performance (execution time, memory usage, throughput)
    """
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__("numpy", permission_level)
        self.metrics = ExternalRepositoryMetrics("numpy")
        self.numpy_available = False
        self.operation_limits = {
            'max_array_size': 1000000,  # 1M elements
            'max_memory_usage': 1073741824,  # 1GB
            'max_execution_time': 300,  # 5 minutes
            'max_ndim': 10
        }
        self.current_memory_usage = 0
        self.operation_history = []
        self.computational_restrictions = {
            'blocked_operations': ['eval', 'exec', 'compile'],
            'blocked_data_types': ['object'],
            'max_recursion_depth': 1000
        }
        
    def initialize_numpy(self, numpy_config: Dict[str, Any]):
        """
        Initialize NumPy with governance oversight.
        
        Args:
            numpy_config: NumPy configuration (precision, error handling, etc.)
        """
        try:
            import numpy as np
            
            self.numpy_available = True
            self.np = np
            
            # Configure NumPy with governance oversight
            np.seterr(
                invalid=numpy_config.get('invalid', 'warn'),
                divide=numpy_config.get('divide', 'warn'),
                overflow=numpy_config.get('overflow', 'warn'),
                underflow=numpy_config.get('underflow', 'ignore')
            )
            
            self.logger.info("NumPy initialized with governance oversight")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize NumPy: {str(e)}")
            raise GovernanceViolation(f"NumPy initialization failed: {str(e)}")
    
    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """
        Enhanced safety checks specific to numerical operations.
        """
        if not self.safety_check_enabled:
            return True
            
        # Check basic safety
        if not super().safety_check(operation, params):
            return False
            
        # NumPy-specific safety checks
        if 'array' in operation.lower() or 'compute' in operation.lower():
            if not self._validate_computational_safety(params):
                return False
                
        return True
    
    def _validate_computational_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of computational operations"""
        array_size = params.get('size', 0)
        ndim = params.get('ndim', 1)
        memory_estimate = params.get('memory_estimate', 0)
        
        # Check array size limit
        if array_size > self.operation_limits['max_array_size']:
            self.logger.warning(f"Array size exceeds limit: {array_size}")
            return False
            
        # Check dimensionality limit
        if ndim > self.operation_limits['max_ndim']:
            self.logger.warning(f"Array dimensions exceed limit: {ndim}")
            return False
            
        # Check memory usage
        if memory_estimate > self.operation_limits['max_memory_usage']:
            self.logger.warning(f"Memory usage exceeds limit: {memory_estimate}")
            return False
        
        # Check blocked operations
        operation_name = params.get('operation', '')
        for blocked in self.computational_restrictions['blocked_operations']:
            if blocked in operation_name.lower():
                self.logger.warning(f"Blocked operation: {blocked}")
                return False
        
        return True
    
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method for NumPy operations.
        """
        start_time = time.time()
        success = False
        
        try:
            if not self.numpy_available:
                raise GovernanceViolation("NumPy not initialized")
            
            # Map operation to NumPy method
            if operation == 'create_array':
                data = params.get('data', [])
                dtype = params.get('dtype', 'float64')
                
                # Create array with governance
                array_size = len(data) if hasattr(data, '__len__') else 1
                memory_estimate = array_size * 8  # 8 bytes per float64
                
                if not self._validate_computational_safety({
                    'size': array_size,
                    'ndim': params.get('ndim', 1),
                    'memory_estimate': memory_estimate,
                    'operation': 'create_array'
                }):
                    raise SafetyViolation("Computational safety validation failed")
                
                result = self.np.array(data, dtype=dtype)
                self.current_memory_usage += memory_estimate
                
            elif operation == 'array_operation':
                array = params.get('array')
                operation_name = params.get('operation', '')
                operation_params = params.get('params', {})
                
                # Check if operation is blocked
                if operation_name in self.computational_restrictions['blocked_operations']:
                    raise SafetyViolation(f"Blocked operation: {operation_name}")
                
                # Execute operation
                if operation_name == 'mean':
                    result = self.np.mean(array)
                elif operation_name == 'std':
                    result = self.np.std(array)
                elif operation_name == 'sum':
                    result = self.np.sum(array)
                elif operation_name == 'dot':
                    other = params.get('other_array')
                    result = self.np.dot(array, other)
                else:
                    result = {"error": f"Unknown operation: {operation_name}"}
                
            elif operation == 'matrix_operation':
                matrix = params.get('matrix')
                operation_name = params.get('operation', '')
                
                # Check matrix size
                matrix_size = matrix.size if hasattr(matrix, 'size') else len(matrix)
                if matrix_size > self.operation_limits['max_array_size']:
                    raise SafetyViolation("Matrix size exceeds limit")
                
                if operation_name == 'transpose':
                    result = self.np.transpose(matrix)
                elif operation_name == 'inverse':
                    result = self.np.linalg.inv(matrix)
                elif operation_name == 'eigenvalues':
                    result = self.np.linalg.eigvals(matrix)
                else:
                    result = {"error": f"Unknown operation: {operation_name}"}
                
            elif operation == 'get_computational_metrics':
                result = self.metrics.get_metrics()
                
                # Add NumPy-specific metrics
                result['numpy_metrics'] = {
                    'current_memory_usage': self.current_memory_usage,
                    'operation_history_size': len(self.operation_history),
                    'operation_limits': self.operation_limits,
                    'numpy_available': self.numpy_available
                }
                
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            success = True
            execution_time = time.time() - start_time
            self.metrics.record_operation(success, execution_time)
            
            # Record operation in history
            self.operation_history.append({
                'operation': operation,
                'timestamp': datetime.utcnow().isoformat(),
                'execution_time': execution_time,
                'success': success
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.record_operation(False, execution_time)
            self.logger.error(f"NumPy operation failed: {operation} - {str(e)}")
            raise
    
    def create_array(self,
                    data: List[Any],
                    dtype: str = 'float64',
                    ndim: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a NumPy array with governance oversight.
        
        Args:
            data: Data for the array
            dtype: Data type for the array
            ndim: Number of dimensions
        
        Returns:
            Array creation result with governance metadata
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.READ_ONLY):
                raise GovernanceViolation("Read permission required for array creation")
            
            # Prepare parameters
            params = {
                'data': data,
                'dtype': dtype,
                'ndim': ndim or 1
            }
            
            # Execute with governance
            result = self.execute_operation('create_array', params, PermissionLevel.READ_ONLY)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'memory_estimate': len(data) * 8,
                'array_size': len(data) if hasattr(data, '__len__') else 1,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Array creation failed: {str(e)}")
            raise
    
    def perform_computation(self,
                          array: Any,
                          operation: str,
                          params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a numerical computation with governance oversight.
        
        Args:
            array: NumPy array for computation
            operation: Computation to perform (mean, std, sum, dot, etc.)
            params: Additional parameters for the computation
        
        Returns:
            Computation result with governance metadata
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.EXECUTE):
                raise GovernanceViolation("Execute permission required for computations")
            
            # Prepare parameters
            params_data = {
                'array': array,
                'operation': operation,
                'params': params or {}
            }
            
            # Execute with governance
            result = self.execute_operation('array_operation', params_data, PermissionLevel.EXECUTE)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'operation_limits': self.operation_limits,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Computation failed: {str(e)}")
            raise
    
    def get_computational_metrics(self) -> Dict[str, Any]:
        """Get computational metrics"""
        return {
            'repository_metrics': self.metrics.get_metrics(),
            'numpy_metrics': self.execute_operation('get_computational_metrics', {}, PermissionLevel.READ_ONLY),
            'current_memory_usage': self.current_memory_usage,
            'operation_history': self.operation_history[-100:],  # Last 100 operations
            'permission_level': self.permission_level.value,
            'computational_restrictions': self.computational_restrictions
        }


# Example usage
if __name__ == "__main__":
    # Create wrapper with appropriate permission level
    wrapper = NumPyGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Initialize NumPy
    # wrapper.initialize_numpy({
    #     'invalid': 'warn',
    #     'divide': 'warn',
    #     'overflow': 'warn',
    #     'underflow': 'ignore'
    # })
    
    print("NumPy Governance Wrapper initialized successfully")
