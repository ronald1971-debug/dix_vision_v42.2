# DIX VISION Bootstrap Migration Plan

## Overview
This document outlines the migration from scattered entry points to a unified bootstrap system as specified in P0 #1.

## Current State (Multiple Entry Points)

### Python Entry Points
1. **LAUNCH_DIX_VISION_DESKTOP.py** - Desktop AgentOS launcher
2. **containers/infrastructure/windows/launcher_entry.py** - PyInstaller entry point
3. **containers/user_interfaces/ui/server.py** - FastAPI backend server
4. **start_dix_vision.bat** - Docker unified startup
5. **launch_real_backend.bat** - Backend launcher
6. **start_complete_stack.bat** - Complete stack launcher
7. **start_dashboard_stack.bat** - Dashboard launcher
8. **start_system.bat** - System launcher
9. **containers/user_interfaces/dashboard2026/launcher.bat** - Dashboard launcher

### Issues with Current State
- **Fragmented entry points**: 9+ different ways to launch the system
- **Inconsistent configuration**: Each entry point has its own config logic
- **No central orchestration**: Each script manages its own dependencies
- **Hard to maintain**: Changes require updating multiple files
- **Confusing for users**: Multiple launch methods with unclear differences

## Target State (Unified Bootstrap)

### Single Entry Point
**bootstrap.py** - Unified bootstrap system with the following capabilities:

```bash
python bootstrap.py [command] [options]
```

### Commands
- `desktop` - Launch Desktop AgentOS with Tauri frontend
- `dashboard` - Launch React dashboard with Python backend  
- `backend` - Launch Python backend only
- `docker` - Launch full Docker stack
- `dev` - Launch development environment
- `portable` - Launch portable .exe mode

### Unified Features
- **Centralized configuration**: Single config system for all modes
- **Unified Python path setup**: Consistent across all containers
- **Graceful fallbacks**: Missing components handled elegantly
- **Process management**: Clean startup/shutdown of all processes
- **Cross-platform**: Works on Windows, Linux, macOS

## Migration Strategy

### Phase 1: Validation (Current)
- [x] Create unified bootstrap.py
- [ ] Test each command mode
- [ ] Verify compatibility with existing scripts
- [ ] Document migration path

### Phase 2: Integration
- [ ] Update existing scripts to call bootstrap.py
- [ ] Create wrapper scripts for backward compatibility
- [ ] Update documentation to reference bootstrap.py
- [ ] Update CI/CD pipelines

### Phase 3: Cleanup
- [ ] Deprecate old entry points (with warnings)
- [ ] Remove duplicate launch scripts
- [ ] Remove hardcoded paths from old scripts
- [ ] Consolidate configuration files

### Phase 4: Completion
- [ ] Remove old entry points
- [ ] Final documentation updates
- [ ] Archive old launch scripts

## Configuration Centralization

### Current Config Locations
- Environment variables in multiple scripts
- Hardcoded paths in launch scripts
- Duplicate port configurations
- Scattered Python path setups

### Target Config Structure
```python
# bootstrap.py config
config = {
    "default_mode": "desktop",
    "default_host": "127.0.0.1",
    "ports": {
        "desktop": 8765,
        "dashboard": 8080,
        "backend": 8000,
        "docker_backend": 8080,
        "docker_dashboard": 5173,
    },
    "paths": {
        "desktop_app": project_root / "dix_desktop",
        "dashboard": project_root / "containers/user_interfaces/dashboard2026",
        "backend": project_root / "containers/user_interfaces/ui",
        "docker_compose": project_root / "docker-compose.main.yml",
    },
}
```

## Backward Compatibility

### Wrapper Scripts
Create wrapper scripts that call bootstrap.py:
```batch
@echo off
REM start_dix_vision.bat - Wrapper for backward compatibility
python bootstrap.py docker %*
```

### Deprecation Warnings
Add warnings to old entry points:
```python
import warnings
warnings.warn("This entry point is deprecated. Use 'python bootstrap.py' instead", DeprecationWarning)
```

## Testing Plan

### Test Cases
1. **Desktop Mode**: Verify Desktop AgentOS launches correctly
2. **Dashboard Mode**: Verify React dashboard + backend start
3. **Backend Mode**: Verify backend-only launch
4. **Docker Mode**: Verify Docker stack starts correctly
5. **Dev Mode**: Verify development environment setup
6. **Portable Mode**: Verify portable .exe behavior
7. **Error Handling**: Verify graceful handling of missing components
8. **Cleanup**: Verify proper process cleanup on exit

### Validation Commands
```bash
# Test each mode
python bootstrap.py desktop
python bootstrap.py dashboard
python bootstrap.py backend
python bootstrap.py docker
python bootstrap.py dev
python bootstrap.py portable

# Test with options
python bootstrap.py desktop --port 9000
python bootstrap.py dashboard --no-browser
python bootstrap.py backend --host 0.0.0.0
```

## Benefits

### Technical Benefits
- **Single source of truth**: One bootstrap system to maintain
- **Consistent behavior**: All modes use same initialization logic
- **Easier debugging**: Centralized logging and error handling
- **Better testing**: Single entry point to test all scenarios
- **Simpler CI/CD**: One command to test all launch modes

### User Benefits
- **Clearer documentation**: One way to launch the system
- **Consistent experience**: Same flags and options across modes
- **Better error messages**: Centralized error handling
- **Easier troubleshooting**: Single place to check logs

## Rollback Plan

If issues arise during migration:
1. Keep old entry points operational during Phase 1-2
2. Revert to old entry points by disabling bootstrap.py wrapper
3. Roll back CI/CD changes to use old entry points
4. Document issues and fix before retrying migration

## Success Criteria

### Technical Criteria
- [ ] All existing launch modes work through bootstrap.py
- [ ] No functionality lost during migration
- [ ] Performance equivalent to current entry points
- [ ] Error handling improved or equivalent
- [ ] All tests pass

### User Criteria
- [ ] Documentation updated and clear
- [ ] Users can launch system with single command
- [ ] Error messages are helpful
- [ ] Backward compatibility maintained during transition

## Timeline

- **Phase 1**: 1-2 days (validation and testing)
- **Phase 2**: 2-3 days (integration and wrappers)
- **Phase 3**: 1-2 days (cleanup and deprecation)
- **Phase 4**: 1 day (final cleanup and documentation)

**Total**: 5-8 days for complete migration

## Next Steps

1. Test bootstrap.py with each command mode
2. Create wrapper scripts for backward compatibility
3. Update documentation
4. Begin Phase 2 integration