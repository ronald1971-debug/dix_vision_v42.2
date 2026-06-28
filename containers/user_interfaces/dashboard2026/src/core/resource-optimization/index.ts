/**
 * Resource Optimization System
 * DIX VISION v42.2 - Phase 2: Resource Optimization
 * 
 * Complete resource optimization system including memory management,
 * CPU optimization, network optimization, and plugin consolidation.
 * 
 * @module resource-optimization
 */

// Memory Management
export { memoryManager } from './MemoryManager';

// CPU Optimization
export { cpuOptimizer } from './CPUOptimizer';

// Network Optimization
export { networkOptimizer } from './NetworkOptimizer';

// Plugin Consolidation
export { pluginConsolidator } from './PluginConsolidator';

// Types
export type { MemoryInfo, MemoryPressureLevel, MemoryCleanupStrategy, MemoryLeak } from './MemoryManager';
export type { WorkerTask, TaskResult } from './CPUOptimizer';
export type { CacheEntry, BandwidthMetrics } from './NetworkOptimizer';
export type { PluginDefinition, ConsolidatedPlugin, CompatibilityLayer, PluginState } from './PluginConsolidator';