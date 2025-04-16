


import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.layouts.landing_layout import landing_layout
from assets.styles import apply_styles
from app.sections.results import display_results
from app.components.admin import is_admin
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

    inner_content = None
    # Display results if analysis has been performed
    if st.session_state.has_analyzed:
        inner_content = display_results

    if st.query_params.get('mode') != 'admin':
        landing_layout(inner_content)

    if st.query_params.get('mode') == 'admin' and is_admin():
        st.write("Upload configs and do secret admin stuff here.")
            # Add your file upload, config save, etc. logic here


# Run the app
if __name__ == "__main__":
    main()


image_path = "audience-image/Audience_7930a9ae_Introduction_03_24_25.png"
audience_insights = generate_audience_insights(image_path)
st.session_state.audience_insights = audience_insights

image_path_2 = "audience-image/Audience_7930a9ae_Media_Consumption_03_24_25.png"
media_consumption = generate_media_consumption(image_path_2)
st.session_state.audience_media_consumption = media_consumption

media_affinity = generate_media_affinity(audience_insights, media_consumption)
st.session_state.media_affinity = media_affinity

pychographic_highlights = generate_pychographic_highlights(audience_insights)
st.session_state.pychographic_highlights = pychographic_highlights


# print(st.session_state.media_affinity['media_affinity_sites'])
# print(st.session_state.pychographic_highlights)
