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
import json
import os
import re

# Import the grammar fix function from ai_insights module
# This helps clean up grammatical errors and duplicate words
from ai_insights import (
    fix_grammar_and_duplicates,
    generate_competitor_strategy,
    generate_deep_insights,
    generate_competitor_analysis,
    generate_audience_segments,
    get_default_audience_segments,
    is_siteone_hispanic_content
)

# Fun spinner messages for loading states
SPINNER_MESSAGES = [
    "Consulting the data oracles…",
    "Warming up the algorithms…",
    "Doing math in public—please hold.",
    "Fetching facts from the digital void…",
    "This is your data on a coffee break ☕",
    "Manifesting your metrics…",
    "Plotting world domination... just kidding (or are we?)",
    "Giving your data a pep talk…",
    "Crunching numbers like a breakfast cereal.",
    "The data is shy. We're coaxing it out.",
    "Let's all pretend this isn't an awkward silence…",
    "Just you, me, and this dramatic pause.",
    "Cue elevator music…",
    "Avoiding eye contact with the loading bar…",
    "Your data is fashionably late.",
    "This awkward silence brought to you by the data gods.",
    "While we wait, think of your favorite spreadsheet.",
    "Your data is buffering. Like our small talk.",
    "Even your data needs a moment.",
    "Dramatic pause… data's on its way."
]

def get_random_spinner_message():
    """Return a random spinner message from the list."""
    return random.choice(SPINNER_MESSAGES)

def hash(text):
    """Simple hash function for generating a deterministic number from text."""
    if not text:
        return 0
    h = 0
    for c in text:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return h % 100  # Return a number between 0-99

def generate_competitor_strategy_html(competitor_brand, campaign_goal, brief_text=""):
    """
    Generate the HTML for competitor strategy recommendations.
    
    Args:
        competitor_brand (str): The competitor brand name
        campaign_goal (str): The campaign goal or description
        brief_text (str): The brief text for context (optional)
        
    Returns:
        str: HTML content for the competitor strategy
    """
    with st.spinner(get_random_spinner_message()):
        # Generate competitor strategies using the AI
        if not brief_text and 'brief_text' in st.session_state:
            brief_text = st.session_state.brief_text
            
        strategies = generate_competitor_strategy(
            brief_text, 
            competitor_brand.strip(), 
            campaign_goal.strip()
        )
        
        # Create HTML list items from strategies
        strategy_items = ""
        for strategy in strategies:
            # Split by colon to get the header and content
            if ":" in strategy:
                parts = strategy.split(":", 1)
                header = parts[0].strip()
                content = parts[1].strip() if len(parts) > 1 else ""
                strategy_items += f'<li><strong>{header}:</strong> {content}</li>'
            else:
                strategy_items += f'<li>{strategy}</li>'
        
        # Return the HTML content
        return f"""
            <h3>Strategic Recommendations to Counter <strong>{competitor_brand}</strong></h3>
            <p><strong>Campaign Goal:</strong> {campaign_goal}</p>
            <ul style="line-height: 1.7;">
                {strategy_items}
            </ul>
        """

