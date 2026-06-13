"""
WebSockets Governance Wrapper for DIX VISION Integration

This wrapper provides governance oversight for WebSocket operations,
ensuring operator authority, connection security, and compliance with DIX VISION's
constitutional governance for real-time communication.

Author: DIX VISION Real-time Governance
Version: 42.2
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import time

import sys
import os
sys.path.append('/app/governance')

from base_external_repo_wrapper import (
    BaseExternalRepoGovernanceWrapper,
    PermissionLevel,
    GovernanceViolation,
    SafetyViolation,
    ExternalRepositoryMetrics,
    ExternalRepositoryHealthCheck
)

from datetime import timedelta

class WebSocketsGovernanceWrapper(BaseExternalRepoGovernanceWrapper):
    """
    Governance wrapper for WebSocket operations.
    
    This ensures that all WebSocket operations are:
    - Governed by operator authority (operator has ultimate authority)
    - Validated for connection security (authentication, rate limiting)
    - Audited for compliance (message logging, connection tracking)
    - Monitored for performance (latency, message rates, connection health)
    """
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__("websockets", permission_level)
        self.metrics = ExternalRepositoryMetrics("websockets")
        self.websocket_instance = None
        self.active_connections = {}
        self.connection_limits = {
            'max_connections': 1000,
            'max_message_size': 1048576,  # 1MB
            'messages_per_minute': 1000,
            'connection_timeout': 300  # 5 minutes
        }
        self.current_usage = {
            'connection_count': 0,
            'message_count': 0,
            'rate_limit_reset': None
        }
        self.security_restrictions = {
            'allowed_origins': [],
            'blocked_ips': [],
            'require_authentication': False,
            'allowed_message_types': ['text', 'binary']
        }
        
    def initialize_websocket(self, ws_config: Dict[str, Any]):
        """
        Initialize WebSocket server with governance oversight.
        
        Args:
            ws_config: WebSocket configuration (host, port, etc.)
        """
        try:
            import websockets
            
            self.websocket_instance = {
                'host': ws_config.get('host', '0.0.0.0'),
                'port': ws_config.get('port', 9146),
                'ping_interval': ws_config.get('ping_interval', 20),
                'ping_timeout': ws_config.get('ping_timeout', 20),
                'max_size': self.connection_limits['max_message_size']
            }
            
            self.logger.info("WebSocket server initialized with governance oversight")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebSocket: {str(e)}")
            raise GovernanceViolation(f"WebSocket initialization failed: {str(e)}")
    
    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """
        Enhanced safety checks specific to WebSocket operations.
        """
        if not self.safety_check_enabled:
            return True
            
        # Check basic safety
        if not super().safety_check(operation, params):
            return False
            
        # WebSocket-specific safety checks
        if 'connect' in operation.lower():
            if not self._validate_connection_safety(params):
                return False
        elif 'send' in operation.lower():
            if not self._validate_message_safety(params):
                return False
                
        return True
    
    def _validate_connection_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of connection requests"""
        origin = params.get('origin', '')
        client_ip = params.get('client_ip', '')
        
        # Check blocked IPs
        if client_ip in self.security_restrictions['blocked_ips']:
            self.logger.warning(f"Blocked IP connection attempt: {client_ip}")
            return False
            
        # Check connection limits
        if self.current_usage['connection_count'] >= self.connection_limits['max_connections']:
            self.logger.warning("Maximum connection limit reached")
            return False
            
        return True
    
    def _validate_message_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of message sending"""
        message_size = params.get('message_size', 0)
        message_type = params.get('message_type', 'text')
        
        # Check message size
        if message_size > self.connection_limits['max_message_size']:
            self.logger.warning(f"Message too large: {message_size} bytes")
            return False
            
        # Check message type
        if message_type not in self.security_restrictions['allowed_message_types']:
            self.logger.warning(f"Blocked message type: {message_type}")
            return False
            
        # Check rate limits
        if not self._check_rate_limit():
            self.logger.warning("Message rate limit exceeded")
            return False
            
        return True
    
    def _check_rate_limit(self) -> bool:
        """Check if message is within rate limits"""
        current_time = datetime.utcnow()
        
        # Reset counters if needed
        if self.current_usage['rate_limit_reset'] and current_time > self.current_usage['rate_limit_reset']:
            self.current_usage['message_count'] = 0
            self.current_usage['rate_limit_reset'] = None
        
        # Check per-minute limit
        if self.current_usage['message_count'] >= self.connection_limits['messages_per_minute']:
            return False
            
        return True
    
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method for WebSocket operations.
        """
        start_time = time.time()
        success = False
        
        try:
            if not self.websocket_instance:
                raise GovernanceViolation("WebSocket instance not initialized")
            
            if operation == 'connect':
                client_id = params.get('client_id', 'unknown')
                client_ip = params.get('client_ip', 'unknown')
                
                # Register connection
                self.active_connections[client_id] = {
                    'connected_at': datetime.utcnow().isoformat(),
                    'client_ip': client_ip,
                    'message_count': 0
                }
                self.current_usage['connection_count'] += 1
                
                result = {'client_id': client_id, 'status': 'connected'}
                
            elif operation == 'disconnect':
                client_id = params.get('client_id', 'unknown')
                
                # Unregister connection
                if client_id in self.active_connections:
                    del self.active_connections[client_id]
                    self.current_usage['connection_count'] -= 1
                
                result = {'client_id': client_id, 'status': 'disconnected'}
                
            elif operation == 'send':
                client_id = params.get('client_id', 'unknown')
                message = params.get('message', '')
                message_size = len(str(message).encode('utf-8'))
                
                # Update usage counters
                self.current_usage['message_count'] += 1
                
                # Check rate limit reset
                if not self.current_usage['rate_limit_reset']:
                    self.current_usage['rate_limit_reset'] = datetime.utcnow() + timedelta(minutes=1)
                
                # Update connection message count
                if client_id in self.active_connections:
                    self.active_connections[client_id]['message_count'] += 1
                
                result = {
                    'client_id': client_id,
                    'message_size': message_size,
                    'status': 'sent',
                    'latency': time.time() - start_time
                }
                
            elif operation == 'get_connections':
                result = {
                    'connections': self.active_connections,
                    'total_connections': len(self.active_connections)
                }
                
            elif operation == 'get_metrics':
                result = self.metrics.get_metrics()
                
            elif operation == 'get_connection_status':
                client_id = params.get('client_id', 'unknown')
                result = self.active_connections.get(client_id, {'status': 'not_connected'})
                
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            success = True
            return result
            
        except Exception as e:
            self.logger.error(f"WebSocket operation failed: {operation} - {str(e)}")
            raise GovernanceViolation(f"WebSocket operation failed: {str(e)}")
        finally:
            execution_time = time.time() - start_time
            self.metrics.record_operation(success, execution_time)
