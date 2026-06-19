/**
 * DYON Domain Module
 * System Cognitive Intelligence Domain
 * 
 * This domain handles system intelligence, architecture analysis,
 * system optimization, and technical cognitive capabilities.
 */

// exports will be added during component migration phase

/**
 * DYON Domain Information
 */
export const DYON_DOMAIN_INFO = {
  name: 'DYON',
  fullName: 'System Cognitive Intelligence',
  version: '1.0.0',
  description: 'System intelligence, architecture analysis, and optimization',
  dependencies: ['shared', 'world_model'],
  runtimeUsage: 'HIGH',
  components: [
    'DyonWorkspacePage',
    'DyonLearningPage',
    // ... additional components
  ],
  widgets: [
    'DyonWorkspace',
    'DyonArchitectureStream',
    'DyonChat',
    // ... additional widgets
  ],
  apis: [],
  routes: [
    '/dyon',
    '/architecture',
  ],
};

/**
 * DYON Domain Public API Surface
 */
export const DYON_PUBLIC_API = {
  // Component exports will be dynamically populated
  // Widget exports will be dynamically populated
  // Service exports will be dynamically populated
  // Hook exports will be dynamically populated
};