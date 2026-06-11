/**
 * INDIRA Workspace Page
 * 
 * Dedicated workspace for INDIRA with coordinated panel layout
 * Provides INDIRA's cognitive operating environment
 * 
 * Layout: 4-panel grid
 * - Context Panel: Objectives, research, models, strategies, opportunities
 * - Cognitive Panel: Portfolio/risk/trade reasoning, confidence analysis
 * - Activity Panel: Research, learning, strategy work, trader modeling
 * - Interaction Panel: Voice, chat, task assignments, quick actions
 */

import { PanelLayout, Panel, PanelSection } from '@/components/agent/Panel';
import { IndiraContextPanel } from '@/components/workspace/IndiraContextPanel';
import { IndiraCognitivePanel } from '@/components/workspace/IndiraCognitivePanel';
import { IndiraActivityPanel } from '@/components/agent/IndiraActivityPanel';
import { Brain, Mic, Users, Activity, FlaskConical, Wifi, WifiOff, TrendingUp } from 'lucide-react';
import { useConnectionState } from '@/context/AgentOpsContext';

interface IndiraWorkspacePageProps {
  // No props currently, but kept for future extension
}

export function IndiraWorkspacePage({}: IndiraWorkspacePageProps) {
  const { connectionState, isConnected, isMockMode } = useConnectionState();

  return (
    <div className="indira-workspace-page flex flex-col h-full">
      {/* Header */}
      <div className="indira-workspace-header flex items-center justify-between border-b border-border bg-muted/30 px-6 py-4">
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-blue-500" />
          <div>
            <h1 className="text-lg font-semibold">INDIRA Workspace</h1>
            <p className="text-xs text-muted-foreground">
              Market intelligence, trader modeling, strategy research, and cognitive processes
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Mock Mode Indicator */}
          {isMockMode && (
            <div className="flex items-center gap-2 px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded">
              <FlaskConical className="w-4 h-4 text-purple-500" />
              <span className="text-xs text-purple-500">MOCK MODE</span>
            </div>
          )}

          {/* Connection Status */}
          <div className="flex items-center gap-2">
            {isConnected ? (
              <Wifi className="w-4 h-4 text-green-500" />
            ) : (
              <WifiOff className="w-4 h-4 text-red-500" />
            )}
            <span className="text-sm text-muted-foreground">
              {getConnectionStatusLabel(connectionState)}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content - 4-Panel Grid */}
      <div className="flex-1 overflow-auto p-6">
        <PanelLayout columns={2} gap={6}>
          {/* Top Row: Context & Cognitive */}
          <IndiraContextPanel />
          <IndiraCognitivePanel />

          {/* Bottom Row: Activity & Interaction */}
          <IndiraActivityPanel />
          <IndiraInteractionPanel />
        </PanelLayout>
      </div>
    </div>
  );
}

// ============================================================================
// INDIRA Interaction Panel
// ============================================================================

