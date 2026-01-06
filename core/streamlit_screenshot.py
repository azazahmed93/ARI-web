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

# =============================================================================
# SECTION-BASED SCREENSHOT CONFIG - For splitting tabs into multiple slides
# =============================================================================
#
# Each section defines:
#   - source_tab: Which Streamlit tab to navigate to
#   - js_setup: JavaScript function name to call for showing/hiding elements
#   - crop_top/crop_bottom: Pixels to crop after capture
#   - extra_padding: Extra viewport padding
#   - min_height: Minimum viewport height (optional)
#   - capture_mode: "panel" (default) or "full_page"
#
# =============================================================================

SECTION_SCREENSHOT_CONFIG = {
    # -------------------------------------------------------------------------
    # TAB 1: Detailed Metrics - Split into 3 sections
    # -------------------------------------------------------------------------
    "Score Card": {
        "source_tab": "Detailed Metrics",
        "js_setup": "showScoreCard",
        "crop_top": 25,
        "crop_bottom": 0,
        "extra_padding": 200,
    },
    "Executive Summary & Detailed Metrics": {
        "source_tab": "Detailed Metrics",
        "js_setup": "showExecutiveSummaryAndMetrics",
        "crop_top": 0,
        "crop_bottom": 0,
        "extra_padding": 200,
    },
    "Advanced Metric Analysis": {
        "source_tab": "Detailed Metrics",
        "js_setup": "showAdvancedAnalysis",
        "crop_top": 0,
        "crop_bottom": 0,
        "extra_padding": 200,
    },
    # -------------------------------------------------------------------------
    # TAB 2: Audience Insights - Split into 3 sections
    # -------------------------------------------------------------------------
    "Psychographic Highlights & Audience Summary": {
        "source_tab": "Audience Insights",
        "js_setup": "showPsychographicAndSummary",
        "crop_top": 0,  # Reduced from 60 to preserve H3 title
        "crop_bottom": 0,
        "extra_padding": 500,
    },
    "Growth Audience Insights": {
        "source_tab": "Audience Insights",
        "js_setup": "showGrowthInsights",
        "crop_top": 0,
        "crop_bottom": 0,
        "extra_padding": 500,
    },
    "Emerging Audience Opportunity": {
        "source_tab": "Audience Insights",
        "js_setup": "showEmergingOpportunity",
        "crop_top": 0,
        "crop_bottom": 0,
        "extra_padding": 500,
        # Removed force_full_page to avoid capturing Enterprise Analytics below
    },
    # -------------------------------------------------------------------------
    # TAB 3 & 4: Unchanged - Full tab capture
    # -------------------------------------------------------------------------
    "Media Affinities": {
        "source_tab": "Media Affinities",
        "js_setup": None,  # No section hiding needed
        "crop_top": 0,  # Reduced from 80 - was clipping top
        "crop_bottom": 0,  # Reduced from 150 - was clipping bottom
        "extra_padding": 200,
    },
    "Trend Analysis": {
        "source_tab": "Trend Analysis",
        "js_setup": None,  # No section hiding needed
        "crop_top": 0,  # Reduced from 130
        "crop_bottom": 0,  # Reduced from 380 - was clipping bottom
        "extra_padding": 200,  # Increased from 0
    },
}

# Legacy config for backward compatibility (maps tab names to first section)
TAB_SCREENSHOT_CONFIG = {
    "Detailed Metrics": SECTION_SCREENSHOT_CONFIG["Score Card"],
    "Audience Insights": SECTION_SCREENSHOT_CONFIG["Psychographic Highlights & Audience Summary"],
    "Media Affinities": SECTION_SCREENSHOT_CONFIG["Media Affinities"],
    "Trend Analysis": SECTION_SCREENSHOT_CONFIG["Trend Analysis"],
}

# Debug mode - set to True to save original + cropped images for comparison
DEBUG_SCREENSHOTS = False
DEBUG_OUTPUT_DIR = "/tmp/ari_screenshot_debug"

# =============================================================================
# JAVASCRIPT FUNCTIONS FOR SECTION HIDING/SHOWING
# =============================================================================
# These functions are injected into the page to control which sections are visible
# for each screenshot. Each function targets specific DOM elements.
# =============================================================================

