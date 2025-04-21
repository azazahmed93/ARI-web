import json
import streamlit as st
from core.ai_insights import ensure_valid_url_in_sites
from assets.content import (
    SITEONE_HISPANIC_SOCIAL_MEDIA,
    SITEONE_HISPANIC_TV_NETWORKS,
    SITEONE_HISPANIC_STREAMING,
)

def media_affinities(is_siteone_hispanic):
    if isinstance(st.session_state.audience_media_consumption, str):
        st.session_state.audience_media_consumption = json.loads(st.session_state.audience_media_consumption)


    # Check if we're analyzing Apple TV+ data
    is_apple_tv_campaign = "Apple TV+" in st.session_state.get("brief_text", "") or "Apple TV" in st.session_state.get("brief_text", "")
    
    if is_apple_tv_campaign:
        # Import Apple audience data functions
        from core.audience.apple_audience_data import generate_audience_affinities, get_apple_audience_data
        
        # Get the audience affinities
        affinity_data = generate_audience_affinities()
        
        # Store the full audience data in session state if not already there
        if 'audience_data' not in st.session_state or st.session_state.audience_data is None:
            st.session_state.audience_data = get_apple_audience_data()
        
        # Display Platform Affinities
        st.markdown("""
        <h3 style="display:flex; align-items:center; gap:10px; margin-top: 20px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 4H5C3.89 4 3 4.9 3 6V18C3 19.1 3.89 20 5 20H19C20.1 20 21 19.1 21 18V6C21 4.9 20.1 4 19 4ZM19 18H5V8H19V18ZM9 10H7V16H9V10ZM13 10H11V16H13V10ZM17 10H15V16H17V10Z" fill="#5865f2"/>
            </svg>
            <span>Apple TV+ Platform Affinities</span>
        </h3>
        """, unsafe_allow_html=True)
        
        st.markdown("*AVI = Affinity Value Index, indicating audience alignment strength*")
        
        # Create grid layout for platform affinities
        platform_cols = st.columns(5)
        
        # Get platform data
        platforms = [(k, v) for k, v in affinity_data["platforms"].items()]
        
        # Display each platform in a card
        for i, (platform, score) in enumerate(platforms):
            with platform_cols[i % 5]:
                st.markdown(f"""
                <div style="background:#e0edff; padding:15px; border-radius:10px; height:110px; margin-bottom:15px; overflow:hidden;">
                    <div style="font-weight:bold; font-size:0.95rem; margin-bottom:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{platform}</div>
                    <div style="font-size:0.85rem; margin-bottom:8px;">Media</div>
                    <div style="font-weight:bold; color:#3b82f6;">AVI: {score}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Create grid layout for content affinities
        st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
        content_cols = st.columns(5)
        
        # Get content data
        contents = [(k, v) for k, v in affinity_data["content"].items()]
        
        # Display each content type in a card
        for i, (content, score) in enumerate(contents):
            with content_cols[i % 5]:
                st.markdown(f"""
                <div style="background:#dbeafe; padding:15px; border-radius:10px; height:110px; margin-bottom:15px; overflow:hidden;">
                    <div style="font-weight:bold; font-size:0.95rem; margin-bottom:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{content}</div>
                    <div style="font-size:0.85rem; margin-bottom:8px;">Content</div>
                    <div style="font-weight:bold; color:#3b82f6;">AVI: {score}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Display Demographic and Lifestyle Affinities
        st.markdown("""
        <h3 style="display:flex; align-items:center; gap:10px; margin-top: 40px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="#5865f2"/>
            </svg>
            <span>Apple TV+ Audience Affinities</span>
        </h3>
        """, unsafe_allow_html=True)
        
        st.markdown("*AVI = Affinity Value Index, indicating audience preference strength*")
        
        # Create grid layout for demographic affinities
        demo_cols = st.columns(5)
        
        # Get demographic data
        demographics = [(k, v) for k, v in affinity_data["demographics"].items()]
        
        # Display each demographic in a card
        for i, (demo, score) in enumerate(demographics):
            with demo_cols[i % 5]:
                st.markdown(f"""
                <div style="background:#d1fae5; padding:15px; border-radius:10px; height:110px; margin-bottom:15px; overflow:hidden;">
                    <div style="font-weight:bold; font-size:0.95rem; margin-bottom:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{demo}</div>
                    <div style="font-size:0.85rem; margin-bottom:8px;">Demographic</div>
                    <div style="font-weight:bold; color:#10b981;">AVI: {score}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Create grid layout for lifestyle affinities
        st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
        lifestyle_cols = st.columns(5)
        
        # Get lifestyle data
        lifestyles = [(k, v) for k, v in affinity_data["lifestyle"].items()]
        
        # Display each lifestyle in a card
        for i, (lifestyle, score) in enumerate(lifestyles):
            with lifestyle_cols[i % 5]:
                st.markdown(f"""
                <div style="background:#fef3c7; padding:15px; border-radius:10px; height:110px; margin-bottom:15px; overflow:hidden;">
                    <div style="font-weight:bold; font-size:0.95rem; margin-bottom:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{lifestyle}</div>
                    <div style="font-size:0.85rem; margin-bottom:8px;">Lifestyle</div>
                    <div style="font-weight:bold; color:#d97706;">AVI: {score}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Add a divider before showing standard media affinity data
        st.markdown("<hr style='margin-top: 40px; margin-bottom: 40px;'>", unsafe_allow_html=True)
    
    # Standard Media Affinity section (shown for all campaigns)
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
        social_media_sites = ensure_valid_url_in_sites(json.loads(st.session_state.media_affinity))
    
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
        tv_network_data = st.session_state.audience_media_consumption['tv_networks']
    
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
        streaming_data = st.session_state.audience_media_consumption['streaming_platforms']
    
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
