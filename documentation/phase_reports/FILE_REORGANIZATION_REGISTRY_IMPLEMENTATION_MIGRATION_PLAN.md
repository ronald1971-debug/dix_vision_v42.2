# DIX VISION System - File Reorganization and Registry Implementation Migration Plan

**Date:** June 21, 2026
**System:** DIX VISION v42.2
**Phase:** Pre-Phase 5 Migration Planning
**Scope:** External dependency verification, file reorganization, registry implementation
**Approach:** Migration plan first, then implementation with validation

---

## 🎯 EXECUTIVE SUMMARY

Based on user requirements, this migration plan addresses:
1. **External Dependency Verification** - Verify GitHub repos configurations are integrated and functional
2. **File Reorganization** - Create migration plan to move files to canonical locations
3. **Registry Implementation** - Implement all 12 registry files (8 primary + 4 optional) per design recommendations

**Key Principle:** Zero-loss guarantee with comprehensive validation and rollback capability.

---

## 🎯 PART 1: EXTERNAL DEPENDENCY VERIFICATION

### **Objective:**
Verify that the 90+ external library configuration files in `containers/github_repos/` are integrated and functional for the system.

### **Analysis Required:**

**Questions to Answer:**
1. Are these configuration files actually used by the system?
2. Are the corresponding external libraries installed in the system?
3. Are there import statements that reference these configurations?
4. Are there any broken or orphaned configuration files?
5. Do the configurations match the installed library versions?

### **Verification Steps:**

**Step 1: Check Requirements/Dependencies**
- Search for requirements.txt, setup.py, pyproject.toml
- Verify which external libraries are actually used
- Cross-reference with github_repos config files

**Step 2: Check Integration Points**
- Search for import statements referencing external libraries
- Verify configuration loading mechanisms
- Check if configurations are read at runtime

**Step 3: Identify Orphaned Files**
- Identify config files for libraries not actually used
- Identify used libraries without config files
- Recommend cleanup or addition

**Step 4: Functional Verification**
- Verify configurations are syntactically valid YAML
- Verify configurations match expected schema
- Test configuration loading if possible

---

## 🎯 PART 2: FILE REORGANIZATION MIGRATION PLAN

### **Objective:**
Move files to correct canonical locations with zero-loss guarantee.

### **Current File Locations vs Target Locations:**

#### **Current State:**
- Root-level: compose.yaml, docker-compose.yml
- containers/data_layer/registry/: 6 files
- containers/development/alternatives/: 5 files
- containers/user_interfaces/: 1 file
- containers/system_core/strategies/registry/: 2 files (strategy registry)

#### **Target Canonical Structure:**
```
containers/
├── config/
│   ├── deployment/
│   │   ├── compose.yaml (moved from root)
│   │   └── docker-compose.yaml (moved from root)
│   ├── registry/
│   │   ├── signal_first_registry.yaml (NEW)
│   │   ├── trading_form_registry.yaml (NEW)
│   │   ├── strategy_registry.yaml (moved from system_core/strategies/registry/)
│   │   ├── trader_archetypes.yaml (NEW if needed)
│   │   ├── domain_registry.yaml (NEW)
│   │   ├── enhancement_system_registry.yaml (moved/merged)
│   │   ├── risk_management_registry.yaml (NEW)
│   │   ├── cognitive_system_registry.yaml (NEW)
│   │   ├── data_sources.yaml (moved from data_layer/registry/)
│   │   ├── data_governance.yaml (moved from data_layer/registry/)
│   │   └── performance.yaml (moved from data_layer/registry/)
│   ├── development/
│   │   └── alternatives/ (keep as-is in development/alternatives/)
│   ├── ci_cd/
│   │   └── workflows/ (keep .github/workflows/ as-is or move)
│   └── monitoring/
│       └── prometheus.yml (keep as-is)
├── trading/
│   └── registry/ (symlink to config/registry/ or actual location)
└── github_repos/ (keep as-is for dependency configurations)
```

