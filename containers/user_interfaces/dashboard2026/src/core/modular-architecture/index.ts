/**
 * Modular Architecture System
 * DIX VISION v42.2 - Phase 1: Architecture Optimization
 * 
 * Complete modular architecture system for Dashboard2026 refactoring.
 * Provides code splitting, lazy loading, resource monitoring, and
 * user profile-based feature loading.
 * 
 * @module modular-architecture
 */

// Core types
export * from './ModuleTypes';

// Module registry
export { moduleRegistry } from './ModuleRegistry';

// Lazy loading system
export {
  LazyLoader,
  LazyLoadingFallback,
  LazyLoadErrorFallback,
  createLazyComponent,
  prefetchModule,
  unloadModule,
  getLoadMetrics,
  checkLazyLoadHealth,
  loadPerformanceMonitor
} from './LazyLoadSystem';

// Route lazy loader
export {
  getModuleIdForRoute,
  shouldLoadModuleForRoute,
  loadRouteComponent,
  renderLazyRoute,
  prefetchRoutes,
  getAllLazyRoutes,
  getRoutesByCategory,
  clearComponentCache,
  getCacheStats
} from './RouteLazyLoader';

// Resource monitor
export {
  resourceMonitor,
  useResourceMonitor
} from './ResourceMonitor';

// User profile manager
export {
  UserProfileProvider,
  useUserProfile,
  compareProfiles,
  getRecommendedProfile
} from './UserProfileManager';

// Feature consolidation plan
export {
  CONSOLIDATED_HUBS,
  HUB_CONFIG,
  CONSOLIDATION_SUMMARY,
  FEATURE_MAPPING
} from './FeatureConsolidationPlan';