from core.analysis import (
    analyze_campaign_brief,
    calculate_benchmark_percentile,
    get_improvement_areas
)
from core.utils import (
    extract_text_from_file,
)
from assets.styles import header_section, render_footer
from core.database import BLOCKED_KEYWORDS

from app.sections.results import display_results
from app.components.psychographic_input import psychographic_input_section, process_psychographic_config
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Global storage for background thread results (thread-safe)
_journey_results = {}
_journey_lock = threading.Lock()

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
from core.brief_journey import generate_journey_from_brief

from components.spinner import get_random_spinner_message
from assets.styles import apply_styles
from core.ai_insights import generate_core_audience_summary, generate_primary_audience_signal, generate_secondary_audience_signal
from core.journey_environments import generate_resonance_scores, generate_retargeting_channels
from core.consumer_journey import generate_consumer_journey_from_brief
import requests
import jwt
import os

def run_parallel_tasks(tasks):
    """
    Execute multiple tasks in parallel using ThreadPoolExecutor.

    Args:
        tasks: List of dicts with 'name', 'func', and 'args' keys

    Returns:
        dict: Results keyed by task name
    """
    results = {}
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        future_to_name = {
            executor.submit(task['func'], *task['args']): task['name']
            for task in tasks
        }

        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                results[name] = future.result()
            except Exception as e:
                print(f"Error in {name}: {str(e)}")
                results[name] = None

    return results


