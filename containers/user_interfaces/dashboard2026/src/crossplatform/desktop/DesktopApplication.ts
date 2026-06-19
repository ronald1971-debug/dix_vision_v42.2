/**
 * Desktop Application System
 * Provides Electron-based desktop application with native performance optimization,
 * multi-monitor support, keyboard shortcuts, and system integration.
 */

// Desktop Application Configuration
export interface DesktopAppConfig {
  appId: string;
  appName: string;
  version: string;
  platform: 'windows' | 'macos' | 'linux';
  architecture: 'x64' | 'arm64';
  electronVersion: string;
  nodeVersion: string;
  chromiumVersion: string;
}

// Window Management
export interface WindowConfig {
  windowId: string;
  title: string;
  width: number;
  height: number;
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
  x?: number;
  y?: number;
  resizable: boolean;
  movable: boolean;
  minimizable: boolean;
  maximizable: boolean;
  closable: boolean;
  fullscreen: boolean;
  frame: boolean;
  transparent: boolean;
  alwaysOnTop: boolean;
  show: boolean;
  backgroundColor: string;
  webPreferences: WebPreferences;
}

export interface WebPreferences {
  nodeIntegration: boolean;
  contextIsolation: boolean;
  enableRemoteModule: boolean;
  sandbox: boolean;
  webSecurity: boolean;
  allowRunningInsecureContent: boolean;
  experimentalFeatures: boolean;
}

// Multi-Monitor Support
export interface MonitorInfo {
  monitorId: string;
  isPrimary: boolean;
  width: number;
  height: number;
  scaleFactor: number;
  position: { x: number; y: number };
  workArea: { x: number; y: number; width: number; height: number };
  rotation: number;
}

export interface MultiMonitorLayout {
  layoutId: string;
  name: string;
  windows: WindowPlacement[];
  created: number;
  lastUsed: number;
}

export interface WindowPlacement {
  windowId: string;
  monitorId: string;
  config: WindowConfig;
  position: { x: number; y: number };
  size: { width: number; height: number };
  state: 'normal' | 'maximized' | 'minimized' | 'fullscreen';
}

// Keyboard Shortcuts
export interface KeyboardShortcut {
  shortcutId: string;
  name: string;
  description: string;
  accelerator: string;
  context: string[];
  action: ShortcutAction;
  enabled: boolean;
  global: boolean;
}

export interface ShortcutAction {
  type: 'command' | 'navigation' | 'ui_action' | 'custom';
  command: string;
  parameters: Record<string, any>;
}

export interface ShortcutRegistry {
  shortcuts: Map<string, KeyboardShortcut>;
  globalShortcuts: Map<string, KeyboardShortcut>;
  contextShortcuts: Map<string, KeyboardShortcut[]>;
}

// System Tray Integration
export interface TrayConfig {
  trayId: string;
  icon: string;
  title: string;
  tooltip: string;
  menuItems: TrayMenuItem[];
  showOnStartup: boolean;
  minimizeToTray: boolean;
  closeToTray: boolean;
}

export interface TrayMenuItem {
  itemId: string;
  label: string;
  type: 'normal' | 'separator' | 'submenu' | 'checkbox' | 'radio';
  enabled: boolean;
  checked?: boolean;
  accelerator?: string;
  action?: string;
  submenu?: TrayMenuItem[];
}

// Native Performance Optimization
export interface PerformanceConfig {
  configId: string;
  hardwareAcceleration: boolean;
  gpuMemoryPolicy: 'default' | 'low' | 'high';
  cpuPolicy: 'default' | 'performance' | 'powersave';
  memoryPolicy: 'default' | 'low' | 'high';
  diskCache: boolean;
  cacheSize: number;
  preloadResources: string[];
  lazyLoading: boolean;
  backgroundProcesses: boolean;
  processPriority: 'low' | 'normal' | 'high';
}

export interface PerformanceMetrics {
  metricsId: string;
  timestamp: number;
  cpuUsage: number;
  memoryUsage: number;
  gpuMemory: number;
  diskUsage: number;
  networkActivity: number;
  frameRate: number;
  responseTime: number;
  startupTime: number;
}

