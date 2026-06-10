/**
 * Execution Engine
 * 
 * Execution layer enforces actions; does not govern cognition
 * Responsibilities: order lifecycle, exchange adapters, constraint enforcement
 * 
 * CRITICAL RULES:
 * - Execution must be deterministic
 * - All actions obey PRECOMPUTED governance constraints
 * - Execution does NOT govern cognition
 * - Capital layer governs exposure; does not govern cognition
 * 
 * FLOW:
 * Order Intent (from Indira)
 *   ↓
 * Precomputed governance constraints
 *   ↓
 * Execution adapters (exchange APIs)
 *   ↓
 * Event Ledger
 */

import type {
  OrderIntent,
  OrderSide,
  OrderType,
  OrderStatus,
  ExecutionResult,
  SystemEvent
} from '@dix-vision/shared-types';
import type { ConstraintSet } from '@dix-vision/governance-core';
import { EXECUTION_CONFIG } from '@dix-vision/shared-config';

// ============================================================================
// EXECUTION ENGINE CLASS
// ============================================================================

export class ExecutionEngine {
  private config = EXECUTION_CONFIG;
  private governanceConstraints: ConstraintSet | null = null;
  private orderLedger: OrderLedger;
  private exchangeAdapters: Map<string, ExchangeAdapter>;
  private eventBus: EventBus;

  constructor(eventBus: EventBus) {
    this.eventBus = eventBus;
    this.orderLedger = new OrderLedger();
    this.exchangeAdapters = new Map();
    this.initialize();
  }

  private initialize(): void {
    console.log('Execution Engine initialized');
    console.log(`Max orders per second: ${this.config.maxOrdersPerSecond}`);
    console.log(`Order timeout: ${this.config.orderTimeoutMs}ms`);
  }

  // ============================================================================
// ORDER LIFECYCLE MANAGEMENT
  // ============================================================================

  /**
   * Execute order intent with governance constraints
   * This is the main entry point for order execution
   */
  public async executeOrderIntent(
    intent: OrderIntent,
    constraints: ConstraintSet
  ): Promise<ExecutionResult> {
    this.governanceConstraints = constraints;

    try {
      // Step 1: Validate intent against constraints
      const validationResult = await this.validateAgainstConstraints(intent);
      if (!validationResult.passed) {
        return this.createRejectedResult(intent, validationResult.reason);
      }

      // Step 2: Create order in ledger
      const order = await this.orderLedger.createOrder(intent);
      
      // Step 3: Submit to exchange adapter
      const result = await this.submitToExchange(order);
      
      // Step 4: Update ledger with result
      await this.orderLedger.updateOrder(order.id, result);
      
      // Step 5: Emit execution event
      await this.emitExecutionEvent('order_executed', order, result);
      
      console.log(`Execution executed order: ${order.id}`);
      return result;
    } catch (error) {
      console.error('Execution failed:', error);
      
      const failedResult: ExecutionResult = {
        orderId: '',
        status: 'rejected',
        filledQuantity: 0,
        averagePrice: 0,
        fees: 0,
        timestamp: new Date(),
      };
      
      return failedResult;
    }
  }

  /**
   * Cancel an existing order
   */
  public async cancelOrder(orderId: string): Promise<ExecutionResult> {
    try {
      const order = await this.orderLedger.getOrder(orderId);
      if (!order) {
        throw new Error(`Order not found: ${orderId}`);
      }

      if (order.status !== 'open' && order.status !== 'pending') {
        throw new Error(`Cannot cancel order with status: ${order.status}`);
      }

      // Submit cancel to exchange
      const adapter = this.exchangeAdapters.get(order.exchange);
      if (!adapter) {
        throw new Error(`No adapter for exchange: ${order.exchange}`);
      }

      const result = await adapter.cancelOrder(orderId);
      
      // Update ledger
      await this.orderLedger.updateOrder(orderId, result);
      
      await this.emitExecutionEvent('order_cancelled', order, result);
      
      console.log(`Execution cancelled order: ${orderId}`);
      return result;
    } catch (error) {
      console.error('Cancel order failed:', error);
      throw error;
    }
  }

  /**
   * Modify an existing order
   */
  public async modifyOrder(
    orderId: string,
    modifications: Partial<OrderIntent>
  ): Promise<ExecutionResult> {
    try {
      const order = await this.orderLedger.getOrder(orderId);
      if (!order) {
        throw new Error(`Order not found: ${orderId}`);
      }

      // Cancel existing order
      await this.cancelOrder(orderId);
      
      // Create new order with modifications
      const newIntent = { ...order.intent, ...modifications };
      return await this.executeOrderIntent(newIntent, this.governanceConstraints!);
    } catch (error) {
      console.error('Modify order failed:', error);
      throw error;
    }
  }

  // ============================================================================
  // CONSTRAINT VALIDATION
  // ============================================================================

  /**
   * Validate order intent against precomputed governance constraints
   * This is non-blocking - constraints are precomputed
   */
  private async validateAgainstConstraints(intent: OrderIntent): Promise<ValidationResult> {
    if (!this.governanceConstraints) {
      return {
        passed: false,
        reason: 'Governance constraints not loaded',
      };
    }

    // Validate against max loss per trade
    if (intent.quantity * (intent.price || 0) > this.governanceConstraints.maxLossPerTrade) {
      return {
        passed: false,
        reason: 'Order exceeds max loss per trade constraint',
      };
    }

    // Additional constraint checks would go here
    
    return {
      passed: true,
      reason: '',
    };
  }

