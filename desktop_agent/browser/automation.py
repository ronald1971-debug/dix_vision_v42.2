"""
Browser Automation - Enhanced browser control with Selenium/Playwright
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class BrowserType(Enum):
    """Supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


@dataclass
class BrowserConfig:
    """Browser configuration."""
    browser_type: BrowserType
    headless: bool = True
    timeout: int = 30
    user_agent: str = "DIX VISION Desktop AgentOS/42.2"
    window_size: tuple = (1920, 1080)


class SeleniumBrowserAutomation:
    """
    Browser automation using Selenium WebDriver.
    
    Provides real browser control for the Browser Cognitive Bridge
    with support for multiple browsers and advanced automation features.
    """
    
    def __init__(self, config: BrowserConfig):
        """
        Initialize Selenium browser automation.
        
        Args:
            config: Browser configuration
        """
        self.config = config
        self.driver = None
        self.is_initialized = False
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> bool:
        """
        Initialize the browser driver.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Import Selenium (lazy import for optional dependency)
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Configure browser options
            if self.config.browser_type == BrowserType.CHROME:
                from selenium.webdriver.chrome.options import Options
                options = Options()
                if self.config.headless:
                    options.add_argument('--headless')
                options.add_argument(f'user-agent={self.config.user_agent}')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                self.driver = webdriver.Chrome(options=options)
                
            elif self.config.browser_type == BrowserType.FIREFOX:
                from selenium.webdriver.firefox.options import Options
                options = Options()
                if self.config.headless:
                    options.add_argument('--headless')
                options.set_preference("general.useragent.override", self.config.user_agent)
                self.driver = webdriver.Firefox(options=options)
                
            elif self.config.browser_type == BrowserType.EDGE:
                from selenium.webdriver.edge.options import Options
                options = Options()
                if self.config.headless:
                    options.add_argument('--headless')
                options.add_argument(f'user-agent={self.config.user_agent}')
                self.driver = webdriver.Edge(options=options)
                
            # Set window size
            self.driver.set_window_size(*self.config.window_size)
            self.driver.implicitly_wait(self.config.timeout)
            
            self.is_initialized = True
            self.logger.info(f"Selenium {self.config.browser_type.value} browser initialized")
            return True
            
        except ImportError:
            self.logger.error("Selenium not installed. Install with: pip install selenium")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            return False
            
    async def navigate(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            self.logger.error(f"Navigation error: {e}")
            return False
            
    async def find_element(self, selector: str, by: str = "css") -> Optional[Any]:
        """
        Find an element by selector.
        
        Args:
            selector: Element selector
            by: Selector type (css, xpath, id, name, class)
            
        Returns:
            Element or None
        """
        try:
            from selenium.webdriver.common.by import By
            
            by_mapping = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
            }
            
            by_type = by_mapping.get(by.lower(), By.CSS_SELECTOR)
            element = self.driver.find_element(by_type, selector)
            return element
            
        except Exception as e:
            self.logger.error(f"Element not found: {e}")
            return None
            
    async def click_element(self, selector: str) -> bool:
        """
        Click an element.
        
        Args:
            selector: Element selector
            
        Returns:
            True if successful, False otherwise
        """
        try:
            element = await self.find_element(selector)
            if element:
                element.click()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Click error: {e}")
            return False
            
    async def type_text(self, selector: str, text: str) -> bool:
        """
        Type text into an element.
        
        Args:
            selector: Element selector
            text: Text to type
            
        Returns:
            True if successful, False otherwise
        """
        try:
            element = await self.find_element(selector)
            if element:
                element.clear()
                element.send_keys(text)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Type error: {e}")
            return False
            
    async def get_text(self, selector: str) -> Optional[str]:
        """
        Get text from an element.
        
        Args:
            selector: Element selector
            
        Returns:
            Element text or None
        """
        try:
            element = await self.find_element(selector)
            if element:
                return element.text
            return None
        except Exception as e:
            self.logger.error(f"Get text error: {e}")
            return None
            
    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get an attribute value from an element.
        
        Args:
            selector: Element selector
            attribute: Attribute name
            
        Returns:
            Attribute value or None
        """
        try:
            element = await self.find_element(selector)
            if element:
                return element.get_attribute(attribute)
            return None
        except Exception as e:
            self.logger.error(f"Get attribute error: {e}")
            return None
            
    async def execute_script(self, script: str) -> Any:
        """
        Execute JavaScript in the browser.
        
        Args:
            script: JavaScript code
            
        Returns:
            Script result
        """
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"Script execution error: {e}")
            return None
            
    async def take_screenshot(self, path: str) -> bool:
        """
        Take a screenshot.
        
        Args:
            path: Screenshot save path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.save_screenshot(path)
            return True
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            return False
            
    async def get_page_source(self) -> str:
        """
        Get the current page HTML.
        
        Returns:
            Page HTML source
        """
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Get page source error: {e}")
            return ""
            
    async def wait_for_element(
        self,
        selector: str,
        timeout: int = 10,
    ) -> Optional[Any]:
        """
        Wait for an element to appear.
        
        Args:
            selector: Element selector
            timeout: Timeout in seconds
            
        Returns:
            Element or None
        """
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as e:
            self.logger.error(f"Wait timeout: {e}")
            return None
            
    async def get_cookies(self) -> List[Dict[str, Any]]:
        """
        Get all cookies.
        
        Returns:
            List of cookies
        """
        try:
            return self.driver.get_cookies()
        except Exception as e:
            self.logger.error(f"Get cookies error: {e}")
            return []
            
    async def add_cookie(self, cookie: Dict[str, Any]) -> bool:
        """
        Add a cookie.
        
        Args:
            cookie: Cookie dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.add_cookie(cookie)
            return True
        except Exception as e:
            self.logger.error(f"Add cookie error: {e}")
            return False
            
    async def close(self) -> None:
        """Close the browser."""
        try:
            if self.driver:
                self.driver.quit()
                self.is_initialized = False
                self.logger.info("Browser closed")
        except Exception as e:
            self.logger.error(f"Close error: {e}")


