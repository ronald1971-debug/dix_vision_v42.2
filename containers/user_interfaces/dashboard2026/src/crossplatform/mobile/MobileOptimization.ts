/**
 * Mobile Optimization System
 * Provides mobile-specific optimizations, touch gestures, offline capabilities,
 * and mobile UI components for professional trading applications.
 */

// Mobile Device Information
export interface MobileDeviceInfo {
  deviceId: string;
  deviceType: 'phone' | 'tablet' | 'phablet';
  platform: 'ios' | 'android' | 'web';
  osVersion: string;
  screenSize: ScreenSize;
  capabilities: DeviceCapabilities;
  orientation: 'portrait' | 'landscape';
  _lastUpdated: number;
}

export interface ScreenSize {
  width: number;
  height: number;
  pixelRatio: number;
  safeArea: { top: number; bottom: number; left: number; right: number };
}

export interface DeviceCapabilities {
  touchSupport: boolean;
  multiTouch: boolean;
  biometricAuth: boolean;
  pushNotifications: boolean;
  offlineSupport: boolean;
  camera: boolean;
  gps: boolean;
  accelerometer: boolean;
}

// Touch Gesture Configuration
export interface TouchGestureConfig {
  gestureId: string;
  gestureType: 'tap' | 'double_tap' | 'long_press' | 'swipe' | 'pinch' | 'rotate' | 'pan';
  enabled: boolean;
  sensitivity: number;
  threshold: number;
  action: GestureAction;
  context: string;
}

export interface GestureAction {
  type: 'navigation' | 'chart_interaction' | 'order_entry' | 'custom';
  target: string;
  parameters: Record<string, any>;
}

// Gesture Recognition Result
export interface GestureResult {
  gestureId: string;
  gestureType: string;
  confidence: number;
  startPoint: { x: number; y: number };
  endPoint: { x: number; y: number };
  duration: number;
  velocity: number;
  parameters: Record<string, number>;
  timestamp: number;
}

// Mobile UI Component Configuration
export interface MobileComponentConfig {
  componentId: string;
  componentType: 'bottom_sheet' | 'carousel' | 'swipeable_card' | 'pull_to_refresh' | 'infinite_scroll';
  layout: MobileLayout;
  styling: MobileStyling;
  behavior: ComponentBehavior;
  performance: PerformanceConfig;
}

export interface MobileLayout {
  responsive: boolean;
  breakpoints: Record<string, number>;
  adaptive: boolean;
  orientation: 'portrait' | 'landscape' | 'both';
}

export interface MobileStyling {
  theme: 'light' | 'dark' | 'auto';
  fontSize: number;
  iconSize: number;
  spacing: number;
  animation: boolean;
  reducedMotion: boolean;
}

export interface ComponentBehavior {
  lazyLoad: boolean;
  virtualScroll: boolean;
  prefetch: boolean;
  cache: boolean;
  offline: boolean;
}

export interface PerformanceConfig {
  animation: boolean;
  transition: boolean;
  gpuAcceleration: boolean;
  memoryLimit: number;
  frameRate: number;
}

// Offline Sync Configuration
export interface OfflineSyncConfig {
  syncId: string;
  strategy: 'cache_first' | 'network_first' | 'cache_only' | 'network_only';
  cacheDuration: number;
  syncInterval: number;
  conflictResolution: 'client_wins' | 'server_wins' | 'merge';
  dataTypes: string[];
  priority: number;
}

export interface SyncStatus {
  syncId: string;
  status: 'idle' | 'syncing' | 'completed' | 'error';
  lastSync: number;
  nextSync: number;
  itemsSynced: number;
  itemsPending: number;
  conflicts: number;
  errors: SyncError[];
}

export interface SyncError {
  errorId: string;
  itemType: string;
  itemId: string;
  error: string;
  timestamp: number;
  retryCount: number;
}

// Push Notification Configuration
export interface PushNotificationConfig {
  notificationId: string;
  type: 'trade_alert' | 'risk_alert' | 'price_alert' | 'system_alert' | 'custom';
  priority: 'high' | 'normal' | 'low';
  sound: string;
  vibration: boolean;
  badge: boolean;
  channels: string[];
  conditions: NotificationCondition[];
}

export interface NotificationCondition {
  conditionId: string;
  field: string;
  operator: string;
  value: any;
}

export interface PushNotification {
  notificationId: string;
  title: string;
  body: string;
  data: Record<string, any>;
  timestamp: number;
  read: boolean;
  actionTaken?: string;
}

