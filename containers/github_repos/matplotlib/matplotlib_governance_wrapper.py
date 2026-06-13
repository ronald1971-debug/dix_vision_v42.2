"""
Matplotlib Governance Wrapper for DIX VISION Integration

This wrapper provides governance oversight for Matplotlib visualization operations,
ensuring operator authority, visualization safety, and compliance with DIX VISION's
constitutional governance for data visualization.

Author: DIX VISION Visualization Governance
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

class MatplotlibGovernanceWrapper(BaseExternalRepoGovernanceWrapper):
    """
    Governance wrapper for Matplotlib visualization operations.
    
    This ensures that all visualization operations are:
    - Governed by operator authority (operator has ultimate authority)
    - Validated for visualization safety (plot size limits, resource usage)
    - Audited for compliance (visualization logging, access tracking)
    - Monitored for performance (render time, memory usage, image size)
    """
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__("matplotlib", permission_level)
        self.metrics = ExternalRepositoryMetrics("matplotlib")
        self.matplotlib_available = False
        self.operation_limits = {
            'max_figure_size': 1000000,  # 1M pixels
            'max_points_per_plot': 100000,
            'max_memory_usage': 536870912,  # 512MB
            'max_execution_time': 120  # 2 minutes
        }
        self.current_memory_usage = 0
        self.operation_history = []
        self.visualization_restrictions = {
            'blocked_operations': ['exec', 'eval'],
            'blocked_plot_types': ['interactive', 'animation'],  # For resource safety
            'max_file_size': 104857600,  # 100MB image file
            'allowed_formats': ['png', 'jpg', 'svg', 'pdf']
        }
        
    def initialize_matplotlib(self, matplotlib_config: Dict[str, Any]):
        """
        Initialize Matplotlib with governance oversight.
        
        Args:
            matplotlib_config: Matplotlib configuration (backend, style, etc.)
        """
        try:
            import matplotlib
            matplotlib.use(marplotlib_config.get('backend', 'Agg'))
            import matplotlib.pyplot as plt
            
            self.matplotlib_available = True
            self.plt = plt
            
            # Configure Matplotlib with governance oversight
            if matplotlib_config.get('style'):
                self.plt.style.use(matplotlib_config['style'])
            
            self.logger.info("Matplotlib initialized with governance oversight")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Matplotlib: {str(e)}")
            raise GovernanceViolation(f"Matplotlib initialization failed: {str(e)}")
    
    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """
        Enhanced safety checks specific to visualization operations.
        """
        if not self.safety_check_enabled:
            return True
            
        # Check basic safety
        if not super().safety_check(operation, params):
            return False
            
        # Matplotlib-specific safety checks
        if 'plot' in operation.lower() or 'visualization' in operation.lower():
            if not self._validate_visualization_safety(params):
                return False
                
        return True
    
    def _validate_visualization_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of visualization operations"""
        figure_size = params.get('figure_size', [0, 0])
        data_points = params.get('data_points', 0)
        memory_estimate = params.get('memory_estimate', 0)
        
        # Check figure size limit (width * height in pixels)
        if isinstance(figure_size, (list, tuple)) and len(figure_size) >= 2:
            pixel_count = figure_size[0] * figure_size[1]
            if pixel_count > self.operation_limits['max_figure_size']:
                self.logger.warning(f"Figure size exceeds limit: {pixel_count} pixels")
                return False
        
        # Check data points limit
        if data_points > self.operation_limits['max_points_per_plot']:
            self.logger.warning(f"Data points exceed limit: {data_points}")
            return False
        
        # Check memory usage
        if memory_estimate > self.operation_limits['max_memory_usage']:
            self.logger.warning(f"Memory usage exceeds limit: {memory_estimate}")
            return False
        
        # Check blocked operations
        operation_name = params.get('operation', '')
        for blocked in self.visualization_restrictions['blocked_operations']:
            if blocked in operation_name.lower():
                self.logger.warning(f"Blocked operation: {blocked}")
                return False
        
        return True
    
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method for Matplotlib operations.
        """
        start_time = time.time()
        success = False
        
        try:
            if not self.matplotlib_available:
                raise GovernanceViolation("Matplotlib not initialized")
            
            # Map operation to Matplotlib method
            if operation == 'create_plot':
                data = params.get('data', [])
                plot_type = params.get('plot_type', 'line')
                figure_size = params.get('figure_size', [10, 6])
                
                # Estimate data points
                data_points = len(data) if hasattr(data, '__len__') else 1
                memory_estimate = data_points * 8  # 8 bytes per point
                
                if not self._validate_visualization_safety({
                    'figure_size': figure_size,
                    'data_points': data_points,
                    'memory_estimate': memory_estimate,
                    'operation': 'create_plot'
                }):
                    raise SafetyViolation("Visualization safety validation failed")
                
                # Create plot
                self.plt.figure(figsize=figure_size)
                
                if plot_type == 'line':
                    self.plt.plot(data)
                elif plot_type == 'bar':
                    self.plt.bar(range(len(data)), data)
                elif plot_type == 'scatter':
                    x_data = params.get('x_data', range(len(data)))
                    self.plt.scatter(x_data, data)
                elif plot_type == 'histogram':
                    self.plt.hist(data)
                else:
                    raise ValueError(f"Unknown plot type: {plot_type}")
                
                result = {
                    'plot_type': plot_type,
                    'data_points': data_points,
                    'figure_size': figure_size,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                self.current_memory_usage += memory_estimate
                
            elif operation == 'save_plot':
                filename = params.get('filename', 'plot.png')
                dpi = params.get('dpi', 100)
                format_type = params.get('format', 'png')
                
                # Check file format
                if format_type not in self.visualization_restrictions['allowed_formats']:
                    raise SafetyViolation(f"Blocked format: {format_type}")
                
                # Save plot
                self.plt.savefig(filename, dpi=dpi, format=format_type, bbox_inches='tight')
                self.plt.close()
                
                result = {
                    'filename': filename,
                    'format': format_type,
                    'dpi': dpi,
                    'saved_at': datetime.utcnow().isoformat()
                }
                
            elif operation == 'visualization_metrics':
                result = self.metrics.get_metrics()
                
                # Add Matplotlib-specific metrics
                result['matplotlib_metrics'] = {
                    'current_memory_usage': self.current_memory_usage,
                    'operation_history_size': len(self.operation_history),
                    'operation_limits': self.operation_limits,
                    'matplotlib_available': self.matplotlib_available
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
            self.logger.error(f"Matplotlib operation failed: {operation} - {str(e)}")
            raise
    
    def create_plot(self,
                  data: List[Any],
                  plot_type: str = 'line',
                  figure_size: List[int] = [10, 6]) -> Dict[str, Any]:
        """
        Create a visualization plot with governance oversight.
        
        Args:
            data: Data for the visualization
            plot_type: Type of plot (line, bar, scatter, histogram)
            figure_size: Figure size in inches [width, height]
        
        Returns:
            Plot creation result with governance metadata
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.READ_ONLY):
                raise GovernanceViolation("Read permission required for plot creation")
            
            # Prepare parameters
            params = {
                'data': data,
                'plot_type': plot_type,
                'figure_size': figure_size
            }
            
            # Execute with governance
            result = self.execute_operation('create_plot', params, PermissionLevel.READ_ONLY)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'visualization_limits': self.operation_limits,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Plot creation failed: {str(e)}")
            raise
    
    def save_plot(self,
                 filename: str,
                 dpi: int = 100,
                 format_type: str = 'png') -> Dict[str, Any]:
        """
        Save the current plot with governance oversight.
        
        Args:
            filename: Output filename
            dpi: Dots per inch
            format_type: File format (png, jpg, svg, pdf)
        
        Returns:
            Save operation result with governance metadata
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.READ_ONLY):
                raise GovernanceViolation("Read permission required for plot saving")
            
            # Prepare parameters
            params = {
                'filename': filename,
                'dpi': dpi,
                'format': format_type
            }
            
            # Execute with governance
            result = self.execute_operation('save_plot', params, PermissionLevel.READ_ONLY)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'file_restrictions': self.visualization_restrictions,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Plot saving failed: {str(e)}")
            raise
    
    def get_visualization_metrics(self) -> Dict[str, Any]:
        """Get visualization metrics"""
        return {
            'repository_metrics': self.metrics.get_metrics(),
            'matplotlib_metrics': self.execute_operation('visualization_metrics', {}, PermissionLevel.READ_ONLY),
            'current_memory_usage': self.current_memory_usage,
            'operation_history': self.operation_history[-100:],
            'permission_level': self.permission_level.value,
            'visualization_restrictions': self.visualization_restrictions
        }


# Example usage
if __name__ == "__main__":
    # Create wrapper with appropriate permission level
    wrapper = MatplotlibGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Initialize Matplotlib
    # wrapper.initialize_matplotlib({
    #     'backend': 'Agg',
    #     'style': 'seaborn'
    # })
    
    print("Matplotlib Governance Wrapper initialized successfully")
