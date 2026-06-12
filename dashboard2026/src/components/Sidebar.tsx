/**
 * Dashboard2026 Sidebar - Natural Domain-Based Navigation
 *
 * Navigation organized by natural domain groupings for intuitive operator experience:
 * - Mission Control
 * - Trading (Markets, Execution, Portfolio)
 * - Intelligence (INDIRA, DYON)
 * - Operations (System, Governance, Infrastructure)
 * - Tools (AI, Testing, Plugins)
 */

import {
  Activity,
  Archive,
  Banknote,
  BarChart3,
  Bot,
  Brain,
  Briefcase,
  CandlestickChart,
  CheckSquare,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Coins,
  Compass,
  FileText,
  Gauge,
  Heart,
  Image as ImageIcon,
  KeyRound,
  Layers,
  LineChart,
  MessageSquare,
  Monitor,
  Network,
  Puzzle,
  Radar,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Target,
  Telescope,
  TrendingUp,
  Users,
  Wrench,
  Zap,
  AlertTriangle,
} from "lucide-react";
import { type ComponentType } from "react";

import {
  type AssetRoute,
  type Route,
  type SystemRoute,
} from "@/router";

interface NavItem<R extends Route> {
  key: R;
  label: string;
  href: string;
  icon: ComponentType<{ className?: string }>;
}

// ==============================================================================
// NAVIGATION SECTIONS - Natural Domain-Based Organization
// ==============================================================================

const MISSION_CONTROL_NAV: Record<string, NavItem<SystemRoute>> = {
  "mission-control": { key: "mission-control", label: "Mission Control", href: "#/mission-control", icon: Monitor },
  operator: { key: "operator", label: "Operator", href: "#/operator", icon: Bot },
  credentials: { key: "credentials", label: "Credentials", href: "#/credentials", icon: KeyRound },
  chat: { key: "chat", label: "Chat", href: "#/chat", icon: MessageSquare },
};

const TRADING_NAV: Record<string, NavItem<SystemRoute | AssetRoute>> = {
  market: { key: "market", label: "Markets", href: "#/market", icon: Compass },
  charting: { key: "charting", label: "Charting", href: "#/charting", icon: LineChart },
  orderflow: { key: "orderflow", label: "Order Flow", href: "#/orderflow", icon: CandlestickChart },
  spot: { key: "spot", label: "Spot", href: "#/spot", icon: BarChart3 },
  perps: { key: "perps", label: "Perps", href: "#/perps", icon: Activity },
  dex: { key: "dex", label: "DEX", href: "#/dex", icon: Layers },
  forex: { key: "forex", label: "Forex", href: "#/forex", icon: Banknote },
  stocks: { key: "stocks", label: "Stocks", href: "#/stocks", icon: TrendingUp },
  trading: { key: "trading", label: "Trading", href: "#/trading", icon: Target },
  positions: { key: "positions", label: "Positions", href: "#/positions", icon: Briefcase },
  execution: { key: "execution", label: "Execution", href: "#/execution", icon: Target },
  "open-orders": { key: "open-orders", label: "Orders & Fills", href: "#/open-orders", icon: Activity },
  portfolio: { key: "portfolio", label: "Portfolio", href: "#/portfolio", icon: Briefcase },
  risk: { key: "risk", label: "Risk", href: "#/risk", icon: Gauge },
  ledger: { key: "ledger", label: "Ledger", href: "#/ledger", icon: FileText },
  strategies: { key: "strategies", label: "Strategies", href: "#/strategies", icon: Brain },
  forms: { key: "forms", label: "Forms", href: "#/forms", icon: Layers },
};

const INTELLIGENCE_NAV: Record<string, NavItem<SystemRoute>> = {
  "indira-workspace": { key: "indira-workspace", label: "INDIRA Workspace", href: "#/indira-workspace", icon: Brain },
  indira: { key: "indira", label: "INDIRA Learning", href: "#/indira", icon: Sparkles },
  "dyon-workspace": { key: "dyon-workspace", label: "DYON Workspace", href: "#/dyon-workspace", icon: Wrench },
  dyon: { key: "dyon", label: "DYON Learning", href: "#/dyon", icon: Sparkles },
  "agent-ops": { key: "agent-ops", label: "Agent Operations", href: "#/agent-ops", icon: Users },
  "operator-workspace": { key: "operator-workspace", label: "Operator Workspace", href: "#/operator-workspace", icon: Bot },
  ai: { key: "ai", label: "AI ASKB", href: "#/ai", icon: Sparkles },
  signals: { key: "signals", label: "Signals", href: "#/signals", icon: Zap },
};

const OPERATIONS_NAV: Record<string, NavItem<SystemRoute>> = {
  syshealth: { key: "syshealth", label: "System Health", href: "#/syshealth", icon: Heart },
  observatory: { key: "observatory", label: "Observatory", href: "#/observatory", icon: Telescope },
  testing: { key: "testing", label: "Testing & Eval", href: "#/testing", icon: CheckSquare },
  alerts: { key: "alerts", label: "Alerts", href: "#/alerts", icon: AlertTriangle },
  onchain: { key: "onchain", label: "On-chain", href: "#/onchain", icon: Coins },
  scout: { key: "scout", label: "Scout", href: "#/scout", icon: Radar },
};