SECTION_JS_FUNCTIONS = '''
// =============================================================================
// SECTION VISIBILITY FUNCTIONS - Based on Actual DOM Structure
// =============================================================================
//
// The page has multiple stTabs elements:
//   - allTabs[0]: Upload/Paste Text tabs
//   - allTabs[1]: Results tabs (Detailed Metrics, Audience Insights, etc.)
//   - allTabs[2]: Nested Priority Improvement tabs
//
// We target allTabs[1] and work with stVerticalBlock children by index.
//
// Tab1 (Detailed Metrics) stVerticalBlock has 9 children:
//   [0] H2 "Audience Resonance Index Scorecard" + radar chart
//   [1] Spacing/hr
//   [2] stHorizontalBlock (KPI boxes area)
//   [3] H3 "Executive Summary" + H3 "Detailed Metrics" with progress bars
//   [4] H3 "Advanced Metric Analysis"
//   [5-8] Advanced analysis content + nested Priority Improvement tabs
//
// Tab2 (Audience Insights) stVerticalBlock has 10 children:
//   [0] H3 "Psychographic Highlights"
//   [1-2] Content including H3 "Audience Summary"
//   [3-5] Summary content
//   [6] H3 "Growth Audience Insights"
//   [7] stHorizontalBlock with Growth cards + iframes
//   [8] H4 "Emerging Audience Opportunity"
//   [9] Emerging iframe content
//
// =============================================================================

function getResultsPanel() {
    // Get the active panel from the results tabs
    // In export mode, allTabs[0] is results; in normal mode, allTabs[1] is results
    // We identify results tabs by looking for "Detailed Metrics" tab button
    const allTabs = document.querySelectorAll('[data-testid="stTabs"]');
    if (allTabs.length === 0) {
        console.log('[SECTION] getResultsPanel: No stTabs found');
        return null;
    }

    // Find which stTabs contains the "Detailed Metrics" tab
    let resultsTabs = null;
    for (const tabsContainer of allTabs) {
        const tabButtons = tabsContainer.querySelectorAll('[data-baseweb="tab"]');
        for (const btn of tabButtons) {
            if (btn.innerText.includes('Detailed Metrics')) {
                resultsTabs = tabsContainer;
                console.log('[SECTION] getResultsPanel: Found results tabs with Detailed Metrics');
                break;
            }
        }
        if (resultsTabs) break;
    }

    if (!resultsTabs) {
        console.log('[SECTION] getResultsPanel: Could not find results tabs by content');
        // Fallback to first stTabs
        resultsTabs = allTabs[0];
    }

    const panels = resultsTabs.querySelectorAll(':scope > div > [role="tabpanel"]');
    for (const panel of panels) {
        if (!panel.hasAttribute('hidden')) {
            return panel;
        }
    }
    console.log('[SECTION] getResultsPanel: No active panel found');
    return null;
}

function getVerticalBlockChildren(panel) {
    // Get direct children of stVerticalBlock inside panel
    const vBlock = panel.querySelector('[data-testid="stVerticalBlock"]');
    if (!vBlock) {
        console.log('[SECTION] getVerticalBlockChildren: stVerticalBlock not found');
        return [];
    }
    return Array.from(vBlock.children);
}

function hideChildrenByIndices(children, indicesToHide) {
    // Hide children at specific indices
    indicesToHide.forEach(i => {
        if (children[i]) {
            children[i].style.display = 'none';
        }
    });
}

function showChildrenByIndices(children, indicesToShow) {
    // Hide ALL children except those at specific indices
    children.forEach((child, i) => {
        if (!indicesToShow.includes(i)) {
            child.style.display = 'none';
        }
    });
}

// =============================================================================
// DETAILED METRICS TAB - Section Visibility Functions
// =============================================================================

function showScoreCard() {
    // Show: [0] title+radar, [1] hr, [2] KPI boxes
    // Hide: [3-8] Executive Summary, Detailed Metrics, Advanced Analysis, etc.

    const panel = getResultsPanel();
    if (!panel) return false;

    console.log('[SECTION] showScoreCard: Starting...');

    const children = getVerticalBlockChildren(panel);
    if (children.length < 4) {
        console.log('[SECTION] showScoreCard: Not enough children, showing full tab');
        return true;
    }

    // Show indices 0, 1, 2 - hide 3 and onwards
    showChildrenByIndices(children, [0, 1, 2]);

    console.log('[SECTION] showScoreCard: Done - showing indices 0-2');
    return true;
}

function showExecutiveSummaryAndMetrics() {
    // Show: [3] Executive Summary + Detailed Metrics
    // Hide: [0-2] title/radar/KPIs, [4-8] Advanced Analysis

    const panel = getResultsPanel();
    if (!panel) return false;

    console.log('[SECTION] showExecutiveSummaryAndMetrics: Starting...');

    const children = getVerticalBlockChildren(panel);
    if (children.length < 4) {
        console.log('[SECTION] showExecutiveSummaryAndMetrics: Not enough children');
        return false;
    }

    // Show only index 3
    showChildrenByIndices(children, [3]);

    console.log('[SECTION] showExecutiveSummaryAndMetrics: Done - showing index 3 only');
    return true;
}

function showAdvancedAnalysis() {
    // Show: [4-8] Advanced Metric Analysis + Priority Improvement Areas
    // Hide: [0-3] Score Card, Executive Summary, Detailed Metrics

    const panel = getResultsPanel();
    if (!panel) return false;

    console.log('[SECTION] showAdvancedAnalysis: Starting...');

    const children = getVerticalBlockChildren(panel);
    if (children.length < 5) {
        console.log('[SECTION] showAdvancedAnalysis: Not enough children');
        return false;
    }

    // Show indices 4 onwards, hide 0-3
    const indicesToShow = [];
    for (let i = 4; i < children.length; i++) {
        indicesToShow.push(i);
    }
    showChildrenByIndices(children, indicesToShow);

    console.log('[SECTION] showAdvancedAnalysis: Done - showing indices 4+');
    return true;
}

// =============================================================================
// AUDIENCE INSIGHTS TAB - Section Visibility Functions
// =============================================================================

function showPsychographicAndSummary() {
    // Show: [0-5] Psychographic Highlights + Audience Summary
    // Hide: [6-9] Growth Insights, Emerging Opportunity

    const panel = getResultsPanel();
    if (!panel) return false;

    console.log('[SECTION] showPsychographicAndSummary: Starting...');

    const children = getVerticalBlockChildren(panel);
    if (children.length < 7) {
        console.log('[SECTION] showPsychographicAndSummary: Not enough children, showing full tab');
        return true;
    }

    // Show indices 0-5, hide 6 onwards
    showChildrenByIndices(children, [0, 1, 2, 3, 4, 5]);

    console.log('[SECTION] showPsychographicAndSummary: Done - showing indices 0-5');
    return true;
}

function showGrowthInsights() {
    // Show: [6-7] Growth Audience Insights
    // Hide: [0-5] Psychographic/Summary, [8-9] Emerging Opportunity

    const panel = getResultsPanel();
    if (!panel) return false;

    console.log('[SECTION] showGrowthInsights: Starting...');

    const children = getVerticalBlockChildren(panel);
    if (children.length < 8) {
        console.log('[SECTION] showGrowthInsights: Not enough children');
        return false;
    }

    // Show indices 6 and 7 only
    showChildrenByIndices(children, [6, 7]);

    console.log('[SECTION] showGrowthInsights: Done - showing indices 6-7');
    return true;
}

function showEmergingOpportunity() {
    // Show: [8-9] Emerging Audience Opportunity ONLY
    // Hide: [0-7] Everything before, [10+] Everything after (Enterprise Analytics)

    const panel = getResultsPanel();
    if (!panel) return false;

    console.log('[SECTION] showEmergingOpportunity: Starting...');

    const children = getVerticalBlockChildren(panel);
    if (children.length < 9) {
        console.log('[SECTION] showEmergingOpportunity: Not enough children');
        return false;
    }

    // Show ONLY indices 8 and 9 (Emerging title + content)
    // Hide everything else including Enterprise Analytics at 10+
    showChildrenByIndices(children, [8, 9]);

    console.log('[SECTION] showEmergingOpportunity: Done - showing indices 8-9 only');
    return true;
}

// Utility function to restore all hidden elements
function restoreAllSections() {
    const panel = getResultsPanel();
    if (!panel) return;

    // Remove all inline display styles to restore visibility
    panel.querySelectorAll('*').forEach(el => {
        if (el.style.display === 'none' || el.style.display === '') {
            el.style.removeProperty('display');
        }
        if (el.style.visibility === 'hidden') {
            el.style.removeProperty('visibility');
        }
    });

    // Also restore direct children of stVerticalBlock
    const children = getVerticalBlockChildren(panel);
    children.forEach(child => {
        child.style.removeProperty('display');
    });

    // Also remove any injected style tags
    document.querySelectorAll('style[id^="section-visibility"]').forEach(s => s.remove());
    document.getElementById('hide-tooltips')?.remove();

    console.log('[SECTION] restoreAllSections: Restored all elements');
}
'''


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

    # Note: Competitor Tactics is handled as a programmatic slide, not a screenshot

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

            # Find all tab buttons and get their text labels
            tab_buttons = page.query_selector_all('[data-baseweb="tab"]')
            tab_names_in_page = [btn.inner_text().strip() for btn in tab_buttons]
            logger.info(f"Found {len(tab_buttons)} tabs in the app: {tab_names_in_page}")

            for i, tab_text in enumerate(tab_names_in_page):
                # Check if this tab should be captured
                if tabs_to_capture and tab_text not in tabs_to_capture:
                    logger.debug(f"Skipping tab: {tab_text}")
                    continue

                logger.info(f"Capturing tab {i+1}: {tab_text}")

                # Re-query and click the tab button by finding it fresh each time
                # This avoids stale element references after DOM changes
                clicked = page.evaluate(f'''() => {{
                    const tabs = document.querySelectorAll('[data-baseweb="tab"]');
                    for (const tab of tabs) {{
                        if (tab.innerText.trim() === "{tab_text}") {{
                            tab.click();
                            return true;
                        }}
                    }}
                    return false;
                }}''')

                if not clicked:
                    logger.warning(f"  Could not click tab: {tab_text}")
                    continue

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


