/**
 * Observability System
 * 
 * Provides telemetry, metrics, logging, and tracing for the DIX VISION system
 * This is a foundational infrastructure package used by all modules
 */

import { OBSERVABILITY_CONFIG } from '@dix-vision/shared-config';

// ============================================================================
// LOGGING SYSTEM
// ============================================================================

export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

export interface LogEntry {
  timestamp: Date;
  level: LogLevel;
  component: string;
  message: string;
  data?: Record<string, unknown>;
  error?: Error;
}

export class Logger {
  private component: string;
  private config = OBSERVABILITY_CONFIG.logging;

  constructor(component: string) {
    this.component = component;
  }

  debug(message: string, data?: Record<string, unknown>): void {
    this.log(LogLevel.DEBUG, message, data);
  }

  info(message: string, data?: Record<string, unknown>): void {
    this.log(LogLevel.INFO, message, data);
  }

  warn(message: string, data?: Record<string, unknown>): void {
    this.log(LogLevel.WARN, message, data);
  }

  error(message: string, error?: Error, data?: Record<string, unknown>): void {
    this.log(LogLevel.ERROR, message, data, error);
  }

  private log(level: LogLevel, message: string, data?: Record<string, unknown>, error?: Error): void {
    // Skip if level is below configured level
    if (!this.shouldLog(level)) {
      return;
    }

    const entry: LogEntry = {
      timestamp: new Date(),
      level,
      component: this.component,
      message,
      data,
      error,
    };

    // Console output
    if (this.config.enableConsole) {
      this.outputToConsole(entry);
    }

    // File output would go here
    if (this.config.enableFile) {
      // Implementation would write to file
    }
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR];
    const currentLevelIndex = levels.indexOf(this.config.level);
    const requestedLevelIndex = levels.indexOf(level);
    return requestedLevelIndex >= currentLevelIndex;
  }

  private outputToConsole(entry: LogEntry): void {
    const timestamp = entry.timestamp.toISOString();
    const prefix = `[${timestamp}] [${entry.level.toUpperCase()}] [${entry.component}]`;
    
    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(prefix, entry.message, entry.data || '');
        break;
      case LogLevel.INFO:
        console.info(prefix, entry.message, entry.data || '');
        break;
      case LogLevel.WARN:
        console.warn(prefix, entry.message, entry.data || '');
        break;
      case LogLevel.ERROR:
        console.error(prefix, entry.message, entry.error || '', entry.data || '');
        break;
    }
  }
}

// ============================================================================
// METRICS SYSTEM
// ============================================================================

export interface Metric {
  name: string;
  value: number;
  timestamp: Date;
  labels?: Record<string, string>;
}

export class MetricsCollector {
  private metrics: Map<string, Metric[]> = new Map();
  private config = OBSERVABILITY_CONFIG.metrics;
  private collectInterval: NodeJS.Timeout | null = null;

  constructor() {
    if (this.config.enabled) {
      this.startCollection();
    }
  }

  private startCollection(): void {
    this.collectInterval = setInterval(() => {
      this.collectSystemMetrics();
    }, this.config.collectIntervalMs);
  }

  stop(): void {
    if (this.collectInterval) {
      clearInterval(this.collectInterval);
      this.collectInterval = null;
    }
  }

  /**
   * Record a metric
   */
  recordMetric(name: string, value: number, labels?: Record<string, string>): void {
    const metric: Metric = {
      name,
      value,
      timestamp: new Date(),
      labels,
    };

    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }

    this.metrics.get(name)!.push(metric);

