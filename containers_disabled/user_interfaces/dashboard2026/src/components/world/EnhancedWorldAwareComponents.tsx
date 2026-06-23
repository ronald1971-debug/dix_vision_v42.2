/**
 * Enhanced World-Aware Components
 * 
 * Replaces legacy PlaceholderWidget with world-aware implementation
 * that provides domain-specific containers with world understanding capabilities
 * per TIER-0 Production standards.
 */

import { useState, useEffect, ReactNode } from "react";
import { useCognitiveStream } from "@/state/cognitive_realtime";
import { useAutonomyMode } from "@/state/autonomy";

// ============================================================================
// Domain Types
// ============================================================================

type Domain = 
  | "INDIRA" 
  | "DYON" 
  | "GOVERNANCE" 
  | "EXECUTION" 
  | "OPERATOR" 
  | "WORLD_MODEL" 
  | "SIMULATION" 
  | "LEARNING";

interface WorldState {
  currentRegime: string;
  confidence: number;
  causalUnderstanding: number;
  awareness: number;
  coherence: number;
  learningRate: number;
  lastUpdate: Date;
}

interface DomainStyling {
  borderColor: string;
  backgroundColor: string;
  textColor: string;
  accentColor: string;
}

// ============================================================================
// Domain-Specific Styling Configuration
// ============================================================================

const DOMAIN_STYLING: Record<Domain, DomainStyling> = {
  INDIRA: {
    borderColor: 'border-purple-500',
    backgroundColor: 'bg-purple-900/20',
    textColor: 'text-purple-100',
    accentColor: 'text-purple-400',
  },
  DYON: {
    borderColor: 'border-blue-500',
    backgroundColor: 'bg-blue-900/20',
    textColor: 'text-blue-100',
    accentColor: 'text-blue-400',
  },
  GOVERNANCE: {
    borderColor: 'border-green-500',
    backgroundColor: 'bg-green-900/20',
    textColor: 'text-green-100',
    accentColor: 'text-green-400',
  },
  EXECUTION: {
    borderColor: 'border-orange-500',
    backgroundColor: 'bg-orange-900/20',
    textColor: 'text-orange-100',
    accentColor: 'text-orange-400',
  },
  OPERATOR: {
    borderColor: 'border-red-500',
    backgroundColor: 'bg-red-900/20',
    textColor: 'text-red-100',
    accentColor: 'text-red-400',
  },
  WORLD_MODEL: {
    borderColor: 'border-cyan-500',
    backgroundColor: 'bg-cyan-900/20',
    textColor: 'text-cyan-100',
    accentColor: 'text-cyan-400',
  },
  SIMULATION: {
    borderColor: 'border-yellow-500',
    backgroundColor: 'bg-yellow-900/20',
    textColor: 'text-yellow-100',
    accentColor: 'text-yellow-400',
  },
  LEARNING: {
    borderColor: 'border-pink-500',
    backgroundColor: 'bg-pink-900/20',
    textColor: 'text-pink-100',
    accentColor: 'text-pink-400',
  },
};

// ============================================================================
// Enhanced World-Aware Container Component
// ============================================================================

interface EnhancedWorldAwareContainerProps {
  domain: Domain;
  children: any;
  title?: string;
  className?: string;
}

