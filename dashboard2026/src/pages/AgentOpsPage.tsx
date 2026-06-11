/**
 * Agent Operations Center Page
 * 
 * Main page for the Agent Operations Center
 * Provides real-time visibility into INDIRA, DYON, and shared activities
 */

import { useState } from 'react';
import { PanelLayout } from '@/components/agent/Panel';
import { IndiraActivityPanel } from '@/components/agent/IndiraActivityPanel';
import { DyonActivityPanel } from '@/components/agent/DyonActivityPanel';
import { SharedActivityPanel } from '@/components/agent/SharedActivityPanel';
import { GlobalEventFeed } from '@/components/agent/GlobalEventFeed';
import { useConnectionState, useGlobalEvents } from '@/context/AgentOpsContext';
import { Brain, Wrench, Users, Activity, Wifi, WifiOff, AlertCircle, FlaskConical } from 'lucide-react';

export function AgentOpsPage() {
  const [activePanel, setActivePanel] = useState<'indira' | 'dyon' | 'shared'>('indira');
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'full'>('grid');
  
  const { connectionState, isConnected, isMockMode } = useConnectionState();
  const globalEvents = useGlobalEvents();

  return (
    <div className="agent-ops-page flex flex-col h-full">
      {/* Header */}
      <div className="agent-ops-header flex items-center justify-between border-b border-border bg-muted/30 px-6 py-4">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-primary" />
          <div>
            <h1 className="text-lg font-semibold">Agent Operations Center</h1>
            <p className="text-xs text-muted-foreground">
              Real-time visibility into INDIRA, DYON, and shared activities
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

          {/* Event Count */}
          <div className="text-sm text-muted-foreground">
            {globalEvents.length} events
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-2 border border-border rounded px-2 py-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
              }`}
            >
              List
            </button>
            <button
              onClick={() => setViewMode('full')}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                viewMode === 'full' ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
              }`}
            >
              Full
            </button>
          </div>
        </div>
      </div>

      {/* Connection Warning */}
      {!isConnected && (
        <div className="mx-6 mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-500" />
          <div>
            <p className="text-sm font-medium text-yellow-500">
              WebSocket Disconnected
            </p>
            <p className="text-xs text-yellow-500/70">
              Real-time updates are not available. Reconnecting...
            </p>
          </div>
        </div>
      )}

      {/* Panel Selector */}
      <div className="flex items-center gap-2 px-6 py-4 border-b border-border">
        <button
          onClick={() => setActivePanel('indira')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            activePanel === 'indira'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          <Brain className="w-4 h-4" />
          <span>INDIRA</span>
        </button>
        <button
          onClick={() => setActivePanel('dyon')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            activePanel === 'dyon'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          <Wrench className="w-4 h-4" />
          <span>DYON</span>
        </button>
        <button
          onClick={() => setActivePanel('shared')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
            activePanel === 'shared'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Shared</span>
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        {viewMode === 'grid' ? (
          <PanelLayout columns={3} gap={6}>
            <IndiraActivityPanel isActive={activePanel === 'indira'} />
            <DyonActivityPanel isActive={activePanel === 'dyon'} />
            <SharedActivityPanel isActive={activePanel === 'shared'} />
          </PanelLayout>
        ) : viewMode === 'full' ? (
          <PanelLayout columns={2} gap={6}>
            <div className="space-y-6">
              {activePanel === 'indira' && (
                <IndiraActivityPanel isActive={true} />
              )}
              {activePanel === 'dyon' && (
                <DyonActivityPanel isActive={true} />
              )}
              {activePanel === 'shared' && (
                <SharedActivityPanel isActive={true} />
              )}
            </div>
            <GlobalEventFeed />
          </PanelLayout>
        ) : (
          <div className="space-y-6">
            {activePanel === 'indira' && (
              <IndiraActivityPanel isActive={true} />
            )}
            {activePanel === 'dyon' && (
              <DyonActivityPanel isActive={true} />
            )}
            {activePanel === 'shared' && (
              <SharedActivityPanel isActive={true} />
            )}
          </div>
        )}
      </div>
    </div>
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
