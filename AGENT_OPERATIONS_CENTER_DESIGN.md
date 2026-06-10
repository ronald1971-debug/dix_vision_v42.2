# Agent Operations Center Design

**Version:** v42.2  
**Date:** 2026-06-10  
**Status:** Design Specification  
**Priority:** 🔴 CRITICAL (Phase 1 Foundation)

---

## Overview

The Agent Operations Center is the **foundational component** for transforming Dashboard2026 from a traditional UI into a cognitive operating environment. It provides real-time visibility into agent activities, unified task management, and central coordination for Operator, INDIRA, and DYON.

**Philosophy:** "Watch the agents work" - Real-time transparency into cognitive processes

---

## Architecture

### Component Hierarchy

```
Agent Operations Center
├── Layout Layer
│   ├── AgentOpsPage (Main Container)
│   ├── PanelLayout (Grid System)
│   └── ResponsiveBreakpoints
├── Agent Panels
│   ├── IndiraActivityPanel
│   ├── DyonActivityPanel
│   └── SharedActivityPanel
├── Feed Components
│   ├── GlobalEventFeed
│   ├── ActivityTimeline
│   └── EventFilters
├── Task Components
│   ├── TaskQueue
│   ├── AssignmentPanel
│   └── ProjectBoard
├── Interaction Components
│   ├── VoiceCommandPanel
│   ├── ChatInterface
│   └── CommandPalette
└── Infrastructure
    ├── WebSocket Manager
    ├── Event Processor
    ├── State Manager
    └── Performance Monitor
```

---

## Detailed Component Design

### 1. AgentOpsPage (Main Container)

**File:** `src/pages/AgentOpsPage.tsx`

**Responsibilities:**
- Main layout container
- WebSocket connection management
- Global state coordination
- Responsive layout control

**Props:** None (uses context/hooks)

**State:**
```typescript
interface AgentOpsState {
  websocketConnected: boolean;
  activePanel: 'indira' | 'dyon' | 'shared' | 'global';
  eventFilters: EventFilter[];
  viewMode: 'grid' | 'list' | 'timeline';
  refreshRate: number;
}
```

**Component Structure:**
```typescript
export function AgentOpsPage() {
  const [state, setState] = useState<AgentOpsState>({
    websocketConnected: false,
    activePanel: 'indira',
    eventFilters: [],
    viewMode: 'grid',
    refreshRate: 1000,
  });

  const { websocket, events } = useAgentWebSocket();
  const { indiraActivities, dyonActivities, sharedTasks } = useAgentData();

  return (
    <div className="agent-ops-page">
      <AgentOpsHeader 
        connectionStatus={websocket.connected}
        activePanel={state.activePanel}
        onPanelChange={(panel) => setState({...state, activePanel: panel})}
      />
      
      <PanelLayout viewMode={state.viewMode}>
        <IndiraActivityPanel 
          activities={indiraActivities}
          isActive={state.activePanel === 'indira'}
        />
        <DyonActivityPanel 
          activities={dyonActivities}
          isActive={state.activePanel === 'dyon'}
        />
        <SharedActivityPanel 
          tasks={sharedTasks}
          isActive={state.activePanel === 'shared'}
        />
        <GlobalEventFeed 
          events={events}
          filters={state.eventFilters}
        />
      </PanelLayout>
      
      <AgentOpsFooter 
        viewMode={state.viewMode}
        onViewModeChange={(mode) => setState({...state, viewMode: mode})}
      />
    </div>
  );
}
```

---

### 2. IndiraActivityPanel

**File:** `src/components/agent/IndiraActivityPanel.tsx`

**Responsibilities:**
- Display INDIRA's current activities
- Show cognitive process visualization
- Provide real-time activity feed
- Enable operator interaction

