/**
 * Shared Analytics Infrastructure
 * 
 * Core analytics infrastructure that can be used by all domains
 * for metrics collection, reporting, dashboards, and real-time analytics.
 */

// ============================================================================
// Analytics Types and Interfaces
// ============================================================================

export interface AnalyticsMetrics {
  performance: PerformanceMetrics;
  usage: UsageMetrics;
  business: BusinessMetrics;
  operational: OperationalMetrics;
}

export interface PerformanceMetrics {
  latency: number;
  throughput: number;
  errorRate: number;
  availability: number;
  resourceUtilization: number;
}

export interface UsageMetrics {
  activeUsers: number;
  requestCount: number;
  featureUsage: Record<string, number>;
  sessionDuration: number;
  bounceRate: number;
}

export interface BusinessMetrics {
  conversionRate: number;
  revenue: number;
  costs: number;
  profit: number;
  efficiency: number;
}

export interface OperationalMetrics {
  uptime: number;
  downtime: number;
  incidents: number;
  meanTimeToRecovery: number;
  meanTimeBetweenFailures: number;
}

export interface AnalyticsReport {
  id: string;
  domain: string;
  type: ReportType;
  period: ReportPeriod;
  generatedAt: Date;
  data: ReportData;
}

export type ReportType = 'daily' | 'weekly' | 'monthly' | 'custom';

export interface ReportPeriod {
  start: Date;
  end: Date;
}

export interface ReportData {
  metrics: AnalyticsMetrics;
  trends: TrendData[];
  insights: Insight[];
  recommendations: Recommendation[];
}

export interface TrendData {
  metric: string;
  values: number[];
  timestamps: Date[];
  trend: 'increasing' | 'decreasing' | 'stable';
  change: number;
}

export interface Insight {
  id: string;
  type: InsightType;
  severity: 'info' | 'warning' | 'critical';
  title: string;
  description: string;
  data: any;
  timestamp: Date;
}

export type InsightType = 'anomaly' | 'opportunity' | 'risk' | 'optimization';

export interface Recommendation {
  id: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  title: string;
  description: string;
  actionItems: string[];
  expectedImpact: string;
  timestamp: Date;
}

export interface AnalyticsDashboard {
  id: string;
  domain: string;
  name: string;
  widgets: DashboardWidget[];
  refreshInterval: number;
  lastUpdated: Date;
}

export interface DashboardWidget {
  id: string;
  type: WidgetType;
  title: string;
  configuration: WidgetConfiguration;
  position: WidgetPosition;
}

export type WidgetType = 'metric' | 'chart' | 'table' | 'heatmap' | 'gauge' | 'map';

export interface WidgetConfiguration {
  dataSource: string;
  filters: Record<string, any>;
  aggregation: string;
  timeRange: string;
  thresholds?: number[];
}

export interface WidgetPosition {
  row: number;
  column: number;
  width: number;
  height: number;
}

// ============================================================================
// Real-time Analytics
// ============================================================================

export interface RealtimeAnalytics {
  domain: string;
  currentMetrics: AnalyticsMetrics;
  recentEvents: AnalyticsEvent[];
  alerts: AnalyticsAlert[];
  predictions: RealtimePrediction[];
}

export interface AnalyticsEvent {
  id: string;
  domain: string;
  type: string;
  title?: string;
  message?: string;
  data: any;
  timestamp: Date;
  severity?: 'info' | 'warning' | 'error' | 'critical';
}

export interface AnalyticsAlert {
  id: string;
  domain: string;
  type: AlertType;
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  data: any;
  timestamp: Date;
  acknowledged: boolean;
}

export type AlertType = 'threshold' | 'anomaly' | 'pattern' | 'prediction';

export interface RealtimePrediction {
  id: string;
  domain: string;
  metric: string;
  currentValue: number;
  predictedValue: number;
  confidence: number;
  timeHorizon: number; // minutes
  timestamp: Date;
}

// ============================================================================
// Analytics Engine
// ============================================================================

export class AnalyticsEngine {
  private static instance: AnalyticsEngine;
  private metrics: Map<string, AnalyticsMetrics> = new Map();
  private events: AnalyticsEvent[] = [];
  private alerts: AnalyticsAlert[] = [];
  private predictions: RealtimePrediction[] = [];
  private dashboards: Map<string, AnalyticsDashboard> = new Map();