def call_lambda_journey_sync_in_background(lambda_url, token, payload, journey_type, request_id):
    """
    Call the Lambda sync endpoint in a background thread.
    Stores the result in global _journey_results dict (thread-safe).

    Args:
        request_id: Unique ID for this request (to avoid conflicts)
    """
    def _make_request():
        import time
        start_time = time.time()

        try:
            print(f"🔄 Background thread: Starting journey generation (type={journey_type}, request_id={request_id})...")
            response = requests.post(
                f"{lambda_url}/journey/generate-sync",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                json=payload,
                timeout=900  # 15 minutes
            )

            if response.status_code in [200, 202]:
                end_time = time.time()
                duration_sec = end_time - start_time
                result = response.json()
                print(f"✅ Background thread: Journey generation completed in {duration_sec:.2f} seconds ({duration_sec/60:.2f} minutes)")

                # Get task_id from Lambda response
                task_id = result.get("task_id")

                # Store result in GLOBAL dict (thread-safe)
                with _journey_lock:
                    if "result" in result:
                        _journey_results[request_id] = {
                            'status': 'completed',
                            'task_id': task_id,
                            'journey_type': journey_type,
                            'result': result["result"]
                        }
                        print(f"✅ Stored result in global dict: request_id={request_id}, task_id={task_id}")
                    else:
                        _journey_results[request_id] = {
                            'status': 'completed',
                            'task_id': task_id,
                            'journey_type': journey_type,
                            'result': None
                        }
            else:
                end_time = time.time()
                duration_sec = end_time - start_time
                print(f"❌ Background thread: Failed after {duration_sec:.2f} seconds - HTTP {response.status_code}")
                with _journey_lock:
                    _journey_results[request_id] = {
                        'status': 'failed',
                        'error': f"HTTP {response.status_code}: {response.text}"
                    }
        except Exception as e:
            end_time = time.time()
            duration_sec = end_time - start_time
            print(f"❌ Background thread: Exception after {duration_sec:.2f} seconds - {e}")
            with _journey_lock:
                _journey_results[request_id] = {
                    'status': 'failed',
                    'error': str(e)
                }

    # Start background thread
    thread = threading.Thread(target=_make_request, daemon=True)
    thread.start()

    print(f"✅ Background thread started for journey generation (request_id={request_id})")
    return thread


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
        from datetime import datetime, timedelta

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
                # st.markdown("<div style='background: #f8fafc; padding: 12px; border-radius: 8px; margin-top: 12px;'>", unsafe_allow_html=True)
                # st.markdown(f"<div style='font-weight: 500;'>File Details:</div>", unsafe_allow_html=True)
                # for key, value in file_details.items():
                #     st.markdown(f"<div style='font-size: 0.9rem; margin-top: 5px;'><span style='color: #64748b;'>{key}:</span> {value}</div>", unsafe_allow_html=True)
                # st.markdown("</div>", unsafe_allow_html=True)
                
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
        
        # Add psychographic input section before analysis button
        if brief_text:
            st.markdown("---")
            psychographic_input_section(brief_text)
        
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
                # Check for validation errors in psychographic config
                has_validation_error = False
                if 'psychographic_config' in st.session_state:
                    config = st.session_state.psychographic_config
                    if config.get('method') == 'generate':
                        # Check if age range has validation error
                        age_input = st.session_state.get('config_age', '')
                        if age_input and age_input.strip():
                            import re
                            age_pattern = r'^(\d{1,3})\s*[-–]\s*(\d{1,3})$'
                            match = re.match(age_pattern, age_input.strip())
                            if not match:
                                st.error("❌ Please fix the age range format before running analysis")
                                has_validation_error = True
                            elif match:
                                min_age, max_age = int(match.group(1)), int(match.group(2))
                                if min_age < 0 or max_age > 120 or min_age >= max_age:
                                    st.error("❌ Please fix the age range values before running analysis")
                                    has_validation_error = True
                
                if not has_validation_error:
                    # Reset journey-related session state for new analysis
                    st.session_state.journey_request_id = None
                    st.session_state.journey_task_id = None
                    st.session_state.journey_status = None
                    st.session_state.journey_start_time = None
                    st.session_state.brief_journey_data = None
                    st.session_state.consumer_journey_data = None
                    st.session_state.journey_ad_format_scores = None
                    st.session_state.journey_programming_show_scores = None
                    st.session_state.journey_retargeting_channels = None
                    st.session_state.journey_audience_profile = None
                    st.session_state.journey_campaign_objectives = None
                    st.session_state.simulation_results = None

                    with st.spinner(get_random_spinner_message()):
                        # Process psychographic configuration if exists
                        demographics_info = None
                        if 'psychographic_config' in st.session_state:
                            # Extract demographics info for use in audience segments
                            config = st.session_state.psychographic_config
                            if config.get('method') == 'generate':
                                demo = config.get('demographics', {})
                                demo_parts = []
                                if demo.get('age'):
                                    demo_parts.append(f"Age: {demo['age']}")
                                if demo.get('gender'):
                                    demo_parts.append(f"Gender: {demo['gender']}")
                                if demo.get('income'):
                                    demo_parts.append(f"Income: {demo['income']}")
                                if demo.get('location'):
                                    demo_parts.append(f"Location: {demo['location']}")
                                demographics_info = " | ".join(demo_parts) if demo_parts else None
                            
                            psychographic_insights = process_psychographic_config(brief_text)
                            if psychographic_insights:
                                st.session_state.audience_insights = psychographic_insights
                        
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
                            import time
                            start_time = time.time()

                            with st.spinner(get_random_spinner_message()):
                                print("=" * 60)
                                print("Starting parallel API call execution...")
                                print("=" * 60)

                                # Generate AI-powered insights for enhanced analysis
                                try:

                                    # Phase 1: Run independent API calls in parallel
                                    phase1_tasks = [
                                        {
                                            'name': 'ai_insights',
                                            'func': generate_deep_insights,
                                            'args': (brief_text, scores)
                                        },
                                        {
                                            'name': 'competitor_analysis',
                                            'func': generate_competitor_analysis,
                                            'args': (brief_text, industry)
                                        },
                                        {
                                            'name': 'audience_segments',
                                            'func': generate_audience_segments,
                                            'args': (brief_text, scores, demographics_info)
                                        }
                                    ]

                                    phase1_start = time.time()
                                    phase1_results = run_parallel_tasks(phase1_tasks)
                                    phase1_time = time.time() - phase1_start
                                    print(f"\n✓ Phase 1 completed in {phase1_time:.2f} seconds")
                                    print(f"  - Generated: AI insights, Competitor analysis, Audience segments")

                                    # Store Phase 1 results in session state
                                    if phase1_results.get('ai_insights'):
                                        st.session_state.ai_insights = phase1_results['ai_insights']

                                    if phase1_results.get('competitor_analysis'):
                                        st.session_state.competitor_analysis = phase1_results['competitor_analysis']

                                    # Only replace audience segments if AI generation was successful
                                    ai_audience_segments = phase1_results.get('audience_segments')
                                    if ai_audience_segments and 'segments' in ai_audience_segments:
                                        st.session_state.audience_segments = ai_audience_segments
                                        segments = st.session_state.audience_segments.get('segments', [])

                                        # Phase 1b: Enrich segments with Census Bureau demographics in parallel
                                        print("\n" + "=" * 60)
                                        print("Starting Census API integration (Phase 1b)...")
                                        print("=" * 60)

                                        try:
                                            from core.census_api import fetch_census_demographics, fetch_census_trends, map_state_to_fips
                                            from core.behavioral_adjustments import enrich_audience_with_demographics
                                            from core.language_recommendations import enrich_segment_with_language_recommendations

                                            def enrich_single_segment(segment):
                                                """Helper function to enrich a single segment with Census data and language recommendations"""
                                                # Get primary state from AI-generated segment
                                                primary_state = segment.get('primary_state')

                                                if not primary_state:
                                                    print(f"⚠ No primary state found for '{segment.get('name')}', skipping Census enrichment")
                                                    return segment

                                                # Map state name to FIPS code
                                                state_fips = map_state_to_fips(primary_state)

                                                if not state_fips:
                                                    print(f"⚠ Could not map '{primary_state}' to FIPS code, skipping Census enrichment")
                                                    return segment

                                                print(f"  Fetching Census data for '{segment.get('name')}' in {primary_state}...")

                                                # Fetch Census data
                                                census_data = fetch_census_demographics(state_fips, year=2024)

                                                if not census_data:
                                                    print(f"⚠ Could not fetch Census data for {primary_state}, skipping enrichment")
                                                    return segment

                                                # Fetch trends (optional, don't fail if not available)
                                                trends_data = None
                                                try:
                                                    trends_data = fetch_census_trends(state_fips, years=[2023, 2024])
                                                except Exception as e:
                                                    print(f"  Could not fetch trends for {primary_state}: {e}")

                                                # Enrich segment with Census data and behavioral adjustments
                                                enriched_segment = enrich_audience_with_demographics(
                                                    segment,
                                                    census_data,
                                                    trends_data
                                                )

                                                print(f"  ✓ Enriched '{segment.get('name')}' with Census demographics")

                                                # Enrich with language recommendations based on demographics
                                                enriched_segment = enrich_segment_with_language_recommendations(enriched_segment)

                                                return enriched_segment

                                            # Create parallel tasks for each segment
                                            phase1b_tasks = [
                                                {
                                                    'name': f'enrich_segment_{i}',
                                                    'func': enrich_single_segment,
                                                    'args': (segment,)
                                                }
                                                for i, segment in enumerate(segments)
                                            ]

                                            # Execute enrichment tasks in parallel
                                            phase1b_start = time.time()
                                            phase1b_results = run_parallel_tasks(phase1b_tasks)
                                            phase1b_time = time.time() - phase1b_start

                                            # Collect enriched segments (maintain order)
                                            enriched_segments = [
                                                phase1b_results.get(f'enrich_segment_{i}', segment)
                                                for i, segment in enumerate(segments)
                                            ]

                                            # Update session state with enriched segments
                                            print("enriched_segments")
                                            print(enriched_segments)
                                            st.session_state.audience_segments['segments'] = enriched_segments
                                            segments = enriched_segments

                                            print(f"\n✓ Phase 1b completed in {phase1b_time:.2f} seconds")
                                            print(f"  - Enriched {len(enriched_segments)} segments with Census data")

                                        except ImportError as e:
                                            print(f"⚠ Census API integration not available: {e}")
                                        except Exception as e:
                                            print(f"⚠ Error during Census enrichment: {e}")
                                            # Continue without Census data if there's an error
                                        
                                        # Phase 2: Generate audience summaries and journey data in parallel
                                        # These depend on Phase 1 results (audience_segments)
                                        if 'audience_insights' in st.session_state and 'audience_media_consumption' in st.session_state:
                                            phase2_tasks = [
                                                {
                                                    'name': 'core_audience',
                                                    'func': generate_core_audience_summary,
                                                    'args': (st.session_state.audience_insights, st.session_state.audience_media_consumption, brief_text)
                                                },
                                                {
                                                    'name': 'primary_audience',
                                                    'func': generate_primary_audience_signal,
                                                    'args': (st.session_state.audience_insights, st.session_state.audience_media_consumption, segments[0].get('name'), brief_text)
                                                },
                                                {
                                                    'name': 'secondary_audience',
                                                    'func': generate_secondary_audience_signal,
                                                    'args': (st.session_state.audience_insights, st.session_state.audience_media_consumption, segments[1].get('name'), brief_text)
                                                }
                                            ]

                                            # NOTE: Journey generation removed from Phase 2
                                            # It will be generated asynchronously via Lambda API

                                            # Execute Phase 2 tasks in parallel (summaries only)
                                            phase2_start = time.time()
                                            phase2_results = run_parallel_tasks(phase2_tasks)
                                            phase2_time = time.time() - phase2_start
                                            print(f"\n✓ Phase 2 completed in {phase2_time:.2f} seconds")
                                            print(f"  - Generated: Audience summaries")

                                            # Store Phase 2 results in session state
                                            if 'audience_summary' not in st.session_state:
                                                st.session_state.audience_summary = {}

                                            if phase2_results.get('core_audience'):
                                                st.session_state.audience_summary['core_audience'] = phase2_results['core_audience']
                                            if phase2_results.get('primary_audience'):
                                                st.session_state.audience_summary['primary_audience'] = phase2_results['primary_audience']
                                            if phase2_results.get('secondary_audience'):
                                                st.session_state.audience_summary['secondary_audience'] = phase2_results['secondary_audience']

                                            # Initiate async journey generation via Lambda API
                                            if not st.session_state.get('journey_task_id'):
                                                try:
                                                    lambda_url = os.environ.get('LAMBDA_URL')
                                                    jwt_secret = os.environ.get('LAMBDA_JWT_SECRET')

                                                    if lambda_url and jwt_secret:
                                                        # Generate JWT token
                                                        payload = {
                                                            'exp': datetime.utcnow() + timedelta(hours=1),
                                                            'iat': datetime.utcnow()
                                                        }
                                                        token = jwt.encode(payload, jwt_secret, algorithm='HS256')
                                                        print("token")
                                                        print(token)

                                                        # Extract audience names from segments
                                                        audience_growth1 = segments[0].get('name', '') if len(segments) > 0 else None
                                                        audience_growth2 = segments[1].get('name', '') if len(segments) > 1 else None
                                                        audience_emerging = segments[2].get('name', '') if len(segments) > 2 else None

                                                        # Determine journey type based on user role
                                                        journey_type = "consumer" if st.session_state.get('is_gm_user') else "brief"

                                                        # Prepare payload based on journey type
                                                        payload = {
                                                            "journey_type": journey_type,
                                                            "brief_content": brief_text,
                                                            "industry": industry,
                                                            "audience_growth1": audience_growth1,
                                                            "audience_growth2": audience_growth2,
                                                            "audience_emerging": audience_emerging
                                                        }

                                                        # Add journey-type-specific audience field
                                                        if journey_type == "consumer":
                                                            payload["audience_core"] = "Core Audience"
                                                        else:
                                                            payload["audience_primary"] = "Primary Target Audience"

                                                        # Call Lambda sync endpoint in background thread
                                                        print(f"\n🚀 Initiating Lambda journey generation in background (type={journey_type})...")

                                                        # Generate unique request_id for this journey generation
                                                        import uuid
                                                        request_id = str(uuid.uuid4())

                                                        # Set initial status
                                                        st.session_state.journey_request_id = request_id
                                                        st.session_state.journey_status = "processing"
                                                        st.session_state.journey_start_time = datetime.now().timestamp()
                                                        print(f"✅ Journey generation initiated with request_id={request_id}")

                                                        # Start background thread (non-blocking)
                                                        call_lambda_journey_sync_in_background(
                                                            lambda_url=lambda_url,
                                                            token=token,
                                                            payload=payload,
                                                            journey_type=journey_type,
                                                            request_id=request_id
                                                        )
                                                    else:
                                                        print("⚠️  Lambda API not configured (LAMBDA_URL or LAMBDA_JWT_SECRET missing)")

                                                except Exception as e:
                                                    print(f"❌ Error calling Lambda: {e}")
                                                    st.session_state.journey_task_id = None

                                    # Generate DMA recommendations
                                    # recommended_dmas = generate_recommended_dmas(brief_text, st.session_state.audience_segments)
                                    # st.session_state.recommended_dmas = recommended_dmas
                                    
                                    # Generate audience reach for recommended DMAs
                                    # audience_reach = generate_audience_reach(recommended_dmas, st.session_state.audience_segments, industry)
                                    # st.session_state.audience_reach = audience_reach
                                    
                                    # Generate market insights
                                    # Get primary audience (first segment)
                                    primary_audience = None
                                    if 'segments' in st.session_state.audience_segments and len(st.session_state.audience_segments['segments']) > 0:
                                        primary_audience = st.session_state.audience_segments['segments'][0]
                                    
                                    # market_insights = generate_market_insights(
                                    #     recommended_dmas,
                                    #     primary_audience,
                                    #     st.session_state.audience_segments,
                                    #     audience_reach
                                    # )
                                    # st.session_state.market_insights = market_insights
                                    
                                    # Store the complete DMA analysis data
                                    # st.session_state.dma_analysis = {
                                    #     "recommendedDMAs": recommended_dmas,
                                    #     "audienceReach": audience_reach,
                                    #     "marketInsights": market_insights
                                    # }
                                    
                                except Exception as e:
                                    # Show more specific error messages
                                    error_msg = str(e).lower()
                                    if "rate limit" in error_msg:
                                        print("⏱️ OpenAI API rate limit reached. Please wait a moment and try again.")
                                    elif "timeout" in error_msg:
                                        print("⌛ Request timed out. The AI service might be experiencing high load. Please try again.")
                                    elif "api key" in error_msg or "authentication" in error_msg:
                                        print("🔑 API key issue detected. Please check your OpenAI API key configuration.")
                                    elif "failed to get response" in error_msg:
                                        print("🔄 Unable to connect to AI service after multiple attempts. Using fallback analysis.")
                                    else:
                                        print(f"Enhanced AI analysis encountered an issue: {str(e)}")
                                    
                                    st.session_state.ai_insights = None
                                    st.session_state.competitor_analysis = None
                                    st.session_state.brief_journey_data = None

                            # Generate Journey Environments resonance scores
                            # Only generate if not already present and OpenAI is available
                            if (st.session_state.journey_ad_format_scores is None or
                                st.session_state.journey_programming_show_scores is None or
                                st.session_state.journey_retargeting_channels is None):

                                try:
                                    # Build audience profile from existing data
                                    audience_profile = None
                                    if st.session_state.get('audience_insights'):
                                        # Extract richer demographics from audience_segments if available
                                        primary_segment = None
                                        if st.session_state.get('audience_segments'):
                                            segments = st.session_state.audience_segments.get('segments', [])
                                            if segments and len(segments) > 0:
                                                primary_segment = segments[0]

                                        # Determine demographics from multiple sources
                                        age_range = st.session_state.audience_insights.get("age_range", "35-54")
                                        income_level = st.session_state.audience_insights.get("income_level", "HHI $150K+")

                                        # Extract from primary segment if available
                                        if primary_segment:
                                            targeting_params = primary_segment.get('targeting_params', {})
                                            age_range = targeting_params.get('age_range', age_range)
                                            income_level = targeting_params.get('income_targeting', income_level)

                                        # Infer profession from segment name or brief
                                        profession = "professionals"
                                        if primary_segment:
                                            segment_name = primary_segment.get('name', '').lower()
                                            if 'tech' in segment_name or 'digital' in segment_name:
                                                profession = "tech professionals"
                                            elif 'stream' in segment_name or 'entertainment' in segment_name:
                                                profession = "entertainment enthusiasts"
                                            elif 'lifestyle' in segment_name or 'culture' in segment_name:
                                                profession = "lifestyle professionals"
                                            elif 'sport' in segment_name or 'athletic' in segment_name:
                                                profession = "sports enthusiasts"

                                        # Determine affluence from income level
                                        affluence = "affluent"
                                        income_lower = income_level.lower()
                                        if any(term in income_lower for term in ['high', '100k+', '150k+', 'premium', 'luxury']):
                                            affluence = "affluent"
                                        elif any(term in income_lower for term in ['mid', 'middle', '50k-100k']):
                                            affluence = "middle class"
                                        elif any(term in income_lower for term in ['low', 'budget', '25k-50k']):
                                            affluence = "budget-conscious"

                                        audience_profile = {
                                            "demographics": {
                                                "ageRange": age_range,
                                                "profession": profession,
                                                "incomeLevel": income_level,
                                                "affluence": affluence
                                            },
                                            "psychographics": st.session_state.audience_insights
                                        }

                                    # Build campaign objectives from brief
                                    campaign_objectives = ["brand awareness", "audience engagement"]
                                    if st.session_state.brief_text:
                                        # Extract objectives from brief
                                        brief_lower = st.session_state.brief_text.lower()
                                        if "conversion" in brief_lower or "sales" in brief_lower:
                                            campaign_objectives.append("conversions")
                                        if "awareness" in brief_lower:
                                            campaign_objectives.append("brand awareness")
                                        if "engagement" in brief_lower:
                                            campaign_objectives.append("engagement")

                                    # Store in session state for component
                                    st.session_state.journey_audience_profile = audience_profile
                                    st.session_state.journey_campaign_objectives = campaign_objectives

                                    # Extract audience summaries for Phase 3
                                    core_audience_summary = None
                                    primary_audience_summary = None
                                    secondary_audience_summary = None

                                    if 'audience_summary' in st.session_state:
                                        core_audience_summary = st.session_state.audience_summary.get('core_audience')
                                        primary_audience_summary = st.session_state.audience_summary.get('primary_audience')
                                        secondary_audience_summary = st.session_state.audience_summary.get('secondary_audience')

                                    # Phase 3: Generate resonance scores and retargeting recommendations in parallel
                                    phase3_tasks = [
                                        {
                                            'name': 'resonance_scores',
                                            'func': generate_resonance_scores,
                                            'args': (audience_profile, campaign_objectives, core_audience_summary, primary_audience_summary, secondary_audience_summary)
                                        },
                                        {
                                            'name': 'retargeting_channels',
                                            'func': generate_retargeting_channels,
                                            'args': (audience_profile, campaign_objectives, core_audience_summary, primary_audience_summary, secondary_audience_summary)
                                        }
                                    ]

                                    phase3_start = time.time()
                                    print("\nGenerating journey environments resonance scores and retargeting channels...")
                                    phase3_results = run_parallel_tasks(phase3_tasks)
                                    phase3_time = time.time() - phase3_start
                                    print(f"\n✓ Phase 3 completed in {phase3_time:.2f} seconds")
                                    print(f"  - Generated: Resonance scores, Programming shows, Retargeting channels")

                                    # Store results in session state
                                    journey_scores = phase3_results.get('resonance_scores')
                                    retargeting_channels = phase3_results.get('retargeting_channels')

                                    if journey_scores:
                                        st.session_state.journey_ad_format_scores = journey_scores.get("ad_format_scores")
                                        st.session_state.journey_programming_show_scores = journey_scores.get("programming_show_scores")

                                        ad_count = len(st.session_state.journey_ad_format_scores or {})
                                        show_count = len(st.session_state.journey_programming_show_scores or {})

                                        print(f"Generated scores for {ad_count} ad formats and {show_count} shows")

                                    if retargeting_channels:
                                        st.session_state.journey_retargeting_channels = retargeting_channels
                                        retarget_count = len(retargeting_channels)
                                        print(f"Generated {retarget_count} retargeting channel recommendations")

                                except Exception as e:
                                    print(f"Error generating journey environments resonance scores: {e}")

                            # Log total execution time
                            total_time = time.time() - start_time
                            print("\n" + "=" * 60)
                            print(f"🎉 All API calls completed!")
                            print(f"⏱️  Total execution time: {total_time:.2f} seconds")
                            print("=" * 60)

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

