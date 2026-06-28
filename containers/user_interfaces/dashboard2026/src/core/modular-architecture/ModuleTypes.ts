/**
 * Modular Architecture Types
 * DIX VISION v42.2 - Phase 1: Architecture Optimization
 * 
 * Defines the core types for the modular architecture system including
 * module categories, load strategies, and feature consolidation patterns.
 */

export type ModuleCategory = 'core' | 'trading' | 'intelligence' | 'operations' | 'plugin';

export type LoadStrategy = 'eager' | 'on_navigation' | 'on_demand' | 'lazy';

export type UserProfile = 'minimal' | 'standard' | 'professional';

export interface ModuleConfig {
  id: string;
  category: ModuleCategory;
  loadStrategy: LoadStrategy;
  dependencies: string[];
  bundleSize: number;
  memoryEstimate: number;
  requiredForProfile: UserProfile[];
  optionalForProfile?: UserProfile[];
  version: string;
}

export interface ModuleLoadResult {
  moduleId: string;
  loadTime: number;
  memoryUsed: number;
  success: boolean;
  error?: Error;
}

export interface ResourceMetrics {
  bundleSize: number;
  memoryUsage: number;
  loadTime: number;
  activeModules: number;
  totalModules: number;
}

export interface FeatureConsolidationPlan {
  originalFeatures: string[];
  consolidatedModules: string[];
  preservationStrategy: string;
  expectedReduction: number;
}