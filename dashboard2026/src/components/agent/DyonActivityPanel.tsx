/**
 * DYON Activity Panel
 * 
 * Displays DYON's current activities and engineering processes
 */

import { Panel, PanelSection, ActivityItem } from './Panel';
import { useDyonActivities } from '@/context/AgentOpsContext';
import type { DyonActivity } from '@/types/agent';
import { Wrench, Cpu, FileCode, TestTube, Database, GitBranch } from 'lucide-react';

interface DyonActivityPanelProps {
  isActive?: boolean;
}

export function DyonActivityPanel({ isActive = false }: DyonActivityPanelProps) {
  const activities = useDyonActivities();

  // Group activities by type
  const refactorActivities = activities.filter(a => 
    a.type === 'refactor-activity' || a.type === 'mutation-candidate'
  );
  const buildActivities = activities.filter(a => 
    a.type === 'build-task' || a.type === 'deployment-task'
  );
  const testingActivities = activities.filter(a => 
    a.type === 'testing-activity' || a.type === 'code-review'
  );
  const analysisActivities = activities.filter(a => 
    a.type === 'repository-analysis' || a.type === 'architecture-work'
  );

  return (
    <Panel
      title="DYON Activities"
      isActive={isActive}
      className="dyon-activity-panel"
    >
      {activities.length === 0 ? (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <div className="text-center">
            <Wrench className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No DYON activities yet</p>
            <p className="text-xs mt-1">Activities will appear here when DYON is working</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Current Status */}
          {activities.length > 0 && activities[0] && (
            <PanelSection title="Current Status">
              <ActivityItem
                title={getActivityTitle(activities[0].type)}
                description={activities[0].context?.repository || 'Repository task'}
                timestamp={activities[0].timestamp}
                status={activities[0].status}
              />
            </PanelSection>
          )}

          {/* Analysis Activities */}
          {analysisActivities.length > 0 && (
            <PanelSection title="Analysis">
              {analysisActivities.slice(0, 3).map(activity => (
                <ActivityItem
                  key={activity.id}
                  title={getActivityTitle(activity.type)}
                  description={activity.context?.repository || 'Code analysis'}
                  timestamp={activity.timestamp}
                  status={activity.status}
                />
              ))}
            </PanelSection>
          )}

          {/* Refactor Activities */}
          {refactorActivities.length > 0 && (
            <PanelSection title="Refactoring">
              {refactorActivities.slice(0, 3).map(activity => (
                <ActivityItem
                  key={activity.id}
                  title={getActivityTitle(activity.type)}
                  description={activity.context?.file || 'Code improvement'}
                  timestamp={activity.timestamp}
                  status={activity.status}
                />
              ))}
            </PanelSection>
          )}

          {/* Build Activities */}
          {buildActivities.length > 0 && (
            <PanelSection title="Build & Deploy">
              {buildActivities.slice(0, 3).map(activity => (
                <ActivityItem
                  key={activity.id}
                  title={getActivityTitle(activity.type)}
                  description="Build process"
                  timestamp={activity.timestamp}
                  status={activity.status}
                />
              ))}
            </PanelSection>
          )}

          {/* Testing Activities */}
          {testingActivities.length > 0 && (
            <PanelSection title="Testing & Review">
              {testingActivities.slice(0, 3).map(activity => (
                <ActivityItem
                  key={activity.id}
                  title={getActivityTitle(activity.type)}
                  description="Quality assurance"
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

function getActivityIcon(type: DyonActivity['type']) {
  switch (type) {
    case 'repository-analysis':
    case 'architecture-work':
      return <Database className="w-4 h-4" />;
    case 'refactor-activity':
    case 'mutation-candidate':
      return <GitBranch className="w-4 h-4" />;
    case 'build-task':
    case 'deployment-task':
      return <Cpu className="w-4 h-4" />;
    case 'testing-activity':
    case 'code-review':
      return <TestTube className="w-4 h-4" />;
    case 'workspace-activity':
      return <FileCode className="w-4 h-4" />;
    default:
      return <Wrench className="w-4 h-4" />;
  }
}

function getActivityTitle(type: DyonActivity['type']): string {
  switch (type) {
    case 'goal-setting':
      return 'Setting Goals';
    case 'task-execution':
      return 'Executing Tasks';
    case 'repository-analysis':
      return 'Repository Analysis';
    case 'mutation-candidate':
      return 'Mutation Candidate';
    case 'refactor-activity':
      return 'Refactoring';
    case 'build-task':
      return 'Building';
    case 'testing-activity':
      return 'Testing';
    case 'code-review':
      return 'Code Review';
    case 'architecture-work':
      return 'Architecture Work';
    case 'infrastructure-task':
      return 'Infrastructure Task';
    case 'debugging-activity':
      return 'Debugging';
    case 'deployment-task':
      return 'Deployment';
    case 'workspace-activity':
      return 'Workspace Activity';
    default:
      return 'Activity';
  }
}