**Sub-Components:**
```
IndiraActivityPanel
├── IndiraContextHeader
│   ├── CurrentGoal
│   ├── CurrentTask
│   ├── AgentStatus
│   └── ActiveMode
├── CognitiveProcessView
│   ├── PortfolioReasoning
│   ├── RiskReasoning
│   ├── TradeReasoning
│   └── ConfidenceAnalysis
├── ActivityFeed
│   ├── ResearchActivities
│   ├── LearningActivities
│   ├── StrategyActivities
│   └── TraderModelingActivities
├── BrowserSessionView
│   ├── ActiveTabs
│   ├── NavigationHistory
│   ├── ResearchContext
│   └── SessionRecording
└── InteractionPanel
    ├── VoiceCommands
    ├── ChatInterface
    └── TaskAssignments
```

**Component Structure:**
```typescript
interface IndiraActivityPanelProps {
  activities: IndiraActivity[];
  isActive: boolean;
}

export function IndiraActivityPanel({ activities, isActive }: IndiraActivityPanelProps) {
  const currentGoal = useCurrentIndiraGoal();
  const currentTask = useCurrentIndiraTask();
  const browserSession = useIndiraBrowserSession();

  return (
    <Panel className={isActive ? 'active' : ''}>
      <IndiraContextHeader
        goal={currentGoal}
        task={currentTask}
        status={activities[0]?.status}
      />
      
      <CognitiveProcessView
        portfolioReasoning={activities.filter(a => a.type === 'portfolio-reasoning')}
        riskReasoning={activities.filter(a => a.type === 'risk-reasoning')}
        tradeReasoning={activities.filter(a => a.type === 'trade-reasoning')}
      />
      
      <ActivityFeed
        activities={activities.filter(a => a.type !== 'reasoning')}
        agent="indira"
      />
      
      <BrowserSessionView
        session={browserSession}
        onTabSelect={(tab) => handleTabSelect(tab)}
      />
      
      <InteractionPanel agent="indira" />
    </Panel>
  );
}
```

**Activity Types:**
```typescript
type IndiraActivityType =
  | 'goal-setting'
  | 'task-execution'
  | 'portfolio-reasoning'
  | 'risk-reasoning'
  | 'trade-reasoning'
  | 'confidence-analysis'
  | 'market-research'
  | 'trader-modeling'
  | 'strategy-creation'
  | 'strategy-evolution'
  | 'learning-activity'
  | 'browser-session';

interface IndiraActivity {
  id: string;
  type: IndiraActivityType;
  timestamp: number;
  status: 'active' | 'completed' | 'paused' | 'error';
  data: unknown;
  context?: {
    objective?: string;
    strategy?: string;
    market?: string;
    trader?: string;
  };
}
```

---

### 3. DyonActivityPanel

**File:** `src/components/agent/DyonActivityPanel.tsx`

**Responsibilities:**
- Display DYON's current activities
- Show engineering process visualization
- Provide real-time activity feed
- Enable operator interaction

**Sub-Components:**
```
DyonActivityPanel
├── DyonContextHeader
│   ├── CurrentGoal
│   ├── CurrentTask
│   ├── AgentStatus
│   └── ActiveRepository
├── EngineeringProcessView
│   ├── RepositoryAnalysis
│   ├── CodeReviewActivities
│   ├── ArchitectureWork
│   └── InfrastructureTasks
├── ActivityFeed
│   ├── MutationActivities
│   ├── RefactorActivities
│   ├── BuildActivities
│   └── TestingActivities
├── WorkspaceView
│   ├── ActiveFiles
│   ├── TerminalSessions
│   ├── DebugActivities
│   └── DeploymentTasks
└── InteractionPanel
    ├── VoiceCommands
    ├── ChatInterface
    └── TaskAssignments
```

