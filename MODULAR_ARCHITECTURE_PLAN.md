# DIX VISION Modular Architecture Plan

## Overview
Refactoring the DIX VISION monorepo into a strict, modular architecture using Turborepo with team-based ownership.

## Architecture Principles

### 1. Clear Module Boundaries
- **Apps**: Complete, deployable applications
- **Packages**: Reusable libraries with strict API boundaries
- **Infrastructure**: CI/CD, deployment, and tooling
- **No circular dependencies** enforced by Turborepo

### 2. Ownership Model
Each module has designated ownership:
- **Cognitive Team**: `cognitive-core`, `indira`, `dyon`
- **Governance Team**: `governance-core`, `risk-engine`, `compliance`
- **Execution Team**: `execution-engine`, `environment-bridge`
- **Platform Team**: `desktop`, `dashboard2026`, `observability`
- **Infrastructure Team**: All CI/CD and deployment

### 3. Dependency Rules
```
# STRICT HIERARCHY (no upward dependencies allowed)

apps/                    # Deployable applications
├── desktop/            # Can depend on any package
├── dashboard2026/      # Can depend on any package
└── agent-runtime/      # Can depend on any package

packages/
├── indira/             # Market intelligence (execution-adjacent)
│   └── depends: cognitive-core, governance-core, execution-engine
├── dyon/               # System monitoring (sensor only)
│   └── depends: cognitive-core, observability
├── execution-engine/   # Execution adapters
│   └── depends: governance-core, shared-types
├── cognitive-core/     # Core cognitive abstractions
│   └── depends: shared-types, shared-config
├── governance-core/    # Governance policies (no downward deps)
│   └── depends: shared-types, shared-config
├── vision-system/      # Visual observation
│   └── depends: cognitive-core, shared-types
├── memory-system/      # Agent memory & RAG
│   └── depends: shared-types, observability
├── skill-framework/    # Skill registry & execution
│   └── depends: cognitive-core, governance-core
└── shared-*            # Foundation (no dependencies on other packages)
```

### 4. Communication Patterns
- **Event-driven**: Cross-module communication via events only
- **API boundaries**: Well-defined interfaces, no direct internal access
- **Governance gating**: All execution decisions pre-filtered through governance

## Migration Strategy

### Phase 1: Foundation (Current)
- ✅ Turborepo infrastructure setup
- ⏳ Create module boundary definitions
- ⏳ Set up ownership documentation

### Phase 2: Core Packages
- Migrate `shared-types` (Python + TypeScript type definitions)
- Migrate `shared-config` (Common configurations)
- Migrate `governance-core` (Governance policies & constraints)

### Phase 3: Domain Packages
- Migrate `cognitive-core` (Core cognitive abstractions)
- Migrate `execution-engine` (Execution adapters)
- Migrate `observability` (Telemetry & monitoring)

### Phase 4: Agent Packages
- Migrate `indira` (Market intelligence)
- Migrate `dyon` (System monitoring)

### Phase 5: Support Packages
- Migrate `vision-system` (Visual observation)
- Migrate `memory-system` (Agent memory & RAG)
- Migrate `skill-framework` (Skill registry)
- Migrate `environment-bridge` (Desktop & browser bridges)

### Phase 6: Applications
- Migrate `desktop` (DIX DESKTOP application)
- Migrate `dashboard2026` (React dashboard)
- Migrate `agent-runtime` (Main orchestration)

### Phase 7: CI/CD Optimization
- Implement Turborepo caching strategy
- Optimize pipeline parallelization
- Set up dependency-aware builds

### Phase 8: Enforcement
- Implement dependency rule enforcement
- Set up automated boundary checks
- Configure ownership-based access controls

## CI/CD Optimization

### Current Issues
- 12+ GitHub workflows (redundant builds)
- No dependency-aware caching
- Full rebuilds on minor changes
- No parallel execution strategy

### Target State
- Single monorepo pipeline with Turborepo
- Intelligent caching (60-80% reduction)
- Parallel execution by dependency graph
- Changed-only builds for PRs
- Release automation with Changesets

## Success Metrics
- **Build time**: Reduce from 30+ min to <10 min
- **CI/CD efficiency**: 60-80% improvement through caching
- **Code ownership**: Clear module ownership with 100% coverage
- **Dependency clarity**: Zero circular dependencies
- **Team autonomy**: Teams can work independently within boundaries

## Next Steps
1. Review and approve module boundaries
2. Set up team ownership assignments
3. Begin Phase 2 migration (core packages)
4. Incremental migration with continuous verification