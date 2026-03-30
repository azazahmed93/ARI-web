import streamlit as st

def trend_analysis(brief_text, audience_segments=None):
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
    from app.components.marketing_trends import display_trend_heatmap
    display_trend_heatmap(brief_text, "Dynamic Media Performance Heatmap")

    # Audience segment performance heatmap
    if audience_segments and isinstance(audience_segments, dict):
        segments = audience_segments.get('segments', [])
        if segments and len(segments) > 0:
            st.markdown("---")
            st.markdown("""
            <h3 style="display:flex; align-items:center; gap:10px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" fill="#5865f2"/>
                </svg>
                Audience Segment Media Recommendation
            </h3>
            """, unsafe_allow_html=True)
            from app.components.marketing_trends import display_audience_segment_heatmap
            display_audience_segment_heatmap(brief_text, audience_segments, "Audience Segment Media Recommendation")