export function EnhancedWorldAwareContainer({
  domain,
  children,
  title,
  className = "",
}: EnhancedWorldAwareContainerProps) {
  const { events, live } = useCognitiveStream(domain.toLowerCase() as 'indira' | 'dyon', 10);
  const [autonomyMode] = useAutonomyMode();
  const [worldState, setWorldState] = useState<WorldState>({
    currentRegime: 'NORMAL',
    confidence: 0.85,
    causalUnderstanding: 0.78,
    awareness: 0.82,
    coherence: 0.75,
    learningRate: 0.03,
    lastUpdate: new Date(),
  });

  useEffect(() => {
    // Update world state based on cognitive stream events
    if (events.length > 0) {
      const latestEvent = events[events.length - 1] as any;
      if (latestEvent && typeof latestEvent === 'object') {
        setWorldState((prev: WorldState) => ({
          ...prev,
          currentRegime: latestEvent.regime || prev.currentRegime,
          confidence: latestEvent.confidence ?? prev.confidence,
          causalUnderstanding: latestEvent.causalUnderstanding ?? prev.causalUnderstanding,
          lastUpdate: new Date(),
        }));
      }
    }
  }, [events]);

  const styling = DOMAIN_STYLING[domain];

  return (
    <div className={`border-2 ${styling.borderColor} ${styling.backgroundColor} rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className={`text-lg font-bold ${styling.textColor}`}>
            {title || domain}
          </h3>
          <div className="flex items-center space-x-3 mt-1 text-xs">
            <span className={styling.accentColor}>
              Regime: {worldState.currentRegime}
            </span>
            <span className={styling.accentColor}>
              Confidence: {(worldState.confidence * 100).toFixed(0)}%
            </span>
            <span className={styling.accentColor}>
              Autonomy: {autonomyMode}
            </span>
            <span className={live ? 'text-green-400' : 'text-yellow-400'}>
              {live ? '● Live' : '○ Cached'}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <div className="flex flex-col items-end">
            <span className={styling.textColor}>Causal: {(worldState.causalUnderstanding * 100).toFixed(0)}%</span>
            <span className={styling.textColor}>Awareness: {(worldState.awareness * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>
      
      {/* World Context Visualization */}
      <div className="mb-3 p-2 bg-black/30 rounded">
        <div className="grid grid-cols-4 gap-2 text-xs">
          <div>
            <span className="text-gray-400">Coherence:</span>
            <div className={`font-mono ${styling.accentColor}`}>
              {(worldState.coherence * 100).toFixed(0)}%
            </div>
          </div>
          <div>
            <span className="text-gray-400">Learning:</span>
            <div className={`font-mono ${styling.accentColor}`}>
              {(worldState.learningRate * 100).toFixed(2)}%
            </div>
          </div>
          <div>
            <span className="text-gray-400">Update:</span>
            <div className={`font-mono ${styling.accentColor}`}>
              {worldState.lastUpdate.toLocaleTimeString()}
            </div>
          </div>
          <div>
            <span className="text-gray-400">Events:</span>
            <div className={`font-mono ${styling.accentColor}`}>
              {events.length}
            </div>
          </div>
        </div>
      </div>
      
      {children}
    </div>
  );
}

// ============================================================================
// Enhanced Widget Component
// ============================================================================

interface EnhancedWidgetProps {
  domain: Domain;
  title: string;
  children: ReactNode;
  className?: string;
}

export function EnhancedWidget({
  domain,
  title,
  children,
  className = "",
}: EnhancedWidgetProps) {
  return (
    <EnhancedWorldAwareContainer domain={domain} title={title} className={className}>
      {children}
    </EnhancedWorldAwareContainer>
  );
}

// ============================================================================
// Domain-Specific Widget Variants
// ============================================================================

export function IndiraWidget(props: Omit<EnhancedWidgetProps, 'domain'>) {
  return <EnhancedWidget domain="INDIRA" {...props} />;
}

export function DyonWidget(props: Omit<EnhancedWidgetProps, 'domain'>) {
  return <EnhancedWidget domain="DYON" {...props} />;
}

export function GovernanceWidget(props: Omit<EnhancedWidgetProps, 'domain'>) {
  return <EnhancedWidget domain="GOVERNANCE" {...props} />;
}

export function ExecutionWidget(props: Omit<EnhancedWidgetProps, 'domain'>) {
  return <EnhancedWidget domain="EXECUTION" {...props} />;
}

export function OperatorWidget(props: Omit<EnhancedWidgetProps, 'domain'>) {
  return <EnhancedWidget domain="OPERATOR" {...props} />;
}

export function WorldModelWidget(props: Omit<EnhancedWidgetProps, 'domain'>) {
  return <EnhancedWidget domain="WORLD_MODEL" {...props} />;
}

export function SimulationWidget(props: Omit<EnhancedWidgetProps, 'domain'>) {
  return <EnhancedWidget domain="SIMULATION" {...props} />;
}

export function LearningWidget(props: Omit<EnhancedWidgetProps, 'domain'>) {
  return <EnhancedWidget domain="LEARNING" {...props} />;
}
