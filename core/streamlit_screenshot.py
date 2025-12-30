"""
Streamlit Screenshot Service - Captures screenshots of Streamlit tabs using Playwright.
"""

import os
import json
import tempfile
import time
import logging
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')


# =============================================================================
# SCREENSHOT CONFIGURATION - ADJUST THESE VALUES TO RESIZE SLIDES
# =============================================================================
#
# How it works:
# 1. Playwright captures the [data-baseweb="tab-panel"] element
# 2. The viewport is resized to fit all scrollable content
# 3. AFTER capture, we crop pixels from top and bottom using PIL
#
# Visual explanation:
#
#   ┌─────────────────────────┐  ← 0px (original top)
#   │  ▓▓▓ CROPPED OUT ▓▓▓   │  ← This area is REMOVED (crop_top pixels)
#   ├─────────────────────────┤  ← crop_top (new top of final image)
#   │                         │
#   │   VISIBLE CONTENT       │  ← This is what appears in the slide
#   │                         │
#   ├─────────────────────────┤  ← original_height - crop_bottom (new bottom)
#   │  ▓▓▓ CROPPED OUT ▓▓▓   │  ← This area is REMOVED (crop_bottom pixels)
#   └─────────────────────────┘  ← original_height (original bottom)
#
# To SHOW MORE content: DECREASE crop values
# To SHOW LESS content: INCREASE crop values
#
# =============================================================================

TAB_SCREENSHOT_CONFIG = {
    "Detailed Metrics": {
        "crop_top": 25,        # Pixels to remove from TOP (increase to hide more header)
        "crop_bottom": 0,      # Pixels to remove from BOTTOM (increase to hide more footer)
        "extra_padding": 200,  # Extra viewport padding when resizing
    },
    "Audience Insights": {
        "crop_top": 60,         # Pixels to remove from top after capture
        "crop_bottom": 0,       # Pixels to remove from bottom after capture
        "extra_padding": 1500,  # Extra padding - increase for more content (was 800)
        "force_full_page": True,
        "capture_mode": "full_page",
        "min_height": 3450,     # Minimum viewport height to ensure full content capture
    },
    "Media Affinities": {
        "crop_top": 80,        # Remove header area (increase to crop more from top)
        "crop_bottom": 150,     # Reduced by 150px to show more content (was 480)
        "extra_padding": 200,
    },
    "Trend Analysis": {
        "crop_top": 130,        # Remove header area (increase to crop more from top)
        "crop_bottom": 380,     # Reduced by 150px to show "About this heatmap" section (was 300)
        "extra_padding": 0,
    },
}

# Debug mode - set to True to save original + cropped images for comparison
DEBUG_SCREENSHOTS = False
DEBUG_OUTPUT_DIR = "/tmp/ari_screenshot_debug"


