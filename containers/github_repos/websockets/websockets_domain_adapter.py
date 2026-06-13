"""
WebSockets Domain Adapter for DIX VISION Integration

This adapter translates WebSocket concepts into DIX VISION's
cognitive architecture, ensuring proper domain mapping and data transformation.

Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

import sys
import os
sys.path.append('/app/adapters')

from base_domain_adapter import (
    SystemDomainAdapter,
    DomainType,
    DataFormat
)

class WebSocketsDomainAdapter(SystemDomainAdapter):
    """
    Domain adapter for WebSocket data.
    
    This adapter handles:
    - WebSocket connection concept mapping
    - Message transformation
    - Real-time data standardization
    - Connection metadata integration
    """
    
    def __init__(self):
        super().__init__("websockets")
        
        # WebSocket-specific concept mappings
        self.register_concept_mapping('connection', 'realtime_link')
        self.register_concept_mapping('message', 'data_transmission')
        self.register_concept_mapping('client', 'cognitive_endpoint')
        self.register_concept_mapping('server', 'central_hub')
        self.register_concept_mapping('ping', 'heartbeat')
        
        # Message type mappings
        self.message_type_mappings = {
            'text': 'structured_data',
            'binary': 'encoded_data',
            'json': 'cognitive_data'
        }
        
    def adapt_connection_data(self, connection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt WebSocket connection data to DIX VISION format.
        
        Args:
            connection: Connection data (client_id, client_ip, etc.)
        
        Returns:
            Adapted connection with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'realtime_link': {
                    'endpoint_id': connection.get('client_id', 'unknown'),
                    'source_address': connection.get('client_ip', 'unknown'),
                    'established_at': connection.get('connected_at', datetime.utcnow().isoformat()),
                    'status': 'active'
                },
                'connection_metadata': {
                    'protocol': 'websocket',
                    'transport': 'tcp',
                    'client_agent': connection.get('user_agent', 'unknown'),
                    'origin': connection.get('origin', 'unknown')
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'link_type': self._classify_connection_type(connection),
                'reliability_score': self._assess_connection_reliability(connection),
                'performance_expectation': self._predict_connection_performance(connection),
                'security_context': self._assess_connection_security(connection)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'websocket_connection',
                'source': 'websockets',
                'cognitive_layer': 'realtime_communication'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt connection data: {str(e)}")
            raise
    
    def adapt_message_data(self, message: Dict[str, Any], connection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt WebSocket message data to DIX VISION format.
        
        Args:
            message: Message data (content, type, etc.)
            connection: Connection context
        
        Returns:
            Adapted message with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'data_transmission': {
                    'endpoint_id': connection.get('client_id', 'unknown'),
                    'content': message.get('content', ''),
                    'message_type': self.message_type_mappings.get(message.get('type', 'text'), 'structured_data'),
                    'timestamp': datetime.utcnow().isoformat()
                },
                'message_metadata': {
                    'size': message.get('size', 0),
                    'encoding': message.get('encoding', 'utf-8'),
                    'direction': message.get('direction', 'unknown'),
                    'sequence_number': message.get('sequence', 0)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'transmission_type': self._classify_message_type(message),
                'data_integrity': self._assess_message_integrity(message),
                'latency_context': self._assess_message_latency(message),
                'cognitive_enhancement': self._add_message_enhancement(message)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'websocket_message',
                'source': 'websockets',
                'cognitive_layer': 'realtime_communication'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt message data: {str(e)}")
            raise
    
    def adapt_heartbeat_data(self, heartbeat: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt WebSocket heartbeat data to DIX VISION format.
        
        Args:
            heartbeat: Heartbeat data (timestamp, latency, etc.)
        
        Returns:
            Adapted heartbeat with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'heartbeat': {
                    'timestamp': heartbeat.get('timestamp', datetime.utcnow().isoformat()),
                    'latency_ms': heartbeat.get('latency', 0),
                    'status': 'healthy'
                },
                'heartbeat_metadata': {
                    'endpoint_id': heartbeat.get('client_id', 'unknown'),
                    'interval': heartbeat.get('interval', 20),
                    'missed_count': heartbeat.get('missed', 0)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'health_status': self._classify_heartbeat_health(heartbeat),
                'connection_quality': self._assess_connection_quality(heartbeat),
                'performance_metrics': self._extract_performance_metrics(heartbeat)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'websocket_heartbeat',
                'source': 'websockets',
                'cognitive_layer': 'health_monitoring'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt heartbeat data: {str(e)}")
            raise
    
    def _classify_connection_type(self, connection: Dict[str, Any]) -> str:
        """Classify the type of WebSocket connection"""
        origin = connection.get('origin', '')
        user_agent = connection.get('user_agent', '').lower()
        
        if 'bot' in user_agent or 'crawler' in user_agent:
            return 'automated_agent'
        elif 'browser' in user_agent:
            return 'web_client'
        elif 'mobile' in user_agent:
            return 'mobile_client'
        else:
            return 'unknown_client'
    
    def _assess_connection_reliability(self, connection: Dict[str, Any]) -> float:
        """Assess connection reliability score"""
        # Base reliability score
        score = 0.8
        
        # Adjust based on available metadata
        if connection.get('message_count', 0) > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def _predict_connection_performance(self, connection: Dict[str, Any]) -> str:
        """Predict connection performance"""
        return 'high_latency' if connection.get('latency', 0) > 100 else 'low_latency'
    
    def _assess_connection_security(self, connection: Dict[str, Any]) -> str:
        """Assess connection security context"""
        origin = connection.get('origin', '')
        return 'secure' if origin.startswith('https://') else 'potentially_insecure'
    
    def _classify_message_type(self, message: Dict[str, Any]) -> str:
        """Classify the type of message"""
        content = str(message.get('content', ''))
        
        try:
            json.loads(content)
            return 'structured_json'
        except:
            if len(content) > 1000:
                return 'large_payload'
            else:
                return 'simple_text'
    
    def _assess_message_integrity(self, message: Dict[str, Any]) -> str:
        """Assess message data integrity"""
        content = message.get('content', '')
        return 'intact' if content else 'empty'
    
    def _assess_message_latency(self, message: Dict[str, Any]) -> str:
        """Assess message latency context"""
        latency = message.get('latency', 0)
        return 'high_latency' if latency > 100 else 'acceptable_latency'
    
    def _add_message_enhancement(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Add cognitive enhancement to message"""
        return {
            'processing_priority': 'normal',
            'caching_recommended': False,
            'monitoring_required': True
        }
    
    def _classify_heartbeat_health(self, heartbeat: Dict[str, Any]) -> str:
        """Classify heartbeat health status"""
        missed = heartbeat.get('missed', 0)
        latency = heartbeat.get('latency', 0)
        
        if missed > 3:
            return 'unhealthy'
        elif latency > 200:
            return 'degraded'
        else:
            return 'healthy'
    
    def _assess_connection_quality(self, heartbeat: Dict[str, Any]) -> str:
        """Assess connection quality"""
        latency = heartbeat.get('latency', 0)
        if latency < 50:
            return 'excellent'
        elif latency < 100:
            return 'good'
        else:
            return 'poor'
    
    def _extract_performance_metrics(self, heartbeat: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance metrics from heartbeat"""
        return {
            'avg_latency': heartbeat.get('latency', 0),
            'missed_heartbeats': heartbeat.get('missed', 0),
            'health_percentage': max(0, 100 - heartbeat.get('missed', 0) * 10)
        }