  private constructor() {
    this.initializeEngine();
  }

  static getInstance(): AnalyticsEngine {
    if (!AnalyticsEngine.instance) {
      AnalyticsEngine.instance = new AnalyticsEngine();
    }
    return AnalyticsEngine.instance;
  }

  private initializeEngine(): void {
    // Initialize analytics engine
    console.log('Analytics Engine initialized');
  }

  // Metrics Management
  recordMetrics(domain: string, metrics: AnalyticsMetrics): void {
    this.metrics.set(domain, metrics);
    this.checkThresholds(domain, metrics);
  }

  getMetrics(domain: string): AnalyticsMetrics | undefined {
    return this.metrics.get(domain);
  }

  getAllMetrics(): Record<string, AnalyticsMetrics> {
    return Object.fromEntries(this.metrics);
  }

  // Event Management
  recordEvent(event: AnalyticsEvent): void {
    this.events.push(event);
    this.analyzeEvent(event);
    this.cleanupOldEvents();
  }

  getEvents(domain?: string, type?: string): AnalyticsEvent[] {
    return this.events.filter(event => {
      if (domain && event.domain !== domain) return false;
      if (type && event.type !== type) return false;
      return true;
    });
  }

  private cleanupOldEvents(): void {
    const maxEvents = 10000;
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours
    
    this.events = this.events.filter(event => {
      const age = Date.now() - event.timestamp.getTime();
      return age < maxAge;
    });

    if (this.events.length > maxEvents) {
      this.events = this.events.slice(-maxEvents);
    }
  }

  // Alert Management
  createAlert(alert: AnalyticsAlert): void {
    this.alerts.push(alert);
  }

  getAlerts(domain?: string, acknowledged?: boolean): AnalyticsAlert[] {
    return this.alerts.filter(alert => {
      if (domain && alert.domain !== domain) return false;
      if (acknowledged !== undefined && alert.acknowledged !== acknowledged) return false;
      return true;
    });
  }

