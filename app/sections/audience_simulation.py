"""
Audience Simulation section for testing marketing messages with different audience segments.
"""
import streamlit as st
import json
import time
from core.audience_simulation import (
    get_audience_profiles,
    simulate_audience_response
)
import os
import streamlit.components.v1 as components

def display_audience_simulation():
    """Display the audience simulation interface."""
    
    # Add minimal CSS for proper rendering
    st.markdown("""
    <style>
    /* Ensure proper column spacing */
    [data-testid="column"] > div {
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header section
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="color: #a855f7; margin-bottom: 10px; font-size: 2.5rem;">Audience Simulation</h1>
        <p style="color: #6b7280; font-size: 1rem; max-width: 600px; margin: 0 auto;">
            Validate marketing strategies with real audience psychology using AI-powered<br>
            behavioral modeling and emerging market intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # RFP Connection Status
    analysis_data = None
    if st.session_state.get('has_analyzed'):
        analysis_data = {
            'industry': st.session_state.get('industry', 'General'),
            'keyAudience': st.session_state.get('brand_name', 'Professional'),
            'summary': st.session_state.get('brief_text', 'Marketing campaign')[:100] + '...'
        }
    
    # Marketing Scenario section with proper Streamlit components
    with st.container():
        st.markdown("### ✨ Marketing Scenario")
        st.markdown("Test marketing messages, positioning strategies, or communication approaches with RFP-based audience segments")
        
        # Create the scenario input area
        scenario = st.text_area(
            "Enter your marketing scenario",
            placeholder="How would you respond to a car brand that offers premium features at non-premium prices, backed by a 10-year warranty?",
            height=120,
            max_chars=500,
            label_visibility="visible"
        )
        
        # Character count and button in same row
        col1, col2 = st.columns([4, 1])
        with col1:
            st.caption(f"{len(scenario)}/500 characters")
        with col2:
            simulate_button = st.button("🚀 Simulate Audience Response", type="primary", use_container_width=True)
    
    # Get audience profiles
    audience_profiles = get_audience_profiles(analysis_data)
    print("audience_profiles:")
    print(audience_profiles)
    
    # Initialize session state for simulation results if not exists
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = None
    
    # Simulation results
    if simulate_button and scenario.strip():
        with st.spinner("🔄 Simulating audience responses..."):
            simulation_results = []
            
            # Progress bar
            progress_bar = st.progress(0)
            
            # Simulate responses for all audiences
            for i, profile in enumerate(audience_profiles):
                # Update progress
                progress_bar.progress((i + 1) / len(audience_profiles))
                
                # Simulate response
                response = simulate_audience_response(profile, scenario, analysis_data)
                simulation_results.append((profile, response))
                
                # Small delay for visual effect
                time.sleep(0.3)
            
            # Clear progress bar
            progress_bar.empty()
            
            # Store results in session state
            st.session_state.simulation_results = simulation_results
    
    elif simulate_button and not scenario.strip():
        st.error("❌ Please enter a marketing scenario to simulate audience responses.")
    
    # Only display cards after simulation button is clicked and we have results
    if st.session_state.simulation_results:
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        
        
        # Always use 4 columns, CSS will handle responsive behavior
        cols = st.columns(4, gap="small")
        for i, (profile, response) in enumerate(st.session_state.simulation_results[:4]):
            with cols[i]:
                display_audience_response_card(profile, response)

def display_audience_response_card(profile, response):
    """Display a single audience response card using Streamlit components."""
    print(f"Displaying card for profile: {profile['name']}")
    print(response)

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    HTML_FILE_PATH = os.path.join(PARENT_DIR, "static", "Simulation/index.html") 

    try:
        with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
            html_code = f.read()

        # Embed the HTML content
        # You can adjust height and scrolling as needed.
        # For a full-page-like experience, you might need a large height.
        # `scrolling=True` allows the component to have its own scrollbar if content overflows.
        # st.components.v1.html(html_code, height=800)
        html_code = html_code.replace("{{SIMULATION_RESPONSE}}", json.dumps(response))
        html_code = html_code.replace("{{ID}}", profile.get('id', 'rfp-core-audience'))
        components.html(html_code, height=900, scrolling=True)

    except FileNotFoundError:
        st.error(f"ERROR: The HTML file was not found at '{HTML_FILE_PATH}'.")
        st.info("Please make sure 'index.html' is in the correct location.")
    except Exception as e:
        st.error(f"An error occurred: {e}")


    # Determine card header gradient based on profile type (matching TypeScript file)
    # header_gradients = {
    #     'Core Target Audience': 'linear-gradient(135deg, #475569 0%, #374151 100%)',  # slate-600 to gray-700
    #     'RFP Core Audience': 'linear-gradient(135deg, #475569 0%, #374151 100%)',     # slate-600 to gray-700
    #     'Growth Audience 1 - Urban Explorers': 'linear-gradient(135deg, #10b981 0%, #2563eb 100%)',  # emerald-500 to blue-600
    #     'Growth Audience 2 - Global Nomads': 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',    # purple-500 to pink-600
    #     'Emerging Audience 3 - Cultural Enthusiasts': 'linear-gradient(135deg, #f97316 0%, #dc2626 100%)'  # orange-500 to red-600
    # }
    
    # # Get header gradient
    # header_gradient = 'linear-gradient(135deg, #475569 0%, #374151 100%)'  # Default gray gradient
    # for key, gradient in header_gradients.items():
    #     if key in profile['name'] or profile['name'] in key:
    #         header_gradient = gradient
    #         break
    
    # # Create card container with styling
    # with st.container():
        # Card styling
        # st.markdown(f"""
        # <style>
        # .card-{profile['id']} {{
        #     background: white;
        #     border-radius: 8px;
        #     overflow: hidden;
        #     box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        #     margin-bottom: 20px;
        # }}
        # .card-header-{profile['id']} {{
        #     background: {header_gradient};
        #     color: white;
        #     padding: 15px;
        # }}
        # </style>
        # """, unsafe_allow_html=True)
        
        # # Card header
        # st.markdown(f"""
        # <div class="card-{profile['id']}">
        #     <div class="card-header-{profile['id']}">
        #         <div style="display: flex; align-items: center;">
        #             <span style="font-size: 20px; margin-right: 8px;">{profile['icon']}</span>
        #             <div>
        #                 <div style="font-weight: 600; font-size: 1rem;">{profile['name']}</div>
        #                 <div style="font-size: 0.85rem; opacity: 0.9;">{profile['description']}</div>
        #             </div>
        #         </div>
        #     </div>
        # </div>
        # """, unsafe_allow_html=True)
        
        # # Card content using Streamlit components
        # with st.container():
        #     # Quote
        #     st.info(f'"{response["quote"]}"')
            
        #     # Metrics header - centered
        #     st.markdown("<h4 style='text-align: center; margin: 20px 0 15px 0; color: #1f2937;'>Audience Resonance Analysis</h4>", unsafe_allow_html=True)
            
        #     # Overall feeling with background
        #     sentiment_colors = {
        #         'positive': '#10b981',
        #         'negative': '#ef4444',
        #         'neutral': '#f59e0b'
        #     }
        #     sentiment_color = sentiment_colors.get(response['sentiment'], '#f59e0b')
            
        #     # Display metrics with styled backgrounds
        #     st.markdown(f"""
        #     <div style="margin-bottom: 8px;">
        #         <div style="background: #f3f4f6; padding: 10px 15px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
        #             <span style="color: #6b7280; font-size: 0.9rem;">Overall Feeling</span>
        #             <span style="color: {sentiment_color}; font-weight: 600; font-size: 1.1rem;">{response['sentiment'].capitalize()}</span>
        #         </div>
        #     </div>
            
        #     <div style="margin-bottom: 8px;">
        #         <div style="background: #e0e7ff; padding: 10px 15px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
        #             <span style="color: #6b7280; font-size: 0.9rem;">Resonance Score</span>
        #             <span style="color: #4f46e5; font-weight: 600; font-size: 1.2rem;">{response['resonanceScore']} <span style="color: #9ca3af; font-size: 0.9rem;">/10</span></span>
        #         </div>
        #     </div>
            
        #     <div style="margin-bottom: 8px;">
        #         <div style="background: #f3e8ff; padding: 10px 15px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
        #             <span style="color: #6b7280; font-size: 0.9rem;">Engagement Level</span>
        #             <span style="color: #9333ea; font-weight: 600; font-size: 1.2rem;">{response['engagementLevel']} <span style="color: #9ca3af; font-size: 0.9rem;">/10</span></span>
        #         </div>
        #     </div>
            
        #     <div style="margin-bottom: 15px;">
        #         <div style="background: #d1fae5; padding: 10px 15px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
        #             <span style="color: #6b7280; font-size: 0.9rem;">Conversion Potential</span>
        #             <span style="color: #059669; font-weight: 600; font-size: 1.2rem;">{response['conversionPotential']} <span style="color: #9ca3af; font-size: 0.9rem;">/10</span></span>
        #         </div>
        #     </div>
        #     """, unsafe_allow_html=True)
            
        #     # Key insights
        #     st.markdown("**Key Insights:**")
        #     for insight in response['keyInsights'][:2]:
        #         st.markdown(f"• {insight}")

