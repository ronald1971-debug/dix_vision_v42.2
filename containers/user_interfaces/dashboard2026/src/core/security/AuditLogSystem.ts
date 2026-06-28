/**
 * Audit Logging and Tracking System
 * DIX VISION v42.2 - Phase 15: Security and Compliance Enhancements (Weeks 49-52)
 */

export interface AuditLogSystem {
  systemId: string;
  logs: AuditLog[];
  config: AuditConfig;
  retention: RetentionPolicy;
  indexing: LogIndexing;
  lastUpdated: number;
}

export interface AuditConfig {
  logLevel: LogLevel;
  logAllActions: boolean;
  logSensitiveData: boolean;
  logMetadata: boolean;
  compressOldLogs: boolean;
  archiveEnabled: boolean;
  realTimeEnabled: boolean;
}

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'critical';

export interface AuditLog {
  logId: string;
  timestamp: number;
  level: LogLevel;
  category: LogCategory;
  userId: string;
  sessionId: string;
  action: string;
  resource: string;
  details: LogDetails;
  ipAddress: string;
  userAgent: string;
  success: boolean;
  duration?: number;
  metadata?: Record<string, any>;
}

export type LogCategory = 
  | 'authentication'
  | 'authorization'
  | 'data-access'
  | 'data-modification'
  | 'system'
  | 'compliance'
  | 'security'
  | 'error';

export interface LogDetails {
  previousValue?: any;
  newValue?: any;
  changes?: Change[];
  reason?: string;
  relatedLogs?: string[];
}

export interface Change {
  field: string;
  previous: any;
  current: any;
}

export interface RetentionPolicy {
  enabled: boolean;
  retentionPeriod: number; // days
  archiveAfter: number; // days
  deleteAfter: number; // days
  categories: Map<LogCategory, RetentionRule>;
}

export interface RetentionRule {
  retentionPeriod: number;
  archiveAfter: number;
  deleteAfter: number;
}

export interface LogIndexing {
  enabled: boolean;
  fields: string[];
  searchEnabled: boolean;
  aggregationEnabled: boolean;
}

export interface AuditQuery {
  startTime?: number;
  endTime?: number;
  userId?: string;
  category?: LogCategory;
  level?: LogLevel;
  action?: string;
  resource?: string;
  ipAddress?: string;
  limit?: number;
  offset?: number;
}

export interface AuditSearchResult {
  logs: AuditLog[];
  total: number;
  queryTime: number;
  hasMore: boolean;
}

export interface AuditReport {
  reportId: string;
  generatedAt: number;
  period: { start: number; end: number };
  summary: AuditSummary;
  topUsers: UserActivitySummary[];
  topActions: ActionSummary[];
  anomalies: Anomaly[];
  complianceIssues: ComplianceIssue[];
}

export interface AuditSummary {
  totalLogs: number;
  logsByLevel: Map<LogLevel, number>;
  logsByCategory: Map<LogCategory, number>;
  failedActions: number;
  successfulActions: number;
  averageDuration: number;
}

export interface UserActivitySummary {
  userId: string;
  username: string;
  totalActions: number;
  failedActions: number;
  uniqueResources: number;
  lastActivity: number;
}

export interface ActionSummary {
  action: string;
  count: number;
  successRate: number;
  averageDuration: number;
  category: LogCategory;
}

export interface Anomaly {
  anomalyId: string;
  type: AnomalyType;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  logs: string[];
  timestamp: number;
}

export type AnomalyType = 
  | 'unusual-pattern'
  | 'volume-spike'
  | 'off-hours-access'
  | 'geo-anomaly'
  | 'privilege-escalation'
  | 'data-exfiltration';

export interface ComplianceIssue {
  issueId: string;
  type: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
  logs: string[];
  remediation: string[];
}

class AuditLogSystemImplementation {
  private system: AuditLogSystem;
  private isInitialized: boolean = false;

