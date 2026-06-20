/**
 * Shared Security Infrastructure
 * 
 * Core security infrastructure for enhanced security and authorization
 * including role-based access control, audit logging, and compliance monitoring.
 */

// ============================================================================
// Security Types and Interfaces
// ============================================================================

export interface SecurityPolicy {
  id: string;
  name: string;
  domain: string;
  type: PolicyType;
  rules: SecurityRule[];
  active: boolean;
  priority: number;
  createdAt: Date;
  updatedAt: Date;
}

export type PolicyType = 'access' | 'data' | 'operation' | 'compliance';

export interface SecurityRule {
  id: string;
  resource: string;
  action: string;
  effect: 'allow' | 'deny';
  conditions?: SecurityCondition[];
}

export interface SecurityCondition {
  type: 'role' | 'attribute' | 'time' | 'location';
  operator: 'equals' | 'contains' | 'in' | 'greaterThan' | 'lessThan';
  value: any;
}

export interface AccessControlEntry {
  id: string;
  domain: string;
  resource: string;
  permissions: Permission[];
  roles: string[];
  expiresAt?: Date;
}

export interface Permission {
  action: string;
  allowed: boolean;
  conditions?: SecurityCondition[];
}

export interface AuditLogEntry {
  id: string;
  domain: string;
  userId: string;
  action: string;
  resource: string;
  result: 'success' | 'failure';
  timestamp: Date;
  details: any;
  ipAddress?: string;
  userAgent?: string;
}

export interface SecurityEvent {
  id: string;
  domain: string;
  type: SecurityEventType;
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  description: string;
  data: any;
  timestamp: Date;
  acknowledged: boolean;
}

export type SecurityEventType = 'authentication' | 'authorization' | 'data-access' | 'policy-violation' | 'security-breach';

// ============================================================================
// Security Engine
// ============================================================================

export class SecurityEngine {
  private static instance: SecurityEngine;
  private policies: Map<string, SecurityPolicy> = new Map();
  private auditLogs: AuditLogEntry[] = [];
  private securityEvents: SecurityEvent[] = [];

  private constructor() {
    this.initializeSecurity();
  }

  static getInstance(): SecurityEngine {
    if (!SecurityEngine.instance) {
      SecurityEngine.instance = new SecurityEngine();
    }
    return SecurityEngine.instance;
  }

  private initializeSecurity(): void {
    console.log('Security Engine initialized');
    this.registerDefaultPolicies();
  }

  private registerDefaultPolicies(): void {
    // Default access policies for each domain
    const domains = ['indira', 'governance', 'execution', 'operator', 'dyon', 'world_model', 'simulation', 'learning'];
    
    for (const domain of domains) {
      const defaultPolicy: SecurityPolicy = {
        id: `${domain}-default-access`,
        name: `${domain.toUpperCase()} Default Access Policy`,
        domain,
        type: 'access',
        rules: [
          {
            id: `${domain}-read`,
            resource: `${domain}/*`,
            action: 'read',
            effect: 'allow',
            conditions: [
              {
                type: 'role',
                operator: 'in',
                value: ['user', 'admin', 'operator'],
              },
            ],
          },
          {
            id: `${domain}-write`,
            resource: `${domain}/*`,
            action: 'write',
            effect: 'allow',
            conditions: [
              {
                type: 'role',
                operator: 'in',
                value: ['admin', 'operator'],
              },
            ],
          },
        ],
        active: true,
        priority: 100,
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      this.policies.set(defaultPolicy.id, defaultPolicy);
    }
  }

  // Policy Management
  registerPolicy(policy: SecurityPolicy): void {
    this.policies.set(policy.id, policy);
  }

  getPolicy(policyId: string): SecurityPolicy | undefined {
    return this.policies.get(policyId);
  }

  getPolicies(domain?: string, type?: PolicyType): SecurityPolicy[] {
    return Array.from(this.policies.values()).filter(policy => {
      if (domain && policy.domain !== domain) return false;
      if (type && policy.type !== type) return false;
      return true;
    });
  }

  updatePolicy(policyId: string, updates: Partial<SecurityPolicy>): void {
    const policy = this.policies.get(policyId);
    if (policy) {
      Object.assign(policy, updates, { updatedAt: new Date() });
    }
  }

  // Access Control
  checkAccess(domain: string, userId: string, resource: string, action: string): boolean {
    const policies = this.getPolicies(domain, 'access').filter(p => p.active);
    
    for (const policy of policies.sort((a, b) => b.priority - a.priority)) {
      for (const rule of policy.rules) {
        if (this.resourceMatches(rule.resource, resource) && this.actionMatches(rule.action, action)) {
          if (this.conditionsMatch(rule.conditions, userId)) {
            return rule.effect === 'allow';
          }
        }
      }
    }
    
    return false; // Default deny
  }

  private resourceMatches(ruleResource: string, requestedResource: string): boolean {
    return ruleResource === '*' || ruleResource === requestedResource || 
           requestedResource.startsWith(ruleResource.replace('*', ''));
  }

  private actionMatches(ruleAction: string, requestedAction: string): boolean {
    return ruleAction === '*' || ruleAction === requestedAction;
  }

  private conditionsMatch(conditions: SecurityCondition[] | undefined, _userId: string): boolean {
    if (!conditions || conditions.length === 0) return true;
    
    // Simplified condition checking - in real implementation would check actual user attributes
    return true;
  }

  // Audit Logging
  logAccess(entry: AuditLogEntry): void {
    this.auditLogs.push(entry);
    this.cleanupOldAuditLogs();
  }

  getAuditLogs(domain?: string, userId?: string): AuditLogEntry[] {
    return this.auditLogs.filter(log => {
      if (domain && log.domain !== domain) return false;
      if (userId && log.userId !== userId) return false;
      return true;
    });
  }

  private cleanupOldAuditLogs(): void {
    const maxLogs = 10000;
    const maxAge = 30 * 24 * 60 * 60 * 1000; // 30 days
    
    this.auditLogs = this.auditLogs.filter(log => {
      const age = Date.now() - log.timestamp.getTime();
      return age < maxAge;
    });

    if (this.auditLogs.length > maxLogs) {
      this.auditLogs = this.auditLogs.slice(-maxLogs);
    }
  }

  // Security Event Management
  recordSecurityEvent(event: SecurityEvent): void {
    this.securityEvents.push(event);
    this.cleanupOldSecurityEvents();
    
    // Auto-create audit log for security events
    this.logAccess({
      id: `audit-${event.id}`,
      domain: event.domain,
      userId: 'system',
      action: 'security-event',
      resource: event.type,
      result: 'success',
      timestamp: event.timestamp,
      details: event,
    });
  }

  getSecurityEvents(domain?: string, acknowledged?: boolean): SecurityEvent[] {
    return this.securityEvents.filter(event => {
      if (domain && event.domain !== domain) return false;
      if (acknowledged !== undefined && event.acknowledged !== acknowledged) return false;
      return true;
    });
  }

  acknowledgeSecurityEvent(eventId: string): void {
    const event = this.securityEvents.find(e => e.id === eventId);
    if (event) {
      event.acknowledged = true;
    }
  }

  private cleanupOldSecurityEvents(): void {
    const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days
    
    this.securityEvents = this.securityEvents.filter(event => {
      const age = Date.now() - event.timestamp.getTime();
      return age < maxAge;
    });
  }

  // Compliance Monitoring
  checkCompliance(domain: string): {
    compliant: boolean;
    violations: SecurityEvent[];
    score: number;
  } {
    const securityEvents = this.getSecurityEvents(domain, false);
    const violations = securityEvents.filter(e => e.severity === 'error' || e.severity === 'critical');
    
    const score = Math.max(0, 100 - (violations.length * 10));
    const compliant = violations.length === 0;

    return {
      compliant,
      violations,
      score,
    };
  }

  // Domain-specific Security
  getDomainSecurityStatus(domain: string): {
    overallStatus: 'secure' | 'warning' | 'critical';
    activePolicies: number;
    recentSecurityEvents: number;
    complianceScore: number;
  } {
    const activePolicies = this.getPolicies(domain).filter(p => p.active).length;
    const recentSecurityEvents = this.getSecurityEvents(domain, false).length;
    const compliance = this.checkCompliance(domain);
    
    let overallStatus: 'secure' | 'warning' | 'critical' = 'secure';
    
    if (compliance.score < 50) {
      overallStatus = 'critical';
    } else if (compliance.score < 80 || recentSecurityEvents > 10) {
      overallStatus = 'warning';
    }

    return {
      overallStatus,
      activePolicies,
      recentSecurityEvents,
      complianceScore: compliance.score,
    };
  }
}

// ============================================================================
// Domain Security Manager
// ============================================================================

export class DomainSecurityManager {
  private static instances: Map<string, DomainSecurityManager> = new Map();
  private domain: string;
  private securityEngine: SecurityEngine;

