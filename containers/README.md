# DIX VISION CONTAINER STRUCTURE

## Overview
The DIX VISION system has been containerized to create a light and clean main folder while maintaining logical organization of all components.

## Container Organization

### 📁 containers/system_core/
Core system modules and cognitive engines
- **core/** - Core authority and belief engine
- **system/** - System modules
- **system_engine/** - System engine components
- **system_unified/** - Unified system components
- **system_unified_engine/** - Unified system engine
- **cognitive_os/** - Cognitive operating system
- **cognitive_control_center/** - Cognitive control center
- **indira_cognitive/** - INDIRA cognitive engine (market intelligence)
- **dyon_cognitive/** - DYON cognitive engine (system intelligence)
- **governance_unified/** - Unified governance system
- **execution_unified/** - Unified execution system
- **learning_engine/** - Learning engine
- **evolution_engine/** - Evolution engine
- **intelligence_engine/** - Intelligence engine
- **world_model/** - World model
- **simulation/** - Simulation system
- **simulation_engine/** - Simulation engine
- **runtime/** - Runtime components
- **state/** - State management
- **trust_root/** - Trust root components
- **mind/** - Mind module
- **immutable_core/** - Immutable core components

### 📁 containers/user_interfaces/
User interfaces and visualization
- **dashboard2026/** - Main dashboard (DASHBOARD2026)
- **dashboard_backend/** - Dashboard backend
- **ui/** - User interface components
- **desktop_agent/** - Desktop agent
- **sensory/** - Sensory input components

### 📁 containers/data_layer/
Data management and storage
- **data/** - Data storage (databases, etc.)
- **data_sources/** - External data sources
- **preservation_layer/** - Data preservation
- **registry/** - System registry and configuration
- **trader_modeling/** - Trader modeling components
- **trader_ontology/** - Trader ontology

### 📁 containers/infrastructure/
Infrastructure and deployment
- **shared_infrastructure/** - Shared infrastructure
- **coordination_layer/** - Coordination between components
- **protocols/** - Communication protocols
- **contracts/** - System contracts
- **risk/** - Risk management
- **windows/** - Windows-specific components
- **monitoring/** - Monitoring system (if present)

### 📁 containers/adapters_integration/
External integrations and adapters
- **adapters/** - Integration adapters
- **integration/** - Integration components
- **interrupt/** - Interrupt handling

### 📁 containers/development/
Development tools and testing
- **tests/** - Test files
- **tools/** - Development tools
- **scripts/** - Utility scripts
- **tmp/** - Temporary files (if present)
- **backups/** - Backup files (if present)
- **checkpoints/** - System checkpoints
- **github_debug_repo/** - GitHub debug repository (if present)
- **alternatives/** - Alternative implementations
- **Test results** - Various test result JSON files

### 📁 containers/documentation/
All documentation
- **docs/** - Original documentation folder
- **Project documentation** - All .md files from the project
- **Architecture docs** - System architecture documentation
- **Implementation docs** - Implementation status and reports
- **Phase completion docs** - Phase completion reports

### 📁 containers/utilities/
Utility scripts and configurations
- **config/** - Configuration files
- **Utility scripts** - Various utility Python scripts
- **Test utilities** - Test-related utilities
- **Batch files** - Windows batch files
- **Archive requirements** - Archival dependency requirements

## Root Directory Structure

The root directory now contains only essential files:

### Configuration Files
- **.dockerignore** - Docker ignore rules
- **.env** - Environment variables
- **.env.dockerless** - Dockerless environment
- **.env.example** - Example environment configuration
- **.env.template** - Environment template
- **.gitignore** - Git ignore rules

### Launch Files
- **LAUNCH_DIX_VISION_DESKTOP.py** - Desktop launcher
- **dix.py** - Main DIX runner
- **auto_pr.py** - Auto GitHub PR system
- **check_pr_status.py** - PR status checker

### Docker Files
- **Dockerfile** - Docker configuration
- **docker-compose.yml** - Docker Compose configuration
- **compose.yaml** - Compose orchestration

### Other Essential Files
- **requirements.txt** - Python dependencies
- **VERSION** - System version

### Development Directories
- **.devin/** - Devin configuration
- **.github/** - GitHub workflows
- **.vscode/** - VSCode configuration
- **containers/** - All containerized components

## Benefits

1. **Clean Root Folder**: Only essential files in the root directory
2. **Logical Organization**: Components grouped by function
3. **Easier Navigation**: Clear separation of concerns
4. **Better Maintenance**: Easier to find and update components
5. **Scalability**: Easy to add new containers as needed
6. **Git Performance**: Cleaner git history and status

## Migration Notes

- All import paths may need to be updated to reflect new container structure
- Docker compose files may need path updates
- Integration scripts should reference new container paths
- Documentation should reference new container organization

## Auto PR Integration

The auto PR system (`auto_pr.py`) automatically creates pull requests every 30 files changed, making it easy to track and review containerization progress.

## Next Steps

1. Update import paths in all Python files
2. Update Docker compose configurations
3. Update any hardcoded paths in scripts
4. Test the containerized system
5. Update documentation to reflect new structure