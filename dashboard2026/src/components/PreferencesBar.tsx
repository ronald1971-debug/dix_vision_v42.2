import { Gauge, LayoutGrid, Palette, Rows3, Sliders, Shield, type LucideIcon } from "lucide-react";

import {
  DENSITY_OPTIONS,
  LAYOUT_OPTIONS,
  THEME_OPTIONS,
  setPreferences,
  usePreferences,
  type Density,
  type LayoutProfile,
  type Theme,
} from "@/preferences/store";
import {
  setWidgetPanelOpen,
  useWidgetPanelOpen,
} from "@/state/widgetVisibility";
import { useState, useEffect } from "react";

// Compliance level options (0, 25, 50, 75, 100)
const COMPLIANCE_LEVELS = [0, 25, 50, 75, 100] as const;
type ComplianceLevel = typeof COMPLIANCE_LEVELS[number];

// Simple compliance store for now (can be moved to preferences store later)
let currentComplianceLevel: ComplianceLevel = 100;
const complianceListeners = new Set<(level: ComplianceLevel) => void>();

export function setComplianceLevel(level: ComplianceLevel) {
  currentComplianceLevel = level;
  complianceListeners.forEach(listener => listener(level));
}

export function useComplianceLevel(): ComplianceLevel {
  const [level, setLevel] = useState(currentComplianceLevel);
  
  useEffect(() => {
    const listener = (newLevel: ComplianceLevel) => setLevel(newLevel);
    complianceListeners.add(listener);
    return (): void => {
      complianceListeners.delete(listener);
    };
  }, []);
  
  return level;
}

/**
 * Tier-7 preferences bar — three pill rotators in the top header.
 *
 * Theme rotates through dark / midnight / ash (mirrored as
 * `data-theme=…` on `<html>` so future Tailwind dark variants and
 * widget-local CSS can key off it). Density rotates through
 * compact / normal / comfortable (mirrored as `data-density=…`,
 * widgets read it via class queries on the root). Layout profile
 * rotates Conservative / Standard / Aggressive / Custom — preset
 * dial values for size cap, drawdown floor, hazard tolerance, and
 * signal threshold. The profile name does not mutate widget code.
 */
function rotate<T>(arr: readonly T[], current: T): T {
  const idx = arr.indexOf(current);
  return arr[(idx + 1) % arr.length];
}

interface PillProps {
  label: string;
  value: string;
  onClick: () => void;
  icon: LucideIcon;
  hint?: string;
}

function Pill({ label, value, onClick, icon: Icon, hint }: PillProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={hint ?? `Cycle ${label}`}
      className="flex items-center gap-1.5 rounded border border-border bg-bg px-2 py-1 text-[10px] uppercase tracking-widest text-slate-300 hover:bg-surface hover:text-slate-100"
    >
      <Icon className="h-3.5 w-3.5" />
      <span className="font-mono text-slate-500">{label}</span>
      <span className="font-mono">{value}</span>
    </button>
  );
}

export function PreferencesBar() {
  const prefs = usePreferences();
  const panelOpen = useWidgetPanelOpen();
  const complianceLevel = useComplianceLevel();

  const getComplianceColor = (level: ComplianceLevel) => {
    if (level >= 75) return "text-green-400 border-green-400/50 bg-green-400/10";
    if (level >= 50) return "text-yellow-400 border-yellow-400/50 bg-yellow-400/10";
    if (level >= 25) return "text-orange-400 border-orange-400/50 bg-orange-400/10";
    return "text-red-400 border-red-400/50 bg-red-400/10";
  };

  const getComplianceLabel = (level: ComplianceLevel) => {
    if (level >= 75) return "FULL";
    if (level >= 50) return "HIGH";
    if (level >= 25) return "MED";
    return "LOW";
  };

  return (
    <div className="flex items-center gap-1.5">
      <Pill
        label="theme"
        value={prefs.theme}
        icon={Palette}
        onClick={() =>
          setPreferences({
            theme: rotate<Theme>(THEME_OPTIONS, prefs.theme),
          })
        }
      />
      <Pill
        label="dens"
        value={prefs.density}
        icon={Rows3}
        onClick={() =>
          setPreferences({
            density: rotate<Density>(DENSITY_OPTIONS, prefs.density),
          })
        }
      />
      <Pill
        label="layout"
        value={prefs.layoutProfile}
        icon={LayoutGrid}
        onClick={() =>
          setPreferences({
            layoutProfile: rotate<LayoutProfile>(
              LAYOUT_OPTIONS,
              prefs.layoutProfile,
            ),
          })
        }
        hint="Conservative ↔ Standard ↔ Aggressive ↔ Custom"
      />
      <button
        type="button"
        onClick={() => {
          const currentIndex = COMPLIANCE_LEVELS.indexOf(complianceLevel);
          const nextIndex = (currentIndex + 1) % COMPLIANCE_LEVELS.length;
          setComplianceLevel(COMPLIANCE_LEVELS[nextIndex]);
        }}
        title={`Compliance: ${complianceLevel}% (${getComplianceLabel(complianceLevel)}) - Click to cycle`}
        className={`flex items-center gap-1.5 rounded border px-2 py-1 text-[10px] uppercase tracking-widest transition-colors ${getComplianceColor(complianceLevel)}`}
      >
        <Shield className="h-3.5 w-3.5" />
        <span className="font-mono text-slate-500">comp</span>
        <span className="font-mono">{complianceLevel}%</span>
      </button>
      <button
        type="button"
        onClick={() => setWidgetPanelOpen(!panelOpen)}
        title="Toggle widget visibility"
        className={`flex items-center gap-1.5 rounded border px-2 py-1 text-[10px] uppercase tracking-widest transition-colors ${
          panelOpen
            ? "border-accent bg-accent/10 text-accent"
            : "border-border bg-bg text-slate-300 hover:bg-surface hover:text-slate-100"
        }`}
      >
        <Sliders className="h-3.5 w-3.5" />
        <span className="font-mono">widgets</span>
      </button>
      <span
        className="hidden items-center gap-1 rounded border border-border bg-bg px-2 py-1 font-mono text-[10px] uppercase tracking-widest text-slate-500 lg:flex"
        title="Open command palette"
      >
        <Gauge className="h-3.5 w-3.5" />
        <span>⌘K</span>
      </span>
    </div>
  );
}