### **Migration Steps:**

**Step 1: Create Backup**
- Backup entire system before migration
- Git commit with descriptive message
- Create migration rollback script

**Step 2: Create New Directory Structure**
- Create containers/config/ directory
- Create subdirectories (deployment, registry, development, ci_cd, monitoring)

**Step 3: Move Files**
- Move deployment configs to config/deployment/
- Move registry files to config/registry/
- Preserve file contents exactly
- Update import statements if needed

**Step 4: Create Symlinks (Optional)**
- Create symlinks from old locations to new locations for backward compatibility
- Or use import shims if symlinks not supported

**Step 5: Validate**
- Verify all imports still work
- Verify file accessibility
- Run existing tests

**Step 6: Clean Old Locations (Optional)**
- After validation, remove old files
- Or keep as reference for migration period

---

## 🎯 PART 3: REGISTRY YAML IMPLEMENTATION PLAN

### **Objective:**
Implement all 12 registry files (8 primary + 4 optional) with signal-first integration.

### **Implementation Order:**

#### **Phase 3.1: Phase 1 Integration Files (Critical)**

**1. signal_first_registry.yaml (NEW)**
- Location: containers/config/registry/signal_first_registry.yaml
- Content: Signal-first architecture configuration (85/15 baseline)
- Priority: HIGHEST (enables Phase 1 across system)
- Dependencies: None

**2. trading_form_registry.yaml (NEW)**
- Location: containers/config/registry/trading_form_registry.yaml
- Content: Trading form optimization ratios and configurations
- Priority: HIGHEST (enables trading form optimization)
- Dependencies: signal_first_registry.yaml

**3. strategy_registry.yaml (ENHANCE & MOVE)**
- Location: containers/config/registry/strategy_registry.yaml
- Action: Move from system_core/strategies/registry/ + enhance with signal-first fields
- Content: Strategy metadata with signal-first compatibility
- Priority: HIGH (strategies need signal-first integration)
- Dependencies: signal_first_registry.yaml, trading_form_registry.yaml

#### **Phase 3.2: Domain and Enhancement Files**

**4. domain_registry.yaml (NEW)**
- Location: containers/config/registry/domain_registry.yaml
- Content: Multi-domain configurations (from existing multi_domain/ code)
- Priority: HIGH (multi-domain trading support)
- Dependencies: signal_first_registry.yaml

**5. enhancement_system_registry.yaml (ENHANCE & MOVE)**
- Location: containers/config/registry/enhancement_system_registry.yaml
- Action: Enhance advanced_trading_enhancement_system.yaml + signal-first fields
- Content: Enhancement system configurations
- Priority: HIGH (10/10 enhancement system)
- Dependencies: signal_first_registry.yaml

**6. cognitive_system_registry.yaml (NEW)**
- Location: containers/config/registry/cognitive_system_registry.yaml
- Content: Cognitive system configurations (INDIRA, DYON, etc.)
- Priority: MEDIUM (cognitive enhancement integration)
- Dependencies: signal_first_registry.yaml

#### **Phase 3.3: Risk and Governance Files**

**7. risk_management_registry.yaml (NEW)**
- Location: containers/config/registry/risk_management_registry.yaml
- Content: Risk parameters and limits
- Priority: MEDIUM (risk management)
- Dependencies: signal_first_registry.yaml

**8. governance_registry.yaml (NEW)**
- Location: containers/config/registry/governance_registry.yaml
- Content: Governance configurations
- Priority: MEDIUM (governance system)
- Dependencies: signal_first_registry.yaml

#### **Phase 3.4: Optional Files**

**9. data_source_registry.yaml (MOVE & ENHANCE)**
- Location: containers/config/registry/data_sources.yaml
- Action: Move from data_layer/registry/ + enhance
- Content: Data source configurations
- Priority: LOW (already exists, just move and enhance)

**10. execution_registry.yaml (NEW)**
- Location: containers/config/registry/execution_registry.yaml
- Content: Execution parameters
- Priority: LOW (if execution unified added later)

