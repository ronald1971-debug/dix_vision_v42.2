"""
DIX VISION v42.2+ Desktop Agent - Profile Manager
Manages browser profiles and user settings
"""

from __future__ import annotations

import asyncio
import logging
import json
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class ProfileType(Enum):
    """Types of browser profiles."""
    DEFAULT = "default"
    INCOGNITO = "incognito"
    CUSTOM = "custom"
    TEMPORARY = "temporary"


@dataclass
class BrowserProfile:
    """Browser profile configuration."""
    profile_id: str
    profile_type: ProfileType
    name: str
    settings: Dict[str, Any]
    cookies: List[Dict[str, Any]]
    extensions: List[str]
    created_at: Optional[float] = None
    last_used: Optional[float] = None


class ProfileManager:
    """Manager for browser profiles and settings."""
    
    def __init__(self, storage_path: str = "/app/data/browser_profiles"):
        """Initialize the Profile Manager."""
        self.logger = logging.getLogger("profile_manager")
        self.logger.setLevel(logging.INFO)
        
        # Profile storage
        self._storage_path = Path(storage_path)
        self._profiles: Dict[str, BrowserProfile] = {}
        self._active_profile_id: Optional[str] = None
        
        # Configuration
        self._config: Dict[str, Any] = {
            "auto_save": True,
            "max_profiles": 20,
            "default_profile": "default",
        }
        
        # Statistics
        self._profiles_created = 0
        self._profiles_loaded = 0
        self._profile_switches = 0
        
        self.logger.info("Profile Manager initialized")
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the profile manager."""
        try:
            self.logger.info("Initializing Profile Manager...")
            
            # Load configuration
            if config:
                self._config.update(config)
            
            # Create storage directory
            self._storage_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing profiles
            await self._load_profiles()
            
            # Create default profile if it doesn't exist
            if "default" not in self._profiles:
                await self.create_profile("default", ProfileType.DEFAULT, "Default Profile")
            
            self.logger.info(f"Profile Manager initialized: {len(self._profiles)} profiles loaded")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Profile Manager: {e}")
            return False
    
    async def create_profile(
        self,
        profile_id: str,
        profile_type: ProfileType,
        name: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a new browser profile."""
        try:
            if len(self._profiles) >= self._config['max_profiles']:
                self.logger.warning(f"Maximum profiles reached: {self._config['max_profiles']}")
                return False
            
            if profile_id in self._profiles:
                self.logger.warning(f"Profile already exists: {profile_id}")
                return False
            
            import time
            profile = BrowserProfile(
                profile_id=profile_id,
                profile_type=profile_type,
                name=name,
                settings=settings or {},
                cookies=[],
                extensions=[],
                created_at=time.time(),
                last_used=None
            )
            
            self._profiles[profile_id] = profile
            self._profiles_created += 1
            
            # Auto-save if enabled
            if self._config['auto_save']:
                await self._save_profile(profile)
            
            self.logger.info(f"Created profile: {profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create profile {profile_id}: {e}")
            return False
    
    async def delete_profile(self, profile_id: str) -> bool:
        """Delete a browser profile."""
        try:
            if profile_id not in self._profiles:
                self.logger.warning(f"Profile not found: {profile_id}")
                return False
            
            # Don't allow deleting the active profile
            if self._active_profile_id == profile_id:
                self.logger.warning(f"Cannot delete active profile: {profile_id}")
                return False
            
            # Don't allow deleting the default profile
            if profile_id == self._config['default_profile']:
                self.logger.warning(f"Cannot delete default profile: {profile_id}")
                return False
            
            # Delete profile file
            profile_file = self._storage_path / f"{profile_id}.json"
            if profile_file.exists():
                profile_file.unlink()
            
            del self._profiles[profile_id]
            
            self.logger.info(f"Deleted profile: {profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete profile {profile_id}: {e}")
            return False
    
    async def switch_to_profile(self, profile_id: str) -> bool:
        """Switch to a specific profile."""
        try:
            if profile_id not in self._profiles:
                self.logger.warning(f"Profile not found: {profile_id}")
                return False
            
            self._active_profile_id = profile_id
            self._profiles[profile_id].last_used = asyncio.get_event_loop().time()
            self._profile_switches += 1
            
            self.logger.info(f"Switched to profile: {profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to switch to profile {profile_id}: {e}")
            return False
    
    async def get_active_profile(self) -> Optional[str]:
        """Get the active profile ID."""
        return self._active_profile_id
    
    async def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific profile."""
        try:
            if profile_id not in self._profiles:
                return None
            
            profile = self._profiles[profile_id]
            return {
                "profile_id": profile.profile_id,
                "profile_type": profile.profile_type.value,
                "name": profile.name,
                "settings": profile.settings,
                "cookies_count": len(profile.cookies),
                "extensions_count": len(profile.extensions),
                "created_at": profile.created_at,
                "last_used": profile.last_used,
                "is_active": profile_id == self._active_profile_id,
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get profile {profile_id}: {e}")
            return None
    
    async def get_all_profiles(self) -> List[Dict[str, Any]]:
        """Get information about all profiles."""
        try:
            profiles_info = []
            for profile_id, profile in self._profiles.items():
                profiles_info.append({
                    "profile_id": profile.profile_id,
                    "profile_type": profile.profile_type.value,
                    "name": profile.name,
                    "settings": profile.settings,
                    "cookies_count": len(profile.cookies),
                    "extensions_count": len(profile.extensions),
                    "created_at": profile.created_at,
                    "last_used": profile.last_used,
                    "is_active": profile_id == self._active_profile_id,
                })
            
            return profiles_info
            
        except Exception as e:
            self.logger.error(f"Failed to get all profiles: {e}")
            return []
    
    async def update_profile_settings(self, profile_id: str, settings: Dict[str, Any]) -> bool:
        """Update settings for a profile."""
        try:
            if profile_id not in self._profiles:
                self.logger.warning(f"Profile not found: {profile_id}")
                return False
            
            self._profiles[profile_id].settings.update(settings)
            
            # Auto-save if enabled
            if self._config['auto_save']:
                await self._save_profile(self._profiles[profile_id])
            
            self.logger.info(f"Updated settings for profile: {profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update settings for profile {profile_id}: {e}")
            return False
    
    async def add_cookie(self, profile_id: str, cookie: Dict[str, Any]) -> bool:
        """Add a cookie to a profile."""
        try:
            if profile_id not in self._profiles:
                self.logger.warning(f"Profile not found: {profile_id}")
                return False
            
            self._profiles[profile_id].cookies.append(cookie)
            
            # Auto-save if enabled
            if self._config['auto_save']:
                await self._save_profile(self._profiles[profile_id])
            
            self.logger.info(f"Added cookie to profile: {profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add cookie to profile {profile_id}: {e}")
            return False
    
    async def clear_cookies(self, profile_id: str) -> bool:
        """Clear all cookies from a profile."""
        try:
            if profile_id not in self._profiles:
                self.logger.warning(f"Profile not found: {profile_id}")
                return False
            
            self._profiles[profile_id].cookies.clear()
            
            # Auto-save if enabled
            if self._config['auto_save']:
                await self._save_profile(self._profiles[profile_id])
            
            self.logger.info(f"Cleared cookies for profile: {profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear cookies for profile {profile_id}: {e}")
            return False
    
    async def _load_profiles(self) -> None:
        """Load profiles from storage."""
        try:
            if not self._storage_path.exists():
                return
            
            for profile_file in self._storage_path.glob("*.json"):
                try:
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        profile_data = json.load(f)
                    
                    profile = BrowserProfile(
                        profile_id=profile_data['profile_id'],
                        profile_type=ProfileType(profile_data['profile_type']),
                        name=profile_data['name'],
                        settings=profile_data['settings'],
                        cookies=profile_data['cookies'],
                        extensions=profile_data['extensions'],
                        created_at=profile_data['created_at'],
                        last_used=profile_data.get('last_used')
                    )
                    
                    self._profiles[profile.profile_id] = profile
                    self._profiles_loaded += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to load profile from {profile_file}: {e}")
            
            self.logger.info(f"Loaded {self._profiles_loaded} profiles from storage")
            
        except Exception as e:
            self.logger.error(f"Failed to load profiles: {e}")
    
    async def _save_profile(self, profile: BrowserProfile) -> bool:
        """Save a profile to storage."""
        try:
            profile_file = self._storage_path / f"{profile.profile_id}.json"
            
            profile_data = asdict(profile)
            profile_data['profile_type'] = profile.profile_type.value
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save profile {profile.profile_id}: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the profile manager."""
        return {
            "active_profile_id": self._active_profile_id,
            "total_profiles": len(self._profiles),
            "profiles_created": self._profiles_created,
            "profiles_loaded": self._profiles_loaded,
            "profile_switches": self._profile_switches,
            "storage_path": str(self._storage_path),
            "config": self._config,
        }
    
    @property
    def active_profile_id(self) -> Optional[str]:
        """Get the active profile ID."""
        return self._active_profile_id