def capture_streamlit_sections(
    session_state: Dict[str, Any],
    app_url: str = "http://localhost:3006",
    sections_to_capture: Optional[List[str]] = None,
    viewport_width: int = 1920,
    viewport_height: int = 1080
) -> Dict[str, bytes]:
    """
    Capture screenshots of Streamlit tab SECTIONS using Playwright.
    This splits tabs into multiple sections for more granular PowerPoint slides.

    Args:
        session_state: Streamlit session state to pass to the app
        app_url: URL where Streamlit app is running
        sections_to_capture: List of section names to capture (None = capture all 8 sections)
        viewport_width: Browser viewport width
        viewport_height: Browser viewport height

    Returns:
        Dict mapping section name to PNG image bytes
    """
    # VERSION MARKER - confirms this updated code is running
    logger.info("=" * 60)
    logger.info("SECTION CAPTURE VERSION: 2024-01-06-v4 (fix Psychographic title + Emerging cropping)")
    logger.info("=" * 60)

    from playwright.sync_api import sync_playwright

    # Default sections to capture (8 sections from 4 tabs)
    if sections_to_capture is None:
        sections_to_capture = [
            "Score Card",
            "Executive Summary & Detailed Metrics",
            "Advanced Metric Analysis",
            "Psychographic Highlights & Audience Summary",
            "Growth Audience Insights",
            "Emerging Audience Opportunity",
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
            json.dumps(value)
            serializable_state[key] = value
        except (TypeError, ValueError):
            skipped_keys.append(key)
            logger.debug(f"Skipped non-serializable key: {key} ({type(value).__name__})")

    serializable_state['has_analyzed'] = True

    logger.info(f"Session state: {len(serializable_state)} keys saved, {len(skipped_keys)} skipped")

    with open(state_file, 'w') as f:
        json.dump(serializable_state, f)
    logger.info(f"Saved session state to {state_file}")

    screenshots = {}

    try:
        with sync_playwright() as p:
            logger.info("Launching headless Chromium browser for section capture...")
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
            time.sleep(3)

            # Inject the section visibility JavaScript functions
            logger.info("Injecting section visibility JavaScript functions...")
            page.evaluate(SECTION_JS_FUNCTIONS)

            # Get all available tabs
            tab_buttons = page.query_selector_all('[data-baseweb="tab"]')
            tab_names_in_page = [btn.inner_text().strip() for btn in tab_buttons]
            logger.info(f"Found {len(tab_buttons)} tabs in the app: {tab_names_in_page}")

            # Track current tab to avoid unnecessary tab switches
            current_tab = None

            for section_name in sections_to_capture:
                section_config = SECTION_SCREENSHOT_CONFIG.get(section_name)
                if not section_config:
                    logger.warning(f"No config found for section: {section_name}")
                    continue

                source_tab = section_config.get("source_tab", section_name)
                js_setup = section_config.get("js_setup")

                logger.info(f"Capturing section: {section_name} (source tab: {source_tab})")

                # Switch to source tab if needed
                if current_tab != source_tab:
                    logger.info(f"  Switching to tab: {source_tab}")
                    clicked = page.evaluate(f'''() => {{
                        const tabs = document.querySelectorAll('[data-baseweb="tab"]');
                        for (const tab of tabs) {{
                            if (tab.innerText.trim() === "{source_tab}") {{
                                tab.click();
                                return true;
                            }}
                        }}
                        return false;
                    }}''')

                    if not clicked:
                        logger.warning(f"  Could not click tab: {source_tab}")
                        continue

                    time.sleep(2)
                    current_tab = source_tab

                    # Wait for any loading spinners
                    try:
                        page.wait_for_selector('[data-testid="stSpinner"]', state='hidden', timeout=5000)
                    except:
                        pass

                    # Re-inject JS functions after tab switch (DOM might have changed)
                    page.evaluate(SECTION_JS_FUNCTIONS)

                # Special handling for specific tabs/sections
                if source_tab == "Audience Insights":
                    # Force large viewport for full content
                    min_height = section_config.get("min_height", 2500)
                    logger.info(f"  [AUDIENCE INSIGHTS] Setting viewport height to {min_height}px")
                    page.set_viewport_size({'width': viewport_width, 'height': min_height})
                    time.sleep(1)
                    # Scroll to trigger lazy loading
                    page.evaluate('() => window.scrollTo(0, 99999)')
                    time.sleep(0.5)
                    page.evaluate('() => window.scrollTo(0, 0)')
                    time.sleep(0.5)

                if source_tab == "Trend Analysis":
                    # Expand "About this heatmap" section
                    logger.info(f"  [TREND ANALYSIS] Expanding 'About this heatmap' section")
                    page.evaluate('''() => {
                        const allSummaries = document.querySelectorAll('summary');
                        for (const summary of allSummaries) {
                            if (summary.textContent.includes('About this heatmap')) {
                                summary.click();
                                return true;
                            }
                        }
                        return false;
                    }''')
                    time.sleep(1)

                # Restore all sections before applying new visibility rules
                page.evaluate('restoreAllSections()')
                time.sleep(0.3)

                # Apply section-specific visibility (if js_setup is defined)
                if js_setup:
                    logger.info(f"  Applying visibility function: {js_setup}()")
                    result = page.evaluate(f'{js_setup}()')
                    logger.info(f"  {js_setup}() returned: {result}")
                    time.sleep(0.5)

                # HIDE the tab bar and other UI elements for clean screenshot
                page.evaluate('''() => {
                    const tabList = document.querySelector('[data-baseweb="tab-list"]');
                    if (tabList) tabList.style.display = 'none';
                    const header = document.querySelector('[data-testid="stHeader"]');
                    if (header) header.style.display = 'none';
                    const toolbar = document.querySelector('[data-testid="stToolbar"]');
                    if (toolbar) toolbar.style.display = 'none';
                    const mainBlock = document.querySelector('[data-testid="stMainBlockContainer"]');
                    if (mainBlock) mainBlock.style.paddingTop = '0';
                }''')

                # Hide tooltips
                page.evaluate('''() => {
                    const style = document.createElement('style');
                    style.id = 'hide-tooltips';
                    style.textContent = `
                        .tooltip, .tooltiptext, .info-icon,
                        .tip-bubble, .tip-content, .tip-icon, .tip-title, .tip-learn-more,
                        [data-testid="stTooltipIcon"], [data-testid="stTooltipHoverTarget"],
                        [data-baseweb="tooltip"], [role="tooltip"] {
                            display: none !important;
                            visibility: hidden !important;
                        }
                    `;
                    if (!document.getElementById('hide-tooltips')) {
                        document.head.appendChild(style);
                    }
                }''')
                time.sleep(0.3)

                # Get config for viewport sizing
                extra_padding = section_config.get("extra_padding", 200)
                capture_mode = section_config.get("capture_mode", "panel")
                min_height = section_config.get("min_height", 0)

                # Find the active tab panel from the RESULTS tabs
                # In export mode: allTabs[0] = Results (no Upload/Paste tabs)
                # In normal mode: allTabs[1] = Results
                # We identify results tabs by looking for "Detailed Metrics" tab button
                logger.info(f"  [DEBUG] Looking for results panel for section: {section_name}")
                panel_info = page.evaluate('''() => {
                    // First, clear any previous capture-target markers
                    document.querySelectorAll('[data-capture-target]').forEach(el => {
                        el.removeAttribute('data-capture-target');
                    });

                    const allTabs = document.querySelectorAll('[data-testid="stTabs"]');
                    const debugInfo = {
                        totalStTabs: allTabs.length,
                        selector: '[data-baseweb="tab-panel"]',
                        message: ''
                    };

                    if (allTabs.length === 0) {
                        debugInfo.message = 'No stTabs found, using first tab-panel';
                        return debugInfo;
                    }

                    // Find which stTabs contains the "Detailed Metrics" tab
                    let resultsTabs = null;
                    let resultsTabsIndex = -1;
                    for (let i = 0; i < allTabs.length; i++) {
                        const tabButtons = allTabs[i].querySelectorAll('[data-baseweb="tab"]');
                        for (const btn of tabButtons) {
                            if (btn.innerText.includes('Detailed Metrics')) {
                                resultsTabs = allTabs[i];
                                resultsTabsIndex = i;
                                break;
                            }
                        }
                        if (resultsTabs) break;
                    }

                    if (!resultsTabs) {
                        debugInfo.message = 'Could not find results tabs by content, using first stTabs';
                        resultsTabs = allTabs[0];
                        resultsTabsIndex = 0;
                    }

                    debugInfo.resultsTabsIndex = resultsTabsIndex;
                    const panels = resultsTabs.querySelectorAll(':scope > div > [role="tabpanel"]');
                    debugInfo.totalPanels = panels.length;

                    for (let i = 0; i < panels.length; i++) {
                        if (!panels[i].hasAttribute('hidden')) {
                            // Mark this panel with a unique ID for selection
                            panels[i].setAttribute('data-capture-target', 'true');
                            debugInfo.selector = '[data-capture-target="true"]';
                            debugInfo.message = 'Found active results panel at stTabs[' + resultsTabsIndex + '], panel index ' + i;
                            debugInfo.panelIndex = i;
                            return debugInfo;
                        }
                    }

                    debugInfo.message = 'No active panel in results tabs';
                    return debugInfo;
                }''')
                logger.info(f"  [DEBUG] Panel info: {panel_info}")
                panel_selector = panel_info.get('selector', '[data-baseweb="tab-panel"]')
                logger.info(f"  Panel selector: {panel_selector}")
                active_panel = page.query_selector(panel_selector)

                if active_panel:
                    scroll_height = active_panel.evaluate('el => el.scrollHeight')
                    client_height = active_panel.evaluate('el => el.clientHeight')

                    # FALLBACK: If panel has zero dimensions, the JS hiding went wrong
                    # Restore and try full page capture
                    if scroll_height == 0 or client_height == 0:
                        logger.warning(f"  Panel has zero dimensions! Restoring and using full page capture...")
                        page.evaluate('restoreAllSections()')
                        time.sleep(0.5)
                        # Re-apply JS setup more carefully
                        if js_setup:
                            logger.info(f"  Re-applying {js_setup}() after restore...")
                            page.evaluate(f'{js_setup}()')
                            time.sleep(0.5)
                        # Get new dimensions
                        scroll_height = active_panel.evaluate('el => el.scrollHeight')
                        client_height = active_panel.evaluate('el => el.clientHeight')
                        logger.info(f"  After restore - Panel dimensions: scrollHeight={scroll_height}, clientHeight={client_height}")
                        # If still zero, use full page capture
                        if scroll_height == 0 or client_height == 0:
                            logger.warning(f"  Still zero dimensions - using full page capture")
                            screenshot_bytes = page.screenshot(type='png', full_page=True)
                            # Apply cropping and continue
                            from PIL import Image
                            import io
                            img = Image.open(io.BytesIO(screenshot_bytes))
                            original_height = img.height
                            original_width = img.width
                            crop_top = section_config.get("crop_top", 0)
                            crop_bottom = section_config.get("crop_bottom", 0)
                            logger.info(f"  Config: crop_top={crop_top}px, crop_bottom={crop_bottom}px, original_height={original_height}px")
                            if crop_top > 0 or crop_bottom > 0:
                                new_top = crop_top
                                new_bottom = original_height - crop_bottom
                                if new_bottom > new_top:
                                    logger.info(f"  Cropping: {original_height}px -> {new_bottom - new_top}px")
                                    img = img.crop((0, new_top, original_width, new_bottom))
                                    output = io.BytesIO()
                                    img.save(output, format='PNG')
                                    screenshot_bytes = output.getvalue()
                            screenshots[section_name] = screenshot_bytes
                            logger.info(f"  ✓ Captured {section_name} (full page fallback) ({len(screenshot_bytes):,} bytes)")
                            page.set_viewport_size({'width': viewport_width, 'height': viewport_height})
                            page.evaluate('''() => {
                                const tabList = document.querySelector('[data-baseweb="tab-list"]');
                                if (tabList) tabList.style.display = '';
                            }''')
                            time.sleep(0.2)
                            continue  # Skip to next section

                    if section_config.get("force_full_page", False):
                        page.evaluate('() => window.scrollTo(0, document.documentElement.scrollHeight)')
                        time.sleep(0.3)
                        page.evaluate('() => window.scrollTo(0, 0)')
                        time.sleep(0.3)
                        page_scroll_height = page.evaluate('() => document.documentElement.scrollHeight')
                        scroll_height = max(scroll_height, page_scroll_height)

                    logger.info(f"  Panel dimensions: scrollHeight={scroll_height}, clientHeight={client_height}")

                    active_panel.evaluate('element => element.scrollTop = 0')
                    page.evaluate('() => window.scrollTo(0, 0)')
                    time.sleep(0.3)

                    bbox = active_panel.bounding_box()
                    if bbox and scroll_height > client_height:
                        new_height = int(bbox['y']) + scroll_height + extra_padding
                        logger.info(f"  Resizing viewport to {new_height}px")
                        page.set_viewport_size({'width': viewport_width, 'height': new_height})
                        time.sleep(0.5)
                        # Re-query using the CORRECT selector (the one we used initially)
                        active_panel = page.query_selector(panel_selector)
                        logger.info(f"  Re-queried panel with selector: {panel_selector}")
                        if active_panel:
                            active_panel.evaluate('element => element.scrollTop = 0')
                            page.evaluate('() => window.scrollTo(0, 0)')

                    if min_height > 0:
                        current_viewport = page.viewport_size
                        if current_viewport and current_viewport['height'] < min_height:
                            logger.info(f"  Expanding viewport to min_height={min_height}px")
                            page.set_viewport_size({'width': viewport_width, 'height': min_height})
                            time.sleep(0.5)

                    if capture_mode == "full_page":
                        logger.info(f"  Using full_page capture mode")
                        screenshot_bytes = page.screenshot(type='png', full_page=True)
                    else:
                        screenshot_bytes = active_panel.screenshot(type='png')
                else:
                    screenshot_bytes = page.screenshot(type='png', full_page=True)
                    logger.info(f"  Fallback: captured full page")

                # Apply cropping
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(screenshot_bytes))
                original_height = img.height
                original_width = img.width

                crop_top = section_config.get("crop_top", 0)
                crop_bottom = section_config.get("crop_bottom", 0)

                logger.info(f"  Config: crop_top={crop_top}px, crop_bottom={crop_bottom}px, original_height={original_height}px")

                if crop_top > 0 or crop_bottom > 0:
                    new_top = crop_top
                    new_bottom = original_height - crop_bottom
                    if new_bottom > new_top:
                        logger.info(f"  Cropping: {original_height}px -> {new_bottom - new_top}px")
                        img = img.crop((0, new_top, original_width, new_bottom))
                        output = io.BytesIO()
                        img.save(output, format='PNG')
                        screenshot_bytes = output.getvalue()

                screenshots[section_name] = screenshot_bytes
                logger.info(f"  ✓ Captured {section_name} ({len(screenshot_bytes):,} bytes, {img.width}x{img.height}px)")

                # Reset viewport for next section
                page.set_viewport_size({'width': viewport_width, 'height': viewport_height})

                # Restore tab bar for next iteration
                page.evaluate('''() => {
                    const tabList = document.querySelector('[data-baseweb="tab-list"]');
                    if (tabList) tabList.style.display = '';
                }''')
                time.sleep(0.2)

            browser.close()
            logger.info(f"Browser closed. Total sections captured: {len(screenshots)}")

    except Exception as e:
        logger.error(f"Error capturing sections: {e}")
        raise

    finally:
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

    elif tab_name == "Competitor Tactics":
        competitor_tactics = session_state.get('competitor_tactics', [])

        tactics_html = ""
        if isinstance(competitor_tactics, list) and len(competitor_tactics) > 0:
            for i, tactic in enumerate(competitor_tactics, 1):
                # Handle tactics that might be formatted as "Header: Content"
                if isinstance(tactic, str):
                    if ':' in tactic:
                        parts = tactic.split(':', 1)
                        header = parts[0].strip()
                        content = parts[1].strip() if len(parts) > 1 else ''
                        tactics_html += f"""
                        <div class="metric-card">
                            <div class="metric-name">{header}</div>
                            <div class="audience-desc">{content}</div>
                        </div>
                        """
                    else:
                        tactics_html += f"""
                        <div class="metric-card">
                            <div class="metric-name">Strategy {i}</div>
                            <div class="audience-desc">{tactic}</div>
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
            .strategy-header {{
                background: linear-gradient(90deg, #6171EA, #3b82f6);
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                font-size: 18px;
                font-weight: 600;
            }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="title">Competitor Strategy Analysis - {brand_name}</div>
                <div class="strategy-header">Fortune 500 Counter-Strategy Recommendations</div>
                {tactics_html if tactics_html else '<p>No competitor tactics generated. Enter a competitor brand to generate strategies.</p>'}
            </div>
        </body>
        </html>
        """

    # =========================================================================
    # NEW SECTION-BASED TEMPLATES (for 8-slide export)
    # =========================================================================

    elif tab_name == "Score Card":
        # Score Card: Title + Radar summary + KPI boxes
        ai_insights = session_state.get('ai_insights', {})
        top_strength = ai_insights.get('top_strength', 'N/A') if isinstance(ai_insights, dict) else 'N/A'
        key_opportunity = ai_insights.get('key_opportunity', 'N/A') if isinstance(ai_insights, dict) else 'N/A'
        roi_potential = ai_insights.get('roi_potential', 'N/A') if isinstance(ai_insights, dict) else 'N/A'

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{styles}
        <style>
            .kpi-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-top: 30px;
            }}
            .kpi-box {{
                padding: 20px;
                border-radius: 12px;
                text-align: center;
            }}
            .kpi-box.strength {{ background: #e0f7ec; border: 2px solid #10b981; }}
            .kpi-box.opportunity {{ background: #fff4e5; border: 2px solid #f59e0b; }}
            .kpi-box.roi {{ background: #fef2f2; border: 2px solid #ef4444; }}
            .kpi-title {{
                font-weight: 600;
                font-size: 14px;
                margin-bottom: 10px;
            }}
            .kpi-value {{
                font-size: 16px;
                line-height: 1.4;
            }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="title">Audience Resonance Index Scorecard - {brand_name}</div>
                <div class="kpi-grid">
                    <div class="kpi-box strength">
                        <div class="kpi-title">Top Strength</div>
                        <div class="kpi-value">{top_strength}</div>
                    </div>
                    <div class="kpi-box opportunity">
                        <div class="kpi-title">Key Opportunity</div>
                        <div class="kpi-value">{key_opportunity}</div>
                    </div>
                    <div class="kpi-box roi">
                        <div class="kpi-title">ROI Potential</div>
                        <div class="kpi-value">{roi_potential}</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    elif tab_name == "Executive Summary & Detailed Metrics":
        ai_insights = session_state.get('ai_insights', {})
        summary = ai_insights.get('summary', 'Executive summary not available') if isinstance(ai_insights, dict) else 'Executive summary not available'

        metrics_html = ""
        for metric_name, value in scores.items():
            try:
                if isinstance(value, (int, float)):
                    name_str = str(metric_name) if not isinstance(metric_name, str) else metric_name
                    display_name = name_str.replace('_', ' ').title()
                    percentage = min(100, max(0, value * 10))
                    color = "#10b981" if value >= 8 else "#f59e0b" if value >= 6 else "#ef4444"
                    metrics_html += f"""
                    <div class="metric-card">
                        <div class="metric-name">{display_name}</div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: {percentage}%; background: {color};"></div>
                        </div>
                        <div class="metric-value" style="color: {color};">{value:.1f}</div>
                    </div>
                    """
            except Exception:
                pass

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{styles}</head>
        <body>
            <div class="container">
                <div class="title">Executive Summary & Detailed Metrics - {brand_name}</div>
                <h3 style="color: #334155;">Executive Summary</h3>
                <p style="font-size: 16px; line-height: 1.6; margin-bottom: 30px;">{summary}</p>
                <h3 style="color: #334155;">Detailed Metrics</h3>
                <div class="grid">
                    {metrics_html}
                </div>
            </div>
        </body>
        </html>
        """

    elif tab_name == "Advanced Metric Analysis":
        metrics_html = ""
        for metric_name, value in scores.items():
            try:
                if isinstance(value, (int, float)):
                    name_str = str(metric_name) if not isinstance(metric_name, str) else metric_name
                    display_name = name_str.replace('_', ' ').title()
                    metrics_html += f"""
                    <div class="metric-card">
                        <div class="metric-name" style="font-size: 18px;">{display_name} - {value:.1f}</div>
                        <div class="audience-desc">In-depth analysis of {display_name.lower()} score and recommendations for improvement.</div>
                    </div>
                    """
            except Exception:
                pass

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
                <div class="title">Advanced Metric Analysis - {brand_name}</div>
                {metrics_html if metrics_html else '<p>No metrics available for analysis.</p>'}
            </div>
        </body>
        </html>
        """

    elif tab_name == "Psychographic Highlights & Audience Summary":
        audience_summary = session_state.get('audience_summary', {})
        core = audience_summary.get('core_audience', 'Core audience not defined')
        primary = audience_summary.get('primary_audience', 'Primary audience signal not defined')
        secondary = audience_summary.get('secondary_audience', 'Secondary audience signal not defined')
        psychographic = session_state.get('pychographic_highlights', 'Psychographic highlights not available')

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{styles}
        <style>
            .audience-section {{
                margin-bottom: 25px;
                padding: 20px;
                background: #f8fafc;
                border-radius: 12px;
                border-left: 4px solid #6171EA;
            }}
            .audience-title {{
                font-size: 18px;
                font-weight: 600;
                color: #6171EA;
                margin-bottom: 10px;
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
                <div class="title">Psychographic Highlights & Audience Summary - {brand_name}</div>
                <h3 style="color: #334155;">Psychographic Highlights</h3>
                <div style="margin-bottom: 30px; font-size: 16px; line-height: 1.6;">{psychographic}</div>
                <h3 style="color: #334155;">Audience Summary</h3>
                <div class="audience-section">
                    <div class="audience-title">Core Audience</div>
                    <div class="audience-desc">{core}</div>
                </div>
                <div class="audience-section">
                    <div class="audience-title">Primary Audience Signal</div>
                    <div class="audience-desc">{primary}</div>
                </div>
                <div class="audience-section">
                    <div class="audience-title">Secondary Audience Signal</div>
                    <div class="audience-desc">{secondary}</div>
                </div>
            </div>
        </body>
        </html>
        """

    elif tab_name == "Growth Audience Insights":
        audience_segments = session_state.get('audience_segments', {})
        segments = audience_segments.get('segments', []) if isinstance(audience_segments, dict) else []

        segments_html = ""
        for i, segment in enumerate(segments[:2]):  # Primary and Secondary only
            if isinstance(segment, dict):
                name = segment.get('name', f'Segment {i+1}')
                description = segment.get('description', 'Description not available')
                label = "Primary" if i == 0 else "Secondary Growth"
                color = "#10b981" if i == 0 else "#6366f1"
                segments_html += f"""
                <div class="segment-card" style="border-color: {color};">
                    <div class="segment-label" style="background: {color};">{label}</div>
                    <div class="segment-name">{name}</div>
                    <div class="segment-desc">{description}</div>
                </div>
                """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{styles}
        <style>
            .segments-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 30px;
            }}
            .segment-card {{
                padding: 25px;
                border-radius: 12px;
                border: 2px solid;
                background: white;
            }}
            .segment-label {{
                display: inline-block;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 15px;
            }}
            .segment-name {{
                font-size: 20px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 12px;
            }}
            .segment-desc {{
                font-size: 15px;
                line-height: 1.6;
                color: #475569;
            }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="title">Growth Audience Insights - {brand_name}</div>
                <div class="segments-grid">
                    {segments_html if segments_html else '<p>No audience segments available.</p>'}
                </div>
            </div>
        </body>
        </html>
        """

    elif tab_name == "Emerging Audience Opportunity":
        audience_segments = session_state.get('audience_segments', {})
        segments = audience_segments.get('segments', []) if isinstance(audience_segments, dict) else []
        emerging = segments[-1] if segments else {}

        name = emerging.get('name', 'Emerging Growth Segment') if isinstance(emerging, dict) else 'Emerging Growth Segment'
        description = emerging.get('description', 'This audience segment shows high potential for growth.') if isinstance(emerging, dict) else 'This audience segment shows high potential for growth.'
        targeting_params = emerging.get('targeting_params', {}) if isinstance(emerging, dict) else {}
        interests = emerging.get('interest_categories', []) if isinstance(emerging, dict) else []

        demographics_html = ""
        if targeting_params:
            demographics_html = f"""
            <p><strong>Age:</strong> {targeting_params.get('age_range', 'N/A')}</p>
            <p><strong>Gender:</strong> {targeting_params.get('gender_targeting', 'N/A')}</p>
            <p><strong>Income:</strong> {targeting_params.get('income_targeting', 'N/A')}</p>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{styles}
        <style>
            .emerging-box {{
                padding: 30px;
                border-left: 4px solid #5865f2;
                background: #f5f7ff;
                border-radius: 12px;
            }}
            .emerging-title {{
                font-size: 24px;
                font-weight: 700;
                color: #4338ca;
                margin-bottom: 15px;
            }}
            .emerging-desc {{
                font-size: 16px;
                line-height: 1.6;
                color: #475569;
                font-style: italic;
                margin-bottom: 20px;
            }}
            .detail-section {{
                margin-top: 15px;
            }}
            .detail-section strong {{
                color: #334155;
            }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="title">Emerging Audience Opportunity - {brand_name}</div>
                <div class="emerging-box">
                    <div class="emerging-title">{name}</div>
                    <div class="emerging-desc">{description}</div>
                    <div class="detail-section">
                        <h4>Demographics</h4>
                        {demographics_html if demographics_html else '<p>Demographics data not available</p>'}
                    </div>
                    <div class="detail-section">
                        <h4>Key Interests</h4>
                        <p>{', '.join(interests) if interests else 'Interests identified through AI pattern recognition'}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    return None


# Convenience function for direct use
def capture_streamlit_screenshots(
    session_state: Dict[str, Any],
    use_live_capture: bool = False,
    app_url: str = "http://localhost:3006",
    use_sections: bool = True
) -> Dict[str, bytes]:
    """
    Capture screenshots of Streamlit content.

    Args:
        session_state: Streamlit session state
        use_live_capture: If True, capture from running app; if False, render HTML
        app_url: URL of the running Streamlit app (only used if use_live_capture=True)
        use_sections: If True, capture 8 sections; if False, capture 4 tabs (legacy)

    Returns:
        Dict mapping section/tab name to PNG bytes
    """
    # New section-based capture (8 slides from 4 tabs)
    sections = [
        "Score Card",
        "Executive Summary & Detailed Metrics",
        "Advanced Metric Analysis",
        "Psychographic Highlights & Audience Summary",
        "Growth Audience Insights",
        "Emerging Audience Opportunity",
        "Media Affinities",
        "Trend Analysis",
    ]

    # Legacy tab-based capture (4 slides)
    tabs = ["Detailed Metrics", "Audience Insights", "Media Affinities", "Trend Analysis"]

    logger.info("=" * 60)
    logger.info("STREAMLIT SCREENSHOT CAPTURE STARTED")
    logger.info(f"Mode: {'Live capture' if use_live_capture else 'HTML rendering'}")
    logger.info(f"Capture type: {'Sections (8 slides)' if use_sections else 'Tabs (4 slides)'}")
    logger.info(f"Items to capture: {sections if use_sections else tabs}")
    logger.info("=" * 60)

    if use_live_capture:
        logger.info(f"Using live capture from: {app_url}")
        if use_sections:
            return capture_streamlit_sections(session_state, app_url, sections)
        else:
            return capture_streamlit_tabs(session_state, app_url, tabs)
    else:
        # Use HTML rendering (doesn't require app to be running)
        logger.info("Using HTML rendering mode (no live app required)")
        screenshots = {}
        items_to_capture = sections if use_sections else tabs
        for item_name in items_to_capture:
            logger.info(f"Processing: {item_name}")
            png_bytes = capture_tab_content_as_html(session_state, item_name)
            if png_bytes:
                screenshots[item_name] = png_bytes
                logger.info(f"  ✓ Successfully captured {item_name}")
            else:
                logger.warning(f"  ✗ Failed to capture {item_name}")

        logger.info("=" * 60)
        logger.info(f"CAPTURE COMPLETE: {len(screenshots)}/{len(items_to_capture)} items captured")
        logger.info("=" * 60)
        return screenshots
