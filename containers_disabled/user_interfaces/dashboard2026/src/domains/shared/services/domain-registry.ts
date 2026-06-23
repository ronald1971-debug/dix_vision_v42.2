/**
 * Domain Registry
 * 
 * Central registry for all domain modules, providing unified access
 * to domain information, dependencies, and management functions.
 */

import { DOMAIN_DEPENDENCIES, getAllDependencies, getLoadOrder, validateDependencies } from '../utils/dependency-graph';
import { DomainEventBus } from '../utils/event-bus';
import { DomainGateway } from '../utils/domain-gateway';

// Import all domain information
import { INDIRA_DOMAIN_INFO } from '../../indira';
import { DYON_DOMAIN_INFO } from '../../dyon';
import { GOVERNANCE_DOMAIN_INFO } from '../../governance';
import { EXECUTION_DOMAIN_INFO } from '../../execution';
import { OPERATOR_DOMAIN_INFO } from '../../operator';
import { WORLD_MODEL_DOMAIN_INFO } from '../../world_model';
import { SIMULATION_DOMAIN_INFO } from '../../simulation';
import { LEARNING_DOMAIN_INFO } from '../../learning';
import { SHARED_DOMAIN_INFO } from '../../shared';

/**
 * All domain information registry
 */
export const DOMAIN_REGISTRY = {
  indira: INDIRA_DOMAIN_INFO,
  dyon: DYON_DOMAIN_INFO,
  governance: GOVERNANCE_DOMAIN_INFO,
  execution: EXECUTION_DOMAIN_INFO,
  operator: OPERATOR_DOMAIN_INFO,
  world_model: WORLD_MODEL_DOMAIN_INFO,
  simulation: SIMULATION_DOMAIN_INFO,
  learning: LEARNING_DOMAIN_INFO,
  shared: SHARED_DOMAIN_INFO,
};

/**
 * Get domain information
 */
export function getDomainInfo(domain: string): typeof DOMAIN_REGISTRY[keyof typeof DOMAIN_REGISTRY] | null {
  return DOMAIN_REGISTRY[domain as keyof typeof DOMAIN_REGISTRY] || null;
}

/**
 * Get all domain names
 */
export function getAllDomainNames(): string[] {
  return Object.keys(DOMAIN_REGISTRY);
}

/**
 * Get domains sorted by runtime usage priority
 */
export function getDomainsByPriority(): string[] {
  const domains = Object.entries(DOMAIN_REGISTRY)
    .sort((a, b) => {
      const priorityOrder = { VERY_HIGH: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
      const aPriority = priorityOrder[a[1].runtimeUsage as keyof typeof priorityOrder] || 999;
      const bPriority = priorityOrder[b[1].runtimeUsage as keyof typeof priorityOrder] || 999;
      return aPriority - bPriority;
    })
    .map(([domain]) => domain);
  
  return domains;
}

/**
 * Get domains by dependency level (base domains first)
 */
export function getDomainsByDependencyLevel(): string[] {
  return getLoadOrder();
}

/**
 * Validate domain configuration
 */
export function validateDomainConfiguration(): {
  valid: boolean;
  errors: string[];
  warnings: string[];
} {
  const validation = validateDependencies();
  const errors = [...validation.errors];
  const warnings = [...validation.warnings];
  
  // Validate domain information completeness
  for (const [domain, info] of Object.entries(DOMAIN_REGISTRY)) {
    if (!info.name || !info.fullName) {
      warnings.push(`Domain '${domain}' has incomplete naming information`);
    }
    
    if (!info.dependencies) {
      warnings.push(`Domain '${domain}' has no dependency information`);
    }
    
    if (!info.components || !Array.isArray(info.components)) {
      warnings.push(`Domain '${domain}' has invalid component information`);
    }
    
    if (!info.routes || !Array.isArray(info.routes)) {
      warnings.push(`Domain '${domain}' has invalid route information`);
    }
  }
  
  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Get domain statistics
 */
export function getDomainStatistics(): {
  totalDomains: number;
  totalComponents: number;
  totalWidgets: number;
  totalAPIs: number;
  totalRoutes: number;
  domainsByRuntimeUsage: Record<string, number>;
  dependencyStats: {
    maxDependencies: number;
    minDependencies: number;
    avgDependencies: number;
  };
} {
  const stats = {
    totalDomains: Object.keys(DOMAIN_REGISTRY).length,
    totalComponents: 0,
    totalWidgets: 0,
    totalAPIs: 0,
    totalRoutes: 0,
    domainsByRuntimeUsage: {} as Record<string, number>,
    dependencyStats: {
      maxDependencies: 0,
      minDependencies: Infinity,
      avgDependencies: 0,
    },
  };
  
  let totalDependencies = 0;
  
  for (const info of Object.values(DOMAIN_REGISTRY)) {
    stats.totalComponents += info.components.length;
    stats.totalWidgets += (info.widgets || []).length;
    stats.totalAPIs += (info.apis || []).length;
    stats.totalRoutes += info.routes.length;
    
    // Runtime usage breakdown
    const usage = info.runtimeUsage;
    stats.domainsByRuntimeUsage[usage] = (stats.domainsByRuntimeUsage[usage] || 0) + 1;
    
    // Dependency statistics
    const depCount = info.dependencies.length;
    totalDependencies += depCount;
    stats.dependencyStats.maxDependencies = Math.max(stats.dependencyStats.maxDependencies, depCount);
    stats.dependencyStats.minDependencies = Math.min(stats.dependencyStats.minDependencies, depCount);
  }
  
  // Calculate average dependencies
  if (stats.totalDomains > 0) {
    stats.dependencyStats.avgDependencies = totalDependencies / stats.totalDomains;
  }
  
  if (stats.dependencyStats.minDependencies === Infinity) {
    stats.dependencyStats.minDependencies = 0;
  }
  
  return stats;
}

/**
 * Initialize domain system
 */
export function initializeDomainSystem(): {
  success: boolean;
  validation: ReturnType<typeof validateDomainConfiguration>;
  loadOrder: string[];
  eventBusStats: ReturnType<typeof DomainEventBus.getSubscriptionStats>;
  gatewayStats: ReturnType<typeof DomainGateway.getRegistryStats>;
} {
  // Validate configuration
  const validation = validateDomainConfiguration();
  
  // Get optimal load order
  const loadOrder = getDomainsByDependencyLevel();
  
  // Get initial system stats
  const eventBusStats = DomainEventBus.getSubscriptionStats();
  const gatewayStats = DomainGateway.getRegistryStats();
  
  return {
    success: validation.valid,
    validation,
    loadOrder,
    eventBusStats,
    gatewayStats,
  };
}

/**
 * Domain system utilities
 */
export const DomainSystem = {
  // Information access
  getDomainInfo,
  getAllDomainNames,
  getDomainsByPriority,
  getDomainsByDependencyLevel,
  
  // Validation and statistics
  validateDomainConfiguration,
  getDomainStatistics,
  initializeDomainSystem,
  
  // Dependency management
  DOMAIN_DEPENDENCIES,
  getAllDependencies,
  getLoadOrder,
  
  // Communication
  EventBus: DomainEventBus,
  Gateway: DomainGateway,
  
  // Registry
  DOMAIN_REGISTRY,
};