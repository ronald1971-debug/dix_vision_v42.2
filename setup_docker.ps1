# Docker Setup Script for DIX VISION
# Run this script in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DIX VISION Docker Setup" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Docker is installed
Write-Host "Step 1: Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    exit 1
}

# Step 2: Check if Docker is running
Write-Host "Step 2: Checking if Docker is running..." -ForegroundColor Yellow
try {
    $dockerPs = docker ps 2>$null
    Write-Host "Docker is running successfully" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    Write-Host "1. Launch Docker Desktop from your desktop" -ForegroundColor Yellow
    Write-Host "2. Wait for it to start (whale icon in system tray)" -ForegroundColor Yellow
    Write-Host "3. Run this script again" -ForegroundColor Yellow
    exit 1
}

# Step 3: Test Docker with hello-world
Write-Host "Step 3: Testing Docker with hello-world container..." -ForegroundColor Yellow
try {
    docker run --rm hello-world
    Write-Host "Docker test successful!" -ForegroundColor Green
} catch {
    Write-Host "Docker test failed. Check Docker Desktop status." -ForegroundColor Red
    exit 1
}

# Step 4: Create container directory structure
Write-Host "Step 4: Creating container directory structure..." -ForegroundColor Yellow
$containerDirs = @(
    "containers\base",
    "containers\trading", 
    "containers\cognitive",
    "containers\automation",
    "containers\data",
    "containers\monitoring",
    "containers\workflow",
    "containers\api",
    "containers\dashboard",
    "monitoring",
    "governance\wrappers"
)

foreach ($dir in $containerDirs) {
    $fullPath = Join-Path $PSScriptRoot $dir
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "Exists: $dir" -ForegroundColor Gray
    }
}

# Step 5: Create base Dockerfile
Write-Host "Step 5: Creating base Python Dockerfile..." -ForegroundColor Yellow
$baseDockerfile = @"
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install common Python packages
RUN pip install --no-cache-dir \
    pydantic==2.5.0 \
    requests==2.31.0 \
    httpx==0.25.0 \
    python-dotenv==1.0.0 \
    pyyaml==6.0.1

# Create directories for governance integration
RUN mkdir -p /app/governance /app/shared /app/config

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8000)); s.close()" || exit 1

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
"@

Set-Content -Path "containers\base\Dockerfile" -Value $baseDockerfile
Write-Host "Base Dockerfile created" -ForegroundColor Green

# Step 6: Create docker-compose.yml
Write-Host "Step 6: Creating docker-compose.yml..." -ForegroundColor Yellow
$dockerCompose = @"
version: '3.8'

services:
  # ========================================
  # DATA SERVICES (Infrastructure)
  # ========================================
  
  redis-service:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    networks:
      - dixvision-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  postgresql-service:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=dixvision
      - POSTGRES_USER=dixvision
      - POSTGRES_PASSWORD=dixvision_secure_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - dixvision-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dixvision"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ========================================
  # MONITORING SERVICES
  # ========================================
  
  prometheus-service:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
    networks:
      - dixvision-network

  grafana-service:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin_secure_password
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped
    networks:
      - dixvision-network

volumes:
  redis-data:
  postgres-data:
  prometheus-data:
  grafana-data:

networks:
  dixvision-network:
    driver: bridge
"@

Set-Content -Path "docker-compose.yml" -Value $dockerCompose
Write-Host "docker-compose.yml created" -ForegroundColor Green

# Step 7: Create Prometheus configuration
Write-Host "Step 7: Creating Prometheus configuration..." -ForegroundColor Yellow
$prometheusConfig = @"
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-service:6379']
  
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgresql-service:5432']
"@

Set-Content -Path "monitoring\prometheus.yml" -Value $prometheusConfig
Write-Host "Prometheus configuration created" -ForegroundColor Green

# Step 8: Create .dockerignore
Write-Host "Step 8: Creating .dockerignore..." -ForegroundColor Yellow
$dockerignore = @"
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Documentation
*.md
docs/

# Tests
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
logs/

# External data
data/
external/
temp/
tmp/

# CI/CD
.github/
.gitlab-ci.yml

# Docker
Dockerfile
docker-compose.yml
.dockerignore
"@

Set-Content -Path ".dockerignore" -Value $dockerignore
Write-Host ".dockerignore created" -ForegroundColor Green

# Step 9: Create governance wrapper template
Write-Host "Step 9: Creating governance wrapper template..." -ForegroundColor Yellow
$governanceWrapper = @"
"""
Base Governance Wrapper for External Container Services
All external services must use this wrapper for governance compliance
"""

import httpx
import os
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class GovernanceDecision(BaseModel):
    approved: bool
    reason: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None

class BaseContainerGovernanceWrapper:
    Base wrapper for all external container services
    Ensures governance compliance for all operations
    
    def __init__(self):
        self.governance_url = os.getenv('GOVERNANCE_URL', 'http://governance:8000')
        self.timeout = httpx.Timeout(10.0)
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
    async def validate_operation(self, operation_data: Dict[str, Any]) -> GovernanceDecision:
        Validate operation with governance before execution
        try:
            response = await self.client.post(
                f"{self.governance_url}/api/validate",
                json=operation_data
            )
            response.raise_for_status()
            return GovernanceDecision(**response.json())
        except httpx.HTTPError as e:
            logger.error(f"Governance validation failed: {e}")
            return GovernanceDecision(approved=False, reason="Governance service unavailable")
    
    async def execute_with_governance(self, operation: str, params: Dict[str, Any]):
        Execute operation with governance oversight
        decision = await self.validate_operation({'operation': operation, 'params': params})
        
        if not decision.approved:
            raise PermissionError(f"Operation rejected: {decision.reason}")
        
        result = await self._execute_operation(operation, params, decision.conditions)
        return result
    
    async def _execute_operation(self, operation: str, params: Dict[str, Any], conditions: Optional[Dict]) -> Any:
        Override this method in subclasses
        raise NotImplementedError("Subclasses must implement _execute_operation")
"@

Set-Content -Path "governance\wrappers\base_wrapper.py" -Value $governanceWrapper
Write-Host "Governance wrapper template created" -ForegroundColor Green

# Step 10: Build and test containers
Write-Host "Step 10: Building Docker images..." -ForegroundColor Yellow
try {
    docker-compose build
    Write-Host "Docker images built successfully" -ForegroundColor Green
} catch {
    Write-Host "Docker build failed. Check configuration." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start services: docker-compose up -d" -ForegroundColor White
Write-Host "2. Check status: docker-compose ps" -ForegroundColor White
Write-Host "3. View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "4. Stop services: docker-compose down" -ForegroundColor White
Write-Host ""
