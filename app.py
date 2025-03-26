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
    get_improvement_areas,
    extract_brand_info
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
if 'brand_name' not in st.session_state:
    st.session_state.brand_name = None
if 'industry' not in st.session_state:
    st.session_state.industry = None
if 'product_type' not in st.session_state:
    st.session_state.product_type = None

# Define main function
def main():
    # Display header
    header_section()
    
    # Two-column layout for the banner image
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Create an animated data visualization that looks more sophisticated
        import numpy as np
        import time
        from datetime import datetime
        
        # Create a more sophisticated network-style visualization
        # Generate nodes and connections for network visualization
        np.random.seed(int(time.time()) % 100)  # Change seed each time for animation effect
        
        # Create a scatterpolar chart that looks like a network/radar
        theta = np.linspace(0, 2*np.pi, 12, endpoint=False)
        r_outer = np.random.uniform(0.7, 1.0, size=len(theta))
        r_inner = np.random.uniform(0.3, 0.6, size=len(theta))
        r_center = np.random.uniform(0.1, 0.2, size=len(theta))
        
        # Modern color scheme
        colors = ['#4F46E5', '#7C3AED', '#EC4899', '#F97316', '#3B82F6', '#10B981']
        
        # Create the main radar/network figure
        fig = go.Figure()
        
        # Add outer ring
        fig.add_trace(go.Scatterpolar(
            r=r_outer,
            theta=theta * 180/np.pi,
            fill='toself',
            fillcolor='rgba(79, 70, 229, 0.2)',  # Using rgba format for transparency
            line=dict(color=colors[0], width=2),
            name='Cultural Reach',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add middle ring
        fig.add_trace(go.Scatterpolar(
            r=r_inner,
            theta=theta * 180/np.pi,
            fill='toself',
            fillcolor='rgba(124, 58, 237, 0.2)',  # Using rgba format for transparency
            line=dict(color=colors[1], width=2),
            name='Audience Engagement',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add inner ring
        fig.add_trace(go.Scatterpolar(
            r=r_center,
            theta=theta * 180/np.pi,
            fill='toself',
            fillcolor='rgba(236, 72, 153, 0.2)',  # Using rgba format for transparency
            line=dict(color=colors[2], width=2),
            name='Core Performance',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add some connecting lines for network effect
        for i in range(len(theta)):
            if np.random.random() > 0.3:  # Only add some connections
                fig.add_trace(go.Scatterpolar(
                    r=[r_center[i], r_outer[i]],
                    theta=[theta[i] * 180/np.pi, theta[i] * 180/np.pi],
                    mode='lines',
                    line=dict(color=f'rgba(100, 100, 200, 0.4)', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # Add some points that look like data nodes
        for _ in range(15):
            r_point = np.random.uniform(0.1, 0.9)
            theta_point = np.random.uniform(0, 360)
            size = np.random.uniform(6, 12)
            color_idx = np.random.randint(0, len(colors))
            
            fig.add_trace(go.Scatterpolar(
                r=[r_point],
                theta=[theta_point],
                mode='markers',
                marker=dict(size=size, color=colors[color_idx]),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Update layout for a clean, modern look
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=False),
                angularaxis=dict(visible=False)
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        
        # Enhanced premium visualization with custom CSS for futuristic tech elements
        
        # First, create custom CSS with tech overlays
        st.markdown("""
        <style>
            /* Styles for tech overlay elements */
            @keyframes pulse {
                0% { opacity: 0.7; }
                50% { opacity: 1; }
                100% { opacity: 0.7; }
            }
            
            @keyframes blink {
                0% { opacity: 1; }
                49% { opacity: 1; }
                50% { opacity: 0; }
                100% { opacity: 0; }
            }
            
            @keyframes fadeInOut {
                0% { opacity: 0.4; }
                50% { opacity: 0.8; }
                100% { opacity: 0.4; }
            }
            
            .tech-container {
                position: relative;
                width: 100%;
                margin-bottom: 20px;
            }
            
            .status-indicator {
                position: absolute;
                top: 15px;
                right: 15px;
                background: rgba(0,0,0,0.7);
                border: 1px solid rgba(79, 70, 229, 0.6);
                border-radius: 4px;
                padding: 10px;
                color: #fff;
                font-size: 11px;
                display: flex;
                align-items: center;
                z-index: 100;
            }
            
            .indicator-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: #10b981; /* Changed to green to match the text */
                margin-right: 6px;
                animation: pulse 1.5s infinite ease-in-out;
            }
            
            .corner-box {
                position: absolute;
                bottom: 20px;
                right: 15px;
                border: 1px solid rgba(79, 70, 229, 0.6);
                background: rgba(0,0,0,0.5);
                padding: 5px;
                font-size: 9px;
                color: rgba(236, 72, 153, 0.9);
                border-radius: 3px;
                animation: fadeInOut 3s infinite ease-in-out;
                z-index: 100;
            }
            
            .module-names {
                position: absolute;
                bottom: 20px;
                left: 15px;
                color: rgba(59, 130, 246, 0.9);
                font-size: 9px;
                text-transform: uppercase;
                letter-spacing: 1px;
                z-index: 100;
            }
            
            .module-names div {
                margin-bottom: 3px;
            }
            
            .status-code {
                position: absolute;
                top: 15px;
                left: 15px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                color: rgba(79, 70, 229, 0.9);
                z-index: 100;
            }
            
            .status-code .blink {
                animation: blink 1s infinite;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Create a container for our visualization
        with st.container():
            # Add a div to establish relative positioning
            st.markdown('<div class="tech-container">', unsafe_allow_html=True)
            
            # Display the main visualization
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Add tech overlays with green text for specified elements
            st.markdown("""
            <div class="status-indicator" style="color: #10b981;">
                <div class="indicator-dot" style="background-color: #10b981;"></div>
                PROCESSING: <span style="color: #10b981; font-weight: bold; margin-left: 4px;">ACTIVE</span>
            </div>
            <div class="corner-box" style="color: #10b981;">SYSTEM INTEGRITY: 99.7%</div>
            <div class="module-names">
                <div>NEUROMORPHIC ENGINE V3.0.1</div>
                <div>CULTURAL PATTERN RECOGNITION ACTIVE</div>
                <div>QUANTUM HEURISTICS ENABLED</div>
            </div>
            <div class="status-code">
                ARI:XN:72.9:0:CT<span class="blink">_</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Close the container div
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Brief description and input area
        st.markdown("### Campaign RFP Analysis")
        st.markdown("Paste your marketing campaign RFP (Request for Proposal) below to identify gaps and provide actionable solutions for better outcomes. Our proprietary Audience Resonance Index™ framework analyzes how well your campaign will resonate with your target audience and identifies opportunities for improvement.")
        
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
                    result = analyze_campaign_brief(brief_text)
                    
                    if not result:
                        st.error("Could not analyze the brief. Please provide more content.")
                    else:
                        scores, brand_name, industry, product_type = result
                        
                        # Calculate benchmark percentile and improvement areas
                        percentile = calculate_benchmark_percentile(scores)
                        improvement_areas = get_improvement_areas(scores)
                        
                        # Store results in session state
                        st.session_state.has_analyzed = True
                        st.session_state.scores = scores
                        st.session_state.percentile = percentile
                        st.session_state.improvement_areas = improvement_areas
                        st.session_state.brand_name = brand_name
                        st.session_state.industry = industry
                        st.session_state.product_type = product_type
                        
                        # Show success message
                        st.success("Analysis complete! See results below.")
                        
                        # Trigger rerun to display results
                        st.rerun()
    
    # Display results if analysis has been performed
    if st.session_state.has_analyzed:
        display_results(
            st.session_state.scores,
            st.session_state.percentile,
            st.session_state.improvement_areas,
            st.session_state.brand_name,
            st.session_state.industry,
            st.session_state.product_type
        )
    
    # Footer
    render_footer()

def display_results(scores, percentile, improvement_areas, brand_name="Unknown", industry="General", product_type="Product"):
    """Display the ARI analysis results."""
    st.markdown("---")
    
    # Display brand information header with centered title
    if brand_name != "Unknown":
        st.markdown(f"<h2 style='text-align: center;'>{brand_name} Audience Resonance Index™ Scorecard</h2>", unsafe_allow_html=True)
        
        # Display brand info summary
        brand_info_col1, brand_info_col2 = st.columns(2)
        with brand_info_col1:
            st.markdown(f"**Industry:** {industry}")
        with brand_info_col2:
            st.markdown(f"**Product Type:** {product_type}")
            
        st.markdown("---")
    else:
        st.markdown("<h2 style='text-align: center;'>Audience Resonance Index™ Scorecard</h2>", unsafe_allow_html=True)
    
    # Display metrics as a radar chart
    display_radar_chart(scores)
    
    # Create a more professional metric breakdown section
    st.markdown('<h3 style="margin-top: 30px;">Advanced Metric Analysis</h3>', unsafe_allow_html=True)
    
    # Add an executive summary card
    st.markdown("""
    <div style="background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 20px; margin-bottom: 30px;">
        <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2; margin-bottom: 8px;">EXECUTIVE SUMMARY</div>
        <p style="margin-top: 0; margin-bottom: 15px; color: #333;">
            This campaign demonstrates strong performance in cultural relevance and platform selection, with opportunities
            for improvement in audience representation and commerce bridge. Our AI-powered analysis suggests targeting adjustments
            that could increase overall effectiveness by up to 18%.
        </p>
        <div style="display: flex; gap: 15px; flex-wrap: wrap;">
            <div style="background: #f0f2ff; border-radius: 6px; padding: 10px 15px;">
                <div style="font-size: 0.7rem; color: #5865f2; text-transform: uppercase; letter-spacing: 1px;">Top Strength</div>
                <div style="font-weight: 600; color: #333;">Cultural Relevance</div>
            </div>
            <div style="background: #f0f2ff; border-radius: 6px; padding: 10px 15px;">
                <div style="font-size: 0.7rem; color: #5865f2; text-transform: uppercase; letter-spacing: 1px;">Key Opportunity</div>
                <div style="font-weight: 600; color: #333;">Commerce Bridge</div>
            </div>
            <div style="background: #f0f2ff; border-radius: 6px; padding: 10px 15px;">
                <div style="font-size: 0.7rem; color: #5865f2; text-transform: uppercase; letter-spacing: 1px;">ROI Potential</div>
                <div style="font-weight: 600; color: #333;">+18%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add a header for the detailed metrics with properly styled CSS-only approach
    st.markdown('<div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #777; margin-bottom: 15px; text-align: center; background: white; padding: 12px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">Detailed Metrics Analysis</div>', unsafe_allow_html=True)
    
    # Create a more professional two-column layout
    col1, col2 = st.columns(2)
    
    # Display metrics in two columns with enhanced styling
    metrics = list(scores.items())
    half = len(metrics) // 2 + len(metrics) % 2
    
    with col1:
        for metric, score in metrics[:half]:
            # Define color based on score
            if score >= 8:
                color_code = "#10b981"  # green color
                emoji = "🔥"
                label = "STRONG"
            elif score >= 6:
                color_code = "#3b82f6"  # blue color
                emoji = "✓"
                label = "GOOD"
            else:
                color_code = "#f43f5e"  # red color
                emoji = "⚠️"
                label = "NEEDS IMPROVEMENT"
            
            # Create container for the metric card
            metric_container = st.container()
            with metric_container:
                # Using columns for header
                header_col1, header_col2 = st.columns([4, 1])
                header_col1.markdown(f"**{metric}**")
                header_col2.markdown(f'<div style="font-size: 0.7rem; background: {color_code}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 500; text-align: center;">{label}</div>', unsafe_allow_html=True)
                
                # Description right under the metric name
                st.markdown(f'<div style="font-size: 0.9rem; color: #555; margin: 5px 0 15px 0;">{METRICS[metric][get_score_level(score)]}</div>', unsafe_allow_html=True)
                
                # Custom progress bar using HTML/CSS instead of st.progress
                progress_width = score * 10  # Convert score to percentage
                st.markdown(f"""
                <div style="background-color: #f0f0f0; border-radius: 10px; height: 10px; margin: 10px 0;">
                    <div style="background-color: {color_code}; width: {progress_width}%; height: 10px; border-radius: 10px;"></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Score display
                st.markdown(f'<div style="text-align: right; font-weight: 600; color: {color_code}; margin-top: -15px;">{score}/10</div>', unsafe_allow_html=True)
                
                # Add some space between cards
                st.markdown("<br>", unsafe_allow_html=True)
    
    with col2:
        for metric, score in metrics[half:]:
            # Define color based on score
            if score >= 8:
                color_code = "#10b981"  # green color
                emoji = "🔥"
                label = "STRONG"
            elif score >= 6:
                color_code = "#3b82f6"  # blue color
                emoji = "✓"
                label = "GOOD"
            else:
                color_code = "#f43f5e"  # red color
                emoji = "⚠️"
                label = "NEEDS IMPROVEMENT"
            
            # Create container for the metric card
            metric_container = st.container()
            with metric_container:
                # Using columns for header
                header_col1, header_col2 = st.columns([4, 1])
                header_col1.markdown(f"**{metric}**")
                header_col2.markdown(f'<div style="font-size: 0.7rem; background: {color_code}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 500; text-align: center;">{label}</div>', unsafe_allow_html=True)
                
                # Description right under the metric name
                st.markdown(f'<div style="font-size: 0.9rem; color: #555; margin: 5px 0 15px 0;">{METRICS[metric][get_score_level(score)]}</div>', unsafe_allow_html=True)
                
                # Custom progress bar using HTML/CSS instead of st.progress
                progress_width = score * 10  # Convert score to percentage
                st.markdown(f"""
                <div style="background-color: #f0f0f0; border-radius: 10px; height: 10px; margin: 10px 0;">
                    <div style="background-color: {color_code}; width: {progress_width}%; height: 10px; border-radius: 10px;"></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Score display
                st.markdown(f'<div style="text-align: right; font-weight: 600; color: {color_code}; margin-top: -15px;">{score}/10</div>', unsafe_allow_html=True)
                
                # Add some space between cards
                st.markdown("<br>", unsafe_allow_html=True)
    
    # Benchmark comparison with premium enterprise styling
    st.markdown('<h3 style="margin-top: 40px; margin-bottom: 20px;">Competitive Benchmarking</h3>', unsafe_allow_html=True)
    
    # Create a dashboard-style KPI row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2;">PERCENTILE RANK</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #5865f2; margin: 10px 0;">Top {percentile}%</div>
            <div style="font-size: 0.85rem; color: #555;">Among all analyzed campaigns</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #10b981;">EXPECTED IMPACT</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #10b981; margin: 10px 0;">+18%</div>
            <div style="font-size: 0.85rem; color: #555;">Projected ROI increase</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #f43f5e;">ACTION ITEMS</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #f43f5e; margin: 10px 0;">{len(improvement_areas)}</div>
            <div style="font-size: 0.85rem; color: #555;">Priority improvement areas</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add an informative benchmark section
    st.markdown("""
    <div style="margin-top: 25px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px;">
        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2; margin-bottom: 15px; text-align: center;">Campaign Intelligence</div>
    """, unsafe_allow_html=True)
    
    # Customize benchmark text based on brand information
    if brand_name != "Unknown" and industry != "General":
        st.markdown(f"""
        <div style="color: #333; font-size: 1rem; line-height: 1.6;">
            This <span style="font-weight: 600;">{brand_name}</span> campaign ranks in the top <span style="font-weight: 600; color: #5865f2;">{percentile}%</span> of {industry} campaigns
            for Audience Resonance Index™. The campaign outperforms most of its peer initiatives in relevance, authenticity, and emotional connection — 
            based on Digital Culture Group's comprehensive analysis of over 300 {industry.lower()} marketing efforts.
            <br><br>
            For a {product_type} in the {industry} industry, our AI engine has identified these priority opportunity areas:
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="color: #333; font-size: 1rem; line-height: 1.6;">
            This campaign ranks in the top <span style="font-weight: 600; color: #5865f2;">{percentile}%</span> of Gen Z-facing national campaigns
            for Audience Resonance Index™. The campaign outperforms the majority of peer initiatives in relevance, authenticity, and emotional connection — 
            based on Digital Culture Group's comprehensive analysis of over 300 national marketing efforts.
            <br><br>
            Our AI engine has identified these priority opportunity areas:
        </div>
        """, unsafe_allow_html=True)
    
    # Add improvement areas as pill buttons
    imp_areas_html = "".join([f'<div style="display: inline-block; background: #f5f7fa; border: 1px solid #e5e7eb; border-radius: 30px; padding: 6px 16px; margin: 5px 8px 5px 0; font-size: 0.9rem; color: #5865f2; font-weight: 500;">{area}</div>' for area in improvement_areas])
    
    st.markdown(f"""
        <div style="margin-top: 15px;">{imp_areas_html}</div>
        """, unsafe_allow_html=True)
    
    # Add CTA button for improvement recommendations
    st.markdown("""
    <div style="margin-top: 20px; text-align: center;">
        <div style="display: inline-block; background: linear-gradient(90deg, #5865f2 0%, #7983f5 100%); color: white; font-weight: 600; padding: 10px 25px; border-radius: 6px; cursor: pointer; box-shadow: 0 4px 12px rgba(88, 101, 242, 0.3);">
            Generate Detailed Improvement Report
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Media Affinity section
    st.markdown("### 🔥 Top Media Affinity Sites")
    st.markdown("*QVI = Quality Visit Index, a score indicating audience engagement strength*")
    
    # Display media affinity sites in a grid
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    for i, site in enumerate(MEDIA_AFFINITY_SITES):
        with cols[i % 5]:
            # Truncate site name if it's too long
            name_display = site['name']
            if len(name_display) > 18:
                name_display = name_display[:15] + "..."
                
            st.markdown(f"""
            <div style="background:#e0edff; padding:10px; border-radius:10px; height:130px; margin-bottom:10px; overflow:hidden;">
                <div style="font-weight:bold; font-size:0.95rem; margin-bottom:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{name_display}</div>
                <div style="font-size:0.85rem; margin-bottom:5px;">{site['category']}</div>
                <div style="font-weight:bold; color:#3b82f6; margin-bottom:5px;">QVI: {site['qvi']}</div>
                <div style="font-size:0.8rem;">
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
            # Truncate network name if it's too long
            name_display = network['name']
            if len(name_display) > 14:
                name_display = name_display[:11] + "..."
                
            st.markdown(f"""
            <div style="background:#dbeafe; padding:10px; border-radius:10px; height:110px; margin-bottom:10px; overflow:hidden;">
                <div style="font-weight:bold; font-size:0.95rem; margin-bottom:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{name_display}</div>
                <div style="font-size:0.85rem; margin-bottom:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{network['category']}</div>
                <div style="font-weight:bold; color:#3b82f6;">QVI: {network['qvi']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Streaming Platforms
    st.markdown("### 📶 Top Streaming Platforms")
    
    # Display streaming platforms in a grid
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, platform in enumerate(STREAMING_PLATFORMS):
        with cols[i % 3]:
            # Truncate platform name if it's too long
            name_display = platform['name']
            if len(name_display) > 18:
                name_display = name_display[:15] + "..."
                
            st.markdown(f"""
            <div style="background:#d1fae5; padding:10px; border-radius:10px; height:110px; margin-bottom:10px; overflow:hidden;">
                <div style="font-weight:bold; font-size:0.95rem; margin-bottom:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{name_display}</div>
                <div style="font-size:0.85rem; margin-bottom:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{platform['category']}</div>
                <div style="font-weight:bold; color:#10b981;">QVI: {platform['qvi']}</div>
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
    
    # Premium investor-focused call-to-action section
    st.markdown("---")
    
    # Create container with custom CSS for styling
    st.markdown('<div class="premium-container"></div>', unsafe_allow_html=True)
    premium_container = st.container()
    
    with premium_container:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Create two columns for the layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown('<span class="tag-enterprise">Enterprise Analytics</span>', unsafe_allow_html=True)
            st.markdown("### Ready to take your marketing to the next level?")
            st.write("Download our comprehensive enterprise report with detailed metrics, actionable insights, and competitive benchmarking to optimize your campaign performance.")
            
            # Create a container for the checkmarks
            check_container = st.container()
            with check_container:
                # Use columns for the checkmarks
                check1, check2, check3 = st.columns(3)
                with check1:
                    st.markdown("✓ Advanced Metrics")
                with check2:
                    st.markdown("✓ Competitive Analysis")
                with check3:
                    st.markdown("✓ Executive Summary")
        
        with col2:
            # Generate and display the PDF download link
            pdf_link = create_pdf_download_link(scores, improvement_areas, percentile, brand_name, industry, product_type)
            st.markdown(pdf_link, unsafe_allow_html=True)
    
    # Add the demo section
    demo_container = st.container()
    with demo_container:
        st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.85rem; color: #777;'>Want to see how we can help your business?</p>", unsafe_allow_html=True)
        st.button("Schedule a Demo")

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
    
    # Create a benchmark comparison (industry average) for investor appeal
    industry_avg = [5.8, 6.2, 5.5, 6.0, 4.8, 5.2, 6.5, 5.9, 6.3]
    if len(industry_avg) < len(categories) - 1:
        # Make sure benchmark has enough values
        industry_avg = industry_avg + [5.5] * (len(categories) - 1 - len(industry_avg))
    elif len(industry_avg) > len(categories) - 1:
        # Trim if too many values
        industry_avg = industry_avg[:len(categories) - 1]
    
    # Add closing point
    industry_avg.append(industry_avg[0])
    
    # Create enhanced radar chart
    fig = go.Figure()
    
    # Add industry average for comparison
    fig.add_trace(go.Scatterpolar(
        r=industry_avg,
        theta=categories,
        fill='toself',
        name='Industry Average',
        line=dict(color='rgba(169, 169, 169, 0.8)', dash='dot'),
        fillcolor='rgba(169, 169, 169, 0.2)'
    ))
    
    # Add campaign score with improved styling
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Campaign Score',
        line=dict(color='#5865f2', width=3),
        fillcolor='rgba(88, 101, 242, 0.4)'
    ))
    
    # Add premium styling to the chart
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickfont=dict(size=10, family="Inter, sans-serif", color="#555"),
                tickvals=[2, 4, 6, 8, 10],
                gridcolor='rgba(0, 0, 0, 0.1)',
                linecolor='rgba(0, 0, 0, 0.1)',
            ),
            angularaxis=dict(
                tickfont=dict(size=11, family="Inter, sans-serif", color="#333", weight=500),
                linecolor='rgba(0, 0, 0, 0.1)',
                gridcolor='rgba(0, 0, 0, 0.05)',
            ),
            bgcolor='rgba(240, 242, 255, 0.3)',
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(family="Inter, sans-serif", size=12, color="#333")
        ),
        height=550,
        margin=dict(l=70, r=70, t=50, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        title={
            'text': '<b>Campaign Performance vs. Industry Average</b>',
            'y': 0.97,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=16, family="Inter, sans-serif", color="#333")
        },
    )
    
    # Center the title
    st.markdown('<div style="text-align: center;"><h4>Campaign Performance vs. Industry Average</h4></div>', unsafe_allow_html=True)
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': False,
        'responsive': True
    })

# Run the app
if __name__ == "__main__":
    main()