    // Keep only recent metrics (last 1000)
    const metrics = this.metrics.get(name)!;
    if (metrics.length > 1000) {
      metrics.shift();
    }
  }

  /**
   * Get metrics for a name
   */
  getMetrics(name: string): Metric[] {
    return this.metrics.get(name) || [];
  }

  /**
   * Get all metrics
   */
  getAllMetrics(): Map<string, Metric[]> {
    return this.metrics;
  }

  /**
   * Collect system metrics
   */
  private collectSystemMetrics(): void {
    // Memory usage
    const memoryUsage = process.memoryUsage();
    this.recordMetric('memory.heap_used', memoryUsage.heapUsed);
    this.recordMetric('memory.heap_total', memoryUsage.heapTotal);
    this.recordMetric('memory.external', memoryUsage.external);

    // CPU usage would go here
    // this.recordMetric('cpu.usage', getCpuUsage());

    // Event loop lag would go here
    // this.recordMetric('event_loop.lag', getEventLoopLag());
  }

  /**
   * Get metrics in Prometheus format
   */
  getPrometheusMetrics(): string {
    let output = '';
    
    for (const [name, metrics] of this.metrics.entries()) {
      if (metrics.length === 0) continue;
      
      const latest = metrics[metrics.length - 1];
      const labelsStr = latest.labels 
        ? '{' + Object.entries(latest.labels).map(([k, v]) => `${k}="${v}"`).join(',') + '}'
        : '';
      
      output += `dix_vision_${name}${labelsStr} ${latest.value} ${latest.timestamp.getTime()}\n`;
    }
    
    return output;
  }
}

// ============================================================================
// TRACING SYSTEM
// ============================================================================

export interface Span {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  operation: string;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  tags?: Record<string, string>;
  status?: string;
}

export class Tracer {
  private spans: Span[] = [];
  private config = OBSERVABILITY_CONFIG.tracing;
  private currentSpan: Span | null = null;

  constructor() {
    if (this.config.enabled) {
      console.log('Tracing enabled');
    }
  }

  /**
   * Start a new span
   */
  startSpan(operation: string, parentSpanId?: string): Span {
    const span: Span = {
      traceId: this.generateTraceId(),
      spanId: this.generateSpanId(),
      parentSpanId,
      operation,
      startTime: new Date(),
    };

    this.spans.push(span);
    this.currentSpan = span;

    return span;
  }

  /**
   * End the current span
   */
  endSpan(tags?: Record<string, string>, status?: string): void {
    if (!this.currentSpan) {
      return;
    }

    this.currentSpan.endTime = new Date();
    this.currentSpan.duration = this.currentSpan.endTime.getTime() - this.currentSpan.startTime.getTime();
    this.currentSpan.tags = tags;
    this.currentSpan.status = status;

    this.currentSpan = null;
  }

  /**
   * Get all spans
   */
  getSpans(): Span[] {
    return this.spans;
  }

  /**
   * Get spans by trace ID
   */
  getSpansByTraceId(traceId: string): Span[] {
    return this.spans.filter(span => span.traceId === traceId);
  }

  private generateTraceId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 16)}`;
  }

  private generateSpanId(): string {
    return Math.random().toString(36).substr(2, 16);
  }
}

// ============================================================================
// TELEMETRY MANAGER
// ============================================================================

export class TelemetryManager {
  private logger: Logger;
  private metrics: MetricsCollector;
  private tracer: Tracer;

  constructor(component: string) {
    this.logger = new Logger(component);
    this.metrics = new MetricsCollector();
    this.tracer = new Tracer();
  }

  getLogger(): Logger {
    return this.logger;
  }

  getMetrics(): MetricsCollector {
    return this.metrics;
  }

  getTracer(): Tracer {
    return this.tracer;
  }

  /**
   * Shutdown telemetry
   */
  async shutdown(): Promise<void> {
    this.metrics.stop();
    // Additional cleanup would go here
  }
}

// ============================================================================
// FACTORY FUNCTIONS
// ============================================================================

/**
 * Create a logger for a component
 */
export function createLogger(component: string): Logger {
  return new Logger(component);
}

/**
 * Create a telemetry manager for a component
 */
export function createTelemetryManager(component: string): TelemetryManager {
  return new TelemetryManager(component);
}