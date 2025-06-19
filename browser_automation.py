"""
Browser Automation Handler using Playwright
Handles all browser operations including login, navigation, and element interaction
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from config import SaaSConfig, SETTINGS
import logging

class BrowserAutomationHandler:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs(SETTINGS["logs_dir"], exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{SETTINGS['logs_dir']}/browser_automation.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def initialize_browser(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=SETTINGS["browser_headless"]
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = await self.context.new_page()
            self.page.set_default_timeout(SETTINGS["page_timeout"])
            self.logger.info("Browser initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {str(e)}")
            return False

    async def login_to_saas(self, config: SaaSConfig, username: str, password: str) -> bool:
        """
        Login to SaaS application using provided credentials
        """
        try:
            self.logger.info(f"Attempting login to {config.name}")

            # Navigate to login page
            await self.page.goto(config.login_url)
            await self.page.wait_for_load_state('networkidle')

            # Fill login credentials
            await self.page.fill(config.username_selector, username)
            await self.page.fill(config.password_selector, password)

            # Click login button
            await self.page.click(config.login_button_selector)
            await self.page.wait_for_load_state('networkidle')

            # Check if login was successful (basic check)
            current_url = self.page.url
            if "login" not in current_url.lower():
                self.logger.info(f"Login successful to {config.name}")
                return True
            else:
                self.logger.error(f"Login failed to {config.name}")
                await self.take_screenshot("login_failed")
                return False

        except Exception as e:
            self.logger.error(f"Login error for {config.name}: {str(e)}")
            await self.take_screenshot("login_error")
            return False

    async def navigate_to_users_page(self, config: SaaSConfig) -> bool:
        """Navigate to the users management page"""
        try:
            await self.page.goto(config.users_page_url)
            await self.page.wait_for_load_state('networkidle')
            self.logger.info(f"Navigated to users page for {config.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to users page: {str(e)}")
            return False

    async def extract_page_content(self) -> str:
        """Extract HTML content from current page"""
        try:
            content = await self.page.content()
            return content
        except Exception as e:
            self.logger.error(f"Failed to extract page content: {str(e)}")
            return ""

    async def find_elements(self, selector: str) -> List[Dict[str, Any]]:
        """Find elements on page and extract their properties"""
        try:
            elements = await self.page.query_selector_all(selector)
            element_data = []

            for element in elements:
                data = {
                    "text": await element.text_content(),
                    "inner_html": await element.inner_html(),
                    "attributes": {}
                }

                # Get common attributes
                for attr in ["id", "class", "data-testid", "role"]:
                    value = await element.get_attribute(attr)
                    if value:
                        data["attributes"][attr] = value

                element_data.append(data)

            return element_data
        except Exception as e:
            self.logger.error(f"Failed to find elements with selector {selector}: {str(e)}")
            return []

    async def click_element(self, selector: str) -> bool:
        """Click an element by selector"""
        try:
            await self.page.click(selector)
            await self.page.wait_for_load_state('networkidle')
            return True
        except Exception as e:
            self.logger.error(f"Failed to click element {selector}: {str(e)}")
            return False

    async def fill_form(self, form_data: Dict[str, str]) -> bool:
        """Fill out a form with provided data"""
        try:
            for selector, value in form_data.items():
                await self.page.fill(selector, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to fill form: {str(e)}")
            return False

    async def take_screenshot(self, name: str = None) -> str:
        """Take screenshot of current page"""
        try:
            if name is None:
                name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            screenshot_path = f"{SETTINGS['logs_dir']}/{name}.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
            return ""

    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to appear on page"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            self.logger.error(f"Element {selector} not found within timeout: {str(e)}")
            return False

    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("Browser cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
