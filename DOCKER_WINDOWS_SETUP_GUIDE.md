# Docker Desktop Windows Setup Guide for DIX VISION

**Status:** Setup Required  
**Platform:** Windows 10/11  
**Purpose:** Enable Docker containerization for DIX VISION external repo integration

---

## Step 1: Download Docker Desktop

### Option A: Download via PowerShell (Automated)
```powershell
# Download Docker Desktop for Windows
$dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$installerPath = "$env:USERPROFILE\Downloads\DockerDesktopInstaller.exe"

Write-Host "Downloading Docker Desktop..."
Invoke-WebRequest -Uri $dockerUrl -OutFile $installerPath -UseBasicParsing

Write-Host "Download complete: $installerPath"
```

### Option B: Manual Download
1. Visit: https://www.docker.com/products/docker-desktop/
2. Click "Download for Windows"
3. Save the installer to your Downloads folder

---

## Step 2: Install Docker Desktop

### Automated Installation:
```powershell
# Run the installer silently
Start-Process -FilePath "$env:USERPROFILE\Downloads\DockerDesktopInstaller.exe" -ArgumentList "install --quiet" -Wait

Write-Host "Docker Desktop installation complete"
```

### Manual Installation:
1. Double-click `Docker Desktop Installer.exe`
2. Follow the installation wizard
3. Ensure "Add shortcut to desktop" is checked
4. Click "Ok" to install

---

## Step 3: Configure Docker Desktop

### Initial Setup:
1. **Launch Docker Desktop** from desktop shortcut
2. **Sign in or create account** (can skip for now)
3. **Accept terms and conditions**
4. **Choose WSL 2 backend** (recommended for Windows)
5. **Click "Finish" to complete setup**

### System Requirements Check:
```powershell
# Check if virtualization is enabled
systeminfo | Select-String "Virtualization"

# Check WSL 2 installation
wsl --status
```

---

## Step 4: Start Docker Desktop

### Manual Start:
- Double-click Docker Desktop icon
- Wait for Docker engine to start (whale icon in system tray)

### PowerShell Start:
```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### Verify Docker is Running:
```powershell
# Wait 30 seconds for Docker to start
Start-Sleep -Seconds 30

# Check Docker version
docker --version

# Check Docker is running
docker ps
```

---

## Step 5: Verify Docker Installation

### Test Docker:
```powershell
# Run test container
docker run hello-world

# Expected output:
# Hello from Docker!
# This message shows that your installation appears to be working correctly.
```

### Check Docker Info:
```powershell
docker info
```

---

## Step 6: Configure Docker for DIX VISION

### Create Docker Directory Structure:
```powershell
cd C:\dix_vision_v42.2

# Create container directories
New-Item -ItemType Directory -Path "containers\base" -Force
New-Item -ItemType Directory -Path "containers\trading" -Force  
New-Item -ItemType Directory -Path "containers\cognitive" -Force
New-Item -ItemType Directory -Path "containers\automation" -Force
New-Item -ItemType Directory -Path "containers\data" -Force
New-Item -ItemType Directory -Path "containers\monitoring" -Force
New-Item -ItemType Directory -Path "containers\workflow" -Force
New-Item -ItemType Directory -Path "containers\api" -Force
New-Item -ItemType Directory -Path "containers\dashboard" -Force
```

### Create Base Dockerfile:
```powershell
# Create base Python Dockerfile
@"
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
  CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
"@ | Out-File -FilePath "containers\base\Dockerfile" -Encoding utf8

Write-Host "Base Dockerfile created"
```

---

## Step 7: Create docker-compose.yml

```powershell
@"
version: '3.8'

