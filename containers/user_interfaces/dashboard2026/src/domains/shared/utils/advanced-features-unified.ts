/**
 * Unified Advanced Features Implementation
 * 
 * Streamlined implementation of scheduling/automation and observability
 * for all domains to complete Phase 7 efficiently.
 */

import { DomainEventBus } from './event-bus';
import type { PerformanceMetrics } from './analytics-engine';

// ============================================================================
// Scheduling and Automation
// ============================================================================

export interface ScheduledJob {
  id: string;
  domain: string;
  name: string;
  type: 'recurring' | 'onetime' | 'conditional';
  schedule: JobSchedule;
  handler: () => Promise<void>;
  status: 'scheduled' | 'running' | 'completed' | 'failed';
  lastRun?: Date;
  nextRun?: Date;
  runCount: number;
  failureCount: number;
}

export interface JobSchedule {
  interval?: number; // milliseconds
  cron?: string;
  trigger?: JobTrigger;
}

export interface JobTrigger {
  type: 'event' | 'condition' | 'manual';
  value: any;
}

export class SchedulingEngine {
  private static instance: SchedulingEngine;
  private jobs: Map<string, ScheduledJob> = new Map();
  private intervals: Map<string, NodeJS.Timeout> = new Map();

  private constructor() {
    this.initializeEngine();
  }

  static getInstance(): SchedulingEngine {
    if (!SchedulingEngine.instance) {
      SchedulingEngine.instance = new SchedulingEngine();
    }
    return SchedulingEngine.instance;
  }

  private initializeEngine(): void {
    console.log('Scheduling Engine initialized');
  }

  scheduleJob(job: ScheduledJob): void {
    this.jobs.set(job.id, job);
    
    if (job.schedule.interval) {
      this.startRecurringJob(job);
    } else if (job.schedule.trigger?.type === 'event') {
      this.setupEventTrigger(job);
    }
  }

  private startRecurringJob(job: ScheduledJob): void {
    const intervalId = setInterval(async () => {
      await this.executeJob(job.id);
    }, job.schedule.interval!);
    
    this.intervals.set(job.id, intervalId);
  }

  private setupEventTrigger(job: ScheduledJob): void {
    DomainEventBus.subscribe(
      job.domain,
      job.schedule.trigger!.value,
      async () => {
        await this.executeJob(job.id);
      }
    );
  }

  private async executeJob(jobId: string): Promise<void> {
    const job = this.jobs.get(jobId);
    if (!job || job.status === 'running') return;

    job.status = 'running';
    job.lastRun = new Date();

    try {
      await job.handler();
      job.status = 'completed';
      job.runCount++;
    } catch (error) {
      job.status = 'failed';
      job.failureCount++;
      console.error(`Job ${jobId} failed:`, error);
    }

    if (job.schedule.interval) {
      job.nextRun = new Date(Date.now() + job.schedule.interval);
    }
  }

  executeJobManually(jobId: string): void {
    this.executeJob(jobId);
  }

  getJob(jobId: string): ScheduledJob | undefined {
    return this.jobs.get(jobId);
  }

  getJobs(domain?: string): ScheduledJob[] {
    return Array.from(this.jobs.values()).filter(job => {
      if (domain && job.domain !== domain) return false;
      return true;
    });
  }

  cancelJob(jobId: string): void {
    const intervalId = this.intervals.get(jobId);
    if (intervalId) {
      clearInterval(intervalId);
      this.intervals.delete(jobId);
    }
    this.jobs.delete(jobId);
  }
}

// ============================================================================
// Advanced Observability
// ============================================================================

export interface ObservabilityMetrics {
  domain: string;
  healthScore: number;
  performance: ObservabilityPerformanceMetrics;
  alerts: ObservabilityAlert[];
  trends: MetricTrend[];
}

export interface ObservabilityPerformanceMetrics {
  latency: number;
  throughput: number;
  errorRate: number;
  resourceUtilization: number;
  availability: number;
}

export interface ObservabilityAlert {
  id: string;
  domain: string;
  type: 'threshold' | 'anomaly' | 'trend';
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  metric: string;
  value: number;
  threshold: number;
  timestamp: Date;
  acknowledged: boolean;
}

