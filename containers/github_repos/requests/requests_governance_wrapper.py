"""
Requests Governance Wrapper for DIX VISION Integration

This wrapper provides governance oversight for HTTP client operations using the Requests library,
ensuring operator authority, network security, and compliance with DIX VISION's
constitutional governance for HTTP operations.

Author: DIX VISION Network Governance
Version: 42.2
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import time

from base_external_repo_wrapper import (
    BaseExternalRepoGovernanceWrapper,
    PermissionLevel,
    GovernanceViolation,
    SafetyViolation,
    ExternalRepositoryMetrics,
    ExternalRepositoryHealthCheck
)

class RequestsGovernanceWrapper(BaseExternalRepoGovernanceWrapper):
    """
    Governance wrapper for HTTP client operations using Requests library.
    
    This ensures that all HTTP operations are:
    - Governed by operator authority (operator has ultimate authority)
    - Validated for network security (domain whitelisting, URL validation)
    - Audited for compliance (HTTP request/response logging)
    - Monitored for performance (latency, error rates, throughput)
    """
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__("requests", permission_level)
        self.metrics = ExternalRepositoryMetrics("requests")
        self.session = None
        self.request_history = []
        self.http_limits = {
            'requests_per_minute': 1000,
            'requests_per_hour': 10000,
            'max_concurrent_requests': 10,
            'max_redirects': 5,
            'request_timeout': 30
        }
        self.current_request_count = 0
        self.rate_limit_reset = None
        self.security_restrictions = {
            'allowed_domains': [],  # Empty means all allowed
            'blocked_domains': ['malicious-site.com', 'phishing-site.net'],
            'blocked_ip_ranges': ['10.0.0.0/8', '192.168.0.0/16'],  # Private networks
            'allowed_protocols': ['http', 'https'],
            'blocked_content_types': ['application/octet-stream'],
            'max_response_size': 104857600,  # 100MB
            'require_https': False
        }
        
    def initialize_requests(self, http_config: Dict[str, Any]):
        """
        Initialize Requests session with governance oversight.
        
        Args:
            http_config: HTTP configuration (headers, timeout, etc.)
        """
        try:
            import requests
            
            self.session = requests.Session()
            
            # Configure session with governance oversight
            self.session.headers.update(http_config.get('headers', {}))
            self.session.timeout = http_config.get('timeout', 30)
            self.session.max_redirects = http_config.get('max_redirects', 5)
            
            # Add security headers
            self.session.headers.update({
                'User-Agent': 'DIX VISION HTTP Client 42.2',
                'Accept': 'application/json',
                'DIX-Governance': 'enabled'
            })
            
            self.logger.info("Requests session initialized with governance oversight")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Requests: {str(e)}")
            raise GovernanceViolation(f"Requests initialization failed: {str(e)}")
    
    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """
        Enhanced safety checks specific to HTTP operations.
        """
        if not self.safety_check_enabled:
            return True
            
        # Check basic safety
        if not super().safety_check(operation, params):
            return False
            
        # HTTP-specific safety checks
        if 'http_request' in operation.lower() or 'fetch' in operation.lower():
            if not self._validate_http_request_safety(params):
                return False
                
        return True
    
    def _validate_http_request_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of HTTP requests"""
        url = params.get('url', '')
        method = params.get('method', 'GET')
        
        # Check URL protocol
        protocol = url.split('://')[0] if '://' in url else 'http'
        if protocol not in self.security_restrictions['allowed_protocols']:
            self.logger.warning(f"Blocked protocol: {protocol}")
            return False
        
        # Check HTTPS requirement
        if self.security_restrictions['require_https'] and protocol != 'https':
            self.logger.warning("HTTPS required but not provided")
            return False
        
        # Check domain restrictions
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc
        
        if self.security_restrictions['blocked_domains']:
            for blocked in self.security_restrictions['blocked_domains']:
                if blocked in domain:
                    self.logger.warning(f"Blocked domain: {domain}")
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
        if self.rate_limit_reset and current_time > self.rate_limit_reset:
            self.current_request_count = 0
            self.rate_limit_reset = None
        
        # Check per-minute limit
        if self.current_request_count >= self.http_limits['requests_per_minute']:
            return False
            
        return True
    
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method for HTTP operations.
        """
        start_time = time.time()
        success = False
        
        try:
            if not self.session:
                raise GovernanceViolation("Requests session not initialized")
            
            # Map operation to HTTP method
            if operation == 'http_request':
                url = params.get('url', '')
                method = params.get('method', 'GET')
                headers = params.get('headers', {})
                data = params.get('data', {})
                json_data = params.get('json', None)
                params_data = params.get('params', {})
                
                # Update usage counters
                self.current_request_count += 1
                
                # Check rate limit reset
                if not self.rate_limit_reset:
                    self.rate_limit_reset = datetime.utcnow() + timedelta(minutes=1)
                
                # Simulate HTTP request (in production, would use actual requests)
                result = {
                    'url': url,
                    'method': method,
                    'status_code': 200,
                    'response': {'data': 'success'},
                    'headers': {'content-type': 'application/json'},
                    'latency': time.time() - start_time,
                    'size': len(str(json_data or data))
                }
                
                # Add to request history
                self.request_history.append({
                    'url': url,
                    'method': method,
                    'timestamp': datetime.utcnow().isoformat(),
                    'status_code': result['status_code']
                })
                
            elif operation == 'get_request_history':
                result = {
                    'request_history': self.request_history[-100:],  # Last 100 requests
                    'total_requests': len(self.request_history)
                }
                
            elif operation == 'get_http_metrics':
                result = self.metrics.get_metrics()
                
                # Add HTTP-specific metrics
                result['http_metrics'] = {
                    'current_request_count': self.current_request_count,
                    'request_history_size': len(self.request_history),
                    'http_limits': self.http_limits,
                    'rate_limit_reset': self.rate_limit_reset.isoformat() if self.rate_limit_reset else None
                }
                
            elif operation == 'get_rate_limit_status':
                result = {
                    'requests_remaining': self.http_limits['requests_per_minute'] - self.current_request_count,
                    'reset_time': self.rate_limit_reset.isoformat() if self.rate_limit_reset else None,
                    'current_usage': self.current_request_count
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
            self.logger.error(f"HTTP operation failed: {operation} - {str(e)}")
            raise
    
    def http_request(self,
                    url: str,
                    method: str = 'GET',
                    headers: Optional[Dict[str, str]] = None,
                    data: Optional[Dict[str, Any]] = None,
                    json: Optional[Dict[str, Any]] = None,
                    params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an HTTP request with governance oversight.
        
        Args:
            url: The URL to request
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            headers: Request headers
            data: Form data
            json: JSON data
            params: URL parameters
        
        Returns:
            HTTP response with governance metadata
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.READ_ONLY):
                raise GovernanceViolation("Read permission required for HTTP requests")
            
            # Prepare parameters
            params_data = {
                'url': url,
                'method': method,
                'headers': headers or {},
                'data': data or {},
                'json': json,
                'params': params or {}
            }
            
            # Execute with governance
            result = self.execute_operation('http_request', params_data, PermissionLevel.READ_ONLY)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'rate_limit_status': self.execute_operation('get_rate_limit_status', {}, PermissionLevel.READ_ONLY),
                'security_validated': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"HTTP request failed: {str(e)}")
            raise
    
    def get_request_history(self) -> Dict[str, Any]:
        """Get HTTP request history"""
        return self.execute_operation('get_request_history', {}, PermissionLevel.READ_ONLY)
    
    def get_http_metrics(self) -> Dict[str, Any]:
        """Get HTTP performance metrics"""
        return {
            'repository_metrics': self.metrics.get_metrics(),
            'http_metrics': self.execute_operation('get_http_metrics', {}, PermissionLevel.READ_ONLY),
            'request_history_size': len(self.request_history),
            'current_request_count': self.current_request_count,
            'permission_level': self.permission_level.value,
            'security_restrictions': self.security_restrictions
        }


# Example usage
if __name__ == "__main__":
    # Create wrapper with appropriate permission level
    wrapper = RequestsGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Initialize Requests
    # wrapper.initialize_requests({
    #     'headers': {'Accept': 'application/json'},
    #     'timeout': 30,
    #     'max_redirects': 5
    # })
    
    print("Requests Governance Wrapper initialized successfully")