// Local Data Caching
export interface CacheConfig {
  cacheId: string;
  strategy: 'memory' | 'disk' | 'hybrid';
  maxSize: number;
  maxAge: number;
  compression: boolean;
  encryption: boolean;
  persistence: boolean;
  syncWithCloud: boolean;
}

export interface CacheEntry {
  entryId: string;
  key: string;
  value: any;
  timestamp: number;
  lastAccessed: number;
  size: number;
  compressed: boolean;
  encrypted: boolean;
}

// Asset Class Desktop Layout
export interface AssetClassDesktopLayout {
  assetClass: 'stocks' | 'forex' | 'futures' | 'options';
  layout: DesktopLayoutConfig;
  panels: PanelConfig[];
  hotkeys: KeyboardShortcut[];
  theme: DesktopTheme;
}

export interface DesktopLayoutConfig {
  singleMonitor: LayoutConfiguration;
  dualMonitor: LayoutConfiguration;
  multiMonitor: LayoutConfiguration;
}

export interface LayoutConfiguration {
  mainLayout: string;
  sidebars: SidebarConfig[];
  toolbars: ToolbarConfig[];
  statusBars: StatusBarConfig[];
  panels: PanelLayout[];
}

export interface SidebarConfig {
  sidebarId: string;
  position: 'left' | 'right';
  width: number;
  collapsible: boolean;
  defaultContent: string[];
  resizable: boolean;
}

export interface ToolbarConfig {
  toolbarId: string;
  position: 'top' | 'bottom' | 'left' | 'right';
  items: ToolbarItem[];
  visible: boolean;
  lockable: boolean;
}

export interface ToolbarItem {
  itemId: string;
  icon: string;
  tooltip: string;
  action: string;
  separator?: boolean;
  dropdown?: ToolbarItem[];
}

export interface StatusBarConfig {
  statusBarId: string;
  position: 'top' | 'bottom';
  sections: StatusBarSection[];
  visible: boolean;
}

export interface StatusBarSection {
  sectionId: string;
  content: string;
  width: number;
  alignment: 'left' | 'center' | 'right';
  updateInterval: number;
}

export interface PanelLayout {
  panelId: string;
  panelType: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  docked: boolean;
  floating: boolean;
  content: string;
}

export interface PanelConfig {
  panelId: string;
  name: string;
  panelType: 'chart' | 'table' | 'watchlist' | 'order_entry' | 'depth' | 'time_sales' | 'custom';
  config: Record<string, any>;
  defaultPosition: string;
  resizable: boolean;
  closable: boolean;
  maximizable: boolean;
  tabbed: boolean;
}

export interface DesktopTheme {
  themeId: string;
  name: string;
  colors: ThemeColors;
  fonts: ThemeFonts;
  icons: IconTheme;
  spacing: SpacingTheme;
}

export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

export interface ThemeFonts {
  primary: string;
  secondary: string;
  code: string;
  ui: string;
  sizes: Record<string, number>;
}

export interface IconTheme {
  set: string;
  size: Record<string, number>;
  color: string;
}

export interface SpacingTheme {
  scale: number;
  unit: string;
  values: Record<string, number>;
}

// Desktop Application System
export class DesktopApplicationSystem {
  private appConfig: DesktopAppConfig;
  private windows: Map<string, WindowConfig>;
  private monitors: Map<string, MonitorInfo>;
  private layouts: Map<string, MultiMonitorLayout>;
  private shortcutRegistry: ShortcutRegistry;
  private trayConfigs: Map<string, TrayConfig>;
  private performanceConfig: PerformanceConfig;
  private performanceMetrics: Map<string, PerformanceMetrics>;
  private cacheConfigs: Map<string, CacheConfig>;
  private cacheEntries: Map<string, CacheEntry>;
  private assetClassLayouts: Map<string, AssetClassDesktopLayout>;
  private themes: Map<string, DesktopTheme>;
  private currentTheme: DesktopTheme;


