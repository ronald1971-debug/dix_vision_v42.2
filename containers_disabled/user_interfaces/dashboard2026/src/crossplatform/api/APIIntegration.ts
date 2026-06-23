/**
 * API & Third-Party Integration System
 * Provides REST API, WebSocket API, webhook system, third-party app marketplace,
 * and developer portal for external integration with the Dashboard2026 platform.
 */

// API Configuration
export interface APIConfig {
  apiId: string;
  name: string;
  version: string;
  baseUrl: string;
  environment: 'development' | 'staging' | 'production';
  authentication: AuthenticationConfig;
  rateLimits: RateLimitConfig;
  cors: CORSConfig;
  logging: LoggingConfig;
}

export interface AuthenticationConfig {
  type: 'api_key' | 'oauth2' | 'jwt' | 'custom';
  apiKeyHeader?: string;
  oauth2Config?: OAuth2Config;
  jwtConfig?: JWTConfig;
  requireAuth: boolean;
  allowGuest: boolean;
}

export interface OAuth2Config {
  authorizationUrl: string;
  tokenUrl: string;
  scopes: string[];
  clientId: string;
  clientSecret: string;
}

export interface JWTConfig {
  secret: string;
  algorithm: string;
  expiresIn: string;
  issuer: string;
}

export interface RateLimitConfig {
  enabled: boolean;
  requestsPerMinute: number;
  requestsPerHour: number;
  requestsPerDay: number;
  burstLimit: number;
  strategy: 'sliding_window' | 'token_bucket' | 'fixed_window';
}

export interface CORSConfig {
  enabled: boolean;
  allowedOrigins: string[];
  allowedMethods: string[];
  allowedHeaders: string[];
  allowCredentials: boolean;
  maxAge: number;
}

export interface LoggingConfig {
  enabled: boolean;
  level: 'debug' | 'info' | 'warn' | 'error';
  format: 'json' | 'text';
  destination: 'console' | 'file' | 'external';
}

// REST API Endpoints
export interface RESTEndpoint {
  endpointId: string;
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  description: string;
  parameters: APIParameter[];
  requestBody?: RequestBodySchema;
  responseSchema: ResponseSchema;
  authentication: boolean;
  rateLimitOverride?: number;
  deprecated: boolean;
  version: string;
}

export interface APIParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  location: 'query' | 'path' | 'header';
  required: boolean;
  description: string;
  defaultValue?: any;
  enum?: any[];
}

export interface RequestBodySchema {
  contentType: string;
  schema: object;
  required: string[];
  properties: Record<string, PropertySchema>;
}

export interface ResponseSchema {
  contentType: string;
  schema: object;
  properties: Record<string, PropertySchema>;
}

export interface PropertySchema {
  type: string;
  description: string;
  required?: boolean;
  properties?: Record<string, PropertySchema>;
  items?: PropertySchema;
}

// WebSocket API
export interface WebSocketEndpoint {
  endpointId: string;
  path: string;
  description: string;
  authentication: boolean;
  rateLimits: WebSocketRateLimit;
  messageTypes: MessageType[];
  compression: boolean;
  heartbeat: HeartbeatConfig;
}

export interface WebSocketRateLimit {
  messagesPerSecond: number;
  connectionsPerUser: number;
  bandwidthLimit: number;
}

export interface MessageType {
  typeId: string;
  name: string;
  direction: 'client_to_server' | 'server_to_client' | 'bidirectional';
  schema: object;
  description: string;
}

export interface HeartbeatConfig {
  enabled: boolean;
  interval: number;
  timeout: number;
}

export interface WebSocketConnection {
  connectionId: string;
  userId: string;
  connectedAt: number;
  lastActivity: number;
  subscriptions: string[];
  metrics: ConnectionMetrics;
}

export interface ConnectionMetrics {
  messagesSent: number;
  messagesReceived: number;
  bytesSent: number;
  bytesReceived: number;
  errors: number;
}

// Webhook System
export interface WebhookConfig {
  webhookId: string;
  name: string;
  url: string;
  events: WebhookEvent[];
  headers: Record<string, string>;
  secret: string;
  active: boolean;
  retryPolicy: RetryPolicy;
  created: number;
  lastTriggered?: number;
}

export interface WebhookEvent {
  eventId: string;
  eventType: string;
  filter?: EventFilter;
}