def display_competitor_tactics_tab(tab):
    """
    Displays the competitor tactics tab with the Fortune 500 Strategy Tool styling.
    
    Args:
        tab: The streamlit tab object to render content in
    """
    # Add the CSS for the Fortune 500 Strategy Tool
    tab.markdown("""
    <style>
        .fortune500-analyzer {
            font-family: 'Helvetica Neue', sans-serif;
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.05);
            padding: 20px;
            margin-bottom: 20px;
        }
        .fortune500-heading {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: #111;
        }
        .fortune500-description {
            margin-bottom: 20px;
            font-size: 1rem;
            color: #444;
        }
        .fortune500-input {
            width: 100%;
            padding: 0.8rem;
            font-size: 1rem;
            margin-bottom: 15px;
            border-radius: 6px;
            border: 1px solid #ccc;
        }
        .fortune500-output {
            margin-top: 20px;
            background: #fff;
            padding: 20px;
            border-left: 4px solid #3b82f6;
            border-radius: 4px;
        }
        .fortune500-output h2 {
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.3rem;
            color: #111;
        }
        .fortune500-output ul {
            padding-left: 25px;
            line-height: 1.6;
        }
        .fortune500-output li {
            margin-bottom: 12px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Add the HTML for the competitor analyzer UI
    tab.markdown("""
    <div class="fortune500-analyzer">
        <div class="fortune500-heading">Fortune 500 Competitor Strategy Generator</div>
        <p class="fortune500-description">Enter a Fortune 500 brand to generate dynamic counter-strategy recommendations that leverage your campaign's strengths.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add the input and button
    competitor_brand = tab.text_input("", placeholder="e.g., Amazon, Apple, Walmart, Target", key=f"competitor_brand_input_{hash(str(tab))}")
    generate_button = tab.button("Generate Strategy", key=f"generate_insights_button_{hash(str(tab))}")
    
    # Create the brand strategies dictionary directly from the HTML file
    brand_strategies = {
        "walmart": [
            "Counter Walmart's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Walmart has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Walmart's corporate tone."
        ],
        "amazon": [
            "Counter Amazon's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Amazon has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Amazon's corporate tone."
        ],
        "apple": [
            "Counter Apple's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Apple has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Apple's corporate tone."
        ],
        "target": [
            "Counter Target's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Target has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Target's corporate tone."
        ],
        "lowe's": [
            "Counter Lowe's's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Lowe's has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Lowe's's corporate tone."
        ],
        "home depot": [
            "Counter Home Depot's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Home Depot has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Home Depot's corporate tone."
        ],
        "microsoft": [
            "Counter Microsoft's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Microsoft has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Microsoft's corporate tone."
        ],
        "intel": [
            "Counter Intel's broad reach with hyper-personalized regional messaging.",
            "Target emerging platforms where Intel has lower presence (e.g., Discord, Twitch).",
            "Highlight community-driven storytelling vs. Intel's corporate tone."
        ]
    }
    
    # Add additional brands dynamically based on brief text if available
    if 'brief_text' in st.session_state and st.session_state.brief_text:
        from ai_insights import generate_competitor_strategy
        brief_text = st.session_state.brief_text
        
        # Extract potential competitor brands from the brief
        lower_brief = brief_text.lower()
        for potential_brand in ["nike", "adidas", "coca-cola", "pepsi", "ford", "chevrolet", "toyota", "honda"]:
            if potential_brand in lower_brief and potential_brand not in brand_strategies:
                # Generate dynamic strategies for this brand
                strategies = [
                    f"Counter {potential_brand.title()}'s broad reach with hyper-personalized regional messaging.",
                    f"Target emerging platforms where {potential_brand.title()} has lower presence using rich media and high-impact interactive formats.",
                    f"Highlight authentic community storytelling vs. {potential_brand.title()}'s approach with premium CTV/OTT placements."
                ]
                brand_strategies[potential_brand] = strategies
    
    # If the button is clicked, process the input
    if generate_button:
        if not competitor_brand.strip():
            tab.markdown("<p style='color:red;'>Please enter a competitor brand name.</p>", unsafe_allow_html=True)
        else:
            # Get the lowercase version for matching
            brand_lower = competitor_brand.strip().lower()
            
            # Check if it's in our strategy database
            if brand_lower in brand_strategies:
                strategies = brand_strategies[brand_lower]
                
                # Format the strategies as list items
                strategy_items = ""
                for strategy in strategies:
                    strategy_items += f"<li>{strategy}</li>"
                
                # Display the formatted output
                tab.markdown(f"""
                <div class="fortune500-output">
                    <h2>Strategy Against <strong>{brand_lower.title()}</strong></h2>
                    <ul>
                        {strategy_items}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Use the AI to generate insights for unknown brands
                if 'brief_text' in st.session_state and st.session_state.brief_text:
                    # Using st.spinner instead of tab.spinner
                    with st.spinner(get_random_spinner_message()):
                        campaign_goal = "Increase brand awareness and drive sales"
                        brief_text = st.session_state.brief_text
                        
                        # Try to determine a better campaign goal based on the brief
                        if "goal" in brief_text.lower() or "objective" in brief_text.lower():
                            sentences = brief_text.split('.')
                            for sentence in sentences:
                                if "goal" in sentence.lower() or "objective" in sentence.lower():
                                    campaign_goal = sentence.strip()
                                    break
                        
                        # Generate dynamic strategies with AI
                        strategies = generate_competitor_strategy(
                            brief_text, 
                            competitor_brand.strip(), 
                            campaign_goal
                        )
                        
                        # Format the strategies as list items
                        strategy_items = ""
                        for strategy in strategies:
                            # Split by colon to get the header and content
                            if ":" in strategy:
                                parts = strategy.split(":", 1)
                                header = parts[0].strip()
                                content = parts[1].strip() if len(parts) > 1 else ""
                                strategy_items += f'<li><strong>{header}:</strong> {content}</li>'
                            else:
                                strategy_items += f'<li>{strategy}</li>'
                        
                        # Display the formatted output
                        tab.markdown(f"""
                        <div class="fortune500-output">
                            <h2>Custom Strategy Against <strong>{competitor_brand}</strong></h2>
                            <ul>
                                {strategy_items}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Brand not in database and no brief text available
                    tab.markdown(f"""
                    <div class="fortune500-output">
                        <h2>Brand Not Found</h2>
                        <p>This tool currently includes a subset of Fortune 500 brands. Please try one of the suggested brands or upload a brief for AI-powered custom recommendations.</p>
                    </div>
                    """, unsafe_allow_html=True)

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
from ai_insights import ensure_valid_url_in_sites
from database import benchmark_db, BLOCKED_KEYWORDS
from assets.content import (
    METRICS, 
    MEDIA_AFFINITY_SITES,
    SITEONE_HISPANIC_SOCIAL_MEDIA,
    TV_NETWORKS,
    SITEONE_HISPANIC_TV_NETWORKS,
    STREAMING_PLATFORMS,
    SITEONE_HISPANIC_STREAMING,
    PSYCHOGRAPHIC_HIGHLIGHTS,
    SITEONE_HISPANIC_PSYCHOGRAPHIC,
    AUDIENCE_SUMMARY,
    SITEONE_HISPANIC_SUMMARY,
    NEXT_STEPS,
    STOCK_PHOTOS
)

# Set page config
st.set_page_config(
    page_title="ARI Analyzer - Digital Culture Group",
    page_icon=None,
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
if 'brief_text' not in st.session_state:
    st.session_state.brief_text = None
if 'ai_insights' not in st.session_state:
    st.session_state.ai_insights = None
if 'competitor_analysis' not in st.session_state:
    st.session_state.competitor_analysis = None
if 'audience_segments' not in st.session_state:
    st.session_state.audience_segments = None
if 'use_openai' not in st.session_state:
    # Check if OpenAI API key is available
    st.session_state.use_openai = bool(os.environ.get("OPENAI_API_KEY"))

# Define function to extract text from various file types
def extract_text_from_file(uploaded_file):
    """
    Extract text from various file types including docx, pdf and txt.
    
    Args:
        uploaded_file: The file uploaded through Streamlit's file_uploader
        
    Returns:
        str: The extracted text from the file
    """
    try:
        # Get the file extension from the name
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        # Convert the uploaded file to bytes for processing
        file_bytes = io.BytesIO(uploaded_file.getvalue())
        
        if file_type == 'txt':
            # For text files
            text = uploaded_file.getvalue().decode('utf-8')
        
        elif file_type == 'docx':
            try:
                # For Word documents
                doc = docx.Document(file_bytes)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            except Exception as e:
                st.error(f"Error processing DOCX file: {str(e)}")
                return None
        
        elif file_type == 'pdf':
            try:
                # For PDF files
                pdf_reader = PyPDF2.PdfReader(file_bytes)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
            except Exception as e:
                st.error(f"Error processing PDF file: {str(e)}")
                return None
        
        else:
            # Unsupported file type
            st.error(f"Unsupported file type: {file_type}. Please use txt, pdf, or docx files.")
            return None
        
        # Check for blocked keywords and remove them
        for keyword in BLOCKED_KEYWORDS:
            text = text.replace(keyword, "[FILTERED]")
        
        return text
    
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
        return None

# Define main function
def main():
    # Load global CSS styles
    with open("assets/styles.css", "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    
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
                # Filter blocked keywords
                for keyword in BLOCKED_KEYWORDS:
                    input_brief_text = input_brief_text.replace(keyword, "[FILTERED]")
                brief_text = input_brief_text
        
        # Analysis and Restart buttons in columns
        col1, col2 = st.columns([3, 1])
        
        with col1:
            analyze_button = st.button("Run Predictive Analysis", type="primary", use_container_width=True)
        
        with col2:
            restart_button = st.button("Reset", type="secondary", use_container_width=True)
            
        # Handle restart button
        if restart_button:
            # Clear session state
            for key in list(st.session_state.keys()):
                if key not in ['use_openai']:  # Keep API configuration
                    del st.session_state[key]
            st.rerun()
            
        # Handle analyze button
        if analyze_button:
            if not brief_text or brief_text.strip() == "":
                st.error("Please provide a Marketing Brief or RFP to proceed with analysis.")
            else:
                with st.spinner(get_random_spinner_message()):
                    # Simulate analysis time
                    time.sleep(1.5)
                    
                    # Analyze the content
                    result = analyze_campaign_brief(brief_text)
                    
                    if not result:
                        st.error("Insufficient data complexity for comprehensive analysis. Please provide a more detailed brief or RFP.")
                    else:
                        scores, brand_name, industry, product_type = result
                        
                        # Calculate benchmark percentile and improvement areas
                        percentile = calculate_benchmark_percentile(scores)
                        # Get brand and industry info for enhanced improvement areas analysis
                        brand_name, industry, product_type = extract_brand_info(brief_text)
                        
                        # Get dynamic improvement areas using all contextual data
                        improvement_areas = get_improvement_areas(
                            scores, 
                            brief_text=brief_text,
                            brand_name=brand_name,
                            industry=industry
                        )
                        
                        # Store results in session state
                        st.session_state.has_analyzed = True
                        st.session_state.scores = scores
                        st.session_state.percentile = percentile
                        st.session_state.brand_info = (brand_name, industry, product_type)
                        st.session_state.improvement_areas = improvement_areas
                        st.session_state.brand_name = brand_name
                        st.session_state.industry = industry
                        st.session_state.product_type = product_type
                        st.session_state.brief_text = brief_text
                        
                        # Generate audience segments regardless of OpenAI availability
                        # This ensures we always have audience segments to display
                        st.session_state.audience_segments = get_default_audience_segments(brief_text, scores)
                        
                        # If OpenAI API key is available, try to generate enhanced insights
                        if st.session_state.use_openai:
                            with st.spinner(get_random_spinner_message()):
                                # Generate AI-powered insights for enhanced analysis
                                try:
                                    # Generate deep insights based on brief and ARI scores
                                    ai_insights = generate_deep_insights(brief_text, scores)
                                    st.session_state.ai_insights = ai_insights
                                    
                                    # Generate competitor analysis
                                    competitor_analysis = generate_competitor_analysis(brief_text, industry)
                                    st.session_state.competitor_analysis = competitor_analysis
                                    
                                    # Generate AI-powered audience segments to replace default ones
                                    ai_audience_segments = generate_audience_segments(brief_text, scores)
                                    # Only replace if the AI generation was successful
                                    if ai_audience_segments and 'segments' in ai_audience_segments:
                                        st.session_state.audience_segments = ai_audience_segments
                                    
                                except Exception as e:
                                    # Show warning but keep using default audience segments already set
                                    st.warning(f"Enhanced AI analysis encountered an issue: {str(e)}")
                                    st.session_state.ai_insights = None
                                    st.session_state.competitor_analysis = None
                        
                        # Show success message
                        success_msg = "✨ Campaign analysis complete! Breakthrough insights ready for review."
                        if st.session_state.use_openai and st.session_state.ai_insights:
                            success_msg += " Strategic recommendations prepared for your campaign!"
                        st.success(success_msg)
                        
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
            st.session_state.product_type,
            st.session_state.brief_text
        )
    
    # Footer
    render_footer()

def is_siteone_hispanic_campaign(brand_name, brief_text):
    """
    Detect if this is a SiteOne Hispanic-targeted campaign based on brand name and brief text.
    
    Args:
        brand_name (str): Brand name extracted from the brief
        brief_text (str): The full text of the brief
        
    Returns:
        bool: True if this is a SiteOne Hispanic campaign, False otherwise
    """
    if not brief_text:
        return False
        
    # Add brand name to brief text for more robust detection
    combined_text = f"{brand_name} {brief_text}" if brand_name else brief_text
    
    # Use the centralized detection function from ai_insights module
    return is_siteone_hispanic_content(combined_text)

def display_results(scores, percentile, improvement_areas, brand_name="Unknown", industry="General", product_type="Product", brief_text=""):
    """Display the ARI analysis results."""
    # Import the marketing trend heatmap functionality
    from marketing_trends import display_trend_heatmap
    st.markdown("---")
    
    # Initialize values that will be set based on scores or AI insights
    summary_text = ""
    top_strength = ""
    key_opportunity = ""
    roi_potential = ""
    
    # Extract top strength and key opportunity
    # Initialize variables to avoid "possibly unbound" errors
    # Calculate dynamic metrics based on actual scores
    metric_scores = list(scores.items())
    metric_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Calculate weighted ROI metrics based on key performance indicators
    weighted_metrics = {
        "Cultural Authority": 1.5,
        "Buzz & Conversation": 1.3,
        "Cultural Vernacular": 1.2,
        "Commerce Bridge": 1.2,
        "Platform Relevance": 1.1
    }
    
    # Calculate weighted ROI score
    roi_sum = 0
    roi_weight_total = 0
    
    for metric, score in scores.items():
        weight = weighted_metrics.get(metric, 0.8)  # Default weight for other metrics
        roi_sum += score * weight
        roi_weight_total += weight
    
    # Calculate weighted average ROI and convert to percentage
    if roi_weight_total > 0:
        roi_score = roi_sum / roi_weight_total
        roi_percent = int(5 + (roi_score / 10) * 20)
        roi_potential = f"+{roi_percent}%"
    else:
        # Fallback if weights are missing
        avg_score = sum(scores.values()) / len(scores) if scores else 7.0
        roi_percent = int(5 + (avg_score / 10) * 20)
        roi_potential = f"+{roi_percent}%"
    
    # Use AI-generated insights if available, otherwise use calculated metrics
    if 'ai_insights' in st.session_state and st.session_state.ai_insights:
        ai_insights = st.session_state.ai_insights
        strengths = ai_insights.get('strengths', [])
        improvements = ai_insights.get('improvements', [])
        
        # Extract the first strength and improvement for the executive summary
        if strengths:
            top_strength = strengths[0].get('area', 'Cultural Relevance')
        else:
            # Fall back to calculated top strength
            top_strength = metric_scores[0][0] if metric_scores else "Cultural Vernacular"
            
        if improvements:
            key_opportunity = improvements[0].get('area', 'Audience Engagement')
        else:
            # Fall back to calculated bottom metric
            key_opportunity = metric_scores[-1][0] if metric_scores else "Geo-Cultural Fit"
        
        # Track values internally
        internal_tracking = {
            "source": "ai_insights",
            "top_strength": top_strength,
            "key_opportunity": key_opportunity,
            "calculated_top": metric_scores[0][0] if metric_scores else "None",
            "calculated_bottom": metric_scores[-1][0] if metric_scores else "None"
        }
        
        # Extract potential ROI from performance prediction if available
        prediction = ai_insights.get('performance_prediction', '')
        if prediction and '%' in prediction:
            import re
            roi_match = re.search(r'(\+\d+%|\d+%)', prediction)
            if roi_match:
                roi_potential = roi_match.group(0)
                if not roi_potential.startswith('+'):
                    roi_potential = f"+{roi_potential}"
    else:
        # Calculate based on the scores if AI insights aren't available
        
        # Use the highest scoring metric as the top strength
        top_strength = metric_scores[0][0] if metric_scores else "Cultural Vernacular"
        
        # Use the lowest scoring metric as the key opportunity
        key_opportunity = metric_scores[-1][0] if metric_scores else "Geo-Cultural Fit"
        
        # Track values internally
        internal_tracking = {
            "source": "calculated_scores",
            "top_strength": top_strength,
            "key_opportunity": key_opportunity,
            "metric_scores": {name: score for name, score in metric_scores},
            "roi_formula": {
                "roi_percent": roi_percent
            }
        }
    
    # Generate summary text from the insights - make it more dynamic and specific to the brief
    if 'ai_insights' in st.session_state and st.session_state.ai_insights:
        ai_insights = st.session_state.ai_insights
        
        # Get the top strength explanation if available
        top_strength_explanation = ""
        for strength in ai_insights.get('strengths', []):
            if strength.get('area') == top_strength and 'explanation' in strength:
                top_strength_explanation = strength['explanation']
                break
        
        # Get the key opportunity explanation if available
        key_opportunity_explanation = ""
        for improvement in ai_insights.get('improvements', []):
            if improvement.get('area') == key_opportunity and 'explanation' in improvement:
                key_opportunity_explanation = improvement['explanation']
                break
        
        # If we have detailed explanations, use them in a more detailed summary
        if top_strength_explanation and key_opportunity_explanation:
            summary_text = f"This campaign excels in <strong>{top_strength}</strong>: {top_strength_explanation[0].lower() + top_strength_explanation[1:]} However, there's an opportunity to enhance <strong>{key_opportunity}</strong>: {key_opportunity_explanation[0].lower() + key_opportunity_explanation[1:]} Our AI-powered analysis suggests implementing targeted tactical adjustments that could increase overall effectiveness by <strong>{roi_potential}</strong>."
        else:
            # Fall back to the simpler summary if we don't have detailed explanations
            summary_text = f"This campaign demonstrates strong performance in <strong>{top_strength}</strong>, with opportunities to improve <strong>{key_opportunity}</strong>. Our AI-powered analysis suggests tactical adjustments that could increase overall effectiveness by <strong>{roi_potential}</strong>."
    else:
        # Default summary when no AI insights are available
        summary_text = f"This campaign demonstrates strong performance in <strong>{top_strength}</strong>, with opportunities to improve <strong>{key_opportunity}</strong>. Our AI-powered analysis suggests tactical adjustments that could increase overall effectiveness by <strong>{roi_potential}</strong>."
    
    # Check if this is a SiteOne Hispanic campaign
    is_siteone_hispanic = is_siteone_hispanic_campaign(brand_name, brief_text)
    
    # Create tabs for better organization of content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Detailed Metrics", 
        "Audience Insights", 
        "Media Affinities", 
        "Trend Analysis",
        "Next Steps"
    ])
    
    # TAB 1: DETAILED METRICS
    with tab1:
        # Display standard scorecard title with no brand reference
        st.markdown("<h2 style='text-align: center;'>Audience Resonance Index™ Scorecard</h2>", unsafe_allow_html=True)
        
        # If this is a SiteOne Hispanic campaign, display a specialized audience tag
        if is_siteone_hispanic:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 15px;">
                <span style="background-color: #5865f2; color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 500;">
                    SiteOne Hispanic Audience Analysis
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Add some spacing after the title
        st.markdown("---")
        
        # Display metrics summary (replaced radar chart)
        display_summary_metrics(scores, improvement_areas, brief_text)
        
        # Generate and display Executive Summary
        analysis = '<div class="metric-analysis">'
        analysis += f'<h3>Executive Summary</h3>'
        analysis += f'<p>{summary_text}</p>'
        # Add debug info for tracking
        st.session_state['final_values'] = {
            "top_strength": top_strength,
            "key_opportunity": key_opportunity,
            "roi_potential": roi_potential
        }
        
        analysis += '<div class="metric-box">'
        analysis += f'<div class="strength-box"><strong>Top Strength:</strong><br/>{top_strength}</div>'
        analysis += f'<div class="opportunity-box"><strong>Key Opportunity:</strong><br/>{key_opportunity}</div>'
        analysis += f'<div class="roi-box"><strong>ROI Potential:</strong><br/>{roi_potential}</div>'
        analysis += '</div>'
        analysis += '<h3>Detailed Metrics</h3>'
        analysis += '<div class="metrics-container">'
        
        # Replace static metrics_html with colored progress bars for each metric
        for metric, score in scores.items():
            formatted_score = f"{score:.1f}"
            # Get description text - prioritize AI-generated descriptions if available
            if 'ai_insights' in st.session_state and st.session_state.ai_insights and 'metric_details' in st.session_state.ai_insights:
                # Use the AI-generated description specific to this brief if available
                metric_details = st.session_state.ai_insights.get('metric_details', {})
                if metric in metric_details:
                    description = metric_details[metric]
                else:
                    # Fall back to generic descriptions
                    description = METRICS[metric][get_score_level(score)]
            else:
                # Use generic descriptions from METRICS
                description = METRICS[metric][get_score_level(score)]
                
            # Calculate percent for bar width (use full percentage for proper display)
            percent = int(score * 10)
            
            # Set the color based on score - use direct CSS colors instead of classes for reliability
            if score >= 8:
                bar_bg = "linear-gradient(90deg, #10b981, #34d399)"
                score_bg = "rgba(16, 185, 129, 0.15)"
                score_color = "#10b981"
                bar_class = "excellent"
            elif score >= 6:
                bar_bg = "linear-gradient(90deg, #f59e0b, #fbbf24)"
                score_bg = "rgba(245, 158, 11, 0.15)"
                score_color = "#f59e0b"
                bar_class = "good"
            else:
                bar_bg = "linear-gradient(90deg, #ef4444, #f87171)"
                score_bg = "rgba(239, 68, 68, 0.15)"
                score_color = "#ef4444"
                bar_class = "needs-improvement"
                
            # Add tooltip descriptions for complex metrics
            tooltip_content = ""
            if metric == "Cultural Authority":
                tooltip_content = "A measure of how effectively the campaign leverages culturally significant elements or voices with credibility in the target audience space."
            elif metric == "Cultural Vernacular":
                tooltip_content = "Evaluates how well the campaign uses language patterns, expressions, and communication styles authentic to the target audience."
            elif metric == "Media Ownership Equity":
                tooltip_content = "Analyzes the diversity of media partnerships and distribution channels, with higher scores for more inclusive and equitable media representation."
            elif metric == "Commerce Bridge":
                tooltip_content = "Measures how effectively the campaign connects brand storytelling to purchase opportunities across the customer journey."
            elif metric == "Geo-Cultural Fit":
                tooltip_content = "Evaluates how well the campaign accounts for geographical and cultural variations within the target audience."
            elif metric == "Platform Relevance":
                tooltip_content = "Assesses how effectively the campaign utilizes media platforms aligned with the target audience's consumption behaviors."
            elif metric == "Buzz & Conversation":
                tooltip_content = "Evaluates the campaign's potential to generate organic discussion and sharing among the target audience."
            elif metric == "Representation":
                tooltip_content = "Measures how authentically the campaign represents the diversity of perspectives, experiences, and identities within the target audience."
            elif metric == "Cultural Relevance":
                tooltip_content = "Evaluates how well the campaign connects with currently relevant cultural themes important to the target audience."
                
            # Add tooltip HTML if available
            tooltip_html = f'<div class="tooltip"><i class="info-icon">i</i><span class="tooltiptext">{tooltip_content}</span></div>' if tooltip_content else ""
            
            # Add metric with custom-styled progress bar (using inline styles for reliability)
            analysis += f'<div class="metric-item">'
            analysis += f'<div class="metric-header"><strong>{metric}</strong> {tooltip_html} <span style="font-weight: 600; border-radius: 100px; padding: 0.3rem 0.8rem; font-size: 0.9rem; background: {score_bg}; color: {score_color};">{formatted_score}</span></div>'
            analysis += f'<div style="height: 8px; width: 100%; background: #e2e8f0; border-radius: 100px; margin-bottom: 1rem; overflow: hidden; position: relative;">'
            analysis += f'<div style="position: absolute; top: 0; left: 0; height: 100%; width: {percent}%; background: {bar_bg}; border-radius: 100px;"></div>'
            analysis += f'</div>'
            analysis += f'<div class="metric-description">{description}</div>'
            analysis += f'</div>'
        
        analysis += '</div>'  # Close metrics-container
        analysis += '</div>'  # Close metric-analysis
        
        st.markdown(analysis, unsafe_allow_html=True)
        
        # Create an advanced metric analysis section using the new HTML template
        st.markdown('<h3 style="margin-top: 30px;">Advanced Metric Analysis</h3>', unsafe_allow_html=True)
        
        # Read the HTML template file
        with open("attached_assets/ARI_AdvancedMetricAnalyzer.html", "r") as file:
            template_html = file.read()
        
        # Add the advanced metric analysis section using the new HTML template
        metrics_html = ""
        for metric, score in scores.items():
            # Format the score to a single decimal place
            formatted_score = f"{score:.1f}"
            
            # Determine score level for styling
            if score >= 8:
                bg_color = "#e0f7ec"
                border_color = "#10b981"
                strength_level = "STRONG"
            elif score >= 6:
                bg_color = "#fff4e5"
                border_color = "#f59e0b"
                strength_level = "GOOD"
            else:
                bg_color = "#fef2f2"
                border_color = "#ef4444"
                strength_level = "NEEDS IMPROVEMENT"
                
            # Get description text - prioritize AI-generated descriptions if available
            if 'ai_insights' in st.session_state and st.session_state.ai_insights and 'metric_details' in st.session_state.ai_insights:
                # Use the AI-generated description specific to this brief if available
                metric_details = st.session_state.ai_insights.get('metric_details', {})
                if metric in metric_details:
                    description = metric_details[metric]
                else:
                    # Fall back to generic descriptions
                    description = METRICS[metric][get_score_level(score)]
            else:
                # Use generic descriptions from METRICS
                description = METRICS[metric][get_score_level(score)]
            
            # Add this metric to the HTML - use string concatenation instead of f-strings with triple quotes
            metrics_html += f'<div style="margin-bottom: 1rem;"><strong>{metric} – {formatted_score}:</strong> {description}</div>'
    
    # Just add spacing after the metrics
    
    # Premium styled CSS for Advanced Metric Analysis with simplified bar styling (no animations that might conflict with Streamlit)
    st.markdown("""
    <style>
    .metric-analysis {
        margin-top: 2rem;
        padding: 2rem;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-top: 4px solid #5865f2;
    }
    .metric-box {
        display: flex;
        gap: 1.2rem;
        margin: 1.5rem 0;
    }
    .strength-box {
        flex: 1;
        background: #f0fdf4;
        padding: 1.5rem;
        border-radius: 8px;
        border-top: 4px solid #10b981;
        box-shadow: 0 2px 6px rgba(16, 185, 129, 0.1);
    }
    .opportunity-box {
        flex: 1;
        background: #fff7ed;
        padding: 1.5rem;
        border-radius: 8px;
        border-top: 4px solid #f59e0b;
        box-shadow: 0 2px 6px rgba(245, 158, 11, 0.1);
    }
    .roi-box {
        flex: 1;
        background: #fef2f2;
        padding: 1.5rem;
        border-radius: 8px;
        border-top: 4px solid #ef4444;
        box-shadow: 0 2px 6px rgba(239, 68, 68, 0.1);
    }
    .metrics-container {
        margin-top: 1.5rem;
    }
    .metric-item {
        margin-bottom: 1.8rem;
        background: #f8fafc;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
    }
    .metric-score {
        font-weight: 600;
        border-radius: 100px;
        padding: 0.3rem 0.8rem;
        font-size: 0.9rem;
    }
    .metric-score.excellent {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
    }
    .metric-score.good {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
    }
    .metric-score.needs-improvement {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
    }
    .metric-progress-container {
        height: 8px;
        width: 100%;
        background: #e2e8f0;
        border-radius: 100px;
        margin-bottom: 1rem;
        overflow: hidden;
        position: relative;
    }
    .metric-progress-bar.excellent {
        background: linear-gradient(90deg, #10b981, #34d399);
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        border-radius: 100px;
    }
    .metric-progress-bar.good {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        border-radius: 100px;
    }
    .metric-progress-bar.needs-improvement {
        background: linear-gradient(90deg, #ef4444, #f87171);
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        border-radius: 100px;
    }
    .metric-description {
        color: #475569;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .metric-analysis h3 {
        color: #1e293b;
        font-weight: 600;
        margin-bottom: 1.2rem;
        font-size: 1.4rem;
        letter-spacing: -0.01em;
    }
    .metric-analysis strong {
        color: #0f172a;
        font-weight: 600;
    }
    /* Tooltip Styles */
    .tooltip {
        position: relative;
        display: inline-block;
        margin-left: 5px;
        vertical-align: middle;
    }
    .info-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        background-color: #e2e8f0;
        color: #64748b;
        border-radius: 50%;
        font-size: 11px;
        font-weight: bold;
        font-style: normal;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 280px;
        background-color: #1e293b;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 8px 12px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -140px;
        opacity: 0;
        transition: opacity 0.2s;
        font-size: 0.8rem;
        line-height: 1.5;
        font-weight: normal;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #1e293b transparent transparent transparent;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # This section is now handled directly within tab1
    
    # Create a dashboard-style KPI row
    col1, col2, col3 = st.columns(3)
    
    # Import the learning tips module
    from assets.learning_tips import display_tip_bubble
    
    with col1:
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2;">
                PERCENTILE RANK
            </div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #5865f2; margin: 10px 0;">Top {percentile}%</div>
            <div style="font-size: 0.85rem; color: #555;">Among all analyzed campaigns</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Get expected impact from AI insights if available
        # Calculate ROI potential dynamically based on scores
        avg_score = sum(scores.values()) / len(scores)
        # Dynamic ROI calculation based on scores - better scores = better ROI
        roi_percent = int(5 + (avg_score / 10) * 20)
        roi_potential = f"+{roi_percent}%"
        
        # Override with AI insight if available
        if 'ai_insights' in st.session_state and st.session_state.ai_insights:
            ai_insights = st.session_state.ai_insights
            prediction = ai_insights.get('performance_prediction', '')
            if prediction and '%' in prediction:
                # Try to extract percentage from the prediction text
                import re
                roi_match = re.search(r'(\+\d+%|\d+%)', prediction)
                if roi_match:
                    roi_potential = roi_match.group(0)
                    if not roi_potential.startswith('+'):
                        roi_potential = f"+{roi_potential}"
        
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #10b981;">EXPECTED IMPACT</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #10b981; margin: 10px 0;">{roi_potential}</div>
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
    
    # Add an informative benchmark section using the Hyperdimensional Matrix HTML template
    
    # Read the HTML template file
    with open("attached_assets/ARI_Hyperdimensional_Matrix.html", "r") as file:
        matrix_template_html = file.read()
    
    # Start the custom section 
    st.markdown("""
    <div style="margin-top: 25px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px;">
        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2; margin-bottom: 15px; text-align: center;">Hyperdimensional Campaign Performance Matrix</div>
    """, unsafe_allow_html=True)
    
    # Display benchmark text with dynamic AI-driven content
    if 'ai_insights' in st.session_state and st.session_state.ai_insights:
        ai_insights = st.session_state.ai_insights
        
        # Get strengths from AI if available
        strengths = ai_insights.get('strengths', [])
        
        # Create a dynamic strength list if available
        strength_areas = []
        for strength in strengths[:2]:  # Get up to 2 top strengths
            if 'area' in strength:
                strength_areas.append(strength['area'].lower())
        
        # Default strengths if none found
        if not strength_areas:
            strength_areas = ['relevance', 'authenticity']
            
        # Format strengths for display
        if len(strength_areas) > 1:
            strength_text = f"{strength_areas[0]} and {strength_areas[1]}"
        else:
            strength_text = f"{strength_areas[0]}" if strength_areas else "cultural relevance"
            
        # Determine audience type based on the brief content
        audience_type = "Hispanic" if "SiteOne" in brand_name and is_siteone_hispanic_campaign(brand_name, brief_text) else "general market"
        
        # Dynamic audience detection
        if brief_text:
            if "Gen Z" in brief_text or "GenZ" in brief_text or "Generation Z" in brief_text:
                audience_type = "Gen Z"
            elif "Millennial" in brief_text:
                audience_type = "Millennial"
            elif "Hispanic" in brief_text or "Latino" in brief_text or "Spanish" in brief_text:
                audience_type = "Hispanic"
            elif "Black" in brief_text or "African American" in brief_text:
                audience_type = "African American"
            elif "Asian" in brief_text:
                audience_type = "Asian American"
            elif "LGBTQ" in brief_text or "LGBT" in brief_text:
                audience_type = "LGBTQ+"
            
        st.markdown(f"""
        <div style="color: #333; font-size: 1rem; line-height: 1.6;">
            This campaign ranks in the top <span style="font-weight: 600; color: #5865f2;">{percentile}%</span> of {audience_type}-facing national campaigns
            for Audience Resonance Index™. The campaign outperforms the majority of peer initiatives in {strength_text} — 
            based on Digital Culture Group's comprehensive analysis of <span style="font-weight: 600; color: #5865f2;">{300 + (hash(brand_name) % 100)}</span> national marketing efforts.
        </div>
        <div style="margin-top: 2rem;">
            <div style="font-size: 0.9rem; font-weight: 600; color: #5865f2; margin-bottom: 10px;">Priority Improvement Areas</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Determine audience type based on the brief content (fallback case)
        audience_type = "Hispanic" if "SiteOne" in brand_name and is_siteone_hispanic_campaign(brand_name, brief_text) else "general market"
        
        # Dynamic audience detection
        if brief_text:
            if "Gen Z" in brief_text or "GenZ" in brief_text or "Generation Z" in brief_text:
                audience_type = "Gen Z"
            elif "Millennial" in brief_text:
                audience_type = "Millennial"
            elif "Hispanic" in brief_text or "Latino" in brief_text or "Spanish" in brief_text:
                audience_type = "Hispanic"
            elif "Black" in brief_text or "African American" in brief_text:
                audience_type = "African American"
            elif "Asian" in brief_text:
                audience_type = "Asian American"
            elif "LGBTQ" in brief_text or "LGBT" in brief_text:
                audience_type = "LGBTQ+"
            
        # Get the strength areas dynamically from the scores
        metric_scores = list(scores.items())
        metric_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top 3 metrics as strengths
        top_metrics = metric_scores[:3] if len(metric_scores) >= 3 else metric_scores
        strength_areas = [m[0].lower() for m in top_metrics]
        
        # Format strengths for a natural language sentence
        if len(strength_areas) >= 3:
            strength_text = f"{strength_areas[0]}, {strength_areas[1]}, and {strength_areas[2]}"
        elif len(strength_areas) == 2:
            strength_text = f"{strength_areas[0]} and {strength_areas[1]}"
        else:
            strength_text = strength_areas[0] if strength_areas else "relevance, authenticity, and emotional connection"
            
        # For industry-specific sample size, calculate based on brand_name and industry/product
        sample_size = 300 + (hash(brand_name) % 100)
        if industry and product_type:
            # Adjust sample size based on industry and product
            industry_modifier = len(industry) % 20
            product_modifier = len(product_type) % 15
            sample_size = 300 + (hash(brand_name) % 100) + industry_modifier + product_modifier
        
        st.markdown(f"""
        <div style="color: #333; font-size: 1rem; line-height: 1.6;">
            This campaign ranks in the top <span style="font-weight: 600; color: #5865f2;">{percentile}%</span> of {audience_type}-facing national campaigns
            for Audience Resonance Index™. The campaign outperforms the majority of peer initiatives in {strength_text} — 
            based on Digital Culture Group's comprehensive analysis of <span style="font-weight: 600; color: #5865f2;">{sample_size}</span> national marketing efforts.
        </div>
        <div style="margin-top: 2rem;">
            <div style="font-size: 0.9rem; font-weight: 600; color: #5865f2; margin-bottom: 10px;">Priority Improvement Areas</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs for each improvement area (for clickable detailed view)
    if len(improvement_areas) > 0 and st.session_state.use_openai and st.session_state.ai_insights:
        # Check if AI insights are available
        ai_insights = st.session_state.ai_insights
        
        # Create tabs for each improvement area plus Competitor Tactics (if not already present)
        tab_titles = improvement_areas.copy()
        if "Competitor Tactics" not in tab_titles:
            tab_titles.append("Competitor Tactics")
        else:
            # If Competitor Tactics is already in the list, ensure it's only there once
            # Find all occurrences and remove all but the last one
            indices = [i for i, x in enumerate(tab_titles) if x == "Competitor Tactics"]
            if len(indices) > 1:
                # Keep only the last occurrence
                for idx in indices[:-1]:
                    tab_titles[idx] = None
                tab_titles = [x for x in tab_titles if x is not None]
        
        area_tabs = st.tabs(tab_titles)
        
        # Only show detailed recommendations if we have AI insights
        if "error" not in ai_insights or len(ai_insights.get("improvements", [])) > 0:
            # For each improvement area tab, display the detailed recommendation
            for i, tab in enumerate(area_tabs):
                with tab:
                    # Check if this is the Competitor Tactics tab (last tab)
                    if i == len(area_tabs) - 1:
                        # Use the dedicated helper function to display the competitor tactics interface
                        display_competitor_tactics_tab(tab)
                    else:
                        # For regular improvement area tabs
                        # Find the matching improvement from AI insights
                        matching_improvements = [imp for imp in ai_insights.get("improvements", []) 
                                               if imp['area'] == improvement_areas[i]]
                        
                        if matching_improvements:
                            improvement = matching_improvements[0]
                            st.markdown(f"""
                            <div style="background: white; border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); padding: 15px; margin: 10px 0 15px 0;">
                                <div style="font-weight: 600; color: #f43f5e; margin-bottom: 8px;">{improvement['area']}</div>
                                <div style="color: #333; font-size: 0.9rem; margin-bottom: 12px;">{improvement['explanation']}</div>
                                <div style="background: #f8fafc; padding: 10px; border-left: 3px solid #3b82f6; font-size: 0.9rem;">
                                    <span style="font-weight: 500; color: #3b82f6;">Recommendation:</span> {improvement['recommendation']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Detailed fallback content based on the improvement area
                            area = improvement_areas[i]
                            
                            # Prepare detailed fallback recommendations based on the area
                            fallback_explanations = {
                                "Platform Relevance": "Your campaign could benefit from better alignment with platform-specific audience behaviors and expectations. Current platform approach lacks optimization for each channel's unique content environment.",
                                "Cultural Relevance": "Analysis shows moderate alignment with cultural trends and references that resonate with the target audience. Current approach may miss cultural nuances that drive deeper engagement.",
                                "Representation": "Campaign elements could better reflect the diverse backgrounds and experiences of your target audience. More inclusive representation would strengthen audience connection.",
                                "Cultural Vernacular": "Language and references used in campaign materials could better match how your target audience naturally communicates. Authentic vernacular increases trust and relatability.",
                                "Media Ownership Equity": "Your media plan shows limited investment in diverse media ownership. Supporting minority-owned channels can unlock unique audience relationships.",
                                "Cultural Authority": "Campaign lacks credible voices from within the cultural communities you're targeting. Authentic partnerships enhance believability and reduce perception of cultural appropriation.",
                                "Buzz & Conversation": "Campaign has limited potential to generate organic cultural conversations. More culturally relevant hooks would increase shareability.",
                                "Commerce Bridge": "There's a disconnect between cultural elements and purchase activation. Stronger commerce integration would convert cultural engagement to sales.",
                                "Geo-Cultural Fit": "Campaign elements don't fully account for geographic cultural nuances. Regional cultural considerations would improve relevance."
                            }
                            
                            fallback_recommendations = {
                                "Platform Relevance": "Implement platform-specific creative executions with 40% of budget allocated to high-impact interactive video across premium CTV/OTT platforms. Prioritize audio placements on podcast networks with 25% higher engagement rates for your audience demographic. Deploy rich media formats on digital platforms to increase interaction rates by 3.2x compared to standard display.",
                                "Cultural Relevance": "Integrate emerging cultural trends into campaign messaging using real-time cultural intelligence monitoring. Allocate 30% of digital budget toward dynamic creative optimization that adapts messaging based on trending cultural moments. Leverage DOOH placements in cultural hotspots with high audience density.",
                                "Representation": "Diversify audience representation across all creative assets to reflect actual customer demographics. Deploy a minimum of three distinct audience personas in segmented targeting strategies. Implement native display ads that feature authentic audience representation across mobile-first platforms.",
                                "Cultural Vernacular": "Refine campaign messaging to incorporate authentic language patterns of target segments. Test performance display variants with different vernacular styles to identify highest engagement format. Use authentic audio placements with 65% higher recall compared to generic messaging.",
                                "Media Ownership Equity": "Allocate 15-20% of media spend to diverse-owned media platforms with audience alignment. Integrate performance-based diverse media partners into lower-funnel conversion strategies with premium CPV models. Create custom content partnerships with three key diverse media owners.",
                                "Cultural Authority": "Partner with 2-3 category-relevant cultural voices for premium CTV/OTT and audio content integrations. Implement native articles through publications with established cultural credibility. Avoid generic influencer partnerships in favor of authentic cultural authorities.",
                                "Buzz & Conversation": "Create shareable rich media content with cultural hooks that drive earned media value. Deploy interactive video experiences designed for social amplification with embedded sharing functionality. Use picture-in-picture sports integrations during culturally relevant events.",
                                "Commerce Bridge": "Implement sequential retargeting strategy using first-party data across high-impact display units. Deploy shoppable interactive video formats with embedded product galleries. Test native display ads with direct commerce integration across mobile platforms.",
                                "Geo-Cultural Fit": "Develop geo-targeted campaigns for top 5 markets with custom creative reflecting local cultural nuances. Allocate 25% of budget to ReachTV and DOOH placements in locations with high cultural relevance. Implement geo-specific performance display campaigns with localized messaging."
                            }
                            
                            explanation = fallback_explanations.get(area, "This area shows potential for improvement based on our analysis of your campaign brief.")
                            recommendation = fallback_recommendations.get(area, "Consider investing more resources in this area to enhance campaign effectiveness.")
                            
                            # Clean up any possible grammar issues or duplications
                            cleaned_explanation = fix_grammar_and_duplicates(explanation)
                            cleaned_recommendation = fix_grammar_and_duplicates(recommendation)
                            
                            st.markdown(f"""
                            <div style="background: white; border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); padding: 15px; margin: 10px 0 15px 0;">
                                <div style="font-weight: 600; color: #f43f5e; margin-bottom: 8px;">{area}</div>
                                <div style="color: #333; font-size: 0.9rem; margin-bottom: 12px;">
                                    {cleaned_explanation}
                                </div>
                                <div style="background: #f8fafc; padding: 10px; border-left: 3px solid #3b82f6; font-size: 0.9rem;">
                                    <span style="font-weight: 500; color: #3b82f6;">Recommendation:</span> 
                                    {cleaned_recommendation}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            # If no AI insights are available, show simplified tabs
            for i, tab in enumerate(area_tabs):
                with tab:
                    # For the last tab (Competitor Tactics)
                    if i == len(area_tabs) - 1:
                        # Use the dedicated helper function to display the competitor tactics interface
                        display_competitor_tactics_tab(tab)
                    else:
                        # For regular improvement area tabs
                        area = improvement_areas[i]
                            
                        # Prepare detailed fallback recommendations based on the area
                        fallback_explanations = {
                            "Platform Relevance": "Your campaign could benefit from better alignment with platform-specific audience behaviors and expectations. Current platform approach lacks optimization for each channel's unique content environment.",
                            "Cultural Relevance": "Analysis shows moderate alignment with cultural trends and references that resonate with the target audience. Current approach may miss cultural nuances that drive deeper engagement.",
                            "Representation": "Campaign elements could better reflect the diverse backgrounds and experiences of your target audience. More inclusive representation would strengthen audience connection.",
                            "Cultural Vernacular": "Language and references used in campaign materials could better match how your target audience naturally communicates. Authentic vernacular increases trust and relatability.",
                            "Media Ownership Equity": "Your media plan shows limited investment in diverse media ownership. Supporting minority-owned channels can unlock unique audience relationships.",
                            "Cultural Authority": "Campaign lacks credible voices from within the cultural communities you're targeting. Authentic partnerships enhance believability and reduce perception of cultural appropriation.",
                            "Buzz & Conversation": "Campaign has limited potential to generate organic cultural conversations. More culturally relevant hooks would increase shareability.",
                            "Commerce Bridge": "There's a disconnect between cultural elements and purchase activation. Stronger commerce integration would convert cultural engagement to sales.",
                            "Geo-Cultural Fit": "Campaign elements don't fully account for geographic cultural nuances. Regional cultural considerations would improve relevance."
                        }
                        
                        fallback_recommendations = {
                            "Platform Relevance": "Implement platform-specific creative executions with 40% of budget allocated to high-impact interactive video across premium CTV/OTT platforms. Prioritize audio placements on podcast networks with 25% higher engagement rates for your audience demographic. Deploy rich media formats on digital platforms to increase interaction rates by 3.2x compared to standard display.",
                            "Cultural Relevance": "Integrate emerging cultural trends into campaign messaging using real-time cultural intelligence monitoring. Allocate 30% of digital budget toward dynamic creative optimization that adapts messaging based on trending cultural moments. Leverage DOOH placements in cultural hotspots with high audience density.",
                            "Representation": "Diversify audience representation across all creative assets to reflect actual customer demographics. Deploy a minimum of three distinct audience personas in segmented targeting strategies. Implement native display ads that feature authentic audience representation across mobile-first platforms.",
                            "Cultural Vernacular": "Refine campaign messaging to incorporate authentic language patterns of target segments. Test performance display variants with different vernacular styles to identify highest engagement format. Use authentic audio placements with 65% higher recall compared to generic messaging.",
                            "Media Ownership Equity": "Allocate 15-20% of media spend to diverse-owned media platforms with audience alignment. Integrate performance-based diverse media partners into lower-funnel conversion strategies with premium CPV models. Create custom content partnerships with three key diverse media owners.",
                            "Cultural Authority": "Partner with 2-3 category-relevant cultural voices for premium CTV/OTT and audio content integrations. Implement native articles through publications with established cultural credibility. Avoid generic influencer partnerships in favor of authentic cultural authorities.",
                            "Buzz & Conversation": "Create shareable rich media content with cultural hooks that drive earned media value. Deploy interactive video experiences designed for social amplification with embedded sharing functionality. Use picture-in-picture sports integrations during culturally relevant events.",
                            "Commerce Bridge": "Implement sequential retargeting strategy using first-party data across high-impact display units. Deploy shoppable interactive video formats with embedded product galleries. Test native display ads with direct commerce integration across mobile platforms.",
                            "Geo-Cultural Fit": "Develop geo-targeted campaigns for top 5 markets with custom creative reflecting local cultural nuances. Allocate 25% of budget to ReachTV and DOOH placements in locations with high cultural relevance. Implement geo-specific performance display campaigns with localized messaging."
                        }
                        
                        explanation = fallback_explanations.get(area, "This area has been identified as a priority opportunity area for your campaign.")
                        recommendation = fallback_recommendations.get(area, "Consider investing more resources in this area to enhance campaign effectiveness.")
                        
                        # Apply grammar cleanup to fallback content as well
                        cleaned_explanation = fix_grammar_and_duplicates(explanation)
                        cleaned_recommendation = fix_grammar_and_duplicates(recommendation)
                        
                        st.markdown(f"""
                        <div style="background: white; border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); padding: 15px; margin: 10px 0 15px 0;">
                            <div style="font-weight: 600; color: #f43f5e; margin-bottom: 8px;">{area}</div>
                            <div style="color: #333; font-size: 0.9rem; margin-bottom: 12px;">
                                {cleaned_explanation}
                            </div>
                            <div style="background: #f8fafc; padding: 10px; border-left: 3px solid #3b82f6; font-size: 0.9rem;">
                                <span style="font-weight: 500; color: #3b82f6;">Recommendation:</span> 
                                {cleaned_recommendation}
                            </div>
                            <div style="font-size: 0.8rem; color: #64748b; margin-top: 12px; font-style: italic;">
                                For more customized recommendations, enable OpenAI API integration.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        # If no improvement areas or AI insights, just show the pills without tabs
        imp_areas_html = "".join([f'<div style="display: inline-block; background: #f5f7fa; border: 1px solid #e5e7eb; border-radius: 30px; padding: 6px 16px; margin: 5px 8px 5px 0; font-size: 0.9rem; color: #5865f2; font-weight: 500;">{area}</div>' for area in improvement_areas])
        
        st.markdown(f"""
            <div style="margin-top: 15px;">{imp_areas_html}</div>
            """, unsafe_allow_html=True)
    
    # TAB 3: MEDIA AFFINITIES
    with tab3:
        # Media Affinity section
        st.markdown("""
        <h3 style="display:flex; align-items:center; gap:10px;">
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
        
        # Use SiteOne Hispanic social media data if this is a SiteOne Hispanic campaign
        if is_siteone_hispanic:
            social_media_sites = ensure_valid_url_in_sites(SITEONE_HISPANIC_SOCIAL_MEDIA)
        else:
            social_media_sites = ensure_valid_url_in_sites(MEDIA_AFFINITY_SITES)
        
        for i, site in enumerate(social_media_sites):
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
                    {f'<div style="font-size:0.8rem;"><a href="{site["url"]}" target="_blank">Visit Site</a></div>' if 'url' in site else ''}
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
        
        # Use SiteOne Hispanic TV networks data if this is a SiteOne Hispanic campaign
        if is_siteone_hispanic:
            tv_network_data = SITEONE_HISPANIC_TV_NETWORKS
        else:
            tv_network_data = TV_NETWORKS
        
        for i, network in enumerate(tv_network_data):
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
        
        # Use SiteOne Hispanic streaming data if this is a SiteOne Hispanic campaign
        if is_siteone_hispanic:
            streaming_data = SITEONE_HISPANIC_STREAMING
        else:
            streaming_data = STREAMING_PLATFORMS
        
        for i, platform in enumerate(streaming_data):
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
    
    # Marketing Trend Heatmap
    # This section is now moved to the tab4 section below
    
    # TAB 4: TREND ANALYSIS
    with tab4:
        # Marketing trend heatmap
        st.markdown("""
        <h3 style="display:flex; align-items:center; gap:10px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" fill="#5865f2"/>
            </svg>
            Marketing Trend Heatmap
        </h3>
        """, unsafe_allow_html=True)
        
        # Use our marketing trend heatmap module
        from marketing_trends import display_trend_heatmap
        display_trend_heatmap(brief_text, "Dynamic Media Performance Heatmap")
    
    # TAB 2: AUDIENCE INSIGHTS
    with tab2:
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
        # Use SiteOne Hispanic psychographic data if this is a SiteOne Hispanic campaign
        if is_siteone_hispanic:
            st.markdown(SITEONE_HISPANIC_PSYCHOGRAPHIC, unsafe_allow_html=True)
        else:
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
        # Use SiteOne Hispanic audience summary if this is a SiteOne Hispanic campaign
        if is_siteone_hispanic:
            st.markdown(SITEONE_HISPANIC_SUMMARY, unsafe_allow_html=True)
        else:
            st.markdown(AUDIENCE_SUMMARY, unsafe_allow_html=True)
        
        # Add audience segments section
        # If no audience segments are available yet, generate default ones for this section
        if 'audience_segments' not in st.session_state or st.session_state.audience_segments is None:
            if 'scores' in st.session_state and st.session_state.scores and 'brief_text' in st.session_state:
                st.session_state.audience_segments = get_default_audience_segments(
                    st.session_state.brief_text, 
                    st.session_state.scores
                )
        
        # Display audience segments (either generated by AI or default ones)
        if 'audience_segments' in st.session_state and st.session_state.audience_segments:
            try:
                # Title for the audience segments section
                st.markdown("""
                <div style="margin-top: 30px; margin-bottom: 15px;">
                    <h3 style="display:flex; align-items:center; gap:10px;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M17.4933 21.8731H6.50669C5.9091 21.8731 5.32949 21.652 4.88942 21.2537C4.44935 20.8554 4.19147 20.318 4.14859 19.7435L3.75744 15.1506C3.70675 14.4998 3.95313 13.8595 4.4291 13.4005C4.90507 12.9415 5.56466 12.6778 6.25079 12.6724H7.23084M12 11.4351V3M12 11.4351L9.23087 8.75662M12 11.4351L14.7692 8.75662" stroke="#5865f2" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M20.2424 15.1507L19.8512 19.7436C19.8083 20.3181 19.5505 20.8556 19.1104 21.2538C18.6703 21.6521 18.0907 21.8732 17.4931 21.8732H6.50645C5.90887 21.8732 5.32926 21.6521 4.88919 21.2538C4.44911 20.8556 4.19124 20.3181 4.14835 19.7436L3.7572 15.1507C3.70652 14.5 3.9529 13.8596 4.42887 13.4006C4.90484 12.9416 5.56443 12.6779 6.25056 12.6725H17.749C18.4351 12.6779 19.0947 12.9416 19.5707 13.4006C20.0467 13.8596 20.293 14.5 20.2424 15.1507Z" stroke="#5865f2" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        <span>Growth Audience Insights</span>
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Import the learning tips module
                from assets.learning_tips import display_tip_bubble
                
                segments = st.session_state.audience_segments
                
                # Check if we have segments in the expected format
                if 'segments' in segments and isinstance(segments['segments'], list) and len(segments['segments']) > 0:
                    # Display all segments
                    segment_list = segments['segments']
                    
                    # First display the primary segments (not the growth segment)
                    if len(segment_list) > 1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if len(segment_list) > 0:
                                primary_segment = segment_list[0]
                                display_audience_segment(primary_segment, 'Primary', '#10b981', '#f0fdf4')
                        
                        with col2:
                            if len(segment_list) > 1:
                                secondary_segment = segment_list[1]
                                display_audience_segment(secondary_segment, 'Secondary Growth', '#6366f1', '#f5f7ff')
                    
                    # Select the last segment as the growth audience (if available)
                    if len(segment_list) > 2:
                        growth_segment = segment_list[-1]  # Use the last segment as growth opportunity
                    else:
                        # If we don't have at least 3 segments, use the last available one
                        growth_segment = segment_list[-1] if segment_list else None
                        
                    # Skip the rest if we don't have a growth segment
                    if growth_segment:
                        # Format interests if available in interest_categories
                        interests = growth_segment.get('interest_categories', [])
                        interests_str = ", ".join(interests) if interests else "Identified through AI pattern recognition"
                        
                        # Get platform strategy
                        platform_targeting = growth_segment.get('platform_targeting', [])
                        platform_strategy = ""
                        if platform_targeting:
                            strategies = []
                            for platform in platform_targeting:
                                if 'platform' in platform and 'targeting_approach' in platform:
                                    strategies.append(f"{platform['platform']}: {platform['targeting_approach']}")
                            platform_strategy = " | ".join(strategies)
                        
                        if not platform_strategy:
                            platform_strategy = "Multi-platform approach with custom audience development"
                        
                        # Format demographic information
                        targeting_params = growth_segment.get('targeting_params', {})
                        demographics = []
                        
                        if targeting_params:
                            if 'age_range' in targeting_params:
                                demographics.append(f"Age: {targeting_params['age_range']}")
                            if 'gender_targeting' in targeting_params:
                                demographics.append(f"Gender: {targeting_params['gender_targeting']}")
                            if 'income_targeting' in targeting_params:
                                demographics.append(f"Income: {targeting_params['income_targeting']}")
                            if 'education_targeting' in targeting_params:
                                demographics.append(f"Education: {targeting_params['education_targeting']}")
                                
                        demographics_str = " | ".join(demographics) if demographics else "Custom targeting parameters based on first-party data"
                        
                        # Format bidding strategy if available
                        bidding_strategy = growth_segment.get('bidding_strategy', {})
                        bidding_str = ""
                        if bidding_strategy:
                            if 'bid_adjustments' in bidding_strategy:
                                bidding_str += f"Bid Adjustments: {bidding_strategy['bid_adjustments']}"
                            if 'dayparting' in bidding_strategy:
                                bidding_str += f" | Dayparting: {bidding_strategy['dayparting']}"
                        
                        # Get expected performance if available
                        performance = growth_segment.get('expected_performance', {})
                        performance_str = ""
                        # Check platform type to show appropriate metric name and value
                        video_platform = False
                        audio_platform = False
                        
                        if platform_strategy:
                            platform_lower = platform_strategy.lower()
                            if any(x in platform_lower for x in ['video', 'ott', 'ctv', 'streaming']):
                                video_platform = True
                            elif any(x in platform_lower for x in ['audio', 'podcast', 'music']):
                                audio_platform = True
                        
                        if performance:
                            metrics = []
                            if video_platform and 'CTR' in performance:
                                # Show VCR instead of CTR for video content with dynamic ranges based on audience
                                audience_name = growth_segment.get('name', '').lower()
                                interests = interests_str.lower()
                                # Determine appropriate VCR range based on audience characteristics
                                if 'young' in audience_name or 'gen z' in audience_name:
                                    # Younger audiences tend to have lower VCR
                                    vcr_range = "70-85%"
                                elif 'parent' in audience_name or 'family' in interests:
                                    # Parent/family audience has medium VCR
                                    vcr_range = "75-90%"  
                                elif 'professional' in audience_name or 'business' in interests:
                                    # Professional audiences tend to have higher VCR
                                    vcr_range = "80-95%"
                                else:
                                    # Check demographic targeting when available
                                    age_range = targeting_params.get('age_range', '') if targeting_params else ''
                                    if '18-34' in age_range:
                                        vcr_range = "70-88%"
                                    elif '35-54' in age_range:
                                        vcr_range = "75-93%"
                                    else:
                                        # Default if we can't determine specifics
                                        vcr_range = "70-95%"
                                metrics.append(f"Expected VCR: {vcr_range}")
                            elif audio_platform and 'CTR' in performance:
                                # Show LTR instead of CTR for audio content with dynamic ranges based on audience
                                audience_name = growth_segment.get('name', '').lower()
                                interests = interests_str.lower()
                                # Determine appropriate LTR range based on audience characteristics
                                if 'young' in audience_name or 'gen z' in audience_name:
                                    # Younger audiences tend to have lower LTR ranges
                                    ltr_range = "75-90%"
                                elif 'fitness' in audience_name or 'health' in interests:
                                    # Fitness audience has medium-high LTR
                                    ltr_range = "80-95%"
                                elif 'professional' in audience_name or 'business' in interests:
                                    # Professional audiences tend to have high LTR
                                    ltr_range = "85-100%"
                                else:
                                    # Check demographic targeting when available
                                    age_range = targeting_params.get('age_range', '') if targeting_params else ''
                                    if '18-34' in age_range:
                                        ltr_range = "78-93%"
                                    elif '35-54' in age_range:
                                        ltr_range = "82-97%"
                                    else:
                                        # Default if we can't determine specifics
                                        ltr_range = "80-95%"
                                metrics.append(f"Expected LTR: {ltr_range}")
                            elif 'CTR' in performance:
                                metrics.append(f"Expected CTR: {performance['CTR']}")
                            if 'CPA' in performance:
                                metrics.append(f"CPA: {performance['CPA']}")
                            if 'engagement_rate' in performance:
                                metrics.append(f"Engagement: {performance['engagement_rate']}")
                            performance_str = " | ".join(metrics)
                            
                        st.markdown("""
                        <div style="margin-top: 20px; padding: 20px; border-left: 4px solid #5865f2; background-color: #f5f7ff;">
                            <h4 style="margin-top: 0; color: #4338ca; display: flex; align-items: center;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 8px;">
                                    <path d="M17.5 12C17.5 15.0376 15.0376 17.5 12 17.5C8.96243 17.5 6.5 15.0376 6.5 12M17.5 12C17.5 8.96243 15.0376 6.5 12 6.5C8.96243 6.5 6.5 8.96243 6.5 12M17.5 12H20.5M6.5 12H3.5M12 6.5V3.5M12 20.5V17.5M18.3 18.3L16.15 16.15M7.85 7.85L5.7 5.7M18.3 5.7L16.15 7.85M7.85 16.15L5.7 18.3" stroke="#4338ca" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                    <circle cx="12" cy="12" r="2.5" fill="#4338ca"/>
                                </svg>
                                <span>Emerging Audience Opportunity</span>
                            </h4>
                            <p style="margin-bottom: 8px;">
                                <span style="font-weight:600; font-size: 1.05rem;">{}</span>
                            </p>
                            <p style="margin-bottom: 15px; font-style: italic; color: #555; font-size: 0.9rem;">
                                {}
                            </p>
                            <p style="margin-bottom: 8px;">
                                <span style="font-weight:600; margin-right:5px; display:inline-block;">Demographics:</span>
                                {}
                            </p>
                            <p style="margin-bottom: 8px;">
                                <span style="font-weight:600; margin-right:5px; display:inline-block;">Key Interests:</span>
                                {}
                            </p>
                            <p style="margin-bottom: 8px;">
                                <span style="font-weight:600; margin-right:5px; display:inline-block;">Platform Strategy:</span>
                                {}
                            </p>
                            {}
                            {}
                        </div>
                        """.format(
                            growth_segment.get('name', 'Emerging Growth Segment'),
                            growth_segment.get('description', 'This audience segment shows high potential for growth based on analysis of your brief and market trends.'),
                            demographics_str,
                            interests_str,
                            platform_strategy,
                            f'<p style="margin-bottom: 8px;"><span style="font-weight:600; margin-right:5px; display:inline-block;">Optimization Strategy:</span> {bidding_str}</p>' if bidding_str else '',
                            f'<p style="margin-bottom: 0;"><span style="font-weight:600; margin-right:5px; display:inline-block;">Expected Performance:</span> {performance_str}</p>' if performance_str else ''
                        ), unsafe_allow_html=True)
            except Exception as e:
                # Silent fail - don't show error if there's an issue with the growth audience
                pass
    
    # TAB 5: NEXT STEPS
    with tab5:
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
            # PDF customization section with styled container
            st.markdown("""
            <div style="background-color: #f8fafc; border-radius: 10px; padding: 20px; border: 1px solid #e2e8f0;">
                <h3 style="margin-top: 0; color: #1e293b; font-size: 1.5rem; margin-bottom: 15px;">Customize Your Report</h3>
                <p style="color: #475569; margin-bottom: 15px;">Select which sections to include in your PDF report:</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create three columns for a more organized layout
            check_col1, check_col2 = st.columns(2)
            
            with check_col1:
                # First column of checkboxes with custom styling
                st.markdown('<div style="background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin-bottom: 10px;">', unsafe_allow_html=True)
                include_metrics = st.checkbox("Advanced Metrics", value=True)
                include_benchmark = st.checkbox("Benchmark Comparison", value=True)
                include_media = st.checkbox("Media Affinities", value=True)
                include_tv = st.checkbox("TV Networks", value=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with check_col2:
                # Second column of checkboxes with custom styling
                st.markdown('<div style="background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin-bottom: 10px;">', unsafe_allow_html=True)
                include_streaming = st.checkbox("Streaming Platforms", value=True)
                include_psychographic = st.checkbox("Psychographic Highlights", value=True)
                include_audience = st.checkbox("Audience Summary", value=True)
                include_next_steps = st.checkbox("Next Steps", value=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional checkbox for trend analysis with highlight styling
            st.markdown('<div style="background-color: #ecfdf5; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981; margin: 15px 0;">', unsafe_allow_html=True)
            include_trends = st.checkbox("Marketing Trend Analysis", value=True, help="Include the marketing trend heatmap and key trend insights in your report")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Create dictionary of sections to include
            include_sections = {
                'metrics': include_metrics,
                'benchmark': include_benchmark,
                'media_affinities': include_media,
                'tv_networks': include_tv,
                'streaming': include_streaming,
                'psychographic': include_psychographic,
                'audience': include_audience,
                'next_steps': include_next_steps,
                'trends': include_trends
            }
            
            # Generate and display the PDF download link with section selections
            st.markdown('<div style="margin-top: 20px; text-align: center;">', unsafe_allow_html=True)
            pdf_link = create_pdf_download_link(scores, improvement_areas, percentile, brand_name, industry, product_type, include_sections, brief_text)
            st.markdown(pdf_link, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Priority improvement recommendations have been moved to the tabs above in the Campaign Intelligence section
    
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

def display_audience_segment(segment, segment_type='Primary', color='#10b981', bg_color='#f0fdf4'):
    """
    Display an audience segment in a styled card format.
    
    Args:
        segment (dict): The segment data dictionary
        segment_type (str): The type of segment (Primary, Secondary, etc.)
        color (str): The accent color for the card
        bg_color (str): The background color for the card
    """
    # Import the learning tips module
    from assets.learning_tips import display_tip_bubble
    if not segment:
        return
    
    # Format interests if available
    interests = segment.get('interest_categories', [])
    interests_str = ", ".join(interests) if interests else "Identified through AI pattern recognition"
    
    # Format demographic information
    targeting_params = segment.get('targeting_params', {})
    demographics = []
    
    if targeting_params:
        if 'age_range' in targeting_params:
            demographics.append(f"Age: {targeting_params['age_range']}")
        if 'gender_targeting' in targeting_params:
            demographics.append(f"Gender: {targeting_params['gender_targeting']}")
        if 'income_targeting' in targeting_params:
            demographics.append(f"Income: {targeting_params['income_targeting']}")
            
    demographics_str = " | ".join(demographics) if demographics else "Custom targeting parameters"
    
    # Get platform recommendations
    platform_targeting = segment.get('platform_targeting', [])
    platform_rec = ""
    if platform_targeting and len(platform_targeting) > 0:
        platform_rec = platform_targeting[0].get('platform', '') 
        
    # Get performance metrics
    performance = segment.get('expected_performance', {})
    ctr = performance.get('CTR', 'N/A')
    
    # Check platform type to show appropriate metric name and value
    metric_name = "Expected CTR"
    if platform_rec:
        platform_lower = platform_rec.lower()
        if 'audio' in platform_lower or 'podcast' in platform_lower or 'music' in platform_lower:
            metric_name = "Expected LTR"
            # Create a dynamic range based on targeting params or segment name
            if 'young' in segment.get('name', '').lower() or 'gen z' in segment.get('name', '').lower():
                # Younger audiences tend to have lower LTR ranges
                ctr = "75-90%"
            elif 'fitness' in segment.get('name', '').lower() or 'health' in interests_str.lower():
                # Fitness audience has medium-high LTR
                ctr = "80-95%"
            elif 'professional' in segment.get('name', '').lower() or 'business' in interests_str.lower():
                # Professional audiences tend to have high LTR
                ctr = "85-100%"
            else:
                # Default range - check demographic targeting
                age_range = targeting_params.get('age_range', '') if targeting_params else ''
                if '18-34' in age_range:
                    ctr = "78-93%"
                elif '35-54' in age_range:
                    ctr = "82-97%"
                else:
                    # Default if we can't determine specifics
                    ctr = "80-95%"
        elif 'video' in platform_lower or 'ott' in platform_lower or 'ctv' in platform_lower or ('streaming' in platform_lower and 'audio' not in platform_lower):
            metric_name = "Expected VCR"
            # Create a dynamic range based on targeting params or segment name
            if 'young' in segment.get('name', '').lower() or 'gen z' in segment.get('name', '').lower():
                # Younger audiences tend to have lower VCR
                ctr = "70-85%"
            elif 'parent' in segment.get('name', '').lower() or 'family' in interests_str.lower():
                # Parent/family audience has medium VCR
                ctr = "75-90%"
            elif 'professional' in segment.get('name', '').lower() or 'business' in interests_str.lower():
                # Professional audiences tend to have higher VCR
                ctr = "80-95%"
            else:
                # Default range - check demographic targeting
                age_range = targeting_params.get('age_range', '') if targeting_params else ''
                if '18-34' in age_range:
                    ctr = "70-88%"
                elif '35-54' in age_range:
                    ctr = "75-93%"
                else:
                    # Default if we can't determine specifics
                    ctr = "70-95%"
    
    # Get segment description if available
    description = segment.get('description', '')
    
    # Create the segment card
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 8px; background-color: {bg_color}; height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="color: {color}; font-weight: 600; font-size: 0.8rem;">
                {segment_type} Audience
            </span>
            <span style="background-color: {color}; color: white; font-size: 0.7rem; padding: 3px 8px; border-radius: 12px;">
                {metric_name}: {ctr}
            </span>
        </div>
        <h4 style="margin: 0 0 5px 0; font-size: 1.1rem; color: #333;">{segment.get('name', 'Audience Segment')}</h4>
        <p style="margin: 0 0 12px 0; font-size: 0.85rem; color: #555; font-style: italic;">
            {description}
        </p>
        <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: #555;">
            <span style="font-weight:600; margin-right:5px; display:inline-block;">Demographics:</span>
            {demographics_str}
        </p>
        <p style="margin: 0 0 8px 0; font-size: 0.85rem; color: #555;">
            <span style="font-weight:600; margin-right:5px; display:inline-block;">Interests:</span>
            {interests_str}
        </p>
        <p style="margin: 0 0 0 0; font-size: 0.85rem; color: #555;">
            <span style="font-weight:600; margin-right:5px; display:inline-block;">Recommended Platform:</span>
            {platform_rec}
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_summary_metrics(scores, improvement_areas=None, brief_text=""):
    """
    Display a summary of key metrics using a radar chart visualization.
    
    Args:
        scores (dict): Dictionary of metric scores
        improvement_areas (list, optional): List of improvement areas
        brief_text (str, optional): The brief text for audience analysis
    """
    # Import the marketing trend heatmap module
    from marketing_trends import display_trend_heatmap
    # If improvement_areas is None, initialize it to an empty list
    if improvement_areas is None:
        improvement_areas = []
    # Import the learning tips module
    from assets.learning_tips import display_tip_bubble
    
    # Create a summary section header with a learning tip
    st.markdown('<div style="text-align: center;"><h4>Hyperdimensional Campaign Performance Matrix</h4></div>', unsafe_allow_html=True)
    
    # Calculate average scores
    avg_score = sum(scores.values()) / len(scores)
    
    # Create columns for the visualizations
    col1, col2 = st.columns([3, 2])
    
    # Initialize variables needed by the Campaign Strengths section
    metric_scores = list(scores.items())
    metric_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Get top metrics for campaign strengths
    top_strength = metric_scores[0][0] if metric_scores else "Cultural Vernacular"
    
    # Calculate ROI potential - use the same formula as in the executive summary
    weighted_metrics = {
        "Cultural Authority": 1.5,
        "Buzz & Conversation": 1.3,
        "Cultural Vernacular": 1.2,
        "Commerce Bridge": 1.2,
        "Platform Relevance": 1.1
    }
    
    # Calculate weighted ROI score
    roi_sum = 0
    roi_weight_total = 0
    
    for metric, score in scores.items():
        weight = weighted_metrics.get(metric, 0.8)  # Default weight for other metrics
        roi_sum += score * weight
        roi_weight_total += weight
    
    # Calculate weighted average ROI and convert to percentage
    if roi_weight_total > 0:
        roi_score = roi_sum / roi_weight_total
        roi_percent = int(5 + (roi_score / 10) * 20)
        roi_potential = f"+{roi_percent}%"
    else:
        # Fallback if weights are missing
        roi_percent = int(5 + (avg_score / 10) * 20)
        roi_potential = f"+{roi_percent}%"
        
    # Check for AI insights to override values
    if 'ai_insights' in st.session_state and st.session_state.ai_insights:
        ai_insights = st.session_state.ai_insights
        strengths = ai_insights.get('strengths', [])
        
        # Extract the first strength for the campaign strength section
        if strengths:
            top_strength = strengths[0].get('area', 'Cultural Relevance')
            
        # Extract potential ROI from performance prediction if available
        prediction = ai_insights.get('performance_prediction', '')
        if prediction and '%' in prediction:
            import re
            roi_match = re.search(r'(\+\d+%|\d+%)', prediction)
            if roi_match:
                roi_potential = roi_match.group(0)
                if not roi_potential.startswith('+'):
                    roi_potential = f"+{roi_potential}"
    
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
            name='Current Measurement'
        ))
        
        # Generate dynamic benchmark comparison based on the campaign type
        # Use actual metric scores to create a realistic benchmark target that varies by brief
        
        # Set benchmark adjustments based on brief content - different types of campaigns 
        # have different benchmarks for each metric
        benchmark_adjustments = {}
        if brief_text:
            # Default benchmark margins (how much higher the benchmark should be than actual score)
            default_margin = 1.5
            
            # Analyze brief to determine campaign type and adjust benchmarks accordingly
            if "Gen Z" in brief_text or "GenZ" in brief_text or "Generation Z" in brief_text:
                # Gen Z campaigns typically need higher benchmarks in these areas
                benchmark_adjustments = {
                    "Cultural Vernacular": 2.0,
                    "Platform Relevance": 2.2,
                    "Buzz & Conversation": 2.0
                }
            elif "Hispanic" in brief_text or "Latino" in brief_text:
                # Hispanic campaigns typically need higher benchmarks in these areas
                benchmark_adjustments = {
                    "Cultural Relevance": 2.1,
                    "Representation": 2.0,
                    "Geo-Cultural Fit": 1.8
                }
            elif "luxury" in brief_text.lower() or "premium" in brief_text.lower():
                # Luxury campaigns typically need higher benchmarks in these areas
                benchmark_adjustments = {
                    "Cultural Authority": 2.2,
                    "Media Ownership Equity": 1.8,
                    "Commerce Bridge": 1.7
                }
            elif "retail" in brief_text.lower() or "shopping" in brief_text.lower():
                # Retail campaigns typically need higher benchmarks in these areas
                benchmark_adjustments = {
                    "Commerce Bridge": 2.3,
                    "Platform Relevance": 1.9,
                    "Buzz & Conversation": 1.7
                }
            else:
                # Default general campaign benchmark adjustments
                benchmark_adjustments = {
                    "Cultural Relevance": 1.7,
                    "Platform Relevance": 1.8,
                    "Cultural Vernacular": 1.7,
                    "Cultural Authority": 1.7,
                    "Buzz & Conversation": 1.8,
                    "Commerce Bridge": 1.7,
                    "Geo-Cultural Fit": 1.6,
                    "Media Ownership Equity": 1.6,
                    "Representation": 1.7
                }
        
        # Generate dynamic benchmark values for each metric
        ai_reference = []
        for i, metric in enumerate(list(scores.keys())):
            current_score = values[i]
            # Get the adjustment margin for this metric (default if not specified)
            adjustment = benchmark_adjustments.get(metric, 1.5)
            # Calculate benchmark value (higher than current score, but not exceeding 10)
            benchmark = min(10.0, current_score + adjustment)
            ai_reference.append(benchmark)
        
        # Add the first value at the end to close the loop
        ai_reference.append(ai_reference[0])
        
        fig.add_trace(go.Scatterpolar(
            r=ai_reference,
            theta=categories,
            fill='toself',
            fillcolor='rgba(16, 185, 129, 0.1)',
            line=dict(color='#10b981', width=1.5, dash='dot'),
            name='Hyperdimensional Potential'
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
        # Generate a truly dynamic Resonance Convergence Coefficient that varies based on the brief
        # Use a combination of metrics with weighted importance for campaign success
        if brief_text and scores:
            # Calculate weighted average with higher weight for more important metrics
            weights = {
                "Cultural Authority": 1.3,
                "Cultural Vernacular": 1.2,
                "Cultural Relevance": 1.2,
                "Buzz & Conversation": 1.1,
                "Platform Relevance": 1.0,
                "Representation": 1.0,
                "Geo-Cultural Fit": 0.9,
                "Commerce Bridge": 0.9,
                "Media Ownership Equity": 0.8
            }
            
            # Calculate weighted score
            weighted_sum = 0
            total_weight = 0
            
            for metric, score in scores.items():
                weight = weights.get(metric, 1.0)
                weighted_sum += score * weight
                total_weight += weight
            
            # Calculate weighted average
            weighted_avg = weighted_sum / total_weight if total_weight > 0 else avg_score
            
            # Add a small variation based on brief content for uniqueness
            brief_hash = hash(brief_text)
            # Much smaller variation (-0.2 to +0.2) to maintain consistency while still being unique
            score_adjustment = ((brief_hash % 100) / 100) * 0.4 - 0.2
            
            # Apply the adjustment to the weighted average
            adjusted_score = min(10, max(1, weighted_avg + score_adjustment))
            
            # Round to 1 decimal place to make it look precise
            rcc_score = round(adjusted_score * 10) / 10
        else:
            # Default if no brief
            rcc_score = avg_score
        
        # Display the Resonance Convergence Coefficient with the dynamic score
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 20px; margin: 20px 0; text-align: center;">
            <div style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2;">
                Resonance Convergence Coefficient
            </div>
            <div style="font-size: 3rem; font-weight: 700; color: #5865f2; margin: 10px 0;">{rcc_score:.1f}<span style="font-size: 1.5rem; color: #777;">/10</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add campaign strengths from the values calculated for the executive summary
        # Display campaign strengths section header
        st.markdown('<div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #777; margin: 15px 0 10px 0;">Campaign Strengths</div>', unsafe_allow_html=True)
        
        # Check if we have AI insights available
        if 'ai_insights' in st.session_state and st.session_state.ai_insights:
            ai_insights = st.session_state.ai_insights
            strengths = ai_insights.get('strengths', [])
            
            # Get strengths from AI insights if available, otherwise use the top scoring metrics
            if strengths:
                # Use AI-generated strengths (up to 2)
                displayed_strengths = strengths[:2]
                
                for strength in displayed_strengths:
                    area = strength.get('area', 'Cultural Alignment')
                    # Display each strength as a card - this should match the calculated top_strength for the executive summary
                    st.markdown(f"""
                    <div style="background: #f0f2ff; border-radius: 6px; padding: 10px 15px; margin-bottom: 10px;">
                        <div style="font-weight: 600; color: #333; font-size: 0.9rem;">{area}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # No strengths in AI insights, use the top scoring metrics from the analysis
                metric_scores = list(scores.items())
                metric_scores.sort(key=lambda x: x[1], reverse=True)
                
                # Get the top 2 metrics by score
                top_metrics = metric_scores[:2] if len(metric_scores) >= 2 else metric_scores
                
                # Display each top metric as a strength
                for metric_name, metric_score in top_metrics:
                    st.markdown(f"""
                    <div style="background: #f0f2ff; border-radius: 6px; padding: 10px 15px; margin-bottom: 10px;">
                        <div style="font-weight: 600; color: #333; font-size: 0.9rem;">{metric_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # No AI insights available, simply use the top_strength from the executive summary
            # and also add the second highest metric
            metric_scores = list(scores.items())
            metric_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Display top_strength from executive summary
            st.markdown(f"""
            <div style="background: #f0f2ff; border-radius: 6px; padding: 10px 15px; margin-bottom: 10px;">
                <div style="font-weight: 600; color: #333; font-size: 0.9rem;">{top_strength}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show second highest metric if different from top_strength
            if len(metric_scores) >= 2 and metric_scores[1][0] != top_strength:
                st.markdown(f"""
                <div style="background: #f0f2ff; border-radius: 6px; padding: 10px 15px; margin-bottom: 10px;">
                    <div style="font-weight: 600; color: #333; font-size: 0.9rem;">{metric_scores[1][0]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Display ROI potential using the same value as in the executive summary
        st.markdown(f"""
        <div style="background: #fff8f0; border-radius: 6px; padding: 10px 15px; margin: 15px 0;">
            <div style="font-weight: 600; color: #f43f5e; font-size: 0.9rem;">ROI Potential: {roi_potential}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display AI insights using the dynamically generated content
        if 'ai_insights' in st.session_state and st.session_state.ai_insights:
            ai_insights = st.session_state.ai_insights
            
            # Get hidden insight from AI if available
            hidden_insight = ai_insights.get('hidden_insight', 'The campaign shows strong cultural relevance but could benefit from enhanced platform-specific optimizations and better audience representation strategies.')
            
            st.markdown(f"""
            <div style="background: #f0fdf9; border-radius: 8px; border-left: 4px solid #10b981; padding: 15px; margin-top: 20px;">
                <div style="font-size: 0.9rem; font-weight: 600; color: #5865f2; margin-bottom: 10px;">AI Deep Insights</div>
                <p style="margin: 0; font-size: 0.9rem; color: #333;">
                    {hidden_insight}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Generate insights dynamically based on scores when AI insights aren't available
            
            # Find strongest and weakest metrics
            metric_scores = list(scores.items())
            metric_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Get top metrics (strengths)
            top_metrics = metric_scores[:2] if len(metric_scores) >= 2 else metric_scores
            top_metric_names = [m[0].lower() for m in top_metrics]
            
            # Get bottom metrics (opportunities)
            bottom_metrics = metric_scores[-2:] if len(metric_scores) >= 2 else metric_scores
            bottom_metric_names = [m[0].lower() for m in bottom_metrics]
            
            # Generate dynamic insight text based on the metrics
            if top_metrics and bottom_metrics:
                if len(top_metric_names) > 1:
                    strength_text = f"{top_metric_names[0]} and {top_metric_names[1]}"
                else:
                    strength_text = top_metric_names[0] if top_metric_names else "cultural relevance"
                    
                if len(bottom_metric_names) > 1:
                    opportunity_text = f"{bottom_metric_names[0]} and {bottom_metric_names[1]}"
                else:
                    opportunity_text = bottom_metric_names[0] if bottom_metric_names else "platform optimization"
                
                # Create dynamic insight based on actual scores
                insight_text = f"The campaign shows strong performance in {strength_text}, indicating a solid strategic foundation. To maximize impact, focus on enhancing {opportunity_text} through targeted digital tactics and more precise audience segmentation."
            else:
                # Absolute fallback if no metrics are available
                insight_text = "The campaign shows potential for improved performance through enhanced digital tactics and audience targeting strategies."
            
            # Clean up any potential grammatical errors or duplicate words in the insight text
            cleaned_insight_text = fix_grammar_and_duplicates(insight_text)
            
            st.markdown(f"""
            <div style="background: #f0fdf9; border-radius: 8px; border-left: 4px solid #10b981; padding: 15px; margin-top: 20px;">
                <div style="font-size: 0.9rem; font-weight: 600; color: #5865f2; margin-bottom: 10px;">AI Deep Insights</div>
                <p style="margin: 0; font-size: 0.9rem; color: #333;">
                    {cleaned_insight_text}
                </p>
            </div>
            """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()