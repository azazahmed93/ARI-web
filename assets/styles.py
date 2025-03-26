import streamlit as st

def apply_styles():
    """Apply custom styles for the ARI Analyzer."""
    st.markdown("""
    <style>
    /* Modern enterprise SaaS styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #5865f2 0%, #7983f5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-top: 0;
    }
    
    .description {
        font-size: 1.05rem;
        color: #555;
        text-align: center;
        margin: 1rem auto 1.5rem auto;
        max-width: 800px;
        line-height: 1.6;
    }
    
    /* Enterprise dashboard styling */
    .dashboard-container {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        padding: 24px;
        margin-bottom: 24px;
    }
    
    .stats-pill {
        background: #f5f7fa;
        border-radius: 30px;
        padding: 8px 16px;
        font-weight: 600;
        color: #5865f2;
        margin-right: 12px;
        display: inline-block;
    }
    
    .enterprise-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        color: #5865f2;
        margin-bottom: 8px;
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
    # Create a modern enterprise SaaS header with logo and stats
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        # Logo placeholder - would be an actual logo in production
        st.markdown("""
        <div style="background: linear-gradient(135deg, #5865f2 0%, #7289da 100%); width: 80px; height: 80px; 
        border-radius: 16px; display: flex; align-items: center; justify-content: center; 
        color: white; font-weight: bold; font-size: 24px; box-shadow: 0 4px 10px rgba(88, 101, 242, 0.3);">
        ARI
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<h1 class="main-header">Audience Resonance Index™</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Enterprise Marketing Intelligence Platform</p>', unsafe_allow_html=True)
    
    with col3:
        # Enterprise badge that appeals to investors
        st.markdown("""
        <div style="margin-top: 10px; text-align: center;">
            <div style="background-color: #f0f2ff; border: 1px solid #dbe0ff; border-radius: 4px; padding: 8px; display: inline-block;">
                <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; color: #5865f2;">Enterprise</div>
                <div style="font-weight: 600; font-size: 1.1rem; color: #5865f2;">PRO</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add more realistic business metrics for a marketing analytics SaaS platform
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 15px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2;">PROFILES</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #333; margin: 5px 0;">230M+</div>
            <div style="font-size: 0.8rem; color: #555;">Unique Profiles</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 15px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2;">DEVICES</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #333; margin: 5px 0;">600M+</div>
            <div style="font-size: 0.8rem; color: #555;">Connected Devices</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 15px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2;">ROI IMPACT</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #333; margin: 5px 0;">23%</div>
            <div style="font-size: 0.8rem; color: #555;">Avg. Increase</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 15px; text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; color: #5865f2;">DATA POINTS</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #333; margin: 5px 0;">250M+</div>
            <div style="font-size: 0.8rem; color: #555;">Analyzed Daily</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Product description that highlights the business value
    st.markdown("""
    <div class="description">
        Our proprietary <strong>Audience Resonance Index™</strong> combines advanced AI, cultural analytics, and marketing science to predict campaign effectiveness with 93% accuracy. 
        By measuring how campaigns connect with relevant audience signals, strategic platforms, and cultural values, we help Fortune 500 brands increase marketing ROI by an average of 23%.
    </div>
    """, unsafe_allow_html=True)
    
    # Adding some extra space after the description
    st.markdown("""
    <div style="margin-bottom: 30px;"></div>
    """, unsafe_allow_html=True)

def render_footer():
    """Render the footer section of the app."""
    # Company information section
    st.markdown("""
    <div style="margin-top: 60px; border-top: 1px solid #f0f0f0; padding-top: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div style="margin-bottom: 20px;">
                <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 5px; background: linear-gradient(90deg, #5865f2 0%, #7983f5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Powered by Digital Culture Group</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Copyright and links
    st.markdown("""
    <div style="display: flex; justify-content: space-between; margin-top: 20px; font-size: 0.8rem; color: #777;">
        <div>© 2025 Digital Culture Group, LLC. All rights reserved.</div>
        <div>
            <span style="margin-right: 15px;">Privacy Policy</span>
            <span style="margin-right: 15px;">Terms of Service</span>
            <span>Contact</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
