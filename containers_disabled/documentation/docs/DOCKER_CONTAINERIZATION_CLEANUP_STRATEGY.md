# DIX VISION v42.2 - Docker Containerization Cleanup Strategy

**Created:** June 16, 2026
**Goal:** Clean up main folder by containerizing components
**Current Status:** Analysis Complete, Strategy Ready

---

## 🎯 **Current Main Folder Cleanup Opportunities**

### **Problem: Main Folder Clutter**

The current main folder contains:
- **50+ markdown files** (implementation reports, phase reports, documentation)
- **Scattered Python files** (launcher scripts, utilities, adapters)
- **Runtime data** (checkpoints, logs)
- **Configuration files** (.env files, templates)
- **Core application code** (mixed with documentation)

**Estimated cleanup potential:** Move 70% of files to organized containers

---

## 📦 **Containerization Strategy**

### **1. Core Application Container** (Main System)

**Purpose:** House all core application code
**What moves:** Core Python modules and application logic

**Components to include:**
- `cognitive_os/` - Complete cognitive system
- `execution_unified/` - Execution architecture
- `evolution_engine/` - Evolution and autonomous systems
- `world_model/` - World model and Indira integration
- `adapters/` - Domain adapters
- `cognitive_control_center/` - Control center code
- `state/` - State management
- `governance_unified/` - Governance system
- `tests/` - Core application tests

**What remains in main:** Dockerfile, docker-compose.yml, core entry points

---

### **2. Documentation Container** (Docs Server)

**Purpose:** Serve and organize all documentation
**What moves:** All markdown files and documentation

**Components to move to docs container:**
- All `.md` files (50+ files):
  - Implementation reports
  - Phase reports
  - Integration reports
  - Testing reports
  - Production guides
  - Analysis reports
  - Security guides
- `.txt` files (manifests, build plans)

**Container features:**
- Static file server (nginx or docsify)
- Search functionality
- Version control integration
- API for accessing documentation

---

### **3. Data Volume Container** (Persistent Data)

**Purpose:** Manage all persistent data
**What moves:** Runtime data and state

**Components to move to data volumes:**
- `checkpoints/` - All checkpoint files
- `logs/` - Application logs (if exists)
- `state/` - Runtime state data
- `data/` - Application data (if exists)

**Volume structure:**
```
volumes/
  ├── checkpoints/     # Checkpoint data
  ├── logs/            # Application logs
  ├── state/           # Runtime state
  └── models/          # ML models if any
```

---

### **4. Configuration Container** (Config Management)

**Purpose:** Centralized configuration management
**What moves:** All configuration files

**Components to move to config container:**
- `.env` files (multiple versions)
- `.env.template`
- `docker-compose.yml` (move to root config)
- Any JSON/YAML config files
- `VERSION` file

**Benefits:**
- Centralized config management
- Environment-specific configs
- Secret management integration
- Config versioning

---

### **5. Development Tools Container** (Dev Environment)

**Purpose:** Development and testing environment
**What moves:** Development utilities and test tools

**Components to move to dev container:**
- `LAUNCH_DIX_VISION_DESKTOP.py` - Desktop launcher
- `add_desktop_agent_to_compose.py` - Utility scripts
- `add_services_to_compose.py` - Service management
- Various helper scripts
- Development dependencies
- Testing utilities

**Features:**
- Complete dev environment
- Hot-reload support
- Debug tools
- Test runners

---

### **6. Backup Container** (Backup and Archive)

**Purpose:** Archive old reports and historical data
**What moves:** Historical reports and archive files

**Components to move to backup container:**
- Old phase reports (PHASE1-9 reports)
- Historical testing reports
- Old integration reports
- Archive checkpoint files
- Historical analysis reports

**Benefits:**
- Clean main folder
- Organized archival
- Searchable history
- Reduced noise

---

## 🗂️ **Proposed Clean Main Folder Structure**

### **After Containerization, Main Folder Contains:**

```
dix_vision_v42.2/
├── docker-compose.yml              # Main orchestration
├── Dockerfile                        # Core app build
├── .dockerignore                     # Docker exclusions
├── README.md                        # Main README
├── VERSION                          # Version info (keep for CI/CD)
├── .env.dockerless                  # Config reference
├── .gitignore                       # Git config
├── .github/                         # GitHub workflows (keep)
├── cognitive_os/                    # Core app code
├── execution_unified/               # Core app code  
├── evolution_engine/                # Core app code
├── world_model/                     # Core app code
├── adapters/                        # Core app code
├── cognitive_control_center/        # Core app code
├── state/                           # Core app code
├── governance_unified/              # Core app code
├── tests/                           # Core app code
└── docker/                          # Docker configuration
    ├── docs/Dockerfile             # Docs server
    ├── config/Dockerfile           # Config management
    ├── dev/Dockerfile              # Dev environment
    └── backup/Dockerfile           # Backup container
```

