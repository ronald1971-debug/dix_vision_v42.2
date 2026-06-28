# Container Communication Protocols Documentation

**Version:** 42.2
**Last Updated:** 2026-06-13
**Author:** DIX VISION Communication Framework Team

## Overview

The DIX VISION Container Communication Protocols provide a standardized framework for inter-container messaging, service discovery, and data exchange between all DIX VISION containers. This ensures consistent, secure, and governed communication across the system.

## Architecture

### Communication Components

1. **Message Protocol** (`container_communication.py`)
   - Standardized message format for all container communication
   - Priority-based message handling
   - Correlation tracking for request/response patterns
   - Governance metadata integration

2. **Service Discovery** (`service_discovery.py`)
   - Automatic service registration and health monitoring
   - Load balancing and failover capabilities
   - Standardized API interfaces for all services
   - Service health status tracking

3. **Data Exchange** (`data_exchange_formats.py`)
   - Standardized data formats for container data exchange
   - Data transformation utilities
   - Data validation mechanisms
   - Integrity checking and verification

## Communication Flow

```
Container A → Service Discovery → Container B
     ↓                                    ↓
Message Protocol                    API Interface
     ↓                                    ↓
Data Exchange Format              Response Handler
     ↓                                    ↓
Governance Validation            Data Transformation
```

## Message Protocol

### Message Structure

All container messages follow the `ContainerMessage` structure:

```python
message = ContainerMessage(
    message_type=MessageType.REQUEST,
    source="ccxt-service",
    destination="fastapi-service",
    payload={
        "operation": "get_market_data",
        "symbol": "BTC/USDT",
        "timeframe": "1h"
    },
    priority=Priority.HIGH
)
```

### Message Types

- **REQUEST**: Request for data or operation
- **RESPONSE**: Response to a request
- **NOTIFICATION**: Event notification
- **ERROR**: Error reporting
- **HEARTBEAT**: Health check signal
- **DISCOVERY**: Service discovery signal

### Priority Levels

- **CRITICAL**: System-critical messages
- **HIGH**: High-priority operations
- **NORMAL**: Standard priority
- **LOW**: Low-priority background tasks

## Service Discovery

### Service Registration

Services are automatically registered with the service discovery system:

```python
discovery = ServiceDiscovery()
discovery.register_service(
    service_name="ccxt-service",
    endpoint="http://dix-ccxt-service:8080",
    health_check_path="/health",
    metadata={
        "description": "Trading execution service",
        "category": "trading",
        "priority": "critical"
    }
)
```

### Health Monitoring

The system automatically performs health checks on all registered services:

```python
# Check all services
health_results = discovery.check_all_services()

# Get healthy services only
healthy_services = discovery.get_healthy_services()

# Get service endpoint
endpoint = discovery.get_service_endpoint("ccxt-service")
```

### API Interfaces

Each service exposes a standardized API interface:

```python
api = discovery.get_api_interface("ccxt-service")

# Health check
health = api.get_health()

# Get metrics
metrics = api.get_metrics()

# Execute operation
result = api.execute_operation("get_market_data", {"symbol": "BTC/USDT"})
```

## Data Exchange Formats

### Standard Data Types

1. **MARKET_DATA**: Trading and market information
2. **COGNITIVE_DATA**: AI and cognitive processing results
3. **API_DATA**: API request/response data
4. **TASK_DATA**: Background task information
5. **HTTP_DATA**: HTTP client communication data
6. **BROWSER_DATA**: Browser automation results
7. **SYSTEM_DATA**: System status and metrics

### Data Packet Structure

```python
packet = DataPacket(
    data_type=DataType.MARKET_DATA,
    data_format=DataFormat.JSON,
    data={
        "symbol": "BTC/USDT",
        "price": 50000.0,
        "volume": 1000.0,
        "timestamp": datetime.utcnow().isoformat()
    },
    source="ccxt-service",
    destination="fastapi-service"
)

packet.add_metadata("priority", "high")
packet.add_governance_info("permission_level", "READ_ONLY")
```

### Data Transformation

Standard transformation utilities for data exchange:

```python
transformer = DataTransformer()

# Market to Cognitive
cognitive_data = transformer.transform_market_to_cognitive(market_data)

# API to Task
task_data = transformer.transform_api_to_task(api_data)

# Browser to Cognitive
cognitive_data = transformer.transform_browser_to_cognitive(browser_data)
```

### Data Validation

Built-in validation for all data types:

```python
validator = DataValidator()

# Validate specific data types
is_valid = validator.validate_market_data(data)
is_valid = validator.validate_cognitive_data(data)
is_valid = validator.validate_api_data(data)
```

