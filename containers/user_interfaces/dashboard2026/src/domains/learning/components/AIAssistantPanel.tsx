/**
 * Dashboard2026 AI Assistant Panel
 * DIX VISION v42.2 - Phase: AI Intelligence Enhancement
 * 
 * Context-aware AI assistant panel that provides intelligent assistance,
 * recommendations, and predictions across all dashboard pages.
 */

import { useState, useEffect } from 'react';
import { getAIOrchestrator, type AIRecommendation, type AIPrediction, type AIAssistant } from '@/core/ai';
import { Sparkles, Brain, TrendingUp, AlertTriangle, Zap, ChevronDown, ChevronUp, X, CheckCircle, Lightbulb } from 'lucide-react';

interface AIAssistantPanelProps {
  currentPage: string;
  activeData?: any;
  onAction?: (action: string) => void;
}

export function AIAssistantPanel({ currentPage, activeData, onAction }: AIAssistantPanelProps) {
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [predictions, setPredictions] = useState<AIPrediction[]>([]);
  const [assistants, setAssistants] = useState<AIAssistant[]>([]);
  const [isExpanded, setIsExpanded] = useState(true);
  const [selectedTab, setSelectedTab] = useState<'recommendations' | 'predictions' | 'assistants'>('recommendations');
  const [isLoading, setIsLoading] = useState(false);

  const orchestrator = getAIOrchestrator();

  useEffect(() => {
    updateAIContext();
    loadAIInsights();
    
    // Refresh insights every 30 seconds
    const interval = setInterval(loadAIInsights, 30000);
    
    return () => clearInterval(interval);
  }, [currentPage, activeData]);

  const updateAIContext = () => {
    orchestrator.updateContext({
      currentPage,
      activeData,
      userIntent: ''
    });
  };

  const loadAIInsights = async () => {
    setIsLoading(true);
    try {
      const recs = await orchestrator.generateRecommendations();
      const preds = orchestrator.getPredictions();
      const assts = orchestrator.getAssistantStatus();
      
      setRecommendations(recs);
      setPredictions(preds);
      setAssistants(assts);
    } catch (error) {
      console.error('Failed to load AI insights:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecommendationAction = (recommendation: AIRecommendation) => {
    if (recommendation.suggestedAction && onAction) {
      onAction(recommendation.suggestedAction);
      
      // Learn from user action
      orchestrator.learnFromAction(`accepted_${recommendation.type}`, { recommendation });
    }
  };

  const handleDismissRecommendation = (recommendationId: string) => {
    setRecommendations(prev => prev.filter(r => r.id !== recommendationId));
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-400 bg-red-400/10 border-red-400/30';
      case 'high': return 'text-orange-400 bg-orange-400/10 border-orange-400/30';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30';
      case 'low': return 'text-blue-400 bg-blue-400/10 border-blue-400/30';
      default: return 'text-slate-400 bg-slate-400/10 border-slate-400/30';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'action': return <Zap className="w-4 h-4" />;
      case 'insight': return <Lightbulb className="w-4 h-4" />;
      case 'warning': return <AlertTriangle className="w-4 h-4" />;
      case 'optimization': return <TrendingUp className="w-4 h-4" />;
      default: return <Brain className="w-4 h-4" />;
    }
  };

  if (!isExpanded) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsExpanded(true)}
          className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white p-3 rounded-full shadow-lg transition-all"
        >
          <Sparkles className="w-6 h-6" />
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 max-h-[600px] bg-slate-900 border border-slate-700 rounded-lg shadow-2xl flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 border-b border-slate-700 p-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <h3 className="font-semibold text-white">AI Assistant</h3>
          </div>
          <div className="flex items-center gap-2">
            {isLoading && <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />}
            <button
              onClick={() => setIsExpanded(false)}
              className="text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mt-3">
          <button
            onClick={() => setSelectedTab('recommendations')}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              selectedTab === 'recommendations'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Recommendations ({recommendations.length})
          </button>
          <button
            onClick={() => setSelectedTab('predictions')}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              selectedTab === 'predictions'
                ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Predictions ({predictions.length})
          </button>
          <button
            onClick={() => setSelectedTab('assistants')}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              selectedTab === 'assistants'
                ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Assistants ({assistants.length})
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 space-y-3">
        {selectedTab === 'recommendations' && (
          <>
            {recommendations.length === 0 ? (
              <div className="text-center text-slate-500 text-sm py-8">
                <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No recommendations at this time</p>
              </div>
            ) : (
              recommendations.map(recommendation => (
                <RecommendationCard
                  key={recommendation.id}
                  recommendation={recommendation}
                  onAction={() => handleRecommendationAction(recommendation)}
                  onDismiss={() => handleDismissRecommendation(recommendation.id)}
                  getPriorityColor={getPriorityColor}
                  getTypeIcon={getTypeIcon}
                />
              ))
            )}
          </>
        )}

        {selectedTab === 'predictions' && (
          <>
            {predictions.length === 0 ? (
              <div className="text-center text-slate-500 text-sm py-8">
                <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No predictions available</p>
              </div>
            ) : (
              predictions.map(prediction => (
                <PredictionCard key={prediction.id} prediction={prediction} />
              ))
            )}
          </>
        )}

        {selectedTab === 'assistants' && (
          <>
            {assistants.length === 0 ? (
              <div className="text-center text-slate-500 text-sm py-8">
                <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No AI assistants active</p>
              </div>
            ) : (
              assistants.map(assistant => (
                <AssistantCard key={assistant.id} assistant={assistant} />
              ))
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-slate-700 p-3 bg-slate-800/50">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>AI Intelligence Active</span>
          <span className="flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-green-400" />
            Operational
          </span>
        </div>
      </div>
    </div>
  );
}

function RecommendationCard({ 
  recommendation, 
  onAction, 
  onDismiss, 
  getPriorityColor, 
  getTypeIcon 
}: { 
  recommendation: AIRecommendation; 
  onAction: () => void; 
  onDismiss: () => void;
  getPriorityColor: (priority: string) => string;
  getTypeIcon: (type: string) => React.ReactNode;
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`p-3 border rounded-lg ${getPriorityColor(recommendation.priority)}`}>
      <div className="flex items-start gap-3">
        <div className="mt-0.5">{getTypeIcon(recommendation.type)}</div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <h4 className="font-medium text-white text-sm">{recommendation.title}</h4>
            <button
              onClick={onDismiss}
              className="text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
          <p className="text-xs text-slate-300 mb-2">{recommendation.description}</p>
          
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs">Confidence: {(recommendation.confidence * 100).toFixed(0)}%</span>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1"
            >
              {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              Details
            </button>
          </div>

          {isExpanded && (
            <div className="space-y-2 mt-2 text-xs border-t border-current/10 pt-2">
              <div>
                <span className="font-medium">Reasoning:</span>
                <ul className="list-disc list-inside mt-1 text-slate-400">
                  {recommendation.reasoning.map((reason, idx) => (
                    <li key={idx}>{reason}</li>
                  ))}
                </ul>
              </div>
              <div>
                <span className="font-medium">Impact:</span>
                <div className="mt-1">
                  <span className="text-slate-400">Expected: {recommendation.impact.expected}</span>
                  <span className="ml-2 text-slate-400">Risk: {recommendation.impact.risk}</span>
                </div>
              </div>
            </div>
          )}

          {recommendation.suggestedAction && (
            <button
              onClick={onAction}
              className="mt-2 w-full py-1.5 bg-current/10 hover:bg-current/20 rounded text-xs font-medium transition-colors"
            >
              Take Action
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function PredictionCard({ prediction }: { prediction: AIPrediction }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="p-3 bg-slate-800 border border-slate-700 rounded-lg">
      <div className="flex items-start gap-3">
        <Brain className="w-4 h-4 text-blue-400 mt-0.5" />
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <h4 className="font-medium text-white text-sm capitalize">{prediction.category} Prediction</h4>
            <span className="text-xs text-slate-400">{(prediction.confidence * 100).toFixed(0)}%</span>
          </div>
          <p className="text-xs text-slate-300 mb-2">{prediction.prediction}</p>
          
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs text-slate-500">Timeframe: {prediction.timeframe}</span>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1"
            >
              {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              Details
            </button>
          </div>

          {isExpanded && (
            <div className="space-y-2 mt-2 text-xs border-t border-slate-700 pt-2">
              <div>
                <span className="font-medium text-slate-300">Factors:</span>
                <ul className="list-disc list-inside mt-1 text-slate-400">
                  {prediction.factors.map((factor, idx) => (
                    <li key={idx}>{factor}</li>
                  ))}
                </ul>
              </div>
              <div>
                <span className="font-medium text-slate-300">Recommended Actions:</span>
                <ul className="list-disc list-inside mt-1 text-slate-400">
                  {prediction.recommendedActions.map((action, idx) => (
                    <li key={idx}>{action}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function AssistantCard({ assistant }: { assistant: AIAssistant }) {
  return (
    <div className="p-3 bg-slate-800 border border-slate-700 rounded-lg">
      <div className="flex items-center gap-3 mb-2">
        <Brain className="w-4 h-4 text-green-400" />
        <div className="flex-1">
          <h4 className="font-medium text-white text-sm">{assistant.name}</h4>
          <span className="text-xs text-slate-400 capitalize">{assistant.type}</span>
        </div>
        <div className={`px-2 py-0.5 rounded text-xs ${
          assistant.status === 'active' ? 'bg-green-500/20 text-green-400' :
          assistant.status === 'processing' ? 'bg-yellow-500/20 text-yellow-400' :
          'bg-slate-500/20 text-slate-400'
        }`}>
          {assistant.status}
        </div>
      </div>
      
      <div className="space-y-1">
        <div className="text-xs text-slate-400">
          <span className="font-medium">Confidence:</span> {(assistant.confidence * 100).toFixed(0)}%
        </div>
        <div className="text-xs text-slate-400">
          <span className="font-medium">Capabilities:</span>
        </div>
        <div className="flex flex-wrap gap-1">
          {assistant.capabilities.slice(0, 3).map((capability, idx) => (
            <span key={idx} className="px-1.5 py-0.5 bg-slate-700 rounded text-xs text-slate-300">
              {capability}
            </span>
          ))}
          {assistant.capabilities.length > 3 && (
            <span className="text-xs text-slate-500">+{assistant.capabilities.length - 3} more</span>
          )}
        </div>
      </div>
    </div>
  );
}