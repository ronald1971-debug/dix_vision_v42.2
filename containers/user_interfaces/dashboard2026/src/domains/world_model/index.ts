/**
 * WORLD_MODEL Domain Module
 * World State Management Domain
 * 
 * This domain handles world state modeling, regime tracking,
 * market context analysis, and world understanding.
 */

// exports will be added during component migration phase

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