  constructor() {
    this.appConfig = this.createDefaultAppConfig();
    this.windows = new Map();
    this.monitors = new Map();
    this.layouts = new Map();
    this.shortcutRegistry = {
      shortcuts: new Map(),
      globalShortcuts: new Map(),
      contextShortcuts: new Map()
    };
    this.trayConfigs = new Map();
    this.performanceConfig = this.createDefaultPerformanceConfig();
    this.performanceMetrics = new Map();
    this.cacheConfigs = new Map();
    this.cacheEntries = new Map();
    this.assetClassLayouts = new Map();
    this.themes = new Map();
    this.currentTheme = this.createDefaultTheme();
  }

  initialize(): void {
    this.detectMonitors();
    this.loadDefaultShortcuts();
    this.loadDefaultTrayConfig();
    this.loadDefaultCacheConfigs();
    this.loadAssetClassDesktopLayouts();
    this.loadDefaultThemes();
  }

  // Application Configuration
  getAppConfig(): DesktopAppConfig {
    return this.appConfig;
  }

  // Window Management
  createWindow(config: WindowConfig): string {
    const windowId = config.windowId || `window_${Date.now()}_${Math.random()}`;
    const windowConfig: WindowConfig = {
      ...config,
      windowId
    };
    
    this.windows.set(windowId, windowConfig);
    return windowId;
  }

  getWindow(windowId: string): WindowConfig | undefined {
    return this.windows.get(windowId);
  }

  closeWindow(windowId: string): void {
    this.windows.delete(windowId);
  }

  // Multi-Monitor Support
  detectMonitors(): void {
    // Simulate monitor detection
    const primaryMonitor: MonitorInfo = {
      monitorId: 'monitor_primary',
      isPrimary: true,
      width: 1920,
      height: 1080,
      scaleFactor: 1,
      position: { x: 0, y: 0 },
      workArea: { x: 0, y: 0, width: 1920, height: 1080 },
      rotation: 0
    };
    
    this.monitors.set(primaryMonitor.monitorId, primaryMonitor);
    
    // Could add secondary monitors
  }

  getMonitors(): MonitorInfo[] {
    return Array.from(this.monitors.values());
  }

  getPrimaryMonitor(): MonitorInfo | undefined {
    return Array.from(this.monitors.values()).find(m => m.isPrimary);
  }

  createLayout(name: string, windows: WindowPlacement[]): string {
    const layoutId = `layout_${Date.now()}_${Math.random()}`;
    const layout: MultiMonitorLayout = {
      layoutId,
      name,
      windows,
      created: Date.now(),
      lastUsed: Date.now()
    };
    
    this.layouts.set(layoutId, layout);
    return layoutId;
  }

  saveLayout(layoutId: string): void {
    const layout = this.layouts.get(layoutId);
    if (layout) {
      layout.lastUsed = Date.now();
      this.layouts.set(layoutId, layout);
    }
  }

  loadLayout(layoutId: string): MultiMonitorLayout | undefined {
    const layout = this.layouts.get(layoutId);
    if (layout) {
      layout.lastUsed = Date.now();
      this.layouts.set(layoutId, layout);
    }
    return layout;
  }

  // Keyboard Shortcuts
  registerShortcut(shortcut: KeyboardShortcut): void {
    this.shortcutRegistry.shortcuts.set(shortcut.shortcutId, shortcut);
    
    if (shortcut.global) {
      this.shortcutRegistry.globalShortcuts.set(shortcut.shortcutId, shortcut);
    }
    
    shortcut.context.forEach(context => {
      if (!this.shortcutRegistry.contextShortcuts.has(context)) {
        this.shortcutRegistry.contextShortcuts.set(context, []);
      }
      this.shortcutRegistry.contextShortcuts.get(context)!.push(shortcut);
    });
  }

  unregisterShortcut(shortcutId: string): void {
    const shortcut = this.shortcutRegistry.shortcuts.get(shortcutId);
    if (shortcut) {
      this.shortcutRegistry.shortcuts.delete(shortcutId);
      
      if (shortcut.global) {
        this.shortcutRegistry.globalShortcuts.delete(shortcutId);
      }
      
      shortcut.context.forEach(context => {
        const contextShortcuts = this.shortcutRegistry.contextShortcuts.get(context);
        if (contextShortcuts) {
          const index = contextShortcuts.findIndex(s => s.shortcutId === shortcutId);
          if (index > -1) {
            contextShortcuts.splice(index, 1);
          }
        }
      });
    }
  }

