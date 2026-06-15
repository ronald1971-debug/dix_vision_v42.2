/**
 * Route Lazy Loader
 * DIX VISION v42.2 - Phase 1: Architecture Optimization
 * 
 * Route-based lazy loading system that integrates with the existing
 * hash-based routing system and replaces eager page loading.
 */

import React, { ComponentType, Suspense, lazy } from 'react';
import { createLazyComponent, LazyLoader, LazyLoadingFallback, LazyLoadErrorFallback } from './LazyLoadSystem';
import { moduleRegistry } from './ModuleRegistry';

// Type for route components
export type RouteComponent = ComponentType<any>;

// Route to module ID mapping
const ROUTE_MODULE_MAPPING: Record<string, string> = {
  // Trading routes
  'markets': 'unified-markets',
  'spot': 'unified-markets',
  'perps': 'unified-markets',
  'dex': 'unified-markets',
  'forex': 'unified-markets',
  'stocks': 'unified-markets',
  'nft': 'unified-markets',
  'orderflow': 'order-flow',
  'charting': 'charting',
  'portfolio': 'portfolio',
  'execution': 'execution',
  'positions': 'positions',
  'trading': 'trading',
  
  // Intelligence routes
  'indira': 'indira-learning',
  'indira-cognitive-center': 'indira-cognitive-center',
  'indira-workspace': 'indira-workspace',
  'dyon': 'dyon-learning',
  'dyon-workspace': 'dyon-workspace',
  'chat': 'cognitive-chat',
  'ai': 'ai-features',
  'memory': 'memory',
  
  // Operations routes
  'mission-control': 'mission-control',
  'syshealth': 'system-health',
  'governance': 'governance',
  'security': 'security',
  'risk': 'risk',
  'alerts': 'alerts',
  'audit': 'audit',
  
  // Operator routes (core)
  'operator': 'user-management',
  'credentials': 'authentication',
  
  // Additional routes (mapped to appropriate categories)
  'testing': 'system-health',
  'onchain': 'unified-markets',
  'observatory': 'mission-control',
  'agent-ops': 'mission-control',
  'operator-workspace': 'user-management',
  'strategies': 'portfolio',
  'simulation': 'execution',
  'signals': 'order-flow',
  'forms': 'authentication',
  'adapters': 'api-client',
  'ledger': 'governance',
  'hazards': 'security',
  'plugins': 'system-health',
  'market': 'unified-markets',
  'fabric': 'mission-control',
  'scout': 'order-flow'
};

// Lazy-loaded page components
const lazyPageComponents: Record<string, () => Promise<{ default: RouteComponent }>> = {
  // Trading pages
  markets: () => import('@/pages/MarketsPage').then(m => ({ default: m.MarketsPage })),
  orderflow: () => import('@/pages/OrderFlowPage').then(m => ({ default: m.OrderFlowPage })),
  charting: () => import('@/pages/ChartingPage').then(m => ({ default: m.ChartingPage })),
  portfolio: () => import('@/pages/PortfolioPage').then(m => ({ default: m.PortfolioPage })),
  execution: () => import('@/pages/ExecutionPage').then(m => ({ default: m.ExecutionPage })),
  positions: () => import('@/pages/PositionsPage').then(m => ({ default: m.PositionsPage })),
  trading: () => import('@/pages/TradingPage').then(m => ({ default: m.TradingPage })),
  
  // Intelligence pages
  'indira-learning': () => import('@/pages/IndiraLearningPage').then(m => ({ default: m.IndiraLearningPage })),
  'indira-cognitive-center': () => import('@/pages/IndiraCognitiveCenterPage').then(m => ({ default: m.IndiraCognitiveCenterPage })),
  'indira-workspace': () => import('@/pages/IndiraWorkspacePage').then(m => ({ default: m.IndiraWorkspacePage })),
  'dyon-learning': () => import('@/pages/DyonLearningPage').then(m => ({ default: m.DyonLearningPage })),
  'dyon-workspace': () => import('@/pages/DyonWorkspacePage').then(m => ({ default: m.DyonWorkspacePage })),
  'cognitive-chat': () => import('@/pages/CognitiveChatPage').then(m => ({ default: m.CognitiveChatPage })),
  'ai-features': () => import('@/pages/AIPage').then(m => ({ default: m.AIPage })),
  memory: () => import('@/pages/MemoryPage').then(m => ({ default: m.MemoryPage })),
  
  // Operations pages
  'mission-control': () => import('@/pages/MissionControlPage').then(m => ({ default: m.MissionControlPage })),
  'system-health': () => import('@/pages/SystemHealthPage').then(m => ({ default: m.SystemHealthPage })),
  governance: () => import('@/pages/GovernancePage').then(m => ({ default: m.GovernancePage })),
  security: () => import('@/pages/SecurityPage').then(m => ({ default: m.SecurityPage })),
  risk: () => import('@/pages/RiskPage').then(m => ({ default: m.RiskPage })),
  alerts: () => import('@/pages/AlertsPage').then(m => ({ default: m.AlertsPage })),
  audit: () => import('@/pages/AuditPage').then(m => ({ default: m.AuditPage })),
  
  // Operator pages
  'user-management': () => import('@/pages/OperatorPage').then(m => ({ default: m.OperatorPage })),
  authentication: () => import('@/pages/CredentialsPage').then(m => ({ default: m.CredentialsPage })),
  
  // Additional pages
  testing: () => import('@/pages/TestingPage').then(m => ({ default: m.TestingPage })),
  onchain: () => import('@/pages/OnChainPage').then(m => ({ default: m.OnChainPage })),
  observatory: () => import('@/pages/ObservatoryPage').then(m => ({ default: m.ObservatoryPage })),
  'agent-ops': () => import('@/pages/AgentOpsPage').then(m => ({ default: m.AgentOpsPage })),
  'operator-workspace': () => import('@/pages/OperatorWorkspacePage').then(m => ({ default: m.OperatorWorkspacePage })),
  strategies: () => import('@/pages/StrategiesPage').then(m => ({ default: m.StrategiesPage })),
  simulation: () => import('@/pages/SimulationPage').then(m => ({ default: m.SimulationPage })),
  signals: () => import('@/pages/SignalsPage').then(m => ({ default: m.SignalsPage })),
  forms: () => import('@/pages/FormsPage').then(m => ({ default: m.FormsPage })),
  adapters: () => import('@/pages/AdaptersPage').then(m => ({ default: m.AdaptersPage })),
  ledger: () => import('@/pages/LedgerPage').then(m => ({ default: m.LedgerPage })),
  hazards: () => import('@/pages/HazardsPage').then(m => ({ default: m.HazardsPage })),
  plugins: () => import('@/pages/PluginsPage').then(m => ({ default: m.PluginsPage })),
  fabric: () => import('@/pages/FabricPage').then(m => ({ default: m.FabricPage })),
  scout: () => import('@/pages/ScoutPage').then(m => ({ default: m.ScoutPage }))
};

