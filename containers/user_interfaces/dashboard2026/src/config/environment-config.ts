/**
 * Environment Configuration Management
 * 
 * Comprehensive configuration management system for multi-environment deployment
 * including configuration validation, secret management, and runtime configuration.
 */

// ============================================================================
// Configuration Types
// ============================================================================

export type Environment = 'development' | 'staging' | 'production' | 'dr';

export interface EnvironmentConfig {
  name: Environment;
  region: string;
  infrastructure: InfrastructureConfig;
  database: DatabaseConfig;
  storage: StorageConfig;
  security: SecurityConfig;
  monitoring: MonitoringConfig;
  scaling: ScalingConfig;
}

export interface InfrastructureConfig {
  platform: 'aws' | 'azure' | 'gcp' | 'local';
  cluster: string;
  namespace: string;
  nodeCount: number;
  instanceType: string;
  availabilityZones: string[];
}

export interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  ssl: boolean;
  poolSize: number;
  timeout: number;
  replicas: number;
}

export interface StorageConfig {
  type: 's3' | 'azure-blob' | 'gcs' | 'local';
  bucket: string;
  region: string;
  encryption: boolean;
  lifecycleRules: LifecycleRule[];
}

export interface LifecycleRule {
  id: string;
  prefix: string;
  expirationDays: number;
  transitions: Transition[];
}

export interface Transition {
  storageClass: string;
  days: number;
}

export interface SecurityConfig {
  encryption: boolean;
  keyManagement: string;
  networkPolicies: NetworkPolicy[];
  authentication: AuthenticationConfig;
  authorization: AuthorizationConfig;
}

export interface NetworkPolicy {
  name: string;
  ingress: IngressRule[];
  egress: EgressRule[];
}

export interface IngressRule {
  from: string[];
  ports: number[];
  protocols: string[];
}

export interface EgressRule {
  to: string[];
  ports: number[];
  protocols: string[];
}

export interface AuthenticationConfig {
  method: 'oauth' | 'jwt' | 'api-key' | 'session';
  provider?: string;
  clientId?: string;
  clientSecret?: string;
  sessionTimeout: number;
}

export interface AuthorizationConfig {
  method: 'rbac' | 'abac' | 'custom';
  defaultPolicy: string;
  roleBindings: RoleBinding[];
}

export interface RoleBinding {
  role: string;
  users: string[];
  groups: string[];
}

export interface MonitoringConfig {
  enabled: boolean;
  metricsEndpoint: string;
  loggingEndpoint: string;
  tracingEndpoint: string;
  alertingEnabled: boolean;
  retentionDays: number;
  sampleRate: number;
}

export interface ScalingConfig {
  enabled: boolean;
  minReplicas: number;
  maxReplicas: number;
  targetCPU: number;
  targetMemory: number;
  scaleUpCooldown: number;
  scaleDownCooldown: number;
}

// ============================================================================
// Configuration Management
// ============================================================================

export class ConfigurationManager {
  private static instance: ConfigurationManager;
  private configs: Map<Environment, EnvironmentConfig> = new Map();
  private currentEnvironment: Environment = 'development';
  private overrides: Map<string, string> = new Map();

  private constructor() {
    this.initializeConfiguration();
  }

  static getInstance(): ConfigurationManager {
    if (!ConfigurationManager.instance) {
      ConfigurationManager.instance = new ConfigurationManager();
    }
    return ConfigurationManager.instance;
  }

  private initializeConfiguration(): void {
    // Load environment configurations
    this.loadDefaultConfigurations();
    
    // Load from environment variables
    this.loadFromEnvironment();
    
    // Load from config files
    this.loadFromFiles();
  }

