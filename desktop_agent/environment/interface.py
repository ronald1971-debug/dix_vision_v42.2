"""
Environment Interface - Universal environment abstraction
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Element:
    """Represents an element in an environment."""
    id: str
    type: str
    text: str
    attributes: Dict[str, Any] = None
    children: List['Element'] = None
    parent: Optional['Element'] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.children is None:
            self.children = []


@dataclass
class StateSnapshot:
    """Represents a snapshot of environment state."""
    timestamp: float
    elements: List[Element]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class EnvironmentInterface(ABC):
    """
    Abstract interface for cognitive environments.
    
    Provides a universal abstraction for different types of
    environments (browsers, desktop apps, terminals, etc.) with
    standardized operations for observation, interaction, and state management.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize environment interface.
        
        Args:
            config: Environment configuration
        """
        self.config = config or {}
        self.is_connected = False
        self.session_id: Optional[str] = None
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the environment.
        
        Returns:
            True if successful, False otherwise
        """
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the environment."""
        pass
        
    @abstractmethod
    async def observe(self) -> StateSnapshot:
        """
        Observe the current state of the environment.
        
        Returns:
            Current state snapshot
        """
        pass
        
    @abstractmethod
    async def search(self, query: str) -> List[Element]:
        """
        Search for elements in the environment.
        
        Args:
            query: Search query
            
        Returns:
            List of matching elements
        """
        pass
        
    @abstractmethod
    async def navigate(self, target: str) -> bool:
        """
        Navigate to a specific location in the environment.
        
        Args:
            target: Navigation target (URL, path, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        pass
        
    @abstractmethod
    async def extract(self, elements: List[Element]) -> Dict[str, Any]:
        """
        Extract data from elements.
        
        Args:
            elements: Elements to extract from
            
        Returns:
            Extracted data
        """
        pass
        
    @abstractmethod
    async def interact(self, element: Element, action: str, **kwargs) -> bool:
        """
        Interact with an element.
        
        Args:
            element: Element to interact with
            action: Action to perform (click, type, etc.)
            **kwargs: Additional action parameters
            
        Returns:
            True if successful, False otherwise
        """
        pass
        
    @abstractmethod
    async def record_action(self, action: Dict[str, Any]) -> None:
        """
        Record an action for later replay.
        
        Args:
            action: Action to record
        """
        pass
        
    @abstractmethod
    async def replay_actions(self, actions: List[Dict[str, Any]]) -> bool:
        """
        Replay a sequence of actions.
        
        Args:
            actions: Actions to replay
            
        Returns:
            True if successful, False otherwise
        """
        pass
        
    async def wait_for_element(
        self,
        selector: str,
        timeout: float = 30.0,
    ) -> Optional[Element]:
        """
        Wait for an element to appear.
        
        Args:
            selector: Element selector
            timeout: Timeout in seconds
            
        Returns:
            Element or None if timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            elements = await self.search(selector)
            if elements:
                return elements[0]
            await asyncio.sleep(0.5)
            
        return None
        
    async def take_screenshot(self) -> bytes:
        """
        Take a screenshot of the environment.
        
        Returns:
            Screenshot data
        """
        raise NotImplementedError("Screenshot not implemented for this environment")
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get environment status.
        
        Returns:
            Status dictionary
        """
        return {
            "is_connected": self.is_connected,
            "session_id": self.session_id,
            "config": self.config,
        }
