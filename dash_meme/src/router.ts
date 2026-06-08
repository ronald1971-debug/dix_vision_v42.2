import { useEffect, useState } from "react";

/**
 * Combined router for dash_meme with full dashboard2026 feature parity.
 * Includes all system routes from dashboard2026 plus meme-specific routes.
 */

// Asset routes from dashboard2026
export type AssetRoute =
  | "spot"
  | "perps"
  | "dex"
  | "forex"
  | "stocks"
  | "nft";

// System routes from dashboard2026
export type SystemRoute =
  | "operator"
  | "credentials"
  | "chat"
  | "indira"
  | "dyon"
  | "observatory"
  | "testing"
  | "onchain"
  | "ai"
  | "orderflow"
  | "governance"
  | "risk"
  | "charting"
  | "market"
  | "positions"
  | "trading"
  | "plugins"
  | "syshealth"
  | "alerts"
  | "audit"
  | "scout"
  | "strategies"
  | "memory"
  | "fabric"
  | "simulation"
  | "signals"
  | "forms"
  | "adapters"
  | "ledger"
  | "security"
  | "hazards";

// Meme-specific routes
export type MemeRoute =
  | "explorer"      // landing — Pair Explorer (chart + audit + holders)
  | "pools"         // Pool Explorer
  | "bigswap"       // Big Swap Explorer (large tx feed)
  | "multichart"    // 2x2 / 4x1 multi-pair chart grid
  | "trade"         // manual / semi-auto / full-auto order entry
  | "copy"          // CopyTrading — wallet allowlist + mirrors
  | "sniper"        // Sniper — pre-launch / migration queue
  | "multiswap"     // multi-pair execution batching
  | "wallet"        // Wallet Info — balances + history
  | "stats";        // global stats — gainers / losers / hot / new

export type Route = AssetRoute | SystemRoute | MemeRoute;

const ASSET_ROUTES: readonly AssetRoute[] = [
  "spot",
  "perps",
  "dex",
  "forex",
  "stocks",
  "nft",
];

const SYSTEM_ROUTES: readonly SystemRoute[] = [
  "operator",
  "plugins",
  "credentials",
  "chat",
  "indira",
  "dyon",
  "observatory",
  "testing",
  "onchain",
  "ai",
  "orderflow",
  "governance",
  "risk",
  "charting",
  "market",
  "positions",
  "trading",
  "syshealth",
  "alerts",
  "audit",
  "scout",
  "strategies",
  "memory",
  "fabric",
  "simulation",
  "signals",
  "forms",
  "adapters",
  "ledger",
  "security",
  "hazards",
];

const MEME_ROUTES: readonly MemeRoute[] = [
  "explorer",
  "pools",
  "bigswap",
  "multichart",
  "trade",
  "copy",
  "sniper",
  "multiswap",
  "wallet",
  "stats",
];

const ALL_ROUTES: readonly Route[] = [...ASSET_ROUTES, ...SYSTEM_ROUTES, ...MEME_ROUTES];

/**
 * Default landing route - meme explorer
 */
export const DEFAULT_ROUTE: Route = "explorer";

export function isAssetRoute(route: Route): route is AssetRoute {
  return (ASSET_ROUTES as readonly string[]).includes(route);
}

export function isSystemRoute(route: Route): route is SystemRoute {
  return (SYSTEM_ROUTES as readonly string[]).includes(route);
}

export function isMemeRoute(route: Route): route is MemeRoute {
  return (MEME_ROUTES as readonly string[]).includes(route);
}

function parseRoute(hash: string): Route {
  const cleaned = hash
    .replace(/^#\/?/, "")
    .replace(/^popout\//, "")
    .split("/")[0] ?? "";
  if (cleaned === "") return DEFAULT_ROUTE;
  for (const route of ALL_ROUTES) {
    if (cleaned === route) return route;
  }
  return DEFAULT_ROUTE;
}

export function parseRoute(hash: string): Route {
  const cleaned = hash
    .replace(/^#\/?/, "")
    .replace(/^popout\//, "")
    .trim();
  if (cleaned === "") return DEFAULT_ROUTE;
  for (const route of ALL_ROUTES) {
    if (cleaned === route) return route;
  }
  return DEFAULT_ROUTE;
}

export function isPopoutRoute(hash: string): boolean {
  return hash.startsWith("#/popout/");
}

export function useHashRoute(): Route {
  const [route, setRoute] = useState<Route>(() =>
    parseRoute(window.location.hash),
  );
  useEffect(() => {
    const handler = () => setRoute(parseRoute(window.location.hash));
    window.addEventListener("hashchange", handler);
    return () => window.removeEventListener("hashchange", handler);
  }, []);
  return route;
}

export function useIsPopout(): boolean {
  const [popout, setPopout] = useState<boolean>(() =>
    isPopoutRoute(window.location.hash),
  );
  useEffect(() => {
    const handler = () => setPopout(isPopoutRoute(window.location.hash));
    window.addEventListener("hashchange", handler);
    return () => window.removeEventListener("hashchange", handler);
  }, []);
  return popout;
}

export function navigate(route: Route, suffix = "") {
  window.location.hash = `#/${route}${suffix}`;
}

// Optional sub-state in the URL hash, e.g. `#/explorer/SOL/BONK`.
export function useHashSuffix(): string {
  const [suffix, setSuffix] = useState<string>(() =>
    extractSuffix(window.location.hash),
  );
  useEffect(() => {
    const onHash = () => setSuffix(extractSuffix(window.location.hash));
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);
  return suffix;
}

function extractSuffix(hash: string): string {
  const parts = hash.replace(/^#\/?/, "").split("/");
  return parts.slice(1).join("/");
}

export const ASSET_ROUTE_LIST = ASSET_ROUTES;
export const SYSTEM_ROUTE_LIST = SYSTEM_ROUTES;
export const MEME_ROUTE_LIST = MEME_ROUTES;