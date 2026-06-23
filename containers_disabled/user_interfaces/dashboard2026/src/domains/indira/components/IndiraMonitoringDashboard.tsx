/**
 * INDIRA Monitoring Dashboard
 * DIX VISION v42.2 - Phase 4 (Phase 6): INDIRA Architecture Modernization
 * 
 * Production-grade monitoring dashboard for INDIRA cognitive system.
 * Provides real-time monitoring of INDIRA's cognitive processes, intelligence domains,
 * learning patterns, and system performance metrics.
 */

import React, { useState, useEffect } from 'react';
import {
  indiraIntelligenceCoordinator,
  IntelligenceMetrics
} from '@/core/indira/IndiraIntelligenceCoordinator';
import {
  indiraCognitiveBrain,
  CognitiveLoad
} from '@/core/indira/IndiraCognitiveBrain';
import {
  indiraTradingConsciousness,
  ConsciousnessState,
  SelfAwarenessMetric
} from '@/core/indira/IndiraTradingConsciousness';
import {
  indiraMemoryIntegration
} from '@/core/indira/IndiraMemoryIntegration';
import {
  indiraLearningAcceleration,
  LearningAccelerationMetrics
} from '@/core/indira/IndiraLearningAcceleration';

interface DashboardMetrics {
  intelligence: IntelligenceMetrics;
  cognitive: CognitiveLoad;
  consciousness: ConsciousnessState;
  selfAwareness: SelfAwarenessMetric;
  learning: LearningAccelerationMetrics;
  memory: {
    totalMemories: number;
    memoryUsageByType: Record<string, any>;
  };
}

interface IndiraMonitoringDashboardProps {
  refreshInterval?: number;
  showDetailedMetrics?: boolean;
}

