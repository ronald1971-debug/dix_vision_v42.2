# INDIRA Developer Guide

**DIX VISION v42.2 - Phase 8: INDIRA Dashboard Integration & Advanced Features**

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Component Integration](#component-integration)
3. [API Reference](#api-reference)
4. [Testing and Validation](#testing-and-validation)
5. [Customization](#customization)
6. [Performance Optimization](#performance-optimization)
7. [Development Workflow](#development-workflow)

---

## Architecture Overview

### System Architecture
INDIRA follows a modular architecture with three main layers:

#### 1. Core Layer (`src/core/indira/`)
- **IntelligenceCoordinator:** Central coordinator for cross-domain requests
- **CognitiveBrain:** Attention and memory management
- **TradingConsciousness:** Self-awareness and decision tracking
- **MemoryIntegration:** Vector-based memory storage and retrieval
- **LearningAcceleration:** Pattern learning and optimization

#### 2. Domain Intelligence Layer (`src/core/indira/domain-intelligence/`)
- **EnhancedMarketIntelligence:** Market regime detection and prediction
- **EnhancedTraderIntelligence:** Behavioral analysis and coaching
- **EnhancedStrategyIntelligence:** Strategy generation and optimization
- **EnhancedPortfolioIntelligence:** Portfolio optimization and risk management
- **EnhancedResearchIntelligence:** AI research assistant

#### 3. Presentation Layer (`src/components/indira/`)
- **EnhancedIndiraCognitiveCenter:** Main cognitive center dashboard
- **IndiraRealTimeMonitoring:** Real-time system monitoring
- **IndiraAIPoweredFeatures:** AI-powered automation and coordination
- **IndiraMonitoringDashboard:** Legacy monitoring component

### Data Flow
```
User Input → Presentation Layer → Domain Intelligence → Core Layer → Decision Output → User Feedback
```

### Component Communication
- **Synchronous:** Core operations use direct method calls
- **Asynchronous:** AI operations use async/await for non-blocking execution
- **Event-Driven:** Real-time updates use state management and intervals
- **Coordination:** IntelligenceCoordinator manages cross-domain communication

---

## Component Integration

### Adding a New Domain Intelligence Component

1. **Create the Component File**
```typescript
// src/core/indira/domain-intelligence/EnhancedNewDomainIntelligence.ts

export interface NewDomainConfig {
  // Configuration interface
}

export class EnhancedNewDomainIntelligence {
  private instance: EnhancedNewDomainIntelligence;
  private config: NewDomainConfig;
  private state: any;

  private constructor(config: NewDomainConfig) {
    this.config = config;
    this.state = this.initializeState();
  }

  private initializeState(): any {
    // Initialize component state
    return {};
  }

  // Singleton pattern
  public static getInstance(config?: NewDomainConfig): EnhancedNewDomainIntelligence {
    if (!EnhancedNewDomainIntelligence['instance']) {
      EnhancedNewDomainIntelligence['instance'] = new EnhancedNewDomainIntelligence(
        config || {}
      );
    }
    return EnhancedNewDomainIntelligence['instance'];
  }

  // Public API methods
  public async analyze(input: any): Promise<any> {
    // Analysis logic
  }
}

// Singleton export
export const enhancedNewDomainIntelligence = EnhancedNewDomainIntelligence.getInstance();
```

2. **Export from Domain Intelligence Index**
```typescript
// src/core/indira/domain-intelligence/index.ts

export {
  enhancedNewDomainIntelligence,
  EnhancedNewDomainIntelligence,
  NewDomainConfig
} from './EnhancedNewDomainIntelligence';
```

3. **Update INDIRA Index**
```typescript
// src/core/indira/index.ts

export {
  enhancedNewDomainIntelligence,
  EnhancedNewDomainIntelligence,
  NewDomainConfig
} from './domain-intelligence';
```

### Adding a New AI Feature

1. **Define the Feature Interface**
```typescript
interface AIFeature {
  id: string;
  name: string;
  description: string;
  category: 'automation' | 'recommendation' | 'analysis' | 'coordination';
  enabled: boolean;
  status: 'idle' | 'running' | 'completed' | 'failed';
  performance: {
    executions: number;
    successRate: number;
    averageDuration: number;
  };
}
```

2. **Implement the Feature Logic**
```typescript
const runNewFeature = async (featureId: string) => {
  // Set status to running
  setFeatures(prev => prev.map(feature =>
    feature.id === featureId ? { ...feature, status: 'running' } : feature
  ));

  try {
    // Execute feature logic
    const result = await executeNewFeatureLogic();
    
    // Update performance metrics
    // Generate decision
    // Update state
    
  } catch (error) {
    // Handle error
  }
};
```

3. **Add to Features Array**
```typescript
const [features, setFeatures] = useState<AIFeature[]>([
  // ... existing features
  {
    id: 'new_feature',
    name: 'New AI Feature',
    description: 'Description of the new feature',
    category: 'automation',
    status: 'idle',
    enabled: false,
    performance: {
      executions: 0,
      successRate: 0,
      averageDuration: 0
    }
  }
]);
```

---

## API Reference

### Core INDIRA Components

#### IntelligenceCoordinator
```typescript
interface CoordinationRequest {
  requestId: string;
  domains: string[];
  priority: 'low' | 'medium' | 'high' | 'critical';
  context: any;
}

interface CoordinationResponse {
  success: boolean;
  coordinationResult: any;
  timestamp: number;
}

// Methods
indiraIntelligenceCoordinator.processRequest(request: CoordinationRequest): Promise<CoordinationResponse>
```

#### CognitiveBrain
```typescript
interface AttentionSignal {
  type: 'market' | 'trader' | 'strategy' | 'portfolio' | 'research';
  strength: number;
  priority: 'low' | 'medium' | 'high';
  decayRate: number;
  source: string;
}

// Methods
indiraCognitiveBrain.processAttentionSignal(signal: AttentionSignal): AttentionSignal
indiraCognitiveBrain.getCurrentCognitiveLoad(): number
indiraCognitiveBrain.getMetrics(): CognitiveMetrics
```

#### TradingConsciousness
```typescript
interface TradingDecision {
  id: string;
  domain: string;
  action: string;
  confidence: number;
  reasoning: string[];
  context: any;
}

// Methods
indiraTradingConsciousness.recordDecision(decision: TradingDecision): void
indiraTradingConsciousness.generateSelfAssessment(): SelfAssessment
indiraTradingConsciousness.getCurrentConsciousness(): ConsciousnessLevel
```

### Domain Intelligence Components

#### EnhancedMarketIntelligence
```typescript
interface MarketRegime {
  id: string;
  regimeType: 'bullish' | 'bearish' | 'sideways' | 'volatile' | 'crash' | 'recovery';
  confidence: number;
  startTime: number;
  characteristics: {
    trend: 'up' | 'down' | 'flat';
    volatility: 'low' | 'medium' | 'high' | 'extreme';
    volume: 'low' | 'normal' | 'elevated';
    momentum: 'strong' | 'moderate' | 'weak' | 'negative';
  };
  indicators: {
    priceAction: number;
    momentum: number;
    volume: number;
  };
}

// Methods
enhancedMarketIntelligence.analyzeMarketForRegime(marketData: any): Promise<MarketRegime>
enhancedMarketIntelligence.generateMarketPrediction(marketData: any, predictionType: string): Promise<MarketPrediction>
enhancedMarketIntelligence.getTransitionProbabilities(regimeType: string): TransitionProbability[]
```

#### EnhancedTraderIntelligence
```typescript
interface TraderBehavior {
  id: string;
  traderId: string;
  timestamp: number;
  behaviorType: 'entry' | 'exit' | 'adjust' | 'hold' | 'take_profit' | 'stop_loss';
  action: any;
  psychologicalFactors: {
    fear: number;
    greed: number;
    confidence: number;
    patience: number;
    discipline: number;
  };
  decisionTime: number;
  outcome?: any;
}

// Methods
enhancedTraderIntelligence.recordTraderBehavior(behavior: TraderBehavior): void
enhancedTraderIntelligence.getTraderProfile(traderId: string): TraderProfile
enhancedTraderIntelligence.generateBehavioralCoaching(traderId: string, sessionType: string): BehavioralCoaching
```

#### EnhancedStrategyIntelligence
```typescript
interface TradingStrategy {
  id: string;
  name: string;
  type: 'trend_following' | 'mean_reversion' | 'breakout' | 'scalping' | 'arbitrage' | 'news_based';
  parameters: any;
  marketConditions: string[];
  performance: {
    totalReturn: number;
    annualizedReturn: number;
    maxDrawdown: number;
    sharpeRatio: number;
    winRate: number;
  };
}

// Methods
enhancedStrategyIntelligence.generateStrategy(request: StrategyGenerationRequest): Promise<TradingStrategy>
enhancedStrategyIntelligence.optimizeStrategy(strategyId: string): Promise<OptimizationResult>
enhancedStrategyIntelligence.recommendStrategies(marketData: any, traderProfile: any): Promise<StrategyRecommendation>
```

#### EnhancedPortfolioIntelligence
```typescript
interface PortfolioPosition {
  id: string;
  instrument: string;
  quantity: number;
  currentPrice: number;
  currentWeight: number;
  targetWeight: number;
  entryPrice: number;
  unrealizedPnL: number;
  realizedPnL: number;
  riskContribution: number;
  returnContribution: number;
}

// Methods
enhancedPortfolioIntelligence.addPosition(position: PortfolioPosition): void
enhancedPortfolioIntelligence.removePosition(positionId: string): void
enhancedPortfolioIntelligence.optimizePortfolio(constraints: OptimizationConstraints): Promise<OptimizationResult>
enhancedPortfolioIntelligence.getCurrentMetrics(): PortfolioMetrics
```

#### EnhancedResearchIntelligence
```typescript
interface ResearchQuery {
  id: string;
  query: string;
  type: 'market_analysis' | 'pattern_discovery' | 'backtest' | 'correlation_analysis' | 'sentiment_analysis';
  parameters: any;
  timestamp: number;
  status: 'pending' | 'processing' | 'completed';
  priority: 'low' | 'medium' | 'high';
}

// Methods
enhancedResearchIntelligence.submitResearchQuery(query: ResearchQuery): void
enhancedResearchIntelligence.processResearchQuery(query: ResearchQuery): Promise<ResearchResult>
enhancedResearchIntelligence.createResearchSession(queries: ResearchQuery[]): Promise<ResearchSession>
enhancedResearchIntelligence.getAssistantInfo(): AssistantInfo[]
```

---

## Testing and Validation

### Using the Validation Suite

```typescript
import { indiraValidationSuite } from '@/testing/indira/IndiraValidationSuite';

// Run all validation tests
const results = await indiraValidationSuite.runAllValidation();

// Get validation statistics
const stats = indiraValidationSuite.getValidationStats();

// Run specific test
const specificResult = await indiraValidationSuite.runValidation('market_intelligence_test');

// Get all results
const allResults = indiraValidationSuite.getValidationResults();
```

### Creating Custom Tests

```typescript
// Define custom integration test
const customTest: IntegrationTest = {
  id: 'custom_test',
  name: 'Custom Test Name',
  description: 'Test description',
  components: ['Component1', 'Component2'],
  testFunction: async () => {
    const startTime = Date.now();
    
    try {
      // Test logic here
      const result = await performTest();
      
      const duration = Date.now() - startTime;
      
      return {
        name: 'Custom Test',
        status: result.success ? 'pass' : 'fail',
        duration,
        message: result.message,
        details: result
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      return {
        name: 'Custom Test',
        status: 'fail',
        duration,
        message: `Error: ${error}`,
        details: error
      };
    }
  }
};

// Add to validation suite
indiraValidationSuite['integrationTests'].push(customTest);
```

---

## Customization

### Customizing AI Models

Each domain intelligence component maintains model accuracy statistics. To customize:

1. **Access Model Statistics**
```typescript
const stats = enhancedMarketIntelligence.getModelAccuracyStats();
```

2. **Update Model Parameters**
```typescript
// This would require modifying the component to accept custom parameters
enhancedMarketIntelligence.updateModelParameters(customParams);
```

### Customizing Feature Behavior

Modify the feature execution logic in `IndiraAIPoweredFeatures.tsx`:

```typescript
const runCustomFeature = async (featureId: string) => {
  // Custom feature logic
  const result = await customExecutionLogic(featureId);
  
  // Custom decision generation
  const decision = await generateCustomDecision(result);
  
  // Update state
  setRecentDecisions(prev => [decision, ...prev].slice(0, 10));
};
```

### Customizing Dashboard Panels

Modify the panel rendering in `EnhancedIndiraCognitiveCenter.tsx`:

```typescript
const renderCustomPanel = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Custom Panel</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Custom panel content */}
      </CardContent>
    </Card>
  );
};
```

---

## Performance Optimization

### Memory Management

- **Memory Integration:** Uses vector-based storage with automatic cleanup
- **Cognitive Brain:** Manages attention signals with decay to prevent memory leaks
- **Learning Acceleration:** Consolidates patterns to optimize memory usage

### Optimization Strategies

1. **Lazy Loading:** Only load intelligence domains when needed
2. **Caching:** Cache frequently accessed data (regime, profile, metrics)
3. **Batch Processing:** Process multiple requests in batches when possible
4. **Debouncing:** Debounce rapid updates to prevent excessive computation
5. **Web Workers:** Consider using Web Workers for CPU-intensive operations

### Performance Monitoring

Monitor the following metrics:
- Request latency (should be <150ms)
- Throughput (aim for >200 requests/second)
- Error rate (should be <3%)
- Memory usage (keep below 450MB)
- CPU usage (keep below 50%)

---

## Development Workflow

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd dashboard2026
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm run dev
```

4. **Run tests**
```bash
npm run test
```

### Adding New Features

1. **Create feature branch**
```bash
git checkout -b feature/new-indira-feature
```

2. **Implement feature**
- Add component logic
- Add tests
- Update documentation
- Update type definitions

3. **Test locally**
- Run validation suite
- Test in development environment
- Verify TypeScript compilation

4. **Commit and push**
```bash
git add .
git commit -m "Add new INDIRA feature"
git push origin feature/new-indira-feature
```

### Code Style Guidelines

- **TypeScript:** Use strict type checking
- **Interfaces:** Define clear interfaces for all data structures
- **Async/Await:** Use async/await for asynchronous operations
- **Error Handling:** Implement proper error handling with try/catch
- **Comments:** Document complex logic with JSDoc comments
- **Naming:** Use camelCase for variables, PascalCase for types/classes

---

## Support and Resources

### Documentation
- User Guide: `/docs/INDIRA_USER_GUIDE.md`
- This Developer Guide: `/docs/INDIRA_DEVELOPER_GUIDE.md`
- API Reference: See API Reference section above

### Testing
- Validation Suite: `/src/testing/indira/IndiraValidationSuite.ts`
- Component Tests: `/src/components/indira/__tests__/`

### Source Code
- Core INDIRA: `/src/core/indira/`
- Domain Intelligence: `/src/core/indira/domain-intelligence/`
- Presentation Layer: `/src/components/indira/`

---

## Version Information
- **INDIRA Version:** v42.2
- **Phase:** 8 (Weeks 23-24)
- **Last Updated:** Current development cycle
- **TypeScript Version:** 5.x
- **Build Status:** Production Ready