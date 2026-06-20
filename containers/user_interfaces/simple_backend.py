"""
Simplified Backend for DIX VISION Dashboard
Minimal API server to support dashboard development
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

app = FastAPI(title="DIX VISION Dashboard API - Simplified Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Simple Data Models
# ============================================================================

class ModeSnapshot(BaseModel):
    current_mode: str
    legal_targets: list
    is_locked: bool

class ModeResponse(BaseModel):
    mode: ModeSnapshot

class OperatorSummaryResponse(BaseModel):
    mode: ModeSnapshot
    engines: list
    strategies: dict
    memecoin: dict
    decision_chain_count: int

class TradingAllowedResponse(BaseModel):
    trading_allowed: bool
    development_enabled: bool
    mode: Optional[str]

class SystemHealthResponse(BaseModel):
    components: list
    status: str

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/dashboard/mode", response_model=ModeSnapshot)
async def get_dashboard_mode():
    """Get dashboard mode"""
    return ModeSnapshot(
        current_mode="MANUAL",
        legal_targets=["MANUAL", "SEMI_AUTO", "FULL_AUTO"],
        is_locked=False
    )

@app.get("/api/operator/summary", response_model=OperatorSummaryResponse)
async def get_operator_summary():
    """Get operator summary"""
    return OperatorSummaryResponse(
        mode=ModeSnapshot(
            current_mode="MANUAL",
            legal_targets=["MANUAL", "SEMI_AUTO", "FULL_AUTO"],
            is_locked=False
        ),
        engines=[
            {"engine_name": "execution", "bucket": "alive", "detail": "Development mode active", "plugin_count": 0},
            {"engine_name": "governance", "bucket": "alive", "detail": "Development mode active", "plugin_count": 0},
            {"engine_name": "learning", "bucket": "alive", "detail": "Development mode active", "plugin_count": 0}
        ],
        strategies={"proposed": 0, "canary": 0, "live": 0, "retired": 0, "failed": 0},
        memecoin={"enabled": False, "killed": False, "summary": "Not configured in development"},
        decision_chain_count=0
    )

@app.get("/api/operator/policy-hash")
async def get_policy_hash():
    """Get policy hash"""
    return {"policy_hash": "dev-simplified-backend-v1"}

@app.get("/api/operator/trading-allowed", response_model=TradingAllowedResponse)
async def get_trading_allowed():
    """Get trading allowed status"""
    return TradingAllowedResponse(
        trading_allowed=False,
        development_enabled=True,
        mode="MANUAL"
    )

@app.post("/api/operator/trading-allowed")
async def set_trading_allowed(enabled: bool):
    """Set trading allowed status"""
    return TradingAllowedResponse(
        trading_allowed=enabled,
        development_enabled=True,
        mode="MANUAL"
    )

@app.get("/api/execution/adapters")
async def get_adapters():
    """Get execution adapters"""
    return {
        "count": 0,
        "adapters": []
    }

@app.get("/api/syshealth")
async def get_syshealth():
    """Get system health"""
    return {
        "components": [
            {"name": "frontend", "status": "ok", "detail": "Simplified backend active"},
            {"name": "backend", "status": "ok", "detail": "Simplified API running"},
            {"name": "database", "status": "degraded", "detail": "Not configured in simplified mode"}
        ],
        "ts_utc": datetime.now().isoformat()
    }

@app.get("/api/cognitive/stream")
async def cognitive_stream():
    """Cognitive stream endpoint (SSE placeholder)"""
    return {"message": "Cognitive stream endpoint - simplified version"}

@app.get("/api/system/status")
async def system_status():
    """Get overall system status"""
    return {
        "system_mode": "MANUAL",
        "capital_mode": "STANDARD",
        "risk_state": "LOW",
        "governance_state": "ACTIVE",
        "indira_status": "ONLINE",
        "dyon_status": "ONLINE",
        "execution_status": "ACTIVE",
        "kill_switch_armed": False
    }

# ============================================================================
# Root endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DIX VISION Dashboard API - Simplified Backend",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "dashboard_mode": "/api/dashboard/mode",
            "operator_summary": "/api/operator/summary",
            "policy_hash": "/api/operator/policy-hash",
            "trading_allowed": "/api/operator/trading-allowed",
            "adapters": "/api/execution/adapters",
            "syshealth": "/api/syshealth",
            "cognitive_stream": "/api/cognitive/stream",
            "system_status": "/api/system/status"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)