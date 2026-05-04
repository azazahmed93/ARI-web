import json
import streamlit as st
from core.ai_insights import ensure_valid_url_in_sites
from assets.content import (
    SITEONE_HISPANIC_SOCIAL_MEDIA,
    SITEONE_HISPANIC_TV_NETWORKS,
    SITEONE_HISPANIC_STREAMING,
)


def _collect_background_inventory():
    """Wait for background inventory thread and write results to session_state."""
    from app.layouts.landing_layout import _inventory_results, _inventory_lock

    # Check if background results are already collected
    if st.session_state.get('_inventory_collected'):
        return

    # Check if a background thread was launched
    inv_thread = st.session_state.get('_inventory_thread')
    req_id = st.session_state.get('_inventory_request_id')
    if inv_thread is None or req_id is None:
        return

    # Wait for thread to finish (with timeout + spinner)
    if inv_thread.is_alive():
        with st.spinner("Loading media inventory..."):
            inv_thread.join(timeout=90)

    # Collect results using session-specific request ID
    with _inventory_lock:
        result_entry = _inventory_results.pop(req_id, None)

    if result_entry and result_entry.get('data'):
        data = result_entry['data']
        if data.get('media_affinity'):
            st.session_state.media_affinity = data['media_affinity']

        media_consumption = st.session_state.get('audience_media_consumption', {})
        if isinstance(media_consumption, str):
            media_consumption = json.loads(media_consumption)
        if data.get('tv_networks'):
            media_consumption['tv_networks'] = data['tv_networks']
        if data.get('streaming_platforms'):
            media_consumption['streaming_platforms'] = data['streaming_platforms']
        st.session_state.audience_media_consumption = media_consumption

    st.session_state._inventory_collected = True


def media_affinities(is_siteone_hispanic):
    # Collect background inventory results before rendering
    _collect_background_inventory()

    if isinstance(st.session_state.audience_media_consumption, str):
        st.session_state.audience_media_consumption = json.loads(st.session_state.audience_media_consumption)


    # Standard Media Affinity section
    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 4H5C3.89 4 3 4.9 3 6V18C3 19.1 3.89 20 5 20H19C20.1 20 21 19.1 21 18V6C21 4.9 20.1 4 19 4ZM19 18H5V8H19V18ZM9 10H7V16H9V10ZM13 10H11V16H13V10ZM17 10H15V16H17V10Z" fill="#5865f2"/>
        </svg>
        Top Media Affinity Sites
    </h3>
    """, unsafe_allow_html=True)
    st.markdown("*Website Index = a score indicating audience engagement strength*")
    
    # Display media affinity sites in a grid
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    # Use SiteOne Hispanic social media data if this is a SiteOne Hispanic campaign
    if is_siteone_hispanic:
        social_media_sites = ensure_valid_url_in_sites(SITEONE_HISPANIC_SOCIAL_MEDIA)
    else:
        media_affinity_data = st.session_state.media_affinity
        if isinstance(media_affinity_data, str):
            media_affinity_data = json.loads(media_affinity_data)
        social_media_sites = ensure_valid_url_in_sites(media_affinity_data)
    
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
                <div style="font-weight:bold; color:#3b82f6; margin-bottom:5px;">Website Index: {site['qvi']}</div>
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
        tv_network_data = st.session_state.audience_media_consumption.get('tv_networks', [])

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
                <div style="font-weight:bold; color:#3b82f6;">Website Index: {network['qvi']}</div>
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
        streaming_data = st.session_state.audience_media_consumption.get('streaming_platforms', [])
    
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
                <div style="font-weight:bold; color:#10b981;">Website Index: {platform['qvi']}</div>
            </div>
            """, unsafe_allow_html=True)
