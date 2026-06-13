"""
Data Exchange Format Specifications for DIX VISION Container Communication

This module defines standardized data formats for container data exchange,
ensuring consistent data structure and transformation between services.

Author: DIX VISION Data Exchange Framework
Version: 42.2
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
import json
import base64
import hashlib

class DataType(Enum):
    """Data types for container exchange"""
    MARKET_DATA = "market_data"
    COGNITIVE_DATA = "cognitive_data"
    API_DATA = "api_data"
    TASK_DATA = "task_data"
    HTTP_DATA = "http_data"
    BROWSER_DATA = "browser_data"
    SYSTEM_DATA = "system_data"

class DataFormat(Enum):
    """Data format types"""
    JSON = "json"
    XML = "xml"
    BINARY = "binary"
    PROTOBUF = "protobuf"
    CSV = "csv"

class MessageFormat(Enum):
    """Message format types"""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"


class DataPacket:
    """
    Standardized data packet for container data exchange.
    
    This provides a consistent format for all data exchanged between containers,
    including metadata, governance information, and data integrity checks.
    """
    
    def __init__(self,
                 data_type: DataType,
                 data_format: DataFormat,
                 data: Any,
                 source: str,
                 destination: str,
                 message_format: MessageFormat = MessageFormat.REQUEST):
        self.data_type = data_type
        self.data_format = data_format
        self.data = data
        self.source = source
        self.destination = destination
        self.message_format = message_format
        self.timestamp = datetime.utcnow().isoformat()
        self.metadata = {}
        self.governance = {}
        self.integrity = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert data packet to dictionary"""
        return {
            'data_type': self.data_type.value,
            'data_format': self.data_format.value,
            'data': self._serialize_data(),
            'source': self.source,
            'destination': self.destination,
            'message_format': self.message_format.value,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
            'governance': self.governance,
            'integrity': self._calculate_integrity()
        }
    
    def to_json(self) -> str:
        """Convert data packet to JSON string"""
        return json.dumps(self.to_dict())
    
    def _serialize_data(self) -> Any:
        """Serialize data based on format"""
        if self.data_format == DataFormat.JSON:
            if isinstance(self.data, str):
                return json.loads(self.data)
            return self.data
        elif self.data_format == DataFormat.BINARY:
            if isinstance(self.data, bytes):
                return base64.b64encode(self.data).decode('utf-8')
            return base64.b64encode(str(self.data).encode()).decode('utf-8')
        else:
            return self.data
    
    def _calculate_integrity(self) -> Dict[str, str]:
        """Calculate data integrity checksums"""
        data_str = str(self.data) if not isinstance(self.data, str) else self.data
        return {
            'checksum': hashlib.sha256(data_str.encode()).hexdigest(),
            'algorithm': 'sha256'
        }
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to data packet"""
        self.metadata[key] = value
    
    def add_governance_info(self, key: str, value: Any) -> None:
        """Add governance information to data packet"""
        self.governance[key] = value
    
    def validate_integrity(self) -> bool:
        """Validate data integrity"""
        calculated_checksum = self._calculate_integrity()['checksum']
        stored_checksum = self.integrity.get('checksum', '')
        return calculated_checksum == stored_checksum


class DataTransformer:
    """
    Data transformer for converting between different data formats and types.
    
    This provides standardized transformation methods for data exchange
    between containers with different data requirements.
    """
    
    @staticmethod
    def transform_market_to_cognitive(market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform market data to cognitive data format"""
        return {
            'cognitive_data': {
                'source': 'market',
                'symbol': market_data.get('symbol', 'unknown'),
                'price': market_data.get('price', 0),
                'volume': market_data.get('volume', 0),
                'timestamp': market_data.get('timestamp', datetime.utcnow().isoformat())
            },
            'cognitive_metadata': {
                'confidence': 'high',
                'data_quality': 'verified',
                'analysis_ready': True
            }
        }
    
    @staticmethod
    def transform_api_to_task(api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform API data to task data format"""
        return {
            'task_data': {
                'task_name': f"process_api_{api_data.get('endpoint', 'unknown')}",
                'task_type': 'data_processing',
                'input_data': api_data.get('data', {}),
                'priority': 'normal'
            },
            'task_metadata': {
                'source_service': 'api',
                'estimated_duration': 'short',
                'resource_requirement': 'low'
            }
        }
    
    @staticmethod
    def transform_browser_to_cognitive(browser_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform browser data to cognitive data format"""
        return {
            'cognitive_data': {
                'source': 'browser',
                'url': browser_data.get('url', ''),
                'title': browser_data.get('title', ''),
                'content': browser_data.get('text', ''),
                'timestamp': browser_data.get('timestamp', datetime.utcnow().isoformat())
            },
            'cognitive_metadata': {
                'content_type': 'web_page',
                'relevance': 'unknown',
                'extraction_complete': True
            }
        }
    
    @staticmethod
    def transform_http_to_api(http_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform HTTP data to API data format"""
        return {
            'api_data': {
                'endpoint': http_data.get('url', ''),
                'method': http_data.get('method', 'GET'),
                'response_code': http_data.get('status_code', 200),
                'response_data': http_data.get('response', {}),
                'latency': http_data.get('latency', 0)
            },
            'api_metadata': {
                'success': http_data.get('status_code', 200) < 400,
                'cacheable': True,
                'data_valid': True
            }
        }


class DataValidator:
    """
    Data validator for ensuring data quality and consistency.
    
    This provides validation methods for different data types
    exchanged between containers.
    """
    
    @staticmethod
    def validate_market_data(data: Dict[str, Any]) -> bool:
        """Validate market data structure"""
        required_fields = ['symbol', 'price', 'timestamp']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_cognitive_data(data: Dict[str, Any]) -> bool:
        """Validate cognitive data structure"""
        required_fields = ['source', 'cognitive_data']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_api_data(data: Dict[str, Any]) -> bool:
        """Validate API data structure"""
        required_fields = ['endpoint', 'method', 'response']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_task_data(data: Dict[str, Any]) -> bool:
        """Validate task data structure"""
        required_fields = ['task_name', 'task_type', 'input_data']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_http_data(data: Dict[str, Any]) -> bool:
        """Validate HTTP data structure"""
        required_fields = ['url', 'method', 'status_code']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_browser_data(data: Dict[str, Any]) -> bool:
        """Validate browser data structure"""
        required_fields = ['url', 'title', 'timestamp']
        return all(field in data for field in required_fields)


# Standard data exchange formats for DIX VISION containers
STANDARD_DATA_FORMATS = {
    DataType.MARKET_DATA: {
        'required_fields': ['symbol', 'price', 'timestamp', 'volume'],
        'optional_fields': ['open', 'high', 'low', 'close', 'change', 'percentage'],
        'data_format': DataFormat.JSON
    },
    DataType.COGNITIVE_DATA: {
        'required_fields': ['source', 'cognitive_data', 'cognitive_metadata'],
        'optional_fields': ['confidence', 'data_quality', 'processing_time'],
        'data_format': DataFormat.JSON
    },
    DataType.API_DATA: {
        'required_fields': ['endpoint', 'method', 'response', 'latency'],
        'optional_fields': ['headers', 'status_code', 'error'],
        'data_format': DataFormat.JSON
    },
    DataType.TASK_DATA: {
        'required_fields': ['task_name', 'task_type', 'input_data', 'status'],
        'optional_fields': ['result', 'error', 'retry_count'],
        'data_format': DataFormat.JSON
    },
    DataType.HTTP_DATA: {
        'required_fields': ['url', 'method', 'status_code', 'latency'],
        'optional_fields': ['headers', 'body', 'response'],
        'data_format': DataFormat.JSON
    },
    DataType.BROWSER_DATA: {
        'required_fields': ['url', 'title', 'timestamp', 'content'],
        'optional_fields': ['screenshot', 'elements', 'links'],
        'data_format': DataFormat.JSON
    },
    DataType.SYSTEM_DATA: {
        'required_fields': ['service_name', 'status', 'timestamp'],
        'optional_fields': ['metrics', 'configuration', 'errors'],
        'data_format': DataFormat.JSON
    }
}


# Example usage
if __name__ == "__main__":
    # Create a data packet
    packet = DataPacket(
        data_type=DataType.MARKET_DATA,
        data_format=DataFormat.JSON,
        data={
            'symbol': 'BTC/USDT',
            'price': 50000.0,
            'volume': 1000.0,
            'timestamp': datetime.utcnow().isoformat()
        },
        source='ccxt-service',
        destination='fastapi-service'
    )
    
    packet.add_metadata('priority', 'high')
    packet.add_governance_info('permission_level', 'READ_ONLY')
    
    # Convert to JSON
    packet_json = packet.to_json()
    print(f"Data packet JSON: {packet_json}")
    
    # Transform data
    transformer = DataTransformer()
    cognitive_data = transformer.transform_market_to_cognitive(packet.data)
    print(f"Transformed cognitive data: {cognitive_data}")
    
    # Validate data
    validator = DataValidator()
    is_valid = validator.validate_market_data(packet.data)
    print(f"Market data validation: {is_valid}")
    
    print("Data Exchange Format initialized successfully")
