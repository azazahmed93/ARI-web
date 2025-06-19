from core.analysis import (
    analyze_campaign_brief, 
    calculate_benchmark_percentile, 
    get_improvement_areas,
    extract_brand_info
)
from core.utils import (
    extract_text_from_file,
)
from assets.styles import header_section, render_footer
from core.database import BLOCKED_KEYWORDS

from app.sections.results import display_results
import streamlit as st

# Import the grammar fix function from ai_insights module
# This helps clean up grammatical errors and duplicate words
from core.ai_insights import (
    generate_deep_insights,
    generate_competitor_analysis,
    generate_audience_segments,
    get_default_audience_segments,
    generate_recommended_dmas,
    generate_audience_reach,
    generate_market_insights,
)

from components.spinner import get_random_spinner_message
from assets.styles import apply_styles
from core.ai_insights import generate_core_audience_summary, generate_primary_audience_signal, generate_secondary_audience_signal


def landing_layout(inner_content):

        # Apply custom styles
    apply_styles()

    # Hide sidebar
    hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        [data-testid="stSidebarCollapsedControl"] { display: none; }
    </style>
    """

    st.markdown(hide_sidebar_style, unsafe_allow_html=True)

    with open("assets/styles.css", "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    
    # Display header
    header_section()
    
    # Two-column layout for the banner image
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Create an animated data visualization that looks more sophisticated
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
        st.markdown("Analyze your Advertising RFP or Marketing Brief to leverage our AI-powered Audience Resonance Index framework. We employ computational ethnography and cultural intelligence algorithms to forecast resonance patterns, identify opportunity vectors, and optimize cross-cultural alignment before campaign activation.")
        
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
                    # time.sleep(1.5)
                    
                    # Analyze the content
                    result = analyze_campaign_brief(brief_text)
                    
                    print("result")
                    print(result)
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
                        
                        # Initialize DMA data with default values
                        # This ensures we have DMA data even without OpenAI
                        default_dmas = [501, 803, 602, 807]  # NYC, LA, Chicago, SF
                        default_audience_reach = [
                            {"name": "New York, NY", "audienceReach": 2.8},
                            {"name": "Los Angeles, CA", "audienceReach": 2.1},
                            {"name": "Chicago, IL", "audienceReach": 1.3},
                            {"name": "San Francisco-Oakland-San Jose, CA", "audienceReach": 1.0},
                            {"name": "National Campaign", "audienceReach": 28.5}
                        ]
                        default_market_insights = {
                            "primaryMarketName": "New York",
                            "primaryMarketAudience": "Urban Professionals",
                            "totalAddressableAudience": 7.2
                        }
                        
                        st.session_state.recommended_dmas = default_dmas
                        st.session_state.audience_reach = default_audience_reach
                        st.session_state.market_insights = default_market_insights
                        st.session_state.dma_analysis = {
                            "recommendedDMAs": default_dmas,
                            "audienceReach": default_audience_reach,
                            "marketInsights": default_market_insights
                        }
                        
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
                                        segments = st.session_state.audience_segments.get('segments', [])
                                        
                                        # Generate audience summaries if we have the required data
                                        if 'audience_insights' in st.session_state and 'audience_media_consumption' in st.session_state:
                                            if 'audience_summary' not in st.session_state:
                                                st.session_state.audience_summary = {}
                                            st.session_state.audience_summary['core_audience'] = generate_core_audience_summary(st.session_state.audience_insights, st.session_state.audience_media_consumption, brief_text)
                                            st.session_state.audience_summary['primary_audience'] = generate_primary_audience_signal(st.session_state.audience_insights, st.session_state.audience_media_consumption, segments[0].get('name'), brief_text)
                                            st.session_state.audience_summary['secondary_audience'] = generate_secondary_audience_signal(st.session_state.audience_insights, st.session_state.audience_media_consumption, segments[1].get('name'), brief_text)
                                    
                                    # Generate DMA recommendations
                                    recommended_dmas = generate_recommended_dmas(brief_text, st.session_state.audience_segments)
                                    st.session_state.recommended_dmas = recommended_dmas
                                    
                                    # Generate audience reach for recommended DMAs
                                    audience_reach = generate_audience_reach(recommended_dmas, st.session_state.audience_segments, industry)
                                    st.session_state.audience_reach = audience_reach
                                    
                                    # Generate market insights
                                    # Get primary audience (first segment)
                                    primary_audience = None
                                    if 'segments' in st.session_state.audience_segments and len(st.session_state.audience_segments['segments']) > 0:
                                        primary_audience = st.session_state.audience_segments['segments'][0]
                                    
                                    market_insights = generate_market_insights(
                                        recommended_dmas,
                                        primary_audience,
                                        st.session_state.audience_segments,
                                        audience_reach
                                    )
                                    st.session_state.market_insights = market_insights
                                    
                                    # Store the complete DMA analysis data
                                    st.session_state.dma_analysis = {
                                        "recommendedDMAs": recommended_dmas,
                                        "audienceReach": audience_reach,
                                        "marketInsights": market_insights
                                    }
                                    
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

    if callable(inner_content):
        inner_content(
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

