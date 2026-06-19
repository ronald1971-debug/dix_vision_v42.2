/**
 * Access Control System
 * DIX VISION v42.2 - Phase 15: Security and Compliance Enhancements (Weeks 49-52)
 */

export interface AccessControlSystem {
  systemId: string;
  users: Map<string, User>;
  roles: Map<string, Role>;
  permissions: Map<string, Permission>;
  groups: Map<string, Group>;
  policies: AccessPolicy[];
  sessions: Map<string, AccessSession>;
  requests: AccessRequest[];
  config: AccessControlConfig;
  lastUpdated: number;
}

export interface User {
  userId: string;
  username: string;
  email: string;
  roleIds: string[];
  groupIds: string[];
  permissions: Permission[];
  status: UserStatus;
  profile: UserProfile;
  security: UserSecurity;
  createdAt: number;
  lastModified: number;
  lastLogin: number;
}

export type UserStatus = 'active' | 'inactive' | 'suspended' | 'locked' | 'pending';

export interface UserProfile {
  firstName?: string;
  lastName?: string;
  department?: string;
  jobTitle?: string;
  location?: string;
  timezone?: string;
  language?: string;
}

export interface UserSecurity {
  passwordLastChanged: number;
  passwordExpiry: number;
  mfaEnabled: boolean;
  mfaSecret?: string;
  failedLoginAttempts: number;
  lockedUntil?: number;
  securityQuestions?: SecurityQuestion[];
}

export interface SecurityQuestion {
  question: string;
  answer: string;
  hash: string;
}

export interface Role {
  roleId: string;
  name: string;
  description: string;
  permissions: Permission[];
  inheritsFrom?: string[];
  isSystem: boolean;
  createdAt: number;
}

export interface Permission {
  permissionId: string;
  name: string;
  resource: string;
  action: string;
  conditions?: PermissionCondition[];
  isSystem: boolean;
}

export interface PermissionCondition {
  type: 'time' | 'ip' | 'location' | 'custom';
  operator: 'equals' | 'not-equals' | 'contains' | 'not-contains';
  value: string | string[];
}

export interface Group {
  groupId: string;
  name: string;
  description: string;
  memberIds: string[];
  permissionIds: string[];
  createdAt: number;
}

export interface AccessPolicy {
  policyId: string;
  name: string;
  type: PolicyType;
  rules: AccessRule[];
  priority: number;
  enabled: boolean;
  description: string;
}

export type PolicyType = 'rbac' | 'abac' | 'pbac' | 'custom';

export interface AccessRule {
  ruleId: string;
  subject: Subject;
  resource: Resource;
  action: string;
  effect: 'allow' | 'deny';
  conditions?: RuleCondition[];
}

export interface Subject {
  type: 'user' | 'role' | 'group';
  id: string;
}

export interface Resource {
  type: string;
  id: string;
  attributes?: Record<string, any>;
}

export interface RuleCondition {
  type: 'time' | 'ip' | 'location' | 'attribute';
  operator: string;
  value: any;
}

export interface AccessSession {
  sessionId: string;
  userId: string;
  token: string;
  permissions: Permission[];
  grantedAt: number;
  expiresAt: number;
  ipAddress: string;
  userAgent: string;
  deviceId: string;
  lastActivity: number;
}

export interface AccessRequest {
  requestId: string;
  userId: string;
  requestedResource: string;
  requestedAction: string;
  reason: string;
  status: RequestStatus;
  requestedAt: number;
  reviewedAt?: number;
  reviewedBy?: string;
  decision?: AccessDecision;
}

export type RequestStatus = 'pending' | 'approved' | 'denied' | 'cancelled';

export interface AccessDecision {
  granted: boolean;
  reason: string;
  conditions?: string[];
  expiry?: number;
}

export interface AccessControlConfig {
  defaultRole: string;
  sessionTimeout: number;
  maxConcurrentSessions: number;
  passwordPolicy: PasswordPolicy;
  mfaRequired: boolean;
  ipWhitelist: string[];
  ipBlacklist: string[];
  auditAccess: boolean;
}

export interface PasswordPolicy {
  minLength: number;
  maxLength: number;
  requireUppercase: boolean;
  requireLowercase: boolean;
  requireNumbers: boolean;
  requireSpecialChars: boolean;
  preventReuse: number;
  expirationDays: number;
  lockoutThreshold: number;
  lockoutDuration: number;
}

class AccessControlSystemImplementation {
  private system: AccessControlSystem;