export interface EventFilter {
  field: string;
  operator: string;
  value: any;
}

export interface RetryPolicy {
  maxRetries: number;
  retryDelay: number;
  backoffMultiplier: number;
  exponentialBackoff: boolean;
}

export interface WebhookDelivery {
  deliveryId: string;
  webhookId: string;
  eventId: string;
  payload: any;
  attempt: number;
  status: 'pending' | 'delivered' | 'failed';
  statusCode?: number;
  response?: string;
  timestamp: number;
}

// Third-Party App Marketplace
export interface ThirdPartyApp {
  appId: string;
  name: string;
  description: string;
  version: string;
  author: string;
  category: AppCategory;
  icon: string;
  screenshots: string[];
  pricing: PricingInfo;
  rating: number;
  reviewCount: number;
  downloads: number;
  permissions: AppPermission[];
  endpoints: AppEndpoint[];
  documentation: string;
  support: string;
  status: 'active' | 'inactive' | 'deprecated' | 'beta';
  featured: boolean;
  created: number;
  updated: number;
}

export type AppCategory = 'trading' | 'analysis' | 'risk' | 'data' | 'utility' | 'education';

export interface PricingInfo {
  type: 'free' | 'freemium' | 'paid' | 'subscription';
  price?: number;
  currency?: string;
  trialPeriod?: number;
  features?: PricingTier[];
}

export interface PricingTier {
  name: string;
  price: number;
  features: string[];
  limits: Record<string, number>;
}

export interface AppPermission {
  permissionId: string;
  name: string;
  description: string;
  required: boolean;
  scope: string[];
}

export interface AppEndpoint {
  endpointId: string;
  path: string;
  method: string;
  description: string;
  authentication: boolean;
}

// API Documentation
export interface APIDocumentation {
  docId: string;
  apiId: string;
  version: string;
  title: string;
  description: string;
  baseUrl: string;
  endpoints: RESTEndpoint[];
  websockets: WebSocketEndpoint[];
  webhooks: WebhookEvent[];
  authentication: AuthenticationDocs;
  examples: CodeExample[];
  schemas: SchemaDefinition[];
  _lastUpdated: number;
}

export interface AuthenticationDocs {
  type: string;
  description: string;
  examples: AuthExample[];
}

export interface AuthExample {
  language: string;
  code: string;
  description: string;
}

export interface CodeExample {
  exampleId: string;
  title: string;
  language: string;
  description: string;
  code: string;
  category: string;
}

export interface SchemaDefinition {
  schemaId: string;
  name: string;
  type: string;
  properties: Record<string, PropertySchema>;
  required: string[];
  description: string;
}

// Developer Portal
export interface DeveloperPortal {
  portalId: string;
  apiKey: string;
  apiSecret: string;
  permissions: DeveloperPermission[];
  apps: DeveloperApp[];
  usage: UsageStats;
  billing: BillingInfo;
}

export interface DeveloperPermission {
  permissionId: string;
  name: string;
  scope: string[];
  granted: boolean;
}

export interface DeveloperApp {
  appId: string;
  name: string;
  description: string;
  apiKey: string;
  apiSecret: string;
  callbackUrl: string;
  permissions: string[];
  created: number;
  lastUsed: number;
}

export interface UsageStats {
  period: string;
  requests: number;
  errors: number;
  rateLimitHits: number;
  bandwidth: number;
}

export interface BillingInfo {
  plan: string;
  status: 'active' | 'past_due' | 'cancelled';
  currentUsage: number;
  limits: Record<string, number>;
  billingPeriod: string;
  nextBilling: string;
}

// Asset Class Specific Endpoints
export interface AssetClassAPIEndpoints {
  assetClass: 'stocks' | 'forex' | 'futures' | 'options';
  endpoints: RESTEndpoint[];
  websockets: WebSocketEndpoint[];
  rateLimits: RateLimitConfig;
}

// API & Third-Party Integration System
export class APIIntegrationSystem {
  private apiConfigs: Map<string, APIConfig>;
  private restEndpoints: Map<string, RESTEndpoint>;
  private websocketEndpoints: Map<string, WebSocketEndpoint>;
  private websocketConnections: Map<string, WebSocketConnection>;
  private webhookConfigs: Map<string, WebhookConfig>;
  private webhookDeliveries: Map<string, WebhookDelivery>;
  private thirdPartyApps: Map<string, ThirdPartyApp>;
  private apiDocumentation: Map<string, APIDocumentation>;
  private developerPortals: Map<string, DeveloperPortal>;
  private assetClassEndpoints: Map<string, AssetClassAPIEndpoints>;


