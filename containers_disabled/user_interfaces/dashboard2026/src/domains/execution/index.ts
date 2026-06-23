/**
 * EXECUTION Domain Module
 * Trading & Order Management Domain
 * 
 * This domain handles trading execution, order management,
 * market operations, and trade execution strategies.
 */

// Component exports
export * from './components';

// Widget exports  
export * from './widgets';

// Store exports
export * from './stores';

// Service exports (to be added during service migration)
// export * from './services';

// Hook exports (to be added during hook migration)
// export * from './hooks';

// Type exports (to be added during type migration)
// export * from './types';

// Utility exports (to be added during utility migration)
// export * from './utils';

/**
 * EXECUTION Domain Information
 */
export const EXECUTION_DOMAIN_INFO = {
  name: 'EXECUTION',
  fullName: 'Trading & Order Management',
  version: '1.0.0',
  description: 'Trading execution, order management, and market operations',
  dependencies: ['shared', 'governance', 'indira'],
  runtimeUsage: 'VERY_HIGH',
  components: [
    'FabricPage',
    'ExecutionPage',
    'TradingPage',
    'MarketsPage',
    // ... additional components
  ],
  widgets: [
    'OrderForm',
    'SLTPBuilder',
    'PositionsPanel',
    // ... additional widgets
  ],
  apis: [
    'fabric',
    'markets',
    'signals',
    'memecoin',
  ],
  routes: [
    '/fabric',
    '/execution',
    '/trading',
    '/markets',
  ],
};

/**
 * EXECUTION Domain Public API Surface
 */
export const EXECUTION_PUBLIC_API = {
  // Component exports will be dynamically populated
  // Widget exports will be dynamically populated
  // Service exports will be dynamically populated
  // Hook exports will be dynamically populated
};