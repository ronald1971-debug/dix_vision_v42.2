/**
 * INDIRA Domain Analytics
 * 
 * Domain-specific analytics for market intelligence including
 * market data analytics, signal performance, sentiment analysis,
 * and predictive analytics.
 */

import {
  AnalyticsMetrics,
  recordDomainMetrics,
  recordAnalyticsEvent,
  getRealtimeAnalytics,
  generateAnalyticsReport,
} from '../../shared/utils/analytics-engine';

// ============================================================================
// INDIRA-Specific Metrics
// ============================================================================

export interface IndiraMetrics extends AnalyticsMetrics {
  market: MarketMetrics;
  intelligence: IntelligenceMetrics;
  sentiment: SentimentMetrics;
  predictions: PredictionMetrics;
}

export interface MarketMetrics {
  dataPointsCollected: number;
  dataSourcesActive: number;
  dataFreshness: number; // Average age of data in minutes
  dataQuality: number; // Data quality score 0-1
  coverage: number; // Market coverage percentage
}

export interface IntelligenceMetrics {
  signalsGenerated: number;
  signalAccuracy: number; // Signal accuracy percentage
  signalPrecision: number; // Signal precision percentage
  falsePositives: number;
  falseNegatives: number;
}

export interface SentimentMetrics {
  sentimentScore: number; // -1 to 1
  sentimentVolume: number; // Number of sentiment data points
  sentimentAccuracy: number; // Sentiment analysis accuracy
  newsImpact: number; // News impact score
  socialImpact: number; // Social media impact score
}

export interface PredictionMetrics {
  predictionsMade: number;
  predictionAccuracy: number; // Prediction accuracy percentage
  predictionConfidence: number; // Average confidence score
  successfulPredictions: number;
  failedPredictions: number;
}

// ============================================================================
// INDIRA Analytics Manager
// ============================================================================

export class IndiraAnalytics {
  private static instance: IndiraAnalytics;
  private domain = 'indira';

  private constructor() {
    this.initializeAnalytics();
  }

  static getInstance(): IndiraAnalytics {
    if (!IndiraAnalytics.instance) {
      IndiraAnalytics.instance = new IndiraAnalytics();
    }
    return IndiraAnalytics.instance;
  }

  private initializeAnalytics(): void {
    console.log('INDIRA Analytics initialized');
  }

  // Record INDIRA-specific metrics
  recordMetrics(metrics: IndiraMetrics): void {
    recordDomainMetrics(this.domain, this.convertToBaseMetrics(metrics));
    
    // Record domain-specific event
    recordAnalyticsEvent({
      id: `indira-metrics-${Date.now()}`,
      domain: this.domain,
      type: 'metrics-recorded',
      data: metrics,
      timestamp: new Date(),
    });
  }

  // Market Data Analytics
  recordMarketDataCollection(dataPoints: number, sources: number, freshness: number, quality: number): void {
    recordAnalyticsEvent({
      id: `indira-market-data-${Date.now()}`,
      domain: this.domain,
      type: 'market-data-collection',
      data: {
        dataPoints,
        sources,
        freshness,
        quality,
      },
      timestamp: new Date(),
    });
  }

  recordDataQualityIssue(issue: string, severity: 'info' | 'warning' | 'error'): void {
    recordAnalyticsEvent({
      id: `indira-quality-${Date.now()}`,
      domain: this.domain,
      type: 'data-quality-issue',
      severity,
      title: 'Data Quality Issue',
      message: issue,
      data: { issue },
      timestamp: new Date(),
    });
  }

  // Intelligence Analytics
  recordSignalGeneration(signal: any, accuracy: number, confidence: number): void {
    recordAnalyticsEvent({
      id: `indira-signal-${Date.now()}`,
      domain: this.domain,
      type: 'signal-generated',
      data: {
        signal,
        accuracy,
        confidence,
      },
      timestamp: new Date(),
    });
  }

  recordSignalPerformance(signalId: string, success: boolean, impact: number): void {
    recordAnalyticsEvent({
      id: `indira-signal-perf-${Date.now()}`,
      domain: this.domain,
      type: 'signal-performance',
      data: {
        signalId,
        success,
        impact,
      },
      timestamp: new Date(),
    });
  }

  // Sentiment Analytics
  recordSentimentData(sentiment: number, volume: number, source: string): void {
    recordAnalyticsEvent({
      id: `indira-sentiment-${Date.now()}`,
      domain: this.domain,
      type: 'sentiment-data',
      data: {
        sentiment,
        volume,
        source,
      },
      timestamp: new Date(),
    });
  }

  recordSentimentAnomaly(anomaly: string, severity: 'info' | 'warning' | 'error'): void {
    recordAnalyticsEvent({
      id: `indira-sentiment-anomaly-${Date.now()}`,
      domain: this.domain,
      type: 'sentiment-anomaly',
      severity,
      title: 'Sentiment Anomaly',
      message: anomaly,
      data: { anomaly },
      timestamp: new Date(),
    });
  }

  // Prediction Analytics
  recordPrediction(prediction: any, confidence: number, timeHorizon: number): void {
    recordAnalyticsEvent({
      id: `indira-prediction-${Date.now()}`,
      domain: this.domain,
      type: 'prediction-made',
      data: {
        prediction,
        confidence,
        timeHorizon,
      },
      timestamp: new Date(),
    });
  }