  constructor() {
    this.apiConfigs = new Map();
    this.restEndpoints = new Map();
    this.websocketEndpoints = new Map();
    this.websocketConnections = new Map();
    this.webhookConfigs = new Map();
    this.webhookDeliveries = new Map();
    this.thirdPartyApps = new Map();
    this.apiDocumentation = new Map();
    this.developerPortals = new Map();
    this.assetClassEndpoints = new Map();
  }

  initialize(): void {
    this.loadDefaultAPIConfig();
    this.loadDefaultRESTEndpoints();
    this.loadDefaultWebSocketEndpoints();
    this.loadDefaultWebhookConfigs();
    this.loadDefaultThirdPartyApps();
    this.loadDefaultAssetClassEndpoints();
    this.generateAPIDocumentation();
  }

  // API Configuration Management
  addAPIConfig(config: APIConfig): void {
    this.apiConfigs.set(config.apiId, config);
  }

  getAPIConfig(apiId: string): APIConfig | undefined {
    return this.apiConfigs.get(apiId);
  }

  // REST API Management
  addRESTEndpoint(endpoint: RESTEndpoint): void {
    this.restEndpoints.set(endpoint.endpointId, endpoint);
  }

  getRESTEndpoint(endpointId: string): RESTEndpoint | undefined {
    return this.restEndpoints.get(endpointId);
  }

  async handleRESTRequest(endpointId: string, params: Record<string, any>, body?: any): Promise<any> {
    const endpoint = this.restEndpoints.get(endpointId);
    if (!endpoint) {
      throw new Error(`Endpoint ${endpointId} not found`);
    }
    
    // Validate parameters
    this.validateParameters(endpoint.parameters, params);
    
    // Simulate API response
    return this.generateMockResponse(endpoint, params, body);
  }

  private validateParameters(parameters: APIParameter[], params: Record<string, any>): void {
    for (const param of parameters) {
      if (param.required && params[param.name] === undefined) {
        throw new Error(`Required parameter ${param.name} is missing`);
      }
      
      if (param.enum && params[param.name] !== undefined && !param.enum.includes(params[param.name])) {
        throw new Error(`Parameter ${param.name} must be one of: ${param.enum.join(', ')}`);
      }
    }
  }

  private async generateMockResponse(_endpoint: RESTEndpoint, _params: Record<string, any>, _body?: any): Promise<any> {
    // Simplified mock response generation
    return {
      success: true,
      data: {},
      timestamp: Date.now()
    };
  }

  // WebSocket API Management
  addWebSocketEndpoint(endpoint: WebSocketEndpoint): void {
    this.websocketEndpoints.set(endpoint.endpointId, endpoint);
  }

  getWebSocketEndpoint(endpointId: string): WebSocketEndpoint | undefined {
    return this.websocketEndpoints.get(endpointId);
  }

  async connectWebSocket(endpointId: string, userId: string, token?: string): Promise<WebSocketConnection> {
    const endpoint = this.websocketEndpoints.get(endpointId);
    if (!endpoint) {
      throw new Error(`WebSocket endpoint ${endpointId} not found`);
    }
    
    if (endpoint.authentication && !token) {
      throw new Error('Authentication required');
    }
    
    const connectionId = `ws_${userId}_${Date.now()}_${Math.random()}`;
    const connection: WebSocketConnection = {
      connectionId,
      userId,
      connectedAt: Date.now(),
      lastActivity: Date.now(),
      subscriptions: [],
      metrics: {
        messagesSent: 0,
        messagesReceived: 0,
        bytesSent: 0,
        bytesReceived: 0,
        errors: 0
      }
    };
    
    this.websocketConnections.set(connectionId, connection);
    return connection;
  }

  async sendWebSocketMessage(connectionId: string, message: any): Promise<void> {
    const connection = this.websocketConnections.get(connectionId);
    if (!connection) {
      throw new Error(`Connection ${connectionId} not found`);
    }
    
    connection.metrics.messagesSent++;
    connection.metrics.bytesSent += JSON.stringify(message).length;
    connection.lastActivity = Date.now();
    
    this.websocketConnections.set(connectionId, connection);
  }