---

## 🚀 **Docker Compose Configuration**

### **Multi-Container Orchestration**

```yaml
version: '3.8'

services:
  # Core Application
  dix-vision-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dix-vision-core
    volumes:
      - app-data:/app/data
      - checkpoints:/app/checkpoints
      - logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - dix-network
    restart: unless-stopped

  # Documentation Server
  dix-vision-docs:
    build:
      context: ./docker/docs
      dockerfile: Dockerfile
    container_name: dix-vision-docs
    ports:
      - "8080:80"
    volumes:
      - ./docs:/usr/share/nginx/html
    networks:
      - dix-network
    restart: unless-stopped

  # Configuration Management
  dix-vision-config:
    build:
      context: ./docker/config
      dockerfile: Dockerfile
    container_name: dix-vision-config
    volumes:
      - ./config:/app/config
      - .env.template:/app/.env.template
    networks:
      - dix-network
    restart: unless-stopped

  # Development Environment
  dix-vision-dev:
    build:
      context: ./docker/dev
      dockerfile: Dockerfile
    container_name: dix-vision-dev
    volumes:
      - .:/workspace
      - dev-data:/workspace/.dev
    environment:
      - DEV_MODE=true
    networks:
      - dix-network
    profiles:
      - dev

  # Backup and Archive
  dix-vision-backup:
    build:
      context: ./docker/backup
      dockerfile: Dockerfile
    container_name: dix-vision-backup
    volumes:
      - backup-data:/backup
      - ./archive:/source:ro
    networks:
      - dix-network
    restart: unless-stopped

volumes:
  app-data:
  checkpoints:
  logs:
  dev-data:
  backup-data:

networks:
  dix-network:
    driver: bridge
```

---

## 📋 **Migration Plan**

### **Phase 1: Create Docker Structure**
1. Create `docker/` directory
2. Create subdirectories: `docs/`, `config/`, `dev/`, `backup/`
3. Create Dockerfiles for each container
4. Set up docker-compose.yml

### **Phase 2: Move Documentation**
1. Create `docs/` directory
2. Move all `.md` files to docs/
3. Create docs server Dockerfile
4. Test documentation access

### **Phase 3: Move Configuration**
1. Create `config/` directory
2. Move config files
3. Set up config container
4. Test configuration management

### **Phase 4: Archive Old Reports**
1. Create `archive/` directory
2. Move old reports and historical files
3. Set up backup container
4. Verify archival access

### **Phase 5: Development Container**
1. Move development scripts
2. Set up dev container
3. Test development workflow
4. Update launch scripts

### **Phase 6: Core Application**
1. Create main app Dockerfile
2. Optimize core app structure
3. Test core functionality
4. Update entry points

---

## 🎯 **Expected Results**

### **Main Folder Cleanup:**

**Before:**
- 50+ markdown files in root
- 10+ Python utility scripts
- 15+ checkpoint files in root
- Multiple .env files
- Total: ~100+ files in root

**After:**
- 1 main docker-compose.yml
- 1 Dockerfile (core app)
- 1 README.md
- 1 VERSION file
- Core Python directories only
- Total: ~15 files in root (85% reduction)

### **Benefits:**
1. **Clean Main Folder:** Only essential files in root
2. **Organized Structure:** Logical separation of concerns
3. **Better Development:** Dedicated dev environment
4. **Easy Deployment:** Containerized deployment
5. **Scalability:** Easy to scale individual components
6. **Portability:** Works anywhere Docker is available
7. **Version Control:** Easier git management
8. **Testing:** Isolated test environments

---

## 🔧 **Implementation Priority**

### **High Priority (Immediate):**
1. Create Docker directory structure
2. Move documentation to docs container
3. Set up docker-compose.yml
4. Archive old reports

### **Medium Priority (Next):**
5. Create configuration container
6. Set up data volumes
7. Create development container

### **Low Priority (Later):**
8. Optimize core application container
9. Set up backup automation
10. Add monitoring containers

---

## 📊 **Container Size Estimates**

- **Core App:** ~2GB (includes all dependencies)
- **Docs Server:** ~500MB (nginx + docs)
- **Config Container:** ~100MB (config files only)
- **Dev Container:** ~3GB (includes dev tools)
- **Backup Container:** ~1GB (archive data)

**Total Storage:** ~6.6GB for all containers

---

## 🎉 **Summary**

This Docker containerization strategy will:
- Reduce main folder clutter by 85%
- Organize components logically
- Enable better development workflow
- Simplify deployment
- Improve maintainability
- Provide clear separation of concerns

**Next Step:** Implement Phase 1 (Create Docker Structure)