  executeShortcut(shortcutId: string, context?: string): void {
    let shortcut: KeyboardShortcut | undefined;
    
    if (context) {
      const contextShortcuts = this.shortcutRegistry.contextShortcuts.get(context);
      if (contextShortcuts) {
        shortcut = contextShortcuts.find(s => s.shortcutId === shortcutId);
      }
    }
    
    if (!shortcut) {
      shortcut = this.shortcutRegistry.shortcuts.get(shortcutId);
    }
    
    if (shortcut && shortcut.enabled) {
      this.executeShortcutAction(shortcut.action);
    }
  }

  private executeShortcutAction(action: ShortcutAction): void {
    // Simulate action execution
    console.log(`Executing shortcut action: ${action.command}`, action.parameters);
  }

  getShortcuts(context?: string): KeyboardShortcut[] {
    if (context) {
      return this.shortcutRegistry.contextShortcuts.get(context) || [];
    }
    return Array.from(this.shortcutRegistry.shortcuts.values());
  }

  // System Tray Integration
  setTrayConfig(config: TrayConfig): void {
    this.trayConfigs.set(config.trayId, config);
  }

  getTrayConfig(trayId: string): TrayConfig | undefined {
    return this.trayConfigs.get(trayId);
  }

  // Performance Optimization
  getPerformanceConfig(): PerformanceConfig {
    return this.performanceConfig;
  }

  updatePerformanceConfig(updates: Partial<PerformanceConfig>): void {
    this.performanceConfig = { ...this.performanceConfig, ...updates };
  }

  collectPerformanceMetrics(): PerformanceMetrics {
    const metrics: PerformanceMetrics = {
      metricsId: `metrics_${Date.now()}_${Math.random()}`,
      timestamp: Date.now(),
      cpuUsage: this.measureCPUUsage(),
      memoryUsage: this.measureMemoryUsage(),
      gpuMemory: this.measureGPUMemory(),
      diskUsage: this.measureDiskUsage(),
      networkActivity: this.measureNetworkActivity(),
      frameRate: this.measureFrameRate(),
      responseTime: this.measureResponseTime(),
      startupTime: this.measureStartupTime()
    };
    
    this.performanceMetrics.set(metrics.metricsId, metrics);
    return metrics;
  }

  private measureCPUUsage(): number {
    // Simulated CPU usage
    return Math.random() * 30; // 0-30%
  }

  private measureMemoryUsage(): number {
    // Simulated memory usage
    if ('memory' in performance) {
      return (performance as any).memory.usedJSHeapSize / 1024 / 1024;
    }
    return 200; // 200 MB placeholder
  }

  private measureGPUMemory(): number {
    // Simulated GPU memory
    return 100; // 100 MB placeholder
  }

  private measureDiskUsage(): number {
    // Simulated disk usage
    return 500; // 500 MB placeholder
  }

  private measureNetworkActivity(): number {
    // Simulated network activity
    return Math.random() * 10; // 0-10 MB/s
  }

  private measureFrameRate(): number {
    // Simulated frame rate
    return 60;
  }

  private measureResponseTime(): number {
    // Simulated response time
    return 16; // 16ms
  }

  private measureStartupTime(): number {
    // Simulated startup time
    return 2000; // 2 seconds
  }

  // Local Data Caching
  addCacheConfig(config: CacheConfig): void {
    this.cacheConfigs.set(config.cacheId, config);
  }

  async cacheData(cacheId: string, key: string, value: any): Promise<void> {
    const config = this.cacheConfigs.get(cacheId);
    if (!config) {
      throw new Error(`Cache config ${cacheId} not found`);
    }
    
    const entry: CacheEntry = {
      entryId: `entry_${Date.now()}_${Math.random()}`,
      key,
      value: config.compression ? this.compressData(value) : value,
      timestamp: Date.now(),
      lastAccessed: Date.now(),
      size: this.calculateSize(value),
      compressed: config.compression,
      encrypted: config.encryption
    };
    
    if (config.encryption) {
      entry.value = this.encryptData(entry.value);
    }
    
    this.cacheEntries.set(`${cacheId}:${key}`, entry);
  }