**Component Structure:**
```typescript
interface DyonActivityPanelProps {
  activities: DyonActivity[];
  isActive: boolean;
}

export function DyonActivityPanel({ activities, isActive }: DyonActivityPanelProps) {
  const currentGoal = useCurrentDyonGoal();
  const currentTask = useCurrentDyonTask();
  const workspace = useDyonWorkspace();

  return (
    <Panel className={isActive ? 'active' : ''}>
      <DyonContextHeader
        goal={currentGoal}
        task={currentTask}
        status={activities[0]?.status}
        repository={workspace.repository}
      />
      
      <EngineeringProcessView
        repositoryAnalysis={activities.filter(a => a.type === 'repository-analysis')}
        codeReview={activities.filter(a => a.type === 'code-review')}
        architecture={activities.filter(a => a.type === 'architecture-work')}
      />
      
      <ActivityFeed
        activities={activities.filter(a => !['repository-analysis', 'code-review', 'architecture-work'].includes(a.type))}
        agent="dyon"
      />
      
      <WorkspaceView
        workspace={workspace}
        onFileSelect={(file) => handleFileSelect(file)}
      />
      
      <InteractionPanel agent="dyon" />
    </Panel>
  );
}
```

**Activity Types:**
```typescript
type DyonActivityType =
  | 'goal-setting'
  | 'task-execution'
  | 'repository-analysis'
  | 'mutation-candidate'
  | 'refactor-activity'
  | 'build-task'
  | 'testing-activity'
  | 'code-review'
  | 'architecture-work'
  | 'infrastructure-task'
  | 'debugging-activity'
  | 'deployment-task'
  | 'workspace-activity';

interface DyonActivity {
  id: string;
  type: DyonActivityType;
  timestamp: number;
  status: 'active' | 'completed' | 'paused' | 'error';
  data: unknown;
  context?: {
    repository?: string;
    file?: string;
    module?: string;
    project?: string;
  };
}
```

---

### 4. SharedActivityPanel

**File:** `src/components/agent/SharedActivityPanel.tsx`

**Responsibilities:**
- Display shared tasks and assignments
- Show project coordination
- Provide task management interface
- Enable cross-agent collaboration

**Sub-Components:**
```
SharedActivityPanel
├── TaskQueue
│   ├── PendingTasks
│   ├── ActiveTasks
│   ├── CompletedTasks
│   └── BlockedTasks
├── AssignmentBoard
│   ├── IndiraAssignments
│   ├── DyonAssignments
│   ├── OperatorAssignments
│   └── SharedAssignments
├── ProjectBoard
│   ├── ActiveProjects
│   ├── ProjectProgress
│   ├── MilestoneTracking
│   └── ResourceAllocation
├── CollaborationView
│   ├── AgentCoordination
│   ├── TaskDependencies
│   ├── SharedResources
│   └── CommunicationLog
└── ManagementTools
    ├── TaskCreation
    ├── AssignmentWorkflow
    ├── PriorityManagement
    └── DeadlineTracking
```

**Component Structure:**
```typescript
interface SharedActivityPanelProps {
  tasks: Task[];
  isActive: boolean;
}

export function SharedActivityPanel({ tasks, isActive }: SharedActivityPanelProps) {
  const { projects, assignments } = useSharedTaskSystem();

  return (
    <Panel className={isActive ? 'active' : ''}>
      <TaskQueue
        tasks={tasks}
        onTaskUpdate={(task) => handleTaskUpdate(task)}
      />
      
      <AssignmentBoard
        assignments={assignments}
        onAssignmentChange={(assignment) => handleAssignmentChange(assignment)}
      />
      
      <ProjectBoard
        projects={projects}
        onProjectUpdate={(project) => handleProjectUpdate(project)}
      />
      
      <CollaborationView
        tasks={tasks}
        assignments={assignments}
      />
      
      <ManagementTools
        onTaskCreate={(task) => handleTaskCreate(task)}
        onAssignmentCreate={(assignment) => handleAssignmentCreate(assignment)}
      />
    </Panel>
  );
}
```

**Task System Data Model:**
```typescript
interface Task {
  id: string;
  title: string;
  description: string;
  type: 'research' | 'engineering' | 'trading' | 'analysis' | 'general';
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'pending' | 'active' | 'completed' | 'blocked' | 'cancelled';
  assignedTo: 'indira' | 'dyon' | 'operator' | 'shared';
  createdBy: string;
  createdAt: number;
  deadline?: number;
  dependencies: string[];
  subtasks: SubTask[];
  progress: number;
  context?: {
    project?: string;
    objective?: string;
    relatedTasks?: string[];
  };
}

interface Assignment {
  id: string;
  taskId: string;
  assignedTo: 'indira' | 'dyon' | 'operator';
  assignedBy: string;
  assignedAt: number;
  status: 'accepted' | 'declined' | 'pending';
  notes?: string;
}

interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'paused';
  tasks: string[];
  milestones: Milestone[];
  createdAt: number;
  deadline?: number;
  progress: number;
}
```