class PlaywrightBrowserAutomation:
    """
    Browser automation using Playwright.
    
    Alternative to Selenium with modern async support and better performance.
    """
    
    def __init__(self, config: BrowserConfig):
        """
        Initialize Playwright browser automation.
        
        Args:
            config: Browser configuration
        """
        self.config = config
        self.browser = None
        self.context = None
        self.page = None
        self.is_initialized = False
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> bool:
        """
        Initialize the Playwright browser.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # Launch browser
            browser_type = self.config.browser_type.value
            if browser_type == "chrome":
                browser_type = "chromium"
                
            launch_options = {
                "headless": self.config.headless,
                "user_agent": self.config.user_agent,
            }
            
            self.browser = await getattr(self.playwright, browser_type).launch(**launch_options)
            self.context = await self.browser.new_context(
                viewport={"width": self.config.window_size[0], "height": self.config.window_size[1]}
            )
            self.page = await self.context.new_page()
            
            self.is_initialized = True
            self.logger.info(f"Playwright {browser_type} browser initialized")
            return True
            
        except ImportError:
            self.logger.error("Playwright not installed. Install with: pip install playwright")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            return False
            
    async def navigate(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.page.goto(url, timeout=self.config.timeout * 1000)
            return True
        except Exception as e:
            self.logger.error(f"Navigation error: {e}")
            return False
            
    async def click_element(self, selector: str) -> bool:
        """
        Click an element.
        
        Args:
            selector: Element selector
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.page.click(selector)
            return True
        except Exception as e:
            self.logger.error(f"Click error: {e}")
            return False
            
    async def type_text(self, selector: str, text: str) -> bool:
        """
        Type text into an element.
        
        Args:
            selector: Element selector
            text: Text to type
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.page.fill(selector, text)
            return True
        except Exception as e:
            self.logger.error(f"Type error: {e}")
            return False
            
    async def get_text(self, selector: str) -> Optional[str]:
        """
        Get text from an element.
        
        Args:
            selector: Element selector
            
        Returns:
            Element text or None
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.inner_text()
            return None
        except Exception as e:
            self.logger.error(f"Get text error: {e}")
            return None
            
    async def take_screenshot(self, path: str) -> bool:
        """
        Take a screenshot.
        
        Args:
            path: Screenshot save path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.page.screenshot(path=path)
            return True
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            return False
            
    async def close(self) -> None:
        """Close the browser."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.is_initialized = False
            self.logger.info("Browser closed")
        except Exception as e:
            self.logger.error(f"Close error: {e}")


def create_browser_automation(
    config: BrowserConfig,
    use_playwright: bool = False,
) -> Any:
    """
    Factory function to create browser automation instance.
    
    Args:
        config: Browser configuration
        use_playwright: Whether to use Playwright instead of Selenium
        
    Returns:
        Browser automation instance
    """
    if use_playwright:
        return PlaywrightBrowserAutomation(config)
    else:
        return SeleniumBrowserAutomation(config)
