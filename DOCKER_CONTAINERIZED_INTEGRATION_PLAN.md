# DIX VISION v42.2 — Docker Containerized Integration Plan

**Strategy:** Keep DIX VISION core light, external repos as containers  
**Architecture:** Microservices with Docker Compose orchestration  
**Benefits:** Clean core, isolated dependencies, scalable, production-ready  
**Date:** 2026-06-12

---

## Architecture Overview

### Core Principle: Light DIX VISION Core

**DIX VISION Core Contains:**
- Cognitive architecture (INDIRA/DYON brains)
- Governance layer
- Coordination layer
- Core business logic
- Orchestration interfaces
- Configuration management

**External Dependencies (Containerized):**
- Trading libraries (CCXT, etc.)
- Browser automation (Playwright, etc.)
- Cognitive frameworks (LangChain, etc.)
- Data storage (Redis, PostgreSQL, etc.)
- Monitoring (Prometheus, Grafana, etc.)
- All 100 GitHub repositories

---

## Container Architecture

### Service Categories

#### 1. Trading Services
```yaml
ccxt-service:
  image: dixvision/ccxt:latest
  purpose: Unified exchange API
  ports: ["8001:8001"]
  environment:
    - GOVERNANCE_URL=http://governance:8000
```

#### 2. Cognitive Services
```yaml
langchain-service:
  image: dixvision/langchain:latest
  purpose: LLM orchestration
  environment:
    - OPENAI_API_KEY=${OPENAI_KEY}
    - GOVERNANCE_URL=http://governance:8000

transformers-service:
  image: dixvision/transformers:latest
  purpose: NLP and sentiment analysis
  gpu: true
```

#### 3. Automation Services
```yaml
playwright-service:
  image: dixvision/playwright:latest
  purpose: Browser cognitive bridge
  volumes:
    - ./desktop_agent/browser:/app/data

pyautogui-service:
  image: dixvision/pyautogui:latest
  purpose: Desktop cognitive bridge
  # Host access needed for desktop automation
```

#### 4. Data Services
```yaml
redis-service:
  image: redis:alpine
  purpose: FastRiskCache and session storage
  ports: ["6379:6379"]

postgresql-service:
  image: postgres:15
  purpose: Primary database
  volumes:
    - postgres-data:/var/lib/postgresql/data

influxdb-service:
  image: influxdb:2.0
  purpose: Time series market data
  ports: ["8086:8086"]
```

#### 5. Monitoring Services
```yaml
prometheus-service:
  image: prom/prometheus:latest
  purpose: Metrics collection
  ports: ["9090:9090"]
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

grafana-service:
  image: grafana/grafana:latest
  purpose: Monitoring dashboard
  ports: ["3000:3000"]
```

#### 6. Workflow Services
```yaml
celery-service:
  image: dixvision/celery:latest
  purpose: Background task processing
  depends_on:
    - redis-service

airflow-service:
  image: apache/airflow:latest
  purpose: Workflow orchestration
  ports: ["8080:8080"]
```

---

## Docker Compose Structure

