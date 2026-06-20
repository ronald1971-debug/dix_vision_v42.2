/**
 * Performance Monitoring System
 * 
 * Provides comprehensive performance monitoring for domain operations,
 * including metrics collection, performance alerts, and health monitoring.
 */

// ============================================================================
// Performance Metrics Types
// ============================================================================

export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: number;
  domain?: string;
  operation?: string;
}

export interface PerformanceAlert {
  id: string;
  severity: 'info' | 'warning' | 'error';
  metric: string;
  threshold: number;
  currentValue: number;
  message: string;
  timestamp: number;
}

export interface PerformanceThreshold {
  metric: string;
  warning: number;
  error: number;
  enabled: boolean;
}

export interface PerformanceReport {
  period: {
    start: number;
    end: number;
  };
  metrics: PerformanceMetric[];
  alerts: PerformanceAlert[];
  summary: {
    totalOperations: number;
    averageResponseTime: number;
    errorRate: number;
    healthScore: number;
  };
}

// ============================================================================
// Performance Monitor
// ============================================================================

class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: PerformanceMetric[] = [];
  private alerts: PerformanceAlert[] = [];
  private thresholds: Map<string, PerformanceThreshold> = new Map();
  private maxMetrics: number = 1000;
  private maxAlerts: number = 100;

  private constructor() {
    this.setupDefaultThresholds();
  }

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  /**
   * Setup default performance thresholds
   */
  private setupDefaultThresholds(): void {
    this.setThreshold('responseTime', 1000, 5000);
    this.setThreshold('memoryUsage', 100, 200);
    this.setThreshold('cacheHitRate', 0.5, 0.3);
    this.setThreshold('errorRate', 0.05, 0.1);
    this.setThreshold('selectorExecutionTime', 10, 50);
  }

  /**
   * Record a performance metric
   */
  recordMetric(metric: Omit<PerformanceMetric, 'timestamp'>): void {
    const fullMetric: PerformanceMetric = {
      ...metric,
      timestamp: Date.now(),
    };

    this.metrics.push(fullMetric);

    // Check if we exceed max metrics
    if (this.metrics.length > this.maxMetrics) {
      this.metrics.shift();
    }

    // Check thresholds
    this.checkThresholds(fullMetric);
  }

  /**
   * Record operation timing
   */
  recordTiming(
    domain: string,
    operation: string,
    duration: number
  ): void {
    this.recordMetric({
      name: 'responseTime',
      value: duration,
      unit: 'ms',
      domain,
      operation,
    });
  }

  /**
   * Record cache performance
   */
  recordCachePerformance(
    hits: number,
    _misses: number,
    total: number
  ): void {
    const hitRate = total > 0 ? hits / total : 0;
    this.recordMetric({
      name: 'cacheHitRate',
      value: hitRate,
      unit: 'ratio',
    });
  }

  /**
   * Record selector performance
   */
  recordSelectorPerformance(
    selectorName: string,
    executionTime: number
  ): void {
    this.recordMetric({
      name: 'selectorExecutionTime',
      value: executionTime,
      unit: 'ms',
      operation: selectorName,
    });
  }

  /**
   * Set performance threshold
   */
  setThreshold(
    metric: string,
    warning: number,
    error: number
  ): void {
    this.thresholds.set(metric, {
      metric,
      warning,
      error,
      enabled: true,
    });
  }

  /**
   * Check if metric exceeds thresholds
   */
  private checkThresholds(metric: PerformanceMetric): void {
    const threshold = this.thresholds.get(metric.name);
    if (!threshold || !threshold.enabled) return;

    if (metric.value >= threshold.error) {
      this.createAlert(metric, 'error', threshold.error);
    } else if (metric.value >= threshold.warning) {
      this.createAlert(metric, 'warning', threshold.warning);
    }
  }

  /**
   * Create performance alert
   */
  private createAlert(
    metric: PerformanceMetric,
    severity: 'warning' | 'error',
    threshold: number
  ): void {
    const alert: PerformanceAlert = {
      id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      severity,
      metric: metric.name,
      threshold,
      currentValue: metric.value,
      message: `${metric.name} (${metric.value}${metric.unit}) exceeds ${severity} threshold (${threshold}${metric.unit})`,
      timestamp: Date.now(),
    };

    this.alerts.push(alert);

    // Check if we exceed max alerts
    if (this.alerts.length > this.maxAlerts) {
      this.alerts.shift();
    }

    console.warn(`[Performance Alert] ${alert.message}`);
  }

  /**
   * Get metrics by name
   */
  getMetrics(metricName: string, timeRange?: { start: number; end: number }): PerformanceMetric[] {
    let filtered = this.metrics.filter(m => m.name === metricName);

    if (timeRange) {
      filtered = filtered.filter(m => 
        m.timestamp >= timeRange.start && m.timestamp <= timeRange.end
      );
    }

    return filtered;
  }

  /**
   * Get metrics by domain
   */
  getMetricsByDomain(domain: string, timeRange?: { start: number; end: number }): PerformanceMetric[] {
    let filtered = this.metrics.filter(m => m.domain === domain);

    if (timeRange) {
      filtered = filtered.filter(m => 
        m.timestamp >= timeRange.start && m.timestamp <= timeRange.end
      );
    }

    return filtered;
  }

  /**
   * Get all alerts
   */
  getAlerts(severity?: 'info' | 'warning' | 'error'): PerformanceAlert[] {
    if (severity) {
      return this.alerts.filter(a => a.severity === severity);
    }
    return [...this.alerts];
  }

  /**
   * Clear alerts
   */
  clearAlerts(severity?: 'info' | 'warning' | 'error'): void {
    if (severity) {
      this.alerts = this.alerts.filter(a => a.severity !== severity);
    } else {
      this.alerts = [];
    }
  }

  /**
   * Generate performance report
   */
  generateReport(timeRange: { start: number; end: number }): PerformanceReport {
    const filteredMetrics = this.metrics.filter(m =>
      m.timestamp >= timeRange.start && m.timestamp <= timeRange.end
    );

    const responseTimeMetrics = filteredMetrics.filter(m => m.name === 'responseTime');

    const totalOperations = responseTimeMetrics.length;
    const averageResponseTime = totalOperations > 0
      ? responseTimeMetrics.reduce((sum, m) => sum + m.value, 0) / totalOperations
      : 0;

    // Calculate health score (0-100)
    const responseTimeScore = Math.max(0, 100 - (averageResponseTime / 100)); // 100ms = 99% health
    const errorScore = 100; // Default to perfect error score if no error metrics
    const healthScore = (responseTimeScore + errorScore) / 2;

    return {
      period: timeRange,
      metrics: filteredMetrics,
      alerts: this.alerts.filter(a =>
        a.timestamp >= timeRange.start && a.timestamp <= timeRange.end
      ),
      summary: {
        totalOperations,
        averageResponseTime,
        errorRate: 0,
        healthScore,
      },
    };
  }

  /**
   * Clear all metrics
   */
  clearMetrics(): void {
    this.metrics = [];
  }

  /**
   * Get system health score
   */
  getHealthScore(): number {
    const now = Date.now();
    const oneHourAgo = now - 3600000;
    const report = this.generateReport({ start: oneHourAgo, end: now });
    return report.summary.healthScore;
  }

  /**
   * Get performance statistics
   */
  getStatistics(): {
    totalMetrics: number;
    totalAlerts: number;
    activeAlerts: number;
    metricCount: Map<string, number>;
  } {
    const metricCount = new Map<string, number>();
    this.metrics.forEach(m => {
      metricCount.set(m.name, (metricCount.get(m.name) || 0) + 1);
    });

    return {
      totalMetrics: this.metrics.length,
      totalAlerts: this.alerts.length,
      activeAlerts: this.alerts.filter(a => a.severity === 'error').length,
      metricCount,
    };
  }
}

