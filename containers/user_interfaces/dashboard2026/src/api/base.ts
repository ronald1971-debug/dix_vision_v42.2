/**
 * Shared API-base helper. Every fetch / EventSource in the SPA goes
 * through this so the `VITE_API_BASE` env var is honoured uniformly.
 *
 * Docker-aware configuration:
 * - In Docker: VITE_API_BASE should point to backend container (e.g., "http://dix-vision-backend:8080")
 * - Local: Empty default for relative URLs or specific local backend URL
 * - CDN: External API host for CDN-hosted SPAs
 */
export const API_BASE = (import.meta.env.VITE_API_BASE ?? "").replace(
  /\/$/,
  "",
);

export function apiUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  if (!path.startsWith("/")) {
    return `${API_BASE}/${path}`;
  }
  return `${API_BASE}${path}`;
}

/**
 * Get WebSocket URL based on current environment
 * Handles Docker container networking and local development
 */
export function wsUrl(path: string): string {
  const wsBase = API_BASE.replace(/^http/, 'ws');
  const wsPath = path.startsWith('/') ? path : `/${path}`;
  return `${wsBase}${wsPath}`;
}
