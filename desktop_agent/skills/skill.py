"""
Skill - Reusable capability and automation framework
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SkillMetadata:
    """Metadata for a skill."""
    id: str
    name: str
    description: str
    category: str
    version: str
    author: str
    parameters: Dict[str, Any]
    dependencies: List[str]


class Skill(ABC):
    """
    Base class for skills.
    
    Skills are reusable capabilities that can be invoked by agents
    to perform specific tasks or automations.
    """
    
    def __init__(self, runtime):
        """
        Initialize skill.
        
        Args:
            runtime: AgentRuntime instance
        """
        self.runtime = runtime
        self.enabled = True
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the skill.
        
        Args:
            **kwargs: Skill parameters
            
        Returns:
            Execution result
        """
        pass
        
    @abstractmethod
    def get_metadata(self) -> SkillMetadata:
        """
        Get skill metadata.
        
        Returns:
            Skill metadata
        """
        pass
        
    async def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate skill parameters.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        metadata = self.get_metadata()
        required_params = metadata.parameters.get("required", [])
        
        for param in required_params:
            if param not in parameters:
                self.logger.error(f"Missing required parameter: {param}")
                return False
                
        return True
        
    def enable(self) -> None:
        """Enable the skill."""
        self.enabled = True
        
    def disable(self) -> None:
        """Disable the skill."""
        self.enabled = False
