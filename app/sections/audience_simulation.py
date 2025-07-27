"""
Audience Simulation section for testing marketing messages with different audience segments.
"""
import streamlit as st
import time
from core.audience_simulation import (
    get_audience_profiles,
    simulate_audience_response
)

def display_audience_simulation():
    """Display the audience simulation interface."""
    
    # Header section
    st.markdown("# 🎭 Audience Simulation")
    st.markdown("Validate marketing strategies with real audience psychology using AI-powered behavioral modeling and emerging market intelligence")
    
    # Add some spacing
    st.markdown("---")
    
    # RFP Connection Status
    analysis_data = None
    if st.session_state.get('has_analyzed'):
        analysis_data = {
            'industry': st.session_state.get('industry', 'General'),
            'keyAudience': st.session_state.get('brand_name', 'Professional'),
            'summary': st.session_state.get('brief_text', 'Marketing campaign')[:100] + '...'
        }
        
        st.success(f"✅ Connected to RFP Analysis: {analysis_data['industry']} - {analysis_data['keyAudience']}")
    else:
        st.info("ℹ️ Using market intelligence and trending insights - Upload an RFP in Dashboard for RFP-specific audience analysis")
    
    # Marketing Scenario Input
    st.markdown("### ✨ Marketing Scenario")
    st.markdown("Test marketing messages, positioning strategies, or communication approaches with RFP-based audience segments")
    
    scenario = st.text_area(
        "Enter your marketing scenario",
        placeholder="e.g., How would you respond to a sustainability-focused brand message? What's your reaction to premium pricing for wellness products? How do you feel about digital-first marketing approaches?",
        height=100,
        max_chars=500
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"{len(scenario)}/500 characters")
    with col2:
        simulate_button = st.button("🚀 Simulate Response", type="primary", use_container_width=True)
    
    # Get audience profiles
    audience_profiles = get_audience_profiles(analysis_data)
    
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
            st.success("✅ Simulation complete!")
    
    elif simulate_button and not scenario.strip():
        st.error("❌ Please enter a marketing scenario to simulate audience responses.")
    
    # Display results or empty state
    st.markdown("---")
    
    if st.session_state.simulation_results:
        # Display existing results in a 2x2 grid
        st.markdown("### 📊 Audience Responses")
        
        # Create two rows with two columns each
        for row in range(2):
            cols = st.columns(2)
            for col_idx in range(2):
                profile_idx = row * 2 + col_idx
                if profile_idx < len(st.session_state.simulation_results):
                    profile, response = st.session_state.simulation_results[profile_idx]
                    with cols[col_idx]:
                        display_audience_response_card(profile, response)
    else:
        # Display empty state cards
        st.markdown("### 👥 Audience Profiles")
        st.markdown("*Enter a scenario above to see how these audiences respond*")
        
        # Create two rows with two columns each
        for row in range(2):
            cols = st.columns(2)
            for col_idx in range(2):
                profile_idx = row * 2 + col_idx
                if profile_idx < len(audience_profiles):
                    profile = audience_profiles[profile_idx]
                    with cols[col_idx]:
                        display_empty_audience_card(profile)

def display_audience_response_card(profile, response):
    """Display a single audience response card using Streamlit components."""

    print("Displaying audience response card:")
    print(response)
    
    with st.container():
        # Card header
        st.markdown(f"### {profile['icon']} {profile['name']}")
        st.caption(profile['description'])
        
        # Sentiment indicator
        sentiment_color = {
            'positive': '🟢',
            'negative': '🔴',
            'neutral': '🟡'
        }
        sentiment_emoji = sentiment_color.get(response['sentiment'], '🟡')
        st.markdown(f"**Overall Feeling:** {sentiment_emoji} {response['sentiment'].capitalize()}")
        
        # Quote
        st.info(f'"{response["quote"]}"')
        
        # Metrics in columns
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("Resonance Score", f"{response['resonanceScore']}/10")
        with metric_cols[1]:
            st.metric("Engagement Level", f"{response['engagementLevel']}/10")
        with metric_cols[2]:
            st.metric("Conversion Potential", f"{response['conversionPotential']}/10")
        
        # Key Insights
        st.markdown("**Key Insights:**")
        for insight in response['keyInsights']:
            st.markdown(f"• {insight}")
        
        # Full response (in an expander)
        with st.expander("📄 View Full Response"):
            st.write(response['response'])
        
        # Add separator
        st.markdown("---")

def display_empty_audience_card(profile):
    """Display an empty audience card using Streamlit components."""
    
    with st.container():
        # Card header
        st.markdown(f"### {profile['icon']} {profile['name']}")
        st.caption(profile['description'])
        
        # Traits
        st.markdown("**Key Characteristics:**")
        for trait in profile['traits']:
            st.markdown(f"• {trait}")
        
        # Empty state message
        st.markdown("---")
        st.markdown("*💬 Enter a scenario above to see this audience's response*")
        
        # Add bottom spacing
        st.markdown("")
