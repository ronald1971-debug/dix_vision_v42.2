/**
 * Security and Compliance Enhancements - Phase 15 Index
 * DIX VISION v42.2 - Phase 15: Security and Compliance Enhancements (Weeks 49-52)
 */

export { advancedSecurityFramework } from '../SecurityFramework';
export type {
  SecurityFramework,
  SecurityConfig,
  PasswordPolicy,
  EncryptionManager,
  EncryptedData,
  AuthenticationManager,
  Credentials,
  AuthenticationResult,
  User,
  UserRole,
  Permission,
  Session,
  AuthorizationManager,
  Role,
  ThreatDetectionSystem,
  ThreatScanResult,
  Threat,
  ThreatType,
  SecurityMetrics,
  SecurityPolicy,
  PolicyType,
  PolicyRule,
  PolicyAction,
  ComplianceStatus,
  SecurityComplianceFramework,
  SecurityComplianceRequirement,
  SecurityComplianceControl,
  UserActivity
} from '../SecurityFramework';

export { complianceMonitoringSystem } from '../ComplianceMonitoring';
export type {
  ComplianceMonitoringSystem,
  ComplianceFramework,
  ComplianceRequirement,
  ComplianceControl,
  ControlStatus,
  ControlImplementation,
  Evidence,
  ComplianceAssessment,
  AssessmentFinding,
  RemediationPlan,
  ComplianceViolation,
  Resolution,
  CompliancePolicy
} from '../ComplianceMonitoring';

export { auditLogSystem } from '../AuditLogSystem';
export type {
  AuditLogSystem,
  AuditConfig,
  LogLevel,
  AuditLog,
  LogCategory,
  LogDetails,
  Change,
  RetentionPolicy,
  RetentionRule,
  LogIndexing,
  AuditQuery,
  AuditSearchResult,
  AuditReport,
  AuditSummary,
  UserActivitySummary,
  ActionSummary,
  Anomaly,
  AnomalyType,
  ComplianceIssue
} from '../AuditLogSystem';

export { accessControlSystem } from '../AccessControl';
export type {
  AccessControlSystem,
  UserStatus,
  UserProfile,
  UserSecurity,
  SecurityQuestion,
  PermissionCondition,
  Group,
  AccessPolicy,
  AccessRule,
  Subject,
  Resource,
  RuleCondition,
  AccessSession,
  AccessRequest,
  RequestStatus,
  AccessDecision,
  AccessControlConfig
} from '../AccessControl';