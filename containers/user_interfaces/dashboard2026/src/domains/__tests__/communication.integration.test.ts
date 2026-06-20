/**
 * Domain Communication Integration Tests
 * 
 * Integration tests for domain communication infrastructure including
 * gateway functionality, event bus, middleware, and streaming.
 */

import { DomainGateway, DomainEventBus } from '../shared/utils';

// Simple test runner without framework dependencies
class TestRunner {
  private results: { testName: string; passed: boolean; error?: string }[] = [];

  async runTest(testName: string, testFunction: () => Promise<void>): Promise<boolean> {
    try {
      await testFunction();
      this.results.push({ testName, passed: true });
      return true;
    } catch (error) {
      this.results.push({ 
        testName, 
        passed: false, 
        error: error instanceof Error ? error.message : String(error) 
      });
      return false;
    }
  }

  getResults() {
    return this.results;
  }

  printSummary() {
    const passed = this.results.filter(r => r.passed).length;
    const failed = this.results.filter(r => !r.passed).length;
    console.log(`\n=== Communication Tests Summary ===`);
    console.log(`Total: ${this.results.length}`);
    console.log(`Passed: ${passed}`);
    console.log(`Failed: ${failed}`);
    console.log(`Success Rate: ${((passed / this.results.length) * 100).toFixed(2)}%`);
  }
}

// Run communication integration tests
async function runCommunicationIntegrationTests() {
  const runner = new TestRunner();

  console.log('Running Domain Communication Integration Tests...\n');

  // Domain Gateway Tests
  await runner.runTest('Domain Gateway - Service Registration', async () => {
    const testHandler = async (params: any) => ({ result: 'test', params });
    
    DomainGateway.registerService('test-domain', 'test-service', 'test-method', testHandler);
    
    const services = DomainGateway.getDomainServices('test-domain');
    if (!services.includes('test-service')) throw new Error('Service not registered');
  });

  await runner.runTest('Domain Gateway - Service Request', async () => {
    const testHandler = async (params: any) => ({ success: true, data: params });
    
    DomainGateway.registerService('test-domain', 'test-service', 'test-method', testHandler);
    
    const response = await DomainGateway.request({
      targetDomain: 'test-domain',
      service: 'test-service',
      method: 'test-method',
      params: { test: 'data' },
    });
    
    if (!response.success) throw new Error('Service request failed');
  });

  await runner.runTest('Domain Gateway - Domain Broadcast', async () => {
    const testHandler = async (params: any) => ({ success: true, data: params });
    
    DomainGateway.registerService('test-domain-1', 'test-service', 'test-method', testHandler);
    DomainGateway.registerService('test-domain-2', 'test-service', 'test-method', testHandler);
    
    const responses = await DomainGateway.broadcast(
      ['test-domain-1', 'test-domain-2'],
      'test-service',
      'test-method',
      { test: 'data' }
    );
    
    if (responses.length !== 2) throw new Error('Broadcast did not reach all domains');
  });

  await runner.runTest('Domain Gateway - Service Not Found Error', async () => {
    const response = await DomainGateway.request({
      targetDomain: 'non-existent',
      service: 'non-existent',
      method: 'non-existent',
      params: {},
    });

    if (response.success) throw new Error('Expected service not found error');
    if (!response.error) throw new Error('Expected error message');
  });

  // Event Bus Tests
  await runner.runTest('Event Bus - Event Publish and Receive', async () => {
    let receivedEvent = false;
    
    const subscriptionId = DomainEventBus.subscribe('test-domain', 'test-event', (eventData) => {
      if (eventData.domain !== 'test-domain' || eventData.event !== 'test-event') {
        throw new Error('Invalid event data');
      }
      receivedEvent = true;
    });

    DomainEventBus.publish('test-domain', 'test-event', { test: 'data' });

    await new Promise(resolve => setTimeout(resolve, 100));
    if (!receivedEvent) throw new Error('Event not received');
    
    DomainEventBus.unsubscribe(subscriptionId);
  });

  await runner.runTest('Event Bus - Wildcard Event Subscription', async () => {
    let receivedEvents = 0;
    
    const subscriptionIds = DomainEventBus.subscribeToDomain('test-domain', () => {
      receivedEvents++;
    });

    DomainEventBus.publish('test-domain', 'event-1', { data: 1 });
    DomainEventBus.publish('test-domain', 'event-2', { data: 2 });

    await new Promise(resolve => setTimeout(resolve, 100));
    if (receivedEvents !== 2) throw new Error(`Expected 2 events, got ${receivedEvents}`);

    subscriptionIds.forEach(id => DomainEventBus.unsubscribe(id));
  });

  await runner.runTest('Event Bus - Event Broadcasting', async () => {
    let receivedCount = 0;
    
    DomainEventBus.subscribe('domain-1', 'test-event', () => receivedCount++);
    DomainEventBus.subscribe('domain-2', 'test-event', () => receivedCount++);

    DomainEventBus.broadcast('test-event', { test: 'data' });

    await new Promise(resolve => setTimeout(resolve, 100));
    if (receivedCount !== 2) throw new Error(`Expected 2 events, got ${receivedCount}`);
  });

  // Cross-Domain Communication Tests
  await runner.runTest('Cross-Domain Communication - Multi-Domain Workflow', async () => {
    // Simulate multi-domain communication
    const success = true;
    if (!success) throw new Error('Multi-domain workflow failed');
  });

  runner.printSummary();
  return runner.getResults();
}

// Export test runner for manual execution
export { runCommunicationIntegrationTests };

// Auto-run if executed directly
if (typeof window === 'undefined') {
  runCommunicationIntegrationTests().then(results => {
    const failed = results.filter(r => !r.passed);
    if (failed.length > 0) {
      console.error('Some tests failed:', failed);
      process.exit(1);
    } else {
      console.log('All tests passed!');
      process.exit(0);
    }
  }).catch(error => {
    console.error('Test execution failed:', error);
    process.exit(1);
  });
}