  acknowledgeAlert(alertId: string): void {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
    }
  }

  // Prediction Management
  addPrediction(prediction: RealtimePrediction): void {
    this.predictions.push(prediction);
    this.cleanupOldPredictions();
  }

  getPredictions(domain?: string): RealtimePrediction[] {
    return this.predictions.filter(prediction => {
      if (domain && prediction.domain !== domain) return false;
      return true;
    });
  }

  private cleanupOldPredictions(): void {
    const maxAge = 60 * 60 * 1000; // 1 hour
    
    this.predictions = this.predictions.filter(prediction => {
      const age = Date.now() - prediction.timestamp.getTime();
      return age < maxAge;
    });
  }

  // Dashboard Management
  createDashboard(dashboard: AnalyticsDashboard): void {
    this.dashboards.set(dashboard.id, dashboard);
  }

  getDashboard(id: string): AnalyticsDashboard | undefined {
    return this.dashboards.get(id);
  }

  getDashboards(domain?: string): AnalyticsDashboard[] {
    return Array.from(this.dashboards.values()).filter(dashboard => {
      if (domain && dashboard.domain !== domain) return false;
      return true;
    });
  }

  updateDashboard(id: string, updates: Partial<AnalyticsDashboard>): void {
    const dashboard = this.dashboards.get(id);
    if (dashboard) {
      Object.assign(dashboard, updates, { lastUpdated: new Date() });
    }
  }

  // Analysis Methods
  private analyzeEvent(event: AnalyticsEvent): void {
    // Analyze event for patterns and anomalies
    if (event.severity === 'error' || event.severity === 'critical') {
      this.createAlert({
        id: `alert-${event.id}`,
        domain: event.domain,
        type: 'anomaly',
        severity: event.severity,
        title: `${event.domain} - ${event.type}`,
        message: `Event requires attention: ${event.type}`,
        data: event.data,
        timestamp: event.timestamp,
        acknowledged: false,
      });
    }
  }

  private checkThresholds(domain: string, metrics: AnalyticsMetrics): void {
    // Check performance thresholds
    if (metrics.performance.errorRate > 0.05) {
      this.createAlert({
        id: `alert-error-rate-${domain}-${Date.now()}`,
        domain,
        type: 'threshold',
        severity: 'warning',
        title: 'High Error Rate',
        message: `Error rate exceeds 5%: ${(metrics.performance.errorRate * 100).toFixed(2)}%`,
        data: metrics,
        timestamp: new Date(),
        acknowledged: false,
      });
    }

    if (metrics.performance.availability < 0.99) {
      this.createAlert({
        id: `alert-availability-${domain}-${Date.now()}`,
        domain,
        type: 'threshold',
        severity: 'error',
        title: 'Low Availability',
        message: `Availability below 99%: ${(metrics.performance.availability * 100).toFixed(2)}%`,
        data: metrics,
        timestamp: new Date(),
        acknowledged: false,
      });
    }

    if (metrics.performance.latency > 1000) {
      this.createAlert({
        id: `alert-latency-${domain}-${Date.now()}`,
        domain,
        type: 'threshold',
        severity: 'warning',
        title: 'High Latency',
        message: `Latency exceeds 1000ms: ${metrics.performance.latency.toFixed(2)}ms`,
        data: metrics,
        timestamp: new Date(),
        acknowledged: false,
      });
    }
  }

  // Report Generation
  generateReport(domain: string, type: ReportType, period: ReportPeriod): AnalyticsReport {
    const metrics = this.metrics.get(domain);
    const events = this.getEvents(domain);
    const insights = this.generateInsights(domain, metrics, events);
    const trends = this.generateTrends(domain);
    const recommendations = this.generateRecommendations(insights);

    return {
      id: `report-${domain}-${type}-${Date.now()}`,
      domain,
      type,
      period,
      generatedAt: new Date(),
      data: {
        metrics: metrics || this.getDefaultMetrics(),
        trends,
        insights,
        recommendations,
      },
    };
  }

  private getDefaultMetrics(): AnalyticsMetrics {
    return {
      performance: {
        latency: 0,
        throughput: 0,
        errorRate: 0,
        availability: 1,
        resourceUtilization: 0,
      },
      usage: {
        activeUsers: 0,
        requestCount: 0,
        featureUsage: {},
        sessionDuration: 0,
        bounceRate: 0,
      },
      business: {
        conversionRate: 0,
        revenue: 0,
        costs: 0,
        profit: 0,
        efficiency: 0,
      },
      operational: {
        uptime: 0,
        downtime: 0,
        incidents: 0,
        meanTimeToRecovery: 0,
        meanTimeBetweenFailures: 0,
      },
    };
  }

  private generateInsights(domain: string, metrics?: AnalyticsMetrics, events?: AnalyticsEvent[]): Insight[] {
    const insights: Insight[] = [];

    if (metrics) {
      // Performance insights
      if (metrics.performance.latency > 500) {
        insights.push({
          id: `insight-latency-${domain}-${Date.now()}`,
          type: 'risk',
          severity: 'warning',
          title: 'Performance Degradation',
          description: 'Latency is higher than normal',
          data: { latency: metrics.performance.latency },
          timestamp: new Date(),
        });
      }

      // Usage insights
      if (metrics.usage.activeUsers > 0) {
        insights.push({
          id: `insight-users-${domain}-${Date.now()}`,
          type: 'opportunity',
          severity: 'info',
          title: 'User Activity',
          description: `Currently ${metrics.usage.activeUsers} active users`,
          data: { activeUsers: metrics.usage.activeUsers },
          timestamp: new Date(),
        });
      }
    }

    if (events && events.length > 0) {
      const errorEvents = events.filter(e => e.severity === 'error' || e.severity === 'critical');
      if (errorEvents.length > 0) {
        insights.push({
          id: `insight-errors-${domain}-${Date.now()}`,
          type: 'risk',
          severity: 'critical',
          title: 'Error Spike',
          description: `${errorEvents.length} errors detected`,
          data: { errorCount: errorEvents.length },
          timestamp: new Date(),
        });
      }
    }

    return insights;
  }

  private generateTrends(_domain: string): TrendData[] {
    // Generate trend data - in a real implementation, this would use historical data
    return [];
  }

  private generateRecommendations(insights: Insight[]): Recommendation[] {
    const recommendations: Recommendation[] = [];

    for (const insight of insights) {
      if (insight.type === 'risk' && insight.severity === 'critical') {
        recommendations.push({
          id: `rec-${insight.id}`,
          priority: 'urgent',
          title: `Address: ${insight.title}`,
          description: insight.description,
          actionItems: ['Investigate the issue', 'Implement fix', 'Monitor impact'],
          expectedImpact: 'Reduced risk and improved performance',
          timestamp: new Date(),
        });
      } else if (insight.type === 'risk' && insight.severity === 'warning') {
        recommendations.push({
          id: `rec-${insight.id}`,
          priority: 'high',
          title: `Monitor: ${insight.title}`,
          description: insight.description,
          actionItems: ['Monitor the situation', 'Prepare response plan'],
          expectedImpact: 'Prevent escalation',
          timestamp: new Date(),
        });
      } else if (insight.type === 'opportunity') {
        recommendations.push({
          id: `rec-${insight.id}`,
          priority: 'medium',
          title: `Explore: ${insight.title}`,
          description: insight.description,
          actionItems: ['Analyze opportunity', 'Develop strategy'],
          expectedImpact: 'Potential performance improvement',
          timestamp: new Date(),
        });
      }
    }

    return recommendations;
  }

  // Real-time Analytics
  getRealtimeAnalytics(domain: string): RealtimeAnalytics {
    return {
      domain,
      currentMetrics: this.metrics.get(domain) || this.getDefaultMetrics(),
      recentEvents: this.getEvents(domain).slice(-100),
      alerts: this.getAlerts(domain, false),
      predictions: this.getPredictions(domain),
    };
  }

  getAllRealtimeAnalytics(): Record<string, RealtimeAnalytics> {
    const domains = Array.from(new Set([
      ...this.metrics.keys(),
      ...this.events.map(e => e.domain),
      ...this.alerts.map(a => a.domain),
      ...this.predictions.map(p => p.domain),
    ]));

    const analytics: Record<string, RealtimeAnalytics> = {};
    for (const domain of domains) {
      analytics[domain] = this.getRealtimeAnalytics(domain);
    }
    return analytics;
  }
}

