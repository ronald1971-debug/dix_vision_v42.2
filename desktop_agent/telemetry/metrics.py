"""
Metrics Collector - Performance and usage metrics
"""

import logging
import psutil
import time
from typing import Dict, Any
from datetime import datetime


class MetricsCollector:
    """
    Collects system and application metrics.
    
    Tracks CPU, memory, disk, and network usage along with
    custom application metrics.
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.logger = logging.getLogger(__name__)
        
    def collect_system_metrics(self) -> Dict[str, Any]:
        """
        Collect system-level metrics.
        
        Returns:
            System metrics dictionary
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent if psutil.disk_usage('/') else 0,
            "process_count": len(psutil.pids()),
        }
        
    def collect_process_metrics(self, pid: int) -> Dict[str, Any]:
        """
        Collect metrics for a specific process.
        
        Args:
            pid: Process ID
            
        Returns:
            Process metrics dictionary
        """
        try:
            process = psutil.Process(pid)
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "pid": pid,
                "name": process.name(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_info": process.memory_info()._asdict(),
                "num_threads": process.num_threads(),
                "num_handles": process.num_handles() if hasattr(process, 'num_handles') else 0,
            }
        except psutil.NoSuchProcess:
            return {}
        except Exception as e:
            self.logger.error(f"Error collecting process metrics: {e}")
            return {}
            
    def collect_custom_metric(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """
        Create a custom metric.
        
        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags
            
        Returns:
            Metric dictionary
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "name": name,
            "value": value,
            "tags": tags or {},
        }
