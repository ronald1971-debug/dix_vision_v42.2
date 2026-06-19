"""
Container Communication Protocols for DIX VISION

This framework defines standardized communication protocols for inter-container
messaging, service discovery, and data exchange between DIX VISION containers.

Author: DIX VISION Communication Framework
Version: 42.2
"""

import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from enum import Enum
import json
import hashlib
import uuid

class ProtocolType(Enum):
    """Types of communication protocols"""
    HTTP = "http"
    WEBSOCKET = "websocket"
    REDIS_PUBSUB = "redis_pubsub"
    DIRECT_TCP = "direct_tcp"
    MESSAGE_QUEUE = "message_queue"

class MessageType(Enum):
    """Types of messages between containers"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"

class Priority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class ContainerMessage:
    """
    Standardized message format for container communication.
    
    This ensures all containers use the same message structure for
    consistent data exchange and governance oversight.
    """
    
    def __init__(self,
                 message_type: MessageType,
                 source: str,
                 destination: str,
                 payload: Dict[str, Any],
                 priority: Priority = Priority.NORMAL,
                 correlation_id: Optional[str] = None,
                 timestamp: Optional[str] = None):
        self.message_type = message_type
        self.source = source
        self.destination = destination
        self.payload = payload
        self.priority = priority
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.metadata = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_type': self.message_type.value,
            'source': self.source,
            'destination': self.destination,
            'payload': self.payload,
            'priority': self.priority.value,
            'correlation_id': self.correlation_id,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContainerMessage':
        """Create message from dictionary"""
        return cls(
            message_type=MessageType(data['message_type']),
            source=data['source'],
            destination=data['destination'],
            payload=data['payload'],
            priority=Priority(data['priority']),
            correlation_id=data['correlation_id'],
            timestamp=data['timestamp']
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ContainerMessage':
        """Create message from JSON string"""
        return cls.from_dict(json.loads(json_str))
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to message"""
        self.metadata[key] = value
    
    def generate_hash(self) -> str:
        """Generate hash of message for integrity checking"""
        message_str = self.to_json()
        return hashlib.sha256(message_str.encode()).hexdigest()


class ServiceRegistry:
    """
    Registry for tracking available container services and their endpoints.
    
    This provides service discovery and load balancing for container communication.
    """
    
    def __init__(self):
        self.services = {}
        self.logger = logging.getLogger('service_registry')
        
    def register_service(self,
                        service_name: str,
                        endpoint: str,
                        protocol: ProtocolType,
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Register a container service"""
        try:
            self.services[service_name] = {
                'endpoint': endpoint,
                'protocol': protocol.value,
                'metadata': metadata or {},
                'registered_at': datetime.utcnow().isoformat(),
                'health_status': 'unknown'
            }
            self.logger.info(f"Registered service: {service_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register service {service_name}: {str(e)}")
            return False
    
    def unregister_service(self, service_name: str) -> bool:
        """Unregister a container service"""
        if service_name in self.services:
            del self.services[service_name]
            self.logger.info(f"Unregistered service: {service_name}")
            return True
        return False
    
    def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service information"""
        return self.services.get(service_name)
    
    def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self.services.keys())
    
    def update_health_status(self, service_name: str, status: str) -> bool:
        """Update health status of a service"""
        if service_name in self.services:
            self.services[service_name]['health_status'] = status
            self.services[service_name]['last_health_check'] = datetime.utcnow().isoformat()
            return True
        return False
    
    def get_healthy_services(self) -> List[str]:
        """Get list of healthy services"""
        return [
            name for name, service in self.services.items()
            if service.get('health_status') == 'healthy'
        ]


