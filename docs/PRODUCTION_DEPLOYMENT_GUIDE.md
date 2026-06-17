# Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the DIX VISION v42.2 Cognitive OS to production environments with all production-grade components activated.

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 4 cores (8 cores recommended)
- RAM: 16GB (32GB recommended)
- Storage: 100GB SSD (500GB recommended for historical data)
- Network: Stable internet connection for data feeds

**Software Requirements:**
- Python 3.11+
- Docker (optional, for containerized deployment)
- Redis (for caching and message queues)
- PostgreSQL (for persistence)
- Time-series database (e.g., InfluxDB, TimescaleDB)

### Python Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Production-specific dependencies
pip install cryptography>=41.0.0  # For full cryptographic operations
pip install redis>=5.0.0
pip install psycopg2-binary>=2.9.0
pip install influxdb-client>=1.36.0
```

## Installation

### 1. Environment Setup

```bash
# Clone repository
cd dix_vision_v42.2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install cryptography redis psycopg2-binary influxdb-client
```

### 2. Configuration

Create `.env` file in the root directory:

```bash
# System Configuration
DIX_ENVIRONMENT=production
DIX_LOG_LEVEL=INFO
DIX_DEBUG=false

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dix_vision
POSTGRES_USER=dix_user
POSTGRES_PASSWORD=secure_password_change_me

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Time-series Database
INFLUXDB_HOST=localhost
INFLUXDB_PORT=8086
INFLUXDB_TOKEN=your_token
INFLUXDB_ORG=dix_vision
INFLUXDB_BUCKET=market_data

# Cryptographic Configuration
KEY_STORE_PATH=/secure/keys
ENCRYPTION_KEY_PATH=/secure/keys/master.key
ENABLE_HARDWARE_CRYPTOGRAPHY=false

# Trading Configuration
RISK_MAX_POSITION_SIZE=1000.0
RISK_MAX_PORTFOLIO_VALUE=1000000.0
RISK_MAX_DAILY_LOSS=0.02
RISK_MAX_DRAWDOWN=0.10
RISK_MAX_LEVERAGE=2.0

# Data Feed Configuration
DATA_FEED_PROVIDER=websocket
DATA_FEED_URL=wss://api.example.com/stream
DATA_FEED_API_KEY=your_api_key
```

### 3. Database Initialization

```bash
# Initialize PostgreSQL database
python scripts/init_database.py

# Initialize Redis cache
python scripts/init_redis.py

# Initialize time-series database
python scripts/init_influxdb.py
```

## Production Component Configuration

### Cryptographic Operations

The production cryptographic system supports both full and fallback modes:

**Full Mode (recommended):**
```python
from trust_root.production_crypto import get_production_trust_root

trust_root = get_production_trust_root()
# Uses cryptography library with RSA/ECDSA operations
```

**Fallback Mode:**
- Automatically activated if cryptography library not available
- Uses SHA-256 hashing and HMAC signatures
- Secure for hash-based operations but not full PKI

**Key Management:**
```python
# Register production trust anchor
anchor = trust_root.register_production_trust_anchor(
    anchor_id="production_signing_key",
    purpose="trading_signatures",
    key_type="RSA",
    key_size=4096  # Production recommendation
)

# Store keys securely (never commit to git)
# Use hardware security modules (HSM) in production
```

### Intelligence Engine Configuration

```python
from intelligence_engine.cognitive.production_intelligence import (
    get_production_decision_engine,
    DecisionType,
)

# Get production decision engine
decision_engine = get_production_decision_engine()

# Configure pattern recognition
decision_engine._pattern_recognition = ProductionPatternRecognition(
    window_size=500  # Larger window for production
)

# Configure risk assessment
decision_engine._risk_assessment = ProductionRiskAssessment()
```

### Data Pipeline Configuration

```python
from intelligence_engine.data.production_pipeline import get_production_pipeline

# Get production pipeline
pipeline = get_production_pipeline()

# Configure buffer size
pipeline._buffer = DataBuffer(max_size=50000)  # Production buffer

# Configure subscriptions
pipeline.subscribe("BTC/USD", handle_market_data)
pipeline.subscribe("ETH/USD", handle_market_data)
```

### Trading System Configuration

```python
from execution_unified.production_trading import get_production_trader

# Get production trader with configured parameters
risk_params = RiskParameters(
    max_position_size=1000.0,
    max_portfolio_value=1000000.0,
    max_daily_loss=0.02,
    max_drawdown=0.10,
    max_leverage=2.0
)

trader = get_production_trader(portfolio_value=1000000.0)

# Configure strategies
trader.execute_trading_decision(
    strategy_type=StrategyType.MOMENTUM,
    symbol="BTC/USD",
    current_price=45000.0,
    signal=0.3
)
```

## Deployment Modes

### 1. Standalone Deployment

For single-machine deployment:

```bash
# Start all services
python -m dix_vision.start --mode standalone

# Or use the main entry point
python start.py
```

### 2. Containerized Deployment

Using Docker Compose:

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Distributed Deployment

For high-availability production deployment:

```bash
# Start cognitive OS kernel
python -m cognitive_os.kernel --mode distributed --cluster-size 3

# Start data pipeline workers
python -m intelligence_engine.data.production_pipeline --worker-id 1

# Start trading engine
python -m execution_unified.production_trading --mode production
```

## Monitoring and Observability

### Health Checks

```bash
# System health check
curl http://localhost:8080/health

