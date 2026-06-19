/**
 * LEARNING Domain Module
 * Adaptive Intelligence Domain
 * 
 * This domain handles learning systems, memory management,
 * adaptive intelligence, and knowledge accumulation.
 */

// exports will be added during component migration phase

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