// Cache for lazy-loaded components
const componentCache: Map<string, RouteComponent> = new Map();

/**
 * Get the module ID for a given route
 */
export function getModuleIdForRoute(route: string): string {
  return ROUTE_MODULE_MAPPING[route] || 'system-health';
}

/**
 * Check if a module should be loaded based on user profile
 */
export function shouldLoadModuleForRoute(route: string): boolean {
  const moduleId = getModuleIdForRoute(route);
  const userProfile = moduleRegistry.getUserProfile();
  return moduleRegistry.shouldLoadForProfile(moduleId, userProfile);
}

/**
 * Load a route component with lazy loading
 */
export function loadRouteComponent(route: string): RouteComponent | null {
  // Check if component is already cached
  if (componentCache.has(route)) {
    return componentCache.get(route)!;
  }

  // Check if module should be loaded for current user profile
  if (!shouldLoadModuleForRoute(route)) {
    console.warn(`Route ${route} not available for current user profile`);
    return null;
  }

  // Get the lazy import function for the route
  const importFn = lazyPageComponents[route];
  if (!importFn) {
    console.error(`No lazy import function found for route: ${route}`);
    return null;
  }

  const moduleId = getModuleIdForRoute(route);
  
  // Create lazy component with monitoring
  try {
    const LazyComponent = createLazyComponent(importFn, moduleId);
    componentCache.set(route, LazyComponent);
    return LazyComponent;
  } catch (error) {
    console.error(`Failed to create lazy component for route ${route}:`, error);
    return null;
  }
}

/**
 * Render a route with lazy loading
 */
export function renderLazyRoute(route: string): React.ReactNode {
  const component = loadRouteComponent(route);
  const moduleId = getModuleIdForRoute(route);

  if (!component) {
    return (
      <LazyLoader
        moduleId={moduleId}
        error={
          <LazyLoadErrorFallback 
            error={new Error(`Route ${route} not available`)}
            moduleId={moduleId}
          />
        }
      />
    );
  }

  const Component = component;

  return (
    <LazyLoader
      moduleId={moduleId}
      fallback={<LazyLoadingFallback message={`Loading ${route}...`} moduleId={moduleId} />}
    >
      <Component />
    </LazyLoader>
  );
}

/**
 * Prefetch routes for improved performance
 */
export async function prefetchRoutes(routes: string[]): Promise<void> {
  const prefetchPromises = routes.map(async route => {
    if (!shouldLoadModuleForRoute(route)) return;
    
    const moduleId = getModuleIdForRoute(route);
    if (moduleRegistry.isModuleLoaded(moduleId)) return;

    try {
      const importFn = lazyPageComponents[route];
      if (importFn) {
        await importFn();
        moduleRegistry.markModuleLoaded(moduleId);
      }
    } catch (error) {
      console.error(`Failed to prefetch route ${route}:`, error);
    }
  });

  await Promise.all(prefetchPromises);
}

/**
 * Get all routes that can be lazy-loaded
 */
export function getAllLazyRoutes(): string[] {
  return Object.keys(lazyPageComponents);
}

/**
 * Get routes by category
 */
export function getRoutesByCategory(category: 'trading' | 'intelligence' | 'operations' | 'core'): string[] {
  const categoryModules = moduleRegistry.getModulesByCategory(category as any);
  const categoryModuleIds = categoryModules.map(m => m.id);
  
  return Object.entries(ROUTE_MODULE_MAPPING)
    .filter(([_, moduleId]) => categoryModuleIds.includes(moduleId))
    .map(([route]) => route);
}

/**
 * Clear component cache (useful for testing or memory management)
 */
export function clearComponentCache(): void {
  componentCache.clear();
}

/**
 * Get cache statistics
 */
export function getCacheStats(): {
  cachedRoutes: number;
  totalRoutes: number;
  cacheHitRate: number;
} {
  const totalRoutes = Object.keys(lazyPageComponents).length;
  const cachedRoutes = componentCache.size;
  const cacheHitRate = totalRoutes > 0 ? (cachedRoutes / totalRoutes) * 100 : 0;

  return {
    cachedRoutes,
    totalRoutes,
    cacheHitRate
  };
}