# Component status
curl http://localhost:8080/api/v1/status

# Detailed metrics
curl http://localhost:8080/api/v1/metrics
```

### Log Monitoring

```bash
# View logs
tail -f logs/dix_vision.log

# Filter by component
grep "production_trading" logs/dix_vision.log
grep "production_intelligence" logs/dix_vision.log
```

### Performance Metrics

Key metrics to monitor:

**Cryptographic Operations:**
- Hash generation latency
- Signature verification time
- Encryption/decryption throughput

**Intelligence Engine:**
- Pattern recognition latency
- Decision engine response time
- Risk assessment accuracy

**Data Pipeline:**
- Message processing rate
- Buffer utilization
- Data quality scores

**Trading System:**
- Order execution latency
- Position PnL
- Risk metric compliance
- Strategy performance

### Alerting

Set up alerts for:

- **Critical:** System crashes, database connection failures
- **Warning:** High latency, risk limit breaches, data quality issues
- **Info:** System startups, configuration changes

## Security Hardening

### Key Management

1. **Never commit keys to version control**
2. **Use hardware security modules (HSM) in production**
3. **Rotate keys regularly**
4. **Implement key backup and recovery procedures**

### Network Security

1. **Use TLS for all network communications**
2. **Implement firewall rules**
3. **Use VPN for remote access**
4. **Regular security audits**

### Application Security

1. **Enable full cryptographic operations**
2. **Implement rate limiting**
3. **Input validation and sanitization**
4. **Regular dependency updates**

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);
CREATE INDEX idx_orders_symbol_status ON orders(symbol, status);
CREATE INDEX idx_positions_symbol ON positions(symbol);

-- Partition large tables
CREATE TABLE market_data_2024 PARTITION OF market_data
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### Caching Strategy

```python
# Configure Redis caching
REDIS_TTL_MARKET_DATA = 60  # 1 minute
REDIS_TTL_DECISIONS = 300   # 5 minutes
REDIS_TTL_RISK_METRICS = 600  # 10 minutes
```

### Load Balancing

For distributed deployment:

```python
# Configure multiple decision engine instances
DECISION_ENGINE_INSTANCES = 3
DATA_PIPELINE_WORKERS = 5
TRADING_ENGINE_INSTANCES = 2
```

## Backup and Recovery

### Database Backups

```bash
# Daily PostgreSQL backup
pg_dump dix_vision > backups/dix_vision_$(date +%Y%m%d).sql

# Hourly incremental backup
pg_dump dix_vision --format=custom --file=backups/incremental_$(date +%Y%m%d_%H).backup
```

### Configuration Backups

```bash
# Backup configuration files
tar -czf backups/config_$(date +%Y%m%d).tar.gz .env config/
```

### Recovery Procedures

```bash
# Restore PostgreSQL database
psql dix_vision < backups/dix_vision_20241215.sql

# Restore configuration
tar -xzf backups/config_20241215.tar.gz
```

## Troubleshooting

### Common Issues

**Cryptography Library Not Available:**
```bash
# Install cryptography library
pip install cryptography>=41.0.0

# Verify installation
python -c "from cryptography.hazmat.primitives import hashes"
```

**High Memory Usage:**
```python
# Reduce buffer sizes
pipeline._buffer = DataBuffer(max_size=10000)

# Adjust pattern recognition window
decision_engine._pattern_recognition = ProductionPatternRecognition(window_size=200)
```

**Slow Decision Latency:**
```python
# Enable performance profiling
import cProfile
cProfile.run('decision_engine.make_production_decision(context, decision_type)')
```

### Debug Mode

```bash
# Enable debug logging
DIX_LOG_LEVEL=DEBUG python start.py

# Enable component-specific debugging
DIX_DEBUG_COMPONENTS=production_trading,production_intelligence python start.py
```

## Scaling Guidelines

### Vertical Scaling

- **Small Setup:** 4 cores, 16GB RAM (up to 10 symbols)
- **Medium Setup:** 8 cores, 32GB RAM (10-50 symbols)
- **Large Setup:** 16+ cores, 64GB+ RAM (50+ symbols)

### Horizontal Scaling

- **Data Pipeline:** Add more workers for high-frequency data
- **Decision Engine:** Add instances for parallel decision processing
- **Trading Engine:** Add instances for different asset classes

## Maintenance

### Regular Tasks

**Daily:**
- Check system health and logs
- Review risk metrics
- Verify backup completion

**Weekly:**
- Review performance metrics
- Analyze trading performance
- Update dependencies

**Monthly:**
- Security audits
- Key rotation
- Capacity planning

### Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
systemctl restart dix_vision
```

## Compliance

### Regulatory Requirements

- Implement order audit trails
- Maintain trading records for required periods
- Implement position reporting
- Risk monitoring and reporting

### Data Protection

- Encrypt sensitive data at rest
- Implement data retention policies
- User access controls
- Data breach response procedures

## Support

### Technical Support

- **Documentation:** See `/docs` directory
- **Issues:** Use project issue tracker
- **Emergency:** Contact support team

### Performance Tuning

For performance optimization assistance:
1. Enable performance profiling
2. Collect metrics for 24 hours
3. Contact performance engineering team

---

*Last Updated: June 15, 2026*
*DIX VISION v42.2 Production Deployment Guide*