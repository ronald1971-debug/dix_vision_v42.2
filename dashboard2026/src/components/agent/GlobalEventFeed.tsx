/**
 * Global Event Feed Component
 * 
 * Displays global system events with filtering and timeline views
 */

import { useState, useMemo } from 'react';
import { Panel, PanelSection } from './Panel';
import { useGlobalEvents } from '@/context/AgentOpsContext';
import type { SystemEvent, EventFilter, EventSource } from '@/types/agent';
import { Activity, Filter, AlertTriangle, CheckCircle, XCircle, Info, Search } from 'lucide-react';

export function GlobalEventFeed() {
  const events = useGlobalEvents();
  const [viewMode, setViewMode] = useState<'stream' | 'timeline'>('stream');
  const [filters, setFilters] = useState<EventFilter>({});
  const [searchQuery, setSearchQuery] = useState('');

  // Apply filters and search
  const filteredEvents = useMemo(() => {
    let result = events;

    // Apply source filter
    if (filters.source && filters.source.length > 0) {
      result = result.filter(event => filters.source!.includes(event.source));
    }

    // Apply severity filter
    if (filters.severity && filters.severity.length > 0) {
      result = result.filter(event => filters.severity!.includes(event.severity));
    }

    // Apply agent filter
    if (filters.agent) {
      result = result.filter(event => event.context?.agent === filters.agent);
    }

    // Apply time range filter
    if (filters.timeRange) {
      result = result.filter(
        event => 
          event.timestamp >= filters.timeRange!.start && 
          event.timestamp <= filters.timeRange!.end
      );
    }

    // Apply search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(event => 
        event.type.toLowerCase().includes(query) ||
        JSON.stringify(event.data).toLowerCase().includes(query)
      );
    }

    return result;
  }, [events, filters, searchQuery]);

  // Group events by source for better organization
  const eventsBySource = useMemo(() => {
    const grouped: Record<string, SystemEvent[]> = {};
    filteredEvents.forEach(event => {
      if (!grouped[event.source]) {
        grouped[event.source] = [];
      }
      grouped[event.source].push(event);
    });
    return grouped;
  }, [filteredEvents]);

  const toggleFilter = (filterType: 'source' | 'severity', value: string) => {
    setFilters(prev => {
      const current = prev[filterType] as string[] || [];
      const updated = current.includes(value)
        ? current.filter(v => v !== value)
        : [...current, value];
      
      return {
        ...prev,
        [filterType]: updated.length > 0 ? updated : undefined,
      };
    });
  };

  const toggleAgentFilter = (agent: 'indira' | 'dyon') => {
    setFilters(prev => {
      if (prev.agent === agent) {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { agent: _, ...rest } = prev;
        return rest;
      } else {
        return { ...prev, agent };
      }
    });
  };

  return (
    <Panel
      title="Global Event Feed"
      className="global-event-feed"
    >
      {/* Filter Controls */}
      <div className="mb-4 p-3 bg-muted/30 rounded border border-border">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">Filters</span>
        </div>

        {/* Search */}
        <div className="mb-3">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search events..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-2 bg-background border border-border rounded text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        </div>

        {/* Source Filters */}
        <div className="mb-3">
          <p className="text-xs text-muted-foreground mb-2">Source</p>
          <div className="flex flex-wrap gap-1">
            {renderFilterButtons(
              ['system', 'market', 'trade', 'learning', 'governance', 'indira', 'dyon', 'desktop', 'browser'],
              filters.source || [],
              (value) => toggleFilter('source', value)
            )}
          </div>
        </div>

        {/* Severity Filters */}
        <div className="mb-3">
          <p className="text-xs text-muted-foreground mb-2">Severity</p>
          <div className="flex flex-wrap gap-1">
            {renderFilterButtons(
              ['info', 'warning', 'error', 'critical'],
              filters.severity || [],
              (value) => toggleFilter('severity', value)
            )}
          </div>
        </div>

        {/* Agent Filters */}
        <div className="mb-3">
          <p className="text-xs text-muted-foreground mb-2">Agent</p>
          <div className="flex flex-wrap gap-1">
            <button
              onClick={() => toggleAgentFilter('indira')}
              className={`px-2 py-1 text-xs rounded border transition-colors ${
                filters.agent === 'indira'
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-background border-border hover:bg-muted'
              }`}
            >
              INDIRA
            </button>
            <button
              onClick={() => toggleAgentFilter('dyon')}
              className={`px-2 py-1 text-xs rounded border transition-colors ${
                filters.agent === 'dyon'
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-background border-border hover:bg-muted'
              }`}
            >
              DYON
            </button>
          </div>
        </div>

        {/* Clear Filters */}
        {(filters.source || filters.severity || filters.agent || searchQuery) && (
          <button
            onClick={() => {
              setFilters({});
              setSearchQuery('');
            }}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Clear all filters
          </button>
        )}
      </div>

      {/* View Mode Toggle */}
      <div className="mb-4 flex items-center justify-between">
        <span className="text-sm text-muted-foreground">
          {filteredEvents.length} events
        </span>
        <div className="flex items-center gap-2 border border-border rounded px-2 py-1">
          <button
            onClick={() => setViewMode('stream')}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              viewMode === 'stream'
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-muted'
            }`}
          >
            Stream
          </button>
          <button
            onClick={() => setViewMode('timeline')}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              viewMode === 'timeline'
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-muted'
            }`}
          >
            Timeline
          </button>
        </div>
      </div>

      {/* Event Display */}
      {filteredEvents.length === 0 ? (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <div className="text-center">
            <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No events to display</p>
            <p className="text-xs mt-1">Events will appear here when system activity occurs</p>
          </div>
        </div>
      ) : viewMode === 'stream' ? (
        <StreamView events={filteredEvents} eventsBySource={eventsBySource} />
      ) : (
        <TimelineView events={filteredEvents} />
      )}
    </Panel>
  );
}