class CommunicationProtocol:
    """
    Base communication protocol for container messaging.
    
    This provides standardized methods for sending and receiving messages
    between containers with proper error handling and governance.
    """
    
    def __init__(self, protocol_type: ProtocolType):
        self.protocol_type = protocol_type
        self.service_registry = ServiceRegistry()
        self.logger = logging.getLogger('communication_protocol')
        self.message_handlers = {}
        
    def register_message_handler(self, message_type: MessageType, handler: Callable) -> None:
        """Register a handler for a specific message type"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    def send_message(self, message: ContainerMessage) -> bool:
        """Send a message to the destination container"""
        try:
            # Validate message
            if not self._validate_message(message):
                self.logger.error(f"Invalid message: {message.correlation_id}")
                return False
            
            # Get destination service information
            service_info = self.service_registry.get_service(message.destination)
            if not service_info:
                self.logger.error(f"Service not found: {message.destination}")
                return False
            
            # Send message based on protocol
            if self.protocol_type == ProtocolType.HTTP:
                return self._send_http_message(message, service_info)
            elif self.protocol_type == ProtocolType.REDIS_PUBSUB:
                return self._send_redis_message(message, service_info)
            else:
                self.logger.error(f"Unsupported protocol: {self.protocol_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            return False
    
    def receive_message(self, message: ContainerMessage) -> bool:
        """Receive and process a message"""
        try:
            # Validate message
            if not self._validate_message(message):
                self.logger.error(f"Invalid message: {message.correlation_id}")
                return False
            
            # Route to appropriate handler
            handlers = self.message_handlers.get(message.message_type, [])
            for handler in handlers:
                try:
                    handler(message)
                except Exception as e:
                    self.logger.error(f"Handler failed: {str(e)}")
                    continue
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to receive message: {str(e)}")
            return False
    
    def _validate_message(self, message: ContainerMessage) -> bool:
        """Validate message structure and content"""
        required_fields = ['source', 'destination', 'message_type', 'payload']
        message_dict = message.to_dict()
        
        for field in required_fields:
            if not message_dict.get(field):
                return False
        
        return True
    
    def _send_http_message(self, message: ContainerMessage, service_info: Dict[str, Any]) -> bool:
        """Send message via HTTP protocol"""
        # Implementation would use requests library
        self.logger.info(f"Sending HTTP message to {service_info['endpoint']}")
        return True
    
    def _send_redis_message(self, message: ContainerMessage, service_info: Dict[str, Any]) -> bool:
        """Send message via Redis Pub/Sub protocol"""
        # Implementation would use redis library
        self.logger.info(f"Sending Redis message to {service_info['endpoint']}")
        return True


class DataExchangeProtocol:
    """
    Protocol for data exchange between containers.
    
    This provides standardized methods for sharing data between containers
    with proper transformation and validation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('data_exchange_protocol')
        self.transformers = {}
        self.validators = {}
        
    def register_transformer(self, source_type: str, target_type: str, transformer: Callable) -> None:
        """Register a data transformer"""
        key = f"{source_type}_to_{target_type}"
        self.transformers[key] = transformer
        self.logger.info(f"Registered transformer: {key}")
    
    def register_validator(self, data_type: str, validator: Callable) -> None:
        """Register a data validator"""
        self.validators[data_type] = validator
        self.logger.info(f"Registered validator: {data_type}")
    
    def transform_data(self, data: Any, source_type: str, target_type: str) -> Any:
        """Transform data from source type to target type"""
        key = f"{source_type}_to_{target_type}"
        transformer = self.transformers.get(key)
        
        if transformer:
            return transformer(data)
        else:
            self.logger.warning(f"No transformer found for {key}")
            return data
    
    def validate_data(self, data: Any, data_type: str) -> bool:
        """Validate data against its type specification"""
        validator = self.validators.get(data_type)
        
        if validator:
            return validator(data)
        else:
            self.logger.warning(f"No validator found for {data_type}")
            return True


# Example usage and initialization
if __name__ == "__main__":
    # Initialize communication protocol
    protocol = CommunicationProtocol(ProtocolType.HTTP)
    
    # Register services
    protocol.service_registry.register_service(
        service_name="ccxt-service",
        endpoint="http://dix-ccxt-service:8080",
        protocol=ProtocolType.HTTP,
        metadata={"description": "Trading execution service"}
    )
    
    protocol.service_registry.register_service(
        service_name="langchain-service",
        endpoint="http://dix-langchain-service:8081",
        protocol=ProtocolType.HTTP,
        metadata={"description": "Cognitive enhancement service"}
    )
    
    # Create and send a message
    message = ContainerMessage(
        message_type=MessageType.REQUEST,
        source="dix-fastapi-service",
        destination="dix-ccxt-service",
        payload={
            "operation": "get_market_data",
            "symbol": "BTC/USDT",
            "timeframe": "1h"
        },
        priority=Priority.HIGH
    )
    
    print("Container Communication Protocol initialized successfully")
    print(f"Registered services: {protocol.service_registry.list_services()}")
