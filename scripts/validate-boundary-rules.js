#!/usr/bin/env node

/**
 * Boundary Rules Validator
 * 
 * Validates architectural boundary rules for the DIX VISION system:
 * - No upward dependencies (packages → apps)
 * - No cross-domain violations (indira → dyon, governance → execution)
 * - Event-driven communication only between modules
 * - No direct internal access between modules
 */

const fs = require('fs');
const path = require('path');

// ============================================================================
// BOUNDARY RULES
// ============================================================================

const BOUNDARY_RULES = {
  // Upward dependency rule: Packages cannot depend on Apps
  noUpwardDependencies: {
    description: 'Packages cannot depend on applications',
    validate: (source, target) => {
      const isPackage = source.startsWith('packages/');
      const isApp = target.startsWith('apps/');
      return !(isPackage && isApp);
    },
  },

  // Cross-domain rule: Agents should not directly depend on each other
  noAgentToAgent: {
    description: 'Agents should not directly depend on other agents',
    validate: (source, target) => {
      const agents = ['indira', 'dyon'];
      const isSourceAgent = agents.some(agent => source.includes(agent));
      const isTargetAgent = agents.some(agent => target.includes(agent));
      return !(isSourceAgent && isTargetAgent);
    },
  },

  // Governance independence rule: Governance cannot depend on execution
  governanceIndependence: {
    description: 'Governance cannot depend on execution layer',
    validate: (source, target) => {
      const isGovernance = source.includes('governance');
      const isExecution = target.includes('execution');
      return !(isGovernance && isExecution);
    },
  },

  // Foundation independence rule: Foundation packages have minimal dependencies
  foundationIndependence: {
    description: 'Foundation packages must have minimal dependencies (shared-config can depend on shared-types)',
    validate: (source, target) => {
      const foundation = ['shared-types', 'shared-config'];
      const isFoundation = foundation.some(f => source.includes(f));
      const isPackageDep = target.startsWith('packages/');
      
      // shared-config is allowed to depend on shared-types
      if (source.includes('shared-config') && target.includes('shared-types')) {
        return true;
      }
      
      // shared-types has no dependencies
      if (source.includes('shared-types') && isPackageDep) {
        return false;
      }
      
      return !(isFoundation && isPackageDep);
    },
  },
};

// ============================================================================
// IMPORT ANALYSIS
// ============================================================================

function findImportStatements(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const imports = [];

  // Match TypeScript/JavaScript imports
  const importRegex = /import\s+(?:.*\s+from\s+)?['"]([^'"]+)['"]/g;
  let match;

  while ((match = importRegex.exec(content)) !== null) {
    imports.push({
      type: 'import',
      specifier: match[1],
      line: content.substring(0, match.index).split('\n').length,
    });
  }

  // Match Python imports
  const pythonImportRegex = /from\s+(\S+)\s+import|^import\s+(\S+)/gm;
  while ((match = pythonImportRegex.exec(content)) !== null) {
    const importPath = match[1] || match[2];
    imports.push({
      type: 'python_import',
      specifier: importPath,
      line: content.substring(0, match.index).split('\n').length,
    });
  }

  return imports;
}

function analyzeFileBoundaries(filePath, projectRoot) {
  const relativePath = path.relative(projectRoot, filePath);
  const imports = findImportStatements(filePath);
  const violations = [];

  for (const imp of imports) {
    // Check if import is an internal module
    if (imp.specifier.startsWith('@dix-vision/') || imp.specifier.startsWith('../')) {
      // Resolve the import to a file path
      const targetPath = resolveImportPath(imp.specifier, filePath, projectRoot);

      if (targetPath) {
        // Validate against boundary rules
        for (const [ruleName, rule] of Object.entries(BOUNDARY_RULES)) {
          if (!rule.validate(relativePath, targetPath)) {
            violations.push({
              rule: ruleName,
              description: rule.description,
              file: relativePath,
              line: imp.line,
              import: imp.specifier,
              target: targetPath,
            });
          }
        }
      }
    }
  }

  return violations;
}

function resolveImportPath(importSpecifier, currentFile, projectRoot) {
  // Simple resolution for @dix-vision/ packages
  if (importSpecifier.startsWith('@dix-vision/')) {
    const packageName = importSpecifier.replace('@dix-vision/', '');
    return `packages/${packageName}`;
  }

  // Simple resolution for relative imports
  if (importSpecifier.startsWith('../')) {
    const currentDir = path.dirname(currentFile);
    const resolvedPath = path.resolve(currentDir, importSpecifier);
    return path.relative(projectRoot, resolvedPath);
  }

  return null;
}