// ============================================================================
// Stream View Component
// ============================================================================

interface StreamViewProps {
  events: SystemEvent[];
  eventsBySource: Record<string, SystemEvent[]>;
}

function StreamView({ eventsBySource }: StreamViewProps) {
  return (
    <div className="space-y-4 max-h-[500px] overflow-auto">
      {Object.entries(eventsBySource).map(([source, sourceEvents]) => (
        <PanelSection key={source} title={getSourceLabel(source as EventSource)}>
          <div className="space-y-2">
            {sourceEvents.slice(0, 5).map(event => (
              <EventItem key={event.id} event={event} />
            ))}
            {sourceEvents.length > 5 && (
              <button className="text-xs text-muted-foreground hover:text-foreground">
                + {sourceEvents.length - 5} more
              </button>
            )}
          </div>
        </PanelSection>
      ))}
    </div>
  );
}

// ============================================================================
// Timeline View Component
// ============================================================================

interface TimelineViewProps {
  events: SystemEvent[];
}

function TimelineView({ events }: TimelineViewProps) {
  return (
    <div className="space-y-2 max-h-[500px] overflow-auto">
      {events.map((event, index) => (
        <div key={event.id} className="flex items-start gap-3">
          <div className="flex flex-col items-center">
            <div className={`w-2 h-2 rounded-full ${getSeverityColor(event.severity)}`} />
            {index < events.length - 1 && (
              <div className="w-0.5 h-full bg-border min-h-[32px]" />
            )}
          </div>
          <div className="flex-1">
            <EventItem event={event} compact />
          </div>
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// Event Item Component
// ============================================================================

interface EventItemProps {
  event: SystemEvent;
  compact?: boolean;
}

function EventItem({ event, compact = false }: EventItemProps) {
  return (
    <div
      className={`event-item p-3 rounded border border-border bg-muted/30 hover:bg-muted/50 transition-colors ${
        compact ? 'p-2' : ''
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          {getSeverityIcon(event.severity)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="text-sm font-medium">{formatEventType(event.type)}</p>
            <span className="text-xs text-muted-foreground">•</span>
            <span className="text-xs text-muted-foreground capitalize">{event.source}</span>
          </div>
          {!compact && event.data ? (
            <p className="text-xs text-muted-foreground truncate">
              {formatEventData(event.data)}
            </p>
          ) : null}
          <p className="text-xs text-muted-foreground mt-1">
            {getTimeAgo(event.timestamp)}
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Helper Functions
// ============================================================================

function renderFilterButtons(
  options: string[],
  selected: string[],
  onToggle: (value: string) => void
) {
  return options.map(value => (
    <button
      key={value}
      onClick={() => onToggle(value)}
      className={`px-2 py-1 text-xs rounded border transition-colors ${
        selected.includes(value)
          ? 'bg-primary text-primary-foreground border-primary'
          : 'bg-background border-border hover:bg-muted'
      }`}
    >
      {value}
    </button>
  ));
}

function getSourceLabel(source: EventSource): string {
  const labels: Record<EventSource, string> = {
    system: 'System',
    market: 'Market',
    trade: 'Trade',
    learning: 'Learning',
    governance: 'Governance',
    dyon: 'DYON',
    indira: 'INDIRA',
    desktop: 'Desktop',
    browser: 'Browser',
  };
  return labels[source] || source;
}

function formatEventType(type: string): string {
  return type
    .split(':')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function getSeverityColor(severity: SystemEvent['severity']): string {
  switch (severity) {
    case 'info':
      return 'bg-blue-500';
    case 'warning':
      return 'bg-yellow-500';
    case 'error':
      return 'bg-red-500';
    case 'critical':
      return 'bg-red-600 animate-pulse';
    default:
      return 'bg-gray-500';
  }
}

function getSeverityIcon(severity: SystemEvent['severity']) {
  switch (severity) {
    case 'info':
      return <Info className="w-4 h-4 text-blue-500" />;
    case 'warning':
      return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
    case 'error':
      return <XCircle className="w-4 h-4 text-red-500" />;
    case 'critical':
      return <AlertTriangle className="w-4 h-4 text-red-600" />;
    default:
      return <CheckCircle className="w-4 h-4 text-gray-500" />;
  }
}

function formatEventData(data: unknown): string {
  if (typeof data === 'string') {
    return data;
  }
  if (typeof data === 'object' && data !== null && 'message' in data) {
    return String((data as { message: string }).message);
  }
  return JSON.stringify(data);
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