function IndiraInteractionPanel() {
  // Mock data for demonstration
  const mockVoiceCommands = [
    {
      id: 'voice-1',
      transcript: 'Analyze Bitcoin market trends for the next week',
      intent: { agent: 'indira', action: 'research', context: { market: 'BTC', timeframe: '7d' } },
      response: 'Initiating comprehensive Bitcoin market analysis for 7-day timeframe',
      confidence: 0.92,
      timestamp: Date.now() - 300000,
    },
    {
      id: 'voice-2',
      transcript: 'Show me current portfolio risk assessment',
      intent: { agent: 'indira', action: 'report', context: { type: 'risk', scope: 'portfolio' } },
      response: 'Current portfolio risk is medium. BTC concentration is above limit at 60%',
      confidence: 0.88,
      timestamp: Date.now() - 900000,
    },
  ];

  const mockChatMessages = [
    {
      id: 'chat-1',
      sender: 'operator',
      content: 'Can you explain the reasoning behind the recent BTC trade?',
      context: { tradeId: 'trade-1' },
      timestamp: Date.now() - 600000,
    },
    {
      id: 'chat-2',
      sender: 'indira',
      content: 'The BTC trade was based on a strong momentum signal detected at $42,500 with 75% confidence. Position size of 2.5 BTC was calculated to limit risk to 2% while targeting 3.8% return.',
      context: { tradeId: 'trade-1', reasoningProcessId: 'trade-reasoning-1' },
      timestamp: Date.now() - 550000,
    },
  ];

  const mockTaskAssignments = [
    {
      id: 'assignment-1',
      taskId: 'task-1',
      assignedTo: 'indira',
      assignedBy: 'operator',
      assignedAt: Date.now() - 1800000,
      status: 'accepted',
      notes: 'Priority: High - Analyze Solana memecoin patterns',
    },
    {
      id: 'assignment-2',
      taskId: 'task-2',
      assignedTo: 'indira',
      assignedBy: 'operator',
      assignedAt: Date.now() - 3600000,
      status: 'active',
      notes: 'Develop new momentum-based trading strategy',
    },
  ];

  const mockQuickActions = [
    {
      id: 'action-1',
      label: 'Generate Portfolio Report',
      action: () => console.log('Generate portfolio report'),
      icon: 'Activity',
      shortcut: '⌘P',
    },
    {
      id: 'action-2',
      label: 'Analyze Market',
      action: () => console.log('Analyze market'),
      icon: 'TrendingUp',
      shortcut: '⌘M',
    },
    {
      id: 'action-3',
      label: 'Research Trader',
      action: () => console.log('Research trader'),
      icon: 'Brain',
      shortcut: '⌘T',
    },
    {
      id: 'action-4',
      label: 'Start Voice Command',
      action: () => console.log('Start voice'),
      icon: 'Mic',
      shortcut: '⌘V',
    },
  ];

  // Helper functions inside the component
  function VoiceCommandItem({ command }: { command: typeof mockVoiceCommands[0] }) {
    return (
      <div className="p-2 bg-muted/30 rounded border border-border">
        <div className="flex items-center gap-2 mb-1">
          <Mic className="w-3 h-3 text-blue-500" />
          <span className="text-xs font-medium">"{command.transcript}"</span>
        </div>
        <p className="text-xs text-muted-foreground mb-1">{command.response}</p>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Confidence: {(command.confidence * 100).toFixed(0)}%</span>
          <span>•</span>
          <span>{getTimeAgo(command.timestamp)}</span>
        </div>
      </div>
    );
  }

  function ChatMessageItem({ message }: { message: typeof mockChatMessages[0] }) {
    const isOperator = message.sender === 'operator';
    
    return (
      <div className={`p-2 rounded border ${
        isOperator 
          ? 'bg-blue-500/10 border-blue-500/20 ml-8' 
          : 'bg-purple-500/10 border-purple-500/20 mr-8'
      }`}>
        <div className="flex items-center gap-2 mb-1">
          {isOperator ? <Users className="w-3 h-3 text-blue-500" /> : <Brain className="w-3 h-3 text-purple-500" />}
          <span className="text-xs font-medium capitalize">{message.sender}</span>
        </div>
        <p className="text-xs">{message.content}</p>
        <p className="text-xs text-muted-foreground mt-1">{getTimeAgo(message.timestamp)}</p>
      </div>
    );
  }

  function TaskAssignmentItem({ assignment }: { assignment: typeof mockTaskAssignments[0] }) {
    return (
      <div className="p-2 bg-muted/30 rounded border border-border">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium">Task: {assignment.taskId}</span>
          <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(assignment.status)}`}>
            {assignment.status}
          </span>
        </div>
        {assignment.notes && (
          <p className="text-xs text-muted-foreground mb-1">{assignment.notes}</p>
        )}
        <p className="text-xs text-muted-foreground">
          Assigned {getTimeAgo(assignment.assignedAt)}
        </p>
      </div>
    );
  }

  function QuickActionItem({ action }: { action: typeof mockQuickActions[0] }) {
    const icons: Record<string, React.ComponentType<{ className?: string }>> = {
      Activity,
      TrendingUp,
      Brain,
      Mic,
    };
    const Icon = icons[action.icon];

    return (
      <button
        onClick={action.action}
        className="p-3 bg-muted/30 rounded border border-border hover:bg-muted/50 transition-colors text-left"
      >
        <div className="flex items-center gap-2 mb-1">
          {Icon && <Icon className="w-4 h-4 text-blue-500" />}
          <span className="text-xs font-medium">{action.label}</span>
        </div>
        {action.shortcut && (
          <span className="text-xs text-muted-foreground">{action.shortcut}</span>
        )}
      </button>
    );
  }

  return (
    <Panel
      title="INDIRA Interaction"
      className="indira-interaction-panel"
    >
      <div className="space-y-4">
        {/* Voice Commands */}
        <PanelSection title="Recent Voice Commands">
          <div className="space-y-2">
            {mockVoiceCommands.map(command => (
              <VoiceCommandItem key={command.id} command={command} />
            ))}
          </div>
        </PanelSection>

        {/* Chat Messages */}
        <PanelSection title="Chat">
          <div className="space-y-2 max-h-40 overflow-auto">
            {mockChatMessages.map(message => (
              <ChatMessageItem key={message.id} message={message} />
            ))}
          </div>
        </PanelSection>

        {/* Task Assignments */}
        <PanelSection title="Task Assignments">
          <div className="space-y-2">
            {mockTaskAssignments.map(assignment => (
              <TaskAssignmentItem key={assignment.id} assignment={assignment} />
            ))}
          </div>
        </PanelSection>

        {/* Quick Actions */}
        <PanelSection title="Quick Actions">
          <div className="grid grid-cols-2 gap-2">
            {mockQuickActions.map(action => (
              <QuickActionItem key={action.id} action={action} />
            ))}
          </div>
        </PanelSection>
      </div>
    </Panel>
  );
}

// ============================================================================
// Helper Functions
// ============================================================================

function getConnectionStatusLabel(state: string): string {
  switch (state) {
    case 'connected':
      return 'Connected';
    case 'connecting':
      return 'Connecting...';
    case 'disconnected':
      return 'Disconnected';
    case 'error':
      return 'Connection Error';
    default:
      return 'Unknown';
  }
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'active':
      return 'bg-blue-500/10 text-blue-500';
    case 'completed':
      return 'bg-green-500/10 text-green-500';
    case 'accepted':
      return 'bg-green-500/10 text-green-500';
    case 'pending':
      return 'bg-yellow-500/10 text-yellow-500';
    case 'error':
      return 'bg-red-500/10 text-red-500';
    default:
      return 'bg-gray-500/10 text-gray-500';
  }
}

function getTimeAgo(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) {
    return 'just now';
  } else if (minutes < 60) {
    return `${minutes}m ago`;
  } else if (hours < 24) {
    return `${hours}h ago`;
  } else {
    return `${days}d ago`;
  }
}