function scanProject(projectRoot) {
  const violations = [];
  const dirsToScan = ['packages', 'apps'];

  for (const dir of dirsToScan) {
    const dirPath = path.join(projectRoot, dir);
    if (!fs.existsSync(dirPath)) continue;

    const scanDir = (currentDir) => {
      const items = fs.readdirSync(currentDir);

      for (const item of items) {
        const itemPath = path.join(currentDir, item);
        const stat = fs.statSync(itemPath);

        if (stat.isDirectory()) {
          // Skip node_modules and dist directories
          if (item !== 'node_modules' && item !== 'dist') {
            scanDir(itemPath);
          }
        } else if (stat.isFile()) {
          // Scan TypeScript and Python files
          if (item.endsWith('.ts') || item.endsWith('.tsx') || item.endsWith('.py')) {
            const fileViolations = analyzeFileBoundaries(itemPath, projectRoot);
            violations.push(...fileViolations);
          }
        }
      }
    };

    scanDir(dirPath);
  }

  return violations;
}

// ============================================================================
// ARCHITECTURAL COMPLIANCE CHECKS
// ============================================================================

function checkArchitecturalCompliance(projectRoot) {
  const complianceIssues = [];

  // Check that governance files don't import execution files
  const governanceDir = path.join(projectRoot, 'packages', 'governance-core');
  const executionDir = path.join(projectRoot, 'packages', 'execution-engine');

  if (fs.existsSync(governanceDir) && fs.existsSync(executionDir)) {
    const governanceFiles = getAllFiles(governanceDir, ['.ts', '.tsx']);
    
    for (const file of governanceFiles) {
      const content = fs.readFileSync(file, 'utf-8');
      // Check for execution imports
      if (content.includes('execution-engine') || content.includes('@dix-vision/execution-engine')) {
        complianceIssues.push({
          type: 'governance_independence',
          file: path.relative(projectRoot, file),
          message: 'Governance code should not import execution engine',
        });
      }
    }
  }

  // Check that agent files respect domain boundaries
  const indiraDir = path.join(projectRoot, 'packages', 'indira');
  const dyonDir = path.join(projectRoot, 'packages', 'dyon');

  if (fs.existsSync(indiraDir) && fs.existsSync(dyonDir)) {
    const indiraFiles = getAllFiles(indiraDir, ['.ts', '.tsx']);
    
    for (const file of indiraFiles) {
      const content = fs.readFileSync(file, 'utf-8');
      // Check for dyon imports
      if (content.includes('dyon') || content.includes('@dix-vision/dyon')) {
        complianceIssues.push({
          type: 'agent_separation',
          file: path.relative(projectRoot, file),
          message: 'Indira should not directly import Dyon code',
        });
      }
    }
  }

  return complianceIssues;
}

function getAllFiles(dir, extensions) {
  const files = [];
  const items = fs.readdirSync(dir);

  for (const item of items) {
    const itemPath = path.join(dir, item);
    const stat = fs.statSync(itemPath);

    if (stat.isDirectory()) {
      if (item !== 'node_modules' && item !== 'dist') {
        files.push(...getAllFiles(itemPath, extensions));
      }
    } else if (stat.isFile()) {
      if (extensions.some(ext => item.endsWith(ext))) {
        files.push(itemPath);
      }
    }
  }

  return files;
}

// ============================================================================
// MAIN EXECUTION
// ============================================================================

function main() {
  const projectRoot = path.join(__dirname, '..');

  console.log('🔍 Validating architectural boundary rules...\n');

  // Scan for boundary violations
  const violations = scanProject(projectRoot);

  if (violations.length > 0) {
    console.error('❌ Architectural boundary violations found:\n');

    for (const violation of violations) {
      console.error(`📋 ${violation.rule}:`);
      console.error(`   Description: ${violation.description}`);
      console.error(`   File: ${violation.file}:${violation.line}`);
      console.error(`   Import: ${violation.import}`);
      console.error(`   Target: ${violation.target}`);
      console.error();
    }

    process.exit(1);
  } else {
    console.log('✅ No boundary violations found\n');
  }

  // Check architectural compliance
  console.log('🔍 Checking architectural compliance...\n');
  const complianceIssues = checkArchitecturalCompliance(projectRoot);

  if (complianceIssues.length > 0) {
    console.error('❌ Architectural compliance issues found:\n');

    for (const issue of complianceIssues) {
      console.error(`📋 ${issue.type}:`);
      console.error(`   File: ${issue.file}`);
      console.error(`   Message: ${issue.message}`);
      console.error();
    }

    process.exit(1);
  } else {
    console.log('✅ Architectural compliance verified\n');
  }

  console.log('✅ All boundary checks passed!');
  console.log('\n📊 Summary:');
  console.log('   - Import boundary rules: ✅ PASSED');
  console.log('   - Architectural compliance: ✅ PASSED');
  console.log('\n🎉 Architectural boundaries are intact!');
}

// Run validation
if (require.main === module) {
  main();
}

module.exports = {
  analyzeFileBoundaries,
  scanProject,
  checkArchitecturalCompliance,
};