/**
 * Cross-Platform Module Index
 * Central exports for mobile optimization, desktop application, and API integration systems.
 */

// Mobile Optimization
export {
  type MobileDeviceInfo,
  type ScreenSize,
  type DeviceCapabilities,
  type TouchGestureConfig,
  type GestureAction,
  type GestureResult,
  type MobileComponentConfig,
  type MobileLayout,
  type MobileStyling,
  type ComponentBehavior,
  type PerformanceConfig as MobilePerformanceConfig,
  type OfflineSyncConfig,
  type SyncStatus,
  type SyncError,
  type PushNotificationConfig,
  type NotificationCondition,
  type PushNotification,
  type BiometricAuthConfig,
  type BiometricMethod,
  type AuthResult,
  type AssetClassMobileInterface,
  type MobileLayoutConfig,
  type LayoutConfiguration as MobileLayoutConfiguration,
  type MobileFeature,
  type MobilePerformanceMetrics
} from './mobile/MobileOptimization';

// Desktop Application
export {
  type DesktopAppConfig,
  type WindowConfig,
  type WebPreferences,
  type MonitorInfo,
  type MultiMonitorLayout,
  type WindowPlacement,
  type KeyboardShortcut,
  type ShortcutAction,
  type ShortcutRegistry,
  type TrayConfig,
  type TrayMenuItem,
  type PerformanceConfig as DesktopPerformanceConfig,
  type PerformanceMetrics,
  type CacheConfig,
  type CacheEntry,
  type AssetClassDesktopLayout,
  type DesktopLayoutConfig,
  type LayoutConfiguration as DesktopLayoutConfiguration,
  type SidebarConfig,
  type ToolbarConfig,
  type ToolbarItem,
  type StatusBarConfig,
  type StatusBarSection,
  type PanelLayout,
  type PanelConfig,
  type DesktopTheme,
  type ThemeColors,
  type ThemeFonts,
  type IconTheme,
  type SpacingTheme
} from './desktop/DesktopApplication';

// API Integration
export {
  type APIConfig,
  type AuthenticationConfig,
  type OAuth2Config,
  type JWTConfig,
  type RateLimitConfig,
  type CORSConfig,
  type LoggingConfig,
  type RESTEndpoint,
  type APIParameter,
  type RequestBodySchema,
  type ResponseSchema,
  type PropertySchema,
  type WebSocketEndpoint,
  type WebSocketRateLimit,
  type MessageType,
  type HeartbeatConfig,
  type WebSocketConnection,
  type ConnectionMetrics,
  type WebhookConfig,
  type WebhookEvent,
  type EventFilter,
  type RetryPolicy,
  type WebhookDelivery,
  type ThirdPartyApp,
  type AppCategory,
  type PricingInfo,
  type PricingTier,
  type AppPermission,
  type AppEndpoint,
  type APIDocumentation,
  type AuthenticationDocs,
  type AuthExample,
  type CodeExample,
  type SchemaDefinition,
  type DeveloperPortal,
  type DeveloperPermission,
  type DeveloperApp,
  type UsageStats,
  type BillingInfo,
  type AssetClassAPIEndpoints
} from './api/APIIntegration';

// Module Instances
import { MobileOptimizationSystem } from './mobile/MobileOptimization';
import { DesktopApplicationSystem } from './desktop/DesktopApplication';
import { APIIntegrationSystem } from './api/APIIntegration';

export { MobileOptimizationSystem, DesktopApplicationSystem, APIIntegrationSystem };

export const mobileOptimization = new MobileOptimizationSystem();
export const desktopApplication = new DesktopApplicationSystem();
export const apiIntegration = new APIIntegrationSystem();

// Initialize all systems
export function initializeCrossPlatform(): void {
  mobileOptimization.initialize();
  desktopApplication.initialize();
  apiIntegration.initialize();
}

// Module Information
export const CrossPlatformModuleInfo = {
  name: 'Cross-Platform Module',
  version: '1.0.0',
  description: 'Comprehensive cross-platform support including mobile, desktop, and API integration',
  components: [
    'Mobile Optimization',
    'Desktop Application',
    'API Integration'
  ],
  features: [
    'Responsive mobile design',
    'Touch gesture support',
    'Offline mode with sync',
    'Push notifications',
    'Biometric authentication',
    'Electron desktop app',
    'Multi-monitor support',
    'Keyboard shortcuts',
    'System tray integration',
    'REST API',
    'WebSocket API',
    'Webhook system',
    'Third-party marketplace',
    'Developer portal'
  ],
  platforms: [
    'iOS',
    'Android',
    'Web',
    'Windows',
    'macOS',
    'Linux'
  ],
  integrationPoints: [
    'Portfolio Management',
    'Trading Execution',
    'Risk Management',
    'Compliance',
    'Analytics'
  ]
};