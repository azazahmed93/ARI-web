import streamlit as st
import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def load_export_session_state():
    """
    Load session state from temp file when in export mode.
    This allows Playwright to capture the actual rendered UI.
    """
    export_mode = st.query_params.get('export_mode')
    export_id = st.query_params.get('export_id')

    print(f"[EXPORT DEBUG] export_mode={export_mode}, export_id={export_id}")

    if export_mode == 'true' and export_id:
        # Look for the temp state file
        temp_dir = Path(tempfile.gettempdir()) / "ari_exports"
        state_file = temp_dir / f"{export_id}.json"

        print(f"[EXPORT DEBUG] Looking for state file: {state_file}")
        print(f"[EXPORT DEBUG] File exists: {state_file.exists()}")

        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    saved_state = json.load(f)

                print(f"[EXPORT DEBUG] Loaded state with {len(saved_state)} keys")
                print(f"[EXPORT DEBUG] Keys: {list(saved_state.keys())[:10]}...")

                # Load saved state into session state
                for key, value in saved_state.items():
                    if key not in ['_streamlit_internal']:  # Skip internal keys
                        st.session_state[key] = value

                # Ensure has_analyzed is True so results are displayed
                st.session_state.has_analyzed = True
                st.session_state._export_mode = True

                print(f"[EXPORT DEBUG] Set has_analyzed=True, session state updated")
                return True
            except Exception as e:
                print(f"[EXPORT DEBUG] Error loading export state: {e}")
        else:
            print(f"[EXPORT DEBUG] State file does not exist!")
            # List files in the directory
            if temp_dir.exists():
                files = list(temp_dir.glob("*.json"))
                print(f"[EXPORT DEBUG] Available files in {temp_dir}: {[f.name for f in files]}")

    return False
from app.layouts.landing_layout import landing_layout
from app.sections.results import display_results
from app.components.restricted_access import is_logged_in
from app.sections.admin_uploads import admin_uploads
from core.ai_insights import generate_audience_insights, generate_pychographic_highlights

# Import and run warmup on app load
try:
    from core.ai_warmup import warmup_openai_connection
    # Run warmup in background - non-blocking
    import threading
    if 'warmup_done' not in st.session_state:
        st.session_state.warmup_done = False
    if st.session_state.warmup_done is not True:
        st.session_state.warmup_done = True
        threading.Thread(target=warmup_openai_connection, daemon=True).start()
except Exception as e:
    print(f"Warmup initialization skipped: {e}")

