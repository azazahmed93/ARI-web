import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import requests
from io import BytesIO
import random
import time
import nltk

from analysis import (
    analyze_campaign_brief, 
    get_score_level, 
    calculate_benchmark_percentile, 
    get_improvement_areas
)
from utils import (
    create_pdf_download_link, 
    display_metric_bar, 
    get_tone_of_brief
)
from assets.styles import apply_styles, header_section, render_footer
from assets.content import (
    METRICS, 
    MEDIA_AFFINITY_SITES, 
    TV_NETWORKS, 
    STREAMING_PLATFORMS, 
    PSYCHOGRAPHIC_HIGHLIGHTS,
    AUDIENCE_SUMMARY,
    NEXT_STEPS,
    STOCK_PHOTOS
)

# Set page config
st.set_page_config(
    page_title="ARI Analyzer - Digital Culture Group",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom styles
apply_styles()

# Initialize session state for storing analysis results
if 'has_analyzed' not in st.session_state:
    st.session_state.has_analyzed = False
if 'scores' not in st.session_state:
    st.session_state.scores = None
if 'percentile' not in st.session_state:
    st.session_state.percentile = None
if 'improvement_areas' not in st.session_state:
    st.session_state.improvement_areas = None

# Define main function
def main():
    # Display header
    header_section()
    
    # Two-column layout for the banner image
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display a random stock photo
        analytics_image_url = random.choice(STOCK_PHOTOS["business_analytics"])
        response = requests.get(analytics_image_url)
        image = Image.open(BytesIO(response.content))
        st.image(image, use_column_width=True)
    
    with col2:
        # Brief description and input area
        st.markdown("### Campaign Brief Analysis")
        st.markdown("Paste your marketing campaign brief below to evaluate how well it will resonate with your target audience using our proprietary Audience Resonance Index™ framework.")
        
        # Text input for campaign brief
        brief_text = st.text_area(
            "Campaign Brief",
            height=200,
            help="Enter the full text of your campaign brief here. The more details you provide, the more accurate the analysis will be."
        )
        
        # Analysis button
        if st.button("Run Analysis", type="primary"):
            if not brief_text or brief_text.strip() == "":
                st.error("Please enter a campaign brief to analyze.")
            else:
                with st.spinner("Analyzing your campaign brief..."):
                    # Simulate analysis time
                    time.sleep(1.5)
                    
                    # Analyze the brief
                    scores = analyze_campaign_brief(brief_text)
                    
                    if not scores:
                        st.error("Could not analyze the brief. Please provide more content.")
                    else:
                        # Calculate benchmark percentile and improvement areas
                        percentile = calculate_benchmark_percentile(scores)
                        improvement_areas = get_improvement_areas(scores)
                        
                        # Store results in session state
                        st.session_state.has_analyzed = True
                        st.session_state.scores = scores
                        st.session_state.percentile = percentile
                        st.session_state.improvement_areas = improvement_areas
                        
                        # Show success message
                        st.success("Analysis complete! See results below.")
                        
                        # Trigger rerun to display results
                        st.rerun()
    
    # Display results if analysis has been performed
    if st.session_state.has_analyzed:
        display_results(
            st.session_state.scores,
            st.session_state.percentile,
            st.session_state.improvement_areas
        )
    
    # Footer
    render_footer()

def display_results(scores, percentile, improvement_areas):
    """Display the ARI analysis results."""
    st.markdown("---")
    st.markdown("## Audience Resonance Index™ Scorecard")
    
    # Display a random data visualization image
    viz_image_url = random.choice(STOCK_PHOTOS["data_visualization"])
    response = requests.get(viz_image_url)
    image = Image.open(BytesIO(response.content))
    st.image(image, width=300)
    
    # Display metrics as a radar chart
    display_radar_chart(scores)
    
    # Display each metric with a progress bar
    st.markdown("### Metric Breakdown")
    
    # Two-column layout for metrics
    col1, col2 = st.columns(2)
    
    # Display metrics in two columns
    metrics = list(scores.items())
    half = len(metrics) // 2 + len(metrics) % 2
    
    with col1:
        for metric, score in metrics[:half]:
            st.markdown(f"#### {metric}: {score}/10")
            st.progress(score/10)
            level = get_score_level(score)
            st.markdown(f"*{METRICS[metric][level]}*")
            st.markdown("---")
    
    with col2:
        for metric, score in metrics[half:]:
            st.markdown(f"#### {metric}: {score}/10")
            st.progress(score/10)
            level = get_score_level(score)
            st.markdown(f"*{METRICS[metric][level]}*")
            st.markdown("---")
    
    # Benchmark comparison
    st.markdown("### 📊 Benchmark Comparison")
    st.markdown(f"""
    This campaign ranks in the top **{percentile}% of Gen Z-facing national campaigns** 
    for Audience Resonance Index™ (ARI). That means it outperforms the majority of 
    peer campaigns in relevance, authenticity, and emotional connection — based on 
    Digital Culture Group's analysis of 300+ national efforts. Biggest opportunity areas: 
    **{", ".join(improvement_areas)}**.
    """)
    
    # Media Affinity section
    st.markdown("### 🔥 Top Media Affinity Sites")
    st.markdown("*QVI = Quality Visit Index, a score indicating audience engagement strength*")
    
    # Display media affinity sites in a grid
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    for i, site in enumerate(MEDIA_AFFINITY_SITES):
        with cols[i % 5]:
            st.markdown(f"""
            <div style="background:#e0edff; padding:10px; border-radius:10px; height:120px; margin-bottom:10px;">
                <strong>{site['name']}</strong>
                <div style="font-size:0.9rem;">{site['category']}</div>
                <div style="font-weight:bold; color:#3b82f6;">QVI: {site['qvi']}</div>
                <div style="font-size:0.8rem; margin-top:5px;">
                    <a href="{site['url']}" target="_blank">Visit Site</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # TV Network Affinities
    st.markdown("### 📺 Top TV Network Affinities")
    
    # Display TV networks in a grid
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    for i, network in enumerate(TV_NETWORKS):
        with cols[i % 5]:
            st.markdown(f"""
            <div style="background:#dbeafe; padding:10px; border-radius:10px; height:100px; margin-bottom:10px;">
                <strong>{network['name']}</strong>
                <div style="font-size:0.9rem;">{network['category']}</div>
                <div style="font-weight:bold; color:#1e88e5;">QVI: {network['qvi']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Streaming Platforms
    st.markdown("### 📶 Top Streaming Platforms")
    
    # Display streaming platforms in a grid
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, platform in enumerate(STREAMING_PLATFORMS):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#d1fae5; padding:10px; border-radius:10px; height:100px; margin-bottom:10px;">
                <strong>{platform['name']}</strong>
                <div style="font-size:0.9rem;">{platform['category']}</div>
                <div style="font-weight:bold; color:#059669;">QVI: {platform['qvi']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Psychographic Highlights
    st.markdown("### 🧠 Psychographic Highlights")
    st.markdown(PSYCHOGRAPHIC_HIGHLIGHTS, unsafe_allow_html=True)
    
    # Audience Summary
    st.markdown("### 👥 Audience Summary")
    st.markdown(AUDIENCE_SUMMARY, unsafe_allow_html=True)
    
    # Next Steps
    st.markdown("### 🔧 What's Next?")
    st.markdown(NEXT_STEPS, unsafe_allow_html=True)
    st.markdown("""
    Let's build a breakthrough growth strategy — Digital Culture Group has proven tactics 
    that boost underperforming areas.
    """)
    
    # PDF Download
    st.markdown("### Download Report")
    pdf_link = create_pdf_download_link(scores, improvement_areas, percentile)
    st.markdown(pdf_link, unsafe_allow_html=True)

def display_radar_chart(scores):
    """
    Display a radar chart of ARI metrics.
    
    Args:
        scores (dict): Dictionary of metric scores
    """
    # Prepare data for radar chart
    categories = list(scores.keys())
    values = list(scores.values())
    
    # Add the first value at the end to close the loop
    categories.append(categories[0])
    values.append(values[0])
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='ARI Score',
        line_color='#5865f2',
        fillcolor='rgba(88, 101, 242, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