  constructor() {
    this.system = {
      systemId: 'access_control_001',
      users: new Map(),
      roles: new Map(),
      permissions: new Map(),
      groups: new Map(),
      policies: [],
      sessions: new Map(),
      requests: [],
      config: {
        defaultRole: 'viewer',
        sessionTimeout: 86400000,
        maxConcurrentSessions: 5,
        passwordPolicy: {
          minLength: 12,
          maxLength: 128,
          requireUppercase: true,
          requireLowercase: true,
          requireNumbers: true,
          requireSpecialChars: true,
          preventReuse: 5,
          expirationDays: 90,
          lockoutThreshold: 5,
          lockoutDuration: 900000
        },
        mfaRequired: true,
        ipWhitelist: [],
        ipBlacklist: [],
        auditAccess: true
      },
      lastUpdated: Date.now()
    };
  }

  initialize(): void {
    this.loadDefaultRoles();
    this.loadDefaultPermissions();
    this.loadDefaultPolicies();
  }

  private loadDefaultRoles(): void {
    const roles: Role[] = [
      {
        roleId: 'admin',
        name: 'Administrator',
        description: 'Full system access',
        permissions: [],
        isSystem: true,
        createdAt: Date.now()
      },
      {
        roleId: 'manager',
        name: 'Manager',
        description: 'Team management access',
        permissions: [],
        isSystem: true,
        createdAt: Date.now()
      },
      {
        roleId: 'trader',
        name: 'Trader',
        description: 'Trading operations access',
        permissions: [],
        isSystem: true,
        createdAt: Date.now()
      },
      {
        roleId: 'analyst',
        name: 'Analyst',
        description: 'Analytics and reporting access',
        permissions: [],
        isSystem: true,
        createdAt: Date.now()
      },
      {
        roleId: 'viewer',
        name: 'Viewer',
        description: 'Read-only access',
        permissions: [],
        isSystem: true,
        createdAt: Date.now()
      }
    ];

    roles.forEach(role => this.system.roles.set(role.roleId, role));
  }

  private loadDefaultPermissions(): void {
    const permissions: Permission[] = [
      { permissionId: 'all_access', name: 'All Access', resource: '*', action: '*', isSystem: true },
      { permissionId: 'read_all', name: 'Read All', resource: '*', action: 'read', isSystem: true },
      { permissionId: 'write_all', name: 'Write All', resource: '*', action: 'write', isSystem: true },
      { permissionId: 'delete_all', name: 'Delete All', resource: '*', action: 'delete', isSystem: true },
      { permissionId: 'trading_execute', name: 'Execute Trades', resource: 'trading', action: 'execute', isSystem: false },
      { permissionId: 'trading_view', name: 'View Trades', resource: 'trading', action: 'read', isSystem: false },
      { permissionId: 'analytics_view', name: 'View Analytics', resource: 'analytics', action: 'read', isSystem: false },
      { permissionId: 'users_manage', name: 'Manage Users', resource: 'users', action: 'write', isSystem: false }
    ];

    permissions.forEach(permission => this.system.permissions.set(permission.permissionId, permission));
  }

  private loadDefaultPolicies(): void {
    this.system.policies = [
      {
        policyId: 'policy_default_allow',
        name: 'Default Allow',
        type: 'rbac',
        rules: [],
        priority: 100,
        enabled: true,
        description: 'Default policy allowing access based on roles'
      },
      {
        policyId: 'policy_admin_deny',
        name: 'Admin Deny',
        type: 'abac',
        rules: [
          {
            ruleId: 'admin_time_restrict',
            subject: { type: 'user', id: 'admin' },
            resource: { type: '*', id: '*' },
            action: '*',
            effect: 'deny',
            conditions: [
              { type: 'time', operator: 'not-equals', value: 'business-hours' }
            ]
          }
        ],
        priority: 10,
        enabled: false,
        description: 'Restrict admin access outside business hours'
      }
    ];
  }

  async checkAccess(userId: string, resource: string, action: string): Promise<boolean> {
    const user = this.system.users.get(userId);
    if (!user || user.status !== 'active') return false;

    const userPermissions = this.getUserPermissions(user);
    return userPermissions.some(p => 
      (p.resource === '*' || p.resource === resource) && 
      (p.action === '*' || p.action === action)
    );
  }

