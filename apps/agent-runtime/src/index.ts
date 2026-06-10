/**
 * DIX VISION Agent Runtime
 * 
 * Main orchestration service that coordinates all agents, engines, and services.
 * This is the central entry point for the DIX VISION system.
 */

import { IndiraAgent } from '@dix-vision/indira';
import { DyonAgent } from '@dix-vision/dyon';
import { ExecutionEngine } from '@dix-vision/execution-engine';
import { GovernanceEngine } from '@dix-vision/governance-core';
import { TelemetryManager } from '@dix-vision/observability';
import { SYSTEM_CONFIG, RUNTIME_CONFIG } from '@dix-vision/shared-config';
import type { SystemEvent, SystemHazardEvent, OrderIntent } from '@dix-vision/shared-types';
import type { ConstraintSet } from '@dix-vision/governance-core';

// ============================================================================
// EVENT BUS
// ============================================================================

interface EventBus {
  subscribers: Map<string, ((event: SystemEvent) => void)[]>;
  publish(eventType: string, event: SystemEvent): Promise<void>;
  subscribe(eventType: string, handler: (event: SystemEvent) => void): Promise<void>;
}

class SimpleEventBus implements EventBus {
  subscribers = new Map<string, ((event: SystemEvent) => void)[]>();

  async publish(eventType: string, event: SystemEvent): Promise<void> {
    const handlers = this.subscribers.get(eventType) || [];
    for (const handler of handlers) {
      try {
        await handler(event);
      } catch (error) {
        console.error(`Event handler error for ${eventType}:`, error);
      }
    }
  }

  async subscribe(eventType: string, handler: (event: SystemEvent) => void): Promise<void> {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, []);
    }
    this.subscribers.get(eventType)!.push(handler);
  }
}

// ============================================================================
// AGENT RUNTIME CLASS
// ============================================================================

export class AgentRuntime {
  private eventBus: EventBus;
  private telemetry: TelemetryManager;
  private governanceEngine: GovernanceEngine;
  private indiraAgent: IndiraAgent;
  private dyonAgent: DyonAgent;
  private executionEngine: ExecutionEngine;
  private isRunning = false;

  constructor() {
    this.eventBus = new SimpleEventBus();
    this.telemetry = new TelemetryManager('agent-runtime');
    this.governanceEngine = new GovernanceEngine();
    this.indiraAgent = new IndiraAgent(this.eventBus);
    this.dyonAgent = new DyonAgent(this.eventBus);
    this.executionEngine = new ExecutionEngine(this.eventBus);
    
    this.setupEventSubscriptions();
  }

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  private setupEventSubscriptions(): void {
    // Subscribe to system hazards from Dyon
    this.eventBus.subscribe('system_hazard', this.handleSystemHazard.bind(this));
    
    // Subscribe to execution events
    this.eventBus.subscribe('execution_event', this.handleExecutionEvent.bind(this));
    
    // Subscribe to cognitive events from Indira
    this.eventBus.subscribe('cognitive_event', this.handleCognitiveEvent.bind(this));
  }

  // ============================================================================
  // LIFECYCLE MANAGEMENT
  // ============================================================================

  async start(): Promise<void> {
    if (this.isRunning) {
      console.log('AgentRuntime already running');
      return;
    }

    const logger = this.telemetry.getLogger();
    logger.info('Starting DIX VISION Agent Runtime');
    logger.info(`Version: ${SYSTEM_CONFIG.version}`);
    logger.info(`Codename: ${SYSTEM_CONFIG.codename}`);

    try {
      // Start governance engine (loads constraints)
      logger.info('Initializing governance constraints');
      const constraints = this.governanceEngine.getConstraints();
      
      // Update agents with governance constraints
      this.indiraAgent.updateGovernanceConstraints({
        maxDrawdown: constraints.maxDrawdown,
        maxLossPerTrade: constraints.maxLossPerTrade,
        failClosed: constraints.failClosed,
        timestamp: new Date(),
        version: SYSTEM_CONFIG.version,
      });

      this.executionEngine.updateGovernanceConstraints({
        maxDrawdown: constraints.maxDrawdown,
        maxLossPerTrade: constraints.maxLossPerTrade,
        failClosed: constraints.failClosed,
        timestamp: new Date(),
        version: SYSTEM_CONFIG.version,
      });

      // Start Dyon (system monitoring)
      logger.info('Starting Dyon agent (system monitoring)');
      await this.dyonAgent.start();

      // Start Indira (market intelligence)
      logger.info('Starting Indira agent (market intelligence)');
      await this.indiraAgent.start();

      // Start execution engine
      logger.info('Starting execution engine');
      await this.executionEngine.start();

      this.isRunning = true;
      logger.info('DIX VISION Agent Runtime started successfully');
      
      // Emit system startup event
      await this.eventBus.publish('system_event', {
        id: `startup_${Date.now()}`,
        type: 'runtime_started',
        source: 'agent-runtime',
        timestamp: new Date(),
        data: {
          version: SYSTEM_CONFIG.version,
          agents: ['indira', 'dyon'],
          engines: ['execution', 'governance'],
        },
      });

    } catch (error) {
      logger.error('Failed to start AgentRuntime', error);
      throw error;
    }
  }

