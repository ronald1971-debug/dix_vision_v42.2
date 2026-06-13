"""
FastAPI Domain Adapter for DIX VISION Integration

This adapter translates FastAPI web framework concepts into DIX VISION's
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

class FastAPIDomainAdapter(SystemDomainAdapter):
    """
    Domain adapter for FastAPI web framework data.
    
    This adapter handles:
    - API endpoint concept mapping
    - HTTP request/response transformation
    - API documentation integration
    - API data standardization
    - System performance metrics
    """
    
    def __init__(self):
        super().__init__("fastapi")
        
        # FastAPI-specific concept mappings
        self.register_concept_mapping('endpoint', 'api_interface')
        self.register_concept_mapping('request', 'cognitive_request')
        self.register_concept_mapping('response', 'cognitive_response')
        self.register_concept_mapping('middleware', 'governance_layer')
        self.register_concept_mapping('route', 'cognitive_pathway')
        
        # HTTP method mappings
        self.http_method_mappings = {
            'GET': 'read_operation',
            'POST': 'create_operation',
            'PUT': 'update_operation',
            'DELETE': 'remove_operation',
            'PATCH': 'modify_operation'
        }
        
    def adapt_request_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt HTTP request data to DIX VISION format.
        
        Args:
            request: HTTP request data (method, path, headers, body)
        
        Returns:
            Adapted request with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'cognitive_request': {
                    'pathway': request.get('path', '/'),
                    'operation_type': self.http_method_mappings.get(request.get('method', 'GET'), 'read_operation'),
                    'origin': request.get('headers', {}).get('origin', 'unknown'),
                    'timestamp': datetime.utcnow().isoformat()
                },
                'request_metadata': {
                    'method': request.get('method', 'GET'),
                    'headers': request.get('headers', {}),
                    'content_type': request.get('headers', {}).get('content-type', 'application/json'),
                    'user_agent': request.get('headers', {}).get('user-agent', 'unknown'),
                    'content_length': request.get('content_length', 0)
                }
            }
            
            # Add body if present
            if 'body' in request and request['body']:
                adapted['cognitive_request']['data'] = request['body']
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'request_type': self._classify_request_type(request),
                'complexity': self._assess_request_complexity(request),
                'security_context': self._assess_security_context(request),
                'performance_expectation': self._predict_performance(request)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'api_request',
                'source': 'fastapi',
                'cognitive_layer': 'api_interface'
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
                'cognitive_response': {
                    'pathway': request.get('path', '/'),
                    'operation_type': self.http_method_mappings.get(request.get('method', 'GET'), 'read_operation'),
                    'status_code': response.get('status_code', 200),
                    'status_category': self._categorize_status(response.get('status_code', 200)),
                    'timestamp': datetime.utcnow().isoformat()
                },
                'response_metadata': {
                    'headers': response.get('headers', {}),
                    'content_type': response.get('headers', {}).get('content-type', 'application/json'),
                    'content_length': response.get('content_length', 0),
                    'latency': response.get('latency', 0)
                }
            }
            
            # Add body if present
            if 'body' in response and response['body']:
                adapted['cognitive_response']['data'] = response['body']
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'success': response.get('status_code', 200) < 400,
                'response_type': self._classify_response_type(response),
                'data_integrity': self._assess_data_integrity(response, request),
                'performance_quality': self._assess_performance_quality(response),
                'cognitive_enhancement': self._add_cognitive_enhancement(response, request)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'api_response',
                'source': 'fastapi',
                'cognitive_layer': 'api_interface'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt response data: {str(e)}")
            raise
    
    def adapt_endpoint_data(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt API endpoint registration data to DIX VISION format.
        
        Args:
            endpoint: Endpoint data (path, methods, handler)
        
        Returns:
            Adapted endpoint with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'api_interface': {
                    'pathway': endpoint.get('path', '/'),
                    'allowed_operations': [self.http_method_mappings.get(m, 'unknown') for m in endpoint.get('methods', ['GET'])],
                    'handler': endpoint.get('handler', 'unknown'),
                    'registered_at': endpoint.get('registered_at', datetime.utcnow().isoformat())
                },
                'interface_metadata': {
                    'methods': endpoint.get('methods', ['GET']),
                    'security_requirements': endpoint.get('security', {}),
                    'documentation': endpoint.get('docs', '')
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'interface_type': self._classify_interface_type(endpoint),
                'cognitive_domain': self._determine_cognitive_domain(endpoint),
                'governance_level': self._assess_governance_level(endpoint),
                'complexity': self._assess_endpoint_complexity(endpoint)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'api_endpoint',
                'source': 'fastapi',
                'cognitive_layer': 'api_management'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt endpoint data: {str(e)}")
            raise
    
    def _classify_request_type(self, request: Dict[str, Any]) -> str:
        """Classify the type of API request"""
        method = request.get('method', 'GET')
        path = request.get('path', '/')
        
        if method == 'GET':
            return 'data_retrieval'
        elif method == 'POST':
            if 'create' in path or 'add' in path:
                return 'resource_creation'
            else:
                return 'data_submission'
        elif method == 'PUT':
            return 'resource_update'
        elif method == 'DELETE':
            return 'resource_removal'
        elif method == 'PATCH':
            return 'resource_modification'
        else:
            return 'unknown_operation'
    
    def _assess_request_complexity(self, request: Dict[str, Any]) -> str:
        """Assess the complexity of the request"""
        body = request.get('body', {})
        headers = request.get('headers', {})
        
        if body and len(str(body)) > 10000:
            return 'high_complexity'
        elif body and len(str(body)) > 1000:
            return 'moderate_complexity'
        elif len(headers) > 10:
            return 'moderate_complexity'
        else:
            return 'low_complexity'
    
    def _assess_security_context(self, request: Dict[str, Any]) -> str:
        """Assess the security context of the request"""
        headers = request.get('headers', {})
        
        has_auth = 'authorization' in headers
        has_api_key = 'api_key' in headers or 'x-api-key' in headers
        has_token = 'token' in headers
        
        if has_auth or has_api_key or has_token:
            return 'authenticated'
        else:
            return 'unauthenticated'
    
    def _predict_performance(self, request: Dict[str, Any]) -> str:
        """Predict the performance expectation"""
        complexity = self._assess_request_complexity(request)
        
        if complexity == 'high_complexity':
            return 'high_latency'
        elif complexity == 'moderate_complexity':
            return 'moderate_latency'
        else:
            return 'low_latency'
    
    def _categorize_status(self, status_code: int) -> str:
        """Categorize HTTP status codes"""
        if 200 <= status_code < 300:
            return 'success'
        elif 300 <= status_code < 400:
            return 'redirection'
        elif 400 <= status_code < 500:
            return 'client_error'
        elif 500 <= status_code < 600:
            return 'server_error'
        else:
            return 'unknown_status'
    
    def _classify_response_type(self, response: Dict[str, Any]) -> str:
        """Classify the type of response"""
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
    
    def _assess_data_integrity(self, response: Dict[str, Any], request: Dict[str, Any]) -> str:
        """Assess data integrity of response"""
        # Simplified assessment
        status_code = response.get('status_code', 200)
        if status_code >= 200 and status_code < 300:
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
    
    def _add_cognitive_enhancement(self, response: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        """Add cognitive enhancement to response"""
        return {
            'request_response_correlation': self._calculate_correlation(response, request),
            'data_insights': self._extract_data_insights(response),
            'system_state': 'operational'
        }
    
    def _calculate_correlation(self, response: Dict[str, Any], request: Dict[str, Any]) -> str:
        """Calculate correlation between request and response"""
        # Simplified correlation check
        if response.get('status_code', 200) == 200:
            return 'positive_correlation'
        else:
            return 'negative_correlation'
    
    def _extract_data_insights(self, response: Dict[str, Any]) -> str:
        """Extract insights from response data"""
        body = response.get('body', {})
        if isinstance(body, dict):
            return 'structured_insights_available'
        elif isinstance(body, list):
            return f'array_insights_{len(body)}_items'
        else:
            return 'raw_data_available'
    
    def _classify_interface_type(self, endpoint: Dict[str, Any]) -> str:
        """Classify the type of API interface"""
        path = endpoint.get('path', '').lower()
        
        if 'read' in path or 'get' in path:
            return 'query_interface'
        elif 'create' in path or 'add' in path or 'new' in path:
            return 'creation_interface'
        elif 'update' in path or 'modify' in path or 'edit' in path:
            return 'modification_interface'
        elif 'delete' in path or 'remove' in path or 'destroy' in path:
            return 'deletion_interface'
        else:
            return 'general_interface'
    
    def _determine_cognitive_domain(self, endpoint: Dict[str, Any]) -> str:
        """Determine the cognitive domain of the endpoint"""
        path = endpoint.get('path', '').lower()
        
        if any(domain in path for domain in ['market', 'trading', 'price', 'ticker']):
            return 'market_domain'
        elif any(domain in path for domain in ['cognitive', 'ai', 'reasoning', 'learning']):
            return 'cognitive_domain'
        elif any(domain in path for domain in ['system', 'health', 'status', 'metrics']):
            return 'system_domain'
        elif any(domain in path for domain in ['user', 'auth', 'permission', 'governance']):
            return 'governance_domain'
        else:
            return 'general_domain'
    
    def _assess_governance_level(self, endpoint: Dict[str, Any]) -> str:
        """Assess the governance level required for the endpoint"""
        methods = endpoint.get('methods', [])
        
        if 'DELETE' in methods:
            return 'high_governance'
        elif 'PUT' in methods or 'POST' in methods:
            return 'medium_governance'
        else:
            return 'low_governance'
    
    def _assess_endpoint_complexity(self, endpoint: Dict[str, Any]) -> str:
        """Assess the complexity of the endpoint"""
        path = endpoint.get('path', '')
        handler = endpoint.get('handler', '')
        
        # Path complexity
        path_depth = len([p for p in path.split('/') if p])
        if path_depth > 3:
            path_complexity = 'high'
        elif path_depth > 1:
            path_complexity = 'moderate'
        else:
            path_complexity = 'low'
        
        # Handler complexity
        handler_complexity = 'unknown'
        
        return f'{path_complexity}_complexity'
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        """Main adaptation method for FastAPI data"""
        # Determine data type and route to appropriate adapter
        if isinstance(data, dict):
            if 'method' in data or 'path' in data:
                return self.adapt_request_data(data)
            elif 'status_code' in data or 'latency' in data:
                return self.adapt_response_data(data, {})
            elif 'handler' in data or 'methods' in data:
                return self.adapt_endpoint_data(data)
        
        # Default adaptation
        return self.enhance_data(data)
    
    def reverse_adapt_data(self, internal_data: Any, target_format: DataFormat) -> Any:
        """Reverse adaptation for FastAPI data"""
        # Remove DIX VISION enhancements
        if isinstance(internal_data, dict) and 'data' in internal_data:
            data = internal_data['data']
        else:
            data = internal_data
        
        # Reverse concept mappings
        if target_format == DataFormat.JSON:
            return self._reverse_json_fastapi_data(data)
        
        return data
    
    def _reverse_json_fastapi_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse JSON FastAPI data adaptation"""
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
    adapter = FastAPIDomainAdapter()
    
    # Example request adaptation
    sample_request = {
        'method': 'GET',
        'path': '/api/market/ticker/BTC/USDT',
        'headers': {
            'content-type': 'application/json',
            'user-agent': 'DIX VISION Client'
        },
        'body': {}
    }
    
    adapted_request = adapter.adapt_request_data(sample_request)
    print("Adapted request:", adapted)
    
    print("FastAPI Domain Adapter initialized successfully")
