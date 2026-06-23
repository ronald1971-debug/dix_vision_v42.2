/**
 * Domain Dependency Graph
 * 
 * This module manages the dependency relationships between domains,
 * ensuring proper dependency resolution and preventing circular dependencies.
 */

export interface DomainDependency {
  domain: string;
  dependencies: string[];
  dependents: string[];
}

export const DOMAIN_DEPENDENCIES: Record<string, string[]> = {
  indira: ['shared', 'world_model'],
  dyon: ['shared', 'world_model'],
  governance: ['shared', 'operator'],
  execution: ['shared', 'governance', 'indira'],
  operator: ['shared'],
  world_model: ['shared'],
  simulation: ['shared', 'execution'],
  learning: ['shared', 'indira', 'dyon'],
  shared: [], // Base layer - no dependencies
};

export const DEPENDENT_DOMAINS: Record<string, string[]> = {
  shared: ['indira', 'dyon', 'governance', 'execution', 'operator', 'world_model', 'simulation', 'learning'],
  world_model: ['indira', 'dyon'],
  operator: ['governance'],
  governance: ['execution'],
  indira: ['execution', 'learning'],
  dyon: ['learning'],
  execution: ['simulation'],
};

/**
 * Check if domain A depends on domain B
 */
export function dependsOn(domain: string, target: string): boolean {
  return DOMAIN_DEPENDENCIES[domain]?.includes(target) || false;
}

/**
 * Get all dependencies for a domain (transitive)
 */
export function getAllDependencies(domain: string, visited: Set<string> = new Set()): string[] {
  if (visited.has(domain)) {
    return [];
  }
  
  visited.add(domain);
  const directDeps = DOMAIN_DEPENDENCIES[domain] || [];
  const transitiveDeps: string[] = [];
  
  for (const dep of directDeps) {
    transitiveDeps.push(...getAllDependencies(dep, visited));
  }
  
  return [...new Set([...directDeps, ...transitiveDeps])];
}

/**
 * Get all domains that depend on this domain (transitive)
 */
export function getAllDependents(domain: string, visited: Set<string> = new Set()): string[] {
  if (visited.has(domain)) {
    return [];
  }
  
  visited.add(domain);
  const directDependents = DEPENDENT_DOMAINS[domain] || [];
  const transitiveDependents: string[] = [];
  
  for (const dependent of directDependents) {
    transitiveDependents.push(...getAllDependents(dependent, visited));
  }
  
  return [...new Set([...directDependents, ...transitiveDependents])];
}

/**
 * Check for circular dependencies
 */
export function detectCircularDependencies(): string[][] {
  const circularDeps: string[][] = [];
  
  for (const domain of Object.keys(DOMAIN_DEPENDENCIES)) {
    const dependencies = getAllDependencies(domain);
    
    for (const dep of dependencies) {
      if (getAllDependencies(dep).includes(domain)) {
        if (!circularDeps.some(cycle => cycle.includes(domain) && cycle.includes(dep))) {
          circularDeps.push([domain, dep]);
        }
      }
    }
  }
  
  return circularDeps;
}

/**
 * Get load order for domains based on dependencies
 * Domains with no dependencies load first
 */
export function getLoadOrder(): string[] {
  const loadOrder: string[] = [];
  const remaining = new Set(Object.keys(DOMAIN_DEPENDENCIES));
  const loaded = new Set<string>();
  
  while (remaining.size > 0) {
    let progressMade = false;
    
    for (const domain of Array.from(remaining)) {
      const dependencies = DOMAIN_DEPENDENCIES[domain] || [];
      
      if (dependencies.every(dep => loaded.has(dep))) {
        loadOrder.push(domain);
        loaded.add(domain);
        remaining.delete(domain);
        progressMade = true;
      }
    }
    
    if (!progressMade) {
      throw new Error('Circular dependency detected in domain load order');
    }
  }
  
  return loadOrder;
}

/**
 * Validate domain dependency configuration
 */
export function validateDependencies(): {
  valid: boolean;
  errors: string[];
  warnings: string[];
} {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // Check for circular dependencies
  const circularDeps = detectCircularDependencies();
  if (circularDeps.length > 0) {
    errors.push(`Circular dependencies detected: ${circularDeps.map(cycle => cycle.join(' <-> ')).join(', ')}`);
  }
  
  // Check for undefined dependencies
  for (const [domain, deps] of Object.entries(DOMAIN_DEPENDENCIES)) {
    for (const dep of deps) {
      if (!DOMAIN_DEPENDENCIES[dep]) {
        warnings.push(`Domain '${domain}' depends on undefined domain '${dep}'`);
      }
    }
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}