/**
 * Shared Tool Layers Component
 * 
 * Desktop and Browser layers as shared tools for Operator, INDIRA, DYON
 * 
 * This component provides visualization and management of shared tool layers,
 * showing which agents are currently using Desktop Layer and Browser Layer.
 */

import { useState, useEffect } from 'react';
import { Monitor, Globe, Activity, Lock, Unlock, Clock } from 'lucide-react';
import { Panel, PanelLayout, PanelSection } from '@/components/agent/Panel';

interface LayerStatus {
  layer_type: string;
  available: boolean;
  active_sessions: number;
  recent_activity_count: number;
  current_user: string | null;
  current_user_type: string | null;
}

interface SessionInfo {
  session_id: string;
  entity_type: string;
  entity_id: string;
  layer_type: string;
  started_at: string;
  last_activity: string;
  status: string;
}

export function SharedToolLayers() {
  const [layerStatuses, setLayerStatuses] = useState<Record<string, LayerStatus>>({});
  const [sessions, setSessions] = useState<SessionInfo[]>([]);

  useEffect(() => {
    const fetchToolLayersData = async () => {
      try {
        // In a real implementation, this would fetch from the cognitive control center API
        // For now, we'll simulate the data
        
        const mockLayerStatuses: Record<string, LayerStatus> = {
          desktop_layer: {
            layer_type: 'desktop_layer',
            available: true,
            active_sessions: 0,
            recent_activity_count: 12,
            current_user: null,
            current_user_type: null,
          },
          browser_layer: {
            layer_type: 'browser_layer',
            available: true,
            active_sessions: 0,
            recent_activity_count: 8,
            current_user: null,
            current_user_type: null,
          },
        };

        const mockSessions: SessionInfo[] = [];

        setLayerStatuses(mockLayerStatuses);
        setSessions(mockSessions);
      } catch (error) {
        console.error('Failed to fetch shared tool layers data:', error);
      }
    };

    fetchToolLayersData();
    const interval = setInterval(fetchToolLayersData, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="shared-tool-layers">
      <PanelLayout columns={2} gap={6}>
        {/* Desktop Layer */}
        <Panel>
          <PanelSection title="Desktop Layer - Shared Tool" className="flex-1">
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Monitor className="w-5 h-5 text-blue-500" />
                  <span className="text-sm font-semibold text-blue-500">Desktop Agent Layer</span>
                </div>
                <div className="flex items-center gap-2">
                  {layerStatuses.desktop_layer?.available ? (
                    <div className="flex items-center gap-1 text-xs text-green-400">
                      <Unlock className="w-3 h-3" />
                      <span>Available</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-xs text-orange-400">
                      <Lock className="w-3 h-3" />
                      <span>In Use</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded bg-slate-800/50 border border-border">
                  <div className="text-xs text-muted-foreground mb-1">Status</div>
                  <div className="text-sm font-medium">
                    {layerStatuses.desktop_layer?.available ? 'Available' : 'In Use'}
                  </div>
                </div>
                <div className="p-3 rounded bg-slate-800/50 border border-border">
                  <div className="text-xs text-muted-foreground mb-1">Recent Activity</div>
                  <div className="text-sm font-medium">
                    {layerStatuses.desktop_layer?.recent_activity_count} operations
                  </div>
                </div>
              </div>

              {layerStatuses.desktop_layer?.current_user && (
                <div className="p-3 rounded bg-blue-500/10 border border-blue-500/30">
                  <div className="text-xs text-muted-foreground mb-1">Current User</div>
                  <div className="text-sm font-medium text-blue-400">
                    {layerStatuses.desktop_layer.current_user_type?.toUpperCase()} - {layerStatuses.desktop_layer.current_user}
                  </div>
                </div>
              )}

              <div className="text-xs text-muted-foreground">
                Used by Operator for manual operations, INDIRA for research and testing, DYON for automation and inspection
              </div>
            </div>
          </PanelSection>
        </Panel>

        {/* Browser Layer */}
        <Panel>
          <PanelSection title="Browser Layer - Shared Tool" className="flex-1">
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-green-500" />
                  <span className="text-sm font-semibold text-green-500">Browser Layer</span>
                </div>
                <div className="flex items-center gap-2">
                  {layerStatuses.browser_layer?.available ? (
                    <div className="flex items-center gap-1 text-xs text-green-400">
                      <Unlock className="w-3 h-3" />
                      <span>Available</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-xs text-orange-400">
                      <Lock className="w-3 h-3" />
                      <span>In Use</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded bg-slate-800/50 border border-border">
                  <div className="text-xs text-muted-foreground mb-1">Status</div>
                  <div className="text-sm font-medium">
                    {layerStatuses.browser_layer?.available ? 'Available' : 'In Use'}
                  </div>
                </div>
                <div className="p-3 rounded bg-slate-800/50 border border-border">
                  <div className="text-xs text-muted-foreground mb-1">Recent Activity</div>
                  <div className="text-sm font-medium">
                    {layerStatuses.browser_layer?.recent_activity_count} operations
                  </div>
                </div>
              </div>

              {layerStatuses.browser_layer?.current_user && (
                <div className="p-3 rounded bg-green-500/10 border border-green-500/30">
                  <div className="text-xs text-muted-foreground mb-1">Current User</div>
                  <div className="text-sm font-medium text-green-400">
                    {layerStatuses.browser_layer.current_user_type?.toUpperCase()} - {layerStatuses.browser_layer.current_user}
                  </div>
                </div>
              )}

              <div className="text-xs text-muted-foreground">
                Used by Operator for web interaction, INDIRA for market research, DYON for platform testing
              </div>
            </div>
          </PanelSection>
        </Panel>

        {/* Active Sessions */}
        <Panel className="col-span-2">
          <PanelSection title="Active Tool Layer Sessions" className="flex-1">
            {sessions.length > 0 ? (
              <div className="space-y-2">
                {sessions.map((session) => (
                  <div key={session.session_id} className="p-3 rounded bg-slate-800/50 border border-border">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Activity className="w-4 h-4 text-blue-400" />
                        <div>
                          <div className="text-sm font-medium">{session.entity_id}</div>
                          <div className="text-xs text-muted-foreground">
                            {session.entity_type.toUpperCase()} - {session.layer_type.replace('_', ' ')}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(session.last_activity).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">
                No active tool layer sessions
              </div>
            )}
          </PanelSection>
        </Panel>
      </PanelLayout>
    </div>
  );
}

// Add the import for PanelLayout if not already imported
import { PanelLayout } from '@/components/agent/Panel';