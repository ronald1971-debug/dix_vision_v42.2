/**
 * LEARNING Domain Module
 * Adaptive Intelligence Domain
 * 
 * This domain handles learning systems, memory management,
 * adaptive intelligence, and knowledge accumulation.
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
 * LEARNING Domain Information
 */
export const LEARNING_DOMAIN_INFO = {
  name: 'LEARNING',
  fullName: 'Adaptive Intelligence',
  version: '1.0.0',
  description: 'Learning systems, memory management, and adaptive intelligence',
  dependencies: ['shared', 'indira', 'dyon'],
  runtimeUsage: 'MEDIUM',
  components: [
    'MemoryPage',
    'IndiraLearningPage',
    'DyonLearningPage',
    // ... additional components
  ],
  widgets: [
    'IndiraLearningMode',
    // ... learning-specific widgets
  ],
  apis: ['memory'],
  routes: [
    '/memory',
    '/indira-learning',
    '/dyon-learning',
  ],
};

/**
 * LEARNING Domain Public API Surface
 */
export const LEARNING_PUBLIC_API = {
  // Component exports will be dynamically populated
  // Widget exports will be dynamically populated
  // Service exports will be dynamically populated
  // Hook exports will be dynamically populated
};