  async getCachedData(cacheId: string, key: string): Promise<any | undefined> {
    const entry = this.cacheEntries.get(`${cacheId}:${key}`);
    if (!entry) return undefined;
    
    const config = this.cacheConfigs.get(cacheId);
    if (!config) return undefined;
    
    let value = entry.value;
    
    if (entry.encrypted) {
      value = this.decryptData(value);
    }
    
    if (entry.compressed) {
      value = this.decompressData(value);
    }
    
    entry.lastAccessed = Date.now();
    this.cacheEntries.set(`${cacheId}:${key}`, entry);
    
    return value;
  }

  private compressData(data: any): any {
    // Simplified compression - would use actual compression library
    return data;
  }

  private decompressData(data: any): any {
    // Simplified decompression
    return data;
  }

  private encryptData(data: any): any {
    // Simplified encryption - would use actual encryption
    return data;
  }

  private decryptData(data: any): any {
    // Simplified decryption
    return data;
  }

  private calculateSize(data: any): number {
    // Simplified size calculation
    return JSON.stringify(data).length;
  }

  // Asset Class Desktop Layouts
  getAssetClassLayout(assetClass: string): AssetClassDesktopLayout | undefined {
    return this.assetClassLayouts.get(assetClass);
  }

  // Theme Management
  addTheme(theme: DesktopTheme): void {
    this.themes.set(theme.themeId, theme);
  }

  setTheme(themeId: string): void {
    const theme = this.themes.get(themeId);
    if (theme) {
      this.currentTheme = theme;
    }
  }

  getCurrentTheme(): DesktopTheme {
    return this.currentTheme;
  }

  // Default Configuration Methods
  private createDefaultAppConfig(): DesktopAppConfig {
    return {
      appId: 'com.dashboard2026.desktop',
      appName: 'Dashboard2026',
      version: '1.0.0',
      platform: this.detectPlatform(),
      architecture: 'x64',
      electronVersion: '25.0.0',
      nodeVersion: '18.0.0',
      chromiumVersion: '114.0.0'
    };
  }

  private detectPlatform(): 'windows' | 'macos' | 'linux' {
    const userAgent = navigator.userAgent;
    if (userAgent.includes('Windows')) return 'windows';
    if (userAgent.includes('Mac')) return 'macos';
    if (userAgent.includes('Linux')) return 'linux';
    return 'windows'; // Default
  }

  private createDefaultPerformanceConfig(): PerformanceConfig {
    return {
      configId: 'perf_config_default',
      hardwareAcceleration: true,
      gpuMemoryPolicy: 'default',
      cpuPolicy: 'default',
      memoryPolicy: 'default',
      diskCache: true,
      cacheSize: 500 * 1024 * 1024, // 500 MB
      preloadResources: [],
      lazyLoading: true,
      backgroundProcesses: true,
      processPriority: 'normal'
    };
  }

