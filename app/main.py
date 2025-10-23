import streamlit as st
import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.layouts.landing_layout import landing_layout
from app.sections.results import display_results
from app.components.restricted_access import is_logged_in
from app.sections.admin_uploads import admin_uploads
from core.ai_insights import generate_audience_insights, generate_media_consumption,generate_media_affinity, generate_pychographic_highlights

# Import and run warmup on app load
try:
    from core.ai_warmup import warmup_openai_connection
    # Run warmup in background - non-blocking
    import threading
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

    inner_content = None
    # Display results if analysis has been performed
    if st.session_state.has_analyzed:
        inner_content = display_results

    if st.query_params.get('mode') != 'admin':
        if(is_logged_in()):
            landing_layout(inner_content)
    else:
        admin_uploads()

# Run the app
if __name__ == "__main__":
    main()

# Note: Psychographic data (audience_insights) is now handled by user input
# The following are still generated automatically if admin files exist:

# Generate media consumption if admin file exists
try:
    media_consumption = generate_media_consumption()
    if media_consumption:
        st.session_state.audience_media_consumption = media_consumption
except:
    pass

# Generate media affinity if admin file exists
try:
    media_affinity = generate_media_affinity()
    if media_affinity:
        st.session_state.media_affinity = media_affinity
except:
    pass

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

