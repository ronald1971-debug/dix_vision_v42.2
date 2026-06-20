import type {
  OperatorActionResponse,
  OperatorModeRequest,
  OperatorSummaryResponse,
  OperatorUnlockRequest,
} from "@/types/generated/api";

const BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");

export async function fetchOperatorSummary(
  signal?: AbortSignal,
): Promise<OperatorSummaryResponse> {
  const BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");
  
  try {
    const res = await fetch(`${BASE}/api/operator/summary`, {
      signal,
      headers: { Accept: "application/json" },
    });
    if (!res.ok) {
      throw new Error(
        `GET /api/operator/summary failed: ${res.status} ${res.statusText}`,
      );
    }
    return (await res.json()) as OperatorSummaryResponse;
  } catch (error) {
    // Return fallback summary in development when backend is unavailable
    if (process.env.NODE_ENV === 'development') {
      return {
        mode: {
          current_mode: 'MANUAL',
          legal_targets: ['MANUAL', 'SEMI_AUTO', 'FULL_AUTO'],
          is_locked: false
        },
        engines: [
          { engine_name: 'execution', bucket: 'alive', detail: 'Development mode active', plugin_count: 0 },
          { engine_name: 'governance', bucket: 'alive', detail: 'Development mode active', plugin_count: 0 },
          { engine_name: 'learning', bucket: 'alive', detail: 'Development mode active', plugin_count: 0 }
        ],
        strategies: {
          proposed: 0,
          canary: 0,
          live: 0,
          retired: 0,
          failed: 0
        },
        memecoin: {
          enabled: false,
          killed: false,
          summary: 'Not configured in development'
        },
        decision_chain_count: 0
      } as OperatorSummaryResponse;
    }
    throw error;
  }
}

export interface KillRequestBody {
  reason: string;
  requestor?: string;
}

export async function postOperatorKill(
  body: KillRequestBody,
): Promise<OperatorActionResponse> {
  const res = await fetch(`${BASE}/api/operator/action/kill`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      reason: body.reason,
      requestor: body.requestor ?? "operator",
    }),
  });
  if (!res.ok) {
    throw new Error(
      `POST /api/operator/action/kill failed: ${res.status} ${res.statusText}`,
    );
  }
  return (await res.json()) as OperatorActionResponse;
}

/**
 * POST /api/operator/action/unlock — request the
 * `LOCKED → SAFE` transition through the governance bridge.
 *
 * Mirrors the kill route shape: typed request, decision-bearing
 * `OperatorActionResponse` (approved + summary + decision +
 * audit_id) so the dashboard can show the bridge's reason for
 * approval or refusal.
 */
export async function postOperatorUnlock(
  body: OperatorUnlockRequest = {},
): Promise<OperatorActionResponse> {
  const res = await fetch(`${BASE}/api/operator/action/unlock`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      reason: body.reason ?? "operator unlock",
      requestor: body.requestor ?? "operator",
    }),
  });
  if (!res.ok) {
    throw new Error(
      `POST /api/operator/action/unlock failed: ${res.status} ${res.statusText}`,
    );
  }
  return (await res.json()) as OperatorActionResponse;
}

/**
 * POST /api/operator/action/mode — request a `REQUEST_MODE`
 * transition (e.g. `SAFE → PAPER`, `LIVE → AUTO`). Hardening-S1
 * item 8 edges (`SAFE → PAPER` and `LIVE → AUTO`) require the
 * full consent envelope; other forward edges accept just
 * `target_mode + reason`.
 */
export interface TradingAllowedResponse {
  trading_allowed: boolean;
  development_enabled: boolean;
  mode: string | null;
}

export async function fetchTradingAllowed(
  signal?: AbortSignal,
): Promise<TradingAllowedResponse> {
  const BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");
  
  try {
    const res = await fetch(`${BASE}/api/operator/trading-allowed`, {
      signal,
      headers: { Accept: "application/json" },
    });
    if (!res.ok) {
      throw new Error(`GET /api/operator/trading-allowed failed: ${res.status}`);
    }
    return (await res.json()) as TradingAllowedResponse;
  } catch (error) {
    // Return fallback response in development when backend is unavailable
    if (process.env.NODE_ENV === 'development') {
      return {
        trading_allowed: false,
        development_enabled: true,
        mode: 'MANUAL'
      };
    }
    throw error;
  }
}

export async function postTradingAllowed(
  enabled: boolean,
): Promise<TradingAllowedResponse> {
  const res = await fetch(`${BASE}/api/operator/trading-allowed`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ enabled }),
  });
  if (!res.ok) {
    throw new Error(`POST /api/operator/trading-allowed failed: ${res.status}`);
  }
  return (await res.json()) as TradingAllowedResponse;
}

export async function fetchPolicyHash(
  signal?: AbortSignal,
): Promise<string> {
  const BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");
  
  try {
    const res = await fetch(`${BASE}/api/operator/policy-hash`, {
      signal,
      headers: { Accept: "application/json" },
    });
    if (!res.ok) {
      throw new Error(`GET /api/operator/policy-hash failed: ${res.status}`);
    }
    const data = (await res.json()) as { policy_hash: string };
    return data.policy_hash;
  } catch (error) {
    // Return fallback hash in development when backend is unavailable
    if (process.env.NODE_ENV === 'development') {
      return 'dev-fallback-policy-hash-v1';
    }
    throw error;
  }
}

export async function postOperatorMode(
  body: OperatorModeRequest,
): Promise<OperatorActionResponse> {
  const res = await fetch(`${BASE}/api/operator/action/mode`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      target_mode: body.target_mode,
      reason: body.reason ?? "operator mode request",
      requestor: body.requestor ?? "operator",
      operator_authorized: body.operator_authorized ?? false,
      consent_operator_id: body.consent_operator_id ?? "",
      consent_policy_hash: body.consent_policy_hash ?? "",
      consent_nonce: body.consent_nonce ?? "",
      consent_ts_ns: body.consent_ts_ns ?? 0,
    }),
  });
  if (!res.ok) {
    throw new Error(
      `POST /api/operator/action/mode failed: ${res.status} ${res.statusText}`,
    );
  }
  return (await res.json()) as OperatorActionResponse;
}