const GOVERNANCE_NAV: Record<string, NavItem<SystemRoute>> = {
  governance: { key: "governance", label: "Governance", href: "#/governance", icon: ShieldAlert },
  security: { key: "security", label: "Security", href: "#/security", icon: ShieldCheck },
  risk: { key: "risk", label: "Risk", href: "#/risk", icon: Gauge },
  audit: { key: "audit", label: "Audit", href: "#/audit", icon: ClipboardList },
  hazards: { key: "hazards", label: "Hazards", href: "#/hazards", icon: AlertTriangle },
};

const LEARNING_NAV: Record<string, NavItem<SystemRoute>> = {
  indira: { key: "indira", label: "INDIRA Learning", href: "#/indira", icon: Brain },
  dyon: { key: "dyon", label: "DYON Learning", href: "#/dyon", icon: Wrench },
  memory: { key: "memory", label: "Memory Layer", href: "#/memory", icon: Archive },
  fabric: { key: "fabric", label: "Event Fabric", href: "#/fabric", icon: Network },
  simulation: { key: "simulation", label: "Simulation", href: "#/simulation", icon: Activity },
};

const TOOLS_NAV: Record<string, NavItem<SystemRoute>> = {
  plugins: { key: "plugins", label: "Plugins", href: "#/plugins", icon: Puzzle },
  adapters: { key: "adapters", label: "Adapters", href: "#/adapters", icon: Network },
  dashmeme: { key: "dashmeme", label: "DashMeme", href: "#/dashmeme", icon: Coins },
  nft: { key: "nft", label: "NFT", href: "#/nft", icon: ImageIcon },
};

export interface SidebarProps {
  active: Route;
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ active, collapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={`flex flex-col border-r border-border bg-surface transition-[width] duration-200 ${
        collapsed ? "w-12" : "w-56"
      }`}
      aria-label="primary navigation"
      data-testid="sidebar"
    >
      <button
        type="button"
        onClick={onToggle}
        className="m-1 flex h-9 items-center justify-center rounded border border-transparent text-slate-400 hover:border-border hover:text-accent"
        aria-label={collapsed ? "expand sidebar" : "collapse sidebar"}
        title={collapsed ? "expand" : "collapse"}
      >
        {collapsed ? (
          <ChevronRight className="h-4 w-4" />
        ) : (
          <ChevronLeft className="h-4 w-4" />
        )}
      </button>

      <SidebarSection title="MISSION CONTROL" collapsed={collapsed}>
        {Object.values(MISSION_CONTROL_NAV).map((item) => (
          <SidebarLink
            key={item.key}
            item={item}
            isActive={active === item.key}
            collapsed={collapsed}
          />
        ))}
      </SidebarSection>

      <SidebarSection title="TRADING" collapsed={collapsed}>
        {Object.values(TRADING_NAV).map((item) => (
          <SidebarLink
            key={item.key}
            item={item}
            isActive={active === item.key}
            collapsed={collapsed}
          />
        ))}
      </SidebarSection>

      <SidebarSection title="INTELLIGENCE" collapsed={collapsed}>
        {Object.values(INTELLIGENCE_NAV).map((item) => (
          <SidebarLink
            key={item.key}
            item={item}
            isActive={active === item.key}
            collapsed={collapsed}
          />
        ))}
      </SidebarSection>

      <SidebarSection title="OPERATIONS" collapsed={collapsed}>
        {Object.values(OPERATIONS_NAV).map((item) => (
          <SidebarLink
            key={item.key}
            item={item}
            isActive={active === item.key}
            collapsed={collapsed}
          />
        ))}
      </SidebarSection>

      <SidebarSection title="GOVERNANCE" collapsed={collapsed}>
        {Object.values(GOVERNANCE_NAV).map((item) => (
          <SidebarLink
            key={item.key}
            item={item}
            isActive={active === item.key}
            collapsed={collapsed}
          />
        ))}
      </SidebarSection>

      <SidebarSection title="TOOLS" collapsed={collapsed}>
        {Object.values(TOOLS_NAV).map((item) => (
          <SidebarLink
            key={item.key}
            item={item}
            isActive={active === item.key}
            collapsed={collapsed}
          />
        ))}
      </SidebarSection>
    </aside>
  );
}

function SidebarSection({
  title,
  collapsed,
  children,
}: {
  title: string;
  collapsed: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="mt-2 border-t border-border pt-2">
      {!collapsed && (
        <div className="px-3 pb-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </div>
      )}
      <ul className="flex flex-col">{children}</ul>
    </div>
  );
}

function SidebarLink<R extends Route>({
  item,
  isActive,
  collapsed,
}: {
  item: NavItem<R>;
  isActive: boolean;
  collapsed: boolean;
}) {
  const Icon = item.icon;
  return (
    <li>
      <a
        href={item.href}
        title={item.label}
        aria-current={isActive ? "page" : undefined}
        className={`mx-1 my-0.5 flex items-center gap-2 rounded px-2 py-1.5 text-sm transition-colors ${
          isActive
            ? "bg-accent/10 text-accent"
            : "text-slate-300 hover:bg-bg hover:text-accent"
        }`}
        data-testid={`sidebar-link-${item.key}`}
      >
        <Icon className="h-4 w-4 shrink-0" />
        {!collapsed && <span className="truncate">{item.label}</span>}
      </a>
    </li>
  );
}