# Define main function
def main():

    # Set page config
    st.set_page_config(
        page_title="ARI Analyzer - Digital Culture Group",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Check for export mode FIRST - load saved state if present
    is_export_mode = load_export_session_state()

    # Playwright diagnostic endpoint - access via ?test_playwright=true
    if st.query_params.get('test_playwright') == 'true':
        st.title("Playwright Diagnostic")
        try:
            from playwright.sync_api import sync_playwright
            st.write("✅ Playwright imported successfully")

            with sync_playwright() as p:
                st.write("✅ sync_playwright context created")
                st.write("🔄 Launching browser with extra args...")
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-gpu', '--disable-software-rasterizer', '--no-sandbox']
                )
                st.write("✅ Browser launched!")
                context = browser.new_context(viewport={'width': 1280, 'height': 720})
                page = context.new_page()
                st.write("✅ Page created")
                page.goto('data:text/html,<h1>Test</h1>')
                st.write("✅ Page loaded")
                page.wait_for_timeout(1000)
                st.write("🔄 Taking screenshot...")
                screenshot = page.screenshot(type='png')
                st.write(f"✅ Screenshot taken: {len(screenshot)} bytes")
                browser.close()
                st.write("✅ Browser closed")
                st.success("🎉 Playwright is working correctly!")
        except Exception as e:
            st.error(f"❌ Playwright failed: {e}")
            import traceback
            st.code(traceback.format_exc())
        return

    # Initialize session state for storing analysis results
    if 'has_analyzed' not in st.session_state:
        st.session_state.has_analyzed = False
    if 'scores' not in st.session_state:
        st.session_state.scores = None
    if 'percentile' not in st.session_state:
        st.session_state.percentile = None
    if 'improvement_areas' not in st.session_state:
        st.session_state.improvement_areas = None
    if 'brand_name' not in st.session_state:
        st.session_state.brand_name = None
    if 'industry' not in st.session_state:
        st.session_state.industry = None
    if 'product_type' not in st.session_state:
        st.session_state.product_type = None
    if 'brief_text' not in st.session_state:
        st.session_state.brief_text = None
    if 'ai_insights' not in st.session_state:
        st.session_state.ai_insights = None
    if 'competitor_analysis' not in st.session_state:
        st.session_state.competitor_analysis = None
    if 'audience_segments' not in st.session_state:
        st.session_state.audience_segments = None
    if 'competitor_tactics' not in st.session_state:
        st.session_state.competitor_tactics = []
    if 'media_affinity' not in st.session_state:
        st.session_state.media_affinity = {}
    if 'audience_media_consumption' not in st.session_state:
        st.session_state.audience_media_consumption = {}
    if 'audience_insights' not in st.session_state:
        st.session_state.audience_insights = {}
    if 'pychographic_highlights' not in st.session_state:
        st.session_state.pychographic_highlights = {}
    if 'audience_summary' not in st.session_state:
        st.session_state.audience_summary = {
            "core_audience": "",
            "primary_audience": "",
            "secondary_audience": "",
        }
    if 'use_openai' not in st.session_state:
        # Check if OpenAI API key is available
        st.session_state.use_openai = bool(os.environ.get("OPENAI_API_KEY"))
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    if "user_authenticated" not in st.session_state:
        st.session_state.user_authenticated = False
    if "is_gm_user" not in st.session_state:
        st.session_state.is_gm_user = False

    # Journey Environments resonance scores
    if 'journey_ad_format_scores' not in st.session_state:
        st.session_state.journey_ad_format_scores = None
    if 'journey_programming_show_scores' not in st.session_state:
        st.session_state.journey_programming_show_scores = None
    if 'journey_retargeting_channels' not in st.session_state:
        st.session_state.journey_retargeting_channels = None
    if 'journey_audience_profile' not in st.session_state:
        st.session_state.journey_audience_profile = None
    if 'journey_campaign_objectives' not in st.session_state:
        st.session_state.journey_campaign_objectives = None

    if 'brief_journey_data' not in st.session_state:
        st.session_state.brief_journey_data = None
    
    if 'consumer_journey_data' not in st.session_state:
        st.session_state.consumer_journey_data = None

    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = None
    
    if 'export_id' not in st.session_state:
        st.session_state.export_id = None

    inner_content = None
    # Display results if analysis has been performed
    if st.session_state.has_analyzed:
        inner_content = display_results

    # Check if we're in export mode (set by load_export_session_state)
    is_export_mode = st.session_state.get('_export_mode', False)

    if st.query_params.get('mode') != 'admin':
        if is_export_mode and st.session_state.has_analyzed:
            # In export mode, skip landing layout and show results directly
            # This allows Playwright to capture just the results tabs
            print("[EXPORT MODE] Skipping landing layout, showing results directly")
            display_results(
                st.session_state.get('scores'),
                st.session_state.get('percentile'),
                st.session_state.get('improvement_areas'),
                st.session_state.get('brand_name', 'Brand'),
                st.session_state.get('industry', 'General'),
                st.session_state.get('product_type', 'Product'),
                st.session_state.get('brief_text', ''),
            )
        else:
            # Normal mode - show landing layout
            if(is_logged_in()):
                landing_layout(inner_content)
    else:
        admin_uploads()

# Run the app
if __name__ == "__main__":
    main()



# Generate psychographic highlights only if audience_insights exists (from user input)
if 'audience_insights' in st.session_state and st.session_state.audience_insights:
    try:
        pychographic_highlights = generate_pychographic_highlights(st.session_state.audience_insights)
        st.session_state.pychographic_highlights = pychographic_highlights
    except:
        pass

# Ensure data is in correct format
if 'audience_insights' in st.session_state and isinstance(st.session_state.audience_insights, str):
    st.session_state.audience_insights = json.loads(st.session_state.audience_insights)
if 'audience_media_consumption' in st.session_state and isinstance(st.session_state.audience_media_consumption, str):
    st.session_state.audience_media_consumption = json.loads(st.session_state.audience_media_consumption)

