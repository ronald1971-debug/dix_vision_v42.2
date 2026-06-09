"""
Visual Agent HUD - Agent visualization and observation
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimelineEvent:
    """Event in the timeline."""
    timestamp: datetime
    event_type: str
    agent: str
    data: Dict[str, Any]


class VisualAgentHUD:
    """
    Visual Agent HUD for operator observation.
    
    Provides real-time visualization of agent activities, goals,
    research, observations, beliefs, and proposals through a
    live timeline interface.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize HUD.
        
        Args:
            config: HUD configuration
        """
        self.config = config or {}
        self.is_visible = False
        
        self.timeline: List[TimelineEvent] = []
        self.max_timeline_events = self.config.get("max_events", 1000)
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize HUD."""
        self.logger.info("Visual Agent HUD initialized")
        
    async def show(self) -> None:
        """Show HUD."""
        self.is_visible = True
        self.logger.info("HUD shown")
        
    async def hide(self) -> None:
        """Hide HUD."""
        self.is_visible = False
        self.logger.info("HUD hidden")
        
    async def add_timeline_event(self, event: TimelineEvent) -> None:
        """
        Add event to timeline.
        
        Args:
            event: Timeline event
        """
        self.timeline.append(event)
        
        # Trim if too many events
        if len(self.timeline) > self.max_timeline_events:
            self.timeline = self.timeline[-self.max_timeline_events:]
            
    def get_timeline(self, limit: int = 100) -> List[TimelineEvent]:
        """
        Get timeline events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            Timeline events
        """
        return self.timeline[-limit:]
        
    def filter_timeline(
        self,
        agent: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> List[TimelineEvent]:
        """
        Filter timeline events.
        
        Args:
            agent: Optional agent filter
            event_type: Optional event type filter
            
        Returns:
            Filtered timeline events
        """
        events = self.timeline
        
        if agent:
            events = [e for e in events if e.agent == agent]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
            
        return events
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get HUD status.
        
        Returns:
            Status dictionary
        """
        return {
            "is_visible": self.is_visible,
            "timeline_events": len(self.timeline),
        }


class INDIRAHUD(VisualAgentHUD):
    """
    HUD specific to INDIRA agent.
    
    Shows current goal, task, research, browser, observations,
    beliefs, and proposals.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize INDIRA HUD."""
        super().__init__(config)
        
        self.current_goal: Optional[str] = None
        self.current_task: Optional[str] = None
        self.current_research: Optional[str] = None
        self.current_browser: Optional[str] = None
        self.current_observations: List[str] = []
        self.current_beliefs: Dict[str, Any] = {}
        self.current_proposals: List[Dict[str, Any]] = []
        
    def update_goal(self, goal: str) -> None:
        """Update current goal."""
        self.current_goal = goal
        
    def update_task(self, task: str) -> None:
        """Update current task."""
        self.current_task = task
        
    def get_indira_status(self) -> Dict[str, Any]:
        """Get INDIRA-specific status."""
        return {
            "current_goal": self.current_goal,
            "current_task": self.current_task,
            "current_research": self.current_research,
            "current_browser": self.current_browser,
            "observation_count": len(self.current_observations),
            "belief_count": len(self.current_beliefs),
            "proposal_count": len(self.current_proposals),
        }


class DYONHUD(VisualAgentHUD):
    """
    HUD specific to DYON agent.
    
    Shows current analysis, patch, skill, workflow, and
    repository findings.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize DYON HUD."""
        super().__init__(config)
        
        self.current_analysis: Optional[str] = None
        self.current_patch: Optional[str] = None
        self.current_skill: Optional[str] = None
        self.current_workflow: Optional[str] = None
        self.repository_findings: List[Dict[str, Any]] = []
        
    def update_analysis(self, analysis: str) -> None:
        """Update current analysis."""
        self.current_analysis = analysis
        
    def update_patch(self, patch: str) -> None:
        """Update current patch."""
        self.current_patch = patch
        
    def get_dyon_status(self) -> Dict[str, Any]:
        """Get DYON-specific status."""
        return {
            "current_analysis": self.current_analysis,
            "current_patch": self.current_patch,
            "current_skill": self.current_skill,
            "current_workflow": self.current_workflow,
            "finding_count": len(self.repository_findings),
        }
