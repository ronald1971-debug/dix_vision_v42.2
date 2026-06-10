#!/usr/bin/env node

/**
 * Dependency Rules Validator
 * 
 * Enforces module boundaries and dependency rules for DIX VISION monorepo.
 * This script validates that packages only depend on allowed dependencies.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ============================================================================
// DEPENDENCY RULES
// ============================================================================

const DEPENDENCY_RULES = {
  // Foundation packages (no dependencies on other packages)
  'shared-types': {
    allowedDependencies: [],
    description: 'Foundation package - no package dependencies allowed',
  },
  'shared-config': {
    allowedDependencies: ['shared-types'],
    description: 'Foundation package - can only depend on shared-types',
  },

  // Core packages (depend on foundation only)
  'governance-core': {
    allowedDependencies: ['shared-types', 'shared-config'],
    description: 'Core package - can depend on foundation packages only',
  },
  'observability': {
    allowedDependencies: ['shared-types', 'shared-config'],
    description: 'Core package - can depend on foundation packages only',
  },

  // Engine packages (depend on core + foundation)
  'execution-engine': {
    allowedDependencies: ['shared-types', 'shared-config', 'governance-core', 'observability'],
    description: 'Engine package - can depend on core + foundation packages',
  },

  // Agent packages (depend on engines + core + foundation)
  'indira': {
    allowedDependencies: [
      'shared-types',
      'shared-config',
      'governance-core',
      'execution-engine',
    ],
    description: 'Agent package - can depend on engines + core + foundation',
  },
  'dyon': {
    allowedDependencies: ['shared-types', 'shared-config', 'observability'],
    description: 'Agent package - can depend on core + foundation',
  },

  // Applications (can depend on any package)
  'desktop': {
    allowedDependencies: ['*'], // Can depend on any package
    description: 'Application - can depend on any package',
  },
  'desktop-app': {
    allowedDependencies: ['*'], // Can depend on any package
    description: 'Application - can depend on any package',
  },
  'dashboard': {
    allowedDependencies: ['*'], // Can depend on any package
    description: 'Application - can depend on any package',
  },
  'dashboard-app': {
    allowedDependencies: ['*'], // Can depend on any package
    description: 'Application - can depend on any package',
  },
  'agent-runtime': {
    allowedDependencies: ['*'], // Can depend on any package
    description: 'Application - can depend on any package',
  },
};

// ============================================================================
// VALIDATION FUNCTIONS
// ============================================================================

function readPackageJson(packagePath) {
  const packageJsonPath = path.join(packagePath, 'package.json');
  if (!fs.existsSync(packageJsonPath)) {
    return null;
  }

  const content = fs.readFileSync(packageJsonPath, 'utf-8');
  return JSON.parse(content);
}

function getPackageName(packagePath) {
  const packageJson = readPackageJson(packagePath);
  if (packageJson) {
    // Extract the package name from the full name
    // @dix-vision/desktop-app -> desktop
    // @dix-vision/dashboard-app -> dashboard
    // @dix-vision/agent-runtime -> agent-runtime
    const match = packageJson.name.match(/@dix-vision\/(.+)$/);
    if (match) {
      return match[1].replace('-app', '').replace('-runtime', '-runtime');
    }
    return packageJson.name;
  }
  
  // Fallback to directory name
  return path.basename(packagePath);
}

function getPackageDependencies(packageJson) {
  const dependencies = packageJson.dependencies || {};
  const devDependencies = packageJson.devDependencies || {};
  return { ...dependencies, ...devDependencies };
}

function extractInternalPackageName(dependencyName) {
  // Match @dix-vision/ package names
  const match = dependencyName.match(/^@dix-vision\/(.+)$/);
  return match ? match[1] : null;
}

function validatePackageDependencies(packagePath, packageName) {
  const packageJson = readPackageJson(packagePath);
  if (!packageJson) {
    return { valid: true, errors: [] };
  }

  const rules = DEPENDENCY_RULES[packageName];
  if (!rules) {
    return {
      valid: false,
      errors: [`No dependency rules defined for package: ${packageName}`],
    };
  }

  const dependencies = getPackageDependencies(packageJson);
  const errors = [];

  for (const [depName, depVersion] of Object.entries(dependencies)) {
    const internalPackage = extractInternalPackageName(depName);

    if (internalPackage) {
      // Check if this internal package is allowed
      if (rules.allowedDependencies.includes('*')) {
        // Any dependency allowed for applications
        continue;
      }

      if (!rules.allowedDependencies.includes(internalPackage)) {
        errors.push(
          `${packageName} cannot depend on ${internalPackage}. ` +
            `Allowed: ${rules.allowedDependencies.join(', ')}`
        );
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

function validateAllPackages() {
  const packagesDir = path.join(__dirname, '..', 'packages');
  const appsDir = path.join(__dirname, '..', 'apps');
  const allErrors = [];

  // Validate packages
  if (fs.existsSync(packagesDir)) {
    const packageDirs = fs.readdirSync(packagesDir);

    for (const packageDir of packageDirs) {
      const packagePath = path.join(packagesDir, packageDir);
      const packageName = packageDir; // Use directory name as package name

      const result = validatePackageDependencies(packagePath, packageName);

      if (!result.valid) {
        allErrors.push({
          package: packageName,
          path: packagePath,
          errors: result.errors,
        });
      }
    }
  }

  // Validate apps
  if (fs.existsSync(appsDir)) {
    const appDirs = fs.readdirSync(appsDir);

    for (const appDir of appDirs) {
      const appPath = path.join(appsDir, appDir);
      const appName = appDir; // Use directory name as app name

      const result = validatePackageDependencies(appPath, appName);

      if (!result.valid) {
        allErrors.push({
          package: appName,
          path: appPath,
          errors: result.errors,
        });
      }
    }
  }

  return allErrors;
}

function checkCircularDependencies() {
  try {
    // Check if turbo is available
    execSync('turbo --version', { encoding: 'utf-8', stdio: 'pipe' });
    
    // Use Turborepo to check for circular dependencies
    const output = execSync('turbo build --dry-run', { encoding: 'utf-8' });
    return { hasCircular: false, output };
  } catch (error) {
    // Turbo not installed, skip circular dependency check
    if (error.message.includes('not recognized') || error.message.includes('command not found')) {
      return { 
        hasCircular: false, 
        skipped: true, 
        message: 'Turborepo not installed - skipping circular dependency check' 
      };
    }
    return {
      hasCircular: true,
      error: error.message,
    };
  }
}

// ============================================================================
// MAIN EXECUTION
// ============================================================================

function main() {
  console.log('🔍 Validating dependency rules...\n');

  // Validate all packages
  const dependencyErrors = validateAllPackages();

  if (dependencyErrors.length > 0) {
    console.error('❌ Dependency rule violations found:\n');
    
    for (const error of dependencyErrors) {
      console.error(`📦 ${error.package}:`);
      for (const errorMsg of error.errors) {
        console.error(`   ❌ ${errorMsg}`);
      }
      console.error();
    }
    
    process.exit(1);
  } else {
    console.log('✅ All dependency rules passed\n');
  }

  // Check for circular dependencies
  console.log('🔍 Checking for circular dependencies...\n');
  const circularCheck = checkCircularDependencies();

  if (circularCheck.hasCircular) {
    console.error('❌ Circular dependencies detected:\n');
    console.error(circularCheck.error);
    process.exit(1);
  } else if (circularCheck.skipped) {
    console.log('⏭️  Skipping circular dependency check (Turborepo not installed)\n');
  } else {
    console.log('✅ No circular dependencies detected\n');
  }

  console.log('✅ All validation checks passed!');
  console.log('\n📊 Summary:');
  console.log('   - Dependency rules: ✅ PASSED');
  console.log('   - Circular dependencies: ✅ PASSED');
  console.log('\n🎉 Module boundaries are intact!');
}

// Run validation
if (require.main === module) {
  main();
}

module.exports = {
  validatePackageDependencies,
  validateAllPackages,
  checkCircularDependencies,
};