  private getUserPermissions(user: User): Permission[] {
    const permissions: Permission[] = [];

    // Get role permissions
    user.roleIds.forEach(roleId => {
      const role = this.system.roles.get(roleId);
      if (role) {
        role.permissions.forEach((p: Permission) => permissions.push(p));
      }
    });

    // Get group permissions
    user.groupIds.forEach(groupId => {
      const group = this.system.groups.get(groupId);
      if (group) {
        group.permissionIds.forEach(permId => {
          const perm = this.system.permissions.get(permId);
          if (perm) permissions.push(perm);
        });
      }
    });

    // Add direct permissions
    permissions.push(...user.permissions);

    return permissions;
  }

  async grantPermission(userId: string, permissionId: string): Promise<void> {
    const user = this.system.users.get(userId);
    const permission = this.system.permissions.get(permissionId);

    if (user && permission) {
      user.permissions.push(permission);
      this.system.lastUpdated = Date.now();
    }
  }

  async revokePermission(userId: string, permissionId: string): Promise<void> {
    const user = this.system.users.get(userId);
    if (user) {
      user.permissions = user.permissions.filter(p => p.permissionId !== permissionId);
      this.system.lastUpdated = Date.now();
    }
  }

  async assignRole(userId: string, roleId: string): Promise<void> {
    const user = this.system.users.get(userId);
    const role = this.system.roles.get(roleId);

    if (user && role) {
      if (!user.roleIds.includes(roleId)) {
        user.roleIds.push(roleId);
        this.system.lastUpdated = Date.now();
      }
    }
  }

  async removeRole(userId: string, roleId: string): Promise<void> {
    const user = this.system.users.get(userId);
    if (user) {
      user.roleIds = user.roleIds.filter((id: string) => id !== roleId);
      this.system.lastUpdated = Date.now();
    }
  }

  async addUserToGroup(userId: string, groupId: string): Promise<void> {
    const user = this.system.users.get(userId);
    const group = this.system.groups.get(groupId);

    if (user && group) {
      if (!group.memberIds.includes(userId)) {
        group.memberIds.push(userId);
      }
      if (!user.groupIds.includes(groupId)) {
        user.groupIds.push(groupId);
      }
      this.system.lastUpdated = Date.now();
    }
  }

  async removeUserFromGroup(userId: string, groupId: string): Promise<void> {
    const user = this.system.users.get(userId);
    const group = this.system.groups.get(groupId);

    if (group) {
      group.memberIds = group.memberIds.filter((id: string) => id !== userId);
    }
    if (user) {
      user.groupIds = user.groupIds.filter((id: string) => id !== groupId);
    }

    this.system.lastUpdated = Date.now();
  }

  async requestAccess(userId: string, resource: string, action: string, reason: string): Promise<AccessRequest> {
    const request: AccessRequest = {
      requestId: `request_${Date.now()}`,
      userId,
      requestedResource: resource,
      requestedAction: action,
      reason,
      status: 'pending',
      requestedAt: Date.now()
    };

    this.system.requests.push(request);
    this.system.lastUpdated = Date.now();

    return request;
  }

  async approveRequest(requestId: string, reviewerId: string, decision: AccessDecision): Promise<void> {
    const request = this.system.requests.find(r => r.requestId === requestId);
    if (request && request.status === 'pending') {
      request.status = decision.granted ? 'approved' : 'denied';
      request.reviewedAt = Date.now();
      request.reviewedBy = reviewerId;
      request.decision = decision;
      this.system.lastUpdated = Date.now();

      if (decision.granted) {
        const user = this.system.users.get(request.userId);
        if (user) {
          const tempPermission: Permission = {
            permissionId: `temp_${requestId}`,
            name: `Temporary Access for ${request.requestedResource}`,
            resource: request.requestedResource,
            action: request.requestedAction,
            isSystem: false
          };
          user.permissions.push(tempPermission);

          if (decision.expiry) {
            setTimeout(() => {
              this.revokePermission(request.userId, tempPermission.permissionId);
            }, decision.expiry - Date.now());
          }
        }
      }
    }
  }

  getUser(userId: string): User | undefined {
    return this.system.users.get(userId);
  }

  getAllUsers(): User[] {
    return Array.from(this.system.users.values());
  }

  getRole(roleId: string): Role | undefined {
    return this.system.roles.get(roleId);
  }

  getAllRoles(): Role[] {
    return Array.from(this.system.roles.values());
  }

  getConfig(): AccessControlConfig {
    return this.system.config;
  }
}

export const accessControlSystem = new AccessControlSystemImplementation();
export default AccessControlSystemImplementation;