  private loadDefaultShortcuts(): void {
    const defaultShortcuts: KeyboardShortcut[] = [
      {
        shortcutId: 'shortcut_new_order',
        name: 'New Order',
        description: 'Open new order dialog',
        accelerator: 'CmdOrCtrl+N',
        context: ['global'],
        action: {
          type: 'ui_action',
          command: 'open_order_dialog',
          parameters: {}
        },
        enabled: true,
        global: true
      },
      {
        shortcutId: 'shortcut_buy',
        name: 'Quick Buy',
        description: 'Execute quick buy',
        accelerator: 'CmdOrCtrl+B',
        context: ['chart', 'watchlist'],
        action: {
          type: 'command',
          command: 'quick_buy',
          parameters: {}
        },
        enabled: true,
        global: false
      },
      {
        shortcutId: 'shortcut_sell',
        name: 'Quick Sell',
        description: 'Execute quick sell',
        accelerator: 'CmdOrCtrl+S',
        context: ['chart', 'watchlist'],
        action: {
          type: 'command',
          command: 'quick_sell',
          parameters: {}
        },
        enabled: true,
        global: false
      },
      {
        shortcutId: 'shortcut_close_position',
        name: 'Close Position',
        description: 'Close selected position',
        accelerator: 'CmdOrCtrl+W',
        context: ['positions'],
        action: {
          type: 'command',
          command: 'close_position',
          parameters: {}
        },
        enabled: true,
        global: false
      },
      {
        shortcutId: 'shortcut_refresh',
        name: 'Refresh',
        description: 'Refresh data',
        accelerator: 'F5',
        context: ['global'],
        action: {
          type: 'command',
          command: 'refresh_data',
          parameters: {}
        },
        enabled: true,
        global: true
      },
      {
        shortcutId: 'shortcut_fullscreen',
        name: 'Toggle Fullscreen',
        description: 'Toggle fullscreen mode',
        accelerator: 'F11',
        context: ['global'],
        action: {
          type: 'ui_action',
          command: 'toggle_fullscreen',
          parameters: {}
        },
        enabled: true,
        global: true
      }
    ];
    
    defaultShortcuts.forEach(shortcut => this.registerShortcut(shortcut));
  }

  private loadDefaultTrayConfig(): void {
    const config: TrayConfig = {
      trayId: 'tray_default',
      icon: '/assets/icon.png',
      title: 'Dashboard2026',
      tooltip: 'Dashboard2026 - Professional Trading Platform',
      menuItems: [
        {
          itemId: 'item_show',
          label: 'Show Dashboard',
          type: 'normal',
          enabled: true,
          action: 'show_window'
        },
        {
          itemId: 'item_hide',
          label: 'Hide to Tray',
          type: 'normal',
          enabled: true,
          action: 'hide_window'
        },
        {
          itemId: 'sep1',
          label: '',
          type: 'separator',
          enabled: true
        },
        {
          itemId: 'item_settings',
          label: 'Settings',
          type: 'normal',
          enabled: true,
          action: 'open_settings'
        },
        {
          itemId: 'item_about',
          label: 'About',
          type: 'normal',
          enabled: true,
          action: 'open_about'
        },
        {
          itemId: 'sep2',
          label: '',
          type: 'separator',
          enabled: true
        },
        {
          itemId: 'item_quit',
          label: 'Quit',
          type: 'normal',
          enabled: true,
          action: 'quit_app'
        }
      ],
      showOnStartup: true,
      minimizeToTray: true,
      closeToTray: true
    };
    
    this.setTrayConfig(config);
  }

  private loadDefaultCacheConfigs(): void {
    const configs: CacheConfig[] = [
      {
        cacheId: 'cache_market_data',
        strategy: 'hybrid',
        maxSize: 100 * 1024 * 1024, // 100 MB
        maxAge: 60000, // 1 minute
        compression: true,
        encryption: false,
        persistence: true,
        syncWithCloud: false
      },
      {
        cacheId: 'cache_user_data',
        strategy: 'disk',
        maxSize: 50 * 1024 * 1024, // 50 MB
        maxAge: 3600000, // 1 hour
        compression: true,
        encryption: true,
        persistence: true,
        syncWithCloud: true
      },
      {
        cacheId: 'cache_ui_data',
        strategy: 'memory',
        maxSize: 20 * 1024 * 1024, // 20 MB
        maxAge: 300000, // 5 minutes
        compression: false,
        encryption: false,
        persistence: false,
        syncWithCloud: false
      }
    ];
    
    configs.forEach(config => this.addCacheConfig(config));
  }

