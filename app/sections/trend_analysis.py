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

            # Social Platform Affinity (separate heatmap — informational, kept off the
            # ad-format channel axis and out of the Recommended Platform logic)
            st.markdown("---")
            st.markdown("""
            <h3 style="display:flex; align-items:center; gap:10px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z" fill="#5865f2"/>
                </svg>
                Social Platform Affinity
            </h3>
            """, unsafe_allow_html=True)
            from app.components.marketing_trends import display_social_platform_heatmap
            display_social_platform_heatmap(brief_text, audience_segments, "Social Platform Affinity")