## Standard API Endpoints

All DIX VISION containers expose the following standard endpoints:

- `GET /health` - Service health check
- `GET /metrics` - Service metrics and performance data
- `GET /config` - Service configuration
- `POST /operations/{operation}` - Execute a service operation
- `GET /status` - Service status information
- `GET /governance` - Governance and permission information
- `GET /logs` - Service log entries

## Container Communication Examples

### Example 1: Market Data Request

```python
# CCXT Service sends market data to FastAPI
message = ContainerMessage(
    message_type=MessageType.REQUEST,
    source="ccxt-service",
    destination="fastapi-service",
    payload={
        "operation": "get_market_data",
        "symbol": "BTC/USDT",
        "timeframe": "1h"
    },
    priority=Priority.HIGH
)

protocol.send_message(message)
```

### Example 2: Cognitive Processing Request

```python
# FastAPI Service requests cognitive processing from LangChain
packet = DataPacket(
    data_type=DataType.COGNITIVE_DATA,
    data_format=DataFormat.JSON,
    data={
        "query": "Analyze market trends for BTC/USDT",
        "context": {"timeframe": "1h", "indicators": ["RSI", "MACD"]}
    },
    source="fastapi-service",
    destination="langchain-service"
)

# Transform to cognitive format
transformer = DataTransformer()
cognitive_packet = transformer.transform_market_to_cognitive(packet.data)
```

### Example 3: Background Task Scheduling

```python
# FastAPI Service schedules background task via Celery
message = ContainerMessage(
    message_type=MessageType.REQUEST,
    source="fastapi-service",
    destination="celery-service",
    payload={
        "task_name": "process_market_analysis",
        "task_type": "cognitive_analysis",
        "input_data": {
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "timeframe": "1h"
        }
    },
    priority=Priority.NORMAL
)

# Transform to task format
transformer = DataTransformer()
task_packet = transformer.transform_api_to_task(message.payload)
```

## Security and Governance

### Message Security

- **Integrity Checking**: All messages include checksums for data integrity
- **Governance Metadata**: Operator authority and permission levels embedded in messages
- **Audit Logging**: All communications are logged for governance compliance
- **Rate Limiting**: Message rate limiting to prevent system overload

### Service Authentication

- **Service Registration**: Only registered services can participate in communication
- **Health Validation**: Unhealthy services are automatically excluded from communication
- **Permission Enforcement**: All operations respect operator authority and permission levels

## Performance Optimization

### Connection Pooling

Services maintain connection pools for efficient communication:

```python
# Connection pool configuration
CONNECTION_POOL = {
    "max_connections": 10,
    "min_connections": 2,
    "connection_timeout": 30,
    "max_lifetime": 3600
}
```

### Caching

Data caching for frequently requested information:

```python
# Cache configuration
CACHE_CONFIG = {
    "enabled": True,
    "default_ttl": 60,  # seconds
    "max_size": 1000,
    "cache_types": ["market_data", "api_data"]
}
```

### Load Balancing

Automatic load balancing for services with multiple instances:

```python
# Load balancing strategy
LOAD_BALANCING = {
    "strategy": "round_robin",
    "health_check_interval": 30,
    "unhealthy_threshold": 3,
    "recovery_threshold": 2
}
```

## Troubleshooting

### Common Issues

1. **Service Discovery Fails**
   - Check service registration
   - Verify health check endpoints
   - Review service metadata

2. **Message Not Delivered**
   - Check message integrity
   - Verify destination service health
   - Review message priority and routing

3. **Data Transformation Errors**
   - Validate input data format
   - Check transformation rules
   - Review data type compatibility

### Debugging Tools

Enable debug logging for detailed communication information:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('container_communication')
logger.setLevel(logging.DEBUG)
```

## Best Practices

1. **Always use standard message formats** for container communication
2. **Implement proper error handling** for all communication operations
3. **Use appropriate priority levels** based on message importance
4. **Validate data before transformation** to ensure data quality
5. **Monitor service health** regularly and handle failures gracefully
6. **Use connection pooling** for efficient resource utilization
7. **Implement caching** for frequently accessed data
8. **Follow security guidelines** for all communication operations

## Future Enhancements

- WebSocket support for real-time communication
- gRPC integration for high-performance communication
- Message queue integration for asynchronous processing
- Advanced load balancing strategies
- Circuit breaker patterns for fault tolerance
- Distributed tracing for communication monitoring

## Support

For questions or issues related to container communication protocols, contact:
- DIX VISION Architecture Team
- Documentation: See project README
- Issues: GitHub issue tracker
