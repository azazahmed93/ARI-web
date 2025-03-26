import streamlit as st

def apply_styles():
    """Apply custom styles for the ARI Analyzer."""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
    }
    
    .description {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin: 0.5rem auto;
    }
    
    .metric-container {
        margin-bottom: 1.5rem;
    }
    
    .metric-label {
        font-weight: 700;
        display: flex;
        justify-content: space-between;
        font-size: 1rem;
        margin-bottom: 0.25rem;
    }
    
    .tooltip {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .benchmark {
        margin-top: 2rem;
        padding: 1rem;
        background-color: #f5f7fa;
        border-left: 4px solid #3b82f6;
    }
    
    .affinity-card {
        background-color: #e0edff;
        padding: 1rem;
        border-radius: 10px;
        transition: transform 0.2s;
    }
    
    .network-card {
        background-color: #dbeafe;
        padding: 1rem;
        border-radius: 10px;
    }
    
    .streaming-card {
        background-color: #d1fae5;
        padding: 1rem;
        border-radius: 10px;
    }
    
    .psycho-highlights {
        margin-top: 2rem;
        background-color: #fff9f1;
        padding: 1.5rem;
        border-left: 4px solid #f4b400;
    }
    
    .audience-summary {
        margin-top: 2rem;
        background-color: #e8f0fe;
        padding: 1.2rem 1.5rem;
        border-left: 4px solid #3367d6;
    }
    
    .next-steps {
        margin-top: 2rem;
    }
    
    .footer {
        font-size: 0.9rem;
        color: #555;
        margin-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def header_section():
    """Render the header section of the app."""
    st.markdown('<h1 class="main-header">Audience Resonance Index <span style="font-weight: 500; font-size: 1.2rem;">(ARI)</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">A proprietary framework by <strong>Digital Culture Group</strong></p>', unsafe_allow_html=True)
    st.markdown('<p class="description"><strong>Audience Resonance Index™ (ARI)</strong> measures how effectively a campaign connects with relevant signals, strategic platforms, and audience values. It helps marketers understand their campaign's ability to generate relevance, authenticity, and emotional resonance.</p>', unsafe_allow_html=True)

def render_footer():
    """Render the footer section of the app."""
    st.markdown('<p class="footer">Powered by <strong>Digital Culture Group</strong></p>', unsafe_allow_html=True)
