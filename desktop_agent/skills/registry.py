"""
Skill Registry - Skill management and discovery
"""

import logging
from typing import Dict, List, Optional, Type, Any
from .skill import Skill, SkillMetadata


class SkillRegistry:
    """
    Registry for managing skills.
    
    Handles skill registration, discovery, execution, and
    dependency management for the Desktop AgentOS.
    """
    
    def __init__(self, runtime):
        """
        Initialize skill registry.
        
        Args:
            runtime: AgentRuntime instance
        """
        self.runtime = runtime
        self.skills: Dict[str, Skill] = {}
        self.skill_metadata: Dict[str, SkillMetadata] = {}
        self.categories: Dict[str, List[str]] = {}
        
        self.logger = logging.getLogger(__name__)
        
    def register(self, skill: Skill) -> None:
        """
        Register a skill.
        
        Args:
            skill: Skill instance
        """
        try:
            metadata = skill.get_metadata()
            
            self.skills[metadata.id] = skill
            self.skill_metadata[metadata.id] = metadata
            
            # Add to category
            if metadata.category not in self.categories:
                self.categories[metadata.category] = []
            self.categories[metadata.category].append(metadata.id)
            
            self.logger.info(f"Registered skill: {metadata.name} (id: {metadata.id})")
        except Exception as e:
            self.logger.error(f"Error registering skill: {e}")
            
    def unregister(self, skill_id: str) -> None:
        """
        Unregister a skill.
        
        Args:
            skill_id: Skill identifier
        """
        if skill_id in self.skills:
            metadata = self.skill_metadata[skill_id]
            
            # Remove from category
            if metadata.category in self.categories:
                self.categories[metadata.category] = [
                    s for s in self.categories[metadata.category] if s != skill_id
                ]
                
            del self.skills[skill_id]
            del self.skill_metadata[skill_id]
            
            self.logger.info(f"Unregistered skill: {skill_id}")
            
    def get(self, skill_id: str) -> Optional[Skill]:
        """
        Get a skill by ID.
        
        Args:
            skill_id: Skill identifier
            
        Returns:
            Skill instance or None
        """
        return self.skills.get(skill_id)
        
    def get_metadata(self, skill_id: str) -> Optional[SkillMetadata]:
        """
        Get skill metadata.
        
        Args:
            skill_id: Skill identifier
            
        Returns:
            Skill metadata or None
        """
        return self.skill_metadata.get(skill_id)
        
    async def execute(self, skill_id: str, **kwargs) -> Any:
        """
        Execute a skill.
        
        Args:
            skill_id: Skill identifier
            **kwargs: Skill parameters
            
        Returns:
            Execution result
        """
        skill = self.get(skill_id)
        if not skill:
            self.logger.error(f"Skill not found: {skill_id}")
            return None
            
        if not skill.enabled:
            self.logger.error(f"Skill disabled: {skill_id}")
            return None
            
        # Validate parameters
        if not await skill.validate_parameters(kwargs):
            self.logger.error(f"Invalid parameters for skill: {skill_id}")
            return None
            
        try:
            return await skill.execute(**kwargs)
        except Exception as e:
            self.logger.error(f"Error executing skill {skill_id}: {e}")
            return None
            
    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """
        List skills.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of skill IDs
        """
        if category:
            return self.categories.get(category, [])
        return list(self.skills.keys())
        
    def list_categories(self) -> List[str]:
        """
        List all skill categories.
        
        Returns:
            List of category names
        """
        return list(self.categories.keys())
        
    def search(self, query: str) -> List[SkillMetadata]:
        """
        Search for skills.
        
        Args:
            query: Search query
            
        Returns:
            List of matching skill metadata
        """
        results = []
        
        for metadata in self.skill_metadata.values():
            if (
                query.lower() in metadata.name.lower()
                or query.lower() in metadata.description.lower()
            ):
                results.append(metadata)
                
        return results
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get registry status.
        
        Returns:
            Status dictionary
        """
        return {
            "total_skills": len(self.skills),
            "categories": {
                cat: len(skills)
                for cat, skills in self.categories.items()
            },
            "enabled_skills": sum(1 for s in self.skills.values() if s.enabled),
        }
