# DIX VISION CONTAINERIZATION PLAN

## Objective
Create a light and clean main folder by containerizing as much as possible.

## Current State Analysis
- **Root directories**: 60+ directories
- **Root files**: 100+ files
- **Structure**: Highly cluttered with mixed concerns

## Containerization Structure

### Essential Root Files (Keep in Main)
- **Core configs**: .gitignore, .dockerignore, .env*, docker-compose.yml, Dockerfile, compose.yaml
- **Entry points**: LAUNCH_DIX_VISION_DESKTOP.py, dix.py
- **Dev configs**: .devin/, .github/, .vscode/
- **Auto PR system**: auto_pr.py, check_pr_status.py, AUTO_GITHUB_PR_README.md

### Container Directory Structure

#### 1. containers/system_core/
Core system modules and cognitive engines
- core/
- system/
- system_engine/
- system_unified/
- system_unified_engine/
- cognitive_os/
- cognitive_control_center/
- indira_cognitive/
- dyon_cognitive/
- governance_unified/
- execution_unified/
- learning_engine/
- evolution_engine/
- intelligence_engine/
- world_model/
- simulation/
- simulation_engine/
- runtime/
- state/
- trust_root/

#### 2. containers/user_interfaces/
User interfaces and visualization
- dashboard2026/
- dashboard_backend/
- ui/
- desktop_agent/
- sensory/

#### 3. containers/data_layer/
Data management and storage
- data/
- data_sources/
- preservation_layer/
- memory/
- registry/
- trader_modeling/
- trader_ontology/

#### 4. containers/infrastructure/
Infrastructure and deployment
- infrastructure/
- deployment/
- docker/
- security/
- monitoring/
- shared_infrastructure/
- coordination_layer/
- protocols/
- contracts/
- risk/
- windows/

#### 5. containers/adapters_integration/
External integrations and adapters
- adapters/
- alternatives/
- integration/
- interrupt/

#### 6. containers.development/
Development tools and testing
- tests/
- tools/
- scripts/
- tmp/
- backups/
- checkpoints/
- github_debug_repo/

#### 7. containers/documentation/
All documentation
- docs/
- All *.md files from root

#### 8. containers/utilities/
Utility scripts and configurations
- config/
- operator_governance/
- plugin_system/
- Other utility scripts

#### 9. containers/legacy/
Legacy and alternative implementations
- alternatives/ (if not used)
- Other legacy components

## Migration Steps

1. **Create container directory structure**
2. **Move system components** into containers/system_core/
3. **Move user interfaces** into containers/user_interfaces/
4. **Move data layer** into containers/data_layer/
5. **Move infrastructure** into containers/infrastructure/
6. **Move adapters** into containers/adapters_integration/
7. **Move development tools** into containers/development/
8. **Move documentation** into containers/documentation/
9. **Move utilities** into containers/utilities/
10. **Clean root directory**
11. **Update configuration files**
12. **Update import paths**
13. **Test containerized system**
14. **Commit and push to GitHub**

## Expected Result
- **Root directories**: ~5-10 (essential only)
- **Root files**: ~15-20 (essential only)
- **Clean structure**: Logical organization
- **Maintained functionality**: All imports and paths updated