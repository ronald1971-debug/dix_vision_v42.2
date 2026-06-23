/**
 * Real-Time Performance Dashboard
 * DIX VISION v42.2 - Phase 14: Performance Analytics and Reporting (Weeks 45-48)
 */

export interface PerformanceDashboard {
  dashboardId: string;
  name: string;
  layout: DashboardLayout;
  widgets: Widget[];
  filters: DashboardFilters;
  realTimeData: RealTimeMetrics;
  alerts: DashboardAlert[];
  lastUpdated: number;
}

export interface DashboardLayout {
  type: 'grid' | 'flex' | 'custom';
  columns: number;
  rows: number;
  gap: number;
  responsive: boolean;
}

export interface Widget {
  widgetId: string;
  type: WidgetType;
  title: string;
  position: WidgetPosition;
  size: WidgetSize;
  config: WidgetConfig;
  data: any;
  refreshRate: number;
  lastRefresh: number;
}

export type WidgetType = 
  | 'metric-card'
  | 'line-chart'
  | 'bar-chart'
  | 'pie-chart'
  | 'table'
  | 'heatmap'
  | 'gauge'
  | 'text'
  | 'custom';

export interface WidgetPosition {
  x: number;
  y: number;
}

export interface WidgetSize {
  width: number;
  height: number;
}

export interface WidgetConfig {
  showTitle: boolean;
  showLegend: boolean;
  showGrid: boolean;
  axisLabels: boolean;
  colors: string[];
  thresholds?: Threshold[];
}

export interface Threshold {
  value: number;
  color: string;
  label: string;
}

export interface DashboardFilters {
  timeRange: TimeRange;
  strategyFilter: string[];
  metricFilter: string[];
  customFilters: Map<string, any>;
}

export interface TimeRange {
  type: 'custom' | 'today' | 'yesterday' | 'week' | 'month' | 'quarter' | 'year' | 'all';
  start?: number;
  end?: number;
}

export interface RealTimeMetrics {
  currentReturn: number;
  dailyReturn: number;
  weeklyReturn: number;
  monthlyReturn: number;
  ytdReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  volatility: number;
  beta: number;
  alpha: number;
  winRate: number;
  profitFactor: number;
  positionCount: number;
  exposure: number;
  cash: number;
  lastUpdate: number;
}

export interface DashboardAlert {
  alertId: string;
  type: 'info' | 'warning' | 'error' | 'success';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  metric: string;
  threshold: number;
  currentValue: number;
  timestamp: number;
  acknowledged: boolean;
}

class RealTimePerformanceDashboard {
  private dashboards: Map<string, PerformanceDashboard> = new Map();
  private refreshInterval?: ReturnType<typeof setInterval>;

  initialize(): void {
    this.createDefaultDashboard();
    this.startRealTimeUpdates();
  }