  async subscribeToTopic(connectionId: string, topic: string): Promise<void> {
    const connection = this.websocketConnections.get(connectionId);
    if (!connection) {
      throw new Error(`Connection ${connectionId} not found`);
    }
    
    if (!connection.subscriptions.includes(topic)) {
      connection.subscriptions.push(topic);
      this.websocketConnections.set(connectionId, connection);
    }
  }

  disconnectWebSocket(connectionId: string): void {
    this.websocketConnections.delete(connectionId);
  }

  // Webhook Management
  addWebhookConfig(config: WebhookConfig): void {
    this.webhookConfigs.set(config.webhookId, config);
  }

  getWebhookConfig(webhookId: string): WebhookConfig | undefined {
    return this.webhookConfigs.get(webhookId);
  }

  async triggerWebhook(webhookId: string, event: any): Promise<WebhookDelivery> {
    const webhook = this.webhookConfigs.get(webhookId);
    if (!webhook) {
      throw new Error(`Webhook ${webhookId} not found`);
    }
    
    if (!webhook.active) {
      throw new Error('Webhook is not active');
    }
    
    const deliveryId = `delivery_${Date.now()}_${Math.random()}`;
    const delivery: WebhookDelivery = {
      deliveryId,
      webhookId,
      eventId: event.eventId,
      payload: event,
      attempt: 1,
      status: 'pending',
      timestamp: Date.now()
    };
    
    this.webhookDeliveries.set(deliveryId, delivery);
    
    // Simulate webhook delivery
    try {
      await this.deliverWebhook(webhook, event);
      delivery.status = 'delivered';
      delivery.statusCode = 200;
      webhook.lastTriggered = Date.now();
    } catch (error) {
      delivery.status = 'failed';
      delivery.statusCode = 500;
      delivery.response = error instanceof Error ? error.message : 'Unknown error';
      
      // Retry logic would be implemented here
      if (delivery.attempt < webhook.retryPolicy.maxRetries) {
        // Schedule retry
      }
    }
    
    this.webhookDeliveries.set(deliveryId, delivery);
    this.webhookConfigs.set(webhookId, webhook);
    
    return delivery;
  }

  private async deliverWebhook(webhook: WebhookConfig, event: any): Promise<void> {
    // Simulate webhook delivery
    const headers = {
      ...webhook.headers,
      'Content-Type': 'application/json',
      'X-Webhook-Signature': this.generateSignature(event, webhook.secret)
    };
    
    // Actual implementation would use fetch or axios to deliver webhook
    console.log(`Delivering webhook to ${webhook.url}`, headers, event);
  }

  private generateSignature(payload: any, secret: string): string {
    // Simplified signature generation
    const crypto = require('crypto');
    return crypto
      .createHmac('sha256', secret)
      .update(JSON.stringify(payload))
      .digest('hex');
  }

  // Third-Party App Marketplace
  addThirdPartyApp(app: ThirdPartyApp): void {
    this.thirdPartyApps.set(app.appId, app);
  }

  getThirdPartyApp(appId: string): ThirdPartyApp | undefined {
    return this.thirdPartyApps.get(appId);
  }

  searchApps(category?: AppCategory, query?: string): ThirdPartyApp[] {
    let apps = Array.from(this.thirdPartyApps.values());
    
    if (category) {
      apps = apps.filter(app => app.category === category);
    }
    
    if (query) {
      const lowerQuery = query.toLowerCase();
      apps = apps.filter(app => 
        app.name.toLowerCase().includes(lowerQuery) ||
        app.description.toLowerCase().includes(lowerQuery)
      );
    }
    
    return apps.sort((a, b) => b.rating - a.rating);
  }

  async installApp(appId: string, _userId: string): Promise<void> {
    const app = this.thirdPartyApps.get(appId);
    if (!app) {
      throw new Error(`App ${appId} not found`);
    }
    
    // Simulate app installation
    app.downloads++;
    this.thirdPartyApps.set(appId, app);
  }