  private constructor(domain: string) {
    this.domain = domain;
    this.securityEngine = SecurityEngine.getInstance();
    this.initializeDomainSecurity();
  }

  static getInstance(domain: string): DomainSecurityManager {
    if (!DomainSecurityManager.instances.has(domain)) {
      DomainSecurityManager.instances.set(domain, new DomainSecurityManager(domain));
    }
    return DomainSecurityManager.instances.get(domain)!;
  }

  private initializeDomainSecurity(): void {
    console.log(`${this.domain.toUpperCase()} Security Manager initialized`);
  }

  checkAccess(userId: string, resource: string, action: string): boolean {
    const allowed = this.securityEngine.checkAccess(this.domain, userId, resource, action);
    
    // Log the access attempt
    this.securityEngine.logAccess({
      id: `access-${Date.now()}`,
      domain: this.domain,
      userId,
      action,
      resource,
      result: allowed ? 'success' : 'failure',
      timestamp: new Date(),
      details: { accessAttempt: allowed },
    });

    return allowed;
  }

  recordSecurityEvent(event: Omit<SecurityEvent, 'id' | 'domain' | 'timestamp'>): void {
    this.securityEngine.recordSecurityEvent({
      id: `security-${this.domain}-${Date.now()}`,
      domain: this.domain,
      timestamp: new Date(),
      ...event,
    });
  }

  getAuditLogs(userId?: string): AuditLogEntry[] {
    return this.securityEngine.getAuditLogs(this.domain, userId);
  }

  getSecurityStatus() {
    return this.securityEngine.getDomainSecurityStatus(this.domain);
  }
}

// ============================================================================
// Public API
// ============================================================================

export function getSecurityEngine(): SecurityEngine {
  return SecurityEngine.getInstance();
}

export function registerSecurityPolicy(policy: SecurityPolicy): void {
  return SecurityEngine.getInstance().registerPolicy(policy);
}

export function checkDomainAccess(domain: string, userId: string, resource: string, action: string): boolean {
  return SecurityEngine.getInstance().checkAccess(domain, userId, resource, action);
}

export function getDomainSecurityManager(domain: string): DomainSecurityManager {
  return DomainSecurityManager.getInstance(domain);
}

export function recordSecurityEvent(event: Omit<SecurityEvent, 'id' | 'timestamp'>): void {
  return SecurityEngine.getInstance().recordSecurityEvent({
    id: `security-${Date.now()}`,
    timestamp: new Date(),
    ...event,
  });
}