  private loadAssetClassDesktopLayouts(): void {
    const layouts: AssetClassDesktopLayout[] = [
      {
        assetClass: 'stocks',
        layout: {
          singleMonitor: this.createStockLayoutSingle(),
          dualMonitor: this.createStockLayoutDual(),
          multiMonitor: this.createStockLayoutMulti()
        },
        panels: [
          {
            panelId: 'panel_chart_main',
            name: 'Main Chart',
            panelType: 'chart',
            config: { chartType: 'candlestick', indicators: ['MA', 'RSI', 'MACD'] },
            defaultPosition: 'center',
            resizable: true,
            closable: false,
            maximizable: true,
            tabbed: false
          },
          {
            panelId: 'panel_watchlist',
            name: 'Watchlist',
            panelType: 'watchlist',
            config: { columns: ['symbol', 'price', 'change', 'volume'] },
            defaultPosition: 'left',
            resizable: true,
            closable: true,
            maximizable: true,
            tabbed: true
          },
          {
            panelId: 'panel_positions',
            name: 'Positions',
            panelType: 'table',
            config: { columns: ['symbol', 'quantity', 'entry', 'pnl'] },
            defaultPosition: 'bottom',
            resizable: true,
            closable: true,
            maximizable: true,
            tabbed: true
          }
        ],
        hotkeys: [],
        theme: this.currentTheme
      }
    ];
    
    layouts.forEach(layout => {
      this.assetClassLayouts.set(layout.assetClass, layout);
    });
  }

  private createStockLayoutSingle(): LayoutConfiguration {
    return {
      mainLayout: 'standard',
      sidebars: [
        {
          sidebarId: 'sidebar_left',
          position: 'left',
          width: 300,
          collapsible: true,
          defaultContent: ['watchlist', 'positions'],
          resizable: true
        }
      ],
      toolbars: [
        {
          toolbarId: 'toolbar_top',
          position: 'top',
          items: [],
          visible: true,
          lockable: false
        }
      ],
      statusBars: [
        {
          statusBarId: 'statusbar_bottom',
          position: 'bottom',
          sections: [
            { sectionId: 'section_account', content: 'Account Info', width: 200, alignment: 'left', updateInterval: 5000 },
            { sectionId: 'section_market', content: 'Market Status', width: 150, alignment: 'center', updateInterval: 1000 },
            { sectionId: 'section_time', content: 'Time', width: 100, alignment: 'right', updateInterval: 1000 }
          ],
          visible: true
        }
      ],
      panels: []
    };
  }

  private createStockLayoutDual(): LayoutConfiguration {
    // Simplified dual monitor layout
    return this.createStockLayoutSingle();
  }

  private createStockLayoutMulti(): LayoutConfiguration {
    // Simplified multi monitor layout
    return this.createStockLayoutSingle();
  }

  private loadDefaultThemes(): void {
    const themes: DesktopTheme[] = [
      this.createDefaultTheme(),
      this.createDarkTheme()
    ];
    
    themes.forEach(theme => this.addTheme(theme));
  }

  private createDefaultTheme(): DesktopTheme {
    return {
      themeId: 'theme_light',
      name: 'Light Theme',
      colors: {
        primary: '#1976d2',
        secondary: '#dc004e',
        background: '#ffffff',
        surface: '#f5f5f5',
        text: '#333333',
        textSecondary: '#666666',
        border: '#e0e0e0',
        success: '#4caf50',
        warning: '#ff9800',
        error: '#f44336',
        info: '#2196f3'
      },
      fonts: {
        primary: 'Segoe UI, sans-serif',
        secondary: 'Roboto, sans-serif',
        code: 'Consolas, monospace',
        ui: 'Segoe UI, sans-serif',
        sizes: {
          xs: 12,
          sm: 14,
          md: 16,
          lg: 18,
          xl: 24
        }
      },
      icons: {
        set: 'material',
        size: {
          sm: 16,
          md: 24,
          lg: 32,
          xl: 48
        },
        color: '#666666'
      },
      spacing: {
        scale: 8,
        unit: 'px',
        values: {
          xs: 4,
          sm: 8,
          md: 16,
          lg: 24,
          xl: 32
        }
      }
    };
  }

  private createDarkTheme(): DesktopTheme {
    const lightTheme = this.createDefaultTheme();
    return {
      ...lightTheme,
      themeId: 'theme_dark',
      name: 'Dark Theme',
      colors: {
        primary: '#2196f3',
        secondary: '#e91e63',
        background: '#1e1e1e',
        surface: '#2d2d2d',
        text: '#ffffff',
        textSecondary: '#b0b0b0',
        border: '#404040',
        success: '#66bb6a',
        warning: '#ffa726',
        error: '#ef5350',
        info: '#42a5f5'
      }
    };
  }
}