  private createDefaultDashboard(): void {
    const dashboard: PerformanceDashboard = {
      dashboardId: 'default_dashboard',
      name: 'Performance Overview',
      layout: {
        type: 'grid',
        columns: 4,
        rows: 6,
        gap: 16,
        responsive: true
      },
      widgets: [
        {
          widgetId: 'widget_current_return',
          type: 'metric-card',
          title: 'Current Return',
          position: { x: 0, y: 0 },
          size: { width: 1, height: 1 },
          config: {
            showTitle: true,
            showLegend: false,
            showGrid: false,
            axisLabels: false,
            colors: ['#4CAF50'],
            thresholds: [
              { value: 0, color: '#4CAF50', label: 'Positive' },
              { value: -5, color: '#F44336', label: 'Negative' }
            ]
          },
          data: { value: 12.5, change: 2.3 },
          refreshRate: 30000,
          lastRefresh: Date.now()
        },
        {
          widgetId: 'widget_sharpe_ratio',
          type: 'metric-card',
          title: 'Sharpe Ratio',
          position: { x: 1, y: 0 },
          size: { width: 1, height: 1 },
          config: {
            showTitle: true,
            showLegend: false,
            showGrid: false,
            axisLabels: false,
            colors: ['#2196F3'],
            thresholds: [
              { value: 1, color: '#4CAF50', label: 'Good' },
              { value: 0.5, color: '#FF9800', label: 'Fair' }
            ]
          },
          data: { value: 1.35, change: 0.1 },
          refreshRate: 30000,
          lastRefresh: Date.now()
        },
        {
          widgetId: 'widget_max_drawdown',
          type: 'metric-card',
          title: 'Max Drawdown',
          position: { x: 2, y: 0 },
          size: { width: 1, height: 1 },
          config: {
            showTitle: true,
            showLegend: false,
            showGrid: false,
            axisLabels: false,
            colors: ['#F44336'],
            thresholds: [
              { value: -10, color: '#4CAF50', label: 'Low' },
              { value: -20, color: '#F44336', label: 'High' }
            ]
          },
          data: { value: -8.5, change: -1.2 },
          refreshRate: 30000,
          lastRefresh: Date.now()
        },
        {
          widgetId: 'widget_win_rate',
          type: 'metric-card',
          title: 'Win Rate',
          position: { x: 3, y: 0 },
          size: { width: 1, height: 1 },
          config: {
            showTitle: true,
            showLegend: false,
            showGrid: false,
            axisLabels: false,
            colors: ['#9C27B0'],
            thresholds: [
              { value: 50, color: '#F44336', label: 'Below 50%' },
              { value: 60, color: '#4CAF50', label: 'Above 60%' }
            ]
          },
          data: { value: 62.5, change: 2.5 },
          refreshRate: 30000,
          lastRefresh: Date.now()
        },
        {
          widgetId: 'widget_performance_chart',
          type: 'line-chart',
          title: 'Performance Over Time',
          position: { x: 0, y: 1 },
          size: { width: 2, height: 2 },
          config: {
            showTitle: true,
            showLegend: true,
            showGrid: true,
            axisLabels: true,
            colors: ['#4CAF50', '#2196F3']
          },
          data: {},
          refreshRate: 60000,
          lastRefresh: Date.now()
        },
        {
          widgetId: 'widget_drawdown_chart',
          type: 'line-chart',
          title: 'Drawdown Chart',
          position: { x: 2, y: 1 },
          size: { width: 2, height: 2 },
          config: {
            showTitle: true,
            showLegend: true,
            showGrid: true,
            axisLabels: true,
            colors: ['#F44336']
          },
          data: {},
          refreshRate: 60000,
          lastRefresh: Date.now()
        },
        {
          widgetId: 'widget_positions_table',
          type: 'table',
          title: 'Current Positions',
          position: { x: 0, y: 3 },
          size: { width: 4, height: 2 },
          config: {
            showTitle: true,
            showLegend: false,
            showGrid: true,
            axisLabels: false,
            colors: []
          },
          data: {},
          refreshRate: 30000,
          lastRefresh: Date.now()
        }
      ],
      filters: {
        timeRange: { type: 'month' },
        strategyFilter: [],
        metricFilter: [],
        customFilters: new Map()
      },
      realTimeData: {
        currentReturn: 12.5,
        dailyReturn: 0.15,
        weeklyReturn: 0.8,
        monthlyReturn: 2.3,
        ytdReturn: 8.5,
        sharpeRatio: 1.35,
        maxDrawdown: -8.5,
        volatility: 12.5,
        beta: 0.95,
        alpha: 0.03,
        winRate: 62.5,
        profitFactor: 1.8,
        positionCount: 15,
        exposure: 0.85,
        cash: 150000,
        lastUpdate: Date.now()
      },
      alerts: [],
      lastUpdated: Date.now()
    };

    this.dashboards.set(dashboard.dashboardId, dashboard);
  }

  private startRealTimeUpdates(): void {
    this.refreshInterval = setInterval(() => {
      this.updateDashboardMetrics();
    }, 30000);
  }

  private updateDashboardMetrics(): void {
    for (const dashboard of this.dashboards.values()) {
      dashboard.realTimeData = this.generateRealTimeMetrics();
      dashboard.realTimeData.lastUpdate = Date.now();
      dashboard.lastUpdated = Date.now();

      dashboard.widgets.forEach(widget => {
        if (Date.now() - widget.lastRefresh > widget.refreshRate) {
          widget.data = this.generateWidgetData(widget.type);
          widget.lastRefresh = Date.now();
        }
      });

      this.checkAlerts(dashboard);
    }
  }