services:
  # ========================================
  # CORE DIX VISION SERVICES
  # ========================================
  
  governance:
    build:
      context: .
      dockerfile: governance/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPERATOR_AUTHORITY=true
      - MODE=SAFE
      - PYTHONUNBUFFERED=1
    volumes:
      - ./governance:/app/governance
      - ./shared_infrastructure:/app/shared_infrastructure
      - ./config:/app/config
    restart: unless-stopped
    networks:
      - dixvision-network

  indira-brain:
    build:
      context: .
      dockerfile: indira_cognitive/Dockerfile
    ports:
      - "8002:8002"
    environment:
      - GOVERNANCE_URL=http://governance:8000
      - PYTHONUNBUFFERED=1
    volumes:
      - ./indira_cognitive:/app/indira_cognitive
      - ./shared_infrastructure:/app/shared_infrastructure
      - ./governance:/app/governance
    depends_on:
      - governance
    restart: unless-stopped
    networks:
      - dixvision-network

  dyon-brain:
    build:
      context: .
      dockerfile: dyon_cognitive/Dockerfile
    ports:
      - "8003:8003"
    environment:
      - GOVERNANCE_URL=http://governance:8000
      - PYTHONUNBUFFERED=1
    volumes:
      - ./dyon_cognitive:/app/dyon_cognitive
      - ./shared_infrastructure:/app/shared_infrastructure
      - ./governance:/app/governance
    depends_on:
      - governance
    restart: unless-stopped
    networks:
      - dixvision-network

  coordination-layer:
    build:
      context: .
      dockerfile: coordination_layer/Dockerfile
    ports:
      - "8004:8004"
    environment:
      - GOVERNANCE_URL=http://governance:8000
      - PYTHONUNBUFFERED=1
    volumes:
      - ./coordination_layer:/app/coordination_layer
      - ./shared_infrastructure:/app/shared_infrastructure
      - ./governance:/app/governance
    depends_on:
      - governance
      - redis-service
    restart: unless-stopped
    networks:
      - dixvision-network

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

  influxdb-service:
    image: influxdb:2.0
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=admin_secure_password
      - DOCKER_INFLUXDB_INIT_ORG=dixvision
      - DOCKER_INFLUXDB_INIT_BUCKET=market_data
    volumes:
      - influxdb-data:/var/lib/influxdb2
    restart: unless-stopped
    networks:
      - dixvision-network

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
      - '--web.console.libraries=/etc/prometheus/console_libraries'
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
  influxdb-data:
  prometheus-data:
  grafana-data:

networks:
  dixvision-network:
    driver: bridge
"@ | Out-File -FilePath "docker-compose.yml" -Encoding utf8

Write-Host "docker-compose.yml created"
```

---

## Step 8: Create Monitoring Configuration

```powershell
# Create monitoring directory
New-Item -ItemType Directory -Path "monitoring" -Force

# Create Prometheus configuration
@"
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'governance'
    static_configs:
      - targets: ['governance:8000']
  
  - job_name: 'indira-brain'
    static_configs:
      - targets: ['indira-brain:8002']
  
  - job_name: 'dyon-brain'
    static_configs:
      - targets: ['dyon-brain:8003']
  
  - job_name: 'coordination-layer'
    static_configs:
      - targets: ['coordination-layer:8004']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-service:6379']
  
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgresql-service:5432']
"@ | Out-File -FilePath "monitoring\prometheus.yml" -Encoding utf8

Write-Host "Prometheus configuration created"
```

---

## Step 9: Create .dockerignore

```powershell
@"
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
"@ | Out-File -FilePath ".dockerignore" -Encoding utf8

Write-Host ".dockerignore created"
```

---

## Step 10: Create Governance Wrapper Template

```powershell
# Create governance wrappers directory
New-Item -ItemType Directory -Path "governance\wrappers" -Force

# Create base governance wrapper
@"
"""
Base Governance Wrapper for External Container Services
All external services must use this wrapper for governance compliance
"""

import httpx
import os
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class GovernanceDecision(BaseModel):
    """Governance decision response"""
    approved: bool
    reason: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    operator_override: bool = False