  // API Documentation
  generateAPIDocumentation(): APIDocumentation {
    const docId = `doc_${Date.now()}`;
    const config = this.apiConfigs.get('api_default') || this.createDefaultAPIConfig();
    
    const documentation: APIDocumentation = {
      docId,
      apiId: config.apiId,
      version: config.version,
      title: 'Dashboard2026 API',
      description: 'Comprehensive API for trading, analysis, and integration',
      baseUrl: config.baseUrl,
      endpoints: Array.from(this.restEndpoints.values()),
      websockets: Array.from(this.websocketEndpoints.values()),
      webhooks: this.getAvailableWebhookEvents(),
      authentication: this.generateAuthenticationDocs(config),
      examples: this.generateCodeExamples(),
      schemas: this.generateSchemaDefinitions(),
      _lastUpdated: Date.now()
    };
    
    this.apiDocumentation.set(docId, documentation);
    return documentation;
  }

  getAPIDocumentation(docId: string): APIDocumentation | undefined {
    return this.apiDocumentation.get(docId);
  }

  private getAvailableWebhookEvents(): WebhookEvent[] {
    return [
      {
        eventId: 'event_trade_executed',
        eventType: 'trade.executed',
        filter: undefined
      },
      {
        eventId: 'event_order_filled',
        eventType: 'order.filled',
        filter: undefined
      },
      {
        eventId: 'event_position_closed',
        eventType: 'position.closed',
        filter: undefined
      },
      {
        eventId: 'event_risk_alert',
        eventType: 'risk.alert',
        filter: { field: 'severity', operator: 'equals', value: 'critical' }
      }
    ];
  }

  private generateAuthenticationDocs(config: APIConfig): AuthenticationDocs {
    return {
      type: config.authentication.type,
      description: 'Authentication is required for most endpoints',
      examples: [
        {
          language: 'javascript',
          code: `
const headers = {
  'Authorization': 'Bearer YOUR_API_KEY',
  'Content-Type': 'application/json'
};

fetch('${config.baseUrl}/v1/portfolio', {
  method: 'GET',
  headers: headers
}).then(response => response.json());
          `.trim(),
          description: 'API Key authentication example'
        }
      ]
    };
  }

  private generateCodeExamples(): CodeExample[] {
    return [
      {
        exampleId: 'example_get_portfolio',
        title: 'Get Portfolio',
        language: 'javascript',
        description: 'Retrieve current portfolio information',
        category: 'REST API',
        code: `
const response = await fetch('${this.apiConfigs.get('api_default')?.baseUrl}/v1/portfolio', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY'
  }
});

const portfolio = await response.json();
console.log(portfolio);
        `.trim()
      },
      {
        exampleId: 'example_websocket_connect',
        title: 'WebSocket Connection',
        language: 'javascript',
        description: 'Connect to real-time data stream',
        category: 'WebSocket',
        code: `
const ws = new WebSocket('wss://api.dashboard2026.com/v1/stream');

ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({
    action: 'subscribe',
    topics: ['portfolio', 'orders']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
        `.trim()
      }
    ];
  }

  private generateSchemaDefinitions(): SchemaDefinition[] {
    return [
      {
        schemaId: 'schema_portfolio',
        name: 'Portfolio',
        type: 'object',
        properties: {
          portfolioId: { type: 'string', description: 'Unique portfolio identifier' },
          totalValue: { type: 'number', description: 'Total portfolio value' },
          positions: { type: 'array', description: 'List of positions', items: { type: 'object', description: 'Position object' } }
        },
        required: ['portfolioId', 'totalValue'],
        description: 'Portfolio information schema'
      },
      {
        schemaId: 'schema_order',
        name: 'Order',
        type: 'object',
        properties: {
          orderId: { type: 'string', description: 'Unique order identifier' },
          symbol: { type: 'string', description: 'Trading symbol' },
          side: { type: 'string', description: 'Order side (buy/sell)' },
          quantity: { type: 'number', description: 'Order quantity' },
          price: { type: 'number', description: 'Order price' },
          status: { type: 'string', description: 'Order status' }
        },
        required: ['orderId', 'symbol', 'side', 'quantity'],
        description: 'Order information schema'
      }
    ];
  }

  // Developer Portal
  createDeveloperPortal(userId: string): DeveloperPortal {
    const portalId = `portal_${userId}_${Date.now()}`;
    const apiKey = this.generateAPIKey();
    const apiSecret = this.generateAPISecret();
    
    const portal: DeveloperPortal = {
      portalId,
      apiKey,
      apiSecret,
      permissions: [
        {
          permissionId: 'perm_read',
          name: 'Read Access',
          scope: ['portfolio', 'orders', 'positions'],
          granted: true
        },
        {
          permissionId: 'perm_trade',
          name: 'Trade Access',
          scope: ['orders'],
          granted: false
        }
      ],
      apps: [],
      usage: {
        period: 'current',
        requests: 0,
        errors: 0,
        rateLimitHits: 0,
        bandwidth: 0
      },
      billing: {
        plan: 'free',
        status: 'active',
        currentUsage: 0,
        limits: {
          requestsPerDay: 1000,
          requestsPerMinute: 100
        },
        billingPeriod: 'monthly',
        nextBilling: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
      }
    };
    
    this.developerPortals.set(portalId, portal);
    return portal;
  }

