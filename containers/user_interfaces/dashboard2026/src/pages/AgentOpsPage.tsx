/**
 * Dashboard2026 Agent Operations Center Page
 * 
 * Cognitive Control Center Hub - Real-time observability for INDIRA and DYON
 * 
 * This is the central hub where the Operator can watch agents working in real-time,
 * providing literal observability of cognitive processes as per dashupdate3.txt vision.
 * 
 * Components:
 * - INDIRA Workspace (Current Goal, Task, Research, Trader Modeling, Strategy Work)
 * - DYON Workspace (Current Goal, Repository Task, Mutation, Refactor, Build, Testing)
 * - Shared Components (Assignments, Projects, Task Queue, Agent Timeline, Agent Memory, Activity Feed)
 */

import { useState, useEffect } from 'react';
import { Brain, Wrench, Users, Activity, Clock } from 'lucide-react';
import { Panel, PanelLayout, PanelSection } from '@/components/agent/Panel';
import { SharedToolLayers } from '@/widgets/shared_tools/SharedToolLayers';

interface AgentActivity {
  agent_type: string;
  agent_id: string;
  current_goal: string;
  current_task: string;
  cognitive_process: string;
  tools_in_use: string[];
  memory_accesses: string[];
  timestamp: string;
  current_research?: string;
  current_trader_modeling?: string;
  current_strategy_work?: string;
  current_repository_task?: string;
  current_mutation?: string;
  current_refactor?: string;
  current_build?: string;
  current_testing?: string;
}

interface Assignment {
  assignment_id: string;
  agent_type: string;
  agent_id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
  completed_at?: string;
}

interface TimelineEvent {
  entity_type: string;
  entity_id: string;
  event_type: string;
  timestamp: string;
  data: Record<string, any>;
  workspace?: string;
}