export interface MetricTrend {
  metric: string;
  direction: 'up' | 'down' | 'stable';
  changePercentage: number;
  period: number;
}

export class ObservabilityEngine {
  private static instance: ObservabilityEngine;
  private metrics: Map<string, ObservabilityMetrics> = new Map();
  private alerts: ObservabilityAlert[] = [];
  private thresholds: Map<string, number> = new Map();

  private constructor() {
    this.initializeEngine();
    this.initializeDefaultThresholds();
  }

  static getInstance(): ObservabilityEngine {
    if (!ObservabilityEngine.instance) {
      ObservabilityEngine.instance = new ObservabilityEngine();
    }
    return ObservabilityEngine.instance;
  }

  private initializeEngine(): void {
    console.log('Observability Engine initialized');
  }

  private initializeDefaultThresholds(): void {
    this.thresholds.set('latency', 1000); // 1 second
    this.thresholds.set('errorRate', 0.05); // 5%
    this.thresholds.set('resourceUtilization', 0.8); // 80%
    this.thresholds.set('availability', 0.99); // 99%
  }

  recordMetrics(domain: string, metrics: ObservabilityPerformanceMetrics): void {
    const existing = this.metrics.get(domain);
    const healthScore = this.calculateHealthScore(metrics);
    const trends = this.calculateTrends(existing?.performance, metrics);
    const alerts = this.checkThresholds(domain, metrics);

    this.metrics.set(domain, {
      domain,
      healthScore,
      performance: metrics,
      alerts,
      trends,
    });

    // Record significant alerts
    alerts.forEach(alert => {
      if (alert.severity === 'warning' || alert.severity === 'error' || alert.severity === 'critical') {
        this.alerts.push(alert);
      }
    });

    this.cleanupOldAlerts();
  }

  private calculateHealthScore(metrics: PerformanceMetrics): number {
    const latencyScore = Math.max(0, 1 - (metrics.latency / 1000));
    const errorScore = Math.max(0, 1 - (metrics.errorRate * 20)); // 5% = 0 score
    const availabilityScore = metrics.availability;
    const resourceScore = Math.max(0, 1 - (metrics.resourceUtilization - 0.8) * 5); // 80% = full score

    return Math.round(((latencyScore + errorScore + availabilityScore + resourceScore) / 4) * 100);
  }

  private calculateTrends(previous?: PerformanceMetrics, current?: PerformanceMetrics): MetricTrend[] {
    if (!previous || !current) return [];

    const trends: MetricTrend[] = [];

    const latencyChange = ((current.latency - previous.latency) / previous.latency) * 100;
    trends.push({
      metric: 'latency',
      direction: latencyChange > 5 ? 'up' : latencyChange < -5 ? 'down' : 'stable',
      changePercentage: latencyChange,
      period: 1,
    });

    const errorRateChange = ((current.errorRate - previous.errorRate) / (previous.errorRate || 0.01)) * 100;
    trends.push({
      metric: 'errorRate',
      direction: errorRateChange > 5 ? 'up' : errorRateChange < -5 ? 'down' : 'stable',
      changePercentage: errorRateChange,
      period: 1,
    });

    return trends;
  }

