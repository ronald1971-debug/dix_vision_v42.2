/**
 * Domain Integration Test Suite
 * 
 * Tests the integration between domain state management,
 * communication systems, and dependency resolution.
 * 
 * Note: This file demonstrates test patterns for domain integration.
 * To run actual tests, install jest and configure test environment.
 */

// Import domain stores
import { useIndiraStore } from '../../indira/stores/indira-store';
import { useGovernanceStore } from '../../governance/stores/governance-store';
import { useExecutionStore } from '../../execution/stores/execution-store';
import { useOperatorStore } from '../../operator/stores/operator-store';

// Import communication utilities
import { DomainEventBus } from '../utils/event-bus';
import { DomainGateway } from '../utils/domain-gateway';
import { getLoadOrder, validateDependencies } from '../utils/dependency-graph';

// ============================================================================
// Domain Communication Tests
// ============================================================================

console.log('=== Domain Integration Tests ===\n');

// Clear all state before tests
DomainEventBus.clearAllSubscriptions();
DomainGateway.clearRegistry();

// Test 1: Validate domain dependencies
console.log('Test 1: Validating domain dependencies...');
const validation = validateDependencies();
console.log('  Dependencies valid:', validation.valid);
console.log('  Errors:', validation.errors);
console.log('  Warnings:', validation.warnings);

// Test 2: Calculate load order
console.log('\nTest 2: Calculating load order...');
const loadOrder = getLoadOrder();
console.log('  Load order:', loadOrder);
console.log('  Load order length:', loadOrder.length);

// Test 3: Event publishing and subscription
console.log('\nTest 3: Testing event publishing and subscription...');
const receivedEvents: any[] = [];
DomainEventBus.subscribe('indira', 'test-event', (data) => {
  receivedEvents.push(data);
});
DomainEventBus.publish('indira', 'test-event', { message: 'test' });
console.log('  Events received:', receivedEvents.length);
console.log('  Event data:', receivedEvents[0]);

// Test 4: Domain gateway requests
console.log('\nTest 4: Testing domain gateway requests...');
DomainGateway.registerService('test-domain', 'test-service', 'test-method', async (params) => {
  return { success: true, data: params };
});
DomainGateway.request({
  targetDomain: 'test-domain',
  service: 'test-service',
  method: 'test-method',
  params: { test: true },
}).then(response => {
  console.log('  Gateway response success:', response.success);
  console.log('  Gateway response data:', response.data);
});

// ============================================================================
// Domain State Management Tests
// ============================================================================

console.log('\n=== Domain State Management Tests ===\n');

// Test 5: Initialize INDIRA store
console.log('Test 5: Initializing INDIRA store...');
const indiraStore = useIndiraStore.getState();
console.log('  INDIRA store initialized:', !!indiraStore);
console.log('  Market trend:', indiraStore.marketTrend);
console.log('  Cognitive load:', indiraStore.cognitiveLoad);

// Test 6: Update INDIRA market intelligence
console.log('\nTest 6: Updating INDIRA market intelligence...');
indiraStore.setCurrentRegime('bullish');
indiraStore.setMarketData({ trend: 'up', volatility: 0.3 });
const updatedIndiraState = useIndiraStore.getState();
console.log('  Current regime:', updatedIndiraState.currentRegime);
console.log('  Market trend:', updatedIndiraState.marketTrend);
console.log('  Market volatility:', updatedIndiraState.marketVolatility);

// Test 7: Initialize GOVERNANCE store
console.log('\nTest 7: Initializing GOVERNANCE store...');
const governanceStore = useGovernanceStore.getState();
console.log('  GOVERNANCE store initialized:', !!governanceStore);
console.log('  Approval queue length:', governanceStore.approvalQueue.length);
console.log('  Policy violations length:', governanceStore.policyViolations.length);

// Test 8: Manage GOVERNANCE approval queue
console.log('\nTest 8: Managing GOVERNANCE approval queue...');
governanceStore.addApprovalItem({
  id: 'test-approval',
  type: 'strategy',
  status: 'pending',
  requester: 'test-user',
  timestamp: Date.now(),
});
const updatedGovernanceState = useGovernanceStore.getState();
console.log('  Approval queue length:', updatedGovernanceState.approvalQueue.length);
console.log('  Approval item ID:', updatedGovernanceState.approvalQueue[0]?.id);