  getDeveloperPortal(portalId: string): DeveloperPortal | undefined {
    return this.developerPortals.get(portalId);
  }

  private generateAPIKey(): string {
    return `ak_${Date.now()}_${Math.random().toString(36).substr(2, 16)}`;
  }

  private generateAPISecret(): string {
    return `as_${Date.now()}_${Math.random().toString(36).substr(2, 32)}`;
  }

  // Asset Class Specific Endpoints
  addAssetClassEndpoints(assetClass: string, endpoints: AssetClassAPIEndpoints): void {
    this.assetClassEndpoints.set(assetClass, endpoints);
  }

  getAssetClassEndpoints(assetClass: string): AssetClassAPIEndpoints | undefined {
    return this.assetClassEndpoints.get(assetClass);
  }

  // Default Configuration Methods
  private loadDefaultAPIConfig(): void {
    const config: APIConfig = {
      apiId: 'api_default',
      name: 'Dashboard2026 API',
      version: 'v1',
      baseUrl: 'https://api.dashboard2026.com',
      environment: 'development',
      authentication: {
        type: 'api_key',
        apiKeyHeader: 'X-API-Key',
        requireAuth: true,
        allowGuest: false
      },
      rateLimits: {
        enabled: true,
        requestsPerMinute: 100,
        requestsPerHour: 1000,
        requestsPerDay: 10000,
        burstLimit: 10,
        strategy: 'sliding_window'
      },
      cors: {
        enabled: true,
        allowedOrigins: ['*'],
        allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        allowedHeaders: ['*'],
        allowCredentials: true,
        maxAge: 3600
      },
      logging: {
        enabled: true,
        level: 'info',
        format: 'json',
        destination: 'console'
      }
    };
    
    this.addAPIConfig(config);
  }

  private createDefaultAPIConfig(): APIConfig {
    return {
      apiId: 'api_default',
      name: 'Dashboard2026 API',
      version: 'v1',
      baseUrl: 'https://api.dashboard2026.com',
      environment: 'development',
      authentication: {
        type: 'api_key',
        apiKeyHeader: 'X-API-Key',
        requireAuth: true,
        allowGuest: false
      },
      rateLimits: {
        enabled: true,
        requestsPerMinute: 100,
        requestsPerHour: 1000,
        requestsPerDay: 10000,
        burstLimit: 10,
        strategy: 'sliding_window'
      },
      cors: {
        enabled: true,
        allowedOrigins: ['*'],
        allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        allowedHeaders: ['*'],
        allowCredentials: true,
        maxAge: 3600
      },
      logging: {
        enabled: true,
        level: 'info',
        format: 'json',
        destination: 'console'
      }
    };
  }

  private loadDefaultRESTEndpoints(): void {
    const endpoints: RESTEndpoint[] = [
      {
        endpointId: 'endpoint_get_portfolio',
        path: '/v1/portfolio',
        method: 'GET',
        description: 'Get current portfolio information',
        parameters: [
          {
            name: 'portfolioId',
            type: 'string',
            location: 'query',
            required: false,
            description: 'Portfolio identifier'
          }
        ],
        responseSchema: {
          contentType: 'application/json',
          schema: {},
          properties: {}
        },
        authentication: true,
        deprecated: false,
        version: 'v1'
      },
      {
        endpointId: 'endpoint_create_order',
        path: '/v1/orders',
        method: 'POST',
        description: 'Create new order',
        parameters: [],
        requestBody: {
          contentType: 'application/json',
          schema: {},
          required: ['symbol', 'side', 'quantity', 'price'],
          properties: {
            symbol: { type: 'string', description: 'Trading symbol' },
            side: { type: 'string', description: 'Order side' },
            quantity: { type: 'number', description: 'Order quantity' },
            price: { type: 'number', description: 'Order price' }
          }
        },
        responseSchema: {
          contentType: 'application/json',
          schema: {},
          properties: {}
        },
        authentication: true,
        deprecated: false,
        version: 'v1'
      },
      {
        endpointId: 'endpoint_get_market_data',
        path: '/v1/market/data',
        method: 'GET',
        description: 'Get market data for symbols',
        parameters: [
          {
            name: 'symbols',
            type: 'array',
            location: 'query',
            required: true,
            description: 'Array of symbols'
          }
        ],
        responseSchema: {
          contentType: 'application/json',
          schema: {},
          properties: {}
        },
        authentication: true,
        deprecated: false,
        version: 'v1'
      }
    ];
    
    endpoints.forEach(endpoint => this.addRESTEndpoint(endpoint));
  }

