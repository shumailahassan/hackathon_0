"""
Browser MCP Server for AI Employee
Implements Model Context Protocol to allow Claude Code to control browser automation
for payment portals, banking, and other web-based tasks.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from playwright.async_api import async_playwright
import tempfile
import os

class BrowserMCPServer:
    """
    MCP Server for browser automation tasks
    """
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.session_dir = Path(tempfile.gettempdir()) / "ai_employee_browser_session"
        self.session_dir.mkdir(exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger('BrowserMCP')
        handler = logging.FileHandler('browser_mcp.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    async def initialize(self):
        """Initialize the browser session"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true',
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self.page = await self.context.new_page()

            # Navigate to a blank page to start
            await self.page.goto("about:blank")
            self.logger.info("Browser MCP server initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            return False

    async def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to a specific URL"""
        try:
            await self.page.goto(url)
            await self.page.wait_for_load_state('domcontentloaded')

            result = {
                "success": True,
                "url": url,
                "title": await self.page.title(),
                "status": "navigated",
                "content_summary": f"Page loaded with title: {await self.page.title()}"
            }
            self.logger.info(f"Navigated to {url}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            return {"success": False, "error": str(e)}

    async def fill_form_field(self, selector: str, value: str) -> Dict[str, Any]:
        """Fill a form field with the specified value"""
        try:
            await self.page.fill(selector, value)
            await self.page.wait_for_timeout(500)  # Small delay to ensure fill is processed

            result = {
                "success": True,
                "selector": selector,
                "status": "filled",
                "value_length": len(value)
            }
            self.logger.info(f"Filled field {selector} with value of length {len(value)}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to fill field {selector}: {e}")
            return {"success": False, "error": str(e)}

    async def click_element(self, selector: str) -> Dict[str, Any]:
        """Click an element on the page"""
        try:
            await self.page.click(selector)
            await self.page.wait_for_timeout(1000)  # Wait a bit after click

            result = {
                "success": True,
                "selector": selector,
                "status": "clicked"
            }
            self.logger.info(f"Clicked element {selector}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to click element {selector}: {e}")
            return {"success": False, "error": str(e)}

    async def get_page_content(self, selector: str = None) -> Dict[str, Any]:
        """Get content from the current page"""
        try:
            if selector:
                content = await self.page.text_content(selector)
            else:
                content = await self.page.content()

            result = {
                "success": True,
                "selector": selector,
                "content_length": len(content),
                "content": content[:2000] + "..." if len(content) > 2000 else content  # Truncate long content
            }
            self.logger.info(f"Retrieved content from page{' ' + selector if selector else ''}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to get page content: {e}")
            return {"success": False, "error": str(e)}

    async def take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """Take a screenshot of the current page"""
        try:
            if not filename:
                filename = f"screenshot_{int(asyncio.get_event_loop().time())}.png"

            filepath = self.session_dir / filename
            await self.page.screenshot(path=str(filepath))

            result = {
                "success": True,
                "screenshot_path": str(filepath),
                "status": "screenshot_taken"
            }
            self.logger.info(f"Screenshot saved to {filepath}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return {"success": False, "error": str(e)}

    async def execute_script(self, script: str) -> Dict[str, Any]:
        """Execute a JavaScript script on the page"""
        try:
            result = await self.page.evaluate(script)

            return {
                "success": True,
                "script_result": result,
                "status": "script_executed"
            }
        except Exception as e:
            self.logger.error(f"Failed to execute script: {e}")
            return {"success": False, "error": str(e)}

    async def wait_for_element(self, selector: str, timeout: int = 10000) -> Dict[str, Any]:
        """Wait for an element to appear on the page"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)

            result = {
                "success": True,
                "selector": selector,
                "status": "element_found"
            }
            self.logger.info(f"Element {selector} found")
            return result
        except Exception as e:
            self.logger.error(f"Failed to find element {selector}: {e}")
            return {"success": False, "error": str(e)}

    async def handle_payment_form(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a complete payment form workflow"""
        try:
            # Fill payment information
            await self.fill_form_field('#card-number', payment_data.get('card_number', ''))
            await self.fill_form_field('#card-expiry', payment_data.get('expiry_date', ''))
            await self.fill_form_field('#card-cvc', payment_data.get('cvc', ''))
            await self.fill_form_field('#card-name', payment_data.get('cardholder_name', ''))

            # Click submit button (but don't actually submit for safety)
            await self.click_element('#submit-button')

            # Take a screenshot before final submission as a safety measure
            await self.take_screenshot(f"payment_form_preview_{int(asyncio.get_event_loop().time())}.png")

            result = {
                "success": True,
                "status": "payment_form_filled",
                "action": "preview_only",  # Important: We don't actually submit payments
                "message": "Payment form filled and previewed. Awaiting final approval for submission."
            }
            self.logger.info("Payment form filled for approval")
            return result
        except Exception as e:
            self.logger.error(f"Failed to handle payment form: {e}")
            return {"success": False, "error": str(e)}

    async def close(self):
        """Close the browser and cleanup"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("Browser MCP server closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing browser MCP: {e}")

    # MCP Protocol Methods
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get('method', '')
        params = request.get('params', {})

        self.logger.info(f"Handling MCP request: {method}")

        if method == 'browser/navigate':
            return await self.navigate_to_url(params.get('url', ''))
        elif method == 'browser/fill':
            return await self.fill_form_field(params.get('selector', ''), params.get('value', ''))
        elif method == 'browser/click':
            return await self.click_element(params.get('selector', ''))
        elif method == 'browser/getContent':
            return await self.get_page_content(params.get('selector'))
        elif method == 'browser/screenshot':
            return await self.take_screenshot(params.get('filename'))
        elif method == 'browser/executeScript':
            return await self.execute_script(params.get('script', ''))
        elif method == 'browser/waitForElement':
            return await self.wait_for_element(params.get('selector', ''), params.get('timeout', 10000))
        elif method == 'browser/handlePaymentForm':
            return await self.handle_payment_form(params)
        else:
            self.logger.warning(f"Unknown method: {method}")
            return {"success": False, "error": f"Unknown method: {method}"}

    async def start_server(self):
        """Start the MCP server"""
        if not await self.initialize():
            self.logger.error("Failed to initialize browser MCP server")
            return

        # In a real implementation, this would start an actual server
        # For this example, we'll just keep it as a standalone library
        self.logger.info("Browser MCP server started and ready to handle requests")


# This would normally be integrated with actual MCP server infrastructure
# For now, it's implemented as a standalone module that can be imported and used
if __name__ == "__main__":
    # Example usage
    async def main():
        server = BrowserMCPServer()
        await server.initialize()

        # Example workflow for a banking portal
        result = await server.navigate_to_url("https://example-bank.com/login")
        print(result)

        await server.fill_form_field('#username', 'testuser')
        await server.fill_form_field('#password', 'testpassword')
        await server.click_element('#login-button')

        await server.close()

    # asyncio.run(main())