---

### 5. GlobalEventFeed

**File:** `src/components/agent/GlobalEventFeed.tsx`

**Responsibilities:**
- Display global system events
- Provide filtering and search
- Show event timeline
- Enable event replay

**Sub-Components:**
```
GlobalEventFeed
├── FeedHeader
│   ├── EventCount
│   ├── FilterControls
│   ├── SearchBox
│   └── ViewOptions
├── EventStream
│   ├── SystemEvents
│   ├── MarketEvents
│   ├── TradeEvents
│   ├── LearningEvents
│   ├── GovernanceEvents
│   ├── DyonEvents
│   ├── IndiraEvents
│   ├── DesktopEvents
│   └── BrowserEvents
├── EventTimeline
│   ├── TimeScale
│   ├── EventMarkers
│   ├── TimeNavigation
│   └── PlaybackControls
└── EventDetails
    ├── EventInformation
    ├── RelatedEvents
    ├── ContextInformation
    └── ActionButtons
```

**Component Structure:**
```typescript
interface GlobalEventFeedProps {
  events: SystemEvent[];
  filters: EventFilter[];
}

export function GlobalEventFeed({ events, filters }: GlobalEventFeedProps) {
  const [viewMode, setViewMode] = useState<'stream' | 'timeline'>('stream');
  const [selectedEvent, setSelectedEvent] = useState<SystemEvent | null>(null);
  
  const filteredEvents = useEventFilters(events, filters);

  return (
    <Panel className="global-event-feed">
      <FeedHeader
        eventCount={filteredEvents.length}
        filters={filters}
        onFilterChange={(newFilters) => handleFilterChange(newFilters)}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />
      
      {viewMode === 'stream' ? (
        <EventStream
          events={filteredEvents}
          onEventSelect={setSelectedEvent}
        />
      ) : (
        <EventTimeline
          events={filteredEvents}
          onEventSelect={setSelectedEvent}
        />
      )}
      
      {selectedEvent && (
        <EventDetails
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      )}
    </Panel>
  );
}
```

**Event System Data Model:**
```typescript
interface SystemEvent {
  id: string;
  source: EventSource;
  type: string;
  timestamp: number;
  severity: 'info' | 'warning' | 'error' | 'critical';
  data: unknown;
  context?: {
    agent?: 'indira' | 'dyon';
    task?: string;
    project?: string;
    relatedEvents?: string[];
  };
}

type EventSource =
  | 'system'
  | 'market'
  | 'trade'
  | 'learning'
  | 'governance'
  | 'dyon'
  | 'indira'
  | 'desktop'
  | 'browser';

interface EventFilter {
  source?: EventSource[];
  type?: string[];
  severity?: SystemEvent['severity'][];
  agent?: 'indira' | 'dyon';
  timeRange?: {
    start: number;
    end: number;
  };
  searchQuery?: string;
}
```

---

## WebSocket Infrastructure

### WebSocket Manager

**File:** `src/lib/websocket/AgentWebSocketManager.ts`

**Responsibilities:**
- Manage WebSocket connections
- Handle connection lifecycle
- Implement reconnection logic
- Route messages to components

