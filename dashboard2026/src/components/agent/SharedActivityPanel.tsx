/**
 * Shared Activity Panel
 * 
 * Displays shared tasks and assignments across agents
 */

import { Panel, PanelSection, ActivityItem } from './Panel';
import { useSharedTasks } from '@/context/AgentOpsContext';
import type { Task } from '@/types/agent';
import { CheckSquare, Clock, AlertTriangle, Users, Task } from 'lucide-react';

interface SharedActivityPanelProps {
  isActive?: boolean;
}

export function SharedActivityPanel({ isActive = false }: SharedActivityPanelProps) {
  const tasks = useSharedTasks();

  // Group tasks by status
  const activeTasks = tasks.filter(t => t.status === 'active');
  const pendingTasks = tasks.filter(t => t.status === 'pending');
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const blockedTasks = tasks.filter(t => t.status === 'blocked');

  return (
    <Panel
      title="Shared Tasks"
      isActive={isActive}
      className="shared-activity-panel"
    >
      {tasks.length === 0 ? (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <div className="text-center">
            <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No shared tasks yet</p>
            <p className="text-xs mt-1">Tasks will appear here when assigned</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Active Tasks */}
          {activeTasks.length > 0 && (
            <PanelSection title={`Active (${activeTasks.length})`}>
              {activeTasks.slice(0, 3).map(task => (
                <TaskItem key={task.id} task={task} />
              ))}
            </PanelSection>
          )}

          {/* Pending Tasks */}
          {pendingTasks.length > 0 && (
            <PanelSection title={`Pending (${pendingTasks.length})`}>
              {pendingTasks.slice(0, 3).map(task => (
                <TaskItem key={task.id} task={task} />
              ))}
            </PanelSection>
          )}

          {/* Blocked Tasks */}
          {blockedTasks.length > 0 && (
            <PanelSection title={`Blocked (${blockedTasks.length})`}>
              {blockedTasks.slice(0, 3).map(task => (
                <TaskItem key={task.id} task={task} />
              ))}
            </PanelSection>
          )}

          {/* Completed Tasks */}
          {completedTasks.length > 0 && (
            <PanelSection title={`Completed (${completedTasks.length})`}>
              {completedTasks.slice(0, 3).map(task => (
                <TaskItem key={task.id} task={task} />
              ))}
            </PanelSection>
          )}
        </div>
      )}
    </Panel>
  );
}

interface TaskItemProps {
  task: Task;
}

function TaskItem({ task }: TaskItemProps) {
  return (
    <div
      className="task-item flex items-start gap-3 p-3 rounded border border-border bg-muted/30 hover:bg-muted/50 transition-colors"
    >
      <div className="flex-shrink-0">
        {getTaskIcon(task.status)}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{task.title}</p>
        <p className="text-xs text-muted-foreground truncate">{task.description}</p>
        <div className="flex items-center gap-2 mt-1">
          <p className="text-xs text-muted-foreground">
            Assigned to: <span className="font-medium capitalize">{task.assignedTo}</span>
          </p>
          <span className="text-xs text-muted-foreground">•</span>
          <p className="text-xs text-muted-foreground capitalize">
            {getPriorityLabel(task.priority)}
          </p>
        </div>
        {task.progress > 0 && (
          <div className="mt-2">
            <div className="w-full bg-muted rounded-full h-1.5">
              <div
                className="bg-primary h-1.5 rounded-full transition-all"
                style={{ width: `${task.progress}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-1">{task.progress}% complete</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Helper Functions
// ============================================================================

function getTaskIcon(status: Task['status']) {
  switch (status) {
    case 'active':
      return <Clock className="w-4 h-4 text-blue-500" />;
    case 'completed':
      return <CheckSquare className="w-4 h-4 text-green-500" />;
    case 'blocked':
      return <AlertTriangle className="w-4 h-4 text-red-500" />;
    case 'pending':
    default:
      return <Task className="w-4 h-4 text-gray-500" />;
  }
}

function getPriorityLabel(priority: Task['priority']): string {
  switch (priority) {
    case 'critical':
      return 'Critical';
    case 'high':
      return 'High';
    case 'medium':
      return 'Medium';
    case 'low':
      return 'Low';
    default:
      return 'Unknown';
  }
}