  private generateRealTimeMetrics(): RealTimeMetrics {
    return {
      currentReturn: 12.5 + (Math.random() - 0.5) * 0.5,
      dailyReturn: 0.15 + (Math.random() - 0.5) * 0.1,
      weeklyReturn: 0.8 + (Math.random() - 0.5) * 0.2,
      monthlyReturn: 2.3 + (Math.random() - 0.5) * 0.3,
      ytdReturn: 8.5 + (Math.random() - 0.5) * 0.5,
      sharpeRatio: 1.35 + (Math.random() - 0.5) * 0.1,
      maxDrawdown: -8.5 + (Math.random() - 0.5) * 0.5,
      volatility: 12.5 + (Math.random() - 0.5) * 0.5,
      beta: 0.95 + (Math.random() - 0.5) * 0.05,
      alpha: 0.03 + (Math.random() - 0.5) * 0.01,
      winRate: 62.5 + (Math.random() - 0.5) * 2,
      profitFactor: 1.8 + (Math.random() - 0.5) * 0.2,
      positionCount: 15 + Math.floor((Math.random() - 0.5) * 3),
      exposure: 0.85 + (Math.random() - 0.5) * 0.1,
      cash: 150000 + Math.floor((Math.random() - 0.5) * 20000),
      lastUpdate: Date.now()
    };
  }

  private generateWidgetData(type: WidgetType): any {
    switch (type) {
      case 'metric-card':
        return {
          value: 10 + Math.random() * 10,
          change: (Math.random() - 0.5) * 5
        };
      case 'line-chart':
        return {
          labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`),
          datasets: [
            {
              label: 'Portfolio',
              data: Array.from({ length: 30 }, () => 100 + Math.random() * 50)
            },
            {
              label: 'Benchmark',
              data: Array.from({ length: 30 }, () => 95 + Math.random() * 40)
            }
          ]
        };
      default:
        return {};
    }
  }

  private checkAlerts(dashboard: PerformanceDashboard): void {
    const metrics = dashboard.realTimeData;
    
    if (metrics.maxDrawdown < -15) {
      const alert: DashboardAlert = {
        alertId: `alert_${Date.now()}`,
        type: 'warning',
        severity: 'high',
        message: `Max drawdown exceeded threshold: ${metrics.maxDrawdown.toFixed(2)}%`,
        metric: 'maxDrawdown',
        threshold: -15,
        currentValue: metrics.maxDrawdown,
        timestamp: Date.now(),
        acknowledged: false
      };
      
      const existing = dashboard.alerts.find(a => a.metric === 'maxDrawdown' && !a.acknowledged);
      if (!existing) {
        dashboard.alerts.push(alert);
      }
    }

    if (metrics.sharpeRatio < 0.5) {
      const alert: DashboardAlert = {
        alertId: `alert_${Date.now()}_1`,
        type: 'warning',
        severity: 'medium',
        message: `Sharpe ratio below threshold: ${metrics.sharpeRatio.toFixed(2)}`,
        metric: 'sharpeRatio',
        threshold: 0.5,
        currentValue: metrics.sharpeRatio,
        timestamp: Date.now(),
        acknowledged: false
      };
      
      const existing = dashboard.alerts.find(a => a.metric === 'sharpeRatio' && !a.acknowledged);
      if (!existing) {
        dashboard.alerts.push(alert);
      }
    }
  }

  acknowledgeAlert(dashboardId: string, alertId: string): void {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) return;

    const alert = dashboard.alerts.find(a => a.alertId === alertId);
    if (alert) {
      alert.acknowledged = true;
    }
  }

  getDashboard(dashboardId: string): PerformanceDashboard | undefined {
    return this.dashboards.get(dashboardId);
  }

  getAllDashboards(): PerformanceDashboard[] {
    return Array.from(this.dashboards.values());
  }

  stopUpdates(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = undefined;
    }
  }
}

export const realTimePerformanceDashboard = new RealTimePerformanceDashboard();
export default RealTimePerformanceDashboard;