**Implementation:**
```typescript
class AgentWebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, MessageHandler[]> = new Map();
  private connectionState: ConnectionState = 'disconnected';

  constructor(private url: string) {}

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.ws = new WebSocket(this.url);
    this.connectionState = 'connecting';

    this.ws.onopen = () => {
      this.connectionState = 'connected';
      this.clearReconnectTimer();
      this.emit('connection:connected', {});
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.routeMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      this.connectionState = 'disconnected';
      this.scheduleReconnect();
      this.emit('connection:disconnected', {});
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.connectionState = 'error';
    };
  }

  private routeMessage(message: WebSocketMessage): void {
    const handlers = this.messageHandlers.get(message.type) || [];
    handlers.forEach(handler => handler(message));
  }

  subscribe(eventType: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(eventType)) {
      this.messageHandlers.set(eventType, []);
    }
    this.messageHandlers.get(eventType)!.push(handler);

    return () => {
      const handlers = this.messageHandlers.get(eventType);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) return;

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, 5000); // 5 second reconnect delay
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  disconnect(): void {
    this.clearReconnectTimer();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connectionState = 'disconnected';
  }

  getConnectionState(): ConnectionState {
    return this.connectionState;
  }
}
```

**WebSocket Endpoints:**
```typescript
const WEBSOCKET_ENDPOINTS = {
  INDIRA_ACTIVITY: '/ws/agent/indira/activity',
  DYON_ACTIVITY: '/ws/agent/dyon/activity',
  SHARED_TASKS: '/ws/agent/shared/tasks',
  SYSTEM_EVENTS: '/ws/system/events',
  VOICE_COMMANDS: '/ws/voice/commands',
} as const;
```

---

## State Management

### Agent Operations Context

**File:** `src/context/AgentOpsContext.tsx`

**Responsibilities:**
- Provide global state for Agent Operations Center
- Manage WebSocket connections
- Coordinate between components

**Implementation:**
```typescript
interface AgentOpsContextType {
  websocket: AgentWebSocketManager;
  indiraActivities: IndiraActivity[];
  dyonActivities: DyonActivity[];
  sharedTasks: Task[];
  globalEvents: SystemEvent[];
  connectionState: ConnectionState;
  addIndiraActivity: (activity: IndiraActivity) => void;
  addDyonActivity: (activity: DyonActivity) => void;
  updateSharedTask: (task: Task) => void;
  addGlobalEvent: (event: SystemEvent) => void;
}

const AgentOpsContext = createContext<AgentOpsContextType | null>(null);

export function AgentOpsProvider({ children }: { children: React.ReactNode }) {
  const [indiraActivities, setIndiraActivities] = useState<IndiraActivity[]>([]);
  const [dyonActivities, setDyonActivities] = useState<DyonActivity[]>([]);
  const [sharedTasks, setSharedTasks] = useState<Task[]>([]);
  const [globalEvents, setGlobalEvents] = useState<SystemEvent[]>([]);
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');

  const websocket = useMemo(() => {
    const manager = new AgentWebSocketManager('ws://localhost:8080/ws');
    manager.connect();

    // Subscribe to event types
    manager.subscribe('indira:activity', (message) => {
      setIndiraActivities(prev => [message.data, ...prev]);
    });

    manager.subscribe('dyon:activity', (message) => {
      setDyonActivities(prev => [message.data, ...prev]);
    });

    manager.subscribe('task:update', (message) => {
      setSharedTasks(prev => {
        const index = prev.findIndex(t => t.id === message.data.id);
        if (index > -1) {
          const updated = [...prev];
          updated[index] = message.data;
          return updated;
        }
        return [...prev, message.data];
      });
    });

    manager.subscribe('system:event', (message) => {
      setGlobalEvents(prev => [message.data, ...prev]);
    });

    manager.subscribe('connection:connected', () => {
      setConnectionState('connected');
    });

    manager.subscribe('connection:disconnected', () => {
      setConnectionState('disconnected');
    });

    return manager;
  }, []);

  const addIndiraActivity = useCallback((activity: IndiraActivity) => {
    setIndiraActivities(prev => [activity, ...prev]);
  }, []);

  const addDyonActivity = useCallback((activity: DyonActivity) => {
    setDyonActivities(prev => [activity, ...prev]);
  }, []);

  const updateSharedTask = useCallback((task: Task) => {
    setSharedTasks(prev => {
      const index = prev.findIndex(t => t.id === task.id);
      if (index > -1) {
        const updated = [...prev];
        updated[index] = task;
        return updated;
      }
      return [...prev, task];
    });
  }, []);

  const addGlobalEvent = useCallback((event: SystemEvent) => {
    setGlobalEvents(prev => [event, ...prev]);
  }, []);

  return (
    <AgentOpsContext.Provider
      value={{
        websocket,
        indiraActivities,
        dyonActivities,
        sharedTasks,
        globalEvents,
        connectionState,
        addIndiraActivity,
        addDyonActivity,
        updateSharedTask,
        addGlobalEvent,
      }}
    >
      {children}
    </AgentOpsContext.Provider>
  );
}
```

