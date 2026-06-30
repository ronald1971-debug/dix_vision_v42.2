# DIX VISION Bootstrap Guide

## Overview

The DIX VISION system now uses a **unified bootstrap system** (`bootstrap.py`) that consolidates all entry points into a single, orchestrator-based system. This replaces the previous scattered launch scripts and provides a consistent way to launch the system across all deployment scenarios.

## Quick Start

### Basic Usage
```bash
python bootstrap.py [command] [options]
```

### Common Commands

#### Launch Desktop AgentOS
```bash
python bootstrap.py desktop
```
Launches the Desktop AgentOS with Tauri frontend, including DYON and INDIRA cognitive agents.

#### Launch Dashboard
```bash
python bootstrap.py dashboard
```
Launches the React dashboard with Python backend.

#### Launch Backend Only
```bash
python bootstrap.py backend
```
Launches only the Python backend server.

#### Launch Docker Stack
```bash
python bootstrap.py docker
```
Launches the full Docker stack with all services.

#### Launch Development Environment
```bash
python bootstrap.py dev
```
Launches the development environment with hot reloading.

#### Launch Portable Mode
```bash
python bootstrap.py portable
```
Launches the portable .exe mode with per-user data directory.

## Command Options

### Global Options
- `--host HOST` - Bind host (default: 127.0.0.1)
- `--port PORT` - Port number (mode-specific defaults)
- `--mode MODE` - Operation mode (desktop/production/dev)
- `--no-browser` - Don't auto-open browser
- `--stop` - Stop running services (for docker command)
- `--help` - Show help message

### Example Usage

#### Custom Port
```bash
python bootstrap.py backend --port 9000
python bootstrap.py desktop --port 8765
```

#### Different Host
```bash
python bootstrap.py backend --host 0.0.0.0
python bootstrap.py dashboard --host 192.168.1.100
```

#### No Browser
```bash
python bootstrap.py desktop --no-browser
python bootstrap.py dashboard --no-browser
```

#### Docker Management
```bash
# Start Docker stack
python bootstrap.py docker

# Stop Docker stack
python bootstrap.py docker --stop
```

## Migration from Old Entry Points

### Old → New Mapping

| Old Entry Point | New Command | Notes |
|----------------|-------------|-------|
| `LAUNCH_DIX_VISION_DESKTOP.py` | `python bootstrap.py desktop` | Direct replacement |
| `start_dix_vision.bat` | `python bootstrap.py docker` | Wrapper calls bootstrap |
| `launch_real_backend.bat` | `python bootstrap.py backend` | Direct replacement |
| `containers/user_interfaces/dashboard2026/launcher.bat` | `python bootstrap.py dashboard` | Wrapper calls bootstrap |
| `containers/infrastructure/windows/launcher_entry.py` | `python bootstrap.py portable` | Direct replacement |

### Backward Compatibility

Old scripts have been updated to call the new bootstrap system, so existing workflows will continue to work. However, users are encouraged to migrate to the new unified commands.

## Configuration

### Default Ports
- **Desktop**: 8765
- **Dashboard**: 8080
- **Backend**: 8000
- **Docker Backend**: 8080
- **Docker Dashboard**: 5173