  async stop(): Promise<void> {
    if (!this.isRunning) {
      console.log('AgentRuntime not running');
      return;
    }

    const logger = this.telemetry.getLogger();
    logger.info('Stopping DIX VISION Agent Runtime');

    try {
      // Stop in reverse order of startup
      await this.executionEngine.stop();
      await this.indiraAgent.stop();
      await this.dyonAgent.stop();
      
      this.isRunning = false;
      logger.info('DIX VISION Agent Runtime stopped successfully');
    } catch (error) {
      logger.error('Error stopping AgentRuntime', error);
      throw error;
    }
  }

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  private async handleSystemHazard(event: SystemEvent): Promise<void> {
    const logger = this.telemetry.getLogger();
    const hazard = event.data as SystemHazardEvent;
    
    logger.warn(`System hazard detected: ${hazard.type} (${hazard.severity})`);
    
    // Get emergency policy from governance
    const policy = this.governanceEngine.getEmergencyPolicy(hazard);
    
    if (policy) {
      logger.info(`Executing emergency policy: ${policy.actions.join(', ')}`);
      await this.executeEmergencyActions(policy);
    } else {
      logger.warn(`No emergency policy found for hazard: ${hazard.type}`);
    }
  }

  private async handleExecutionEvent(event: SystemEvent): Promise<void> {
    const logger = this.telemetry.getLogger();
    logger.info(`Execution event: ${event.type}`, event.data);
  }

  private async handleCognitiveEvent(event: SystemEvent): Promise<void> {
    const logger = this.telemetry.getLogger();
    logger.debug(`Cognitive event: ${event.type}`);
  }

  // ============================================================================
  // EMERGENCY ACTIONS
  // ============================================================================

  private async executeEmergencyActions(policy: any): Promise<void> {
    const logger = this.telemetry.getLogger();
    
    for (const action of policy.actions) {
      logger.info(`Executing emergency action: ${action}`);
      
      switch (action) {
        case 'CANCEL_ALL_ORDERS':
          await this.executionEngine.cancelAllOrders();
          break;
        case 'CLOSE_POSITIONS':
          // Implementation would close positions
          logger.warn('Position closing not yet implemented');
          break;
        case 'HALT_TRADING':
          await this.executionEngine.haltTrading();
          break;
        case 'HALT_NEW_ORDERS':
          // Implementation would halt new orders
          logger.warn('Halt new orders not yet implemented');
          break;
        default:
          logger.warn(`Unknown emergency action: ${action}`);
      }
    }
  }

  // ============================================================================
  // PUBLIC API
  // ============================================================================

  /**
   * Get system health status
   */
  getSystemHealth() {
    return this.dyonAgent.getSystemHealth();
  }

  /**
   * Get governance constraints
   */
  getGovernanceConstraints() {
    return this.governanceEngine.getConstraints();
  }

  /**
   * Check if system is healthy
   */
  isSystemHealthy(): boolean {
    return this.dyonAgent.isSystemHealthy() && this.isRunning;
  }

  /**
   * Get telemetry manager
   */
  getTelemetry() {
    return this.telemetry;
  }

  /**
   * Get event bus for external subscriptions
   */
  getEventBus() {
    return this.eventBus;
  }
}

// ============================================================================
// MAIN ENTRY POINT
// ============================================================================

async function main(): Promise<void> {
  const runtime = new AgentRuntime();
  
  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('Received SIGINT, shutting down...');
    await runtime.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('Received SIGTERM, shutting down...');
    await runtime.stop();
    process.exit(0);
  });

  try {
    await runtime.start();
    console.log('DIX VISION Agent Runtime running. Press Ctrl+C to stop.');
  } catch (error) {
    console.error('Failed to start runtime:', error);
    process.exit(1);
  }
}

// Run if this is the main module
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { AgentRuntime as default };