---

## Performance Considerations

### Data Management
- **Activity Limits:** Keep last 1000 activities per agent in memory
- **Event Pagination:** Load events in chunks of 100
- **Lazy Loading:** Load panel data on demand
- **Debouncing:** Debounce rapid activity updates (100ms)

### WebSocket Optimization
- **Message Batching:** Batch rapid messages into single updates
- **Compression:** Use compression for large payloads
- **Selective Subscriptions:** Subscribe only to needed event types
- **Reconnection Strategy:** Exponential backoff for reconnection

### Rendering Optimization
- **Virtual Scrolling:** For long activity feeds
- **React.memo:** Memoize panel components
- **useMemo/useCallback:** Optimize expensive computations
- **Code Splitting:** Lazy load panel components

---

## Testing Strategy

### Unit Tests
- [ ] Component rendering tests
- [ ] State management tests
- [ ] WebSocket manager tests
- [ ] Event processor tests
- [ ] Filter logic tests

### Integration Tests
- [ ] WebSocket connection tests
- [ ] End-to-end activity flow tests
- [ ] Task assignment workflow tests
- [ ] Cross-panel communication tests

### Performance Tests
- [ ] WebSocket message throughput
- [ ] Large dataset rendering
- [ ] Memory leak detection
- [ ] Connection stability tests

### User Acceptance Tests
- [ ] Real-time visibility verification
- [ ] Operator workflow tests
- [ ] Multi-agent coordination tests
- [ ] Error handling tests

---

## Success Criteria

### Functional Requirements
- [ ] Real-time agent activity feeds with <100ms latency
- [ ] Unified task system with assignment workflow
- [ ] Global event feed with filtering
- [ ] WebSocket connection stability (99.9% uptime)
- [ ] Cross-panel communication
- [ ] Voice command integration

### Non-Functional Requirements
- [ ] Support 1000+ concurrent activities
- [ ] Memory usage <500MB for typical workload
- [ ] CPU usage <30% during normal operation
- [ ] Page load time <2 seconds
- [ ] Activity update latency <100ms

### User Experience Requirements
- [ ] Operator can observe INDIRA working in real-time
- [ ] Operator can observe DYON working in real-time
- [ ] Intuitive panel switching
- [ ] Clear activity visualization
- [ ] Responsive design for different screen sizes

---

## Implementation Timeline

### Week 1-2: Foundation
- [ ] Create component structure
- [ ] Implement WebSocket manager
- [ ] Set up state management
- [ ] Create basic panel layouts

### Week 3-4: Agent Panels
- [ ] Implement IndiraActivityPanel
- [ ] Implement DyonActivityPanel
- [ ] Implement SharedActivityPanel
- [ ] Add activity visualization

### Week 5-6: Integration & Polish
- [ ] Implement GlobalEventFeed
- [ ] Add filtering and search
- [ ] Implement interaction panels
- [ ] Performance optimization
- [ ] Testing and refinement

---

## Next Steps

1. **Immediate:** Create component directory structure
2. **Week 1:** Implement WebSocket manager and state management
3. **Week 2:** Create basic panel layouts
4. **Week 3-4:** Implement agent-specific panels
5. **Week 5-6:** Add global event feed and polish

---

**Conclusion:** The Agent Operations Center design provides a comprehensive foundation for the cognitive operating environment transformation. Real-time visibility into agent activities, unified task management, and cross-agent coordination establish the paradigm shift from UI to operating environment.