### docker-compose.yml
```yaml
version: '3.8'

services:
  # ========================================
  # DIX VISION CORE SERVICES
  # ========================================
  
  governance:
    build: ./governance
    ports: ["8000:8000"]
    environment:
      - OPERATOR_AUTHORITY=true
      - MODE=SAFE
    depends_on:
      - postgres-service
      - redis-service

  indira-brain:
    build: ./indira_cognitive
    ports: ["8002:8002"]
    depends_on:
      - governance
      - ccxt-service
      - langchain-service

  dyon-brain:
    build: ./dyon_cognitive
    ports: ["8003:8003"]
    depends_on:
      - governance
      - postgresql-service

  coordination-layer:
    build: ./coordination_layer
    ports: ["8004:8004"]
    depends_on:
      - governance
      - redis-service

  # ========================================
  # EXTERNAL REPO SERVICES
  # ========================================
  
  # Trading Services
  ccxt-service:
    image: dixvision/ccxt:latest
    build: ./containers/ccxt
    ports: ["8100:8100"]
    environment:
      - GOVERNANCE_URL=http://governance:8000
      - LOG_LEVEL=INFO
    restart: unless-stopped

  vectorbt-service:
    image: dixvision/vectorbt:latest
    build: ./containers/vectorbt
    ports: ["8101:8101"]
    environment:
      - GOVERNANCE_URL=http://governance:8000
    restart: unless-stopped

  # Cognitive Services
  langchain-service:
    image: dixvision/langchain:latest
    build: ./containers/langchain
    ports: ["8200:8200"]
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOVERNANCE_URL=http://governance:8000
    restart: unless-stopped

  transformers-service:
    image: dixvision/transformers:latest
    build: ./containers/transformers
    ports: ["8201:8201"]
    runtime: nvidia  # GPU support
    environment:
      - GOVERNANCE_URL=http://governance:8000
    restart: unless-stopped

  spacy-service:
    image: dixvision/spacy:latest
    build: ./containers/spacy
    ports: ["8202:8202"]
    environment:
      - GOVERNANCE_URL=http://governance:8000
    restart: unless-stopped

  # Automation Services
  playwright-service:
    image: dixvision/playwright:latest
    build: ./containers/playwright
    ports: ["8300:8300"]
    volumes:
      - ./desktop_agent/browser:/app/data
      - /tmp/.X11-unix:/tmp/.X11-unix  # X11 for UI
    environment:
      - DISPLAY=${DISPLAY}
      - GOVERNANCE_URL=http://governance:8000
    restart: unless-stopped

  pyautogui-service:
    image: dixvision/pyautogui:latest
    build: ./containers/pyautogui
    ports: ["8301:8301"]
    volumes:
      - ./desktop_agent/desktop:/app/data
    environment:
      - DISPLAY=${DISPLAY}
      - GOVERNANCE_URL=http://governance:8000
    restart: unless-stopped

  # Data Services
  redis-service:
    image: redis:alpine
    ports: ["6379:6379"]
    volumes:
      - redis-data:/data
    restart: unless-stopped

  postgresql-service:
    image: postgres:15
    ports: ["5432:5432"]
    environment:
      - POSTGRES_DB=dixvision
      - POSTGRES_USER=dixvision
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

  influxdb-service:
    image: influxdb:2.0
    ports: ["8086:8086"]
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUX_PASSWORD}
    volumes:
      - influxdb-data:/var/lib/influxdb2
    restart: unless-stopped

  neo4j-service:
    image: neo4j:5.0
    ports: ["7474:7474", "7687:7687"]
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
    volumes:
      - neo4j-data:/data
    restart: unless-stopped

  # Monitoring Services
  prometheus-service:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    restart: unless-stopped

  grafana-service:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped

  # Workflow Services
  celery-service:
    image: dixvision/celery:latest
    build: ./containers/celery
    depends_on:
      - redis-service
    environment:
      - GOVERNANCE_URL=http://governance:8000
    restart: unless-stopped

  airflow-service:
    image: apache/airflow:2.5.0
    ports: ["8080:8080"]
    environment:
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
      - AIRFLOW__DATABASE__SQLALCHEMY_CONN=postgresql+psycopg2://dixvision:${POSTGRES_PASSWORD}@postgresql-service:5432/dixvision
    volumes:
      - airflow-data:/opt/airflow
    restart: unless-stopped

  # API Services
  fastapi-service:
    image: dixvision/fastapi:latest
    build: ./containers/fastapi
    ports: ["8500:8500"]
    environment:
      - GOVERNANCE_URL=http://governance:8000
    restart: unless-stopped

  graphql-service:
    image: dixvision/graphql:latest
    build: ./containers/graphql
    ports: ["8501:8501"]
    environment:
      - GOVERNANCE_URL=http://governance:8000
    restart: unless-stopped

  # Dashboard Services
  streamlit-service:
    image: dixvision/streamlit:latest
    build: ./containers/streamlit
    ports: ["8502:8502"]
    environment:
      - GOVERNANCE_URL=http://governance:8000
    restart: unless-stopped

  # Additional 80+ services for remaining repositories
  # ... (pattern continues for all 100 repos)

volumes:
  redis-data:
  postgres-data:
  influxdb-data:
  neo4j-data:
  prometheus-data:
  grafana-data:
  airflow-data:

networks:
  default:
    name: dixvision-network
```

