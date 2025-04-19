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


audience_insights = generate_audience_insights()
st.session_state.audience_insights = audience_insights

media_consumption = generate_media_consumption()
st.session_state.audience_media_consumption = media_consumption

media_affinity = generate_media_affinity(audience_insights, media_consumption)
st.session_state.media_affinity = media_affinity

pychographic_highlights = generate_pychographic_highlights(audience_insights)
st.session_state.pychographic_highlights = pychographic_highlights


if isinstance(st.session_state.audience_insights, str):
    st.session_state.audience_insights = json.loads(st.session_state.audience_insights)
if isinstance(st.session_state.audience_media_consumption, str):
    st.session_state.audience_media_consumption = json.loads(st.session_state.audience_media_consumption)