  recordPredictionOutcome(predictionId: string, success: boolean, accuracy: number): void {
    recordAnalyticsEvent({
      id: `indira-prediction-outcome-${Date.now()}`,
      domain: this.domain,
      type: 'prediction-outcome',
      data: {
        predictionId,
        success,
        accuracy,
      },
      timestamp: new Date(),
    });
  }

  // Real-time Analytics
  getRealtimeAnalytics() {
    return getRealtimeAnalytics(this.domain);
  }

  // Report Generation
  generateReport(type: 'daily' | 'weekly' | 'monthly', period: { start: Date; end: Date }) {
    return generateAnalyticsReport(this.domain, type, period);
  }

  // Performance Analysis
  analyzePerformance(): {
    overallScore: number;
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
  } {
    const analytics = this.getRealtimeAnalytics();
    const metrics = analytics.currentMetrics;

    const strengths: string[] = [];
    const weaknesses: string[] = [];
    const recommendations: string[] = [];

    // Analyze performance metrics
    if (metrics.performance.latency < 100) {
      strengths.push('Low latency market data processing');
    } else if (metrics.performance.latency > 500) {
      weaknesses.push('High latency in market data processing');
      recommendations.push('Optimize data processing pipeline');
    }

    if (metrics.performance.errorRate < 0.01) {
      strengths.push('Very low error rate');
    } else if (metrics.performance.errorRate > 0.05) {
      weaknesses.push('High error rate');
      recommendations.push('Investigate and fix error sources');
    }

    if (metrics.performance.availability > 0.99) {
      strengths.push('High system availability');
    } else {
      weaknesses.push('System availability below target');
      recommendations.push('Improve system reliability');
    }

    // Calculate overall score
    const performanceScore = (1 - metrics.performance.errorRate) * metrics.performance.availability;
    const efficiencyScore = 1 - (metrics.performance.latency / 1000);
    const overallScore = Math.round(((performanceScore + efficiencyScore) / 2) * 100);

    return {
      overallScore,
      strengths,
      weaknesses,
      recommendations,
    };
  }

  // Market Intelligence Analysis
  analyzeMarketIntelligence(): {
    dataQuality: number;
    signalQuality: number;
    predictionAccuracy: number;
    overall: number;
  } {
    const analytics = this.getRealtimeAnalytics();
    
    // Calculate intelligence quality metrics
    const dataQuality = analytics.currentMetrics.performance.resourceUtilization;
    const signalQuality = analytics.currentMetrics.performance.throughput;
    const predictionAccuracy = analytics.currentMetrics.performance.availability;
    const overall = Math.round(((dataQuality + signalQuality + predictionAccuracy) / 3) * 100);

    return {
      dataQuality: Math.round(dataQuality * 100),
      signalQuality: Math.round(signalQuality * 100),
      predictionAccuracy: Math.round(predictionAccuracy * 100),
      overall,
    };
  }

  // Helper method to convert INDIRA metrics to base metrics
  private convertToBaseMetrics(indiraMetrics: IndiraMetrics): AnalyticsMetrics {
    return {
      performance: indiraMetrics.performance,
      usage: indiraMetrics.usage,
      business: indiraMetrics.business,
      operational: indiraMetrics.operational,
    };
  }

  // Default metrics for INDIRA
  getDefaultMetrics(): IndiraMetrics {
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
      market: {
        dataPointsCollected: 0,
        dataSourcesActive: 0,
        dataFreshness: 0,
        dataQuality: 1,
        coverage: 0,
      },
      intelligence: {
        signalsGenerated: 0,
        signalAccuracy: 0,
        signalPrecision: 0,
        falsePositives: 0,
        falseNegatives: 0,
      },
      sentiment: {
        sentimentScore: 0,
        sentimentVolume: 0,
        sentimentAccuracy: 0,
        newsImpact: 0,
        socialImpact: 0,
      },
      predictions: {
        predictionsMade: 0,
        predictionAccuracy: 0,
        predictionConfidence: 0,
        successfulPredictions: 0,
        failedPredictions: 0,
      },
    };
  }
}

// ============================================================================
// Public API
// ============================================================================

/**
 * Get INDIRA analytics instance
 */
export function getIndiraAnalytics(): IndiraAnalytics {
  return IndiraAnalytics.getInstance();
}

/**
 * Record INDIRA metrics
 */
export function recordIndiraMetrics(metrics: IndiraMetrics): void {
  return IndiraAnalytics.getInstance().recordMetrics(metrics);
}

/**
 * Record market data collection event
 */
export function recordMarketDataCollection(dataPoints: number, sources: number, freshness: number, quality: number): void {
  return IndiraAnalytics.getInstance().recordMarketDataCollection(dataPoints, sources, freshness, quality);
}

/**
 * Record signal generation event
 */
export function recordSignalGeneration(signal: any, accuracy: number, confidence: number): void {
  return IndiraAnalytics.getInstance().recordSignalGeneration(signal, accuracy, confidence);
}

/**
 * Get INDIRA real-time analytics
 */
export function getIndiraRealtimeAnalytics() {
  return IndiraAnalytics.getInstance().getRealtimeAnalytics();
}