  private loadDefaultWebSocketEndpoints(): void {
    const endpoints: WebSocketEndpoint[] = [
      {
        endpointId: 'websocket_stream',
        path: '/v1/stream',
        description: 'Real-time data stream',
        authentication: true,
        rateLimits: {
          messagesPerSecond: 10,
          connectionsPerUser: 5,
          bandwidthLimit: 1024 * 1024 // 1 MB/s
        },
        messageTypes: [
          {
            typeId: 'type_portfolio_update',
            name: 'Portfolio Update',
            direction: 'server_to_client',
            schema: {},
            description: 'Portfolio update message'
          },
          {
            typeId: 'type_order_update',
            name: 'Order Update',
            direction: 'server_to_client',
            schema: {},
            description: 'Order update message'
          },
          {
            typeId: 'type_market_data',
            name: 'Market Data',
            direction: 'server_to_client',
            schema: {},
            description: 'Market data message'
          }
        ],
        compression: true,
        heartbeat: {
          enabled: true,
          interval: 30000,
          timeout: 60000
        }
      }
    ];
    
    endpoints.forEach(endpoint => this.addWebSocketEndpoint(endpoint));
  }

  private loadDefaultWebhookConfigs(): void {
    // Webhook configs are typically created by users, so no defaults
  }

  private loadDefaultThirdPartyApps(): void {
    const apps: ThirdPartyApp[] = [
      {
        appId: 'app_tradingview_integration',
        name: 'TradingView Integration',
        description: 'Seamless integration with TradingView charts and alerts',
        version: '1.2.0',
        author: 'Dashboard2026',
        category: 'trading',
        icon: '/apps/tradingview/icon.png',
        screenshots: [],
        pricing: {
          type: 'freemium',
          features: [
            { name: 'Basic', price: 0, features: ['Chart alerts'], limits: {} },
            { name: 'Pro', price: 9.99, features: ['Chart alerts', 'Order execution', 'Portfolio sync'], limits: { alerts: 1000 } }
          ]
        },
        rating: 4.8,
        reviewCount: 245,
        downloads: 12500,
        permissions: [
          {
            permissionId: 'perm_read_portfolio',
            name: 'Read Portfolio',
            description: 'Access to read portfolio data',
            required: true,
            scope: ['portfolio:read']
          }
        ],
        endpoints: [],
        documentation: 'https://docs.dashboard2026.com/apps/tradingview',
        support: 'support@dashboard2026.com',
        status: 'active',
        featured: true,
        created: Date.now() - 90 * 24 * 60 * 60 * 1000,
        updated: Date.now() - 30 * 24 * 60 * 60 * 1000
      }
    ];
    
    apps.forEach(app => this.addThirdPartyApp(app));
  }

  private loadDefaultAssetClassEndpoints(): void {
    const endpoints: AssetClassAPIEndpoints[] = [
      {
        assetClass: 'stocks',
        endpoints: [],
        websockets: [],
        rateLimits: {
          enabled: true,
          requestsPerMinute: 50,
          requestsPerHour: 500,
          requestsPerDay: 5000,
          burstLimit: 5,
          strategy: 'sliding_window'
        }
      },
      {
        assetClass: 'forex',
        endpoints: [],
        websockets: [],
        rateLimits: {
          enabled: true,
          requestsPerMinute: 100,
          requestsPerHour: 1000,
          requestsPerDay: 10000,
          burstLimit: 10,
          strategy: 'sliding_window'
        }
      }
    ];
    
    endpoints.forEach(endpoint => {
      this.addAssetClassEndpoints(endpoint.assetClass, endpoint);
    });
  }
}