def capture_streamlit_tabs(
    session_state: Dict[str, Any],
    app_url: str = "http://localhost:3006",
    tabs_to_capture: Optional[List[str]] = None,
    viewport_width: int = 1920,
    viewport_height: int = 1080
) -> Dict[str, bytes]:
    """
    Capture screenshots of Streamlit tabs using Playwright.

    Args:
        session_state: Streamlit session state to pass to the app
        app_url: URL where Streamlit app is running
        tabs_to_capture: List of tab names to capture (None = capture all)
        viewport_width: Browser viewport width
        viewport_height: Browser viewport height

    Returns:
        Dict mapping tab name to PNG image bytes
    """
    from playwright.sync_api import sync_playwright

    # Default tabs to capture (matches results.py tab structure)
    if tabs_to_capture is None:
        tabs_to_capture = [
            "Detailed Metrics",
            "Audience Insights",
            "Media Affinities",
            "Trend Analysis",
        ]

    # Save session state to temp file for the export mode
    export_id = f"export_{int(time.time())}"
    temp_dir = Path(tempfile.gettempdir()) / "ari_exports"
    temp_dir.mkdir(exist_ok=True)
    state_file = temp_dir / f"{export_id}.json"

    # Serialize session state (filter out non-serializable items)
    serializable_state = {}
    skipped_keys = []
    for key, value in session_state.items():
        try:
            json.dumps(value)  # Test if serializable
            serializable_state[key] = value
        except (TypeError, ValueError) as e:
            skipped_keys.append(key)
            logger.debug(f"Skipped non-serializable key: {key} ({type(value).__name__})")

    # CRITICAL: Ensure has_analyzed is True so results page is shown
    serializable_state['has_analyzed'] = True

    logger.info(f"Session state: {len(serializable_state)} keys saved, {len(skipped_keys)} skipped")
    logger.info(f"Saved keys: {list(serializable_state.keys())}")
    if skipped_keys:
        logger.warning(f"Skipped keys (non-serializable): {skipped_keys}")

    with open(state_file, 'w') as f:
        json.dump(serializable_state, f)
    logger.info(f"Saved session state to {state_file}")

    screenshots = {}

    try:
        with sync_playwright() as p:
            # Launch browser
            logger.info("Launching headless Chromium browser...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': viewport_width, 'height': viewport_height}
            )
            page = context.new_page()

            # Navigate to app with export mode
            export_url = f"{app_url}?export_mode=true&export_id={export_id}"
            logger.info(f"Navigating to {export_url}")
            page.goto(export_url, wait_until='networkidle', timeout=60000)

            # Wait for Streamlit to fully load
            logger.info("Waiting for Streamlit app to load...")
            page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=30000)
            time.sleep(3)  # Additional wait for full rendering

            # Find all tab buttons
            tab_buttons = page.query_selector_all('[data-baseweb="tab"]')
            logger.info(f"Found {len(tab_buttons)} tabs in the app")

            for i, tab_button in enumerate(tab_buttons):
                tab_text = tab_button.inner_text().strip()

                # Check if this tab should be captured
                if tabs_to_capture and tab_text not in tabs_to_capture:
                    logger.debug(f"Skipping tab: {tab_text}")
                    continue

                logger.info(f"Capturing tab {i+1}: {tab_text}")

                # Click the tab
                tab_button.click()
                time.sleep(2)  # Wait for tab content to fully render

                # Wait for any loading spinners to disappear
                try:
                    page.wait_for_selector('[data-testid="stSpinner"]', state='hidden', timeout=5000)
                except:
                    pass  # No spinner or already hidden

                # SPECIAL HANDLING: Force large viewport for Audience Insights EARLY
                if tab_text == "Audience Insights":
                    print("\n" + "="*60)
                    print(">>> AUDIENCE INSIGHTS: FORCING 3450px VIEWPORT <<<")
                    print("="*60 + "\n")
                    logger.info(f"  [AUDIENCE INSIGHTS] Forcing viewport to 3450px height")
                    page.set_viewport_size({'width': viewport_width, 'height': 3450})
                    time.sleep(1)
                    # Scroll to very bottom to trigger all lazy loading
                    page.evaluate('() => window.scrollTo(0, 99999)')
                    time.sleep(0.5)
                    page.evaluate('() => window.scrollTo(0, 0)')
                    time.sleep(0.5)

                # SPECIAL HANDLING: Expand "About this heatmap" expander for Trend Analysis
                if tab_text == "Trend Analysis":
                    logger.info(f"  [TREND ANALYSIS] Expanding 'About this heatmap' section")
                    try:
                        # Find and click the expander with "About this heatmap" text
                        expander_clicked = page.evaluate('''() => {
                            // Find all expander headers
                            const expanders = document.querySelectorAll('[data-testid="stExpander"]');
                            for (const expander of expanders) {
                                const header = expander.querySelector('summary, [data-testid="stExpanderHeader"]');
                                if (header && header.textContent.includes('About this heatmap')) {
                                    // Check if it's collapsed (aria-expanded="false" or similar)
                                    const details = expander.querySelector('details');
                                    if (details && !details.hasAttribute('open')) {
                                        header.click();
                                        return true;
                                    } else if (!details) {
                                        // Try clicking anyway
                                        header.click();
                                        return true;
                                    }
                                }
                            }
                            // Alternative: try finding by text content
                            const allSummaries = document.querySelectorAll('summary');
                            for (const summary of allSummaries) {
                                if (summary.textContent.includes('About this heatmap')) {
                                    summary.click();
                                    return true;
                                }
                            }
                            return false;
                        }''')
                        if expander_clicked:
                            logger.info(f"  [TREND ANALYSIS] Expander clicked, waiting for content to render")
                            time.sleep(1)  # Wait for expander content to render
                        else:
                            logger.warning(f"  [TREND ANALYSIS] Could not find 'About this heatmap' expander")
                    except Exception as e:
                        logger.warning(f"  [TREND ANALYSIS] Error expanding section: {e}")

                # HIDE the tab bar and other UI elements for clean screenshot
                hidden_count = page.evaluate('''() => {
                    // Hide tab bar
                    const tabList = document.querySelector('[data-baseweb="tab-list"]');
                    if (tabList) tabList.style.display = 'none';

                    // Hide Streamlit header/toolbar
                    const header = document.querySelector('[data-testid="stHeader"]');
                    if (header) header.style.display = 'none';

                    // Hide deploy button
                    const deployBtn = document.querySelector('[data-testid="stDeployButton"]');
                    if (deployBtn) deployBtn.style.display = 'none';

                    // Hide toolbar
                    const toolbar = document.querySelector('[data-testid="stToolbar"]');
                    if (toolbar) toolbar.style.display = 'none';

                    // Remove top padding from main container
                    const mainBlock = document.querySelector('[data-testid="stMainBlockContainer"]');
                    if (mainBlock) mainBlock.style.paddingTop = '0';

                    // ============================================================
                    // COMPREHENSIVE TOOLTIP HIDING - Multiple approaches
                    // ============================================================

                    // 1. Hide all Streamlit tooltip icons (the small info "i" icons)
                    document.querySelectorAll('[data-testid="stTooltipIcon"]').forEach(el => {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                    });

                    // 2. Hide tooltip hover targets (containers that show tooltips on hover)
                    document.querySelectorAll('[data-testid="stTooltipHoverTarget"]').forEach(el => {
                        el.style.display = 'none';
                    });
                    document.querySelectorAll('[data-testid="tooltipHoverTarget"]').forEach(el => {
                        el.style.display = 'none';
                    });

                    // 3. Hide any elements with class containing "tooltip"
                    document.querySelectorAll('[class*="tooltip"], [class*="Tooltip"]').forEach(el => {
                        el.style.display = 'none';
                    });

                    // 4. Hide BaseWeb tooltips
                    document.querySelectorAll('[data-baseweb="tooltip"]').forEach(el => {
                        el.style.display = 'none';
                    });
                    document.querySelectorAll('[role="tooltip"]').forEach(el => {
                        el.style.display = 'none';
                    });

                    // 5. Hide Streamlit's caption elements that might contain help text
                    document.querySelectorAll('[data-testid="stCaptionContainer"]').forEach(el => {
                        // Check if this is a help tooltip caption (usually smaller font)
                        if (el.textContent && el.textContent.length > 200) {
                            // This might be tooltip help text that expanded
                            el.style.display = 'none';
                        }
                    });

                    // 6. Hide small SVG icons that are typically info/help icons
                    document.querySelectorAll('svg').forEach(svg => {
                        const parent = svg.closest('button, [data-testid="stTooltipIcon"], .stTooltipIcon');
                        // Check if it's an info icon (usually small, with specific paths)
                        if (parent && (parent.getAttribute('data-testid') === 'stTooltipIcon' ||
                            parent.classList.contains('stTooltipIcon'))) {
                            parent.style.display = 'none';
                        }
                        // Also check for standalone info SVGs
                        const box = svg.getBoundingClientRect();
                        if (box.width <= 20 && box.height <= 20) {
                            // Small SVG that could be a help icon
                            const nearbyText = svg.parentElement?.textContent || '';
                            if (nearbyText.includes('ⓘ') || svg.innerHTML.includes('circle')) {
                                svg.style.display = 'none';
                            }
                        }
                    });

                    // 7. Hide elements with specific Streamlit help classes
                    document.querySelectorAll('.stTooltipIcon, .stHelp').forEach(el => {
                        el.style.display = 'none';
                    });

                    // 8. Hide any button that looks like an info button (typically 16-24px square with SVG)
                    document.querySelectorAll('button').forEach(btn => {
                        const rect = btn.getBoundingClientRect();
                        if (rect.width <= 30 && rect.height <= 30 && btn.querySelector('svg')) {
                            // Small button with SVG - likely info/help button
                            const svg = btn.querySelector('svg');
                            if (svg && svg.innerHTML.includes('path')) {
                                btn.style.visibility = 'hidden';
                            }
                        }
                    });

                    // 9. SPECIFICALLY hide custom tooltip elements from results.py and learning_tips.py
                    // These are the main culprits showing as "large text blocks"

                    // Count elements for debugging
                    let hiddenCount = 0;

                    // Hide .tooltip containers and their .tooltiptext content (from detailed_metrics.py)
                    document.querySelectorAll('.tooltip').forEach(el => {
                        el.style.display = 'none';
                        hiddenCount++;
                    });
                    document.querySelectorAll('.tooltiptext').forEach(el => {
                        el.style.display = 'none';
                        hiddenCount++;
                    });
                    document.querySelectorAll('.info-icon').forEach(el => {
                        el.style.display = 'none';
                        hiddenCount++;
                    });

                    // Hide .tip-bubble containers and their content (from learning_tips.py)
                    document.querySelectorAll('.tip-bubble').forEach(el => {
                        el.style.display = 'none';
                        hiddenCount++;
                    });
                    document.querySelectorAll('.tip-content').forEach(el => {
                        el.style.display = 'none';
                        hiddenCount++;
                    });
                    document.querySelectorAll('.tip-icon').forEach(el => {
                        el.style.display = 'none';
                        hiddenCount++;
                    });
                    document.querySelectorAll('.tip-title').forEach(el => {
                        el.style.display = 'none';
                        hiddenCount++;
                    });
                    document.querySelectorAll('.tip-learn-more').forEach(el => {
                        el.style.display = 'none';
                        hiddenCount++;
                    });

                    console.log('[SCREENSHOT] Hidden ' + hiddenCount + ' tooltip elements');

                    // 10. Add CSS to force hide ALL tooltip-related elements with !important
                    const style = document.createElement('style');
                    style.textContent = `
                        /* Streamlit built-in tooltips */
                        [data-testid="stTooltipIcon"],
                        [data-testid="stTooltipHoverTarget"],
                        [data-baseweb="tooltip"],
                        [role="tooltip"],
                        .stTooltipIcon,

                        /* Custom tooltips from detailed_metrics.py */
                        .tooltip,
                        .tooltiptext,
                        .info-icon,

                        /* Custom tip bubbles from learning_tips.py */
                        .tip-bubble,
                        .tip-content,
                        .tip-icon,
                        .tip-title,
                        .tip-learn-more,

                        /* Generic tooltip class patterns */
                        [class*="tooltip"],
                        [class*="Tooltip"] {
                            display: none !important;
                            visibility: hidden !important;
                            opacity: 0 !important;
                            height: 0 !important;
                            width: 0 !important;
                            overflow: hidden !important;
                        }
                    `;
                    document.head.appendChild(style);

                    return hiddenCount;
                }''')
                logger.info(f"  Hidden {hidden_count} tooltip elements")
                time.sleep(0.5)

                # Find the active tab panel (the one that's currently visible)
                # Streamlit shows only the active panel
                active_panel = page.query_selector('[data-baseweb="tab-panel"]')

                if active_panel:
                    # Get full scrollable height of the panel content
                    # For some tabs, we need to get the full document height, not just panel
                    scroll_height = active_panel.evaluate('el => el.scrollHeight')
                    client_height = active_panel.evaluate('el => el.clientHeight')

                    # Check if this tab needs full page capture (configured in TAB_SCREENSHOT_CONFIG)
                    tab_config_temp = TAB_SCREENSHOT_CONFIG.get(tab_text, {})
                    if tab_config_temp.get("force_full_page", False):
                        # Scroll to bottom first to ensure all content is loaded (triggers lazy loading)
                        page.evaluate('() => window.scrollTo(0, document.documentElement.scrollHeight)')
                        time.sleep(0.5)
                        # Scroll back to top
                        page.evaluate('() => window.scrollTo(0, 0)')
                        time.sleep(0.3)

                        # Get the full page scroll height - don't subtract anything
                        page_scroll_height = page.evaluate('() => document.documentElement.scrollHeight')
                        # Use the maximum of panel and page scroll height
                        scroll_height = max(scroll_height, page_scroll_height)
                        logger.info(f"  {tab_text}: force_full_page=True, page_scroll_height={page_scroll_height}, using {scroll_height}")

                    logger.info(f"  Panel dimensions: scrollHeight={scroll_height}, clientHeight={client_height}")

                    # Scroll to top of panel
                    active_panel.evaluate('element => element.scrollTop = 0')
                    page.evaluate('() => window.scrollTo(0, 0)')
                    time.sleep(0.3)

                    # Get tab-specific config for viewport sizing
                    tab_config = TAB_SCREENSHOT_CONFIG.get(tab_text, {})
                    extra_padding = tab_config.get("extra_padding", 200)

                    # Get the current bounding box
                    bbox = active_panel.bounding_box()
                    if bbox:
                        # If content is taller than viewport, resize viewport to fit full content
                        if scroll_height > client_height:
                            # Set viewport height to accommodate full content
                            new_height = int(bbox['y']) + scroll_height + extra_padding
                            logger.info(f"  Resizing viewport: bbox_y={int(bbox['y'])}, scroll_height={scroll_height}, padding={extra_padding}, new_height={new_height}")
                            page.set_viewport_size({'width': viewport_width, 'height': new_height})
                            time.sleep(0.5)  # Wait for re-render

                            # Re-get the panel after viewport resize
                            active_panel = page.query_selector('[data-baseweb="tab-panel"]')
                            if active_panel:
                                active_panel.evaluate('element => element.scrollTop = 0')
                                page.evaluate('() => window.scrollTo(0, 0)')

                        # Check capture mode from config
                        capture_mode = tab_config.get("capture_mode", "panel")
                        min_height = tab_config.get("min_height", 0)

                        # If min_height is specified, ensure viewport is at least that tall
                        if min_height > 0:
                            current_viewport = page.viewport_size
                            if current_viewport and current_viewport['height'] < min_height:
                                logger.info(f"  Expanding viewport to min_height={min_height}px")
                                page.set_viewport_size({'width': viewport_width, 'height': min_height})
                                time.sleep(0.5)
                                # Scroll to bottom and back to trigger rendering
                                page.evaluate('() => window.scrollTo(0, document.documentElement.scrollHeight)')
                                time.sleep(0.3)
                                page.evaluate('() => window.scrollTo(0, 0)')
                                time.sleep(0.3)

                        if capture_mode == "full_page":
                            # Capture FULL PAGE screenshot (captures everything visible)
                            logger.info(f"  Using full_page capture mode")
                            screenshot_bytes = page.screenshot(type='png', full_page=True)
                        else:
                            # Capture the panel element directly (default)
                            screenshot_bytes = active_panel.screenshot(type='png')

                        # Screenshot captured successfully
                        pass
                    else:
                        # Fallback: capture full page
                        screenshot_bytes = page.screenshot(type='png', full_page=True)
                        logger.info(f"  Fallback: captured full page")
                else:
                    # Fallback: capture main content area
                    main_content = page.query_selector('[data-testid="stAppViewContainer"]')
                    if main_content:
                        screenshot_bytes = main_content.screenshot(type='png')
                        logger.info(f"  Fallback: captured from main container")
                    else:
                        screenshot_bytes = page.screenshot(type='png', full_page=True)
                        logger.info(f"  Fallback: captured full page")

                # =================================================================
                # POST-PROCESS: Apply cropping to ALL screenshots (moved outside conditionals)
                # =================================================================
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(screenshot_bytes))
                original_height = img.height
                original_width = img.width

                # Get tab-specific cropping from configuration
                tab_crop_config = TAB_SCREENSHOT_CONFIG.get(tab_text, {})
                crop_top = tab_crop_config.get("crop_top", 0)
                crop_bottom = tab_crop_config.get("crop_bottom", 0)

                logger.info(f"  Config for '{tab_text}': crop_top={crop_top}px, crop_bottom={crop_bottom}px, original_height={original_height}px")

                # Debug mode: save original screenshot before cropping
                if DEBUG_SCREENSHOTS:
                    import os
                    os.makedirs(DEBUG_OUTPUT_DIR, exist_ok=True)
                    debug_filename = f"{DEBUG_OUTPUT_DIR}/{tab_text.replace(' ', '_')}_ORIGINAL.png"
                    with open(debug_filename, 'wb') as f:
                        f.write(screenshot_bytes)
                    logger.info(f"  DEBUG: Saved original to {debug_filename}")

                # Apply cropping if needed
                if crop_top > 0 or crop_bottom > 0:
                    new_top = crop_top
                    new_bottom = original_height - crop_bottom
                    if new_bottom > new_top:
                        logger.info(f"  Cropping: original={original_height}px, new_top={new_top}px, new_bottom={new_bottom}px, final_height={new_bottom - new_top}px")
                        img = img.crop((0, new_top, original_width, new_bottom))
                        # Save cropped image back to bytes
                        output = io.BytesIO()
                        img.save(output, format='PNG')
                        screenshot_bytes = output.getvalue()

                        # Debug mode: save cropped screenshot
                        if DEBUG_SCREENSHOTS:
                            debug_filename = f"{DEBUG_OUTPUT_DIR}/{tab_text.replace(' ', '_')}_CROPPED.png"
                            with open(debug_filename, 'wb') as f:
                                f.write(screenshot_bytes)
                            logger.info(f"  DEBUG: Saved cropped to {debug_filename}")
                    else:
                        logger.warning(f"  Skipping crop: new_bottom ({new_bottom}) <= new_top ({new_top})")

                screenshots[tab_text] = screenshot_bytes
                logger.info(f"  ✓ Captured {tab_text} ({len(screenshot_bytes):,} bytes, {img.width}x{img.height}px)")

                # Reset viewport for next tab
                page.set_viewport_size({'width': viewport_width, 'height': viewport_height})

                # RESTORE the tab bar for next iteration (in case we need to click other tabs)
                page.evaluate('''() => {
                    const tabList = document.querySelector('[data-baseweb="tab-list"]');
                    if (tabList) tabList.style.display = '';
                }''')
                time.sleep(0.2)

                # ALWAYS reset viewport to default before next tab
                page.set_viewport_size({'width': viewport_width, 'height': viewport_height})
                logger.info(f"  Reset viewport to {viewport_width}x{viewport_height} for next tab")

            browser.close()
            logger.info(f"Browser closed. Total screenshots captured: {len(screenshots)}")

    except Exception as e:
        logger.error(f"Error capturing tabs: {e}")
        raise

    finally:
        # Cleanup temp file
        if state_file.exists():
            state_file.unlink()

    return screenshots