// Test 9: Initialize EXECUTION store
console.log('\nTest 9: Initializing EXECUTION store...');
const executionStore = useExecutionStore.getState();
console.log('  EXECUTION store initialized:', !!executionStore);
console.log('  Orders length:', executionStore.orders.length);
console.log('  Positions length:', executionStore.positions.length);

// Test 10: Manage EXECUTION orders and positions
console.log('\nTest 10: Managing EXECUTION orders and positions...');
executionStore.addOrder({
  id: 'test-order',
  symbol: 'BTC-USDT',
  side: 'buy',
  type: 'limit',
  quantity: 1,
  price: 50000,
  status: 'pending',
  timestamp: Date.now(),
});
executionStore.addPosition({
  id: 'test-position',
  symbol: 'BTC-USDT',
  quantity: 1,
  entryPrice: 50000,
  currentPrice: 51000,
  unrealizedPnL: 1000,
  side: 'long',
});
const updatedExecutionState = useExecutionStore.getState();
console.log('  Orders length:', updatedExecutionState.orders.length);
console.log('  Positions length:', updatedExecutionState.positions.length);
console.log('  Order ID:', updatedExecutionState.orders[0]?.id);

// Test 11: Initialize OPERATOR store
console.log('\nTest 11: Initializing OPERATOR store...');
const operatorStore = useOperatorStore.getState();
console.log('  OPERATOR store initialized:', !!operatorStore);
console.log('  System active:', operatorStore.systemStatus.isActive);
console.log('  Autonomy mode:', operatorStore.autonomyMode.currentMode);

// Test 12: Manage OPERATOR system controls
console.log('\nTest 12: Managing OPERATOR system controls...');
operatorStore.setAutonomyMode('autonomous');
operatorStore.setSystemActive(false);
const updatedOperatorState = useOperatorStore.getState();
console.log('  Autonomy mode:', updatedOperatorState.autonomyMode.currentMode);
console.log('  System active:', updatedOperatorState.systemStatus.isActive);

// Test 13: Handle kill switch activation
console.log('\nTest 13: Testing kill switch activation...');
operatorStore.triggerKillSwitch('system', 'critical error');
const operatorState = useOperatorStore.getState();
console.log('  Kill switch active:', operatorState.killSwitch.isActive);
console.log('  Triggered by:', operatorState.killSwitch.triggeredBy);
console.log('  Trigger reason:', operatorState.killSwitch.triggerReason);

// ============================================================================
// Cross-Domain Integration Tests
// ============================================================================

console.log('\n=== Cross-Domain Integration Tests ===\n');

// Test 14: Cross-domain state synchronization
console.log('Test 14: Testing cross-domain state synchronization...');
const indiraStore2 = useIndiraStore.getState();
const executionStore2 = useExecutionStore.getState();
indiraStore2.setCurrentRegime('bearish');
executionStore2.setTradingMode('manual');
const indiraState2 = useIndiraStore.getState();
const executionState2 = useExecutionStore.getState();
console.log('  INDIRA regime:', indiraState2.currentRegime);
console.log('  EXECUTION trading mode:', executionState2.tradingStatus.mode);

// Test 15: Governance and execution coordination
console.log('\nTest 15: Testing governance and execution coordination...');
const governanceStore2 = useGovernanceStore.getState();
const executionStore3 = useExecutionStore.getState();
governanceStore2.addApprovalItem({
  id: 'strategy-approval-2',
  type: 'strategy',
  status: 'pending',
  requester: 'trader',
  timestamp: Date.now(),
});
governanceStore2.updateApprovalStatus('strategy-approval-2', 'approved');
executionStore3.setTradingActive(true);
const governanceState2 = useGovernanceStore.getState();
const executionState3 = useExecutionStore.getState();
console.log('  Approval status:', governanceState2.approvalQueue.find(a => a.id === 'strategy-approval-2')?.status);
console.log('  Trading active:', executionState3.tradingStatus.isActive);

// Test 16: Operator domain overrides
console.log('\nTest 16: Testing operator domain overrides...');
const operatorStore2 = useOperatorStore.getState();
operatorStore2.toggleOverride(true);
const operatorState2 = useOperatorStore.getState();
console.log('  Operator override active:', operatorState2.autonomyMode.overrideActive);

console.log('\n=== All Tests Completed ===');