  constructor() {
    this.system = {
      systemId: 'audit_log_001',
      logs: [],
      config: {
        logLevel: 'info',
        logAllActions: true,
        logSensitiveData: false,
        logMetadata: true,
        compressOldLogs: true,
        archiveEnabled: true,
        realTimeEnabled: true
      },
      retention: {
        enabled: true,
        retentionPeriod: 365,
        archiveAfter: 90,
        deleteAfter: 1095,
        categories: new Map([
          ['authentication', { retentionPeriod: 365, archiveAfter: 90, deleteAfter: 1825 }],
          ['compliance', { retentionPeriod: 2555, archiveAfter: 365, deleteAfter: 3650 }],
          ['security', { retentionPeriod: 2555, archiveAfter: 365, deleteAfter: 3650 }]
        ])
      },
      indexing: {
        enabled: true,
        fields: ['userId', 'category', 'action', 'resource', 'timestamp'],
        searchEnabled: true,
        aggregationEnabled: true
      },
      lastUpdated: Date.now()
    };
  }

  initialize(): void {
    this.isInitialized = true;
  }

  async log(log: Omit<AuditLog, 'logId' | 'timestamp'>): Promise<string> {
    const auditLog: AuditLog = {
      logId: `log_${Date.now()}_${Math.random().toString(36).substring(7)}`,
      timestamp: Date.now(),
      ...log
    };

    this.system.logs.push(auditLog);
    this.system.lastUpdated = Date.now();

    return auditLog.logId;
  }

  async query(query: AuditQuery): Promise<AuditSearchResult> {
    let filteredLogs = [...this.system.logs];

    if (query.startTime) {
      filteredLogs = filteredLogs.filter(l => l.timestamp >= query.startTime);
    }
    if (query.endTime) {
      filteredLogs = filteredLogs.filter(l => l.timestamp <= query.endTime);
    }
    if (query.userId) {
      filteredLogs = filteredLogs.filter(l => l.userId === query.userId);
    }
    if (query.category) {
      filteredLogs = filteredLogs.filter(l => l.category === query.category);
    }
    if (query.level) {
      filteredLogs = filteredLogs.filter(l => l.level === query.level);
    }
    if (query.action) {
      filteredLogs = filteredLogs.filter(l => l.action === query.action);
    }
    if (query.resource) {
      filteredLogs = filteredLogs.filter(l => l.resource === query.resource);
    }
    if (query.ipAddress) {
      filteredLogs = filteredLogs.filter(l => l.ipAddress === query.ipAddress);
    }

    const total = filteredLogs.length;
    const offset = query.offset || 0;
    const limit = query.limit || 100;

    filteredLogs = filteredLogs.slice(offset, offset + limit);

    return {
      logs: filteredLogs,
      total,
      queryTime: Date.now(),
      hasMore: offset + limit < total
    };
  }

  async generateReport(period: { start: number; end: number }): Promise<AuditReport> {
    const logsInRange = this.system.logs.filter(l => l.timestamp >= period.start && l.timestamp <= period.end);

    const summary: AuditSummary = {
      totalLogs: logsInRange.length,
      logsByLevel: this.groupByLevel(logsInRange),
      logsByCategory: this.groupByCategory(logsInRange),
      failedActions: logsInRange.filter(l => !l.success).length,
      successfulActions: logsInRange.filter(l => l.success).length,
      averageDuration: this.calculateAverageDuration(logsInRange)
    };

    const topUsers = this.calculateTopUsers(logsInRange);
    const topActions = this.calculateTopActions(logsInRange);
    const anomalies = this.detectAnomalies(logsInRange);
    const complianceIssues = this.detectComplianceIssues(logsInRange);

    return {
      reportId: `report_${Date.now()}`,
      generatedAt: Date.now(),
      period,
      summary,
      topUsers,
      topActions,
      anomalies,
      complianceIssues
    };
  }

  private groupByLevel(logs: AuditLog[]): Map<LogLevel, number> {
    const groups = new Map<LogLevel, number>();
    logs.forEach(log => {
      const count = groups.get(log.level) || 0;
      groups.set(log.level, count + 1);
    });
    return groups;
  }

