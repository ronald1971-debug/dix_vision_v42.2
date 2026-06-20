/**
 * SIMULATION Domain Module
 * Testing & Backtesting Domain
 * 
 * This domain handles simulation testing, backtesting,
 * strategy validation, and performance analysis.
 */

// Component exports (to be added during component migration)
// export * from './components';

// Widget exports (to be added during widget migration)
// export * from './widgets';

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
 * SIMULATION Domain Information
 */
export const SIMULATION_DOMAIN_INFO = {
  name: 'SIMULATION',
  fullName: 'Testing & Backtesting',
  version: '1.0.0',
  description: 'Simulation testing, backtesting, and strategy validation',
  dependencies: ['shared', 'execution'],
  runtimeUsage: 'MEDIUM',
  components: [
    'SimulationPage',
    'TestingPage',
    // ... additional components
  ],
  widgets: [
    // ... simulation-specific widgets
  ],
  apis: [
    'simulation',
    'testing',
  ],
  routes: [
    '/simulation',
    '/testing',
  ],
};

/**
 * SIMULATION Domain Public API Surface
 */
export const SIMULATION_PUBLIC_API = {
  // Component exports will be dynamically populated
  // Widget exports will be dynamically populated
  // Service exports will be dynamically populated
  // Hook exports will be dynamically populated
};