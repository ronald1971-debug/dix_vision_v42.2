/**
 * Mock Data Generators for Agent Operations Center
 * 
 * Generates realistic mock data for testing the Agent Operations Center UI
 * without requiring backend WebSocket endpoints
 */

import type {
  IndiraActivity,
  DyonActivity,
  Task,
  SystemEvent,
  WebSocketMessage,
} from '@/types/agent';

// ============================================================================
// Utility Functions
// ============================================================================

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function getRandomElement<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}

function getRandomNumber(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

function getRandomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ============================================================================
// INDIRA Activity Generator
// ============================================================================

const INDIRA_ACTIVITY_TYPES: IndiraActivity['type'][] = [
  'goal-setting',
  'task-execution',
  'portfolio-reasoning',
  'risk-reasoning',
  'trade-reasoning',
  'confidence-analysis',
  'market-research',
  'trader-modeling',
  'strategy-creation',
  'strategy-evolution',
  'learning-activity',
  'browser-session',
];

const INDIRA_STATUSES: IndiraActivity['status'][] = ['active', 'completed', 'paused'];

const RESEARCH_TOPICS = [
  'Bitcoin market analysis',
  'Ethereum DeFi protocols',
  'Solana memecoin trends',
  'Traditional equities correlation',
  'FX market regime detection',
];

const TRADER_IDS = ['0x1234...', '0xabcd...', 'wallet_789', 'whale_42'];

const STRATEGY_NAMES = [
  'Momentum Reversal',
  'Liquidity Arbitrage',
  'Sentiment-Based Trading',
  'Cross-Asset Mean Reversion',
];

export function generateIndiraActivity(): IndiraActivity {
  const type = getRandomElement(INDIRA_ACTIVITY_TYPES);
  const status = getRandomElement(INDIRA_STATUSES);

  const baseActivity: IndiraActivity = {
    id: generateId(),
    type,
    timestamp: Date.now() - getRandomInt(0, 3600000), // Within last hour
    status,
    data: {},
  };

  // Add context based on activity type
  if (type === 'market-research') {
    baseActivity.context = {
      objective: 'Market analysis',
      market: getRandomElement(RESEARCH_TOPICS),
    };
  } else if (type === 'trader-modeling') {
    baseActivity.context = {
      objective: 'Trader profiling',
      trader: getRandomElement(TRADER_IDS),
    };
  } else if (type === 'strategy-creation' || type === 'strategy-evolution') {
    baseActivity.context = {
      objective: 'Strategy development',
      strategy: getRandomElement(STRATEGY_NAMES),
    };
  }

  return baseActivity;
}

export function generateIndiraActivities(count: number = 10): IndiraActivity[] {
  return Array.from({ length: count }, () => generateIndiraActivity()).sort(
    (a, b) => b.timestamp - a.timestamp
  );
}

// ============================================================================
// DYON Activity Generator
// ============================================================================

const DYON_ACTIVITY_TYPES: DyonActivity['type'][] = [
  'goal-setting',
  'task-execution',
  'repository-analysis',
  'mutation-candidate',
  'refactor-activity',
  'build-task',
  'testing-activity',
  'code-review',
  'architecture-work',
  'infrastructure-task',
  'debugging-activity',
  'deployment-task',
  'workspace-activity',
];

const DYON_STATUSES: DyonActivity['status'][] = ['active', 'completed', 'paused', 'error'];

const REPO_PATHS = [
  'src/execution_engine/',
  'src/intelligence_engine/',
  'src/learning_engine/',
  'src/governance_engine/',
  'desktop_agent/',
];

const FILE_NAMES = [
  'engine.py',
  'trading_model.ts',
  'risk_analyzer.py',
  'data_processor.ts',
  'api_handler.py',
];

export function generateDyonActivity(): DyonActivity {
  const type = getRandomElement(DYON_ACTIVITY_TYPES);
  const status = getRandomElement(DYON_STATUSES);

  const baseActivity: DyonActivity = {
    id: generateId(),
    type,
    timestamp: Date.now() - getRandomInt(0, 3600000),
    status,
    data: {},
  };

  // Add context based on activity type
  if (type === 'repository-analysis') {
    baseActivity.context = {
      repository: getRandomElement(REPO_PATHS),
    };
  } else if (
    type === 'refactor-activity' ||
    type === 'mutation-candidate' ||
    type === 'workspace-activity'
  ) {
    baseActivity.context = {
      repository: getRandomElement(REPO_PATHS),
      file: getRandomElement(FILE_NAMES),
    };
  }

  return baseActivity;
}

export function generateDyonActivities(count: number = 10): DyonActivity[] {
  return Array.from({ length: count }, () => generateDyonActivity()).sort(
    (a, b) => b.timestamp - a.timestamp
  );
}

// ============================================================================
// Task Generator
// ============================================================================

const TASK_TYPES: Task['type'][] = [
  'research',
  'engineering',
  'trading',
  'analysis',
  'general',
];

const TASK_PRIORITIES: Task['priority'][] = ['critical', 'high', 'medium', 'low'];

const TASK_STATUSES: Task['status'][] = [
  'pending',
  'active',
  'completed',
  'blocked',
  'cancelled',
];

const TASK_ASSIGNED_TO: Task['assignedTo'][] = [
  'indira',
  'dyon',
  'operator',
  'shared',
];

const TASK_TITLES = [
  'Analyze Bitcoin market trends',
  'Refactor execution engine performance',
  'Implement slippage prediction model',
  'Review risk management system',
  'Update governance constraints',
  'Research Solana memecoin patterns',
  'Optimize WebSocket message handling',
  'Create trader similarity clustering',
];

const TASK_DESCRIPTIONS = [
  'Detailed analysis required for decision making',
  'Performance optimization needed for production',
  'New model implementation for improved accuracy',
  'Security and compliance review necessary',
  'System update to maintain operational requirements',
];

export function generateTask(): Task {
  const title = getRandomElement(TASK_TITLES);
  const description = getRandomElement(TASK_DESCRIPTIONS);

  return {
    id: generateId(),
    title,
    description,
    type: getRandomElement(TASK_TYPES),
    priority: getRandomElement(TASK_PRIORITIES),
    status: getRandomElement(TASK_STATUSES),
    assignedTo: getRandomElement(TASK_ASSIGNED_TO),
    createdBy: 'operator',
    createdAt: Date.now() - getRandomInt(0, 86400000), // Within last day
    deadline: Date.now() + getRandomInt(3600000, 604800000), // 1-7 days from now
    dependencies: [],
    subtasks: [],
    progress: getRandomInt(0, 100),
    context: {
      project: 'System Optimization',
      objective: 'Improve overall system performance',
    },
  };
}

export function generateTasks(count: number = 15): Task[] {
  return Array.from({ length: count }, () => generateTask()).sort(
    (a, b) => b.createdAt - a.createdAt
  );
}

// ============================================================================
// System Event Generator
// ============================================================================

const EVENT_SOURCES: SystemEvent['source'][] = [
  'system',
  'market',
  'trade',
  'learning',
  'governance',
  'dyon',
  'indira',
  'desktop',
  'browser',
];

const EVENT_SEVERITIES: SystemEvent['severity'][] = ['info', 'warning', 'error', 'critical'];

const EVENT_TYPES = [
  'system:startup',
  'system:shutdown',
  'system:error',
  'market:regime-change',
  'market:volatility-spike',
  'trade:executed',
  'trade:failed',
  'learning:model-updated',
  'governance:constraint-violation',
  'dyon:mutation-applied',
  'indira:insight-generated',
  'desktop:application-launched',
  'browser:navigation',
];

const EVENT_MESSAGES: Record<string, string> = {
  'system:startup': 'System started successfully',
  'system:shutdown': 'System shutdown initiated',
  'system:error': 'Critical system error detected',
  'market:regime-change': 'Market regime changed to trending',
  'market:volatility-spike': 'Unusual volatility detected',
  'trade:executed': 'Trade executed successfully',
  'trade:failed': 'Trade execution failed',
  'learning:model-updated': 'ML model updated with new data',
  'governance:constraint-violation': 'Risk constraint violation detected',
  'dyon:mutation-applied': 'Code mutation applied successfully',
  'indira:insight-generated': 'New trading insight generated',
  'desktop:application-launched': 'Desktop application launched',
  'browser:navigation': 'Browser navigation event',
};

export function generateSystemEvent(): SystemEvent {
  const type = getRandomElement(EVENT_TYPES);
  const source = getRandomElement(EVENT_SOURCES);
  const severity = getRandomElement(EVENT_SEVERITIES);

  const baseEvent: SystemEvent = {
    id: generateId(),
    source,
    type,
    timestamp: Date.now() - getRandomInt(0, 7200000), // Within last 2 hours
    severity,
    data: {
      message: EVENT_MESSAGES[type] || 'Event occurred',
    },
  };

  // Add context based on source
  if (source === 'indira' || source === 'dyon') {
    baseEvent.context = {
      agent: source as 'indira' | 'dyon',
    };
  }

  return baseEvent;
}

export function generateSystemEvents(count: number = 20): SystemEvent[] {
  return Array.from({ length: count }, () => generateSystemEvent()).sort(
    (a, b) => b.timestamp - a.timestamp
  );
}

// ============================================================================
// WebSocket Message Generator
// ============================================================================

export function generateIndiraWebSocketMessage(): WebSocketMessage {
  return {
    type: 'indira:activity',
    data: generateIndiraActivity(),
    timestamp: Date.now(),
  };
}

export function generateDyonWebSocketMessage(): WebSocketMessage {
  return {
    type: 'dyon:activity',
    data: generateDyonActivity(),
    timestamp: Date.now(),
  };
}

export function generateTaskWebSocketMessage(): WebSocketMessage {
  return {
    type: 'task:update',
    data: generateTask(),
    timestamp: Date.now(),
  };
}

export function generateSystemEventWebSocketMessage(): WebSocketMessage {
  return {
    type: 'system:event',
    data: generateSystemEvent(),
    timestamp: Date.now(),
  };
}

export function generateRandomWebSocketMessage(): WebSocketMessage {
  const generators = [
    generateIndiraWebSocketMessage,
    generateDyonWebSocketMessage,
    generateTaskWebSocketMessage,
    generateSystemEventWebSocketMessage,
  ];
  
  return getRandomElement(generators)();
}

// ============================================================================
// Mock WebSocket Manager for Testing
// ============================================================================

/**
 * Mock WebSocket manager that simulates real-time data
 * Generates mock messages periodically
 */
export class MockWebSocketManager {
  private intervalId: NodeJS.Timeout | null = null;
  private subscribers: Map<string, ((message: WebSocketMessage) => void)[]> = new Map();
  private isRunning = false;

  constructor() {
    // Start generating mock data
    this.start();
  }

  private start(): void {
    if (this.isRunning) return;
    
    this.isRunning = true;
    
    // Generate a random message every 2-5 seconds
    this.intervalId = setInterval(() => {
      const message = generateRandomWebSocketMessage();
      this.routeMessage(message);
    }, getRandomInt(2000, 5000));
  }

  private stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.isRunning = false;
  }

  private routeMessage(message: WebSocketMessage): void {
    // Route to specific event type handlers
    const handlers = this.subscribers.get(message.type) || [];
    handlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error('Error in mock message handler:', error);
      }
    });

    // Route to wildcard handlers
    const wildcardHandlers = this.subscribers.get('*') || [];
    wildcardHandlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error('Error in wildcard mock handler:', error);
      }
    });
  }

  subscribe(eventType: string, handler: (message: WebSocketMessage) => void): () => void {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, []);
    }
    this.subscribers.get(eventType)!.push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.subscribers.get(eventType);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  disconnect(): void {
    this.stop();
    this.subscribers.clear();
  }

  // Simulate connection state changes
  getConnectionState(): 'connected' {
    return this.isRunning ? 'connected' : 'disconnected';
  }

  isConnected(): boolean {
    return this.isRunning;
  }

  connect(): void {
    this.start();
  }
}

// Global mock manager instance
let mockManagerInstance: MockWebSocketManager | null = null;

export function getMockWebSocketManager(): MockWebSocketManager {
  if (!mockManagerInstance) {
    mockManagerInstance = new MockWebSocketManager();
  }
  return mockManagerInstance;
}

export function resetMockWebSocketManager(): void {
  if (mockManagerInstance) {
    mockManagerInstance.disconnect();
    mockManagerInstance = null;
  }
}
