"""
Plugin Registry - Dynamic plugin loading and management
"""

import importlib
import inspect
import logging
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from dataclasses import dataclass


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    module_path: str


class Plugin:
    """Base class for plugins."""
    
    def __init__(self, runtime):
        """
        Initialize plugin.
        
        Args:
            runtime: AgentRuntime instance
        """
        self.runtime = runtime
        self.enabled = True
        
    async def initialize(self) -> None:
        """Initialize the plugin."""
        pass
        
    async def start(self) -> None:
        """Start the plugin."""
        pass
        
    async def stop(self) -> None:
        """Stop the plugin."""
        pass
        
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        raise NotImplementedError
        

class PluginRegistry:
    """
    Registry for managing plugins.
    
    Handles plugin discovery, loading, initialization,
    and lifecycle management with dependency resolution.
    """
    
    def __init__(self, runtime):
        """
        Initialize plugin registry.
        
        Args:
            runtime: AgentRuntime instance
        """
        self.runtime = runtime
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        
        self.logger = logging.getLogger(__name__)
        
    def discover_plugins(self, plugin_dir: str) -> List[str]:
        """
        Discover plugins in a directory.
        
        Args:
            plugin_dir: Directory to search for plugins
            
        Returns:
            List of plugin module names
        """
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            self.logger.warning(f"Plugin directory not found: {plugin_dir}")
            return []
            
        plugins = []
        
        for item in plugin_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                plugins.append(item.name)
            elif item.suffix == ".py" and item.name != "__init__.py":
                plugins.append(item.stem)
                
        self.logger.info(f"Discovered plugins: {plugins}")
        return plugins
        
    async def load_plugin(
        self,
        module_name: str,
        plugin_path: Optional[str] = None,
    ) -> Optional[Plugin]:
        """
        Load a plugin module.
        
        Args:
            module_name: Module name to load
            plugin_path: Optional custom path
            
        Returns:
            Plugin instance or None
        """
        try:
            if plugin_path:
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    plugin_path,
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                module = importlib.import_module(module_name)
                
            # Find Plugin subclasses
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Plugin)
                    and obj != Plugin
                ):
                    plugin_classes.append(obj)
                    
            if not plugin_classes:
                self.logger.error(f"No Plugin class found in {module_name}")
                return None
                
            # Instantiate the first plugin class found
            plugin_class = plugin_classes[0]
            plugin = plugin_class(self.runtime)
            
            # Get metadata
            try:
                metadata = plugin.metadata
                self.plugin_metadata[metadata.name] = metadata
            except NotImplementedError:
                self.logger.warning(f"Plugin {module_name} missing metadata")
                
            self.plugins[module_name] = plugin
            self.logger.info(f"Loaded plugin: {module_name}")
            
            return plugin
            
        except Exception as e:
            self.logger.error(f"Error loading plugin {module_name}: {e}")
            return None
            
    async def initialize_plugin(self, plugin_name: str) -> None:
        """
        Initialize a loaded plugin.
        
        Args:
            plugin_name: Plugin name
        """
        if plugin_name in self.plugins:
            try:
                await self.plugins[plugin_name].initialize()
                self.logger.info(f"Initialized plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Error initializing plugin {plugin_name}: {e}")
                
    async def start_plugin(self, plugin_name: str) -> None:
        """
        Start a plugin.
        
        Args:
            plugin_name: Plugin name
        """
        if plugin_name in self.plugins:
            try:
                await self.plugins[plugin_name].start()
                self.logger.info(f"Started plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Error starting plugin {plugin_name}: {e}")
                
    async def stop_plugin(self, plugin_name: str) -> None:
        """
        Stop a plugin.
        
        Args:
            plugin_name: Plugin name
        """
        if plugin_name in self.plugins:
            try:
                await self.plugins[plugin_name].stop()
                self.logger.info(f"Stopped plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Error stopping plugin {plugin_name}: {e}")
                
    async def unload_plugin(self, plugin_name: str) -> None:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Plugin name
        """
        if plugin_name in self.plugins:
            try:
                await self.stop_plugin(plugin_name)
                del self.plugins[plugin_name]
                if plugin_name in self.plugin_metadata:
                    del self.plugin_metadata[plugin_name]
                self.logger.info(f"Unloaded plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Error unloading plugin {plugin_name}: {e}")
                
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a loaded plugin.
        
        Args:
            plugin_name: Plugin name
            
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_name)
        
    def get_all_plugins(self) -> Dict[str, Plugin]:
        """
        Get all loaded plugins.
        
        Returns:
            Dictionary of plugins
        """
        return self.plugins.copy()
        
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """
        Get plugin metadata.
        
        Args:
            plugin_name: Plugin name
            
        Returns:
            Plugin metadata or None
        """
        return self.plugin_metadata.get(plugin_name)
        
    async def resolve_dependencies(self, plugin_name: str) -> bool:
        """
        Resolve plugin dependencies.
        
        Args:
            plugin_name: Plugin name
            
        Returns:
            True if dependencies are satisfied, False otherwise
        """
        metadata = self.plugin_metadata.get(plugin_name)
        if not metadata:
            return True
            
        for dep in metadata.dependencies:
            if dep not in self.plugins:
                self.logger.error(f"Missing dependency: {dep}")
                return False
                
        return True