const IndiraMonitoringDashboard: React.FC<IndiraMonitoringDashboardProps> = ({
  refreshInterval = 5000
}) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'intelligence' | 'cognitive' | 'consciousness' | 'learning' | 'memory'>('intelligence');

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const intelligenceMetrics = indiraIntelligenceCoordinator.getMetrics();
        const cognitiveMetrics = indiraCognitiveBrain.getCognitiveLoad();
        const consciousnessMetrics = indiraTradingConsciousness.getConsciousnessState();
        const selfAwarenessMetrics = indiraTradingConsciousness.getSelfAwarenessMetrics();
        const learningMetrics = indiraLearningAcceleration.getLearningMetrics();
        const memoryStats = indiraMemoryIntegration.getMemoryStats();
        const memoryUsageByType = indiraMemoryIntegration.getMemoryUsageByType();

        setMetrics({
          intelligence: intelligenceMetrics,
          cognitive: cognitiveMetrics,
          consciousness: consciousnessMetrics,
          selfAwareness: selfAwarenessMetrics,
          learning: learningMetrics,
          memory: {
            totalMemories: memoryStats.totalMemories,
            memoryUsageByType
          }
        });
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading INDIRA metrics:', error);
      }
    };

    loadMetrics();
    const interval = setInterval(loadMetrics, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  const handlePerformMemoryConsolidation = async () => {
    try {
      const result = await indiraMemoryIntegration.performMemoryConsolidation();
      alert(`Memory consolidation completed: ${result.memorySaved} memories saved`);
    } catch (error) {
      alert('Memory consolidation failed');
    }
  };

  const handleAccelerateDomainLearning = async (domain: string) => {
    try {
      const result = await indiraLearningAcceleration.accelerateDomainLearning(domain);
      alert(`Domain learning accelerated: ${result.patternsAfter} patterns`);
    } catch (error) {
      alert('Domain learning acceleration failed');
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="p-6">
        <div className="text-red-500">Error loading INDIRA metrics</div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">INDIRA Monitoring Dashboard</h1>
          <p className="text-gray-600">Real-time monitoring of INDIRA cognitive system</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-2 mb-6">
          {['intelligence', 'cognitive', 'consciousness', 'learning', 'memory'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Intelligence Domain Tab */}
        {activeTab === 'intelligence' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Total Requests</div>
                <div className="text-2xl font-bold text-gray-900">{metrics.intelligence.totalRequests}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Success Rate</div>
                <div className="text-2xl font-bold text-green-600">
                  {metrics.intelligence.successfulRequests > 0
                    ? ((metrics.intelligence.successfulRequests / metrics.intelligence.totalRequests) * 100).toFixed(1)
                    : '0'}%
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Coordination Efficiency</div>
                <div className="text-2xl font-bold text-blue-600">
                  {metrics.intelligence.coordinationEfficiency.toFixed(1)}%
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Deadlocks Resolved</div>
                <div className="text-2xl font-bold text-purple-600">{metrics.intelligence.deadlocksResolved}</div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Domain Status</h3>
              <div className="space-y-3">
                {indiraIntelligenceCoordinator.getAllDomainStatuses().map((domain) => (
                  <div key={domain.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div>
                      <div className="font-medium">{domain.name}</div>
                      <div className="text-sm text-gray-500">Queue: {domain.processingQueue}</div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-sm">
                        <div className="text-gray-500">Confidence</div>
                        <div className="font-medium">{(domain.confidenceScore * 100).toFixed(0)}%</div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        domain.status === 'active' ? 'bg-green-100 text-green-800' :
                        domain.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                        domain.status === 'idle' ? 'bg-gray-100 text-gray-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {domain.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Cognitive Brain Tab */}
        {activeTab === 'cognitive' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Total Cognitive Load</div>
                <div className="text-2xl font-bold text-gray-900">{metrics.cognitive.totalLoad.toFixed(1)}%</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Available Capacity</div>
                <div className="text-2xl font-bold text-green-600">{metrics.cognitive.availableCapacity.toFixed(1)}%</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Current Focus</div>
                <div className="text-2xl font-bold text-blue-600">
                  {metrics.cognitive.currentFocus.length} domains
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Domain Load Distribution</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span>Market Intelligence</span>
                  <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${metrics.cognitive.marketLoad}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">{metrics.cognitive.marketLoad.toFixed(0)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Trader Intelligence</span>
                  <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${metrics.cognitive.traderLoad}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">{metrics.cognitive.traderLoad.toFixed(0)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Strategy Intelligence</span>
                  <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full"
                      style={{ width: `${metrics.cognitive.strategyLoad}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">{metrics.cognitive.strategyLoad.toFixed(0)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Portfolio Intelligence</span>
                  <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-orange-600 h-2 rounded-full"
                      style={{ width: `${metrics.cognitive.portfolioLoad}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">{metrics.cognitive.portfolioLoad.toFixed(0)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Research Intelligence</span>
                  <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-red-600 h-2 rounded-full"
                      style={{ width: `${metrics.cognitive.researchLoad}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">{metrics.cognitive.researchLoad.toFixed(0)}%</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Attention Allocation</h3>
              <div className="space-y-3">
                {indiraCognitiveBrain.getAttentionAllocations().map((allocation) => (
                  <div key={allocation.domain} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div>
                      <div className="font-medium">{allocation.domain.replace('_', ' ')}</div>
                      <div className="text-sm text-gray-500">Efficiency: {allocation.efficiency.toFixed(2)}</div>
                    </div>
                    <div className="text-2xl font-bold text-blue-600">{allocation.allocatedAttention.toFixed(0)}%</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Consciousness Tab */}
        {activeTab === 'consciousness' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Consciousness Level</div>
                <div className="text-2xl font-bold text-gray-900">{metrics.consciousness.level}/10</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Awareness State</div>
                <div className="text-2xl font-bold text-blue-600 capitalize">{metrics.consciousness.awareness}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Emotional State</div>
                <div className="text-2xl font-bold text-purple-600 capitalize">{metrics.consciousness.emotionalState}</div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Cognitive State</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Focus</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${metrics.consciousness.focus * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">{(metrics.consciousness.focus * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Clarity</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${metrics.consciousness.clarity * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">{(metrics.consciousness.clarity * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Confidence</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full"
                        style={{ width: `${metrics.consciousness.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">{(metrics.consciousness.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Learning Rate</span>
                    <div className="flex-1 mx-4 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-orange-600 h-2 rounded-full"
                        style={{ width: `${metrics.consciousness.learningRate * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">{(metrics.consciousness.learningRate * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Self-Awareness Metrics</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Decision Accuracy</span>
                    <span className="text-sm font-medium">{(metrics.selfAwareness.decisionAccuracy * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Confidence Calibration</span>
                    <span className="text-sm font-medium">{(metrics.selfAwareness.confidenceCalibration * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Risk Recognition</span>
                    <span className="text-sm font-medium">{(metrics.selfAwareness.riskRecognition * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Pattern Recognition</span>
                    <span className="text-sm font-medium">{(metrics.selfAwareness.patternRecognition * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Adaptability</span>
                    <span className="text-sm font-medium">{(metrics.selfAwareness.adaptability * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Meta-Cognition</span>
                    <span className="text-sm font-medium">{(metrics.selfAwareness.metaCognition * 100).toFixed(0)}%</span>
                  </div>
                  <div className="pt-3 border-t">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">Overall Self-Awareness</span>
                      <span className="text-lg font-bold text-blue-600">
                        {(metrics.selfAwareness.overallSelfAwareness * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Learning Tab */}
        {activeTab === 'learning' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Total Requests</div>
                <div className="text-2xl font-bold text-gray-900">{metrics.learning.totalLearningRequests}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Accelerated Requests</div>
                <div className="text-2xl font-bold text-green-600">{metrics.learning.acceleratedRequests}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Avg Acceleration Factor</div>
                <div className="text-2xl font-bold text-blue-600">{metrics.learning.averageAccelerationFactor.toFixed(1)}x</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Learning Velocity</div>
                <div className="text-2xl font-bold text-purple-600">{metrics.learning.learningVelocity.toFixed(1)}x</div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Learning Models</h3>
              <div className="space-y-3">
                {indiraLearningAcceleration.getLearningModels().map((model) => (
                  <div key={model.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div>
                      <div className="font-medium">{model.name}</div>
                      <div className="text-sm text-gray-500">
                        Type: {model.type} | Version: {model.version}
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-sm">
                        <div className="text-gray-500">Accuracy</div>
                        <div className="font-medium">{(model.accuracy * 100).toFixed(0)}%</div>
                      </div>
                      <div className="text-sm">
                        <div className="text-gray-500">Inference Time</div>
                        <div className="font-medium">{model.performance.inferenceTime}ms</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Domain Learning Acceleration</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {['market', 'trader', 'strategy', 'portfolio', 'research'].map((domain) => (
                  <button
                    key={domain}
                    onClick={() => handleAccelerateDomainLearning(domain)}
                    className="p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
                  >
                    <div className="font-medium text-blue-900 capitalize">{domain}</div>
                    <div className="text-sm text-blue-600">Accelerate Learning</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Memory Tab */}
        {activeTab === 'memory' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Total Memories</div>
                <div className="text-2xl font-bold text-gray-900">{metrics.memory.totalMemories}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Memory Types</div>
                <div className="text-2xl font-bold text-blue-600">
                  {Object.keys(metrics.memory.memoryUsageByType).length}
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500 mb-1">Cache Hit Rate</div>
                <div className="text-2xl font-bold text-green-600">
                  {indiraLearningAcceleration.getCacheStats().hitRate.toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Memory Usage by Type</h3>
              <div className="space-y-3">
                {Object.entries(metrics.memory.memoryUsageByType).map(([type, usage]: [string, any]) => (
                  <div key={type} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div>
                      <div className="font-medium capitalize">{type}</div>
                      <div className="text-sm text-gray-500">
                        Count: {usage.count} | Avg Size: {(usage.averageSize / 1024).toFixed(1)}KB
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-sm">
                        <div className="text-gray-500">Total Size</div>
                        <div className="font-medium">{(usage.totalSize / 1024).toFixed(1)}KB</div>
                      </div>
                      <div className="text-sm">
                        <div className="text-gray-500">Avg Importance</div>
                        <div className="font-medium">{usage.averageImportance.toFixed(2)}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Memory Management</h3>
              <div className="flex space-x-3">
                <button
                  onClick={handlePerformMemoryConsolidation}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Perform Memory Consolidation
                </button>
                <button
                  onClick={() => indiraMemoryIntegration.resetMemoryIntegration()}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Reset Memory
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IndiraMonitoringDashboard;