### Data Directory (Portable Mode)
The portable mode uses a per-user data directory:
- **Windows**: `%LOCALAPPDATA%\DIX VISION\`
- **Linux/Mac**: `~/.local/share/DIX VISION/`

### Environment Variables
The bootstrap system sets the following environment variables:
- `DIX_MODE` - Operation mode
- `DIX_BIND_HOST` - Bind host
- `DIX_PORT` - Port number
- `DIX_DATA_ROOT` - Data directory root
- `DIX_COCKPIT_TOKEN_FILE` - Authentication token file
- `DIX_PAIRING_DB` - Pairing database path
- `DIX_LEDGER_DB` - Ledger database path
- `DIX_EPISODIC_DB` - Episodic memory database path
- `DIX_WALLET_POLICY_DB` - Wallet policy database path

## Architecture

### Bootstrap System Components

1. **Configuration Manager**: Centralized configuration for all modes
2. **Python Path Setup**: Unified Python path configuration
3. **Process Manager**: Handles process lifecycle and cleanup
4. **Mode-Specific Launchers**: Specialized launchers for each deployment mode
5. **Error Handler**: Graceful error handling and fallbacks

### Mode-Specific Launchers

#### Desktop Launcher
- Initializes Desktop AgentOS runtime
- Launches DYON and INDIRA cognitive agents
- Sets up browser environment bridge
- Opens Tauri frontend

#### Dashboard Launcher
- Starts Python backend server
- Launches React development server
- Opens browser to dashboard
- Handles dependency installation

#### Backend Launcher
- Starts Python backend only
- Supports custom host/port configuration
- Provides health endpoint
- Handles graceful shutdown

#### Docker Launcher
- Checks Docker status
- Starts Docker Compose stack
- Monitors container health
- Opens browser to services
- Handles stack shutdown

#### Development Launcher
- Enables hot reloading
- Starts both backend and dashboard
- Provides development logging
- Supports debugging modes

#### Portable Launcher
- Sets up per-user data directory
- Generates authentication tokens
- Configures local databases
- Provides desktop experience

## Troubleshooting

### Common Issues

#### Bootstrap Not Found
```bash
# Ensure you're in the project root
cd C:\dix_vision_v42.2
python bootstrap.py --help
```

#### Port Already in Use
```bash
# Use a different port
python bootstrap.py backend --port 9000
```

#### Docker Not Running
```bash
# Start Docker Desktop before running
python bootstrap.py docker
```

#### Module Import Errors
```bash
# The bootstrap system automatically sets up Python paths
# If issues persist, check that all containers are present
python bootstrap.py backend --mode dev
```

### Logging

All bootstrap operations are logged to the console. For detailed logging, check:
- **Desktop**: `dix_vision_desktop.log`
- **Portable**: `%LOCALAPPDATA%\DIX VISION\logs\`
- **Docker**: Docker container logs

## Advanced Usage

### Custom Configuration
You can modify the configuration in `bootstrap.py`:

```python
config = {
    "default_mode": "desktop",
    "default_host": "127.0.0.1",
    "ports": {
        "desktop": 8765,
        "dashboard": 8080,
        # Add custom ports
    },
    "paths": {
        # Add custom paths
    },
}
```

### Programmatic Usage
You can also use the bootstrap system programmatically:

```python
from bootstrap import DIXVisionBootstrap
import asyncio

async def main():
    bootstrap = DIXVisionBootstrap()
    args = type('Args', (), {
        'command': 'backend',
        'host': '127.0.0.1',
        'port': 8000,
        'mode': None,
        'no_browser': True,
        'stop': False
    })()
    
    await bootstrap.launch_backend(args)

asyncio.run(main())
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Start DIX VISION
  run: |
    python bootstrap.py docker --no-browser
    
- name: Run Tests
  run: |
    python bootstrap.py backend --port 9000 --no-browser &
    pytest tests/
    
- name: Cleanup
  run: |
    python bootstrap.py docker --stop
```

### Docker Compose Integration
The bootstrap system integrates with existing Docker Compose files:
- `docker-compose.main.yml` - Main stack
- `docker-compose.dev.yml` - Development stack
- `docker-compose.prod.yml` - Production stack

## Security Considerations

### Authentication Tokens
The portable mode generates secure authentication tokens automatically:
- Tokens are stored in per-user data directory
- Tokens are URL-safe and cryptographically random
- Tokens are regenerated if lost or corrupted

### Network Binding
- Default binding is to `127.0.0.1` (localhost only)
- Use `--host 0.0.0.0` for external access (caution recommended)
- Docker mode uses internal networking by default

### Data Isolation
- Portable mode uses per-user data directories
- Docker mode uses container volumes
- Development mode uses project directory

## Performance

### Startup Times
- **Desktop**: ~5-10 seconds (agent initialization)
- **Dashboard**: ~3-5 seconds (backend + React)
- **Backend**: ~2-3 seconds (FastAPI startup)
- **Docker**: ~15-30 seconds (container startup)

### Resource Usage
- **Desktop**: ~500MB RAM (agents + runtime)
- **Dashboard**: ~300MB RAM (backend + dev server)
- **Backend**: ~200MB RAM (FastAPI only)
- **Docker**: ~2GB RAM (full stack)

## Support

### Getting Help
```bash
python bootstrap.py --help
```

### Reporting Issues
When reporting issues, include:
- Bootstrap command used
- Error messages from logs
- System information (OS, Python version)
- Mode-specific configuration

### Documentation
- `BOOTSTRAP_MIGRATION_PLAN.md` - Migration details
- `BOOTSTRAP_GUIDE.md` - This guide
- Project README - General system documentation

## Future Enhancements

Planned improvements to the bootstrap system:
- [ ] Health check integration
- [ ] Automatic dependency management
- [ ] Configuration file support
- [ ] Multi-environment support
- [ ] Metrics and monitoring
- [ ] Plugin system for custom launchers