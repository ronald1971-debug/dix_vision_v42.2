"""
Celery Governance Wrapper for DIX VISION Integration

This wrapper provides governance oversight for Celery distributed task queue operations,
ensuring operator authority, task safety, and compliance with DIX VISION's
constitutional governance for background task processing.

Author: DIX VISION Task Governance
Version: 42.2
"""

import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.append('/app/governance')

from base_external_repo_wrapper import (
    BaseExternalRepoGovernanceWrapper,
    ExternalRepositoryMetrics,
    GovernanceViolation,
    PermissionLevel,
    SafetyViolation,
)


class CeleryGovernanceWrapper(BaseExternalRepoGovernanceWrapper):
    """
    Governance wrapper for Celery distributed task queue operations.
    
    This ensures that all task operations are:
    - Governed by operator authority (operator has ultimate authority)
    - Validated for task safety (task execution limits, resource controls)
    - Audited for compliance (task logging, execution tracking)
    - Monitored for performance (task latency, queue depth, worker status)
    """
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__("celery", permission_level)
        self.metrics = ExternalRepositoryMetrics("celery")
        self.celery_app = None
        self.active_tasks = {}
        self.task_limits = {
            'max_task_duration': 3600,  # 1 hour
            'max_retries': 3,
            'task_timeout': 300,
            'max_concurrent_tasks': 50
        }
        self.current_task_count = 0
        self.task_execution_history = []
        self.security_restrictions = {
            'allowed_task_modules': [],  # Empty means all allowed
            'blocked_task_modules': ['os.system', 'subprocess.run', 'exec', 'eval'],
            'max_task_args_length': 1048576,  # 1MB
            'allowed_result_types': ['dict', 'list', 'str', 'int', 'float', 'bool', 'NoneType']
        }
        
    def initialize_celery(self, broker_url: str, result_backend: str, task_config: Dict[str, Any]):
        """
        Initialize Celery with governance oversight.
        
        Args:
            broker_url: Message broker URL (e.g., Redis)
            result_backend: Result backend URL
            task_config: Task configuration (task names, routes, etc.)
        """
        try:
            from celery import Celery
            
            self.celery_app = Celery(
                task_config.get('app_name', 'dixvision_tasks'),
                broker=broker_url,
                backend=result_backend
            )
            
            # Configure task settings with governance oversight
            self.celery_app.conf.update(
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                task_track_started=True,
                task_time_limit=self.task_limits['max_task_duration'],
                task_soft_time_limit=self.task_limits['task_timeout'],
                task_acks_late=True,
                worker_prefetch_multiplier=4,
                task_max_retries=self.task_limits['max_retries'],
                task_default_retry_delay=60,
            )
            
            self.logger.info("Celery initialized with governance oversight")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Celery: {str(e)}")
            raise GovernanceViolation(f"Celery initialization failed: {str(e)}")
    
    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """
        Enhanced safety checks specific to task operations.
        """
        if not self.safety_check_enabled:
            return True
            
        # Check basic safety
        if not super().safety_check(operation, params):
            return False
            
        # Task-specific safety checks
        if 'execute_task' in operation.lower() or 'apply_async' in operation.lower():
            if not self._validate_task_safety(params):
                return False
                
        return True
    
    def _validate_task_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of task execution"""
        task_name = params.get('task_name', '')
        task_args = params.get('args', [])
        task_kwargs = params.get('kwargs', {})
        
        # Check blocked task modules
        for blocked_module in self.security_restrictions['blocked_task_modules']:
            if blocked_module in task_name.lower():
                self.logger.warning(f"Blocked task module: {blocked_module}")
                return False
        
        # Check task arguments size
        args_length = len(str(task_args)) + len(str(task_kwargs))
        if args_length > self.security_restrictions['max_task_args_length']:
            self.logger.warning(f"Task arguments too large: {args_length} bytes")
            return False
        
        # Check concurrent task limit
        if self.current_task_count >= self.task_limits['max_concurrent_tasks']:
            self.logger.warning("Max concurrent tasks limit reached")
            return False
        
        return True
    
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method for Celery operations.
        """
        start_time = time.time()
        success = False
        
        try:
            if not self.celery_app:
                raise GovernanceViolation("Celery instance not initialized")
            
            # Map operation to Celery method
            if operation == 'execute_task':
                task_name = params.get('task_name', '')
                args = params.get('args', [])
                kwargs = params.get('kwargs', {})
                options = params.get('options', {})
                
                # Check task safety
                if not self._validate_task_safety(params):
                    raise SafetyViolation("Task safety validation failed")
                
                # Update task count
                self.current_task_count += 1
                
                # Simulate task execution (in production, would use actual Celery)
                task_id = f"task_{int(time.time() * 1000)}"
                self.active_tasks[task_id] = {
                    'task_name': task_name,
                    'started_at': datetime.utcnow().isoformat(),
                    'status': 'pending'
                }
                
                result = {
                    'task_id': task_id,
                    'task_name': task_name,
                    'status': 'queued',
                    'queued_at': datetime.utcnow().isoformat()
                }
                
            elif operation == 'check_task_status':
                task_id = params.get('task_id')
                
                if task_id not in self.active_tasks:
                    raise ValueError(f"Task not found: {task_id}")
                
                result = {
                    'task_id': task_id,
                    'status': self.active_tasks[task_id]['status'],
                    'task_name': self.active_tasks[task_id]['task_name'],
                    'started_at': self.active_tasks[task_id]['started_at']
                }
                
            elif operation == 'get_active_tasks':
                result = {
                    'active_tasks': self.active_tasks,
                    'task_count': len(self.active_tasks)
                }
                
            elif operation == 'cancel_task':
                task_id = params.get('task_id')
                
                if task_id not in self.active_tasks:
                    raise ValueError(f"Task not found: {task_id}")
                
                self.active_tasks[task_id]['status'] = 'cancelled'
                self.current_task_count = max(0, self.current_task_count - 1)
                
                result = {
                    'task_id': task_id,
                    'status': 'cancelled',
                    'cancelled_at': datetime.utcnow().isoformat()
                }
                
            elif operation == 'get_task_metrics':
                result = self.metrics.get_metrics()
                
                # Add Celery-specific metrics
                result['celery_metrics'] = {
                    'current_task_count': self.current_task_count,
                    'active_tasks': len(self.active_tasks),
                    'task_execution_history': len(self.task_execution_history),
                    'task_limits': self.task_limits
                }
                
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            success = True
            execution_time = time.time() - start_time
            self.metrics.record_operation(success, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.record_operation(False, execution_time)
            self.logger.error(f"Celery operation failed: {operation} - {str(e)}")
            raise
    
    def execute_task(self,
                    task_name: str,
                    args: Optional[List[Any]] = None,
                    kwargs: Optional[Dict[str, Any]] = None,
                    options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a Celery task with governance oversight.
        
        Args:
            task_name: Name of the task to execute
            args: Task positional arguments
            kwargs: Task keyword arguments
            options: Celery execution options (countdown, retry, etc.)
        
        Returns:
            Task execution result with governance metadata
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.EXECUTE):
                raise GovernanceViolation("Execute permission required for task execution")
            
            # Prepare parameters
            params = {
                'task_name': task_name,
                'args': args or [],
                'kwargs': kwargs or {},
                'options': options or {}
            }
            
            # Execute with governance
            result = self.execute_operation('execute_task', params, PermissionLevel.EXECUTE)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'task_limits': self.task_limits,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Record task execution
            self.task_execution_history.append({
                'task_name': task_name,
                'task_id': result['task_id'],
                'executed_at': datetime.utcnow().isoformat(),
                'status': 'queued'
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            raise
    
    def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """Check the status of a task"""
        return self.execute_operation('check_task_status', {'task_id': task_id}, PermissionLevel.READ_ONLY)
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a task"""
        return self.execute_operation('cancel_task', {'task_id': task_id}, PermissionLevel.EXECUTE)
    
    def get_task_metrics(self) -> Dict[str, Any]:
        """Get task execution metrics"""
        return {
            'repository_metrics': self.metrics.get_metrics(),
            'celery_metrics': self.execute_operation('get_task_metrics', {}, PermissionLevel.READ_ONLY),
            'current_task_count': self.current_task_count,
            'active_tasks': self.active_tasks,
            'task_execution_history': self.task_execution_history[-100:],  # Last 100 tasks
            'permission_level': self.permission_level.value,
            'security_restrictions': self.security_restrictions
        }


# Example usage
if __name__ == "__main__":
    # Create wrapper with appropriate permission level
    wrapper = CeleryGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Initialize Celery (would need actual Redis/Pg for production)
    # wrapper.initialize_celery(
    #     broker_url='redis://localhost:6379/0',
    #     result_backend='redis://localhost:6379/0',
    #     task_config={'app_name': 'dixvision_tasks'}
    # )
    
    print("Celery Governance Wrapper initialized successfully")