  private loadDefaultConfigurations(): void {
    // Development Configuration
    const devConfig: EnvironmentConfig = {
      name: 'development',
      region: 'local',
      infrastructure: {
        platform: 'local',
        cluster: 'dev-cluster',
        namespace: 'development',
        nodeCount: 1,
        instanceType: 't2.medium',
        availabilityZones: ['local'],
      },
      database: {
        host: 'localhost',
        port: 5432,
        database: 'dix_vision_dev',
        username: 'dev_user',
        password: 'dev_password',
        ssl: false,
        poolSize: 5,
        timeout: 30000,
        replicas: 0,
      },
      storage: {
        type: 'local',
        bucket: 'dix-vision-dev',
        region: 'local',
        encryption: false,
        lifecycleRules: [],
      },
      security: {
        encryption: false,
        keyManagement: 'local',
        networkPolicies: [],
        authentication: {
          method: 'session',
          sessionTimeout: 3600,
        },
        authorization: {
          method: 'rbac',
          defaultPolicy: 'allow-all',
          roleBindings: [],
        },
      },
      monitoring: {
        enabled: true,
        metricsEndpoint: 'http://localhost:9090',
        loggingEndpoint: 'http://localhost:9200',
        tracingEndpoint: 'http://localhost:14268',
        alertingEnabled: false,
        retentionDays: 7,
        sampleRate: 1.0,
      },
      scaling: {
        enabled: false,
        minReplicas: 1,
        maxReplicas: 1,
        targetCPU: 80,
        targetMemory: 80,
        scaleUpCooldown: 60,
        scaleDownCooldown: 60,
      },
    };

    // Staging Configuration
    const stagingConfig: EnvironmentConfig = {
      name: 'staging',
      region: 'us-east-1',
      infrastructure: {
        platform: 'aws',
        cluster: 'staging-cluster',
        namespace: 'staging',
        nodeCount: 3,
        instanceType: 't3.large',
        availabilityZones: ['us-east-1a', 'us-east-1b', 'us-east-1c'],
      },
      database: {
        host: 'staging-db.example.com',
        port: 5432,
        database: 'dix_vision_staging',
        username: 'staging_user',
        password: 'staging_password',
        ssl: true,
        poolSize: 10,
        timeout: 30000,
        replicas: 1,
      },
      storage: {
        type: 's3',
        bucket: 'dix-vision-staging',
        region: 'us-east-1',
        encryption: true,
        lifecycleRules: [
          {
            id: 'dev-lifecycle',
            prefix: 'dev/',
            expirationDays: 7,
            transitions: [],
          },
        ],
      },
      security: {
        encryption: true,
        keyManagement: 'aws-kms',
        networkPolicies: [
          {
            name: 'staging-network-policy',
            ingress: [
              {
                from: ['0.0.0.0/0'],
                ports: [443, 80],
                protocols: ['TCP'],
              },
            ],
            egress: [
              {
                to: ['0.0.0.0/0'],
                ports: [443],
                protocols: ['TCP'],
              },
            ],
          },
        ],
        authentication: {
          method: 'oauth',
          provider: 'auth0',
          clientId: 'staging-client-id',
          clientSecret: 'staging-client-secret',
          sessionTimeout: 7200,
        },
        authorization: {
          method: 'rbac',
          defaultPolicy: 'allow-authenticated',
          roleBindings: [
            {
              role: 'admin',
              users: ['admin@example.com'],
              groups: ['admins'],
            },
            {
              role: 'user',
              users: ['*'],
              groups: ['users'],
            },
          ],
        },
      },
      monitoring: {
        enabled: true,
        metricsEndpoint: 'https://staging-metrics.example.com',
        loggingEndpoint: 'https://staging-logs.example.com',
        tracingEndpoint: 'https://staging-tracing.example.com',
        alertingEnabled: true,
        retentionDays: 30,
        sampleRate: 0.5,
      },
      scaling: {
        enabled: true,
        minReplicas: 2,
        maxReplicas: 10,
        targetCPU: 70,
        targetMemory: 70,
        scaleUpCooldown: 120,
        scaleDownCooldown: 300,
      },
    };

    // Production Configuration
    const prodConfig: EnvironmentConfig = {
      name: 'production',
      region: 'us-east-1',
      infrastructure: {
        platform: 'aws',
        cluster: 'prod-cluster',
        namespace: 'production',
        nodeCount: 6,
        instanceType: 'm5.large',
        availabilityZones: ['us-east-1a', 'us-east-1b', 'us-east-1c'],
      },
      database: {
        host: 'prod-db.example.com',
        port: 5432,
        database: 'dix_vision_prod',
        username: 'prod_user',
        password: 'prod_password',
        ssl: true,
        poolSize: 20,
        timeout: 30000,
        replicas: 2,
      },
      storage: {
        type: 's3',
        bucket: 'dix-vision-prod',
        region: 'us-east-1',
        encryption: true,
        lifecycleRules: [
          {
            id: 'production-lifecycle',
            prefix: 'logs/',
            expirationDays: 90,
            transitions: [
              {
                storageClass: 'STANDARD_IA',
                days: 30,
              },
              {
                storageClass: 'GLACIER',
                days: 60,
              },
            ],
          },
        ],
      },
      security: {
        encryption: true,
        keyManagement: 'aws-kms',
        networkPolicies: [
          {
            name: 'production-network-policy',
            ingress: [
              {
                from: ['0.0.0.0/0'],
                ports: [443],
                protocols: ['TCP'],
              },
            ],
            egress: [
              {
                to: ['0.0.0.0/0'],
                ports: [443],
                protocols: ['TCP'],
              },
            ],
          },
        ],
        authentication: {
          method: 'oauth',
          provider: 'auth0',
          clientId: 'prod-client-id',
          clientSecret: 'prod-client-secret',
          sessionTimeout: 3600,
        },
        authorization: {
          method: 'rbac',
          defaultPolicy: 'deny-all',
          roleBindings: [
            {
              role: 'admin',
              users: ['admin@example.com'],
              groups: ['admins'],
            },
            {
              role: 'operator',
              users: ['operator@example.com'],
              groups: ['operators'],
            },
            {
              role: 'user',
              users: ['*'],
              groups: ['users'],
            },
          ],
        },
      },
      monitoring: {
        enabled: true,
        metricsEndpoint: 'https://prod-metrics.example.com',
        loggingEndpoint: 'https://prod-logs.example.com',
        tracingEndpoint: 'https://prod-tracing.example.com',
        alertingEnabled: true,
        retentionDays: 90,
        sampleRate: 0.1,
      },
      scaling: {
        enabled: true,
        minReplicas: 3,
        maxReplicas: 50,
        targetCPU: 70,
        targetMemory: 70,
        scaleUpCooldown: 60,
        scaleDownCooldown: 180,
      },
    };

    // DR Configuration
    const drConfig: EnvironmentConfig = {
      name: 'dr',
      region: 'us-west-2',
      infrastructure: {
        platform: 'aws',
        cluster: 'dr-cluster',
        namespace: 'dr',
        nodeCount: 3,
        instanceType: 't3.large',
        availabilityZones: ['us-west-2a', 'us-west-2b', 'us-west-2c'],
      },
      database: {
        host: 'dr-db.example.com',
        port: 5432,
        database: 'dix_vision_dr',
        username: 'dr_user',
        password: 'dr_password',
        ssl: true,
        poolSize: 10,
        timeout: 30000,
        replicas: 1,
      },
      storage: {
        type: 's3',
        bucket: 'dix-vision-dr',
        region: 'us-west-2',
        encryption: true,
        lifecycleRules: [],
      },
      security: {
        encryption: true,
        keyManagement: 'aws-kms',
        networkPolicies: [],
        authentication: {
          method: 'oauth',
          provider: 'auth0',
          clientId: 'dr-client-id',
          clientSecret: 'dr-client-secret',
          sessionTimeout: 7200,
        },
        authorization: {
          method: 'rbac',
          defaultPolicy: 'allow-authenticated',
          roleBindings: [],
        },
      },
      monitoring: {
        enabled: true,
        metricsEndpoint: 'https://dr-metrics.example.com',
        loggingEndpoint: 'https://dr-logs.example.com',
        tracingEndpoint: 'https://dr-tracing.example.com',
        alertingEnabled: true,
        retentionDays: 30,
        sampleRate: 0.5,
      },
      scaling: {
        enabled: false,
        minReplicas: 1,
        maxReplicas: 5,
        targetCPU: 80,
        targetMemory: 80,
        scaleUpCooldown: 120,
        scaleDownCooldown: 300,
      },
    };

    this.configs.set('development', devConfig);
    this.configs.set('staging', stagingConfig);
    this.configs.set('production', prodConfig);
    this.configs.set('dr', drConfig);
  }

