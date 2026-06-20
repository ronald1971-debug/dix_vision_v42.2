/**
 * INDIRA Domain Module
 * Market Cognitive Intelligence Domain
 * 
 * This domain handles market intelligence, cognitive analysis, 
 * trading insights, and market prediction capabilities.
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
 * INDIRA Domain Information
 */
export const INDIRA_DOMAIN_INFO = {
  name: 'INDIRA',
  fullName: 'Market Cognitive Intelligence',
  version: '1.0.0',
  description: 'Market intelligence, cognitive analysis, and trading insights',
  dependencies: ['shared', 'world_model'],
  runtimeUsage: 'VERY_HIGH',
  components: [
    'IndiraCognitiveCenterPage',
    'IndiraWorkspacePage',
    'CognitiveObservatory',
    // ... additional components
  ],
  widgets: [
    'CognitiveObservatory',
    'IndiraLearningMode',
    'IndiraChat',
    // ... additional widgets
  ],
  apis: [
    'indiraIntelligence',
    'cognitive',
    'cognitive_chat',
    'memory',
  ],
  routes: [
    '/',
    '/indira-workspace',
    '/ai',
    '/cognitive-chat',
  ],
};

/**
 * INDIRA Domain Public API Surface
 */
export const INDIRA_PUBLIC_API = {
  // Component exports will be dynamically populated
  // Widget exports will be dynamically populated
  // Service exports will be dynamically populated
  // Hook exports will be dynamically populated
};