// ============================================================================
// Public API
// ============================================================================

/**
 * Get analytics engine instance
 */
export function getAnalyticsEngine(): AnalyticsEngine {
  return AnalyticsEngine.getInstance();
}

/**
 * Record metrics for a domain
 */
export function recordDomainMetrics(domain: string, metrics: AnalyticsMetrics): void {
  return AnalyticsEngine.getInstance().recordMetrics(domain, metrics);
}

/**
 * Get metrics for a domain
 */
export function getDomainMetrics(domain: string): AnalyticsMetrics | undefined {
  return AnalyticsEngine.getInstance().getMetrics(domain);
}

/**
 * Record an analytics event
 */
export function recordAnalyticsEvent(event: AnalyticsEvent): void {
  return AnalyticsEngine.getInstance().recordEvent(event);
}

/**
 * Get analytics events
 */
export function getAnalyticsEvents(domain?: string, type?: string): AnalyticsEvent[] {
  return AnalyticsEngine.getInstance().getEvents(domain, type);
}

/**
 * Generate analytics report
 */
export function generateAnalyticsReport(domain: string, type: ReportType, period: ReportPeriod): AnalyticsReport {
  return AnalyticsEngine.getInstance().generateReport(domain, type, period);
}

/**
 * Create analytics dashboard
 */
export function createAnalyticsDashboard(dashboard: AnalyticsDashboard): void {
  return AnalyticsEngine.getInstance().createDashboard(dashboard);
}

/**
 * Get analytics dashboard
 */
export function getAnalyticsDashboard(id: string): AnalyticsDashboard | undefined {
  return AnalyticsEngine.getInstance().getDashboard(id);
}

/**
 * Get real-time analytics
 */
export function getRealtimeAnalytics(domain: string): RealtimeAnalytics {
  return AnalyticsEngine.getInstance().getRealtimeAnalytics(domain);
}