export interface ComponentStatus {
  name: string;
  status: "ok" | "degraded" | "error" | "unknown";
  detail?: string;
  latency_ms?: number;
}

export interface SysHealthPayload {
  components: ComponentStatus[];
  dead_man?: { active: boolean; last_heartbeat_utc: string; ttl_sec: number };
  latency_guard?: { breached: boolean; p99_ms: number; threshold_ms: number };
  ts_utc?: string;
}

export async function fetchSysHealth(signal?: AbortSignal): Promise<SysHealthPayload> {
  try {
    const BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");
    const res = await fetch(`${BASE}/api/syshealth`, {
      signal,
      headers: { Accept: "application/json" },
    });
    if (!res.ok) {
      throw new Error(`GET /api/syshealth failed: ${res.status} ${res.statusText}`);
    }
    return (await res.json()) as SysHealthPayload;
  } catch (error) {
    // Return fallback health status in development when backend is unavailable
    if (process.env.NODE_ENV === 'development') {
      return {
        components: [
          { name: 'frontend', status: 'ok', detail: 'Development mode active' },
          { name: 'api', status: 'degraded', detail: 'Backend not running (development)' }
        ],
        ts_utc: new Date().toISOString()
      };
    }
    throw error;
  }
}
