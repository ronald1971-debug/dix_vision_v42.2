"""
Pandas Governance Wrapper for DIX VISION Integration

This wrapper provides governance oversight for Pandas data analysis operations,
ensuring operator authority, data safety, and compliance with DIX VISION's
constitutional governance for data operations.

Author: DIX VISION Data Analysis Governance
Version: 42.2
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import time

from base_external_repo_wrapper import (
    BaseExternalRepoGovernanceWrapper,
    PermissionLevel,
    GovernanceViolation,
    SafetyViolation,
    ExternalRepositoryMetrics,
    ExternalRepositoryHealthCheck
)

class PandasGovernanceWrapper(BaseExternalRepoGovernanceWrapper):
    """
    Governance wrapper for Pandas data analysis operations.
    
    This ensures that all data operations are:
    - Governed by operator authority (operator has ultimate authority)
    - Validated for data safety (data size limits, schema validation)
    - Audited for compliance (data operation logging, access tracking)
    - Monitored for performance (query time, memory usage, data throughput)
    """
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__("pandas", permission_level)
        self.metrics = ExternalRepositoryMetrics("pandas")
        self.pandas_available = False
        self.operation_limits = {
            'max_dataframe_rows': 1000000,
            'max_dataframe_columns': 1000,
            'max_memory_usage': 1073741824,  # 1GB
            'max_execution_time': 600  # 10 minutes
        }
        self.current_memory_usage = 0
        self.operation_history = []
        self.data_restrictions = {
            'blocked_operations': ['eval', 'exec', 'compile'],
            'blocked_data_types': ['object'],
            'max_file_size': 104857600,  # 100MB
            'allowed_formats': ['csv', 'json', 'parquet', 'excel']
        }
        
    def initialize_pandas(self, pandas_config: Dict[str, Any]):
        """
        Initialize Pandas with governance oversight.
        
        Args:
            pandas_config: Pandas configuration (precision, error handling, etc.)
        """
        try:
            import pandas as pd
            
            self.pandas_available = True
            self.pd = pd
            
            # Configure Pandas with governance oversight
            pd.set_option('display.max_rows', pandas_config.get('max_rows', 100))
            pd.set_option('display.max_columns', pandas_config.get('max_columns', 20))
            pd.set_option('display.precision', pandas_config.get('precision', 6))
            pd.set_option('mode.chained_assignment', pandas_config.get('chained_assignment', 'warn'))
            
            self.logger.info("Pandas initialized with governance oversight")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Pandas: {str(e)}")
            raise GovernanceViolation(f"Pandas initialization failed: {str(e)}")
    
    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """
        Enhanced safety checks specific to data operations.
        """
        if not self.safety_check_enabled:
            return True
            
        # Check basic safety
        if not super().safety_check(operation, params):
            return False
            
        # Pandas-specific safety checks
        if 'dataframe' in operation.lower() or 'analysis' in operation.lower():
            if not self._validate_data_safety(params):
                return False
                
        return True
    
    def _validate_data_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of data operations"""
        row_count = params.get('row_count', 0)
        col_count = params.get('col_count', 0)
        memory_estimate = params.get('memory_estimate', 0)
        file_size = params.get('file_size', 0)
        
        # Check dataframe size limits
        if row_count > self.operation_limits['max_dataframe_rows']:
            self.logger.warning(f"Row count exceeds limit: {row_count}")
            return False
            
        if col_count > self.operation_limits['max_dataframe_columns']:
            self.logger.warning(f"Column count exceeds limit: {col_count}")
            return False
        
        # Check memory usage
        if memory_estimate > self.operation_limits['max_memory_usage']:
            self.logger.warning(f"Memory usage exceeds limit: {memory_estimate}")
            return False
        
        # Check file size
        if file_size > self.data_restrictions['max_file_size']:
            self.logger.warning(f"File size exceeds limit: {file_size}")
            return False
        
        # Check blocked operations
        operation_name = params.get('operation', '')
        for blocked in self.data_restrictions['blocked_operations']:
            if blocked in operation_name.lower():
                self.logger.warning(f"Blocked operation: {blocked}")
                return False
        
        return True
    
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method for Pandas operations.
        """
        start_time = time.time()
        success = False
        
        try:
            if not self.pandas_available:
                raise GovernanceViolation("Pandas not initialized")
            
            # Map operation to Pandas method
            if operation == 'create_dataframe':
                data = params.get('data', [])
                columns = params.get('columns', None)
                
                # Estimate memory
                row_count = len(data) if hasattr(data, '__len__') else 1
                col_count = len(columns) if columns else len(data[0]) if data else 1
                memory_estimate = row_count * col_count * 8  # 8 bytes per element
                
                if not self._validate_data_safety({
                    'row_count': row_count,
                    'col_count': col_count,
                    'memory_estimate': memory_estimate,
                    'operation': 'create_dataframe'
                }):
                    raise SafetyViolation("Data safety validation failed")
                
                result = self.pd.DataFrame(data, columns=columns)
                self.current_memory_usage += memory_estimate
                
            elif operation == 'dataframe_operation':
                df = params.get('dataframe')
                operation_name = params.get('operation', '')
                operation_params = params.get('params', {})
                
                # Check if operation is blocked
                if operation_name in self.data_restrictions['blocked_operations']:
                    raise SafetyViolation(f"Blocked operation: {operation_name}")
                
                # Execute operation
                if operation_name == 'head':
                    n = operation_params.get('n', 5)
                    result = df.head(n)
                elif operation_name == 'describe':
                    result = df.describe()
                elif operation_name == 'groupby':
                    group_by = operation_params.get('group_by')
                    result = df.groupby(group_by)
                elif operation_name == 'merge':
                    other_df = params.get('other_dataframe')
                    result = df.merge(other_df, **operation_params)
                elif operation_name == 'query':
                    query_string = operation_params.get('query')
                    result = df.query(query_string)
                else:
                    result = {"error": f"Unknown operation: {operation_name}"}
                
            elif operation == 'data_analysis':
                df = params.get('dataframe')
                analysis_type = params.get('analysis_type', 'summary')
                
                if analysis_type == 'summary':
                    result = {
                        'shape': df.shape,
                        'columns': df.columns.tolist(),
                        'dtypes': df.dtypes.astype(str).to_dict(),
                        'memory_usage': df.memory_usage(deep=True).sum()
                    }
                elif analysis_type == 'statistics':
                    result = df.describe().to_dict()
                elif analysis_type == 'missing_values':
                    result = df.isnull().sum().to_dict()
                else:
                    result = {"error": f"Unknown analysis type: {analysis_type}"}
                
            elif operation == 'get_data_metrics':
                result = self.metrics.get_metrics()
                
                # Add Pandas-specific metrics
                result['pandas_metrics'] = {
                    'current_memory_usage': self.current_memory_usage,
                    'operation_history_size': len(self.operation_history),
                    'operation_limits': self.operation_limits,
                    'pandas_available': self.pandas_available
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
            self.logger.error(f"Pandas operation failed: {operation} - {str(e)}")
            raise
    
    def create_dataframe(self,
                        data: List[Any],
                        columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a Pandas DataFrame with governance oversight.
        
        Args:
            data: Data for the dataframe
            columns: Column names for the dataframe
        
        Returns:
            DataFrame creation result with governance metadata
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.READ_ONLY):
                raise GovernanceViolation("Read permission required for dataframe creation")
            
            # Prepare parameters
            params = {
                'data': data,
                'columns': columns
            }
            
            # Execute with governance
            result = self.execute_operation('create_dataframe', params, PermissionLevel.READ_ONLY)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'data_limits': self.operation_limits,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"DataFrame creation failed: {str(e)}")
            raise
    
    def perform_analysis(self,
                       dataframe: Any,
                       analysis_type: str = 'summary') -> Dict[str, Any]:
        """
        Perform data analysis with governance oversight.
        
        Args:
            dataframe: Pandas DataFrame for analysis
            analysis_type: Type of analysis to perform
        
        Returns:
            Analysis result with governance metadata
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.READ_ONLY):
                raise GovernanceViolation("Read permission required for data analysis")
            
            # Prepare parameters
            params = {
                'dataframe': dataframe,
                'analysis_type': analysis_type
            }
            
            # Execute with governance
            result = self.execute_operation('data_analysis', params, PermissionLevel.READ_ONLY)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'operation_limits': self.operation_limits,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Data analysis failed: {str(e)}")
            raise
    
    def get_data_metrics(self) -> Dict[str, Any]:
        """Get data processing metrics"""
        return {
            'repository_metrics': self.metrics.get_metrics(),
            'pandas_metrics': self.execute_operation('get_data_metrics', {}, PermissionLevel.READ_ONLY),
            'current_memory_usage': self.current_memory_usage,
            'operation_history': self.operation_history[-100:],
            'permission_level': self.permission_level.value,
            'data_restrictions': self.data_restrictions
        }


# Example usage
if __name__ == "__main__":
    # Create wrapper with appropriate permission level
    wrapper = PandasGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Initialize Pandas
    # wrapper.initialize_pandas({
    #     'max_rows': 100,
    #     'max_columns': 20,
    #     'precision': 6,
    #     'chained_assignment': 'warn'
    # })
    
    print("Pandas Governance Wrapper initialized successfully")