def capture_tab_content_as_html(
    session_state: Dict[str, Any],
    tab_name: str
) -> Optional[bytes]:
    """
    Generate HTML for a specific tab and render to image using Playwright.
    This is a fallback method that doesn't require the Streamlit app to be running.

    Args:
        session_state: Streamlit session state
        tab_name: Name of the tab to render

    Returns:
        PNG image bytes or None if rendering fails
    """
    from playwright.sync_api import sync_playwright

    logger.info(f"Generating HTML for tab: {tab_name}")

    # Generate HTML based on tab name
    html_content = _generate_tab_html(session_state, tab_name)
    if not html_content:
        logger.warning(f"No HTML template available for tab: {tab_name}")
        return None

    logger.debug(f"Generated HTML content ({len(html_content):,} chars)")

    try:
        with sync_playwright() as p:
            logger.info(f"Launching browser to render {tab_name}...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})

            # Load HTML content
            page.set_content(html_content)
            time.sleep(1)  # Wait for rendering

            # Capture screenshot
            screenshot_bytes = page.screenshot(type='png', full_page=True)
            logger.info(f"  ✓ Rendered {tab_name} ({len(screenshot_bytes):,} bytes)")

            browser.close()
            return screenshot_bytes

    except Exception as e:
        logger.error(f"Error rendering HTML for {tab_name}: {e}")
        return None


def _generate_tab_html(session_state: Dict[str, Any], tab_name: str) -> Optional[str]:
    """
    Generate static HTML for a tab based on session state.

    This creates a simplified HTML representation of the tab content
    that can be rendered to an image.
    """
    # Safely get values with type checking
    scores = session_state.get('scores', {})
    if not isinstance(scores, dict):
        scores = {}

    brand_name = session_state.get('brand_name', 'Brand')
    if not isinstance(brand_name, str):
        brand_name = str(brand_name) if brand_name else 'Brand'

    logger.debug(f"Generating HTML for {tab_name} with {len(scores)} metrics")

    # Common styles
    styles = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            padding: 40px;
            margin: 0;
            color: #1e293b;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .title {
            font-size: 32px;
            font-weight: 700;
            color: #6171EA;
            margin-bottom: 30px;
            border-bottom: 3px solid #6171EA;
            padding-bottom: 15px;
        }
        .metric-card {
            background: #f8fafc;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .metric-name {
            font-size: 16px;
            font-weight: 600;
            color: #334155;
            margin-bottom: 10px;
        }
        .metric-bar {
            height: 24px;
            background: #e2e8f0;
            border-radius: 12px;
            overflow: hidden;
        }
        .metric-fill {
            height: 100%;
            background: linear-gradient(90deg, #6171EA, #10b981);
            border-radius: 12px;
            transition: width 0.3s ease;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #6171EA;
            margin-top: 8px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
    </style>
    """

    if tab_name == "Detailed Metrics":
        metrics_html = ""
        for metric_name, value in scores.items():
            try:
                if isinstance(value, (int, float)):
                    # Ensure metric_name is a string
                    name_str = str(metric_name) if not isinstance(metric_name, str) else metric_name
                    display_name = name_str.replace('_', ' ').title()
                    percentage = min(100, max(0, value))
                    metrics_html += f"""
                    <div class="metric-card">
                        <div class="metric-name">{display_name}</div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: {percentage}%"></div>
                        </div>
                        <div class="metric-value">{value:.1f}</div>
                    </div>
                    """
            except Exception as e:
                logger.warning(f"Skipping metric {metric_name}: {e}")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{styles}</head>
        <body>
            <div class="container">
                <div class="title">Detailed Metrics - {brand_name}</div>
                <div class="grid">
                    {metrics_html}
                </div>
            </div>
        </body>
        </html>
        """

    elif tab_name == "Audience Insights":
        audiences = session_state.get('audiences', {})
        core = audiences.get('core', 'Core audience description not available')
        primary = audiences.get('primary', 'Primary audience description not available')
        secondary = audiences.get('secondary', 'Secondary audience description not available')

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{styles}
        <style>
            .audience-section {{
                margin-bottom: 30px;
                padding: 25px;
                background: #f8fafc;
                border-radius: 12px;
                border-left: 4px solid #6171EA;
            }}
            .audience-title {{
                font-size: 20px;
                font-weight: 600;
                color: #6171EA;
                margin-bottom: 15px;
            }}
            .audience-desc {{
                font-size: 16px;
                line-height: 1.6;
                color: #475569;
            }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="title">Audience Insights - {brand_name}</div>
                <div class="audience-section">
                    <div class="audience-title">🎯 Core Audience</div>
                    <div class="audience-desc">{core}</div>
                </div>
                <div class="audience-section">
                    <div class="audience-title">👥 Primary Audience</div>
                    <div class="audience-desc">{primary}</div>
                </div>
                <div class="audience-section">
                    <div class="audience-title">🌐 Secondary Audience</div>
                    <div class="audience-desc">{secondary}</div>
                </div>
            </div>
        </body>
        </html>
        """

    elif tab_name == "Media Affinities":
        media_affinities = session_state.get('media_affinities', [])

        media_html = ""
        for i, item in enumerate(media_affinities[:10]):
            if isinstance(item, dict):
                site = item.get('site', f'Site {i+1}')
                qvi = item.get('qvi', 0)
                media_html += f"""
                <div class="metric-card">
                    <div class="metric-name">{site}</div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="width: {min(100, qvi)}%"></div>
                    </div>
                    <div class="metric-value">QVI: {qvi:.1f}</div>
                </div>
                """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{styles}</head>
        <body>
            <div class="container">
                <div class="title">Media Affinities - {brand_name}</div>
                {media_html if media_html else '<p>No media affinity data available</p>'}
            </div>
        </body>
        </html>
        """

    elif tab_name == "Trend Analysis":
        # Get trend data from session state
        ai_insights = session_state.get('ai_insights', {})
        improvements = ai_insights.get('improvements', []) if isinstance(ai_insights, dict) else []
        percentile = session_state.get('percentile', 50)

        trends_html = ""
        if improvements:
            for imp in improvements[:5]:
                if isinstance(imp, dict):
                    area = imp.get('area', '')
                    rec = imp.get('recommendation', '')
                    trends_html += f"""
                    <div class="metric-card">
                        <div class="metric-name">{area}</div>
                        <div class="audience-desc">{rec}</div>
                    </div>
                    """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{styles}
        <style>
            .audience-desc {{
                font-size: 16px;
                line-height: 1.6;
                color: #475569;
            }}
            .benchmark {{
                background: linear-gradient(90deg, #6171EA, #10b981);
                color: white;
                padding: 20px;
                border-radius: 12px;
                margin-top: 30px;
                text-align: center;
            }}
            .benchmark-value {{
                font-size: 48px;
                font-weight: 700;
            }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="title">Marketing Trend Analysis - {brand_name}</div>
                <h3 style="color: #334155; margin-bottom: 20px;">Strategic Recommendations</h3>
                {trends_html if trends_html else '<p>No trend data available</p>'}
                <div class="benchmark">
                    <div>Benchmark Ranking</div>
                    <div class="benchmark-value">Top {percentile}%</div>
                    <div>of all campaigns analyzed</div>
                </div>
            </div>
        </body>
        </html>
        """

    elif tab_name == "Next Steps":
        next_steps = session_state.get('next_steps', session_state.get('recommendations', []))

        steps_html = ""
        if isinstance(next_steps, list):
            for i, step in enumerate(next_steps[:5], 1):
                steps_html += f"""
                <div class="metric-card">
                    <div class="metric-name">Step {i}</div>
                    <div class="audience-desc">{step}</div>
                </div>
                """
        elif isinstance(next_steps, str):
            steps_html = f'<div class="metric-card"><div class="audience-desc">{next_steps}</div></div>'

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{styles}
        <style>
            .audience-desc {{
                font-size: 16px;
                line-height: 1.6;
                color: #475569;
            }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="title">Recommended Next Steps - {brand_name}</div>
                {steps_html if steps_html else '<p>No recommendations available</p>'}
            </div>
        </body>
        </html>
        """

    return None


# Convenience function for direct use
def capture_streamlit_screenshots(
    session_state: Dict[str, Any],
    use_live_capture: bool = False,
    app_url: str = "http://localhost:3006"
) -> Dict[str, bytes]:
    """
    Capture screenshots of Streamlit content.

    Args:
        session_state: Streamlit session state
        use_live_capture: If True, capture from running app; if False, render HTML
        app_url: URL of the running Streamlit app (only used if use_live_capture=True)

    Returns:
        Dict mapping tab name to PNG bytes
    """
    # Tabs that can be rendered as HTML (have templates)
    tabs = ["Detailed Metrics", "Audience Insights", "Media Affinities", "Trend Analysis"]

    logger.info("=" * 60)
    logger.info("STREAMLIT SCREENSHOT CAPTURE STARTED")
    logger.info(f"Mode: {'Live capture' if use_live_capture else 'HTML rendering'}")
    logger.info(f"Tabs to capture: {tabs}")
    logger.info("=" * 60)

    if use_live_capture:
        logger.info(f"Using live capture from: {app_url}")
        return capture_streamlit_tabs(session_state, app_url, tabs)
    else:
        # Use HTML rendering (doesn't require app to be running)
        logger.info("Using HTML rendering mode (no live app required)")
        screenshots = {}
        for tab_name in tabs:
            logger.info(f"Processing tab: {tab_name}")
            png_bytes = capture_tab_content_as_html(session_state, tab_name)
            if png_bytes:
                screenshots[tab_name] = png_bytes
                logger.info(f"  ✓ Successfully captured {tab_name}")
            else:
                logger.warning(f"  ✗ Failed to capture {tab_name}")

        logger.info("=" * 60)
        logger.info(f"CAPTURE COMPLETE: {len(screenshots)}/{len(tabs)} tabs captured")
        logger.info("=" * 60)
        return screenshots