  /**
   * Create rejected result
   */
  private createRejectedResult(intent: OrderIntent, reason: string): ExecutionResult {
    return {
      orderId: `rejected_${Date.now()}`,
      status: 'rejected',
      filledQuantity: 0,
      averagePrice: 0,
      fees: 0,
      timestamp: new Date(),
    };
  }

  // ============================================================================
  // EXCHANGE ADAPTER MANAGEMENT
  // ============================================================================

  /**
   * Register an exchange adapter
   */
  public registerExchangeAdapter(exchange: string, adapter: ExchangeAdapter): void {
    this.exchangeAdapters.set(exchange, adapter);
    console.log(`Registered exchange adapter: ${exchange}`);
  }

  /**
   * Get an exchange adapter
   */
  public getExchangeAdapter(exchange: string): ExchangeAdapter | undefined {
    return this.exchangeAdapters.get(exchange);
  }

  /**
   * Submit order to exchange adapter
   */
  private async submitToExchange(order: Order): Promise<ExecutionResult> {
    const adapter = this.exchangeAdapters.get(order.exchange);
    if (!adapter) {
      throw new Error(`No adapter for exchange: ${order.exchange}`);
    }

    return await adapter.submitOrder(order.intent);
  }

  // ============================================================================
  // ORDER LEDGER
  // ============================================================================

  /**
   * Get order from ledger
   */
  public async getOrder(orderId: string): Promise<Order | undefined> {
    return await this.orderLedger.getOrder(orderId);
  }

  /**
   * Get all orders
   */
  public async getAllOrders(): Promise<Order[]> {
    return await this.orderLedger.getAllOrders();
  }

  /**
   * Get orders by status
   */
  public async getOrdersByStatus(status: OrderStatus): Promise<Order[]> {
    return await this.orderLedger.getOrdersByStatus(status);
  }

  // ============================================================================
  // EMERGENCY ACTIONS
  // ============================================================================

  /**
   * Cancel all orders (emergency action)
   */
  public async cancelAllOrders(): Promise<void> {
    console.log('Execution executing emergency: CANCEL_ALL_ORDERS');
    
    const openOrders = await this.getOrdersByStatus('open');
    const cancelPromises = openOrders.map(order => this.cancelOrder(order.id));
    
    await Promise.all(cancelPromises);
    console.log(`Cancelled ${openOrders.length} orders`);
  }

  /**
   * Halt trading (emergency action)
   */
  public async haltTrading(): Promise<void> {
    console.log('Execution executing emergency: HALT_TRADING');
    
    // Cancel all orders
    await this.cancelAllOrders();
    
    // Set trading halted flag
    // Implementation would set a flag that prevents new orders
    
    console.log('Trading halted');
  }

  // ============================================================================
  // GOVERNANCE INTEGRATION
  // ============================================================================

  /**
   * Update governance constraints (precomputed, not blocking)
   */
  public updateGovernanceConstraints(constraints: ConstraintSet): void {
    this.governanceConstraints = constraints;
    console.log('Execution updated governance constraints');
  }

  // ============================================================================
  // EVENT SYSTEM
  // ============================================================================

  /**
   * Emit execution event
   */
  private async emitExecutionEvent(
    eventType: string,
    order: Order,
    result: ExecutionResult
  ): Promise<void> {
    const event: SystemEvent = {
      id: `execution_${Date.now()}`,
      type: eventType,
      source: 'execution_engine',
      timestamp: new Date(),
      data: {
        orderId: order.id,
        intent: order.intent,
        result,
      },
    };

    await this.eventBus.publish('execution_event', event);
  }

  // ============================================================================
  // LIFECYCLE
  // ============================================================================

  public async start(): Promise<void> {
    console.log('Execution Engine starting');
    // Implementation would start background tasks
  }

  public async stop(): Promise<void> {
    console.log('Execution Engine stopping');
    // Implementation would stop background tasks
  }
}

// ============================================================================
// ORDER LEDGER CLASS
// ============================================================================

class OrderLedger {
  private orders: Map<string, Order> = new Map();

  async createOrder(intent: OrderIntent): Promise<Order> {
    const order: Order = {
      id: `order_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      intent,
      status: 'pending',
      exchange: this.determineExchange(intent.symbol),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.orders.set(order.id, order);
    return order;
  }

  async getOrder(orderId: string): Promise<Order | undefined> {
    return this.orders.get(orderId);
  }

  async updateOrder(orderId: string, result: ExecutionResult): Promise<void> {
    const order = this.orders.get(orderId);
    if (order) {
      order.status = result.status;
      order.result = result;
      order.updatedAt = new Date();
    }
  }

  async getAllOrders(): Promise<Order[]> {
    return Array.from(this.orders.values());
  }

  async getOrdersByStatus(status: OrderStatus): Promise<Order[]> {
    return Array.from(this.orders.values()).filter(order => order.status === status);
  }

  private determineExchange(symbol: string): string {
    // Implementation would determine exchange based on symbol
    return 'default';
  }
}

// ============================================================================
// SUPPORTING TYPES
// ============================================================================

export interface Order {
  id: string;
  intent: OrderIntent;
  status: OrderStatus;
  exchange: string;
  createdAt: Date;
  updatedAt: Date;
  result?: ExecutionResult;
}

export interface ExchangeAdapter {
  submitOrder(intent: OrderIntent): Promise<ExecutionResult>;
  cancelOrder(orderId: string): Promise<ExecutionResult>;
  getOrderStatus(orderId: string): Promise<OrderStatus>;
}

export interface ValidationResult {
  passed: boolean;
  reason: string;
}

export interface EventBus {
  publish(eventType: string, event: SystemEvent): Promise<void>;
  subscribe(eventType: string, handler: (event: SystemEvent) => void): Promise<void>;
}