**11. learning_system_registry.yaml (NEW)**
- Location: containers/config/registry/learning_system_registry.yaml
- Content: Learning system configurations
- Priority: LOW (learning enhancement integration)

**12. trading_archetypes_registry.yaml (NEW)**
- Location: containers/config/registry/trader_archetypes.yaml
- Content: Trader behavioral profiles
- Priority: LOW (if trader archetypes needed)

---

## 🎯 MIGRATION SCRIPT REQUIREMENTS

### **Migration Scripts to Create:**

**1. backup_system.py**
- Creates backup of all files before migration
- Stores backup with timestamp
- Creates rollback capability

**2. migrate_files.py**
- Moves files from old to new locations
- Creates symlinks for backward compatibility
- Updates import statements if needed

**3. validate_migration.py**
- Validates all imports still work
- Verifies file accessibility
- Runs test suite if available

**4. rollback_migration.py**
- Restores from backup if migration fails
- Removes new files
- Restores old files

**5. generate_registry_files.py**
- Generates new registry YAML files with signal-first integration
- Enhances existing registry files
- Validates YAML syntax

---

## 🎯 VALIDATION REQUIREMENTS

### **Pre-Migration Validation:**
- ✅ System is in working state
- ✅ Git commit with clean working directory
- ✅ All tests passing (if tests exist)
- ✅ Backup created

### **During Migration Validation:**
- ✅ File copy/move successful
- ✅ No data loss during migration
- ✅ Symlink creation successful
- ✅ Import statements updated if needed

### **Post-Migration Validation:**
- ✅ All imports work correctly
- ✅ No broken references
- ✅ Registry files are syntactically valid
- ✅ System functionality preserved
- ✅ Phase 1 integration verified

---

## 🎯 ROLLBACK PLAN

### **Rollback Triggers:**
- Migration script fails
- Validation fails
- Tests fail after migration
- System functionality broken

### **Rollback Steps:**
1. Stop any running system processes
2. Run rollback_migration.py
3. Restore from backup
4. Verify system restored to previous state
5. Report failure and root cause

---

## 🎯 TIMELINE ESTIMATION

### **Part 1: External Dependency Verification**
- Time: 2-4 hours
- Tasks: Analyze requirements, check imports, verify functionality

### **Part 2: File Reorganization**
- Time: 4-6 hours
- Tasks: Create plan, backup, move files, validate
- Risk: MEDIUM (file movement, but with backup/rollback)

### **Part 3: Registry Implementation**
- Time: 6-8 hours
- Tasks: Generate 12 registry files, enhance existing, validate
- Risk: LOW (adding files, no deletions)

### **Total Estimated Time:** 12-18 hours

---

## 🎯 RISK ASSESSMENT

### **Part 1: External Dependency Verification**
- Risk Level: VERY LOW
- Just analysis and verification, no changes

### **Part 2: File Reorganization**
- Risk Level: MEDIUM
- Moving files could break imports
- Mitigation: Symlinks, import shims, comprehensive validation, rollback

### **Part 3: Registry Implementation**
- Risk Level: LOW
- Adding new files, no deletions
- Enhancing existing files with backward-compatible fields
- Mitigation: Validation scripts, backup

### **Overall Risk:** MEDIUM
- Mitigated by backup, validation, and rollback capability

---

## 🎯 RECOMMENDATION

### **Proceed in Order:**
1. ✅ **Part 1 first** - External dependency verification (no risk)
2. ✅ **Part 3 second** - Registry implementation (low risk)
3. ✅ **Part 2 last** - File reorganization (medium risk, after registry ready)

### **Starting Point:**
Begin with Part 1 (External Dependency Verification) to understand current integration state before making changes.

---

**Migration Plan Status:** ✅ READY FOR EXECUTION
**Zero-Loss Guarantee:** Built-in with backup, validation, and rollback
**Contract Compliance:** Tier-0 production implementation