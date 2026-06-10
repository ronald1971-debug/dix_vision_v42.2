/**
 * Shared Type Definitions for DIX VISION System
 * 
 * This package contains type definitions shared across all modules:
 * - TypeScript types for frontend/backend communication
 * - Python type stubs for cross-language compatibility
 * - Governance constraint types
 * - Event system types
 * - Domain model types
 */

import { z } from 'zod';

// ============================================================================
// CORE SYSTEM TYPES
// ============================================================================

export type SystemStatus = 'operational' | 'degraded' | 'maintenance' | 'emergency';

export interface SystemHealth {
  status: SystemStatus;
  uptime: number;
  lastCheck: Date;
  components: ComponentHealth[];
}

export interface ComponentHealth {
  name: string;
  status: SystemStatus;
  latency?: number;
  errorRate?: number;
  lastError?: string;
}

// ============================================================================
// GOVERNANCE TYPES
// ============================================================================

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface GovernanceConstraints {
  maxDrawdown: number; // percentage
  maxLossPerTrade: number; // percentage
  failClosed: boolean;
  forbiddenBehaviors: string[];
  requiredBehaviors: string[];
}

export interface RiskProfile {
  level: RiskLevel;
  exposure: number;
  marginUsed: number;
  portfolio: Position[];
}

export interface Position {
  symbol: string;
  size: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnl: number;
}

// ============================================================================
// EXECUTION TYPES
// ============================================================================

export type OrderSide = 'buy' | 'sell';
export type OrderType = 'market' | 'limit' | 'stop' | 'stop_limit';
export type OrderStatus = 'pending' | 'open' | 'filled' | 'cancelled' | 'rejected';

export interface OrderIntent {
  side: OrderSide;
  type: OrderType;
  symbol: string;
  quantity: number;
  price?: number;
  stopPrice?: number;
  timeInForce?: 'GTC' | 'IOC' | 'FOK';
  metadata?: Record<string, unknown>;
}

export interface ExecutionResult {
  orderId: string;
  status: OrderStatus;
  filledQuantity: number;
  averagePrice: number;
  fees: number;
  timestamp: Date;
}

// ============================================================================
// COGNITIVE TYPES
// ============================================================================

export type AgentType = 'indira' | 'dyon';

export interface CognitiveEvent {
  type: string;
  agent: AgentType;
  timestamp: Date;
  data: unknown;
  confidence: number;
}

export interface MarketAnalysis {
  symbol: string;
  sentiment: 'bullish' | 'bearish' | 'neutral';
  signals: TradingSignal[];
  confidence: number;
  reasoning: string[];
}

export interface TradingSignal {
  type: 'entry' | 'exit' | 'hold';
  strength: number;
  timeframe: string;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// SYSTEM HAZARD TYPES (DYON)
// ============================================================================

export type HazardType = 
  | 'websocket_timeout'
  | 'exchange_unreachable'
  | 'stale_market_data'
  | 'process_crash'
  | 'data_integrity_failure'
  | 'clock_drift_detected'
  | 'memory_exhaustion';

export interface SystemHazardEvent {
  type: HazardType;
  severity: RiskLevel;
  component: string;
  timestamp: Date;
  details: Record<string, unknown>;
  requiresEmergencyAction: boolean;
}

// ============================================================================
// EVENT SYSTEM TYPES
// ============================================================================

export interface SystemEvent {
  id: string;
  type: string;
  source: string;
  timestamp: Date;
  data: unknown;
  correlationId?: string;
  causationId?: string;
}

// ============================================================================
// ZOD SCHEMAS FOR VALIDATION
// ============================================================================

export const GovernanceConstraintsSchema = z.object({
  maxDrawdown: z.number().min(0).max(100),
  maxLossPerTrade: z.number().min(0).max(100),
  failClosed: z.boolean(),
  forbiddenBehaviors: z.array(z.string()),
  requiredBehaviors: z.array(z.string()),
});

export const OrderIntentSchema = z.object({
  side: z.enum(['buy', 'sell']),
  type: z.enum(['market', 'limit', 'stop', 'stop_limit']),
  symbol: z.string(),
  quantity: z.number().positive(),
  price: z.number().positive().optional(),
  stopPrice: z.number().positive().optional(),
  timeInForce: z.enum(['GTC', 'IOC', 'FOK']).optional(),
  metadata: z.record(z.unknown()).optional(),
});

export const SystemHazardEventSchema = z.object({
  type: z.enum([
    'websocket_timeout',
    'exchange_unreachable',
    'stale_market_data',
    'process_crash',
    'data_integrity_failure',
    'clock_drift_detected',
    'memory_exhaustion'
  ]),
  severity: z.enum(['low', 'medium', 'high', 'critical']),
  component: z.string(),
  timestamp: z.date(),
  details: z.record(z.unknown()),
  requiresEmergencyAction: z.boolean(),
});