"""
Requests Domain Adapter for DIX VISION Integration

This adapter translates HTTP client concepts into DIX VISION's
cognitive architecture, ensuring proper domain mapping and data transformation.

Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append('/app/adapters')

from base_domain_adapter import DataFormat, SystemDomainAdapter


class RequestsDomainAdapter(SystemDomainAdapter):
    """
    Domain adapter for HTTP client data using Requests library.
    
    This adapter handles:
    - HTTP concept mapping
    - Request/response data transformation
    - Network protocol integration
    - HTTP status standardization
    - Response data enhancement
    """
    
    def __init__(self):
        super().__init__("requests")
        
        # Requests-specific concept mappings
        self.register_concept_mapping('request', 'network_operation')
        self.register_concept_mapping('response', 'network_outcome')
        self.register_concept_mapping('session', 'connection_context')
        self.register_concept_mapping('header', 'metadata_transmission')
        self.register_concept_mapping('url', 'resource_identifier')
        
        # HTTP method mappings
        self.http_method_mappings = {
            'GET': 'read_operation',
            'POST': 'create_operation',
            'PUT': 'update_operation',
            'DELETE': 'remove_operation',
            'PATCH': 'modify_operation',
            'HEAD': 'metadata_operation',
            'OPTIONS': 'capability_operation'
        }
        
        # HTTP status category mappings
        self.status_category_mappings = {
            'success': (200, 299),
            'redirection': (300, 399),
            'client_error': (400, 499),
            'server_error': (500, 599)
        }
        
    def adapt_request_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt HTTP request data to DIX VISION format.
        
        Args:
            request: HTTP request data (url, method, headers, body)
        
        Returns:
            Adapted request with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'network_operation': {
                    'resource_identifier': request.get('url', ''),
                    'operation_type': self.http_method_mappings.get(request.get('method', 'GET'), 'read_operation'),
                    'protocol': self._extract_protocol(request.get('url', '')),
                    'initiated_at': datetime.utcnow().isoformat()
                },
                'operation_metadata': {
                    'method': request.get('method', 'GET'),
                    'headers': request.get('headers', {}),
                    'body': request.get('data', {}) or request.get('json', {}) or {},
                    'parameters': request.get('params', {}),
                    'content_type': request.get('headers', {}).get('content-type', 'application/json'),
                    'user_agent': request.get('headers', {}).get('user-agent', 'unknown')
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'operation_class': self._classify_operation(request),
                'complexity': self._assess_operation_complexity(request),
                'security_context': self._assess_security_context(request),
                'performance_expectation': self._predict_performance(request),
                'resource_domain': self._extract_domain(request.get('url', ''))
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'http_request',
                'source': 'requests',
                'cognitive_layer': 'network_layer'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt request data: {str(e)}")
            raise
    
    def adapt_response_data(self, response: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt HTTP response data to DIX VISION format.
        
        Args:
            response: HTTP response data (status_code, headers, body)
            request: Original request for context
        
        Returns:
            Adapted response with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'network_outcome': {
                    'resource_identifier': request.get('url', ''),
                    'operation_type': self.http_method_mappings.get(request.get('method', 'GET'), 'read_operation'),
                    'status_code': response.get('status_code', 200),
                    'status_category': self._categorize_status(response.get('status_code', 200)),
                    'completed_at': datetime.utcnow().isoformat()
                },
                'outcome_metadata': {
                    'headers': response.get('headers', {}),
                    'content_type': response.get('headers', {}).get('content-type', 'application/json'),
                    'content_length': response.get('size', 0),
                    'latency': response.get('latency', 0),
                    'response_body': response.get('response', {})
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'success': response.get('status_code', 200) in range(200, 300),
                'outcome_type': self._classify_outcome(response),
                'data_integrity': self._assess_data_integrity(response),
                'performance_quality': self._assess_performance_quality(response),
                'cognitive_insight': self._extract_cognitive_insight(response, request)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'http_response',
                'source': 'requests',
                'cognitive_layer': 'network_layer'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt response data: {str(e)}")
            raise
    
    def adapt_session_data(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt Requests session data to DIX VISION format.
        
        Args:
            session: Session data (headers, cookies, etc.)
        
        Returns:
            Adapted session with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'connection_context': {
                    'context_id': session.get('session_id', 'unknown'),
                    'state': session.get('state', 'active'),
                    'established_at': session.get('created_at', datetime.utcnow().isoformat())
                },
                'context_metadata': {
                    'headers': session.get('headers', {}),
                    'cookies': session.get('cookies', {}),
                    'auth': session.get('auth', {}),
                    'proxies': session.get('proxies', {}),
                    'timeout': session.get('timeout', 30),
                    'max_redirects': session.get('max_redirects', 5)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'context_type': self._classify_context_type(session),
                'persistence': self._assess_persistence(session),
                'security': self._assess_session_security(session),
                'performance': self._assess_session_performance(session)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'http_session',
                'source': 'requests',
                'cognitive_layer': 'connection_management'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt session data: {str(e)}")
            raise
    
    def _classify_operation(self, request: Dict[str, Any]) -> str:
        """Classify the type of operation"""
        method = request.get('method', 'GET')
        url = request.get('url', '').lower()
        
        if any(domain in url for domain in ['api', 'service']):
            return 'api_operation'
        elif any(domain in url for domain in ['static', 'asset', 'resource']):
            return 'resource_operation'
        elif any(domain in url for domain in ['auth', 'login', 'token']):
            return 'authentication_operation'
        elif any(domain in url for domain in ['data', 'info', 'content']):
            return 'data_operation'
        else:
            return 'general_operation'
    
    def _assess_operation_complexity(self, request: Dict[str, Any]) -> str:
        """Assess the complexity of the operation"""
        body = request.get('data', {}) or request.get('json', {})
        headers = request.get('headers', {})
        
        body_size = len(str(body))
        if body_size > 100000:
            return 'high_complexity'
        elif body_size > 10000:
            return 'moderate_complexity'
        elif len(headers) > 10:
            return 'moderate_complexity'
        else:
            return 'low_complexity'
    
    def _assess_security_context(self, request: Dict[str, Any]) -> str:
        """Assess the security context of the operation"""
        url = request.get('url', '')
        headers = request.get('headers', {})
        
        has_auth = 'authorization' in headers
        has_api_key = 'api_key' in headers or 'x-api-key' in headers
        has_https = url.startswith('https://')
        
        if has_auth or has_api_key:
            return 'authenticated'
        elif has_https:
            return 'encrypted'
        else:
            return 'unencrypted'
    
    def _predict_performance(self, request: Dict[str, Any]) -> str:
        """Predict the performance expectation"""
        complexity = self._assess_operation_complexity(request)
        
        if complexity == 'high_complexity':
            return 'high_latency'
        elif complexity == 'moderate_complexity':
            return 'moderate_latency'
        else:
            return 'low_latency'
    
    def _extract_protocol(self, url: str) -> str:
        """Extract protocol from URL"""
        if url.startswith('https://'):
            return 'https'
        elif url.startswith('http://'):
            return 'http'
        else:
            return 'unknown'
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc if parsed.netloc else 'unknown'
    
    def _categorize_status(self, status_code: int) -> str:
        """Categorize HTTP status codes"""
        for category, (low, high) in self.status_category_mappings.items():
            if low <= status_code <= high:
                return category
        return 'unknown_status'
    
    def _classify_outcome(self, response: Dict[str, Any]) -> str:
        """Classify the type of outcome"""
        content_type = response.get('headers', {}).get('content-type', '')
        
        if 'json' in content_type:
            return 'structured_data'
        elif 'html' in content_type:
            return 'web_page'
        elif 'xml' in content_type:
            return 'xml_data'
        elif 'text' in content_type:
            return 'plain_text'
        elif 'image' in content_type:
            return 'binary_image'
        else:
            return 'unknown_format'
    
    def _assess_data_integrity(self, response: Dict[str, Any]) -> str:
        """Assess data integrity of response"""
        status_code = response.get('status_code', 200)
        if 200 <= status_code < 300:
            return 'integrity_verified'
        else:
            return 'integrity_questionable'
    
    def _assess_performance_quality(self, response: Dict[str, Any]) -> str:
        """Assess the quality of response performance"""
        latency = response.get('latency', 0)
        
        if latency < 0.1:
            return 'excellent_performance'
        elif latency < 0.5:
            return 'good_performance'
        elif latency < 2.0:
            return 'acceptable_performance'
        else:
            return 'poor_performance'
    
    def _extract_cognitive_insight(self, response: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cognitive insight from the response"""
        status_code = response.get('status_code', 200)
        latency = response.get('latency', 0)
        
        return {
            'request_response_correlation': 'positive' if status_code < 400 else 'negative',
            'latency_category': self._assess_performance_quality(response),
            'data_availability': 'data_available' if response.get('response') else 'no_data',
            'cache_recommendation': 'cacheable' if status_code == 200 and latency < 0.5 else 'not_cacheable'
        }
    
    def _classify_context_type(self, session: Dict[str, Any]) -> str:
        """Classify the type of session context"""
        has_auth = session.get('auth')
        has_cookies = session.get('cookies')
        has_proxies = session.get('proxies')
        
        if has_auth and has_cookies:
            return 'authenticated_session'
        elif has_cookies:
            return 'cookie_based_session'
        elif has_proxies:
            return 'proxied_session'
        else:
            return 'simple_session'
    
    def _assess_persistence(self, session: Dict[str, Any]) -> str:
        """Assess the persistence of the session"""
        cookies = session.get('cookies', {})
        auth = session.get('auth')
        
        if cookies or auth:
            return 'persistent_context'
        else:
            return 'ephemeral_context'
    
    def _assess_session_security(self, session: Dict[str, Any]) -> str:
        """Assess the security of the session"""
        auth = session.get('auth')
        ssl_verify = session.get('verify', True)
        
        if auth and ssl_verify:
            return 'high_security'
        elif ssl_verify:
            return 'standard_security'
        else:
            return 'low_security'
    
    def _assess_session_performance(self, session: Dict[str, Any]) -> str:
        """Assess the performance characteristics of the session"""
        connection_pool_size = session.get('connection_pool_size', 10)
        
        if connection_pool_size > 10:
            return 'high_performance'
        elif connection_pool_size > 5:
            return 'standard_performance'
        else:
            return 'basic_performance'
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        """Main adaptation method for Requests data"""
        # Determine data type and route to appropriate adapter
        if isinstance(data, dict):
            if 'method' in data or 'url' in data:
                return self.adapt_request_data(data)
            elif 'status_code' in data or 'latency' in data:
                return self.adapt_response_data(data, {})
            elif 'session_id' in data or 'headers' in data:
                return self.adapt_session_data(data)
        
        # Default adaptation
        return self.enhance_data(data)
    
    def reverse_adapt_data(self, internal_data: Any, target_format: DataFormat) -> Any:
        """Reverse adaptation for Requests data"""
        # Remove DIX VISION enhancements
        if isinstance(internal_data, dict) and 'data' in internal_data:
            data = internal_data['data']
        else:
            data = internal_data
        
        # Reverse concept mappings
        if target_format == DataFormat.JSON:
            return self._reverse_json_requests_data(data)
        
        return data
    
    def _reverse_json_requests_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse JSON Requests data adaptation"""
        reverse_mappings = {v: k for k, v in self.concept_mappings.items()}
        adapted = {}
        
        for key, value in data.items():
            external_key = reverse_mappings.get(key, key)
            
            if isinstance(value, dict):
                adapted[external_key] = {reverse_mappings.get(k, k): v for k, v in value.items()}
            elif isinstance(value, list):
                adapted[external_key] = [
                    {reverse_mappings.get(k, k): v for k, v in item.items()} if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                adapted[external_key] = value
        
        return adapted


# Example usage
if __name__ == "__main__":
    adapter = RequestsDomainAdapter()
    
    # Example request adaptation
    sample_request = {
        'method': 'GET',
        'url': 'https://api.example.com/market/ticker',
        'headers': {
            'content-type': 'application/json',
            'user-agent': 'DIX VISION Client'
        },
        'data': {}
    }
    
    adapted_request = adapter.adapt_request_data(sample_request)
    print("Adapted request:", adapted_request)
    
    print("Requests Domain Adapter initialized successfully")
