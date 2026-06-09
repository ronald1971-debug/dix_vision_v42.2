"""
Telemetry System - Complete transparency and monitoring
"""

import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Metric:
    """Telemetry metric."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    metadata: Dict[str, Any]


class TelemetrySystem:
    """
    Telemetry system for complete transparency.
    
    Collects agent telemetry, latency, activity, browser activity,
    desktop activity, skill usage, and research metrics.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize telemetry system.
        
        Args:
            config: Telemetry configuration
        """
        self.config = config or {}
        self.is_active = False
        
        self.metrics: List[Metric] = []
        self.max_metrics = self.config.get("max_metrics", 10000)
        
        # Performance tracking
        self.agent_latencies: Dict[str, List[float]] = {}
        self.agent_activities: Dict[str, List[Dict[str, Any]]] = {}
        self.browser_activities: List[Dict[str, Any]] = []
        self.desktop_activities: List[Dict[str, Any]] = []
        self.skill_usage: Dict[str, int] = {}
        self.research_metrics: Dict[str, Any] = {}
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize telemetry system."""
        self.is_active = True
        self.logger.info("Telemetry System initialized")
        
    async def record_metric(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """
        Record a metric.
        
        Args:
            name: Metric name
            value: Metric value
            tags: Metric tags
            metadata: Additional metadata
        """
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            tags=tags or {},
            metadata=metadata or {},
        )
        
        self.metrics.append(metric)
        
        # Trim if too many metrics
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
            
    async def record_agent_latency(self, agent: str, latency: float) -> None:
        """
        Record agent latency.
        
        Args:
            agent: Agent name
            latency: Latency in seconds
        """
        if agent not in self.agent_latencies:
            self.agent_latencies[agent] = []
        self.agent_latencies[agent].append(latency)
        
    async def record_agent_activity(
        self,
        agent: str,
        activity: Dict[str, Any],
    ) -> None:
        """
        Record agent activity.
        
        Args:
            agent: Agent name
            activity: Activity data
        """
        if agent not in self.agent_activities:
            self.agent_activities[agent] = []
        self.agent_activities[agent].append(activity)
        
    async def record_browser_activity(self, activity: Dict[str, Any]) -> None:
        """
        Record browser activity.
        
        Args:
            activity: Activity data
        """
        self.browser_activities.append(activity)
        
    async def record_desktop_activity(self, activity: Dict[str, Any]) -> None:
        """
        Record desktop activity.
        
        Args:
            activity: Activity data
        """
        self.desktop_activities.append(activity)
        
    async def record_skill_usage(self, skill: str) -> None:
        """
        Record skill usage.
        
        Args:
            skill: Skill name
        """
        self.skill_usage[skill] = self.skill_usage.get(skill, 0) + 1
        
    async def get_metrics(
        self,
        name: Optional[str] = None,
        limit: int = 100,
    ) -> List[Metric]:
        """
        Get metrics.
        
        Args:
            name: Optional metric name filter
            limit: Maximum number of metrics to return
            
        Returns:
            List of metrics
        """
        metrics = self.metrics
        
        if name:
            metrics = [m for m in metrics if m.name == name]
            
        return metrics[-limit:]
        
    async def get_agent_stats(self, agent: str) -> Dict[str, Any]:
        """
        Get statistics for an agent.
        
        Args:
            agent: Agent name
            
        Returns:
            Agent statistics
        """
        latencies = self.agent_latencies.get(agent, [])
        activities = self.agent_activities.get(agent, [])
        
        if not latencies:
            return {
                "agent": agent,
                "avg_latency": 0,
                "max_latency": 0,
                "min_latency": 0,
                "activity_count": len(activities),
            }
            
        return {
            "agent": agent,
            "avg_latency": sum(latencies) / len(latencies),
            "max_latency": max(latencies),
            "min_latency": min(latencies),
            "activity_count": len(activities),
        }
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get telemetry status.
        
        Returns:
            Status dictionary
        """
        return {
            "is_active": self.is_active,
            "total_metrics": len(self.metrics),
            "agents_monitored": list(self.agent_latencies.keys()),
            "browser_activities": len(self.browser_activities),
            "desktop_activities": len(self.desktop_activities),
            "unique_skills": len(self.skill_usage),
        }
