# Configuration System Centralization Plan

## Overview
This document outlines the consolidation of the fragmented configuration system as specified in P0 #3.

## Current State (Fragmented Configuration)

### Existing Config Systems
1. **containers/system_core/system/config.py** - Basic config with dot-path access
2. **containers/system_core/system_unified/config.py** - System config with JSON file loading  
3. **containers/system_core/system_engine/config.py** - Advanced pydantic-settings based config with precedence
4. **Bootstrap configuration** - Hardcoded config in bootstrap.py
5. **Environment variables** - Scattered across multiple files
6. **YAML configs** - Various registry/engine YAML files
7. **.env files** - Multiple .env files across containers

### Configuration Distribution
- **2,211+ files** contain config/settings references
- **Multiple config managers** across different containers
- **Inconsistent precedence** rules between systems
- **No central validation** of configuration values
- **Scattered defaults** across multiple files
- **No audit trail** for configuration changes

### Issues with Current State
- **Fragmented configuration**: 3+ different config systems
- **Inconsistent access patterns**: Different APIs across containers
- **No single source of truth**: Multiple config files with overlapping keys
- **Hard to debug**: No unified view of active configuration
- **Security risks**: Inconsistent handling of sensitive values
- **Maintenance overhead**: Changes require updating multiple files

## Target State (Unified Configuration System)

### Central Configuration Manager
**config_manager.py** - Single source of truth for all configuration

```python
class UnifiedConfigManager:
    """Centralized configuration management for DIX VISION system"""
    
    def __init__(self):
        self.entries = {}
        self.sources = {}
        self.validators = {}
        self.cache = {}
        
    def load_config(self, config_path: str = None)
    def get(self, key: str, default: Any = None) -> Any
    def set(self, key: str, value: Any, source: str = None)
    def validate(self, key: str, value: Any) -> bool
    def get_source(self, key: str) -> str
    def get_all(self) -> dict[str, Any]
    def reload(self)
    def export(self, format: str = "json") -> str
```