  private loadFromEnvironment(): void {
    // Load environment from NODE_ENV
    const env = process.env.NODE_ENV as Environment;
    if (env && this.configs.has(env)) {
      this.currentEnvironment = env;
    }

    // Load configuration overrides from environment variables
    Object.keys(process.env).forEach(key => {
      if (key.startsWith('DIX_VISION_')) {
        this.overrides.set(key, process.env[key] || '');
      }
    });
  }

  private loadFromFiles(): void {
    // Load from config files if they exist
    // This would typically load from JSON/YAML files
    console.log('Configuration files would be loaded here');
  }

  // Configuration Access
  setEnvironment(environment: Environment): void {
    if (!this.configs.has(environment)) {
      throw new Error(`Environment ${environment} not configured`);
    }
    this.currentEnvironment = environment;
  }

  getEnvironment(): Environment {
    return this.currentEnvironment;
  }

  getConfig(environment?: Environment): EnvironmentConfig {
    const env = environment || this.currentEnvironment;
    const config = this.configs.get(env);
    if (!config) {
      throw new Error(`Configuration for environment ${env} not found`);
    }
    return this.applyOverrides(config);
  }

  getConfigValue<T>(path: string, defaultValue?: T): T {
    const config = this.getConfig();
    const value = this.getNestedValue(config, path);
    return value !== undefined ? value : defaultValue as T;
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  private applyOverrides(config: EnvironmentConfig): EnvironmentConfig {
    const configString = JSON.stringify(config);
    let overridden = configString;

    this.overrides.forEach((value, key) => {
      const configKey = key.replace('DIX_VISION_', '').toLowerCase();
      const regex = new RegExp(`"${configKey}":\\s*"([^"]*)"`, 'g');
      overridden = overridden.replace(regex, `"${configKey}": "${value}"`);
    });

    return JSON.parse(overridden);
  }

  // Configuration Validation
  validateConfiguration(environment: Environment): {
    valid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const config = this.configs.get(environment);
    if (!config) {
      return {
        valid: false,
        errors: [`Environment ${environment} not configured`],
        warnings: [],
      };
    }

    const errors: string[] = [];
    const warnings: string[] = [];

    // Validate infrastructure
    if (!config.infrastructure.cluster) {
      errors.push('Infrastructure cluster is required');
    }
    if (config.infrastructure.nodeCount < 1) {
      errors.push('Infrastructure node count must be at least 1');
    }

    // Validate database
    if (!config.database.host) {
      errors.push('Database host is required');
    }
    if (config.database.port < 1 || config.database.port > 65535) {
      errors.push('Database port must be between 1 and 65535');
    }
    if (!config.database.database) {
      errors.push('Database name is required');
    }
    if (config.database.poolSize < 1) {
      warnings.push('Database pool size should be at least 1');
    }

    // Validate storage
    if (!config.storage.bucket) {
      errors.push('Storage bucket is required');
    }

    // Validate monitoring
    if (config.monitoring.enabled) {
      if (!config.monitoring.metricsEndpoint) {
        errors.push('Metrics endpoint is required when monitoring is enabled');
      }
      if (config.monitoring.sampleRate < 0 || config.monitoring.sampleRate > 1) {
        errors.push('Monitoring sample rate must be between 0 and 1');
      }
    }

    // Validate scaling
    if (config.scaling.enabled) {
      if (config.scaling.minReplicas < 1) {
        errors.push('Scaling min replicas must be at least 1 when scaling is enabled');
      }
      if (config.scaling.maxReplicas < config.scaling.minReplicas) {
        errors.push('Scaling max replicas must be greater than min replicas');
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }

  // Configuration Migration
  migrateConfiguration(fromEnv: Environment, toEnv: Environment): boolean {
    const fromConfig = this.configs.get(fromEnv);
    if (!fromConfig) {
      console.error(`Source environment ${fromEnv} not found`);
      return false;
    }

    // Create a copy of the configuration
    const toConfig: EnvironmentConfig = JSON.parse(JSON.stringify(fromConfig));
    toConfig.name = toEnv;

    // Apply environment-specific adjustments
    switch (toEnv) {
      case 'production':
        toConfig.database.poolSize = Math.max(toConfig.database.poolSize, 20);
        toConfig.monitoring.sampleRate = 0.1;
        toConfig.scaling.minReplicas = 3;
        break;
      case 'staging':
        toConfig.monitoring.sampleRate = 0.5;
        toConfig.scaling.minReplicas = 2;
        break;
    }

    this.configs.set(toEnv, toConfig);
    return true;
  }

  // Configuration Export/Import
  exportConfiguration(environment: Environment): string {
    const config = this.getConfig(environment);
    return JSON.stringify(config, null, 2);
  }

  importConfiguration(environment: Environment, configJson: string): boolean {
    try {
      const config = JSON.parse(configJson) as EnvironmentConfig;
      const validation = this.validateConfiguration(environment);
      
      if (validation.valid) {
        this.configs.set(environment, config);
        return true;
      } else {
        console.error('Configuration validation failed:', validation.errors);
        return false;
      }
    } catch (error) {
      console.error('Failed to parse configuration:', error);
      return false;
    }
  }
}

// ============================================================================
// Public API
// ============================================================================

/**
 * Get configuration manager instance
 */
export function getConfigurationManager(): ConfigurationManager {
  return ConfigurationManager.getInstance();
}

/**
 * Set current environment
 */
export function setEnvironment(environment: Environment): void {
  return ConfigurationManager.getInstance().setEnvironment(environment);
}

/**
 * Get current environment
 */
export function getEnvironment(): Environment {
  return ConfigurationManager.getInstance().getEnvironment();
}

/**
 * Get configuration for environment
 */
export function getConfig(environment?: Environment): EnvironmentConfig {
  return ConfigurationManager.getInstance().getConfig(environment);
}

/**
 * Get specific configuration value
 */
export function getConfigValue<T>(path: string, defaultValue?: T): T {
  return ConfigurationManager.getInstance().getConfigValue(path, defaultValue);
}

/**
 * Validate configuration
 */
export function validateConfiguration(environment: Environment): {
  valid: boolean;
  errors: string[];
  warnings: string[];
} {
  return ConfigurationManager.getInstance().validateConfiguration(environment);
}