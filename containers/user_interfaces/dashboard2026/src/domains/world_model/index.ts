/**
 * WORLD_MODEL Domain Module
 * World State Management Domain
 * 
 * This domain handles world state modeling, regime tracking,
 * market context analysis, and world understanding.
 */

// Component exports (to be added during component migration)
// export * from './components';

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
 * WORLD_MODEL Domain Information
 */
export const WORLD_MODEL_DOMAIN_INFO = {
  name: 'WORLD_MODEL',
  fullName: 'World State Management',
  version: '1.0.0',
  description: 'World state modeling, regime tracking, and market context',
  dependencies: ['shared'],
  runtimeUsage: 'HIGH',
  components: [
    'ObservatoryPage',
    'MarketContextPage',
    // ... additional components
  ],
  widgets: [
    'CognitiveObservatory',
    'RegimeTimeline',
    // ... additional widgets
  ],
  apis: ['cognitive'], // shared with INDIRA
  routes: [
    '/observatory',
    '/market-context',
  ],
};

/**
 * WORLD_MODEL Domain Public API Surface
 */
export const WORLD_MODEL_PUBLIC_API = {
  // Component exports will be dynamically populated
  // Widget exports will be dynamically populated
  // Service exports will be dynamically populated
  // Hook exports will be dynamically populated
};