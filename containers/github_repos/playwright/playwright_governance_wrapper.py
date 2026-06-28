"""
Playwright Governance Wrapper for DIX VISION Integration

This wrapper provides governance oversight for browser automation operations
through Playwright, ensuring operator authority, safety checks, and compliance
with DIX VISION's constitutional governance for Desktop AgentOS.

Author: DIX VISION Desktop Agent Governance
Version: 42.2
"""

import sys
import time
from datetime import datetime
from typing import Any, Dict

sys.path.append('/app/governance')

from base_external_repo_wrapper import (
    BaseExternalRepoGovernanceWrapper,
    ExternalRepositoryMetrics,
    GovernanceViolation,
    PermissionLevel,
)


class PlaywrightGovernanceWrapper(BaseExternalRepoGovernanceWrapper):
    """
    Governance wrapper for Playwright browser automation operations.
    
    This ensures that all browser operations are:
    - Governed by operator authority (operator has ultimate authority)
    - Validated for safety (restricted URLs, safe actions)
    - Audited for compliance (browser action logging, session tracking)
    - Monitored for performance (page load times, action success rates)
    """
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__("playwright", permission_level)
        self.metrics = ExternalRepositoryMetrics("playwright")
        self.playwright_instance = None
        self.browser_session = {}
        self.safety_restrictions = {
            'allowed_domains': [],  # Empty means all allowed (will be configured)
            'blocked_domains': ['malicious-site.com', 'phishing-site.com'],
            'allowed_actions': ['navigate', 'click', 'type', 'screenshot', 'extract'],
            'blocked_actions': ['download', 'execute_script', 'upload'],
            'max_session_duration': 3600,  # 1 hour
            'max_pages_per_session': 50
        }
        self.active_sessions = 0
        self.session_limits = {
            'max_concurrent_sessions': 3,
            'max_daily_sessions': 10
        }
        
    def initialize_playwright(self, browser_config: Dict[str, Any]):
        """
        Initialize Playwright with governance oversight.
        
        Args:
            browser_config: Browser configuration (headless, browser type, etc.)
        """
        try:
            from playwright.sync_api import sync_playwright
            
            browser_type = browser_config.get('browser_type', 'chromium')
            headless = browser_config.get('headless', True)
            
            self.logger.info(f"Initializing Playwright with {browser_type} browser (headless: {headless})")
            self.playwright_instance = sync_playwright().start()
            
            self.logger.info("Playwright initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Playwright: {str(e)}")
            raise GovernanceViolation(f"Playwright initialization failed: {str(e)}")
    
    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """
        Enhanced safety checks specific to browser automation.
        """
        if not self.safety_check_enabled:
            return True
            
        # Check basic safety
        if not super().safety_check(operation, params):
            return False
            
        # Browser-specific safety checks
        if 'navigate' in operation.lower():
            if not self._validate_navigation_safety(params):
                return False
                
        if 'action' in operation.lower():
            if not self._validate_action_safety(params):
                return False
                
        return True
    
    def _validate_navigation_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of navigation operations"""
        url = params.get('url', '')
        
        if not url:
            self.logger.warning("Navigation without URL")
            return False
            
        # Check URL format
        if not url.startswith(('http://', 'https://')):
            self.logger.warning(f"Invalid URL protocol: {url}")
            return False
            
        # Check blocked domains
        for blocked_domain in self.safety_restrictions['blocked_domains']:
            if blocked_domain in url:
                self.logger.warning(f"Blocked domain detected: {blocked_domain}")
                return False
                
        # Check allowed domains if configured
        if self.safety_restrictions['allowed_domains']:
            domain_allowed = any(allowed in url for allowed in self.safety_restrictions['allowed_domains'])
            if not domain_allowed:
                self.logger.warning(f"Domain not in allowed list: {url}")
                return False
                
        return True
    
    def _validate_action_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of browser actions"""
        action = params.get('action', '')
        
        # Check blocked actions
        if action in self.safety_restrictions['blocked_actions']:
            self.logger.warning(f"Blocked action attempted: {action}")
            return False
            
        # Check if action is allowed
        if self.safety_restrictions['allowed_actions'] and action not in self.safety_restrictions['allowed_actions']:
            self.logger.warning(f"Action not in allowed list: {action}")
            return False
            
        return True
    
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method for Playwright operations.
        """
        start_time = time.time()
        success = False
        
        try:
            if not self.playwright_instance:
                raise GovernanceViolation("Playwright instance not initialized")
            
            # Map operation to Playwright method
            if operation == 'start_browser':
                browser_type = params.get('browser_type', 'chromium')
                headless = params.get('headless', True)
                
                if browser_type == 'chromium':
                    browser = self.playwright_instance.chromium
                elif browser_type == 'firefox':
                    browser = self.playwright_instance.firefox
                else:
                    browser = self.playwright_instance.webkit
                
                context = browser.launch(headless=headless)
                page = context.new_page()
                
                session_id = f"session_{int(time.time())}"
                self.browser_session[session_id] = {
                    'browser': browser,
                    'context': context,
                    'page': page,
                    'start_time': datetime.utcnow(),
                    'page_count': 0
                }
                
                self.active_sessions += 1
                result = {'session_id': session_id, 'status': 'started'}
                
            elif operation == 'navigate':
                session_id = params.get('session_id')
                url = params.get('url')
                
                if session_id not in self.browser_session:
                    raise ValueError("Invalid session ID")
                    
                page = self.browser_session[session_id]['page']
                page.goto(url)
                
                self.browser_session[session_id]['page_count'] += 1
                result = {'url': url, 'status': 'navigated'}
                
            elif operation == 'screenshot':
                session_id = params.get('session_id')
                path = params.get('path', 'screenshot.png')
                
                if session_id not in self.browser_session:
                    raise ValueError("Invalid session ID")
                    
                page = self.browser_session[session_id]['page']
                page.screenshot(path=path)
                
                result = {'path': path, 'status': 'screenshot_captured'}
                
            elif operation == 'extract_text':
                session_id = params.get('session_id')
                
                if session_id not in self.browser_session:
                    raise ValueError("Invalid session ID")
                    
                page = self.browser_session[session_id]['page']
                text = page.inner_text('body')
                
                result = {'text': text, 'status': 'text_extracted'}
                
            elif operation == 'close_browser':
                session_id = params.get('session_id')
                
                if session_id not in self.browser_session:
                    raise ValueError("Invalid session ID")
                    
                session = self.browser_session[session_id]
                session['page'].close()
                session['context'].close()
                session['browser'].close()
                
                del self.browser_session[session_id]
                self.active_sessions -= 1
                result = {'session_id': session_id, 'status': 'closed'}
                
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            success = True
            execution_time = time.time() - start_time
            self.metrics.record_operation(success, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.record_operation(False, execution_time)
            self.logger.error(f"Playwright operation failed: {operation} - {str(e)}")
            raise
    
    def navigate_with_governance(self, 
                                session_id: str, 
                                url: str) -> Dict[str, Any]:
        """
        Navigate to URL with full governance oversight.
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.EXECUTE):
                raise GovernanceViolation("Execute permission required for browser navigation")
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                raise ValueError("Invalid URL protocol")
            
            # Execute with governance
            params = {
                'session_id': session_id,
                'url': url
            }
            
            result = self.execute_operation('navigate', params, PermissionLevel.EXECUTE)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Browser navigation failed: {str(e)}")
            raise
    
    def extract_page_content(self, session_id: str) -> Dict[str, Any]:
        """
        Extract page content with governance oversight.
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.READ_ONLY):
                raise GovernanceViolation("Read permission required for content extraction")
            
            # Execute with governance
            params = {'session_id': session_id}
            result = self.execute_operation('extract_text', params, PermissionLevel.READ_ONLY)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content extraction failed: {str(e)}")
            raise
    
    def get_browser_metrics(self) -> Dict[str, Any]:
        """Get browser automation metrics"""
        return {
            'repository_metrics': self.metrics.get_metrics(),
            'active_sessions': self.active_sessions,
            'session_limits': self.session_limits,
            'safety_restrictions': self.safety_restrictions,
            'permission_level': self.permission_level.value
        }


# Example usage
if __name__ == "__main__":
    # Create wrapper with appropriate permission level
    wrapper = PlaywrightGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Initialize Playwright
    # wrapper.initialize_playwright({
    #     'browser_type': 'chromium',
    #     'headless': True
    # })
    
    print("Playwright Governance Wrapper initialized successfully")
