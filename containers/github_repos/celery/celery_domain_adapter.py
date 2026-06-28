"""
Celery Domain Adapter for DIX VISION Integration

This adapter translates Celery distributed task queue concepts into DIX VISION's
cognitive architecture, ensuring proper domain mapping and data transformation.

Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append('/app/adapters')

from base_domain_adapter import DataFormat, SystemDomainAdapter


class CeleryDomainAdapter(SystemDomainAdapter):
    """
    Domain adapter for Celery distributed task queue data.
    
    This adapter handles:
    - Task concept mapping
    - Task execution data transformation
    - Worker status integration
    - Queue data standardization
    - Task result enhancement
    """
    
    def __init__(self):
        super().__init__("celery")
        
        # Celery-specific concept mappings
        self.register_concept_mapping('task', 'cognitive_operation')
        self.register_concept_mapping('worker', 'processing_unit')
        self.register_concept_mapping('queue', 'cognitive_channel')
        self.register_concept_mapping('broker', 'message_transport')
        self.register_concept_mapping('result', 'operation_outcome')
        
        # Task status mappings
        self.task_status_mappings = {
            'PENDING': 'operation_queued',
            'STARTED': 'operation_in_progress',
            'SUCCESS': 'operation_completed',
            'FAILURE': 'operation_failed',
            'RETRY': 'operation_retrying',
            'REVOKED': 'operation_cancelled'
        }
        
    def adapt_task_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt Celery task data to DIX VISION format.
        
        Args:
            task: Task data (task_name, args, kwargs, options)
        
        Returns:
            Adapted task with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'cognitive_operation': {
                    'operation_id': task.get('task_id', 'unknown'),
                    'operation_type': task.get('task_name', 'unknown_operation'),
                    'initiated_at': datetime.utcnow().isoformat()
                },
                'operation_parameters': {
                    'arguments': task.get('args', []),
                    'keyword_arguments': task.get('kwargs', {}),
                    'execution_options': task.get('options', {})
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'operation_class': self._classify_operation(task),
                'complexity': self._assess_operation_complexity(task),
                'resource_requirement': self._assess_resource_requirement(task),
                'expected_duration': self._predict_operation_duration(task),
                'priority': task.get('options', {}).get('priority', 'normal')
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'task',
                'source': 'celery',
                'cognitive_layer': 'task_management'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt task data: {str(e)}")
            raise
    
    def adapt_task_result_data(self, result: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt Celery task result data to DIX VISION format.
        
        Args:
            result: Task result data (status, result_value, traceback, etc.)
            task: Original task for context
        
        Returns:
            Adapted result with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'operation_outcome': {
                    'operation_id': result.get('task_id', 'unknown'),
                    'operation_type': task.get('task_name', 'unknown_operation'),
                    'status': self.task_status_mappings.get(result.get('status', 'UNKNOWN'), 'operation_unknown'),
                    'completed_at': datetime.utcnow().isoformat()
                },
                'outcome_metadata': {
                    'result_value': result.get('result', None),
                    'traceback': result.get('traceback', ''),
                    'error': result.get('error', ''),
                    'execution_time': result.get('execution_time', 0),
                    'retries': result.get('retries', 0)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'success': result.get('status') == 'SUCCESS',
                'outcome_type': self._classify_outcome(result),
                'data_quality': self._assess_data_quality(result),
                'performance_quality': self._assess_performance_quality(result),
                'cognitive_insight': self._extract_cognitive_insight(result, task)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'task_result',
                'source': 'celery',
                'cognitive_layer': 'task_management'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt task result data: {str(e)}")
            raise
    
    def adapt_worker_data(self, worker: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt Celery worker data to DIX VISION format.
        
        Args:
            worker: Worker data (worker_name, status, active_tasks, etc.)
        
        Returns:
            Adapted worker with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'processing_unit': {
                    'unit_id': worker.get('worker_name', 'unknown'),
                    'status': worker.get('status', 'unknown'),
                    'availability': worker.get('availability', 'unknown')
                },
                'unit_metadata': {
                    'active_operations': worker.get('active_tasks', 0),
                    'total_operations': worker.get('total_tasks', 0),
                    'queue': worker.get('queue', 'default'),
                    'hostname': worker.get('hostname', 'unknown'),
                    'started_at': worker.get('started_at', 'unknown')
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'unit_capacity': self._assess_unit_capacity(worker),
                'workload': self._assess_workload(worker),
                'efficiency': self._assess_efficiency(worker),
                'health': self._assess_health(worker)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'worker',
                'source': 'celery',
                'cognitive_layer': 'resource_management'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt worker data: {str(e)}")
            raise
    
    def adapt_queue_data(self, queue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt Celery queue data to DIX VISION format.
        
        Args:
            queue: Queue data (queue_name, size, etc.)
        
        Returns:
            Adapted queue with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'cognitive_channel': {
                    'channel_id': queue.get('queue_name', 'default'),
                    'channel_type': queue.get('queue_type', 'fifo'),
                    'size': queue.get('size', 0)
                },
                'channel_metadata': {
                    'max_size': queue.get('max_size', 0),
                    'pending_tasks': queue.get('pending', 0),
                    'priority': queue.get('priority', 'normal')
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'channel_load': self._assess_channel_load(queue),
                'throughput': self._assess_throughput(queue),
                'blocking': self._assess_blocking(queue),
                'recommendation': self._generate_recommendation(queue)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'queue',
                'source': 'celery',
                'cognitive_layer': 'task_management'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt queue data: {str(e)}")
            raise
    
    def _classify_operation(self, task: Dict[str, Any]) -> str:
        """Classify the type of operation"""
        task_name = task.get('task_name', '').lower()
        
        if 'process' in task_name or 'compute' in task_name:
            return 'computation_operation'
        elif 'fetch' in task_name or 'retrieve' in task_name or 'get' in task_name:
            return 'data_retrieval_operation'
        elif 'store' in task_name or 'save' in task_name or 'write' in task_name:
            return 'data_storage_operation'
        elif 'send' in task_name or 'notify' in task_name or 'alert' in task_name:
            return 'communication_operation'
        elif 'analyze' in task_name or 'evaluate' in task_name or 'assess' in task_name:
            return 'analysis_operation'
        else:
            return 'general_operation'
    
    def _assess_operation_complexity(self, task: Dict[str, Any]) -> str:
        """Assess the complexity of the operation"""
        args = task.get('args', [])
        kwargs = task.get('kwargs', {})
        
        total_size = len(str(args)) + len(str(kwargs))
        
        if total_size > 100000:
            return 'high_complexity'
        elif total_size > 10000:
            return 'moderate_complexity'
        else:
            return 'low_complexity'
    
    def _assess_resource_requirement(self, task: Dict[str, Any]) -> str:
        """Assess the resource requirement of the operation"""
        task_name = task.get('task_name', '').lower()
        
        if any(hint in task_name for hint in ['machine_learning', 'training', 'model', 'compute']):
            return 'high_resource'
        elif any(hint in task_name for hint in ['process', 'analyze', 'transform']):
            return 'moderate_resource'
        else:
            return 'low_resource'
    
    def _predict_operation_duration(self, task: Dict[str, Any]) -> str:
        """Predict the expected duration of the operation"""
        task_name = task.get('task_name', '').lower()
        complexity = self._assess_operation_complexity(task)
        
        if complexity == 'high_complexity':
            return 'long_duration'
        elif complexity == 'moderate_complexity':
            return 'medium_duration'
        elif any(hint in task_name for hint in ['quick', 'simple', 'lightweight']):
            return 'short_duration'
        else:
            return 'normal_duration'
    
    def _classify_outcome(self, result: Dict[str, Any]) -> str:
        """Classify the type of outcome"""
        status = result.get('status', 'UNKNOWN')
        
        if status == 'SUCCESS':
            return 'successful_outcome'
        elif status == 'FAILURE':
            return 'failed_outcome'
        elif status == 'RETRY':
            return 'retrying_outcome'
        elif status == 'REVOKED':
            return 'cancelled_outcome'
        else:
            return 'unknown_outcome'
    
    def _assess_data_quality(self, result: Dict[str, Any]) -> str:
        """Assess the quality of the result data"""
        result_value = result.get('result')
        status = result.get('status')
        
        if status == 'SUCCESS' and result_value is not None:
            if isinstance(result_value, (dict, list)):
                return 'structured_data'
            elif isinstance(result_value, str):
                return 'text_data'
            else:
                return 'primitive_data'
        else:
            return 'no_data'
    
    def _assess_performance_quality(self, result: Dict[str, Any]) -> str:
        """Assess the quality of the performance"""
        execution_time = result.get('execution_time', 0)
        
        if execution_time < 1:
            return 'excellent_performance'
        elif execution_time < 10:
            return 'good_performance'
        elif execution_time < 60:
            return 'acceptable_performance'
        else:
            return 'poor_performance'
    
    def _extract_cognitive_insight(self, result: Dict[str, Any], task: Dict[str, Any]) -> str:
        """Extract cognitive insight from the result"""
        status = result.get('status', 'UNKNOWN')
        retries = result.get('retries', 0)
        
        if status == 'SUCCESS':
            return f'task_completed_successfully_after_{retries}_attempts' if retries > 0 else 'task_completed_successfully'
        elif status == 'FAILURE':
            return f'task_failed_after_{retries}_retry_attempts'
        elif status == 'RETRY':
            return f'task_retrying_attempt_{retries + 1}'
        else:
            return 'task_status_unknown'
    
    def _assess_unit_capacity(self, worker: Dict[str, Any]) -> str:
        """Assess the capacity of the processing unit"""
        active = worker.get('active_tasks', 0)
        total = worker.get('total_tasks', 0)
        
        if total == 0:
            return 'unused_capacity'
        
        utilization = active / total
        
        if utilization > 0.8:
            return 'high_utilization'
        elif utilization > 0.5:
            return 'moderate_utilization'
        elif utilization > 0.2:
            return 'low_utilization'
        else:
            return 'minimal_utilization'
    
    def _assess_workload(self, worker: Dict[str, Any]) -> str:
        """Assess the workload of the processing unit"""
        active = worker.get('active_tasks', 0)
        
        if active > 10:
            return 'heavy_workload'
        elif active > 5:
            return 'moderate_workload'
        elif active > 0:
            return 'light_workload'
        else:
            return 'idle'
    
    def _assess_efficiency(self, worker: Dict[str, Any]) -> str:
        """Assess the efficiency of the processing unit"""
        # Simplified efficiency assessment
        return 'normal_efficiency'
    
    def _assess_health(self, worker: Dict[str, Any]) -> str:
        """Assess the health of the processing unit"""
        status = worker.get('status', 'unknown')
        
        if status == 'ONLINE':
            return 'healthy'
        elif status == 'OFFLINE':
            return 'unhealthy'
        else:
            return 'unknown_health'
    
    def _assess_channel_load(self, queue: Dict[str, Any]) -> str:
        """Assess the load of the cognitive channel"""
        size = queue.get('size', 0)
        max_size = queue.get('max_size', 0)
        
        if max_size > 0:
            utilization = size / max_size
            if utilization > 0.8:
                return 'high_load'
            elif utilization > 0.5:
                return 'moderate_load'
            else:
                return 'low_load'
        else:
            return 'unknown_load'
    
    def _assess_throughput(self, queue: Dict[str, Any]) -> str:
        """Assess the throughput of the cognitive channel"""
        # Simplified throughput assessment
        return 'normal_throughput'
    
    def _assess_blocking(self, queue: Dict[str, Any]) -> str:
        """Assess if the channel is blocking"""
        size = queue.get('size', 0)
        
        if size > 0:
            return 'non_blocking'
        else:
            return 'blocking'
    
    def _generate_recommendation(self, queue: Dict[str, Any]) -> str:
        """Generate recommendation for the cognitive channel"""
        size = queue.get('size', 0)
        
        if size > 100:
            return 'consider_adding_workers'
        elif size > 10:
            return 'monitor_queue_depth'
        else:
            return 'no_action_needed'
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        """Main adaptation method for Celery data"""
        # Determine data type and route to appropriate adapter
        if isinstance(data, dict):
            if 'task_name' in data or 'task_id' in data:
                return self.adapt_task_data(data)
            elif 'status' in data and 'result' in data:
                return self.adapt_task_result_data(data, {})
            elif 'worker_name' in data or 'worker_id' in data:
                return self.adapt_worker_data(data)
            elif 'queue_name' in data or 'queue' in data:
                return self.adapt_queue_data(data)
        
        # Default adaptation
        return self.enhance_data(data)
    
    def reverse_adapt_data(self, internal_data: Any, target_format: DataFormat) -> Any:
        """Reverse adaptation for Celery data"""
        # Remove DIX VISION enhancements
        if isinstance(internal_data, dict) and 'data' in internal_data:
            data = internal_data['data']
        else:
            data = internal_data
        
        # Reverse concept mappings
        if target_format == DataFormat.JSON:
            return self._reverse_json_celery_data(data)
        
        return data
    
    def _reverse_json_celery_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse JSON Celery data adaptation"""
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
    adapter = CeleryDomainAdapter()
    
    # Example task adaptation
    sample_task = {
        'task_name': 'process_market_data',
        'task_id': 'task_123456',
        'args': ['BTC/USDT'],
        'kwargs': {'timeframe': '1h'},
        'options': {'priority': 'high', 'countdown': 60}
    }
    
    adapted_task = adapter.adapt_task_data(sample_task)
    print("Adapted task:", adapted_task)
    
    print("Celery Domain Adapter initialized successfully")
