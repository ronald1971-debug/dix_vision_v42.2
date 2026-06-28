/**
 * Plugin System
 * DIX VISION v42.2 - Phase 3: Plugin Preservation
 * 
 * Complete plugin system including infrastructure, API management,
 * state migration, marketplace integration, and development framework.
 * 
 * @module plugin-system
 */

// Core Plugin System
export { enhancedPluginSystem } from './EnhancedPluginSystem';

// Plugin API Management
export { pluginAPIManager } from './PluginAPIManager';

// Plugin State Migration
export { pluginStateMigrator } from './PluginStateMigrator';

// Plugin Enhancement
export { pluginEnhancementFactory } from './PluginEnhancer';

// Plugin Marketplace
export { pluginMarketplace } from './PluginMarketplace';

// Plugin Development Framework
export { 
  pluginDevelopmentFramework, 
  pluginMonitoringSystem 
} from './PluginDevelopmentFramework';

// Types
export type { 
  EnhancedPluginRecord, 
  PluginHealthStatus, 
  PluginMetrics as PluginRecordMetrics,
  PluginConfiguration,
  PluginCompatibilityInfo
} from './EnhancedPluginSystem';

export type {
  OriginalPluginAPI,
  EnhancedPluginAPI,
  PluginAPICompatibilityLayer,
  StateAdapter
} from './PluginAPIManager';

export type {
  StateMigrationPlan,
  MigrationStep,
  StateSnapshot
} from './PluginStateMigrator';

export type {
  MarketplacePlugin,
  PluginRating,
  PluginReview,
  PluginVerification,
  PluginPricing,
  PluginStatistics
} from './PluginMarketplace';

export type {
  PluginProject,
  PluginProjectConfig,
  TestResult
} from './PluginDevelopmentFramework';

export type {
  PluginMetrics as MonitoringPluginMetrics,
  ExecutionRecord,
  AlertThresholds
} from './PluginDevelopmentFramework';