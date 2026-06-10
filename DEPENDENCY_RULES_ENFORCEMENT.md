# Dependency Rules and Enforcement Setup

## Overview
Automated enforcement of module boundaries, dependency rules, and architectural compliance for the DIX VISION monorepo.

---

## Enforcement Strategy

### Multi-Layer Enforcement
1. **Turborepo Dependency Rules** - Build-time enforcement
2. **Automated Validation Scripts** - CI/CD checks
3. **Pre-commit Hooks** - Local developer enforcement
4. **Documentation Requirements** - Manual compliance

---

## 1. Turborepo Dependency Rules

### Current Configuration
Update `turbo.json` with explicit dependency constraints:

```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"],
      "env": ["NODE_ENV"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    }
  },
  "globalDependencies": ["**/.env.*local"]
}
```

### Package-Specific Constraints
Each package should enforce its allowed dependencies through `tsconfig.json` references:

```json
// packages/indira/tsconfig.json
{
  "references": [
    { "path": "../shared-types" },
    { "path": "../shared-config" },
    { "path": "../governance-core" },
    { "path": "../execution-engine" }
    // ❌ NO references to packages above this level
  ]
}
```

---

## 2. Automated Validation Script

Create a validation script to check dependency rules:<tool_call>write<arg_key>file_path</arg_key><arg_value>C:\dix_vision_v42.2\scripts\validate-dependency-rules.js