---

## Container Implementation Strategy

### Phase 1: Infrastructure Containers (Week 1)

#### Base Services
```bash
# Create container structure
mkdir -p containers/{base,trading,cognitive,automation,data,monitoring,workflow,api,dashboard}

# Base Dockerfile for Python containers
cat > containers/base/Dockerfile <<EOF
FROM python:3.11-slim

WORKDIR /app

# Common dependencies
RUN pip install --no-cache-dir \
    pydantic \
    requests \
    httpx \
    python-dotenv

# Governance client
COPY governance/wrappers/base_wrapper.py /app/governance/
COPY shared_infrastructure/logging.py /app/shared/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

ENV PYTHONUNBUFFERED=1
EOF
```

#### Data Services Setup
```bash
# Start with core data services
docker-compose up -d redis-service postgresql-service
docker-compose up -d influxdb-service neo4j-service
```

---

### Phase 2: Critical Trading Container (Week 1-2)

#### CCXT Container
```dockerfile
# containers/ccxt/Dockerfile
FROM containers/base

RUN pip install --no-cache-dir ccxt

COPY governance/wrappers/ccxt_wrapper.py /app/governance/
COPY adapters/ccxt_adapter.py /app/adapters/
COPY config/ccxt_config.yaml /app/config/

EXPOSE 8100

CMD ["python", "-m", "adapters.ccxt_adapter"]
```

#### CCXT Adapter with Governance
```python
# adapters/ccxt_adapter.py
from governance.wrappers.ccxt_wrapper import CCXTGovernanceWrapper
import ccxt

class CCXTAdapter:
    def __init__(self, exchange_id, governance_url):
        self.governance = CCXTGovernanceWrapper(governance_url)
        self.exchange = ccxt.create_exchange(exchange_id)
    
    async def execute_trade(self, symbol, side, amount):
        # Governance validation
        decision = await self.governance.validate_trade_request({
            'symbol': symbol,
            'side': side, 
            'amount': amount
        })
        
        if decision.approved:
            result = await self.exchange.create_order(symbol, side, 'market', amount)
            await self.governance.log_execution(result)
            return result
        else:
            raise GovernanceViolation(f"Trade rejected: {decision.reason}")
```

---

### Phase 3: Cognitive Containers (Week 2-3)

#### LangChain Container
```dockerfile
# containers/langchain/Dockerfile
FROM containers/base

RUN pip install --no-cache-dir \
    langchain \
    openai \
    chromadb

COPY governance/wrappers/langchain_wrapper.py /app/governance/
COPY shared_infrastructure/langchain_interface.py /app/shared/

EXPOSE 8200

CMD ["python", "-m", "shared_infrastructure.langchain_interface"]
```

#### Transformers Container (GPU)
```dockerfile
# containers/transformers/Dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3.11 python3-pip

WORKDIR /app

RUN pip install --no-cache-dir \
    transformers \
    torch \
    torchvision

COPY governance/wrappers/transformers_wrapper.py /app/governance/

EXPOSE 8201

CMD ["python", "-m", "governance.wrappers.transformers_wrapper"]
```

---

### Phase 4: Automation Containers (Week 3-4)

#### Playwright Container
```dockerfile
# containers/playwright/Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0

RUN pip install --no-cache-dir \
    pydantic \
    requests

COPY governance/wrappers/playwright_wrapper.py /app/governance/
COPY desktop_agent/browser/playwright_bridge.py /app/

EXPOSE 8300

# Install Playwright browsers
RUN playwright install --with-deps chromium

CMD ["python", "-m", "desktop_agent.browser.playwright_bridge"]
```

---

## Governance Integration Pattern

### Standard Container Governance Wrapper
```python
# governance/wrappers/base_wrapper.py
from abc import ABC, abstractmethod
import httpx
import os

class BaseContainerGovernanceWrapper(ABC):
    def __init__(self):
        self.governance_url = os.getenv('GOVERNANCE_URL', 'http://governance:8000')
        self.client = httpx.AsyncClient()
    
    async def validate_operation(self, operation_data):
        """All container operations must be validated by governance"""
        response = await self.client.post(
            f"{self.governance_url}/api/validate",
            json=operation_data
        )
        return response.json()
    
    async def log_operation(self, operation_data, result):
        """All container operations must be logged"""
        await self.client.post(
            f"{self.governance_url}/api/log",
            json={
                'operation': operation_data,
                'result': result,
                'timestamp': time.time()
            }
        )
    
    @abstractmethod
    async def execute_with_governance(self, operation, params):
        """Container-specific execution with governance oversight"""
        pass
```