// ============================================================================
// Performance Timer Utility
// ============================================================================

export class PerformanceTimer {
  private startTime: number;
  private endTime: number | null = null;
  private domain?: string;
  private operation?: string;

  constructor(domain?: string, operation?: string) {
    this.startTime = performance.now();
    this.domain = domain;
    this.operation = operation;
  }

  stop(): number {
    if (this.endTime === null) {
      this.endTime = performance.now();
      const duration = this.endTime - this.startTime;

      if (this.domain && this.operation) {
        PerformanceMonitor.getInstance().recordTiming(
          this.domain,
          this.operation,
          duration
        );
      }

      return duration;
    }
    return this.endTime - this.startTime;
  }

  getDuration(): number {
    if (this.endTime === null) {
      return performance.now() - this.startTime;
    }
    return this.endTime - this.startTime;
  }
}

/**
 * Create a performance timer
 */
export function createTimer(domain?: string, operation?: string): PerformanceTimer {
  return new PerformanceTimer(domain, operation);
}

/**
 * Wrap a function with performance tracking
 */
export async function withPerformanceTracking<T>(
  domain: string,
  operation: string,
  fn: () => Promise<T>
): Promise<T> {
  const timer = createTimer(domain, operation);
  try {
    const result = await fn();
    timer.stop();
    return result;
  } catch (error) {
    timer.stop();
    throw error;
  }
}

// ============================================================================
// Public API
// ============================================================================

/**
 * Record a performance metric
 */
export function recordPerformanceMetric(metric: Omit<PerformanceMetric, 'timestamp'>): void {
  return PerformanceMonitor.getInstance().recordMetric(metric);
}

/**
 * Get performance metrics
 */
export function getPerformanceMetrics(metricName: string, timeRange?: { start: number; end: number }): PerformanceMetric[] {
  return PerformanceMonitor.getInstance().getMetrics(metricName, timeRange);
}

/**
 * Get performance alerts
 */
export function getPerformanceAlerts(severity?: 'info' | 'warning' | 'error'): PerformanceAlert[] {
  return PerformanceMonitor.getInstance().getAlerts(severity);
}

/**
 * Set performance threshold
 */
export function setPerformanceThreshold(metric: string, warning: number, error: number): void {
  return PerformanceMonitor.getInstance().setThreshold(metric, warning, error);
}

/**
 * Generate performance report
 */
export function generatePerformanceReport(timeRange: { start: number; end: number }): PerformanceReport {
  return PerformanceMonitor.getInstance().generateReport(timeRange);
}

/**
 * Get system health score
 */
export function getSystemHealthScore(): number {
  return PerformanceMonitor.getInstance().getHealthScore();
}

/**
 * Get performance statistics
 */
export function getPerformanceStatistics() {
  return PerformanceMonitor.getInstance().getStatistics();
}

/**
 * Clear performance metrics
 */
export function clearPerformanceMetrics(): void {
  return PerformanceMonitor.getInstance().clearMetrics();
}