// Biometric Authentication
export interface BiometricAuthConfig {
  authId: string;
  methods: BiometricMethod[];
  fallbackToPin: boolean;
  timeout: number;
  maxAttempts: number;
  lockoutDuration: number;
}

export interface BiometricMethod {
  type: 'fingerprint' | 'face_id' | 'iris' | 'voice' | 'pattern';
  enabled: boolean;
  priority: number;
}

export interface AuthResult {
  authId: string;
  success: boolean;
  method: string;
  timestamp: number;
  attemptNumber: number;
  lockedOut?: boolean;
  lockoutExpiry?: number;
}

// Asset Class Mobile Interface
export interface AssetClassMobileInterface {
  assetClass: 'stocks' | 'forex' | 'futures' | 'options';
  layout: MobileLayoutConfig;
  features: MobileFeature[];
  gestures: TouchGestureConfig[];
  components: MobileComponentConfig[];
}

export interface MobileLayoutConfig {
  portrait: LayoutConfiguration;
  landscape: LayoutConfiguration;
}

export interface LayoutConfiguration {
  header: boolean;
  footer: boolean;
  mainContent: string[];
  sidebars: string[];
  overlays: string[];
}

export interface MobileFeature {
  featureId: string;
  name: string;
  enabled: boolean;
  position: 'header' | 'footer' | 'overlay' | 'main';
  priority: number;
}

// Mobile Performance Monitoring
export interface MobilePerformanceMetrics {
  metricsId: string;
  deviceId: string;
  timestamp: number;
  frameRate: number;
  memoryUsage: number;
  batteryLevel: number;
  networkLatency: number;
  renderTime: number;
  interactionLatency: number;
  offlineMode: boolean;
}

// Mobile Optimization System
export class MobileOptimizationSystem {
  private deviceInfo: Map<string, MobileDeviceInfo>;
  private gestureConfigs: Map<string, TouchGestureConfig>;
  private gestureResults: Map<string, GestureResult>;
  private mobileComponents: Map<string, MobileComponentConfig>;
  private offlineSyncConfigs: Map<string, OfflineSyncConfig>;
  private syncStatuses: Map<string, SyncStatus>;
  private pushNotificationConfigs: Map<string, PushNotificationConfig>;
  private notifications: Map<string, PushNotification>;
  private biometricAuthConfigs: Map<string, BiometricAuthConfig>;
  private authResults: Map<string, AuthResult>;
  private assetClassInterfaces: Map<string, AssetClassMobileInterface>;
  private performanceMetrics: Map<string, MobilePerformanceMetrics>;


  constructor() {
    this.deviceInfo = new Map();
    this.gestureConfigs = new Map();
    this.gestureResults = new Map();
    this.mobileComponents = new Map();
    this.offlineSyncConfigs = new Map();
    this.syncStatuses = new Map();
    this.pushNotificationConfigs = new Map();
    this.notifications = new Map();
    this.biometricAuthConfigs = new Map();
    this.authResults = new Map();
    this.assetClassInterfaces = new Map();
    this.performanceMetrics = new Map();
  }

  initialize(): void {
    this.loadDefaultGestureConfigs();
    this.loadDefaultMobileComponents();
    this.loadDefaultOfflineSyncConfigs();
    this.loadDefaultPushNotificationConfigs();
    this.loadDefaultBiometricAuthConfig();
    this.loadAssetClassMobileInterfaces();
  }

  // Device Information Management
  registerDevice(deviceId: string, deviceInfo: MobileDeviceInfo): void {
    this.deviceInfo.set(deviceId, deviceInfo);
  }

  getDeviceInfo(deviceId: string): MobileDeviceInfo | undefined {
    return this.deviceInfo.get(deviceId);
  }