### Configuration Precedence Chain
1. **Environment variables** (highest precedence)
2. **Command-line arguments**
3. **User config file** (~/.dix_vision/config.json)
4. **Project config file** (config/system_config.json)
5. **Registry YAML files** (registry/*.yaml)
6. **Defaults** (lowest precedence)

### Configuration Schema
```yaml
# config/system_config.yaml
system:
  mode: "development"  # development, production, desktop, portable
  log_level: "INFO"
  max_workers: 4
  
network:
  host: "127.0.0.1"
  ports:
    desktop: 8765
    dashboard: 8080
    backend: 8000
    
memory:
  warning_threshold: 70  # percent
  critical_threshold: 85  # percent
  process_limit: 1024  # MB
  
paths:
  data_root: "~/.local/share/dix_vision"
  logs: "~/.local/share/dix_vision/logs"
  cache: "~/.cache/dix_vision"
  
features:
  enable_metrics: true
  enable_monitoring: true
  enable_telemetry: false
```

## Migration Strategy

### Phase 1: Analysis (Current)
- [x] Identify all config systems
- [ ] Document current config patterns
- [ ] Map configuration dependencies
- [ ] Identify configuration conflicts

### Phase 2: Unification
- [ ] Create unified config manager
- [ ] Implement precedence chain
- [ ] Add validation system
- [ ] Create configuration schema

### Phase 3: Integration
- [ ] Update bootstrap to use unified config
- [ ] Update containers to use unified config
- [ ] Remove old config systems
- [ ] Add configuration migration tool

### Phase 4: Cleanup
- [ ] Remove duplicate config files
- [ ] Update documentation
- [ ] Archive removed code

## Unified Config Manager Design

### Core Components

#### 1. Configuration Source Chain
```python
class ConfigSourceChain:
    """Manages configuration source precedence"""
    
    def __init__(self):
        self.sources = [
            EnvironmentSource(),
            CommandLineSource(),
            UserConfigSource(),
            ProjectConfigSource(),
            RegistrySource(),
            DefaultSource()
        ]
        
    def load(self) -> dict[str, Any]
    def get_precedence(self, key: str) -> ConfigSource
    def merge(self) -> dict[str, Any]
```

#### 2. Configuration Validator
```python
class ConfigValidator:
    """Validates configuration values"""
    
    def __init__(self):
        self.schemas = {}
        self.validators = {}
        
    def register_schema(self, key: str, schema: dict)
    def validate(self, key: str, value: Any) -> ValidationResult
    def validate_all(self, config: dict[str, Any]) -> ValidationResult
```

#### 3. Configuration Cache
```python
class ConfigCache:
    """Caches configuration values for performance"""
    
    def __init__(self):
        self.cache = {}
        self.ttl = {}
        
    def get(self, key: str) -> Any
    def set(self, key: str, value: Any, ttl: int = None)
    def invalidate(self, key: str = None)
    def clear(self)
```

#### 4. Configuration Auditor
```python
class ConfigAuditor:
    """Audits configuration changes and access"""
    
    def __init__(self):
        self.log = []
        self.watchers = {}
        
    def log_access(self, key: str, source: str)
    def log_change(self, key: str, old_value: Any, new_value: Any)
    def get_audit_log(self) -> list[dict]
    def register_watcher(self, key: str, callback: Callable)
```

### Configuration Sources

#### Environment Source
```python
class EnvironmentSource(ConfigSource):
    """Loads configuration from environment variables"""
    
    def __init__(self, prefix: str = "DIX_"):
        self.prefix = prefix
        
    def load(self) -> dict[str, Any]
    def get_precedence(self) -> int
```

#### YAML File Source
```python
class YAMLFileSource(ConfigSource):
    """Loads configuration from YAML files"""
    
    def __init__(self, path: str):
        self.path = path
        
    def load(self) -> dict[str, Any]
    def get_precedence(self) -> int
```

#### Registry Source
```python
class RegistrySource(ConfigSource):
    """Loads configuration from registry YAML files"""
    
    def __init__(self, registry_path: str = "registry"):
        self.registry_path = registry_path
        
    def load(self) -> dict[str, Any]
    def get_precedence(self) -> int
```

## Integration Points

### Bootstrap Integration
```python
# bootstrap.py
from config_manager import UnifiedConfigManager

config = UnifiedConfigManager()
config.load_config()

# Use config instead of hardcoded values
port = config.get("network.ports.desktop", 8765)
host = config.get("network.host", "127.0.0.1")
```

### Container Integration
```python
# containers/system_core/system/config.py
from config_manager import get_config

def get_config_value(key: str, default: Any = None) -> Any:
    """Backward-compatible wrapper"""
    return get_config().get(key, default)
```

### Legacy Integration
```python
# Backward compatibility wrappers
def get_config():
    """Legacy wrapper for existing code"""
    return UnifiedConfigManager.get_instance()

def get(key: str, default: Any = None) -> Any:
    """Legacy wrapper for existing code"""
    return get_config().get(key, default)
```

## Configuration Schema

### System Configuration
```yaml
system:
  mode: str  # development, production, desktop, portable
  log_level: str  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  max_workers: int  # Number of worker threads
  timeout_seconds: int  # Default timeout for operations
```

### Network Configuration
```yaml
network:
  host: str  # Bind host
  ports:
    desktop: int  # Desktop AgentOS port
    dashboard: int  # Dashboard port
    backend: int  # Backend port
    docker_backend: int  # Docker backend port
    docker_dashboard: int  # Docker dashboard port
```

### Memory Configuration
```yaml
memory:
  warning_threshold: int  # Memory warning threshold (%)
  critical_threshold: int  # Memory critical threshold (%)
  process_limit: int  # Process memory limit (MB)
  enable_monitoring: bool  # Enable memory monitoring
```

### Path Configuration
```yaml
paths:
  data_root: str  # Data directory root
  logs: str  # Logs directory
  cache: str  # Cache directory
  config: str  # Configuration directory
```

### Feature Configuration
```yaml
features:
  enable_metrics: bool  # Enable metrics collection
  enable_monitoring: bool  # Enable system monitoring
  enable_telemetry: bool  # Enable telemetry
  enable_debug_mode: bool  # Enable debug features
```

## File Consolidation Map

### Files to Enhance
- **containers/system_core/system_engine/config.py** → Use as base for unified system
- **containers/system_core/system/config.py** → Convert to wrapper
- **containers/system_core/system_unified/config.py** → Convert to wrapper

### Files to Create
- **config_manager.py** - Main unified config manager
- **config/system_config.yaml** - Main configuration file
- **config/defaults.yaml** - Default values
- **config/schema.yaml** - Configuration schema

### Files to Remove
- Duplicate config files in development alternatives
- Legacy config files in system_core
- Hardcoded config values in bootstrap.py

## Testing Plan

### Unit Tests
- [ ] Config source chain precedence
- [ ] Configuration validation
- [ ] Configuration caching
- [ ] Configuration auditing

### Integration Tests
- [ ] Bootstrap integration
- [ ] Container integration
- [ ] Legacy compatibility
- [ ] Configuration reloading

### Performance Tests
- [ ] Config loading performance
- [ ] Cache effectiveness
- [ ] Memory overhead
- [ ] Concurrent access

## Benefits

### Technical Benefits
- **Single source of truth**: One configuration system
- **Consistent access patterns**: Same API across all components
- **Centralized validation**: All config values validated consistently
- **Audit trail**: Full history of configuration changes
- **Better debugging**: Unified view of active configuration

### Operational Benefits
- **Easier configuration**: Single file to edit
- **Better security**: Consistent handling of sensitive values
- **Improved reliability**: Validation prevents invalid configs
- **Simpler deployment**: One config file per environment
- **Better documentation**: Centralized config documentation

## Migration Path

### Step 1: Create Unified Manager
- Implement core config manager
- Implement config source chain
- Implement validation system
- Implement auditing system

### Step 2: Create Configuration Files
- Create config/system_config.yaml
- Create config/defaults.yaml
- Create config/schema.yaml
- Migrate existing config values

### Step 3: Integrate with Bootstrap
- Update bootstrap.py to use unified config
- Remove hardcoded config values
- Add config validation on startup
- Add config file watching

### Step 4: Update Containers
- Update system_core config to use wrapper
- Update development alternatives to use wrapper
- Remove duplicate config implementations
- Update imports and references

### Step 5: Remove Old Config
- Remove old config files
- Remove duplicate config implementations
- Update documentation
- Archive removed code

## Rollback Plan

If issues arise during migration:
1. Keep old config files during Phase 1-2
2. Revert to old config by disabling unified manager
3. Restore duplicate config files if needed
4. Document issues and fix before retrying migration

## Success Criteria

### Technical Criteria
- [ ] All configuration uses unified system
- [ ] No configuration functionality lost
- [ ] Configuration loading is fast
- [ ] Validation is comprehensive
- [ ] Audit trail is complete

### Operational Criteria
- [ ] Configuration is easier to manage
- [ ] Security is improved or equivalent
- [ ] Debugging is simplified
- [ ] Performance is maintained
- [ ] Backward compatibility is preserved

## Timeline

- **Phase 1**: 2-3 days (analysis and documentation)
- **Phase 2**: 3-4 days (unification and implementation)
- **Phase 3**: 3-4 days (integration and testing)
- **Phase 4**: 1-2 days (cleanup and documentation)

**Total**: 9-13 days for complete config centralization

## Next Steps

1. Complete analysis of current config systems
2. Design unified config manager architecture
3. Begin implementation of core components
4. Create configuration schema and files
5. Integrate with bootstrap system