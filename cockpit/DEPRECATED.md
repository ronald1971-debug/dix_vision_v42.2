# cockpit/ - DEPRECATED

This directory contains the legacy cockpit dashboard frontend and backend.

## Status: DEPRECATED ⚠️

The cockpit backend has been migrated to `ui/cockpit_routes.py` and is now served by the canonical `ui/server.py` FastAPI app.

The static frontend in `cockpit/static/` is legacy and should use dashboard2026/ instead.

## Migration Path

- **Backend:** Already migrated to `ui/cockpit_routes.py` ✅
- **Frontend:** Use `dashboard2026/` instead ✅
- **Meme Dashboard:** Use `dash_meme/` for meme-specific trading ✅

## Canonical Production Entry Point

```bash
uvicorn ui.server:app   # Serves React dashboard at /dash2/ + ALL routes including cockpit
```

## Legacy Entry Point (Still Functional)

```bash
uvicorn cockpit:app     # Serves only cockpit endpoints, no React dashboard
```

**Note:** The legacy entry point is retained for backward compatibility but is no longer the recommended deployment method.

## Removal Timeline

After a confidence period (e.g., 6 weeks), the cockpit/ directory can be:
1. Removed entirely if no legacy deployments exist
2. Kept as-is if legacy deployments require it

**Last Updated:** 2026-06-08