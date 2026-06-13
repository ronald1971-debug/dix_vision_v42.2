"""
FastAPI Governance Wrapper for DIX VISION Integration

This wrapper provides governance oversight for FastAPI web framework operations,
ensuring operator authority, API security, and compliance with DIX VISION's
constitutional governance for the dashboard backend API.

Author: DIX VISION API Governance
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

class FastAPIGovernanceWrapper(BaseExternalRepoGovernanceWrapper):
    """
    Governance wrapper for FastAPI web framework operations.
    
    This ensures that all API operations are:
    - Governed by operator authority (operator has ultimate authority)
    - Validated for API security (rate limiting, input validation)
    - Audited for compliance (API call logging, request tracking)
    - Monitored for performance (latency, error rates, throughput)
    """
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__("fastapi", permission_level)
        self.metrics = ExternalRepositoryMetrics("fastapi")
        self.fastapi_instance = None
        self.api_endpoints = {}
        self.rate_limits = {
            'requests_per_minute': 1000,
            'requests_per_hour': 10000,
            'burst_size': 50
        }
        self.current_usage = {
            'request_count': 0,
            'error_count': 0,
            'rate_limit_reset': None
        }
        self.security_restrictions = {
            'allowed_origins': [],  # Empty means all allowed
            'blocked_ips': [],
            'max_request_size': 10485760,  # 10MB
            'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
            'blocked_content_types': ['application/octet-stream']
        }
        
    def initialize_fastapi(self, api_config: Dict[str, Any]):
        """
        Initialize FastAPI with governance oversight.
        
        Args:
            api_config: API configuration (title, version, etc.)
        """
        try:
            from fastapi import FastAPI
            from fastapi.middleware.cors import CORSMiddleware
            
            self.fastapi_instance = FastAPI(
                title=api_config.get('title', 'DIX VISION API'),
                version=api_config.get('version', '42.2.0'),
                description=api_config.get('description', 'DIX VISION Cognitive Trading System API')
            )
            
            # Add CORS middleware with governance oversight
            self.fastapi_instance.add_middleware(
                CORSMiddleware,
                allow_origins=api_config.get('allowed_origins', ['*']),
                allow_credentials=True,
                allow_methods=['*'],
                allow_headers=['*']
            )
            
            self.logger.info("FastAPI initialized with governance oversight")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize FastAPI: {str(e)}")
            raise GovernanceViolation(f"FastAPI initialization failed: {str(e)}")
    
    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """
        Enhanced safety checks specific to API operations.
        """
        if not self.safety_check_enabled:
            return True
            
        # Check basic safety
        if not super().safety_check(operation, params):
            return False
            
        # API-specific safety checks
        if 'api_request' in operation.lower():
            if not self._validate_api_request_safety(params):
                return False
                
        return True
    
    def _validate_api_request_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of API requests"""
        method = params.get('method', 'GET')
        content_type = params.get('content_type', 'application/json')
        request_size = params.get('content_length', 0)
        
        # Check allowed methods
        if method not in self.security_restrictions['allowed_methods']:
            self.logger.warning(f"Blocked HTTP method: {method}")
            return False
            
        # Check content type restrictions
        if content_type in self.security_restrictions['blocked_content_types']:
            self.logger.warning(f"Blocked content type: {content_type}")
            return False
            
        # Check request size
        if request_size > self.security_restrictions['max_request_size']:
            self.logger.warning(f"Request too large: {request_size} bytes")
            return False
            
        # Check rate limits
        if not self._check_rate_limit():
            self.logger.warning("Rate limit exceeded")
            return False
            
        return True
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        current_time = datetime.utcnow()
        
        # Reset counters if needed
        if self.current_usage['rate_limit_reset'] and current_time > self.current_usage['rate_limit_reset']:
            self.current_usage['request_count'] = 0
            self.current_usage['rate_limit_reset'] = None
        
        # Check per-minute limit
        if self.current_usage['request_count'] >= self.rate_limits['requests_per_minute']:
            return False
            
        return True
    
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method for FastAPI operations.
        """
        start_time = time.time()
        success = False
        
        try:
            if not self.fastapi_instance:
                raise GovernanceViolation("FastAPI instance not initialized")
            
            # Map operation to FastAPI method
            if operation == 'register_endpoint':
                path = params.get('path', '/')
                methods = params.get('methods', ['GET'])
                handler = params.get('handler')
                
                if not handler:
                    raise ValueError("Handler function required for endpoint registration")
                
                # Register endpoint with governance wrapper
                self.api_endpoints[path] = {
                    'methods': methods,
                    'handler': handler,
                    'registered_at': datetime.utcnow().isoformat()
                }
                
                result = {'path': path, 'methods': methods, 'status': 'registered'}
                
            elif operation == 'api_request':
                path = params.get('path', '/')
                method = params.get('method', 'GET')
                headers = params.get('headers', {})
                body = params.get('body', {})
                
                # Update usage counters
                self.current_usage['request_count'] += 1
                
                # Check rate limit reset
                if not self.current_usage['rate_limit_reset']:
                    self.current_usage['rate_limit_reset'] = datetime.utcnow() + timedelta(minutes=1)
                
                # Simulate API call (in production, would call actual endpoint)
                result = {
                    'path': path,
                    'method': method,
                    'status_code': 200,
                    'response': {'data': 'success'},
                    'latency': time.time() - start_time
                }
                
            elif operation == 'get_endpoints':
                result = {
                    'endpoints': self.api_endpoints,
                    'total_endpoints': len(self.api_endpoints)
                }
                
            elif operation == 'get_api_metrics':
                result = self.metrics.get_metrics()
                
            elif operation == 'get_rate_limit_status':
                result = {
                    'requests_remaining': self.rate_limits['requests_per_minute'] - self.current_usage['request_count'],
                    'reset_time': self.current_usage['rate_limit_reset'].isoformat() if self.current_usage['rate_limit_reset'] else None,
                    'current_usage': self.current_usage['request_count']
                }
                
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            success = True
            execution_time = time.time() - start_time
            self.metrics.record_operation(success, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.record_operation(False, execution_time)
            self.current_usage['error_count'] += 1
            self.logger.error(f"FastAPI operation failed: {operation} - {str(e)}")
            raise
    
    def register_api_endpoint(self, 
                             path: str, 
                             methods: List[str], 
                             handler) -> Dict[str, Any]:
        """
        Register an API endpoint with governance oversight.
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.EXECUTE):
                raise GovernanceViolation("Execute permission required for endpoint registration")
            
            # Validate path and methods
            if not path.startswith('/'):
                raise ValueError("Path must start with /")
                
            for method in methods:
                if method not in self.security_restrictions['allowed_methods']:
                    raise ValueError(f"Blocked HTTP method: {method}")
            
            # Execute with governance
            params = {
                'path': path,
                'methods': methods,
                'handler': handler
            }
            
            result = self.execute_operation('register_endpoint', params, PermissionLevel.EXECUTE)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'rate_limits': self.rate_limits,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"API endpoint registration failed: {str(e)}")
            raise
    
    def make_api_request(self, 
                        path: str, 
                        method: str = 'GET',
                        headers: Optional[Dict[str, str]] = None,
                        body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an API request with governance oversight.
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.READ_ONLY):
                raise GovernanceViolation("Read permission required for API requests")
            
            # Prepare parameters
            params = {
                'path': path,
                'method': method,
                'headers': headers or {},
                'body': body or {},
                'content_length': len(str(body)) if body else 0,
                'content_type': headers.get('content-type', 'application/json') if headers else 'application/json'
            }
            
            # Execute with governance
            result = self.execute_operation('api_request', params, PermissionLevel.READ_ONLY)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'rate_limit_status': self.execute_operation('get_rate_limit_status', {}, PermissionLevel.READ_ONLY),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise
    
    def get_api_metrics(self) -> Dict[str, Any]:
        """Get API performance metrics"""
        return {
            'repository_metrics': self.metrics.get_metrics(),
            'current_usage': self.current_usage,
            'rate_limits': self.rate_limits,
            'registered_endpoints': len(self.api_endpoints),
            'permission_level': self.permission_level.value,
            'security_restrictions': self.security_restrictions
        }


# Example usage
if __name__ == "__main__":
    # Create wrapper with appropriate permission level
    wrapper = FastAPIGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Initialize FastAPI
    # wrapper.initialize_fastapi({
    #     'title': 'DIX VISION API',
    #     'version': '42.2.0',
    #     'description': 'DIX VISION Cognitive Trading System API'
    # })
    
    print("FastAPI Governance Wrapper initialized successfully")