export function AgentOpsPage() {
  const [indiraActivity, setIndiraActivity] = useState<AgentActivity | null>(null);
  const [dyonActivity, setDyonActivity] = useState<AgentActivity | null>(null);
  const [taskQueue, setTaskQueue] = useState<Assignment[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);

  // Fetch real-time agent activities
  useEffect(() => {
    const fetchAgentActivities = async () => {
      try {
        // Fetch INDIRA activity
        const indiraResponse = await fetch('/api/agent-ops/indira/activity');
        if (indiraResponse.ok) {
          setIndiraActivity(await indiraResponse.json());
        }

        // Fetch DYON activity
        const dyonResponse = await fetch('/api/agent-ops/dyon/activity');
        if (dyonResponse.ok) {
          setDyonActivity(await dyonResponse.json());
        }

        // Fetch task queue
        const queueResponse = await fetch('/api/agent-ops/task-queue');
        if (queueResponse.ok) {
          setTaskQueue(await queueResponse.json());
        }

        // Fetch timeline
        const timelineResponse = await fetch('/api/agent-ops/timeline?limit=30');
        if (timelineResponse.ok) {
          setTimeline(await timelineResponse.json());
        }

        // Fetch recent activity
        const activityResponse = await fetch('/api/agent-ops/activity-feed/recent?minutes=5&limit=20');
        if (activityResponse.ok) {
          setRecentActivity(await activityResponse.json());
        }
      } catch (error) {
        console.error('Failed to fetch agent operations data:', error);
      }
    };

    fetchAgentActivities();
    const interval = setInterval(fetchAgentActivities, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="agent-ops-page flex flex-col h-full">
      {/* Header */}
      <div className="agent-ops-header flex items-center justify-between border-b border-border bg-muted/30 px-6 py-4">
        <div className="flex items-center gap-3">
          <Users className="w-6 h-6 text-blue-500" />
          <div>
            <h1 className="text-lg font-semibold">Agent Operations Center</h1>
            <p className="text-xs text-muted-foreground">
              Cognitive Control Center - Real-time agent observability
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded bg-blue-500/10 border border-blue-500/30">
            <Activity className="w-4 h-4 text-blue-500" />
            <span className="text-xs font-medium text-blue-500">Live Updates</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        <PanelLayout columns={2} gap={6}>
          {/* INDIRA Workspace */}
          <Panel>
            <PanelSection title="INDIRA Workspace - Watch INDIRA Working" className="flex-1">
              {indiraActivity ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5 text-purple-500" />
                    <span className="text-sm font-semibold text-purple-500">INDIRA Trading Intelligence</span>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Current Goal</div>
                      <div className="text-sm font-medium">{indiraActivity.current_goal}</div>
                    </div>
                    
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Current Task</div>
                      <div className="text-sm">{indiraActivity.current_task}</div>
                    </div>
                    
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Cognitive Process</div>
                      <div className="text-sm text-blue-400">{indiraActivity.cognitive_process}</div>
                    </div>

                    {indiraActivity.current_research && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Current Research</div>
                        <div className="text-sm">{indiraActivity.current_research}</div>
                      </div>
                    )}

                    {indiraActivity.current_trader_modeling && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Trader Modeling</div>
                        <div className="text-sm">{indiraActivity.current_trader_modeling}</div>
                      </div>
                    )}

                    {indiraActivity.current_strategy_work && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Strategy Work</div>
                        <div className="text-sm">{indiraActivity.current_strategy_work}</div>
                      </div>
                    )}

                    <div className="pt-3 border-t border-border">
                      <div className="text-xs text-muted-foreground mb-2">Tools in Use</div>
                      <div className="flex flex-wrap gap-2">
                        {indiraActivity.tools_in_use.map((tool, idx) => (
                          <span key={idx} className="text-xs px-2 py-1 rounded bg-slate-800 border border-border">
                            {tool}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      <span>Last updated: {new Date(indiraActivity.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">
                  INDIRA is currently inactive or not connected.
                </div>
              )}
            </PanelSection>
          </Panel>

          {/* DYON Workspace */}
          <Panel>
            <PanelSection title="DYON Workspace - Watch DYON Working" className="flex-1">
              {dyonActivity ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 mb-4">
                    <Wrench className="w-5 h-5 text-green-500" />
                    <span className="text-sm font-semibold text-green-500">DYON Engineering Intelligence</span>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Current Goal</div>
                      <div className="text-sm font-medium">{dyonActivity.current_goal}</div>
                    </div>
                    
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Current Task</div>
                      <div className="text-sm">{dyonActivity.current_task}</div>
                    </div>
                    
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Cognitive Process</div>
                      <div className="text-sm text-green-400">{dyonActivity.cognitive_process}</div>
                    </div>

                    {dyonActivity.current_repository_task && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Repository Task</div>
                        <div className="text-sm">{dyonActivity.current_repository_task}</div>
                      </div>
                    )}

                    {dyonActivity.current_refactor && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Refactor</div>
                        <div className="text-sm">{dyonActivity.current_refactor}</div>
                      </div>
                    )}

                    {dyonActivity.current_build && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Build</div>
                        <div className="text-sm">{dyonActivity.current_build}</div>
                      </div>
                    )}

                    {dyonActivity.current_testing && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Testing</div>
                        <div className="text-sm">{dyonActivity.current_testing}</div>
                      </div>
                    )}

                    <div className="pt-3 border-t border-border">
                      <div className="text-xs text-muted-foreground mb-2">Tools in Use</div>
                      <div className="flex flex-wrap gap-2">
                        {dyonActivity.tools_in_use.map((tool, idx) => (
                          <span key={idx} className="text-xs px-2 py-1 rounded bg-slate-800 border border-border">
                            {tool}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      <span>Last updated: {new Date(dyonActivity.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">
                  DYON is currently inactive or not connected.
                </div>
              )}
            </PanelSection>
          </Panel>

          {/* Task Queue */}
          <Panel>
            <PanelSection title="Task Queue" className="flex-1">
              {taskQueue.length > 0 ? (
                <div className="space-y-2 max-h-[300px] overflow-y-auto">
                  {taskQueue.map((task) => (
                    <div key={task.assignment_id} className="p-3 rounded bg-slate-800/50 border border-border">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">{task.title}</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          task.priority === 'critical' ? 'bg-red-500/20 text-red-400' :
                          task.priority === 'high' ? 'bg-orange-500/20 text-orange-400' :
                          task.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-slate-700 text-slate-400'
                        }`}>
                          {task.priority}
                        </span>
                      </div>
                      <div className="text-xs text-muted-foreground">{task.description}</div>
                      <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                        <span>{task.agent_type}</span>
                        <span>•</span>
                        <span>{task.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">No tasks in queue</div>
              )}
            </PanelSection>
          </Panel>

          {/* Recent Activity Feed */}
          <Panel>
            <PanelSection title="Recent Activity Feed" className="flex-1">
              {recentActivity.length > 0 ? (
                <div className="space-y-2 max-h-[300px] overflow-y-auto">
                  {recentActivity.map((activity, idx) => (
                    <div key={idx} className="p-3 rounded bg-slate-800/50 border border-border">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium">{activity.agent_id}</span>
                        <span className="text-xs text-muted-foreground">
                          {new Date(activity.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="text-sm">{activity.description}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">No recent activity</div>
              )}
            </PanelSection>
          </Panel>

          {/* Agent Timeline */}
          <Panel className="col-span-2">
            <PanelSection title="Agent Timeline" className="flex-1">
              {timeline.length > 0 ? (
                <div className="space-y-2 max-h-[200px] overflow-y-auto">
                  {timeline.map((event, idx) => (
                    <div key={idx} className="p-3 rounded bg-slate-800/50 border border-border">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium">{event.entity_id} - {event.event_type}</span>
                        <span className="text-xs text-muted-foreground">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {event.entity_type} {event.workspace ? `• ${event.workspace}` : ''}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">No timeline events</div>
              )}
            </PanelSection>
          </Panel>

          {/* Shared Tool Layers */}
          <Panel className="col-span-2">
            <PanelSection title="Shared Tool Layers" className="flex-1">
              <SharedToolLayers />
            </PanelSection>
          </Panel>
        </PanelLayout>
      </div>
    </div>
  );
}