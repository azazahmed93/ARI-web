"""
Screenshot Service - Local screenshot capture using Playwright.
Replaced cloud-based services (Browserless, ScreenshotAPI) with local Playwright.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from io import BytesIO

# Configure logging
logger = logging.getLogger(__name__)


class PlaywrightScreenshotService:
    """
    Screenshot service using local Playwright installation.

    Requires:
    - pip install playwright
    - playwright install chromium
    """

    def __init__(self):
        self._browser = None
        self._playwright = None

    def capture_html(
        self,
        html_content: str,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        full_page: bool = True,
        wait_time: int = 2000
    ) -> bytes:
        """
        Capture screenshot from HTML content.

        Args:
            html_content: Raw HTML to render
            viewport_width: Browser viewport width
            viewport_height: Browser viewport height
            full_page: Whether to capture full scrollable page
            wait_time: Time to wait for page to render (ms)

        Returns:
            PNG image bytes
        """
        from playwright.sync_api import sync_playwright
        import time

        logger.info(f"Capturing HTML screenshot ({len(html_content):,} chars)")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': viewport_width, 'height': viewport_height})

            # Load HTML content
            page.set_content(html_content)

            # Wait for rendering
            if wait_time > 0:
                time.sleep(wait_time / 1000)

            # Capture screenshot
            screenshot_bytes = page.screenshot(type='png', full_page=full_page)

            browser.close()
            logger.info(f"  ✓ Screenshot captured ({len(screenshot_bytes):,} bytes)")

            return screenshot_bytes

    def capture_url(
        self,
        url: str,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        full_page: bool = True,
        wait_for_selector: Optional[str] = None,
        wait_time: int = 3000
    ) -> bytes:
        """
        Capture screenshot from a URL.

        Args:
            url: URL to navigate to and capture
            viewport_width: Browser viewport width
            viewport_height: Browser viewport height
            full_page: Whether to capture full scrollable page
            wait_for_selector: CSS selector to wait for before capture
            wait_time: Time to wait for page to render (ms)

        Returns:
            PNG image bytes
        """
        from playwright.sync_api import sync_playwright
        import time

        logger.info(f"Capturing URL screenshot: {url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': viewport_width, 'height': viewport_height})

            # Navigate to URL
            page.goto(url, wait_until='networkidle', timeout=60000)

            # Wait for selector if specified
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector, timeout=15000)

            # Additional wait time
            if wait_time > 0:
                time.sleep(wait_time / 1000)

            # Capture screenshot
            screenshot_bytes = page.screenshot(type='png', full_page=full_page)

            browser.close()
            logger.info(f"  ✓ Screenshot captured ({len(screenshot_bytes):,} bytes)")

            return screenshot_bytes


def create_screenshot_service() -> PlaywrightScreenshotService:
    """
    Factory function to create the Playwright screenshot service.

    Returns:
        PlaywrightScreenshotService instance

    Raises:
        ImportError if Playwright is not installed
    """
    try:
        from playwright.sync_api import sync_playwright
        logger.info("Playwright screenshot service initialized")
        return PlaywrightScreenshotService()
    except ImportError:
        raise ImportError(
            "Playwright is not installed. Run: pip install playwright && playwright install chromium"
        )


def capture_react_component(
    component_name: str,
    html_content: str,
    data_replacements: Dict[str, Any],
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    wait_time: int = 4000
) -> bytes:
    """
    Convenience function to capture a React component screenshot.

    Args:
        component_name: Name of the component for logging
        html_content: HTML template content
        data_replacements: Dictionary of template variables to replace
        viewport_width: Viewport width
        viewport_height: Viewport height
        wait_time: Time to wait for React to render

    Returns:
        PNG image bytes
    """
    logger.info(f"Capturing React component: {component_name}")

    # Replace template variables
    processed_html = html_content
    for key, value in data_replacements.items():
        placeholder = '{{' + key + '}}'
        if placeholder in processed_html:
            if isinstance(value, (dict, list)):
                processed_html = processed_html.replace(placeholder, json.dumps(value))
            else:
                processed_html = processed_html.replace(placeholder, str(value))

    # Add export mode indicator to the HTML
    export_script = """
    <script>
        window.EXPORT_MODE = true;
        window.addEventListener('load', function() {
            document.body.setAttribute('data-export-mode', 'true');
        });
    </script>
    """
    processed_html = processed_html.replace('</head>', f'{export_script}</head>')

    # Capture screenshot using Playwright
    service = create_screenshot_service()
    return service.capture_html(
        processed_html,
        viewport_width=viewport_width,
        viewport_height=viewport_height,
        wait_time=wait_time
    )


def test_screenshot_service() -> bool:
    """
    Test if screenshot service is working.

    Returns:
        True if service is operational
    """
    try:
        service = create_screenshot_service()
        test_html = "<html><body><h1>Test</h1></body></html>"
        result = service.capture_html(test_html, viewport_width=800, viewport_height=600)
        return len(result) > 0
    except Exception as e:
        logger.error(f"Screenshot service test failed: {e}")
        return False
