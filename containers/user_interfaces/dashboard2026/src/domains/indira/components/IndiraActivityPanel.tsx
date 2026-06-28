/**
 * INDIRA Activity Panel
 * 
 * Displays INDIRA's current activities and cognitive processes
 */

import { Panel, PanelSection, ActivityItem } from '@/components/agent/Panel';
import { indiraIntelligenceCoordinator } from '@/core/indira/IndiraIntelligenceCoordinator';
import type { IndiraActivity } from '@/types/agent';
import { Brain } from 'lucide-react';

// Real hook that connects to the actual INDIRA cognitive system
// with enhanced error handling to prevent white screen
const useIndiraActivities = (): IndiraActivity[] => {
  console.log('[IndiraActivityPanel] Getting activities from INDIRA coordinator...');
  
  try {
    // Safe check if coordinator exists
    if (!indiraIntelligenceCoordinator || typeof indiraIntelligenceCoordinator.getMetrics !== 'function') {
      console.warn('[IndiraActivityPanel] INDIRA coordinator not available, using fallback');
      return getFallbackActivities();
    }
    
    const metrics = indiraIntelligenceCoordinator.getMetrics();
    console.log('[IndiraActivityPanel] Got metrics:', metrics);
    
    // Create real activities based on actual system metrics
    const activities: IndiraActivity[] = [
      {
        id: `indira-metrics-${Date.now()}`,
        type: 'portfolio-reasoning',
        timestamp: Date.now(),
        status: metrics.successfulRequests > 0 ? 'active' : 'paused',
        data: {
          totalRequests: metrics.totalRequests,
          coordinationEfficiency: metrics.coordinationEfficiency,
          averageResponseTime: metrics.averageResponseTime
        }
      },
      {
        id: `indira-learning-${Date.now()}`,
        type: 'learning-activity',
        timestamp: Date.now() - 3600000,
        status: 'completed',
        data: {
          deadlocksResolved: metrics.deadlocksResolved,
          priorityViolations: metrics.priorityViolations
        }
      }
    ];
    
    console.log('[IndiraActivityPanel] Created activities:', activities);
    return activities;
  } catch (error) {
    console.error('[IndiraActivityPanel] Failed to get activities from INDIRA coordinator:', error);
    // Return fallback activities to prevent white screen
    return getFallbackActivities();
  }
};

// Fallback activities that don't require INDIRA coordinator
function getFallbackActivities(): IndiraActivity[] {
  return [
    {
      id: `indira-fallback-${Date.now()}`,
      type: 'portfolio-reasoning',
      timestamp: Date.now(),
      status: 'active',
      data: {
        message: 'INDIRA coordinator initializing',
        fallback: true
      }
    }
  ];
}

interface IndiraActivityPanelProps {
  isActive?: boolean;
}

export function IndiraActivityPanel({ isActive = false }: IndiraActivityPanelProps) {
  const activities = useIndiraActivities();

  // Group activities by type
  const researchActivities = activities.filter((a: IndiraActivity) => 
    a.type === 'market-research' || a.type === 'trader-modeling'
  );
  const strategyActivities = activities.filter((a: IndiraActivity) => 
    a.type === 'strategy-creation' || a.type === 'strategy-evolution'
  );
  const reasoningActivities = activities.filter((a: IndiraActivity) => 
    a.type.includes('reasoning') || a.type === 'confidence-analysis'
  );
  const learningActivities = activities.filter((a: IndiraActivity) => 
    a.type === 'learning-activity'
  );

  return (
    <Panel
      title="INDIRA Activities"
      isActive={isActive}
      className="indira-activity-panel"
    >
      {activities.length === 0 ? (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <div className="text-center">
            <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No INDIRA activities yet</p>
            <p className="text-xs mt-1">Activities will appear here when INDIRA is working</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Current Status */}
          {activities.length > 0 && activities[0] && (
            <PanelSection title="Current Status">
              <ActivityItem
                title={getActivityTitle(activities[0].type)}
                description={activities[0].context?.objective || 'Active task'}
                timestamp={activities[0].timestamp}
                status={activities[0].status}
              />
            </PanelSection>
          )}

          {/* Research Activities */}
          {researchActivities.length > 0 && (
            <PanelSection title="Research">
              {researchActivities.slice(0, 3).map((activity: IndiraActivity) => (
                <ActivityItem
                  key={activity.id}
                  title={getActivityTitle(activity.type)}
                  description={activity.context?.market || 'Market analysis'}
                  timestamp={activity.timestamp}
                  status={activity.status}
                />
              ))}
            </PanelSection>
          )}

          {/* Strategy Activities */}
          {strategyActivities.length > 0 && (
            <PanelSection title="Strategy Work">
              {strategyActivities.slice(0, 3).map((activity: IndiraActivity) => (
                <ActivityItem
                  key={activity.id}
                  title={getActivityTitle(activity.type)}
                  description={activity.context?.strategy || 'Strategy development'}
                  timestamp={activity.timestamp}
                  status={activity.status}
                />
              ))}
            </PanelSection>
          )}

          {/* Reasoning Activities */}
          {reasoningActivities.length > 0 && (
            <PanelSection title="Cognitive Process">
              {reasoningActivities.slice(0, 3).map((activity: IndiraActivity) => (
                <ActivityItem
                  key={activity.id}
                  title={getActivityTitle(activity.type)}
                  description="Reasoning in progress"
                  timestamp={activity.timestamp}
                  status={activity.status}
                />
              ))}
            </PanelSection>
          )}

          {/* Learning Activities */}
          {learningActivities.length > 0 && (
            <PanelSection title="Learning">
              {learningActivities.slice(0, 3).map((activity: IndiraActivity) => (
                <ActivityItem
                  key={activity.id}
                  title={getActivityTitle(activity.type)}
                  description="Knowledge acquisition"
                  timestamp={activity.timestamp}
                  status={activity.status}
                />
              ))}
            </PanelSection>
          )}
        </div>
      )}
    </Panel>
  );
}

// ============================================================================
// Helper Functions
// ============================================================================

function getActivityTitle(type: IndiraActivity['type']): string {
  switch (type) {
    case 'goal-setting':
      return 'Setting Objectives';
    case 'task-execution':
      return 'Executing Tasks';
    case 'portfolio-reasoning':
      return 'Portfolio Analysis';
    case 'risk-reasoning':
      return 'Risk Assessment';
    case 'trade-reasoning':
      return 'Trade Analysis';
    case 'confidence-analysis':
      return 'Confidence Evaluation';
    case 'market-research':
      return 'Market Research';
    case 'trader-modeling':
      return 'Trader Modeling';
    case 'strategy-creation':
      return 'Strategy Creation';
    case 'strategy-evolution':
      return 'Strategy Evolution';
    case 'learning-activity':
      return 'Learning Activity';
    case 'browser-session':
      return 'Browser Session';
    default:
      return 'Activity';
  }
}
