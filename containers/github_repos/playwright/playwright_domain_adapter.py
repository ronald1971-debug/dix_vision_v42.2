"""
Playwright Domain Adapter for DIX VISION Integration

This adapter translates Playwright browser automation concepts into DIX VISION's
cognitive architecture, ensuring proper domain mapping and data transformation.

Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append('/app/adapters')

from base_domain_adapter import DataFormat, SystemDomainAdapter


class PlaywrightDomainAdapter(SystemDomainAdapter):
    """
    Domain adapter for Playwright browser automation data.
    
    This adapter handles:
    - Browser automation concept mapping
    - Page interaction data transformation
    - Content extraction integration
    - Session data standardization
    - Cognitive enhancement for browser operations
    """
    
    def __init__(self):
        super().__init__("playwright")
        
        # Playwright-specific concept mappings
        self.register_concept_mapping('browser', 'cognitive_interface')
        self.register_concept_mapping('page', 'content_context')
        self.register_concept_mapping('element', 'interface_component')
        self.register_concept_mapping('action', 'interaction_operation')
        self.register_concept_mapping('screenshot', 'visual_capture')
        
        # Browser action mappings
        self.action_mappings = {
            'click': 'select_interaction',
            'fill': 'input_interaction',
            'type': 'input_interaction',
            'navigate': 'context_transition',
            'scroll': 'content_exploration',
            'screenshot': 'visual_capture',
            'content': 'text_extraction',
            'evaluate': 'script_execution'
        }
        
    def adapt_browser_action_data(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt Playwright browser action data to DIX VISION format.
        
        Args:
            action: Action data (action_type, selector, parameters)
        
        Returns:
            Adapted action with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'interaction_operation': {
                    'operation_type': self.action_mappings.get(action.get('action_type', 'unknown'), 'unknown_interaction'),
                    'target_component': action.get('selector', 'unknown'),
                    'initiated_at': datetime.utcnow().isoformat()
                },
                'operation_parameters': {
                    'action_type': action.get('action_type', 'unknown'),
                    'selector': action.get('selector', ''),
                    'parameters': action.get('parameters', {}),
                    'timeout': action.get('timeout', 30000)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'action_class': self._classify_action(action),
                'complexity': self._assess_action_complexity(action),
                'security_context': self._assess_security_context(action),
                'performance_expectation': self._predict_performance(action),
                'target_domain': self._extract_target_domain(action)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'browser_action',
                'source': 'playwright',
                'cognitive_layer': 'browser_interface'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt browser action data: {str(e)}")
            raise
    
    def adapt_page_content_data(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt Playwright page content data to DIX VISION format.
        
        Args:
            content: Content data (url, title, text, elements)
        
        Returns:
            Adapted content with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'content_context': {
                    'context_url': content.get('url', ''),
                    'context_title': content.get('title', ''),
                    'context_type': content.get('content_type', 'web_page'),
                    'captured_at': datetime.utcnow().isoformat()
                },
                'content_metadata': {
                    'text_content': content.get('text', ''),
                    'html_content': content.get('html', ''),
                    'elements': content.get('elements', []),
                    'links': content.get('links', []),
                    'images': content.get('images', [])
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'content_class': self._classify_content(content),
                'richness': self._assess_content_richness(content),
                'relevance': self._assess_content_relevance(content),
                'data_quality': self._assess_data_quality(content),
                'cognitive_insight': self._extract_cognitive_insight(content)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'page_content',
                'source': 'playwright',
                'cognitive_layer': 'content_acquisition'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt page content data: {str(e)}")
            raise
    
    def adapt_screenshot_data(self, screenshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt Playwright screenshot data to DIX VISION format.
        
        Args:
            screenshot: Screenshot data (path, size, timestamp)
        
        Returns:
            Adapted screenshot with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'visual_capture': {
                    'capture_path': screenshot.get('path', ''),
                    'capture_type': screenshot.get('type', 'png'),
                    'capture_dimensions': {
                        'width': screenshot.get('width', 0),
                        'height': screenshot.get('height', 0)
                    },
                    'captured_at': datetime.utcnow().isoformat()
                },
                'capture_metadata': {
                    'context_url': screenshot.get('url', ''),
                    'element_target': screenshot.get('element', None),
                    'clip_region': screenshot.get('clip', {}),
                    'quality': screenshot.get('quality', 100)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'capture_purpose': self._determine_capture_purpose(screenshot),
                'visual_quality': self._assess_visual_quality(screenshot),
                'information_density': self._assess_information_density(screenshot),
                'analysis_ready': True
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'screenshot',
                'source': 'playwright',
                'cognitive_layer': 'visual_interface'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt screenshot data: {str(e)}")
            raise
    
    def adapt_session_data(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt Playwright session data to DIX VISION format.
        
        Args:
            session: Session data (browser_type, pages, cookies, etc.)
        
        Returns:
            Adapted session with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'cognitive_interface': {
                    'interface_id': session.get('session_id', 'unknown'),
                    'interface_type': session.get('browser_type', 'chromium'),
                    'state': session.get('state', 'active'),
                    'established_at': session.get('created_at', datetime.utcnow().isoformat())
                },
                'interface_metadata': {
                    'user_agent': session.get('user_agent', 'unknown'),
                    'viewport': session.get('viewport', {}),
                    'cookies': session.get('cookies', []),
                    'pages': session.get('pages', []),
                    'context_count': session.get('context_count', 1)
                }
            }
            
            # Add cognitive enhancement
            adapted['cognitive_metadata'] = {
                'interface_capacity': self._assess_interface_capacity(session),
                'interaction_depth': self._assess_interaction_depth(session),
                'session_persistence': self._assess_session_persistence(session),
                'automation_capability': self._assess_automation_capability(session)
            }
            
            return self.enhance_data(adapted, {
                'data_type': 'browser_session',
                'source': 'playwright',
                'cognitive_layer': 'session_management'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt session data: {str(e)}")
            raise
    
    def _classify_action(self, action: Dict[str, Any]) -> str:
        """Classify the type of browser action"""
        action_type = action.get('action_type', '').lower()
        
        if action_type in ['click', 'tap', 'double_click']:
            return 'selection_action'
        elif action_type in ['fill', 'type', 'press']:
            return 'input_action'
        elif action_type in ['navigate', 'goto']:
            return 'navigation_action'
        elif action_type in ['scroll', 'wheel']:
            return 'exploration_action'
        elif action_type == 'screenshot':
            return 'visual_action'
        elif action_type in ['content', 'text', 'inner_text']:
            return 'extraction_action'
        elif action_type in ['evaluate', 'evaluate_handle']:
            return 'script_action'
        else:
            return 'general_action'
    
    def _assess_action_complexity(self, action: Dict[str, Any]) -> str:
        """Assess the complexity of the browser action"""
        parameters = action.get('parameters', {})
        selector = action.get('selector', '')
        
        param_count = len(parameters)
        selector_depth = selector.count('>')
        
        if param_count > 5 or selector_depth > 3:
            return 'high_complexity'
        elif param_count > 2 or selector_depth > 1:
            return 'moderate_complexity'
        else:
            return 'low_complexity'
    
    def _assess_security_context(self, action: Dict[str, Any]) -> str:
        """Assess the security context of the action"""
        action_type = action.get('action_type', '').lower()
        parameters = action.get('parameters', {})
        
        if action_type in ['evaluate', 'evaluate_handle', 'execute']:
            return 'high_risk'
        elif action_type in ['fill', 'type']:
            return 'medium_risk'
        elif action_type in ['navigate', 'goto']:
            return 'navigation_risk'
        else:
            return 'low_risk'
    
    def _predict_performance(self, action: Dict[str, Any]) -> str:
        """Predict the performance expectation"""
        action_type = action.get('action_type', '').lower()
        complexity = self._assess_action_complexity(action)
        
        if action_type == 'screenshot':
            return 'high_latency'
        elif complexity == 'high_complexity':
            return 'moderate_latency'
        else:
            return 'low_latency'
    
    def _extract_target_domain(self, action: Dict[str, Any]) -> str:
        """Extract the target domain from the action"""
        selector = action.get('selector', '')
        url = action.get('url', '')
        
        if url:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc if parsed.netloc else 'unknown'
        else:
            return 'current_page'
    
    def _classify_content(self, content: Dict[str, Any]) -> str:
        """Classify the type of page content"""
        content_type = content.get('content_type', '').lower()
        url = content.get('url', '').lower()
        
        if 'json' in content_type or 'api' in url:
            return 'api_response'
        elif any(domain in url for domain in ['dashboard', 'admin', 'panel']):
            return 'dashboard_content'
        elif any(domain in url for domain in ['shop', 'store', 'cart']):
            return 'ecommerce_content'
        elif any(domain in url for domain in ['blog', 'article', 'news']):
            return 'article_content'
        else:
            return 'web_content'
    
    def _assess_content_richness(self, content: Dict[str, Any]) -> str:
        """Assess the richness of the content"""
        text_length = len(content.get('text', ''))
        elements_count = len(content.get('elements', []))
        links_count = len(content.get('links', []))
        
        total_content = text_length + elements_count + links_count
        
        if total_content > 10000:
            return 'rich_content'
        elif total_content > 1000:
            return 'moderate_content'
        else:
            return 'minimal_content'
    
    def _assess_content_relevance(self, content: Dict[str, Any]) -> str:
        """Assess the relevance of the content"""
        url = content.get('url', '').lower()
        
        if any(term in url for term in ['api', 'data', 'json']):
            return 'high_relevance'
        elif any(term in url for term in ['dashboard', 'admin']):
            return 'operational_relevance'
        else:
            return 'general_relevance'
    
    def _assess_data_quality(self, content: Dict[str, Any]) -> str:
        """Assess the quality of the data"""
        text = content.get('text', '')
        html = content.get('html', '')
        
        if text and html:
            return 'high_quality'
        elif text:
            return 'medium_quality'
        else:
            return 'low_quality'
    
    def _extract_cognitive_insight(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cognitive insight from the content"""
        text = content.get('text', '')
        url = content.get('url', '')
        
        return {
            'content_density': 'high' if len(text) > 1000 else 'low',
            'interactive_elements': len(content.get('links', [])) + len(content.get('elements', [])),
            'structural_complexity': 'complex' if len(text) > 5000 else 'simple',
            'data_extraction_ready': True
        }
    
    def _determine_capture_purpose(self, screenshot: Dict[str, Any]) -> str:
        """Determine the purpose of the screenshot"""
        element = screenshot.get('element')
        full_page = screenshot.get('full_page', False)
        
        if element:
            return 'element_capture'
        elif full_page:
            return 'page_capture'
        else:
            return 'viewport_capture'
    
    def _assess_visual_quality(self, screenshot: Dict[str, Any]) -> str:
        """Assess the visual quality of the screenshot"""
        quality = screenshot.get('quality', 100)
        width = screenshot.get('width', 0)
        height = screenshot.get('height', 0)
        
        if quality >= 90 and width > 1000 and height > 800:
            return 'high_quality'
        elif quality >= 70:
            return 'acceptable_quality'
        else:
            return 'low_quality'
    
    def _assess_information_density(self, screenshot: Dict[str, Any]) -> str:
        """Assess the information density of the screenshot"""
        # Simplified assessment based on dimensions
        area = screenshot.get('width', 0) * screenshot.get('height', 0)
        
        if area > 2000000:
            return 'high_density'
        elif area > 500000:
            return 'medium_density'
        else:
            return 'low_density'
    
    def _assess_interface_capacity(self, session: Dict[str, Any]) -> str:
        """Assess the capacity of the browser interface"""
        context_count = session.get('context_count', 1)
        pages_count = len(session.get('pages', []))
        
        if context_count > 3 or pages_count > 10:
            return 'high_capacity'
        elif context_count > 1 or pages_count > 5:
            return 'moderate_capacity'
        else:
            return 'single_capacity'
    
    def _assess_interaction_depth(self, session: Dict[str, Any]) -> str:
        """Assess the interaction depth of the session"""
        cookies_count = len(session.get('cookies', []))
        
        if cookies_count > 20:
            return 'deep_interaction'
        elif cookies_count > 5:
            return 'moderate_interaction'
        else:
            return 'shallow_interaction'
    
    def _assess_session_persistence(self, session: Dict[str, Any]) -> str:
        """Assess the persistence of the session"""
        cookies = session.get('cookies', [])
        storage = session.get('storage', {})
        
        if cookies or storage:
            return 'persistent_session'
        else:
            return 'ephemeral_session'
    
    def _assess_automation_capability(self, session: Dict[str, Any]) -> str:
        """Assess the automation capability of the session"""
        browser_type = session.get('browser_type', '').lower()
        
        if browser_type in ['chromium', 'firefox', 'webkit']:
            return 'full_automation'
        else:
            return 'limited_automation'
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        """Main adaptation method for Playwright data"""
        # Determine data type and route to appropriate adapter
        if isinstance(data, dict):
            if 'action_type' in data or 'selector' in data:
                return self.adapt_browser_action_data(data)
            elif 'url' in data and 'text' in data:
                return self.adapt_page_content_data(data)
            elif 'path' in data and 'type' in data:
                return self.adapt_screenshot_data(data)
            elif 'session_id' in data or 'browser_type' in data:
                return self.adapt_session_data(data)
        
        # Default adaptation
        return self.enhance_data(data)
    
    def reverse_adapt_data(self, internal_data: Any, target_format: DataFormat) -> Any:
        """Reverse adaptation for Playwright data"""
        # Remove DIX VISION enhancements
        if isinstance(internal_data, dict) and 'data' in internal_data:
            data = internal_data['data']
        else:
            data = internal_data
        
        # Reverse concept mappings
        if target_format == DataFormat.JSON:
            return self._reverse_json_playwright_data(data)
        
        return data
    
    def _reverse_json_playwright_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse JSON Playwright data adaptation"""
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
    adapter = PlaywrightDomainAdapter()
    
    # Example action adaptation
    sample_action = {
        'action_type': 'click',
        'selector': '#submit-button',
        'parameters': {'timeout': 30000},
        'url': 'https://example.com'
    }
    
    adapted_action = adapter.adapt_browser_action_data(sample_action)
    print("Adapted action:", adapted_action)
    
    print("Playwright Domain Adapter initialized successfully")