  detectDevice(): MobileDeviceInfo {
    const userAgent = navigator.userAgent;
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    let deviceType: 'phone' | 'tablet' | 'phablet';
    let platform: 'ios' | 'android' | 'web';
    
    if (width >= 768) {
      deviceType = 'tablet';
    } else if (width >= 360) {
      deviceType = 'phablet';
    } else {
      deviceType = 'phone';
    }
    
    if (/iPad|iPhone|iPod/.test(userAgent)) {
      platform = 'ios';
    } else if (/Android/.test(userAgent)) {
      platform = 'android';
    } else {
      platform = 'web';
    }
    
    const capabilities: DeviceCapabilities = {
      touchSupport: 'ontouchstart' in window,
      multiTouch: 'ontouchstart' in window && navigator.maxTouchPoints > 1,
      biometricAuth: this.checkBiometricSupport(),
      pushNotifications: 'Notification' in window,
      offlineSupport: 'serviceWorker' in navigator,
      camera: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      gps: 'geolocation' in navigator,
      accelerometer: 'DeviceMotionEvent' in window
    };
    
    const deviceInfo: MobileDeviceInfo = {
      deviceId: this.generateDeviceId(),
      deviceType,
      platform,
      osVersion: this.getOSVersion(userAgent),
      screenSize: {
        width,
        height,
        pixelRatio: window.devicePixelRatio || 1,
        safeArea: this.getSafeArea()
      },
      capabilities,
      orientation: width > height ? 'landscape' : 'portrait',
      _lastUpdated: Date.now()
    };
    
    return deviceInfo;
  }

