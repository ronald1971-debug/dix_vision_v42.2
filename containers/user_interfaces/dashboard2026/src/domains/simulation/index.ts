/**
 * SIMULATION Domain Module
 * Testing & Backtesting Domain
 * 
 * This domain handles simulation testing, backtesting,
 * strategy validation, and performance analysis.
 */

// exports will be added during component migration phase

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