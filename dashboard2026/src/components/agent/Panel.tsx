/**
 * Basic Panel Components for Agent Operations Center
 */

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface PanelProps {
  children: ReactNode;
  className?: string;
  title?: string;
  isActive?: boolean;
  collapsible?: boolean;
  onCollapse?: () => void;
}

/**
 * Basic panel component with optional header
 */
export function Panel({
  children,
  className,
  title,
  isActive = false,
  collapsible = false,
  onCollapse,
}: PanelProps) {
  return (
    <div
      className={cn(
        'panel',
        'border border-border bg-surface rounded-lg overflow-hidden',
        'flex flex-col',
        isActive && 'active border-accent',
        className
      )}
    >
      {title && (
        <div className="panel-header flex items-center justify-between border-b border-border bg-muted/30 px-4 py-2">
          <h3 className="text-sm font-semibold">{title}</h3>
          {collapsible && onCollapse && (
            <button
              onClick={onCollapse}
              className="text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Collapse panel"
            >
              −
            </button>
          )}
        </div>
      )}
      <div className="panel-content flex-1 overflow-auto p-4">
        {children}
      </div>
    </div>
  );
}

interface PanelLayoutProps {
  children: ReactNode;
  columns?: number;
  gap?: number;
  className?: string;
}

/**
 * Panel layout grid component
 */
export function PanelLayout({
  children,
  columns = 2,
  gap = 4,
  className,
}: PanelLayoutProps) {
  return (
    <div
      className={cn(
        'panel-layout',
        'grid',
        `grid-cols-${columns}`,
        `gap-${gap}`,
        'h-full',
        className
      )}
      style={{
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: `${gap * 0.25}rem`,
      }}
    >
      {children}
    </div>
  );
}

interface PanelSectionProps {
  children: ReactNode;
  title?: string;
  className?: string;
}

/**
 * Panel section for grouping content within a panel
 */
export function PanelSection({ children, title, className }: PanelSectionProps) {
  return (
    <div className={cn('panel-section', 'mb-4 last:mb-0', className)}>
      {title && (
        <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
          {title}
        </h4>
      )}
      {children}
    </div>
  );
}

interface ActivityItemProps {
  title: string;
  description?: string;
  timestamp: number;
  status?: 'active' | 'completed' | 'paused' | 'error';
  className?: string;
}

/**
 * Individual activity item component
 */
export function ActivityItem({
  title,
  description,
  timestamp,
  status = 'active',
  className,
}: ActivityItemProps) {
  const timeAgo = getTimeAgo(timestamp);

  return (
    <div
      className={cn(
        'activity-item',
        'flex items-start gap-3 p-3 rounded border border-border bg-muted/30',
        'hover:bg-muted/50 transition-colors',
        className
      )}
    >
      <div
        className={cn(
          'status-indicator',
          'w-2 h-2 rounded-full mt-1.5 flex-shrink-0',
          getStatusColor(status)
        )}
      />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{title}</p>
        {description && (
          <p className="text-xs text-muted-foreground truncate">{description}</p>
        )}
        <p className="text-xs text-muted-foreground mt-1">{timeAgo}</p>
      </div>
    </div>
  );
}

// ============================================================================
// Helper Functions
// ============================================================================

function getStatusColor(status: ActivityItemProps['status']): string {
  switch (status) {
    case 'active':
      return 'bg-green-500';
    case 'completed':
      return 'bg-blue-500';
    case 'paused':
      return 'bg-yellow-500';
    case 'error':
      return 'bg-red-500';
    default:
      return 'bg-gray-500';
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