  private generateDeviceId(): string {
    return `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getOSVersion(userAgent: string): string {
    // Simplified OS version detection
    if (/iPhone OS (\d+_\d+)/.test(userAgent)) {
      return userAgent.match(/iPhone OS (\d+_\d+)/)?.[1] || 'unknown';
    }
    if (/Android (\d+\.\d+)/.test(userAgent)) {
      return userAgent.match(/Android (\d+\.\d+)/)?.[1] || 'unknown';
    }
    return 'web';
  }

  private getSafeArea(): { top: number; bottom: number; left: number; right: number } {
    const style = getComputedStyle(document.body);
    return {
      top: parseInt(style.getPropertyValue('safe-area-inset-top') || '0'),
      bottom: parseInt(style.getPropertyValue('safe-area-inset-bottom') || '0'),
      left: parseInt(style.getPropertyValue('safe-area-inset-left') || '0'),
      right: parseInt(style.getPropertyValue('safe-area-inset-right') || '0')
    };
  }

  private checkBiometricSupport(): boolean {
    // Simplified biometric support check
    return false; // Would need actual implementation
  }

  // Touch Gesture Management
  addGestureConfig(config: TouchGestureConfig): void {
    this.gestureConfigs.set(config.gestureId, config);
  }

  recognizeGesture(touchData: any[]): GestureResult | null {
    // Simplified gesture recognition
    if (touchData.length < 2) return null;
    
    const startPoint = { x: touchData[0].x, y: touchData[0].y };
    const endPoint = { x: touchData[touchData.length - 1].x, y: touchData[touchData.length - 1].y };
    const duration = touchData[touchData.length - 1].timestamp - touchData[0].timestamp;
    
    const deltaX = endPoint.x - startPoint.x;
    const deltaY = endPoint.y - startPoint.y;
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
    const velocity = distance / duration;
    
    let gestureType = 'tap';
    if (distance > 50 && duration < 500) {
      gestureType = Math.abs(deltaX) > Math.abs(deltaY) ? 
        (deltaX > 0 ? 'swipe_right' : 'swipe_left') :
        (deltaY > 0 ? 'swipe_down' : 'swipe_up');
    } else if (duration > 500) {
      gestureType = 'long_press';
    }
    
    const result: GestureResult = {
      gestureId: `gesture_${Date.now()}_${Math.random()}`,
      gestureType,
      confidence: 0.8,
      startPoint,
      endPoint,
      duration,
      velocity,
      parameters: { deltaX, deltaY, distance },
      timestamp: Date.now()
    };
    
    this.gestureResults.set(result.gestureId, result);
    return result;
  }

  // Mobile Component Management
  addMobileComponent(config: MobileComponentConfig): void {
    this.mobileComponents.set(config.componentId, config);
  }

  getMobileComponent(componentId: string): MobileComponentConfig | undefined {
    return this.mobileComponents.get(componentId);
  }

  optimizeComponent(componentId: string): MobileComponentConfig | undefined {
    const component = this.mobileComponents.get(componentId);
    if (!component) return undefined;
    
    const _deviceInfo = this.detectDevice();
    
    // Optimize based on device capabilities
    const optimized: MobileComponentConfig = {
      ...component,
      performance: {
        ...component.performance,
        animation: _deviceInfo.capabilities.touchSupport,
        transition: _deviceInfo.capabilities.touchSupport,
        gpuAcceleration: true,
        memoryLimit: _deviceInfo.deviceType === 'phone' ? 50 : 100,
        frameRate: _deviceInfo.deviceType === 'phone' ? 30 : 60
      }
    };
    
    this.mobileComponents.set(componentId, optimized);
    return optimized;
  }

  // Offline Sync Management
  addOfflineSyncConfig(config: OfflineSyncConfig): void {
    this.offlineSyncConfigs.set(config.syncId, config);
  }

  async startOfflineSync(syncId: string, data: any[]): Promise<SyncStatus> {
    const config = this.offlineSyncConfigs.get(syncId);
    if (!config) {
      throw new Error(`Sync config ${syncId} not found`);
    }
    
    const status: SyncStatus = {
      syncId,
      status: 'syncing',
      lastSync: Date.now(),
      nextSync: Date.now() + config.syncInterval,
      itemsSynced: 0,
      itemsPending: data.length,
      conflicts: 0,
      errors: []
    };
    
    this.syncStatuses.set(syncId, status);
    
    try {
      // Simulate sync process
      for (const item of data) {
        await this.syncItem(item, config);
        status.itemsSynced++;
        status.itemsPending--;
      }
      
      status.status = 'completed';
    } catch (error) {
      status.status = 'error';
      status.errors.push({
        errorId: `error_${Date.now()}`,
        itemType: 'general',
        itemId: 'unknown',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: Date.now(),
        retryCount: 0
      });
    }
    
    this.syncStatuses.set(syncId, status);
    return status;
  }

  private async syncItem(_item: any, config: OfflineSyncConfig): Promise<void> {
    // Simplified sync logic
    if (config.strategy === 'cache_first') {
      // Try cache first, then network
    } else if (config.strategy === 'network_first') {
      // Try network first, then cache
    }
    // Actual implementation would sync with backend
  }

  getSyncStatus(syncId: string): SyncStatus | undefined {
    return this.syncStatuses.get(syncId);
  }

  // Push Notification Management
  addPushNotificationConfig(config: PushNotificationConfig): void {
    this.pushNotificationConfigs.set(config.notificationId, config);
  }

  async sendPushNotification(notificationId: string, title: string, body: string, data: Record<string, any>): Promise<void> {
    const config = this.pushNotificationConfigs.get(notificationId);
    if (!config) {
      throw new Error(`Notification config ${notificationId} not found`);
    }
    
    const notification: PushNotification = {
      notificationId: `notif_${Date.now()}_${Math.random()}`,
      title,
      body,
      data,
      timestamp: Date.now(),
      read: false
    };
    
    this.notifications.set(notification.notificationId, notification);
    
    // Actual implementation would use device push notification API
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body,
        data,
        badge: config.badge ? '1' : undefined,
        icon: '/icon.png',
        requireInteraction: config.priority === 'high'
      });
    }
  }

  async requestNotificationPermission(): Promise<boolean> {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return false;
  }

  // Biometric Authentication
  addBiometricAuthConfig(config: BiometricAuthConfig): void {
    this.biometricAuthConfigs.set(config.authId, config);
  }

  async authenticate(authId: string): Promise<AuthResult> {
    const config = this.biometricAuthConfigs.get(authId);
    if (!config) {
      throw new Error(`Auth config ${authId} not found`);
    }
    
    // Check if locked out
    const recentAttempts = Array.from(this.authResults.values())
      .filter(r => r.authId === authId && r.timestamp > Date.now() - config.lockoutDuration);
    
    if (recentAttempts.length >= config.maxAttempts) {
      const lockoutExpiry = Date.now() + config.lockoutDuration;
      return {
        authId,
        success: false,
        method: 'biometric',
        timestamp: Date.now(),
        attemptNumber: recentAttempts.length + 1,
        lockedOut: true,
        lockoutExpiry
      };
    }
    
    // Simulate biometric authentication
    const success = await this.performBiometricAuth(config);
    
    const result: AuthResult = {
      authId,
      success,
      method: config.methods[0]?.type || 'fingerprint',
      timestamp: Date.now(),
      attemptNumber: recentAttempts.length + 1
    };
    
    this.authResults.set(`${authId}_${Date.now()}`, result);
    return result;
  }

  private async performBiometricAuth(_config: BiometricAuthConfig): Promise<boolean> {
    // Simplified biometric auth - would use actual APIs
    return true;
  }

  // Asset Class Mobile Interfaces
  getAssetClassInterface(assetClass: string): AssetClassMobileInterface | undefined {
    return this.assetClassInterfaces.get(assetClass);
  }

  // Performance Monitoring
  collectPerformanceMetrics(deviceId: string): MobilePerformanceMetrics {
    
    const metrics: MobilePerformanceMetrics = {
      metricsId: `metrics_${Date.now()}_${Math.random()}`,
      deviceId,
      timestamp: Date.now(),
      frameRate: this.measureFrameRate(),
      memoryUsage: this.measureMemoryUsage(),
      batteryLevel: this.getBatteryLevel(),
      networkLatency: this.measureNetworkLatency(),
      renderTime: this.measureRenderTime(),
      interactionLatency: this.measureInteractionLatency(),
      offlineMode: !navigator.onLine
    };
    
    this.performanceMetrics.set(metrics.metricsId, metrics);
    return metrics;
  }

  private measureFrameRate(): number {
    // Simplified frame rate measurement
    return 60;
  }

  private measureMemoryUsage(): number {
    // Simplified memory measurement
    if ('memory' in performance) {
      return (performance as any).memory.usedJSHeapSize / 1024 / 1024;
    }
    return 50; // Placeholder
  }

  private getBatteryLevel(): number {
    // Simplified battery level
    return 100;
  }

  private measureNetworkLatency(): number {
    // Simplified network latency
    return 50;
  }

  private measureRenderTime(): number {
    // Simplified render time
    return 16;
  }

  private measureInteractionLatency(): number {
    // Simplified interaction latency
    return 50;
  }

  // Default Data Loading
  private loadDefaultGestureConfigs(): void {
    const defaultGestures: TouchGestureConfig[] = [
      {
        gestureId: 'gesture_chart_swipe',
        gestureType: 'swipe',
        enabled: true,
        sensitivity: 1.0,
        threshold: 50,
        action: {
          type: 'chart_interaction',
          target: 'chart',
          parameters: { action: 'pan' }
        },
        context: 'chart'
      },
      {
        gestureId: 'gesture_chart_pinch',
        gestureType: 'pinch',
        enabled: true,
        sensitivity: 1.0,
        threshold: 10,
        action: {
          type: 'chart_interaction',
          target: 'chart',
          parameters: { action: 'zoom' }
        },
        context: 'chart'
      },
      {
        gestureId: 'gesture_order_swipe',
        gestureType: 'swipe',
        enabled: true,
        sensitivity: 1.0,
        threshold: 100,
        action: {
          type: 'order_entry',
          target: 'order_form',
          parameters: { action: 'submit' }
        },
        context: 'order'
      }
    ];
    
    defaultGestures.forEach(gesture => this.addGestureConfig(gesture));
  }

  private loadDefaultMobileComponents(): void {
    const defaultComponents: MobileComponentConfig[] = [
      {
        componentId: 'component_bottom_sheet',
        componentType: 'bottom_sheet',
        layout: {
          responsive: true,
          breakpoints: { mobile: 768, tablet: 1024 },
          adaptive: true,
          orientation: 'both'
        },
        styling: {
          theme: 'auto',
          fontSize: 16,
          iconSize: 24,
          spacing: 8,
          animation: true,
          reducedMotion: false
        },
        behavior: {
          lazyLoad: true,
          virtualScroll: true,
          prefetch: false,
          cache: true,
          offline: false
        },
        performance: {
          animation: true,
          transition: true,
          gpuAcceleration: true,
          memoryLimit: 50,
          frameRate: 60
        }
      },
      {
        componentId: 'component_pull_to_refresh',
        componentType: 'pull_to_refresh',
        layout: {
          responsive: true,
          breakpoints: { mobile: 768, tablet: 1024 },
          adaptive: true,
          orientation: 'both'
        },
        styling: {
          theme: 'auto',
          fontSize: 16,
          iconSize: 24,
          spacing: 8,
          animation: true,
          reducedMotion: false
        },
        behavior: {
          lazyLoad: false,
          virtualScroll: false,
          prefetch: true,
          cache: true,
          offline: true
        },
        performance: {
          animation: true,
          transition: true,
          gpuAcceleration: true,
          memoryLimit: 30,
          frameRate: 60
        }
      }
    ];
    
    defaultComponents.forEach(component => this.addMobileComponent(component));
  }

  private loadDefaultOfflineSyncConfigs(): void {
    const defaultConfigs: OfflineSyncConfig[] = [
      {
        syncId: 'sync_portfolio',
        strategy: 'cache_first',
        cacheDuration: 3600000, // 1 hour
        syncInterval: 300000, // 5 minutes
        conflictResolution: 'client_wins',
        dataTypes: ['portfolio', 'positions', 'orders'],
        priority: 1
      },
      {
        syncId: 'sync_market_data',
        strategy: 'network_first',
        cacheDuration: 60000, // 1 minute
        syncInterval: 10000, // 10 seconds
        conflictResolution: 'server_wins',
        dataTypes: ['quotes', 'charts', 'news'],
        priority: 2
      }
    ];
    
    defaultConfigs.forEach(config => this.addOfflineSyncConfig(config));
  }

  private loadDefaultPushNotificationConfigs(): void {
    const defaultConfigs: PushNotificationConfig[] = [
      {
        notificationId: 'notif_trade_alert',
        type: 'trade_alert',
        priority: 'high',
        sound: 'default',
        vibration: true,
        badge: true,
        channels: ['trade_alerts'],
        conditions: [
          {
            conditionId: 'cond_trade_filled',
            field: 'status',
            operator: 'equals',
            value: 'filled'
          }
        ]
      },
      {
        notificationId: 'notif_risk_alert',
        type: 'risk_alert',
        priority: 'high',
        sound: 'alert',
        vibration: true,
        badge: true,
        channels: ['risk_alerts'],
        conditions: [
          {
            conditionId: 'cond_risk_breach',
            field: 'riskLevel',
            operator: 'equals',
            value: 'critical'
          }
        ]
      }
    ];
    
    defaultConfigs.forEach(config => this.addPushNotificationConfig(config));
  }

  private loadDefaultBiometricAuthConfig(): void {
    const config: BiometricAuthConfig = {
      authId: 'auth_biometric_default',
      methods: [
        {
          type: 'fingerprint',
          enabled: true,
          priority: 1
        },
        {
          type: 'face_id',
          enabled: true,
          priority: 2
        }
      ],
      fallbackToPin: true,
      timeout: 30000,
      maxAttempts: 3,
      lockoutDuration: 300000 // 5 minutes
    };
    
    this.addBiometricAuthConfig(config);
  }

  private loadAssetClassMobileInterfaces(): void {
    const interfaces: AssetClassMobileInterface[] = [
      {
        assetClass: 'stocks',
        layout: {
          portrait: {
            header: true,
            footer: true,
            mainContent: ['chart', 'positions', 'orders'],
            sidebars: [],
            overlays: ['order_entry']
          },
          landscape: {
            header: true,
            footer: true,
            mainContent: ['chart', 'positions'],
            sidebars: ['orders', 'watchlist'],
            overlays: ['order_entry']
          }
        },
        features: [
          { featureId: 'feat_quotes', name: 'Live Quotes', enabled: true, position: 'header', priority: 1 },
          { featureId: 'feat_chart', name: 'Interactive Charts', enabled: true, position: 'main', priority: 2 },
          { featureId: 'feat_orders', name: 'Quick Order Entry', enabled: true, position: 'overlay', priority: 3 }
        ],
        gestures: [
          this.gestureConfigs.get('gesture_chart_swipe')!,
          this.gestureConfigs.get('gesture_chart_pinch')!
        ],
        components: [
          this.mobileComponents.get('component_bottom_sheet')!,
          this.mobileComponents.get('component_pull_to_refresh')!
        ]
      },
      {
        assetClass: 'forex',
        layout: {
          portrait: {
            header: true,
            footer: true,
            mainContent: ['chart', 'rates', 'positions'],
            sidebars: [],
            overlays: ['order_entry']
          },
          landscape: {
            header: true,
            footer: true,
            mainContent: ['chart', 'rates'],
            sidebars: ['positions', 'order_book'],
            overlays: ['order_entry']
          }
        },
        features: [
          { featureId: 'feat_rates', name: 'Live Rates', enabled: true, position: 'header', priority: 1 },
          { featureId: 'feat_pairs', name: 'Currency Pairs', enabled: true, position: 'main', priority: 2 },
          { featureId: 'feat_calculator', name: 'Position Calculator', enabled: true, position: 'overlay', priority: 3 }
        ],
        gestures: [
          this.gestureConfigs.get('gesture_chart_swipe')!,
          this.gestureConfigs.get('gesture_chart_pinch')!
        ],
        components: [
          this.mobileComponents.get('component_bottom_sheet')!,
          this.mobileComponents.get('component_pull_to_refresh')!
        ]
      }
    ];
    
    interfaces.forEach(iface => {
      this.assetClassInterfaces.set(iface.assetClass, iface);
    });
  }
}