  private groupByCategory(logs: AuditLog[]): Map<LogCategory, number> {
    const groups = new Map<LogCategory, number>();
    logs.forEach(log => {
      const count = groups.get(log.category) || 0;
      groups.set(log.category, count + 1);
    });
    return groups;
  }

  private calculateAverageDuration(logs: AuditLog[]): number {
    const logsWithDuration = logs.filter(l => l.duration !== undefined);
    if (logsWithDuration.length === 0) return 0;
    const total = logsWithDuration.reduce((sum, l) => sum + (l.duration || 0), 0);
    return total / logsWithDuration.length;
  }

  private calculateTopUsers(logs: AuditLog[]): UserActivitySummary[] {
    const userMap = new Map<string, UserActivitySummary>();

    logs.forEach(log => {
      const existing = userMap.get(log.userId);
      if (existing) {
        existing.totalActions++;
        if (!log.success) existing.failedActions++;
        existing.lastActivity = Math.max(existing.lastActivity, log.timestamp);
      } else {
        userMap.set(log.userId, {
          userId: log.userId,
          username: log.userId,
          totalActions: 1,
          failedActions: log.success ? 0 : 1,
          uniqueResources: 1,
          lastActivity: log.timestamp
        });
      }
    });

    return Array.from(userMap.values())
      .sort((a, b) => b.totalActions - a.totalActions)
      .slice(0, 10);
  }

  private calculateTopActions(logs: AuditLog[]): ActionSummary[] {
    const actionMap = new Map<string, ActionSummary>();

    logs.forEach(log => {
      const existing = actionMap.get(log.action);
      if (existing) {
        existing.count++;
        if (log.success) {
          existing.successRate = (existing.successRate * (existing.count - 1) + 1) / existing.count;
        }
      } else {
        actionMap.set(log.action, {
          action: log.action,
          count: 1,
          successRate: log.success ? 1 : 0,
          averageDuration: log.duration || 0,
          category: log.category
        });
      }
    });

    return Array.from(actionMap.values())
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }

  private detectAnomalies(logs: AuditLog[]): Anomaly[] {
    const anomalies: Anomaly[] = [];
    const actionCounts = new Map<string, number>();

    logs.forEach(log => {
      const key = `${log.userId}_${log.action}`;
      actionCounts.set(key, (actionCounts.get(key) || 0) + 1);
    });

    actionCounts.forEach((count, key) => {
      if (count > 100) {
        anomalies.push({
          anomalyId: `anomaly_${Date.now()}`,
          type: 'volume-spike',
          severity: 'high',
          description: `Unusual volume of actions: ${count} for ${key}`,
          logs: [],
          timestamp: Date.now()
        });
      }
    });

    return anomalies;
  }

  private detectComplianceIssues(logs: AuditLog[]): ComplianceIssue[] {
    const issues: ComplianceIssue[] = [];
    const failedAuthLogs = logs.filter(l => l.category === 'authentication' && !l.success);

    if (failedAuthLogs.length > 10) {
      issues.push({
        issueId: `issue_${Date.now()}`,
        type: 'security',
        severity: 'high',
        description: 'High number of failed authentication attempts',
        logs: failedAuthLogs.slice(0, 10).map(l => l.logId),
        remediation: ['Review access logs', 'Block suspicious IPs', 'Enable account lockout']
      });
    }

    return issues;
  }

  applyRetentionPolicy(): void {
    if (!this.system.retention.enabled) return;

    const now = Date.now();
    const dayMs = 86400000;

    this.system.logs = this.system.logs.filter(log => {
      const ageInDays = (now - log.timestamp) / dayMs;
      const rule = this.system.retention.categories.get(log.category);
      const retentionDays = rule?.retentionPeriod || this.system.retention.retentionPeriod;
      return ageInDays <= retentionDays;
    });
  }

  getConfig(): AuditConfig {
    return this.system.config;
  }

  updateConfig(config: Partial<AuditConfig>): void {
    this.system.config = { ...this.system.config, ...config };
    this.system.lastUpdated = Date.now();
  }
}

export const auditLogSystem = new AuditLogSystemImplementation();
export default AuditLogSystemImplementation;