  private checkThresholds(domain: string, metrics: PerformanceMetrics): ObservabilityAlert[] {
    const alerts: ObservabilityAlert[] = [];

    // Check latency threshold
    if (metrics.latency > this.thresholds.get('latency')!) {
      alerts.push({
        id: `alert-latency-${domain}-${Date.now()}`,
        domain,
        type: 'threshold',
        severity: metrics.latency > this.thresholds.get('latency')! * 2 ? 'error' : 'warning',
        message: `High latency: ${metrics.latency.toFixed(2)}ms`,
        metric: 'latency',
        value: metrics.latency,
        threshold: this.thresholds.get('latency')!,
        timestamp: new Date(),
        acknowledged: false,
      });
    }

    // Check error rate threshold
    if (metrics.errorRate > this.thresholds.get('errorRate')!) {
      alerts.push({
        id: `alert-error-${domain}-${Date.now()}`,
        domain,
        type: 'threshold',
        severity: metrics.errorRate > this.thresholds.get('errorRate')! * 2 ? 'error' : 'warning',
        message: `High error rate: ${(metrics.errorRate * 100).toFixed(2)}%`,
        metric: 'errorRate',
        value: metrics.errorRate,
        threshold: this.thresholds.get('errorRate')!,
        timestamp: new Date(),
        acknowledged: false,
      });
    }

    // Check availability threshold
    if (metrics.availability < this.thresholds.get('availability')!) {
      alerts.push({
        id: `alert-availability-${domain}-${Date.now()}`,
        domain,
        type: 'threshold',
        severity: 'error',
        message: `Low availability: ${(metrics.availability * 100).toFixed(2)}%`,
        metric: 'availability',
        value: metrics.availability,
        threshold: this.thresholds.get('availability')!,
        timestamp: new Date(),
        acknowledged: false,
      });
    }

    // Check resource utilization threshold
    if (metrics.resourceUtilization > this.thresholds.get('resourceUtilization')!) {
      alerts.push({
        id: `alert-resource-${domain}-${Date.now()}`,
        domain,
        type: 'threshold',
        severity: metrics.resourceUtilization > this.thresholds.get('resourceUtilization')! * 1.2 ? 'error' : 'warning',
        message: `High resource utilization: ${(metrics.resourceUtilization * 100).toFixed(2)}%`,
        metric: 'resourceUtilization',
        value: metrics.resourceUtilization,
        threshold: this.thresholds.get('resourceUtilization')!,
        timestamp: new Date(),
        acknowledged: false,
      });
    }

    return alerts;
  }

  private cleanupOldAlerts(): void {
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours
    
    this.alerts = this.alerts.filter(alert => {
      const age = Date.now() - alert.timestamp.getTime();
      return age < maxAge && !alert.acknowledged;
    });
  }

  getMetrics(domain: string): ObservabilityMetrics | undefined {
    return this.metrics.get(domain);
  }

  getAllMetrics(): Record<string, ObservabilityMetrics> {
    return Object.fromEntries(this.metrics);
  }

  getAlerts(domain?: string, acknowledged?: boolean): ObservabilityAlert[] {
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

  setThreshold(metric: string, value: number): void {
    this.thresholds.set(metric, value);
  }

  getOverallSystemHealth(): {
    overallScore: number;
    domainScores: Record<string, number>;
    criticalAlerts: number;
    recommendations: string[];
  } {
    const domainScores: Record<string, number> = {};
    let totalScore = 0;
    let domainCount = 0;

    for (const [domain, metrics] of this.metrics.entries()) {
      domainScores[domain] = metrics.healthScore;
      totalScore += metrics.healthScore;
      domainCount++;
    }

    const overallScore = domainCount > 0 ? Math.round(totalScore / domainCount) : 100;
    const criticalAlerts = this.alerts.filter(a => a.severity === 'critical').length;

    const recommendations: string[] = [];
    if (overallScore < 80) {
      recommendations.push('System health below optimal - investigate domains with low scores');
    }
    if (criticalAlerts > 0) {
      recommendations.push('Critical alerts require immediate attention');
    }
    if (recommendations.length === 0) {
      recommendations.push('System operating within normal parameters');
    }

    return {
      overallScore,
      domainScores,
      criticalAlerts,
      recommendations,
    };
  }
}

// ============================================================================
// Public API
// ============================================================================

export function getSchedulingEngine(): SchedulingEngine {
  return SchedulingEngine.getInstance();
}

export function scheduleJob(job: ScheduledJob): void {
  return SchedulingEngine.getInstance().scheduleJob(job);
}

export function getObservabilityEngine(): ObservabilityEngine {
  return ObservabilityEngine.getInstance();
}

export function recordObservabilityMetrics(domain: string, metrics: PerformanceMetrics): void {
  // Convert to ObservabilityPerformanceMetrics
  const observabilityMetrics: ObservabilityPerformanceMetrics = {
    latency: metrics.latency || 0,
    throughput: metrics.throughput || 0,
    errorRate: metrics.errorRate || 0,
    availability: metrics.availability || 1,
    resourceUtilization: metrics.resourceUtilization || 0,
  };
  return ObservabilityEngine.getInstance().recordMetrics(domain, observabilityMetrics);
}

export function getOverallSystemHealth() {
  return ObservabilityEngine.getInstance().getOverallSystemHealth();
}