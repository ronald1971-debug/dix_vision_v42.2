/**
 * GOVERNANCE Domain Module
 * Policy & Risk Management Domain
 * 
 * This domain handles governance, risk management, audit trails,
 * policy enforcement, and regulatory compliance.
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
 * GOVERNANCE Domain Information
 */
export const GOVERNANCE_DOMAIN_INFO = {
  name: 'GOVERNANCE',
  fullName: 'Policy & Risk Management',
  version: '1.0.0',
  description: 'Governance, risk management, and regulatory compliance',
  dependencies: ['shared', 'operator'],
  runtimeUsage: 'VERY_HIGH',
  components: [
    'GovernancePage',
    'AuditPage',
    'RiskPage',
    'AlertsPage',
    // ... additional components
  ],
  widgets: [
    'PromotionGatesPanel',
    'HazardMonitorGrid',
    'ApprovalQueueWidget',
    // ... additional widgets
  ],
  apis: [
    'governance',
    'audit',
    'alerts',
    'credentials',
  ],
  routes: [
    '/governance',
    '/risk',
    '/alerts',
    '/audit',
  ],
};

/**
 * GOVERNANCE Domain Public API Surface
 */
export const GOVERNANCE_PUBLIC_API = {
  // Component exports will be dynamically populated
  // Widget exports will be dynamically populated
  // Service exports will be dynamically populated
  // Hook exports will be dynamically populated
};