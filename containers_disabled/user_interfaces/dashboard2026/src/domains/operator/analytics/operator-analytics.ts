/**
 * OPERATOR Domain Analytics
 * 
 * Domain-specific analytics for operator including
 * user engagement metrics, dashboard usage, feature adoption,
 * and user experience analytics.
 */

import {
  AnalyticsMetrics,
  recordDomainMetrics,
  recordAnalyticsEvent,
  getRealtimeAnalytics,
  generateAnalyticsReport,
} from '../../shared/utils/analytics-engine';

export interface OperatorMetrics extends AnalyticsMetrics {
  userEngagement: UserEngagementMetrics;
  dashboardUsage: DashboardUsageMetrics;
  featureAdoption: FeatureAdoptionMetrics;
  userExperience: UserExperienceMetrics;
}

export interface UserEngagementMetrics {
  activeUsers: number;
  totalSessions: number;
  averageSessionDuration: number;
  returnUsers: number;
  newUsers: number;
}

export interface DashboardUsageMetrics {
  pageViews: number;
  uniquePages: number;
  mostUsedDashboards: Record<string, number>;
  averageLoadTime: number;
  errorRate: number;
}

export interface FeatureAdoptionMetrics {
  totalFeatures: number;
  adoptedFeatures: number;
  featureUsage: Record<string, number>;
  adoptionRate: number;
}

export interface UserExperienceMetrics {
  satisfactionScore: number;
  netPromoterScore: number;
  taskCompletionRate: number;
  errorFrequency: number;
  accessibilityScore: number;
}

export class OperatorAnalytics {
  private static instance: OperatorAnalytics;
  private domain = 'operator';

  private constructor() {
    this.initializeAnalytics();
  }

  static getInstance(): OperatorAnalytics {
    if (!OperatorAnalytics.instance) {
      OperatorAnalytics.instance = new OperatorAnalytics();
    }
    return OperatorAnalytics.instance;
  }

  private initializeAnalytics(): void {
    console.log('OPERATOR Analytics initialized');
  }

  recordMetrics(metrics: OperatorMetrics): void {
    recordDomainMetrics(this.domain, this.convertToBaseMetrics(metrics));
    recordAnalyticsEvent({
      id: `operator-metrics-${Date.now()}`,
      domain: this.domain,
      type: 'metrics-recorded',
      data: metrics,
      timestamp: new Date(),
    });
  }

  recordUserActivity(userId: string, activity: string, dashboard: string): void {
    recordAnalyticsEvent({
      id: `operator-user-${Date.now()}`,
      domain: this.domain,
      type: 'user-activity',
      data: { userId, activity, dashboard },
      timestamp: new Date(),
    });
  }

  recordDashboardLoad(dashboard: string, loadTime: number, success: boolean): void {
    recordAnalyticsEvent({
      id: `operator-dashboard-${Date.now()}`,
      domain: this.domain,
      type: 'dashboard-load',
      severity: success ? 'info' : 'warning',
      data: { dashboard, loadTime, success },
      timestamp: new Date(),
    });
  }

  recordUserFeedback(userId: string, rating: number, feedback: string): void {
    recordAnalyticsEvent({
      id: `operator-feedback-${Date.now()}`,
      domain: this.domain,
      type: 'user-feedback',
      data: { userId, rating, feedback },
      timestamp: new Date(),
    });
  }

  getRealtimeAnalytics() {
    return getRealtimeAnalytics(this.domain);
  }

  generateReport(type: 'daily' | 'weekly' | 'monthly', period: { start: Date; end: Date }) {
    return generateAnalyticsReport(this.domain, type, period);
  }

  analyzeUserEngagement(): {
    engagementScore: number;
    activeUsers: number;
    averageSessionDuration: number;
    retentionRate: number;
    recommendations: string[];
  } {
    const analytics = this.getRealtimeAnalytics();
    const metrics = analytics.currentMetrics;

    const engagementScore = Math.round(metrics.performance.availability * 100);
    const activeUsers = metrics.usage.activeUsers;
    const averageSessionDuration = metrics.usage.sessionDuration;
    const retentionRate = metrics.business.conversionRate;

    const recommendations: string[] = [];

    if (activeUsers < 10) {
      recommendations.push('Increase user engagement initiatives');
    } else if (activeUsers > 50) {
      recommendations.push('Maintain current engagement levels');
    }

    if (averageSessionDuration < 300) {
      recommendations.push('Improve dashboard engagement');
    }

    if (retentionRate < 0.5) {
      recommendations.push('Focus on user retention strategies');
    }

    return {
      engagementScore,
      activeUsers,
      averageSessionDuration: Math.round(averageSessionDuration),
      retentionRate: Math.round(retentionRate * 100),
      recommendations,
    };
  }

  private convertToBaseMetrics(operatorMetrics: OperatorMetrics): AnalyticsMetrics {
    return {
      performance: operatorMetrics.performance,
      usage: operatorMetrics.usage,
      business: operatorMetrics.business,
      operational: operatorMetrics.operational,
    };
  }

  getDefaultMetrics(): OperatorMetrics {
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
      userEngagement: {
        activeUsers: 0,
        totalSessions: 0,
        averageSessionDuration: 0,
        returnUsers: 0,
        newUsers: 0,
      },
      dashboardUsage: {
        pageViews: 0,
        uniquePages: 0,
        mostUsedDashboards: {},
        averageLoadTime: 0,
        errorRate: 0,
      },
      featureAdoption: {
        totalFeatures: 0,
        adoptedFeatures: 0,
        featureUsage: {},
        adoptionRate: 0,
      },
      userExperience: {
        satisfactionScore: 0,
        netPromoterScore: 0,
        taskCompletionRate: 0,
        errorFrequency: 0,
        accessibilityScore: 0,
      },
    };
  }
}

export function getOperatorAnalytics(): OperatorAnalytics {
  return OperatorAnalytics.getInstance();
}