"""
Simplified FastAPI Server for Dashboard Integration Testing
Includes only the dashboard API routes without full DIX VISION dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dashboard_test_server")

# Create FastAPI app
app = FastAPI(
    title="Dashboard2026 Integration Test Server",
    description="Simplified server for testing dashboard API integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dashboard_test_server"}

# Import dashboard API routers
try:
    from dashboard2026.api.indira_intelligence_api import router as indira_router
    from dashboard2026.api.markets_api import router as markets_router
    
    app.include_router(indira_router, tags=["INDIRA Intelligence"])
    app.include_router(markets_router, tags=["Unified Markets"])
    
    logger.info("Dashboard API routers loaded successfully")
except ImportError as e:
    logger.error(f"Failed to load dashboard API routers: {e}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Dashboard2026 Integration Test Server",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "indira": "/api/indira/*",
            "markets": "/api/markets/*"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Dashboard Test Server on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