---

## Benefits of This Approach

### 1. Clean Core Repository
```bash
dix_vision_v42.2/
├── governance/           # Core governance logic
├── indira_cognitive/     # Core INDIRA brain
├── dyon_cognitive/       # Core DYON brain
├── coordination_layer/   # Core coordination
├── desktop_agent/        # Core agent interfaces
├── docker-compose.yml    # Orchestration
├── containers/           # External repo containers
│   ├── ccxt/
│   ├── playwright/
│   ├── langchain/
│   └── ... (100 containers)
└── config/               # Core configuration
```

### 2. Independent Version Management
```bash
# Update CCXT without touching core
docker pull ccxt/ccxt:latest
docker-compose build ccxt-service
docker-compose up -d ccxt-service

# Core DIX VISION remains unchanged
```

### 3. Easy Scaling
```yaml
# Scale cognitive services
docker-compose up -d --scale langchain-service=3
docker-compose up -d --scale transformers-service=2
```

### 4. Development Workflow
```bash
# Developers only need core repo
git clone https://github.com/yourorg/dix_vision.git

# External containers are built automatically
docker-compose build
docker-compose up
```

### 5. Production Deployment
```bash
# Same containers in production
docker-compose -f docker-compose.prod.yml up -d
```

---

## Implementation Timeline

### Week 1: Foundation
- Set up Docker infrastructure
- Create base container templates
- Implement core data services (Redis, PostgreSQL)
- Governance container interface

### Week 2-3: Critical Services
- CCXT container (trading foundation)
- LangChain container (cognitive foundation)
- Playwright container (automation foundation)
- Core governance integration

### Week 4-6: High Priority Services
- Cognitive containers (Transformers, spaCy)
- Automation containers (PyAutoGUI)
- Monitoring containers (Prometheus, Grafana)
- Workflow containers (Celery, Airflow)

### Week 7-10: Remaining Services
- Additional 80+ containers
- Each container: 1-2 days
- Parallel development possible

### Week 11-12: Integration & Testing
- Cross-container communication
- Performance optimization
- Security validation
- Documentation

---

## Immediate Next Steps

### Step 1: Docker Setup (Day 1)
```bash
# Create container structure
mkdir -p containers/{base,trading,cognitive,automation,data,monitoring}

# Create base Dockerfile
# Create docker-compose.yml structure
# Set up governance container interface
```

### Step 2: First Container - CCXT (Day 2-3)
```bash
# Create CCXT container
cd containers/ccxt
# Build governance wrapper
# Test governance integration
# Validate exchange connectivity
```

### Step 3: Core Data Services (Day 4)
```bash
# Set up Redis, PostgreSQL, InfluxDB
# Configure persistence
# Test connectivity with core
```

### Step 4: Validation & Refinement (Day 5)
```bash
# End-to-end testing
# Performance validation
# Security checks
# Documentation
```

---

## Risk Mitigation

### Container Isolation
- Each container isolated from core
- Governance enforcement at container boundaries
- No direct container-to-container communication (via governance only)

### Security
- Container scanning for vulnerabilities
- Minimal base images
- Non-root container users
- Resource limits

### Reliability
- Health checks for all containers
- Auto-restart policies
- Backup strategies for data containers
- Rollback capability

---

**Recommendation:** Proceed with Docker containerized approach

**First Action:** Set up Docker infrastructure and implement CCXT container as proof of concept

**Operator Approval Required:** To proceed with containerized integration

---

**Document Status:** Containerized Integration Plan Complete  
**Architecture:** Microservices with Docker Compose  
**Benefits:** Clean core, isolated dependencies, production-ready  
**Next Action:** Begin Docker setup and CCXT container implementation  
**Maintained By:** DIX VISION Development Team  
**Date:** 2026-06-12