class BaseContainerGovernanceWrapper:
    """
    Base wrapper for all external container services
    Ensures governance compliance for all operations
    """
    
    def __init__(self):
        self.governance_url = os.getenv('GOVERNANCE_URL', 'http://governance:8000')
        self.timeout = httpx.Timeout(10.0)
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
    async def validate_operation(self, operation_data: Dict[str, Any]) -> GovernanceDecision:
        """
        Validate operation with governance before execution
        All external operations must call this first
        """
        try:
            response = await self.client.post(
                f"{self.governance_url}/api/validate",
                json=operation_data
            )
            response.raise_for_status()
            return GovernanceDecision(**response.json())
        except httpx.HTTPError as e:
            logger.error(f"Governance validation failed: {e}")
            # Fail closed - reject if governance unavailable
            return GovernanceDecision(
                approved=False,
                reason="Governance service unavailable"
            )
    
    async def log_operation(self, operation_data: Dict[str, Any], result: Any):
        """Log all operations for audit trail"""
        try:
            await self.client.post(
                f"{self.governance_url}/api/log",
                json={
                    'operation': operation_data,
                    'result': str(result),
                    'timestamp': httpx._time.time()
                }
            )
        except httpx.HTTPError as e:
            logger.error(f"Failed to log operation: {e}")
    
    async def execute_with_governance(self, operation: str, params: Dict[str, Any]):
        """
        Template method for executing operations with governance oversight
        External services must implement this pattern
        """
        # Step 1: Validate with governance
        decision = await self.validate_operation({
            'operation': operation,
            'params': params
        })
        
        if not decision.approved and not decision.operator_override:
            raise PermissionError(f"Operation rejected by governance: {decision.reason}")
        
        # Step 2: Execute the operation (to be implemented by subclass)
        result = await self._execute_operation(operation, params, decision.conditions)
        
        # Step 3: Log the operation
        await self.log_operation({'operation': operation, 'params': params}, result)
        
        return result
    
    async def _execute_operation(self, operation: str, params: Dict[str, Any], conditions: Optional[Dict]) -> Any:
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_operation")
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
"@ | Out-File -FilePath "governance\wrappers\base_wrapper.py" -Encoding utf8

Write-Host "Base governance wrapper created"
```

---

## Quick Start Commands

### Complete Setup Script:
```powershell
# Run this entire setup at once
cd C:\dix_vision_v42.2

# 1. Create directory structure
New-Item -ItemType Directory -Path "containers\base" -Force
New-Item -ItemType Directory -Path "containers\trading" -Force
New-Item -ItemType Directory -Path "containers\cognitive" -Force
New-Item -ItemType Directory -Path "containers\automation" -Force
New-Item -ItemType Directory -Path "containers\data" -Force
New-Item -ItemType Directory -Path "containers\monitoring" -Force
New-Item -ItemType Directory -Path "containers\workflow" -Force
New-Item -ItemType Directory -Path "containers\api" -Force
New-Item -ItemType Directory -Path "containers\dashboard" -Force
New-Item -ItemType Directory -Path "monitoring" -Force
New-Item -ItemType Directory -Path "governance\wrappers" -Force

Write-Host "Directory structure created successfully"

# 2. Test Docker
docker --version
docker ps
```

---

## Troubleshooting

### Docker Desktop won't start:
1. Ensure WSL 2 is installed: `wsl --install`
2. Enable virtualization in BIOS
3. Restart Docker Desktop
4. Check Windows Hyper-V is enabled

### Permission errors:
1. Run PowerShell as Administrator
2. Check Docker Desktop is running
3. Verify Docker daemon is started

### Network issues:
1. Check Windows Firewall settings
2. Ensure Docker can access internet
3. Verify Docker network is created: `docker network ls`

---

## Next Steps After Setup

Once Docker is running:
1. Test basic container: `docker run hello-world`
2. Build base images: `docker-compose build`
3. Start core services: `docker-compose up -d governance redis-service`
4. Check logs: `docker-compose logs -f`
5. Stop services: `docker-compose down`

---

**Document Status:** Docker Setup Guide Complete  
**Platform:** Windows 10/11  
**Next Action:** Execute setup commands  
**Maintained By:** DIX VISION Development Team  
**Date:** 2026-06-12
