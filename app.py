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
import docx
import PyPDF2
import io
import os

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

# Import new AI analysis functions
from ai_analysis import (
    analyze_brief_with_ai,
    generate_ai_recommendations
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
# New AI Analysis session state variables
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = None
if 'ai_recommendations' not in st.session_state:
    st.session_state.ai_recommendations = None
if 'brief_text' not in st.session_state:
    st.session_state.brief_text = None

# Define function to extract text from various file types
def extract_text_from_file(uploaded_file):
    """
    Extract text from various file types including docx, pdf and txt.
    
    Args:
        uploaded_file: The file uploaded through Streamlit's file_uploader
        
    Returns:
        str: The extracted text from the file
    """
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == 'txt':
        # For text files
        return uploaded_file.getvalue().decode('utf-8')
    
    elif file_type == 'docx':
        # For Word documents
        doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    elif file_type == 'pdf':
        # For PDF files
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        return text
    
    else:
        # Unsupported file type
        return None

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
        
        # Modern color scheme - we'll keep this for styling the tech container
        colors = ['#4F46E5', '#7C3AED', '#EC4899', '#F97316', '#3B82F6', '#10B981']
        
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
                border: 2px solid #10b981; /* Thicker green border matching the indicator color */
                background: rgba(0,0,0,0.8); /* Darker background for better contrast */
                padding: 5px;
                font-size: 9px;
                color: rgba(236, 72, 153, 0.9);
                border-radius: 3px;
                animation: fadeInOut 3s infinite ease-in-out;
                z-index: 100;
            }
            
            .module-names {
                position: absolute;
                top: 50px; /* Keep higher position */
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
        
        # Create a container for our tech visualization (without radar chart)
        with st.container():
            # Add a div to establish relative positioning
            st.markdown('<div class="tech-container">', unsafe_allow_html=True)
            
            # Display tech elements without the background box
            st.markdown("""
            <div style="width: 100%; height: 250px; position: relative;">
            </div>
            """, unsafe_allow_html=True)
            
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
        # Campaign analysis description and input area
        st.markdown("### Pre-Launch Campaign Intelligence")
        st.markdown("Analyze your Advertising RFP or Marketing Brief to leverage our AI-powered Audience Resonance Index™ framework. We employ computational ethnography and cultural intelligence algorithms to forecast resonance patterns, identify opportunity vectors, and optimize cross-cultural alignment before campaign activation.")
        
        # Create tabs for input methods
        tab1, tab2 = st.tabs(["Upload Document", "Paste Text"])
        
        brief_text = ""
        
        with tab1:
            # File uploader for document input
            st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)  # Add some spacing
            uploaded_file = st.file_uploader(
                "Upload Marketing Brief or RFP", 
                type=["txt", "pdf", "docx"],
                help="Supported formats: TXT, PDF, DOCX. Maximum file size: 200MB."
            )
            
            # Display file details if uploaded
            if uploaded_file is not None:
                file_details = {
                    "Filename": uploaded_file.name,
                    "File size": f"{round(uploaded_file.size / 1024, 2)} KB",
                    "File type": uploaded_file.type
                }
                
                # Show the file details in a cleaner way
                st.markdown("<div style='background: #f8fafc; padding: 12px; border-radius: 8px; margin-top: 12px;'>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-weight: 500;'>File Details:</div>", unsafe_allow_html=True)
                for key, value in file_details.items():
                    st.markdown(f"<div style='font-size: 0.9rem; margin-top: 5px;'><span style='color: #64748b;'>{key}:</span> {value}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Extract text from the file
                file_text = extract_text_from_file(uploaded_file)
                if file_text:
                    brief_text = file_text
                    st.success(f"File processed successfully. Ready for analysis.")
                else:
                    st.error("Could not extract text from the file. Please check the file format.")
        
        with tab2:
            # Text input for manual entry
            input_brief_text = st.text_area(
                "Marketing Brief | RFP",
                height=200,
                help="Provide your complete RFP or marketing brief for comprehensive analysis. Greater detail yields more precise predictive intelligence and actionable recommendations."
            )
            if input_brief_text:
                brief_text = input_brief_text
        
        # Analysis button
        if st.button("Run Predictive Analysis", type="primary"):
            if not brief_text or brief_text.strip() == "":
                st.error("Please provide a Marketing Brief or RFP to proceed with analysis.")
            else:
                with st.spinner("Processing multi-dimensional cultural analysis vectors..."):
                    # Simulate analysis time
                    time.sleep(1.5)
                    
                    # Store brief text for AI analysis
                    st.session_state.brief_text = brief_text
                    
                    # Analyze the content with regular analysis
                    result = analyze_campaign_brief(brief_text)
                    
                    if not result:
                        st.error("Insufficient data complexity for comprehensive analysis. Please provide a more detailed brief or RFP.")
                    else:
                        scores, brand_name, industry, product_type = result
                        
                        # Use Apple as the default brand name for the demo
                        if not brand_name or brand_name.lower() == "unknown":
                            brand_name = "Apple"
                        
                        # Calculate benchmark percentile and improvement areas
                        percentile = calculate_benchmark_percentile(scores)
                        improvement_areas = get_improvement_areas(scores)
                        
                        # Run the AI analysis in the background
                        with st.spinner("Running advanced GPT-4o AI analysis..."):
                            try:
                                # Get AI analysis of the brief
                                ai_analysis = analyze_brief_with_ai(brief_text, brand_name)
                                
                                # Generate AI recommendations based on the scores
                                ai_recommendations = generate_ai_recommendations(scores, brand_name)
                                
                                # Store AI results in session state
                                st.session_state.ai_analysis = ai_analysis
                                st.session_state.ai_recommendations = ai_recommendations
                            except Exception as e:
                                st.warning(f"AI-powered advanced analysis unavailable. Using standard analysis model. Error: {e}")
                                st.session_state.ai_analysis = None
                                st.session_state.ai_recommendations = None
                        
                        # Store results in session state
                        st.session_state.has_analyzed = True
                        st.session_state.scores = scores
                        st.session_state.percentile = percentile
                        st.session_state.improvement_areas = improvement_areas
                        st.session_state.brand_name = brand_name
                        st.session_state.industry = industry
                        st.session_state.product_type = product_type
                        
                        # Show success message
                        st.success("Predictive resonance modeling complete. Intelligence insights generated successfully.")
                        
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
    
    # Display standard scorecard title with no brand reference
    st.markdown("<h2 style='text-align: center;'>Audience Resonance Index™ Scorecard</h2>", unsafe_allow_html=True)
    
    # Add some spacing after the title
    st.markdown("---")
    
    # Display metrics summary (replaced radar chart)
    display_summary_metrics(scores)
    
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
    
    # Display benchmark text (with no campaign-specific references)
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
    
    # GPT-4 AI Insights Section (only if AI analysis is available)
    if st.session_state.ai_analysis:
        st.markdown("""
        <h3 style="display:flex; align-items:center; gap:10px; margin-top: 40px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20ZM11 16H13V18H11V16ZM12.61 6.04C10.55 5.74 8.73 7.01 8.18 8.83C8 9.41 8.44 10 9.05 10H9.25C9.66 10 9.99 9.71 10.13 9.33C10.45 8.44 11.4 7.83 12.43 8.05C13.38 8.25 14.08 9.18 14 10.15C13.9 11.49 12.38 11.78 11.55 13.03C11.55 13.04 11.54 13.04 11.54 13.05C11.53 13.07 11.52 13.08 11.51 13.1C11.42 13.25 11.33 13.42 11.26 13.6C11.25 13.63 11.23 13.65 11.22 13.68C11.21 13.7 11.21 13.72 11.2 13.75C11.08 14.09 11 14.5 11 15H13C13 14.58 13.11 14.23 13.28 13.93C13.3 13.9 13.31 13.87 13.33 13.84C13.41 13.7 13.51 13.57 13.61 13.45C13.62 13.44 13.63 13.42 13.64 13.41C13.74 13.29 13.85 13.18 13.97 13.07C14.93 12.16 16.23 11.42 15.96 9.51C15.72 7.77 14.35 6.3 12.61 6.04Z" fill="#5865f2"/>
            </svg>
            AI-Powered Campaign Intelligence
        </h3>
        """, unsafe_allow_html=True)
        
        # Display the AI analysis executive summary
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 20px; margin-bottom: 20px;">
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2; margin-bottom: 8px;">EXECUTIVE SUMMARY</div>
            <p style="margin-top: 0; margin-bottom: 15px; color: #333; line-height: 1.6;">
                {st.session_state.ai_analysis.get('executive_summary', 'AI analysis not available.')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show AI analysis scores
        st.markdown("""
        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #777; margin: 25px 0 15px 0; text-align: center; background: white; padding: 12px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            GPT-4o Analysis Metrics
        </div>
        """, unsafe_allow_html=True)
        
        ai_metrics = {
            "Cultural Relevance": st.session_state.ai_analysis.get('cultural_relevance_score', 5),
            "Audience Alignment": st.session_state.ai_analysis.get('audience_alignment_score', 5),
            "Platform Strategy": st.session_state.ai_analysis.get('platform_strategy_score', 5),
            "Creative Alignment": st.session_state.ai_analysis.get('creative_alignment_score', 5)
        }
        
        # Create columns for AI metrics
        col1, col2 = st.columns(2)
        ai_metrics_list = list(ai_metrics.items())
        
        with col1:
            for metric, score in ai_metrics_list[:2]:
                # Define color based on score
                if score >= 8:
                    color_code = "#10b981"  # green
                elif score >= 6:
                    color_code = "#3b82f6"  # blue
                else:
                    color_code = "#f43f5e"  # red
                
                progress_width = score * 10  # Convert score to percentage
                
                # Create metric display
                st.markdown(f"""
                <div style="background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 15px; margin-bottom: 15px;">
                    <div style="font-weight: 600; margin-bottom: 10px;">{metric}</div>
                    <div style="background-color: #f0f0f0; border-radius: 10px; height: 10px; margin: 10px 0;">
                        <div style="background-color: {color_code}; width: {progress_width}%; height: 10px; border-radius: 10px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <div style="font-size: 0.8rem; color: #777;">Score</div>
                        <div style="font-weight: 600; color: {color_code};">{score}/10</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            for metric, score in ai_metrics_list[2:]:
                # Define color based on score
                if score >= 8:
                    color_code = "#10b981"  # green
                elif score >= 6:
                    color_code = "#3b82f6"  # blue
                else:
                    color_code = "#f43f5e"  # red
                
                progress_width = score * 10  # Convert score to percentage
                
                # Create metric display
                st.markdown(f"""
                <div style="background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 15px; margin-bottom: 15px;">
                    <div style="font-weight: 600; margin-bottom: 10px;">{metric}</div>
                    <div style="background-color: #f0f0f0; border-radius: 10px; height: 10px; margin: 10px 0;">
                        <div style="background-color: {color_code}; width: {progress_width}%; height: 10px; border-radius: 10px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <div style="font-size: 0.8rem; color: #777;">Score</div>
                        <div style="font-weight: 600; color: {color_code};">{score}/10</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Display Improvement Recommendations
        st.markdown("""
        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #777; margin: 25px 0 15px 0; text-align: center; background: white; padding: 12px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            Strategic Recommendations
        </div>
        """, unsafe_allow_html=True)
        
        # Display improvement areas from AI analysis
        if 'improvement_areas' in st.session_state.ai_analysis and st.session_state.ai_analysis['improvement_areas']:
            for i, area in enumerate(st.session_state.ai_analysis['improvement_areas']):
                st.markdown(f"""
                <div style="background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 15px; margin-bottom: 15px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="width: 30px; height: 30px; border-radius: 50%; background: #f0f7ff; color: #3b82f6; display: flex; align-items: center; justify-content: center; font-weight: 600;">{i+1}</div>
                        <div style="font-weight: 600;">{area}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Display AI-generated recommendations if available
        if st.session_state.ai_recommendations:
            st.markdown("""
            <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #777; margin: 25px 0 15px 0; text-align: center; background: white; padding: 12px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                Tactical Execution Plan
            </div>
            """, unsafe_allow_html=True)
            
            for metric, data in st.session_state.ai_recommendations.items():
                with st.expander(f"**{metric}**", expanded=False):
                    st.markdown(f"### Why This Matters")
                    st.markdown(data.get('importance', 'No data available'))
                    
                    st.markdown("### Recommended Actions")
                    for i, rec in enumerate(data.get('recommendations', [])):
                        st.markdown(f"{i+1}. {rec}")
                    
                    st.markdown("### Industry Examples")
                    for example in data.get('examples', []):
                        st.markdown(f"- {example}")
    
    # Media Affinity section
    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px; margin-top: 40px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 4H5C3.89 4 3 4.9 3 6V18C3 19.1 3.89 20 5 20H19C20.1 20 21 19.1 21 18V6C21 4.9 20.1 4 19 4ZM19 18H5V8H19V18ZM9 10H7V16H9V10ZM13 10H11V16H13V10ZM17 10H15V16H17V10Z" fill="#5865f2"/>
        </svg>
        Top Media Affinity Sites
    </h3>
    """, unsafe_allow_html=True)
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
    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 3H3C1.9 3 1 3.9 1 5V17C1 18.1 1.9 19 3 19H8V21H16V19H21C22.1 19 23 18.1 23 17V5C23 3.9 22.1 3 21 3ZM21 17H3V5H21V17Z" fill="#5865f2"/>
            <path d="M16 11L10 15V7L16 11Z" fill="#5865f2"/>
        </svg>
        Top TV Network Affinities
    </h3>
    """, unsafe_allow_html=True)
    
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
    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM10 16.5V7.5L16 12L10 16.5Z" fill="#5865f2"/>
        </svg>
        Top Streaming Platforms
    </h3>
    """, unsafe_allow_html=True)
    
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
    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="#5865f2"/>
            <path d="M9 10.5C9.83 10.5 10.5 9.83 10.5 9C10.5 8.17 9.83 7.5 9 7.5C8.17 7.5 7.5 8.17 7.5 9C7.5 9.83 8.17 10.5 9 10.5ZM15 10.5C15.83 10.5 16.5 9.83 16.5 9C16.5 8.17 15.83 7.5 15 7.5C14.17 7.5 13.5 8.17 13.5 9C13.5 9.83 14.17 10.5 15 10.5ZM12 17C14.33 17 16.33 15.67 17.25 13.75L15.5 12.92C14.92 14.17 13.58 15 12 15C10.42 15 9.08 14.17 8.5 12.92L6.75 13.75C7.67 15.67 9.67 17 12 17Z" fill="#5865f2"/>
        </svg>
        Psychographic Highlights
    </h3>
    """, unsafe_allow_html=True)
    st.markdown(PSYCHOGRAPHIC_HIGHLIGHTS, unsafe_allow_html=True)
    
    # Audience Summary
    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 11C17.66 11 18.99 9.66 18.99 8C18.99 6.34 17.66 5 16 5C14.34 5 13 6.34 13 8C13 9.66 14.34 11 16 11ZM8 11C9.66 11 10.99 9.66 10.99 8C10.99 6.34 9.66 5 8 5C6.34 5 5 6.34 5 8C5 9.66 6.34 11 8 11ZM8 13C5.67 13 1 14.17 1 16.5V19H15V16.5C15 14.17 10.33 13 8 13ZM16 13C15.71 13 15.38 13.02 15.03 13.05C16.19 13.89 17 15.02 17 16.5V19H23V16.5C23 14.17 18.33 13 16 13Z" fill="#5865f2"/>
        </svg>
        Audience Summary
    </h3>
    """, unsafe_allow_html=True)
    st.markdown(AUDIENCE_SUMMARY, unsafe_allow_html=True)
    
    # Next Steps
    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19.14 12.94C19.18 12.64 19.2 12.33 19.2 12C19.2 11.68 19.18 11.36 19.13 11.06L21.16 9.48C21.34 9.34 21.39 9.07 21.28 8.87L19.36 5.55C19.24 5.33 18.99 5.26 18.77 5.33L16.38 6.29C15.88 5.91 15.35 5.59 14.76 5.35L14.4 2.81C14.36 2.57 14.16 2.4 13.92 2.4H10.08C9.84 2.4 9.65 2.57 9.61 2.81L9.25 5.35C8.66 5.59 8.12 5.92 7.63 6.29L5.24 5.33C5.02 5.25 4.77 5.33 4.65 5.55L2.74 8.87C2.62 9.08 2.66 9.34 2.86 9.48L4.89 11.06C4.84 11.36 4.8 11.69 4.8 12C4.8 12.31 4.82 12.64 4.87 12.94L2.84 14.52C2.66 14.66 2.61 14.93 2.72 15.13L4.64 18.45C4.76 18.67 5.01 18.74 5.23 18.67L7.62 17.71C8.12 18.09 8.65 18.41 9.24 18.65L9.6 21.19C9.65 21.43 9.84 21.6 10.08 21.6H13.92C14.16 21.6 14.36 21.43 14.39 21.19L14.75 18.65C15.34 18.41 15.88 18.09 16.37 17.71L18.76 18.67C18.98 18.75 19.23 18.67 19.35 18.45L21.27 15.13C21.39 14.91 21.34 14.66 21.15 14.52L19.14 12.94ZM12 15.6C10.02 15.6 8.4 13.98 8.4 12C8.4 10.02 10.02 8.4 12 8.4C13.98 8.4 15.6 10.02 15.6 12C15.6 13.98 13.98 15.6 12 15.6Z" fill="#5865f2"/>
        </svg>
        What's Next?
    </h3>
    """, unsafe_allow_html=True)
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
        # Create a custom HTML link that looks like a button but opens an email client
        st.markdown("""
        <a href="mailto:crystal@digitalculture.group?subject=Schedule a Demo for ARI Analyzer&body=I would like to schedule a demo for the Audience Resonance Index Analyzer." 
           style="display: inline-block; padding: 0.5rem 1rem; font-weight: 600; text-align: center; 
                  background-color: #5865f2; color: white; text-decoration: none; 
                  border-radius: 0.25rem; cursor: pointer; margin: 0.5rem 0;">
            Schedule a Demo
        </a>
        """, unsafe_allow_html=True)

def display_summary_metrics(scores):
    """
    Display a summary of key metrics using a radar chart visualization.
    
    Args:
        scores (dict): Dictionary of metric scores
    """
    # Create a summary section header
    st.markdown('<div style="text-align: center;"><h4>Key Performance Metrics Summary</h4></div>', unsafe_allow_html=True)
    
    # Calculate average scores
    avg_score = sum(scores.values()) / len(scores)
    
    # Create columns for the visualizations
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Create a radar chart
        categories = list(scores.keys())
        values = list(scores.values())
        
        # Add the first value at the end to close the loop
        categories.append(categories[0])
        values.append(values[0])
        
        # Create the radar chart using plotly
        fig = go.Figure()
        
        # Add radar chart trace
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(88, 101, 242, 0.3)',
            line=dict(color='#5865f2', width=2),
            name='Campaign Scores'
        ))
        
        # Add "AI Insight" reference trace
        # This is a simulated perfect score for comparison
        ai_reference = [9.0] * len(scores)
        ai_reference.append(ai_reference[0])  # Close the loop
        
        fig.add_trace(go.Scatterpolar(
            r=ai_reference,
            theta=categories,
            fill='toself',
            fillcolor='rgba(16, 185, 129, 0.1)',
            line=dict(color='#10b981', width=1.5, dash='dot'),
            name='AI Insights'
        ))
        
        # Update layout with custom styling
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    tickfont=dict(size=9),
                    tickvals=[2, 4, 6, 8, 10],
                    gridcolor="rgba(0,0,0,0.1)",
                ),
                angularaxis=dict(
                    tickfont=dict(size=10, color="#444"),
                    gridcolor="rgba(0,0,0,0.1)",
                )
            ),
            showlegend=True,
            legend=dict(
                x=0.85,
                y=1.2,
                orientation='h',
                font=dict(size=10)
            ),
            margin=dict(l=80, r=80, t=20, b=80),
            height=450,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Display the average score in a prominent way
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 20px; margin: 20px 0; text-align: center;">
            <div style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2;">Overall Campaign Score</div>
            <div style="font-size: 3rem; font-weight: 700; color: #5865f2; margin: 10px 0;">{avg_score:.1f}<span style="font-size: 1.5rem; color: #777;">/10</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display AI insights
        st.markdown("""
        <div style="background: #f0fdf9; border-radius: 8px; border-left: 4px solid #10b981; padding: 15px; margin-top: 20px;">
            <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #10b981; margin-bottom: 5px;">AI Insight</div>
            <p style="margin: 0; font-size: 0.9rem; color: #333;">
                The campaign shows strong cultural relevance but could benefit from enhanced platform-specific optimizations and better audience representation strategies.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()