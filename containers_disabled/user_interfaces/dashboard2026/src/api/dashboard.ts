/**
 * Read-only fetchers for the `/api/dashboard/...` router (DASH-1).
 * The vanilla `dashboard_routes.py` already exposes these endpoints;
 * the wave-02 SPA consumes them through TanStack Query.
 */

export interface ModeSnapshot {
  current_mode: string;
  legal_targets: string[];
  is_locked: boolean;
}

export interface ModeResponse {
  mode: ModeSnapshot;
}

export async function fetchMode(signal?: AbortSignal): Promise<ModeSnapshot> {
  try {
    const BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");
    const res = await fetch(`${BASE}/api/dashboard/mode`, {
      signal,
      headers: { Accept: "application/json" },
    });
    if (!res.ok) {
      throw new Error(
        `GET /api/dashboard/mode failed: ${res.status} ${res.statusText}`,
      );
    }
    const body = (await res.json()) as ModeResponse;
    return body.mode;
  } catch (error) {
    // Return fallback mode in development when backend is unavailable
    if (process.env.NODE_ENV === 'development') {
      return {
        current_mode: 'MANUAL',
        legal_targets: ['MANUAL', 'SEMI_AUTO', 'FULL_AUTO'],
        is_locked: false
      };
    }
    throw error;
  }
}
